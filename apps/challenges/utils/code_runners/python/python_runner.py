import docker
import docker.errors
import os
import shutil
import tempfile
from requests.exceptions import ReadTimeout

try:
    client = docker.from_env()
except Exception:
    client = None

def run_code(user_code, input_data="", time_limit=2.0):
    base_dir = os.path.join(os.getcwd(), "temp_submissions")
    os.makedirs(base_dir, exist_ok=True)

    temp_dir = tempfile.mkdtemp(dir=base_dir)
    
    try:
        with open(os.path.join(temp_dir, "solution.py"), "w") as f:
            f.write(user_code)
        
        with open(os.path.join(temp_dir, "input.txt"), "w") as f:
            f.write(input_data)

        try:
            abs_temp_dir = os.path.abspath(temp_dir)
            print(abs_temp_dir)
            print(temp_dir)
            print(base_dir)
            container = client.containers.run(
                image="python:3.9-slim",
                command='sh -c "python /app/solution.py < /app/input.txt"',
                volumes={abs_temp_dir: {'bind': '/app', 'mode': 'rw'}},
                working_dir="/app",
                mem_limit="128m",
                network_disabled=True,
                detach=True
            )

        except docker.errors.ImageNotFound:
            return {"status": "System Error", "output": "Python image not found. Run 'docker pull python:3.9-slim'"}
        
        except docker.errors.APIError as e:
            return {"status": "System Error", "output": f"Docker API Error: {str(e)}"}
        

        try:
            result = container.wait(timeout=time_limit)
            
            if result['StatusCode'] != 0:
                logs = container.logs().decode('utf-8')
                return {"status": "Runtime Error", "output": logs}

            logs = container.logs(stream=False)
            if len(logs) > 1024 * 1024: 
                return {"status": "Output Limit Exceeded", "output": ""}
            
            return {"status": "OK", "output": logs.decode('utf-8').strip()}

        except (ReadTimeout, Exception):
            try:
                container.kill()
            except:
                pass
            return {"status": "Time Limit Exceeded", "output": ""}
            
        finally:
            try:
                container.remove(force=True)
            except:
                pass

    except Exception as e:
        return {"status": "System Error", "output": str(e)}
    
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass