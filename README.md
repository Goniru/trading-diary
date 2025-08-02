# 📈 주식 매매 일기

Streamlit과 SQLite를 이용해 만든 간단한 주식 매매 일기 웹 앱입니다.  
거래 예측과 실제 청산 정보를 기록하고, 실시간 수익률을 확인할 수 있습니다.

---

## 📌 주요 기능

- 티커, 방향, 진입가격, 예측 근거, 진입시간 등 거래 정보 입력
- 청산 가격과 시간 등록 후 자동 수익률 계산
- Streamlit UI 기반 실시간 편집 및 저장
- SQLite를 통한 영속적인 데이터 저장
- 청산된 거래만 따로 모아 관리 가능

---

## 🖼️ 사용 예시

추후 추가 예정

---

## 🚀 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/Goniru/trading-diary.git
cd your-repo-name

# 2. 가상환경 설정 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 필요한 패키지 설치
pip install -r requirements.txt

# 4. 실행
streamlit run app.py
```

# ** 주의사항 **
- db는 예시 파일이므로 삭제 후 최초 실행
- streamlit 기반 앱이기 때문에 파이썬 코드실행이 아닌 streamlit run app.py로 실행해야 함
- main이 아닌 app을 실행해야 함

## ⚙️ 사용 기술

- Python
- Streamlit
- SQLite
- Pandas

## 개발자

Gonriu
