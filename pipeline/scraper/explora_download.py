"""Diagnóstico F1, parte 3: baixar a imagem da página do hit atual.

Prova a "rota do cache": espera o #DocumentoImg renderizar e puxa os bytes
da própria sessão do navegador (fetch same-origin com cookies). Se sair um
JPG legível, o risco técnico do download está encerrado.

Uso: uv run python pipeline/scraper/explora_download.py   (sempre headed)
"""

import base64
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
OUT_DIR = pathlib.Path("dados/raw_pdf/teste")


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
    print("\n  >>> CAPTCHA — resolve na janela, eu espero...")
    for _ in range(timeout_min * 12):
        time.sleep(5)
        if not captcha_presente(driver):
            print("  >>> resolvido, seguindo!\n")
            return True
    return False


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    opts = Options()  # headed: imagem só renderiza com tela
    opts.add_argument("--window-size=1600,1000")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(60)
        driver.get(URL)
        espera_humano_captcha(driver)

        # espera a busca E a imagem da página do hit carregarem de verdade
        print("Esperando a imagem da página do hit renderizar...")
        src = None
        for i in range(60):  # até ~2 min
            time.sleep(2)
            espera_humano_captcha(driver)
            # candidata 1: #DocumentoImg; candidata 2: qualquer img grande do cache
            info = driver.execute_script("""
                var out = {doc: null, best: null};
                var d = document.getElementById('DocumentoImg');
                if (d) out.doc = {src: d.src || '', w: d.naturalWidth || 0};
                var best = null;
                document.querySelectorAll('img').forEach(function(im){
                    if ((im.src||'').toLowerCase().indexOf('cache') >= 0 &&
                        im.naturalWidth > (best ? best.w : 800))
                        best = {src: im.src, w: im.naturalWidth};
                });
                out.best = best;
                return out;
            """)
            if i % 5 == 0:
                d = info.get("doc") or {}
                b = info.get("best") or {}
                print(f"  [{(i+1)*2:3d}s] DocumentoImg w={d.get('w',0)} src=...{(d.get('src','') or '')[-45:]}"
                      f" | melhor_cache w={b.get('w',0)}")
            d = info.get("doc") or {}
            if d.get("w", 0) > 400 and ".jpg" in (d.get("src", "") or "").lower():
                src = d["src"]
                print(f"  imagem da vista pronta: naturalWidth={d['w']}px")
                break
        if not src:
            print("! imagem não renderizou; abortando")
            return

        pasta_txt = driver.find_element(By.ID, "PastaTxt").get_attribute("title")
        print(f"Hit atual: {pasta_txt!r}")
        print(f"URL da imagem: ...{src[-80:]}")

        # Hipótese full-res: o nome é I{pag}-1-0-{vistaW}-{vistaH}-{fullW}-{fullH}.JPG;
        # pedir a vista no tamanho do original deve devolver resolução cheia.
        import re
        m = re.search(r"(I\d+-\d+-\d+)-(\d{6})-(\d{6})-(\d{6})-(\d{6})(\.JPG)", src, re.I)
        candidatos = [("vista", src)]
        if m:
            full = f"{m.group(1)}-{m.group(4)}-{m.group(5)}-{m.group(4)}-{m.group(5)}{m.group(6)}"
            candidatos.append(("fullres", src.replace(m.group(0), full)))
            print(f"URL full-res construída: ...{full}")

        def baixa(u):
            return driver.execute_async_script("""
                var cb = arguments[arguments.length-1];
                fetch(arguments[0], {credentials:'same-origin'})
                  .then(r => { if (!r.ok) throw new Error('HTTP '+r.status); return r.blob(); })
                  .then(b => { var fr = new FileReader();
                               fr.onload = () => cb(fr.result);
                               fr.readAsDataURL(b); })
                  .catch(e => cb('ERR:' + e.message));
            """, u)

        for nome, u in candidatos:
            data_url = baixa(u)
            if not data_url or data_url.startswith("ERR:"):
                print(f"! fetch {nome} falhou: {data_url}")
                continue
            header, b64 = data_url.split(",", 1)
            raw = base64.b64decode(b64)
            destino = OUT_DIR / f"pagina_teste_{nome}.jpg"
            destino.write_bytes(raw)
            print(f"SALVO: {destino.name} ({len(raw)/1024:.0f} KB, mime={header})")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
