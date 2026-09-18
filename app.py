import os
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Liga de Prognósticos — AF Porto Elite S2", layout="wide"
)

# Conexão ao Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# CALENDÁRIO OFICIAL EMBUTIDO (JORNADAS 1 A 30)
# ---------------------------------------------------------
CALENDARIO_LOCAL = {
    "1": [
        {"id_jogo": "J1_G1", "casa": "S.C. Castêlo Maia", "fora": "A.D. Grijó"},
        {
            "id_jogo": "J1_G2",
            "casa": "F.C. Infesta",
            "fora": "Varzim S.C. 'B' - SDUQ",
        },
        {
            "id_jogo": "J1_G3",
            "casa": "C.D. Candal",
            "fora": "Valadares Gaia F.C. - SAD",
        },
        {
            "id_jogo": "J1_G4",
            "casa": "A.R.D.C. Gondim Maia",
            "fora": "F.C. Pedroso",
        },
        {
            "id_jogo": "J1_G5",
            "casa": "Pedrouços Atl. C.",
            "fora": "S.C. Dragões Sandinenses",
        },
        {"id_jogo": "J1_G6", "casa": "U.D. Beiriz", "fora": "F.C. Avintes"},
        {
            "id_jogo": "J1_G7",
            "casa": "S.C. Salgueiros 'B' - SAD",
            "fora": "C.F. Oliveira Douro",
        },
        {
            "id_jogo": "J1_G8",
            "casa": "Atl. C. Bougadense",
            "fora": "Desp. Leça Balio",
        },
    ],
    "2": [
        {"id_jogo": "J2_G9", "casa": "A.D. Grijó", "fora": "Atl. C. Bougadense"},
        (
            {
                "id_jogo": "J2_G10",
                "casa": "Varzim S.C. 'B' - SDUQ",
                "fora": "S.C. Castêlo Maia",
            }
        ),
        (
            {
                "id_jogo": "J2_G11",
                "casa": "Valadares Gaia F.C. - SAD",
                "fora": "F.C. Infesta",
            }
        ),
        {"id_jogo": "J2_G12", "casa": "F.C. Pedroso", "fora": "C.D. Candal"},
        (
            {
                "id_jogo": "J2_G13",
                "casa": "S.C. Dragões Sandinenses",
                "fora": "A.R.D.C. Gondim Maia",
            }
        ),
        (
            {
                "id_jogo": "J2_G14",
                "casa": "F.C. Avintes",
                "fora": "Pedrouços Atl. C.",
            }
        ),
        (
            {
                "id_jogo": "J2_G15",
                "casa": "C.F. Oliveira Douro",
                "fora": "U.D. Beiriz",
            }
        ),
        (
            {
                "id_jogo": "J2_G16",
                "casa": "Desp. Leça Balio",
                "fora": "S.C. Salgueiros 'B' - SAD",
            }
        ),
    ],
}


def carregar_resultados_bd():
  resultados = {}
  try:
    res = supabase.table("jornadas").select("*").execute()
    if res.data:
      for item in res.data:
        resultados[item["id_jogo"]] = {
            "res_casa": item.get("res_casa"),
            "res_fora": item.get("res_fora"),
        }
  except Exception as e:
    pass
  return resultados


def carregar_palpites_bd():
  palpites = {}
  try:
    res = supabase.table("palpites").select("*").execute()
    if res.data:
      for item in res.data:
        jog = item.get("jogador")
        id_j = item.get("id_jogo")
        if jog and id_j:
          if jog not in palpites:
            palpites[jog] = {}
          palpites[jog][id_j] = {
              "c": item.get("p_casa", 0),
              "f": item.get("p_fora", 0),
          }
  except Exception as e:
    pass
  return palpites


resultados_dados = carregar_resultados_bd()
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
  jogos = CALENDARIO_LOCAL.get(str(num_jornada), [])
  if not jogos:
    return False
  for j in jogos:
    res = resultados_dados.get(j["id_jogo"], {})
    if res.get("res_casa") is None or res.get("res_fora") is None:
      return False
  return True


def obter_jornada_ativa():
  total = len(CALENDARIO_LOCAL)
  for j in range(1, total + 1):
    if not jornada_concluida(j):
      return j
  return total if total > 0 else 1


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
    pts_t, ex_t, tend_t = (
        {j: 0 for j in jogadores},
        {j: 0 for j in jogadores},
        {j: 0 for j in jogadores},
    )
    for j_num in CALENDARIO_LOCAL.keys():
      for jogo in CALENDARIO_LOCAL[j_num]:
        id_j = jogo["id_jogo"]
        res = resultados_dados.get(id_j, {})
        rc, rf = res.get("res_casa"), res.get("res_fora")
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
    jogos_j = CALENDARIO_LOCAL.get(str(j_ativa), [])
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
              "", min_value=0, max_value=15, value=p_ant["c"], key=f"p_c_{id_j}"
          )
        with col3:
          pf = st.number_input(
              "", min_value=0, max_value=15, value=p_ant["f"], key=f"p_f_{id_j}"
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
        st.success(f"Prognósticos de {nome} guardados com sucesso!")
        st.rerun()

# ---------------------------------------------------------
# ABA 3: PAINEL ADMIN
# ---------------------------------------------------------
elif aba == "⚙️ Painel Admin":
  st.header("⚙️ Painel de Administração")
  sub1, sub2 = st.tabs(["⚽ Inserir Resultados", "🗑️ Gerir / Apagar Jogadores"])

  with sub1:
    lista_j = [int(k) for k in CALENDARIO_LOCAL.keys()]
    j_sel = st.selectbox("Selecionar Jornada para Atualizar:", sorted(lista_j))

    with st.form("form_admin"):
      novos_res = []
      for jogo in CALENDARIO_LOCAL.get(str(j_sel), []):
        id_j = jogo["id_jogo"]
        res_ant = resultados_dados.get(id_j, {})
        val_c = (
            0 if res_ant.get("res_casa") is None else int(res_ant["res_casa"])
        )
        val_f = (
            0 if res_ant.get("res_fora") is None else int(res_ant["res_fora"])
        )

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
        registos_jornada = []
        for nr in novos_res:
          res_c = nr["c"] if marcar_fechado else None
          res_f = nr["f"] if marcar_fechado else None
          registos_jornada.append({
              "id_jogo": nr["id_jogo"],
              "jornada": j_sel,
              "res_casa": res_c,
              "res_fora": res_f,
          })
        supabase.table("jornadas").upsert(
            registos_jornada, on_conflict="id_jogo"
        ).execute()
        st.success(f"Resultados da Jornada {j_sel} guardados com sucesso!")
        st.rerun()

  with sub2:
    st.subheader("Eliminar Participante")
    lista_jogs = list(palpites_dados.keys())
    if not lista_jogs:
      st.info("Não existem jogadores registados.")
    else:
      jog_del = st.selectbox(
          "Seleciona o jogador a eliminar:", sorted(lista_jogs)
      )
      if st.button("❌ Eliminar Jogador"):
        supabase.table("palpites").delete().eq("jogador", jog_del).execute()
        st.success(f"O participante '{jog_del}' foi eliminado!")
        st.rerun()
