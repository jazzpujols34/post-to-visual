# Knowledge: Anti-AI Writing Guide

> Reference checklist for avoiding AI-sounding prose in English AND Chinese.
> Source files: `X-reference-post/#8 - Anti_AI_writing.md` (English), `#9 - Anti_AI_writing_Chinese.md` (中文)
> Read this before: writing articles, blog posts, documentation, or any public-facing prose.

## Banned Vocabulary

These words are statistically overused by LLMs. One or two may be fine; clusters of them are a dead giveaway.

**Never use (find a specific alternative every time):**
delve, crucial, pivotal, tapestry (figurative), testament, landscape (figurative), vibrant, intricate/intricacies, underscore (as verb), showcase, fostering, garner, meticulous/meticulously, bolstered, enduring, interplay, enhance (prefer "improve" or be specific), additionally (sentence opener), align with

**Use sparingly (only when literally accurate):**
key (as adjective), valuable, highlight (as verb), emphasizing, crucial, significant

## Structural Tells to Avoid

### Puffery & Significance Inflation
- Don't puff up importance: "stands as a testament to", "marks a pivotal moment", "reflects broader trends"
- Don't use travel-guide language: "nestled in", "in the heart of", "boasts a", "rich cultural heritage", "diverse array"
- Don't add "broader context" sentences that could apply to anything

### Superficial Analysis (the "-ing" Trap)
Bad: "The team migrated to microservices, **highlighting** the importance of scalability."
Good: "The team migrated to microservices because the monolith couldn't handle peak traffic."

The pattern: tacking on a present-participle phrase (highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, contributing to, fostering, encompassing) that adds no real information. Kill these on sight.

### Fake Balance
- "Not just X, but also Y" — sounds like clearing up a misconception nobody had
- "Despite its [positive thing], [subject] faces challenges..." — the formulaic challenges-and-future-prospects sandwich
- "It's not about X, it's about Y" — performative reframing

### Rule of Three
Bad: "a vibrant, dynamic, and transformative initiative"
AI loves triplet adjectives/phrases. Use one precise word instead of three vague ones.

### Elegant Variation (Synonym Cycling)
Bad: Calling the same thing "the framework", "the tool", "the platform", "the solution" across consecutive sentences to avoid repetition.
Good: Just repeat the word. Readers don't mind. Forced synonyms are disorienting.

### Copula Avoidance
Bad: "serves as", "stands as", "marks", "represents", "holds the distinction of being"
Good: "is"

### Vague Attribution
Bad: "Experts argue...", "Industry reports suggest...", "Observers have noted..."
Good: Name the expert. Cite the report. Or don't make the claim.

## Formatting Tells

- **Overuse of bold** — don't bold every key term like a slide deck
- **Em dash overuse** — AI uses em dashes where commas or periods work fine. Use sparingly.
- **Title Case Headings** — use sentence case for article headings
- **Emoji in headings** — never (also covered by UI/UX rule)
- **Inline-header bullet lists** — "**Bold header:** description" for every bullet. Mix it up.
- **Unnecessary tables** — don't tabularize things that read better as prose

## Tone Tells

- "I hope this helps" / "Let me know if you'd like..." / "Certainly!" — collaborative leaking from chat mode
- "In this article, we will explore..." — don't announce what you're about to do, just do it
- Clearing throat before every section — no "Let's dive in" / "Now let's turn to" / "Moving on to"

## 中文 AI 寫作特徵（繁體中文專用）

Source: Wikipedia 中文版「AI生成文的特徵」+ 朱宥勳「AI腔」分析

### 中文禁用句型

**否定平行結構（最大 AI 腔）：**
- 「這不是……而是……」
- 「不僅是……更是……」
- 「並非……而是……」

這些句型做的是「區分」和「定義」，看似有深度但常常內容空洞。偶爾用可以，連續出現就是 AI。

**排比句濫用：**
- 三段式排比（「形容詞、形容詞、形容詞」或「短語、短語、短語」）
- 中文 AI 特別愛用工整的三段排比讓文章看起來結構嚴謹

Bad: 「其內容風格、價值立場與表述方式的評價差異」
Good: 挑最重要的一個講清楚就好

### 中文禁用詞彙/短語

**重要性膨脹：**
- 「具有深遠的意義」「在該領域扮演關鍵角色」「對……做出重要貢獻」
- 「是……的靈魂人物」「是……的關鍵推手」
- 「顯示其於產業中具一定能見度」

**模糊歸因：**
- 「據多家媒體報導」「學界普遍認為」「相關人士指出」
- 「被引用於媒體評論與文化研究中」
→ 跟英文一樣：說出是哪家媒體、哪位學者，否則刪掉

**宣傳腔：**
- 旅遊指南式語言：「擁有豐富的文化底蘊」「座落於……」「享有……美譽」
- 「展現了……的決心」「彰顯了……的重要性」「體現了……的精神」

**協作式洩漏（從聊天模式帶出的痕跡）：**
- 「希望這對你有幫助」「你說得沒錯」「當然可以」
- 「你希望我……嗎？」

### 中文格式特徵

- **粗體濫用：** 把每個關鍵詞都加粗，像投影片而非文章
- **列表式行文：** 每個項目都是「**粗體標題：** 描述」格式
- **不成節的編號段落：** 把散文拆成 1. 2. 3. 4. 5. 6. 配粗體小標題，看似結構化實則空洞
- **Markdown 語法外洩：** `**粗體**` `# 標題` 出現在不該出現的地方

### 中文內容特徵

- **忽略細節、語調籠統正面：** AI 傾向產出統計上最常見的正向描述，省略具體、不尋常的事實
- **「前景」公式：** 「儘管……有其意義，但面臨的挑戰有……」結尾加正面展望。刪掉整段。
- **過度強調歷史意義：** 即使是經緯度、人口數據這種平淡資訊，AI 也會加上「具有重要意義」
- **免責聲明洩漏：** 「作為一位機器人」「截至我的訓練資料」「相關資訊有限」

### 中文寫作的正確做法

- 用具體數字取代形容詞（「從 X 降到 Y」比「大幅改善」好）
- 用口語轉折取代工整排比（「老實說」「結果發現」比「值得注意的是」自然）
- 用「我們」第一人稱敘事，不用被動語態堆疊
- 段落長度要有變化——每段都一樣長是 AI 特徵
- 加入 1-2 個「人味」時刻：驚訝、吐槽、實務經驗分享

## The Core Principle

AI writing regresses to the statistical mean: simultaneously less specific and more exaggerated. The fix is the opposite — in any language:

**Be specific. Be concrete. Say less.**

- Replace adjectives with facts
- Replace significance claims with evidence
- Replace triplets with one precise word
- Replace "serves as" with "is"（中文：「扮演關鍵角色」→ 直接說「是」）
- If a sentence could apply to any topic, delete it（中文：能套用在任何主題的句子，刪掉）
