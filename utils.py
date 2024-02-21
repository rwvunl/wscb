import json
import re
import hashlib  # to encrypt users' password
import hmac  # to encrypt JWT signature when generating JWT
import base64

base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

SECRET_KEY = "this_is_a_secret"
def base62_encode(num):
    if num == 0:
        return base62_chars[0]
    arr = []
    base = len(base62_chars)
    while num:
        rem = num % base
        num = num // base
        arr.append(base62_chars[rem])
    arr.reverse()
    return ''.join(arr)


def base62_decode(string):
    base = len(base62_chars)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += base62_chars.index(char) * (base ** power)
        idx += 1
    return num


def is_valid_url(url):
    """Check if the provided URL is valid."""
    regex = re.compile(
        r'^(?:http|http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def get_hash(password, salt):
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest()


def get_hmac(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).digest()


def generate_jwt(payload, key):
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = base64.b64encode(json.dumps(header).encode('utf-8')).decode('utf-8')
    encoded_payload =base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
    signature = get_hmac(key, msg=f"{encoded_header}.{encoded_payload}")
    encoded_signature = hmac_to_base64(signature)
    jwt = f"{encoded_header}.{encoded_payload}.{encoded_signature}"
    return jwt


def get_username_from_jwt(jwt):
    jwt = jwt.split('.')
    payload = json.loads(base64.b64decode(jwt[1]).decode('utf-8'))
    return payload['username']


def validate_password_format(password):
    password_pattern = re.compile(r"^[a-zA-Z0-9]{8,}$")  # Minimum of 8 characters, only letters and numbers
    if password_pattern.match(password):
        return True
    return False


def is_input_password_correct(password, input_password, salt):
    if get_hash(password, salt) != get_hash(input_password, salt):
        return False
    return True


def hmac_to_base64(data):
    encoded = ''
    num_bits = 0
    buffer = 0
    for byte in data:
        buffer = (buffer << 8) | byte
        num_bits += 8
        while num_bits >= 6:
            num_bits -= 6
            index = (buffer >> num_bits) & 0x3F
            encoded += base64_chars[index]
    if num_bits > 0:
        buffer <<= (6 - num_bits)
        index = buffer & 0x3F
        encoded += base64_chars[index]
        encoded += '=' * (4 - len(encoded) % 4)
    return encoded


def base64_to_hmac(data):
    decoded = bytearray()
    buffer = 0
    num_bits = 0
    for char in data:
        if char == '=':
            break
        index = base64_chars.find(char)
        buffer = (buffer << 6) | index
        num_bits += 6

        while num_bits >= 8:
            num_bits -= 8
            byte = (buffer >> num_bits) & 0xFF
            decoded.append(byte)

    return bytes(decoded)

def validate_jwt(jwt):
    jwt = jwt.split('.')
    length = len(jwt)
    if length != 3:
        return False
    else:
        received_signature = jwt[2]
        header = jwt[0]
        payload = jwt[1]
        signature = get_hmac(key=SECRET_KEY, msg=f"{header}.{payload}")
        encoded_signature = hmac_to_base64(signature)
        if received_signature == encoded_signature:
            return True
        else:
            return  False

if __name__ == '__main__':
    # print(base62_encode(999999999999999999999999999999))
    # print(base62_decode(base62_encode(999999999999999999999999999999)))
    username = "test"
    jwt = generate_jwt(payload={'username': username}, key=SECRET_KEY)
    print(jwt)
    print(validate_jwt(jwt))
    jwt = "sdfsdf.eyJ1c2VybmFtZSI6ICJ0ZXN0In0=.Swg1ng91VwsXbPB9B85Lx33RYKN/o4m5vRqCgPS+eWA="
    print(jwt)
    print(validate_jwt(jwt))
    a = b'\xe0]\xa4K\x80N\xec\xfav\x1b/\x8aZ:\xd6\x9a8\x109Y\xb7\x81\xbaNL\xb5\xba?\x80&\xb0b'
    print(hmac_to_base64(a))
    print(base64_to_hmac(hmac_to_base64(a)))
