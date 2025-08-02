import sqlite3
from datetime import datetime
import streamlit as st
import os
import pandas as pd
import yfinance as yf
#####################
# 실행 시 app.py 실행
#####################


# SQLite 연결 및 테이블 생성 (파일이 없을 때만)
db_path = "trading_diary.db"
initialize_db = not os.path.exists(db_path)
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

if initialize_db:
    c.execute('''
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            direction INTEGER,     -- 1: 상승, 0: 하락
            entry_price REAL,
            entry_time TEXT,
            reason TEXT,
            is_closed INTEGER,
            exit_price REAL,
            exit_time TEXT,
            return_rate REAL
        )
    ''')
    conn.commit()

st.title("📘 주식 매매 일기")

@st.dialog("새 매매 기록 입력")
def entry_form():
    with st.form("entry_form"):
        col1, col2 = st.columns([2, 1], vertical_alignment="bottom")
        with col1:
            ticker = st.text_input("티커")
        with col2:
            option_map = {
                1: ":material/trending_up:",
                0: ":material/trending_down:"
            }
            direction = st.segmented_control(
                "상승/하락 예측",
                options=option_map.keys(),
                format_func=lambda option: option_map[option],
                selection_mode="single",
            )

        entry_price = st.number_input("예측 시점의 가격", step=0.01)
        reason = st.text_area("매매 근거 메모")
        submit = st.form_submit_button("기록 추가")

        if submit:
            if direction is None:
                st.error("방향을 선택해주세요!")
            elif not ticker or entry_price <= 0:
                st.error("입력값을 모두 확인해주세요.")
            else:
                now = datetime.now().isoformat()
                c.execute('''
                    INSERT INTO trades (
                        ticker, direction, entry_price, entry_time, reason,
                        is_closed, exit_price, exit_time, return_rate
                    ) VALUES (?, ?, ?, ?, ?, 0, NULL, NULL, NULL)
                ''', (ticker, direction, entry_price, now, reason))
                conn.commit()
                st.success("기록이 성공적으로 저장되었습니다!")
                st.rerun()

if st.button("➕ 새 매매 기록 추가"):
    entry_form()

# 실시간 가격 가져오기 함수
def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d', interval='1m')
        return round(data['Close'].iloc[-1], 2)
    except:
        return None

# 미청산 거래 내역 표시
st.header("📄 미청산 거래 내역")
df = pd.read_sql_query("SELECT id, ticker, direction, entry_price, entry_time, reason FROM trades WHERE is_closed = 0 ORDER BY entry_time DESC", conn)


cols = st.columns(2)
for i, (_, row) in enumerate(df.iterrows()):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {row['ticker']} {'🟢 상승' if row['direction'] == 1 else '🔴 하락'}")
            st.caption(f"진입 시각: {row['entry_time']}")
            st.markdown(f"**진입가:** {row['entry_price']:.2f}$")
            st.markdown(f"**메모:** {row['reason']}")

            current_price = get_price(row['ticker'])
            if current_price:
                delta = (current_price - row['entry_price']) / row['entry_price'] * 100
                st.metric("현재가", f"{current_price:.2f}", f"{delta:.2f}%")
            else:
                st.warning("현재가를 가져올 수 없습니다.")

            if st.button("청산하기", key=f"close_{row['id']}"):
                exit_time = datetime.now().isoformat()
                exit_price = current_price
                return_rate = (exit_price - row['entry_price']) / row['entry_price'] * 100
                if row["direction"] == 0:
                    return_rate *= -1
                c.execute('''
                    UPDATE trades
                    SET is_closed = 1,
                        exit_price = ?,
                        exit_time = ?,
                        return_rate = ?
                    WHERE id = ?
                ''', (exit_price, exit_time, return_rate, row['id']))
                conn.commit()
                st.success("✅ 청산 완료!")
                st.rerun()

# 전체 미청산 거래 요약 테이블
st.divider()
st.subheader("📊 전체 미청산 거래 요약")
if df.empty:
    st.info("진행중인 거래가 없습니다.")
else:
    # 보기용 한글 컬럼으로 변환
    df["예측"] = df["direction"].map({1: "📈 상승", 0: "📉 하락"})
    display_df = df.rename(columns={
        "id": "ID",
        "ticker": "티커",
        "entry_price": "진입가",
        "entry_time": "진입 시간",
        "reason": "매매 근거"
    })
st.dataframe(display_df[["ID", "티커", "예측", "진입가", "진입 시간", "매매 근거"]], use_container_width=True)
