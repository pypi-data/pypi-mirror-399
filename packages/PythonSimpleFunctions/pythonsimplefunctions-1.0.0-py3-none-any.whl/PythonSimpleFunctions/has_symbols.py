def has_symbols(string):
    return any(a in "~`!@#$%^&*()_+-=[]{}\\|'\";:,.<>/?" for a in string)

def has_symbols2(string):
    symbols = "~`!@#$%^&*()_+-=[]{}\\|'\";:,.<>/?"
    for a in symbols:
        if a in string:
            return True
    return False
