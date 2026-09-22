```python
import streamlit as st
import requests
import calendar
from datetime import date, datetime, timedelta

# ==================================================
# 기본 설정
# ==================================================

st.set_page_config(
    page_title="보라고등학교 휴일",
    page_icon="🏫",
    layout="wide"
)

# 경기도교육청
OFFICE_CODE = "J10"

# 보라고등학교
SCHOOL_CODE = "7530882"

# NEIS 학사일정 API
API_URL = "https://open.neis.go.kr/hub/SchoolSchedule"

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.stApp {
    background: #f7f8fa;
}

.block-container {
    max-width: 1050px;
    padding-top: 30px;
}

/* 헤더 */

.header {
    background: white;
    padding: 28px;
    border-radius: 22px;
    border: 1px solid #eeeeee;
    margin-bottom: 18px;
}

.title {
    font-size: 30px;
    font-weight: 800;
    color: #17181a;
}

.subtitle {
    color: #8a8f98;
    font-size: 14px;
    margin-top: 5px;
}


/* D-Day */

.dday {
    background: #17181a;
    color: white;
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
}

.dday-label {
    font-size: 12px;
    color: #aeb3ba;
}

.dday-main {
    font-size: 24px;
    font-weight: 800;
    margin-top: 5px;
}

.dday-date {
    font-size: 13px;
    color: #bfc3c9;
    margin-top: 5px;
}


/* 달력 */

.calendar {
    background: white;
    border-radius: 20px;
    padding: 15px;
    border: 1px solid #eeeeee;
}

.weekday {
    text-align: center;
    font-weight: 700;
    font-size: 13px;
    padding: 5px;
    color: #777;
}

.sat {
    color: #3977e8;
}

.sun {
    color: #e45c5c;
}


.day {
    background: #fafafa;
    border: 1px solid #eeeeee;
    border-radius: 12px;
    min-height: 105px;
    padding: 8px;
    margin-bottom: 7px;
}

.empty {
    min-height: 105px;
}

.today {
    border: 2px solid #17181a;
    background: white;
}

.date {
    font-size: 14px;
    font-weight: 700;
}

.date-sat {
    color: #3977e8;
}

.date-sun {
    color: #e45c5c;
}


/* 일정 */

.event {
    font-size: 10px;
    padding: 4px;
    border-radius: 6px;
    margin-top: 5px;
    line-height: 1.2;
}

.normal {
    background: #eeeeef;
    color: #555;
}

.holiday {
    background: #ffe6e6;
    color: #c34d4d;
}

.vacation {
    background: #e1f4e5;
    color: #38824b;
}

.closed {
    background: #fff0d5;
    color: #99631d;
}


/* 일정 목록 */

.schedule {
    background: white;
    border: 1px solid #eeeeee;
    border-radius: 14px;
    padding: 14px 17px;
    margin-bottom: 8px;
}

.schedule-date {
    font-size: 12px;
    color: #9297a0;
}

.schedule-name {
    font-size: 15px;
    font-weight: 650;
    margin-top: 3px;
}

.schedule-content {
    color: #777;
    font-size: 12px;
    margin-top: 4px;
}


/* 모바일 */

@media(max-width:700px) {

    .block-container {
        padding: 15px 8px;
    }

    .header {
        padding: 21px;
        border-radius: 17px;
    }

    .title {
        font-size: 24px;
    }

    .dday {
        padding: 20px;
        border-radius: 17px;
    }

    .day {
        min-height: 78px;
        padding: 5px;
    }

    .empty {
        min-height: 78px;
    }

    .event {
        font-size: 8px;
        padding: 3px;
    }

    .date {
        font-size: 12px;
    }

}

</style>
""", unsafe_allow_html=True)


# ==================================================
# NEIS API
# ==================================================

@st.cache_data(ttl=3600)
def get_schedule(year):

    params = {
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


# ==================================================
# 데이터 정리
# ==================================================

def parse_schedule(rows):

    schedule = {}

    for row in rows:

        ymd = row.get("AA_YMD")

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
            "name": row.get("EVENT_NM", ""),
            "content": row.get("EVENT_CNTNT", "")
        }

        schedule.setdefault(d, []).append(event)

    return schedule


# ==================================================
# 일정 종류
# ==================================================

def get_type(name, content):

    text = (
        name + content
    ).replace(" ", "")

    if "방학" in text:
        return "vacation"

    if "재량휴업일" in text:
        return "closed"

    holidays = [
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

    for word in holidays:

        if word in text:
            return "holiday"

    return "normal"


# ==================================================
# 휴일 계산
# ==================================================

def get_holidays(year, schedule):

    result = {}

    current = date(year, 1, 1)
    end = date(year, 12, 31)

    # 주말
    while current <= end:

        if current.weekday() >= 5:
            result[current] = "주말"

        current += timedelta(days=1)

    # 학교 일정
    for d, events in schedule.items():

        for event in events:

            t = get_type(
                event["name"],
                event["content"]
            )

            if t in [
                "holiday",
                "vacation",
                "closed"
            ]:

                result[d] = event["name"]

    return result


# ==================================================
# 헤더
# ==================================================

st.markdown("""
<div class="header">

<div class="title">
🏫 보라고등학교
</div>

<div class="subtitle">
휴일 · 방학 · 학사일정
</div>

</div>
""", unsafe_allow_html=True)


# ==================================================
# 연도
# ==================================================

today = date.today()

year = st.selectbox(
    "학년도",
    range(
        today.year - 1,
        today.year + 3
    ),
    index=1,
    format_func=lambda x: f"{x}학년도"
)


# ==================================================
# API
# ==================================================

rows, error = get_schedule(year)

if error:

    st.error(
        "NEIS 데이터를 가져오지 못했습니다.\n\n"
        + error
    )

    st.stop()

schedule = parse_schedule(rows)

holidays = get_holidays(
    year,
    schedule
)


# ==================================================
# 다음 휴일
# ==================================================

future = [
    d for d in holidays
    if d >= today
]

if future:

    next_holiday = min(future)

    diff = (
        next_holiday - today
    ).days

    if diff == 0:
        dday = "오늘은 휴일!"
    else:
        dday = f"D-{diff}"

    st.markdown(f"""
    <div class="dday">

        <div class="dday-label">
        NEXT HOLIDAY
        </div>

        <div class="dday-main">
        {dday} · {holidays[next_holiday]}
        </div>

        <div class="dday-date">
        {next_holiday.strftime("%Y년 %m월 %d일")}
        ({WEEKDAYS[next_holiday.weekday()]})
        </div>

    </div>
    """, unsafe_allow_html=True)


# ==================================================
# 월 선택
# ==================================================

month = st.selectbox(
    "월",
    range(1, 13),
    index=today.month - 1,
    format_func=lambda x: f"{x}월"
)


# ==================================================
# 달력
# ==================================================

st.markdown(
    f'<div style="font-size:20px;font-weight:800;'
    f'margin:25px 0 12px 2px;">'
    f'{year}년 {month}월'
    f'</div>',
    unsafe_allow_html=True
)

# 요일
cols = st.columns(7)

for i, weekday in enumerate(WEEKDAYS):

    with cols[i]:

        css = "weekday"

        if i == 5:
            css += " sat"

        elif i == 6:
            css += " sun"

        st.markdown(
            f'<div class="{css}">{weekday}</div>',
            unsafe_allow_html=True
        )


# 날짜
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
                    '<div class="empty"></div>',
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

            number_class = "date"

            if i == 5:
                number_class += " date-sat"

            elif i == 6:
                number_class += " date-sun"

            st.markdown(
                f'<div class="{number_class}">'
                f'{day}'
                f'</div>',
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

                t = get_type(
                    name,
                    event["content"]
                )

                if t == "holiday":

                    css = "event holiday"
                    emoji = "🎉"

                elif t == "vacation":

                    css = "event vacation"
                    emoji = "🏖️"

                elif t == "closed":

                    css = "event closed"
                    emoji = "🏫"

                else:

                    css = "event normal"
                    emoji = "📌"

                short = (
                    name[:12] + "..."
                    if len(name) > 12
                    else name
                )

                st.markdown(
                    f'<div class="{css}">'
                    f'{emoji} {short}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            if (
                d.weekday() >= 5
                and not events
            ):

                st.markdown(
                    '<div class="event holiday">'
                    '휴일'
                    '</div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


# ==================================================
# 이번 달 일정
# ==================================================

st.markdown(
    '<div style="font-size:20px;font-weight:800;'
    'margin:25px 0 12px 2px;">'
    '📋 이번 달 일정'
    '</div>',
    unsafe_allow_html=True
)

events = []

for d, items in schedule.items():

    if (
        d.year == year
        and d.month == month
    ):

        for item in items:

            events.append(
                (d, item)
            )

events.sort(
    key=lambda x: x[0]
)


if events:

    for d, event in events:

        t = get_type(
            event["name"],
            event["content"]
        )

        if t == "holiday":
            emoji = "🎉"

        elif t == "vacation":
            emoji = "🏖️"

        elif t == "closed":
            emoji = "🏫"

        else:
            emoji = "📌"

        content = ""

        if event["content"]:

            content = (
                f'<div class="schedule-content">'
                f'{event["content"]}'
                f'</div>'
            )

        st.markdown(
            f"""
            <div class="schedule">

                <div class="schedule-date">
                {d.strftime("%m월 %d일")}
                ({WEEKDAYS[d.weekday()]})
                </div>

                <div class="schedule-name">
                {emoji} {event["name"]}
                </div>

                {content}

            </div>
            """,
            unsafe_allow_html=True
        )

else:

    st.info(
        "이번 달 학사일정이 없습니다."
    )


# ==================================================
# 하단
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.caption(
    "NEIS 학사일정 · 보라고등학교"
)
```
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
