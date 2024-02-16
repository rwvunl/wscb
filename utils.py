import json
import re
import hashlib
import hmac

base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


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


def base64_encode(input_string):
    input_bytes = input_string.encode('utf-8')
    result = ""
    for i in range(0, len(input_bytes), 3):
        chunk = input_bytes[i:i + 3]
        if len(chunk) < 3:
            chunk += b'\x00' * (3 - len(chunk))
        block1 = chunk[0] >> 2
        block2 = ((chunk[0] & 0x03) << 4) | (chunk[1] >> 4)
        block3 = ((chunk[1] & 0x0F) << 2) | (chunk[2] >> 6)
        block4 = chunk[2] & 0x3F
        result += base64_chars[block1]
        result += base64_chars[block2]
        result += base64_chars[block3]
        result += base64_chars[block4]
    padding = len(result) % 4
    if padding:
        result += "=" * (4 - padding)
    return result


def base64_decode(encoded_string):
    result_bytes = bytearray()
    encoded_bytes = encoded_string.encode('utf-8')
    encoded_bytes = encoded_bytes.rstrip(b'=')
    for i in range(0, len(encoded_bytes), 4):
        chunk = encoded_bytes[i:i + 4]
        block1 = base64_chars.index(chr(chunk[0])) << 2 | base64_chars.index(chr(chunk[1])) >> 4
        block2 = (base64_chars.index(chr(chunk[1])) & 0x0F) << 4 | base64_chars.index(chr(chunk[2])) >> 2
        block3 = (base64_chars.index(chr(chunk[2])) & 0x03) << 6 | base64_chars.index(chr(chunk[3]))
        result_bytes.append(block1)
        result_bytes.append(block2)
        result_bytes.append(block3)
    return result_bytes.decode('utf-8')


def get_hash(password, salt):
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest()


def get_hmac(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).digest()


def generate_jwt(payload, key):
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = base64_encode(json.dumps(header))
    encoded_payload = base64_encode(json.dumps(payload))
    signature = get_hmac(key, msg=f"{encoded_header}.{encoded_payload}")
    encoded_signature = hamc_to_base64(signature)
    jwt = f"{encoded_header}.{encoded_payload}.{encoded_signature}"
    return jwt


def validate_password_format(password):
    password_pattern = re.compile(r"^[a-zA-Z0-9]{8,}$")  # 最少8位，只包含字母和数字
    if password_pattern.match(password):
        return True
    return False


def is_input_password_correct(password, input_password, salt):
    if get_hash(password, salt) != get_hash(input_password, salt):

        return False
    return True


def hamc_to_base64(data):
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


if __name__ == '__main__':
    print(base62_encode(999999999999999999999999999999))
    print(base62_decode(base62_encode(999999999999999999999999999999)))
    print(base64_encode(json.dumps({"alg": "HS256", "typ": "JWT"})))
    print(base64_decode(base64_encode(json.dumps({"alg": "HS256", "typ": "JWT"}))))
    a = b'\xe0]\xa4K\x80N\xec\xfav\x1b/\x8aZ:\xd6\x9a8\x109Y\xb7\x81\xbaNL\xb5\xba?\x80&\xb0b'
    print(hamc_to_base64(a))
    print(base64_to_hmac(hamc_to_base64(a)))
