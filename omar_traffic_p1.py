import streamlit as st
import pandas as pd
import joblib
import psycopg2
import bcrypt
import re
from datetime import datetime, time

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="UK Road Traffic Predictor - Omar Khalifa",
    page_icon="🚦",
    layout="wide"
)

# ================================
# DATABASE CONFIG
# ================================
DB_CONFIG = {
    "host": "ep-steep-morning-ahhoeiz5-pooler.c-3.us-east-1.aws.neon.tech",
    "database": "traffic_predictor_db",
    "user": "neondb_owner",
    "password": "npg_XNZ0K2btduAc", 
    "port": 5432
   
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

#==============================
# Validator 1: schemas required
#==============================
REQUIRED_COLUMNS = {
    "Junction",
    "Vehicles",
    "DateTime"
}

REQUIRED_FEATURES = [
    "Vehicles",
    "Hour",
    "DayOfWeek",
    "Month",
    "Weekend",
    "RushHour"
]
# ================================
# AUTH HELPERS
# ================================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

# ================================
# FEATURE ENGINEERING
# ================================
def build_feature_row(vehicles, date_input, time_input):
    dt = datetime.combine(date_input, time_input)
    hour = dt.hour
    dayofweek = dt.weekday()
    month = dt.month
    weekend = 1 if dayofweek >= 5 else 0
    rushhour = 1 if (7 <= hour <= 9) or (16 <= hour <= 19) else 0

    return pd.DataFrame([{
        "Vehicles": vehicles,
        "Hour": hour,
        "DayOfWeek": dayofweek,
        "Month": month,
        "Weekend": weekend,
        "RushHour": rushhour
    }])
#=================================
# ENSURING THE COLLECT MODEL IS UPLOADED
#=================================
def load_model_safely(uploaded_file):
    try:
        model = joblib.load(uploaded_file)

        if not hasattr(model, "predict"):
            raise ValueError("Uploaded file is not a trained ML model.")

        if hasattr(model, "feature_names_in_"):
            missing = set(REQUIRED_FEATURES) - set(model.feature_names_in_)
            if missing:
                raise ValueError(
                    f"Model trained with incompatible features. Missing: {missing}"
                )

        return model, None

    except Exception as e:
        return None, str(e)
# ================================
# MODEL VALIDATOR
# ===============================

def validate_model(model):
    if model is None:
        return False, (
            "❌ Wrong file uploaded.\n\n"
            "Please upload a **trained machine learning model (.pkl)**.\n\n"
            "The model must:\n"
            "- Be trained (not an empty or raw object)\n"
            "- Support `.predict()`\n"
            "- Be saved using `joblib.dump()`"
        )

    if not hasattr(model, "predict"):
        return False, (
            "❌ Invalid model uploaded.\n\n"
            "The uploaded file is **not a trained ML model**.\n\n"
            "Expected:\n"
            "- A trained classifier/regressor\n"
            "- Saved as `.pkl` using joblib"
        )

    if hasattr(model, "feature_names_in_"):
        missing_features = set(REQUIRED_FEATURES) - set(model.feature_names_in_)
        if missing_features:
            return False, (
                "❌ Incompatible trained model.\n\n"
                "This model was trained using different input features.\n\n"
                "Expected features:\n"
                "- Vehicles\n"
                "- Hour\n"
                "- DayOfWeek\n"
                "- Month\n"
                "- Weekend\n"
                "- RushHour\n\n"
                f"❌ Missing features: {', '.join(missing_features)}"
            )

    return True, None


#================================
# DATASET VALIDATOR
#===============================
def validate_dataset(df: pd.DataFrame):
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        return False, (
            "❌ Wrong dataset uploaded.\n\n"
            "The dataset must contain the following columns:\n\n"
            "- Junction\n"
            "- Vehicles\n"
            "- DateTime (YYYY-MM-DD HH:MM:SS)\n\n"
            f"❌ Missing columns: {', '.join(missing_columns)}"
        )

    try:
        pd.to_datetime(df["DateTime"])
    except Exception:
        return False, (
            "❌ Invalid DateTime format.\n\n"
            "Expected format example:\n"
            "2023-06-01 08:00:00"
        )

    return True, None

# ================================
# SESSION STATE
# ================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

# ================================
# LOGIN PAGE
# ================================
def login_page():
    st.subheader("🔐 Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):

        if not username or not password:
            st.error("❌ All fields are required.")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT password_hash FROM users WHERE username=%s",
            (username,)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and verify_password(password, user[0]):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# ================================
# REGISTER PAGE (FIXED)
# ================================
def register_page():
    st.subheader("📝 Register")

    username = st.text_input("Username", key="reg_username")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

    if st.button("Register", key="reg_btn"):

        # Validation
        if not username or not email or not password or not confirm:
            st.error("❌ All fields are required.")
            return

        if not is_valid_email(email):
            st.error("❌ Invalid email format.")
            return

        if len(password) < 6:
            st.error("❌ Password must be at least 6 characters.")
            return

        if password != confirm:
            st.error("❌ Passwords do not match.")
            return

        hashed = hash_password(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # check duplicates
            cur.execute(
                "SELECT 1 FROM users WHERE username=%s OR email=%s",
                (username, email)
            )

            if cur.fetchone():
                st.error("❌ Username or email already exists.")
                return

            cur.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
            """, (username, email, hashed))

            conn.commit()
            cur.close()
            conn.close()

            st.success("✅ Account created successfully. Please log in.")

        except Exception as e:
            st.error(f"❌ Registration failed: {e}")

# ================================
# AUTH GATE
# ================================
if not st.session_state.authenticated:
    st.title("🚦 UK Road Traffic Predictor")

    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login_page()
    with tab2:
        register_page()

    st.stop()

# ================================
# LOGOUT
# ================================
st.sidebar.success(f"👤 Logged in as {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()



# ===============================
# Dashboard
# ================================
st.sidebar.markdown("## 📊 Dashboard")

menu = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "🚦 Predictor",
        "📊 Prediction History",
        "📈 Analytics",
        "⚙️ Account",
        "🚪 Logout"
    ],
    key="nav_menu"
)

# ================================
# MAIN APP
# ================================
st.title("🚦 UK Road Traffic Congestion Predictor")
st.caption("Upload trained model & dataset to begin")

# ===============================
# FILE UPLOADS
# ==============================
model_file = st.sidebar.file_uploader("📦 Upload Model (.pkl)", type=["pkl"])
data_file = st.sidebar.file_uploader("📊 Upload Dataset (.csv)", type=["csv"])

# ===========================
# CORRECT FILE UPLOAD
# ==========================
model = None
data = None



if model_file:
    model, model_error = load_model_safely(model_file)
    if model_error:
        st.error(
            "❌ Invalid model uploaded.\n\n"
            "Please upload a **trained .pkl model** using features:\n"
            "Vehicles, Hour, DayOfWeek, Month, Weekend, RushHour"
        )
        st.stop()

if data_file:
    try:
        temp_df = pd.read_csv(data_file)
        valid, error_msg = validate_dataset(temp_df)
        if not valid:
            st.error(error_msg)
            st.stop()
        data = temp_df
    except Exception as e:
        st.error(f"❌ Failed to read dataset: {e}")
        st.stop()

model = joblib.load(model_file) if model_file else None
data = pd.read_csv(data_file) if data_file else None

st.markdown("---")

# ================================
# JUNCTION PREDICTION
# ================================
if model is not None and data is not None and "Junction" in data.columns:

    junctions = sorted(data["Junction"].dropna().unique())

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_junction = st.selectbox("🚧 Junction", junctions)
    with col2:
        selected_date = st.date_input("📅 Date", datetime.today())
    with col3:
        selected_time = st.time_input("⏰ Time", time(8, 0))

    if st.button("🚗 Predict Traffic"):
        junction_data = data[data["Junction"] == selected_junction]

        if junction_data.empty:
            st.warning("⚠️ No data for this junction.")
        else:
            estimated_vehicles = junction_data["Vehicles"].mean()
            feature_row = build_feature_row(
                estimated_vehicles,
                selected_date,
                selected_time
            )

            prediction = model.predict(feature_row)[0]

            if prediction == "High":
                st.error("🚨 HIGH TRAFFIC")
            elif prediction == "Medium":
                st.warning("⚠️ MEDIUM TRAFFIC")
            else:
                st.success("✅ LOW TRAFFIC")
# ================================
# BATCH PREDICTION
# ================================
st.markdown("---")
st.markdown("## 📊 Batch Prediction (All Records)")

if st.button("Run Prediction for Entire Dataset"):
    if model is None or data is None:
        st.warning("⚠️ Please upload both model and dataset.")
    else:
        try:
            processed = data.copy()
            processed["DateTime"] = pd.to_datetime(processed["DateTime"])

            processed["Hour"] = processed["DateTime"].dt.hour
            processed["DayOfWeek"] = processed["DateTime"].dt.dayofweek
            processed["Month"] = processed["DateTime"].dt.month
            processed["Weekend"] = processed["DayOfWeek"].isin([5, 6]).astype(int)
            processed["RushHour"] = processed["Hour"].isin([7, 8, 9, 16, 17, 18]).astype(int)

            features = processed[['Vehicles', 'Hour', 'DayOfWeek', 'Month', 'Weekend', 'RushHour']]
            predictions = model.predict(features)

            results_df = data.copy()
            results_df["Predicted_Congestion"] = predictions

            st.success("✅ Batch prediction completed")

            st.dataframe(results_df.head(20))

            csv = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Prediction Results",
                csv,
                "traffic_predictions.csv",
                "text/csv"
            )

        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
# ================================
# FOOTER
# ================================
st.markdown("---")
st.caption("Developed by **Omar Khalifa** | Secure Traffic Prediction System")



