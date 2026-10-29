# retail-sales-assistant
# Retail Sales Assistant API

A Gemini-powered retail sales assistant built with Python, FastAPI and Pandas. The project analyses retail transaction data and provides sales insights through REST API endpoints.

## Features

- **Total Revenue:** Calculate total revenue from retail transactions.
- **Top Products:** Identify the top five products ranked by revenue.
- **Monthly Revenue:** Retrieve revenue summaries by month.
- **Revenue by Month:** Query revenue for a specific month.
- **AI-Powered Questions:** Use Google's Gemini API to answer supported retail sales questions in natural language.
- **Interactive API Documentation:** Explore and test endpoints using Swagger UI.

## Tech Stack

- Python
- FastAPI
- Pandas
- Google Gemini API (`google-genai`)
- Uvicorn

## Project Structure

```text
retail-sales-assistant/
├── api.py
├── retail_assistant.py
├── data/
│   ├── Online Retail.xlsx
│   └── online_retail_clean.csv
├── .venv/
├── README.md
└── .gitignore
```

*Note: The files shown are the expected project layout; your actual files may differ.*

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd retail-sales-assistant
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository URL.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install fastapi uvicorn pandas openpyxl google-genai
```

### 4. Configure your Gemini API key

Obtain an API key from [Google AI Studio](https://aistudio.google.com/apikey).

Set it in your PowerShell terminal:

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Replace the placeholder with your own key. Never commit your API key to GitHub.

### 5. Start the API

```powershell
python -m uvicorn api:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/sales/total-revenue` | Returns total sales revenue |
| GET | `/sales/top-products?n=5` | Returns the top products by revenue |
| GET | `/sales/monthly-revenue` | Returns revenue grouped by month |
| GET | `/sales/revenue/2011-03` | Returns revenue for a specified month |
| POST | `/ask` | Answers supported sales questions using Gemini |

## Example Usage

### Get total revenue

Open:

`http://127.0.0.1:8000/sales/total-revenue`

Example response:

```json
{
  "total_revenue": 9747747.93,
  "currency": "GBP"
}
```

### Ask a sales question

Send a POST request to `/ask` with this JSON body:

```json
{
  "question": "What is the total sales revenue?"
}
```

Example response:

```json
{
  "question": "What is the total sales revenue