from pyspark.sql import SparkSession
from delta.tables import DeltaTable
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class OptimizationResult:
    """Results from optimization operation"""
    table_name: str
    files_before: int
    files_after: int
    size_before_mb: float
    size_after_mb: float
    duration_seconds: float
    zorder_columns: Optional[List[str]]
    recommendations: List[str]
    files_removed: int
    compression_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeltaOptimizer:
    """Smart Delta Lake table optimizer with auto-tuning capabilities"""
    
    DEFAULT_TARGET_FILE_SIZE_MB = 128
    MIN_FILE_SIZE_MB = 10
    MAX_ZORDER_COLUMNS = 3
    
    def __init__(
        self, 
        spark: SparkSession, 
        target_file_size_mb: int = DEFAULT_TARGET_FILE_SIZE_MB,
        verbose: bool = True
    ):
        self.spark = spark
        self.target_file_size_mb = target_file_size_mb
        self.verbose = verbose
        
    def _log(self, message: str):
        if self.verbose:
            print(message)
    
    def analyze_table(self, table_path: str) -> Dict[str, Any]:
        """Analyze table structure and file statistics"""
        delta_table = DeltaTable.forPath(self.spark, table_path)
        detail = delta_table.detail().collect()[0]
        
        file_stats_query = f"""
            SELECT 
                COUNT(*) as num_files,
                SUM(size) as total_bytes,
                AVG(size) as avg_bytes,
                MIN(size) as min_bytes,
                MAX(size) as max_bytes,
                STDDEV(size) as stddev_bytes
            FROM delta.`{table_path}`
        """
        
        stats = self.spark.sql(file_stats_query).collect()[0]
        
        return {
            'num_files': stats['num_files'],
            'total_size_mb': stats['total_bytes'] / (1024 * 1024) if stats['total_bytes'] else 0,
            'avg_file_size_mb': stats['avg_bytes'] / (1024 * 1024) if stats['avg_bytes'] else 0,
            'min_file_size_mb': stats['min_bytes'] / (1024 * 1024) if stats['min_bytes'] else 0,
            'max_file_size_mb': stats['max_bytes'] / (1024 * 1024) if stats['max_bytes'] else 0,
            'stddev_file_size_mb': stats['stddev_bytes'] / (1024 * 1024) if stats['stddev_bytes'] else 0,
            'partition_columns': detail.get('partitionColumns', [])
        }
    
    def recommend_zorder_columns(
        self, 
        table_path: str, 
        max_columns: int = MAX_ZORDER_COLUMNS
    ) -> List[str]:
        """Recommend Z-ORDER columns based on column characteristics"""
        df = self.spark.read.format("delta").load(table_path)
        total_count = df.count()
        
        if total_count == 0:
            return []
        
        recommendations = []
        unsuitable_types = ['binary', 'array', 'map', 'struct']
        
        for field in df.schema.fields:
            col_name = field.name
            col_type = field.dataType.typeName()
            
            if col_type in unsuitable_types:
                continue
            
            distinct_count = df.select(col_name).distinct().count()
            cardinality_ratio = distinct_count / total_count
            
            if 0.1 <= cardinality_ratio <= 0.8:
                score = 1 - abs(cardinality_ratio - 0.5) / 0.5
                recommendations.append({
                    'column': col_name,
                    'score': score
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return [r['column'] for r in recommendations[:max_columns]]
    
    def auto_optimize(
        self, 
        table_path: str, 
        zorder_columns: Optional[List[str]] = None,
        auto_zorder: bool = True,
        dry_run: bool = False,
        force: bool = False
    ) -> OptimizationResult:
        """Optimize Delta table with intelligent defaults"""
        self._log(f"Analyzing table: {table_path}")
        start_time = time.time()
        
        before_stats = self.analyze_table(table_path)
        
        self._log(f"Current state:")
        self._log(f"  Files: {before_stats['num_files']:,}")
        self._log(f"  Total size: {before_stats['total_size_mb']:.2f} MB")
        self._log(f"  Average file size: {before_stats['avg_file_size_mb']:.2f} MB")
        
        reasons = []
        if before_stats['num_files'] > 100:
            reasons.append(f"High file count: {before_stats['num_files']} files")
        
        if before_stats['avg_file_size_mb'] < self.target_file_size_mb * 0.5:
            reasons.append(f"Small files detected: avg {before_stats['avg_file_size_mb']:.1f}MB")
        
        if auto_zorder and zorder_columns is None:
            self._log("\nAnalyzing columns for Z-ORDER...")
            zorder_columns = self.recommend_zorder_columns(table_path)
            if zorder_columns:
                self._log(f"  Recommended: {', '.join(zorder_columns)}")
        
        if dry_run:
            self._log("\nDry run mode - no changes made")
            return OptimizationResult(
                table_name=table_path,
                files_before=before_stats['num_files'],
                files_after=before_stats['num_files'],
                size_before_mb=before_stats['total_size_mb'],
                size_after_mb=before_stats['total_size_mb'],
                duration_seconds=time.time() - start_time,
                zorder_columns=zorder_columns,
                recommendations=reasons,
                files_removed=0,
                compression_ratio=1.0
            )
        
        self._log("\nExecuting OPTIMIZE...")
        delta_table = DeltaTable.forPath(self.spark, table_path)
        
        if zorder_columns:
            self._log(f"  Z-ORDER by: {', '.join(zorder_columns)}")
            delta_table.optimize().executeZOrderBy(zorder_columns)
        else:
            delta_table.optimize().executeCompaction()
        
        after_stats = self.analyze_table(table_path)
        duration = time.time() - start_time
        files_removed = before_stats['num_files'] - after_stats['num_files']
        
        self._log("\nOptimization complete:")
        self._log(f"  Files: {before_stats['num_files']:,} -> {after_stats['num_files']:,}")
        self._log(f"  Duration: {duration:.1f} seconds")
        
        return OptimizationResult(
            table_name=table_path,
            files_before=before_stats['num_files'],
            files_after=after_stats['num_files'],
            size_before_mb=before_stats['total_size_mb'],
            size_after_mb=after_stats['total_size_mb'],
            duration_seconds=duration,
            zorder_columns=zorder_columns,
            recommendations=reasons,
            files_removed=files_removed,
            compression_ratio=before_stats['total_size_mb'] / after_stats['total_size_mb'] if after_stats['total_size_mb'] > 0 else 1.0
        )
    
    def batch_optimize(self, table_paths: List[str], **kwargs) -> List[OptimizationResult]:
        """Optimize multiple tables"""
        results = []
        for i, table_path in enumerate(table_paths, 1):
            self._log(f"\n[{i}/{len(table_paths)}] Processing: {table_path}")
            try:
                result = self.auto_optimize(table_path, **kwargs)
                results.append(result)
            except Exception as e:
                self._log(f"Error: {str(e)}")
        return results
