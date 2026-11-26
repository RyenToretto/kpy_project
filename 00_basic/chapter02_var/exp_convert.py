def bootstrap():
    print(f'\n\n{'*' * 12} 数据类型转换 {'*' * 12}', sep='', end='\n\n')

    a1 = '2026'
    PI = 3.14159
    is_happy = True

    print(f'\n--->转换为整数 int')

    a2 = int(a1) # 如果不符合转换要求，则会报错
    print(f'纯数字的字符串: {type(a1)} {a1} ===> {type(a2)} {a2}')

    a3 = int(PI) # 浮点数可以转换成整数，但是却会只保留整数部分
    print(f'浮点数: {type(PI)} {PI} ===> {type(a3)} {a3}')

    a4 = int(is_happy) # True 会转换成 1; False 会转换成 0; 
    print(f'布尔: {type(is_happy)} {is_happy} ===> {type(a4)} {a4}')

    print(f'\n--->进制转换 init')
    s1 = '10'
    s2 = int(s1, 2)
    print(f'转换成2进制整数: {type(s2)} {s2}')
    s3 = '1a'
    s4 = int(s3, 16)
    print(f'转换成16进制整数: {type(s4)} {s4}')

    print(f'\n--->转换为浮点数 float')
    b1 = '19.987654321'
    b2 = float(b1)
    b3 = float(PI)
    b4 = float(a1)
    b5 = 2026
    b6 = float(b5)
    b7 = float(is_happy)
    print(f'浮点字符串: {type(b1)} {b1} ===> {type(b2)} {b2}')
    print(f'浮点数: {type(PI)} {PI} ===> {type(b3)} {b3}')
    print(f'整数字符串: {type(a1)} {a1} ===> {type(b4)} {b4}')
    print(f'整数: {type(b5)} {b5} ===> {type(b6)} {b6}')
    print(f'布尔: {type(is_happy)} {is_happy} ===> {type(b7)} {b7}')

    print(f'\n--->转换为布尔 bool')
    d1 = 'abc123'
    d2 = bool(d1)
    d3 = bool('')
    d4 = 0
    d5 = bool(0)
    d6 = 1
    d7 = bool(1)
    d8 = 2
    d9 = bool(2)
    d10 = -1
    d11 = bool(d10)
    print(f'字符串: {type(d1)} {d1} ===> {type(d2)} {d2}')
    print(f'空串 ===> {type(d3)} {d3}')
    print(f'bool({d4}) ===> {type(d5)} {d5}')
    print(f'bool({d6}) ===> {type(d7)} {d7}')
    print(f'bool({d8}) ===> {type(d9)} {d9}')
    print(f'bool({d10}) ===> {type(d11)} {d11}')

    print(f'\n--->转换为字符串 str')
    e1 = 5
    r1 = str(e1)
    e2 = PI
    r2 = str(e2)
    e3 = True
    r3 = str(e3)
    e4 = False
    r4 = str(e4)
    print(f'str({e1}) ===> {type(r1)} {r1}')
    print(f'str({e2}) ===> {type(r2)} {r2}')
    print(f'str({e3}) ===> {type(r3)} {r3}')
    print(f'str({e4}) ===> {type(r4)} {r4}')

if __name__ == '__main__':
    bootstrap()