"""
Content Repurposer — Fomofly 替代（文字版）
衛教講座大綱/文字稿 → 各平台爆款貼文
"""

from google import genai
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

PLATFORMS = {
    "1": {
        "key": "threads",
        "name": "Threads",
        "limit": 500,
        "formula": "本地產品/現象切入 → 打破認知 → 營養師補完整 → 互動提問",
        "note": "口語有觀點，結尾留問題讓人想回覆",
    },
    "2": {
        "key": "xiaohongshu",
        "name": "小紅書",
        "limit": 1000,
        "formula": "痛點標題 → 科學解釋 → 實用清單 → 保存CTA",
        "note": "加大馬本地錨點，emoji豐富，繁簡都要考慮",
    },
    "3": {
        "key": "tiktok",
        "name": "TikTok 口播腳本",
        "limit": 2000,
        "formula": "開頭3秒驚人聲明 → 問題/故事 → 解決方案 → 行動號召",
        "note": "按秒分段，節奏快，加停頓提示",
    },
    "4": {
        "key": "youtube",
        "name": "YouTube 影片腳本",
        "limit": 5000,
        "formula": "Hook(15秒) → 問題(1分鐘) → 解決方案 → 例子 → 總結 → 訂閱CTA",
        "note": "詳細腳本，加關鍵字，章節時間戳",
    },
    "5": {
        "key": "instagram",
        "name": "Instagram",
        "limit": 2200,
        "formula": "視覺說明 → 核心價值 → 保存提醒 → Hashtag",
        "note": "加馬來西亞本地標籤",
    },
}


def repurpose(source: str, platform_keys: list, content_type: str = "衛教講座") -> dict:
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    results = {}

    for p in platform_keys:
        platform = next((v for v in PLATFORMS.values() if v["key"] == p), PLATFORMS["1"])
        prompt = f"""{config.RD_CONTEXT}

將以下「{content_type}」改寫成 {platform['name']} 爆款貼文：

原始內容：
{source}

平台要求：
- 字數上限：{platform['limit']} 字
- 爆款公式：{platform['formula']}
- 風格備註：{platform['note']}
- 必須加入馬來西亞在地食物/場景/用語
- 開頭第一句必須超強（3秒抓眼球）
- 內容科學正確，加入具體數字或研究佐證
- 結尾有明確 CTA（保存/預約/留言/分享）
{'- 結尾加10個相關Hashtag（含馬來西亞本地標籤）' if p in ['xiaohongshu', 'instagram'] else ''}

直接輸出貼文內容，不需要說明。"""

        response = client.models.generate_content(model=config.GEMINI_MODEL, contents=prompt)
        results[p] = {"platform": platform["name"], "content": response.text}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"repurposed_{timestamp}.md"
    text = f"# 內容改寫：{content_type}\n\n生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n## 原始內容\n{source}\n\n---\n\n"
    for data in results.values():
        text += f"## {data['platform']}\n\n{data['content']}\n\n---\n\n"
    out.write_text(text, encoding="utf-8")

    return {"results": results, "output_file": str(out)}


def run_interactive():
    print("\n✂️ 衛教內容改寫（Fomofly 文字版替代）")
    print("=" * 40)
    print("支援平台：")
    for k, v in PLATFORMS.items():
        print(f"  {k}. {v['name']}")

    print("\n輸入原始內容（講座重點/大綱/文字稿）")
    print("輸入完畢後，空白行按兩次 Enter：")
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

    source = "\n".join(lines)
    if not source.strip():
        print("❌ 未輸入內容")
        return

    platform_input = input("選擇平台編號（逗號分隔，如：1,2,3，預設1,2,3）：").strip() or "1,2,3"
    selected_nums = [x.strip() for x in platform_input.split(",")]
    platform_keys = [PLATFORMS[n]["key"] for n in selected_nums if n in PLATFORMS]

    content_type = input("內容類型（預設：衛教講座）：").strip() or "衛教講座"

    print(f"\n⏳ 生成 {len(platform_keys)} 個平台的貼文中...")
    result = repurpose(source, platform_keys, content_type)

    for data in result["results"].values():
        print(f"\n{'='*40}\n📱 {data['platform']}\n{'='*40}")
        print(data["content"])

    print(f"\n✅ 已儲存：{result['output_file']}")
