def bootstrap():
    weight = int(input('请输入你的体重(kg):'))
    height = int(input('请输入你的身高(cm):')) / 100
    bmi = round(weight / (height ** 2), 2)
    if bmi < 18.5:
        print(f'bmi = {bmi}: 偏瘦')
    elif bmi < 23.9:
        print(f'bmi = {bmi}: 完美身材')
    else:
        print(f'bmi = {bmi}: 偏胖了哟')

if __name__ == '__main__':
    bootstrap()