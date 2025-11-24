import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap

def show_prediction():
    st.title("Customer Churn Prediction")

    st.write("""
    Enter customer information below to check whether the customer is **at risk of churning**
    and obtain a **personalized retention recommendation**.
    """)

    # Load model & preprocessing
    model = joblib.load("models/final_churn_lgbm.pkl")
    scaler = joblib.load("models/robust_scaler.pkl")

    feature_columns = [
        "satisfaction_score",
        "monthly_charges",
        "online_security",
        "number_of_dependents",
        "tenure",
        "contract_Month-to-Month",
        "contract_One Year",
        "contract_Two Year"
    ]

    # ---- INPUT FORM ----
    with st.form("churn_form"):
        contract = st.selectbox(
            "What type of contract does the customer currently have?",
            ["Month-to-Month", "Two Year", "One Year"]
        )
        monthly_charges = st.number_input(
            "How much is the customer's monthly charge ($)?",
            min_value=0.0, max_value=200.0, value=70.0
        )
        tenure = st.number_input(
            "How long has the customer been subscribed? (months)",
            min_value=0, max_value=72, value=12
        )
        online_security = st.selectbox(
            "Does the customer subscribe to Online Security?",
            ["No", "Yes"]
        )
        dependents = st.number_input(
            "How many dependents does the customer have?",
            min_value=0, max_value=10, value=0
        )
        satisfaction = st.slider(
            "Customer satisfaction score",
            1, 5, 3
        )

        submitted = st.form_submit_button("🔮 Predict Churn")

    # ---- PREDICTION ----
    if submitted:
        with st.spinner("Analyzing customer churn..."):

            # Manual Encoding
            contract_Month_to_Month = 1 if contract == "Month-to-Month" else 0
            contract_One_Year = 1 if contract == "One Year" else 0
            contract_Two_Year = 1 if contract == "Two Year" else 0
            OnlineSecurity = 1 if online_security == "Yes" else 0

            df_input = pd.DataFrame([{
                "satisfaction_score": satisfaction,
                "monthly_charges": monthly_charges,
                "online_security": OnlineSecurity,
                "number_of_dependents": dependents,
                "tenure": tenure,
                "contract_Month-to-Month": contract_Month_to_Month,
                "contract_One Year": contract_One_Year,
                "contract_Two Year": contract_Two_Year
            }])

        # Scale only true numeric columns
        num_cols = ["satisfaction_score", "monthly_charges", "number_of_dependents", "tenure"]

        scaled_num = scaler.transform(df_input[num_cols])
        scaled_num_df = pd.DataFrame(scaled_num, columns=num_cols)

        # Combine scaled numerics + binary categorical
        df_scaled = pd.concat(
            [scaled_num_df, df_input.drop(columns=num_cols)],
            axis=1
        )

        # Maintain exact order as model trained
        df_scaled = df_scaled[feature_columns]

        # Predict probability
        prob_churn = model.predict_proba(df_scaled)[0][1]
        label = "Churn" if prob_churn >= 0.5 else "Not Churn"

        # ---- DISPLAY RESULTS ----
        st.divider()
        st.subheader("📌 Prediction Result")
        st.metric("Customer Status", label)
        st.metric("Churn Probability", f"{prob_churn:.2%}")

        # ---- RETENTION STRATEGY ----
        cltv = monthly_charges * tenure
        expected_loss = cltv * prob_churn
        max_offer = expected_loss * 0.7 

        if prob_churn < 0.30:
            strategy = "No offer needed — maintain standard communication."
        elif prob_churn < 0.60:
            strategy = "Send tailored engagement campaigns, upsell online security, loyalty rewards."
        elif prob_churn < 0.80:
            strategy = f"Targeted discounts & proactive success calls. Offer up to **${max_offer:.2f}**."
        else:
            strategy = f"High-risk: bundle retention + renewal incentives. Offer up to **${max_offer:.2f}**."

        st.divider()
        st.subheader("🎯 Recommended Retention Strategy")
        st.write(f"""
        - **Customer Lifetime Value (CLTV):** ${cltv:.2f}  
        - **Expected Loss if Churn:** ${expected_loss:.2f}  
        - **Maximum Retention Offer:** ${max_offer:.2f}  
        - **Strategy:** **{strategy}**
        """)

    st.markdown("---")
    st.caption("Telecom Churn Prediction — Machine Learning for Customer Retention")
