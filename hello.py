import streamlit as st

col01, col02, col03 = st.columns([0.25, 0.5, 0.25])
with col02:
    st.image("https://www.hda.belgium.be/themes/custom/hda/logo.svg")

user_request = st.text_input("Search", label_visibility='hidden')
st.write("")

col11, col12, col13 = st.columns([0.425, 0.15, 0.425])
with col12:
    search_button = st.button("Search")

if search_button or user_request:
    st.write(user_request)
        
