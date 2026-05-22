"""
NotebookLM Prep Tool
"""

from groq import Groq
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def prepare_for_notebooklm(topic: str, abstracts: str) -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = f"""{config.RD_CONTEXT}

主題：{topic}
文獻內容：
{abstracts}

請生成：

## 📋 NotebookLM 使用問題清單

**基礎理解：**
1. [問題1] 2. [問題2] 3. [問題3]

**深入分析：**
4. [問題4] 5. [問題5]

**臨床應用：**
6. [問題6] 7. [問題7]

**內容創作：**
8. 這些研究如何用馬來西亞華裔受眾能理解的方式解釋？
9. 哪個發現最適合做成 Threads 貼文？
10. 生成一個適合馬來西亞華裔的案例故事

---

## 🎙️ Podcast Audio Overview 提示

---

## 📊 文獻重點摘要
**共同發現：** **數據亮點：** **研究限制：** **臨床意義：**

---

## ✍️ 內容創作素材
**Threads 爆款開頭（3個版本）：**
**小紅書標題（3個版本）：**
**衛教重點（5個，每點可做一張 Canva 圖卡）：**
"""
    completion = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
    )
    content = completion.choices[0].message.content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"notebooklm_prep_{timestamp}.md"
    out.write_text(f"# NotebookLM 前置準備：{topic}\n\n{content}", encoding="utf-8")
    return {"content": content, "output_file": str(out)}
