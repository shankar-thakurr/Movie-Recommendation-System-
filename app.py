import requests
import streamlit as st

# =============================
# CONFIG
# =============================
# If you want to use the live Render API, uncomment the first line. For local testing, use localhost.
# API_BASE = "https://movie-rec-466x.onrender.com"
API_BASE = "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

OMDB_API_KEY = st.secrets.get("OMDB_API_KEY", "YOUR_OMDB_API_KEY_HERE")
OMDB_BASE = "http://www.omdbapi.com/"

st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================
# PREMIUM STYLES
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap');

/* ═══════════════════════════════════════
   ROOT & GLOBAL
═══════════════════════════════════════ */
:root {
  --bg:         #080b0f;
  --bg2:        #0d1117;
  --bg3:        #111820;
  --surface:    #161d28;
  --surface2:   #1c2535;
  --border:     rgba(255,255,255,0.07);
  --border2:    rgba(255,255,255,0.12);
  --gold:       #f5c518;
  --gold2:      #e8b400;
  --red:        #e53e3e;
  --rt:         #fa320a;
  --meta:       #54b3f5;
  --text:       #e8eaf0;
  --text2:      #8b95a8;
  --text3:      #4a5568;
  --accent:     #3b82f6;
  --radius:     14px;
  --radius-lg:  20px;
}

/* Force dark background everywhere */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .main {
  background: var(--bg) !important;
  color: var(--text) !important;
}

[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}

/* Remove all default Streamlit padding clutter */
.block-container {
  padding: 0 2rem 3rem 2rem !important;
  max-width: 1500px !important;
}

/* Hide Streamlit default top padding */
[data-testid="stAppViewContainer"] > .main > .block-container {
  padding-top: 0 !important;
}

/* Global font */
html, body, [class*="css"], p, div, span, label, button {
  font-family: 'Outfit', sans-serif !important;
}

/* ═══════════════════════════════════════
   SIDEBAR TOGGLE ICON — @font-face OVERRIDE
   Replace Material Symbols font with a blank font
   so the ligature text renders as nothing, then
   show our own icon via ::after on the button.
═══════════════════════════════════════ */

/* Override Material Symbols with a blank/empty font
   This breaks the ligature so no text renders at all */
@font-face {
  font-family: 'Material Symbols Rounded';
  src: url('data:font/woff2;base64,d09GMgABAAAAAAIsAAsAAAAABjQAAAHgAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhYbDBsQBmAAXBEICjQEEAULDAABNgIkAxAEIAWEbgcgG4oFyB4AAAAAAAAA') format('woff2');
  font-weight: 100 700;
  font-style: normal;
}

/* Since font is blank, the span is invisible — now add our icon on the BUTTON */
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"],
[data-testid="stSidebar"] button[kind="header"] {
  position: relative !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 50% !important;
  width: 2.2rem !important;
  height: 2.2rem !important;
  min-width: 2.2rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s ease !important;
  padding: 0 !important;
}
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"]::after,
[data-testid="stSidebar"] button[kind="header"]::after {
  content: '' !important;
  position: absolute !important;
  width: 8px !important;
  height: 8px !important;
  border-left: 2.5px solid #f5c518 !important;
  border-bottom: 2.5px solid #f5c518 !important;
  transform: rotate(45deg) !important;
  left: 53% !important;
  top: 50% !important;
  margin-top: -4px !important;
  margin-left: -6px !important;
}
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"]:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {
  background: rgba(245,197,24,0.12) !important;
  border-color: #f5c518 !important;
  box-shadow: 0 0 14px rgba(245,197,24,0.2) !important;
}

[data-testid="collapsedControl"] {
  position: relative !important;
  background: #161d28 !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 50% !important;
  width: 2.2rem !important;
  height: 2.2rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s ease !important;
}
[data-testid="collapsedControl"]::after {
  content: '' !important;
  position: absolute !important;
  width: 8px !important;
  height: 8px !important;
  border-right: 2.5px solid #f5c518 !important;
  border-top: 2.5px solid #f5c518 !important;
  transform: rotate(45deg) !important;
  left: 45% !important;
  top: 50% !important;
  margin-top: -4px !important;
  margin-left: -4px !important;
}
[data-testid="collapsedControl"]:hover {
  background: rgba(245,197,24,0.12) !important;
  border-color: #f5c518 !important;
  box-shadow: 0 0 14px rgba(245,197,24,0.2) !important;
}

/* Sidebar collapse button — inject ‹ via ::before on button */
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"],
[data-testid="stSidebar"] button[kind="header"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 50% !important;
  width: 2.2rem !important;
  height: 2.2rem !important;
  min-width: 2.2rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s ease !important;
  padding: 0 !important;
  position: relative !important;
  overflow: visible !important;
}
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"]::before,
[data-testid="stSidebar"] button[kind="header"]::before {
  content: '⟨' !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 1.3rem !important;
  font-weight: 400 !important;
  color: var(--gold) !important;
  line-height: 1 !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
}
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"]:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {
  background: rgba(245,197,24,0.12) !important;
  border-color: var(--gold) !important;
  box-shadow: 0 0 14px rgba(245,197,24,0.2) !important;
}

/* Collapsed control — sidebar open button (outside sidebar) */
[data-testid="collapsedControl"] {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 50% !important;
  width: 2.2rem !important;
  height: 2.2rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s ease !important;
  position: relative !important;
  overflow: visible !important;
}
[data-testid="collapsedControl"]::before {
  content: '⟩' !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 1.3rem !important;
  font-weight: 400 !important;
  color: var(--gold) !important;
  line-height: 1 !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
}
[data-testid="collapsedControl"]:hover {
  background: rgba(245,197,24,0.12) !important;
  border-color: var(--gold) !important;
  box-shadow: 0 0 14px rgba(245,197,24,0.2) !important;
}

/* Inputs */
[data-testid="stTextInput"] input {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 1rem !important;
  padding: 0.75rem 1.1rem !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px rgba(245,197,24,0.12) !important;
  outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--text3) !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
}

/* Buttons */
[data-testid="stButton"] > button {
  background: linear-gradient(135deg, #1a2332, #222d3d) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.03em !important;
  padding: 0.35rem 0.7rem !important;
  transition: all 0.2s !important;
  width: 100% !important;
}
[data-testid="stButton"] > button:hover {
  background: linear-gradient(135deg, var(--gold2), #d4a000) !important;
  border-color: var(--gold) !important;
  color: #000 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(245,197,24,0.3) !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* Slider */
[data-testid="stSlider"] { filter: brightness(0.9); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 3px; }

/* ═══════════════════════════════════════
   HEADER HERO BANNER
═══════════════════════════════════════ */
.site-header {
  background: linear-gradient(180deg, #0d1117 0%, rgba(8,11,15,0) 100%),
              radial-gradient(ellipse 80% 60% at 50% -10%, rgba(245,197,24,0.08) 0%, transparent 70%);
  padding: 2.5rem 0 1rem 0;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}
.site-title {
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 3.5rem !important;
  letter-spacing: 0.12em !important;
  background: linear-gradient(135deg, #ffffff 0%, var(--gold) 60%, #e8b400 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1 !important;
  margin: 0 !important;
}
.site-tagline {
  color: var(--text2);
  font-size: 0.9rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 0.4rem;
}

/* ═══════════════════════════════════════
   SECTION HEADINGS
═══════════════════════════════════════ */
.section-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 2rem 0 1rem 0;
}
.section-heading .line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border2), transparent);
}
.section-heading h2 {
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 1.6rem !important;
  letter-spacing: 0.1em !important;
  color: var(--text) !important;
  margin: 0 !important;
  white-space: nowrap;
}
.section-heading .dot {
  width: 6px; height: 6px;
  background: var(--gold);
  border-radius: 50%;
  flex-shrink: 0;
}

/* ═══════════════════════════════════════
   SEARCH BAR WRAPPER
═══════════════════════════════════════ */
.search-wrapper {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 16px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1.5rem;
  position: relative;
}
.search-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text2);
  margin-bottom: 0.5rem;
}

/* ═══════════════════════════════════════
   POSTER CARDS WITH HOVER OVERLAY
═══════════════════════════════════════ */
.movie-card-wrap {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: var(--surface);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  cursor: pointer;
  margin-bottom: 4px;
  aspect-ratio: 2/3;
}
.movie-card-wrap:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 16px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(245,197,24,0.3);
}
.movie-card-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.movie-card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    transparent 40%,
    rgba(0,0,0,0.5) 65%,
    rgba(0,0,0,0.92) 100%
  );
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 12px 10px;
  opacity: 0;
  transition: opacity 0.25s ease;
}
.movie-card-wrap:hover .movie-card-overlay { opacity: 1; }
.card-title {
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
  line-height: 1.25;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-rating {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(245,197,24,0.9);
  color: #000;
  font-weight: 700;
  font-size: 0.7rem;
  padding: 2px 7px;
  border-radius: 4px;
  width: fit-content;
}
.card-year {
  font-size: 0.72rem;
  color: rgba(255,255,255,0.6);
  margin-top: 3px;
}

/* No-poster placeholder */
.no-poster {
  aspect-ratio: 2/3;
  background: linear-gradient(135deg, var(--surface), var(--surface2));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text3);
  font-size: 2rem;
  border: 1px solid var(--border);
}

/* Movie title below card (fallback / always visible) */
.card-label {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text2);
  line-height: 1.3;
  height: 2.2em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-top: 6px;
}

/* ═══════════════════════════════════════
   DETAILS PAGE
═══════════════════════════════════════ */
.details-hero {
  background: linear-gradient(135deg, var(--surface) 0%, var(--bg3) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2rem;
  margin-bottom: 1.5rem;
}
.details-poster img {
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.7);
  width: 100%;
}
.details-title {
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 3rem !important;
  letter-spacing: 0.06em !important;
  color: #fff !important;
  line-height: 1.05 !important;
  margin: 0 0 0.4rem 0 !important;
}
.details-year {
  font-size: 1.1rem;
  color: var(--gold);
  font-weight: 600;
  letter-spacing: 0.04em;
}
.genre-pill {
  display: inline-block;
  background: rgba(245,197,24,0.1);
  border: 1px solid rgba(245,197,24,0.25);
  color: var(--gold);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 99px;
  margin: 3px 3px 3px 0;
  display: inline-block;
}
.details-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0.75rem 0;
  align-items: center;
}
.meta-pill {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text2);
  font-size: 0.75rem;
  padding: 4px 12px;
  border-radius: 99px;
}
.plot-text {
  font-family: 'Crimson Pro', Georgia, serif !important;
  font-size: 1.05rem !important;
  line-height: 1.75 !important;
  color: #c8cdd8 !important;
  margin-top: 1rem !important;
}

/* ═══════════════════════════════════════
   OMDB RATINGS BLOCK
═══════════════════════════════════════ */
.omdb-wrap {
  background: linear-gradient(145deg, #0a0f18, #111a26);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-lg);
  padding: 1.75rem 2rem;
  margin-top: 1.5rem;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 8px 32px rgba(0,0,0,0.4);
}
.omdb-heading {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.1rem;
  letter-spacing: 0.12em;
  color: var(--text2);
  text-transform: uppercase;
  margin-bottom: 1.2rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}
.ratings-flex { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 1.25rem; }
.rating-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
  position: relative;
  overflow: hidden;
}
.rating-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.rating-card.imdb::before  { background: linear-gradient(90deg, var(--gold), transparent); }
.rating-card.rt::before    { background: linear-gradient(90deg, var(--rt), transparent); }
.rating-card.meta::before  { background: linear-gradient(90deg, var(--meta), transparent); }
.r-source {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  margin-bottom: 8px;
}
.r-value { font-size: 1.8rem; font-weight: 700; line-height: 1; }
.r-value.imdb  { color: var(--gold); }
.r-value.rt    { color: var(--rt); }
.r-value.meta  { color: var(--meta); }
.r-bar { margin-top: 8px; width: 80px; height: 4px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden; }
.r-bar-fill { height: 4px; border-radius: 99px; }
.votes-note { font-size: 0.72rem; color: var(--text3); margin-bottom: 1rem; }

/* Meta chips grid */
.chips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 1.25rem;
}
.info-chip {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 10px 14px;
}
.chip-label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  margin-bottom: 5px;
}
.chip-value { font-size: 0.9rem; font-weight: 600; color: var(--text); }

/* People section */
.people-section { margin-bottom: 1rem; }
.people-key {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  margin-bottom: 5px;
}
.people-val { font-size: 0.9rem; color: #c8cdd8; line-height: 1.5; }

/* Awards */
.awards-bar {
  margin-top: 1rem;
  background: linear-gradient(90deg, rgba(245,197,24,0.06), transparent);
  border-left: 3px solid var(--gold);
  border-radius: 0 10px 10px 0;
  padding: 10px 16px;
  font-size: 0.88rem;
  color: #c8cdd8;
}
.awards-bar strong { color: var(--gold); }

/* ═══════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════ */
.sidebar-logo {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.8rem;
  letter-spacing: 0.12em;
  background: linear-gradient(135deg, #fff, var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.2rem;
}
.sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: 1rem 0;
}
.sidebar-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  margin-bottom: 0.6rem;
}

/* ═══════════════════════════════════════
   STAT STRIP (details page)
═══════════════════════════════════════ */
.stat-strip {
  display: flex;
  gap: 1px;
  background: var(--border);
  border-radius: 12px;
  overflow: hidden;
  margin: 1rem 0;
}
.stat-item {
  flex: 1;
  background: var(--surface);
  padding: 12px 8px;
  text-align: center;
}
.stat-val { font-size: 1.1rem; font-weight: 700; color: var(--text); }
.stat-key { font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text3); margin-top: 3px; }

/* ═══════════════════════════════════════
   BACK BUTTON (details page)
═══════════════════════════════════════ */
.back-btn-wrap [data-testid="stButton"] > button {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text2) !important;
  font-size: 0.82rem !important;
  padding: 0.4rem 1rem !important;
  width: auto !important;
  border-radius: 99px !important;
}
.back-btn-wrap [data-testid="stButton"] > button:hover {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ═══════════════════════════════════════
   INFO / ERROR / WARNING
═══════════════════════════════════════ */
[data-testid="stAlert"] {
  background: var(--surface) !important;
  border-radius: 12px !important;
  border-left-color: var(--gold) !important;
  color: var(--text) !important;
}

/* spinner */
[data-testid="stSpinner"] { color: var(--gold) !important; }

/* Caption */
[data-testid="stCaptionContainer"] { color: var(--text3) !important; font-size: 0.8rem !important; }

/* Markdown headings */
h1, h2, h3, h4 { color: var(--text) !important; }

</style>
""", unsafe_allow_html=True)

# sidebar icon fix using streamlit-js-eval
# pip install streamlit-js-eval
try:
    from streamlit_js_eval import streamlit_js_eval
    streamlit_js_eval(js_expressions="""
      (function() {
        function fix() {
          document.querySelectorAll('.material-symbols-rounded').forEach(function(el) {
            var t = el.innerText || el.textContent;
            if (t && (t.indexOf('arrow') > -1 || t.indexOf('chevron') > -1)) {
              el.innerText = '';
              el.style.cssText = 'width:14px;height:14px;display:inline-block;border-right:2.5px solid #f5c518;border-top:2.5px solid #f5c518;transform:rotate(45deg);margin:4px;';
            }
          });
        }
        fix();
        new MutationObserver(fix).observe(document.body, {childList:true,subtree:true});
      })()
    """, key="icon_fix", want_output=False)
except ImportError:
    pass  # streamlit-js-eval not installed — sidebar icon will show default

# =============================
# STATE + ROUTING
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id   = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


# =============================
# OMDB HELPERS
# =============================
@st.cache_data(ttl=3600)
def fetch_omdb_by_title(title: str, year: str = "") -> dict | None:
    if not OMDB_API_KEY or OMDB_API_KEY == "YOUR_OMDB_API_KEY_HERE":
        return None
    params = {"apikey": OMDB_API_KEY, "t": title, "type": "movie", "plot": "full"}
    if year:
        params["y"] = year
    try:
        r = requests.get(OMDB_BASE, params=params, timeout=10)
        data = r.json()
        return data if data.get("Response") == "True" else None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_omdb_by_imdbid(imdb_id: str) -> dict | None:
    if not OMDB_API_KEY or OMDB_API_KEY == "YOUR_OMDB_API_KEY_HERE":
        return None
    try:
        r = requests.get(OMDB_BASE, params={"apikey": OMDB_API_KEY, "i": imdb_id, "plot": "full"}, timeout=10)
        data = r.json()
        return data if data.get("Response") == "True" else None
    except Exception:
        return None


def _rating_type(source: str) -> str:
    s = source.lower()
    if "internet movie" in s or "imdb" in s: return "imdb"
    if "rotten" in s: return "rt"
    if "metacritic" in s: return "meta"
    return "imdb"


def _bar_color(t: str) -> str:
    return {"imdb": "#f5c518", "rt": "#fa320a", "meta": "#54b3f5"}.get(t, "#f5c518")


def _normalize(val: str) -> float | None:
    try:
        v = val.strip()
        if "%" in v:   return float(v.replace("%", ""))
        if "/" in v:
            n, d = v.split("/")
            return float(n) / float(d) * 100
        return None
    except: return None


def na(v) -> str | None:
    if not v or str(v).strip() in ("N/A", "", "nan", "None"): return None
    return str(v).strip()


def render_omdb_section(omdb: dict):
    ratings   = omdb.get("Ratings", [])
    director  = na(omdb.get("Director"))
    actors    = na(omdb.get("Actors"))
    writer    = na(omdb.get("Writer"))
    runtime   = na(omdb.get("Runtime"))
    language  = na(omdb.get("Language"))
    country   = na(omdb.get("Country"))
    box_office= na(omdb.get("BoxOffice"))
    rated     = na(omdb.get("Rated"))
    awards    = na(omdb.get("Awards"))
    votes     = na(omdb.get("imdbVotes"))
    metascore = na(omdb.get("Metascore"))
    production= na(omdb.get("Production"))
    website   = na(omdb.get("Website"))

    html = "<div class='omdb-wrap'>"
    html += "<div class='omdb-heading'>⬡&nbsp; Ratings &amp; Full Details</div>"

    # Ratings
    if ratings:
        html += "<div class='ratings-flex'>"
        for r in ratings:
            src  = r.get("Source", "")
            val  = r.get("Value", "")
            t    = _rating_type(src)
            sc   = _normalize(val)
            short = src.replace("Internet Movie Database","IMDb").replace("Rotten Tomatoes","Rotten Tomatoes")
            bar  = f"<div class='r-bar'><div class='r-bar-fill' style='width:{sc:.0f}%;background:{_bar_color(t)};'></div></div>" if sc is not None else ""
            html += f"""<div class='rating-card {t}'>
                <div class='r-source'>{short}</div>
                <div class='r-value {t}'>{val}</div>
                {bar}
            </div>"""
        html += "</div>"

    if votes:
        html += f"<div class='votes-note'>⭐ {votes} IMDb votes</div>"

    # Meta chips
    chips = [
        ("Runtime",    runtime),
        ("Rated",      rated),
        ("Language",   language),
        ("Country",    country),
        ("Box Office", box_office),
        ("Production", production),
    ]
    if metascore:
        chips.append(("Metascore", f"{metascore}/100"))

    valid = [(l, v) for l, v in chips if v]
    if valid:
        html += "<div class='chips-grid'>"
        for label, value in valid:
            html += f"<div class='info-chip'><div class='chip-label'>{label}</div><div class='chip-value'>{value}</div></div>"
        html += "</div>"

    # People
    html += "<div class='people-section'>"
    for key, val in [("Director", director), ("Writer", writer), ("Cast", actors)]:
        if val:
            html += f"<div style='margin-bottom:0.85rem;'><div class='people-key'>{key}</div><div class='people-val'>{val}</div></div>"
    html += "</div>"

    # Awards
    if awards and awards.lower() not in ("n/a", ""):
        html += f"<div class='awards-bar'>🏆 <strong>Awards</strong> &nbsp;·&nbsp; {awards}</div>"

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# =============================
# POSTER GRID
# =============================
def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.markdown("<div style='color:var(--text3);padding:2rem;text-align:center;'>No movies to show.</div>", unsafe_allow_html=True)
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols, gap="small")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]; idx += 1
            tmdb_id = m.get("tmdb_id")
            title   = m.get("title", "Untitled")
            poster  = m.get("poster_url")
            rating  = m.get("imdb_rating") or m.get("vote_average") or ""
            year    = m.get("year", "") or (m.get("release_date") or "")[:4]

            with colset[c]:
                if poster:
                    rating_html = f"<div class='card-rating'>⭐ {rating}</div>" if rating else ""
                    year_html   = f"<div class='card-year'>{year}</div>" if year else ""
                    st.markdown(f"""
                    <div class='movie-card-wrap'>
                        <img src='{poster}' loading='lazy' />
                        <div class='movie-card-overlay'>
                            <div class='card-title'>{title}</div>
                            {rating_html}
                            {year_html}
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='no-poster'>🎬</div>", unsafe_allow_html=True)

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(f"<div class='card-label'>{title}</div>", unsafe_allow_html=True)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append({
                "tmdb_id":   tmdb["tmdb_id"],
                "title":     tmdb.get("title") or x.get("title") or "Untitled",
                "poster_url":tmdb.get("poster_url"),
            })
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()
    if isinstance(data, dict) and "results" in data:
        raw_items = []
        for m in (data.get("results") or []):
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id: continue
            raw_items.append({"tmdb_id": int(tmdb_id), "title": title,
                "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                "release_date": m.get("release_date", "")})
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title   = (m.get("title") or "").strip()
            if not title or not tmdb_id: continue
            raw_items.append({"tmdb_id": int(tmdb_id), "title": title,
                "poster_url": m.get("poster_url"), "release_date": m.get("release_date", "")})
    else:
        return [], []

    matched    = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items
    suggestions = []
    for x in final_list[:10]:
        year  = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))
    cards = [{"tmdb_id": x["tmdb_id"], "title": x["title"],
              "poster_url": x["poster_url"], "year": (x.get("release_date") or "")[:4]}
             for x in final_list[:limit]]
    return suggestions, cards


# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>CineMatch</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:var(--text3);font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:1rem;'>Movie Recommender</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    if st.button("🏠  Home"):
        goto_home()

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>Home Feed Category</div>", unsafe_allow_html=True)
    home_category = st.selectbox(
        "Home Feed Category", ["trending", "popular", "top_rated", "now_playing", "upcoming"], index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div class='sidebar-label' style='margin-top:1rem;'>Grid Columns</div>", unsafe_allow_html=True)
    grid_cols = st.slider("Grid Columns", 4, 8, 6, label_visibility="collapsed")

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>🔑 OMDB API Key</div>", unsafe_allow_html=True)
    user_key = st.text_input("OMDB API Key", type="password", placeholder="omdbapi.com free key", label_visibility="collapsed")
    if user_key:
        OMDB_API_KEY = user_key
    st.markdown("<div style='font-size:0.7rem;color:var(--text3);margin-top:4px;'>For IMDb/RT ratings on details page</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# SITE HEADER
# ══════════════════════════════════════════
st.markdown("""
<div class='site-header'>
  <div class='site-title'>CineMatch</div>
  <div class='site-tagline'>Discover · Explore · Recommend</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# VIEW: HOME
# ══════════════════════════════════════════
if st.session_state.view == "home":

    # Search bar
    st.markdown("<div class='search-label'>🔍 &nbsp;Search by movie title</div>", unsafe_allow_html=True)
    typed = st.text_input("Search movie", placeholder="e.g.  Inception,  The Dark Knight,  Interstellar...",
                          label_visibility="collapsed")

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters.")
        else:
            with st.spinner("Searching..."):
                data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)

                if suggestions:
                    labels   = ["— select a movie —"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Quick select", labels, index=0, label_visibility="collapsed")
                    if selected != "— select a movie —":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No results found — try a different keyword.")

                st.markdown(f"""<div class='section-heading'>
                    <div class='dot'></div>
                    <h2>SEARCH RESULTS</h2>
                    <div class='line'></div>
                </div>""", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search")
        st.stop()

    # Home feed
    cat_display = home_category.replace("_", " ").upper()
    st.markdown(f"""<div class='section-heading'>
        <div class='dot'></div>
        <h2>{cat_display}</h2>
        <div class='line'></div>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Loading..."):
        home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})

    if err or not home_cards:
        st.error(f"Feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")


# ══════════════════════════════════════════
# VIEW: DETAILS
# ══════════════════════════════════════════
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Back button
    st.markdown("<div class='back-btn-wrap'>", unsafe_allow_html=True)
    if st.button("← Back"):
        goto_home()
    st.markdown("</div>", unsafe_allow_html=True)

    with st.spinner("Loading movie..."):
        data, err = api_get_json(f"/movie/id/{tmdb_id}")

    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    title   = data.get("title", "")
    release = data.get("release_date") or ""
    year    = release[:4]
    overview= data.get("overview") or "No overview available."
    genres_raw = data.get("genres", [])
    genres  = genres_raw if isinstance(genres_raw, list) else []
    vote    = na(str(data.get("vote_average", "")))
    runtime = na(str(data.get("runtime", "")))
    lang    = na(data.get("original_language", ""))
    status  = na(data.get("status", ""))
    budget  = data.get("budget")
    revenue = data.get("revenue")
    imdb_id = data.get("imdb_id") or ""
    poster  = data.get("poster_url")
    backdrop= data.get("backdrop_url")

    # ── Hero layout ──
    st.markdown("<div class='details-hero'>", unsafe_allow_html=True)
    left, right = st.columns([1, 2.6], gap="large")

    with left:
        if poster:
            st.markdown(f"<div class='details-poster'><img src='{poster}' /></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='no-poster' style='aspect-ratio:2/3;border-radius:14px;font-size:3rem;'>🎬</div>", unsafe_allow_html=True)

    with right:
        # Title + year
        st.markdown(f"<div class='details-title'>{title}</div>", unsafe_allow_html=True)
        if year:
            st.markdown(f"<div class='details-year'>{year}</div>", unsafe_allow_html=True)

        # Genre pills
        if genres:
            genre_html = "".join([
                f"<span class='genre-pill'>{g['name'] if isinstance(g, dict) else g}</span>"
                for g in genres
            ])
            st.markdown(f"<div style='margin:0.75rem 0;'>{genre_html}</div>", unsafe_allow_html=True)

        # Stat strip
        stats = []
        if vote:          stats.append((vote, "Rating"))
        if runtime:       stats.append((f"{runtime} min", "Runtime"))
        if lang:          stats.append((lang.upper(), "Language"))
        if status:        stats.append((status, "Status"))
        if budget and int(budget or 0) > 0:
            stats.append((f"${int(budget):,}", "Budget"))
        if revenue and int(revenue or 0) > 0:
            stats.append((f"${int(revenue):,}", "Revenue"))

        if stats:
            strip = "".join([
                f"<div class='stat-item'><div class='stat-val'>{v}</div><div class='stat-key'>{k}</div></div>"
                for v, k in stats
            ])
            st.markdown(f"<div class='stat-strip'>{strip}</div>", unsafe_allow_html=True)

        # Plot
        st.markdown(f"<div class='plot-text'>{overview}</div>", unsafe_allow_html=True)

        # OMDB section
        omdb_data = None
        if imdb_id:
            omdb_data = fetch_omdb_by_imdbid(imdb_id)
        if not omdb_data and title:
            omdb_data = fetch_omdb_by_title(title, year)

        if omdb_data:
            render_omdb_section(omdb_data)
        elif OMDB_API_KEY == "YOUR_OMDB_API_KEY_HERE":
            st.markdown("<div style='color:var(--text3);font-size:0.82rem;margin-top:1rem;'>💡 Add OMDB key in sidebar to see ratings, director, cast & awards.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close details-hero

    # Backdrop
    if backdrop:
        st.markdown("<div style='border-radius:16px;overflow:hidden;margin-bottom:1.5rem;'>", unsafe_allow_html=True)
        st.image(backdrop, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Recommendations ──
    if title:
        with st.spinner("Finding similar movies..."):
            bundle, err2 = api_get_json("/movie/search", params={"query": title, "tfidf_top_n": 12, "genre_limit": 12})

        if not err2 and bundle:
            tfidf_cards = to_cards_from_tfidf_items(bundle.get("tfidf_recommendations"))
            genre_cards = bundle.get("genre_recommendations", [])

            if tfidf_cards:
                st.markdown("""<div class='section-heading'>
                    <div class='dot'></div><h2>SIMILAR MOVIES</h2><div class='line'></div>
                </div>""", unsafe_allow_html=True)
                poster_grid(tfidf_cards, cols=grid_cols, key_prefix="tfidf")

            if genre_cards:
                st.markdown("""<div class='section-heading'>
                    <div class='dot'></div><h2>MORE LIKE THIS</h2><div class='line'></div>
                </div>""", unsafe_allow_html=True)
                poster_grid(genre_cards, cols=grid_cols, key_prefix="genre")

        else:
            with st.spinner("Fetching genre recommendations..."):
                genre_only, err3 = api_get_json("/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18})
            if not err3 and genre_only:
                st.markdown("""<div class='section-heading'>
                    <div class='dot'></div><h2>MORE LIKE THIS</h2><div class='line'></div>
                </div>""", unsafe_allow_html=True)
                poster_grid(genre_only, cols=grid_cols, key_prefix="genre_fallback")
            else:
                st.info("No recommendations available right now.")
