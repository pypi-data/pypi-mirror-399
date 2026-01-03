import argparse
from .checker import Checker
from .reporter import Reporter


def main():
    parser = argparse.ArgumentParser(description="EnvHealth System Diagnostics")

    parser.add_argument("--json", action="store_true", help="Output report in JSON")
    parser.add_argument("--html", action="store_true", help="Output report in HTML format")
    parser.add_argument("--pdf", action="store_true", help="Export report as PDF")

    args = parser.parse_args()

    chk = Checker()
    data = chk.full_report()
    rep = Reporter(data)

    if args.json:
        print(rep.to_json())
        return

    if args.html:
        html = rep.to_html()
        fname = "envhealth_report.html"
        with open(fname, "w") as f:
            f.write(html)
        print(f"HTML report generated: {fname}")
        return

    if args.pdf:
        fname = rep.to_pdf()
        print(f"PDF report generated: {fname}")
        return

    print(rep.pretty_text())
