import math

def between_powers_of_two(x):
    if x <= 0:
        raise ValueError("x 必须是正数")
    n = math.floor(math.log2(x))
    return n, n + 1  # 表示 2^n <= x < 2^(n+1)



print(between_powers_of_two(4504111))  # 输出: (4, 5) 因为 2^4=16 <= 20 < 32=2^5