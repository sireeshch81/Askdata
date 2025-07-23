import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import hashlib
import plotly.express as px

DB_URL = f"mysql+mysqlconnector://{st.secrets['connections']['mysql']['username']}:{st.secrets['connections']['mysql']['password']}@{st.secrets['connections']['mysql']['host']}:{st.secrets['connections']['mysql']['port']}/{st.secrets['connections']['mysql']['database']}"
engine = create_engine(DB_URL)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_login(username, password):
    with engine.connect() as conn:
        rs = conn.execute(
            text("SELECT id FROM users WHERE username = :username AND password = :password"),
            {"username": username, "password": hash_password(password)}
        )
        row = rs.fetchone()
        return row[0] if row else None
def get_user_roles(user_id):
    with engine.connect() as conn:
        rs = conn.execute(
            text("SELECT roles.role_name FROM roles "
                 "INNER JOIN user_roles ON roles.id = user_roles.role_id "
                 "WHERE user_roles.user_id = :user_id"),
            {"user_id": user_id}
        )
        return [r[0] for r in rs.fetchall()]

def has_role(role):
    return "roles" in st.session_state and role in st.session_state["roles"]

def fetch_sales_reports():
    query = """
    SELECT
        sr.id,
        co.name AS company,
        i.industry_name AS industry,
        c.country_name AS country,
        sr.report_date,
        sr.sales_amount,
        sr.currency
    FROM sales_reports sr
    JOIN companies co ON sr.company_id = co.id
    JOIN industries i ON sr.industry_id = i.id
    JOIN countries c ON sr.country_id = c.id
    ORDER BY sr.report_date DESC
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def sales_by(x_field="company"):
    # Group and sum for bar plot
    data = fetch_sales_reports()
    return data.groupby(x_field)['sales_amount'].sum().reset_index()




def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = validate_login(username, password)
        if user_id:
            st.session_state["user_id"] = user_id
            st.session_state["roles"] = get_user_roles(user_id)
            st.session_state["page"] = "dashboard"  # <--- Track what page to show
            st.success("Login successful!")
            st.rerun()  # <--- force UI refresh
        else:
            st.error("Invalid credentials.")

def dashboard_page():
    st.title("Dashboard")
    st.write(f"Welcome, your roles: {', '.join(st.session_state['roles'])}")

    st.header("Sales Reports Table")
    df = fetch_sales_reports()
    st.dataframe(df)
    
    st.subheader("Sales by:")
    option = st.selectbox(
        "Select grouping for bar graph", 
        ("company", "industry", "country")
    )
    bar_data = sales_by(option)
    fig = px.bar(
        bar_data, x=option, y="sales_amount",
        labels={option: option.capitalize(), "sales_amount": "Total Sales"},
        title=f"Total Sales by {option.capitalize()}"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Role-based content rendering
    if has_role("admin"):
        st.subheader("Admin Panel")
        st.markdown("### User Management")
        st.info("Only admins can see this section.")
        # Example admin-only button
        if st.button("Add New User"):
            st.success("Pretend to add a new user!")
    
    if has_role("moderator"):
        st.subheader("Moderator Panel")
        st.markdown("### Moderation Area")
        st.info("Only moderators can see this section.")
        # Example moderator-only action
        if st.button("Review Reports"):
            st.success("Pretend to review reported posts!")
    
    if has_role("user"):
        st.subheader("User Panel")
        st.markdown("### General User Section")
        st.info("Regular users & above can see this.")

    # Add a logout button
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ----- Main app logic -----
if "user_id" not in st.session_state:
    login_page()
else:
    dashboard_page()


