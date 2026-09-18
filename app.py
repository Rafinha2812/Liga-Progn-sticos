import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Liga de Prognósticos - AF Porto Elite S2", layout="wide"
)

# Conexão com o Supabase através dos Secrets do Streamlit
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Carregar/Inicializar Calendário na Base de Dados se estiver vazia
def inicializar_calendario_bd():
  res = supabase.table("jornadas").select("id_jogo").limit(1).execute()
  if not res.data and os.path.exists("Calendário.csv"):
    df_cal = pd.read_csv("Calendário.csv")
    dados_para_inserir = []
    for idx, row in df_cal.iterrows():
      j_num = row["jornada"]
      dados_para_inserir.append({
          "id_jogo": f"J{j_num}_G{idx+1}",
          "jornada": int(j_num),
          "casa": str(row["casa"]).strip(),
          "fora": str(row["fora"]).strip(),
          "res_casa": None,
          "res_fora": None,
      })
    supabase.table("jornadas").insert(dados_para_inserir).execute()


# Tentar inicializar o calendário
import os

try:
  inicializar_calendario_bd()
except Exception as e:
  pass


# Funções de Leitura e Escrita na BD
def carregar_jornadas_bd():
  res = (
      supabase.table("jornadas")
      .select("*")
      .order("jornada", desc=False)
      .execute()
  )
  jornadas = {}
  for item in res.data:
    j_str = str(item["jornada"])
    if j_str not in jornadas:
      jornadas[j_str] = []
    jornadas[j_str].append(item)
  return jornadas


def carregar_palpites_bd():
  res = supabase.table("palpites").select("*").execute()
  palpites = {}
  for item in res.data:
    jog = item["jogador"]
    if jog not in palpites:
      palpites[jog] = {}
    palpites[jog][item["id_jogo"]] = {"c": item["p_casa"], "f": item["p_fora"]}
  return palpites


jornadas_dados = carregar_jornadas_bd()
palpites_dados = carregar_palpites_bd()


def calcular_pontos(p_c, p_f, r_c, r_f):
  if r_c is None or r_f is None or p_c is None or p_f is None:
    return 0
  if p_c == r_c and p_f == r_f:
    return 2
  tend_p = (p_c > p_f) - (p_c < p_f)
  tend_r = (r_c > r_f) - (r_c < r_f)
  if tend_p == tend_r:
    return 1
  return 0


def jornada_concluida(num_jornada):
  jogos = jornadas_dados.get(str(num_jornada), [])
  if not jogos:
    return False
  return all(
      j["res_casa"] is not None and j["res_fora"] is not None for j in jogos
  )


def obter_jornada_ativa():
  total = len(jornadas_dados)
  for j in range(1, total + 1):
    if not jornada_concluida(j):
      return j
  return total if total > 0 else 1


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

# Interface
st.title("🏆 Liga de Prognósticos — AF Porto (Elite Série 2)")

aba = st.sidebar.radio(
    "Navegação",
    ["📊 Classificações", "📝 Inserir Palpites", "⚙️ Painel Admin"],
)

# ---------------------------------------------------------
# ABA 1: CLASSIFICAÇÕES
# ---------------------------------------------------------
if aba == "📊 Classificações":
  st.header("📊 Tabelas de Classificação")
  jogadores = list(palpites_dados.keys())

  if not jogadores:
    st.info("Ainda não existem palpites registados.")
  else:
    sub_aba1, sub_aba2, sub_aba3 = st.tabs(
        ["🏆 Geral (Época)", "📅 Por Mês", "⚽ Por Jornada"]
    )

    with sub_aba1:
      st.subheader("Classificação Geral Acumulada")
      pts_t, ex_t, tend_t = (
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
      )

      for j_num in jornadas_dados.keys():
        for jogo in jornadas_dados[j_num]:
          id_j, rc, rf = jogo["id_jogo"], jogo["res_casa"], jogo["res_fora"]
          for jog in jogadores:
            palp = palpites_dados[jog].get(id_j)
            if palp and rc is not None and rf is not None:
              pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
              pts_t[jog] += pts
              if pts == 2:
                ex_t[jog] += 1
              elif pts == 1:
                tend_t[jog] += 1

      df_g = (
          pd.DataFrame({
              "Participante": jogadores,
              "Pontos Totais": [pts_t[j] for j in jogadores],
              "Resultados Exatos (2 pts)": [ex_t[j] for j in jogadores],
              "Tendências Certas (1 pt)": [tend_t[j] for j in jogadores],
          })
          .sort_values(by="Pontos Totais", ascending=False)
          .reset_index(drop=True)
      )
      df_g.index += 1
      st.table(df_g)

    with sub_aba2:
      st.subheader("Classificação por Mês")
      mes_sel = st.selectbox("Escolher Mês:", LISTA_MESES)
      pts_m, ex_m, tend_m = (
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
      )

      for j_num in jornadas_dados.keys():
        if obter_mes_por_jornada(j_num) == mes_sel:
          for jogo in jornadas_dados[j_num]:
            id_j, rc, rf = jogo["id_jogo"], jogo["res_casa"], jogo["res_fora"]
            for jog in jogadores:
              palp = palpites_dados[jog].get(id_j)
              if palp and rc is not None and rf is not None:
                pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
                pts_m[jog] += pts
                if pts == 2:
                  ex_m[jog] += 1
                elif pts == 1:
                  tend_m[jog] += 1

      df_m = (
          pd.DataFrame({
              "Participante": jogadores,
              f"Pontos ({mes_sel})": [pts_m[j] for j in jogadores],
              "Resultados Exatos (2 pts)": [ex_m[j] for j in jogadores],
              "Tendências Certas (1 pt)": [tend_m[j] for j in jogadores],
          })
          .sort_values(by=f"Pontos ({mes_sel})", ascending=False)
          .reset_index(drop=True)
      )
      df_m.index += 1
      st.table(df_m)

    with sub_aba3:
      st.subheader("Pontuação Individual por Jornada")
      lista_j = [int(k) for k in jornadas_dados.keys()]
      j_sel_tab = st.selectbox("Escolher Jornada:", sorted(lista_j))
      pts_j, ex_j, tend_j = (
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
      )

      for jogo in jornadas_dados.get(str(j_sel_tab), []):
        id_j, rc, rf = jogo["id_jogo"], jogo["res_casa"], jogo["res_fora"]
        for jog in jogadores:
          palp = palpites_dados[jog].get(id_j)
          if palp and rc is not None and rf is not None:
            pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
            pts_j[jog] += pts
            if pts == 2:
              ex_j[jog] += 1
            elif pts == 1:
              tend_j[jog] += 1

      df_j = (
          pd.DataFrame({
              "Participante": jogadores,
              f"Pontos J{j_sel_tab}": [pts_j[j] for j in jogadores],
              "Resultados Exatos (2 pts)": [ex_j[j] for j in jogadores],
              "Tendências Certas (1 pt)": [tend_j[j] for j in jogadores],
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

  lista_existentes = list(palpites_dados.keys())
  opcao_jog = (
      st.radio(
          "Identificação do Apostador:",
          ["Apostador Existente", "Novo Apostador"],
          horizontal=True,
      )
      if lista_existentes
      else "Novo Apostador"
  )

  if opcao_jog == "Apostador Existente":
    nome = st.selectbox("Seleciona o teu nome:", sorted(lista_existentes))
  else:
    nome = st.text_input("Escreve o teu Nome / Alcunha:").strip()

  if nome:
    jogos_j = jornadas_dados.get(str(j_ativa), [])
    with st.form("form_palpites"):
      st.subheader(f"Palpites de {nome} para a Jornada {j_ativa}")
      novos_p = {}
      for jogo in jogos_j:
        id_j = jogo["id_jogo"]
        p_ant = palpites_dados.get(nome, {}).get(id_j, {"c": 0, "f": 0})
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
        registos = []
        for id_j, val in novos_p.items():
          registos.append({
              "jogador": nome,
              "id_jogo": id_j,
              "p_casa": val["c"],
              "p_fora": val["f"],
          })
        supabase.table("palpites").upsert(
            registos, on_conflict="jogador,id_jogo"
        ).execute()
        st.success(
            f"Prognósticos de {nome} guardados na base de dados com sucesso!"
        )
        st.rerun()

# ---------------------------------------------------------
# ABA 3: PAINEL ADMIN
# ---------------------------------------------------------
elif aba == "⚙️ Painel Admin":
  st.header("⚙️ Painel de Administração")
  sub1, sub2 = st.tabs(["⚽ Inserir Resultados", "🗑️ Gerir / Apagar Jogadores"])

  with sub1:
    lista_j = [int(k) for k in jornadas_dados.keys()]
    j_sel = st.selectbox("Selecionar Jornada para Atualizar:", sorted(lista_j))

    with st.form("form_admin"):
      novos_res = []
      for jogo in jornadas_dados[str(j_sel)]:
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
          res_c = nr["c"] if marcar_fechado else None
          res_f = nr["f"] if marcar_fechado else None
          supabase.table("jornadas").update(
              {"res_casa": res_c, "res_fora": res_f}
          ).eq("id_jogo", nr["id_jogo"]).execute()
        st.success(f"Resultados da Jornada {j_sel} guardados na base de dados!")
        st.rerun()

  with sub2:
    st.subheader("Eliminar Participante")
    lista_jogs = list(palpites_dados.keys())
    if not lista_jogs:
      st.info("Não existem jogadores registados.")
    else:
      jog_del = st.selectbox("Seleciona o jogador a eliminar:", sorted(lista_jogs))
      if st.button("❌ Eliminar Jogador"):
        supabase.table("palpites").delete().eq("jogador", jog_del).execute()
        st.success(f"O participante '{jog_del}' foi eliminado!")
        st.rerun()
