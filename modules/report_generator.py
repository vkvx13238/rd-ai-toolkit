"""
Nutrition Education Report Generator — Gamma 替代
一句話主題 → 完整衛教報告（可貼入 Gamma/投影片）
"""

from google import genai
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

REPORT_TYPES = {
    "1": ("衛教報告", "全面的營養衛教文件"),
    "2": ("外食攻略", "特定飲食情境的實用指南"),
    "3": ("迷思破解", "破解常見營養謠言的報告"),
    "4": ("比較分析", "比較不同飲食法或食品"),
    "5": ("族群指南", "針對特定族群的個人化指南"),
}


def generate_report(topic: str, report_type: str = "衛教報告", audience: str = "一般民眾") -> dict:
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    prompt = f"""{config.RD_CONTEXT}

請生成一份完整的營養衛教報告：
主題：{topic}
類型：{report_type}
目標族群：{audience}

用 Markdown 格式輸出（適合直接貼入 Gamma 或轉成投影片）：

---
# {topic}
**{report_type} | {audience} | {datetime.now().strftime('%Y年%m月')}**

## 01 為什麼你需要了解這個？
（數據切入，引發共鳴，2-3段）

## 02 核心知識
（3-5個重點，每點：標題 + 說明 + 在地例子）

## 03 實用行動指南
（5-7個可立即執行的步驟，含馬來西亞/台灣場景）

## 04 常見問題 Q&A
（3個最常被問的問題）

## 05 數字記憶
（3-5個關鍵數字，一眼就能記住）

## 06 關鍵摘要（適合貼入 Canva 圖卡）
（5個重點，每點15字以內）

## 07 參考資料方向
（告訴讀者可用哪些關鍵字到 PubMed/Google Scholar 自行查詢）
---

語氣：專業但親切，適合一般民眾理解。加入馬來西亞在地食物和場景例子。"""

    response = client.models.generate_content(model=config.GEMINI_MODEL, contents=prompt)
    content = response.text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = topic.replace(" ", "_")[:25]
    out = config.OUTPUTS_DIR / f"report_{safe}_{timestamp}.md"
    out.write_text(content, encoding="utf-8")
    return {"report": content, "output_file": str(out)}


def run_interactive():
    print("\n📊 衛教報告生成器（Gamma 替代）")
    print("=" * 40)
    print("報告類型：")
    for k, (name, desc) in REPORT_TYPES.items():
        print(f"  {k}. {name} — {desc}")

    topic = input("\n主題（如：地中海飲食、外食控糖攻略）：").strip()
    type_choice = input("選擇報告類型編號（預設1）：").strip() or "1"
    report_type = REPORT_TYPES.get(type_choice, REPORT_TYPES["1"])[0]
    audience = input("目標族群（預設：一般民眾）：").strip() or "一般民眾"

    print("\n⏳ 生成報告中（約20-30秒）...")
    result = generate_report(topic, report_type, audience)
    print("\n" + result["report"][:600] + "\n\n...（完整報告已儲存）")
    print(f"\n✅ 已儲存：{result['output_file']}")
    print(f"💡 把 {result['output_file']} 的內容貼入 Gamma.app 即可生成投影片！")
