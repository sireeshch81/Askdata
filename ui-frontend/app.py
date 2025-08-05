import streamlit as st
import requests
import jwt
from keycloak import KeycloakOpenID
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import pandas as pd
import os

st.set_page_config(layout="wide")


def show_fixed_branding():
    cols = st.columns([1, 3])  # narrow col for logo, wider for text

    with cols[0]:
        st.image("cgilogo.png", width=120)  # Use st.image for reliable loading

    with cols[1]:
        st.markdown(
            """
            <h1 style="color:#b22222; font-weight: 900; margin-bottom: 0; 
                       font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                AskData
            </h1>
            <p style="font-style: italic; color: #666; font-size: 18px; margin-top: 4px;
                      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Ask Naturally. Understand Instantly.
            </p>
            """,
            unsafe_allow_html=True,
        )


# --- CSS Styling ---
st.markdown(
    """
    <style>
    /* User info container fixed top-right */
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

    /* Main content container */
    .app-content {
        margin-top: 180px;
        margin-left: 18px;
        margin-right: 18px;
        max-width: 1150px;
        margin-left: auto;
        margin-right: auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Custom tabs */
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

    /* Login form container and input width */
    .login-form-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 100px;
    }
    .login-form-container input[type="text"],
    .login-form-container input[type="password"] {
        max-width: 180px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
        font-size: 14px !important;
        padding: 6px 10px !important;
        border-radius: 5px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Keycloak config
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


def authenticate_user():
    if "token" not in st.session_state:
        # Clear relevant keys on logout or first load
        for key in [
            "search_results",
            "selected_customer",
            "last_customer_name",
            "last_email",
            "last_phone",
            "customer_name_input",
            "email_input",
            "phone_input",
        ]:
            st.session_state.pop(key, None)

        st.markdown('<div class="login-form-container">', unsafe_allow_html=True)

        st.title("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            try:
                token = keycloak_openid.token(username, password)
                st.session_state["token"] = token
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")

        return None
    else:
        return st.session_state.get("token", None)


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


def customer_search_tab():
    token = st.session_state["token"]

    customer_name_input = st.session_state.get("customer_name_input", "")
    email_input = st.session_state.get("email_input", "")
    phone_input = st.session_state.get("phone_input", "")

    st.title("🔍 Search Customers")

    with st.form("search_form"):
        cols = st.columns(3)
        with cols[0]:
            customer_name_input = st.text_input(
                "Customer Name",
                key="customer_name_input",
                placeholder="e.g. John Doe",
            )
        with cols[1]:
            email_input = st.text_input(
                "Email", key="email_input", placeholder="e.g. john@example.com"
            )
        with cols[2]:
            phone_input = st.text_input(
                "Phone", key="phone_input", placeholder="e.g. +1 234 567 8900"
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
        else:
            try:
                params = {}
                if st.session_state["last_customer_name"]:
                    params["customer_name"] = st.session_state[
                        "last_customer_name"
                    ]
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
                        st.session_state["search_results"] = customers
                        st.session_state["selected_customer"] = None
                    else:
                        st.info(
                            "No customers matched your search criteria. Please try different keywords."
                        )
                        st.session_state["search_results"] = []
                        st.session_state["selected_customer"] = None
                else:
                    detail = response.json().get("detail", "")
                    if detail.lower() in [
                        "customers not found",
                        "customer not found",
                        "no customers found",
                    ]:
                        st.info(
                            "No customers matched your search criteria. Please try different keywords."
                        )
                        st.session_state["search_results"] = []
                        st.session_state["selected_customer"] = None
                    else:
                        st.error(f"Error: {detail or 'Unknown error'}")
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

    customers = st.session_state.get("search_results", [])
    if customers:
        df = pd.DataFrame(customers)
        df["Full Name"] = df["first_name"] + " " + df["last_name"]
        display_df = df[
            ["customer_id", "Full Name", "email", "phone", "date_of_birth"]
        ].rename(
            columns={
                "customer_id": "Customer ID",
                "Full Name": "Name",
                "email": "Email",
                "phone": "Phone",
                "date_of_birth": "DOB",
            }
        )

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_selection(
            selection_mode="single",
            use_checkbox=True,
            suppressRowClickSelection=True,
        )
        gb.configure_pagination(paginationAutoPageSize=True)
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
        gb.configure_column(
            "Email", header_name="📧 Email", tooltipField="Email"
        )
        gb.configure_column(
            "Phone", header_name="📞 Phone", tooltipField="Phone"
        )
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

        grid_options = gb.build()

        grid_response = AgGrid(
            display_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="material",
            height=480,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
        )

        selected_rows = grid_response.get("selected_rows")
        if selected_rows is None:
            selected_rows = []
        elif isinstance(selected_rows, pd.DataFrame):
            selected_rows = selected_rows.to_dict(orient="records")

        if len(selected_rows) > 0:
            selected = selected_rows[0]
            st.session_state["selected_customer"] = selected
            st.success(
                f"✅ Selected: {selected.get('Name')} (ID: {selected.get('Customer ID')})"
            )
        else:
            st.session_state["selected_customer"] = None

    selected_customer = st.session_state.get("selected_customer")
    if selected_customer:
        st.markdown("----")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "➡️ Next: View Details & Recommendations",
                key="next_button_customer",
            ):
                st.session_state["page"] = "customer_details"
                st.rerun()
    else:
        st.info("ℹ️ Please select a customer from the table above to proceed.")


def customer_details_tab():
    token = st.session_state["token"]

    selected_customer = st.session_state.get("selected_customer")
    if not selected_customer:
        st.warning(
            "No customer selected. Please go back and select a customer."
        )
        if st.button("Back to Search", key="back_to_search_from_details"):
            # Reset to empty search page:
            st.session_state["page"] = "search_customer"
            # Clear all search inputs, results, selections:
            for key in [
                "search_results",
                "selected_customer",
                "last_customer_name",
                "last_email",
                "last_phone",
                "customer_name_input",
                "email_input",
                "phone_input",
            ]:
                st.session_state.pop(key, None)
            st.rerun()
        return

    st.title("Customer Details & Recommendations")

    # Display customer details
    st.subheader(
        f"Customer: {selected_customer['Name']} (ID: {selected_customer['Customer ID']})"
    )
    st.write(f"Email: {selected_customer['Email']}")
    st.write(f"Phone: {selected_customer['Phone']}")
    st.write(f"Date of Birth: {selected_customer['DOB']}")

    # Placeholder for recommendations logic
    st.markdown("### Recommendations")
    st.info(
        "Here you can display product or financial recommendations for the selected customer."
    )

    if st.button("Back to Search", key="back_to_search_button"):
        # Reset to empty search page:
        st.session_state["page"] = "search_customer"
        # Clear all search inputs, results, selections:
        for key in [
            "search_results",
            "selected_customer",
            "last_customer_name",
            "last_email",
            "last_phone",
            "customer_name_input",
            "email_input",
            "phone_input",
        ]:
            st.session_state.pop(key, None)
        st.rerun()



def product_search_tab():
    st.title("🔎 Search Products")

    with st.form("product_search_form"):
        product_name = st.text_input(
            "Product Name", placeholder="Enter product name or keyword"
        )
        submitted = st.form_submit_button("Search")

    if submitted:
        st.success(
            f"Search for product: {product_name} (This is a placeholder)"
        )


def main():
    # Show branding fixed at top (once)
    show_fixed_branding()

    if "page" not in st.session_state:
        st.session_state["page"] = "search_customer"
    if "search_mode" not in st.session_state:
        st.session_state["search_mode"] = "search_customer"

    token = authenticate_user()
    if not token:
        return

    user_info = get_user_info_from_token(token)
    if show_user_info_and_logout(user_info, button_key="logout_button"):
        # Clear all session state and rerun on logout
        for key in list(st.session_state.keys()):
            st.session_state.pop(key)
        st.rerun()

    st.markdown('<div class="app-content">', unsafe_allow_html=True)

    # Create native tabs
    tab_customer, tab_product = st.tabs(
        ["Search by Customer", "Search by Product"]
    )

    with tab_customer:
        st.session_state["search_mode"] = "search_customer"
        if st.session_state["page"] == "search_customer":
            customer_search_tab()
        elif st.session_state["page"] == "customer_details":
            customer_details_tab()

    with tab_product:
        st.session_state["search_mode"] = "search_product"
        if st.session_state["page"] in ["search_customer", "search_product"]:
            product_search_tab()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()