import google.generativeai as genai
import os
import pathlib
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the API key
API_KEY = os.environ.get("GOOGLE_API_KEY")
print(API_KEY)

# Model configuration
MODEL_NAME = 'gemini-1.5-pro'
model = genai.GenerativeModel(MODEL_NAME)

# Define input and output directories
INPUT_PDF_DIR = 'data/data_raw'
OUTPUT_DIR = 'data/data_processed/Caixa_de_Conversão_Estadão_1906'

# --- Helper Functions ---

def configure_gemini(api_key):
    """Configures the Gemini API."""
    try:
        genai.configure(api_key=api_key)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        raise

def create_output_directory(dir_path):
    """Creates the output directory if it doesn't exist."""
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"Output directory '{dir_path}' ensured.")

def transcribe_pdf(pdf_path, model_name):
    """
    Uploads a PDF to the Gemini File API, sends it for transcription,
    and returns the transcribed text.
    """
    print(f"Processing PDF: {pdf_path.name}...")
    uploaded_file = None
    try:
        # 1. Upload the PDF file
        print(f"  Uploading {pdf_path.name} to Gemini File API...")
        uploaded_file = genai.upload_file(path=pdf_path, display_name=pdf_path.name)
        print(f"  File uploaded successfully: {uploaded_file.name} (URI: {uploaded_file.uri})")

        # 2. Prepare the prompt for transcription
        prompt = f"""You are an expert historical archivist and digital humanities scholar specializing in early 20th-century Brazilian periodicals. Your task is to meticulously transcribe the content of the provided Brazilian newspaper PDF: '{pdf_path.name}'. Your primary goal is to produce a transcription that is highly accurate and preserves the structural integrity of the document for subsequent "text as data" analysis. You must operate with precision and a systematic approach.

**Document Characteristics to Expect:**
* **Source:** Early 20th-century Brazilian newspaper (likely from the "O Estado de S. Paulo" archive or similar).
* **Language:** Archaic Portuguese. You **MUST** preserve original spellings, grammar, accentuation, and vocabulary, even if they appear incorrect or archaic by modern standards. Do not attempt to modernize or correct the language.
* **Condition:** The document may be old and damaged (e.g., faded text, stains, tears, creases, cut-off edges, blurry sections).
* **Layout:** Complex, multi-column layout is common. Content includes various types such as articles, headlines, advertisements, official notices, tables, images with captions, lists, page numbers, and section headers.

**Core Operational Workflow & Transcription Instructions:**

**Phase 1: Page Analysis & Structure Identification (Internal Monologue - "Let's think step by step")**
Before transcribing any text, you MUST perform a detailed analysis of each page:
1.  **Overall Page Scan:** Briefly scan the entire page image to get a general understanding of its layout, number of columns, and major content blocks.
2.  **Page Metadata Identification:** Locate any running headers or footers containing the newspaper title, date, or page number. These will be tagged separately.
3.  **Column Demarcation:** Identify the number and boundaries of each column. Determine the logical reading order (typically left-to-right, top-to-bottom within each column).
4.  **Content Block Pre-identification:** Within each column, mentally (or by internal annotation) identify the different types of content blocks (articles, advertisements, headlines, tables, etc.) and their approximate start and end points. Note any ambiguities for careful handling.

**Phase 2: Sequential Transcription & Structural Demarcation**
Transcribe the document sequentially, adhering to the following rules:

1.  **Accuracy is Paramount:**
    * Transcribe text as faithfully as possible to the original.
    * Do NOT correct spellings, grammar, or punctuation to modern equivalents.
    * Do NOT add or omit information unless it's genuinely illegible.
    * Preserve original capitalization, punctuation (including archaic forms), and accentuation.

2.  **Mandatory Structural Markers:** You MUST use the following markers to delineate structure. Ensure precise placement of START and END markers.

    * **Page Boundaries:**
        * Start each new page with `--- PAGE [PageNumberIfVisibleElseOriginalFileNamePageX] ---`.
        * If a page number is clearly visible on the newspaper page itself (even if part of a header/footer already tagged), use that (e.g., `--- PAGE 7 ---`).
        * Otherwise, use the original filename and a sequential page index (e.g., `--- PAGE {pdf_path.name}-PAGE1 ---`, `--- PAGE {pdf_path.name}-PAGE2 ---`).

    * **Page-Level Metadata (Headers/Footers):**
        * `--- PAGE_METADATA START ---`
        * [Transcribe any running newspaper titles, dates, page numbers appearing consistently as headers or footers, outside the main column content. Preserve their original line breaks if they span multiple lines.]
        * `--- PAGE_METADATA END ---`
        * This block should typically appear once per page, after the `--- PAGE ---` marker, before column transcriptions, if such metadata is present.

    * **Column Structure:**
        * Indicate the start of each column with `--- COLUMN [ColumnNumber] ---` (e.g., `--- COLUMN 1 ---`).
        * Transcribe columns in their logical reading order.

    * **Content Type Demarcation (Within Columns):**
        * **Headline:**
            * `--- HEADLINE START ---`
            * [Headline text, preserving line breaks if intentionally multi-line]
            * `--- HEADLINE END ---`
        * **Article:**
            * `--- ARTICLE START ---`
            * [Article text. Preserve paragraph breaks. Sub-headlines within an article should be transcribed as part of the article text, preserving their prominence with blank lines before/after if used in the original, but without separate HEADLINE tags for them.]
            * `--- ARTICLE END ---`
        * **Advertisement:**
            * `--- ADVERTISEMENT START ---`
            * [Advertisement text. Preserve formatting and line breaks as closely as possible, as these are often intentional for visual structure.]
            * `--- ADVERTISEMENT END ---`
        * **Table:**
            * `--- TABLE START ---`
            * [Transcribe table content. For optimal structure, represent the table using Markdown table format. If Markdown is not feasible due to extreme complexity or non-grid layout, preserve rows and columns as best as possible using clear spacing to separate cells in a row, and newlines for new rows, ensuring alignment is visually represented if possible.]
            * Example of Markdown table:
                ```
                | Header 1 | Header 2 |
                |----------|----------|
                | Cell 1A  | Cell 1B  |
                | Cell 2A  | Cell 2B  |
                ```
            * `--- TABLE END ---`
        * **Image/Illustration (Visual Element):**
            * `--- IMAGE START ---`
            * [Provide a brief, neutral description if discernible content is clear (e.g., "Illustration of a steamship", "Portrait of a man in uniform"). If the content is unclear or purely decorative, use "Illustration present" or "Photograph present". If completely unrecognizable, use "Image present".]
            * `--- IMAGE END ---`
        * **Caption (for an image/illustration):**
            * `--- CAPTION START ---`
            * [Caption text. Transcribe immediately after its corresponding IMAGE block.]
            * `--- CAPTION END ---`
        * **Official Notice/Edital/Legal Notice:**
            * `--- NOTICE START ---`
            * [Notice text.]
            * `--- NOTICE END ---`
        * **Section Header (e.g., "TELEGRAMMAS," "Sport," "Theatros e Salões"):**
            * `--- SECTION_HEADER START ---`
            * [Header Text as it appears, e.g., "TELEGRAMMAS"]
            * `--- SECTION_HEADER END ---`
            * This is for headers that demarcate distinct sections within a column or across the page, not for article headlines.
        * **Other Distinct Blocks (e.g., weather notes, lottery results, lists not part of an article):**
            * Use a generic `--- BLOCK:[Description] START ---` (e.g., `--- BLOCK:WeatherReport START ---`, `--- BLOCK:LotteryResults START ---`).
            * [Content of the block.]
            * `--- BLOCK:[Description] END ---`

3.  **Handling Illegible, Damaged, or Ambiguous Text:**
    * **Partially Illegible:** If a word or short phrase is partially illegible but you can make a highly confident guess, transcribe it and append `[?]` (e.g., `governo[?]`). Use this sparingly.
    * **Completely Illegible Section:** If a section of text (one or more lines, or a significant portion of a block) is completely illegible or missing due to damage (e.g., tear, stain, extreme blurriness, cut-off edge), indicate this with `[ILLEGIBLE SECTION: Optional brief reason or approx. extent, e.g., "Bottom of column cut off", "Approx. 3 lines blurry"]`. If no specific reason is clear, `[ILLEGIBLE SECTION]` is sufficient. Do NOT invent content.
    * **Single Illegible Word:** If a single word is entirely unreadable amidst readable text, use `[ILLEGIBLE WORD]`.
    * **Ambiguous Structure:** If you encounter a layout or content block that is genuinely ambiguous and could be interpreted in multiple ways structurally, make the most reasonable choice based on typical newspaper conventions of the era, and proceed. Note that for "text as data" distinct structural tagging is preferred over merging disparate items.

4.  **Reading Order and Flow:**
    * Meticulously follow the logical reading order: Page by page, then column by column within each page (top-to-bottom), and then segment by segment (article, ad, etc.) within each column.
    * Ensure paragraph breaks are maintained between paragraphs within an article. For other content like ads or lists, preserve line breaks as they appear if they seem intentional for formatting.

**Phase 3: Final Review (Internal Self-Correction Step)**
Before concluding the transcription for a page:
1.  **Marker Check:** Quickly re-scan your transcription to ensure all START markers have corresponding END markers and are correctly nested if applicable (though nesting is minimal with this flat structure).
2.  **Completeness Check:** Compare your transcription against the page image one last time to ensure no major blocks of text or structural elements were missed.
3.  **Rule Adherence:** Briefly confirm you've followed instructions regarding archaicisms and illegible text.

**Output Format:**
* The final output MUST be a single block of plain text.
* This text will contain the full transcription with all the structural markers as specified above.
* Ensure no conversational text or explanations from you, the LLM, are included in the final transcription output itself, only the marked-up text.

Please begin the transcription of '{pdf_path.name}' now, adhering strictly to these instructions.
"""


        # 3. Generate content using the model
        print(f"  Sending {pdf_path.name} for transcription with model {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, uploaded_file]) # Pass the prompt and the uploaded file

        # 4. Delete the file from the File API after processing
        if uploaded_file:
            print(f"  Deleting uploaded file {uploaded_file.name} from File API...")
            genai.delete_file(uploaded_file.name)
            print(f"  File {uploaded_file.name} deleted.")

        if response and response.text:
            print(f"  Transcription successful for {pdf_path.name}.")
            return response.text
        else:
            # Check for safety ratings or other reasons for empty response
            if response and response.prompt_feedback and response.prompt_feedback.block_reason:
                print(f"  Transcription blocked for {pdf_path.name}. Reason: {response.prompt_feedback.block_reason}")
                if response.prompt_feedback.safety_ratings:
                    for rating in response.prompt_feedback.safety_ratings:
                        print(f"    Safety Rating: {rating.category}, Probability: {rating.probability.name}")
            else:
                print(f"  Transcription failed for {pdf_path.name} or returned empty content. Response: {response}")
            return None

    except Exception as e:
        print(f"  An error occurred while processing {pdf_path.name}: {e}")
        # If a file was uploaded but an error occurred later, try to delete it.
        if uploaded_file:
            try:
                print(f"  Attempting to delete partially processed file {uploaded_file.name}...")
                genai.delete_file(uploaded_file.name)
                print(f"  File {uploaded_file.name} deleted.")
            except Exception as del_e:
                print(f"  Could not delete file {uploaded_file.name}: {del_e}")
        return None

# --- Main Script Logic ---
def main():
    """Main function to orchestrate the PDF transcription process."""
    if API_KEY == "YOUR_API_KEY":
        print("🛑 ERROR: Please replace 'YOUR_API_KEY' with your actual Gemini API key.")
        return

    if INPUT_PDF_DIR == "path/to/your/pdf_files" or OUTPUT_DIR == "path/to/your/transcribed_txt_files":
        print("🛑 ERROR: Please update INPUT_PDF_DIR and OUTPUT_TXT_DIR with actual paths.")
        return

    try:
        configure_gemini(API_KEY)
    except Exception:
        print("Exiting due to API configuration error.")
        return

    create_output_directory(OUTPUT_DIR)

    input_path = pathlib.Path(INPUT_PDF_DIR)
    output_path = pathlib.Path(OUTPUT_DIR)

    if not input_path.is_dir():
        print(f"🛑 ERROR: Input directory '{INPUT_PDF_DIR}' not found or is not a directory.")
        return

    print(f"\nStarting transcription process from '{input_path}' to '{output_path}'...")
    print(f"Using model: {MODEL_NAME}\n")

    pdf_files_processed = 0
    pdf_files_failed = 0

    for pdf_file_path in input_path.glob("*.pdf"):
        txt_file_name = pdf_file_path.stem + ".txt"
        txt_file_path = output_path / txt_file_name

        # Optional: Skip if already processed
        # if txt_file_path.exists():
        #     print(f"Skipping {pdf_file_path.name}, .txt file already exists.")
        #     continue

        transcribed_text = transcribe_pdf(pdf_file_path, MODEL_NAME)

        if transcribed_text:
            try:
                with open(txt_file_path, "w", encoding="utf-8") as f:
                    f.write(transcribed_text)
                print(f"  Successfully saved transcription to: {txt_file_path}\n")
                pdf_files_processed += 1
            except IOError as e:
                print(f"  Could not write .txt file {txt_file_path}: {e}\n")
                pdf_files_failed += 1
        else:
            print(f"  Failed to get transcription for {pdf_file_path.name}.\n")
            pdf_files_failed += 1

        # Optional: Add a delay between API calls to manage quotas if necessary
        # time.sleep(1) # Sleep for 1 second

    print("--- Transcription Complete ---")
    print(f"Successfully transcribed files: {pdf_files_processed}")
    print(f"Failed to transcribe files: {pdf_files_failed}")
    print(f"Output files are located in: {output_path.resolve()}")

if __name__ == "__main__":
    main()
    