# 🏏 The 12th Man (AI Cricket Auditor)

**The 12th Man** is an enterprise-grade AI application that automates the settlement of fantasy cricket leagues. It combines **Computer Vision**, **Web Scraping**, and **Generative AI** to analyze results, calculate financial settlements, and generate sarcastic match reports.

Built as a showcase for the **Google Cloud AI Agent Development Kit (ADK)**, it demonstrates a "Hybrid AI" strategy by combining managed **Gemini 2.0** APIs with self-hosted **Gemma 2** open models on **Vertex AI**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Google Cloud](https://img.shields.io/badge/Platform-Google%20Cloud%20Vertex%20AI-yellow)

---

## 🏗️ Hybrid AI Architecture

This project implements a **Multi-Agent System** where distinct agents handle specific cognitive tasks. It separates "Heavy Reasoning" (Gemini) from "Creative Writing" (Gemma).

```mermaid
graph TD
    User([👤 User]) -->|Uploads Screenshot & URLs| UI[🖥️ Streamlit Frontend]
    UI -->|HTTP POST| API[⚙️ FastAPI Orchestrator]
    
    subgraph "Phase 1: Ingestion & Perception"
        API --> Vision[👁️ Vision Agent<br>(Gemini 2.0 Flash)]
        Vision -->|Player Mappings| Scraper[🕸️ Scraper Agent<br>(Playwright Stealth)]
        Scraper -->|Scores & Commentary| Auditor[🧮 Auditor Agent<br>(Settlement Logic)]
    end
    
    subgraph "Phase 2: Intelligence Layer (Google Cloud)"
        Auditor --> Analyst[📈 Analyst Agent<br>(Gemini 2.0 Reasoning)]
        Scraper --> Forecaster[🔮 Forecaster Agent<br>(Predictive Strategy)]
        Scraper --> Commentator[🎙️ Commentator Agent<br>(Self-Hosted Gemma 2)]
        
        Analyst <-->|Managed API| Gemini[☁️ Google Gemini API]
        Commentator <-->|Endpoint| Vertex[☁️ Vertex AI Model Garden]
    end
    
    Analyst -->|Insight| API
    Forecaster -->|Hot Pick| API
    Commentator -->|Sarcasm| API
    API -->|JSON Report| UI

```

---

## 🚀 The Agent Squad

| Agent | Role | Technology |
| --- | --- | --- |
| **👁️ Vision** | Extracts player names & codes from WhatsApp screenshots. | **Gemini 2.0 Flash** (Multimodal) |
| **🕸️ Scraper** | Fetches live scores & commentary text from ESPNcricinfo. | **Playwright** (Stealth Mode) |
| **🧮 Auditor** | Calculates winner, total pot, and payments `(Diff / 5)`. | **Python** (Core Logic) |
| **📈 Analyst** | Identifies the "MVP" and explains *why* the winner won. | **Gemini 2.0 Flash** (Reasoning) |
| **🎙️ Commentator** | Generates a sarcastic, roasting summary of the match. | **Gemma 2 (9B)** on **Vertex AI** |
| **🔮 Forecaster** | Predicts the "Hot Pick" player for the next round. | **Python** (Predictive Logic) |

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Managed AI:** Google Gen AI SDK (`google-genai`)
* **Infrastructure AI:** Google Vertex AI SDK (`google-cloud-aiplatform`)
* **Web Scraping:** Playwright, BeautifulSoup4
* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit, Pandas
* **Testing:** Pytest (Unit & Integration)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone [https://github.com/yourusername/the-12th-man.git](https://github.com/yourusername/the-12th-man.git)
cd the-12th-man

```

### 2. Set up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium

```

### 4. Google Cloud Configuration

Create a `.env` file in the root directory. You need both an API Key (for Gemini) and a Vertex AI Endpoint (for Gemma).

```bash
# --- Gemini 2.0 (Vision & Analyst) ---
GOOGLE_API_KEY="AIzaSy..."

# --- Vertex AI (Gemma 2 Commentator) ---
GOOGLE_PROJECT_ID="your-gcp-project-id"
GOOGLE_REGION="us-central1"
VERTEX_ENDPOINT_ID="1234567890..." 

```

> **Tip:** To get a `VERTEX_ENDPOINT_ID`, go to **Vertex AI Model Garden**, search for **Gemma 2**, and click "Deploy".

---

## 🏃‍♂️ Running the Application

This is a Client-Server application. You must run **two** separate terminals.

### Terminal 1: Backend (The Brain)

Starts the API server on `http://127.0.0.1:8000`.

```bash
uvicorn api:app --reload

```

### Terminal 2: Frontend (The Face)

Starts the UI on `http://localhost:8501`.

```bash
streamlit run app.py

```

---

## 🧪 Testing

The project includes a comprehensive test suite that verifies both logic and real-world API connectivity.

```bash
# Run all tests
pytest

# Test only the Web Scraper (opens browser)
pytest -k scraper

# Test connection to Google Gemini
pytest -k vision

# Test connection to Vertex AI (Gemma)
pytest -k commentator

```

## 📂 Project Structure

```
the-12th-man/
├── agents/             # 🧠 The Agent Ecosystem
│   ├── workflow.py     # Orchestrator (Pipeline Definition)
│   ├── vision.py       # Gemini 2.0 Vision
│   ├── scraper.py      # Dual-URL Scraper
│   ├── auditor.py      # Math Engine
│   ├── analyst.py      # Insight Generator
│   ├── commentator.py  # Vertex AI Gemma Connector
│   └── state.py        # Shared Data Schema
├── tests/              # 🧪 Test Suite
│   ├── test_agents.py  # Unit & Integration Tests
├── api.py              # ⚙️ FastAPI Backend
├── app.py              # 🖥️ Streamlit Frontend
├── requirements.txt    # Dependencies
└── .env                # Secrets

```

## 📝 License

MIT License

```

```
