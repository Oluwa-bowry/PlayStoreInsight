import streamlit as st
import pandas as pd
import numpy as np
import joblib

# -------------------- Load Pre-Trained Objects --------------------
# Load the preprocessor, logistic regression model, and thresholds
preprocessor = joblib.load("preprocessor.pkl")
log_reg = joblib.load("log_reg.pkl")
thresholds = joblib.load("thresholds.pkl")  # thresholds: {'rating': ..., 'price (usd)': ..., 'time_since_update': ..., 'app_age': ...}

# -------------------- Dashboard Title --------------------
st.title("Google Play Favorability Dashboard")
st.write("This tool predicts app performance on Google Play and provides recommendations to enhance your app's appeal to Google Play users.")

# -------------------- User Input Section --------------------
st.header("Enter Your App's Characteristics")

# Inputs corresponding to the predictive model
rating = st.number_input("App Rating", min_value=0.0, max_value=5.0, value=3.0, step=0.1)
price = st.number_input("App Price (USD)", min_value=0.0, value=2.99, step=0.5)
app_age = st.number_input("App Age (Years)", min_value=0.0, value=2.0, step=0.1)
time_since_update = st.number_input("Time Since Last Update (Years)", min_value=0.0, value=1.5, step=0.1)
default_category_encoded = 0.5  # This can be refined if more data is available.
content_rating = st.selectbox("Content Rating", ["Kids", "Everyone", "Teen", "17+", "Everyone 10+", "Adults only 18+", "Unrated"])
free = st.selectbox("Is the app free?", ["True", "False"])

# Assemble the input data for the predictive model
input_data = pd.DataFrame({
    "rating": [rating],
    "price (usd)": [price],
    "app_age": [app_age],
    "time_since_update": [time_since_update],
    "category_encoded": [default_category_encoded],
    "content_rating": [content_rating],
    "free": [free]
})

st.write("### Your App's Input Data")
st.dataframe(input_data)

# -------------------- Prediction & Recommendation --------------------
if st.button("Evaluate and Get Recommendations"):
     # Transform the input data using the preprocessor
    processed_input = preprocessor.transform(input_data)
    
    # Predict the probability for class 0 (Google Play favorability)
    google_play_prob = log_reg.predict_proba(processed_input)[0][0]  # Probability of being favorable for Google Play
    
    # Display the probability correctly
    st.success(f"Predicted Favorability for Google Play: {google_play_prob:.2%}")
    
    # Generate threshold-based recommendations
    recommendations = {}
    
    # For each key metric, compare the input value with the threshold and create advice.
    # For rating: Higher is better
    if rating < thresholds["rating"]:
        recommendations["Rating"] = f"Increase your rating to at least {thresholds['rating']:.2f} (current: {rating:.2f})."
    else:
        recommendations["Rating"] = "Your rating meets or exceeds the recommended threshold."
    
    # For price: Lower is better
    if price > thresholds["price (usd)"]:
        recommendations["Price"] = f"Reduce your price below {thresholds['price (usd)']:.2f} USD (current: {price:.2f} USD)."
    else:
        recommendations["Price"] = "Your price is within the optimal range."
    
    # For time since update: Lower is better (more frequent updates)
    if time_since_update > thresholds["time_since_update"]:
        recommendations["Update Frequency"] = f"Consider updating your app more frequently; aim for less than {thresholds['time_since_update']:.2f} years (current: {time_since_update:.2f} years)."
    else:
        recommendations["Update Frequency"] = "Your update frequency is good."
    
    # For app age: Newer might be more favorable
    if app_age > thresholds["app_age"]:
        recommendations["App Age"] = f"Consider refreshing your app; optimal app age is below {thresholds['app_age']:.2f} years (current: {app_age:.2f} years)."
    else:
        recommendations["App Age"] = "Your app age is within the recommended range."
    
    # Display recommendations
    st.write("### Recommendations to Enhance Google Play Success")
    for key, advice in recommendations.items():
        st.write(f"**{key}:** {advice}")
    
    # Optionally, create a composite score indicating how far the app is from thresholds:
    # Calculate gaps (normalized differences)
    rating_gap = max(0, thresholds["rating"] - rating)
    price_gap = max(0, price - thresholds["price (usd)"])
    update_gap = max(0, time_since_update - thresholds["time_since_update"])
    age_gap = max(0, app_age - thresholds["app_age"])
    
    composite_gap = rating_gap + price_gap + update_gap + age_gap
    st.write(f"**Composite Improvement Gap:** {composite_gap:.2f}")
