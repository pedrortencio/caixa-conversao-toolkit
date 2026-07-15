"""Diagnóstico F1, parte 7: rota PDF oficial COM anti-detecção (stealth leve).

A parte 6 mostrou que o clique em "Create" da janela Download PDF é barrado
quando o Chrome está com a marca de automação (faixa "controlled by automated
test software" + navigator.webdriver=true). Aqui removemos essas marcas com
Selenium puro (sem undetected-chromedriver) e deixamos o Pedro clicar Create
NA MÃO (clique físico = gesto confiável, isTrusted=true, mais difícil de
detectar que um .click() de script).

Stealth aplicado:
  - --disable-blink-features=AutomationControlled  (tira a faixa e o flag)
  - excludeSwitches ['enable-automation'] + useAutomationExtension False
  - CDP: Object.defineProperty(navigator,'webdriver',{get:()=>undefined})

Uso: uv run python pipeline/scraper/explora_export3.py   (sempre headed)
"""

import json
import pathlib
import re
import time
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
OUT_DIR = pathlib.Path("dados/raw_pdf/teste")
DIAG_DIR = pathlib.Path("dados/scraping/diag")


def captcha_presente(driver):
    try:
        els = driver.find_elements(
            By.XPATH,
            "//*[contains(@src,'captcha') or contains(@id,'captcha') or contains(@class,'captcha')"
            " or contains(@src,'recaptcha') or contains(@title,'reCAPTCHA')]")
        return any(e.is_displayed() for e in els)
    except Exception:
        return False


def espera(driver, cond, timeout=60, passo=1.0):
    for _ in range(int(timeout / passo)):
        try:
            r = cond(driver)
            if r:
                return r
        except Exception:
            pass
        time.sleep(passo)
    return None


def confere_stealth(driver):
    """Imprime o que um detector veria: navigator.webdriver e a faixa."""
    wd = driver.execute_script("return navigator.webdriver;")
    ua = driver.execute_script("return navigator.userAgent;")
    print(f"  navigator.webdriver = {wd!r}  (queremos None/False)")
    print(f"  userAgent contém 'Headless': {'Headless' in ua}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    opts = Options()
    opts.add_argument("--window-size=1600,1000")
    # --- stealth leve ---
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    # download automático em PDF
    opts.add_experimental_option("prefs", {
        "download.default_directory": str(OUT_DIR.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    })
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=opts)
    try:
        # esconde navigator.webdriver ANTES de qualquer script da página rodar
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', "
                      "{get: () => undefined});"
        })
        driver.set_page_load_timeout(90)
        driver.get(URL)

        print("Checando stealth:")
        confere_stealth(driver)

        espera(driver, lambda d: "/" in d.find_element(By.ID, "ocorrenciaatualdiv").text,
               timeout=60)
        print(f"Busca: {driver.find_element(By.ID, 'ocorrenciaatualdiv').text.strip()!r}")
        print(f"Hit: {driver.find_element(By.ID, 'PastaTxt').get_attribute('title')!r}")
        espera(driver, lambda d: "Wait..." not in d.find_element(By.TAG_NAME, "body").text,
               timeout=60, passo=2.0)

        # abre a janela de exportação (mesma função que o menu do viewer usa)
        print("\nAbrindo a janela Download PDF (PDFExportAbre)...")
        driver.execute_script("try { PDFExportAbre(); } catch(e) {}")
        espera(driver, lambda d: next(
            (f for f in d.find_elements(By.TAG_NAME, "iframe")
             if "Export" in (f.get_attribute("name") or "")), None), timeout=20)

        antes = set(OUT_DIR.glob("*"))
        print("\n  >>> A janela Download PDF está aberta.")
        print("  >>> Deixa 'Pages from 1 to 1' e clica CREATE VOCÊ MESMO (clique físico).")
        print("  >>> Se aparecer CAPTCHA, resolve. Monitoro pasta + rede por 5 min...\n")

        fim = time.time() + 300
        arquivo = None
        vistos = set()
        while time.time() < fim:
            time.sleep(4)
            # avisa se algo com cara de bloqueio/captcha surgiu
            if captcha_presente(driver) and "captcha" not in vistos:
                vistos.add("captcha")
                print("  >>> CAPTCHA apareceu — resolve na janela.")
            novos = [a for a in set(OUT_DIR.glob("*")) - antes
                     if not a.name.endswith(".crdownload")]
            if novos:
                arquivo = max(novos, key=lambda a: a.stat().st_mtime)
                time.sleep(3)
                break

        # captura TODA a rota de exportação no log de rede
        urls = []
        try:
            for entry in driver.get_log("performance"):
                msg = json.loads(entry["message"])["message"]
                if msg.get("method") == "Network.requestWillBeSent":
                    u = msg.get("params", {}).get("request", {}).get("url", "")
                    if re.search(r"SaveAsFile|PDFExport|MediaExport|\.pdf|Captcha", u, re.I):
                        urls.append(u)
                if msg.get("method") == "Network.responseReceived":
                    resp = msg.get("params", {}).get("response", {})
                    u = resp.get("url", "")
                    if re.search(r"SaveAsFile|PDFExport", u, re.I):
                        urls.append(f"[{resp.get('status')}] {u}")
        except Exception as e:
            print(f"  (performance log indisponível: {e})")
        if urls:
            print("\nRota de exportação vista na rede:")
            for u in dict.fromkeys(urls):
                print(f"  {u}")
            (DIAG_DIR / "export_urls.txt").write_text(
                "\n".join(dict.fromkeys(urls)), encoding="utf-8")

        driver.save_screenshot(str(DIAG_DIR / "tela_export3_fim.png"))
        if arquivo:
            print(f"\nSALVOU: {arquivo.name} ({arquivo.stat().st_size / 1024:.0f} KB)")
            print("  >>> Abre o PDF e confere se o texto está legível para transcrição.")
        else:
            print("\n(nenhum arquivo novo; se o Create foi barrado de novo, "
                  "escalamos para undetected-chromedriver em modo headed)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
