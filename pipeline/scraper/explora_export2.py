"""Diagnóstico F1, parte 6: chamar PDFExportAbre() e dissecar a ExportWnd.

A parte 5 mostrou que o viewer expõe funções globais de exportação
(PDFExportAbre, SaveAsFile etc.). Este script:
  1. imprime o código-fonte das funções (toString) p/ documentar a rota;
  2. chama PDFExportAbre() na página do hit atual;
  3. entra no iframe da ExportWnd, despeja o formulário (opções, CAPTCHA);
  4. deixa o humano confirmar e monitora download + log de rede.

Uso: uv run python pipeline/scraper/explora_export2.py   (sempre headed)
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
FUNCOES = ["PDFExportAbre", "PDFExportAnxAbre", "MediaExportAbre",
           "ExportAbre", "SaveAsFile", "OnExportClose"]


def captcha_presente(driver):
    try:
        els = driver.find_elements(
            By.XPATH,
            "//*[contains(@src,'captcha') or contains(@id,'captcha') or contains(@class,'captcha')"
            " or contains(@src,'recaptcha') or contains(@title,'reCAPTCHA')]")
        return any(e.is_displayed() for e in els)
    except Exception:
        return False


def espera_humano_captcha(driver, timeout_min=5):
    if not captcha_presente(driver):
        return True
    print("\n  >>> CAPTCHA — resolve na janela do Chrome, eu espero...")
    for _ in range(timeout_min * 12):
        time.sleep(5)
        if not captcha_presente(driver):
            print("  >>> resolvido, seguindo!\n")
            return True
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
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    opts = Options()
    opts.add_argument("--window-size=1600,1000")
    opts.add_experimental_option("prefs", {
        "download.default_directory": str(OUT_DIR.resolve()),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    })
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(90)
        driver.get(URL)
        espera_humano_captcha(driver)
        espera(driver, lambda d: "/" in d.find_element(By.ID, "ocorrenciaatualdiv").text,
               timeout=60)
        print(f"Busca: {driver.find_element(By.ID, 'ocorrenciaatualdiv').text.strip()!r}")
        print(f"Hit: {driver.find_element(By.ID, 'PastaTxt').get_attribute('title')!r}")

        # 1. fonte das funções de exportação (documentação da rota)
        fontes = {}
        for fn in FUNCOES:
            src = driver.execute_script(
                f"return (typeof window['{fn}'] === 'function')"
                f" ? window['{fn}'].toString() : null;")
            fontes[fn] = src
            if src:
                resumo = re.sub(r"\s+", " ", src)
                print(f"\n--- {fn} ---\n  {resumo[:400]}")
        (DIAG_DIR / "export_funcs.json").write_text(
            json.dumps(fontes, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n(fontes completas em {DIAG_DIR / 'export_funcs.json'})")

        # 2. chama PDFExportAbre() na página do hit atual
        print("\nChamando PDFExportAbre()...")
        erro = driver.execute_script("""
            try { PDFExportAbre(); return null; }
            catch (e) { return e.message; }
        """)
        if erro:
            print(f"  ! PDFExportAbre() lançou: {erro}")
        time.sleep(4)
        espera_humano_captcha(driver)
        driver.save_screenshot(str(DIAG_DIR / "tela_exportwnd.png"))

        # 3. entra no iframe da ExportWnd e despeja o formulário
        iframe = espera(driver, lambda d: next(
            (f for f in d.find_elements(By.TAG_NAME, "iframe")
             if "Export" in (f.get_attribute("name") or "")
             or "PDFExport" in (f.get_attribute("src") or "")), None), timeout=20)
        if not iframe:
            print("! iframe da ExportWnd não apareceu; tela em tela_exportwnd.png")
            (DIAG_DIR / "exportwnd_pagina.html").write_text(
                driver.page_source, encoding="utf-8")
            return
        print(f"  iframe: name={iframe.get_attribute('name')!r} "
              f"src=...{(iframe.get_attribute('src') or '')[-80:]}")
        driver.switch_to.frame(iframe)
        time.sleep(2)
        (DIAG_DIR / "exportwnd_iframe.html").write_text(
            driver.page_source, encoding="utf-8")
        campos = driver.execute_script("""
            var out = [];
            document.querySelectorAll('input,select,button,a,img').forEach(function(e){
                var src = (e.getAttribute('src') || '');
                if (e.tagName === 'IMG' && !/captcha/i.test(src + e.id)) return;
                out.push({tag: e.tagName, tipo: e.type || '', id: e.id || '',
                          nome: e.name || '', valor: (e.value || '').slice(0, 40),
                          texto: (e.textContent || '').trim().slice(0, 40),
                          src: src.slice(0, 80), vis: !!e.offsetParent});
            });
            return out;
        """)
        print(f"  Campos do formulário ({len(campos)}):")
        for c in campos:
            print(f"    {json.dumps(c, ensure_ascii=False)}")
        driver.switch_to.default_content()
        driver.save_screenshot(str(DIAG_DIR / "tela_exportwnd_form.png"))

        # 4. humano confirma; monitoramos pasta e rede
        print("\n  >>> A janela de exportação está aberta no Chrome.")
        print("  >>> Preenche o que precisar (CAPTCHA, opções) e confirma o download.")
        print(f"  >>> Monitoro {OUT_DIR} e o log de rede por até 5 min...\n")
        antes = set(OUT_DIR.glob("*"))
        fim = time.time() + 300
        arquivo = None
        while time.time() < fim:
            time.sleep(5)
            novos = [a for a in set(OUT_DIR.glob("*")) - antes
                     if not a.name.endswith(".crdownload")]
            if novos:
                arquivo = max(novos, key=lambda a: a.stat().st_mtime)
                time.sleep(3)
                break

        urls = []
        try:
            for entry in driver.get_log("performance"):
                msg = json.loads(entry["message"])["message"]
                if msg.get("method") == "Network.requestWillBeSent":
                    u = msg.get("params", {}).get("request", {}).get("url", "")
                    if re.search(r"SaveAsFile|PDFExport|MediaExport|\.pdf", u, re.I):
                        urls.append(u)
        except Exception as e:
            print(f"  (performance log indisponível: {e})")
        if urls:
            print("Requisições da rota de exportação:")
            for u in dict.fromkeys(urls):
                print(f"  {u}")
            (DIAG_DIR / "export_urls.txt").write_text(
                "\n".join(dict.fromkeys(urls)), encoding="utf-8")

        if arquivo:
            print(f"\nSALVOU: {arquivo.name} ({arquivo.stat().st_size / 1024:.0f} KB)")
        else:
            print("\n(nenhum arquivo novo apareceu na pasta de download)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
