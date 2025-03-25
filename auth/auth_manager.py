import streamlit as st
from firebase_admin import auth

def check_authentication():
    """Check if user is authenticated"""
    return 'user_token' in st.session_state

def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        # Verify password and set session
        st.session_state['user_token'] = user.uid
        st.session_state['user_email'] = email
        return True
    except:
        return False

def logout_user():
    if 'user_token' in st.session_state:
        del st.session_state['user_token']
    if 'user_email' in st.session_state:
        del st.session_state['user_email']

def create_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return True
    except:
        return False
