def binary_add(value1,value2):
    bin1 = str(value1)
    bin2 = str(value2)
    num1 = int(bin1, 2)
    num2 = int(bin2, 2)
    x = num1 + num2
    sum = bin(x)[2:]
    return sum

def binary_substract(value1,value2):
    bin1 = str(value1)
    bin2 = str(value2)
    num1 = int(bin1, 2)
    num2 = int(bin2, 2)
    x = num1 - num2
    sum = bin(x)[2:]
    return sum

def binary_divide(value1,value2):
    bin1 = str(value1)
    bin2 = str(value2)
    num1 = int(bin1, 2)
    num2 = int(bin2, 2)
    x = num1 / num2
    sum = bin(x)[2:]
    return sum

def binary_multiply(value1,value2):
    bin1 = str(value1)
    bin2 = str(value2)
    num1 = int(bin1, 2)
    num2 = int(bin2, 2)
    x = num1 * num2
    sum = bin(x)[2:]
    return sum

def binary_shift_right(binary_value,shift_val):
    length = len(str(binary_value))
    rslt = bin(int(str(binary_value), 2) >> shift_val)[2:]
    rslt = rslt.zfill(length)
    return rslt

def binary_shift_left(binary_value,shift_val):
    length = len(str(binary_value))
    rslt = bin(int(str(binary_value), 2) << shift_val)[2:]
    rslt = rslt.zfill(length)
    return rslt
