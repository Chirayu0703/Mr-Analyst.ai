import streamlit as st
st.title("Mr Analyst, Your personal AI Assitance")

st.write("welcome to Indias best AI platform for analyst")

st.file_uploader("Kindly upload your file",type=["csv",".xlxs","pdf"])

st.button("Upload Now")

st.title("Ask AI about your file")

st.text_input("Ask your question")

st.button("Ask AI")
st.button("Generate Sql Code")