import click
from pyspark.sql import SparkSession


@click.group()
def cli():
    """Delta Lake Utilities CLI"""
    pass


@cli.command()
@click.argument('table_path')
def optimize(table_path):
    """Optimize Delta table"""
    from delta_utils import DeltaOptimizer
    
    spark = SparkSession.builder.appName("DeltaOptimizer").getOrCreate()
    optimizer = DeltaOptimizer(spark)
    result = optimizer.auto_optimize(table_path)
    
    click.echo(f"\nOptimization complete!")
    click.echo(f"Files: {result.files_before} -> {result.files_after}")


@cli.command()
@click.argument('table_path')
def health(table_path):
    """Check Delta table health"""
    from delta_utils import DeltaHealthChecker
    
    spark = SparkSession.builder.appName("DeltaHealthChecker").getOrCreate()
    checker = DeltaHealthChecker(spark)
    report = checker.check_table(table_path)
    
    checker.print_report(report)


if __name__ == '__main__':
    cli()
