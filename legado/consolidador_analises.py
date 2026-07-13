import pandas as pd
import json
import pathlib

# --- CONFIGURAÇÃO ---
# 1. Verifique se este é o caminho para a pasta com os seus resultados JSON.
JSON_INPUT_DIR = 'data/jsonO_Paiz_1906'

# 2. Este será o nome do seu ficheiro de base de dados final.
# <-- MUDANÇA: Alterado o nome da variável e a extensão do ficheiro.
EXCEL_OUTPUT_FILE = 'data/analise_consolidada_Paiz_1906.xlsx'

def consolidar_json_para_excel(): # <-- MUDANÇA: Nome da função atualizado para clareza
    """
    Lê todos os ficheiros JSON de um diretório, junta os dados e salva como um único ficheiro Excel (.xlsx).
    Este script é robusto o suficiente para lidar com JSONs que contenham um único objeto ou uma lista de objetos.
    """
    json_path = pathlib.Path(JSON_INPUT_DIR)
    if not json_path.is_dir():
        print(f"🛑 ERRO: O diretório de entrada '{json_path}' não foi encontrado.")
        return

    lista_de_dados = []
    print(f"Lendo ficheiros JSON do diretório: {json_path.resolve()}...")

    # Itera sobre todos os ficheiros que terminam com .json na pasta de entrada.
    for json_file in json_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
                if isinstance(dados, list):
                    lista_de_dados.extend(dados)
                else:
                    lista_de_dados.append(dados)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  ! Aviso: Não foi possível ler ou decodificar o ficheiro {json_file.name}. Erro: {e}")

    if not lista_de_dados:
        print("🛑 ERRO: Nenhum dado JSON válido foi carregado. Verifique o conteúdo da pasta de entrada.")
        return

    print(f"\nForam processados com sucesso {len(lista_de_dados)} registos de análise.")

    df = pd.DataFrame(lista_de_dados)

    # Salva o DataFrame como um ficheiro Excel.
    try:
        # <-- MUDANÇA: A função to_csv() foi substituída por to_excel().
        # O argumento index=False é mantido para não salvar o índice do pandas como uma coluna.
        df.to_excel(EXCEL_OUTPUT_FILE, index=False)
        
        # <-- MUDANÇA: Mensagem de sucesso atualizada.
        print(f"\n✅ Sucesso! Os dados foram consolidados no ficheiro Excel: '{EXCEL_OUTPUT_FILE}'")
        
    except Exception as e:
        # <-- MUDANÇA: Mensagem de erro atualizada.
        print(f"🛑 ERRO: Não foi possível salvar o ficheiro Excel. Erro: {e}")

# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    consolidar_json_para_excel() # <-- MUDANÇA: Chamada da função atualizada