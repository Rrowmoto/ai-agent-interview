from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

API_BASE_URL = "https://tokenrhythm.studio/v1"
API_KEY = "sk_tr_0iPwfmIhkm8c9n3cwAmFHfVbDquBL7_9v3iY96hMuSs"
MODEL_ID = "deepseek-v4-flash-0731"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 代理请求到 TokenRhythm API，跟前端 index.html 的调用格式完全一致
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": data.get("model", MODEL_ID),
                "messages": data.get("messages", []),
                "temperature": data.get("temperature", 0.7),
                "max_tokens": data.get("max_tokens", 1000)
            },
            timeout=30
        )
        # 直接把上游响应原样转回给前端
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": {"message": f"API请求失败: {str(e)}"}}), 502
    except Exception as e:
        return jsonify({"error": {"message": f"服务器错误: {str(e)}"}}), 500

if __name__ == '__main__':
    # host=0.0.0.0 让局域网内其他设备也能访问
    app.run(host='0.0.0.0', port=5000, debug=False)
