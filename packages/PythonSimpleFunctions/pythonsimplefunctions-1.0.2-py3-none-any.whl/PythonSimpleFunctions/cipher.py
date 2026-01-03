alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def caesar_cipher(text: str, shift: int):
    translation_char = dict(zip(alphabet, alphabet[shift:] + alphabet[:shift]))
    temp = ""
    for char in text.upper():
        temp_char = translation_char.get(char, char)
        temp += temp_char
    return temp


def decipher_caesar_cipher(text: str, shift: int):
    translation_char = dict(zip(alphabet, alphabet[-shift:] + alphabet[:-shift]))
    temp = ""
    for char in text.upper():
        temp_char = translation_char.get(char, char)
        temp += temp_char
    return temp


def keyword_cipher(text: str, keyword: str):
    keys = "".join(dict.fromkeys(keyword.upper()))
    for char in alphabet:
        if char not in keys:
            keys += char
    translation_char = str.maketrans(alphabet, keys)
    return text.upper().translate(translation_char)


def decipher_keyword_cipher(text: str, keyword: str):
    keys = "".join(dict.fromkeys(keyword.upper()))
    for char in alphabet:
        if char not in keys:
            keys += char
    translation_char = str.maketrans(keys, alphabet)
    return text.upper().translate(translation_char)


def transposition_cipher(text: str):
    even = ""
    odd = ""
    counter = 0
    while counter < len(text):
        if counter % 2 == 0:
            even += text[counter].upper()
        else:
            odd += text[counter].upper()
        counter += 1
    return even + odd