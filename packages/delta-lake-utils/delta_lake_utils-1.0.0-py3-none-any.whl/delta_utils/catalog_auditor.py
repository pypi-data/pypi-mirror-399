from pyspark.sql import SparkSession
from typing import Dict, List
import pandas as pd


class CatalogAuditor:
    """Audit Unity Catalog permissions"""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def list_catalogs(self) -> pd.DataFrame:
        """List all catalogs"""
        return self.spark.sql("SHOW CATALOGS").toPandas()
    
    def list_schemas(self, catalog: str) -> pd.DataFrame:
        """List schemas in a catalog"""
        return self.spark.sql(f"SHOW SCHEMAS IN {catalog}").toPandas()
    
    def get_table_permissions(
        self, 
        catalog: str, 
        schema: str, 
        table: str
    ) -> pd.DataFrame:
        """Get permissions for a table"""
        try:
            return self.spark.sql(
                f"SHOW GRANTS ON TABLE {catalog}.{schema}.{table}"
            ).toPandas()
        except Exception as e:
            print(f"Error getting permissions: {str(e)}")
            return pd.DataFrame()
