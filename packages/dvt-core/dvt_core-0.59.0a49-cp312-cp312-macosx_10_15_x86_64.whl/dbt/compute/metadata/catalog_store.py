# =============================================================================
# DVT Catalog Store
# =============================================================================
# DuckDB-based catalog store for DVT projects.
#
# This store contains PROJECT CATALOG data:
# - targets: Available connections from profiles.yml
# - source_definitions: Sources with connections from manifest
# - model_definitions: Models with targets from manifest
# - catalog_nodes: Enriched catalog for docs visualization
# - lineage_edges: DAG lineage for visualization
#
# Location: <project>/.dvt/catalog.duckdb
#
# SEPARATION OF CONCERNS:
# - catalog.duckdb: Project structure (targets, sources, models, lineage)
# - metastore.duckdb: Runtime data (profile_results, column_metadata, row_counts)
#
# This separation ensures that catalog operations don't interfere with
# runtime operations like profiling, run, build, etc.
#
# DVT v0.59.0: Initial implementation
# =============================================================================

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TargetDefinition:
    """Target/connection definition from profiles.yml."""
    name: str
    adapter_type: str
    database: Optional[str] = None
    schema_name: Optional[str] = None
    is_default: bool = False
    host: Optional[str] = None  # Sanitized, no secrets
    port: Optional[int] = None
    meta: Optional[str] = None  # JSON
    last_verified: Optional[datetime] = None


@dataclass
class SourceTableDefinition:
    """Source table definition from manifest (sources.yml)."""
    unique_id: str  # source.project.source_name.table_name
    source_name: str
    table_name: str
    connection_name: str  # Target/output to use for this source
    database: Optional[str] = None
    schema_name: Optional[str] = None
    adapter_type: Optional[str] = None
    identifier: Optional[str] = None  # Physical table name if different
    description: Optional[str] = None
    loader: Optional[str] = None
    meta: Optional[str] = None  # JSON
    freshness: Optional[str] = None  # JSON
    columns: Optional[str] = None  # JSON array
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ModelDefinition:
    """Model definition from manifest."""
    unique_id: str
    name: str
    connection_name: str  # Target for this model
    database: Optional[str] = None
    schema_name: Optional[str] = None
    adapter_type: Optional[str] = None
    materialized: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None  # JSON array
    meta: Optional[str] = None  # JSON
    config: Optional[str] = None  # JSON
    columns: Optional[str] = None  # JSON array
    depends_on_nodes: Optional[str] = None  # JSON array
    compiled_sql_hash: Optional[str] = None  # For change detection
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CatalogNode:
    """Enriched catalog node for dvt docs generate."""
    unique_id: str
    resource_type: str  # 'model', 'source', 'test', 'seed', 'snapshot'
    name: str
    schema_name: Optional[str] = None
    database: Optional[str] = None
    connection_name: Optional[str] = None
    adapter_type: Optional[str] = None
    description: Optional[str] = None
    icon_type: Optional[str] = None
    color_hex: Optional[str] = None
    materialized: Optional[str] = None
    tags: Optional[str] = None  # JSON array
    meta: Optional[str] = None  # JSON object
    columns: Optional[str] = None  # JSON array
    row_count: Optional[int] = None
    bytes_stored: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LineageEdge:
    """Lineage edge representing a dependency between nodes."""
    id: Optional[int] = None
    source_node_id: str = ""
    target_node_id: str = ""
    edge_type: str = ""  # 'ref', 'source', 'depends_on'
    is_cross_connection: bool = False
    source_connection: Optional[str] = None
    target_connection: Optional[str] = None


class CatalogStore:
    """
    DuckDB-based catalog store for a DVT project.

    Location: <project_root>/.dvt/catalog.duckdb

    Tables:
    - targets: Available connections from profiles.yml
    - source_definitions: Sources with connections from manifest
    - model_definitions: Models with targets from manifest
    - catalog_nodes: Enriched catalog for docs
    - lineage_edges: DAG lineage for visualization

    This store is SEPARATE from metastore.duckdb to avoid interference
    between catalog operations and runtime operations.
    """

    DVT_DIR = ".dvt"
    CATALOG_DB = "catalog.duckdb"

    def __init__(self, project_root: Path):
        """
        Initialize the catalog store.

        Args:
            project_root: Path to the DVT project root directory
        """
        if not HAS_DUCKDB:
            raise ImportError(
                "DuckDB is required for catalog store. "
                "Install with: pip install duckdb"
            )

        self.project_root = Path(project_root)
        self.dvt_dir = self.project_root / self.DVT_DIR
        self.db_path = self.dvt_dir / self.CATALOG_DB
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    @property
    def conn(self) -> "duckdb.DuckDBPyConnection":
        """Get or create database connection."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "CatalogStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # =========================================================================
    # Initialization
    # =========================================================================

    def initialize(self, drop_existing: bool = True) -> None:
        """
        Initialize the catalog store.

        Creates:
        1. .dvt/ directory if it doesn't exist
        2. catalog.duckdb database
        3. Schema tables (empty)

        Args:
            drop_existing: If True, drops existing tables and recreates them
                          with empty schemas. Default is True to ensure clean
                          initialization on each `dvt init`.
        """
        self.dvt_dir.mkdir(parents=True, exist_ok=True)

        if drop_existing:
            self._drop_all_tables()

        self._create_schema()

    def _drop_all_tables(self) -> None:
        """Drop all catalog tables to reset to empty state."""
        tables = [
            "lineage_edges",
            "catalog_nodes",
            "model_definitions",
            "source_definitions",
            "targets",
        ]
        for table in tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {table}")

        # Drop sequences
        self.conn.execute("DROP SEQUENCE IF EXISTS seq_lineage_edges_id")

    def _create_schema(self) -> None:
        """Create the database schema tables."""

        # Targets table - stores available connections from profiles.yml
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS targets (
                name VARCHAR PRIMARY KEY,
                adapter_type VARCHAR NOT NULL,
                database VARCHAR,
                schema_name VARCHAR,
                is_default BOOLEAN DEFAULT FALSE,
                host VARCHAR,
                port INTEGER,
                meta JSON,
                last_verified TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Source definitions - stores sources with their connections from manifest
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS source_definitions (
                unique_id VARCHAR PRIMARY KEY,
                source_name VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                connection_name VARCHAR NOT NULL,
                database VARCHAR,
                schema_name VARCHAR,
                adapter_type VARCHAR,
                identifier VARCHAR,
                description TEXT,
                loader VARCHAR,
                meta JSON,
                freshness JSON,
                columns JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Model definitions - stores models with their targets from manifest
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS model_definitions (
                unique_id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                connection_name VARCHAR NOT NULL,
                database VARCHAR,
                schema_name VARCHAR,
                adapter_type VARCHAR,
                materialized VARCHAR,
                description TEXT,
                tags JSON,
                meta JSON,
                config JSON,
                columns JSON,
                depends_on_nodes JSON,
                compiled_sql_hash VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Catalog nodes - enriched catalog for docs visualization
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS catalog_nodes (
                unique_id VARCHAR PRIMARY KEY,
                resource_type VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                schema_name VARCHAR,
                database VARCHAR,
                connection_name VARCHAR,
                adapter_type VARCHAR,
                description TEXT,
                icon_type VARCHAR,
                color_hex VARCHAR,
                materialized VARCHAR,
                tags JSON,
                meta JSON,
                columns JSON,
                row_count BIGINT,
                bytes_stored BIGINT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Lineage edges - DAG lineage for visualization
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_lineage_edges_id START 1;
            CREATE TABLE IF NOT EXISTS lineage_edges (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_lineage_edges_id'),
                source_node_id VARCHAR NOT NULL,
                target_node_id VARCHAR NOT NULL,
                edge_type VARCHAR NOT NULL,
                is_cross_connection BOOLEAN DEFAULT FALSE,
                source_connection VARCHAR,
                target_connection VARCHAR
            )
        """)

        # Create indexes
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_definitions_connection
            ON source_definitions(connection_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_model_definitions_connection
            ON model_definitions(connection_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_catalog_nodes_type
            ON catalog_nodes(resource_type)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_catalog_nodes_connection
            ON catalog_nodes(connection_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lineage_edges_source
            ON lineage_edges(source_node_id)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lineage_edges_target
            ON lineage_edges(target_node_id)
        """)

    # =========================================================================
    # Target Operations
    # =========================================================================

    def save_target(self, target: TargetDefinition) -> None:
        """Save a target definition to the store."""
        self.conn.execute("""
            INSERT OR REPLACE INTO targets
            (name, adapter_type, database, schema_name, is_default,
             host, port, meta, last_verified, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, [
            target.name, target.adapter_type, target.database,
            target.schema_name, target.is_default, target.host,
            target.port, target.meta, target.last_verified
        ])

    def save_targets_batch(self, targets: List[TargetDefinition]) -> None:
        """Save multiple targets in a batch."""
        for target in targets:
            self.save_target(target)

    def get_target(self, name: str) -> Optional[TargetDefinition]:
        """Get a target by name."""
        result = self.conn.execute("""
            SELECT name, adapter_type, database, schema_name, is_default,
                   host, port, meta, last_verified
            FROM targets WHERE name = ?
        """, [name]).fetchone()

        if result:
            return TargetDefinition(
                name=result[0], adapter_type=result[1], database=result[2],
                schema_name=result[3], is_default=result[4], host=result[5],
                port=result[6], meta=result[7], last_verified=result[8]
            )
        return None

    def get_all_targets(self) -> List[TargetDefinition]:
        """Get all targets."""
        results = self.conn.execute("""
            SELECT name, adapter_type, database, schema_name, is_default,
                   host, port, meta, last_verified
            FROM targets ORDER BY is_default DESC, name
        """).fetchall()

        return [
            TargetDefinition(
                name=r[0], adapter_type=r[1], database=r[2],
                schema_name=r[3], is_default=r[4], host=r[5],
                port=r[6], meta=r[7], last_verified=r[8]
            )
            for r in results
        ]

    def get_default_target(self) -> Optional[TargetDefinition]:
        """Get the default target."""
        result = self.conn.execute("""
            SELECT name, adapter_type, database, schema_name, is_default,
                   host, port, meta, last_verified
            FROM targets WHERE is_default = TRUE LIMIT 1
        """).fetchone()

        if result:
            return TargetDefinition(
                name=result[0], adapter_type=result[1], database=result[2],
                schema_name=result[3], is_default=result[4], host=result[5],
                port=result[6], meta=result[7], last_verified=result[8]
            )
        return None

    def clear_targets(self) -> None:
        """Clear all targets."""
        self.conn.execute("DELETE FROM targets")

    # =========================================================================
    # Source Definition Operations
    # =========================================================================

    def save_source_definition(self, source: SourceTableDefinition) -> None:
        """Save a source definition to the store."""
        self.conn.execute("""
            INSERT OR REPLACE INTO source_definitions
            (unique_id, source_name, table_name, connection_name,
             database, schema_name, adapter_type, identifier,
             description, loader, meta, freshness, columns, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, [
            source.unique_id, source.source_name, source.table_name,
            source.connection_name, source.database, source.schema_name,
            source.adapter_type, source.identifier, source.description,
            source.loader, source.meta, source.freshness, source.columns
        ])

    def save_source_definitions_batch(self, sources: List[SourceTableDefinition]) -> None:
        """Save multiple source definitions in a batch."""
        for source in sources:
            self.save_source_definition(source)

    def get_source_definition(self, unique_id: str) -> Optional[SourceTableDefinition]:
        """Get a source definition by unique ID."""
        result = self.conn.execute("""
            SELECT unique_id, source_name, table_name, connection_name,
                   database, schema_name, adapter_type, identifier,
                   description, loader, meta, freshness, columns,
                   created_at, updated_at
            FROM source_definitions WHERE unique_id = ?
        """, [unique_id]).fetchone()

        if result:
            return SourceTableDefinition(
                unique_id=result[0], source_name=result[1], table_name=result[2],
                connection_name=result[3], database=result[4], schema_name=result[5],
                adapter_type=result[6], identifier=result[7], description=result[8],
                loader=result[9], meta=result[10], freshness=result[11],
                columns=result[12], created_at=result[13], updated_at=result[14]
            )
        return None

    def get_sources_by_connection(self, connection_name: str) -> List[SourceTableDefinition]:
        """Get all sources for a specific connection."""
        results = self.conn.execute("""
            SELECT unique_id, source_name, table_name, connection_name,
                   database, schema_name, adapter_type, identifier,
                   description, loader, meta, freshness, columns,
                   created_at, updated_at
            FROM source_definitions
            WHERE connection_name = ?
            ORDER BY source_name, table_name
        """, [connection_name]).fetchall()

        return [
            SourceTableDefinition(
                unique_id=r[0], source_name=r[1], table_name=r[2],
                connection_name=r[3], database=r[4], schema_name=r[5],
                adapter_type=r[6], identifier=r[7], description=r[8],
                loader=r[9], meta=r[10], freshness=r[11],
                columns=r[12], created_at=r[13], updated_at=r[14]
            )
            for r in results
        ]

    def get_all_source_definitions(self) -> List[SourceTableDefinition]:
        """Get all source definitions."""
        results = self.conn.execute("""
            SELECT unique_id, source_name, table_name, connection_name,
                   database, schema_name, adapter_type, identifier,
                   description, loader, meta, freshness, columns,
                   created_at, updated_at
            FROM source_definitions
            ORDER BY source_name, table_name
        """).fetchall()

        return [
            SourceTableDefinition(
                unique_id=r[0], source_name=r[1], table_name=r[2],
                connection_name=r[3], database=r[4], schema_name=r[5],
                adapter_type=r[6], identifier=r[7], description=r[8],
                loader=r[9], meta=r[10], freshness=r[11],
                columns=r[12], created_at=r[13], updated_at=r[14]
            )
            for r in results
        ]

    def clear_source_definitions(self) -> None:
        """Clear all source definitions."""
        self.conn.execute("DELETE FROM source_definitions")

    # =========================================================================
    # Model Definition Operations
    # =========================================================================

    def save_model_definition(self, model: ModelDefinition) -> None:
        """Save a model definition to the store."""
        self.conn.execute("""
            INSERT OR REPLACE INTO model_definitions
            (unique_id, name, connection_name, database, schema_name,
             adapter_type, materialized, description, tags, meta,
             config, columns, depends_on_nodes, compiled_sql_hash, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, [
            model.unique_id, model.name, model.connection_name,
            model.database, model.schema_name, model.adapter_type,
            model.materialized, model.description, model.tags, model.meta,
            model.config, model.columns, model.depends_on_nodes,
            model.compiled_sql_hash
        ])

    def save_model_definitions_batch(self, models: List[ModelDefinition]) -> None:
        """Save multiple model definitions in a batch."""
        for model in models:
            self.save_model_definition(model)

    def get_model_definition(self, unique_id: str) -> Optional[ModelDefinition]:
        """Get a model definition by unique ID."""
        result = self.conn.execute("""
            SELECT unique_id, name, connection_name, database, schema_name,
                   adapter_type, materialized, description, tags, meta,
                   config, columns, depends_on_nodes, compiled_sql_hash,
                   created_at, updated_at
            FROM model_definitions WHERE unique_id = ?
        """, [unique_id]).fetchone()

        if result:
            return ModelDefinition(
                unique_id=result[0], name=result[1], connection_name=result[2],
                database=result[3], schema_name=result[4], adapter_type=result[5],
                materialized=result[6], description=result[7], tags=result[8],
                meta=result[9], config=result[10], columns=result[11],
                depends_on_nodes=result[12], compiled_sql_hash=result[13],
                created_at=result[14], updated_at=result[15]
            )
        return None

    def get_models_by_connection(self, connection_name: str) -> List[ModelDefinition]:
        """Get all models for a specific connection."""
        results = self.conn.execute("""
            SELECT unique_id, name, connection_name, database, schema_name,
                   adapter_type, materialized, description, tags, meta,
                   config, columns, depends_on_nodes, compiled_sql_hash,
                   created_at, updated_at
            FROM model_definitions
            WHERE connection_name = ?
            ORDER BY name
        """, [connection_name]).fetchall()

        return [
            ModelDefinition(
                unique_id=r[0], name=r[1], connection_name=r[2],
                database=r[3], schema_name=r[4], adapter_type=r[5],
                materialized=r[6], description=r[7], tags=r[8],
                meta=r[9], config=r[10], columns=r[11],
                depends_on_nodes=r[12], compiled_sql_hash=r[13],
                created_at=r[14], updated_at=r[15]
            )
            for r in results
        ]

    def get_all_model_definitions(self) -> List[ModelDefinition]:
        """Get all model definitions."""
        results = self.conn.execute("""
            SELECT unique_id, name, connection_name, database, schema_name,
                   adapter_type, materialized, description, tags, meta,
                   config, columns, depends_on_nodes, compiled_sql_hash,
                   created_at, updated_at
            FROM model_definitions
            ORDER BY name
        """).fetchall()

        return [
            ModelDefinition(
                unique_id=r[0], name=r[1], connection_name=r[2],
                database=r[3], schema_name=r[4], adapter_type=r[5],
                materialized=r[6], description=r[7], tags=r[8],
                meta=r[9], config=r[10], columns=r[11],
                depends_on_nodes=r[12], compiled_sql_hash=r[13],
                created_at=r[14], updated_at=r[15]
            )
            for r in results
        ]

    def clear_model_definitions(self) -> None:
        """Clear all model definitions."""
        self.conn.execute("DELETE FROM model_definitions")

    # =========================================================================
    # Catalog Node Operations
    # =========================================================================

    def save_catalog_node(self, node: CatalogNode) -> None:
        """Save a catalog node to the store."""
        self.conn.execute("""
            INSERT OR REPLACE INTO catalog_nodes
            (unique_id, resource_type, name, schema_name, database,
             connection_name, adapter_type, description, icon_type, color_hex,
             materialized, tags, meta, columns, row_count, bytes_stored,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, [
            node.unique_id, node.resource_type, node.name,
            node.schema_name, node.database,
            node.connection_name, node.adapter_type,
            node.description, node.icon_type, node.color_hex,
            node.materialized, node.tags, node.meta, node.columns,
            node.row_count, node.bytes_stored, node.created_at
        ])

    def get_catalog_node(self, unique_id: str) -> Optional[CatalogNode]:
        """Get a catalog node by unique ID."""
        result = self.conn.execute("""
            SELECT unique_id, resource_type, name, schema_name, database,
                   connection_name, adapter_type, description, icon_type, color_hex,
                   materialized, tags, meta, columns, row_count, bytes_stored,
                   created_at, updated_at
            FROM catalog_nodes WHERE unique_id = ?
        """, [unique_id]).fetchone()

        if result:
            return CatalogNode(
                unique_id=result[0], resource_type=result[1], name=result[2],
                schema_name=result[3], database=result[4],
                connection_name=result[5], adapter_type=result[6],
                description=result[7], icon_type=result[8], color_hex=result[9],
                materialized=result[10], tags=result[11], meta=result[12],
                columns=result[13], row_count=result[14], bytes_stored=result[15],
                created_at=result[16], updated_at=result[17]
            )
        return None

    def get_catalog_nodes_by_type(self, resource_type: str) -> List[CatalogNode]:
        """Get all catalog nodes of a specific type."""
        results = self.conn.execute("""
            SELECT unique_id, resource_type, name, schema_name, database,
                   connection_name, adapter_type, description, icon_type, color_hex,
                   materialized, tags, meta, columns, row_count, bytes_stored,
                   created_at, updated_at
            FROM catalog_nodes WHERE resource_type = ? ORDER BY name
        """, [resource_type]).fetchall()

        return [
            CatalogNode(
                unique_id=r[0], resource_type=r[1], name=r[2],
                schema_name=r[3], database=r[4],
                connection_name=r[5], adapter_type=r[6],
                description=r[7], icon_type=r[8], color_hex=r[9],
                materialized=r[10], tags=r[11], meta=r[12],
                columns=r[13], row_count=r[14], bytes_stored=r[15],
                created_at=r[16], updated_at=r[17]
            )
            for r in results
        ]

    def get_catalog_nodes_by_connection(self, connection_name: str) -> List[CatalogNode]:
        """Get all catalog nodes for a specific connection."""
        results = self.conn.execute("""
            SELECT unique_id, resource_type, name, schema_name, database,
                   connection_name, adapter_type, description, icon_type, color_hex,
                   materialized, tags, meta, columns, row_count, bytes_stored,
                   created_at, updated_at
            FROM catalog_nodes WHERE connection_name = ? ORDER BY resource_type, name
        """, [connection_name]).fetchall()

        return [
            CatalogNode(
                unique_id=r[0], resource_type=r[1], name=r[2],
                schema_name=r[3], database=r[4],
                connection_name=r[5], adapter_type=r[6],
                description=r[7], icon_type=r[8], color_hex=r[9],
                materialized=r[10], tags=r[11], meta=r[12],
                columns=r[13], row_count=r[14], bytes_stored=r[15],
                created_at=r[16], updated_at=r[17]
            )
            for r in results
        ]

    def get_all_catalog_nodes(self) -> List[CatalogNode]:
        """Get all catalog nodes."""
        results = self.conn.execute("""
            SELECT unique_id, resource_type, name, schema_name, database,
                   connection_name, adapter_type, description, icon_type, color_hex,
                   materialized, tags, meta, columns, row_count, bytes_stored,
                   created_at, updated_at
            FROM catalog_nodes ORDER BY resource_type, name
        """).fetchall()

        return [
            CatalogNode(
                unique_id=r[0], resource_type=r[1], name=r[2],
                schema_name=r[3], database=r[4],
                connection_name=r[5], adapter_type=r[6],
                description=r[7], icon_type=r[8], color_hex=r[9],
                materialized=r[10], tags=r[11], meta=r[12],
                columns=r[13], row_count=r[14], bytes_stored=r[15],
                created_at=r[16], updated_at=r[17]
            )
            for r in results
        ]

    def clear_catalog_nodes(self) -> None:
        """Clear all catalog nodes."""
        self.conn.execute("DELETE FROM catalog_nodes")

    # =========================================================================
    # Lineage Edge Operations
    # =========================================================================

    def save_lineage_edge(self, edge: LineageEdge) -> int:
        """Save a lineage edge to the store. Returns the edge ID."""
        if edge.id:
            self.conn.execute("""
                INSERT OR REPLACE INTO lineage_edges
                (id, source_node_id, target_node_id, edge_type,
                 is_cross_connection, source_connection, target_connection)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                edge.id, edge.source_node_id, edge.target_node_id, edge.edge_type,
                edge.is_cross_connection, edge.source_connection, edge.target_connection
            ])
            return edge.id
        else:
            result = self.conn.execute("""
                INSERT INTO lineage_edges
                (source_node_id, target_node_id, edge_type,
                 is_cross_connection, source_connection, target_connection)
                VALUES (?, ?, ?, ?, ?, ?)
                RETURNING id
            """, [
                edge.source_node_id, edge.target_node_id, edge.edge_type,
                edge.is_cross_connection, edge.source_connection, edge.target_connection
            ]).fetchone()
            return result[0] if result else 0

    def get_upstream_edges(self, node_id: str) -> List[LineageEdge]:
        """Get all edges where this node is the target (upstream dependencies)."""
        results = self.conn.execute("""
            SELECT id, source_node_id, target_node_id, edge_type,
                   is_cross_connection, source_connection, target_connection
            FROM lineage_edges WHERE target_node_id = ?
        """, [node_id]).fetchall()

        return [
            LineageEdge(
                id=r[0], source_node_id=r[1], target_node_id=r[2],
                edge_type=r[3], is_cross_connection=r[4],
                source_connection=r[5], target_connection=r[6]
            )
            for r in results
        ]

    def get_downstream_edges(self, node_id: str) -> List[LineageEdge]:
        """Get all edges where this node is the source (downstream dependents)."""
        results = self.conn.execute("""
            SELECT id, source_node_id, target_node_id, edge_type,
                   is_cross_connection, source_connection, target_connection
            FROM lineage_edges WHERE source_node_id = ?
        """, [node_id]).fetchall()

        return [
            LineageEdge(
                id=r[0], source_node_id=r[1], target_node_id=r[2],
                edge_type=r[3], is_cross_connection=r[4],
                source_connection=r[5], target_connection=r[6]
            )
            for r in results
        ]

    def get_all_lineage_edges(self) -> List[LineageEdge]:
        """Get all lineage edges."""
        results = self.conn.execute("""
            SELECT id, source_node_id, target_node_id, edge_type,
                   is_cross_connection, source_connection, target_connection
            FROM lineage_edges ORDER BY source_node_id, target_node_id
        """).fetchall()

        return [
            LineageEdge(
                id=r[0], source_node_id=r[1], target_node_id=r[2],
                edge_type=r[3], is_cross_connection=r[4],
                source_connection=r[5], target_connection=r[6]
            )
            for r in results
        ]

    def get_cross_connection_edges(self) -> List[LineageEdge]:
        """Get all edges that cross connection boundaries."""
        results = self.conn.execute("""
            SELECT id, source_node_id, target_node_id, edge_type,
                   is_cross_connection, source_connection, target_connection
            FROM lineage_edges WHERE is_cross_connection = TRUE
            ORDER BY source_node_id, target_node_id
        """).fetchall()

        return [
            LineageEdge(
                id=r[0], source_node_id=r[1], target_node_id=r[2],
                edge_type=r[3], is_cross_connection=r[4],
                source_connection=r[5], target_connection=r[6]
            )
            for r in results
        ]

    def clear_lineage_edges(self) -> None:
        """Clear all lineage edges and reset sequence."""
        self.conn.execute("DELETE FROM lineage_edges")
        # Reset sequence to start fresh
        try:
            self.conn.execute("ALTER SEQUENCE seq_lineage_edges_id RESTART WITH 1")
        except Exception:
            pass  # Sequence might not exist yet

    # =========================================================================
    # Batch Operations
    # =========================================================================

    def clear_all(self) -> None:
        """Clear all catalog data."""
        self.clear_targets()
        self.clear_source_definitions()
        self.clear_model_definitions()
        self.clear_catalog_nodes()
        self.clear_lineage_edges()

    def populate_from_manifest(
        self,
        manifest_data: Dict[str, Any],
        default_target: str,
        targets_info: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Populate the catalog store from manifest data.

        Args:
            manifest_data: Parsed manifest.json data
            default_target: Default target name
            targets_info: Dict of target name -> {adapter_type, database, schema, ...}
        """
        # Clear existing data
        self.clear_source_definitions()
        self.clear_model_definitions()
        self.clear_lineage_edges()

        # Save targets
        self.clear_targets()
        for target_name, target_info in targets_info.items():
            target = TargetDefinition(
                name=target_name,
                adapter_type=target_info.get('type', 'unknown'),
                database=target_info.get('database'),
                schema_name=target_info.get('schema'),
                is_default=(target_name == default_target),
                host=target_info.get('host'),
                port=target_info.get('port'),
            )
            self.save_target(target)

        # Process sources
        for unique_id, source_data in manifest_data.get('sources', {}).items():
            connection = source_data.get('connection') or default_target
            adapter_type = targets_info.get(connection, {}).get('type')

            source = SourceTableDefinition(
                unique_id=unique_id,
                source_name=source_data.get('source_name', ''),
                table_name=source_data.get('name', ''),
                connection_name=connection,
                database=source_data.get('database'),
                schema_name=source_data.get('schema'),
                adapter_type=adapter_type,
                identifier=source_data.get('identifier'),
                description=source_data.get('description'),
                loader=source_data.get('loader'),
                meta=json.dumps(source_data.get('meta')) if source_data.get('meta') else None,
                columns=json.dumps(source_data.get('columns')) if source_data.get('columns') else None,
            )
            self.save_source_definition(source)

        # Process models
        for unique_id, node_data in manifest_data.get('nodes', {}).items():
            if node_data.get('resource_type') != 'model':
                continue

            config = node_data.get('config', {})
            connection = config.get('target') or default_target
            adapter_type = targets_info.get(connection, {}).get('type')

            model = ModelDefinition(
                unique_id=unique_id,
                name=node_data.get('name', ''),
                connection_name=connection,
                database=node_data.get('database'),
                schema_name=node_data.get('schema'),
                adapter_type=adapter_type,
                materialized=config.get('materialized'),
                description=node_data.get('description'),
                tags=json.dumps(list(node_data.get('tags', []))) if node_data.get('tags') else None,
                meta=json.dumps(node_data.get('meta')) if node_data.get('meta') else None,
                config=json.dumps(config) if config else None,
                columns=json.dumps(node_data.get('columns')) if node_data.get('columns') else None,
                depends_on_nodes=json.dumps(node_data.get('depends_on', {}).get('nodes', [])),
            )
            self.save_model_definition(model)

        # Build lineage edges
        node_connections = {}

        # Map sources to connections
        for unique_id, source_data in manifest_data.get('sources', {}).items():
            node_connections[unique_id] = source_data.get('connection') or default_target

        # Map models to connections
        for unique_id, node_data in manifest_data.get('nodes', {}).items():
            if node_data.get('resource_type') == 'model':
                config = node_data.get('config', {})
                node_connections[unique_id] = config.get('target') or default_target

        # Create edges
        for unique_id, node_data in manifest_data.get('nodes', {}).items():
            if node_data.get('resource_type') != 'model':
                continue

            target_connection = node_connections.get(unique_id, default_target)
            depends_on = node_data.get('depends_on', {}).get('nodes', [])

            for dep_id in depends_on:
                source_connection = node_connections.get(dep_id, default_target)

                if dep_id.startswith('source.'):
                    edge_type = 'source'
                elif dep_id.startswith('model.'):
                    edge_type = 'ref'
                else:
                    edge_type = 'depends_on'

                is_cross = source_connection != target_connection

                edge = LineageEdge(
                    source_node_id=dep_id,
                    target_node_id=unique_id,
                    edge_type=edge_type,
                    is_cross_connection=is_cross,
                    source_connection=source_connection,
                    target_connection=target_connection,
                )
                self.save_lineage_edge(edge)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def exists(self) -> bool:
        """Check if the catalog store exists."""
        return self.db_path.exists()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the catalog store."""
        targets_count = self.conn.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
        sources_count = self.conn.execute("SELECT COUNT(*) FROM source_definitions").fetchone()[0]
        models_count = self.conn.execute("SELECT COUNT(*) FROM model_definitions").fetchone()[0]
        catalog_count = self.conn.execute("SELECT COUNT(*) FROM catalog_nodes").fetchone()[0]
        edges_count = self.conn.execute("SELECT COUNT(*) FROM lineage_edges").fetchone()[0]
        cross_edges = self.conn.execute(
            "SELECT COUNT(*) FROM lineage_edges WHERE is_cross_connection = TRUE"
        ).fetchone()[0]

        return {
            "targets": targets_count,
            "sources": sources_count,
            "models": models_count,
            "catalog_nodes": catalog_count,
            "lineage_edges": edges_count,
            "cross_connection_edges": cross_edges,
            "db_path": str(self.db_path),
        }

    def get_federation_summary(self) -> Dict[str, Any]:
        """Get a summary of federation paths in the project."""
        # Group sources by connection
        sources_by_conn = self.conn.execute("""
            SELECT connection_name, COUNT(*) as count
            FROM source_definitions
            GROUP BY connection_name
        """).fetchall()

        # Group models by connection
        models_by_conn = self.conn.execute("""
            SELECT connection_name, COUNT(*) as count
            FROM model_definitions
            GROUP BY connection_name
        """).fetchall()

        # Get cross-connection edge count
        cross_edges = self.conn.execute(
            "SELECT COUNT(*) FROM lineage_edges WHERE is_cross_connection = TRUE"
        ).fetchone()[0]

        return {
            "sources_by_connection": {r[0]: r[1] for r in sources_by_conn},
            "models_by_connection": {r[0]: r[1] for r in models_by_conn},
            "cross_connection_edges": cross_edges,
            "federation_paths_exist": cross_edges > 0,
        }
