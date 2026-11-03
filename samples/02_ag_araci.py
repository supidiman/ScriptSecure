import subprocess
import sys


def check_host(host: str) -> str:
    """Sunucunun erisilebilir olup olmadigini kontrol eder."""
    result = subprocess.run(f"ping -c 2 {host}", shell=True, capture_output=True, text=True)
    return result.stdout


if __name__ == "__main__":
    print(check_host(sys.argv[1]))
