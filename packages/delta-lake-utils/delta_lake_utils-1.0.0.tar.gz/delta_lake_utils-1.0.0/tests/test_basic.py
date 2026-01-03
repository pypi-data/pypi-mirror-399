"""Basic tests for delta-lake-utils"""


def test_import():
    """Test that package can be imported"""
    from delta_utils import DeltaOptimizer, DeltaHealthChecker
    assert DeltaOptimizer is not None
    assert DeltaHealthChecker is not None


def test_version():
    """Test version is defined"""
    import delta_utils
    assert hasattr(delta_utils, '__version__')
    assert delta_utils.__version__ == "1.0.0"
