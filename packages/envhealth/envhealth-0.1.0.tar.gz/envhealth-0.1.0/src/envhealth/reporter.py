import json
from datetime import datetime
from colorama import Fore, Style


class ConsoleReporter:
    def render(self, results):
        print(Fore.CYAN + "\n=== PYTHON ENVIRONMENT HEALTH REPORT ===" + Style.RESET_ALL)
        print("Generated:", datetime.now())
        print("----------------------------------------")

        print(Fore.YELLOW + "\nPython:" + Style.RESET_ALL)
        for k, v in results["python"].items():
            print(f"  {k}: {v}")

        print(Fore.YELLOW + "\nSystem:" + Style.RESET_ALL)
        for k, v in results["system"].items():
            print(f"  {k}: {v}")

        print(Fore.YELLOW + "\nGPU:" + Style.RESET_ALL)
        print("  Available:", results["gpu"]["available"])
        if results["gpu"].get("devices"):
            for gpu in results["gpu"]["devices"]:
                print(f"  {gpu}")

        print(Fore.YELLOW + "\nDependency Conflicts:" + Style.RESET_ALL)
        print(results["dependencies"].get("conflicts") or "None")

        print(Fore.RED + "\nWarnings:" + Style.RESET_ALL)
        if results["warnings"]:
            for w in results["warnings"]:
                print(" -", w)
        else:
            print(" None")


class HTMLReporter:
    def save(self, results, path="env_report.html"):
        html = f"""
<html>
<head><title>Environment Health Report</title></head>
<body>
<h1>Environment Health Report</h1>
<pre>{json.dumps(results, indent=4)}</pre>
</body>
</html>
"""
        with open(path, "w") as f:
            f.write(html)
        return path


class JSONReporter:
    def save(self, results, path="env_report.json"):
        with open(path, "w") as f:
            json.dump(results, f, indent=4)
        return path


class MarkdownReporter:
    def save(self, results, path="env_report.md"):
        md = "# Environment Health Report\n\n"
        md += f"Generated: {datetime.now()}\n\n"
        md += "## Python\n"
        for k, v in results["python"].items():
            md += f"- **{k}**: {v}\n"

        md += "\n## System\n"
        for k, v in results["system"].items():
            md += f"- **{k}**: {v}\n"

        md += "\n## GPU\n"
        md += f"- Available: {results['gpu']['available']}\n"

        md += "\n## Warnings\n"
        if results["warnings"]:
            for w in results["warnings"]:
                md += f"- {w}\n"
        else:
            md += "None\n"

        with open(path, "w") as f:
            f.write(md)

        return path
