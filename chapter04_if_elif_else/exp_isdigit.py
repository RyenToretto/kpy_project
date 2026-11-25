def bootstrap():
    num = input('请输入1~120的数字')
    if num.isdigit():
        num = int(num)
        if 1 <= num <= 120:
            print(f'Your input {num} is good')
        else:
            print(f'Your input {num} is too large')
    else:
        print('请输入数字')

if __name__ == '__main__':
    bootstrap()