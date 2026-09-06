import logging

import duckdb

logger = logging.getLogger(__name__)

class DuckDBClient:
    """
    Manages connections and analytical queries against the Parquet Data Lake.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path)
        
    def register_parquet_view(self, view_name: str, parquet_glob: str) -> None:
        """
        Registers a view over a collection of Parquet files.
        parquet_glob e.g.: 'datasets/raw/match_events/**/*.parquet'
        """
        try:
            query = (
                f"CREATE OR REPLACE VIEW {view_name} "
                f"AS SELECT * FROM read_parquet('{parquet_glob}', hive_partitioning=true)"
            )
            self.conn.execute(query)
            logger.info(f"Registered view {view_name} for {parquet_glob}")
        except Exception as e:
            logger.error(f"Failed to register view {view_name}: {e}")
            raise

    def query(self, sql: str):
        """
        Executes a SQL query and returns a DuckDB relation.
        To get a pandas dataframe, call .df() on the result.
        """
        return self.conn.execute(sql)

    def get_table_schema(self, table_or_view: str):
        """
        Returns the schema of the registered table or view.
        """
        return self.conn.execute(f"DESCRIBE {table_or_view}").fetchall()
        
    def close(self):
        self.conn.close()
