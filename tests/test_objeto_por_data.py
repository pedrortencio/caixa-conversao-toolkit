"""Testes da resolucao de objeto por data.

O que precisa nao falhar: nunca devolver um objeto como se a data estivesse
confirmada quando ela foi inferida. A resolucao carrega o metodo junto, e
`incerto` e resultado legitimo.
"""
from __future__ import annotations

from datetime import date

from pipeline.triagem import objeto_por_data as mod


# --- o parser de dia e mes ---------------------------------------------------


def test_le_dia_e_mes_do_masthead_limpo():
    assert mod.parse_dia_mes("Rio de Janeiro - domingo, 11 de marco de 1906") == (11, 3)


def test_ignora_o_ano_impresso_porque_o_ocr_o_corrompe():
    """`per103730_1912_00017` traz `dé 1913` num jornal de 1912. O ano vem do
    nome do objeto, nunca do masthead."""
    assert mod.parse_dia_mes("Qfrarta-feira j? de Janeiro dé 1913") is None
    assert mod.parse_dia_mes("Quarta-feira 17 de Janeiro dé 1913") == (17, 1)


def test_tolera_ruido_do_ocr_no_dia_da_semana():
    assert mod.parse_dia_mes("ter<|á>.féira 16 de Janeiro de i91S") == (16, 1)


def test_tolera_mes_sem_a_preposicao():
    assert mod.parse_dia_mes("Rio, 5 marco 1910") == (5, 3)


def test_recusa_data_impossivel():
    assert mod.parse_dia_mes("32 de janeiro de 1912") is None


def test_recusa_linha_sem_data():
    assert mod.parse_dia_mes("ASSIGNATURAS PAGAMENTO ADIANTADO") is None


def test_numero_do_objeto_sai_do_identificador():
    assert mod.numero_do_objeto("per103730_1912_00017") == 17
    assert mod.numero_do_objeto("per089842_1906_01703") == 1703


# --- a resolucao -------------------------------------------------------------


def indice(pares: dict[int, tuple[int, int, int]]) -> dict[str, date]:
    return {f"per103730_{a}_{n:05d}": date(a, m, d) for n, (a, m, d) in pares.items()}


def test_acerto_direto_quando_o_masthead_do_dia_e_legivel():
    r = mod.resolve(date(1912, 1, 17), indice({17: (1912, 1, 17)}))
    assert r.objeto == "per103730_1912_00017"
    assert r.metodo == "masthead"


def test_vizinhos_fixam_o_dia_que_o_ocr_perdeu():
    """O caso `gn1912`: 00016 traz 16 de janeiro, 00018 traz 18, e 00017 e
    ilegivel. A aritmetica fecha e a data e 17."""
    r = mod.resolve(date(1912, 1, 17), indice({16: (1912, 1, 16), 18: (1912, 1, 18)}))
    assert r.objeto == "per103730_1912_00017"
    assert r.metodo == "vizinhos"


def test_incerto_quando_ha_dia_sem_edicao_entre_as_ancoras():
    """Se o intervalo de numeros nao bate com o intervalo de dias, houve dia sem
    edicao no meio e a contagem nao pode ser exata."""
    r = mod.resolve(date(1912, 1, 17), indice({15: (1912, 1, 15), 18: (1912, 1, 19)}))
    assert r.metodo == "incerto"
    assert r.objeto is not None


def test_ancora_so_de_um_lado_nao_confirma():
    r = mod.resolve(date(1912, 1, 17), indice({10: (1912, 1, 10)}))
    assert r.metodo == "incerto"


def test_sem_ancora_nenhuma_nao_inventa():
    r = mod.resolve(date(1912, 1, 17), {})
    assert r.objeto is None
    assert r.metodo == "sem_ancora"


def test_a_evidencia_nomeia_as_ancoras_usadas():
    r = mod.resolve(date(1912, 1, 17), indice({16: (1912, 1, 16), 18: (1912, 1, 18)}))
    assert "per103730_1912_00016" in r.evidencia
    assert "per103730_1912_00018" in r.evidencia


def test_ancoras_distantes_ainda_resolvem_se_a_aritmetica_fecha():
    pares = {1: (1912, 1, 1), 31: (1912, 1, 31)}
    r = mod.resolve(date(1912, 1, 17), indice(pares))
    assert r.objeto == "per103730_1912_00017"
    assert r.metodo == "vizinhos"


def test_escolhe_as_ancoras_mais_proximas_em_data():
    """Com muitas ancoras, tem de pegar as que cercam o alvo de perto. Ordenar
    por numero do objeto e fatiar por data pega a ultima em ordem de numero, que
    e outra coisa."""
    r = mod.resolve(
        date(1912, 1, 17),
        indice({2: (1912, 1, 2), 16: (1912, 1, 16), 18: (1912, 1, 18), 30: (1912, 1, 30)}),
    )
    assert r.metodo == "vizinhos"
    assert "per103730_1912_00016" in r.evidencia
    assert "per103730_1912_00030" not in r.evidencia


def test_espinha_descarta_a_data_que_nao_cabe_na_cadeia():
    """Medido em O Paiz 1910: 16,4% das datas lidas sao falsas, pescadas dentro
    de materias. `09223` saiu como 30 de dezembro entre vizinhos de 5 e 7 de
    janeiro. A espinha e a maior cadeia consistente entre numero e data."""
    bruto = indice({23: (1910, 12, 30), 24: (1910, 1, 5), 26: (1910, 1, 7), 28: (1910, 1, 9)})
    limpo = mod.espinha(bruto)
    assert "per103730_1910_00023" not in limpo
    assert len(limpo) == 3


def test_espinha_preserva_indice_ja_consistente():
    bruto = indice({16: (1912, 1, 16), 17: (1912, 1, 17), 18: (1912, 1, 18)})
    assert mod.espinha(bruto) == bruto


def test_resolve_ignora_ancora_fora_da_espinha():
    """A ancora falsa nao pode ser escolhida so por estar perto em data."""
    bruto = indice(
        {23: (1910, 5, 18), 24: (1910, 5, 12), 26: (1910, 5, 14), 28: (1910, 5, 16)}
    )
    r = mod.resolve(date(1910, 5, 13), bruto)
    assert r.metodo == "vizinhos"
    assert "per103730_1910_00023" not in r.evidencia


def test_numeracao_que_nao_cresce_com_a_data_nao_resolve():
    """Medido em O Paiz 1910: o numero do objeto nao e monotono na data. A
    premissa do modulo nao vale ali, e isso tem de sair como `incerto`."""
    r = mod.resolve(
        date(1910, 5, 14),
        {
            "per178691_1910_09510": date(1910, 2, 5),
            "per178691_1910_09223": date(1910, 12, 30),
        },
    )
    assert r.metodo == "incerto"


def test_alvo_fora_do_intervalo_coberto_e_incerto():
    r = mod.resolve(date(1912, 2, 20), indice({16: (1912, 1, 16), 18: (1912, 1, 18)}))
    assert r.metodo == "incerto"
