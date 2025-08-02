import streamlit as st

pages = {
    "Pages": [
        st.Page("main.py", title="진행중인 거래"),
        st.Page("closed_trades.py", title="완료된 거래"),
    ]
}

pg = st.navigation(pages, position="top")
pg.run()