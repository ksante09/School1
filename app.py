```python
import streamlit as st
import requests
import calendar
from datetime import datetime, date, timedelta

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="보라고등학교",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

OFFICE_CODE = "J10"
SCHOOL_CODE = "7530882"
API_URL = "https://open.neis.go.kr/hub/SchoolSchedule"

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* 전체 */
.stApp {
    background: #f7f8fa;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* 헤더 */
.header {
    background: white;
    border-radius: 20px;
    padding: 28px 30px;
    margin-bottom: 20px;
    border: 1px solid #eeeeee;
}

.header-title {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -1px;
}

.header-sub {
    color: #6b7280;
    margin-top: 5px;
    font-size: 14px;
}

/* D-Day */
.dday {
    background: #111827;
    color: white;
    border-radius: 20px;
    padding: 25px 28px;
    margin-bottom: 20px;
}

.dday-small {
    color: #9ca3af;
    font-size: 13px;
}

.dday-title {
    font-size: 23px;
    font-weight: 700;
    margin-top: 5px;
}

.dday-date {
    color: #d1d5db;
    margin-top: 5px;
}

/* 섹션 */
.section-title {
    font-size: 20px;
    font-weight: 750;
    color: #111827;
    margin-top: 28px;
    margin-bottom: 12px;
}

/* 달력 */
.calendar-card {
    background: white;
    border-radius: 20px;
    padding: 20px;
    border: 1px solid #eeeeee;
}

/* 날짜 */
.day {
    min-height: 105px;
    padding: 10px;
    border-radius: 13px;
    background: #fafafa;
    border: 1px solid #f0f0f0;
    margin-bottom: 8px;
}

.day:hover {
    border-color: #d1d5db;
}

.day-number {
    font-size: 14px;
    font-weight: 700;
    color: #374151;
}

.saturday {
    color: #2563eb;
}

.sunday {
    color: #ef4444;
}

.today {
    border: 2px solid #111827;
    background: white;
}

.empty-day {
    min-height: 105px;
    background: transparent;
}

/* 일정 태그 */
.event {
    font-size: 11px;
    line-height: 1.3;
    padding: 4px 6px;
    margin-top: 5px;
    border-radius: 6px;
    background: #eeeeee;
    color: #374151;
}

.event-holiday {
    background: #fee2e2;
    color: #b91c1c;
}

.event-vacation {
    background: #dcfce7;
    color: #166534;
}

.event-closed {
    background: #fef3c7;
    color: #92400e;
}

/* 일정 리스트 */
.schedule-item {
    background: white;
    border: 1px solid #eeeeee;
    border-radius: 14px;
    padding: 15px 18px;
    margin-bottom: 8px;
}

.schedule-date {
    font-size: 12px;
    color: #6b7280;
}

.schedule-name {
    font-size: 15px;
    font-weight: 650;
    color: #111827;
    margin-top: 3px;
}

/* 모바일 */
@media (max-width: 768px) {

    .block-container {
        padding-left: 12px;
        padding-right: 12px;
        padding-top: 1rem;
    }

    .header {
        padding: 22px;
        border-radius: 16px;
    }

    .header-title {
        font-size: 25px;
    }

    .dday {
        border-radius: 16px;
        padding: 20px;
    }

    .day {
        min-height: 82px;
        padding: 7px;
    }

    .empty-day {
        min-height: 82px;
    }

    .event {
        font-size: 9px;
        padding: 3px 4px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NEIS API
# =========================================================

@st.cache_data(ttl=3600)
def get_schedule(year):

    try:

        api_key = st.secrets["NEIS_API_KEY"]

    except:

        return None, "NEIS_API_KEY가 설정되지 않았습니다."

    params = {
        "KEY": api_key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000,
        "ATPT_OFCDC_SC_CODE": OFFICE_CODE,
        "SD_SCHUL_CODE": SCHOOL_CODE,
        "AY": year
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "SchoolSchedule" not in data:
            return [], None

        rows = data["SchoolSchedule"][1]["row"]

        return rows, None

    except Exception as e:

        return None, str(e)


# =========================================================
# 데이터 정리
# =========================================================

def parse_schedule(rows):

    result = {}

    for row in rows:

        ymd = row.get("AA_YMD", "")

        if not ymd:
            continue

        try:

            d = datetime.strptime(
                ymd,
                "%Y%m%d"
            ).date()

        except:

            continue

        event = {
            "name": row.get("EVENT_NM", "").strip(),
            "content": row.get("EVENT_CNTNT", "").strip()
        }

        result.setdefault(d, []).append(event)

    return result


# =========================================================
# 일정 종류
# =========================================================

def event_type(name, content):

    text = (
        name + " " + content
    ).replace(" ", "")

    if "방학" in text:
        return "vacation"

    if "재량휴업일" in text:
        return "closed"

    holiday_words = [
        "공휴일",
        "대체공휴일",
        "설날",
        "추석",
        "어린이날",
        "현충일",
        "광복절",
        "개천절",
        "한글날",
        "성탄절",
        "삼일절",
        "부처님오신날"
    ]

    if any(
        word in text
        for word in holiday_words
    ):
        return "holiday"

    return "normal"


# =========================================================
# 휴일
# =========================================================

def make_holidays(year, schedule):

    holidays = {}

    d = date(year, 1, 1)
    end = date(year, 12, 31)

    while d <= end:

        if d.weekday() >= 5:
            holidays[d] = "주말"

        d += timedelta(days=1)

    for d, events in schedule.items():

        for event in events:

            t = event_type(
                event["name"],
                event["content"]
            )

            if t in [
                "holiday",
                "vacation",
                "closed"
            ]:
                holidays[d] = event["name"]

    return holidays


# =========================================================
# 헤더
# =========================================================

st.markdown("""
<div class="header">

<div class="header-title">
🏫 보라고등학교
</div>

<div class="header-sub">
휴일 · 방학 · 학사일정을 한눈에 확인하세요
</div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# 연도
# =========================================================

current_year = date.today().year

year = st.selectbox(
    "학년도",
    range(
        current_year - 1,
        current_year + 3
    ),
    index=1,
    label_visibility="collapsed"
)


# =========================================================
# API
# =========================================================

rows, error = get_schedule(year)

if error:

    st.error(error)
    st.stop()

if rows is None:

    st.stop()

schedule = parse_schedule(rows)

holidays = make_holidays(
    year,
    schedule
)


# =========================================================
# 다음 휴일
# =========================================================

today = date.today()

future_holidays = [
    d for d in holidays
    if d >= today
]

next_holiday = (
    min(future_holidays)
    if future_holidays
    else None
)


if next_holiday:

    diff = (
        next_holiday - today
    ).days

    if diff == 0:
        dday = "TODAY"
    else:
        dday = f"D-{diff}"

    reason = holidays[next_holiday]

    st.markdown(f"""
    <div class="dday">

        <div class="dday-small">
        NEXT HOLIDAY
        </div>

        <div class="dday-title">
        {dday} · {reason}
        </div>

        <div class="dday-date">
        {next_holiday.strftime("%Y년 %m월 %d일")}
        ({WEEKDAYS[next_holiday.weekday()]})
        </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 월 선택
# =========================================================

month = st.selectbox(
    "월",
    range(1, 13),
    index=today.month - 1,
    format_func=lambda x: f"{x}월"
)


# =========================================================
# 달력
# =========================================================

st.markdown(
    f'<div class="section-title">'
    f'{year}년 {month}월'
    f'</div>',
    unsafe_allow_html=True
)

# 요일
cols = st.columns(7)

for i, day_name in enumerate(WEEKDAYS):

    with cols[i]:

        if i == 5:

            st.markdown(
                f"<div style='text-align:center;"
                f"color:#2563eb;font-weight:700'>"
                f"{day_name}</div>",
                unsafe_allow_html=True
            )

        elif i == 6:

            st.markdown(
                f"<div style='text-align:center;"
                f"color:#ef4444;font-weight:700'>"
                f"{day_name}</div>",
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"<div style='text-align:center;"
                f"color:#6b7280;font-weight:700'>"
                f"{day_name}</div>",
                unsafe_allow_html=True
            )


weeks = calendar.Calendar(
    firstweekday=0
).monthdayscalendar(
    year,
    month
)


for week in weeks:

    cols = st.columns(7)

    for i, day in enumerate(week):

        with cols[i]:

            if day == 0:

                st.markdown(
                    '<div class="empty-day"></div>',
                    unsafe_allow_html=True
                )

                continue

            d = date(
                year,
                month,
                day
            )

            classes = ["day"]

            if d == today:
                classes.append("today")

            st.markdown(
                f'<div class="{" ".join(classes)}">',
                unsafe_allow_html=True
            )

            if i == 6:

                color_class = "sunday"

            elif i == 5:

                color_class = "saturday"

            else:

                color_class = ""

            st.markdown(
                f'<div class="day-number '
                f'{color_class}">'
                f'{day}</div>',
                unsafe_allow_html=True
            )

            events = schedule.get(
                d,
                []
            )

            for event in events:

                name = event["name"]

                if not name:
                    continue

                t = event_type(
                    name,
                    event["content"]
                )

                if t == "holiday":

                    css = "event event-holiday"
                    emoji = "🎉"

                elif t == "vacation":

                    css = "event event-vacation"
                    emoji = "🏖️"

                elif t == "closed":

                    css = "event event-closed"
                    emoji = "🏫"

                else:

                    css = "event"
                    emoji = "📌"

                short_name = (
                    name[:11] + "..."
                    if len(name) > 11
                    else name
                )

                st.markdown(
                    f'<div class="{css}">'
                    f'{emoji} {short_name}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            if (
                d.weekday() >= 5
                and not events
            ):

                st.markdown(
                    '<div class="event '
                    'event-holiday">'
                    '휴일'
                    '</div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


# =========================================================
# 일정
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📋 이번 달 일정'
    '</div>',
    unsafe_allow_html=True
)

month_events = []

for d, events in schedule.items():

    if (
        d.year == year
        and d.month == month
    ):

        for event in events:

            month_events.append(
                (d, event)
            )

month_events.sort(
    key=lambda x: x[0]
)


if month_events:

    for d, event in month_events:

        t = event_type(
            event["name"],
            event["content"]
        )

        if t == "vacation":
            emoji = "🏖️"

        elif t == "closed":
            emoji = "🏫"

        elif t == "holiday":
            emoji = "🎉"

        else:
            emoji = "📌"

        st.markdown(f"""
        <div class="schedule-item">

            <div class="schedule-date">
            {d.strftime("%m월 %d일")}
            ({WEEKDAYS[d.weekday()]})
            </div>

            <div class="schedule-name">
            {emoji} {event["name"]}
            </div>

        </div>
        """, unsafe_allow_html=True)

else:

    st.info(
        "이번 달에는 등록된 학사일정이 없습니다."
    )


# =========================================================
# 하단
# =========================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)

st.caption(
    "NEIS 학사일정 API · "
    "보라고등학교 (J10 / 7530882)"
)
```
