# 🎬 CineMatch — Movie Recommendation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

**A premium, full-stack movie recommendation system powered by TF-IDF content-based filtering, TMDB API, and OMDb API.**

[Features](#-features) · [Tech Stack](#-tech-stack) · [Setup](#-setup) · [API Endpoints](#-api-endpoints) · [Project Structure](#-project-structure)

</div>

---

## ✨ Features

- 🔍 **Smart Search** — Search movies by title with real-time TMDB results
- 🎯 **TF-IDF Recommendations** — Content-based filtering using TF-IDF vectorization and cosine similarity
- 🎭 **Genre-Based Suggestions** — Discover movies in similar genres
- 🎬 **Rich Movie Details** — Poster, backdrop, plot, ratings, cast, director, awards & more
- ⭐ **Multi-Source Ratings** — IMDb, Rotten Tomatoes, and Metacritic scores via OMDb
- 📊 **Visual Rating Bars** — Animated progress bars for each rating source
- 🏠 **Dynamic Home Feed** — Trending, Popular, Top Rated, Now Playing, Upcoming categories
- 🎨 **Premium Dark UI** — Cinematic design with glassmorphism, gold accents, and smooth animations
- 📱 **Responsive Grid** — Adjustable poster grid columns (4–8)
- 🔑 **OMDB Integration** — Optional API key for enhanced movie details

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python) with custom CSS |
| **Backend API** | FastAPI + Uvicorn |
| **ML Engine** | Scikit-Learn (TF-IDF Vectorizer + Cosine Similarity) |
| **Data** | Pandas, NumPy, SciPy |
| **Movie Data** | TMDB API (posters, details) + OMDb API (ratings, cast) |
| **Serialization** | Pickle (pre-computed TF-IDF matrix) |
| **HTTP Client** | HTTPX (async), Requests |

---

## 🚀 Setup

### Prerequisites

- Python 3.12+
- TMDB API Key (set as environment variable)
- OMDb API Key (optional, for enhanced ratings)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key_here
OMDB_API_KEY=your_omdb_api_key_here
```

Create `.streamlit/secrets.toml`:

```toml
OMDB_API_KEY = "your_omdb_api_key_here"
```

### 5. Run the Backend (FastAPI)

```bash
uvicorn main:app --reload --port 8000
```

### 6. Run the Frontend (Streamlit)

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` 🎉

---

## 📡 API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server health & loaded data status |

### Home Feed
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/home` | Home feed (trending, popular, top_rated, now_playing, upcoming) |

### Movie Details
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/movie/id/{tmdb_id}` | Get full movie details by TMDB ID |
| `GET` | `/movie/{title}` | Get movie details by title |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tmdb/search` | Search movies on TMDB |
| `GET` | `/movie/search` | Full search bundle (details + TF-IDF + genre recommendations) |

### Recommendations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/recommend/tfidf` | TF-IDF content-based recommendations |
| `GET` | `/recommend/genre` | Genre-based recommendations |

---

## 📁 Project Structure

```
Movie Recommendation System/
├── 📄 app.py                  # Streamlit frontend (premium UI)
├── 📄 main.py                 # FastAPI backend (API server)
├── 📓 movies.ipynb             # Jupyter notebook (data preprocessing & model training)
├── 📊 movies_metadata.csv      # Raw movie metadata dataset
├── 🔧 df.pkl                  # Preprocessed DataFrame (pickle)
├── 🔧 indices.pkl             # Title-to-index mapping (pickle)
├── 🔧 tfidf.pkl               # Trained TF-IDF vectorizer (pickle)
├── 🔧 tfidf_matrix.pkl        # Pre-computed TF-IDF matrix (pickle)
├── 📄 requirements.txt        # Python dependencies
├── 📄 pyproject.toml           # Project metadata
├── 📄 .env                    # Environment variables (API keys)
├── 📄 .gitignore              # Git ignore rules
├── 📁 .streamlit/
│   └── secrets.toml           # Streamlit secrets (OMDB key)
└── 📁 .venv/                  # Virtual environment (not tracked)
```

---

## 🧠 How It Works

### TF-IDF Content-Based Filtering

1. **Pre-processing**: Movie metadata (genres, keywords, overview, cast, crew) is combined into a single text feature
2. **Vectorization**: TF-IDF Vectorizer converts text into numerical feature vectors
3. **Similarity**: Cosine similarity between movie vectors identifies the most similar movies
4. **Ranking**: Results are sorted by similarity score and returned as recommendations

### Data Flow

```
User Search → Streamlit UI → FastAPI Backend → TF-IDF Engine → Cosine Similarity
                                    ↓                              ↓
                              TMDB API (posters)          Top-N Similar Movies
                              OMDb API (ratings)                   ↓
                                    ↓                    Enriched with TMDB data
                              Movie Details ←──────────── Final Recommendations
```

---

## 🌐 Deployment

The backend API is deployed on **Render**:

```
https://movie-rec-466x.onrender.com
```

To deploy the Streamlit frontend on **Streamlit Cloud**:

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and select `app.py`
4. Add `OMDB_API_KEY` in Streamlit Cloud secrets

---

## 📸 Screenshots

| Home Feed | Movie Details |
|-----------|---------------|
| Premium dark UI with poster grid | Full details with ratings & recommendations |

---

## 📝 License

This project is for educational/personal use.

---

<div align="center">

**Built with ❤️ by Manish**

⭐ Star this repo if you found it useful!

</div>
"# Movie-Recommendation-System-" 
