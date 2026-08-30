from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__, template_folder='templates')
CORS(app)

# 配置
API_BASE_URL = "https://tokenrhythm.studio/v1"
API_KEY = "sk_tr_0iPwfmIhkm8c9n3cwAmFHfVbDquBL7_9v3iY96hMuSs"
MODEL_ID = "deepseek-v4-flash"

# 读取系统提示词
with open('system_prompt.txt', 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# 简单的对话历史存储（生产环境请用redis/db）
conversations = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')

    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    # 获取或创建会话历史
    if session_id not in conversations:
        conversations[session_id] = []

    # 构建消息列表
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversations[session_id][-10:]:  # 保留最近10轮
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    try:
        # 调用 TokenRhythm API
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_ID,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        assistant_message = result['choices'][0]['message']['content']

        # 更新历史
        conversations[session_id].append({"role": "user", "content": user_message})
        conversations[session_id].append({"role": "assistant", "content": assistant_message})

        return jsonify({
            'response': assistant_message,
            'session_id': session_id
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API请求失败: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    if session_id in conversations:
        conversations[session_id] = []
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
