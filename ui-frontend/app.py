import streamlit as st
import requests
import jwt
import matplotlib.pyplot as plt
import pandas as pd
from keycloak import KeycloakOpenID
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from datetime import datetime
from pymongo import MongoClient
import hashlib
import plotly.express as px
import time


st.set_page_config(layout="wide")

# --- Branding & Styling ---
def show_fixed_branding():
    cols = st.columns([1.2, 2.2])  # logo + text
    with cols[0]:
        st.image("cgilogo.png", width=120)
    with cols[1]:
        st.markdown(
            """
            <h1 style="color:#b22222; font-weight: 700; margin-bottom: 0; 
                       font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                AskData
            </h1>
            <p style="font-style: italic; color: #666; font-size: 18px; margin-top: 2px;
                      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Ask Naturally. Understand Instantly.
            </p>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
<style>
/* Your CSS styles unchanged */
.user-info-logout-container {
    position: fixed;
    top: 15px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    background: #ffffffcc;
    padding: 8px 16px;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(178, 34, 34, 0.4);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 15px;
    user-select: none;
    z-index: 11000;
    white-space: nowrap;
}
.user-info-text {
    color: #222;
    user-select: text;
    line-height: 1.2;
}
.user-info-text b {
    margin-right: 8px;
}
.logout-button {
    background-color: #b22222;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 900;
    font-size: 14px;
    user-select: none;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 10px rgba(178, 34, 34, 0.6);
    white-space: nowrap;
}
.logout-button:hover {
    background-color: #7f1616;
    box-shadow: 0 6px 15px rgba(127, 22, 22, 0.9);
}
.app-content {
    margin-top: 80px;
    margin-left: auto;
    margin-right: auto;
    max-width: 1150px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
[data-baseweb="tab-list"] {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0;
    gap: 16px !important;
    justify-content: center;
}
[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 16px;
    padding: 8px 22px;
    border-radius: 10px;
    border: 2px solid #b22222;
    margin: 0 4px;
    color: #b22222;
    transition: all 0.3s ease;
    background-color: white;
}
[data-baseweb="tab"]:hover {
    background-color: #ffeaea;
    cursor: pointer;
}
[data-baseweb="tab"][aria-selected="true"] {
    background-color: #b22222 !important;
    color: white !important;
    font-weight: bold;
}
.login-form-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 150px;
}
.login-form-container input[type="text"],
.login-form-container input[type="password"] {
    max-width: 100px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
    font-size: 14px !important;
    padding: 6px 10px !important;
    border-radius: 5px !important;
}
.login-box {
    background: white;
    padding: 2rem 3rem;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.05);
    width: 50%;
    max-width: 200px;
    text-align: center;
    margin-top: 80px;
}
.login-form-container {
    margin-top: 0 !important;
    padding-top: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}
.customer-card {
    background: white;
    padding: 2.5rem 3rem;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    max-width: 700px;
    margin: 3rem auto 1rem auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #222;
    line-height: 1.6;
    user-select: text;
}
.customer-header {
    font-weight: 900;
    font-size: 2.2rem;
    color: #b22222;
    margin-bottom: 1.5rem;
}
.customer-card p {
    font-size: 1.1rem;
    margin: 0.5rem 0;
}
.customer-card p strong {
    margin-left: 0.3rem;
    color: #555;
}
.recommendations-section {
    max-width: 700px;
    margin: 1rem auto 3rem auto;
    padding-top: 1.5rem;
    border-top: 3px solid #b22222;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    user-select: text;
    color: #222;
}
.recommendations-section h3 {
    font-weight: 800;
    font-size: 1.7rem;
    color: #b22222;
    margin-bottom: 1rem;
}
.back-button {
    background-color: #b22222;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    color: white;
    font-weight: 700;
    cursor: pointer;
    font-size: 16px;
    margin-top: 0;
    margin-bottom: 4rem;
    display: block;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    user-select: none;
    transition: background-color 0.3s ease;
}
.back-button:hover {
    background-color: #7f1616;
}
.recommendation-card {
    background: #fff0f0;
    padding: 0.8rem 1rem;
    border-radius: 15px;
    margin-bottom: 0.8rem;
    box-shadow: 0 3px 8px rgba(178,34,34,0.12);
    cursor: pointer;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    transition: background-color 0.3s ease;
}
.recommendation-card:hover {
    background-color: #ffeaea;
}
.recommendation-card-expanded {
    background: #fff8f8;
    padding: 1rem 1.2rem;
    border-radius: 15px;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 14px rgba(178,34,34,0.25);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.offer-customer-button-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}
.offer-customer-button {
    background-color: #b22222;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 700;
    font-size: 16px;
    user-select: none;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 10px rgba(178, 34, 34, 0.6);
    white-space: nowrap;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.offer-customer-button:hover {
    background-color: #7f1616;
    box-shadow: 0 6px 15px rgba(127, 22, 22, 0.9);
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Keycloak Configuration ---
KEYCLOAK_SERVER_URL = "http://keycloak:8080/auth"
KEYCLOAK_REALM_NAME = "askdata-realm"
KEYCLOAK_CLIENT_ID = "askdataclient"
KEYCLOAK_CLIENT_SECRET = "ooDSACRdaN3sbUzgCdaMGNt9Ez2YQv7j"

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM_NAME,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
)

# --- Authentication Functions ---
def authenticate_user():
    if "token" not in st.session_state:
        # Clear old session keys on logout or first load
        for key in [
            "search_results",
            "selected_customer",
            "last_customer_name",
            "last_email",
            "last_phone",
            "customer_name_input",
            "email_input",
            "phone_input",
            "page",
            "rec_expanded_idx",
            "nl_query_input",
            "generated_sql",
            "edited_sql_input",
            "sql_results",
            "search_method",  # clear search method on logout
            "search_method_prev",
            "manual_search_results",
            "nlp_search_results",
        ]:
            st.session_state.pop(key, None)

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            st.markdown("### Login to CGI AskData")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

            if submitted:
                try:
                    token = keycloak_openid.token(username, password)
                    st.session_state["token"] = token
                    st.rerun()
                except Exception:
                    st.error("Invalid credentials. Please try again.")

        return None
    else:
        return st.session_state.get("token")


def get_user_info_from_token(token):
    access_token_str = token.get("access_token")
    if not access_token_str:
        return None
    try:
        decoded_token = jwt.decode(
            access_token_str, options={"verify_signature": False}
        )
        return {
            "name": decoded_token.get("name", "N/A"),
            "email": decoded_token.get("email", "N/A"),
            "realm_roles": decoded_token.get("realm_access", {}).get(
                "roles", []
            ),
            "client_roles": decoded_token.get("resource_access", {})
            .get(KEYCLOAK_CLIENT_ID, {})
            .get("roles", []),
        }
    except Exception as e:
        st.error(f"Token error: {e}")
        return None


def show_user_info_and_logout(user_info, button_key="logout_button"):
    st.markdown(
        '<div class="user-info-logout-container">', unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="user-info-text">
            👤 <b>{user_info.get('name', 'N/A')}</b><br/>
            ✉️ {user_info.get('email', 'N/A')}
        </div>
        """,
        unsafe_allow_html=True,
    )
    logout_clicked = st.button(
        "Logout", key=button_key, help="Logout from the application"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return logout_clicked


# --- API Functions ---
def offer_customer(customer_id: int):
    """
    Call the dw-backend API to offer customer products
    """

    
    # Retry configuration
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://dw-backend:5001/offer-customer",
                json={"customer_id": str(customer_id)},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Offer successfully created for customer {customer_id}")
                return result
            else:
                st.error(f"❌ Failed to create offer for customer {customer_id}. Status: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            if "Failed to resolve 'dw-backend'" in str(e):
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ dw-backend service not available (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    st.error(f"❌ dw-backend service is not running or not accessible. Please ensure the service is started.")
                    st.info("💡 Try running: docker-compose up dw-backend -d")
                    return None
            else:
                st.error(f"❌ Connection error: {str(e)}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error connecting to dw-backend API: {str(e)}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None
    
    return None


# --- MongoDB Connection ---
def get_mongo_client():
    return MongoClient(
        host="mongodb",
        port=27017,
        username="mongo_root",
        password="mongo_password",
        authSource="admin",
        authMechanism="SCRAM-SHA-256",
    )


def get_recommendations_for_customer(customer_id: int):
    client = get_mongo_client()
    db = client.askdata_mongo
    collection = db.recommendations

    doc = collection.find_one({"customer_id": str(customer_id)})
    client.close()
    return doc


def get_customers_for_product(product_name: str):
    """
    Fetch customers associated with a given product_id from MongoDB.
    """
    client = get_mongo_client()
    db = client.askdata_mongo
    collection = db.recommendations  # Adjust collection name if needed

    # Example: Find all customers who have this product_id in their products list
    customers = list(collection.find({"recommendations.product_name": product_name}))
    print("Customers for product:", customers)  # <-- Print all customers here

    client.close()
    return customers

# --- Manual Customer Search ---
def manual_customer_search():
    customer_name_input = st.session_state.get("customer_name_input", "")
    email_input = st.session_state.get("email_input", "")
    phone_input = st.session_state.get("phone_input", "")

    with st.form("manual_search_form"):
        cols = st.columns(3)
        with cols[0]:
            customer_name_input = st.text_input(
                "Customer Name",
                key="customer_name_input",
                placeholder="e.g. John Doe",
                value=customer_name_input,
            )
        with cols[1]:
            email_input = st.text_input(
                "Email",
                key="email_input",
                placeholder="e.g. john@example.com",
                value=email_input,
            )
        with cols[2]:
            phone_input = st.text_input(
                "Phone",
                key="phone_input",
                placeholder="e.g. +1 234 567 8900",
                value=phone_input,
            )
        submitted = st.form_submit_button("Search")

    if submitted:
        st.session_state["last_customer_name"] = customer_name_input.strip()
        st.session_state["last_email"] = email_input.strip()
        st.session_state["last_phone"] = phone_input.strip()

        if not (
            st.session_state["last_customer_name"]
            or st.session_state["last_email"]
            or st.session_state["last_phone"]
        ):
            st.error("Please enter at least one search criteria.")
            st.session_state["manual_search_results"] = []
            st.session_state["selected_customer"] = None
        else:
            try:
                params = {}
                if st.session_state["last_customer_name"]:
                    params["customer_name"] = st.session_state["last_customer_name"]
                if st.session_state["last_email"]:
                    params["email"] = st.session_state["last_email"]
                if st.session_state["last_phone"]:
                    params["phone"] = st.session_state["last_phone"]

                response = requests.get(
                    "http://askdata-api-backend:5004/customer_detail",
                    params=params,
                )
                if response.status_code == 200:
                    customers = response.json()
                    if customers:
                        st.session_state["manual_search_results"] = customers
                        st.session_state["selected_customer"] = None
                    else:
                        st.info(
                            "⚠️ No customers matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["manual_search_results"] = []
                        st.session_state["selected_customer"] = None
                else:
                    detail = response.json().get("detail", "")
                    if detail.lower() == "customers not found":
                        st.warning(
                            "⚠️ No customers matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["manual_search_results"] = []
                        st.session_state["selected_customer"] = None
                    else:
                        st.error(f"Error: {detail or 'Unknown error'}")
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

# --- NLP Customer Search ---
def nlp_customer_search():
    nl_query = st.text_area(
        "Enter your query in natural language",
        height=100,
        placeholder="e.g. Find customers named John with email gmail.com",
        key="nl_query_input",
    )

    generate_clicked = st.button("Generate SQL", key="generate_sql_button")

    if generate_clicked:
        if not nl_query.strip():
            st.error("Please enter a natural language query.")
            st.session_state.pop("generated_sql", None)
            st.session_state.pop("nlp_search_results", None)
            st.session_state["selected_customer"] = None
        else:
            with st.spinner("Generating SQL..."):
                try:
                    response = requests.post(
                        "http://askdata-api-backend:5004/generate_sql",
                        json={"nl_query": nl_query},
                    )
                    response.raise_for_status()
                    sql_query = response.json().get("sql", "")
                    if sql_query:
                        st.session_state["generated_sql"] = sql_query
                        st.success("✅ SQL query generated successfully!")
                        st.session_state.pop("nlp_search_results", None)
                        st.session_state["selected_customer"] = None
                    else:
                        st.info("⚠️ No SQL query returned from backend.")
                        st.session_state.pop("generated_sql", None)
                        st.session_state.pop("nlp_search_results", None)
                        st.session_state["selected_customer"] = None
                except Exception as e:
                    st.error(f"Error generating SQL: {e}")
                    st.session_state.pop("generated_sql", None)
                    st.session_state.pop("nlp_search_results", None)
                    st.session_state["selected_customer"] = None

    sql_query = st.session_state.get("generated_sql", "")

    if sql_query:
        edited_sql = st.text_area(
            "Edit SQL if needed",
            value=sql_query,
            height=150,
            key="edited_sql_input",
        )

        run_clicked = st.button("Run SQL", key="run_sql_button")

        if run_clicked:
            if not edited_sql.strip():
                st.error("SQL query cannot be empty.")
                st.session_state.pop("nlp_search_results", None)
                st.session_state["selected_customer"] = None
            else:
                with st.spinner("Running SQL query..."):
                    try:
                        response = requests.post(
                            "http://askdata-api-backend:5004/run_custom_query",
                            json={"sql_query": edited_sql},
                        )
                        response.raise_for_status()
                        results = response.json().get("results", [])
                        if results:
                            log_query_to_mongo(results)
                            st.session_state["nlp_search_results"] = results
                            st.session_state["selected_customer"] = None
                        else:
                            st.warning(
                                "⚠️ No customers matched your search criteria. Please try different filters or check for typos."
                            )
                            st.session_state["nlp_search_results"] = []
                            st.session_state["selected_customer"] = None
                    except Exception as e:
                        st.error(f"Error running SQL query: {e}")
                        st.session_state.pop("nlp_search_results", None)
                        st.session_state["selected_customer"] = None

# --- Display Search Results (manual or NLP) ---

def display_search_results(mode="manual"):
    # --- Fetch data from session ---
    if mode == "manual":
        customers = st.session_state.get("manual_search_results", [])
    else:
        customers = st.session_state.get("nlp_search_results", [])

    if not customers:
        st.info("No results to display yet. Please perform a search.")
        return

    df = pd.DataFrame(customers)

    # --- Convert all values to strings to avoid serialization issues ---
    df = df.astype(str)
    
    # --- Ensure unique column names to avoid AgGrid / JSON errors ---
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols == dup] = [f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols

    # --- Determine display_df based on mode ---
    if mode == "manual":
        # --- Manual search: static mapping ---
        if "customer_id" in df.columns:
            customer_id_col = "customer_id"
        elif "member_id" in df.columns:
            customer_id_col = "member_id"
        else:
            customer_id_col = df.columns[0]

        if "first_name" in df.columns and "last_name" in df.columns:
            df["Name"] = df["first_name"] + " " + df["last_name"]
            name_col = "Name"
        elif "Name" in df.columns:
            name_col = "Name"
        else:
            name_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

        display_cols = [
            customer_id_col,
            name_col,
            "email" if "email" in df.columns else None,
            "phone" if "phone" in df.columns else None,
            "date_of_birth" if "date_of_birth" in df.columns else None,
        ]
        display_cols = [col for col in display_cols if col is not None]

        display_df = df[display_cols].rename(
            columns={
                customer_id_col: "Customer ID",
                name_col: "Name",
                "email": "Email",
                "phone": "Phone",
                "date_of_birth": "DOB",
            }
        )
    else:
        # --- NLP mode: show all columns as returned by query ---
        display_df = df.copy()

        # Map member_id/customer_id to Customer ID if row-level data
        if "first_name" in display_df.columns and "last_name" in display_df.columns:
            display_df["Name"] = display_df["first_name"] + " " + display_df["last_name"]
            name_col = "Name"
        elif "Name" in display_df.columns:
            name_col = "Name"
        else:
            name_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        if "member_id" in display_df.columns or "customer_id" in display_df.columns:
            if "Customer ID" not in display_df.columns:
                if "member_id" in display_df.columns:
                    display_df["Customer ID"] = display_df["member_id"]
                else:
                    display_df["Customer ID"] = display_df["customer_id"]
        rename_map = {}
        if "email" in display_df.columns:
            rename_map["email"] = "Email"
        if "phone" in display_df.columns:
            rename_map["phone"] = "Phone"
        if "date_of_birth" in display_df.columns:
            rename_map["date_of_birth"] = "DOB"
        display_df.rename(columns=rename_map, inplace=True)

    # --- AgGrid setup ---
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True if "Customer ID" in display_df.columns else False,
        suppressRowClickSelection=True,
    )
    #gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        cellStyle=JsCode(
            """
            function(params) {
                if (params.node.isSelected()) {
                    return {'backgroundColor': '#b9d6f2'};
                } else if (params.rowIndex % 2 === 0) {
                    return {'backgroundColor': '#f9f9f9'};
                }
            }
            """
        ),
    )

    # --- Format known columns ---
    if "Email" in display_df.columns:
        gb.configure_column("Name", header_name="Name", tooltipField="Name")
    if "Email" in display_df.columns:
        gb.configure_column("Email", header_name="📧 Email", tooltipField="Email")
    if "Phone" in display_df.columns:
        gb.configure_column("Phone", header_name="📞 Phone", tooltipField="Phone")
    if "DOB" in display_df.columns:
        gb.configure_column(
            "DOB",
            header_name="🎂 Date of Birth",
            type=["dateColumnFilter", "customDateTimeFormat"],
            valueFormatter=JsCode(
                """
                function(params) {
                    if (!params.value) return '';
                    return new Date(params.value).toLocaleDateString();
                }
                """
            ),
        )

    # --- Enable horizontal scroll ---
    gb.configure_grid_options(domLayout='autoHeight', suppressHorizontalScroll=False)
    gb.configure_grid_options(ensureDomOrder=True)
    gb.configure_grid_options(allowHorizontalScroll=True)

    # --- Dynamic key to refresh AgGrid when columns change ---
    query_columns = "_".join(sorted(display_df.columns))
    grid_key = f"aggrid_{mode}_{hashlib.md5(query_columns.encode()).hexdigest()}"

    grid_response = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="material",
        height=480,
        fit_columns_on_grid_load=False,  # Disable auto-fit to allow scrolling
        allow_unsafe_jscode=True,
        reload_data=True,
        key=grid_key,
    )

    # --- Handle selection ---
    selected_rows = grid_response.get("selected_rows")
    if selected_rows is None:
        selected_rows = []
    elif isinstance(selected_rows, pd.DataFrame):
        selected_rows = selected_rows.to_dict(orient="records")

    if selected_rows and "Customer ID" in selected_rows[0]:
        st.session_state["selected_customer"] = selected_rows[0]
        st.success(
            f"✅ Selected: {selected_rows[0].get('Name', 'Unknown')} (ID: {selected_rows[0].get('Customer ID', 'N/A')})"
        )
    else:
        st.session_state["selected_customer"] = None
        if len(display_df) > 0:
            st.info("ℹ️ Please select a customer from the table above to proceed.")




# --- Customer Details Tab ---
def customer_details_tab():
    selected_customer = st.session_state.get("selected_customer")
    if not selected_customer:
        st.warning(
            "No customer selected. Please go back and select a customer."
        )
        if st.button("Back to Search", key="back_to_search_from_details"):
            st.session_state["page"] = "search_customer"
            for key in [
                "search_results",
                "selected_customer",
                "last_customer_name",
                "last_email",
                "last_phone",
                "customer_name_input",
                "email_input",
                "phone_input",
                "nl_query_input",
                "generated_sql",
                "edited_sql_input",
                "sql_results",
                "search_method",
            ]:
                st.session_state.pop(key, None)
            st.rerun()
        return

    customer_id = selected_customer.get("Customer ID") or selected_customer.get("customer_id")
    if customer_id is None:
        st.error("Selected customer missing Customer ID. Please select again.")
        return

    rec_doc = get_recommendations_for_customer(customer_id)

    cols = st.columns([1, 1, 1])

    card_style = """
        background: white; 
        padding: 1rem; 
        border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px; 
        line-height: 1.4;
        width: 80%;
        height: 230px;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        box-sizing: border-box;
    """

    content_style = """
        flex-grow: 1;
        overflow-wrap: break-word;
    """

    image_style = """
        width: 80px;
        height: 80px;
        margin-left: 12px;
        flex-shrink: 0;
    """

    # --- KYC Card ---
    with cols[0]:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{content_style}">
                    <h3 style="color:#b22222; font-weight: 900; margin-bottom: 0.8rem;">Customer KYC</h3>
                    <p>👤 <strong>Name:</strong> {selected_customer.get("Name", "N/A")} (ID: {customer_id})</p>
                    <p>✉️ <strong>Email:</strong> {selected_customer.get("Email", "N/A")}</p>
                    <p>📞 <strong>Phone:</strong> {selected_customer.get("Phone", "N/A")}</p>
                    <p>🎂 <strong>Date of Birth:</strong> {selected_customer.get("DOB", "N/A")}</p>
                </div>
                <img src="https://img.icons8.com/color/96/id-verified.png" alt="KYC" style="{image_style}"/>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Customer Profile Card ---
    with cols[1]:
        profile = rec_doc.get("customer_profile") if rec_doc else None
        if profile:
            st.markdown(
                f"""
                <div style="{card_style}">
                    <div style="{content_style}">
                        <h3 style="color:#b22222; font-weight: 900; margin-bottom: 0.5rem;">Customer Profile</h3>
                        <p><strong>Annual Income:</strong> ${profile.get('annual_income', 'N/A'):,}</p>
                        <p><strong>Credit Score:</strong> {profile.get('credit_score', 'N/A')}</p>
                        <p><strong>Health Score:</strong> {profile.get('health_score', 'N/A')}</p>
                        <p><strong>Risk Category:</strong> {str(profile.get('risk_category', 'N/A')).capitalize()}</p>
                        <p><strong>Utilization Ratio:</strong> {profile.get('utilization_ratio', 'N/A')}</p>
                    </div>
                    <img src="https://img.icons8.com/color/96/business-report.png" alt="Profile" style="{image_style}"/>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No customer profile data available.")

    # --- Recommendations + Offer Button ---
    with cols[2]:
        st.markdown(
            """
            <h3 style="color:#b22222; font-weight: 450900; margin-bottom: 0.5rem;">Recommendations</h3>
            """,
            unsafe_allow_html=True,
        )

        if rec_doc and "recommendations" in rec_doc and rec_doc["recommendations"]:
            icon_map = {
                "credit_card": "💳",
                "savings_account": "🏦",
                "cd": "📄",
                "loan": "💰",
                "investment": "📈",
            }
            for rec in rec_doc["recommendations"]:
                icon = icon_map.get(rec.get("product_type", "").lower(), "🔹")
                product_name = rec.get("product_name", "Unknown Product")
                score = rec.get("score", "N/A")
                rank = rec.get("rank", "N/A")
                confidence = rec.get("confidence", "N/A")
                reason = rec.get("reason", "No explanation provided.")

                with st.expander(f"{icon} {product_name} (Score: {score})"):
                    st.markdown(
                        f"""
                        <p><strong>Rank:</strong> {rank}</p>
                        <p><strong>Confidence:</strong> {confidence}%</p>
                        <p><strong>Reason:</strong> {reason}</p>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No recommendations found for this customer.")

        # --- Offer Customer button below recommendations ---
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🎯 Offer Customer",
            key=f"offer_customer_{customer_id}",
            help="Create offer for this customer",
            use_container_width=True
        ):
            result = offer_customer(customer_id)
            if result:
                st.success(f"✅ Offer created successfully for customer {customer_id}!")
                st.info("Check the dw-backend for offer details.")

    # --- Chart or other results ---
    display_results_with_chart()

    # --- Back button ---
    if st.button("⬅️ Back to Search", key="back_button_from_details"):
        st.session_state["page"] = "search_customer"
        st.rerun()

# --- Main Customer Search Tab with toggle ---
def customer_search_tab():
    st.title("👥 Search Customers")

    prev_method = st.session_state.get("search_method_prev", "Manual")
    search_method = st.radio(
        "Choose search method:",
        ["Manual", "Natural Language Query"],
        key="search_method",
        horizontal=True,
    )

    # Clear results, selections, and generated query on mode change
    if search_method != prev_method:
        if search_method == "Manual":
            st.session_state["nlp_search_results"] = []
            st.session_state.pop("generated_sql", None)      # Clear generated SQL from NLP
            st.session_state.pop("nlp_query_input", None)   # Clear NLP input box if any
        else:
            st.session_state["manual_search_results"] = []
        st.session_state["selected_customer"] = None
        st.session_state["search_method_prev"] = search_method
        st.rerun()

    # Show search inputs and results based on mode
    if search_method == "Manual":
        manual_customer_search()
        display_search_results(mode="manual")
        next_btn_key = "next_button_manual"
    else:
        nlp_customer_search()
        display_search_results(mode="nlp")
        next_btn_key = "next_button_nlp"
    # Next button to go to details page if a customer is selected
    selected_customer = st.session_state.get("selected_customer")
    if selected_customer:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Next: View Details & Recommendations", key=next_btn_key):
                st.session_state["page"] = "customer_details"
                st.rerun()
    else:
        # Show this info only if there are search results to select from
        search_results = (
            st.session_state.get("manual_search_results", [])
            if search_method == "Manual"
            else st.session_state.get("nlp_search_results", [])
        )
       # if search_results:
       #     st.info("ℹ️ Please select a customer from the table above to proceed.")


# Now you can call it inside display_results_with_chart

# ---------------- show_bar_chart ----------------
def show_bar_chart(collection_name: str, title: str, key: str, width: int = 320):
    client = get_mongo_client()
    db = client.askdata_mongo
    collection = db[collection_name]

    pipeline = [
        {"$group": {"_id": "$date", "total_queries": {"$sum": "$query_count"}}},
        {"$sort": {"_id": 1}}
    ]
    results = list(collection.aggregate(pipeline))
    client.close()

    if not results:
        st.info(f"📭 No data available for {title}.")
        return

    df = pd.DataFrame(results)
    df.rename(columns={"_id": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)

    color_map = {
        "nlp_queries": "#2196F3",      # Customer
        "product_queries": "#FF9800",  # Product
    }
    bar_color = color_map.get(collection_name, "#4CAF50")

    fig = px.bar(
        df,
        x="date",
        y="total_queries",
        title=title,
        labels={"total_queries": "Number of Queries", "date": "Date"},
        text="total_queries",
    )

    fig.update_traces(
        textposition="outside",
        marker_color=bar_color,
        marker_line_color="rgba(0,0,0,0.5)",
        marker_line_width=1,
        opacity=0.9,
    )

    fig.update_layout(
        width=width,
        height=250,
        bargap=0.25,
        margin=dict(l=10, r=10, t=30, b=25),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#333", size=11),
        title=dict(font=dict(size=13, color="#b22222"))
    )

    st.plotly_chart(fig, use_container_width=False, key=key)


# ---------------- display_results_with_chart ----------------
def display_results_with_chart():
    st.markdown(
        "<h3 style='color:#b22222; text-align:left; margin-top:0.1rem;'>📊 KPI: Query Volume</h3>",
        unsafe_allow_html=True
    )

    # Spacer-based columns to keep cards side by side
    customer_col, product_col, spacer_right = st.columns([0.8, 0.8, 1], gap="small")

    card_width = 280

    # ---------------- Customer Queries Card ----------------
    with customer_col:
        st.markdown(
            f"""
            <div style="
                background-color: #fff;
                border-radius: 12px;
                padding: 0.5rem;
                width:{card_width}px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align:left;
                margin-bottom:0.5rem;
            ">
                <h4>Customer Queries</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        show_bar_chart(
            collection_name="nlp_queries",
            title="Customer Queries",
            key="chart_customer_queries",
            width=card_width
        )

    # ---------------- Product Queries Card ----------------
    with product_col:
        st.markdown(
            f"""
            <div style="
                background-color: #fff;
                border-radius: 12px;
                padding: 0.5rem;
                width:{card_width}px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align:left;
                margin-bottom:0.5rem;
            ">
                <h4>Product Queries</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        show_bar_chart(
            collection_name="product_queries",
            title="Product Queries",
            key="chart_product_queries",
            width=card_width
        )



def manual_product_search():
    product_name_input = st.session_state.get("product_name_input", "")
    product_type_input = st.session_state.get("product_type_input", "")
    product_category_input = st.session_state.get("product_category_input", "")

    with st.form("manual_product_search_form"):
        cols = st.columns(3)
        with cols[0]:
            product_name_input = st.text_input(
                "Product Name",
                key="product_name_input",
                placeholder="e.g. Platinum Credit Card",
                value=product_name_input,
            )
        with cols[1]:
            product_type_input = st.text_input(
                "Product Type",
                key="product_type_input",
                placeholder="e.g. credit_card, personal_loan",
                value=product_type_input,
            )
        with cols[2]:
            product_category_input = st.text_input(
                "Product Category",
                key="product_category_input",
                placeholder="e.g. premium, standard",
                value=product_category_input,
            )
        submitted = st.form_submit_button("Search")

    if submitted:
        st.session_state["last_product_name"] = product_name_input.strip()
        st.session_state["last_product_type"] = product_type_input.strip()
        st.session_state["last_product_category"] = product_category_input.strip()

        if not (
            st.session_state["last_product_name"]
            or st.session_state["last_product_type"]
            or st.session_state["last_product_category"]
        ):
            st.error("Please enter at least one search criteria.")
            st.session_state["manual_product_search_results"] = []
            st.session_state["selected_product"] = None
        else:
            try:
                params = {}
                if st.session_state["last_product_name"]:
                    params["product_name"] = st.session_state["last_product_name"]
                if st.session_state["last_product_type"]:
                    params["product_type"] = st.session_state["last_product_type"]
                if st.session_state["last_product_category"]:
                    params["product_category"] = st.session_state["last_product_category"]

                response = requests.get(
                    "http://askdata-api-backend:5004/products",
                    params=params,
                )
                if response.status_code == 200:
                    products = response.json()
                    if products:
                        st.session_state["manual_product_search_results"] = products
                        st.session_state["selected_product"] = None
                    else:
                        st.info(
                            "⚠️ No products matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["manual_product_search_results"] = []
                        st.session_state["selected_product"] = None
                else:
                    detail = response.json().get("detail", "")
                    if detail.lower() == "products not found":
                        st.warning(
                            "⚠️ No products matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["manual_product_search_results"] = []
                        st.session_state["selected_product"] = None
                    else:
                        st.error(f"Error: {detail or 'Unknown error'}")
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

def nlp_product_search():
    nl_query = st.text_area(
        "Enter your query in natural language",
        height=100,
        placeholder="e.g. Show me premium credit cards with cashback",
        key="nl_product_query_input",
    )

    generate_clicked = st.button("Generate SQL", key="generate_product_sql_button")

    if generate_clicked:
        if not nl_query.strip():
            st.error("Please enter a natural language query.")
            st.session_state.pop("generated_product_sql", None)
            st.session_state.pop("nlp_product_search_results", None)
            st.session_state["selected_product"] = None
        else:
            with st.spinner("Generating SQL..."):
                try:
                    response = requests.post(
                        "http://askdata-api-backend:5004/generate_product_sql",
                        json={"nl_query": nl_query},
                    )
                    response.raise_for_status()
                    sql_query = response.json().get("sql", "")
                    if sql_query:
                        st.session_state["generated_product_sql"] = sql_query
                        st.success("✅ SQL query generated successfully!")
                        st.session_state.pop("nlp_product_search_results", None)
                        st.session_state["selected_product"] = None
                    else:
                        st.info("⚠️ No SQL query returned from backend.")
                        st.session_state.pop("generated_product_sql", None)
                        st.session_state.pop("nlp_product_search_results", None)
                        st.session_state["selected_product"] = None
                except Exception as e:
                    st.error(f"Error generating SQL: {e}")
                    st.session_state.pop("generated_product_sql", None)
                    st.session_state.pop("nlp_product_search_results", None)
                    st.session_state["selected_product"] = None

    sql_query = st.session_state.get("generated_product_sql", "")

    if sql_query:
        edited_sql = st.text_area(
            "Edit SQL if needed",
            value=sql_query,
            height=150,
            key="edited_product_sql_input",
        )

        run_clicked = st.button("Run SQL", key="run_product_sql_button")

        if run_clicked:
            if not edited_sql.strip():
                st.error("SQL query cannot be empty.")
                st.session_state.pop("nlp_product_search_results", None)
                st.session_state["selected_product"] = None
            else:
                # Clean SQL for safe execution
                cleaned_sql = " ".join(edited_sql.strip().rstrip(";").splitlines())
                payload = {"sql_query": cleaned_sql}
                with st.spinner("Running SQL query..."):
                    try:
                        response = requests.post(
                            "http://askdata-api-backend:5004/run_custom_product_query",
                            json=payload,
                            headers={"Content-Type": "application/json"},
                        )
                        response.raise_for_status()
                        results = response.json().get("results", [])
                        if results:
                            st.session_state["nlp_product_search_results"] = results
                            st.session_state["selected_product"] = None
                        else:
                            st.warning(
                                "⚠️ No products matched your search criteria. Please try different filters or check for typos."
                            )
                            st.session_state["nlp_product_search_results"] = []
                            st.session_state["selected_product"] = None
                    except Exception as e:
                        st.error(f"Error running SQL query: {e}")
                        st.session_state.pop("nlp_product_search_results", None)
                        st.session_state["selected_product"] = None

def display_product_search_results(mode="manual"):
    # --- Fetch data from session ---
    if mode == "manual":
        products = st.session_state.get("manual_product_search_results", [])
    else:
        products = st.session_state.get("nlp_product_search_results", [])
        nlp_query_text = st.session_state.get("current_product_nlp_query", "")
        if nlp_query_text:
            log_product_query_to_mongo(nlp_query_text)

    if not products:
        st.info("No results to display yet. Please perform a search.")
        return

    # --- Deduplicate keys in each dict to avoid DataFrame issues ---
    cleaned_products = []
    for p in products:
        new_p = {}
        for k, v in p.items():
            if k not in new_p:
                new_p[k] = v
            else:
                count = 1
                new_k = f"{k}_{count}"
                while new_k in new_p:
                    count += 1
                    new_k = f"{k}_{count}"
                new_p[new_k] = v
        cleaned_products.append(new_p)

    # --- Convert to DataFrame ---
    df = pd.DataFrame(cleaned_products)
    if df.empty:
        st.info("No valid product records found.")
        return

    # --- Ensure Product ID and Name exist ---
    if "product_id" not in df.columns:
        df.insert(0, "product_id", "N/A")
    if "product_name" not in df.columns:
        df.insert(1, "product_name", "Unknown Product")

    # --- Determine display columns ---
    predefined_cols = [
        "product_id",
        "product_name",
        "product_type" if "product_type" in df.columns else None,
        "product_category" if "product_category" in df.columns else None,
        "interest_rate" if "interest_rate" in df.columns else None,
        "credit_limit_min" if "credit_limit_min" in df.columns else None,
        "credit_limit_max" if "credit_limit_max" in df.columns else None,
        "annual_fee" if "annual_fee" in df.columns else None,
    ]
    predefined_cols = [c for c in predefined_cols if c]

    # --- Include any extra NLP-returned columns dynamically ---
    other_cols = [c for c in df.columns if c not in predefined_cols]
    display_cols = predefined_cols + other_cols

    display_df = df[display_cols].rename(
        columns={
            "product_id": "Product ID",
            "product_name": "Product Name",
            "product_type": "Type",
            "product_category": "Category",
            "interest_rate": "Interest Rate",
            "credit_limit_min": "Credit Limit Min",
            "credit_limit_max": "Credit Limit Max",
            "annual_fee": "Annual Fee",
        }
    )

    # --- Pin Product ID/Name first ---
    cols = list(display_df.columns)
    pinned = ["Product ID", "Product Name"]
    other_cols = [c for c in cols if c not in pinned]
    display_df = display_df[pinned + other_cols]

    # --- Ensure unique column names (after renaming) ---
    cols = pd.Series(display_df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_idx = cols[cols == dup].index
        for i, idx in enumerate(dup_idx):
            if i == 0:
                continue
            cols[idx] = f"{cols[idx]}_{i}"
    display_df.columns = cols

    # --- AgGrid Setup ---
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True,
        suppressRowClickSelection=True,
    )

    # --- Pagination size selectbox ---
    page_size = st.selectbox("Rows per page:", [10, 20, 50, 100], index=1)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)

    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        cellStyle=JsCode(
            """
            function(params) {
                if (params.node.isSelected()) {
                    return {'backgroundColor': '#f7e6ff'};
                } else if (params.rowIndex % 2 === 0) {
                    return {'backgroundColor': '#f9f9f9'};
                }
            }
            """
        ),
    )

    # --- Column headers with emojis ---
    header_mapping = {
        "Product Name": "🏷️ Product Name",
        "Type": "🗂 Type",
        "Category": "📦 Category",
        "Interest Rate": "💲 Interest Rate",
        "Annual Fee": "💸 Annual Fee",
        "Credit Limit Min": "🔢 Credit Limit Min",
        "Credit Limit Max": "🔢 Credit Limit Max",
    }
    for col in display_df.columns:
        if col in header_mapping:
            gb.configure_column(col, header_name=header_mapping[col], tooltipField=col)
        else:
            gb.configure_column(col, tooltipField=col)

    # --- Dynamic key to refresh AgGrid when columns change ---
    query_columns = "_".join(sorted(display_df.columns))
    grid_key = f"aggrid_product_{mode}_{hashlib.md5(query_columns.encode()).hexdigest()}"

    # --- Display AgGrid ---
    grid_response = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="material",
        height=500,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        reload_data=True,
        key=grid_key,
    )

    # --- Handle selection ---
    selected_rows = grid_response.get("selected_rows")
    if selected_rows is None:
        selected_rows = []
    elif isinstance(selected_rows, pd.DataFrame):
        selected_rows = selected_rows.to_dict(orient="records")

    if selected_rows:
        st.session_state["selected_product"] = selected_rows[0]
        st.success(
            f"✅ Selected: {selected_rows[0].get('Product Name')} (ID: {selected_rows[0].get('Product ID')})"
        )
    else:
        st.session_state["selected_product"] = None
        st.info("ℹ️ Please select a product from the table above to proceed.")


def manual_product_search():
    product_name_input = st.session_state.get("product_name_input", "")
    product_type_input = st.session_state.get("product_type_input", "")
    product_category_input = st.session_state.get("product_category_input", "")

    with st.form("manual_product_search_form"):
        cols = st.columns(3)
        with cols[0]:
            product_name_input = st.text_input(
                "Product Name",
                key="product_name_input",
                placeholder="e.g. Platinum Credit Card",
                value=product_name_input,
            )
        with cols[1]:
            product_type_input = st.text_input(
                "Product Type",
                key="product_type_input",
                placeholder="e.g. credit_card, personal_loan",
                value=product_type_input,
            )
        with cols[2]:
            product_category_input = st.text_input(
                "Product Category",
                key="product_category_input",
                placeholder="e.g. premium, standard",
                value=product_category_input,
            )
        submitted = st.form_submit_button("Search")

    if submitted:
        st.session_state["last_product_name"] = product_name_input.strip()
        st.session_state["last_product_type"] = product_type_input.strip()
        st.session_state["last_product_category"] = product_category_input.strip()

        if not (
            st.session_state["last_product_name"]
            or st.session_state["last_product_type"]
            or st.session_state["last_product_category"]
        ):
            st.error("Please enter at least one search criteria.")
            st.session_state["manual_product_search_results"] = []
            st.session_state["selected_product"] = None
        else:
            try:
                params = {}
                if st.session_state["last_product_name"]:
                    params["product_name"] = st.session_state["last_product_name"]
                if st.session_state["last_product_type"]:
                    params["product_type"] = st.session_state["last_product_type"]
                if st.session_state["last_product_category"]:
                    params["product_category"] = st.session_state["last_product_category"]

                response = requests.get(
                    "http://askdata-api-backend:5004/products",
                    params=params,
                )
                if response.status_code == 200:
                    products = response.json()
                    if products:
                        st.session_state["manual_product_search_results"] = products
                        st.session_state["selected_product"] = None
                    else:
                        st.info(
                            "⚠️ No products matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["manual_product_search_results"] = []
                        st.session_state["selected_product"] = None
                else:
                    detail = response.json().get("detail", "")
                    if detail.lower() == "products not found":
                        st.warning(
                            "⚠️ No products matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["manual_product_search_results"] = []
                        st.session_state["selected_product"] = None
                    else:
                        st.error(f"Error: {detail or 'Unknown error'}")
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

def nlp_product_search():
    nl_query = st.text_area(
        "Enter your query in natural language",
        height=100,
        placeholder="e.g. Show me premium credit cards with cashback",
        key="nl_product_query_input",
    )

    generate_clicked = st.button("Generate SQL", key="generate_product_sql_button")

    if generate_clicked:
        if not nl_query.strip():
            st.error("Please enter a natural language query.")
            st.session_state.pop("generated_product_sql", None)
            st.session_state.pop("nlp_product_search_results", None)
            st.session_state["selected_product"] = None
        else:
            # --- Log NLP product query for KPI chart ---
            current_user = st.session_state.get("username", "unknown")
            log_product_query_to_mongo(nl_query, current_user)

            with st.spinner("Generating SQL..."):
                try:
                    response = requests.post(
                        "http://askdata-api-backend:5004/generate_product_sql",
                        json={"nl_query": nl_query},
                    )
                    response.raise_for_status()
                    sql_query = response.json().get("sql", "")
                    if sql_query:
                        st.session_state["generated_product_sql"] = sql_query
                        st.success("✅ SQL query generated successfully!")
                        st.session_state.pop("nlp_product_search_results", None)
                        st.session_state["selected_product"] = None
                    else:
                        st.info("⚠️ No SQL query returned from backend.")
                        st.session_state.pop("generated_product_sql", None)
                        st.session_state.pop("nlp_product_search_results", None)
                        st.session_state["selected_product"] = None
                except Exception as e:
                    st.error(f"Error generating SQL: {e}")
                    st.session_state.pop("generated_product_sql", None)
                    st.session_state.pop("nlp_product_search_results", None)
                    st.session_state["selected_product"] = None

    sql_query = st.session_state.get("generated_product_sql", "")
    if sql_query:
        edited_sql = st.text_area(
        "Edit SQL if needed",
        value=sql_query,
        height=150,
        key="edited_product_sql_input",
    )

    run_clicked = st.button("Run SQL", key="run_product_sql_button")
    if run_clicked:
        if not edited_sql.strip():
            st.error("SQL query cannot be empty.")
            st.session_state.pop("nlp_product_search_results", None)
            st.session_state["selected_product"] = None
        else:
            # Prepare payload safely for multi-line SQL
            edited_sql_safe = " ".join(edited_sql.splitlines())
            payload = {"sql_query": edited_sql_safe}
            with st.spinner("Running SQL query..."):
                try:
                    response = requests.post(
                        "http://askdata-api-backend:5004/run_custom_product_query",
                        json=payload,  # ensure JSON embed
                        headers={"Content-Type": "application/json"}  # explicit header
                    )
                    response.raise_for_status()
                    results = response.json().get("results", [])
                    if results:
                        st.session_state["nlp_product_search_results"] = results
                        st.session_state["selected_product"] = None
                    else:
                        st.warning(
                            "⚠️ No products matched your search criteria. Please try different filters or check for typos."
                        )
                        st.session_state["nlp_product_search_results"] = []
                        st.session_state["selected_product"] = None
                except requests.HTTPError as http_err:
                    st.error(f"HTTP error running SQL query: {http_err}")
                except Exception as e:
                    st.error(f"Error running SQL query: {e}")
                    st.session_state.pop("nlp_product_search_results", None)
                    st.session_state["selected_product"] = None
      
        
def display_product_search_results(mode="manual"):
    # --- Fetch data from session ---
    if mode == "manual":
        products = st.session_state.get("manual_product_search_results", [])
    else:
        products = st.session_state.get("nlp_product_search_results", [])
        nlp_query_text = st.session_state.get("current_product_nlp_query", "")
        if nlp_query_text:
            # Optional: log NLP query to Mongo or analytics
            pass

    if not products:
        st.info("No results to display yet. Please perform a search.")
        return

    df = pd.DataFrame(products)

    if df.empty:
        st.info("No valid product records found.")
        return

    # --- Convert all values to strings to avoid serialization issues ---
    df = df.astype(str)
    
    # --- Ensure unique column names ---
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_idx = cols[cols == dup].index
        for i, idx in enumerate(dup_idx):
            if i == 0:
                continue
            cols[idx] = f"{cols[idx]}_{i}"
    df.columns = cols

    # --- Column mapping for display ---
    column_mapping = {
        "product_id": "Product ID",
        "product_name": "🏷️ Product Name",
        "product_type": "🗂 Type",
        "product_category": "📦 Category",
        "interest_rate": "💲 Interest Rate",
        "credit_limit_min": "🔢 Credit Limit Min",
        "credit_limit_max": "🔢 Credit Limit Max",
        "annual_fee": "💸 Annual Fee",
        "rewards_program": "🎁 Rewards",
        "benefits": "✨ Benefits",
        "eligibility_criteria": "✅ Eligibility",
        "is_active": "Active",
    }

    display_cols = [col for col in column_mapping if col in df.columns]
    display_df = df[display_cols].rename(columns={k: column_mapping[k] for k in display_cols})

    # --- AgGrid setup ---
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True if "Product ID" in display_df.columns else False,
        suppressRowClickSelection=True,
    )
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        cellStyle=JsCode(
            """
            function(params) {
                if (params.node.isSelected()) {
                    return {'backgroundColor': '#f7e6ff'};
                } else if (params.rowIndex % 2 === 0) {
                    return {'backgroundColor': '#f9f9f9'};
                }
            }
            """
        ),
    )

    gb.configure_grid_options(domLayout='autoHeight', suppressHorizontalScroll=False)
    gb.configure_grid_options(ensureDomOrder=True)
    gb.configure_grid_options(allowHorizontalScroll=True)

    # --- Dynamic key for AgGrid refresh ---
    query_columns = "_".join(sorted(display_df.columns))
    grid_key = f"aggrid_product_{mode}_{hashlib.md5(query_columns.encode()).hexdigest()}"

    # --- Display AgGrid ---
    grid_response = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="material",
        height=480,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        reload_data=True,
        key=grid_key,
    )

    # --- Handle selection safely ---
    selected_rows = grid_response.get("selected_rows")
    if selected_rows is None:
        selected_rows = []
    elif isinstance(selected_rows, pd.DataFrame):
        selected_rows = selected_rows.to_dict(orient="records")

    if selected_rows and "Product ID" in selected_rows[0]:
        st.session_state["selected_product"] = selected_rows[0]
        st.success(
            f"✅ Selected: {selected_rows[0].get('🏷️ Product Name', 'Unknown')} "
            f"(ID: {selected_rows[0].get('Product ID', 'N/A')})"
        )
    else:
        st.session_state["selected_product"] = None
        if len(display_df) > 0:
            st.info("ℹ️ Please select a product from the table above to proceed.")


def product_details_tab():
    selected_product = st.session_state.get("selected_product")
    if not selected_product:
        st.warning("No product selected. Please go back and select a product.")
        if st.button("Back to Product Search", key="back_to_product_search_from_details"):
            st.session_state["page"] = "search_product"
            for key in [
                "manual_product_search_results",
                "nlp_product_search_results",
                "selected_product",
                "last_product_name",
                "last_product_type",
                "last_product_category",
                "product_name_input",
                "product_type_input",
                "product_category_input",
                "generated_product_sql",
                "edited_product_sql_input",
            ]:
                st.session_state.pop(key, None)
            st.rerun()
        return

    product_id = selected_product.get("Product ID") or selected_product.get("product_id")
    if product_id is None:
        st.error("Selected product missing Product ID. Please select again.")
        return

    card_style = """
        background: white; 
        padding: 1rem; 
        border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px; 
        line-height: 1.4;
        width: 100%;
        height: auto;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    """
    content_style = "flex-grow: 1; overflow-wrap: break-word;"
    image_style = "width: 80px; height: 80px; margin-top: 12px;"

    # --- Three columns for the cards ---
    cols = st.columns(3)

    # --- Product Details ---
    with cols[0]:
        st.markdown(
            f"""
            <div style="{card_style}">
                <h3 style="color:#b22222; font-weight: 900; margin-bottom: 0.8rem;"> 🏦 Product Details</h3>
                <p><strong>Name:</strong> {selected_product.get('🏷️ Product Name', 'N/A')} (ID: {product_id})</p>
                <p>🗂 <strong>Type:</strong> {selected_product.get('🗂 Type', 'N/A')}</p>
                <p>📦 <strong>Category:</strong> {selected_product.get('📦 Category', 'N/A')}</p>
                <p>💲 <strong>Interest Rate:</strong> {selected_product.get('💲 Interest Rate', 'N/A')}</p>
                <p>💸 <strong>Annual Fee:</strong> {selected_product.get('💸 Annual Fee', 'N/A')}</p>
                <p>✅ <strong>Active:</strong> {selected_product.get('Active', 'N/A')}</p>
                <p>🔹<strong>Credit Limit Min:</strong> {selected_product.get('🔢 Credit Limit Min', 'N/A')}</p>
                <p>🔺<strong>Credit Limit Max:</strong> {selected_product.get('🔢 Credit Limit Max', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- More Info ---
    with cols[1]:
        st.markdown(
            f"""
            <div style="{card_style}">
                <h3 style="color:#b22222; font-weight: 900; margin-bottom: 0.8rem;"> ✨ Key Features</h3>
                <p><strong>Minimum Income Required:</strong> {selected_product.get('Minimum Income Required', 'N/A')}</p>
                <p><strong>Minimum Credit Score:</strong> {selected_product.get('Minimum Credit Score', 'N/A')}</p>
                <p><strong>Maximum Debt to Income:</strong> {selected_product.get('Maximum Debt to Income', 'N/A')}</p>
                <p><strong>Rewards Program:</strong> {selected_product.get('🎁 Rewards', 'N/A')}</p>
                <p><strong>Benefits:</strong> {selected_product.get('✨ Benefits', 'N/A')}</p>
                <p><strong>Eligibility Criteria:</strong> {selected_product.get('✅ Eligibility', 'N/A')}</p>
                <p><strong>Created At:</strong> {selected_product.get('Created At', 'N/A')}</p>
                <p><strong>Updated At:</strong> {selected_product.get('Updated At', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Customer Relevance ---
    with cols[2]:
        st.markdown(
            f"""
            <div style="{card_style}">
                <h3 style="color:#b22222; font-weight: 900; margin-bottom: 0.8rem;"> 👤 Customer Relevance</h3>
                <p>Coming soon: Personalized customer relevance insights and recommendations for this product.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Back button ---
    if st.button("⬅️ Back to Product Search", key="back_button_from_product_details"):
        st.session_state["page"] = "search_product"
        st.rerun()


def product_search_tab():
    st.title("🏦 Search Products")

    prev_method = st.session_state.get("product_search_method_prev", "Manual")
    search_method = st.radio(
        "Choose search method:",
        ["Manual", "Natural Language Query"],
        key="product_search_method",
        horizontal=True,
    )

    # Clear results, selections, and generated query on mode change
    if search_method != prev_method:
        if search_method == "Manual":
            st.session_state["nlp_product_search_results"] = []
            st.session_state.pop("generated_product_sql", None)
            st.session_state.pop("nl_product_query_input", None)
        else:
            st.session_state["manual_product_search_results"] = []
        st.session_state["selected_product"] = None
        st.session_state["product_search_method_prev"] = search_method
        st.rerun()

    # Show search inputs and results based on mode
    if search_method == "Manual":
        manual_product_search()
        display_product_search_results(mode="manual")
        next_btn_key = "next_button_product_manual"
    else:
        nlp_product_search()
        display_product_search_results(mode="nlp")
        next_btn_key = "next_button_product_nlp"

    # Next button to go to details page if a product is selected
    selected_product = st.session_state.get("selected_product")
    if selected_product:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Next: View Product Details", key=next_btn_key):
                st.session_state["page"] = "product_details"
                st.rerun()
    else:
        search_results = (
            st.session_state.get("manual_product_search_results", [])
            if search_method == "Manual"
            else st.session_state.get("nlp_product_search_results", [])
        )
        # if search_results:
        #     st.info("ℹ️ Please select a product from the table above

def log_query_to_mongo(query_text: str):
    """
    Log a user query to MongoDB by incrementing the query_count for the current date.
    """
    client = get_mongo_client()
    db = client.askdata_mongo
    collection = db.nlp_queries

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    collection.update_one(
        {"date": today_str},
        {
            "$inc": {"query_count": 1},
            "$setOnInsert": {"date": today_str}
        },
        upsert=True
    )

    client.close()
    
def log_product_query_to_mongo(query_text: str, user: str = "unknown"):
    """
    Log a product query to MongoDB by incrementing the query_count for the current date and query text.
    """
    client = get_mongo_client()
    db = client.askdata_mongo
    collection = db.product_queries

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    collection.update_one(
        {"date": today_str, "query": query_text, "user": user},
        {
            "$inc": {"query_count": 1},
            "$setOnInsert": {"date": today_str, "timestamp": datetime.utcnow()}
        },
        upsert=True
    )
    client.close()


    
# --- Main app ---
def main():
    token = authenticate_user()
    if not token:
        return

    user_info = get_user_info_from_token(token)
    if not user_info:
        st.error("Failed to decode user information from token.")
        return

    show_fixed_branding()
    if show_user_info_and_logout(user_info):
        st.session_state.clear()
        st.rerun()

    page = st.session_state.get("page", "search_customer")

    with st.container():
        tabs = st.tabs(
            [
                "Search by Customer",
                "Search by Product",
            ]
        )
        if page == "search_customer":
            with tabs[0]:
                customer_search_tab()
            with tabs[1]:
                product_search_tab()
        elif page == "customer_details":
            with tabs[0]:
                customer_details_tab()
                #display_results_with_chart()
            with tabs[1]:
                product_search_tab()
        elif page == "product_details":
            with tabs[0]:
                customer_search_tab()
            with tabs[1]:
                product_details_tab()
        else:
            with tabs[0]:
                customer_search_tab()
            with tabs[1]:
                product_search_tab()


if __name__ == "__main__":
    main()
    