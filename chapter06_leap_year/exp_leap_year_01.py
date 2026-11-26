"""
闰年判断, 输入一个年份(大于1582的整数):
    世纪闰年可以整除是400;
    假闰年既能整除100, 也能整除4;
    普通闰年能整除4;
    其他的，包含假闰年，都是平年;

    判断闰年不能只看“能否被4整除”，必须按照以下优先级顺序进行判断：
        ‌第一步：看能否被400整除？‌
            如果能，是‌闰年‌。（例如：2000年）
            如果不能，进入第二步。
        ‌第二步：看能否被100整除？‌
            如果能，是‌平年‌。（例如：1900年、2100年）
            如果不能，进入第三步。
        ‌第三步：看能否被4整除？‌
            如果能，是‌闰年‌。（例如：2024年、1996年）
            如果不能，是‌平年‌。（例如：2023年、1901年）
"""

def bootstrap():
    leap_year = input('请输入年份')
    if leap_year.isdigit():
        leap_year = int(leap_year)
        if  leap_year > 1582:
            if leap_year % 400 == 0:
                print(f'{leap_year} 是世纪闰年')
            elif leap_year % 4 == 0 and leap_year % 100 != 0:
                print(f'{leap_year} 是普通闰年')
            else:
                print(f'{leap_year} 是平年')
    else:
        print('Please input a years number.')
if __name__ == '__main__':
    bootstrap()
