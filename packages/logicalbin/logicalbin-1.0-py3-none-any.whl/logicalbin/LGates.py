# 1 - x &1
def NOT(x,Output='normal'):
    if Output == 'normal':
        return 1 - x &1
    if Output == 'inverted':
        return NOT(1 - x) &1

    else: return 'Error'

def AND(a,b,A_input='normal',B_input='normal',Output='normal'):

    if A_input == 'normal' and B_input == 'normal' and Output == 'normal':
        return a & b &1

    if A_input == 'inverted' and B_input == 'normal' and Output == 'normal':
        return NOT(a) & b &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'normal':
        return a & NOT(b) &1
    if A_input == 'normal' and B_input == 'normal' and Output == 'inverted':
        return NOT(a & b) &1

    if A_input == 'inverted' and B_input == 'inverted' and Output == 'normal':
        return NOT(a) & NOT(b) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'inverted':
        return NOT(a & NOT(b)) &1
    if A_input == 'inverted' and B_input == 'normal' and Output == 'inverted':
        return NOT(NOT(a) & b) &1
    if A_input == 'inverted' and B_input == 'inverted' and Output == 'inverted':
        return NOT(NOT(a) & NOT(b)) &1

    else: return 'Error'

def OR(a,b,A_input='normal',B_input='normal',Output='normal'):
    if A_input == 'normal' and B_input == 'normal' and Output == 'normal':
        return a | b &1

    if A_input == 'inverted' and B_input == 'normal' and Output == 'normal':
        return NOT(a) | b &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'normal':
        return a | NOT(b) &1
    if A_input == 'normal' and B_input == 'normal' and Output == 'inverted':
        return NOT(a | b) &1

    if A_input == 'inverted' and B_input == 'inverted' and Output == 'normal':
        return NOT(a) | NOT(b) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'inverted':
        return NOT(a | NOT(b)) &1
    if A_input == 'inverted' and B_input == 'normal' and Output == 'inverted':
        return NOT(NOT(a) | b) &1
    if A_input == 'inverted' and B_input == 'inverted' and Output == 'inverted':
        return NOT(NOT(a) | NOT(b)) &1

    else: return 'Error'

# ~ (a & b) &1
def NAND(a,b,A_input='normal',B_input='normal',Output='normal'):
    if A_input == 'normal' and B_input == 'normal' and Output == 'normal':
        return ~(a & b) &1

    if A_input == 'inverted' and B_input == 'normal' and Output == 'normal':
        return ~(NOT(a) & b) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'normal':
        return ~(a & NOT(b)) &1
    if A_input == 'normal' and B_input == 'normal' and Output == 'inverted':
        return NOT(~(a & b)) &1

    if A_input == 'inverted' and B_input == 'inverted' and Output == 'normal':
        return ~(NOT(a) & NOT(b)) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'inverted':
        return NOT(~(a & NOT(b))) &1
    if A_input == 'inverted' and B_input == 'normal' and Output == 'inverted':
        return NOT(~(NOT(a) & b)) &1
    if A_input == 'inverted' and B_input == 'inverted' and Output == 'inverted':
        return NOT(~(NOT(a) & NOT(b))) &1

    else: return 'Error'

# ~ (a | b) &1
def NOR(a,b,A_input='normal',B_input='normal',Output='normal'):
    if A_input == 'normal' and B_input == 'normal' and Output == 'normal':
        return ~(a | b) &1

    if A_input == 'inverted' and B_input == 'normal' and Output == 'normal':
        return ~(NOT(a) | b) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'normal':
        return ~(a | NOT(b)) &1
    if A_input == 'normal' and B_input == 'normal' and Output == 'inverted':
        return NOT(~(a | b)) &1

    if A_input == 'inverted' and B_input == 'inverted' and Output == 'normal':
        return ~(NOT(a) | NOT(b)) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'inverted':
        return NOT(~(a | NOT(b))) &1
    if A_input == 'inverted' and B_input == 'normal' and Output == 'inverted':
        return NOT(~(NOT(a) | b)) &1
    if A_input == 'inverted' and B_input == 'inverted' and Output == 'inverted':
        return NOT(~(NOT(a) | NOT(b))) &1

    else: return 'Error'

# a ^ b &1
def XOR(a,b,A_input='normal',B_input='normal',Output='normal'):
    if A_input == 'normal' and B_input == 'normal' and Output == 'normal':
        return a ^ b &1

    if A_input == 'inverted' and B_input == 'normal' and Output == 'normal':
        return NOT(a) ^ b &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'normal':
        return a ^ NOT(b) &1
    if A_input == 'normal' and B_input == 'normal' and Output == 'inverted':
        return NOT(a ^ b) &1

    if A_input == 'inverted' and B_input == 'inverted' and Output == 'normal':
        return NOT(a) ^ NOT(b) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'inverted':
        return NOT(a ^ NOT(b)) &1
    if A_input == 'inverted' and B_input == 'normal' and Output == 'inverted':
        return NOT(NOT(a) ^ b) &1
    if A_input == 'inverted' and B_input == 'inverted' and Output == 'inverted':
        return NOT(NOT(a) ^ NOT(b)) &1

    else: return 'Error'

# ~(a ^ b) &1
def XNOR(a,b,A_input='normal',B_input='normal',Output='normal'):
    if A_input == 'normal' and B_input == 'normal' and Output == 'normal':
        return ~(a ^ b) &1

    if A_input == 'inverted' and B_input == 'normal' and Output == 'normal':
        return ~(NOT(a) ^ b) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'normal':
        return ~(a ^ NOT(b)) &1
    if A_input == 'normal' and B_input == 'normal' and Output == 'inverted':
        return NOT(~(a ^ b)) &1

    if A_input == 'inverted' and B_input == 'inverted' and Output == 'normal':
        return ~(NOT(a) ^ NOT(b)) &1
    if A_input == 'normal' and B_input == 'inverted' and Output == 'inverted':
        return ~(NOT(a ^ NOT(b))) &1
    if A_input == 'inverted' and B_input == 'normal' and Output == 'inverted':
        return NOT(~(NOT(a) ^ b)) &1
    if A_input == 'inverted' and B_input == 'inverted' and Output == 'inverted':
        return NOT(~(NOT(a) ^ NOT(b))) &1

    else: return 'Error'

class GATE():
    def NOT():
        return "| Input (A) | Output (NOT A) |\n|-----------|----------------|\n|     0     |       1        |\n|     1     |       0        |"

    def AND():
        return "| A | B |  A . B  |\n|---|---|---------|\n| 0 | 0 |    0    |\n| 0 | 1 |    0    |\n| 1 | 0 |    0    |\n| 1 | 1 |    1    |"

    def OR():
        return "| A | B | A + B  |\n|---|---|--------|\n| 0 | 0 |   0    |\n| 0 | 1 |   1    |\n| 1 | 0 |   1    |\n| 1 | 1 |   1    |"

    def NAND():
        return "| A | B | A · B  |  NAND Output |\n|---|---|--------|--------------|\n| 0 | 0 |   0    |      1       |\n| 0 | 1 |   0    |      1       |\n| 1 | 0 |   0    |      1       |\n| 1 | 1 |   1    |      0       |"

    def NOR():
        return "| A | B |  A + B | NOR Output  |\n|---|---|--------|-------------|\n| 0 | 0 |   0    |     1       |\n| 0 | 1 |   1    |     0       |\n| 1 | 0 |   1    |     0       |\n| 1 | 1 |   1    |     0       |"

    def XOR():
        return "| A | B |  XOR Output |\n|---|---|-------------|\n| 0 | 0 |     0       |\n| 0 | 1 |     1       |\n| 1 | 0 |     1       |\n| 1 | 1 |     0       |"

    def XNOR():
        return "| A | B | XOR  |  XNOR Output  |\n|---|---|------|---------------|\n| 0 | 0 |  0   |      1        |\n| 0 | 1 |  1   |      0        |\n| 1 | 0 |  1   |      0        |\n| 1 | 1 |  0   |      1        |"


