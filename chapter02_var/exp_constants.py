def bootstrap(u_num):
    print(f'\n\n{'*' * 12} start {'*' * 12}', sep='', end='\n\n')

    '''命名标准：
        - 每个单词都使用小写字母
        - 开头不能是数字
        - 每个单词与单词之间以下划线连接
    '''

    '''python 定义变量是不指定类型的
        - python 没有专门的常量类型
        - 大家普遍以全大写命名的变量 来表示常量
        - 可以使用 type 和 isinstance 来测试和判断数据类型
            - 整型    1                             int 不带小数点
            - 浮点型   3.14159                       float 有小数点 
            - 复数    1.23j                         带有实部和虚部的数字；一般科学运算需要
            - 布尔型   False / True                    表示真假
            - 字符串   'Hello world'                 str
            - 列表     [1, '2', 3, 4]               有序的集合，可以包含任何数据类型
            - 元组     [1, 'a', 3, 4]               类似列表，但是不可变
            - 集合     { 1, 2, 3 }                  无序且不重复的元素集合
            - 字典     { name: 'John', age: 30 }    键值对的集合
    '''
    print(f'{u_num} 的类型是 {type(u_num)}')  # True

    PI = 3.1415926
    print(f'PI = {PI}', type(PI), isinstance(PI, str))           # False

    exp_num = 56 # <class int>
    print('exp_num', type(exp_num), isinstance(exp_num, int))    # True

    exp_dou = 7.8 # <class float>
    print('exp_dou', type(exp_dou), isinstance(exp_dou, float))  # True

    empty_str = str() # <class str>
    empty_str = '' # <class str>
    print('empty_str', type(empty_str), isinstance(empty_str, str))    # True

    multi_str = '''--->第一行
    --->第二行
    ''' # <class str>
    print(multi_str, type(multi_str), isinstance(multi_str, str))    # True

    exp_str = '1234asd' # <class str>
    print('exp_str', type(exp_str), isinstance(exp_str, str))    # True
    print(f'字符串拼接：{exp_str + ' and more'}')
    print(f'字符串乘法：{'-****-' * 3}; {exp_str * 2}')
    print(f'转义符：It\'s me.')

if __name__ == '__main__':
    bootstrap(input('请输入一个数字> '))