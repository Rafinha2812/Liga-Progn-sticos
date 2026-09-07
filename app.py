import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Liga de Prognósticos - AF Porto Elite S2", layout="wide"
)

FICHEIRO_DADOS = "dados_liga.json"
OPCOES_CALENDARIO = ["Calendário.csv", "calendario.csv", "Calendario.csv"]


# Mapeamento Oficial das Jornadas por Mês (Época 2026/2027)
def obter_mes_por_jornada(j):
  j = int(j)
  if j in [1, 2]:
    return "Setembro 2026"
  elif j in [3, 4, 5, 6]:
    return "Outubro 2026"
  elif j in [7, 8, 9, 10]:
    return "Novembro 2026"
  elif j in [11, 12, 13]:
    return "Dezembro 2026"
  elif j in [14, 15, 16]:
    return "Janeiro 2027"
  elif j in [17, 18, 19, 20]:
    return "Fevereiro 2027"
  elif j in [21, 22, 23, 24]:
    return "Março 2027"
  elif j in [25, 26, 27, 28]:
    return "Abril 2027"
  elif j in [29, 30]:
    return "Maio 2027"
  return "Outro"


LISTA_MESES = [
    "Setembro 2026",
    "Outubro 2026",
    "Novembro 2026",
    "Dezembro 2026",
    "Janeiro 2027",
    "Fevereiro 2027",
    "Março 2027",
    "Abril 2027",
    "Maio 2027",
]


def obter_ficheiro_calendario():
  for f in OPCOES_CALENDARIO:
    if os.path.exists(f):
      return f
  return None


def carregar_calendario_csv():
  ficheiro = obter_ficheiro_calendario()
  if not ficheiro:
    st.error("⚠️ Ficheiro 'Calendário.csv' não foi encontrado na pasta!")
    return {}

  df_cal = pd.read_csv(ficheiro)
  jornadas = {}

  for j_num, group in df_cal.groupby("jornada"):
    jogos = []
    for idx, row in group.iterrows():
      id_j = f"J{j_num}_G{idx+1}"
      jogos.append({
          "id_jogo": id_j,
          "casa": str(row["casa"]).strip(),
          "fora": str(row["fora"]).strip(),
          "res_casa": None,
          "res_fora": None,
      })
    jornadas[str(j_num)] = jogos
  return jornadas


def carregar_dados():
  if os.path.exists(FICHEIRO_DADOS):
    with open(FICHEIRO_DADOS, "r", encoding="utf-8") as f:
      return json.load(f)
  else:
    dados_iniciais = {"jornadas": carregar_calendario_csv(), "palpites": {}}
    guardar_dados(dados_iniciais)
    return dados_iniciais


def guardar_dados(dados):
  with open(FICHEIRO_DADOS, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)


dados = carregar_dados()


def calcular_pontos(p_c, p_f, r_c, r_f):
  if r_c is None or r_f is None or p_c is None or p_f is None:
    return 0
  # 2 Pontos: Resultado Exato
  if p_c == r_c and p_f == r_f:
    return 2

  # 1 Ponto: Tendência (1X2)
  tend_p = (p_c > p_f) - (p_c < p_f)
  tend_r = (r_c > r_f) - (r_c < r_f)
  if tend_p == tend_r:
    return 1
  return 0


def jornada_concluida(num_jornada):
  jogos = dados["jornadas"].get(str(num_jornada), [])
  if not jogos:
    return False
  return all(
      j["res_casa"] is not None and j["res_fora"] is not None for j in jogos
  )


def obter_jornada_ativa():
  total_jornadas = len(dados["jornadas"])
  for j in range(1, total_jornadas + 1):
    if not jornada_concluida(j):
      return j
  return total_jornadas


# Interface Principal
st.title("🏆 Liga de Prognósticos — AF Porto (Elite Série 2)")

aba = st.sidebar.radio(
    "Navegação",
    [
        "📊 Classificações",
        "📝 Inserir Palpites",
        "⚙️ Painel Admin (Resultados)",
    ],
)

# ---------------------------------------------------------
# ABA 1: CLASSIFICAÇÕES (GERAL, MENSAL, JORNADA)
# ---------------------------------------------------------
if aba == "📊 Classificações":
  st.header("📊 Tabelas de Classificação")

  jogadores = list(dados["palpites"].keys())
  if not jogadores:
    st.info("Ainda não existem palpites registados.")
  else:
    sub_aba1, sub_aba2, sub_aba3 = st.tabs(
        ["🏆 Geral (Época)", "📅 Por Mês", "⚽ Por Jornada"]
    )

    # -----------------------------------------------------
    # SUB-ABA 1.1: CLASSIFICAÇÃO GERAL
    # -----------------------------------------------------
    with sub_aba1:
      st.subheader("Classificação Geral Acumulada")

      pontos_totais = {j: 0 for j in jogadores}
      exatos_totais = {j: 0 for j in jogadores}
      tendencias_totais = {j: 0 for j in jogadores}

      for j_num in dados["jornadas"].keys():
        jogos = dados["jornadas"][j_num]
        for jogo in jogos:
          id_j = jogo["id_jogo"]
          rc, rf = jogo["res_casa"], jogo["res_fora"]

          for jog in jogadores:
            palp = dados["palpites"][jog].get(id_j)
            if palp and rc is not None and rf is not None:
              pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
              pontos_totais[jog] += pts
              if pts == 2:
                exatos_totais[jog] += 1
              elif pts == 1:
                tendencias_totais[jog] += 1

      df_geral = (
          pd.DataFrame({
              "Participante": jogadores,
              "Pontos Totais": [pontos_totais[j] for j in jogadores],
              "Resultados Exatos (2 pts)": [exatos_totais[j] for j in jogadores],
              "Tendências Certas (1 pt)": [
                  tendencias_totais[j] for j in jogadores
              ],
          })
          .sort_values(by="Pontos Totais", ascending=False)
          .reset_index(drop=True)
      )

      df_geral.index += 1
      st.table(df_geral)

    # -----------------------------------------------------
    # SUB-ABA 1.2: CLASSIFICAÇÃO MENSAL
    # -----------------------------------------------------
    with sub_aba2:
      st.subheader("Classificação por Mês")
      mes_sel = st.selectbox("Escolher o Mês:", LISTA_MESES)

      pontos_mes = {j: 0 for j in jogadores}
      exatos_mes = {j: 0 for j in jogadores}
      tendencias_mes = {j: 0 for j in jogadores}

      for j_num in dados["jornadas"].keys():
        if obter_mes_por_jornada(j_num) == mes_sel:
          jogos = dados["jornadas"][j_num]
          for jogo in jogos:
            id_j = jogo["id_jogo"]
            rc, rf = jogo["res_casa"], jogo["res_fora"]

            for jog in jogadores:
              palp = dados["palpites"][jog].get(id_j)
              if palp and rc is not None and rf is not None:
                pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
                pontos_mes[jog] += pts
                if pts == 2:
                  exatos_mes[jog] += 1
                elif pts == 1:
                  tendencias_mes[jog] += 1

      df_mes = (
          pd.DataFrame({
              "Participante": jogadores,
              f"Pontos ({mes_sel})": [pontos_mes[j] for j in jogadores],
              "Resultados Exatos (2 pts)": [exatos_mes[j] for j in jogadores],
              "Tendências Certas (1 pt)": [tendencias_mes[j] for j in jogadores],
          })
          .sort_values(by=f"Pontos ({mes_sel})", ascending=False)
          .reset_index(drop=True)
      )

      df_mes.index += 1
      st.table(df_mes)

    # -----------------------------------------------------
    # SUB-ABA 1.3: CLASSIFICAÇÃO POR JORNADA
    # -----------------------------------------------------
    with sub_aba3:
      st.subheader("Pontuação Individual por Jornada")
      lista_j = [int(k) for k in dados["jornadas"].keys()]
      j_sel_tab = st.selectbox("Escolher Jornada:", sorted(lista_j))

      pontos_j = {j: 0 for j in jogadores}
      exatos_j = {j: 0 for j in jogadores}
      tendencias_j = {j: 0 for j in jogadores}

      jogos_j = dados["jornadas"].get(str(j_sel_tab), [])
      for jogo in jogos_j:
        id_j = jogo["id_jogo"]
        rc, rf = jogo["res_casa"], jogo["res_fora"]

        for jog in jogadores:
          palp = dados["palpites"][jog].get(id_j)
          if palp and rc is not None and rf is not None:
            pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
            pontos_j[jog] += pts
            if pts == 2:
              exatos_j[jog] += 1
            elif pts == 1:
              tendencias_j[jog] += 1

      df_j = (
          pd.DataFrame({
              "Participante": jogadores,
              f"Pontos J{j_sel_tab}": [pontos_j[j] for j in jogadores],
              "Resultados Exatos (2 pts)": [exatos_j[j] for j in jogadores],
              "Tendências Certas (1 pt)": [tendencias_j[j] for j in jogadores],
          })
          .sort_values(by=f"Pontos J{j_sel_tab}", ascending=False)
          .reset_index(drop=True)
      )

      df_j.index += 1
      st.table(df_j)

# ---------------------------------------------------------
# ABA 2: INSERIR PALPITES
# ---------------------------------------------------------
elif aba == "📝 Inserir Palpites":
  st.header("📝 Registar Prognósticos")

  j_ativa = obter_jornada_ativa()
  st.info(f"🔒 **Jornada Aberta para Palpites:** Jornada {j_ativa}")

  if j_ativa > 1:
    st.caption(
        f"As jornadas 1 a {j_ativa-1} já se encontram encerradas. A Jornada"
        f" {j_ativa+1} só abrirá quando o Admin concluir a Jornada {j_ativa}."
    )

  nome = st.text_input("Teu Nome / Alcunha:")

  if nome:
    jogos_jornada = dados["jornadas"].get(str(j_ativa), [])
    if not jogos_jornada:
      st.warning("Não existem jogos registados para esta jornada.")
    else:
      with st.form("form_palpites"):
        st.subheader(f"Jogos da Jornada {j_ativa}")
        novos_p = {}

        for jogo in jogos_jornada:
          id_j = jogo["id_jogo"]
          p_ant = dados["palpites"].get(nome, {}).get(id_j, {"c": 0, "f": 0})

          col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
          with col1:
            st.write(f"**{jogo['casa']}**")
          with col2:
            pc = st.number_input(
                "",
                min_value=0,
                max_value=15,
                value=p_ant["c"],
                key=f"p_c_{id_j}",
            )
          with col3:
            pf = st.number_input(
                "",
                min_value=0,
                max_value=15,
                value=p_ant["f"],
                key=f"p_f_{id_j}",
            )
          with col4:
            st.write(f"**{jogo['fora']}**")

          novos_p[id_j] = {"c": pc, "f": pf}

        if st.form_submit_button("Guardar Prognósticos"):
          if nome not in dados["palpites"]:
            dados["palpites"][nome] = {}
          dados["palpites"][nome].update(novos_p)
          guardar_dados(dados)
          st.success(
              f"Prognósticos de {nome} guardados para a Jornada {j_ativa}!"
          )

# ---------------------------------------------------------
# ABA 3: PAINEL ADMIN
# ---------------------------------------------------------
elif aba == "⚙️ Painel Admin (Resultados)":
  st.header("⚙️ Inserir Resultados Oficiais")

  lista_jornadas = [int(k) for k in dados["jornadas"].keys()]
  j_sel = st.selectbox(
      "Selecionar Jornada para Atualizar:", sorted(lista_jornadas)
  )

  with st.form("form_admin"):
    novos_res = []
    for jogo in dados["jornadas"][str(j_sel)]:
      id_j = jogo["id_jogo"]
      val_c = 0 if jogo["res_casa"] is None else int(jogo["res_casa"])
      val_f = 0 if jogo["res_fora"] is None else int(jogo["res_fora"])

      col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
      with col1:
        st.write(f"**{jogo['casa']}**")
      with col2:
        rc = st.number_input(
            "", min_value=0, max_value=15, value=val_c, key=f"r_c_{id_j}"
        )
      with col3:
        rf = st.number_input(
            "", min_value=0, max_value=15, value=val_f, key=f"r_f_{id_j}"
        )
      with col4:
        st.write(f"**{jogo['fora']}**")

      novos_res.append({"id_jogo": id_j, "c": rc, "f": rf})

    marcar_fechado = st.checkbox(
        "Marcar TODOS os jogos desta jornada como concluídos"
    )

    if st.form_submit_button("Guardar Resultados"):
      for nr in novos_res:
        for jg in dados["jornadas"][str(j_sel)]:
          if jg["id_jogo"] == nr["id_jogo"]:
            if marcar_fechado:
              jg["res_casa"] = nr["c"]
              jg["res_fora"] = nr["f"]
            else:
              jg["res_casa"] = None
              jg["res_fora"] = None

      guardar_dados(dados)
      st.success(f"Resultados da Jornada {j_sel} atualizados!")
      if marcar_fechado:
        st.info(f"🔓 A Jornada {j_sel + 1} fica agora disponível para palpites!")