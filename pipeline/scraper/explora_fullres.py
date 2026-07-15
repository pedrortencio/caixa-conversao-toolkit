"""Diagnóstico F1, parte 4: página em resolução de trabalho (legível p/ transcrição).

Testa as duas rotas deixadas em aberto pela parte 3 (`explora_download.py`):
  A) ZOOM programático no viewer → o cache gera imagem maior → fetch same-origin;
  B) EXPORTAÇÃO oficial (botão de salvar → SaveAsFile.ashx), com o humano
     operando o diálogo na primeira vez enquanto o log de rede grava a
     requisição para automatizarmos depois.

Uso: uv run python pipeline/scraper/explora_fullres.py   (sempre headed)
     Fica na página do 1º hit da busca; Pedro resolve CAPTCHA/diálogo na janela.
"""

import base64
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


# ---------- helpers já validados nas partes 2-3 ----------

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


def fecha_modais(driver):
    for _ in range(10):
        overlays = [o for o in driver.find_elements(By.CSS_SELECTOR, "div.TelerikModalOverlay")
                    if o.is_displayed()]
        if not overlays:
            return True
        if captcha_presente(driver):
            if not espera_humano_captcha(driver):
                return False
            continue
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
        if not fechado:
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


def info_imagem(driver):
    """src e naturalWidth do #DocumentoImg (ou None se não renderizou)."""
    return driver.execute_script("""
        var d = document.getElementById('DocumentoImg');
        if (!d || !d.src || d.naturalWidth < 50) return null;
        return {src: d.src, w: d.naturalWidth, h: d.naturalHeight};
    """)


def espera_imagem(driver, timeout=120):
    print("Esperando a imagem da página renderizar...")
    for i in range(timeout // 2):
        time.sleep(2)
        espera_humano_captcha(driver)
        d = info_imagem(driver)
        if d and d["w"] > 400 and ".jpg" in d["src"].lower():
            print(f"  imagem pronta: {d['w']}x{d['h']}px")
            return d
        if i % 5 == 0:
            print(f"  [{(i + 1) * 2:3d}s] ainda esperando (w={(d or {}).get('w', 0)})")
    return None


def baixa_para(driver, url, destino):
    """fetch same-origin dentro da sessão; devolve tamanho em bytes ou None."""
    data_url = driver.execute_async_script("""
        var cb = arguments[arguments.length-1];
        fetch(arguments[0], {credentials:'same-origin'})
          .then(r => { if (!r.ok) throw new Error('HTTP '+r.status); return r.blob(); })
          .then(b => { var fr = new FileReader();
                       fr.onload = () => cb(fr.result);
                       fr.readAsDataURL(b); })
          .catch(e => cb('ERR:' + e.message));
    """, url)
    if not data_url or data_url.startswith("ERR:"):
        print(f"  ! fetch falhou: {data_url}")
        return None
    raw = base64.b64decode(data_url.split(",", 1)[1])
    destino.write_bytes(raw)
    return len(raw)


# ---------- ROTA A: zoom programático ----------

def rota_zoom(driver):
    print("\n===== ROTA A: zoom programático =====")
    base = espera_imagem(driver)
    if not base:
        print("! imagem base não renderizou; abortando rota A")
        return None
    print(f"Baseline (vista): {base['w']}x{base['h']}  ...{base['src'][-60:]}")

    # inventário: controles com cara de zoom + funções globais do viewer
    ctrls = driver.execute_script("""
        var out = [];
        document.querySelectorAll(
            "[id*='oom'],[title*='oom'],[onclick*='oom'],[id*='mplia'],[title*='mplia'],[alt*='oom']"
        ).forEach(function(e){
            out.push({tag: e.tagName, id: e.id || '', title: e.title || '',
                      onclick: (e.getAttribute('onclick') || '').slice(0, 90),
                      vis: !!e.offsetParent});
        });
        return out;
    """)
    fns = driver.execute_script(
        "return Object.keys(window).filter(function(k){return /zoom/i.test(k);});")
    print(f"Controles candidatos: {json.dumps(ctrls, ensure_ascii=False, indent=1)[:1200]}")
    print(f"Funções globais com 'zoom': {fns}")

    # candidato preferido: botão de zoom-in nativo
    botao = None
    for c in ctrls:
        if c["vis"] and re.search(r"(zoomin|zoom_in|mais|plus|\+)", (c["id"] + c["title"]).lower()):
            botao = c["id"]
            break
    if not botao:
        vis = [c for c in ctrls if c["vis"] and c["id"]]
        botao = vis[0]["id"] if vis else None
    if not botao:
        print("! nenhum controle de zoom visível; despejando tela p/ análise")
        driver.save_screenshot(str(DIAG_DIR / "tela_zoom_nada.png"))
        return None
    print(f"Clicando zoom via #{botao} (até 10x, observando o src)...")

    melhor = dict(base)
    for i in range(10):
        try:
            el = driver.find_element(By.ID, botao)
            driver.execute_script("arguments[0].click();", el)
        except Exception as e:
            print(f"  ! clique {i + 1} falhou: {e}")
            break
        time.sleep(3)
        espera_humano_captcha(driver)
        d = info_imagem(driver)
        if not d:
            print(f"  [{i + 1}] imagem sumiu do DOM (viewer pode ter trocado p/ tiles)")
            break
        novo = d["src"] != melhor["src"] or d["w"] != melhor["w"]
        print(f"  [{i + 1}] {d['w']}x{d['h']} {'NOVO' if novo else '(igual)'} ...{d['src'][-55:]}")
        if d["w"] > melhor["w"]:
            melhor = d
        if not novo and i >= 2:
            print("  (estabilizou, parando)")
            break

    if melhor["w"] <= base["w"]:
        print("Rota A: zoom NÃO aumentou a resolução da imagem principal.")
        driver.save_screenshot(str(DIAG_DIR / "tela_zoom_fim.png"))
        return None

    destino = OUT_DIR / "pagina_teste_zoom.jpg"
    tam = baixa_para(driver, melhor["src"], destino)
    if tam:
        print(f"Rota A SALVOU: {destino.name} ({melhor['w']}x{melhor['h']}, {tam / 1024:.0f} KB)")
        return {"rota": "zoom", "w": melhor["w"], "h": melhor["h"], "bytes": tam}
    return None


# ---------- ROTA B: exportação oficial (SaveAsFile.ashx) ----------

def pedidos_de_rede(driver, padrao=r"SaveAsFile|\.ashx"):
    """Varre o performance log do Chrome atrás de requisições de download."""
    urls = []
    try:
        for entry in driver.get_log("performance"):
            msg = json.loads(entry["message"])["message"]
            if msg.get("method") not in ("Network.requestWillBeSent",):
                continue
            u = msg.get("params", {}).get("request", {}).get("url", "")
            if re.search(padrao, u, re.I):
                urls.append(u)
    except Exception as e:
        print(f"  (performance log indisponível: {e})")
    return urls


def rota_export(driver):
    print("\n===== ROTA B: exportação oficial =====")
    fecha_modais(driver)

    # inventário: botões com cara de salvar/baixar/imprimir/exportar
    cands = driver.execute_script("""
        var out = [];
        document.querySelectorAll(
            "[id*='ave'],[id*='own'],[id*='rint'],[id*='mprim'],[id*='xport'],[id*='PDF']," +
            "[title*='alvar'],[title*='ownload'],[title*='mprim'],[title*='PDF']"
        ).forEach(function(e){
            out.push({tag: e.tagName, id: e.id || '', title: e.title || '',
                      onclick: (e.getAttribute('onclick') || '').slice(0, 90),
                      vis: !!e.offsetParent});
        });
        return out;
    """)
    print(f"Candidatos a botão de exportação: "
          f"{json.dumps(cands, ensure_ascii=False, indent=1)[:1500]}")

    botao = None
    for c in cands:
        if c["vis"] and re.search(r"(save|salvar|download)", (c["id"] + c["title"]).lower()):
            botao = c["id"]
            break
    if not botao:
        print("! nenhum botão de salvar visível; tela em tela_export_nada.png")
        driver.save_screenshot(str(DIAG_DIR / "tela_export_nada.png"))
        return None

    arquivos_antes = set(OUT_DIR.glob("*"))
    print(f"Clicando #{botao}...")
    driver.execute_script(
        "arguments[0].click();", driver.find_element(By.ID, botao))
    time.sleep(3)
    espera_humano_captcha(driver)

    # despeja o diálogo que abriu (se abriu) e passa o volante pro humano
    driver.save_screenshot(str(DIAG_DIR / "tela_export_dialogo.png"))
    (DIAG_DIR / "export_dialogo.html").write_text(driver.page_source, encoding="utf-8")
    print("\n  >>> Se abriu um diálogo de salvar/exportar, OPERA ELE NA JANELA")
    print("  >>> (escolhe formato/página e confirma). Eu monitoro a pasta de")
    print(f"  >>> download ({OUT_DIR}) e o log de rede por até 4 min...\n")

    novo_arquivo, fim = None, time.time() + 240
    while time.time() < fim:
        time.sleep(5)
        espera_humano_captcha(driver)
        atuais = set(OUT_DIR.glob("*"))
        candidatos = [a for a in atuais - arquivos_antes
                      if not a.name.endswith(".crdownload")]
        if candidatos:
            novo_arquivo = max(candidatos, key=lambda a: a.stat().st_mtime)
            time.sleep(3)  # deixa o Chrome terminar de escrever
            break

    urls = pedidos_de_rede(driver)
    if urls:
        print("Requisições de download vistas no log de rede:")
        for u in dict.fromkeys(urls):
            print(f"  {u}")
        (DIAG_DIR / "export_urls.txt").write_text("\n".join(dict.fromkeys(urls)),
                                                  encoding="utf-8")
    else:
        print("(nenhuma requisição SaveAsFile/.ashx apareceu no log de rede)")

    if not novo_arquivo:
        print("Rota B: nenhum arquivo novo apareceu na pasta de download.")
        return None
    tam = novo_arquivo.stat().st_size
    print(f"Rota B SALVOU: {novo_arquivo.name} ({tam / 1024:.0f} KB)")
    return {"rota": "export", "arquivo": novo_arquivo.name, "bytes": tam}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    opts = Options()  # headed: imagem/diálogos só renderizam com tela
    opts.add_argument("--window-size=1600,1000")
    opts.add_experimental_option("prefs", {
        "download.default_directory": str(OUT_DIR.resolve()),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    })
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=opts)
    resultados = []
    try:
        driver.set_page_load_timeout(60)
        driver.get(URL)
        espera_humano_captcha(driver)
        espera(driver, lambda d: "/" in d.find_element(By.ID, "ocorrenciaatualdiv").text)
        print(f"Busca: {driver.find_element(By.ID, 'ocorrenciaatualdiv').text.strip()!r}")
        print(f"Hit: {driver.find_element(By.ID, 'PastaTxt').get_attribute('title')!r}")
        espera(driver, lambda d: "Wait..." not in d.find_element(By.TAG_NAME, "body").text,
               timeout=60, passo=2.0)
        fecha_modais(driver)

        r = rota_zoom(driver)
        if r:
            resultados.append(r)
        r = rota_export(driver)
        if r:
            resultados.append(r)

        print("\n===== RESUMO =====")
        if not resultados:
            print("Nenhuma rota entregou arquivo; ver dumps em", DIAG_DIR)
        for r in resultados:
            print(" ", r)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
