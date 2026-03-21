import requests
import os
import base64
import time

JUDGE0_URL = f"http://{os.environ.get('DROPLET_PORT', '167.71.228.16')}:2358"

STATUS_MAP = {
    3: "Accepted",
    4: "Wrong Answer",
    5: "Time Limit Exceeded",
    6: "Compilation Error",
    7: "Runtime Error (SIGSEGV)",
    8: "Runtime Error (SIGXFSZ)",
    9: "Runtime Error (SIGFPE)",
    10: "Runtime Error (SIGABRT)",
    11: "Runtime Error (NZEC)",
    12: "Runtime Error (Other)",
    13: "Internal Error",
    14: "Exec Format Error",
}

def judge_single_test(source_code, language_id, stdin, expected_output, cpu_time_limit=None, memory_limit=None):
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        "expected_output": expected_output,
    }
    if cpu_time_limit:
        payload["cpu_time_limit"] = cpu_time_limit / 1000   
    if memory_limit:
        payload["memory_limit"] = memory_limit * 1024  

    try:
        response = requests.post(
            f"{JUDGE0_URL}/submissions?base64_encoded=false&wait=true",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "status": {"id": 0, "description": "Internal Error"},
            "stderr": str(e),
            "stdout": None,
            "time": None,
            "memory": None,
            "compile_output": None,
        }

def encode_base64(s):
    if not s:
        return ""
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')

def decode_base64(s):
    if not s:
        return ""
    try:
        return base64.b64decode(s).decode('utf-8')
    except Exception:
        return s

def batch_judge_tests(source_code, language_id, test_cases, cpu_time_limit=None, memory_limit=None):
    """
    Barcha testlarni birdaniga batch API orqali Judge0 ga yuboradi.
    Natijalarni kuting va dict ko'rinishida qaytaring.
    """
    tests_run = []
    overall_verdict = "Accepted"
    max_time = 0.0
    max_memory = 0
    total_tests = len(test_cases)
    
    if total_tests == 0:
        return {
            "verdict": overall_verdict,
            "status_key": "accepted",
            "tests_run": [],
            "total_tests": 0,
            "passed_tests": 0,
            "max_time": None,
            "max_memory": None,
        }

    b64_source = encode_base64(source_code)
    
    submissions_payload = []
    for test in test_cases:
        payload = {
            "source_code": b64_source,
            "language_id": language_id,
            "stdin": encode_base64(test.get("input", "")),
            "expected_output": encode_base64(test.get("expected", "")),
        }
        if cpu_time_limit:
            payload["cpu_time_limit"] = cpu_time_limit / 1000   
        if memory_limit:
            payload["memory_limit"] = memory_limit * 1024  
        submissions_payload.append(payload)
        
    try:
        post_url = f"{JUDGE0_URL}/submissions/batch?base64_encoded=true"
        response = requests.post(post_url, json={"submissions": submissions_payload}, timeout=30)
        response.raise_for_status()
        tokens = [item["token"] for item in response.json()]
    except Exception as e:
        return {
            "verdict": "Internal Error",
            "status_key": "internal_error",
            "tests_run": [{"error": f"Failed to submit batch: {str(e)}", "status": "Internal Error"}],
            "total_tests": total_tests,
            "passed_tests": 0,
            "max_time": None,
            "max_memory": None
        }

    tokens_str = ",".join(tokens)
    get_url = f"{JUDGE0_URL}/submissions/batch?tokens={tokens_str}&base64_encoded=true&fields=status_id,time,memory,stdout,stderr,compile_output"
    
    # Polling logic
    while True:
        try:
            res = requests.get(get_url, timeout=30)
            res.raise_for_status()
            batch_result = res.json()["submissions"]
            
            # Check if any are still pending (status_id 1 = In Queue, 2 = Processing)
            if any(br.get("status_id") in [1, 2] for br in batch_result):
                time.sleep(1)
                continue
                
            break
        except Exception:
            time.sleep(1)
            # We assume it will eventually resolve or timeout in celery task itself, or limit retry loop.
            pass

    passed_tests = 0
    for i, test in enumerate(test_cases, 1):
        br = batch_result[i-1]
        status_id = br.get("status_id", 0)
        status_desc = STATUS_MAP.get(status_id, "Unknown")
        time_taken = br.get("time")
        memory_taken = br.get("memory")
        stdout = decode_base64(br.get("stdout"))
        stderr = decode_base64(br.get("stderr"))
        compile_output = decode_base64(br.get("compile_output"))
        
        if time_taken:
            try:
                max_time = max(max_time, float(time_taken))
            except (ValueError, TypeError):
                pass
        if memory_taken:
            try:
                max_memory = max(max_memory, int(memory_taken))
            except (ValueError, TypeError):
                pass

        error_msg = ""
        if stderr:
             error_msg = stderr
        elif compile_output:
             error_msg = compile_output

        test_result = {
            "test_number": i,
            "status": status_desc,
            "input": test.get("input", ""),
            "expected": test.get("expected", "").strip(),
            "user_output": stdout.strip(),
            "time": time_taken,
            "memory": memory_taken,
            "error": error_msg,
        }
        tests_run.append(test_result)
        
        if status_id == 3:
            passed_tests += 1
        
        # Stop considering successive runs on first fail? Batch runs all of them inherently, 
        # so we just gather results but set overall_verdict on first fail.
        if status_id != 3 and overall_verdict == "Accepted":
             overall_verdict = status_desc

    status_key_map = {
        "Accepted": "accepted",
        "Wrong Answer": "wrong_answer",
        "Time Limit Exceeded": "time_limit_exceeded",
        "Compilation Error": "compilation_error",
        "Internal Error": "internal_error",
    }
    status_key = status_key_map.get(overall_verdict, "runtime_error")

    return {
        "verdict": overall_verdict,
        "status_key": status_key,
        "tests_run": tests_run,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "max_time": f"{max_time:.3f}" if max_time else None,
        "max_memory": max_memory if max_memory else None,
    }
