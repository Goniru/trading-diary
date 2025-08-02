import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="청산된 거래 내역", page_icon="✅")
st.title("✅ 청산된 거래 내역")

db_path = "trading_diary.db"

# 1. 청산된 거래 불러오기
with sqlite3.connect(db_path, check_same_thread=False) as conn:
    df = pd.read_sql_query("SELECT * FROM trades WHERE is_closed = 1 ORDER BY exit_time DESC", conn)

if df.empty:
    st.info("아직 청산된 거래가 없습니다.")
else:
    # 보기용 한글 컬럼 추가
    df["예측"] = df["direction"].map({1: "📈 상승", 0: "📉 하락"})

    # 2. 편집 화면용 데이터프레임 생성
    display_df = df.rename(columns={
        "entry_price": "진입가",
        "exit_price": "청산가",
        "exit_time": "청산 시각",
        "return_rate": "수익률",
        "reason": "매매 근거"
    })

    # direction 컬럼 유지하면서 표시만 안 하도록
    edit_columns = ["id", "ticker", "direction", "예측", "진입가", "청산가", "청산 시각", "수익률", "매매 근거"]

    edited = st.data_editor(
        display_df[edit_columns],
        use_container_width=True,
        disabled=["id", "ticker", "예측", "진입가", "수익률", "direction"],
        hide_index=True,
        key="bulk_editor",
        num_rows="dynamic",
        column_order=("id", "ticker", "예측", "진입가", "청산가", "청산 시각", "수익률", "매매 근거"),
        column_config={
            "수익률": st.column_config.NumberColumn(
                help="수익률 퍼센트",
                format="%.2f％"
            ),
        },
    )

    # 3. 저장 버튼
    if st.button("💾 전체 저장하기"):
        try:
            with sqlite3.connect(db_path, check_same_thread=False) as conn:
                c = conn.cursor()

                # 기존 청산된 거래 삭제
                c.execute("DELETE FROM trades WHERE is_closed = 1")

                # 새로 저장
                for _, row in edited.iterrows():
                    row_id = row["id"]
                    ticker = row["ticker"]
                    entry_price = df[df["id"] == row_id]["entry_price"].values[0]
                    direction = row["direction"]  # 바로 edited에서 가져옴
                    entry_time = df[df["id"] == row_id]["entry_time"].values[0]
                    is_closed = 1

                    exit_price = float(row["청산가"])
                    exit_time = str(row["청산 시각"])
                    reason = str(row["매매 근거"])

                    # 수익률 자동 계산
                    return_rate = round(((exit_price - entry_price) / entry_price) * 100, 2)
                    if direction == 0:
                        return_rate *= -1

                    # 저장
                    c.execute(
                        '''
                        INSERT INTO trades (id, ticker, direction, entry_price, entry_time,
                                            is_closed, exit_price, exit_time, return_rate, reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            row_id, ticker, direction, entry_price, entry_time,
                            is_closed, exit_price, exit_time, return_rate, reason
                        )
                    )
                conn.commit()
                st.success("전체 데이터가 저장되었습니다!")
                st.rerun()
        except Exception as e:
            st.error(f"❌ 저장 실패: {e}")
