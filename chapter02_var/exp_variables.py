def bootstrap():
    print(f'\n\n{'*' * 12} start {'*' * 12}', sep='', end='\n\n')

    # 一次创建3个变量，每个变量的值相同
    num1 = num2 = num3 = 3
    print(num1, num2, num3)

    # 一次创建多个变量，每个变量的值不同
    num_a, num_b, num_c = 3, 4, 5
    print(num_a, num_b, num_c)

if __name__ == '__main__':
    bootstrap()