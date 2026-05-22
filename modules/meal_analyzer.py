"""
Meal Photo Analyzer — Lifesum 替代
學員上傳餐點照片 → 熱量/巨量營養素/控糖評估
"""

import base64
from pathlib import Path
from datetime import datetime
from groq import Groq
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def analyze_meal(image_path: str, client_info: str = "") -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)

    path = Path(image_path)
    media_type_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }
    media_type = media_type_map.get(path.suffix.lower(), "image/jpeg")
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    data_url = f"data:{media_type};base64,{image_data}"

    prompt = f"""{config.RD_CONTEXT}

你是一位專業營養師，正在分析學員上傳的餐點照片。
{f'學員資訊：{client_info}' if client_info else ''}

請分析照片中的餐點，用繁體中文回答：

## 🍽️ 餐點辨識
辨識到的食物（份量估計、烹調方式）

## 📊 熱量與營養素估算
| 項目 | 數值 |
|------|------|
| 熱量 | XX–XX kcal |
| 碳水化合物 | XXg |
| 蛋白質 | XXg |
| 脂肪 | XXg |
| 膳食纖維 | XXg |

## ✅ 這餐的優點（2-3點）

## ⚠️ 需要注意（2-3點）

## 💡 營養師建議
如何讓這餐更均衡（1-2個具體建議）

## 🩺 控糖評估
血糖衝擊：低/中/高｜理由一句話
"""

    completion = client.chat.completions.create(
        model=config.GROQ_VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ],
        }],
        max_tokens=1500,
    )

    analysis = completion.choices[0].message.content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"meal_analysis_{timestamp}.md"
    out.write_text(
        f"# 餐點分析報告\n\n**時間：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{analysis}",
        encoding="utf-8",
    )
    return {"analysis": analysis, "output_file": str(out)}
