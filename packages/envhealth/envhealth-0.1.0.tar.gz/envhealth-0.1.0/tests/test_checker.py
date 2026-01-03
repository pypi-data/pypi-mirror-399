from envhealth import EnvironmentChecker

def test_python_check():
    checker = EnvironmentChecker()
    res = checker.check_python()
    assert "current_version" in checker.results["python"]
    assert res in [True, False]

def test_system_check():
    checker = EnvironmentChecker()
    checker.check_system()
    assert "cpu_count" in checker.results["system"]

def test_gpu_field_exists():
    checker = EnvironmentChecker()
    checker.check_gpu()
    assert "available" in checker.results["gpu"]