import uuid
from datetime import datetime

from data_engine.profiling.duckdb_client import DuckDBClient
from evolution.snapshot import ColumnSchema, ColumnStatistics, DatasetSnapshot


class DatasetProfiler:
    """
    Extracts deterministic schemas and statistics using DuckDB.
    """
    def __init__(self, duckdb_client: DuckDBClient):
        self.client = duckdb_client

    def profile_view(self, dataset_id: str, view_name: str) -> DatasetSnapshot:
        """
        Profiles a registered view in DuckDB and returns a snapshot.
        """
        # Extract Schema
        schema_rows = self.client.get_table_schema(view_name)
        
        schema_def = []
        for row in schema_rows:
            col_name = row[0]
            col_type = row[1]
            nullable = row[2] == 'YES'
            
            # Approximate cardinality using hyperloglog
            card_res = self.client.query(
                f"SELECT approx_count_distinct({col_name}) FROM {view_name}"
            ).fetchone()
            cardinality = card_res[0] if card_res else None
            
            schema_def.append(ColumnSchema(
                column=col_name,
                data_type=col_type,
                nullable=nullable,
                cardinality=cardinality
            ))

        # Extract Statistics
        stats = {}
        total_rows_res = self.client.query(f"SELECT count(*) FROM {view_name}").fetchone()
        total_rows = total_rows_res[0] if total_rows_res else 0

        for col in schema_def:
            # We only extract min/max/mean/var for numeric types roughly
            is_numeric = "INT" in col.data_type.upper() or "DOUBLE" in col.data_type.upper() or "FLOAT" in col.data_type.upper()
            
            # Null rate
            null_res = self.client.query(f"SELECT count(*) FROM {view_name} WHERE {col.column} IS NULL").fetchone()
            null_count = null_res[0] if null_res else 0
            null_rate = null_count / total_rows if total_rows > 0 else 0.0

            min_val, max_val, mean_val, var_val = None, None, None, None
            if is_numeric and total_rows > 0:
                stat_query = f"SELECT min({col.column}), max({col.column}), avg({col.column}), var_pop({col.column}) FROM {view_name}"
                stat_res = self.client.query(stat_query).fetchone()
                if stat_res:
                    min_val = stat_res[0]
                    max_val = stat_res[1]
                    mean_val = stat_res[2]
                    var_val = stat_res[3]

            stats[col.column] = ColumnStatistics(
                null_rate=null_rate,
                min=min_val,
                max=max_val,
                mean=mean_val,
                variance=var_val
            )

        return DatasetSnapshot(
            dataset_id=dataset_id,
            snapshot_id=str(uuid.uuid4()),
            captured_at=datetime.utcnow(),
            schema_def=schema_def,
            statistics=stats
        )
