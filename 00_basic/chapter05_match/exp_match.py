def bootstrap():
    score = int(input('请输入你的成绩'))
    if score > 100:
        print('作弊?!')
    elif score >= 90:
        print('A')
    elif score >= 80:
        print('B')
    elif score >= 70:
        print('C')
    else:
        print('D')

if __name__ == '__main__':
    bootstrap()