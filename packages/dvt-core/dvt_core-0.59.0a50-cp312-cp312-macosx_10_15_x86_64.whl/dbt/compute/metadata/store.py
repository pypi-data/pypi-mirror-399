# =============================================================================
# DVT Project Metastore
# =============================================================================
# DuckDB-based metastore for DVT project RUNTIME data.
#
# RUNTIME/OPERATIONAL DATA (populated during execution):
# - column_metadata: Column schema info from federated runs
# - row_counts: Cached row counts from dvt snap
# - profile_results: Data profiling from dvt profile
#
# NOTE: Catalog data (targets, sources, models, lineage) is now stored
# in a SEPARATE catalog.duckdb file. See CatalogStore class.
#
# Static registry data (type mappings, syntax rules, adapter queries) comes
# from the shipped adapters_registry.duckdb via AdaptersRegistry class.
#
# Location: <project>/.dvt/metastore.duckdb
#
# DVT v0.54.0: Initial implementation
# DVT v0.55.0: Refactored to separate project metadata from shipped registry
# DVT v0.59.0: Separated into metastore.duckdb (runtime) and catalog.duckdb
#              (project catalog). Renamed from metadata_store.duckdb.
# =============================================================================

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

from dbt.compute.metadata.adapters_registry import (
    AdaptersRegistry,
    TypeMapping,
    SyntaxRule,
    get_registry,
    get_spark_type as registry_get_spark_type,
    get_syntax_rule as registry_get_syntax_rule,
    get_metadata_query as registry_get_metadata_query,
)


@dataclass
class ColumnMetadata:
    """Metadata for a single column."""
    column_name: str
    adapter_type: str
    spark_type: str
    is_nullable: bool
    is_primary_key: bool
    ordinal_position: int


@dataclass
class TableMetadata:
    """Metadata for a table/view (columns only, no row count)."""
    source_name: str
    table_name: str
    adapter_name: str
    connection_name: str
    schema_name: str
    columns: List[ColumnMetadata]
    last_refreshed: datetime


@dataclass
class RowCountInfo:
    """Row count information for a table."""
    source_name: str
    table_name: str
    row_count: int
    last_refreshed: datetime


# =============================================================================
# Profile Results (v0.56.0 - dvt profile command)
# =============================================================================

@dataclass
class ColumnProfileResult:
    """Profile result for a single column."""
    source_name: str
    table_name: str
    column_name: str
    profile_mode: str  # 'minimal', 'explorative', 'sensitive', 'time-series'

    # Basic metrics (all modes)
    row_count: Optional[int] = None
    null_count: Optional[int] = None
    null_percent: Optional[float] = None
    distinct_count: Optional[int] = None
    distinct_percent: Optional[float] = None

    # Numeric metrics (explorative+)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    stddev_value: Optional[float] = None
    p25: Optional[float] = None
    p50: Optional[float] = None
    p75: Optional[float] = None

    # String metrics (explorative+)
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None

    # Distribution data (JSON strings)
    histogram: Optional[str] = None  # JSON: bucket counts
    top_values: Optional[str] = None  # JSON: top N values with counts

    # Quality alerts (JSON string)
    alerts: Optional[str] = None  # JSON: [{type, severity, message}]

    # Metadata
    profiled_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


# NOTE: CatalogNode, LineageEdge, TargetDefinition, SourceTableDefinition,
# ModelDefinition are now in catalog_store.py (v0.59.0 refactor)


class ProjectMetadataStore:
    """
    DuckDB-based metastore for a DVT project runtime data.

    Location: <project_root>/.dvt/metastore.duckdb

    Tables (runtime/operational data):
    - column_metadata: Schema info from federated runs
    - row_counts: Cached row counts from dvt snap
    - profile_results: Data profiling from dvt profile

    NOTE: Catalog data (targets, sources, models, lineage) is stored in
    a separate catalog.duckdb file. See CatalogStore class.

    NOTE: Static registry data (type mappings, syntax rules, adapter queries)
    comes from the shipped adapters_registry.duckdb via AdaptersRegistry class.
    """

    DVT_DIR = ".dvt"
    METADATA_DB = "metastore.duckdb"  # Renamed from metadata_store.duckdb in v0.59.0

    def __init__(self, project_root: Path):
        """
        Initialize the metadata store.

        Args:
            project_root: Path to the DVT project root directory
        """
        if not HAS_DUCKDB:
            raise ImportError(
                "DuckDB is required for metadata store. "
                "Install with: pip install duckdb"
            )

        self.project_root = Path(project_root)
        self.dvt_dir = self.project_root / self.DVT_DIR
        self.db_path = self.dvt_dir / self.METADATA_DB
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        self._registry: Optional[AdaptersRegistry] = None

    @property
    def conn(self) -> "duckdb.DuckDBPyConnection":
        """Get or create database connection."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    @property
    def registry(self) -> AdaptersRegistry:
        """Get the shipped adapters registry (singleton)."""
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "ProjectMetadataStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # =========================================================================
    # Initialization
    # =========================================================================

    def initialize(self, drop_existing: bool = True) -> None:
        """
        Initialize the metadata store.

        Creates:
        1. .dvt/ directory if it doesn't exist
        2. metastore.duckdb database
        3. Schema tables (column_metadata, row_counts, profile_results)

        Args:
            drop_existing: If True, drops existing tables and recreates them
                          with empty schemas. Default is True to ensure clean
                          initialization on each `dvt init`.

        NOTE: No registry data is loaded - that comes from shipped DuckDB.
        """
        # Create .dvt/ directory
        self.dvt_dir.mkdir(parents=True, exist_ok=True)

        # Drop existing tables if requested (for clean init)
        if drop_existing:
            self._drop_all_tables()

        # Create schema tables
        self._create_schema()

    def _drop_all_tables(self) -> None:
        """Drop all metastore tables to reset to empty state."""
        tables = [
            "profile_results",
            "row_counts",
            "column_metadata",
        ]
        for table in tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {table}")

    def _create_schema(self) -> None:
        """Create the database schema tables."""

        # Column metadata table (populated by dvt snap or federated runs)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS column_metadata (
                source_name VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                column_name VARCHAR NOT NULL,
                adapter_name VARCHAR NOT NULL,
                connection_name VARCHAR NOT NULL,
                schema_name VARCHAR,
                adapter_type VARCHAR NOT NULL,
                spark_type VARCHAR NOT NULL,
                is_nullable BOOLEAN DEFAULT TRUE,
                is_primary_key BOOLEAN DEFAULT FALSE,
                ordinal_position INTEGER,
                last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(source_name, table_name, column_name)
            )
        """)

        # Row counts table (ONLY populated by dvt snap, not during runs)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS row_counts (
                source_name VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                row_count BIGINT,
                last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(source_name, table_name)
            )
        """)

        # =====================================================================
        # v0.56.0: Profile Results (dvt profile command)
        # =====================================================================
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS profile_results (
                source_name VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                column_name VARCHAR NOT NULL,
                profile_mode VARCHAR NOT NULL,

                -- Basic metrics (all modes)
                row_count BIGINT,
                null_count BIGINT,
                null_percent DOUBLE,
                distinct_count BIGINT,
                distinct_percent DOUBLE,

                -- Numeric metrics (explorative+)
                min_value DOUBLE,
                max_value DOUBLE,
                mean_value DOUBLE,
                median_value DOUBLE,
                stddev_value DOUBLE,
                p25 DOUBLE,
                p50 DOUBLE,
                p75 DOUBLE,

                -- String metrics (explorative+)
                min_length INTEGER,
                max_length INTEGER,
                avg_length DOUBLE,

                -- Distribution data (JSON)
                histogram JSON,
                top_values JSON,

                -- Quality alerts
                alerts JSON,

                -- Metadata
                profiled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_ms INTEGER,

                PRIMARY KEY(source_name, table_name, column_name, profile_mode)
            )
        """)

        # NOTE: Catalog tables (catalog_nodes, lineage_edges, targets,
        # source_definitions, model_definitions) are now in catalog.duckdb
        # See CatalogStore class (v0.59.0 refactor)

        # Create indexes for fast lookups
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_column_metadata_source
            ON column_metadata(source_name, table_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_column_metadata_adapter
            ON column_metadata(adapter_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_row_counts_source
            ON row_counts(source_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_profile_results_table
            ON profile_results(source_name, table_name)
        """)

    # =========================================================================
    # Type Registry Queries (delegated to shipped AdaptersRegistry)
    # =========================================================================

    def get_spark_type(
        self,
        adapter_name: str,
        adapter_type: str,
        spark_version: str = "all"
    ) -> Optional[str]:
        """
        Look up the Spark type for an adapter type.

        Delegates to the shipped AdaptersRegistry.

        Args:
            adapter_name: Name of the adapter (e.g., 'postgres', 'snowflake')
            adapter_type: Native adapter type (e.g., 'VARCHAR', 'INTEGER')
            spark_version: Target Spark version (default: 'all')

        Returns:
            Spark type string or None if not found
        """
        mapping = self.registry.get_spark_type(adapter_name, adapter_type, spark_version)
        return mapping.spark_type if mapping else None

    def get_type_mappings(
        self,
        adapter_name: str,
        spark_version: str = "all"
    ) -> List[Tuple[str, str]]:
        """
        Get all type mappings for an adapter.

        Delegates to the shipped AdaptersRegistry.

        Returns:
            List of (adapter_type, spark_type) tuples
        """
        mappings = self.registry.get_all_mappings_for_adapter(adapter_name)
        return [(m.adapter_type, m.spark_type) for m in mappings]

    # =========================================================================
    # Syntax Registry Queries (delegated to shipped AdaptersRegistry)
    # =========================================================================

    def get_syntax_rule(self, adapter_name: str) -> Optional[SyntaxRule]:
        """
        Get syntax rules for an adapter.

        Delegates to the shipped AdaptersRegistry.

        Args:
            adapter_name: Name of the adapter

        Returns:
            SyntaxRule or None if not found
        """
        return self.registry.get_syntax_rule(adapter_name)

    def quote_identifier(self, adapter_name: str, identifier: str) -> str:
        """Quote an identifier for the given adapter."""
        return self.registry.quote_identifier(adapter_name, identifier)

    # =========================================================================
    # Adapter Metadata Queries (delegated to shipped AdaptersRegistry)
    # =========================================================================

    def get_metadata_query(
        self,
        adapter_name: str,
        query_type: str
    ) -> Optional[str]:
        """
        Get the metadata query template for an adapter.

        Delegates to the shipped AdaptersRegistry.

        Args:
            adapter_name: Name of the adapter
            query_type: Type of query ('columns', 'tables', 'row_count', 'primary_key')

        Returns:
            Query template string or None if not found
        """
        query = self.registry.get_metadata_query(adapter_name, query_type)
        return query.query_template if query else None

    # =========================================================================
    # Column Metadata Operations
    # =========================================================================

    def save_table_metadata(self, metadata: TableMetadata) -> None:
        """
        Save table column metadata to the store.

        This is called during federated execution to capture schema info.

        Args:
            metadata: TableMetadata object with column info
        """
        # Delete existing entries for this table
        self.conn.execute("""
            DELETE FROM column_metadata
            WHERE source_name = ? AND table_name = ?
        """, [metadata.source_name, metadata.table_name])

        # Insert new entries
        for col in metadata.columns:
            self.conn.execute("""
                INSERT INTO column_metadata
                (source_name, table_name, column_name, adapter_name, connection_name,
                 schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                 ordinal_position, last_refreshed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                metadata.source_name,
                metadata.table_name,
                col.column_name,
                metadata.adapter_name,
                metadata.connection_name,
                metadata.schema_name,
                col.adapter_type,
                col.spark_type,
                col.is_nullable,
                col.is_primary_key,
                col.ordinal_position,
                metadata.last_refreshed
            ])

    def get_table_metadata(
        self,
        source_name: str,
        table_name: str
    ) -> Optional[TableMetadata]:
        """
        Get cached column metadata for a table.

        Args:
            source_name: Name of the source
            table_name: Name of the table

        Returns:
            TableMetadata or None if not cached
        """
        results = self.conn.execute("""
            SELECT
                source_name, table_name, column_name, adapter_name, connection_name,
                schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                ordinal_position, last_refreshed
            FROM column_metadata
            WHERE source_name = ? AND table_name = ?
            ORDER BY ordinal_position
        """, [source_name, table_name]).fetchall()

        if not results:
            return None

        # Build column list
        columns = []
        for r in results:
            columns.append(ColumnMetadata(
                column_name=r[2],
                adapter_type=r[6],
                spark_type=r[7],
                is_nullable=r[8],
                is_primary_key=r[9],
                ordinal_position=r[10]
            ))

        # Build TableMetadata from first row
        first = results[0]
        return TableMetadata(
            source_name=first[0],
            table_name=first[1],
            adapter_name=first[3],
            connection_name=first[4],
            schema_name=first[5],
            columns=columns,
            last_refreshed=first[11]
        )

    def get_all_sources(self) -> List[Tuple[str, str]]:
        """
        Get all source/table combinations in the store.

        Returns:
            List of (source_name, table_name) tuples
        """
        results = self.conn.execute("""
            SELECT DISTINCT source_name, table_name
            FROM column_metadata
            ORDER BY source_name, table_name
        """).fetchall()

        return [(r[0], r[1]) for r in results]

    def clear_column_metadata(self) -> None:
        """Clear all column metadata."""
        self.conn.execute("DELETE FROM column_metadata")

    # =========================================================================
    # Row Count Operations (dvt snap only)
    # =========================================================================

    def save_row_count(
        self,
        source_name: str,
        table_name: str,
        row_count: int,
        last_refreshed: Optional[datetime] = None
    ) -> None:
        """
        Save row count for a table.

        This is ONLY called by dvt snap, not during regular runs.

        Args:
            source_name: Name of the source
            table_name: Name of the table
            row_count: Number of rows
            last_refreshed: Timestamp (defaults to now)
        """
        if last_refreshed is None:
            last_refreshed = datetime.now()

        self.conn.execute("""
            INSERT OR REPLACE INTO row_counts
            (source_name, table_name, row_count, last_refreshed)
            VALUES (?, ?, ?, ?)
        """, [source_name, table_name, row_count, last_refreshed])

    def get_row_count(self, source_name: str, table_name: str) -> Optional[RowCountInfo]:
        """
        Get cached row count for a table.

        Args:
            source_name: Name of the source
            table_name: Name of the table

        Returns:
            RowCountInfo or None if not cached
        """
        result = self.conn.execute("""
            SELECT source_name, table_name, row_count, last_refreshed
            FROM row_counts
            WHERE source_name = ? AND table_name = ?
        """, [source_name, table_name]).fetchone()

        if result:
            return RowCountInfo(
                source_name=result[0],
                table_name=result[1],
                row_count=result[2],
                last_refreshed=result[3]
            )
        return None

    def get_all_row_counts(self) -> List[RowCountInfo]:
        """
        Get all cached row counts.

        Returns:
            List of RowCountInfo objects
        """
        results = self.conn.execute("""
            SELECT source_name, table_name, row_count, last_refreshed
            FROM row_counts
            ORDER BY source_name, table_name
        """).fetchall()

        return [
            RowCountInfo(
                source_name=r[0],
                table_name=r[1],
                row_count=r[2],
                last_refreshed=r[3]
            )
            for r in results
        ]

    def clear_row_counts(self) -> None:
        """Clear all row count data."""
        self.conn.execute("DELETE FROM row_counts")

    def clear_snapshot(self) -> None:
        """Clear all snapshot data (both column metadata and row counts)."""
        self.clear_column_metadata()
        self.clear_row_counts()

    def clear_all_metadata(self) -> None:
        """Clear ALL metadata from the store (columns, row counts, profiles)."""
        self.clear_column_metadata()
        self.clear_row_counts()
        self.clear_profile_results()

    def has_source_metadata(self) -> bool:
        """
        Check if there is any source metadata in the store.

        Used to determine if this is the first run (auto-snapshot needed).

        Returns:
            True if source metadata exists, False otherwise
        """
        result = self.conn.execute("""
            SELECT COUNT(*) FROM column_metadata
            WHERE source_name NOT LIKE 'model:%'
        """).fetchone()[0]
        return result > 0

    def has_any_metadata(self) -> bool:
        """
        Check if there is any metadata (sources or models) in the store.

        Returns:
            True if any metadata exists, False otherwise
        """
        result = self.conn.execute(
            "SELECT COUNT(*) FROM column_metadata"
        ).fetchone()[0]
        return result > 0

    # =========================================================================
    # Legacy Compatibility - save_table_metadata with row_count
    # =========================================================================

    def save_table_metadata_with_row_count(
        self,
        source_name: str,
        table_name: str,
        adapter_name: str,
        connection_name: str,
        schema_name: str,
        columns: List[ColumnMetadata],
        row_count: Optional[int],
        last_refreshed: datetime
    ) -> None:
        """
        Save both column metadata and row count (used by dvt snap).

        Args:
            source_name: Name of the source
            table_name: Name of the table
            adapter_name: Name of the adapter
            connection_name: Name of the connection
            schema_name: Schema name
            columns: List of ColumnMetadata
            row_count: Number of rows (or None)
            last_refreshed: Timestamp
        """
        # Save column metadata
        metadata = TableMetadata(
            source_name=source_name,
            table_name=table_name,
            adapter_name=adapter_name,
            connection_name=connection_name,
            schema_name=schema_name,
            columns=columns,
            last_refreshed=last_refreshed
        )
        self.save_table_metadata(metadata)

        # Save row count separately (only if provided)
        if row_count is not None:
            self.save_row_count(source_name, table_name, row_count, last_refreshed)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def exists(self) -> bool:
        """Check if the metadata store exists."""
        return self.db_path.exists()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the metadata store."""
        # Count column metadata
        tables_count = self.conn.execute(
            "SELECT COUNT(DISTINCT source_name || '.' || table_name) FROM column_metadata"
        ).fetchone()[0]

        columns_count = self.conn.execute(
            "SELECT COUNT(*) FROM column_metadata"
        ).fetchone()[0]

        # Count row counts
        row_counts_count = self.conn.execute(
            "SELECT COUNT(*) FROM row_counts"
        ).fetchone()[0]

        # Get registry stats
        registry = self.registry
        adapters = registry.get_supported_adapters()

        return {
            "metadata_tables": tables_count,
            "metadata_columns": columns_count,
            "row_counts_cached": row_counts_count,
            "registry_adapters": len(adapters),
            "supported_adapters": adapters,
            "db_path": str(self.db_path),
        }

    def migrate_from_legacy(self) -> bool:
        """
        Migrate from legacy metadata.duckdb format to new format.

        Returns:
            True if migration was performed, False if not needed
        """
        legacy_path = self.dvt_dir / "metadata.duckdb"
        if not legacy_path.exists():
            return False

        # Check if new store already exists
        if self.db_path.exists():
            return False

        try:
            # Connect to legacy database
            legacy_conn = duckdb.connect(str(legacy_path), read_only=True)

            # Check if metadata_snapshot table exists
            result = legacy_conn.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = 'metadata_snapshot'
            """).fetchone()[0]

            if result == 0:
                legacy_conn.close()
                return False

            # Initialize new store
            self.initialize()

            # Migrate metadata_snapshot to column_metadata
            rows = legacy_conn.execute("""
                SELECT DISTINCT
                    source_name, table_name, column_name, adapter_name, connection_name,
                    schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                    ordinal_position, last_refreshed
                FROM metadata_snapshot
            """).fetchall()

            for row in rows:
                self.conn.execute("""
                    INSERT OR REPLACE INTO column_metadata
                    (source_name, table_name, column_name, adapter_name, connection_name,
                     schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                     ordinal_position, last_refreshed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, list(row))

            # Migrate row_count data (distinct per table)
            row_count_rows = legacy_conn.execute("""
                SELECT DISTINCT source_name, table_name, row_count, MAX(last_refreshed)
                FROM metadata_snapshot
                WHERE row_count IS NOT NULL
                GROUP BY source_name, table_name, row_count
            """).fetchall()

            for row in row_count_rows:
                if row[2] is not None:  # row_count
                    self.conn.execute("""
                        INSERT OR REPLACE INTO row_counts
                        (source_name, table_name, row_count, last_refreshed)
                        VALUES (?, ?, ?, ?)
                    """, list(row))

            legacy_conn.close()
            return True

        except Exception as e:
            print(f"[DVT] Warning: Migration failed: {e}")
            return False

    # =========================================================================
    # Profile Results Operations (v0.56.0 - dvt profile command)
    # =========================================================================

    def save_profile_result(self, result: ColumnProfileResult) -> None:
        """
        Save a column profile result to the store.

        Args:
            result: ColumnProfileResult object
        """
        self.conn.execute("""
            INSERT OR REPLACE INTO profile_results
            (source_name, table_name, column_name, profile_mode,
             row_count, null_count, null_percent, distinct_count, distinct_percent,
             min_value, max_value, mean_value, median_value, stddev_value,
             p25, p50, p75, min_length, max_length, avg_length,
             histogram, top_values, alerts, profiled_at, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            result.source_name, result.table_name, result.column_name, result.profile_mode,
            result.row_count, result.null_count, result.null_percent,
            result.distinct_count, result.distinct_percent,
            result.min_value, result.max_value, result.mean_value,
            result.median_value, result.stddev_value,
            result.p25, result.p50, result.p75,
            result.min_length, result.max_length, result.avg_length,
            result.histogram, result.top_values, result.alerts,
            result.profiled_at or datetime.now(), result.duration_ms
        ])

    def save_profile_results_batch(self, results: List[ColumnProfileResult]) -> None:
        """
        Save multiple profile results in a batch.

        Args:
            results: List of ColumnProfileResult objects
        """
        for result in results:
            self.save_profile_result(result)

    def get_profile_result(
        self,
        source_name: str,
        table_name: str,
        column_name: str,
        profile_mode: str
    ) -> Optional[ColumnProfileResult]:
        """
        Get a profile result for a specific column.

        Args:
            source_name: Name of the source
            table_name: Name of the table
            column_name: Name of the column
            profile_mode: Profile mode ('minimal', 'explorative', etc.)

        Returns:
            ColumnProfileResult or None if not found
        """
        result = self.conn.execute("""
            SELECT source_name, table_name, column_name, profile_mode,
                   row_count, null_count, null_percent, distinct_count, distinct_percent,
                   min_value, max_value, mean_value, median_value, stddev_value,
                   p25, p50, p75, min_length, max_length, avg_length,
                   histogram, top_values, alerts, profiled_at, duration_ms
            FROM profile_results
            WHERE source_name = ? AND table_name = ? AND column_name = ? AND profile_mode = ?
        """, [source_name, table_name, column_name, profile_mode]).fetchone()

        if result:
            return ColumnProfileResult(
                source_name=result[0], table_name=result[1],
                column_name=result[2], profile_mode=result[3],
                row_count=result[4], null_count=result[5], null_percent=result[6],
                distinct_count=result[7], distinct_percent=result[8],
                min_value=result[9], max_value=result[10], mean_value=result[11],
                median_value=result[12], stddev_value=result[13],
                p25=result[14], p50=result[15], p75=result[16],
                min_length=result[17], max_length=result[18], avg_length=result[19],
                histogram=result[20], top_values=result[21], alerts=result[22],
                profiled_at=result[23], duration_ms=result[24]
            )
        return None

    def get_table_profile(
        self,
        source_name: str,
        table_name: str,
        profile_mode: Optional[str] = None
    ) -> List[ColumnProfileResult]:
        """
        Get all profile results for a table.

        Args:
            source_name: Name of the source
            table_name: Name of the table
            profile_mode: Optional mode filter

        Returns:
            List of ColumnProfileResult objects
        """
        if profile_mode:
            results = self.conn.execute("""
                SELECT source_name, table_name, column_name, profile_mode,
                       row_count, null_count, null_percent, distinct_count, distinct_percent,
                       min_value, max_value, mean_value, median_value, stddev_value,
                       p25, p50, p75, min_length, max_length, avg_length,
                       histogram, top_values, alerts, profiled_at, duration_ms
                FROM profile_results
                WHERE source_name = ? AND table_name = ? AND profile_mode = ?
                ORDER BY column_name
            """, [source_name, table_name, profile_mode]).fetchall()
        else:
            results = self.conn.execute("""
                SELECT source_name, table_name, column_name, profile_mode,
                       row_count, null_count, null_percent, distinct_count, distinct_percent,
                       min_value, max_value, mean_value, median_value, stddev_value,
                       p25, p50, p75, min_length, max_length, avg_length,
                       histogram, top_values, alerts, profiled_at, duration_ms
                FROM profile_results
                WHERE source_name = ? AND table_name = ?
                ORDER BY column_name
            """, [source_name, table_name]).fetchall()

        return [
            ColumnProfileResult(
                source_name=r[0], table_name=r[1], column_name=r[2], profile_mode=r[3],
                row_count=r[4], null_count=r[5], null_percent=r[6],
                distinct_count=r[7], distinct_percent=r[8],
                min_value=r[9], max_value=r[10], mean_value=r[11],
                median_value=r[12], stddev_value=r[13],
                p25=r[14], p50=r[15], p75=r[16],
                min_length=r[17], max_length=r[18], avg_length=r[19],
                histogram=r[20], top_values=r[21], alerts=r[22],
                profiled_at=r[23], duration_ms=r[24]
            )
            for r in results
        ]

    def get_all_profiled_tables(self) -> List[Tuple[str, str, str, datetime]]:
        """
        Get all profiled tables with their latest profile timestamp.

        Returns:
            List of (source_name, table_name, profile_mode, profiled_at) tuples
        """
        results = self.conn.execute("""
            SELECT source_name, table_name, profile_mode, MAX(profiled_at) as last_profiled
            FROM profile_results
            GROUP BY source_name, table_name, profile_mode
            ORDER BY source_name, table_name
        """).fetchall()

        return [(r[0], r[1], r[2], r[3]) for r in results]

    def get_profile_alerts(self, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all profile alerts, optionally filtered by source.

        Args:
            source_name: Optional source filter

        Returns:
            List of alert dicts with source/table/column info
        """
        import json

        if source_name:
            results = self.conn.execute("""
                SELECT source_name, table_name, column_name, alerts
                FROM profile_results
                WHERE source_name = ? AND alerts IS NOT NULL
            """, [source_name]).fetchall()
        else:
            results = self.conn.execute("""
                SELECT source_name, table_name, column_name, alerts
                FROM profile_results
                WHERE alerts IS NOT NULL
            """).fetchall()

        all_alerts = []
        for r in results:
            try:
                alerts = json.loads(r[3]) if r[3] else []
                for alert in alerts:
                    alert["source_name"] = r[0]
                    alert["table_name"] = r[1]
                    alert["column_name"] = r[2]
                    all_alerts.append(alert)
            except json.JSONDecodeError:
                pass

        return all_alerts

    def clear_profile_results(self, source_name: Optional[str] = None) -> None:
        """
        Clear profile results, optionally for a specific source.

        Args:
            source_name: Optional source filter
        """
        if source_name:
            self.conn.execute("DELETE FROM profile_results WHERE source_name = ?", [source_name])
        else:
            self.conn.execute("DELETE FROM profile_results")
