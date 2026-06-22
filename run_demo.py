import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def start_process(command):
    return subprocess.Popen(command, cwd=BASE_DIR)


def main():
    streamlit = start_process(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ]
    )
    portal = start_process([sys.executable, "portal.py"])

    print("DecisionCore DSS demo is running.")
    print("Login:     http://localhost:5000")
    print("Dashboard: http://localhost:8501")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            if streamlit.poll() is not None:
                raise RuntimeError("Streamlit server stopped unexpectedly.")
            if portal.poll() is not None:
                raise RuntimeError("Login portal stopped unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        for process in (streamlit, portal):
            if process.poll() is None:
                process.terminate()


if __name__ == "__main__":
    main()
