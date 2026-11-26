"""
高斯求和: 计算 1 + 2 + 3 + … … + 100 的和
"""

def bootstrap():
    result = 0
    for n in range(100):
        result += n + 1
    print(f'{result}')
if __name__ == '__main__':
    bootstrap()
