import streamlit as st
from keycloak import KeycloakOpenID
import jwt

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
        st.title("Keycloak Authentication")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                token = keycloak_openid.token(username, password)
                st.session_state['token'] = token   # Save token to session state
                st.success("You are logged in!")
                st.rerun()
            except Exception as e:
                print(e)
                st.error(f"Authentication failed: {str(e)}")
    return st.session_state.get('token', None)

def main():
    token = authenticate_user()

    if token:
        st.success("You are logged in!")
        st.write("JWT Token Info:")
        st.json(token)

        access_token_str = token.get('access_token')
        if access_token_str:
            try:
                decoded_token = jwt.decode(access_token_str, options={"verify_signature": False})
                st.write("Decoded Access Token Payload:")
                st.json(decoded_token)

                if "realm_access" in decoded_token and "roles" in decoded_token["realm_access"]:
                    st.write(f"Realm Roles: {decoded_token['realm_access']['roles']}")
                if "resource_access" in decoded_token and KEYCLOAK_CLIENT_ID in decoded_token["resource_access"] and "roles" in decoded_token["resource_access"][KEYCLOAK_CLIENT_ID]:
                    st.write(f"Client Roles: {decoded_token['resource_access'][KEYCLOAK_CLIENT_ID]['roles']}")
            except jwt.ExpiredSignatureError:
                st.error("Access token has expired.")
            except jwt.InvalidTokenError as e:
                st.error(f"Invalid access token: {e}")
        else:
            st.warning("Access token not found in the response.")

        # Optional: Add a logout button
        if st.button("Logout"):
            del st.session_state['token']
            st.rerun()
    else:
        st.warning("Please log in to use the app.")

if __name__ == "__main__":
    main()
