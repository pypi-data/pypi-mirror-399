def has_numbers(string):
    return any(a.isdigit() for a in string)

def has_numbers2(string):
    num = "0123456789"
    for a in num:
        if a in string:
            return True
    return False
