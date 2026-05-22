"""
Meal Photo Analyzer — 兩步驟：AI辨識 → 資料庫查精確數值
"""

import base64
import json
from pathlib import Path
from datetime import datetime
from groq import Groq
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from modules.nutrition_db import lookup, format_nutrition_table


def analyze_meal(image_path: str, client_info: str = "") -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)
    path = Path(image_path)
    media_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
    media_type = media_map.get(path.suffix.lower(), "image/jpeg")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data_url = f"data:{media_type};base64,{b64}"

    # ── Step 1：辨識食物清單（JSON 格式）────────────────────────────────
    id_prompt = """你是營養師助理。仔細看這張餐點照片，辨識所有食物，以 JSON array 回答（只回 JSON，不要其他文字）：
[{"zh": "食物中文名", "en": "food english name", "g": 估計克數}]
例：[{"zh": "白飯", "en": "white rice", "g": 200}, {"zh": "雞腿", "en": "chicken leg", "g": 150}]
份量請根據一般食器大小估算。"""

    foods = []
    try:
        id_resp = client.chat.completions.create(
            model=config.GROQ_VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": id_prompt},
            ]}],
            max_tokens=500,
        )
        raw = id_resp.choices[0].message.content.strip()
        # 取出 JSON 部分
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            foods = json.loads(raw[start:end])
    except Exception:
        foods = []

    # ── Step 2：查資料庫取精確數值 ────────────────────────────────────────
    db_results = []
    for item in foods:
        # 先試中文名，再試英文名
        result = lookup(item.get("zh", ""), item.get("g", 100))
        if not result:
            result = lookup(item.get("en", ""), item.get("g", 100))
        if result:
            db_results.append(result)

    nutrition_table = format_nutrition_table(db_results) if db_results else ""

    # ── Step 3：AI 生成完整分析（帶精確數值）───────────────────────────
    nutrition_context = ""
    if nutrition_table:
        nutrition_context = f"\n\n【資料庫查詢結果 — 請直接使用這些精確數值】\n{nutrition_table}\n"

    analysis_prompt = f"""{config.RD_CONTEXT}

你是一位專業營養師，正在分析學員上傳的餐點照片。
{f'學員資訊：{client_info}' if client_info else ''}
{nutrition_context}

請用繁體中文回答，格式如下：

## 🍽️ 餐點辨識
（列出辨識到的食物與估計份量）

## 📊 熱量與營養素
{'（請直接使用上方資料庫的精確數值填入下表）' if db_results else '（AI估算，僅供參考）'}
| 項目 | 數值 | 資料來源 |
|------|------|---------|
| 熱量 | XX kcal | {'本地資料庫/USDA' if db_results else 'AI估算'} |
| 碳水化合物 | XXg | |
| 蛋白質 | XXg | |
| 脂肪 | XXg | |
| 膳食纖維 | XXg | |

## ✅ 這餐的優點（2-3點）

## ⚠️ 需要注意（2-3點）

## 💡 營養師建議（1-2個具體建議）

## 🩺 控糖評估
血糖衝擊：低/中/高｜理由一句話
"""

    analysis_resp = client.chat.completions.create(
        model=config.GROQ_VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data_url}},
            {"type": "text", "text": analysis_prompt},
        ]}],
        max_tokens=1500,
    )
    analysis = analysis_resp.choices[0].message.content

    # 如果有資料庫結果，附在最後
    if nutrition_table:
        analysis += f"\n\n---\n## 📋 營養資料庫明細（精確數值）\n{nutrition_table}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"meal_analysis_{timestamp}.md"
    out.write_text(f"# 餐點分析\n\n{analysis}", encoding="utf-8")
    return {"analysis": analysis, "output_file": str(out)}
