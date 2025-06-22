# ai_steve

## 概要

**ai_steve**は、Odyssey論文・公式実装をベースにした「人と一緒に遊ぶマインクラフトAIチャットBot」です。
Minecraftサーバー内で人間のチャットに自然言語で返答し、複雑なタスク（例: "mine diamond"）も自律的にサブゴール分解・実行します。  
GPU不要でローカルCPUのみで動作します。
mine diamondの一言のみでダイヤモンドを自力で入手する程度の能力はあります。
（開発中であり、全てのチャットを命令と受け取って意図しない命令を実行し始めたり、そもそも反応が遅すぎたり、まだまだ一緒に遊んで楽しめるレベルではありません。）

---

## Installation

### 1. 必要な前提

- OS: Unix系 筆者はUbuntu 20.04/22.04, WSL2
- Python: 3.9〜3.12
- Node.js: v22.x系
- Minecraftサーバー: 1.19, 1.20, 1.20.4 Fabric（mod導入推奨、pause未導入でも動作可）

### 2. クローン

```bash
git clone <このリポジトリ>
cd ai_steve
```

### 3. Python依存

```bash
conda create -n ai_steve python=3.12
conda activate ai_steve
pip install -r requirements.txt
```

### 4. Node.js依存・Mineflayerビルド

```bash
npm install -g yarn
cd Odyssey/odyssey/env/mineflayer
yarn install
cd mineflayer-collectblock
npx tsc
cd ..
yarn install
cd node_modules/mineflayer-collectblock
npx tsc
```

### 5. モデル・埋め込み（git-lfs推奨）

```bash
# git-lfsが未インストールの場合
conda install -c conda-forge git-lfs
git lfs install

# 埋め込みモデル
git clone https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2.git
cd paraphrase-multilingual-MiniLM-L12-v2
git lfs pull
cd ..

# LLM本体（例: MineMA-3-8b-v4）
git clone https://huggingface.co/Aiwensile2/MineMA-8B.git
cd MineMA-8B/MineMA-3-8b-v4
git lfs pull
cd ../../
```

**⚠️ 注意: LLM本体（MineMA-3-8b-v4）は約15GB以上の大容量ファイルです。 **

---

## Usage

### 1. LLM-Backend（LLM推論APIサーバー）

```bash
cd ai_steve/LLM-Backend
python main.py
```
（初回はモデルロードに時間がかかります）

### 2. Mineflayerサーバー（Node.js, Minecraft連携API）

```bash
cd ai_steve/Odyssey/odyssey/env/mineflayer
node --max-old-space-size=16384 index.js 3000
```
**⚠️ Node.jsプロセスでメモリ不足の場合は`--max-old-space-size`の値を増やしてください。
8GB以上推奨。筆者は16GB割り当ててようやく落ちなくなりました。**

### 3. Odyssey本体（AIエージェント/Flaskサーバー）

```bash
cd ai_steve
python main.py
```

### 4. チャットBot（mineflayer/mc_bot.js）

```bash
cd ai_steve
node mc_bot.js
```

### 5. Minecraftサーバー

- Windows側で1.19, 1.20 バニラサーバーを起動 (1.20.4で動作確認)
- WSLからは`MC_SERVER_HOST`にLAN内IPを指定

---

## 使い方と注意

- Minecraft内で「mine diamond」など自然言語でチャット
- 詳細な設定は`ai_steve/Odyssey/conf/config.json`等を参照
- それぞれのポート割り当て、ipアドレス指定、等は自由にやってください
---

## ライセンス

MIT License（Odyssey本家に準拠）

---

## 引用

Odyssey:  
https://arxiv.org/abs/2407.15325
https://github.com/zju-vipa/Odyssey
