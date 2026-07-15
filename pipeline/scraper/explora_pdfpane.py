"""Diagnóstico F1, parte 5: painel "Edições em PDF" e a janela ExportWnd.

A parte 4 achou no DOM um sliding pane com title "Edições em PDF" e uma
RadWindow oculta ExportWnd. Este script mapeia a rota oficial de PDF:
  1. abre o painel "Edições em PDF" e despeja o conteúdo (links? lista?);
  2. vasculha o JS da página por quem chama ExportWnd / SaveAsFile.ashx;
  3. se houver link/botão de PDF, clica o primeiro e monitora o download.

Uso: uv run python pipeline/scraper/explora_pdfpane.py   (sempre headed)
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
PANE_TAB = "RAD_SLIDING_PANE_TAB_Custom1RadSlidingPane"


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


def acha_saveasfile_no_js(driver):
    """Procura 'SaveAsFile' e 'ExportWnd' nos scripts/handlers da página."""
    trechos = driver.execute_script(r"""
        var alvos = /SaveAsFile|ExportWnd/gi, out = [];
        function cata(texto, origem){
            if (!texto) return;
            var m;
            while ((m = alvos.exec(texto)) !== null) {
                out.push({origem: origem,
                          trecho: texto.slice(Math.max(0, m.index - 120), m.index + 160)});
                if (out.length > 40) return;
            }
        }
        document.querySelectorAll('script:not([src])').forEach(
            function(s, i){ cata(s.textContent, 'script inline #' + i); });
        document.querySelectorAll('[onclick]').forEach(
            function(e){ cata(e.getAttribute('onclick'), '<' + e.tagName + ' id=' + e.id + '> onclick'); });
        return out;
    """)
    fns = driver.execute_script("""
        return Object.keys(window).filter(function(k){
            if (!/export|save|pdf/i.test(k)) return false;
            try { return typeof window[k] === 'function'; } catch(e) { return false; }
        });
    """)
    return trechos, fns


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

        # 1. JS: quem fala em SaveAsFile / ExportWnd?
        print("\n----- Referências a SaveAsFile/ExportWnd no JS -----")
        trechos, fns = acha_saveasfile_no_js(driver)
        for t in trechos[:12]:
            trecho_limpo = re.sub(r"\s+", " ", t["trecho"])
            print(f"  [{t['origem']}] ...{trecho_limpo}...")
        print(f"  Funções globais export/save/pdf: {fns}")
        (DIAG_DIR / "saveasfile_js.json").write_text(
            json.dumps({"trechos": trechos, "funcoes": fns}, ensure_ascii=False, indent=1),
            encoding="utf-8")

        # 2. Abre o painel "Edições em PDF"
        print("\n----- Painel 'Edições em PDF' -----")
        tab = espera(driver, lambda d: d.find_element(By.ID, PANE_TAB), timeout=20)
        if not tab:
            print("! aba do painel não encontrada")
            return
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(4)
        espera_humano_captcha(driver)
        driver.save_screenshot(str(DIAG_DIR / "tela_pdfpane.png"))

        pane = driver.execute_script("""
            var p = document.getElementById('Custom1RadSlidingPane');
            return p ? p.innerHTML : null;
        """)
        if pane:
            (DIAG_DIR / "pdfpane.html").write_text(pane, encoding="utf-8")
            print(f"  conteúdo do pane salvo ({len(pane)} chars) em pdfpane.html")
        else:
            (DIAG_DIR / "pdfpane.html").write_text(driver.page_source, encoding="utf-8")
            print("  ! #Custom1RadSlidingPane sem innerHTML; salvei page_source inteiro")

        # inventário de clicáveis dentro do pane
        itens = driver.execute_script("""
            var out = [];
            var raiz = document.getElementById('Custom1RadSlidingPane') || document;
            raiz.querySelectorAll('a,input[type=button],input[type=submit],button,[onclick]')
                .forEach(function(e){
                    out.push({tag: e.tagName, id: e.id || '',
                              texto: (e.textContent || e.value || '').trim().slice(0, 60),
                              href: (e.getAttribute('href') || '').slice(0, 120),
                              onclick: (e.getAttribute('onclick') || '').slice(0, 120),
                              vis: !!e.offsetParent});
                });
            return out;
        """)
        print(f"  Clicáveis no pane ({len(itens)}):")
        for it in itens[:15]:
            print(f"    {json.dumps(it, ensure_ascii=False)}")

        # 3. Se há algo com cara de PDF/download, clica o primeiro e monitora
        alvo = next((it for it in itens if it["vis"] and re.search(
            r"(pdf|salvar|download|baixar|export)",
            (it["id"] + it["texto"] + it["href"] + it["onclick"]).lower())), None)
        if not alvo:
            print("\n  (nenhum item com cara de PDF/download para clicar; fim do mapeamento)")
            return
        print(f"\n  Clicando: {json.dumps(alvo, ensure_ascii=False)}")
        antes = set(OUT_DIR.glob("*"))
        sel = f"#{alvo['id']}" if alvo["id"] else None
        if sel:
            driver.execute_script(
                "arguments[0].click();", driver.find_element(By.CSS_SELECTOR, sel))
        else:
            driver.execute_script("""
                var raiz = document.getElementById('Custom1RadSlidingPane') || document;
                var alvoTexto = arguments[0];
                var els = raiz.querySelectorAll('a,input,button,[onclick]');
                for (var i = 0; i < els.length; i++) {
                    var e = els[i];
                    if (((e.textContent || e.value || '').trim().slice(0,60)) === alvoTexto) {
                        e.click(); return;
                    }
                }
            """, alvo["texto"])
        time.sleep(3)
        espera_humano_captcha(driver)
        driver.save_screenshot(str(DIAG_DIR / "tela_pdfpane_clique.png"))
        print("  >>> Se abriu diálogo/CAPTCHA, resolve na janela; monitoro a pasta 3 min...")

        fim = time.time() + 180
        arquivo = None
        while time.time() < fim:
            time.sleep(5)
            espera_humano_captcha(driver)
            novos = [a for a in set(OUT_DIR.glob("*")) - antes
                     if not a.name.endswith(".crdownload")]
            if novos:
                arquivo = max(novos, key=lambda a: a.stat().st_mtime)
                time.sleep(3)
                break

        # registra as requisições de rede da sessão
        urls = []
        try:
            for entry in driver.get_log("performance"):
                msg = json.loads(entry["message"])["message"]
                if msg.get("method") == "Network.requestWillBeSent":
                    u = msg.get("params", {}).get("request", {}).get("url", "")
                    if re.search(r"SaveAsFile|\.ashx|\.pdf", u, re.I):
                        urls.append(u)
        except Exception as e:
            print(f"  (performance log indisponível: {e})")
        if urls:
            print("  Requisições de download vistas:")
            for u in dict.fromkeys(urls):
                print(f"    {u}")
            (DIAG_DIR / "export_urls.txt").write_text(
                "\n".join(dict.fromkeys(urls)), encoding="utf-8")

        if arquivo:
            print(f"\nSALVOU: {arquivo.name} ({arquivo.stat().st_size / 1024:.0f} KB)")
        else:
            print("\n(nenhum arquivo novo; ver dumps em dados/scraping/diag)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
