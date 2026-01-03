import json
from .pdf_report import export_pdf


class Reporter:
    def __init__(self, data):
        self.data = data

    def to_json(self):
        return json.dumps(self.data, indent=4)

    def pretty_text(self):
        out = []
        for section, values in self.data.items():
            out.append(f"\n=== {section.upper()} ===")
            for k, v in values.items():
                out.append(f"{k}: {v}")
        return "\n".join(out)

    def to_html(self):
        html = ["<html><body><h1>EnvHealth Report</h1>"]
        for section, values in self.data.items():
            html.append(f"<h2>{section.upper()}</h2><ul>")
            for k, v in values.items():
                html.append(f"<li><b>{k}</b>: {v}</li>")
            html.append("</ul>")
        html.append("</body></html>")
        return "\n".join(html)

    def to_pdf(self, filename="envhealth_report.pdf"):
        export_pdf(self.data, filename)
        return filename
