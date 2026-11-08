import io

import pandas as pd
import requests
import streamlit as st
import urllib3

# verify=False 會產生警告，這裡關閉警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="MOPS 開放資料檢視", page_icon="📊", layout="wide")

DEFAULT_URL = "https://mopsfin.twse.com.tw/opendata/t187ap46_O_1.csv"


@st.cache_data(ttl=3600, show_spinner="資料下載中...")
def load_data(url: str, verify_ssl: bool) -> pd.DataFrame:
    """下載 CSV 並轉成 DataFrame（快取 1 小時）"""
    response = requests.get(url, verify=verify_ssl, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(io.BytesIO(response.content), encoding="utf-8-sig")  # 繁體中文
    return df.dropna()


st.title("📊 MOPS 開放資料檢視")

with st.sidebar:
    st.header("設定")
    url = st.text_input("CSV 連結", value=DEFAULT_URL)
    verify_ssl = st.checkbox("驗證 SSL 憑證", value=False,
                             help="原程式使用 verify=False，若來源憑證正常可勾選")
    if st.button("🔄 重新載入資料"):
        st.cache_data.clear()
        st.rerun()

try:
    df = load_data(url, verify_ssl)
except Exception as e:
    st.error(f"資料載入失敗：{e}")
    st.stop()

st.success(f"載入完成：共 {len(df):,} 筆、{len(df.columns)} 個欄位")

# 關鍵字搜尋
keyword = st.text_input("🔍 關鍵字搜尋（搜尋所有欄位）")
if keyword:
    mask = df.astype(str).apply(
        lambda col: col.str.contains(keyword, case=False, na=False)
    ).any(axis=1)
    df_show = df[mask]
    st.caption(f"符合 {len(df_show):,} 筆")
else:
    df_show = df

st.dataframe(df_show, use_container_width=True, height=600)

# 下載按鈕
csv_bytes = df_show.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ 下載 CSV", data=csv_bytes,
                   file_name="data01.csv", mime="text/csv")
