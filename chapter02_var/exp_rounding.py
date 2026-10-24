import math

def bootstrap():
    print(f'\n\n{'*' * 12} start {'*' * 12}', sep='', end='\n\n')

    num1 = 2.1
    num2 = 15.256
    total = num1 + num2
    print(f'2.1 + 15.256 = {total}')
    print(f'四舍五入(保留整数部分) = {round(total)}')
    print(f'四舍五入(保留2位小数) = {round(total, 2)}')
    print(f'向上去整 = {math.ceil(total)}')
    print(f'向下去整 = {math.floor(total)}')

if __name__ == '__main__':
    bootstrap()
