def bootstrap():
    var = input('请输入你的年龄>') # 用户输出的任何东西，都会做字符串处理

    print(type(var))
    var = int(var)
    print(type(var))

    b_year = 2026 - var
    print('Your birth year is {bYear}.')
    print(f'Your birth year is {b_year}.') # 内容格式化

if __name__ == '__main__':
    bootstrap()