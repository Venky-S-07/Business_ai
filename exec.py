import pandas as pd
import plotly.express as px


def execute_ai_code(ai_response: dict, df: pd.DataFrame) -> pd.DataFrame:
    # Validate that the AI response contains executable pandas code.
    # Raises an error if the key is missing or unsafe keywords are found.
    if "pandas_code" not in ai_response:
        raise ValueError(
            f"AI response missing 'pandas_code'. Error: {ai_response.get('error', 'Unknown')}"
        )

    code = ai_response["pandas_code"]

    # Block dangerous built-ins to prevent arbitrary code execution.
    blocked_keywords = ["import os", "import sys", "open(", "exec(", "eval("]
    for keyword in blocked_keywords:
        if keyword in code:
            raise ValueError(f"Unsafe code detected: '{keyword}' is not allowed.")

    # Run the AI code in an isolated environment with only df and pd available.
    # The code must produce a variable named 'result_df'.
    local_env = {"df": df, "pd": pd}
    exec(code, {}, local_env)

    result_df = local_env.get("result_df")
    if result_df is None:
        raise ValueError("AI code must produce a variable named 'result_df'.")

    return result_df


def create_chart(result_df: pd.DataFrame, ai_response: dict):
    # Extract chart type and axis config from the AI response.
    # Normalize color to None if the model returned "null" or an empty string.
    chart_type = ai_response["chart_type"].lower().strip()
    config = ai_response["chart_config"]

    x     = config.get("x")
    y     = config.get("y")
    color = config.get("color")
    title = config.get("title")

    if color in ("null", "", None):
        color = None

    # Build and return the appropriate Plotly chart based on chart_type.
    if chart_type == "bar":
        fig = px.bar(result_df, x=x, y=y, color=color, title=title, barmode="group")
    elif chart_type == "line":
        fig = px.line(result_df, x=x, y=y, color=color, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(result_df, x=x, y=y, color=color, title=title)
    elif chart_type == "pie":
        fig = px.pie(result_df, names=x, values=y, title=title)
    else:
        raise ValueError(f"Unsupported chart type: '{chart_type}'.")

    return fig


if __name__ == "__main__":
    from main import model_r

    # Quick smoke test using a minimal DataFrame to verify the full pipeline.
    test_df = pd.DataFrame({"Month": ["Jan", "Feb"], "Revenue": [100, 200]})

    try:
        response = model_r(test_df, "What is the revenue by month?")
        result_df = execute_ai_code(response, test_df)
        print(result_df)

        fig = create_chart(result_df, response)
        fig.show()
    except Exception as e:
        print(f"Test execution failed: {e}")
