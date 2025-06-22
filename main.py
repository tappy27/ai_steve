import os
import sys

# Odysseyディレクトリをimportパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "Odyssey")))

from flask import Flask, request, jsonify
from odyssey import Odyssey
from odyssey.utils import config
from odyssey.agents.llama import ModelType

app = Flask(__name__)

# Odysseyインスタンスの初期化
odyssey_bot = Odyssey(
    mc_port=config.get('MC_SERVER_PORT'),
    mc_host=config.get('MC_SERVER_HOST'),
    env_wait_ticks=100,
    skill_library_dir="./Odyssey/skill_library",
    reload=True,
    embedding_dir=config.get('SENTENT_EMBEDDING_DIR'),
    environment='explore',
    resume=False,
    server_port=config.get('NODE_SERVER_PORT'),
    critic_agent_model_name=ModelType.LLAMA3_8B_V4 if hasattr(ModelType, 'LLAMA3_8B_V4') else ModelType.LLAMA3_8B_V3,
    comment_agent_model_name=ModelType.LLAMA3_8B_V4 if hasattr(ModelType, 'LLAMA3_8B_V4') else ModelType.LLAMA3_8B_V3,
    planner_agent_qa_model_name=ModelType.LLAMA3_8B_V4 if hasattr(ModelType, 'LLAMA3_8B_V4') else ModelType.LLAMA3_8B_V3,
    planner_agent_model_name=ModelType.LLAMA3_8B_V4 if hasattr(ModelType, 'LLAMA3_8B_V4') else ModelType.LLAMA3_8B_V3,
    action_agent_model_name=ModelType.LLAMA3_8B_V4 if hasattr(ModelType, 'LLAMA3_8B_V4') else ModelType.LLAMA3_8B_V3,
    username='ai_steve'
)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Node.js側(mineflayer)からチャット内容を受け取り、Odysseyで推論し、返答を返す
    """
    data = request.get_json()
    chat_message = data.get('message', '')
    user = data.get('user', 'player')
    if not chat_message:
        return jsonify({'error': 'No message provided'}), 400

    # チャット内容をタスクとしてOdysseyに渡す
    try:
        # ユーザーチャットをcontextの先頭に明示的に追加し、Odyssey本体のプロンプト設計を崩さず組み込む
        context = f"[User指示]: {chat_message}\n[User名]: {user}"
        # rolloutでreset_env=Trueを指定し、reset()の二重呼び出しを避ける
        messages, reward, done, info = odyssey_bot.rollout(
            task=chat_message,
            context=context,
            reset_env=True
        )
        # Odysseyの返答（AIの発話）を抽出
        ai_reply = ""
        if messages and len(messages) > 1:
            ai_reply = getattr(messages[-1], 'content', '')
        return jsonify({'reply': ai_reply})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('AI_STEVE_API_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
