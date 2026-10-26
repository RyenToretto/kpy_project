"""
- 算数运算符
    - +    加
    - -    减
    - *    乘
    - /    除
    - //   除然后取整
    - %    取余
    - **   幂
"""
def bootstrap():
    print(f'\n\n{'*' * 12} 算数运算符 {'*' * 12}', sep='', end='\n\n')

    a = 10
    b = 3

    print(f'{a} + {b} = {a + b}')
    print(f'{a} - {b} = {a - b}')
    print(f'{a} * {b} = {a * b}')
    print(f'{a} / {b} = {a / b}')
    print(f'{a} // {b} = {a // b}')
    print(f'{a} % {b} = {a % b}')
    print(f'{a} ** {b} = {a ** b}')

if __name__ == '__main__':
    bootstrap()