import sys
import json
from io import StringIO
import traceback

def execute_code(code):
    """Execute user code and capture output"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = StringIO()
    redirected_error = StringIO()
    
    sys.stdout = redirected_output
    sys.stderr = redirected_error
    
    result = {
        'success': False,
        'output': '',
        'error': '',
        'return_value': None
    }
    
    try:
        # Execute the code
        exec_globals = {}
        exec(code, exec_globals)
        
        result['success'] = True
        result['output'] = redirected_output.getvalue()
        
    except Exception as e:
        result['error'] = traceback.format_exc()
        result['output'] = redirected_output.getvalue()
    
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return result

if __name__ == '__main__':
    # Read code from file
    with open('/code/user_code.py', 'r') as f:
        user_code = f.read()
    
    result = execute_code(user_code)
    
    # Write result to file
    with open('/code/result.json', 'w') as f:
        json.dump(result, f)