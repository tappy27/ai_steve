import json
from fastapi import FastAPI, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any

# LLaMA-8B (LoRAファインチューニング済み) のロード
from transformers import LlamaForCausalLM, AutoTokenizer
import torch

LLAMA_MODEL_PATH = "ai_steve/MineMA-3-8b-v4"

tokenizer = AutoTokenizer.from_pretrained(LLAMA_MODEL_PATH)
llama_model = LlamaForCausalLM.from_pretrained(
    LLAMA_MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

FUNC_JSON_PATH = "ai_steve/skill_data/func.json"
SKILL_HISTORY_PATH = "ai_steve/skill_data/skill_history.json"
COMPOSITE_SKILL_PATH = "ai_steve/skill_data/composite_skills.json"
DIARY_PATH = "ai_steve/skill_data/diary.json"

# スキルリストのロード
with open(FUNC_JSON_PATH, "r", encoding="utf-8") as f:
    skill_dict = json.load(f)
skill_names = list(skill_dict.keys())

# SentenceTransformerモデルのロード（例: all-MiniLM-L6-v2）
st_model = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class LlamaRequest(BaseModel):
    system: str = "You are a Large Language Model, and your task is to answer questions posed by users about Minecraft. Utilize your knowledge and understanding of the game to provide detailed, accurate, and helpful responses. Use your capabilities to assist users in solving problems, understanding game mechanics, and enhancing their Minecraft experience."
    user: str

class PlanSkillRequest(BaseModel):
    user: str
    top_k: int = 5

class AddSkillRequest(BaseModel):
    skill_name: str
    skill_type: str
    description: str = ""

class EditSkillRequest(BaseModel):
    skill_name: str
    skill_type: str
    description: str = ""

class RenameSkillRequest(BaseModel):
    old_skill_name: str
    new_skill_name: str

class CriticFeedbackRequest(BaseModel):
    user: str
    skill: str
    error_log: str

class DeleteSkillRequest(BaseModel):
    skill_name: str

# 1. Compositional Skill管理API
class CompositeSkill(BaseModel):
    name: str
    description: str = ""
    steps: List[str]  # ["mine_wood", "craft_planks", "craft_stick"]
    dependencies: List[str] = []

@app.post("/add_composite_skill")
def add_composite_skill(skill: CompositeSkill):
    try:
        with open(COMPOSITE_SKILL_PATH, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
    except FileNotFoundError:
        comp_data = {}
    if skill.name in comp_data:
        return {"error": f"Composite skill '{skill.name}' already exists."}
    comp_data[skill.name] = skill.dict()
    with open(COMPOSITE_SKILL_PATH, "w", encoding="utf-8") as f:
        json.dump(comp_data, f, ensure_ascii=False, indent=2)
    return {"message": f"Composite skill '{skill.name}' added."}

@app.get("/get_composite_skill")
def get_composite_skill(name: str):
    try:
        with open(COMPOSITE_SKILL_PATH, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
    except FileNotFoundError:
        return {"error": "No composite skills found."}
    if name not in comp_data:
        return {"error": f"Composite skill '{name}' not found."}
    return comp_data[name]

@app.get("/list_composite_skills")
def list_composite_skills():
    try:
        with open(COMPOSITE_SKILL_PATH, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
    except FileNotFoundError:
        return {}
    return comp_data

@app.post("/edit_composite_skill")
def edit_composite_skill(skill: CompositeSkill):
    try:
        with open(COMPOSITE_SKILL_PATH, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
    except FileNotFoundError:
        return {"error": "No composite skills found."}
    if skill.name not in comp_data:
        return {"error": f"Composite skill '{skill.name}' not found."}
    comp_data[skill.name] = skill.dict()
    with open(COMPOSITE_SKILL_PATH, "w", encoding="utf-8") as f:
        json.dump(comp_data, f, ensure_ascii=False, indent=2)
    return {"message": f"Composite skill '{skill.name}' updated."}

@app.post("/delete_composite_skill")
def delete_composite_skill(req: DeleteSkillRequest):
    try:
        with open(COMPOSITE_SKILL_PATH, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
    except FileNotFoundError:
        return {"error": "No composite skills found."}
    if req.skill_name not in comp_data:
        return {"error": f"Composite skill '{req.skill_name}' not found."}
    comp_data.pop(req.skill_name)
    with open(COMPOSITE_SKILL_PATH, "w", encoding="utf-8") as f:
        json.dump(comp_data, f, ensure_ascii=False, indent=2)
    return {"message": f"Composite skill '{req.skill_name}' deleted."}

# 2. 状況ログ・日記モードAPI
class DiaryEntry(BaseModel):
    timestamp: str
    event: str
    detail: Dict[str, Any] = {}

@app.post("/add_diary")
def add_diary(entry: DiaryEntry):
    try:
        with open(DIARY_PATH, "r", encoding="utf-8") as f:
            diary = json.load(f)
    except FileNotFoundError:
        diary = []
    diary.append(entry.dict())
    with open(DIARY_PATH, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=2)
    return {"message": "Diary entry added."}

@app.get("/list_diary")
def list_diary():
    try:
        with open(DIARY_PATH, "r", encoding="utf-8") as f:
            diary = json.load(f)
    except FileNotFoundError:
        diary = []
    return diary

# 3. Skill実行ループ（擬似的なHuman-in-the-loop/自律ループAPI）
class RunLoopRequest(BaseModel):
    user: str
    max_steps: int = 5

@app.post("/run_loop")
def run_loop(req: RunLoopRequest):
    log = []
    current_input = req.user
    for i in range(req.max_steps):
        # スキル計画
        plan_result = plan_skill(PlanSkillRequest(user=current_input, top_k=1))
        skill = plan_result["llm_predicted_skill"]
        log.append({"step": i+1, "input": current_input, "planned_skill": skill})
        # 擬似的に「失敗」させてCriticに反省させる
        error_log = "材料が足りませんでした"
        critic_result = critic_feedback(CriticFeedbackRequest(user=current_input, skill=skill, error_log=error_log))
        log.append({"step": i+1, "critic_feedback": critic_result["critic_feedback"]})
        # Criticのフィードバックを次のinputに
        current_input = critic_result["critic_feedback"]
    return {"run_log": log}

# 既存API（省略: ここまでの内容は前回までの内容と同じ）

# ...（既存のsearch_skill, llama_infer, plan_skill, add_skill, edit_skill, rename_skill, delete_skill, list_skills, get_skill, skill_history, critic_feedback も全て有効です）
