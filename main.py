"""
RD AI Toolkit — 營養師 AI 工作系統
對應工具：Fomofly / Lifesum / Eat This Much / Perplexity / Gamma / Canva / NotebookLM / Kajabi
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 啟動時檢查 API Key
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("❌ 請設定 ANTHROPIC_API_KEY")
    print("   方法：複製 .env.example 為 .env，填入你的 API Key")
    sys.exit(1)


MENU = """
╔══════════════════════════════════════════╗
║       🥗 RD AI Toolkit  v1.0            ║
║       營養師 AI 工作系統                  ║
╠══════════════════════════════════════════╣
║  1. 📸  餐點照片分析    （Lifesum）       ║
║  2. 📅  週菜單生成      （Eat This Much） ║
║  3. 🔬  最新營養研究    （Perplexity）    ║
║  4. 📊  衛教報告生成    （Gamma）         ║
║  5. ✂️  講座內容改寫    （Fomofly文字版） ║
║  6. 🎨  Canva圖卡文案   （Canva）        ║
║  7. 📚  NotebookLM準備  （NotebookLM）   ║
║  8. 🏫  課程架構生成    （Kajabi）        ║
║                                          ║
║  Q. 離開                                 ║
╚══════════════════════════════════════════╝
"""


def main():
    print(MENU)

    while True:
        choice = input("選擇功能（1-8 或 Q）：").strip().upper()

        if choice == "1":
            from modules.meal_analyzer import run_interactive
            run_interactive()

        elif choice == "2":
            from modules.menu_generator import run_interactive
            run_interactive()

        elif choice == "3":
            from modules.research_searcher import run_interactive
            run_interactive()

        elif choice == "4":
            from modules.report_generator import run_interactive
            run_interactive()

        elif choice == "5":
            from modules.content_repurposer import run_interactive
            run_interactive()

        elif choice == "6":
            from modules.canva_content import run_interactive
            run_interactive()

        elif choice == "7":
            from modules.notebooklm_prep import run_interactive
            run_interactive()

        elif choice == "8":
            from modules.kajabi_builder import run_interactive
            run_interactive()

        elif choice == "Q":
            print("\n👋 再見！")
            break

        else:
            print("❓ 請輸入 1-8 或 Q")

        print("\n" + "=" * 44)
        input("按 Enter 返回主選單...")
        print(MENU)


if __name__ == "__main__":
    main()
