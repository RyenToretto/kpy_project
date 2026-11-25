def bootstrap():
    num = int(input('请输入数字'))
    match num:
        case 1:
            print('num is 1')
        case 2:
            print('num is 2')  #
        case _:  # 匹配所有其他的值
            print('other')

if __name__ == '__main__':
    bootstrap()