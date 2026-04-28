"""
csv_analyzer.py
---------------
Anish's CSV Analyzer — beginner project using Pandas + Claude API.

What it does:
  1. Loads any CSV file
  2. Builds a plain-English summary of the data using Pandas
  3. Sends that summary to Claude
  4. Claude explains what the data means, spots patterns, and suggests questions

How to run:
  python csv_analyzer.py               <- will ask you to type a filename
  python csv_analyzer.py mydata.csv    <- pass filename directly

Requirements:
  pip install anthropic pandas python-dotenv
"""

import sys
import anthropic
import pandas as pd
from dotenv import load_dotenv

# ── Setup ─────────────────────────────────────────────────────────────────────

load_dotenv()  # reads ANTHROPIC_API_KEY from .env file
client = anthropic.Anthropic()


# ── Step 1: Load the CSV ──────────────────────────────────────────────────────

def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame. Shows a helpful error if it fails."""
    try:
        df = pd.read_csv(filepath)
        print(f"\n  Loaded '{filepath}' — {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        print(f"\n  Error: Could not find '{filepath}'")
        print("  Make sure the file is in the same folder as this script.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error reading CSV: {e}")
        sys.exit(1)


# ── Step 2: Build a summary using Pandas ─────────────────────────────────────

def build_summary(df: pd.DataFrame, filepath: str) -> str:
    """
    Turn the DataFrame into a structured text summary.
    This is what we'll send to Claude — not the raw CSV (which could be huge).
    """

    lines = []

    # Basic info
    lines.append(f"Dataset: {filepath}")
    lines.append(f"Size: {len(df)} rows x {len(df.columns)} columns")
    lines.append("")

    # Column names and their types
    lines.append("Columns:")
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_info = f" ({null_count} missing values)" if null_count > 0 else ""
        lines.append(f"  - {col} [{dtype}]{null_info}")
    lines.append("")

    # First 5 rows so Claude can see what the data looks like
    lines.append("First 5 rows:")
    lines.append(df.head(5).to_string(index=False))
    lines.append("")

    # Stats for numeric columns (mean, min, max, etc.)
    numeric_cols = df.select_dtypes(include="number")
    if not numeric_cols.empty:
        lines.append("Numeric column statistics:")
        lines.append(numeric_cols.describe().round(2).to_string())
        lines.append("")

    # For text/category columns — show most common values
    text_cols = df.select_dtypes(include=["object", "category"])
    if not text_cols.empty:
        lines.append("Text column summaries (most common values):")
        for col in text_cols.columns:
            top = df[col].value_counts().head(5)
            lines.append(f"\n  {col}:")
            for val, count in top.items():
                lines.append(f"    '{val}': {count} times")
    lines.append("")

    # Any columns that look like dates
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
    if date_cols:
        lines.append(f"Possible date columns: {date_cols}")
        lines.append("")

    return "\n".join(lines)


# ── Step 3: Ask Claude to explain it ─────────────────────────────────────────

def ask_claude(summary: str) -> str:
    """Send the data summary to Claude and get an explanation back."""

    system_prompt = """You are a friendly data analyst helping a student understand a dataset.

When given a dataset summary, you:
1. Explain in plain English what this dataset is about
2. Point out the most interesting patterns or numbers you notice
3. Mention anything unusual (missing data, outliers, surprising values)
4. Suggest 3 specific questions worth investigating with this data

Keep your language simple and clear — no jargon. 
Be specific: mention actual column names and real numbers from the data.
Format your response with clear sections using headers."""

    user_message = f"""Here is a summary of a CSV dataset. Please analyze it and explain what it shows.

{summary}"""

    print("\n  Sending to Claude for analysis...\n")

    # Use streaming so the response prints word by word (looks cooler!)
    full_response = ""

    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n")
    return full_response


# ── Step 4: Follow-up questions loop ─────────────────────────────────────────

def follow_up_loop(summary: str, initial_answer: str):
    """
    After the initial analysis, let the user ask follow-up questions.
    We keep the conversation history so Claude remembers context.
    """

    # Start with what Claude already said
    conversation = [
        {
            "role": "user",
            "content": f"Please analyze this dataset:\n\n{summary}"
        },
        {
            "role": "assistant",
            "content": initial_answer
        }
    ]

    system_prompt = """You are a friendly data analyst helping a student understand a dataset.
You have already analyzed the dataset and are now answering follow-up questions.
Be specific, use real numbers from the data, and keep answers clear and concise."""

    print("─" * 60)
    print("  Ask follow-up questions about your data!")
    print("  (Type 'quit' or press Enter with no text to exit)")
    print("─" * 60)

    while True:
        question = input("\nYour question: ").strip()

        if not question or question.lower() in ["quit", "exit", "q"]:
            print("\n  Thanks for using the CSV Analyzer! Great work, Anish.")
            break

        # Add the new question to conversation history
        conversation.append({"role": "user", "content": question})

        print()
        response_text = ""

        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=system_prompt,
            messages=conversation
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_text += text

        print("\n")

        # Add Claude's answer to history for next question
        conversation.append({"role": "assistant", "content": response_text})


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("       CSV ANALYZER — powered by Claude")
    print("=" * 60)

    # Get filename from command line or ask the user
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = input("\n  Enter CSV filename (e.g. nba_stats.csv): ").strip()

    # Run the pipeline
    df = load_csv(filepath)
    summary = build_summary(df, filepath)
    initial_answer = ask_claude(summary)

    # Optional: follow-up questions
    print("─" * 60)
    cont = input("  Ask follow-up questions? (y/n): ").strip().lower()
    if cont == "y":
        follow_up_loop(summary, initial_answer)
    else:
        print("\n  Done!")


if __name__ == "__main__":
    main()