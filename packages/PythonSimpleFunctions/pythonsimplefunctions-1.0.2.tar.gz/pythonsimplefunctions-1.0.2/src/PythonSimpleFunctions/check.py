numbers = "0123456789"
space = " "
symbols = "~`!@#$%^&*()_+-=[]{}\\|'\";:,.<>/?"


def has_numbers(string):
    return any(a.isdigit() for a in string)


def has_numbers2(string):
    for a in numbers:
        if a in string:
            return True
    return False


def has_spaces(string):
    return any(a == space for a in string)


def has_spaces2(string):
    for a in string:
        if a == space:
            return True
    return False


def has_symbols(string):
    return any(a in symbols for a in string)


def has_symbols2(string):
    for a in symbols:
        if a in string:
            return True
    return False