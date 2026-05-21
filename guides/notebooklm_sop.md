# NotebookLM 使用 SOP — 論文變 Podcast

## 什麼是 NotebookLM？
Google 出品的 AI 筆記工具，可上傳多份文件後：
- 問任何問題（AI 只從你的文件回答，不亂編）
- 一鍵生成 Audio Overview（兩個 AI 主持人像談話節目一樣討論）
- 支援中文（包括繁體/簡體）

---

## 標準工作流程

### 流程一：論文研究 → Podcast

**Step 1：找論文（用功能 3 搜尋後）**
```
PubMed → 搜尋關鍵字 → 下載 PDF 或複製 Abstract
```

**Step 2：用本 Toolkit 預處理（功能 7）**
```
python main.py → 選 7 → 貼入摘要
→ 得到：NotebookLM問題清單 + Podcast提示詞
```

**Step 3：上傳到 NotebookLM**
1. 前往 [notebooklm.google.com](https://notebooklm.google.com)
2. 新增 Notebook
3. 上傳來源（最多 50 份）：
   - PDF 論文
   - 功能 7 生成的 .md 文件
   - YouTube 影片連結
   - 貼入文字

**Step 4：生成 Audio Overview**
1. 點右側「Audio Overview」
2. 在「Customize」框貼入功能 7 生成的 Podcast 提示詞：
   ```
   請重點討論：[主題]的[重點]，
   特別關注[關注點]，
   以馬來西亞華裔一般民眾能理解的方式說明，
   舉生活化的例子。
   ```
3. 點「Generate」等待 2-3 分鐘
4. 下載 MP3

**Step 5：用法**
- 剪輯成 Podcast 片段上傳
- 用作內部學習資料
- 製作成圖文貼文的音頻版

---

## 流程二：衛教素材整理

上傳：
- 20篇你收藏的論文
- 你的舊貼文截圖（複製文字）
- 衛教講義 PDF

問法範例：
- 「從這些文件中，找出5個最適合馬來西亞華裔受眾的控糖重點」
- 「哪個研究發現最令人驚訝？用一句話說明」
- 「整合這些資料，生成一份外食攻略」

---

## 實用提示

| 情境 | NotebookLM 使用方式 |
|------|---------------------|
| 備考/面試 | 上傳教科書章節 → 問題演練 |
| 客戶衛教備課 | 上傳相關論文 → 生成摘要 |
| 內容創作 | 論文 → Audio → 剪成Reels |
| 競品分析 | 上傳競品貼文截圖文字 → 分析風格 |
