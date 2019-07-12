def mupltiple_suffix(num):
    if num % 10 == 1 and num % 100 != 11:
        return ''
    elif num % 10 in (2, 3, 4) and num % 100 not in (12, 13, 14):
        return 'а'
    else:
        return 'ов'
