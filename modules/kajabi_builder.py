"""
Kajabi Course Builder — Kajabi 替代（架構生成）
輸入課程主題 → 自動生成完整課程架構、銷售頁文案、Email序列
"""

import google.generativeai as genai
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def generate_course_structure(
    topic: str,
    target: str = "馬來西亞華裔，30-50歲，有控糖/減脂需求",
    price: str = "5000 TWD",
    modules: int = 6,
) -> dict:
    model = genai.GenerativeModel(config.GEMINI_MODEL)

    prompt = f"""{config.RD_CONTEXT}

請為以下線上課程生成完整架構（適合上架到 Kajabi）：

課程主題：{topic}
目標學員：{target}
課程定價：{price}
單元數量：{modules} 個單元

請輸出：

## 📚 課程架構

**課程名稱**（有吸引力的完整名稱）
**副標題**（一句話說明價值）
**課程時長**（預估）

### 單元列表（{modules}個）
每個單元：
- 單元名稱
- 學習目標（1句話）
- 課堂內容（3-5個主題）
- 包含資源（講義/食譜/工作表/影片）

---

## 💰 銷售頁文案

**主標題**（解決痛點的強力標題）
**副標題**
**你將學到**（6個具體成果）
**這堂課適合你，如果…**（3個情境）
**學員見證**（3個虛構範本，可替換成真實見證）
**課程包含**（清單）
**常見問題**（5個Q&A）
**行動號召**（購買按鈕文案）

---

## 📧 Email 歡迎序列（5封）

**Email 1（購買後立即）：** 主旨 + 重點內容
**Email 2（Day 3）：** 主旨 + 重點內容
**Email 3（Day 7）：** 主旨 + 重點內容
**Email 4（Day 14）：** 主旨 + 重點內容
**Email 5（Day 30）：** 主旨 + 重點內容

---

語言：繁體中文，馬來西亞在地化，價值主張清晰。"""

    response = model.generate_content(prompt)
    content = response.text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = topic.replace(" ", "_")[:20]
    out = config.OUTPUTS_DIR / f"kajabi_course_{safe}_{timestamp}.md"
    out.write_text(f"# Kajabi 課程架構：{topic}\n\n生成日期：{datetime.now().strftime('%Y-%m-%d')}\n\n{content}", encoding="utf-8")
    return {"content": content, "output_file": str(out)}


def run_interactive():
    print("\n🏫 Kajabi 課程架構生成器")
    print("=" * 40)
    topic = input("課程主題（如：21天控糖飲食計畫、外食也能瘦）：").strip()
    target = input("目標學員（預設：馬來西亞華裔30-50歲控糖/減脂族）：").strip() or "馬來西亞華裔30-50歲，有控糖/減脂需求"
    price = input("定價（預設：5000 TWD）：").strip() or "5000 TWD"
    modules = int(input("單元數（預設6）：").strip() or "6")
    print("\n⏳ 生成課程架構中（約30秒）...")
    result = generate_course_structure(topic, target, price, modules)
    print("\n" + result["content"][:800] + "\n\n...（完整架構已儲存）")
    print(f"\n✅ 已儲存：{result['output_file']}")
    print("💡 將上述架構直接貼入 Kajabi 的課程建立頁面即可！")
