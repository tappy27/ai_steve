import json
from sentence_transformers import SentenceTransformer, util

# スキルリストのロード
with open("../Odyssey/MC-Comprehensive-Skill-Library/json/func.json", "r", encoding="utf-8") as f:
    skill_dict = json.load(f)

# スキル名リスト
skill_names = list(skill_dict.keys())

# SentenceTransformerモデルのロード（例: all-MiniLM-L6-v2）
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_skills(task_query, top_k=5):
    # クエリとスキル名をエンコード
    query_emb = model.encode([task_query], convert_to_tensor=True)
    skill_embs = model.encode(skill_names, convert_to_tensor=True)
    # コサイン類似度でTop-K検索
    hits = util.semantic_search(query_emb, skill_embs, top_k=top_k)[0]
    results = [(skill_names[hit['corpus_id']], hit['score']) for hit in hits]
    return results

if __name__ == "__main__":
    # 例: "craft an iron sword" で検索
    query = "craft an iron sword"
    results = search_skills(query)
    print("Top-5類似スキル:")
    for name, score in results:
        print(f"{name} (score: {score:.4f})")
