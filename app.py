from flask import Flask, request, jsonify
import random
import string

app = Flask(__name__)
url_mapping = dict() # 用于存储URL映射关系的字典


def generate_short_url():
    """生成短标识符"""
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))  # 生成6位长度的随机字符串作为短标识符
    return short_url


@app.route('/shorten', methods=['POST'])
def shorten_url():
    """将长URL映射到短标识符上"""
    long_url = request.json.get('long_url')
    if not long_url:
        return jsonify({'error': 'Long URL is required'}), 400

    short_url = generate_short_url()
    url_mapping[short_url] = long_url
    return jsonify({'short_url': short_url}), 201


@app.route('/resolve/<short_url>', methods=['GET'])
def resolve_url(short_url):
    """根据短标识符获取长URL"""
    long_url = url_mapping.get(short_url)
    if not long_url:
        return jsonify({'error': 'Short URL not found'}), 404

    return jsonify({'long_url': long_url})


@app.route('/delete/<short_url>', methods=['DELETE'])
def delete_url(short_url):
    """删除URL映射关系"""
    if short_url not in url_mapping:
        return jsonify({'error': 'Short URL not found'}), 404

    del url_mapping[short_url]
    return '', 204


if __name__ == '__main__':
    app.run()
