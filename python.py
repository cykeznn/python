# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 設定
st.set_page_config(page_title="App 訂閱支出轉資產計算器", layout="centered")

# 顏色
st.markdown(
    """
    <style>
    # all
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: "Microsoft JhengHei", "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    #側邊欄背景
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        font-family: "Microsoft JhengHei", sans-serif !important;
    }
    
    #側邊欄文字、標籤
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    
    #數字藍色、標籤深灰色
    [data-testid="stMetricValue"] {
        color: #46A3FF !important;
    }
    [data-testid="stMetricLabel"] {
        color: #666666 !important; 
    }
    
    #文字、項目清單
    .stText, p, span {
        color: #000000 !important;
    }

    #框框
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 1px solid #CCCCCC !important; 
        border-radius: 4px !important;      
        background-color: #FFFFFF !important;
    }

    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #46A3FF !important;
        box-shadow: 0 0 0 1px #46A3FF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 標題
st.title("訂閱支出轉資產計算系統﹐20260529")
st.write("前兩年純本金定期定額、後四年全額轉投台股股權的複利增殖模型。")

st.divider()

# 初始化 Session State (保持資料)
if "app_list" not in st.session_state:
    st.session_state.app_list = []

# 固定參數
BANK_RATE = 0.0165   # 中信定存利率 1.65%
STOCK_FEE_RATE = 0.001425  # 台股券商手續費 0.1425%
STOCK_TAX_RATE = 0.003     # 政府證交稅 0.3%

#側邊欄
st.sidebar.header("新增要攔截的 App")
app_name = st.sidebar.text_input("App 名稱", placeholder="例如：retro, Netflix")
period_choice = st.sidebar.radio("繳費週期", ["月繳", "年繳"])
app_fee = st.sidebar.number_input("扣款金額 (元)", min_value=0.0, step=100.0, value=1000.0)

if st.sidebar.button("➕ 加入攔截清單"):
    if app_name.strip() == "":
        st.sidebar.error("請輸入 App 名稱！")
    else:
        st.session_state.app_list.append({
            "name": app_name,
            "fee": app_fee,
            "period": period_choice
        })
        st.sidebar.success(f"已成功攔截 {app_name}！")

if st.sidebar.button("🗑️ 清空所有項目"):
    st.session_state.app_list = []
    st.sidebar.warning("清單已清空")

#主畫面
st.subheader("📋 目前已攔截的 App 清單")
if not st.session_state.app_list:
    st.info("目前清單空空如也，請使用左側欄位新增 App 項目。")
else:
    for i, app in enumerate(st.session_state.app_list):
        st.text(f"項目 {i+1}: {app['name']} ({app['period']}) — ${app['fee']:,.0f} 元")
    
    st.divider()
    
#前兩年保留單利分段算法
    monthly_inputs = []
    total_principal = 0

    for m in range(1, 25):
        invest_this_month = 0
        for app in [a for a in st.session_state.app_list if a['period'] == "年繳"]:
            if m == 1 or m == 13:
                invest_this_month += app['fee']
        for app in [a for a in st.session_state.app_list if a['period'] == "月繳"]:
            invest_this_month += app['fee']
        
        monthly_inputs.append(invest_this_month)
        total_principal += invest_this_month

    total_interest_stage1 = 0
    for i, amount in enumerate(monthly_inputs):
        if amount > 0:
            months = 24 - i
            interest = amount * BANK_RATE * (months / 12)
            total_interest_stage1 += interest

# 第二年底總累積規模
    stage1_final_balance = sum(monthly_inputs) + total_interest_stage1

#前兩年結果
    st.subheader("第一階段：兩年期財務打底結果")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="2年總投入本金", value=f"${total_principal:,.0f} 元")
    col2.metric(label="2年定存總利息", value=f"${total_interest_stage1:,.0f} 元")
    col3.metric(label="第二年底總資產", value=f"${stage1_final_balance:,.0f} 元")
    st.write(f"*(註：本階段採中信銀行固定利率 {BANK_RATE*100:.2f}% 單利分段計息，無扣手續費)*")

    st.divider()

#後四年台股ETF投資
    st.subheader("第二階段：後四年轉投台股 ETF 資產配置")

    st.write(
        "兩年期滿後，系統將自動把第二年底資產 "
        "全額轉入台股 ETF市場，進行長期複利投資。"
    )

#選擇ETF
    etf_choice = st.selectbox(
        "選擇台股 ETF 類型",
        [
            "成長型",
            "低費用市值型",
            "高股息型"
        ]
    )

# 根據 ETF 自動給預設年化報酬
    if "成長型" in etf_choice:
        default_rate = 8.0
    elif "低費用市值型" in etf_choice:
        default_rate = 8.5
    else:
        default_rate = 6.0

#調整報酬率
    stock_rate_input = st.slider(
        "調整預期年化報酬率 (%)",
        min_value=-10.0,
        max_value=20.0,
        value=float(default_rate),
        step=0.5
    )

    stock_rate = stock_rate_input / 100

    st.divider()

# ETF 四年
    stock_balance = stage1_final_balance
    yearly_growth_data = []

    for year in range(3, 7):
        start_of_year = stock_balance
        # ETF 年化複利（含股息再投入）
        stock_balance = stock_balance * (1 + stock_rate)
        annual_profit = stock_balance - start_of_year

        yearly_growth_data.append({
            "年份": f"第 {year} 年",
            "年初資產": round(start_of_year),
            "年末資產": round(stock_balance),
            "年度獲利": round(annual_profit)
        })

# ETF 四年總獲利
    total_stock_interest = stock_balance - stage1_final_balance

# 第六年底賣出：扣除交易成本

    final_cash_received = stock_balance * (1 - STOCK_FEE_RATE - STOCK_TAX_RATE)
    net_profit = final_cash_received - total_principal
    roi = (net_profit / total_principal) * 100

    st.subheader("第六年底資產總結報告")

    col4, col5, col6 = st.columns(3)
    col4.metric(label="ETF 四年總獲利", value=f"${total_stock_interest:,.0f} 元")
    col5.metric(label="六年後實際領回", value=f"${final_cash_received:,.0f} 元")
    col6.metric(label="六年總投資報酬率", value=f"{roi:.2f}%")

    st.write("* 已自動扣除台股 ETF 賣出成本：0.1425% 手續費與 0.3% 證交稅 *")
    st.divider()

# ETF 資產成長軌跡
    st.subheader("ETF 四年資產成長軌跡")
    for data in yearly_growth_data:
        st.write(
            f"{data['年份']}｜"
            f"${data['年初資產']:,.0f} → "
            f"${data['年末資產']:,.0f} "
            f"(年度成長 +${data['年度獲利']:,.0f})"
        )

    st.divider()

# Pandas DataFrame
    st.subheader("資產成長折線圖")
    
    raw_chart_data = {
        "年份": ["第 2 年底"] + [d["年份"] for d in yearly_growth_data],
        "資產總額 (元)": [round(stage1_final_balance)] + [d["年末資產"] for d in yearly_growth_data]
    }
    
# Dataframe
    df = pd.DataFrame(raw_chart_data)
    
    st.line_chart(data=df, x="年份", y="資產總額 (元)")

    st.divider()

# 結論
    st.success(
        f"透過2年定存 + 4年ETF複利，"
        f"成功將原本會流失的訂閱支出，"
        f"累積成第六年底 ${final_cash_received:,.0f} 元的資產啦！"
    )
