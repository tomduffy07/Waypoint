"""
Waypoint — Boston prototype
Run:
    pip install streamlit
    streamlit run waypoint_boston.py

This is a local prototype with illustrative travel estimates.
It does not use live maps, MBTA data, flight feeds, GPS tracking, or emergency dispatch.
"""

from datetime import datetime, time, timedelta
import streamlit as st

st.set_page_config(
    page_title="Waypoint | Boston",
    page_icon="✈️",
    layout="wide",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background:
          radial-gradient(ellipse at 8% 0%, rgba(116,35,143,.25), transparent 35%),
          radial-gradient(ellipse at 95% 100%, rgba(223,76,72,.16), transparent 35%),
          #0b0910;
        color: #f7f3fa;
    }
    [data-testid="stSidebar"] {background:#15111c;}
    h1, h2, h3 {color:#fff;}
    .brand {font-size:14px;letter-spacing:5px;color:#d98be8;font-weight:700;}
    .hero {
      padding:28px;border:1px solid #392641;border-radius:18px;
      background:linear-gradient(115deg,rgba(111,35,135,.32),rgba(236,91,91,.10));
    }
    .muted {color:#b7adbf;}
    .card {
      background:#191520;border:1px solid #352b3c;border-radius:15px;
      padding:17px;margin-bottom:12px;
    }
    .safety {
      background:#211923;border:1px solid #80505b;border-radius:15px;padding:17px;
    }
    div.stButton > button {
      background:linear-gradient(110deg,#9e35bb,#e75e77);
      color:white;border:0;border-radius:10px;font-weight:700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sample Boston recommendations ----------
PLACES = [
    {
        "name": "Boston Public Garden",
        "neighborhood": "Back Bay / Beacon Hill",
        "emoji": "🌳",
        "categories": ["Outdoors", "History"],
        "visit": 35,
        "travel": 25,
        "dayparts": ["Daytime", "Evening"],
        "description": "A classic Boston green space with paths, gardens, and lagoon views.",
    },
    {
        "name": "Boston Common & Freedom Trail",
        "neighborhood": "Downtown",
        "emoji": "🏛️",
        "categories": ["History", "Outdoors"],
        "visit": 45,
        "travel": 25,
        "dayparts": ["Daytime", "Evening"],
        "description": "Explore the historic Common and a section of the Freedom Trail.",
    },
    {
        "name": "North End",
        "neighborhood": "North End",
        "emoji": "🍝",
        "categories": ["Food", "History"],
        "visit": 55,
        "travel": 30,
        "dayparts": ["Daytime", "Evening"],
        "description": "Historic streets, Italian cafés, bakeries, and neighborhood character.",
    },
    {
        "name": "Faneuil Hall & Quincy Market",
        "neighborhood": "Downtown",
        "emoji": "🛍️",
        "categories": ["Shopping", "Food", "History"],
        "visit": 40,
        "travel": 25,
        "dayparts": ["Daytime", "Evening"],
        "description": "A busy historic marketplace with food stalls and shops.",
    },
    {
        "name": "Institute of Contemporary Art",
        "neighborhood": "Seaport",
        "emoji": "🎨",
        "categories": ["Culture", "Waterfront"],
        "visit": 55,
        "travel": 30,
        "dayparts": ["Daytime"],
        "description": "Contemporary art and harbor views on the waterfront.",
    },
    {
        "name": "Boston Harborwalk",
        "neighborhood": "Waterfront",
        "emoji": "⛵",
        "categories": ["Waterfront", "Outdoors"],
        "visit": 35,
        "travel": 30,
        "dayparts": ["Daytime", "Evening"],
        "description": "Enjoy a stretch of Boston Harbor and the city skyline.",
    },
    {
        "name": "Newbury Street",
        "neighborhood": "Back Bay",
        "emoji": "🛍️",
        "categories": ["Shopping", "Food"],
        "visit": 45,
        "travel": 30,
        "dayparts": ["Daytime", "Evening"],
        "description": "Boutiques, cafés, and classic Back Bay architecture.",
    },
    {
        "name": "Museum of Fine Arts",
        "neighborhood": "Fenway",
        "emoji": "🖼️",
        "categories": ["Culture", "History"],
        "visit": 65,
        "travel": 35,
        "dayparts": ["Daytime"],
        "description": "A major art collection spanning centuries and cultures.",
    },
]

CATEGORIES = ["History", "Food", "Culture", "Outdoors", "Shopping", "Waterfront"]


def format_duration(minutes: int) -> str:
    hours, mins = divmod(max(0, minutes), 60)
    if hours and mins:
        return f"{hours} hr {mins} min"
    if hours:
        return f"{hours} hr"
    return f"{mins} min"


def build_itinerary(
    total_minutes: int,
    interests: list[str],
    daypart: str,
    pace: str,
    safe_return: bool,
):
    """Build a simple ranked itinerary using sample, non-live estimates."""
    airport_transfer = 35  # illustrative one-way estimate
    return_buffer = 90 if safe_return else 60
    usable_minutes = total_minutes - airport_transfer - return_buffer

    if usable_minutes < 35:
        return [], usable_minutes, return_buffer, airport_transfer

    candidates = [
        place for place in PLACES
        if daypart in place["dayparts"]
        and (not interests or any(x in interests for x in place["categories"]))
    ]

    candidates.sort(
        key=lambda p: (
            sum(category in interests for category in p["categories"]),
            -p["travel"],
        ),
        reverse=True,
    )

    max_stops = {"Relaxed": 1, "Balanced": 2, "Fast-paced": 3}[pace]
    itinerary = []
    used = 0

    for place in candidates:
        duration = place["travel"] + place["visit"]
        if len(itinerary) < max_stops and used + duration <= usable_minutes:
            itinerary.append(place)
            used += duration

    return itinerary, usable_minutes - used, return_buffer, airport_transfer


# ---------- Header ----------
st.markdown('<div class="brand">WAYPOINT · BOSTON</div>', unsafe_allow_html=True)
st.title("Make the stop count.")
st.markdown(
    '<div class="hero"><h2>Don’t just wait. Wander.</h2>'
    '<p class="muted">Turn your time between flights into a Boston mini-trip. '
    'Tell us how much time you have, what you enjoy, and when your next flight leaves.</p>'
    '<b>✈️ Starting point: Boston Logan International Airport (BOS)</b></div>',
    unsafe_allow_html=True,
)

discover_tab, itinerary_tab, safety_tab = st.tabs(
    ["✦ Discover", "◎ My itinerary", "♧ Safety center"]
)

# ---------- Discover ----------
with discover_tab:
    st.subheader("Build your stop")

    left, right = st.columns([1, 1], gap="large")

    with left:
        hours_col, minutes_col = st.columns(2)
        with hours_col:
            hours = st.selectbox("Available time — hours", [2, 3, 4, 5, 6, 7, 8, 10], index=2)
        with minutes_col:
            extra_minutes = st.selectbox("Additional minutes", [0, 15, 30, 45], index=0)

        departure = st.time_input("Next flight departure time", value=time(18, 0))
        daypart = st.selectbox("When are you exploring?", ["Daytime", "Evening", "Late night"])
        interests = st.multiselect(
            "What are you interested in?",
            CATEGORIES,
            default=["History"],
        )
        pace = st.selectbox("Travel style", ["Balanced", "Relaxed", "Fast-paced"])

        safe_return = st.toggle(
            "Safe Return mode",
            value=True,
            help="Uses a larger return buffer in the sample itinerary.",
        )

        generate = st.button("Build my Boston itinerary →", use_container_width=True)

    with right:
        st.markdown("### Boston, waiting for you")
        st.markdown(
            """
            <div class="card">
            <h3>📍 Logan → Greater Boston</h3>
            <p class="muted">Explore the North End, the Public Garden, the Freedom Trail,
            the Seaport, and more.</p>
            <p>🏛️ History &nbsp; 🍝 Food &nbsp; 🌳 Outdoors</p>
            <small class="muted">Boston launch market · Sample destination list</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info(
            "Travel estimates and destination availability in this prototype are "
            "illustrative. Check live directions, opening hours, and MBTA service "
            "before leaving the airport."
        )

    if generate:
        total = hours * 60 + extra_minutes
        plan, flexible, buffer, airport_transfer = build_itinerary(
            total,
            interests,
            daypart,
            pace,
            safe_return,
        )

        st.session_state["plan"] = plan
        st.session_state["total"] = total
        st.session_state["buffer"] = buffer
        st.session_state["safe_return"] = safe_return
        st.session_state["departure"] = departure.strftime("%I:%M %p")
        st.session_state["flexible"] = flexible
        st.session_state["airport_transfer"] = airport_transfer

        st.divider()
        st.markdown("## Your Boston stop")

        if not plan:
            st.warning(
                "There may not be enough time for a city visit after allowing for "
                "the airport transfer and return buffer. Consider staying at Logan "
                "or choosing an airport-area activity."
            )
        else:
            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("Available time", format_duration(total))
            metric2.metric("Recommended stops", len(plan))
            metric3.metric("Return buffer", f"{buffer} min")

            for number, place in enumerate(plan, start=1):
                with st.container(border=True):
                    st.markdown(
                        f"### {number}. {place['emoji']} {place['name']}"
                    )
                    st.caption(
                        f"{place['neighborhood']} · "
                        f"{place['visit']} min suggested visit · "
                        f"{place['travel']} min sample travel estimate"
                    )
                    st.write(place["description"])

            st.markdown("### Return plan")
            st.write(
                f"- Target departure from your final stop: **work backward from "
                f"your flight time** using the return buffer."
            )
            st.write(f"- Sample airport transfer allowance: **{airport_transfer} minutes**.")
            st.write(f"- Pre-departure buffer: **{buffer} minutes**.")
            st.caption(
                "The app does not know your airline's check-in deadline, boarding "
                "time, security wait, or live traffic. Verify these independently."
            )

# ---------- Itinerary ----------
with itinerary_tab:
    st.subheader("My itinerary")
    plan = st.session_state.get("plan", [])

    if not plan:
        st.info("Build an itinerary in Discover to see your Boston stops here.")
    else:
        st.caption(
            f"Boston · Logan round trip · Flight departure: "
            f"{st.session_state.get('departure', 'Not set')}"
        )
        for i, place in enumerate(plan, 1):
            st.markdown(
                f"""
                <div class="card">
                <h3>{i}. {place['emoji']} {place['name']}</h3>
                <p class="muted">{place['neighborhood']} · "
                {place['visit']} minute suggested visit</p>
                <p>{place['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("### ✈️ Return to Boston Logan")
        st.write(
            "Check a live route to Logan before leaving your final stop. "
            "Do not rely on the sample travel estimates as a guarantee."
        )

        share_text = (
            "My Waypoint Boston plan: "
            + " → ".join(place["name"] for place in plan)
            + f". Safe Return: {'on' if st.session_state.get('safe_return') else 'off'}."
        )
        st.markdown("**Trip summary to share with someone you trust:**")
        st.code(share_text)

# ---------- Safety center ----------
with safety_tab:
    st.subheader("Safety center")
    st.write("Exploration should feel exciting, not uncertain.")

    safe_return = st.toggle(
        "Enable Safe Return",
        value=st.session_state.get("safe_return", True),
        key="safety_toggle",
    )
    st.session_state["safe_return"] = safe_return

    st.markdown(
        """
        <div class="safety">
        <h3>🛡️ Safe Return</h3>
        <p>Waypoint builds a return buffer into the itinerary and encourages
        travelers to use busy, well-lit public areas and verified transportation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⏱ Return buffer")
        st.write("The prototype reserves 90 minutes before departure when Safe Return is on.")
        st.markdown("### 📍 Trip sharing")
        st.write("Copy your itinerary summary and send it to a trusted contact.")
    with col2:
        st.markdown("### 🚶 Route awareness")
        st.write("Prefer well-lit, populated streets and official transit or licensed transport.")
        st.markdown("### ✓ Personal check-in")
        reminder_minutes = st.selectbox(
            "When would you like to check in?",
            [30, 60, 90],
            format_func=lambda n: f"In {n} minutes",
        )
        st.write(
            f"Suggested check-in: {datetime.now() + timedelta(minutes=reminder_minutes):%I:%M %p}"
        )
        st.caption("This is a suggested time only; this prototype does not send notifications.")

    st.markdown("---")
    st.markdown("### Emergency information")
    st.error(
        "If you are in immediate danger or need urgent assistance in the United States, "
        "call 911. Contact airport staff or Massachusetts State Police for airport-related help."
    )
    st.markdown("[📞 Call 911](tel:911)")
    st.caption(
        "This prototype cannot call emergency services automatically, track your location, "
        "dispatch help, or notify a trusted contact. The 911 link requires a compatible device."
    )

st.markdown("---")
st.caption(
    "WAYPOINT · BOSTON PILOT · MAKE THE STOP COUNT. | "
    "Prototype only — sample recommendations, not live navigation or safety monitoring."
)
