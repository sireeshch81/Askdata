import streamlit as st
import requests
import jwt
from keycloak import KeycloakOpenID

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
        # Clear residual customer-related state
        for key in ['search_results', 'selected_customer_id', 'selected_customer_radio']:
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

def render_user_header(user_info):
    st.markdown(
        """
        <style>
        .header-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
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
        """,
        unsafe_allow_html=True,
    )

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
            for key in ['token', 'search_results', 'selected_customer_id', 'selected_customer_radio']:
                st.session_state.pop(key, None)
            st.rerun()

def render_customer_details(customer):
    if not customer:
        st.info("Select a customer to see details here.")
        return

    card_html = f"""
    <style>
    .card {{
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
        background: #f9f9f9;
        max-width: 420px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .field-label {{
        font-weight: 600;
        color: #555;
        width: 130px;
        display: inline-block;
    }}
    .field-value {{
        color: #222;
        font-size: 16px;
        display: inline-block;
    }}
    .field-row {{
        margin-bottom: 8px;
    }}
    </style>

    <div class="card">
        <div class="field-row"><span class="field-label">Customer ID:</span> <span class="field-value">{customer.get("customer_id","")}</span></div>
        <div class="field-row"><span class="field-label">First Name:</span> <span class="field-value">{customer.get("first_name","")}</span></div>
        <div class="field-row"><span class="field-label">Last Name:</span> <span class="field-value">{customer.get("last_name","")}</span></div>
        <div class="field-row"><span class="field-label">✉️ Email:</span> <span class="field-value">{customer.get("email","")}</span></div>
        <div class="field-row"><span class="field-label">📞 Phone:</span> <span class="field-value">{customer.get("phone","")}</span></div>
        <div class="field-row"><span class="field-label">🎂 Date of Birth:</span> <span class="field-value">{customer.get("date_of_birth","")}</span></div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

def main():
    token = authenticate_user()

    if token:
        user_info = get_user_info_from_token(token)
        if not user_info:
            st.warning("Could not decode user info. Try logging in again.")
            return

        render_user_header(user_info)
        st.markdown('<div class="app-content">', unsafe_allow_html=True)

        st.markdown("### 🔍 Search Customers or Products")

        with st.form("search_form"):
            customer_query = st.text_input(
                "", placeholder="Ask for a customer detail or a product"
            )
            submitted = st.form_submit_button("Search")

        if submitted:
            if not customer_query.strip():
                st.error("Please enter a valid search query.")
            else:
                try:
                    response = requests.get(
                        "http://askdata-api-backend:5004/customer_detail",
                        params={"customer_name": customer_query}
                    )
                    if response.status_code == 200:
                        customers = response.json()
                        if customers:
                            st.session_state['search_results'] = customers
                            st.session_state['selected_customer_id'] = None
                        else:
                            st.warning("No customers found.")
                            st.session_state['search_results'] = []
                            st.session_state['selected_customer_id'] = None
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to fetch data: {e}")

        customers = st.session_state.get('search_results', [])

        if customers:
            left_col, right_col = st.columns([1, 2])

            with left_col:
                st.markdown("#### Customers Found")
                options = []
                for idx, cust in enumerate(customers, start=1):
                    full_name = f"{cust['first_name']} {cust['last_name']}"
                    options.append((cust['customer_id'], f"{idx}. {full_name}"))

                id_to_label = {cid: label for cid, label in options}

                selected_id = st.radio(
                    "Select a customer:",
                    options=[cid for cid, _ in options],
                    format_func=lambda cid: id_to_label[cid],
                    key="selected_customer_radio"
                )
                st.session_state['selected_customer_id'] = selected_id

            with right_col:
                selected_cust = next(
                    (c for c in customers if c['customer_id'] == st.session_state.get('selected_customer_id')), None
                )
                render_customer_details(selected_cust)

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
