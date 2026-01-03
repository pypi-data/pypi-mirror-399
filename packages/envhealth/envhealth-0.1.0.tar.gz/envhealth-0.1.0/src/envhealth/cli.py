import argparse
from .checker import EnvironmentChecker
from .reporter import (
    ConsoleReporter,
    HTMLReporter,
    JSONReporter,
    MarkdownReporter,
)


def main():
    parser = argparse.ArgumentParser(description="Environment Health Checker")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    parser.add_argument("--markdown", action="store_true", help="Generate Markdown report")
    args = parser.parse_args()

    checker = EnvironmentChecker()
    results = checker.run_all()

    ConsoleReporter().render(results)

    if args.html:
        path = HTMLReporter().save(results)
        print(f"\nHTML report saved at: {path}")

    if args.json:
        path = JSONReporter().save(results)
        print(f"JSON report saved at: {path}")

    if args.markdown:
        path = MarkdownReporter().save(results)
        print(f"Markdown report saved at: {path}")
