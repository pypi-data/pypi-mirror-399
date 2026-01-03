from envhealth import Checker


def test_full_report_structure():
    chk = Checker()
    report = chk.full_report()

    assert "system" in report
    assert "cpu" in report
    assert "memory" in report
    assert "disk" in report
    assert "cuda" in report
    assert "internet" in report
    assert "proxy" in report
