import os
from pathlib import Path
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

GEMINI_MODEL = "gemini-1.5-flash"
PERPLEXITY_MODEL = "sonar"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

RD_CONTEXT = """
你正在協助一位馬來西亞華裔台灣國考營養師（RD）。
專長：控糖減脂、外食攻略、體重管理諮詢
目標受眾：馬來西亞華裔，30-50歲，有控糖/減脂需求
內容平台：Threads、Instagram、小紅書、YouTube、TikTok
主要語言：繁體中文（主）、簡體中文（小紅書）
在地脈絡：馬來西亞hawker food、mamak档、台式便當、夜市外食
"""
