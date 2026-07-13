import os
import re
import json
import pathlib
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL ---
# Carrega as variáveis de ambiente (onde a tua API Key está guardada)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- DIRETÓRIOS DE TRABALHO ---
# ATENÇÃO: Confirma que este é o caminho exato onde os teus ficheiros .txt estão!
# Usei o caminho que aparecia na tua imagem.
INPUT_TXT_DIR = 'data/data_processed/Caixa_de_Conversão_Paiz_1906'

# Pasta onde os ficheiros .json resultantes serão guardados.
OUTPUT_JSON_DIR = 'data/analises_json'

# Modelo a ser usado para a tarefa de classificação
MODEL_NAME = 'gemini-1.5-pro-latest'


# --- FUNÇÃO DE EXTRAÇÃO (O nosso "operário extrator") ---
def extrair_artigos_da_transcricao(texto_transcrito: str) -> list[str]:
    """
    Usa expressões regulares para encontrar e extrair todo o texto
    que está entre '--- ARTICLE START ---' e '--- ARTICLE END ---'.
    """
    artigos = re.findall(r'--- ARTICLE START ---(.*?)--- ARTICLE END ---', texto_transcrito, re.DOTALL)
    artigos_limpos = [artigo.strip() for artigo in artigos]
    print(f"  > Foram encontrados {len(artigos_limpos)} artigos no ficheiro.")
    return artigos_limpos


# --- FUNÇÃO DE CLASSIFICAÇÃO (O nosso "operário classificador") ---
def classificar_texto_como_historiador(texto_artigo: str) -> str | None:
    """
    Envia um artigo para ser classificado pelo prompt do historiador económico.
    """
    # ATENÇÃO: Cola aqui o teu prompt de classificação completo e generalizado.
    prompt_historiador = """You are an expert Economic Historian specializing in early 20th-century Brazil, with deep knowledge of the monetary debates surrounding the creation of the "Caixa de Conversão" in 1906. Your task is to analyze snippets of text from early 20th-century Brazilian newspapers and classify mentions related to the "Caixa de Conversão" based on their alignment with "Expansionist" or "Orthodox" monetary perspectives of the era.

Definitions and Context (Based on 1906 Brazilian Monetary Debates):

Caixa de Conversão (and related terms): This refers to the proposed currency conversion office. Also consider related concepts discussed in the context of its creation, such as the "fixação do valor da moeda," "conversão do papel moeda," "emissão de papel conversível em ouro," especially as linked to the "Convênio de Taubaté" (e.g., its Article 8 which proposed using a £15 million loan as backing for such a Caixa).

Orthodox Perspective:
Advocates for a high, fixed conversion rate for the mil-réis (e.g., close to the old par of 27d per mil-réis).
Prioritizes strict adherence to the gold standard, emphasizing currency stability, and the "probidade do paiz."
Expresses concerns about inflation and the potential devaluation of existing paper money if the Caixa is implemented with a lower conversion rate.
Often reflects the interests of importers, creditors, and those valuing a "strong" currency.
Criticizes proposals seen as "quebranto do padrão monetário" or an "attentado á probidade do paiz."
May view the primary role of a conversion office as strictly maintaining a fixed gold value, potentially with deflationary consequences.

Expansionist Perspective:
Advocates for a lower, possibly more flexible, or pragmatic conversion rate for the mil-réis (e.g., 12d, 15d, or a rate that benefits export sectors).
Prioritizes the needs of productive sectors, especially agriculture (like coffee), and seeks to alleviate deflationary pressures.
Views the Caixa de Conversão as a tool to provide currency elasticity, facilitate trade, attract capital for development, and support schemes like the "valorização do café."
May see a new, convertible currency (even at a new rate) as a way to restore credit and overcome the problems of inconvertible paper money and fluctuating exchange rates.
Often references successful examples from other countries (e.g., Argentina's Caisse of Conversion) as a model for economic recovery and growth.

Neutral/Factual Perspective:
The mention is purely informational, reporting on parliamentary discussions, the text of proposals (like the Convênio de Taubaté), or economic data related to the Caixa without expressing a clear opinion or leaning.
The text presents different viewpoints on the Caixa with apparent balance, without endorsing one over the other.

Mixed/Ambiguous Perspective:
The text contains elements supporting both orthodox and expansionist viewpoints simultaneously, making a single classification difficult.
The author's stance is unclear, vague, or too subtly expressed for a definitive classification, even considering the immediate context.

Task:
For each provided text snippet that mentions or directly discusses the "Caixa de Conversão" (or clearly related concepts as defined above):
1. Identify the relevant sentence(s) or paragraph.
2. Classify the stance expressed in that segment into one of the following categories:
   - Clearly Orthodox
   - Leaning Orthodox
   - Clearly Expansionist
   - Leaning Expansionist
   - Neutral/Factual
   - Mixed/Ambiguous
3. Extract the specific text snippet (quote) that provides the primary evidence for your classification. Keep it concise but sufficient to understand the reasoning.
4. Provide a brief justification (1-2 sentences) explaining why you chose that category, linking it to the definitions provided.
5. Assign a confidence level to your classification: High, Medium, or Low.

Input Data:
You will be provided with text from early 20th-century Brazilian newspapers.

Output Format:
For each identified and classified mention, provide the output as a JSON object with the following structure:
{
  "newspaper": "Name of the newspaper (e.g., Correio Paulistano, Gazeta de Noticias, O Paiz, etc.)",
  "date_of_article": "Date of the article (if available in the snippet, otherwise use the general context of 1906)",
  "original_snippet_context": "A brief surrounding context of the mention, if helpful for understanding.",
  "relevant_quote": "The exact quote discussing the Caixa de Conversão or related concepts.",
  "classification": "Your chosen category (e.g., Clearly Orthodox, Leaning Expansionist, Neutral/Factual, etc.)",
  "justification": "Your brief explanation for the classification.",
  "confidence": "High, Medium, or Low"
}

If a text snippet contains multiple distinct mentions with different stances, create a separate JSON object for each. If a snippet does not contain any relevant mention, output an empty list or a message indicating no relevant mentions found.

Example of how to approach a snippet (Hypothetical):
Snippet from Correio Paulistano, 1906:
"...o illustre Senador X defendeu ardorosamente a creação da Caixa de Conversão, affirmando que a fixação do valor da moeda em 15d traria a salvação da lavoura cafeeira, permittindo a exportação vantajosa e o pagamento das dividas dos agricultores. Contudo, o Deputado Y argumentou que tal medida seria um golpe na fé publica e prejudicaria os credores da nação..."

Potential Output (for the first part):
{
  "newspaper": "Correio Paulistano",
  "date_of_article": "1906",
  "original_snippet_context": "Debate on the creation of the Caixa de Conversão.",
  "relevant_quote": "o illustre Senador X defendeu ardorosamente a creação da Caixa de Conversão, affirmando que a fixação do valor da moeda em 15d traria a salvação da lavoura cafeeira, permittindo a exportação vantajosa e o pagamento das dividas dos agricultores.",
  "classification": "Clearly Expansionist",
  "justification": "The text explicitly supports the Caixa and a lower conversion rate (15d) to benefit the coffee sector and debtors, aligning with expansionist goals.",
  "confidence": "High"
}

Begin analysis with the provided text datasets.
    """
    
    try:
        print(f"    -> Enviando artigo para classificação...")
        prompt_completo = f"{prompt_historiador}\n\n--- INICIAR ANÁLISE DO TEXTO ABAIXO ---\n\n{texto_artigo}"
        
        generation_config = {"response_mime_type": "application/json"}
        model = genai.GenerativeModel(MODEL_NAME, generation_config=generation_config)
        
        response = model.generate_content(prompt_completo)
        
        if not (response and response.text):
            print("      ! A classificação falhou ou retornou vazia.")
            return None
            
        print("    -> Classificação recebida com sucesso.")
        return response.text

    except Exception as e:
        print(f"      ! Ocorreu um erro durante a chamada à API de classificação: {e}")
        return None


# --- LÓGICA PRINCIPAL (O Orquestrador da Análise) ---
def main():
    """
    Orquestra o pipeline de análise: Ler TXT -> Extrair Artigos -> Classificar -> Salvar JSON.
    """
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        print("🛑 ERRO: Chave da API não configurada. Verifica o teu ficheiro .env")
        return

    genai.configure(api_key=API_KEY)
    
    input_path = pathlib.Path(INPUT_TXT_DIR)
    output_path = pathlib.Path(OUTPUT_JSON_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    print("-" * 50)
    print(f"Iniciando Análise de Transcrições")
    print(f"Pasta de Entrada (TXTs): {input_path.resolve()}")
    print(f"Pasta de Saída (JSONs): {output_path.resolve()}")
    print("-" * 50)

    if not input_path.is_dir():
        print(f"🛑 ERRO: O diretório de entrada '{input_path}' não foi encontrado.")
        return

    for txt_file_path in input_path.glob("*.txt"):
        print(f"\nLendo ficheiro de transcrição: {txt_file_path.name}")

        try:
            # PASSO 1: Ler o conteúdo do ficheiro .txt
            texto_completo = txt_file_path.read_text(encoding="utf-8")
            
            # PASSO 2: Extrair os artigos do texto lido
            artigos_para_analise = extrair_artigos_da_transcricao(texto_completo)

            if not artigos_para_analise:
                print(f"  Nenhum artigo demarcado com '--- ARTICLE START ---' foi encontrado. A avançar.")
                continue

            # PASSO 3: Classificar cada artigo encontrado
            for i, artigo in enumerate(artigos_para_analise):
                print(f"  Analisando Artigo {i + 1}/{len(artigos_para_analise)} de {txt_file_path.name}")
                
                resultado_json_str = classificar_texto_como_historiador(artigo)

                # PASSO 4: Salvar o resultado JSON num ficheiro
                if resultado_json_str:
                    try:
                        json.loads(resultado_json_str) # Valida se é um JSON válido
                        
                        nome_ficheiro_saida = f"{txt_file_path.stem}_classificacao_{i+1}.json"
                        caminho_ficheiro_saida = output_path / nome_ficheiro_saida

                        with open(caminho_ficheiro_saida, "w", encoding="utf-8") as f:
                            f.write(resultado_json_str)
                        print(f"    -> Análise guardada em: {caminho_ficheiro_saida.name}")

                    except (json.JSONDecodeError, IOError) as e:
                        print(f"    ! Erro ao guardar o ficheiro JSON: {e}")

        except Exception as e:
            print(f"  ! Erro ao processar o ficheiro {txt_file_path.name}: {e}")
    
    print("\n--- Análise de todas as transcrições concluída ---")


if __name__ == "__main__":
    main()