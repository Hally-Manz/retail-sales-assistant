
from fastapi import FastAPI
import pandas as pd
import os
from google import genai
from pydantic import BaseModel
client = genai.Client()


app = FastAPI(title="Retail Sales Assistant API")
class QuestionRequest(BaseModel):
    question: str

# Load the sales data
df = pd.read_csv("data/online_retail_clean.csv", parse_dates=["InvoiceDate"])
df["Revenue"] = df["Quantity"] * df["UnitPrice"]


@app.get("/")
def home():
    return {"message": "Welcome to the Retail Sales Assistant API!"}


@app.get("/sales/total-revenue")
def get_total_revenue():
    total = round(float(df["Revenue"].sum()), 2)
    return {
        "total_revenue": total,
        "currency": "GBP"
    }


@app.get("/sales/top-products")
def get_top_products(n: int = 5):
    top = (
        df.groupby("Description")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .round(2)
    )

    return {
        "top_products": [
            {"product": product, "revenue": float(revenue)}
            for product, revenue in top.items()
        ],
        "currency": "GBP"
    }


# Create a month column for analysis
df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)


@app.get("/sales/monthly-revenue")
def get_monthly_revenue():
    monthly = df.groupby("Month")["Revenue"].sum().round(2)

    return {
        "monthly_revenue": [
            {"month": month, "revenue": float(revenue)}
            for month, revenue in monthly.items()
        ],
        "currency": "GBP"
    }


@app.get("/sales/revenue/{month}")
def get_revenue_for_month(month: str):
    monthly_data = df[df["Month"] == month]

    if monthly_data.empty:
        return {
            "error": f"No sales data found for {month}",
            "expected_format": "YYYY-MM"
        }

    revenue = round(float(monthly_data["Revenue"].sum()), 2)

    return {
        "month": month,
        "revenue": revenue,
        "currency": "GBP"
    }





@app.post("/ask")
def ask_gemini(request: QuestionRequest):
    question = request.question.lower()

    if "total revenue" in question or "total sales revenue" in question:
        total = round(float(df["Revenue"].sum()), 2)

        prompt = f"""
        The actual total revenue is £{total:,.2f} GBP.
        Answer using this figure without changing it.
        User's question: {request.question}
        """

    elif "top" in question and "product" in question:
        top = (
            df.groupby("Description")["Revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .round(2)
        )

        products = "\n".join(
            f"{i}. {product}: £{revenue:,.2f}"
            for i, (product, revenue) in enumerate(top.items(), start=1)
        )

        prompt = f"""
        These are the actual top 5 products by revenue:
        {products}

        Answer using these figures. Do not invent or change data.
        User's question: {request.question}
        """

    elif "revenue" in question and any(
        month in question
        for month in [
            "january", "february", "march", "april",
            "may", "june", "july", "august",
            "september", "october", "november", "december"
        ]
    ):
        monthly = df.groupby("Month")["Revenue"].sum()

        matching_months = [
            month for month in monthly.index
            if month in question
            or (
                pd.to_datetime(month + "-01").strftime("%B").lower() in question
            )
        ]

        if matching_months:
            month = matching_months[0]
            revenue = round(float(monthly[month]), 2)

            prompt = f"""
            The actual revenue for {month} is £{revenue:,.2f} GBP.
            Answer the user's question using this figure.
            Do not change or invent the number.
            User's question: {request.question}
            """
        else:
            prompt = f"""
            The requested month could not be identified in the dataset.
            Ask the user to specify a month and year, for example March 2011.
            User's question: {request.question}
            """

    else:
        prompt = f"""
        You are a retail sales assistant.
        This question is not yet connected to a calculation from the dataset.
        Do not invent sales figures. Ask the user to clarify their question.
        User's question: {request.question}
        """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return {
        "question": request.question,
        "answer": response.text
    }


