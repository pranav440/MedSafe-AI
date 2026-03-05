import subprocess
import sys
import os
import time

def start_process(name, command, cwd=None):
    """Starts a subprocess and returns it, handling basic errors."""
    print(f"[{name}] Starting...")
    try:
        # Use shell=True for npm on Windows
        is_shell = command.startswith("npm")
        # Pipe stdout/stderr so they interleave in the master console, or to DEVNULL if too noisy
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=is_shell,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        time.sleep(1) # Give it a second to fail immediately if there's a typo
        if process.poll() is not None:
            print(f"[{name}] ERROR: Process crashed immediately with exit code {process.returncode}")
            return None
        return process
    except Exception as e:
        print(f"[{name}] ERROR: Failed to start process: {e}")
        return None

def main():
    print("==================================================")
    print(" MedSafe AI – System Boot sequence initiated")
    print("==================================================")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "medsafe-insight-main")
    
    processes = []
    
    # 1. Start Flask API
    flask_proc = start_process("Flask API", f"{sys.executable} api/app.py", cwd=root_dir)
    if flask_proc: processes.append(("Flask API", flask_proc))
    
    # 2. Start Vitals Simulator (Fallback for Kafka Producer)
    # We replaced the raw Kafka producer with our robust simulator script earlier
    sim_proc = start_process("Vitals Simulator", f"{sys.executable} simulator.py", cwd=root_dir)
    if sim_proc: processes.append(("Vitals Simulator", sim_proc))
    
    # 3. Start Kafka Consumer (If available/configured)
    consumer_proc = start_process("Kafka Consumer", f"{sys.executable} kafka/consumer.py", cwd=root_dir)
    if consumer_proc: processes.append(("Kafka Consumer", consumer_proc))
    
    # 4. Start React Frontend
    frontend_proc = start_process("Frontend UI", "npm run dev", cwd=frontend_dir)
    if frontend_proc: processes.append(("Frontend UI", frontend_proc))
    
    print("\n[System] All configured services have been launched.")
    print("[System] Dashboard should be available at http://localhost:8080")
    print("[System] Press Ctrl+C to stop all services.\n")
    
    try:
        # Keep main thread alive while subprocesses run
        while True:
            time.sleep(1)
            for name, p in processes:
                if p.poll() is not None:
                    print(f"\n[WARNING] {name} exited unexpectedly with code {p.returncode}")
                    processes.remove((name, p))
                    
            if not processes:
                print("\n[System] All services have exited. Shutting down.")
                break
                
    except KeyboardInterrupt:
        print("\n[System] Shutdown requested. Terminating all services...")
        for name, p in processes:
            print(f"[{name}] Terminating...")
            p.terminate()
            
        # Give them a moment to terminate gracefully before killing
        time.sleep(2)
        for name, p in processes:
            if p.poll() is None:
                p.kill()
                
        print("[System] Shutdown complete.")

if __name__ == "__main__":
    main()
