from google import genai
import pandas as pd
import plistlib
import json
from bs4 import BeautifulSoup
import io
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

def load_data(file_source):
    with open("data.csv", "rb") as f:
        data = plistlib.load(f)

    html_bytes = data["WebMainResource"]["WebResourceData"]

    html = html_bytes.decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")

    csv_text = soup.find("pre").text

    return pd.read_csv(io.StringIO(csv_text))

df = load_data("data.csv")

client = genai.Client(api_key=api_key)

def extract_schema(df):
    schema = {}

    schema["rows"] = len(df)
    schema["columns"] = len(df.columns)

    column_info = []

    for col in df.columns:
        info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].notnull().sum()),
                "null": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique())
        }

        column_info.append(info)

    schema["column_details"] = column_info

    return schema


def build_prompt(schema, user_query):
    schema_context = f"""
    Dataset Summary

    Total Rows: {schema['rows']}
    Total Columns: {schema['columns']}

    Columns:
    """

    for col in schema["column_details"]:
        schema_context += f"""
        - {col['name']}
            type: {col['dtype']}
            unique values: {col['unique_values']}
            null values: {col['null']}
        """

    prompt = f"""
    You are a Python Data Analyst bot. 
    DATASET SCHEMA:
    {schema_context}

    USER REQUEST: "{user_query}"

    OUTPUT FORMAT:
    Return ONLY a valid JSON object. Do not include markdown formatting like ```json. 
    The JSON must follow this structure:
    {{
        "reasoning": "Brief explanation of the logic used.",
        "pandas_code": "The exact python code to transform the dataframe 'df' into the required result set.",
        "chart_type": "one of ['bar', 'line', 'pie', 'scatter', 'table']",
        "chart_config": {{
            "x": "column_name_for_x_axis",
            "y": "column_name_for_y_axis",
            "title": "A descriptive title"
        }}
    }}

    CONSTRAINTS:
    - Use only the dataframe named 'df'.
    - Ensure 'pandas_code' results in a variable named 'result_df'.
    - If the query cannot be answered, return {{"error": "reason"}}.
    """

    return prompt


def model_r():
    schema = extract_schema(df)
    prompt = build_prompt(schema,"give me monthly revenu of q4")

    response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
    )

    text = response.text.strip()

    # remove markdown if present
    if text.startswith("```"):
        text = text.split("```")[1]

    text = text.replace("json", "").strip()

    return json.loads(text)
