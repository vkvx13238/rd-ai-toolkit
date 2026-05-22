"""
Weekly Menu Generator — AI 生成食物清單 → 資料庫查精確營養 → 組合菜單
"""

import json
from groq import Groq
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from modules.nutrition_db import lookup


def generate_menu(daily_calories: int, goal: str = "減脂", restrictions: str = "",
                  food_pref: str = "馬來西亞華人飲食", days: int = 7) -> dict:
    client = Groq(api_key=config.GROQ_API_KEY)

    # ── Step 1：生成結構化食物清單（JSON）────────────────────────────────
    plan_prompt = f"""{config.RD_CONTEXT}

為以下學員制定 {days} 天飲食計畫：
- 每日熱量：{daily_calories} kcal｜目標：{goal}
- 飲食限制：{restrictions or '無'}｜偏好：{food_pref}
- 熱量分配：早餐25%｜午餐35%｜晚餐30%｜點心10%

只輸出 JSON，格式：
{{"days": [{{"day": 1, "breakfast": [{{"zh": "食物名", "en": "food name", "g": 克數}}], "lunch": [...], "dinner": [...], "snack": [...]}}]}}

每餐 2-4 種食物，份量合理，符合馬來西亞在地飲食。只輸出 JSON，不要其他文字。"""

    days_data = []
    try:
        plan_resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": plan_prompt}],
            max_tokens=3000,
        )
        raw = plan_resp.choices[0].message.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            days_data = json.loads(raw[start:end]).get("days", [])
    except Exception:
        days_data = []

    # ── Step 2：查資料庫，計算精確營養 ─────────────────────────────────
    def lookup_foods(items: list) -> tuple[list, dict]:
        results = []
        total = {"calories": 0, "carbs": 0.0, "protein": 0.0, "fat": 0.0, "fiber": 0.0}
        for item in items:
            r = lookup(item.get("zh", ""), item.get("g", 100)) or \
                lookup(item.get("en", ""), item.get("g", 100))
            name = item.get("zh", item.get("en", "未知"))
            g = item.get("g", 100)
            if r:
                results.append(f"{name}({g}g)｜{r['calories']}kcal C:{r['carbs_g']}g P:{r['protein_g']}g F:{r['fat_g']}g [{'資料庫✓' if '本地' in r['source'] else 'USDA✓'}]")
                total["calories"] += r["calories"]
                total["carbs"] += r["carbs_g"]
                total["protein"] += r["protein_g"]
                total["fat"] += r["fat_g"]
                total["fiber"] += r["fiber_g"]
            else:
                results.append(f"{name}({g}g)｜[AI估算]")
        return results, total

    # ── Step 3：組合完整菜單文字 ────────────────────────────────────────
    WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]
    menu_lines = [f"# {days}天菜單｜{daily_calories}kcal｜{goal}\n",
                  f"> 生成日期：{datetime.now().strftime('%Y-%m-%d')}｜營養數值來源：本地資料庫/USDA（✓）或AI估算\n"]

    if days_data:
        for d in days_data[:days]:
            day_num = d.get("day", 1)
            weekday = WEEKDAYS[(day_num - 1) % 7]
            bf, bf_total = lookup_foods(d.get("breakfast", []))
            lu, lu_total = lookup_foods(d.get("lunch", []))
            di, di_total = lookup_foods(d.get("dinner", []))
            sn, sn_total = lookup_foods(d.get("snack", []))

            day_total_cal = bf_total["calories"] + lu_total["calories"] + di_total["calories"] + sn_total["calories"]
            day_total_c = round(bf_total["carbs"] + lu_total["carbs"] + di_total["carbs"] + sn_total["carbs"], 1)
            day_total_p = round(bf_total["protein"] + lu_total["protein"] + di_total["protein"] + sn_total["protein"], 1)
            day_total_f = round(bf_total["fat"] + lu_total["fat"] + di_total["fat"] + sn_total["fat"], 1)

            menu_lines.append(f"\n### Day {day_num}（星期{weekday}）")
            menu_lines.append(f"🌅 **早餐**｜{bf_total['calories']} kcal")
            menu_lines.extend([f"   · {x}" for x in bf])
            menu_lines.append(f"☀️ **午餐**｜{lu_total['calories']} kcal")
            menu_lines.extend([f"   · {x}" for x in lu])
            menu_lines.append(f"🌙 **晚餐**｜{di_total['calories']} kcal")
            menu_lines.extend([f"   · {x}" for x in di])
            menu_lines.append(f"🍎 **點心**｜{sn_total['calories']} kcal")
            menu_lines.extend([f"   · {x}" for x in sn])
            menu_lines.append(f"📊 **今日合計：{day_total_cal} kcal｜C:{day_total_c}g P:{day_total_p}g F:{day_total_f}g**")
    else:
        # Fallback：資料庫查詢失敗，AI 直接生成
        fallback_prompt = f"""{config.RD_CONTEXT}

請為以下學員制定 {days} 天菜單：
每日熱量：{daily_calories} kcal｜目標：{goal}
飲食限制：{restrictions or '無'}｜偏好：{food_pref}

每天格式：
### Day X（星期X）
🌅 早餐：食物（份量）｜XX kcal | C:Xg P:Xg F:Xg
☀️ 午餐：食物（份量）｜XX kcal | C:Xg P:Xg F:Xg
🌙 晚餐：食物（份量）｜XX kcal | C:Xg P:Xg F:Xg
🍎 點心：食物（份量）｜XX kcal
📊 今日合計：XX kcal | C:Xg P:Xg F:Xg"""
        fallback_resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": fallback_prompt}],
            max_tokens=4000,
        )
        menu_lines.append(fallback_resp.choices[0].message.content)
        menu_lines.append("\n> ⚠️ 本次使用 AI 估算數值，精確度較低")

    content = "\n".join(menu_lines)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = config.OUTPUTS_DIR / f"menu_{days}days_{timestamp}.md"
    out.write_text(content, encoding="utf-8")
    return {"menu": content, "output_file": str(out)}
