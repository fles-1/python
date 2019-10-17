import re


def fun(numstr: str):
    """需要输入为字符串"""
    num = numstr.upper()
    if 'E' not in num:
        return numstr
    lower = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
             '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '+': '', '-': '⁻'}  # '+': '⁺' 省略加号

    e = num.find('E')

    big = num[:e]
    symbol = '×10'
    if num[e + 1] in ('+', '-'):
        symbol += lower.get(num[e + 1])
        e += 1

    num2 = num[e + 1:]
    # 去除多余的0
    for i in range(len(num2)):
        if num2[i] == '0':
            e += 1
        else:
            break

    little = ''.join([lower.get(i) for i in num[e + 1:]])
    return big + symbol + little


print(fun('3.1E-5'))  # 12315×10²¹⁵¹²
