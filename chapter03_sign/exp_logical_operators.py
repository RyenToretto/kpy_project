"""
- 逻辑运算符
    - x and y    x 和 y 都为 True, 才返回 True
    - x or y     x 和 y 有一个为 True, 就返回 True
    - not x      如果 x 为 True, 则返回 False; 如果 x 为 False, 则返回 True
"""
def bootstrap():
    print(f'\n\n{'*' * 12} 逻辑运算符 {'*' * 12}', sep='', end='\n\n')

    a = 10
    b = 3

    print(f'{a} == {b} = {a == b}')
    print(f'{a} != {b} = {a != b}')
    print(f'{a} >= {b} = {a >= b}')
    print(f'{a} <= {b} = {a <= b}')
    print(f'{a} > {b} = {a > b}')
    print(f'{a} < {b} = {a < b}')
    print(f'3.0 == 3 = {3.0 == 3}') # Python 会将 int 转换成 float 再比较;
    print(f'{"3.0" == 3}') # Python 中 ==，会首先判断是否同类型
    # print(f'{"3.0" < 3}') # Python 中 大于/小于 这样的比较是不合法的，会报错

    '''
        - 比较字符串时，不是按单词意思、长度或字母数量比较，而是按字符的 Unicode 编码值(ascii码值)，从左到右逐个比较。
    '''
    print(f'hello == hi = {"hello" < "hi"}') # True;
    print(f'e 的 ascii 码值: {ord("e")}') # 101;
    print(f'i 的 ascii 码值: {ord("i")}') # 105;

if __name__ == '__main__':
    bootstrap()