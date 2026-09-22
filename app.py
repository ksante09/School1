import streamlit as st
import calendar
from datetime import date, timedelta


# ==============================
# 기본 설정
# ==============================

st.set_page_config(
    page_title="보라고등학교 휴일",
    page_icon="🏫",
    layout="wide"
)

SCHOOL_NAME = "보라고등학교"

WEEKDAYS = [
    "월", "화", "수",
    "목", "금", "토", "일"
]


# ==============================
# CSS
# ==============================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f6f8;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 30px;
    }

    .header {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        border: 1px solid #eeeeee;
    }

    .title {
        font-size: 30px;
        font-weight: 800;
    }

    .subtitle {
        color: #888888;
        margin-top: 5px;
    }

    .dday {
        background-color: #202124;
        color: white;
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
    }

    .dday-title {
        font-size: 24px;
        font-weight: 800;
    }

    .dday-date {
        color: #bbbbbb;
        margin-top: 5px;
    }

    .weekday {
        text-align: center;
        font-weight: bold;
        padding: 8px;
    }

    .sat {
        color: #377be6;
    }

    .sun {
        color: #e05252;
    }

    .day {
        background-color: white;
        border: 1px solid #eeeeee;
        border-radius: 12px;
        min-height: 100px;
        padding: 8px;
        margin-bottom: 8px;
    }

    .empty {
        min-height: 100px;
    }

    .today {
        border: 2px solid #222222;
    }

    .date {
        font-weight: bold;
    }

    .date-sat {
        color: #377be6;
    }

    .date-sun {
        color: #e05252;
    }

    .event {
        font-size: 10px;
        padding: 4px;
        border-radius: 5px;
        margin-top: 5px;
    }

    .holiday {
        background-color: #ffe2e2;
        color: #c33;
    }

    .vacation {
        background-color: #e1f4e5;
        color: #287a3c;
    }

    .closed {
        background-color: #fff0d5;
        color: #95631d;
    }

    @media (max-width: 700px) {

        .block-container {
            padding: 10px;
        }

        .title {
            font-size: 24px;
        }

        .day {
            min-height: 75px;
            padding: 5px;
        }

        .empty {
            min-height: 75px;
        }

        .event {
            font-size: 8px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==============================
# 헤더
# ==============================

st.markdown(
    """
    <div class="header">
        <div class="title">
            🏫 보라고등학교
        </div>

        <div class="subtitle">
            휴일 · 방학 · 재량휴업일 · 학사일정
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==============================
# 오늘 날짜
# ==============================

today = date.today()


# ==============================
# 연도 / 월 선택
# ==============================

col1, col2 = st.columns(2)

with col1:
    year = st.selectbox(
        "연도",
        range(today.year - 1, today.year + 3),
        index=1
    )

with col2:
    month = st.selectbox(
        "월",
        range(1, 13),
        index=today.month - 1,
        format_func=lambda x: f"{x}월"
    )


# ==============================
# 기본 휴일 데이터
# ==============================

holidays = {}


# 주말 자동 등록
current = date(year, 1, 1)
end = date(year, 12, 31)

while current <= end:

    if current.weekday() >= 5:
        holidays[current] = "주말"

    current += timedelta(days=1)


# ==============================
# 주요 공휴일
# ==============================

fixed_holidays = {
    (1, 1): "신정",
    (3, 1): "삼일절",
    (5, 5): "어린이날",
    (6, 6): "현충일",
    (8, 15): "광복절",
    (10, 3): "개천절",
    (10, 9): "한글날",
    (12, 25): "성탄절"
}

for (m, d), name in fixed_holidays.items():

    holiday_date = date(year, m, d)

    holidays[holiday_date] = name


# ==============================
# 다음 휴일
# ==============================

future_holidays = [
    d for d in holidays
    if d >= today
]

future_holidays.sort()

if future_holidays:

    next_holiday = future_holidays[0]

    days_left = (
        next_holiday - today
    ).days

    if days_left == 0:
        dday_text = "오늘은 휴일입니다!"
    else:
        dday_text = f"D-{days_left}"

    holiday_name = holidays[next_holiday]

    st.markdown(
        f"""
        <div class="dday">

            <div>
                NEXT HOLIDAY
            </div>

            <div class="dday-title">
                {dday_text} · {holiday_name}
            </div>

            <div class="dday-date">
                {next_holiday.strftime("%Y년 %m월 %d일")}
                ({WEEKDAYS[next_holiday.weekday()]})
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================
# 달력 제목
# ==============================

st.markdown(
    f"""
    <h2>
        📅 {year}년 {month}월
    </h2>
    """,
    unsafe_allow_html=True
)


# ==============================
# 요일
# ==============================

cols = st.columns(7)

for i in range(7):

    with cols[i]:

        if i == 5:
            class_name = "weekday sat"

        elif i == 6:
            class_name = "weekday sun"

        else:
            class_name = "weekday"

        st.markdown(
            f"""
            <div class="{class_name}">
                {WEEKDAYS[i]}
            </div>
            """,
            unsafe_allow_html=True
        )


# ==============================
# 달력
# ==============================

weeks = calendar.monthcalendar(
    year,
    month
)

for week in weeks:

    cols = st.columns(7)

    for i, day in enumerate(week):

        with cols[i]:

            # 빈 날짜
            if day == 0:

                st.markdown(
                    '<div class="empty"></div>',
                    unsafe_allow_html=True
                )

                continue

            current_date = date(
                year,
                month,
                day
            )

            class_name = "day"

            if current_date == today:
                class_name += " today"

            st.markdown(
                f'<div class="{class_name}>',
                unsafe_allow_html=True
            )

            # 날짜 색깔
            if i == 5:
                date_class = "date date-sat"

            elif i == 6:
                date_class = "date date-sun"

            else:
                date_class = "date"

            st.markdown(
                f"""
                <div class="{date_class}">
                    {day}
                </div>
                """,
                unsafe_allow_html=True
            )

            # 휴일 표시
            if current_date in holidays:

                holiday_name = holidays[current_date]

                if holiday_name == "주말":

                    st.markdown(
                        """
                        <div class="event holiday">
                            휴일
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div class="event holiday">
                            🎉 {holiday_name}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ==============================
# 안내
# ==============================

st.divider()

st.info(
    "현재 버전은 인증키 없이 실행하기 위해 "
    "주말과 주요 공휴일을 표시합니다."
)

st.caption(
    "보라고등학교 휴일 정보"
)
