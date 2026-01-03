from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class HealthIssue:
    severity: HealthStatus
    category: str
    message: str
    recommendation: str
    metric_value: Any


class DeltaHealthChecker:
    """Comprehensive Delta Lake table health diagnostics"""
    
    SMALL_FILE_THRESHOLD_MB = 10
    SMALL_FILE_COUNT_WARNING = 100
    SMALL_FILE_COUNT_CRITICAL = 500
    
    def __init__(self, spark: SparkSession, verbose: bool = True):
        self.spark = spark
        self.verbose = verbose
    
    def check_table(self, table_path: str) -> Dict[str, Any]:
        """Run comprehensive health check"""
        issues = []
        
        # Check small files
        small_files_issue = self._check_small_files(table_path)
        if small_files_issue:
            issues.append(small_files_issue)
        
        # Calculate overall status
        if not issues:
            overall_status = HealthStatus.HEALTHY
            score = 100
        elif any(i.severity == HealthStatus.CRITICAL for i in issues):
            overall_status = HealthStatus.CRITICAL
            score = 30
        else:
            overall_status = HealthStatus.WARNING
            score = 60
        
        return {
            'overall_status': overall_status,
            'score': score,
            'issues': issues,
            'num_issues': len(issues),
            'table_path': table_path
        }
    
    def _check_small_files(self, table_path: str) -> Optional[HealthIssue]:
        """Check for excessive small files"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(CASE WHEN size < {self.SMALL_FILE_THRESHOLD_MB * 1024 * 1024} 
                        THEN 1 ELSE 0 END) as small_files
                FROM delta.`{table_path}`
            """
            stats = self.spark.sql(query).collect()[0]
            
            small_count = stats['small_files']
            
            if small_count >= self.SMALL_FILE_COUNT_CRITICAL:
                return HealthIssue(
                    severity=HealthStatus.CRITICAL,
                    category="Small Files",
                    message=f"{small_count:,} files smaller than {self.SMALL_FILE_THRESHOLD_MB}MB",
                    recommendation="Run OPTIMIZE to consolidate files",
                    metric_value=small_count
                )
            elif small_count >= self.SMALL_FILE_COUNT_WARNING:
                return HealthIssue(
                    severity=HealthStatus.WARNING,
                    category="Small Files",
                    message=f"{small_count:,} small files detected",
                    recommendation="Consider running OPTIMIZE",
                    metric_value=small_count
                )
            return None
        except Exception as e:
            if self.verbose:
                print(f"Error checking small files: {str(e)}")
            return None
    
    def print_report(self, health_report: Dict[str, Any]):
        """Print formatted health report"""
        print("\n" + "=" * 70)
        print("DELTA TABLE HEALTH REPORT")
        print("=" * 70)
        print(f"Table: {health_report['table_path']}")
        print(f"Overall Status: {health_report['overall_status'].value}")
        print(f"Health Score: {health_report['score']}/100")
        print("=" * 70)
        
        if not health_report['issues']:
            print("\nNo issues detected. Table is healthy.")
        else:
            print(f"\nIssues Found: {health_report['num_issues']}\n")
            for i, issue in enumerate(health_report['issues'], 1):
                print(f"{i}. [{issue.severity.value}] {issue.category}")
                print(f"   Problem: {issue.message}")
                print(f"   Fix: {issue.recommendation}\n")
