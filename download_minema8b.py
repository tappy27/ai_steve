from huggingface_hub import snapshot_download

# MineMA-3-8b-v4のみをダウンロード
snapshot_download(
    repo_id="Aiwensile2/MineMA-8B",
    allow_patterns=["MineMA-3-8b-v4/*"],
    local_dir="./MineMA-3-8b-v4",
    local_dir_use_symlinks=False
)
print("ダウンロード完了: ./MineMA-3-8b-v4")
