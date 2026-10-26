"""
- 赋值运算符
    - =     等
    - +=    自加
    - -=    自减
    - *=    自乘
    - /=    自除
    - //=   自除然后取整
    - %=    自取余
    - **=   自幂
"""
def bootstrap():
    print(f'\n\n{'*' * 12} 算数运算符 {'*' * 12}', sep='', end='\n\n')

    a = 10
    a += 10

    print(f'a += 10 = {a}')

if __name__ == '__main__':
    bootstrap()