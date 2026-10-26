"""
- Python 中的小整数，通常指的是 -5 至 256 之间的整数
- 当你在 Python 中创建一个整数对象时，Python 会根据该整数的值动态地为其分配内润空间
- 对于小整数，Python 会使用一种称为“小整数缓存”的机制来优化内存使用
- 这个缓存池中的整数对象会被重复利用，减少内存分配和释放的开销，扩展程序的性能。

- 如果你需要跟踪 Python 对象的内存地址，可以使用 Python 内置函数 id() 来获取对象的唯一标识符
- 这个标识符通常可以近似地表示对象的内存地址，但并不是真正的内存地址，而是 Python 解释器生成的一个唯一标识符，用于区分不同的对象实例
"""
def bootstrap():
    print(f'\n\n{'*' * 12} 数据类型转换 {'*' * 12}', sep='', end='\n\n')

    a1 = 3
    addr1 = id(a1)

    a2 = 3
    addr2 = id(a2)

    a3 = 4
    addr3 = id(a3)

    a4 = 300
    addr4 = id(a4) # IDE 也做了更大的缓存

    a5 = 300
    addr5 = id(a5)

    print(f'addr1: {addr1}')
    print(f'addr2: {addr2}')
    print(f'addr3: {addr3}')
    print(f'addr4: {addr4}')
    print(f'addr5: {addr5}')

if __name__ == '__main__':
    bootstrap()