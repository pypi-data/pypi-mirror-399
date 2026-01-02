import platform

def detect_cpu_features() -> set[str]:
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for l in f:
                    if l.startswith("flags"):
                        return set(l.split(":")[1].split())
        except:
            pass
    return set()

def cpu_summary() -> dict:
    return {
        "os": platform.platform(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "simd": ", ".join(sorted(detect_cpu_features())) or "unknown"
    }
