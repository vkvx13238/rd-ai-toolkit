"""
Canva Content Generator — Canva 替代（文案部分）
生成圖卡文案，直接貼入 Canva 即用
"""

import google.generativeai as genai
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
    model = genai.GenerativeModel(config.GEMINI_MODEL)

    prompt = f"""{config.RD_CONTEXT}

生成 {num_cards} 張 Canva 圖卡文案，主題：「{topic}」
類型：{card_type}

每張圖卡格式：
---
**圖卡 [N]**
📌 主標題（≤12字，抓眼球）
📝 副標題（≤20字）
💡 內容要點：
  · 要點1（≤15字）
  · 要點2（≤15字）
  · 要點3（≤15字）
🔢 關鍵數字/金句（最好記的那個）
🏷️ 適用Hashtag：3個
🎨 建議配色：（如：綠色系/珊瑚橘/深藍白）
---

要求：
- 文字精簡有力，適合視覺圖卡
- 加入馬來西亞在地食物例子
- 含1個英文術語/數字增加可信度
- 繁體中文為主"""

    response = model.generate_content(prompt)
    content = response.text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"canva_{timestamp}.md"
    out.write_text(f"# Canva 圖卡文案：{topic}｜{card_type}\n\n{content}", encoding="utf-8")
    return {"content": content, "output_file": str(out)}


def run_interactive():
    print("\n🎨 Canva 圖卡文案生成")
    print("=" * 40)
    for k, (name, desc) in CARD_TYPES.items():
        print(f"  {k}. {name} — {desc}")

    topic = input("\n主題（如：蛋白質、大馬外食控糖）：").strip()
    type_choice = input("圖卡類型編號（預設2）：").strip() or "2"
    card_type = CARD_TYPES.get(type_choice, CARD_TYPES["2"])[0]
    num = int(input("張數（預設3）：").strip() or "3")

    print("\n⏳ 生成文案中...")
    result = generate_canva_copy(topic, card_type, num)
    print("\n" + result["content"])
    print(f"\n✅ 已儲存：{result['output_file']}")
    print("📋 複製以上文案，直接貼入 Canva 圖卡！")
