"""
Nutrition Research Searcher — Perplexity 替代
"""

from groq import Groq
import requests
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def search_research(query: str) -> dict:
    if config.PERPLEXITY_API_KEY:
        return _via_perplexity(query)
    return _via_groq(query)


def _via_perplexity(query: str) -> dict:
    headers = {"Authorization": f"Bearer {config.PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": config.PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": f"{config.RD_CONTEXT}\n搜尋2023-2026年科學研究，繁體中文回答，必須附具體文獻。"},
            {"role": "user", "content": f"""搜尋「{query}」的最新科學研究：
## 🔬 研究摘要（3-5個關鍵發現）
## 📊 重要數據與數字
## ⚠️ 研究限制
## 📚 文獻來源（作者、期刊、年份）
## 💬 社群媒體一句話（適合Threads/小紅書，馬來西亞受眾）"""},
        ],
    }
    resp = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return _save(query, data["choices"][0]["message"]["content"], data.get("citations", []))


def _via_groq(query: str) -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = f"""{config.RD_CONTEXT}

請整理「{query}」的科學研究知識（優先2020-2025年）：

## 🔬 研究摘要（3-5個關鍵發現）
## 📊 重要數據與數字
## ⚠️ 研究限制或爭議
## 📚 文獻來源（真實文獻請列出；不確定的標「請到 PubMed 驗證」）
## 💬 社群媒體一句話開頭（馬來西亞華人受眾，Threads/小紅書適用）

注意：內容必須科學正確，不確定的請說明。"""
    completion = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return _save(query, completion.choices[0].message.content, [])


def _save(query: str, content: str, citations: list) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"research_{timestamp}.md"
    text = f"# 研究搜尋：{query}\n\n查詢日期：{datetime.now().strftime('%Y-%m-%d')}\n\n{content}"
    if citations:
        text += "\n\n---\n## 🔗 來源連結\n" + "\n".join(f"{i+1}. {u}" for i, u in enumerate(citations))
    out.write_text(text, encoding="utf-8")
    return {"content": content, "citations": citations, "output_file": str(out)}
