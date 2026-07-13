"""Diagnóstico F1, parte 2: o painel "Match thumbs" expõe a lista de hits?

Carrega a busca, abre o menu de thumbs, clica em "Match thumbs" e despeja o
conteúdo do ThumbsRadDock (títulos/atributos das miniaturas) para ver se cada
hit vem com Ano/Edição/página legíveis.

Uso: uv run python pipeline/scraper/explora_thumbs.py
"""

import time
import pathlib
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BIB = "178691_03"
TERMO = '"caixa de conversão"'
URL = (
    "https://memoria.bn.gov.br/DocReader/DocReader.aspx?bib="
    + BIB + "&pesq=" + urllib.parse.quote(TERMO)
)
OUT_DIR = pathlib.Path("dados/scraping/diag")


def espera(driver, cond, timeout=40, passo=1.0):
    for _ in range(int(timeout / passo)):
        try:
            r = cond(driver)
            if r:
                return r
        except Exception:
            pass
        time.sleep(passo)
    return None


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,1000")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(60)
        driver.get(URL)

        # 1. Espera a busca do deep-link concluir (contador "Matchs N/M")
        ok = espera(driver, lambda d: "/" in d.find_element(By.ID, "ocorrenciaatualdiv").text)
        print(f"Busca concluída: {driver.find_element(By.ID, 'ocorrenciaatualdiv').text.strip()!r}")
        print(f"Hit atual (PastaTxt): {driver.find_element(By.ID, 'PastaTxt').get_attribute('title')!r}")

        # (o spinner da imagem principal não some em headless; seguimos sem ele)

        # 2. Abre o menu de thumbs e clica em "Match thumbs" — via JS, que
        # ignora visibilidade/interactabilidade (necessário em headless)
        driver.execute_script("document.getElementById('ThumbsBtn').click();")
        time.sleep(3)
        item = espera(driver, lambda d: next(
            (a for a in d.find_elements(By.CSS_SELECTOR, "#ThumbsMenu a, #ThumbsMenu span")
             if "match" in (a.text or a.get_attribute('textContent') or "").lower()), None), timeout=15)
        if not item:
            print("! item 'Match thumbs' não encontrado; itens do menu:")
            for a in driver.find_elements(By.CSS_SELECTOR, "#ThumbsMenu a, #ThumbsMenu span"):
                t = a.get_attribute("textContent") or ""
                if t.strip():
                    print("   -", repr(t.strip()[:40]))
            return
        print(f"Clicando (JS) no item de menu: {(item.get_attribute('textContent') or '').strip()!r}")
        driver.execute_script("arguments[0].click();", item)

        # 3. Espera o dock de thumbs povoar (imagens aparecerem) e despeja
        espera(driver, lambda d: len(d.find_elements(
            By.CSS_SELECTOR, "#ThumbsRadDock img[src*='.jpg'], #ThumbsRadDock img[src*='Thumb']")) > 0,
            timeout=45, passo=2.0)
        dock = espera(driver, lambda d: d.find_element(By.ID, "ThumbsRadDock"), timeout=20)
        html = dock.get_attribute("innerHTML")
        (OUT_DIR / "thumbs_dock.html").write_text(html, encoding="utf-8")
        driver.save_screenshot(str(OUT_DIR / "tela_thumbs.png"))

        # 4. Inventário: imagens/links dentro do dock com seus title/alt/onclick
        thumbs = dock.find_elements(By.CSS_SELECTOR, "img, a, div[title], span[title]")
        print(f"\nElementos no dock: {len(thumbs)}; com metadados:")
        n = 0
        for t in thumbs:
            title = t.get_attribute("title") or t.get_attribute("alt") or ""
            onclick = (t.get_attribute("onclick") or "")[:60]
            if title.strip():
                n += 1
                print(f"  [{t.tag_name}] title={title!r} onclick={onclick!r}")
            if n >= 25:
                print("  ... (truncado)")
                break
        print(f"\nDump completo em {OUT_DIR}/thumbs_dock.html + tela_thumbs.png")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
