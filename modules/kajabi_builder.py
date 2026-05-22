"""
Kajabi Course Builder
"""

from groq import Groq
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def generate_course_structure(topic: str, target: str = "馬來西亞華裔，30-50歲，有控糖/減脂需求",
                               price: str = "5000 TWD", modules: int = 6) -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = f"""{config.RD_CONTEXT}

請為以下線上課程生成完整架構：
課程主題：{topic}｜目標學員：{target}｜定價：{price}｜單元數：{modules}

## 📚 課程架構
**課程名稱**（有吸引力）｜**副標題**｜**課程時長**

### 單元列表（{modules}個）
每個單元：單元名稱｜學習目標｜課堂內容（3-5主題）｜包含資源

---

## 💰 銷售頁文案
**主標題**｜**副標題**｜**你將學到**（6個成果）｜**適合你，如果…**（3個情境）
**學員見證**（3個範本）｜**課程包含**｜**常見問題**（5個Q&A）｜**行動號召**

---

## 📧 Email 歡迎序列（5封）
Email 1-5：主旨 + 重點內容

---
語言：繁體中文，馬來西亞在地化。"""

    completion = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )
    content = completion.choices[0].message.content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = topic.replace(" ", "_")[:20]
    out = config.OUTPUTS_DIR / f"kajabi_course_{safe}_{timestamp}.md"
    out.write_text(f"# Kajabi 課程架構：{topic}\n\n{content}", encoding="utf-8")
    return {"content": content, "output_file": str(out)}
