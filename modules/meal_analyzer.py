"""
Meal Photo Analyzer — Lifesum 替代
學員上傳餐點照片 → 熱量/巨量營養素/控糖評估
"""

from google import genai
import PIL.Image
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def analyze_meal(image_path: str, client_info: str = "") -> dict:
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    image = PIL.Image.open(image_path)

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

## ✅ 這餐的優點
（2-3點）

## ⚠️ 需要注意
（2-3點）

## 💡 營養師建議
如何讓這餐更均衡（1-2個具體建議）
下一餐搭配提醒

## 🩺 控糖評估
血糖衝擊：低/中/高｜理由一句話
"""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=[image, prompt],
    )
    analysis = response.text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"meal_analysis_{timestamp}.md"
    out.write_text(
        f"# 餐點分析報告\n\n**時間：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{analysis}",
        encoding="utf-8",
    )
    return {"analysis": analysis, "output_file": str(out)}


def run_interactive():
    print("\n📸 餐點照片分析（Lifesum 替代）")
    print("=" * 40)
    image_path = input("照片路徑（拖曳到終端機）：").strip().strip('"')
    if not Path(image_path).exists():
        print(f"❌ 找不到：{image_path}")
        return
    client_info = input("學員資訊（選填，如：糖尿病、目標1500kcal）：").strip()
    print("\n⏳ 分析中...")
    result = analyze_meal(image_path, client_info)
    print("\n" + result["analysis"])
    print(f"\n✅ 已儲存：{result['output_file']}")
