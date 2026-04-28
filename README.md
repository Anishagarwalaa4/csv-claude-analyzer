# 📊 CSV Claude Analyzer

> Drop in any CSV. Claude reads it, finds patterns, and explains what the data means in plain English.

A Python command-line tool that ingests arbitrary CSV files, generates structured Pandas summaries, and uses the Claude API to produce human-readable analysis with conversational follow-up support.

---

## ✨ What it does

```
$ python csv_analyzer.py nba_stats.csv

  Loaded 'nba_stats.csv' — 11700 rows, 22 columns
  Sending to Claude for analysis...

## What this dataset shows
This is a dataset of NBA player statistics covering 27 seasons (1996-2024)...

## Interesting patterns
- Average points per game across all players: 8.2
- The 'pts' column has notable right-skew, with elite scorers averaging 27+ PPG
...

## 3 questions worth investigating
1. Has the game shifted toward higher-scoring guards over time?
2. Do draft round and college origin predict career longevity?
3. Which combinations of stats (e.g., usage % + true shooting %) identify true superstars?

────────────────────────────────────────
  Ask follow-up questions? (y/n): y

Your question: which players are statistical outliers?
```

---

## 🧠 How it works

```
   CSV file
      ↓
  Pandas (load + summarize)
      ↓
  Structured text summary
   (columns, dtypes, head, describe, nulls)
      ↓
  Claude API (streaming)
      ↓
  Plain-English analysis
      ↓
  Optional follow-up Q&A loop
   (with conversation history)
```

The key insight: instead of sending the raw CSV to Claude, the script first uses Pandas to build a compact text summary (column names, types, statistics, sample rows). This works for CSVs of any size and produces consistent, fast results.

---

## 🛠️ Tech stack

- **Python 3.10+**
- **Claude Sonnet 4.5** via the official `anthropic` SDK
- **Pandas** for data summarization
- **python-dotenv** for API key management
- **Streaming responses** — output appears in real-time

---

## 📂 Project structure

```
csv-claude-analyzer/
├── csv_analyzer.py     # Main script
├── requirements.txt    # Python dependencies
├── .env.example        # API key template (real .env is gitignored)
├── .gitignore
├── sample_data.csv     # Optional test dataset
└── README.md
```

---

## 🚀 Getting started

### Prerequisites
- Python 3.10 or newer
- An [Anthropic API key](https://console.anthropic.com)

### Setup

```bash
# Clone the repo
git clone https://github.com/Anishagarwalaa4/csv-claude-analyzer.git
cd csv-claude-analyzer

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Then open .env and paste your real key
```

### Run it

```bash
# Pass the CSV filename as an argument
python csv_analyzer.py your_data.csv

# Or run without arguments to be prompted for a filename
python csv_analyzer.py
```

---

## 🧩 Engineering highlights

- **Schema-agnostic design** — Works on any CSV regardless of column names, types, or size. The summary builder dynamically detects numeric vs categorical vs date columns.
- **Streaming responses** — Output prints token-by-token as Claude generates it, instead of blocking until the full reply arrives.
- **Multi-turn conversation** — Follow-up questions reuse the dataset summary as shared context, so Claude can answer "drill-down" questions without re-uploading data.
- **Defensive file handling** — Friendly errors for missing files, malformed CSVs, and encoding issues.

---

## 💡 Sample questions to try after the initial analysis

- "Which columns are the most predictive of [target]?"
- "Are there any missing-data patterns I should worry about?"
- "What would be a good way to visualize this?"
- "Suggest a feature engineering idea based on these columns."

---

## 📚 What I learned building this

- How to design system prompts that produce structured, predictable output from an LLM
- The streaming response pattern with the Anthropic SDK
- How to maintain conversation history across multi-turn LLM interactions
- Why summarizing data with Pandas before sending to an LLM beats sending raw rows (cheaper, faster, more accurate)

---

## 🔮 What's next

- [ ] Add a Streamlit web UI for non-technical users
- [ ] Auto-generate matplotlib visualizations alongside the analysis
- [ ] Support for Excel files and JSON inputs
- [ ] Save analysis sessions as markdown reports

---

## 👋 About

Built by **Anish Agarwal**, a 10th grade student in San Diego interested in sensor data pipelines and LLM-assisted research. Currently seeking summer research opportunities in environmental sensing, robotics, or applied AI.

📧 anishagarwalaa4@gmail.com
🔗 [github.com/Anishagarwalaa4](https://github.com/Anishagarwalaa4)
