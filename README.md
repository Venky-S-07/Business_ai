# 📊 InsightAI — Visual Business Intelligence

A conversational business intelligence app powered by **Google Gemini** and **Streamlit**. Upload a CSV dataset, ask questions in plain English, and get AI-generated charts and data summaries instantly.

---

## Features

- **Conversational data queries** — ask questions like *"What is the highest revenue by month?"*
- **AI-generated pandas code** — Gemini writes and executes the transformation logic automatically
- **Self-healing retry loop** — if generated code fails, the AI diagnoses and fixes its own errors (up to 3 attempts)
- **Self-critic verification** — after the first successful run, the AI reviews its own output for correctness before displaying results
- **Interactive Plotly charts** — bar, line, scatter, and pie charts rendered in a dark-themed UI
- **Safe code execution** — dangerous built-ins (`os`, `sys`, `exec`, `eval`, `open`) are blocked before any AI code is run
- **WebArchive plist support** — in addition to standard CSVs, the app can parse CSV data embedded in `.webarchive` plist files

---

## Project Structure

```
.
├── app.py        # Streamlit UI — file upload, chat input, retry loop, results display
├── exec.py       # Code executor and Plotly chart builder
├── main.py       # Schema extraction, prompt builder, Gemini API client
├── .env          # Environment variables (not committed — see setup below)
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

You can obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Run the app

```bash
streamlit run app.py
```

---

## Usage

1. Open the app in your browser (Streamlit will print the local URL).
2. Upload a **CSV file** using the sidebar.
3. Preview your data in the expandable **Data Preview** panel.
4. Type a natural language question in the chat input at the bottom.
5. The app will display:
   - **AI Reasoning** — the model's explanation of its approach
   - **Visualization** — an interactive Plotly chart
   - **Data Summary** — the resulting DataFrame
   - **Pipeline Code** — the pandas code the AI generated (expandable)

---

## How It Works

```
User Query
    │
    ▼
extract_schema(df)          ← Summarises column names, dtypes, nulls, unique counts
    │
    ▼
build_prompt(schema, query) ← Constructs a structured prompt for Gemini
    │
    ▼
Gemini API (model_r)        ← Returns JSON: reasoning + pandas_code + chart_config
    │
    ▼
execute_ai_code(response, df) ← Safely executes pandas_code, produces result_df
    │
    ▼
create_chart(result_df, response) ← Renders Plotly figure from chart_config
    │
    ▼
Streamlit UI                ← Displays chart, table, reasoning, and code
```

If execution fails at any step, the error is fed back to Gemini for self-correction (up to 3 retries).

---

## Environment Variables

| Variable         | Description                        |
|------------------|------------------------------------|
| `GEMINI_API_KEY` | Your Google Gemini API key         |

---

## Requirements

See `requirements.txt`. Key dependencies:

| Package           | Purpose                                      |
|-------------------|----------------------------------------------|
| `streamlit`       | Web UI framework                             |
| `pandas`          | Data manipulation and analysis               |
| `plotly`          | Interactive chart rendering                  |
| `google-genai`    | Google Gemini API client                     |
| `python-dotenv`   | Load environment variables from `.env`       |
| `beautifulsoup4`  | Parse HTML inside WebArchive plist files     |

---

## Notes

- The Gemini model used is `gemini-3.1-flash-lite-preview`. Update the model string in `main.py` if you switch to a different version.
- AI-generated code runs inside a restricted `exec()` sandbox — only `df` and `pd` are available in the execution scope.
- The app does not persist query history between sessions.
