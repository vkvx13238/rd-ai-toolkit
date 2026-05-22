"""
NotebookLM Prep Tool — NotebookLM 前置處理
把多篇論文/文章整理成 NotebookLM 可直接用的格式
並生成 Podcast 問題清單、關鍵詞摘要
"""

import google.generativeai as genai
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def prepare_for_notebooklm(topic: str, abstracts: str) -> dict:
    model = genai.GenerativeModel(config.GEMINI_MODEL)

    prompt = f"""{config.RD_CONTEXT}

你將幫助我使用 Google NotebookLM 分析以下營養研究文獻。

主題：{topic}
文獻內容：
{abstracts}

請生成：

## 📋 NotebookLM 使用問題清單
（把這些問題逐一輸入到 NotebookLM 的聊天框）

**基礎理解：**
1. [問題1]
2. [問題2]
3. [問題3]

**深入分析：**
4. [問題4]
5. [問題5]

**臨床應用：**
6. [問題6]
7. [問題7]

**內容創作：**
8. 這些研究可以如何用馬來西亞華裔受眾能理解的方式解釋？
9. 哪個發現最適合做成 Threads 貼文？
10. 生成一個適合馬來西亞華裔的案例故事

---

## 🎙️ Podcast Audio Overview 提示
（在 NotebookLM 的 Audio Overview 區塊輸入）

「請重點討論：{topic}的[填入重點]，特別關注[填入關注點]，避免過於技術性，以一般民眾能理解的方式說明。」

---

## 📊 文獻重點摘要

根據提供的文獻內容：

**共同發現：**
**數據亮點：**
**研究限制：**
**臨床意義：**

---

## ✍️ 內容創作素材

**Threads 爆款開頭（3個版本）：**

**小紅書標題（3個版本）：**

**衛教重點（5個，每點可做一張 Canva 圖卡）：**
"""

    response = model.generate_content(prompt)
    content = response.text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"notebooklm_prep_{timestamp}.md"
    out.write_text(f"# NotebookLM 前置準備：{topic}\n\n{content}", encoding="utf-8")
    return {"content": content, "output_file": str(out)}


def run_interactive():
    print("\n📚 NotebookLM 前置準備工具")
    print("=" * 40)
    print("把論文/文章摘要整理好，再丟進 NotebookLM 效率更高！\n")

    topic = input("研究主題（如：鎂與胰島素抵抗）：").strip()
    print("\n貼入論文摘要或重點（可多篇，輸入完後空白行按兩次 Enter）：")
    lines, empty = [], 0
    while True:
        line = input()
        if line == "":
            empty += 1
            if empty >= 2:
                break
        else:
            empty = 0
            lines.append(line)

    abstracts = "\n".join(lines)
    if not abstracts.strip():
        print("❌ 未輸入文獻內容")
        return

    print("\n⏳ 整理中...")
    result = prepare_for_notebooklm(topic, abstracts)
    print("\n" + result["content"])
    print(f"\n✅ 已儲存：{result['output_file']}")
    print("\n📌 下一步：把 .md 檔案上傳到 NotebookLM，再用問題清單逐一提問！")
