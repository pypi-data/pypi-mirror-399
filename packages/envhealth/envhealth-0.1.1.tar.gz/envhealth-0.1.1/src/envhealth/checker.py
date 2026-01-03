import platform
import shutil
import psutil
import socket

from .cuda_check import check_cuda
from .network_check import check_internet, check_proxy


class Checker:
    """
    Core System Checker
    Old features preserved, new features extended
    """

    def basic_system_info(self):
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "hostname": socket.gethostname(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

    def cpu_info(self):
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "cpu_usage_percent": psutil.cpu_percent(interval=1)
        }

    def memory_info(self):
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "used_percent": memory.percent
        }

    def disk_info(self):
        total, used, free = shutil.disk_usage("/")
        return {
            "total_gb": round(total / (1024 ** 3), 2),
            "used_gb": round(used / (1024 ** 3), 2),
            "free_gb": round(free / (1024 ** 3), 2),
            "used_percent": round((used / total) * 100, 2)
        }

    def cuda_performance(self):
        return check_cuda()

    def internet_status(self):
        return check_internet()

    def proxy_status(self):
        return check_proxy()

    def full_report(self):
        return {
            "system": self.basic_system_info(),
            "cpu": self.cpu_info(),
            "memory": self.memory_info(),
            "disk": self.disk_info(),
            "cuda": self.cuda_performance(),
            "internet": self.internet_status(),
            "proxy": self.proxy_status()
        }
