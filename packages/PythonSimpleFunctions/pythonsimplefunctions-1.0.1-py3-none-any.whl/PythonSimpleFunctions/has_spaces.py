def has_spaces(string):
    return any(a == " " for a in string)

def has_spaces2(string):
    for a in string:
        if a == " ":
            return True
    return False
