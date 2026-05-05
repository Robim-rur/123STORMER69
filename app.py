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
# Bancos
"BBAS3.SA","ITUB4.SA","ITSA4.SA","BBDC4.SA","BBDC3.SA","SANB11.SA",
"BPAC11.SA","BRSR6.SA","BMGB4.SA","PSSA3.SA","IRBR3.SA",

# Energia / Petróleo
"PETR4.SA","PETR3.SA","PRIO3.SA","RECV3.SA","RRRP3.SA",
"UGPA3.SA","VBBR3.SA",

# Mineração
"VALE3.SA","CSNA3.SA","USIM5.SA","GGBR4.SA","GOAU4.SA","BRAP4.SA",

# Papel e Celulose
"SUZB3.SA","KLBN11.SA","KLBN4.SA","KLBN3.SA",

# Energia elétrica
"CMIG4.SA","TAEE11.SA","CPFE3.SA","EQTL3.SA","ELET3.SA","ELET6.SA",
"ALUP11.SA","TRPL4.SA","NEOE3.SA","ENGI11.SA",

# Saneamento
"SBSP3.SA","SAPR11.SA","CSMG3.SA",

# Consumo
"MGLU3.SA","LREN3.SA","ASAI3.SA","PCAR3.SA","CRFB3.SA",
"ARZZ3.SA","SOMA3.SA",

# Saúde
"HAPV3.SA","QUAL3.SA","FLRY3.SA","RDOR3.SA",

# Construção
"MRVE3.SA","EZTC3.SA","CYRE3.SA","DIRR3.SA","TEND3.SA",

# Tecnologia
"TOTS3.SA","POSI3.SA","LWSA3.SA",

# Transporte
"RAIL3.SA","CCRO3.SA","ECOR3.SA","AZUL4.SA","GOLL4.SA",

# Industriais
"WEGE3.SA","ROMI3.SA","KEPL3.SA","RAPT4.SA",

# Alimentos
"JBSS3.SA","BRFS3.SA","MRFG3.SA","BEEF3.SA",

# ETFs
"BOVA11.SA","SMAL11.SA","IVVB11.SA","DIVO11.SA",

# FIIs
"KNRI11.SA","HGLG11.SA","MXRF11.SA","XPML11.SA",
"VISC11.SA","XPLG11.SA","HGRE11.SA","BRCO11.SA",

# BDRs
"AAPL34.SA","MSFT34.SA","GOGL34.SA","AMZO34.SA",
"META34.SA","TSLA34.SA","NVDC34.SA",
"JPMC34.SA","BOAC34.SA","WFCB34.SA",
"WALM34.SA","COST34.SA","PEPB34.SA","KOCA34.SA",
"JNJB34.SA","PFEF34.SA","MRCK34.SA",
"DISB34.SA","NKEE34.SA","SBUX34.SA"

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
