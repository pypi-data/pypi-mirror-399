import os
from typing import Dict, Optional


class MedallionGenerator:
    """Generate medallion architecture boilerplate code"""
    
    BRONZE_TEMPLATE = '''# Bronze Layer - {table_name}
# Raw data ingestion

from pyspark.sql import functions as F

source_path = "{source_path}"
bronze_path = "{bronze_path}"

df = spark.read.format("{source_format}").load(source_path)

bronze_df = df.withColumn("_ingestion_timestamp", F.current_timestamp())

bronze_df.write.format("delta").mode("append").save(bronze_path)
'''
    
    def __init__(self, base_path: str):
        self.base_path = base_path.rstrip('/')
    
    def generate_layer(
        self,
        table_name: str,
        layer: str,
        source_path: Optional[str] = None,
        source_format: str = "json",
        output_dir: str = "./notebooks"
    ) -> str:
        """Generate notebook for a specific layer"""
        layer = layer.lower()
        
        if layer not in ['bronze', 'silver', 'gold']:
            raise ValueError(f"Invalid layer: {layer}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        bronze_path = f"{self.base_path}/bronze/{table_name}"
        
        if layer == 'bronze':
            template = self.BRONZE_TEMPLATE
            context = {
                'table_name': table_name,
                'source_path': source_path or '/mnt/source/data',
                'bronze_path': bronze_path,
                'source_format': source_format
            }
        else:
            template = f"# {layer.capitalize()} Layer - {table_name}\n"
            context = {'table_name': table_name}
        
        notebook_content = template.format(**context)
        
        output_path = os.path.join(output_dir, f"{table_name}_{layer}.py")
        with open(output_path, 'w') as f:
            f.write(notebook_content)
        
        return output_path
    
    def generate_full_pipeline(
        self,
        table_name: str,
        source_path: Optional[str] = None,
        source_format: str = "json",
        output_dir: str = "./notebooks"
    ) -> Dict[str, str]:
        """Generate complete medallion pipeline"""
        notebooks = {}
        
        for layer in ['bronze', 'silver', 'gold']:
            path = self.generate_layer(
                table_name=table_name,
                layer=layer,
                source_path=source_path,
                source_format=source_format,
                output_dir=output_dir
            )
            notebooks[layer] = path
        
        print(f"\nGenerated medallion pipeline for '{table_name}':")
        for layer, path in notebooks.items():
            print(f"  {layer}: {path}")
        
        return notebooks
