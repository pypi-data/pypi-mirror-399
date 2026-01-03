from envhealth import Checker, Reporter


def test_reporter_outputs():
    chk = Checker()
    data = chk.full_report()

    rep = Reporter(data)

    assert isinstance(rep.pretty_text(), str)
    assert isinstance(rep.to_json(), str)
    assert "<html>" in rep.to_html()
