import requests
import os

JUDGE0_URL = f"http://{os.environ.get('DROPLET_PORT', '167.71.228.16')}:2358"


def judge_single_test(source_code, language_id, stdin, expected_output, cpu_time_limit=None, memory_limit=None):
    """
    Judge0 API ga bitta test yuboradi va natijani qaytaradi.
    """
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        "expected_output": expected_output,
    }
    if cpu_time_limit:
        payload["cpu_time_limit"] = cpu_time_limit / 1000  # ms -> seconds
    if memory_limit:
        payload["memory_limit"] = memory_limit * 1024  # MB -> KB

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


# Judge0 status IDs:
# 1 = In Queue, 2 = Processing, 3 = Accepted
# 4 = Wrong Answer, 5 = TLE, 6 = Compilation Error
# 7-12 = Runtime Error variants, 13 = IE, 14 = Exec Format Error

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


def judge_all_tests(source_code, language_id, test_cases, cpu_time_limit=None, memory_limit=None):
    """
    Barcha testlarni ketma-ket tekshiradi. Har bir test natijasini tests_run ro'yxatiga qo'shadi.
    Birinchi xato testda to'xtaydi.
    """
    tests_run = []
    overall_verdict = "Accepted"
    max_time = 0.0
    max_memory = 0

    for i, test in enumerate(test_cases, 1):
        input_str = test.get("input", "")
        expected_str = test.get("expected", "")

        result = judge_single_test(
            source_code=source_code,
            language_id=language_id,
            stdin=input_str,
            expected_output=expected_str,
            cpu_time_limit=cpu_time_limit,
            memory_limit=memory_limit,
        )

        status_id = result.get("status", {}).get("id", 0)
        status_desc = result.get("status", {}).get("description", "Unknown")
        time_taken = result.get("time")
        memory_taken = result.get("memory")
        stdout = result.get("stdout") or ""
        stderr = result.get("stderr") or ""
        compile_output = result.get("compile_output") or ""

        # Track max time/memory
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

        # Build error message
        error_msg = ""
        if stderr:
            error_msg = stderr
        elif compile_output:
            error_msg = compile_output

        test_result = {
            "test_number": i,
            "status": STATUS_MAP.get(status_id, status_desc),
            "input": input_str,
            "expected": expected_str.strip(),
            "user_output": stdout.strip(),
            "time": time_taken,
            "memory": memory_taken,
            "error": error_msg,
        }
        tests_run.append(test_result)

        # If not accepted, set overall verdict and stop
        if status_id != 3:
            overall_verdict = STATUS_MAP.get(status_id, status_desc)
            break

    # Determine status key for Submission model
    status_key_map = {
        "Accepted": "accepted",
        "Wrong Answer": "wrong_answer",
        "Time Limit Exceeded": "time_limit_exceeded",
        "Compilation Error": "compilation_error",
        "Internal Error": "internal_error",
    }
    # Default runtime_error for anything else
    status_key = status_key_map.get(overall_verdict, "runtime_error")

    return {
        "verdict": overall_verdict,
        "status_key": status_key,
        "tests_run": tests_run,
        "total_tests": len(test_cases),
        "passed_tests": len([t for t in tests_run if t["status"] == "Accepted"]),
        "max_time": f"{max_time:.3f}" if max_time else None,
        "max_memory": max_memory if max_memory else None,
    }
