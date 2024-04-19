import streamlit as st

class _sessionstate:
    def __init__(self):
        self.user_authenticated = False

def get(**kwargs):
    """Gets a sessionstate object for the current session."""
    if not hasattr(st, '_session_state'):
        st._session_state = _sessionstate()
    for key, value in kwargs.items():
        if not hasattr(st._session_state, key):
            setattr(st._session_state, key, value)
    return st._session_state