import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import numpy as np

# =========================
# 🔐 SENHA (ALTERE AQUI)
# =========================
PASSWORD = "LUCRO6"

# =========================
# LOGIN
# =========================
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
# APP PRINCIPAL
# =========================
st.set_page_config(layout="wide")
st.title("Backtest - Rompimento de Fundo + EMA69")

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

STOP = 0.95
GAIN = 1.08

def backtest(ticker):

    try:
        df = yf.download(ticker, period="3y", interval="1d", progress=False)

        if df.empty or len(df) < 120:
            return None

        df["EMA69"] = ta.trend.ema_indicator(df["Close"], window=69)
        df["Fundo"] = df["Low"].rolling(5).min().shift(1)

        trades = []

        for i in range(70, len(df)-2):

            D = df.iloc[i]
            D1 = df.iloc[i+1]

            if D["Close"] <= D["EMA69"]:
                continue

            if not (D["Low"] < D["Fundo"] and D["Close"] < D["Fundo"]):
                continue

            entrada = D["High"]

            if D1["High"] <= entrada:
                continue

            stop = entrada * STOP
            gain = entrada * GAIN

            result = None

            for j in range(i+1, len(df)):

                c = df.iloc[j]

                if c["Low"] <= stop:
                    result = -1
                    break

                if c["High"] >= gain:
                    result = 1
                    break

            if result is not None:
                trades.append(result)

        if len(trades) == 0:
            return None

        trades = np.array(trades)

        return {
            "Ativo": ticker.replace(".SA",""),
            "Trades": len(trades),
            "WinRate %": round((trades == 1).mean()*100,2),
            "Expectativa": round(trades.mean(),3)
        }

    except:
        return None


if st.button("Rodar Backtest"):

    resultados = []

    for a in ativos:
        r = backtest(a)
        if r:
            resultados.append(r)

    if resultados:

        df = pd.DataFrame(resultados)

        st.subheader("📊 Ranking por Probabilidade")
        st.dataframe(df.sort_values("WinRate %", ascending=False))

        st.subheader("📈 Ranking por Expectativa")
        st.dataframe(df.sort_values("Expectativa", ascending=False))

    else:
        st.warning("Sem resultados")
