# envhealth

[![Downloads](https://img.shields.io/pypi/dm/envhealth.svg)](https://pypi.org/project/envhealth/)
[![Python Versions](https://img.shields.io/pypi/pyversions/envhealth.svg)](https://pypi.org/project/envhealth/)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/envhealth.svg)](LICENSE)


EnvHealth is a powerful Python utility to check **system environment health**.
---

## Features
- Operating System details  
- CPU usage and core stats  
- RAM usage  
- Disk usage  
- CUDA GPU availability + performance benchmark  
- Internet connection diagnostics  
- Proxy configuration detection

Supports multiple report formats:

- Pretty terminal output
- JSON
- HTML
- PDF


---

## Installation
You can install envhealth via pip:
```python
pip install envhealth
```

# Usage
## CLI Usage
- Run the environment checker in the console:
    ```python
        envhealth
    ```
- Generate HTML, JSON, or Markdown reports:
    ```python
        envhealth --html
        envhealth --json
        envhealth --pdf
    ```

## Programatic Usage
- Use ``envhealth`` in your Python scripts:
    ```python
    from envhealth import Checker, Reporter

    chk = Checker()
    data = chk.full_report()

    rep = Reporter(data)
    print(rep.pretty_text())
    rep.to_pdf()

    ```
# Sample Output
## Console Output
```yaml
    === SYSTEM ===
    os: Windows
    os_version: 10.0.19045
    hostname: PC
    architecture: AMD64
    processor: Intel(R) Core(TM) i5
    python_version: 3.11

    === CPU ===
    physical_cores: 4
    total_cores: 8
    cpu_usage_percent: 12.5

    === MEMORY ===
    total_gb: 16.0
    available_gb: 9.1
    used_percent: 43

    === DISK ===
    total_gb: 512
    used_gb: 320
    free_gb: 192
    used_percent: 62.5

    === CUDA ===
    cuda_available: True
    gpu_name: NVIDIA RTX 3060
    benchmark_time_sec: 0.1182

    === INTERNET ===
    connected: True
    status_code: 200

    === PROXY ===
    proxy_enabled: False

```
## JSON Output
```json
    {
    "system": {
        "os": "Windows",
        "hostname": "PC"
    },
    "cpu": {
        "physical_cores": 4,
        "cpu_usage_percent": 11.3
    },
    "cuda": {
        "cuda_available": true,
        "gpu_name": "RTX 3060"
    },
    "internet": {
        "connected": true
    }
    }

```
## HTML Output
Produces file ```envhealth_report.html``` which contains
```html
    <h1>EnvHealth Report</h1>
    <h2>SYSTEM</h2>
    <li><b>os</b>: Windows</li>
    <li><b>hostname</b>: PC</li>
    ...

```
# Support
Supported Platforms: 
* Windows
* Linux
* macOS

# TODO
- [ ] Roadmap
- [ ] CUDA performance check
- [ ] Internet & proxy diagnostics
- [ ] PDF export
- [ ] GUI dashboard / VS Code integration

## License
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)


## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## ⭐ Support
If you find this useful, please star the repository.