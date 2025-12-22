import docker
import os
import shutil
import tempfile
from requests.exceptions import ReadTimeout

client = docker.from_env()

def run_code(user_code, input_data="", time_limit=2.0):
    temp_dir = tempfile.mkdtemp()
    
    try:
        with open(os.path.join(temp_dir, "solution.py"), "w") as f:
            f.write(user_code)
        
        with open(os.path.join(temp_dir, "input.txt"), "w") as f:
            f.write(input_data)

        container = client.containers.run(
            image="python:3.9-slim",
            command='sh -c "python /app/solution.py < /app/input.txt"',
            volumes={temp_dir: {'bind': '/app', 'mode': 'rw'}},
            working_dir="/app",
            mem_limit="128m",
            network_disabled=True,
            detach=True
        )

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
            container.kill()
            return {"status": "Time Limit Exceeded", "output": ""}
            
        finally:
            try:
                container.remove(force=True)
            except:
                pass

    except Exception as e:
        return {"status": "System Error", "output": str(e)}
    finally:
        shutil.rmtree(temp_dir)