# bot/commands/pi_status.py
import subprocess


def handle_pi_status(_: list[str]) -> str:
    temp = get_cpu_temp()
    mem = get_memory_usage()
    cpu = get_cpu_usage()
    return f"Temp:{temp} Mem:{mem} CPU:{cpu}"


def get_cpu_temp() -> str:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_c = int(f.read().strip()) / 1000
            return f"{temp_c:.1f}C"
    except Exception:
        return "N/A"


def get_memory_usage() -> str:
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem_info = {}
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().split()[0]
                mem_info[key] = int(val)
        total = mem_info.get("MemTotal", 0)
        available = mem_info.get("MemAvailable", 0)
        if total > 0:
            used_pct = ((total - available) / total) * 100
            return f"{used_pct:.0f}%"
        return "N/A"
    except Exception:
        return "N/A"


def get_cpu_usage() -> str:
    try:
        result = subprocess.run(
            ["grep", "cpu ", "/proc/stat"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        fields = result.stdout.strip().split()
        idle = int(fields[4])
        total = sum(int(x) for x in fields[1:])
        usage = ((total - idle) / total) * 100
        return f"{usage:.0f}%"
    except Exception:
        return "N/A"
