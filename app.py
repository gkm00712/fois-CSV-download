import streamlit as st
import requests

# Set up the visual configuration of the page
st.set_page_config(page_title="FOIS Data Exporter", page_icon="🚆", layout="centered")

st.title("🚆 Automated FOIS Data Exporter")
st.write("Solve the CAPTCHA in your browser, paste your session cookie below, and download reports.")

# --- SECTION 1: Target URL Config ---
# The base URL without any parameters attached
TARGET_URL = "https://www.fois.indianrail.gov.in/ecbs/RouterServlet"

# --- SECTION 2: Authentication ---
st.subheader("🔑 Session Authentication")
cookie_input = st.text_area(
    "Paste your browser 'Cookie' header string here:",
    placeholder="Example: JSESSIONID=0000XXXX... (Paste the full string)",
    help="Get this from the Network tab after manually passing the CAPTCHA."
)

# --- SECTION 3: Input Parameters ---
st.subheader("📝 Query Parameters")

col1, col2 = st.columns(2)

with col1:
    station_to = st.text_input("Destination Station (txtSttnTo)", value="fgtp")
    consignee = st.text_input("Consignee (txtConsignee)", value="NTPC")
    user_id = st.text_input("User (user)", value="NTPC")

with col2:
    # Uses text input to match the exact format 'DD-MM-YYYY'
    sys_date = st.text_input("System Date (txtSysDate)", value="11-06-2026")
    sub_op = st.text_input("Sub-operation", value="insight")

# Advanced fixed parameters (hidden inside an expander to keep the UI clean)
with st.expander("Advanced Hidden Parameters"):
    sttn_from = st.text_input("txtSttnFrom", value="")
    commodity = st.text_input("txtCommodity", value="")
    consignor = st.text_input("txtConsignor", value="")
    locn_flag = st.text_input("locnflag", value="S")
    usr_flag = st.text_input("usrflag", value="C")
    flag = st.text_input("txtFlag", value="S")
    t_flag = st.text_input("txtTFlag", value="S")

# --- SECTION 4: Processing & Downloading ---
st.markdown("---")

if st.button("🚀 Fetch Data from Server", type="primary"):
    if not cookie_input:
        st.error("❌ Please provide a valid session cookie string first!")
    else:
        # Reconstruct the headers using your pasted cookie
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie_input.strip()
        }
        
        # Build the exact payload dictionary 
        payload = {
            "operation": "query",
            "suboperation": sub_op,
            "txtSttnFrom": sttn_from,
            "txtSttnTo": station_to,
            "txtCommodity": commodity,
            "txtConsignor": consignor,
            "txtConsignee": consignee,
            "locnflag": locn_flag,
            "user": user_id,
            "usrflag": usr_flag,
            "txtSysDate": sys_date,
            "txtFlag": flag,
            "txtTFlag": t_flag
        }
        
        with st.spinner("Connecting to FOIS server and querying data..."):
            try:
                # Fire the GET request, attaching the payload parameters automatically
                response = requests.get(TARGET_URL, params=payload, headers=headers, timeout=25)
                
                if response.status_code == 200:
                    csv_data = response.content
                    
                    # Basic validation check to ensure we didn't just download the HTML login/CAPTCHA page
                    if b"<html" in csv_data[:200].lower() or b"<!doctype" in csv_data[:200].lower():
                        st.warning("⚠️ Warning: The server responded with a webpage instead of a CSV. Your session cookie has likely expired. Please solve the CAPTCHA again and paste the new cookie.")
                    else:
                        st.success("✅ Data fetched successfully!")
                        
                        # Dynamic file name generation
                        generated_filename = f"FOIS_Report_{consignee}_{station_to}_{sys_date}.csv"
                        
                        # Streamlit native download button
                        st.download_button(
                            label="📥 Download CSV File",
                            data=csv_data,
                            file_name=generated_filename,
                            mime="text/csv"
                        )
                else:
                    st.error(f"❌ Server Error! HTTP Status Code: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Connection Failed: {str(e)}")
