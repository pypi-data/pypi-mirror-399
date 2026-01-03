import base64

def base64_to_string(string):
    return base64.b64decode(string.encode('utf-8')).decode('utf-8')
