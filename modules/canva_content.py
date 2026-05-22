"""
Canva Content Generator — Canva 替代（文案部分）
"""

from groq import Groq
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

CARD_TYPES = {
    "1": ("食物對比卡", "比較兩種食物的營養差異，打破迷思"),
    "2": ("小知識卡", "單一營養知識精華，數字視覺化"),
    "3": ("外食攻略卡", "特定場景的選擇攻略（mamak/便當店/飲料店）"),
    "4": ("迷思破解卡", "❌真相✅的對比格式"),
    "5": ("週計畫卡", "7天行動計畫或Tracker格式"),
    "6": ("數字記憶卡", "關鍵營養數字，一眼記住"),
}


def generate_canva_copy(topic: str, card_type: str = "小知識卡", num_cards: int = 3) -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = f"""{config.RD_CONTEXT}

生成 {num_cards} 張 Canva 圖卡文案，主題：「{topic}」，類型：{card_type}

每張格式：
---
**圖卡 [N]**
📌 主標題（≤12字）
📝 副標題（≤20字）
💡 要點：
  · 要點1（≤15字）
  · 要點2（≤15字）
  · 要點3（≤15字）
🔢 關鍵數字/金句
🏷️ Hashtag：3個
🎨 建議配色
---

要求：文字精簡，加入馬來西亞在地例子，含英文術語/數字增加可信度，繁體中文為主"""

    completion = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    content = completion.choices[0].message.content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"canva_{timestamp}.md"
    out.write_text(f"# Canva 圖卡文案：{topic}｜{card_type}\n\n{content}", encoding="utf-8")
    return {"content": content, "output_file": str(out)}
