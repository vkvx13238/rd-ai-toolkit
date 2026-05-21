"""
Weekly Menu Generator — Eat This Much 替代
輸入熱量目標 → 自動生成 N 天菜單＋採購清單
"""

import anthropic
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def generate_menu(
    daily_calories: int,
    goal: str = "減脂",
    restrictions: str = "",
    food_pref: str = "馬來西亞華人飲食",
    days: int = 7,
) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    prompt = f"""{config.RD_CONTEXT}

請為以下學員制定 {days} 天菜單：

每日熱量目標：{daily_calories} kcal
目標：{goal}
飲食限制：{restrictions or '無'}
飲食偏好：{food_pref}

熱量分配：早餐25%、午餐35%、晚餐30%、點心10%
蛋白質目標：體重60kg × 1.6g = 96g/天
優先使用當地常見食材，外食選項請標註「外食✓」

每天格式：
### Day X（星期X）
🌅 早餐：食物（份量）｜XXX kcal | C:Xg P:Xg F:Xg
☀️ 午餐：食物（份量）｜XXX kcal | C:Xg P:Xg F:Xg
🌙 晚餐：食物（份量）｜XXX kcal | C:Xg P:Xg F:Xg
🍎 點心：食物（份量）｜XXX kcal
📊 今日合計：XXX kcal | C:Xg P:Xg F:Xg

最後附：
## 🛒 採購清單（按食材分類）

## 💡 使用說明（3-5點重要提醒）
"""

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"menu_{days}days_{timestamp}.md"
    out.write_text(
        f"# {days}天菜單｜{daily_calories}kcal｜{goal}\n\n生成日期：{datetime.now().strftime('%Y-%m-%d')}\n\n{content}",
        encoding="utf-8",
    )
    return {"menu": content, "output_file": str(out)}


def run_interactive():
    print("\n📅 週菜單生成器（Eat This Much 替代）")
    print("=" * 40)
    cal = int(input("每日熱量目標（kcal）：").strip())
    goal = input("目標（減脂/增肌/控糖/維持，預設減脂）：").strip() or "減脂"
    restrictions = input("飲食限制（如：不吃豬肉，或留空）：").strip()
    pref = input("飲食偏好（預設：馬來西亞華人飲食）：").strip() or "馬來西亞華人飲食"
    days = int(input("天數（預設7）：").strip() or "7")
    print("\n⏳ 生成菜單中（約20秒）...")
    result = generate_menu(cal, goal, restrictions, pref, days)
    print("\n" + result["menu"][:800] + "\n\n...（完整菜單已儲存）")
    print(f"\n✅ 已儲存：{result['output_file']}")
