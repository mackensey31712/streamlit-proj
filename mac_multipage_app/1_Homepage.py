import streamlit as st
from session_state import get  # Import the session state module

def main():
    # Get the user authentication status and username from the session state
    session_state = get(user_authenticated=False, username="")
    
    if not session_state.user_authenticated:  # Show login form if not authenticated
        st.title("Please Login")

        # Access usernames and passwords from secrets.toml
        usernames_and_passwords = st.secrets["passwords"]

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in usernames_and_passwords and password == usernames_and_passwords[username]:
                st.success("Login successful")
                session_state.user_authenticated = True
                session_state.username = username
                st.rerun()
            else:
                st.error("😕Incorrect username or password")
    else:  # Show Homepage if authenticated
        st.title("Homepage")
        st.write(f"Welcome, {session_state.username}!")

        if st.button("Log Out"):
            session_state.user_authenticated = False
            session_state.username = ""
            st.rerun()

if __name__ == "__main__":
    main()



# import streamlit as st

# import hmac

# st.set_page_config(
#     page_title="SRR Homepage",
#     page_icon="👋"
# )

# def check_password():
#     """Returns `True` if the user had a correct password."""

#     def login_form():
#         """Form with widgets to collect user information"""
#         with st.form("Credentials"):
#             st.text_input("Username", key="username")
#             st.text_input("Password", type="password", key="password")
#             st.form_submit_button("Log in", on_click=password_entered)

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if st.session_state["username"] in st.secrets[
#             "passwords"
#         ] and hmac.compare_digest(
#             st.session_state["password"],
#             st.secrets.passwords[st.session_state["username"]],
#         ):
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # Don't store the username or password.
#             del st.session_state["username"]
#         else:
#             st.session_state["password_correct"] = False

#     # Return True if the username + password is validated.
#     if st.session_state.get("password_correct", False):
#         return True

#     # Show inputs for username + password.
#     login_form()
#     if "password_correct" in st.session_state:
#         st.error("😕 User not known or password incorrect")
#     return False


# if not check_password():
#     st.stop()


# st.header("Welcome to my Streamlit DA Projects")
# st.sidebar.success("Select a page above.")

# st.write(":point_left: Browse through my projects")

