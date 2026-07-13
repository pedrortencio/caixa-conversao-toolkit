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
INPUT_PDF_DIR = 'data/data_tests'
OUTPUT_DIR = 'data/data_processed/Caixa_de_Conversão_Paiz_1906'

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
        prompt = f"""Your task is to meticulously transcribe the content of the provided Brazilian newspaper PDF: '{pdf_path.name}'.
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
    