import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# =========================
# 🔐 LOGIN
# =========================
PASSWORD = "LUCRO6"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:

    st.title("🔐 Acesso ao Sistema")

    senha = st.text_input("Digite a senha", type="password")

    if st.button("Entrar"):
        if senha == PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")

    st.stop()

# =========================
# APP
# =========================
st.set_page_config(layout="wide")
st.title("Radar - Ataque ao Último Fundo (Swing Livre)")

ativos = [
"RRRP3","ALOS3","ALPA4","ABEV3","ARZZ3","ASAI3","AZUL4",
"B3SA3","BBAS3","BBDC3","BBDC4","BBSE3","BEEF3","BPAC11",
"BRAP4","BRFS3","BRKM5","CCRO3","CMIG4","CMIN3","COGN3",
"CPFE3","CPLE6","CRFB3","CSAN3","CSNA3","CYRE3","DXCO3",
"EGIE3","ELET3","ELET6","EMBR3","ENEV3","ENGI11","EQTL3",
"EZTC3","FLRY3","GGBR4","GOAU4","GOLL4","HAPV3","HYPE3",
"ITSA4","ITUB4","JBSS3","KLBN11","LREN3","LWSA3","MGLU3",
"MRFG3","MRVE3","MULT3","NTCO3","PETR3","PETR4","PRIO3",
"RADL3","RAIL3","RAIZ4","RENT3","RECV3","SANB11","SBSP3",
"SLCE3","SMTO3","SUZB3","TAEE11","TIMS3","TTEN3","TOTS3",
"TRPL4","UGPA3","USIM5","VALE3","VIVT3","VIVA3","WEGE3",
"YDUQ3","AURE3","BHIA3","CASH3","CVCB3","DIRR3","ENAT3",
"GMAT3","IFCM3","INTB3","JHSF3","KEPL3","MOVI3","ORVR3",
"PETZ3","PLAS3","POMO4","POSI3","RANI3","RAPT4","STBP3",
"TEND3","TUPY3","BRSR6","CXSE3",

"AAPL34","AMZO34","GOGL34","MSFT34","TSLA34","META34",
"NFLX34","NVDC34","MELI34","BABA34","DISB34","PYPL34",
"JNJB34","PGCO34","KOCH34","VISA34","WMTB34","NIKE34",
"ADBE34","AVGO34","CSCO34","COST34","CVSH34","GECO34",
"GSGI34","HDCO34","INTC34","JPMC34","MAEL34","MCDP34",
"MDLZ34","MRCK34","ORCL34","PEP334","PFIZ34","PMIC34",
"QCOM34","SBUX34","TGTB34","TMOS34","TXN34","UNHH34",
"UPSB34","VZUA34","ABTT34","AMGN34","AXPB34","BAOO34",
"C2OL34","HONB34","BICE34","BERK34","GOGL35",

"BOVA11","IVVB11","SMAL11","HASH11","GOLD11","DIVO11",
"NDIV11","SPUB11",

"GARE11","HGLG11","XPLG11","VILG11","BRCO11","BTLG11",
"XPML11","VISC11","HSML11","MALL11","KNRI11","JSRE11",
"PVBI11","HGRE11","MXRF11","KNCR11","KNIP11","CPTS11",
"IRDM11","TGAR11","TRXF11","HGRU11","ALZR11","XPCA11",
"VGIA11","RBRR11","KNSC11","CACR11","HABT11","DEVA11",
"HGCR11","MCCI11","RECR11","VRTA11","BCFF11","HFOF11",
"XPSF11","RBRP11","RBRF11","URIT11","RZTR11","RURA11",
"VGIR11","CVBI11","UTLL11","GGRC11","HERT11","AUVP11","IEEX11"
]

# =========================
# DETECÇÃO DE SWING LOW + ATAQUE
# =========================
def backtest(ticker):

    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)

        if df.empty or len(df) < 50:
            return None

        sinais = 0
        score_total = 0

        for i in range(5, len(df)-5):

            # =========================
            # PIVÔ DE FUNDO (SWING LOW)
            # =========================
            window = df.iloc[i-5:i+6]

            curr = df.iloc[i]

            is_swing_low = curr["Low"] == window["Low"].min()

            if not is_swing_low:
                continue

            ultimo_fundo = curr["Low"]

            # =========================
            # ATAQUE AO FUNDO (ROMPIMENTO OU TESTE)
            # =========================
            proximidade = (curr["Close"] - ultimo_fundo) / ultimo_fundo

            ataque = curr["Low"] <= ultimo_fundo * 1.005

            # =========================
            # PRESSÃO (FORÇA VENDEDORA)
            # =========================
            range_candle = curr["High"] - curr["Low"]

            if range_candle == 0:
                continue

            fechamento_fraco = (curr["Close"] - curr["Low"]) / range_candle

            pressao = fechamento_fraco < 0.35

            if ataque and pressao:

                sinais += 1

                score = 0

                # quanto mais fundo “atacado”, maior o score
                score += (1 - max(0, proximidade)) * 5

                # pressão de venda
                score += (1 - fechamento_fraco) * 4

                score_total += score

        if sinais == 0:
            return None

        edge = score_total / sinais

        return {
            "Ativo": ticker.replace(".SA",""),
            "Sinais": sinais,
            "Edge Score": round(edge, 3)
        }

    except:
        return None


# =========================
# EXECUÇÃO
# =========================
if st.button("Rodar Radar"):

    resultados = []

    for a in ativos:
        r = backtest(a)
        if r:
            resultados.append(r)

    if resultados:

        df = pd.DataFrame(resultados)

        st.subheader("📊 Ranking de Edge (Ataque ao Último Fundo)")
        st.dataframe(df.sort_values("Edge Score", ascending=False))

        st.subheader("📈 Frequência de Ataques")
        st.dataframe(df.sort_values("Sinais", ascending=False))

    else:
        st.warning("Nenhum ativo atacando fundo no momento")
