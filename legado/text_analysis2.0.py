import os
import re
import json
import pathlib
import google.generativeai as genai
from dotenv import load_dotenv
import time # For adding delays if needed

# --- CONFIGURAÇÃO INICIAL ---
# Carrega as variáveis de ambiente (onde a tua API Key está guardada)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- DIRETÓRIOS DE TRABALHO ---
# ATENÇÃO: Confirma que este é o caminho exato onde os teus ficheiros .txt estão!
# O usuário deve ajustar este caminho para cada um dos 5 jornais.
# Exemplo: 'data/data_processed/Caixa_de_Conversao_O_Paiz_1906'
INPUT_TXT_DIR = 'data/data_processed/Caixa_de_Conversão_Gazeta_1906' # AJUSTE CONFORME NECESSÁRIO

# Pasta onde os ficheiros .json resultantes serão guardados.
OUTPUT_JSON_DIR = 'data/jsonGazeta_1906' # AJUSTE CONFORME NECESSÁRIO

# Modelo a ser usado para a tarefa de classificação
MODEL_NAME = 'gemini-1.5-pro-latest'


# --- FUNÇÃO DE EXTRAÇÃO DE DATA DO CONTEÚDO ---
def extrair_data_do_conteudo(texto_completo: str) -> str | None:
    """
    Tenta extrair a data do conteúdo do texto, prioritariamente de um bloco de metadados.
    Retorna a data no formato YYYY-MM-DD ou uma string parcial se a conversão completa falhar.
    """
    metadata_match = re.search(r'--- PAGE_METADATA START ---(.*?)--- PAGE_METADATA END ---', texto_completo, re.DOTALL | re.IGNORECASE)
    text_to_search_date = ""
    
    if metadata_match:
        text_to_search_date = metadata_match.group(1)
    else:
        # Fallback: search in the first ~500 characters if no metadata block
        text_to_search_date = texto_completo[:500]

    # Regex para encontrar datas como "DD de MONTH de YYYY" ou "DAYOFWEEK, DD de MONTH de YYYY"
    date_pattern = re.compile(
        r'(?:[A-ZÀ-ÖØ-Þ]+-FEIRA,\s*)?'  # Opcional "DIASEMANA-FEIRA, "
        r'(\d{1,2})\s+DE\s+([A-ZÇÃÕÉÊÍÓÔÚ]+)\s+DE\s+(1906)', # DD de MES de 1906
        re.IGNORECASE
    )
    
    match = date_pattern.search(text_to_search_date)
    
    if match:
        dia_str, mes_nome, ano_str = match.groups()
        
        mes_map = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
            'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
            'agosto': '08', 'setembro': '09', 'outubro': '10',
            'novembro': '11', 'dezembro': '12'
        }
        
        mes_nome_lower = mes_nome.lower()
        mes_num_str = mes_map.get(mes_nome_lower)
        
        if mes_num_str:
            try:
                dia_formatado = f"{int(dia_str):02d}"
                return f"{ano_str}-{mes_num_str}-{dia_formatado}"
            except ValueError:
                print(f"    ! Aviso: Dia '{dia_str}' inválido encontrado.")
                return f"{ano_str} (Mês: {mes_nome}, Dia: {dia_str} - erro de formatação)"
        else:
            print(f"    ! Aviso: Mês '{mes_nome}' não reconhecido.")
            return f"{ano_str} (Mês: {mes_nome} não mapeado, Dia: {dia_str})"
            
    return None # Nenhuma data encontrada


# --- FUNÇÃO DE CLASSIFICAÇÃO (O nosso "operário classificador") ---
def classificar_edicao_completa_como_historiador(texto_edicao_completa: str, nome_jornal: str, data_edicao: str) -> str | None:
    """
    Envia a edição completa de um jornal para ser classificada pelo prompt do historiador económico.
    Inclui o nome do jornal e a data da edição no prompt para melhor contexto.
    """
    # Este é o prompt atualizado para a análise holística da edição completa, com os {} escapados.
    prompt_historiador = f"""You are an expert Economic Historian specializing in early 20th-century Brazil, with deep knowledge of the monetary debates surrounding the creation of the "Caixa de Conversão" in 1906. Your task is to perform a holistic analysis of the entire provided text of a daily newspaper edition and determine its single, dominant editorial stance on the "Caixa de Conversão" debate for that day.

Definitions and Context (Based on 1906 Brazilian Monetary Debates):

* **Caixa de Conversão (and related terms):** This refers to the proposed currency conversion office. Also consider related concepts discussed in the context of its creation, such as the "fixação do valor da moeda," "conversão do papel moeda," "emissão de papel conversível em ouro," especially as linked to the "Convênio de Taubaté" (e.g., its Article 8 which proposed using a £15 million loan as backing for such a Caixa).
* **Orthodox Perspective:**
    * Advocates for a high, fixed conversion rate for the mil-réis (e.g., close to the old par of 27d per mil-réis).
    * Prioritizes strict adherence to the gold standard, emphasizing currency stability, and the "probidade do paiz."
    * Expresses concerns about inflation and the potential devaluation of existing paper money if the Caixa is implemented with a lower conversion rate.
    * Often reflects the interests of importers, creditors, and those valuing a "strong" currency.
    * Criticizes proposals seen as "quebranto do padrão monetário" or an "attentado á probidade do paiz."
    * May view the primary role of a conversion office as strictly maintaining a fixed gold value, potentially with deflationary consequences.
* **Expansionist Perspective:**
    * Advocates for a lower, possibly more flexible, or pragmatic conversion rate for the mil-réis (e.g., 12d, 15d, or a rate that benefits export sectors).
    * Prioritizes the needs of productive sectors, especially agriculture (like coffee), and seeks to alleviate deflationary pressures.
    * Views the Caixa de Conversão as a tool to provide currency elasticity, facilitate trade, attract capital for development, and support schemes like the "valorização do café."
    * May see a new, convertible currency (even at a new rate) as a way to restore credit and overcome the problems of inconvertible paper money and fluctuating exchange rates.
    * Often references successful examples from other countries (e.g., Argentina's Caisse of Conversion) as a model for economic recovery and growth.

### **NEW: Heuristics for Sophisticated Analysis and Weighing Evidence**

To perform this task accurately, you must apply the following critical reasoning principles:

1.  **Distinguish Subject from Argument (Crucial):** An article's topic does not automatically define its stance. You must identify the author's *argumentative purpose*.
    * **Example:** An article might extensively discuss Argentina's export success (a topic favored by Expansionists) but use it as an **Orthodox cautionary tale**. If the article's conclusion is that this success is fragile without fiscal discipline and that Brazil should not be deceived by this "false mirage," then the article's stance is **Orthodox**, despite its subject matter. Do not classify based on keywords alone; analyze the core message.
2.  **Differentiate Reporting from Endorsing:** The newspaper might report on the arguments of a politician or another entity without endorsing them. Look for the newspaper's own editorial voice, framing language, or the prominence given to certain views to determine the paper's own stance. An article quoting an expansionist politician is not necessarily an expansionist article.
3.  **Weigh a Day's Edition Holistically:** A front-page editorial or a multi-day series by a named author carries significantly more weight than a brief, neutral market report or a passing mention. Your final classification for the day should reflect the most prominent and forcefully argued position presented in the edition.

Task:

You will analyze the **entire text** of a single daily newspaper edition. Your goal is to produce **one single classification and a corresponding numerical score** that represents the newspaper's overall stance for that day, applying the heuristics above.

1.  **Synthesize the Edition:** Read through the entire text and identify all content related to the "Caixa de Conversão" debate.
2.  **Determine the Dominant Stance & Score:** Based on the balance, framing, and prominence of the arguments, determine the single most representative classification and its corresponding numerical score. The categories and scores are:
    * `Clearly Orthodox` (Score: -2.0)
    * `Leaning Orthodox` (Score: -1.0)
    * `Neutral/Factual` (Score: 0.0)
    * `Mixed/Ambiguous` (Score: 0.0)
    * `Leaning Expansionist` (Score: 1.0)
    * `Clearly Expansionist` (Score: 2.0)
3.  **Provide Justification:** Write a concise justification explaining *why* you chose this overall classification and score.
4.  **Extract Key Evidence:** Identify and extract **1 to 3 of the most significant quotes** from the edition that best support your overall classification.
5.  **Assign a Confidence Level:** Assign a confidence level to your overall classification: `High`, `Medium`, or `Low`.

Input Data:
You will be provided with the full text from a single daily edition of the newspaper '{nome_jornal}' dated approximately '{data_edicao}'.

Output Format:
For the entire newspaper edition provided, provide the output as a **single JSON object** with the following structure:

{{
  "newspaper": "{nome_jornal}",
  "date_of_article": "{data_edicao}",
  "overall_classification": "The single chosen category for the entire edition (e.g., Leaning Orthodox)",
  "stance_score": -1.0,
  "overall_justification": "Your summary and reasoning for the overall classification of the edition.",
  "confidence": "High, Medium, or Low",
  "supporting_evidence": [
    {{
      "quote": "The first key quote that supports the overall classification.",
      "reason_for_inclusion": "Briefly explain why this quote is significant (e.g., 'From a front-page editorial', 'A direct statement of the paper's policy')."
    }},
    {{
      "quote": "The second key quote that supports the overall classification.",
      "reason_for_inclusion": "Briefly explain why this quote is significant (e.g., 'A prominently featured argument from an influential politician')."
    }}
  ]
}}

If the entire daily edition text contains no relevant mentions of the "Caixa de Conversão" or related concepts, output a JSON object like this:
{{
  "newspaper": "{nome_jornal}",
  "date_of_article": "{data_edicao}",
  "overall_classification": "No Relevant Mentions Found",
  "overall_justification": "The edition was scanned and no articles or mentions related to the Caixa de Conversão debate were identified.",
  "confidence": "High",
  "supporting_evidence": []
}}

Begin analysis with the provided newspaper edition.
"""
    
    try:
        print(f"      -> Enviando edição completa para classificação holística (Jornal: {nome_jornal}, Data: {data_edicao})...")
        prompt_completo = f"{prompt_historiador}\n\n--- START OF FULL NEWSPAPER EDITION TEXT TO ANALYZE ---\n\n{texto_edicao_completa}\n\n--- END OF FULL NEWSPAPER EDITION TEXT TO ANALYZE ---"
        
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json", 
            temperature=0.2 
        )
        
        model = genai.GenerativeModel(MODEL_NAME, generation_config=generation_config)
        response = model.generate_content(prompt_completo)
        
        if not (response and hasattr(response, 'text') and response.text):
            print("        ! A classificação falhou ou retornou vazia.")
            return None
            
        print("      -> Classificação da edição completa recebida com sucesso.")
        return response.text

    except Exception as e:
        print(f"        ! Ocorreu um erro durante a chamada à API de classificação: {e}")
        import traceback
        traceback.print_exc()
        return None


# --- LÓGICA PRINCIPAL (O Orquestrador da Análise) ---
def main():
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("🛑 ERRO: Chave da API GOOGLE_API_KEY não configurada. Verifica o teu ficheiro .env ou a variável de ambiente.")
        return

    genai.configure(api_key=API_KEY)
    
    input_path = pathlib.Path(INPUT_TXT_DIR)
    output_path = pathlib.Path(OUTPUT_JSON_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    print("-" * 70)
    print(f"Iniciando Análise Holística de Edições de Jornais")
    print(f"Pasta de Entrada (TXTs): {input_path.resolve()}")
    print(f"Pasta de Saída (JSONs): {output_path.resolve()}")
    print(f"Modelo LLM: {MODEL_NAME}")
    print("-" * 70)

    if not input_path.is_dir():
        print(f"🛑 ERRO: O diretório de entrada '{input_path}' não foi encontrado.")
        return

    nome_do_jornal_base = input_path.name.replace('Caixa_de_Conversao_', '').replace('_1906', '').replace('_', ' ')

    for txt_file_path in sorted(input_path.glob("*.txt")):
        print(f"\nLendo e processando edição: {txt_file_path.name}")
        
        texto_edicao_completa = ""
        try:
            # PASSO 1: Ler o conteúdo completo do ficheiro .txt (edição diária)
            texto_edicao_completa = txt_file_path.read_text(encoding="utf-8")
            if not texto_edicao_completa.strip():
                print(f"    O ficheiro {txt_file_path.name} está vazio. A avançar.")
                continue

            # PASSO 2: Extrair a data do conteúdo
            data_para_prompt = extrair_data_do_conteudo(texto_edicao_completa)
            if not data_para_prompt:
                data_para_prompt = "1906 (data não encontrada no conteúdo)"
                print(f"    ! Aviso: Não foi possível extrair a data do conteúdo de {txt_file_path.name}. Usando fallback.")
            else:
                print(f"    Data extraída do conteúdo: {data_para_prompt}")

            # PASSO 3: Classificar a edição completa
            resultado_json_str = classificar_edicao_completa_como_historiador(
                texto_edicao_completa, nome_do_jornal_base, data_para_prompt
            )

            # PASSO 4: Salvar o resultado JSON (que deve ser um único objeto)
            if resultado_json_str:
                try:
                    # Validar que a resposta é um JSON válido antes de salvar
                    json_data_to_save = json.loads(resultado_json_str) 
                    
                    nome_ficheiro_saida = f"{txt_file_path.stem}_classificacao_holistica.json"
                    caminho_ficheiro_saida = output_path / nome_ficheiro_saida

                    with open(caminho_ficheiro_saida, "w", encoding="utf-8") as f:
                        json.dump(json_data_to_save, f, ensure_ascii=False, indent=4)
                    print(f"    -> Análise da edição guardada em: {caminho_ficheiro_saida.name}")

                except json.JSONDecodeError:
                    print(f"        ! Resposta da API não é um JSON válido para {txt_file_path.name}.")
                    debug_file_name = f"{txt_file_path.stem}_raw_invalid_json.txt"
                    debug_file_path = output_path / debug_file_name
                    with open(debug_file_path, "w", encoding="utf-8") as df:
                       df.write(resultado_json_str)
                    print(f"        ! Resposta bruta guardada em: {debug_file_path.name}")
            else:
                print(f"    Nenhuma classificação retornada para a edição {txt_file_path.name}.")
            
            # Atraso opcional para não exceder limites da API (requests por minuto)
            # Descomente a linha abaixo se encontrar erros de limite de taxa.
            # time.sleep(1) 

        except Exception as e:
            print(f"    ! Erro GERAL ao processar o ficheiro {txt_file_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n--- Análise de todas as edições concluída ---")


if __name__ == "__main__":
    main()