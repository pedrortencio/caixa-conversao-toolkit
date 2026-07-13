"""Exploração inicial da busca do DocReader (diagnóstico da F1).

Carrega o viewer com deep-link de busca ("caixa de conversão"), espera os
resultados via AJAX e despeja o DOM + inventário de elementos para mapear a
estrutura da lista de hits. Não baixa página nenhuma.

Uso: uv run python pipeline/scraper/explora_busca.py [--headed]
"""

import sys
import time
import pathlib
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BIB = "178691_03"  # O Paiz 1900-1909 (teste de regressão: 1906)
TERMO = '"caixa de conversão"'
URL = (
    "https://memoria.bn.gov.br/DocReader/DocReader.aspx?bib="
    + BIB + "&pesq=" + urllib.parse.quote(TERMO)
)
OUT_DIR = pathlib.Path("dados/scraping/diag")


def inventario(driver):
    """Lista elementos com id sugestivo de resultados de pesquisa."""
    linhas = []
    for el in driver.find_elements(By.XPATH, "//*[@id]"):
        try:
            eid = el.get_attribute("id") or ""
            if any(k in eid.lower() for k in ("pesq", "result", "lista", "hit", "ocorr")):
                txt = (el.text or "").strip()
                linhas.append(
                    f"{el.tag_name:8s} id={eid:45s} visivel={el.is_displayed()!s:5s} "
                    f"len_texto={len(txt):6d} | {txt[:100].replace(chr(10), ' / ')}"
                )
        except Exception:
            continue
    return linhas


def main():
    headed = "--headed" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    opts = Options()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,1000")
    # Selenium puro: o curl mostrou que a BN não usa anti-bot agressivo.
    # Se algum dia bloquear, voltar ao undetected-chromedriver (modo headed).

    print(f"Abrindo ({'headed' if headed else 'headless'}): {URL}")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(60)
        driver.get(URL)

        # O deep-link deve preencher PesquisarTxt e clicar Pesquisar2Btn sozinho.
        # Espera-se AJAX; poll até algum elemento de pesquisa ganhar texto.
        achou = False
        for i in range(30):  # até ~60 s
            time.sleep(2)
            inv = inventario(driver)
            com_texto = [l for l in inv if "len_texto=     0" not in l and "len_texto=" in l]
            grandes = [l for l in inv if any(f"len_texto={n}" in l for n in [])]  # placeholder
            if any(int(l.split("len_texto=")[1].split()[0]) > 200 for l in inv if "len_texto=" in l):
                achou = True
                print(f"  [{(i+1)*2:3d}s] resultados aparentes no DOM")
                break
            if i == 9 and not achou:
                # fallback: dispara a busca manualmente
                print("  [ 20s] sem resultados; tentando preencher e clicar manualmente...")
                try:
                    campo = driver.find_element(By.ID, "PesquisarTxt")
                    campo.clear()
                    campo.send_keys(TERMO)
                    driver.find_element(By.ID, "PesquisarBtn").click()
                    print("  busca disparada manualmente")
                except Exception as e:
                    print(f"  fallback falhou: {e}")

        # Despejo final
        (OUT_DIR / "dom_completo.html").write_text(driver.page_source, encoding="utf-8")
        inv = inventario(driver)
        (OUT_DIR / "inventario_elementos.txt").write_text("\n".join(inv), encoding="utf-8")
        driver.save_screenshot(str(OUT_DIR / "tela.png"))

        print(f"\nElementos de pesquisa encontrados: {len(inv)}")
        for l in inv:
            print("  " + l)
        print(f"\nDumps salvos em {OUT_DIR}/ (dom_completo.html, inventario_elementos.txt, tela.png)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
