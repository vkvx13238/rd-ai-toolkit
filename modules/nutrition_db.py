"""
Nutrition Database — 本地資料庫 + USDA FoodData Central 備援
資料來源：台灣衛福部食品營養成分資料庫、Malaysian Food Composition Database、USDA
每100g 數值（大馬在地食物標注為每份）
"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

USDA_KEY = "DEMO_KEY"
USDA_BASE = "https://api.nal.usda.gov/fdc/v1"

# ─────────────────────────────────────────────────────────────────────────────
# 本地資料庫（每100g，大馬在地食物標注 per_serving=True 代表每份）
# cal=kcal, carbs/prot/fat/fiber=g
# ─────────────────────────────────────────────────────────────────────────────
_DB = {
    # ── 主食 ─────────────────────────────────────────────────────────────
    "白飯":          {"cal": 130, "carbs": 28.5, "prot": 2.7,  "fat": 0.3, "fiber": 0.4},
    "糙米飯":         {"cal": 122, "carbs": 25.6, "prot": 2.7,  "fat": 1.0, "fiber": 1.8},
    "五穀飯":         {"cal": 118, "carbs": 24.5, "prot": 3.1,  "fat": 1.2, "fiber": 2.5},
    "白麵條(熟)":     {"cal": 138, "carbs": 27.4, "prot": 4.5,  "fat": 1.0, "fiber": 1.0},
    "全麥麵條(熟)":   {"cal": 124, "carbs": 24.0, "prot": 5.0,  "fat": 0.8, "fiber": 3.2},
    "白吐司":         {"cal": 265, "carbs": 49.4, "prot": 8.8,  "fat": 3.2, "fiber": 2.7},
    "全麥吐司":       {"cal": 247, "carbs": 43.1, "prot": 9.7,  "fat": 3.4, "fiber": 7.0},
    "燕麥(乾)":       {"cal": 389, "carbs": 66.3, "prot": 16.9, "fat": 6.9, "fiber": 10.6},
    "燕麥粥":         {"cal": 71,  "carbs": 12.0, "prot": 2.5,  "fat": 1.4, "fiber": 1.7},
    "地瓜":           {"cal": 86,  "carbs": 20.1, "prot": 1.6,  "fat": 0.1, "fiber": 3.0},
    "玉米":           {"cal": 86,  "carbs": 19.0, "prot": 3.2,  "fat": 1.2, "fiber": 2.7},
    "冬粉(熟)":       {"cal": 84,  "carbs": 20.4, "prot": 0.1,  "fat": 0.0, "fiber": 0.2},
    "米粉(熟)":       {"cal": 109, "carbs": 24.8, "prot": 1.6,  "fat": 0.2, "fiber": 0.6},

    # ── 大馬在地食物（每份） ──────────────────────────────────────────────
    "nasi lemak":        {"cal": 644, "carbs": 78.0, "prot": 14.8, "fat": 30.9, "fiber": 3.0, "ps": True, "note": "含椰漿飯+蛋+江魚仔+花生+sambal"},
    "nasi goreng":       {"cal": 322, "carbs": 46.5, "prot": 10.8, "fat": 10.8, "fiber": 2.2, "ps": True},
    "roti canai":        {"cal": 301, "carbs": 43.0, "prot": 6.2,  "fat": 12.1, "fiber": 1.4, "ps": True, "note": "含dal curry"},
    "char kuey teow":    {"cal": 480, "carbs": 70.0, "prot": 17.0, "fat": 16.6, "fiber": 2.7, "ps": True},
    "wonton mee":        {"cal": 380, "carbs": 63.0, "prot": 15.9, "fat": 7.5,  "fiber": 2.3, "ps": True},
    "bak kut teh":       {"cal": 250, "carbs": 7.4,  "prot": 28.0, "fat": 13.1, "fiber": 0.9, "ps": True},
    "laksa":             {"cal": 590, "carbs": 76.0, "prot": 26.0, "fat": 21.0, "fiber": 4.0, "ps": True},
    "hokkien mee":       {"cal": 430, "carbs": 66.4, "prot": 17.0, "fat": 11.6, "fiber": 3.0, "ps": True},
    "chicken rice":      {"cal": 500, "carbs": 65.0, "prot": 30.0, "fat": 14.4, "fiber": 1.8, "ps": True},
    "mixed rice":        {"cal": 511, "carbs": 58.0, "prot": 22.0, "fat": 20.0, "fiber": 3.0, "ps": True, "note": "白飯+2菜1肉"},
    "curry chicken":     {"cal": 200, "carbs": 8.0,  "prot": 18.5, "fat": 11.0, "fiber": 2.0},
    "sambal":            {"cal": 59,  "carbs": 7.5,  "prot": 1.5,  "fat": 2.8,  "fiber": 1.8},
    "fried rice":        {"cal": 163, "carbs": 25.6, "prot": 4.5,  "fat": 5.1,  "fiber": 0.8},
    "mee goreng mamak":  {"cal": 410, "carbs": 62.0, "prot": 14.0, "fat": 12.3, "fiber": 3.2, "ps": True},

    # ── 台式食物（每份） ──────────────────────────────────────────────────
    "滷肉飯":            {"cal": 285, "carbs": 38.5, "prot": 12.3, "fat": 8.5,  "fiber": 1.0, "ps": True},
    "台式便當":          {"cal": 620, "carbs": 74.5, "prot": 28.0, "fat": 21.5, "fiber": 4.5, "ps": True},
    "雞腿便當":          {"cal": 660, "carbs": 72.0, "prot": 32.0, "fat": 22.0, "fiber": 4.0, "ps": True},
    "排骨便當":          {"cal": 680, "carbs": 74.0, "prot": 27.0, "fat": 26.0, "fiber": 3.5, "ps": True},
    "鹹酥雞":            {"cal": 283, "carbs": 16.0, "prot": 22.0, "fat": 14.0, "fiber": 0.5},
    "珍珠奶茶":          {"cal": 498, "carbs": 97.9, "prot": 6.5,  "fat": 9.7,  "fiber": 0,   "ps": True, "note": "700ml含珍珠"},
    "豆花":              {"cal": 56,  "carbs": 7.2,  "prot": 4.2,  "fat": 1.4,  "fiber": 0.3},

    # ── 飲料（每份） ──────────────────────────────────────────────────────
    "teh tarik":         {"cal": 85,  "carbs": 13.4, "prot": 2.8,  "fat": 2.6,  "fiber": 0,   "ps": True},
    "teh o":             {"cal": 30,  "carbs": 7.5,  "prot": 0.2,  "fat": 0.0,  "fiber": 0,   "ps": True},
    "kopi":              {"cal": 68,  "carbs": 10.1, "prot": 2.1,  "fat": 2.5,  "fiber": 0,   "ps": True},
    "kopi o":            {"cal": 25,  "carbs": 6.0,  "prot": 0.5,  "fat": 0.2,  "fiber": 0,   "ps": True},
    "milo":              {"cal": 124, "carbs": 20.8, "prot": 4.2,  "fat": 3.0,  "fiber": 0.5, "ps": True},
    "100plus":           {"cal": 36,  "carbs": 9.0,  "prot": 0.0,  "fat": 0.0,  "fiber": 0,   "ps": True, "note": "325ml"},
    "豆漿(無糖)":        {"cal": 31,  "carbs": 2.2,  "prot": 3.0,  "fat": 1.5,  "fiber": 0.3},
    "豆漿(有糖)":        {"cal": 54,  "carbs": 6.3,  "prot": 3.5,  "fat": 1.8,  "fiber": 0.3},
    "低脂牛奶":          {"cal": 42,  "carbs": 5.0,  "prot": 3.4,  "fat": 1.0,  "fiber": 0},
    "全脂牛奶":          {"cal": 61,  "carbs": 4.7,  "prot": 3.2,  "fat": 3.3,  "fiber": 0},

    # ── 蛋白質（每100g熟重）─────────────────────────────────────────────
    "雞胸肉(熟)":        {"cal": 165, "carbs": 0.0,  "prot": 31.0, "fat": 3.6,  "fiber": 0},
    "雞腿肉(熟)":        {"cal": 185, "carbs": 0.0,  "prot": 24.0, "fat": 9.5,  "fiber": 0},
    "水煮蛋":            {"cal": 155, "carbs": 1.1,  "prot": 13.0, "fat": 11.0, "fiber": 0},
    "荷包蛋":            {"cal": 185, "carbs": 0.5,  "prot": 12.4, "fat": 14.6, "fiber": 0},
    "嫩豆腐":            {"cal": 76,  "carbs": 1.9,  "prot": 8.1,  "fat": 4.2,  "fiber": 0.3},
    "板豆腐":            {"cal": 83,  "carbs": 2.3,  "prot": 8.4,  "fat": 4.8,  "fiber": 0.2},
    "鮭魚(熟)":          {"cal": 208, "carbs": 0.0,  "prot": 20.4, "fat": 13.4, "fiber": 0},
    "鯖魚(熟)":          {"cal": 205, "carbs": 0.0,  "prot": 19.0, "fat": 13.9, "fiber": 0},
    "豬里肌(熟)":        {"cal": 143, "carbs": 0.0,  "prot": 21.8, "fat": 5.9,  "fiber": 0},
    "牛腱(熟)":          {"cal": 175, "carbs": 0.0,  "prot": 28.6, "fat": 6.1,  "fiber": 0},
    "蝦(熟)":            {"cal": 99,  "carbs": 0.9,  "prot": 24.0, "fat": 0.3,  "fiber": 0},
    "毛豆":              {"cal": 122, "carbs": 8.9,  "prot": 11.9, "fat": 5.2,  "fiber": 5.2},
    "鷹嘴豆(熟)":        {"cal": 164, "carbs": 27.4, "prot": 8.9,  "fat": 2.6,  "fiber": 7.6},

    # ── 蔬菜（每100g生重）───────────────────────────────────────────────
    "花椰菜":            {"cal": 34,  "carbs": 7.0,  "prot": 2.8,  "fat": 0.4,  "fiber": 2.6},
    "菠菜":              {"cal": 23,  "carbs": 3.6,  "prot": 2.9,  "fat": 0.4,  "fiber": 2.2},
    "空心菜":            {"cal": 19,  "carbs": 3.1,  "prot": 1.8,  "fat": 0.2,  "fiber": 2.1},
    "豆芽":              {"cal": 30,  "carbs": 5.9,  "prot": 3.0,  "fat": 0.2,  "fiber": 1.8},
    "苦瓜":              {"cal": 17,  "carbs": 3.7,  "prot": 1.0,  "fat": 0.2,  "fiber": 2.8},
    "番茄":              {"cal": 18,  "carbs": 3.9,  "prot": 0.9,  "fat": 0.2,  "fiber": 1.2},
    "小黃瓜":            {"cal": 15,  "carbs": 3.6,  "prot": 0.7,  "fat": 0.1,  "fiber": 0.5},
    "高麗菜":            {"cal": 25,  "carbs": 5.8,  "prot": 1.3,  "fat": 0.1,  "fiber": 2.5},
    "秋葵":              {"cal": 33,  "carbs": 7.5,  "prot": 1.9,  "fat": 0.2,  "fiber": 3.2},
    "絲瓜":              {"cal": 20,  "carbs": 4.4,  "prot": 1.2,  "fat": 0.2,  "fiber": 1.1},

    # ── 水果（每100g）────────────────────────────────────────────────────
    "香蕉":              {"cal": 89,  "carbs": 22.8, "prot": 1.1,  "fat": 0.3,  "fiber": 2.6},
    "蘋果":              {"cal": 52,  "carbs": 13.8, "prot": 0.3,  "fat": 0.2,  "fiber": 2.4},
    "芒果":              {"cal": 60,  "carbs": 15.0, "prot": 0.8,  "fat": 0.4,  "fiber": 1.6},
    "木瓜":              {"cal": 43,  "carbs": 10.8, "prot": 0.5,  "fat": 0.3,  "fiber": 1.7},
    "西瓜":              {"cal": 30,  "carbs": 7.6,  "prot": 0.6,  "fat": 0.2,  "fiber": 0.4},
    "榴槤":              {"cal": 147, "carbs": 27.1, "prot": 1.5,  "fat": 5.3,  "fiber": 3.8},
    "橙子":              {"cal": 47,  "carbs": 11.8, "prot": 0.9,  "fat": 0.1,  "fiber": 2.4},
    "葡萄":              {"cal": 69,  "carbs": 18.1, "prot": 0.6,  "fat": 0.2,  "fiber": 0.9},
    "奇異果":            {"cal": 61,  "carbs": 14.7, "prot": 1.1,  "fat": 0.5,  "fiber": 3.0},

    # ── 堅果/油脂 ─────────────────────────────────────────────────────
    "花生(水煮)":        {"cal": 318, "carbs": 11.4, "prot": 13.5, "fat": 24.6, "fiber": 5.5},
    "杏仁":              {"cal": 579, "carbs": 21.6, "prot": 21.2, "fat": 49.9, "fiber": 12.5},
    "核桃":              {"cal": 654, "carbs": 13.7, "prot": 15.2, "fat": 65.2, "fiber": 6.7},
    "橄欖油":            {"cal": 884, "carbs": 0.0,  "prot": 0.0,  "fat": 100.0,"fiber": 0},
    "椰子油":            {"cal": 892, "carbs": 0.0,  "prot": 0.0,  "fat": 100.0,"fiber": 0},

    # ── 乳製品/其他 ──────────────────────────────────────────────────
    "希臘優格(無糖)":    {"cal": 97,  "carbs": 3.6,  "prot": 9.0,  "fat": 5.0,  "fiber": 0},
    "無糖優格":          {"cal": 61,  "carbs": 4.7,  "prot": 3.5,  "fat": 3.3,  "fiber": 0},
}


def _local_lookup(food_name: str) -> tuple[str, dict] | tuple[None, None]:
    """模糊比對本地資料庫，回傳 (matched_key, data)"""
    key = food_name.lower().strip()
    # 完全比對
    for db_key, data in _DB.items():
        if key == db_key.lower():
            return db_key, data
    # 包含比對
    for db_key, data in _DB.items():
        if key in db_key.lower() or db_key.lower() in key:
            return db_key, data
    return None, None


def _usda_lookup(food_name: str, portion_g: float) -> dict | None:
    """USDA FoodData Central 查詢"""
    try:
        resp = requests.get(
            f"{USDA_BASE}/foods/search",
            params={"query": food_name, "api_key": USDA_KEY, "pageSize": 1,
                    "dataType": ["Foundation", "SR Legacy"]},
            timeout=8,
        )
        if resp.status_code != 200:
            return None
        foods = resp.json().get("foods", [])
        if not foods:
            return None
        food = foods[0]
        n = {item["nutrientName"]: item.get("value", 0) for item in food.get("foodNutrients", [])}
        m = portion_g / 100
        return {
            "name": food["description"],
            "portion_g": round(portion_g),
            "calories": round(n.get("Energy", 0) * m),
            "carbs_g": round(n.get("Carbohydrate, by difference", 0) * m, 1),
            "protein_g": round(n.get("Protein", 0) * m, 1),
            "fat_g": round(n.get("Total lipid (fat)", 0) * m, 1),
            "fiber_g": round(n.get("Fiber, total dietary", 0) * m, 1),
            "source": "USDA",
        }
    except Exception:
        return None


def lookup(food_name: str, portion_g: float = 100) -> dict | None:
    """
    查詢食物營養資訊。
    優先順序：本地資料庫 → USDA FoodData Central
    回傳 dict 或 None（找不到）
    """
    db_key, data = _local_lookup(food_name)
    if data:
        is_per_serving = data.get("ps", False)
        if is_per_serving:
            # 本地資料庫已是每份數值，不乘以 portion_g
            return {
                "name": db_key,
                "portion_g": "每份",
                "calories": data["cal"],
                "carbs_g": data["carbs"],
                "protein_g": data["prot"],
                "fat_g": data["fat"],
                "fiber_g": data["fiber"],
                "source": "本地資料庫",
                "note": data.get("note", ""),
            }
        m = portion_g / 100
        return {
            "name": db_key,
            "portion_g": round(portion_g),
            "calories": round(data["cal"] * m),
            "carbs_g": round(data["carbs"] * m, 1),
            "protein_g": round(data["prot"] * m, 1),
            "fat_g": round(data["fat"] * m, 1),
            "fiber_g": round(data["fiber"] * m, 1),
            "source": "本地資料庫",
            "note": data.get("note", ""),
        }
    return _usda_lookup(food_name, portion_g)


def format_nutrition_table(results: list[dict]) -> str:
    """把多個食物的營養資料格式化成表格"""
    if not results:
        return ""
    lines = ["| 食物 | 份量 | 熱量 | 碳水 | 蛋白質 | 脂肪 | 纖維 | 來源 |",
             "|------|------|------|------|--------|------|------|------|"]
    total = {"calories": 0, "carbs_g": 0.0, "protein_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    for r in results:
        portion = f"{r['portion_g']}g" if isinstance(r["portion_g"], (int, float)) else r["portion_g"]
        lines.append(f"| {r['name']} | {portion} | {r['calories']} kcal | {r['carbs_g']}g | {r['protein_g']}g | {r['fat_g']}g | {r['fiber_g']}g | {r['source']} |")
        if isinstance(r["portion_g"], (int, float)):
            for k in total:
                total[k] += r.get(k, 0)
    lines.append(f"| **合計** | — | **{round(total['calories'])} kcal** | **{round(total['carbs_g'],1)}g** | **{round(total['protein_g'],1)}g** | **{round(total['fat_g'],1)}g** | **{round(total['fiber_g'],1)}g** | — |")
    return "\n".join(lines)
