import base64
import json
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Liga de Prognósticos — AF Porto Elite S2", layout="wide"
)

# Configurações do GitHub via Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
FILE_PATH = "dados_liga.json"
URL_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# CALENDÁRIO OFICIAL EMBUTIDO (JORNADAS 1 A 30 COMPLETO)
CALENDARIO_LOCAL = {
    "1": [
        {"id_jogo": "J1_G1", "casa": "S.C. Castêlo Maia", "fora": "A.D. Grijó"},
        {"id_jogo": "J1_G2", "casa": "F.C. Infesta", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J1_G3", "casa": "C.D. Candal", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J1_G4", "casa": "A.R.D.C. Gondim Maia", "fora": "F.C. Pedroso"},
        {"id_jogo": "J1_G5", "casa": "Pedrouços Atl. C.", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J1_G6", "casa": "U.D. Beiriz", "fora": "F.C. Avintes"},
        {"id_jogo": "J1_G7", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J1_G8", "casa": "Atl. C. Bougadense", "fora": "Desp. Leça Balio"},
    ],
    "2": [
        {"id_jogo": "J2_G9", "casa": "A.D. Grijó", "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J2_G10", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J2_G11", "casa": "Valadares Gaia F.C. - SAD", "fora": "F.C. Infesta"},
        {"id_jogo": "J2_G12", "casa": "F.C. Pedroso", "fora": "C.D. Candal"},
        {"id_jogo": "J2_G13", "casa": "S.C. Dragões Sandinenses", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J2_G14", "casa": "F.C. Avintes", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J2_G15", "casa": "C.F. Oliveira Douro", "fora": "U.D. Beiriz"},
        {"id_jogo": "J2_G16", "casa": "Desp. Leça Balio", "fora": 'S.C. Salgueiros "B" - SAD'},
    ],
    "3": [
        {"id_jogo": "J3_G17", "casa": "A.D. Grijó", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J3_G18", "casa": "S.C. Castêlo Maia", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J3_G19", "casa": "F.C. Infesta", "fora": "F.C. Pedroso"},
        {"id_jogo": "J3_G20", "casa": "C.D. Candal", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J3_G21", "casa": "A.R.D.C. Gondim Maia", "fora": "F.C. Avintes"},
        {"id_jogo": "J3_G22", "casa": "Pedrouços Atl. C.", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J3_G23", "casa": "U.D. Beiriz", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J3_G24", "casa": "Atl. C. Bougadense", "fora": 'S.C. Salgueiros "B" - SAD'},
    ],
    "4": [
        {"id_jogo": "J4_G25", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J4_G26", "casa": "Valadares Gaia F.C. - SAD", "fora": "A.D. Grijó"},
        {"id_jogo": "J4_G27", "casa": "F.C. Pedroso", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J4_G28", "casa": "S.C. Dragões Sandinenses", "fora": "F.C. Infesta"},
        {"id_jogo": "J4_G29", "casa": "F.C. Avintes", "fora": "C.D. Candal"},
        {"id_jogo": "J4_G30", "casa": "C.F. Oliveira Douro", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J4_G31", "casa": "Desp. Leça Balio", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J4_G32", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "U.D. Beiriz"},
    ],
    "5": [
        {"id_jogo": "J5_G33", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J5_G34", "casa": "A.D. Grijó", "fora": "F.C. Pedroso"},
        {"id_jogo": "J5_G35", "casa": "S.C. Castêlo Maia", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J5_G36", "casa": "F.C. Infesta", "fora": "F.C. Avintes"},
        {"id_jogo": "J5_G37", "casa": "C.D. Candal", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J5_G38", "casa": "A.R.D.C. Gondim Maia", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J5_G39", "casa": "Pedrouços Atl. C.", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J5_G40", "casa": "Atl. C. Bougadense", "fora": "U.D. Beiriz"},
    ],
    "6": [
        {"id_jogo": "J6_G41", "casa": "Valadares Gaia F.C. - SAD", "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J6_G42", "casa": "F.C. Pedroso", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J6_G43", "casa": "S.C. Dragões Sandinenses", "fora": "A.D. Grijó"},
        {"id_jogo": "J6_G44", "casa": "F.C. Avintes", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J6_G45", "casa": "C.F. Oliveira Douro", "fora": "F.C. Infesta"},
        {"id_jogo": "J6_G46", "casa": "Desp. Leça Balio", "fora": "C.D. Candal"},
        {"id_jogo": "J6_G47", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J6_G48", "casa": "U.D. Beiriz", "fora": "Pedrouços Atl. C."},
    ],
    "7": [
        {"id_jogo": "J7_G49", "casa": "Valadares Gaia F.C. - SAD", "fora": "F.C. Pedroso"},
        {"id_jogo": "J7_G50", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J7_G51", "casa": "A.D. Grijó", "fora": "F.C. Avintes"},
        {"id_jogo": "J7_G52", "casa": "S.C. Castêlo Maia", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J7_G53", "casa": "F.C. Infesta", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J7_G54", "casa": "C.D. Candal", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J7_G55", "casa": "A.R.D.C. Gondim Maia", "fora": "U.D. Beiriz"},
        {"id_jogo": "J7_G56", "casa": "Atl. C. Bougadense", "fora": "Pedrouços Atl. C."},
    ],
    "8": [
        {"id_jogo": "J8_G57", "casa": "F.C. Pedroso", "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J8_G58", "casa": "S.C. Dragões Sandinenses", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J8_G59", "casa": "F.C. Avintes", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J8_G60", "casa": "C.F. Oliveira Douro", "fora": "A.D. Grijó"},
        {"id_jogo": "J8_G61", "casa": "Desp. Leça Balio", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J8_G62", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "F.C. Infesta"},
        {"id_jogo": "J8_G63", "casa": "U.D. Beiriz", "fora": "C.D. Candal"},
        {"id_jogo": "J8_G64", "casa": "Pedrouços Atl. C.", "fora": "A.R.D.C. Gondim Maia"},
    ],
    "9": [
        {"id_jogo": "J9_G65", "casa": "F.C. Pedroso", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J9_G66", "casa": "Valadares Gaia F.C. - SAD", "fora": "F.C. Avintes"},
        {"id_jogo": "J9_G67", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J9_G68", "casa": "A.D. Grijó", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J9_G69", "casa": "S.C. Castêlo Maia", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J9_G70", "casa": "F.C. Infesta", "fora": "U.D. Beiriz"},
        {"id_jogo": "J9_G71", "casa": "C.D. Candal", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J9_G72", "casa": "Atl. C. Bougadense", "fora": "A.R.D.C. Gondim Maia"},
    ],
    "10": [
        {"id_jogo": "J10_G73", "casa": "S.C. Dragões Sandinenses", "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J10_G74", "casa": "F.C. Avintes", "fora": "F.C. Pedroso"},
        {"id_jogo": "J10_G75", "casa": "C.F. Oliveira Douro", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J10_G76", "casa": "Desp. Leça Balio", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J10_G77", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "A.D. Grijó"},
        {"id_jogo": "J10_G78", "casa": "U.D. Beiriz", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J10_G79", "casa": "Pedrouços Atl. C.", "fora": "F.C. Infesta"},
        {"id_jogo": "J10_G80", "casa": "A.R.D.C. Gondim Maia", "fora": "C.D. Candal"},
    ],
    "11": [
        {"id_jogo": "J11_G81", "casa": "S.C. Dragões Sandinenses", "fora": "F.C. Avintes"},
        {"id_jogo": "J11_G82", "casa": "F.C. Pedroso", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J11_G83", "casa": "Valadares Gaia F.C. - SAD", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J11_G84", "casa": 'Varzim S.C. "B" - SDUQ', "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J11_G85", "casa": "A.D. Grijó", "fora": "U.D. Beiriz"},
        {"id_jogo": "J11_G86", "casa": "S.C. Castêlo Maia", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J11_G87", "casa": "F.C. Infesta", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J11_G88", "casa": "Atl. C. Bougadense", "fora": "C.D. Candal"},
    ],
    "12": [
        {"id_jogo": "J12_G89", "casa": "F.C. Avintes", "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J12_G90", "casa": "C.F. Oliveira Douro", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J12_G91", "casa": "Desp. Leça Balio", "fora": "F.C. Pedroso"},
        {"id_jogo": "J12_G92", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J12_G93", "casa": "U.D. Beiriz", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J12_G94", "casa": "Pedrouços Atl. C.", "fora": "A.D. Grijó"},
        {"id_jogo": "J12_G95", "casa": "A.R.D.C. Gondim Maia", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J12_G96", "casa": "C.D. Candal", "fora": "F.C. Infesta"},
    ],
    "13": [
        {"id_jogo": "J13_G97", "casa": "F.C. Avintes", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J13_G98", "casa": "S.C. Dragões Sandinenses", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J13_G99", "casa": "F.C. Pedroso", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J13_G100", "casa": "Valadares Gaia F.C. - SAD", "fora": "U.D. Beiriz"},
        {"id_jogo": "J13_G101", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J13_G102", "casa": "A.D. Grijó", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J13_G103", "casa": "S.C. Castêlo Maia", "fora": "C.D. Candal"},
        {"id_jogo": "J13_G104", "casa": "Atl. C. Bougadense", "fora": "F.C. Infesta"},
    ],
    "14": [
        {"id_jogo": "J14_G105", "casa": "Atl. C. Bougadense", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J14_G106", "casa": "Desp. Leça Balio", "fora": "F.C. Avintes"},
        {"id_jogo": "J14_G107", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J14_G108", "casa": "U.D. Beiriz", "fora": "F.C. Pedroso"},
        {"id_jogo": "J14_G109", "casa": "Pedrouços Atl. C.", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J14_G110", "casa": "A.R.D.C. Gondim Maia", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J14_G111", "casa": "C.D. Candal", "fora": "A.D. Grijó"},
        {"id_jogo": "J14_G112", "casa": "F.C. Infesta", "fora": "S.C. Castêlo Maia"},
    ],
    "15": [
        {"id_jogo": "J15_G113", "casa": "C.F. Oliveira Douro", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J15_G114", "casa": "F.C. Avintes", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J15_G115", "casa": "S.C. Dragões Sandinenses", "fora": "U.D. Beiriz"},
        {"id_jogo": "J15_G116", "casa": "F.C. Pedroso", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J15_G117", "casa": "Valadares Gaia F.C. - SAD", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J15_G118", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "C.D. Candal"},
        {"id_jogo": "J15_G119", "casa": "A.D. Grijó", "fora": "F.C. Infesta"},
        {"id_jogo": "J15_G120", "casa": "S.C. Castêlo Maia", "fora": "Atl. C. Bougadense"},
    ],
    "16": [
        {"id_jogo": "J16_G121", "casa": "A.D. Grijó", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J16_G122", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "F.C. Infesta"},
        {"id_jogo": "J16_G123", "casa": "Valadares Gaia F.C. - SAD", "fora": "C.D. Candal"},
        {"id_jogo": "J16_G124", "casa": "F.C. Pedroso", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J16_G125", "casa": "S.C. Dragões Sandinenses", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J16_G126", "casa": "F.C. Avintes", "fora": "U.D. Beiriz"},
        {"id_jogo": "J16_G127", "casa": "C.F. Oliveira Douro", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J16_G128", "casa": "Desp. Leça Balio", "fora": "Atl. C. Bougadense"},
    ],
    "17": [
        {"id_jogo": "J17_G129", "casa": "Atl. C. Bougadense", "fora": "A.D. Grijó"},
        {"id_jogo": "J17_G130", "casa": "S.C. Castêlo Maia", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J17_G131", "casa": "F.C. Infesta", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J17_G132", "casa": "C.D. Candal", "fora": "F.C. Pedroso"},
        {"id_jogo": "J17_G133", "casa": "A.R.D.C. Gondim Maia", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J17_G134", "casa": "Pedrouços Atl. C.", "fora": "F.C. Avintes"},
        {"id_jogo": "J17_G135", "casa": "U.D. Beiriz", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J17_G136", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "Desp. Leça Balio"},
    ],
    "18": [
        {"id_jogo": "J18_G137", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "A.D. Grijó"},
        {"id_jogo": "J18_G138", "casa": "Valadares Gaia F.C. - SAD", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J18_G139", "casa": "F.C. Pedroso", "fora": "F.C. Infesta"},
        {"id_jogo": "J18_G140", "casa": "S.C. Dragões Sandinenses", "fora": "C.D. Candal"},
        {"id_jogo": "J18_G141", "casa": "F.C. Avintes", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J18_G142", "casa": "C.F. Oliveira Douro", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J18_G143", "casa": "Desp. Leça Balio", "fora": "U.D. Beiriz"},
        {"id_jogo": "J18_G144", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "Atl. C. Bougadense"},
    ],
    "19": [
        {"id_jogo": "J19_G145", "casa": "Atl. C. Bougadense", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J19_G146", "casa": "A.D. Grijó", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J19_G147", "casa": "S.C. Castêlo Maia", "fora": "F.C. Pedroso"},
        {"id_jogo": "J19_G148", "casa": "F.C. Infesta", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J19_G149", "casa": "C.D. Candal", "fora": "F.C. Avintes"},
        {"id_jogo": "J19_G150", "casa": "A.R.D.C. Gondim Maia", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J19_G151", "casa": "Pedrouços Atl. C.", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J19_G152", "casa": "U.D. Beiriz", "fora": 'S.C. Salgueiros "B" - SAD'},
    ],
    "20": [
        {"id_jogo": "J20_G153", "casa": "Valadares Gaia F.C. - SAD", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J20_G154", "casa": "F.C. Pedroso", "fora": "A.D. Grijó"},
        {"id_jogo": "J20_G155", "casa": "S.C. Dragões Sandinenses", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J20_G156", "casa": "F.C. Avintes", "fora": "F.C. Infesta"},
        {"id_jogo": "J20_G157", "casa": "C.F. Oliveira Douro", "fora": "C.D. Candal"},
        {"id_jogo": "J20_G158", "casa": "Desp. Leça Balio", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J20_G159", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J20_G160", "casa": "U.D. Beiriz", "fora": "Atl. C. Bougadense"},
    ],
    "21": [
        {"id_jogo": "J21_G161", "casa": "Atl. C. Bougadense", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J21_G162", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "F.C. Pedroso"},
        {"id_jogo": "J21_G163", "casa": "A.D. Grijó", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J21_G164", "casa": "S.C. Castêlo Maia", "fora": "F.C. Avintes"},
        {"id_jogo": "J21_G165", "casa": "F.C. Infesta", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J21_G166", "casa": "C.D. Candal", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J21_G167", "casa": "A.R.D.C. Gondim Maia", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J21_G168", "casa": "Pedrouços Atl. C.", "fora": "U.D. Beiriz"},
    ],
    "22": [
        {"id_jogo": "J22_G169", "casa": "F.C. Pedroso", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J22_G170", "casa": "S.C. Dragões Sandinenses", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J22_G171", "casa": "F.C. Avintes", "fora": "A.D. Grijó"},
        {"id_jogo": "J22_G172", "casa": "C.F. Oliveira Douro", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J22_G173", "casa": "Desp. Leça Balio", "fora": "F.C. Infesta"},
        {"id_jogo": "J22_G174", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "C.D. Candal"},
        {"id_jogo": "J22_G175", "casa": "U.D. Beiriz", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J22_G176", "casa": "Pedrouços Atl. C.", "fora": "Atl. C. Bougadense"},
    ],
    "23": [
        {"id_jogo": "J23_G177", "casa": "Atl. C. Bougadense", "fora": "F.C. Pedroso"},
        {"id_jogo": "J23_G178", "casa": "Valadares Gaia F.C. - SAD", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J23_G179", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "F.C. Avintes"},
        {"id_jogo": "J23_G180", "casa": "A.D. Grijó", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J23_G181", "casa": "S.C. Castêlo Maia", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J23_G182", "casa": "F.C. Infesta", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J23_G183", "casa": "C.D. Candal", "fora": "U.D. Beiriz"},
        {"id_jogo": "J23_G184", "casa": "A.R.D.C. Gondim Maia", "fora": "Pedrouços Atl. C."},
    ],
    "24": [
        {"id_jogo": "J24_G185", "casa": "S.C. Dragões Sandinenses", "fora": "F.C. Pedroso"},
        {"id_jogo": "J24_G186", "casa": "F.C. Avintes", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J24_G187", "casa": "C.F. Oliveira Douro", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J24_G188", "casa": "Desp. Leça Balio", "fora": "A.D. Grijó"},
        {"id_jogo": "J24_G189", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J24_G190", "casa": "U.D. Beiriz", "fora": "F.C. Infesta"},
        {"id_jogo": "J24_G191", "casa": "Pedrouços Atl. C.", "fora": "C.D. Candal"},
        {"id_jogo": "J24_G192", "casa": "A.R.D.C. Gondim Maia", "fora": "Atl. C. Bougadense"},
    ],
    "25": [
        {"id_jogo": "J25_G193", "casa": "Atl. C. Bougadense", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J25_G194", "casa": "F.C. Pedroso", "fora": "F.C. Avintes"},
        {"id_jogo": "J25_G195", "casa": "Valadares Gaia F.C. - SAD", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J25_G196", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "Desp. Leça Balio"},
        {"id_jogo": "J25_G197", "casa": "A.D. Grijó", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J25_G198", "casa": "S.C. Castêlo Maia", "fora": "U.D. Beiriz"},
        {"id_jogo": "J25_G199", "casa": "F.C. Infesta", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J25_G200", "casa": "C.D. Candal", "fora": "A.R.D.C. Gondim Maia"},
    ],
    "26": [
        {"id_jogo": "J26_G201", "casa": "F.C. Avintes", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J26_G202", "casa": "C.F. Oliveira Douro", "fora": "F.C. Pedroso"},
        {"id_jogo": "J26_G203", "casa": "Desp. Leça Balio", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J26_G204", "casa": 'S.C. Salgueiros "B" - SAD', "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J26_G205", "casa": "U.D. Beiriz", "fora": "A.D. Grijó"},
        {"id_jogo": "J26_G206", "casa": "Pedrouços Atl. C.", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J26_G207", "casa": "A.R.D.C. Gondim Maia", "fora": "F.C. Infesta"},
        {"id_jogo": "J26_G208", "casa": "C.D. Candal", "fora": "Atl. C. Bougadense"},
    ],
    "27": [
        {"id_jogo": "J27_G209", "casa": "Atl. C. Bougadense", "fora": "F.C. Avintes"},
        {"id_jogo": "J27_G210", "casa": "S.C. Dragões Sandinenses", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J27_G211", "casa": "F.C. Pedroso", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J27_G212", "casa": "Valadares Gaia F.C. - SAD", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J27_G213", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "U.D. Beiriz"},
        {"id_jogo": "J27_G214", "casa": "A.D. Grijó", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J27_G215", "casa": "S.C. Castêlo Maia", "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J27_G216", "casa": "F.C. Infesta", "fora": "C.D. Candal"},
    ],
    "28": [
        {"id_jogo": "J28_G217", "casa": "C.F. Oliveira Douro", "fora": "F.C. Avintes"},
        {"id_jogo": "J28_G218", "casa": "Desp. Leça Balio", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J28_G219", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "F.C. Pedroso"},
        {"id_jogo": "J28_G220", "casa": "U.D. Beiriz", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J28_G221", "casa": "Pedrouços Atl. C.", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J28_G222", "casa": "A.R.D.C. Gondim Maia", "fora": "A.D. Grijó"},
        {"id_jogo": "J28_G223", "casa": "C.D. Candal", "fora": "S.C. Castêlo Maia"},
        {"id_jogo": "J28_G224", "casa": "F.C. Infesta", "fora": "Atl. C. Bougadense"},
    ],
    "29": [
        {"id_jogo": "J29_G225", "casa": "C.F. Oliveira Douro", "fora": "Atl. C. Bougadense"},
        {"id_jogo": "J29_G226", "casa": "F.C. Avintes", "fora": "Desp. Leça Balio"},
        {"id_jogo": "J29_G227", "casa": "S.C. Dragões Sandinenses", "fora": 'S.C. Salgueiros "B" - SAD'},
        {"id_jogo": "J29_G228", "casa": "F.C. Pedroso", "fora": "U.D. Beiriz"},
        {"id_jogo": "J29_G229", "casa": "Valadares Gaia F.C. - SAD", "fora": "Pedrouços Atl. C."},
        {"id_jogo": "J29_G230", "casa": 'Varzim S.C. "B" - SDUQ', "fora": "A.R.D.C. Gondim Maia"},
        {"id_jogo": "J29_G231", "casa": "A.D. Grijó", "fora": "C.D. Candal"},
        {"id_jogo": "J29_G232", "casa": "S.C. Castêlo Maia", "fora": "F.C. Infesta"},
    ],
    "30": [
        {"id_jogo": "J30_G233", "casa": "Desp. Leça Balio", "fora": "C.F. Oliveira Douro"},
        {"id_jogo": "J30_G234", "casa": 'S.C. Salgueiros "B" - SAD', "fora": "F.C. Avintes"},
        {"id_jogo": "J30_G235", "casa": "U.D. Beiriz", "fora": "S.C. Dragões Sandinenses"},
        {"id_jogo": "J30_G236", "casa": "Pedrouços Atl. C.", "fora": "F.C. Pedroso"},
        {"id_jogo": "J30_G237", "casa": "A.R.D.C. Gondim Maia", "fora": "Valadares Gaia F.C. - SAD"},
        {"id_jogo": "J30_G238", "casa": "C.D. Candal", "fora": 'Varzim S.C. "B" - SDUQ'},
        {"id_jogo": "J30_G239", "casa": "F.C. Infesta", "fora": "A.D. Grijó"},
        {"id_jogo": "J30_G240", "casa": "Atl. C. Bougadense", "fora": "S.C. Castêlo Maia"},
    ],
}


# LEITURA E ESCRITA DIRETA NO GITHUB
def carregar_dados_github():
  try:
    res = requests.get(URL_API, headers=HEADERS)
    if res.status_code == 200:
      conteudo = res.json()
      dados_json = json.loads(
          base64.b64decode(conteudo["content"]).decode("utf-8")
      )
      st.session_state.sha = conteudo["sha"]
      return dados_json.get("resultados", {}), dados_json.get("palpites", {})
  except Exception as e:
    st.error(f"Erro ao sincronizar com o GitHub: {e}")
  return {}, {}


def guardar_dados_github():
  dados_para_salvar = {
      "resultados": st.session_state.resultados_dados,
      "palpites": st.session_state.palpites_dados,
  }
  conteudo_b64 = base64.b64encode(
      json.dumps(dados_para_salvar, indent=2).encode("utf-8")
  ).decode("utf-8")

  payload = {
      "message": "Atualização de palpites/resultados",
      "content": conteudo_b64,
  }
  if "sha" in st.session_state:
    payload["sha"] = st.session_state.sha

  try:
    res = requests.put(URL_API, headers=HEADERS, json=payload)
    if res.status_code in [200, 201]:
      st.session_state.sha = res.json()["content"]["sha"]
      return True
  except Exception as e:
    st.error(f"Erro ao gravar no GitHub: {e}")
  return False


# Sincroniza dados na leitura
resultados_dados, palpites_dados = carregar_dados_github()
st.session_state.resultados_dados = resultados_dados
st.session_state.palpites_dados = palpites_dados


# REGRA DE PONTUAÇÃO: RESULTADO EXATO = 3 PONTOS | TENDÊNCIA CERTA = 1 PONTO
def calcular_pontos(p_c, p_f, r_c, r_f):
  if r_c is None or r_f is None or p_c is None or p_f is None:
    return 0
  if p_c == r_c and p_f == r_f:
    return 3  # <--- AGORA VALE 3 PONTOS
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
              if pts == 3:
                ex_t[jog] += 1
              elif pts == 1:
                tend_t[jog] += 1

      df_g = (
          pd.DataFrame({
              "Participante": jogadores,
              "Pontos Totais": [pts_t[j] for j in jogadores],
              "Resultados Exatos (3 pts)": [ex_t[j] for j in jogadores],
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
      for j_num in CALENDARIO_LOCAL.keys():
        if obter_mes_por_jornada(j_num) == mes_sel:
          for jogo in CALENDARIO_LOCAL[j_num]:
            id_j = jogo["id_jogo"]
            res = resultados_dados.get(id_j, {})
            rc, rf = res.get("res_casa"), res.get("res_fora")
            for jog in jogadores:
              palp = palpites_dados[jog].get(id_j)
              if palp and rc is not None and rf is not None:
                pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
                pts_m[jog] += pts
                if pts == 3:
                  ex_m[jog] += 1
                elif pts == 1:
                  tend_m[jog] += 1
      df_m = (
          pd.DataFrame({
              "Participante": jogadores,
              f"Pontos ({mes_sel})": [pts_m[j] for j in jogadores],
              "Resultados Exatos (3 pts)": [ex_m[j] for j in jogadores],
              "Tendências Certas (1 pt)": [tend_m[j] for j in jogadores],
          })
          .sort_values(by=f"Pontos ({mes_sel})", ascending=False)
          .reset_index(drop=True)
      )
      df_m.index += 1
      st.table(df_m)

    with sub_aba3:
      st.subheader("Pontuação Individual por Jornada")
      lista_j = [int(k) for k in CALENDARIO_LOCAL.keys()]
      j_sel_tab = st.selectbox("Escolher Jornada:", sorted(lista_j))
      pts_j, ex_j, tend_j = (
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
          {j: 0 for j in jogadores},
      )
      for jogo in CALENDARIO_LOCAL.get(str(j_sel_tab), []):
        id_j = jogo["id_jogo"]
        res = resultados_dados.get(id_j, {})
        rc, rf = res.get("res_casa"), res.get("res_fora")
        for jog in jogadores:
          palp = palpites_dados[jog].get(id_j)
          if palp and rc is not None and rf is not None:
            pts = calcular_pontos(palp["c"], palp["f"], rc, rf)
            pts_j[jog] += pts
            if pts == 3:
              ex_j[jog] += 1
            elif pts == 1:
              tend_j[jog] += 1
      df_j = (
          pd.DataFrame({
              "Participante": jogadores,
              f"Pontos J{j_sel_tab}": [pts_j[j] for j in jogadores],
              "Resultados Exatos (3 pts)": [ex_j[j] for j in jogadores],
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

  opcao_jog = st.radio(
      "Identificação do Apostador:",
      ["Apostador Existente", "Novo Apostador"],
      horizontal=True,
  )

  nome = ""

  if opcao_jog == "Apostador Existente":
    if lista_existentes:
      opcoes_com_placeholder = ["-- Seleciona o teu nome --"] + sorted(
          lista_existentes
      )
      escolha = st.selectbox(
          "Seleciona o teu nome da lista:", opcoes_com_placeholder, index=0
      )
      if escolha != "-- Seleciona o teu nome --":
        nome = escolha
    else:
      st.warning(
          "Ainda não existem apostadores registados. Seleciona 'Novo"
          " Apostador' para criar o primeiro."
      )

  elif opcao_jog == "Novo Apostador":
    nome = st.text_input("Escreve o teu Nome / Alcunha:").strip()

  # O FORMULÁRIO SÓ É EXIBIDO QUANDO HOUVER UM NOME DE APOSTADOR VÁLIDO
  if nome:
    jogos_j = CALENDARIO_LOCAL.get(str(j_ativa), [])
    palpites_do_jogador = palpites_dados.get(nome, {})

    with st.form(key=f"form_palpites_{nome}"):
      st.subheader(f"Palpites de {nome} para a Jornada {j_ativa}")
      novos_p = {}
      for jogo in jogos_j:
        id_j = jogo["id_jogo"]

        val_c = 0
        val_f = 0
        if id_j in palpites_do_jogador:
          val_c = int(palpites_do_jogador[id_j].get("c", 0))
          val_f = int(palpites_do_jogador[id_j].get("f", 0))

        col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
        with col1:
          st.write(f"**{jogo['casa']}**")
        with col2:
          pc = st.number_input(
              "",
              min_value=0,
              max_value=15,
              value=val_c,
              key=f"input_c_{nome}_{id_j}",
          )
        with col3:
          pf = st.number_input(
              "",
              min_value=0,
              max_value=15,
              value=val_f,
              key=f"input_f_{nome}_{id_j}",
          )
        with col4:
          st.write(f"**{jogo['fora']}**")
        novos_p[id_j] = {"c": pc, "f": pf}

      if st.form_submit_button("Guardar Prognósticos"):
        if nome not in st.session_state.palpites_dados:
          st.session_state.palpites_dados[nome] = {}

        for id_j, val in novos_p.items():
          st.session_state.palpites_dados[nome][id_j] = {
              "c": val["c"],
              "f": val["f"],
          }

        if guardar_dados_github():
          st.success(f"Prognósticos de {nome} guardados com sucesso no GitHub!")
          st.rerun()
        else:
          st.error("Erro ao guardar os dados no GitHub. Verifica o Token.")

# ---------------------------------------------------------
# ABA 3: PAINEL ADMIN
# ---------------------------------------------------------
elif aba == "⚙️ Painel Admin":
  st.header("⚙️ Painel de Administração")
  sub1, sub2, sub3 = st.tabs(
      ["⚽ Inserir Resultados", "🗑️ Gerir / Apagar Jogadores", "📦 Backup"]
  )

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
        for nr in novos_res:
          res_c = nr["c"] if marcar_fechado else None
          res_f = nr["f"] if marcar_fechado else None
          st.session_state.resultados_dados[nr["id_jogo"]] = {
              "res_casa": res_c,
              "res_fora": res_f,
          }

        if guardar_dados_github():
          st.success(f"Resultados da Jornada {j_sel} guardados com sucesso!")
          st.rerun()
        else:
          st.error("Erro ao guardar os resultados no GitHub.")

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
        if jog_del in st.session_state.palpites_dados:
          del st.session_state.palpites_dados[jog_del]
        if guardar_dados_github():
          st.success(f"O participante '{jog_del}' foi eliminado!")
          st.rerun()
        else:
          st.error("Erro ao atualizar o ficheiro no GitHub.")

  with sub3:
    st.subheader("📦 Cópia de Segurança dos Dados")
    dados_backup = json.dumps(
        {
            "resultados": st.session_state.resultados_dados,
            "palpites": st.session_state.palpites_dados,
        },
        indent=2,
    )

    st.download_button(
        label="⬇️ Descarregar Ficheiro de Backup (.json)",
        data=dados_backup,
        file_name="dados_liga_backup.json",
        mime="application/json",
    )
