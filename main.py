import os
import pickle
import traceback
from typing import Optional, List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


# =========================
# ENV
# =========================
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")   # Add TMDB_API_KEY in your .env
OMDB_BASE    = "http://www.omdbapi.com/"
TMDB_BASE    = "https://api.themoviedb.org/3"
TMDB_IMG     = "https://image.tmdb.org/t/p/w500"

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="Movie Recommender API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# PICKLE GLOBALS
# =========================
BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
DF_PATH           = os.path.join(BASE_DIR, "df.pkl")
INDICES_PATH      = os.path.join(BASE_DIR, "indices.pkl")
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")
TFIDF_PATH        = os.path.join(BASE_DIR, "tfidf.pkl")

df:           Optional[pd.DataFrame] = None
indices_obj:  Any                    = None
tfidf_matrix: Any                    = None
tfidf_obj:    Any                    = None
TITLE_TO_IDX: Optional[Dict[str, int]] = None


# =========================
# PYDANTIC MODELS
# =========================
class MovieCard(BaseModel):
    tmdb_id:      Optional[int]  = None
    imdb_id:      str            = ""
    title:        str            = "Untitled"
    year:         Optional[str]  = None
    poster_url:   Optional[str]  = None
    backdrop_url: Optional[str]  = None
    imdb_rating:  Optional[str]  = None
    vote_average: Optional[float]= None
    genre:        Optional[str]  = None
    release_date: Optional[str]  = None


class MovieDetails(BaseModel):
    tmdb_id:      Optional[int]  = None
    imdb_id:      str            = ""
    title:        str            = ""
    year:         Optional[str]  = None
    rated:        Optional[str]  = None
    released:     Optional[str]  = None
    runtime:      Optional[str]  = None
    genre:        Optional[str]  = None
    genres:       Optional[List[Dict]] = None
    director:     Optional[str]  = None
    actors:       Optional[str]  = None
    plot:         Optional[str]  = None
    overview:     Optional[str]  = None
    poster_url:   Optional[str]  = None
    backdrop_url: Optional[str]  = None
    imdb_rating:  Optional[str]  = None
    vote_average: Optional[float]= None
    imdb_votes:   Optional[str]  = None
    box_office:   Optional[str]  = None
    language:     Optional[str]  = None
    original_language: Optional[str] = None
    country:      Optional[str]  = None
    awards:       Optional[str]  = None
    budget:       Optional[int]  = None
    revenue:      Optional[int]  = None
    status:       Optional[str]  = None
    release_date: Optional[str]  = None


class TFIDFRecItem(BaseModel):
    title:  str
    score:  float
    tmdb:   Optional[MovieCard] = None
    omdb:   Optional[MovieCard] = None


class SearchBundleResponse(BaseModel):
    query:                str
    movie_details:        MovieDetails
    tfidf_recommendations: List[TFIDFRecItem]
    genre_recommendations: List[MovieCard] = []


# =========================
# UTILS
# =========================
def _norm_title(t: str) -> str:
    return str(t).strip().lower()


def fix_poster(url: Optional[str]) -> Optional[str]:
    if not url or url == "N/A":
        return None
    return url


def na_to_none(val: Any) -> Optional[str]:
    if val is None or str(val).strip() in ("N/A", "", "nan", "None"):
        return None
    return str(val)


# =========================
# TMDB HELPERS
# =========================
async def tmdb_get(path: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    if not TMDB_API_KEY:
        return {}
    p = {"api_key": TMDB_API_KEY, "language": "en-US", **params}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f"{TMDB_BASE}{path}", params=p)
        if r.status_code != 200:
            return {}
        return r.json()
    except Exception as e:
        print(f"[TMDB ERROR] {path}: {e}")
        return {}


def tmdb_movie_to_card(m: dict) -> MovieCard:
    poster   = f"{TMDB_IMG}{m['poster_path']}"   if m.get("poster_path")   else None
    backdrop = f"{TMDB_IMG}{m['backdrop_path']}" if m.get("backdrop_path") else None
    return MovieCard(
        tmdb_id      = m.get("id"),
        imdb_id      = m.get("imdb_id", ""),
        title        = m.get("title") or m.get("name") or "Untitled",
        year         = (m.get("release_date") or "")[:4] or None,
        release_date = m.get("release_date"),
        poster_url   = poster,
        backdrop_url = backdrop,
        vote_average = m.get("vote_average"),
        genre        = ", ".join([g["name"] for g in m.get("genres", [])]) if m.get("genres") else None,
    )


def tmdb_movie_to_details(m: dict) -> MovieDetails:
    poster   = f"{TMDB_IMG}{m['poster_path']}"   if m.get("poster_path")   else None
    backdrop = f"{TMDB_IMG}{m['backdrop_path']}" if m.get("backdrop_path") else None
    return MovieDetails(
        tmdb_id           = m.get("id"),
        imdb_id           = m.get("imdb_id", ""),
        title             = m.get("title", ""),
        release_date      = m.get("release_date"),
        year              = (m.get("release_date") or "")[:4] or None,
        overview          = na_to_none(m.get("overview")),
        plot              = na_to_none(m.get("overview")),
        poster_url        = poster,
        backdrop_url      = backdrop,
        vote_average      = m.get("vote_average"),
        genres            = m.get("genres", []),
        genre             = ", ".join([g["name"] for g in m.get("genres", [])]),
        runtime           = str(m["runtime"]) if m.get("runtime") else None,
        status            = m.get("status"),
        original_language = m.get("original_language"),
        budget            = m.get("budget") or None,
        revenue           = m.get("revenue") or None,
    )


async def tmdb_search_movie(query: str, page: int = 1) -> List[dict]:
    data = await tmdb_get("/search/movie", {"query": query, "page": page})
    return data.get("results", [])


async def tmdb_movie_details(tmdb_id: int) -> Optional[dict]:
    data = await tmdb_get(f"/movie/{tmdb_id}", {"append_to_response": "external_ids"})
    if not data or data.get("success") is False:
        return None
    # Attach imdb_id from external_ids if present
    ext = data.get("external_ids", {})
    if ext.get("imdb_id"):
        data["imdb_id"] = ext["imdb_id"]
    return data


async def tmdb_category_movies(category: str, page: int = 1) -> List[dict]:
    """
    category: trending | popular | top_rated | now_playing | upcoming
    """
    if category == "trending":
        data = await tmdb_get("/trending/movie/week", {"page": page})
    elif category in ("popular", "top_rated", "now_playing", "upcoming"):
        data = await tmdb_get(f"/movie/{category}", {"page": page})
    else:
        data = await tmdb_get("/movie/popular", {"page": page})
    return data.get("results", [])


async def tmdb_similar(tmdb_id: int, limit: int = 12) -> List[MovieCard]:
    data = await tmdb_get(f"/movie/{tmdb_id}/similar")
    results = data.get("results", [])[:limit]
    return [tmdb_movie_to_card(m) for m in results]


async def tmdb_by_genre(genre_ids: List[int], limit: int = 12) -> List[MovieCard]:
    ids_str = ",".join(str(g) for g in genre_ids)
    data = await tmdb_get("/discover/movie", {
        "with_genres": ids_str,
        "sort_by": "popularity.desc",
    })
    results = data.get("results", [])[:limit]
    return [tmdb_movie_to_card(m) for m in results]


# =========================
# OMDB HELPERS
# =========================
async def omdb_get(params: Dict[str, Any]) -> Dict[str, Any]:
    if not OMDB_API_KEY:
        return {"Response": "False", "Error": "No OMDB key"}
    q = dict(params)
    q["apikey"] = OMDB_API_KEY
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(OMDB_BASE, params=q)
        if r.status_code != 200:
            return {"Response": "False", "Error": f"HTTP {r.status_code}"}
        return r.json()
    except Exception as e:
        return {"Response": "False", "Error": str(e)}


async def omdb_details_by_title(title: str) -> Optional[Dict[str, Any]]:
    data = await omdb_get({"t": title, "type": "movie", "plot": "full"})
    return data if data.get("Response") == "True" else None


async def omdb_details_by_id(imdb_id: str) -> Optional[Dict[str, Any]]:
    data = await omdb_get({"i": imdb_id, "plot": "full"})
    return data if data.get("Response") == "True" else None


def omdb_to_card(m: dict) -> MovieCard:
    return MovieCard(
        imdb_id    = m.get("imdbID", ""),
        title      = m.get("Title", "Untitled"),
        year       = na_to_none(m.get("Year")),
        poster_url = fix_poster(m.get("Poster")),
        imdb_rating= na_to_none(m.get("imdbRating")),
        genre      = na_to_none(m.get("Genre")),
    )


def omdb_to_details(m: dict) -> MovieDetails:
    return MovieDetails(
        imdb_id    = m.get("imdbID", ""),
        title      = m.get("Title", ""),
        year       = na_to_none(m.get("Year")),
        rated      = na_to_none(m.get("Rated")),
        released   = na_to_none(m.get("Released")),
        runtime    = na_to_none(m.get("Runtime")),
        genre      = na_to_none(m.get("Genre")),
        director   = na_to_none(m.get("Director")),
        actors     = na_to_none(m.get("Actors")),
        plot       = na_to_none(m.get("Plot")),
        overview   = na_to_none(m.get("Plot")),
        poster_url = fix_poster(m.get("Poster")),
        imdb_rating= na_to_none(m.get("imdbRating")),
        imdb_votes = na_to_none(m.get("imdbVotes")),
        box_office = na_to_none(m.get("BoxOffice")),
        language   = na_to_none(m.get("Language")),
        country    = na_to_none(m.get("Country")),
        awards     = na_to_none(m.get("Awards")),
    )


# =========================
# TF-IDF HELPERS
# =========================
def build_title_to_idx_map(indices: Any) -> Dict[str, int]:
    title_to_idx: Dict[str, int] = {}
    try:
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
    except Exception:
        raise RuntimeError("indices.pkl must be dict or pandas Series-like")
    return title_to_idx


def get_local_idx_by_title(title: str) -> int:
    global TITLE_TO_IDX
    if TITLE_TO_IDX is None:
        raise HTTPException(status_code=500, detail="TF-IDF index map not initialized")
    key = _norm_title(title)
    if key in TITLE_TO_IDX:
        return int(TITLE_TO_IDX[key])
    raise HTTPException(status_code=404, detail=f"Title not found: '{title}'")


def tfidf_recommend_titles(query_title: str, top_n: int = 10) -> List[Tuple[str, float]]:
    global df, tfidf_matrix
    if df is None or tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="TF-IDF resources not loaded")

    idx    = get_local_idx_by_title(query_title)
    qv     = tfidf_matrix[idx]
    scores = (tfidf_matrix @ qv.T).toarray().ravel()
    order  = np.argsort(-scores)

    out: List[Tuple[str, float]] = []
    for i in order:
        if int(i) == int(idx):
            continue
        try:
            title_i = str(df.iloc[int(i)]["title"])
        except Exception:
            continue
        out.append((title_i, float(scores[int(i)])))
        if len(out) >= top_n:
            break
    return out


# =========================
# STARTUP: LOAD PICKLES
# =========================
@app.on_event("startup")
def load_pickles():
    global df, indices_obj, tfidf_matrix, tfidf_obj, TITLE_TO_IDX
    print("[STARTUP] Loading pickle files...")

    with open(DF_PATH,           "rb") as f: df           = pickle.load(f)
    with open(INDICES_PATH,      "rb") as f: indices_obj  = pickle.load(f)
    with open(TFIDF_MATRIX_PATH, "rb") as f: tfidf_matrix = pickle.load(f)
    with open(TFIDF_PATH,        "rb") as f: tfidf_obj    = pickle.load(f)

    TITLE_TO_IDX = build_title_to_idx_map(indices_obj)

    print(f"[STARTUP] df={df.shape}, titles={len(TITLE_TO_IDX)}, tfidf={tfidf_matrix.shape}")

    if df is None or "title" not in df.columns:
        raise RuntimeError("df.pkl must contain a DataFrame with a 'title' column")

    if not TMDB_API_KEY:
        print("[STARTUP] WARNING: TMDB_API_KEY not set — posters/home feed will be empty!")
    if not OMDB_API_KEY:
        print("[STARTUP] WARNING: OMDB_API_KEY not set — ratings/details fallback disabled")

    print("[STARTUP] All loaded successfully!")


# =========================
# ROUTES
# =========================

@app.get("/health")
def health():
    return {
        "status":        "ok",
        "titles_loaded": len(TITLE_TO_IDX) if TITLE_TO_IDX else 0,
        "tmdb_key":      bool(TMDB_API_KEY),
        "omdb_key":      bool(OMDB_API_KEY),
    }


# ── HOME FEED (TMDB — with posters!) ──────────────────────────────────────────
@app.get("/home", response_model=List[MovieCard])
async def home(
    category: str = Query("trending", regex="^(trending|popular|top_rated|now_playing|upcoming)$"),
    limit:    int = Query(24, ge=1, le=50),
):
    """
    Home feed from TMDB — returns real posters.
    category: trending | popular | top_rated | now_playing | upcoming
    """
    if not TMDB_API_KEY:
        # Fallback: return titles from local df (no posters)
        global df
        if df is None:
            raise HTTPException(status_code=500, detail="No data source available")
        cards = []
        for _, row in df.head(limit).iterrows():
            title = str(row.get("title", "")).strip()
            if not title or title == "nan":
                continue
            cards.append(MovieCard(title=title))
        return cards

    results = await tmdb_category_movies(category, page=1)
    cards   = [tmdb_movie_to_card(m) for m in results[:limit]]
    return cards


# ── TMDB SEARCH ───────────────────────────────────────────────────────────────
@app.get("/tmdb/search")
async def tmdb_search_route(
    query: str = Query(..., min_length=1),
    page:  int = Query(1, ge=1, le=10),
):
    """Search movies via TMDB — returns posters."""
    results = await tmdb_search_movie(query, page=page)
    cards   = [tmdb_movie_to_card(m) for m in results]
    return {"results": [c.model_dump() for c in cards], "total": len(cards)}


# ── TMDB MOVIE DETAILS BY TMDB ID ─────────────────────────────────────────────
@app.get("/movie/id/{tmdb_id}", response_model=MovieDetails)
async def movie_details_by_tmdb_id(tmdb_id: int):
    """
    Get full movie details by TMDB ID.
    Also fetches OMDB data (ratings/awards) if imdb_id is available.
    """
    data = await tmdb_movie_details(tmdb_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Movie not found: tmdb_id={tmdb_id}")

    details = tmdb_movie_to_details(data)

    # Enrich with OMDB if we have imdb_id
    if details.imdb_id and OMDB_API_KEY:
        omdb = await omdb_details_by_id(details.imdb_id)
        if omdb:
            details.imdb_rating = na_to_none(omdb.get("imdbRating"))
            details.imdb_votes  = na_to_none(omdb.get("imdbVotes"))
            details.box_office  = na_to_none(omdb.get("BoxOffice"))
            details.director    = na_to_none(omdb.get("Director"))
            details.actors      = na_to_none(omdb.get("Actors"))
            details.awards      = na_to_none(omdb.get("Awards"))
            details.rated       = na_to_none(omdb.get("Rated"))
            details.country     = na_to_none(omdb.get("Country"))
            details.language    = na_to_none(omdb.get("Language"))
            if not details.plot:
                details.plot = na_to_none(omdb.get("Plot"))

    return details


# ── LEGACY: OMDB DETAILS BY IMDB ID ───────────────────────────────────────────
@app.get("/movie/imdb/{imdb_id}", response_model=MovieDetails)
async def movie_details_by_imdb_id(imdb_id: str):
    data = await omdb_details_by_id(imdb_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Movie not found: {imdb_id}")
    return omdb_to_details(data)


# ── TF-IDF RECOMMENDATIONS ────────────────────────────────────────────────────
@app.get("/recommend/tfidf")
async def recommend_tfidf(
    title: str = Query(..., min_length=1),
    top_n: int = Query(10, ge=1, le=50),
):
    recs = tfidf_recommend_titles(title, top_n=top_n)
    return [{"title": t, "score": s} for t, s in recs]


# ── GENRE RECOMMENDATIONS (TMDB) ──────────────────────────────────────────────
@app.get("/recommend/genre", response_model=List[MovieCard])
async def recommend_by_genre(
    tmdb_id: int = Query(...),
    limit:   int = Query(12, ge=1, le=30),
):
    """Get similar movies by genre using TMDB discover."""
    data = await tmdb_movie_details(tmdb_id)
    if not data:
        raise HTTPException(status_code=404, detail="Movie not found")

    genre_ids = [g["id"] for g in data.get("genres", [])]
    if not genre_ids:
        return []

    cards = await tmdb_by_genre(genre_ids, limit=limit)
    # Remove the movie itself
    cards = [c for c in cards if c.tmdb_id != tmdb_id]
    return cards[:limit]


# ── BUNDLE: Details + TF-IDF + Genre recs ─────────────────────────────────────
@app.get("/movie/search")
async def search_bundle(
    query:        str = Query(..., min_length=1),
    tfidf_top_n:  int = Query(12, ge=1, le=30),
    genre_limit:  int = Query(12, ge=1, le=30),
):
    """
    Full bundle:
    - Movie details (TMDB primary, OMDB enrichment)
    - TF-IDF content recommendations (with TMDB posters)
    - Genre-based recommendations (TMDB)
    """
    # 1. TMDB search to get tmdb_id
    tmdb_results = await tmdb_search_movie(query, page=1)
    tmdb_data    = tmdb_results[0] if tmdb_results else None
    tmdb_id      = tmdb_data["id"] if tmdb_data else None

    # 2. Full TMDB details
    details: MovieDetails
    if tmdb_id:
        full = await tmdb_movie_details(tmdb_id)
        details = tmdb_movie_to_details(full) if full else MovieDetails(title=query)
    else:
        details = MovieDetails(title=query)

    # 3. Enrich with OMDB
    if details.imdb_id and OMDB_API_KEY:
        omdb = await omdb_details_by_id(details.imdb_id)
        if omdb:
            details.imdb_rating = na_to_none(omdb.get("imdbRating"))
            details.imdb_votes  = na_to_none(omdb.get("imdbVotes"))
            details.box_office  = na_to_none(omdb.get("BoxOffice"))
            details.director    = na_to_none(omdb.get("Director"))
            details.actors      = na_to_none(omdb.get("Actors"))
            details.awards      = na_to_none(omdb.get("Awards"))
            details.rated       = na_to_none(omdb.get("Rated"))

    # 4. TF-IDF recs — fetch TMDB poster for each
    tfidf_items: List[TFIDFRecItem] = []
    recs: List[Tuple[str, float]]   = []
    try:
        recs = tfidf_recommend_titles(details.title, top_n=tfidf_top_n)
    except Exception:
        try:
            recs = tfidf_recommend_titles(query, top_n=tfidf_top_n)
        except Exception:
            recs = []

    for title, score in recs:
        tmdb_card: Optional[MovieCard] = None
        try:
            sr = await tmdb_search_movie(title, page=1)
            if sr:
                tmdb_card = tmdb_movie_to_card(sr[0])
        except Exception:
            pass
        tfidf_items.append(TFIDFRecItem(title=title, score=score, tmdb=tmdb_card))

    # 5. Genre recs from TMDB
    genre_cards: List[MovieCard] = []
    if tmdb_id:
        try:
            similar = await tmdb_similar(tmdb_id, limit=genre_limit)
            genre_cards = [c for c in similar if c.tmdb_id != tmdb_id]
        except Exception:
            pass

        if not genre_cards and tmdb_data:
            genre_ids = [g["id"] for g in (tmdb_data.get("genres") or [])]
            if not genre_ids and full:
                genre_ids = [g["id"] for g in (full.get("genres") or [])]
            if genre_ids:
                genre_cards = await tmdb_by_genre(genre_ids, limit=genre_limit)
                genre_cards = [c for c in genre_cards if c.tmdb_id != tmdb_id]

    return {
        "query":                 query,
        "movie_details":         details.model_dump(),
        "tfidf_recommendations": [i.model_dump() for i in tfidf_items],
        "genre_recommendations": [c.model_dump() for c in genre_cards[:genre_limit]],
    }


# ── DEBUG ──────────────────────────────────────────────────────────────────────
@app.get("/debug/df")
def debug_df():
    global df
    if df is None:
        return {"error": "df not loaded"}
    return {
        "shape":         list(df.shape),
        "columns":       df.columns.tolist(),
        "sample_titles": df["title"].head(10).tolist(),
    }