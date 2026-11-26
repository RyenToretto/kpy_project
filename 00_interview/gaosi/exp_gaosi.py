"""
高斯求和: 计算 1 + 2 + 3 + … … + 100 的和
"""

def bootstrap():
    n = 1
    result = 0
    while n <= 100:
        result += n
        n += 1
    print(f'{result}')
if __name__ == '__main__':
    bootstrap()
