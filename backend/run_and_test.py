import sys
import time
import subprocess
from pathlib import Path

# Enable UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("Launching Uvicorn server in background...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait for server to bind port and respond to health check
        print("Waiting for server to become responsive...")
        import httpx
        server_ready = False
        for attempt in range(25):
            time.sleep(1)
            try:
                r = httpx.get("http://127.0.0.1:8000/api/health", timeout=1.0)
                if r.status_code == 200:
                    print(f"Server is live and healthy (detected on attempt {attempt + 1})!\n")
                    server_ready = True
                    break
            except Exception:
                pass

        if not server_ready:
            print("Server did not become healthy in time.")
            stdout, stderr = proc.communicate(timeout=2)
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            sys.exit(1)

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import test_live_system
        test_live_system.run_tests()
        print("\nAll live system tests completed successfully!")
    finally:
        print("Stopping server process...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server cleanly stopped.")

if __name__ == "__main__":
    main()
