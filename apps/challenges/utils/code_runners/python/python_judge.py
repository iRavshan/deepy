from .python_runner import run_code

test_cases = [
    {"input": "2 3", "expected": "5"},       # Oddiy test
    {"input": "10 20", "expected": "30"},    # Ikkinchi test
    {"input": "-5 5", "expected": "0"}       # Uchunchi test
]


def judge_submission(user_code, test_cases, time_limit=2.0):    
    for i, test in enumerate(test_cases, 1):
        input_str = test["input"]
        expected_str = test["expected"]
        
        result = run_code(
            user_code=user_code, 
            input_data=input_str, 
            time_limit=time_limit
        )
        
        # 2. Tizim xatosi yoki Time Limit
        if result["status"] != "OK":
            return {
                "verdict": result["status"], # Masalan: "Time Limit Exceeded"
                "failed_test": i
            }
        
        # 3. Javobni solishtirish
        # strip() juda muhim, chunki print() oxiriga \n qo'shadi
        user_output = result["output"].strip()
        expected_output = expected_str.strip()
        
        if user_output != expected_output:
            return {
                "verdict": "Wrong Answer",
                "failed_test": i,
                "input": input_str,
                "user_output": user_output,
                "expected": expected_output
            }
            
        print(f"✅ Test {i} dan o'tdi")

    return {"verdict": "Accepted", "failed_test": None}