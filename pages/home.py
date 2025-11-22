import streamlit as st

def show_home():
    st.title("👋 Welcome to the Telecom Churn Prediction App")
    st.markdown("""
        This interactive application provides **customer churn analysis and retention strategy recommendations** 
    built from a Machine Learning project.

    The main goals of this dashboard:
    - Identify customer churn
    - Suggest targeted retention strategies
    """)

    st.subheader("Business Value")
    st.write("""
    - Reduce customer churn through proactive intervention  
    - Improve customer lifetime value (CLV)  
    - Optimize marketing and retention spending  
    - Increase satisfaction and loyalty across customer segments
    """)