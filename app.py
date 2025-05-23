import re
import os
import streamlit as st
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer


# Function to generate a strong password based on the user's name
def generate_personalized_password(name):
    name_part = name.capitalize()
    num_part = random.randint(1,10000) 
    special_chars = "!@#$%^&*"
    special_part = ''.join(random.choices(special_chars, k=2)) 
    
    # Generate different password options
    password_options = [
        f"{name_part}{num_part}{special_part}",
        f"{special_part}{name_part}{num_part}",
        f"{num_part}{name_part}{special_part}"
    ]
    return random.sample(password_options, 3)  

# Function to check password strength
def check_password_strength(password):
    score = 0
    errors = []
    
    # Length Check
    if len(password) >= 8:
        score += 1
    else:
        errors.append("❌ Password should be at least 8 characters long.")
    
    # Upper & Lowercase Check
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    else:
        errors.append("❌ Include both uppercase and lowercase letters.")
    
    # Digit Check
    if re.search(r"\d", password):
        score += 1
    else:
        errors.append("❌ Add at least one number (0-9).")
    
    # Special Character Check
    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        errors.append("❌ Include at least one special character (!@#$%^&*).")
    
    return score, errors

# Load saved passwords
DATA_FILE = "passwords.json"

def load_data():
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            pass
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


st.title("🔒 Password Strength Checker & Generator")
password = st.text_input("Enter your password:", type="password")

if password:
    score, errors = check_password_strength(password)
    
    if score == 4:
        st.success("✅ Strong Password!")
    elif score == 3:
        st.warning("⚠️ Moderate Password - Consider adding more security features.")
        st.write(errors)
    else:
        st.error("❌ Weak Password - Improve it using the suggestions below:")
        for error in errors:
            st.write(error)


# Generate password button state
if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False
    
if st.button("Can I generate your password?"):
    st.session_state.generate_clicked = True

# Show input field only if generate button was clicked
if st.session_state.generate_clicked:
    with st.expander("About to Password"):
        st.write("if you want to generate a password please enter your name here, This app provide a strong password suggestion and its own feature to save your generated password into app memory and if you not remember your password you also find your password with your name in one click:",)
    user_name = st.text_input("Enter your name to generate a password:", key="generate_name")
    if st.button("Generate Password"):
        if user_name:
            data = load_data()
            suggested_passwords = generate_personalized_password(user_name)
            user_password = {"user_name":user_name,"password":suggested_passwords}
            data.append(user_password)
            save_data(data)
            # save_password(user_name, suggested_passwords)
            st.success("Here are three password suggestions:")
            for pwd in suggested_passwords:
                st.code(pwd)
        else:
            st.error("Please enter your name before generating a password.")

def search_blogs(query, user_data):
    """AI-powered blog search using TF-IDF (title, blog_name, and description)."""
    if not user_data or not query.strip():
        return []
    
    # Include title, blog_name, and description in search
    text_data = [f"{b['user_name'].lower()}" for b in user_data]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(text_data)
    query_vector = vectorizer.transform([query.lower()])
    
    scores = (tfidf_matrix * query_vector.T).toarray()
    results = sorted(zip(scores, user_data), key=lambda x: -x[0][0])
    
    return [b for score, b in results if score[0] > 0]


st.header("🔍 Retrieve Saved Password")
retrieve_name = st.text_input("Enter your name to retrieve your password:", key="retrieve_name").lower()

if st.button("Retrieve Password"):
    passwords = load_data()
    results = search_blogs(retrieve_name, passwords)
    if results:
        for retrieve_name in results:
            with st.expander(f"📰 {retrieve_name['user_name']}"):
                st.write(f"{retrieve_name['password']}")
        # st.success(f"Your saved password: `{[{user_name:[retrieve_name]}]}`")
    else:
        st.error("No password found for this name.")
