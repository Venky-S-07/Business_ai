import pandas as pd
import plotly.express as px
from main import model_r,load_data

df = load_data("data.csv")

def execute_ai_code(ai_response,df):

    code = ai_response["pandas_code"]

    blocked = ["import os", "import sys", "open(", "exec(", "eval("]

    for word in blocked:
        if word in code:
            raise ValueError("Unsafe code detected")

    local_env = {
            "df": df,
            "pd": pd
    }

    exec(code, {}, local_env)

    result_df = local_env.get("result_df")

    if result_df is None:
        raise ValueError("AI code must create a variable named result_df")

    return result_df

def create_chart(result_df, ai_response):

    chart_type = ai_response["chart_type"].lower().strip()
    config = ai_response["chart_config"]

    x = config["x"]
    y = config["y"]
    title = config["title"]

    if chart_type == "bar":
        fig = px.bar(result_df, x=x, y=y, title=title)

    elif chart_type == "line":
        fig = px.line(result_df, x=x, y=y, title=title)

    elif chart_type == "scatter":
        fig = px.scatter(result_df, x=x, y=y, title=title)

    else:
        raise ValueError("Unsupported chart type")

    fig.show()

    return fig


ai_response = model_r()

result_df = execute_ai_code(ai_response, df)

print(result_df)

create_chart(result_df,ai_response)
