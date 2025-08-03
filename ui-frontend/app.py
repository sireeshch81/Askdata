import streamlit as st
import requests
import jwt
from keycloak import KeycloakOpenID
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import pandas as pd

st.set_page_config(layout="wide")

# Fix placeholder text color for gray backgrounds
st.markdown(
    """
    <style>
    ::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }
    input::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }
    input::-moz-placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }
    input:-ms-input-placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }
    input::-ms-input-placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Keycloak Configuration
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
    if 'token' not in st.session_state:
        for key in ['search_results', 'selected_customer', 'last_customer_name', 'last_email', 'last_phone',
                    'customer_name_input', 'email_input', 'phone_input']:
            st.session_state.pop(key, None)

        st.title("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            try:
                token = keycloak_openid.token(username, password)
                st.session_state['token'] = token
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
        return None
    else:
        return st.session_state.get('token', None)

def get_user_info_from_token(token):
    access_token_str = token.get('access_token')
    if not access_token_str:
        return None
    try:
        decoded_token = jwt.decode(access_token_str, options={"verify_signature": False})
        return {
            "name": decoded_token.get("name", "N/A"),
            "email": decoded_token.get("email", "N/A"),
            "realm_roles": decoded_token.get("realm_access", {}).get("roles", []),
            "client_roles": decoded_token.get("resource_access", {}).get(KEYCLOAK_CLIENT_ID, {}).get("roles", [])
        }
    except Exception as e:
        st.error(f"Token error: {e}")
        return None

def main():
    token = authenticate_user()
    if not token:
        return

    user_info = get_user_info_from_token(token)
    if not user_info:
        st.warning("Could not decode user info. Try logging in again.")
        return

    # User header & logout button UI
    st.markdown("""
        <style>
        .header-container {
            position: fixed;
            top: 0; left: 0; right: 0;
            background-color: white;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
            font-size: 14px;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 20px;
            z-index: 9999;
        }
        .user-info {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            line-height: 1.1;
        }
        .logout-button > button {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            margin-left: 10px;
        }
        .logout-button > button:hover {
            background-color: #218838;
        }
        .app-content {
            margin-top: 70px;
        }
        </style>
        """, unsafe_allow_html=True)

    cols = st.columns([1, 1, 1])
    with cols[0]:
        st.write("")
    with cols[1]:
        st.markdown(f"""
            <div class="user-info">
                <div>👤 <b>{user_info['name']}</b></div>
                <div>✉️ {user_info['email']}</div>
            </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        if st.button("Logout"):
            for key in ['token', 'search_results', 'selected_customer', 'last_customer_name', 'last_email', 'last_phone',
                        'customer_name_input', 'email_input', 'phone_input']:
                st.session_state.pop(key, None)
            st.rerun()

    # --- SEARCH FUNCTIONALITY ---

    # Initialize last search parameters in session_state
    if 'last_customer_name' not in st.session_state:
        st.session_state['last_customer_name'] = ""
    if 'last_email' not in st.session_state:
        st.session_state['last_email'] = ""
    if 'last_phone' not in st.session_state:
        st.session_state['last_phone'] = ""

    customer_name_input = st.session_state.get('customer_name_input', "")
    email_input = st.session_state.get('email_input', "")
    phone_input = st.session_state.get('phone_input', "")

    # Clear search results if any input changes before submitting
    if (
        customer_name_input != st.session_state['last_customer_name'] or
        email_input != st.session_state['last_email'] or
        phone_input != st.session_state['last_phone']
    ):
        st.session_state['search_results'] = []
        st.session_state['selected_customer'] = None

    st.markdown('<div class="app-content">', unsafe_allow_html=True)
    st.title("🔍 Search Customers")

    with st.form("search_form"):
        cols = st.columns(3)
        with cols[0]:
            customer_name_input = st.text_input(
                "Customer Name",
                key='customer_name_input',
                placeholder="e.g. John Doe"
            )
        with cols[1]:
            email_input = st.text_input(
                "Email",
                key='email_input',
                placeholder="e.g. john@example.com"
            )
        with cols[2]:
            phone_input = st.text_input(
                "Phone",
                key='phone_input',
                placeholder="e.g. +1 234 567 8900"
            )
        submitted = st.form_submit_button("Search")

    if submitted:
        st.session_state['last_customer_name'] = customer_name_input.strip()
        st.session_state['last_email'] = email_input.strip()
        st.session_state['last_phone'] = phone_input.strip()

        if not (st.session_state['last_customer_name'] or st.session_state['last_email'] or st.session_state['last_phone']):
            st.error("Please enter at least one search criteria.")
        else:
            try:
                params = {}
                if st.session_state['last_customer_name']:
                    params['customer_name'] = st.session_state['last_customer_name']
                if st.session_state['last_email']:
                    params['email'] = st.session_state['last_email']
                if st.session_state['last_phone']:
                    params['phone'] = st.session_state['last_phone']

                response = requests.get(
                    "http://askdata-api-backend:5004/customer_detail",
                    params=params
                )
                if response.status_code == 200:
                    customers = response.json()
                    if customers:
                        st.session_state['search_results'] = customers
                        st.session_state['selected_customer'] = None
                    else:
                        st.warning("No customers found.")
                        st.session_state['search_results'] = []
                        st.session_state['selected_customer'] = None
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

    customers = st.session_state.get('search_results', [])

    if customers:
        df = pd.DataFrame(customers)
        df['Full Name'] = df['first_name'] + " " + df['last_name']

        display_df = df[
            ['customer_id', 'Full Name', 'email', 'phone', 'date_of_birth']
        ].rename(columns={
            'customer_id': 'Customer ID',
            'Full Name': 'Name',
            'email': 'Email',
            'phone': 'Phone',
            'date_of_birth': 'DOB'
        })

        gb = GridOptionsBuilder.from_dataframe(display_df)

        gb.configure_selection(
            selection_mode='single',
            use_checkbox=True,
            suppressRowClickSelection=True
        )
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(
            editable=False,
            filter=True,
            sortable=True,
            resizable=True,
            cellStyle=JsCode("""
                function(params) {
                    if (params.node.isSelected()) {
                        return {'backgroundColor': '#b9d6f2'};
                    } else if (params.rowIndex % 2 === 0) {
                        return {'backgroundColor': '#f9f9f9'};
                    }
                }
            """)
        )
        gb.configure_column(
            "Email",
            header_name="📧 Email",
            tooltipField="Email",
        )
        gb.configure_column(
            "Phone",
            header_name="📞 Phone",
            tooltipField="Phone",
        )
        gb.configure_column(
            "DOB",
            header_name="🎂 Date of Birth",
            type=["dateColumnFilter","customDateTimeFormat"],
            valueFormatter=JsCode("""
                function(params) {
                    if (!params.value) return '';
                    return new Date(params.value).toLocaleDateString();
                }
            """),
        )

        grid_options = gb.build()

        grid_response = AgGrid(
            display_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme='material',
            height=450,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
        )

        selected_rows = grid_response['selected_rows']
        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            if st.session_state.get('selected_customer') != selected_rows[0]:
                st.session_state['selected_customer'] = selected_rows[0]
            st.success(f"Selected Customer: {selected_rows[0]['Name']} (ID: {selected_rows[0]['Customer ID']})")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
