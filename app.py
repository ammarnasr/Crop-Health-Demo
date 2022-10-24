import streamlit as st
from multipage import MultiPage
from Tabs import  landingpage, lai, cab, truecolor, fcover, clp

# streamlit_app.py

def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://i.ibb.co/QCJ6zT6/bg.png");
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

 

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True



st.set_page_config(
    page_title="Crop Health",
    page_icon="🌾",
)


# add_bg_from_url()
if True:
# if check_password():
    
    # Create an instance of the app 
    app = MultiPage()

    # Add all your applications (pages) here
    app.add_page("Home", landingpage.app)
    app.add_page("LAI", lai.app)
    app.add_page("CAB", cab.app)
    app.add_page("FCOVER", fcover.app)
    # app.add_page("CLP", clp.app)
    app.add_page("TRUECOLOR", truecolor.app)

    # The main app
    app.run()