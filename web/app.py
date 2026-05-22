import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, stream_with_context, Response
from werkzeug.utils import secure_filename
import tempfile
import json

import config
from modules.meal_analyzer import analyze_meal
from modules.menu_generator import generate_menu
from modules.research_searcher import search_research
from modules.report_generator import generate_report, REPORT_TYPES
from modules.content_repurposer import repurpose, PLATFORMS
from modules.canva_content import generate_canva_copy, CARD_TYPES
from modules.notebooklm_prep import prepare_for_notebooklm
from modules.kajabi_builder import generate_course_structure
from modules.nutrition_db import lookup, format_nutrition_table

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB upload limit
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


# ── 1. Meal Analyzer ──────────────────────────────────────────────────────────
@app.route("/analyze-meal", methods=["POST"])
def api_analyze_meal():
    if "photo" not in request.files:
        return jsonify({"error": "沒有收到照片"}), 400
    file = request.files["photo"]
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "請上傳 JPG / PNG / WEBP 格式的照片"}), 400

    client_info = request.form.get("client_info", "")

    with tempfile.NamedTemporaryFile(
        suffix=Path(secure_filename(file.filename)).suffix, delete=False
    ) as tmp:
        file.save(tmp.name)
        try:
            result = analyze_meal(tmp.name, client_info)
        finally:
            os.unlink(tmp.name)

    return jsonify({"result": result["analysis"]})


# ── 2. Menu Generator ─────────────────────────────────────────────────────────
@app.route("/generate-menu", methods=["POST"])
def api_generate_menu():
    data = request.get_json()
    try:
        result = generate_menu(
            daily_calories=int(data["calories"]),
            goal=data.get("goal", "減脂"),
            restrictions=data.get("restrictions", ""),
            food_pref=data.get("food_pref", "馬來西亞華人飲食"),
            days=int(data.get("days", 7)),
        )
        return jsonify({"result": result["menu"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 3. Research Searcher ──────────────────────────────────────────────────────
@app.route("/search-research", methods=["POST"])
def api_search_research():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "請輸入研究主題"}), 400
    result = search_research(query)
    return jsonify({"result": result["content"], "citations": result["citations"]})


# ── 4. Report Generator ───────────────────────────────────────────────────────
@app.route("/generate-report", methods=["POST"])
def api_generate_report():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "請輸入主題"}), 400
    result = generate_report(
        topic=topic,
        report_type=data.get("report_type", "衛教報告"),
        audience=data.get("audience", "一般民眾"),
    )
    return jsonify({"result": result["report"]})


# ── 5. Content Repurposer ─────────────────────────────────────────────────────
@app.route("/repurpose-content", methods=["POST"])
def api_repurpose_content():
    data = request.get_json()
    source = data.get("source", "").strip()
    if not source:
        return jsonify({"error": "請輸入原始內容"}), 400
    platforms = data.get("platforms", ["threads", "xiaohongshu", "tiktok"])
    result = repurpose(source, platforms, data.get("content_type", "衛教講座"))
    return jsonify({"results": result["results"]})


# ── 6. Canva Content ──────────────────────────────────────────────────────────
@app.route("/canva-content", methods=["POST"])
def api_canva_content():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "請輸入主題"}), 400
    result = generate_canva_copy(
        topic=topic,
        card_type=data.get("card_type", "小知識卡"),
        num_cards=int(data.get("num_cards", 3)),
    )
    return jsonify({"result": result["content"]})


# ── 7. NotebookLM Prep ────────────────────────────────────────────────────────
@app.route("/notebooklm-prep", methods=["POST"])
def api_notebooklm_prep():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    abstracts = data.get("abstracts", "").strip()
    if not topic or not abstracts:
        return jsonify({"error": "請填入主題和文獻內容"}), 400
    result = prepare_for_notebooklm(topic, abstracts)
    return jsonify({"result": result["content"]})


# ── 8. Kajabi Builder ─────────────────────────────────────────────────────────
@app.route("/kajabi-builder", methods=["POST"])
def api_kajabi_builder():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "請輸入課程主題"}), 400
    result = generate_course_structure(
        topic=topic,
        target=data.get("target", "馬來西亞華裔30-50歲，有控糖/減脂需求"),
        price=data.get("price", "5000 TWD"),
        modules=int(data.get("modules", 6)),
    )
    return jsonify({"result": result["content"]})


# ── 9. Nutrition Lookup ───────────────────────────────────────────────────────
@app.route("/nutrition-lookup", methods=["POST"])
def api_nutrition_lookup():
    data = request.get_json(force=True)
    food = (data.get("food", "") or "").strip()
    portion = float(data.get("portion_g", 100) or 100)
    if not food:
        return jsonify({"error": "請輸入食物名稱"}), 400
    result = lookup(food, portion)
    if not result:
        # 嘗試 unicode normalize 後再查一次
        import unicodedata
        food_nfc = unicodedata.normalize("NFC", food)
        result = lookup(food_nfc, portion)
    if not result:
        return jsonify({"error": f"找不到「{food}」(repr:{repr(food)})，請試試英文名稱"}), 404
    return jsonify({"result": result})


@app.route("/nutrition-debug")
def nutrition_debug():
    from modules.nutrition_db import _DB, _local_lookup
    keys = list(_DB.keys())[:10]
    test_key = "白飯"  # 白飯
    matched_key, matched_data = _local_lookup(test_key)
    return jsonify({
        "first_10_keys": keys,
        "test_lookup_白飯": {"matched": matched_key, "found": matched_data is not None},
        "test_key_repr": repr(test_key),
        "first_db_key_repr": repr(list(_DB.keys())[0]),
        "equal": test_key == list(_DB.keys())[0],
    })


# ── Config ────────────────────────────────────────────────────────────────────
@app.route("/api/config")
def api_config():
    return jsonify({
        "report_types": list(REPORT_TYPES.values()),
        "platforms": {k: v["name"] for k, v in PLATFORMS.items()},
        "card_types": list(CARD_TYPES.values()),
        "has_perplexity": bool(config.PERPLEXITY_API_KEY),
        "has_groq": bool(config.GROQ_API_KEY),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
