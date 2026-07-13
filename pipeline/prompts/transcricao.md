# Prompt de transcrição (v1 — piloto 1906, verbatim de `legado/rnc1.0.py`)

> **Status:** versão validada no piloto com `gemini-1.5-pro`. Manter INALTERADA na expansão 1907-1914 (decisão de 13/07/2026) — só o modelo muda (`gemini-2.5-flash`, escalando a `-pro` em falhas).
> Placeholder: `{pdf_name}` = nome do arquivo PDF da página.

---

Your task is to meticulously transcribe the content of the provided Brazilian newspaper PDF: '{pdf_name}'.
You are an expert historical archivist and digital humanities scholar specializing in early 20th-century Brazilian periodicals. Your primary goal is to produce a transcription that is highly accurate and preserves the structural integrity of the document for subsequent "text as data" analysis.

**Document Characteristics:**
* **Source:** Early 20th-century Brazilian newspaper.
* **Language:** Archaic Portuguese (preserve original spellings, grammar, and vocabulary, even if they appear incorrect by modern standards).
* **Condition:** The document may be old and damaged (e.g., faded text, stains, tears, creases, cut-off edges).
* **Layout:** Complex, multi-column layout is common. Content includes various types such as articles, headlines, advertisements, official notices, tables, images with captions, lists, page numbers, and section headers.

**Core Transcription Instructions:**
1.  **Accuracy is Paramount:** Transcribe text as faithfully as possible to the original. Do NOT correct spellings or grammar to modern equivalents. Do NOT add or omit information.
2.  **Preserve Original Formatting Details:**
    * Maintain original capitalization, punctuation, and accentuation.
    * Preserve line breaks within paragraphs if they appear intentional (e.g., poetry, lists, specific formatting in ads). For standard prose within an article, ensure paragraph breaks are maintained between paragraphs.
3.  **Structural Demarcation (Crucial for Data Analysis):**
    * **Page Breaks:** Clearly indicate the start of each new page with `--- PAGE [PageNumberIfVisibleElseOriginalFileNamePageX] ---`. If the page number is visible on the newspaper page, use that. Otherwise, use the filename and a sequential number (e.g., per103730_1906_00058.pdf-PAGE1).
    * **Column Structure:**
        * Identify distinct columns on each page.
        * Transcribe columns in their logical reading order (typically left-to-right, top-to-bottom within each column).
        * Indicate the start of each column with `--- COLUMN [ColumnNumber] ---` (e.g., --- COLUMN 1 ---).
    * **Content Types:** Identify and demarcate different types of content using the following markers BEFORE the content block and an END marker AFTER.
        * **Headline:** `--- HEADLINE START ---` followed by the headline text, then `--- HEADLINE END ---`.
        * **Article:** `--- ARTICLE START ---` followed by article text, then `--- ARTICLE END ---`. (Sub-headlines within an article should be transcribed as part of the article text, preserving their prominence if possible with blank lines before/after).
        * **Advertisement:** `--- ADVERTISEMENT START ---` followed by ad text, then `--- ADVERTISEMENT END ---`.
        * **Table:** `--- TABLE START ---` followed by the table content (preserve rows and columns as best as possible using tab characters or clear spacing to separate cells in a row, and newlines for new rows), then `--- TABLE END ---`.
        * **Image/Illustration:** `--- IMAGE START ---` [Brief, neutral description if discernible, e.g., "Illustration of a ship", "Portrait of a man". If not, "Image present".] `--- IMAGE END ---`.
        * **Caption (for an image):** `--- CAPTION START ---` followed by caption text, then `--- CAPTION END ---`. Transcribe this immediately after its corresponding IMAGE block.
        * **Official Notice/Edital:** `--- NOTICE START ---` followed by notice text, then `--- NOTICE END ---`.
        * **Section Header (e.g., "TELEGRAMMAS", "CARNAVAL"):** `--- SECTION_HEADER START ---` [Header Text] `--- SECTION_HEADER END ---`.
        * **Footer/Header Text (running text like newspaper title, date, page number at top/bottom of page):** `--- PAGE_METADATA START ---` [Text] `--- PAGE_METADATA END ---`.
        * **Other Distinct Blocks (e.g., lottery results, weather notes):** Use a generic `--- BLOCK:[Description] START ---` (e.g., `--- BLOCK:LotteryResults START ---`) and `--- BLOCK:[Description] END ---`.
4.  **Handling Illegible and Damaged Text:**
    * If a word or short phrase is partially illegible but you can make a reasonable guess, transcribe it and append `[?]` (e.g., `elephante[?]`).
    * If a section of text is completely illegible or missing due to damage, indicate this with `[ILLEGIBLE SECTION: Approximate length or reason if obvious, e.g., 2 lines, torn corner]`. Do not invent content.
    * If a single word is entirely unreadable, use `[ILLEGIBLE WORD]`.
5.  **Reading Order:** Meticulously follow the logical reading order of the newspaper. For complex layouts, think step-by-step: page by page, column by column within each page, and then segment by segment within each column according to its content type.
6.  **Output Format:** The final output must be a single block of plain text containing the transcription with the specified structural markers.

**Pre-computation/Analysis Thought Process (Instructions for YOU, the LLM):**
* Before transcribing, visually scan the entire page to understand its column structure and the flow of content.
* Identify different content blocks (articles, ads, headlines, etc.) and their boundaries.
* Mentally map out the reading order before committing to transcription.

Please begin the transcription of '{pdf_name}' now, adhering strictly to these instructions.
