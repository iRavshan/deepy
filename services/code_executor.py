import docker
import json
import tempfile
import os
import time
import platform

class CodeExecutor:
    def __init__(self):
        # Detect OS and configure Docker client accordingly
        system = platform.system()
        
        if system == 'Windows':
            # Try multiple connection methods for Windows
            try:
                # Method 1: Named pipe (default for Docker Desktop)
                self.client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
            except Exception:
                try:
                    # Method 2: TCP connection
                    self.client = docker.DockerClient(base_url='tcp://localhost:2375')
                except Exception:
                    # Method 3: Environment default
                    self.client = docker.from_env()
        else:
            # Linux/Mac - use default socket
            self.client = docker.from_env()
        
        self.image_name = 'code-runner:latest'
        self.timeout = 30
    
    def test_connection(self):
        """Test if Docker is accessible"""
        try:
            self.client.ping()
            return True, "Docker connection successful"
        except Exception as e:
            return False, f"Docker connection failed: {str(e)}"
        
    def execute_code(self, code, language='python', inputs=None):
        """Execute user code in a Docker container"""
        
        # First, test Docker connection
        connected, message = self.test_connection()
        if not connected:
            return {
                'success': False,
                'error': f'Cannot connect to Docker: {message}',
                'output': ''
            }
        
        if language != 'python':
            return {
                'success': False,
                'error': 'Only Python is currently supported',
                'output': ''
            }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write user code to file
            code_file = os.path.join(tmpdir, 'user_code.py')
            with open(code_file, 'w') as f:
                f.write(code)
            
            # Write inputs to file if provided
            if inputs is not None:
                inputs_file = os.path.join(tmpdir, 'inputs.json')
                with open(inputs_file, 'w') as f:
                    json.dump(inputs, f)
            
            result_file = os.path.join(tmpdir, 'result.json')
            
            try:
                # Run container with resource limits
                container = self.client.containers.run(
                    self.image_name,
                    detach=True,
                    remove=True,
                    network_mode='none',
                    mem_limit='128m',
                    cpu_quota=50000,
                    volumes={
                        tmpdir: {'bind': '/code', 'mode': 'rw'}
                    },
                    working_dir='/code'
                )
                
                # Wait for container to finish with timeout
                start_time = time.time()
                exit_status = container.wait(timeout=self.timeout)
                
                # Read result
                if os.path.exists(result_file):
                    with open(result_file, 'r') as f:
                        result = json.load(f)
                else:
                    result = {
                        'success': False,
                        'error': 'No result file generated',
                        'output': ''
                    }
                
                return result
                
            except docker.errors.ContainerError as e:
                return {
                    'success': False,
                    'error': f'Container error: {str(e)}',
                    'output': ''
                }
            except docker.errors.ImageNotFound:
                return {
                    'success': False,
                    'error': 'Code runner image not found. Please build it first: docker build -t code-runner:latest .',
                    'output': ''
                }
            except docker.errors.APIError as e:
                return {
                    'success': False,
                    'error': f'Docker API error: {str(e)}. Make sure Docker Desktop is running and accessible.',
                    'output': ''
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Unexpected error: {str(e)}',
                    'output': ''
                }