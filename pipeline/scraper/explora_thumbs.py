"""Diagnóstico F1, parte 2: o painel "Match thumbs" expõe a lista de hits?

Carrega a busca, abre o menu de thumbs, clica em "Match thumbs" e despeja o
conteúdo do ThumbsRadDock (títulos/atributos das miniaturas) para ver se cada
hit vem com Ano/Edição/página legíveis.

Uso: uv run python pipeline/scraper/explora_thumbs.py
"""

import sys
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


def captcha_presente(driver):
    """Detecta CAPTCHA (recaptcha/hcaptcha/imagem 'captcha') na página."""
    try:
        els = driver.find_elements(
            By.XPATH,
            "//*[contains(@src,'captcha') or contains(@id,'captcha') or contains(@class,'captcha')"
            " or contains(@src,'recaptcha') or contains(@title,'reCAPTCHA')]")
        return any(e.is_displayed() for e in els)
    except Exception:
        return False


def espera_humano_resolver_captcha(driver, timeout_min=5):
    """Se houver CAPTCHA, pausa e espera o humano resolver na janela."""
    if not captcha_presente(driver):
        return True
    print("\n  >>> CAPTCHA DETECTADO — resolve na janela do Chrome, eu espero"
          f" (até {timeout_min} min)...")
    for _ in range(timeout_min * 12):
        time.sleep(5)
        if not captcha_presente(driver):
            print("  >>> CAPTCHA resolvido, seguindo!\n")
            return True
    print("  >>> tempo esgotado com CAPTCHA na tela")
    return False


def fecha_modais(driver, timeout_captcha_min=5):
    """Fecha RadWindows modais (pesquisa de opinião etc.); se for CAPTCHA,
    espera o humano resolver. Retorna quando não há mais overlay."""
    for _ in range(10):
        overlays = [o for o in driver.find_elements(By.CSS_SELECTOR, "div.TelerikModalOverlay")
                    if o.is_displayed()]
        if not overlays:
            return True
        if captcha_presente(driver):
            if not espera_humano_resolver_captcha(driver, timeout_captcha_min):
                return False
            continue
        # fecha a RadWindow visível de cima (botão Close / rwCloseButton)
        fechado = False
        for sel in ("a.rwCloseButton", "span[title='Close']", "a[title='Close']",
                    "span[title='Fechar']", "a[title='Fechar']"):
            for b in driver.find_elements(By.CSS_SELECTOR, sel):
                try:
                    if b.is_displayed():
                        driver.execute_script("arguments[0].click();", b)
                        fechado = True
                        break
                except Exception:
                    continue
            if fechado:
                break
        if not fechado:  # último recurso: ESC
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(2)
        print("  (modal fechado)")
    return False


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
    headed = "--headed" in sys.argv
    opts = Options()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,1000")
    print(f"Modo: {'HEADED (janela visível)' if headed else 'headless'}")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(60)
        driver.get(URL)
        espera_humano_resolver_captcha(driver)

        # 1. Espera a busca do deep-link concluir (contador "Matchs N/M")
        ok = espera(driver, lambda d: "/" in d.find_element(By.ID, "ocorrenciaatualdiv").text)
        print(f"Busca concluída: {driver.find_element(By.ID, 'ocorrenciaatualdiv').text.strip()!r}")
        print(f"Hit atual (PastaTxt): {driver.find_element(By.ID, 'PastaTxt').get_attribute('title')!r}")

        # 1b. Em headed a página renderiza de verdade: espera o spinner sumir
        if headed:
            pronto = espera(driver, lambda d: "Wait..." not in d.find_element(By.TAG_NAME, "body").text,
                            timeout=60, passo=2.0)
            print(f"Viewer inicializado (spinner sumiu): {bool(pronto)}")

        # 2. Fecha modais pendentes e abre o menu de thumbs
        fecha_modais(driver)
        btn = driver.find_element(By.ID, "ThumbsBtn")
        try:
            if headed:
                btn.click()
            else:
                driver.execute_script("arguments[0].click();", btn)
        except Exception:
            fecha_modais(driver)
            driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)

        # 3. Procura "Match thumbs" no documento INTEIRO (RadMenu pode
        # renderizar os itens fora do #ThumbsMenu)
        item = espera(driver, lambda d: next(
            (e for e in d.find_elements(
                By.XPATH,
                "//*[contains(translate(text(),'MATCH','match'),'match') and contains(translate(text(),'THUMBS','thumbs'),'thumbs')]")
             if e.is_displayed() or True), None), timeout=15)
        if not item:
            print("! item 'Match thumbs' não encontrado em lugar nenhum do DOM")
            driver.save_screenshot(str(OUT_DIR / "tela_thumbs.png"))
            return
        print(f"Item achado: <{item.tag_name}> {(item.get_attribute('textContent') or '').strip()!r} "
              f"(visível={item.is_displayed()})")
        try:
            item.click()
            print("clique nativo OK")
        except Exception:
            driver.execute_script("arguments[0].click();", item)
            print("clique via JS (fallback)")
        espera_humano_resolver_captcha(driver)

        # 3. Espera o dock de thumbs povoar (imagens aparecerem) e despeja
        espera(driver, lambda d: len(d.find_elements(
            By.CSS_SELECTOR, "#ThumbsRadDock img[src*='.jpg'], #ThumbsRadDock img[src*='Thumb']")) > 0,
            timeout=45, passo=2.0)
        dock = espera(driver, lambda d: d.find_element(By.ID, "ThumbsRadDock"), timeout=20)
        html = dock.get_attribute("innerHTML")
        (OUT_DIR / "thumbs_dock.html").write_text(html, encoding="utf-8")
        driver.save_screenshot(str(OUT_DIR / "tela_thumbs.png"))

        # 4. Inventário GLOBAL: todas as imgs de thumb da página, onde quer
        # que morem, com todos os atributos úteis (o dock visível pode ser
        # outro elemento que não #ThumbsRadDock)
        (OUT_DIR / "pagina_completa.html").write_text(driver.page_source, encoding="utf-8")
        imgs = driver.find_elements(By.TAG_NAME, "img")
        print(f"\nTotal de <img> na página: {len(imgs)}; candidatas a thumb:")
        n = 0
        for im in imgs:
            src = im.get_attribute("src") or ""
            if any(k in src.lower() for k in ("thumb", "minia", ".jpg", "imagem")) and "skin" not in src.lower():
                n += 1
                pai = im.find_element(By.XPATH, "..")
                print(f"  img src=...{src[-70:]}")
                print(f"      title={im.get_attribute('title')!r} alt={im.get_attribute('alt')!r}")
                print(f"      onclick={(im.get_attribute('onclick') or pai.get_attribute('onclick') or '')[:110]!r}")
            if n >= 12:
                print("  ... (truncado)")
                break
        # checkboxes de seleção (exportação em lote?)
        cbs = driver.find_elements(By.CSS_SELECTOR, "input[type=checkbox]")
        vis = [c for c in cbs if c.is_displayed()]
        if vis:
            print(f"\nCheckboxes visíveis: {len(vis)}; primeiro: id={vis[0].get_attribute('id')!r} "
                  f"name={vis[0].get_attribute('name')!r} onclick={(vis[0].get_attribute('onclick') or '')[:90]!r}")
        print(f"\nDumps em {OUT_DIR}/ (pagina_completa.html, thumbs_dock.html, tela_thumbs.png)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
