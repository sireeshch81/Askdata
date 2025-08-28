import plotly.express as px
import time
import json
from stmarkdown import stmarkdown

# --- Optional debug: inspect serialization issues before rendering AgGrid ---
if st.session_state.get("debug_aggrid"):
    with st.expander("Debug: AgGrid serializability (products)", expanded=False):
        issues = analyze_df_for_aggrid(display_df)
        if issues:
            st.error(f"Found {len(issues)} non-serializable values (showing up to 100).")
            st.dataframe(pd.DataFrame(issues))
        else:
            st.success("AgGrid data appears JSON-serializable.")

# --- Debug controls and serialization helpers ---
def enable_debug_controls():
    st.sidebar.checkbox("Debug AgGrid serialization", value=False, key="debug_aggrid")

def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False

def analyze_records_serializability(records, max_issues=100):
    """
    Recursively walk through a nested structure (list/dict) and collect
    any values that are not JSON-serializable.
    """
    issues = []

    def walk(x, path):
        if is_json_serializable(x):
            return
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(x, (list, tuple, set)):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        else:
            t = type(x).__name__
            try:
                rep = repr(x)
            except Exception:
                rep = "<unrepresentable>"
            issues.append({"path": path or "<root>", "type": t, "value": rep[:200]})

    walk(records, "")
    if len(issues) > max_issues:
        issues = issues[:max_issues]
    return issues

def analyze_df_for_aggrid(df, sample_rows=100):
    """
    Convert the first N rows of a DataFrame to records and analyze for non-serializable values.
    """
    try:
        records = df.head(sample_rows).to_dict(orient="records")
    except Exception as e:
        return [{"path": "<to_dict>", "type": "Exception", "value": str(e)}]
    return analyze_records_serializability(records)
