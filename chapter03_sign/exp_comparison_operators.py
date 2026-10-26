"""
- 比较(关系)运算符
    - ==     等
    - !=    不等于
    - >=    大于等于
    - <=    小于等于
    - >     大于
    - <     小于
"""
def bootstrap():
    print(f'\n\n{'*' * 12} 算数运算符 {'*' * 12}', sep='', end='\n\n')

    a = 10
    b = 3

    print(f'{a} == {b} = {a == b}')
    print(f'{a} != {b} = {a != b}')
    print(f'{a} >= {b} = {a >= b}')
    print(f'{a} <= {b} = {a <= b}')
    print(f'{a} > {b} = {a > b}')
    print(f'{a} < {b} = {a < b}')

if __name__ == '__main__':
    bootstrap()