"""
Retail Sales Assistant
An LLM agent (Gemini) that answers questions about retail sales data by
calling real pandas functions, so the numbers come from the data, not the model.
"""
import os
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types

# ---------- Config ----------
DATA_PATH = "data/online_retail_clean.csv"   # your cleaned file from the retail project
MODEL = "gemini-3.8-flash"                   # check the Gemini docs for the current model name

# ---------- Load data ----------
# Adjust column names to match your own dataset.
df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)   # e.g. "2011-03"


# ---------- Tools (plain Python functions the model can call) ----------
# The docstrings and type hints matter: Gemini reads them to decide when
# and how to call each function.

def total_revenue() -> dict:
    """Return the total revenue across the whole dataset."""
    return {"total_revenue": round(float(df["Revenue"].sum()), 2)}


def top_products(n: int = 5) -> list:
    """Return the top n products ranked by total revenue.

    Args:
        n: how many products to return.
    """
    top = (df.groupby("Description")["Revenue"].sum()
             .sort_values(ascending=False).head(n).round(2))
    return [{"product": k, "revenue": float(v)} for k, v in top.items()]


def monthly_revenue() -> dict:
    """Return total revenue for every month, as {"YYYY-MM": revenue}."""
    m = df.groupby("Month")["Revenue"].sum().round(2)
    return {k: float(v) for k, v in m.items()}


def revenue_for_month(month: str) -> dict:
    """Return the revenue for one month.

    Args:
        month: the month in YYYY-MM format, e.g. "2011-03".
    """
    sub = df[df["Month"] == month]
    if sub.empty:
        return {"error": f"No data for {month}"}
    return {"month": month, "revenue": round(float(sub["Revenue"].sum()), 2)}


def plot_monthly_revenue() -> dict:
    """Create an interactive Plotly chart of monthly revenue and save it as an HTML file."""
    m = df.groupby("Month", as_index=False)["Revenue"].sum()
    fig = px.line(m, x="Month", y="Revenue", markers=True, title="Monthly Revenue")
    fig.write_html("monthly_revenue.html")
    return {"saved_to": "monthly_revenue.html"}


TOOLS = [total_revenue, top_products, monthly_revenue, revenue_for_month, plot_monthly_revenue]

SYSTEM_PROMPT = (
    "You are a retail sales analyst assistant. Always use the provided tools to get "
    "numbers; never guess or invent figures. If the data cannot answer a question, "
    "say so. Keep answers short and clear, and mention the currency as GBP (£)."
)


# ---------- Agent loop ----------
def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("Set the GEMINI_API_KEY environment variable first.")

    client = genai.Client()  # reads GEMINI_API_KEY automatically
    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, tools=TOOLS)
    # Passing Python functions as tools lets the SDK call them automatically
    # when the model requests them, then send the results back to the model.
    chat = client.chats.create(model=MODEL, config=config)

    print("Retail Sales Assistant (type 'quit' to exit)")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        try:
            reply = chat.send_message(question)
            print("Assistant:", reply.text)
        except Exception as e:  # e.g. rate limit or network error
            print("Error:", e)


if __name__ == "__main__":
    main()
