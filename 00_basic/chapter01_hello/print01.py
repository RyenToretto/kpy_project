import time

def bootstrap():
    print('\n\n==== 格式化字符串 ===>', sep='', end='\n\n')

    year = 1996
    str_month = '正月'
    num_month = 1
    day = 20
    """
    print(*objects, sep=' ', end='\n', file=None, flush=False)
         # sep=" "：  对象之间的分隔符，默认是 一个空格
         # end="\n"： 整行结束后追加什么，默认是 换行符 \n
         # file=None：写到哪里，默认 None，实际写到 sys.stdout（标准输出），也就是终端
         # flush=False：要不要立刻刷出缓冲区.默认 False。设为 True 时，这次 print 后立刻把缓冲区刷出去
    %%   输出 %
    %s   字符串
    %d   十进制整数
    %02d 输出的整数显示位数，不足的地方用0补全
    %f   输出浮点数
    %.2f 输出浮点数，保留2位小数
    print('我的生日是农历%d年%s月%d日' % (year, str_month, day))
    print('农历%02d月需要读%s月' % (num_month, str_month))

    实际存进去的不是 19.985
        IEEE 754 双精度只能精确表示分母是 2 的幂的分数。0.985 不行，所以 Python 会选最近的二进制近似值：
            19.984  →  19.98400000000000176...   （略大一点）
            19.985  →  19.98499999999999943...   （略小一点）
            19.986  →  19.98600000000000065...   （略大一点）
    Python 3 的 round()、%.2f、format(..., '.2f') 默认都是 银行家舍入
        银行家舍入（四舍六入五成双 / round half to even）：刚好落在中点时，让留下的那一位变成偶数
        银行家舍入是 IEEE 754 的默认，用来避免「总是遇 5 就进」带来的系统性偏大。
    """
    print('今天气温 %.2f' % 19.984) # 今天气温 19.98
    print('今天气温 %.2f' % 19.985) # 今天气温 19.98
    print('今天气温 %.2f' % 19.975) # 今天气温 19.98
    print('今天气温 %.2f' % 19.986) # 今天气温 19.99
    print("loading", end=" ", flush=True)
    time.sleep(3)
    print("done")

if __name__ == '__main__':
    bootstrap()
