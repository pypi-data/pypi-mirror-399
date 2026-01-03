import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        # 记录开始时间
        start_time = time.time()
        # 调用原函数
        result = func(*args, **kwargs)
        # 记录结束时间
        end_time = time.time()
        # 计算执行时间
        execution_time = end_time - start_time
        print(f"{func.__name__} 函数执行时间: {execution_time} 秒")
        return result
    return wrapper
