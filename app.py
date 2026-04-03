import requests
import streamlit as st
import time

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# 🌗 THEME TOGGLE
# =============================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

toggle = st.sidebar.toggle("🌙 Dark Mode")

if toggle:
    st.session_state.theme = "dark"
else:
    st.session_state.theme = "light"

# =============================
# 🎨 UI
# =============================
st.markdown(f"""
<style>

/* =========================
   🎨 THEME VARIABLES
========================= */

:root {{
    --bg: {"#F2F3F5" if st.session_state.theme == "light" else "#121212"};
    --card-bg: {"#ffffff" if st.session_state.theme == "light" else "#1E1E1E"};
    --text-primary: {"#2D3436" if st.session_state.theme == "light" else "#E0E0E0"};
    --text-secondary: {"#3B3B98" if st.session_state.theme == "light" else "#B0B0B0"};
    --border: {"#4B5563" if st.session_state.theme == "light" else "#D1D5DB"}; 
    --accent: {"#008080" if st.session_state.theme == "light" else "#00E5E5"};
    --cta: {"#FF7E5F" if st.session_state.theme == "light" else "#F25912"};
}}

/* =========================
   GLOBAL FIX
========================= */

html, body {{
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
}}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.block-container {{
    background-color: var(--bg) !important;
}}

/* FIX TEXT COLORS EVERYWHERE */
* {{
    color: var(--text-primary) !important;
}}

/* =========================
   HEADER
========================= */

.title {{
    text-align:center;
    font-size:3.5rem;
    font-weight:800;
    text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    color: var(--text-secondary) !important;
}}

.subtitle {{
    text-align: center;
    font-size: 1.1rem;
    color: var(--accent);
    margin-top: -5px;
    margin-bottom: 10px;
    color: var(--text-secondary) !important;
}}

/* =========================
   HERO BANNER
========================= */

.hero {{
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 20px;
}}

.hero img {{
    width: 100%;
    height: 400px;
    object-fit: cover;
}}

.hero-overlay {{
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 20px;
    background: linear-gradient(to top, rgba(0,0,0,0.85), transparent);
}}

.hero-title {{
    font-size: 2rem;
    font-weight: 700;
    color: white;
}}

.hero-meta {{
    font-size: 0.9rem;
    color: #ddd;
}}

/* =========================
   CARD
========================= */

.card {{
    background: var(--card-bg);
    border-radius: 18px;
    overflow: hidden;
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}}

.card:hover {{
    transform: scale(1.05);
    box-shadow: 0 20px 50px rgba(0,0,0,0.25);
}}

/* =========================
   INPUT + SELECTBOX
========================= */

.stTextInput input{{
    background-color: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}}

/* =========================
   SIDEBAR
========================= */

[data-testid="stSidebar"] {{
    background-color: var(--card-bg) !important;
}}

[data-testid="stSidebar"] * {{
    color: var(--text-primary) !important;
}}

/* =========================
   BUTTON
========================= */

button {{
    border-radius: 12px !important;
}}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* =========================
   CLEAN SELECTBOX (FINAL FIX)
========================= */

/* Remove all outer spacing */
div[data-baseweb="select"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Main visible box */
div[data-baseweb="select"] > div {
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    background-color: var(--card-bg) !important;

    padding: 0 10px !important;
    height: 42px !important;

    display: flex !important;
    align-items: center !important;

    box-shadow: none !important;
}

/* Kill ALL inner borders + spacing */
div[data-baseweb="select"] * {
    border: none !important;
    box-shadow: none !important;
}

/* Input styling */
div[data-baseweb="select"] input {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
}

/* Arrow icon */
div[data-baseweb="select"] svg {
    color: var(--text-primary) !important;
}

/* Hover */
div[data-baseweb="select"] > div:hover {
    border: 1.5px solid var(--accent) !important;
}

/* Focus */
div[data-baseweb="select"] > div:focus-within {
    border: 1.5px solid var(--accent) !important;
}

</style>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
params = st.query_params

if "view" not in st.session_state:
    st.session_state.view = params.get("view", "home")

if "id" in params:
    st.session_state.selected_tmdb_id = int(params["id"])
    st.session_state.view = "details"

# =============================
# API
# =============================
@st.cache_data(ttl=60)
def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# =============================
# 🎥 YOUTUBE TRAILER LINK
# =============================
def get_youtube_link(title):
    query = title.replace(" ", "+") + "+official+trailer"
    return f"https://www.youtube.com/results?search_query={query}"

# =============================
# GRID
# =============================
def poster_grid(cards, cols=6):
    rows = (len(cards) + cols - 1) // cols
    i = 0

    for _ in range(rows):
        row = st.columns(cols)

        for col in row:
            if i >= len(cards):
                break

            m = cards[i]
            i += 1

            poster = m.get("poster_url", "")
            title = m.get("title", "No Title")
            rating = m.get("vote_average", "")

            col.markdown(
                f"""
                <a href="?view=details&id={m['tmdb_id']}" style="text-decoration:none;">
                    <div class="card">
                        <img src="{poster}" class="movie-img"/>
                        <div class="rating">⭐ {rating}</div>
                        <div style="padding:10px;">
                            <p style="margin:0; font-weight:600; font-size:0.9rem; color:#111827;">
                                {title}
                            </p>
                        </div>
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )

# =============================
# SIDEBAR 
# =============================
with st.sidebar:
    st.markdown("## 🎬 Browse")

    category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"]
    )

    cols = st.slider("Columns", 4, 8, 6)

# =============================
# HEADER
# =============================
st.markdown("<div class='title'>🎬 Movie Recommender</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Discover movies like Netflix 🍿</div>",
    unsafe_allow_html=True
)
st.divider()

# =============================
# HOME
# =============================
if st.session_state.view == "home":

    search = st.text_input("🔍 Search movies")

    data = api_get("/tmdb/search", {"query": search}) if search else api_get("/home", {"category": category, "limit": 24})

    if not data:
        st.error("Failed to load movies")
        st.stop()

    results = data.get("results", []) if search else data

    cards = [
        {
            "tmdb_id": m["id"] if search else m["tmdb_id"],
            "title": m.get("title"),
            "poster_url": f"{TMDB_IMG}{m['poster_path']}" if search and m.get("poster_path") else m.get("poster_url"),
            "vote_average": m.get("vote_average", "")
        }
        for m in results[:24]
    ]

    poster_grid(cards, cols)

# =============================
# DETAILS
# =============================
elif st.session_state.view == "details":

    tmdb_id = st.session_state.selected_tmdb_id

    # BACK BUTTON
    if st.button("← Back"):
        st.query_params.clear()
        st.session_state.view = "home"
        st.rerun()

    data = api_get(f"/movie/id/{tmdb_id}")

    if not data:
        st.error("Movie not found")
        st.stop()

    if isinstance(data, list):
        data = data[0]

    # HERO
    if data.get("backdrop_url"):
        st.image(data.get("backdrop_url"), use_container_width=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        if data.get("poster_url"):
            st.image(data.get("poster_url"), use_container_width=True)

    with col2:
        st.markdown(f"## {data.get('title','No Title')}")
        st.write("📅", data.get("release_date", "N/A"))
        st.write("🎭", ", ".join([g["name"] for g in data.get("genres", [])]))

        # 🎥 YOUTUBE TRAILER BUTTON 
        st.markdown("### 🎥 Trailer")

        youtube_link = get_youtube_link(data.get("title", ""))

        st.markdown(
            f"""
            <div style="margin-top:10px;">
                <a href="{youtube_link}" target="_blank" style="text-decoration:none;">
                    <button style="
                        background: linear-gradient(90deg,#ef4444,#dc2626);
                        border:none;
                        padding:14px 28px;
                        color:white;
                        border-radius:12px;
                        font-weight:600;
                        font-size:1rem;
                        box-shadow:0 6px 20px rgba(239,68,68,0.4);
                        cursor:pointer;">
                        ▶ Watch Trailer
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        

        st.markdown("### Overview")
        st.write(data.get("overview", "No description"))

    st.divider()

    bundle = api_get("/movie/search", {"query": data.get("title","")})

    if bundle:
        st.markdown("### 🔎 Similar Movies")

        tfidf = [
            {
                "tmdb_id": x["tmdb"]["tmdb_id"],
                "title": x["tmdb"]["title"],
                "poster_url": x["tmdb"]["poster_url"]
            }
            for x in bundle.get("tfidf_recommendations", [])
            if x.get("tmdb")
        ]

        poster_grid(tfidf, cols)

        st.markdown("### 🎭 Genre Based")
        poster_grid(bundle.get("genre_recommendations", []), cols)