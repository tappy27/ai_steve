# ai_steve_odyssey

Odyssey/Voyager型のMinecraft AIエージェント用APIサーバー（FastAPI実装）
Odyssey: https://arxiv.org/abs/2407.15325
Voyager: https://voyager.minedojo.org/

## 機能概要
- Skill Library（func.json）管理API（追加・編集・削除・リネーム・履歴・一覧）
- Compositional Skill（手順付き複合スキル）管理API
- LLaMA-8Bベースの自然言語→スキル名変換API
- Critic（反省・リトライ案生成）API
- 日記・行動履歴API
- 擬似的な自律実行ループAPI

## 使い方
1. 必要な依存をconda/pipでインストール
2. サーバー起動
   ```
   source ~/miniconda/bin/activate ./ai_steve_env
   uvicorn ai_steve.api_server:app --reload
   ```
3. API例（curl）
   ```
   curl -X POST "http://127.0.0.1:8000/plan_skill" -H "Content-Type: application/json" -d '{"user": "木を集めて"}'
   curl -X POST "http://127.0.0.1:8000/add_skill" -H "Content-Type: application/json" -d '{"skill_name": "make_stick", "skill_type": "composite"}'
   curl http://127.0.0.1:8000/list_skills
   ```

## 注意
- Odyssey本体やCline、miniconda、venv等はリポジトリには含めず、Skill Libraryのjsonのみで動作します。
- MineMA-3-8b-v4等のモデルはHugging Faceから各自ダウンロードしてください。
