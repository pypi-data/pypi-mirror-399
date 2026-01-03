from pyspark.sql import SparkSession, DataFrame
from delta.tables import DeltaTable
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import time


@dataclass
class ProfileResult:
    """Results from performance profiling"""
    operation_name: str
    duration_seconds: float
    rows_processed: int
    bytes_processed: int
    throughput_rows_per_sec: float
    throughput_mb_per_sec: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeltaProfiler:
    """Performance profiling for Delta Lake operations"""
    
    def __init__(self, spark: SparkSession, verbose: bool = True):
        self.spark = spark
        self.verbose = verbose
        self.results: List[ProfileResult] = []
    
    def profile_read(
        self, 
        table_path: str, 
        filter_expr: str = None
    ) -> ProfileResult:
        """Profile read operation performance"""
        start_time = time.time()
        
        df = self.spark.read.format("delta").load(table_path)
        
        if filter_expr:
            df = df.filter(filter_expr)
        
        row_count = df.count()
        duration = time.time() - start_time
        
        delta_table = DeltaTable.forPath(self.spark, table_path)
        detail = delta_table.detail().collect()[0]
        total_bytes = detail.get('sizeInBytes', 0)
        
        throughput_rows = row_count / duration if duration > 0 else 0
        throughput_mb = (total_bytes / 1024 / 1024) / duration if duration > 0 else 0
        
        result = ProfileResult(
            operation_name=f"read:{table_path}",
            duration_seconds=duration,
            rows_processed=row_count,
            bytes_processed=total_bytes,
            throughput_rows_per_sec=throughput_rows,
            throughput_mb_per_sec=throughput_mb
        )
        
        self.results.append(result)
        
        if self.verbose:
            print(f"\nProfiling Results:")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Rows: {row_count:,}")
            print(f"  Throughput: {throughput_rows:,.0f} rows/sec")
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all profiling results"""
        if not self.results:
            return {"message": "No profiling results available"}
        
        total_duration = sum(r.duration_seconds for r in self.results)
        total_rows = sum(r.rows_processed for r in self.results)
        
        return {
            'num_operations': len(self.results),
            'total_duration_seconds': total_duration,
            'total_rows_processed': total_rows,
            'operations': [r.to_dict() for r in self.results]
        }
    
    def clear_results(self):
        """Clear all stored profiling results"""
        self.results.clear()
