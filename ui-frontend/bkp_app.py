import streamlit as st
import requests
from keycloak import KeycloakOpenID
import jwt

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
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                token = keycloak_openid.token(username, password)
                st.session_state['token'] = token
                st.rerun()  # Use st.rerun instead of experimental_rerun
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
    col_left, col_right = st.columns([10, 2])
    with col_left:
        st.markdown("")  # Empty to push right side content
    with col_right:
        with st.container():
            st.markdown(
                f"""
                <div style='text-align: right; font-size: 14px;'>
                    👤 <b>{user_info['name']}</b>&nbsp;&nbsp;✉️ {user_info['email']}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Logout"):
                del st.session_state['token']
                st.rerun()

def main():
    token = authenticate_user()

    if token:
        user_info = get_user_info_from_token(token)
        if user_info:
            render_user_header(user_info)

            st.markdown("---")
            st.markdown("### 🔍 Search Customers or Products")

            customer_query = st.text_input(
                "",
                placeholder="Ask for a customer detail or a product",
                key="search_input"
            )

            if st.button("Search"):
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
                                st.subheader("Customer Details")
                                for customer in customers:
                                    st.markdown("---")
                                    st.write(f"ID: {customer['customer_id']}")
                                    st.write(f"First Name: {customer['first_name']}")
                                    st.write(f"Last Name: {customer['last_name']}")
                                    st.write(f"Email: {customer['email']}")
                                    st.write(f"Phone: {customer.get('phone', 'N/A')}")
                                    st.write(f"Date of Birth: {customer.get('date_of_birth', 'N/A')}")
                            else:
                                st.warning("No customers found.")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Failed to fetch data: {e}")
        else:
            st.warning("Could not decode user info. Try logging in again.")

if __name__ == "__main__":
    main()
