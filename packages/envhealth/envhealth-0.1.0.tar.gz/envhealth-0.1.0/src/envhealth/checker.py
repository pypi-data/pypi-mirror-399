import platform
import subprocess
import sys
import psutil
from packaging import version


class EnvironmentChecker:
    def __init__(self):
        self.results = {
            "python": {},
            "dependencies": {},
            "system": {},
            "gpu": {},
            "warnings": []
        }

    def check_python(self, min_version="3.8"):
        current = platform.python_version()
        ok = version.parse(current) >= version.parse(min_version)

        self.results["python"] = {
            "current_version": current,
            "minimum_required": min_version,
            "status": "OK" if ok else "FAIL"
        }

        if not ok:
            self.results["warnings"].append(
                f"Python version {current} is below recommended {min_version}"
            )

        return ok

    def check_dependencies(self):
        try:
            conflicts = subprocess.check_output(
                [sys.executable, "-m", "pip", "check"],
                text=True
            )

            if conflicts.strip():
                self.results["dependencies"]["conflicts"] = conflicts.strip()
                self.results["warnings"].append("Package conflicts detected")
            else:
                self.results["dependencies"]["conflicts"] = None

        except Exception as e:
            self.results["dependencies"]["error"] = str(e)

    def check_system(self):
        cpu_count = psutil.cpu_count()
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)

        self.results["system"] = {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu_count": cpu_count,
            "ram_gb": ram_gb,
        }

        if ram_gb < 4:
            self.results["warnings"].append("System RAM is below 4GB")

    def check_gpu(self):
        try:
            result = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                text=True
            )
            gpus = []
            for line in result.strip().split("\n"):
                name, memory = line.split(",")
                gpus.append({"name": name.strip(), "memory": memory.strip()})

            self.results["gpu"]["available"] = True
            self.results["gpu"]["devices"] = gpus

        except Exception:
            self.results["gpu"]["available"] = False

    def run_all(self):
        self.check_python()
        self.check_dependencies()
        self.check_system()
        self.check_gpu()
        return self.results
