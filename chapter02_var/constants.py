def bootstrap():
    print('\n\n==== start ===>', sep='', end='\n\n')

    # python 没有专门的常量类型，所以大家普遍以全大写命名的变量 来表示常量
    PI = 3.1415926
    print(f'PI = {PI}')

if __name__ == '__main__':
    bootstrap()