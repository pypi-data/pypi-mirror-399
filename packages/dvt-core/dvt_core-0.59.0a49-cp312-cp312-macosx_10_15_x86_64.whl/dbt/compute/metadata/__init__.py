# =============================================================================
# DVT Metadata Layer
# =============================================================================
# DVT uses TWO DuckDB databases in <project>/.dvt/ directory:
#
# 1. metastore.duckdb - Runtime/operational data
#    - column_metadata: Schema info from federated runs
#    - row_counts: Cached row counts from dvt snap
#    - profile_results: Data profiling from dvt profile
#
# 2. catalog.duckdb - Project catalog (federation-aware)
#    - targets: Available connections from profiles.yml
#    - source_definitions: Sources with connections from manifest
#    - model_definitions: Models with targets from manifest
#    - catalog_nodes: Enriched catalog for docs visualization
#    - lineage_edges: DAG lineage for visualization
#
# This separation ensures catalog operations don't interfere with
# runtime operations like profiling, run, build, etc.
#
# DVT v0.54.0: Initial implementation
# DVT v0.55.0: Added AdaptersRegistry for shipped registry database
# DVT v0.56.0: Added profile_results, catalog_nodes, lineage_edges tables
# DVT v0.59.0: Separated into metastore.duckdb and catalog.duckdb
# =============================================================================

from dbt.compute.metadata.store import (
    ProjectMetadataStore,
    ColumnMetadata,
    TableMetadata,
    RowCountInfo,
    ColumnProfileResult,
)
from dbt.compute.metadata.catalog_store import (
    CatalogStore,
    TargetDefinition,
    SourceTableDefinition,
    ModelDefinition,
    CatalogNode,
    LineageEdge,
)
from dbt.compute.metadata.registry import TypeRegistry, SyntaxRegistry
from dbt.compute.metadata.adapters_registry import AdaptersRegistry

__all__ = [
    # Metastore (runtime data)
    "ProjectMetadataStore",
    "ColumnMetadata",
    "TableMetadata",
    "RowCountInfo",
    "ColumnProfileResult",
    # Catalog store (project catalog)
    "CatalogStore",
    "TargetDefinition",
    "SourceTableDefinition",
    "ModelDefinition",
    "CatalogNode",
    "LineageEdge",
    # Registries
    "TypeRegistry",
    "SyntaxRegistry",
    "AdaptersRegistry",
]
