import docker
import docker.errors
import os
import shutil
import tempfile
import subprocess
from requests.exceptions import ReadTimeout

try:
    client = docker.from_env()
    client.ping() # Check if reachable
except Exception:
    client = None

def run_code(user_code, input_data="", time_limit=2.0):
    base_dir = os.path.join(os.getcwd(), "temp_submissions")
    os.makedirs(base_dir, exist_ok=True)

    temp_dir = tempfile.mkdtemp(dir=base_dir)
    
    try:
        # Prepare files
        solution_path = os.path.join(temp_dir, "solution.py")
        input_path = os.path.join(temp_dir, "input.txt")
        
        with open(solution_path, "w") as f:
            f.write(user_code)
        
        with open(input_path, "w") as f:
            f.write(input_data)

        # 1. Try Docker Execution
        if client:
            try:
                return run_with_docker(client, temp_dir, time_limit)
            except Exception as e:
                print(f"Docker failed, falling back to local: {e}")
                # Fallback to local
                return run_with_subprocess(solution_path, input_path, time_limit)
        else:
            # 2. Local Execution (Subprocess)
            return run_with_subprocess(solution_path, input_path, time_limit)

    except Exception as e:
        return {"status": "System Error", "output": str(e)}
    
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

def run_with_docker(client, temp_dir, time_limit):
    abs_temp_dir = os.path.abspath(temp_dir)
    try:
        container = client.containers.run(
            image="python:3.9-slim",
            command='sh -c "python /app/solution.py < /app/input.txt"',
            volumes={abs_temp_dir: {'bind': '/app', 'mode': 'rw'}},
            working_dir="/app",
            mem_limit="128m",
            network_disabled=True,
            detach=True
        )

        result = container.wait(timeout=time_limit)
        
        if result['StatusCode'] != 0:
            logs = container.logs().decode('utf-8')
            container.remove(force=True)
            return {"status": "Runtime Error", "output": logs}

        logs = container.logs(stream=False)
        container.remove(force=True)
        
        if len(logs) > 1024 * 1024: 
            return {"status": "Output Limit Exceeded", "output": ""}
        
        return {"status": "OK", "output": logs.decode('utf-8').strip()}

    except ReadTimeout:
        try:
            container.kill()
            container.remove(force=True)
        except:
            pass
        return {"status": "Time Limit Exceeded", "output": ""}
    except Exception as e:
        raise e

def run_with_subprocess(solution_path, input_path, time_limit):
    try:
        # Safe-ish local run
        with open(input_path, 'r') as infile:
            result = subprocess.run(
                ['python', solution_path],
                stdin=infile,
                capture_output=True,
                text=True,
                timeout=time_limit
            )
        
        if result.returncode != 0:
            return {"status": "Runtime Error", "output": result.stderr}
            
        return {"status": "OK", "output": result.stdout}

    except subprocess.TimeoutExpired:
        return {"status": "Time Limit Exceeded", "output": ""}
    except Exception as e:
        return {"status": "System Error", "output": f"Local run error: {str(e)}"}