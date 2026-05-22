"""
Weekly Menu Generator — Eat This Much 替代
"""

from groq import Groq
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def generate_menu(daily_calories: int, goal: str = "減脂", restrictions: str = "",
                  food_pref: str = "馬來西亞華人飲食", days: int = 7) -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = f"""{config.RD_CONTEXT}

請為以下學員制定 {days} 天菜單：
每日熱量目標：{daily_calories} kcal｜目標：{goal}
飲食限制：{restrictions or '無'}｜飲食偏好：{food_pref}

熱量分配：早餐25%、午餐35%、晚餐30%、點心10%
蛋白質目標：體重60kg × 1.6g = 96g/天
外食選項請標註「外食✓」

每天格式：
### Day X（星期X）
🌅 早餐：食物（份量）｜XXX kcal | C:Xg P:Xg F:Xg
☀️ 午餐：食物（份量）｜XXX kcal | C:Xg P:Xg F:Xg
🌙 晚餐：食物（份量）｜XXX kcal | C:Xg P:Xg F:Xg
🍎 點心：食物（份量）｜XXX kcal
📊 今日合計：XXX kcal | C:Xg P:Xg F:Xg

最後附：
## 🛒 採購清單（按食材分類）
## 💡 使用說明（3-5點）
"""
    completion = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )
    content = completion.choices[0].message.content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"menu_{days}days_{timestamp}.md"
    out.write_text(f"# {days}天菜單｜{daily_calories}kcal｜{goal}\n\n{content}", encoding="utf-8")
    return {"menu": content, "output_file": str(out)}
