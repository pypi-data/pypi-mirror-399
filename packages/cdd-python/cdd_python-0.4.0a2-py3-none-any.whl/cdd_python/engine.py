import subprocess
import platform
from pathlib import Path


class CDDEngine:
    def __init__(self):
        self.bin_path = Path(__file__).parent / "bin"

    def execute_audit(self, target_url: str):
        system = platform.system().lower()
        if system == "windows":
            binary = "cdd-core-win.exe"
        elif system == "darwin":
            binary = "cdd-core-macos"
        else:
            binary = "cdd-core-linux"

        binary_path = self.bin_path / binary

        print(f"🛡️ Launching CDD Python Attack on: {target_url}")
        try:
            subprocess.run(
                [str(binary_path), target_url],
                capture_output=False,  # Pour voir le tableau en direct
                text=True,
            )
        except Exception as e:
            print(f"Execution failed: {e}")


if __name__ == "__main__":
    engine = CDDEngine()
    engine.execute_audit("http://localhost:8000")
