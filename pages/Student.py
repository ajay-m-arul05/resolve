import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
CSV_FILE = 'issues.csv'
UPLOAD_FOLDER = 'uploads'

# --- Helper Functions ---
def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# --- Page Initialization ---
st.set_page_config(page_title="Student Dashboard", page_icon="👨‍🎓", layout="wide")
st.title("👨‍🎓 Student Dashboard")
if 'upvoted_issues' not in st.session_state:
    st.session_state.upvoted_issues = []

# --- UI Tabs ---
tab1, tab2 = st.tabs(["**📢 Report a New Issue**", "**📊 View Dashboard**"])

# --- This is the section to add an issue ---
with tab1:
    st.header("Tell Us What Needs Fixing")
    st.markdown("Your feedback is crucial. Fill out the form below to report an issue.")
    
    with st.form("issue_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("📝 **Issue Title**", placeholder="e.g., Broken Window in Library")
            uploaded_image = st.file_uploader("🖼️ **Upload an Image** (Optional)", type=['png', 'jpg', 'jpeg'])
        with col2:
            description = st.text_area("✍️ **Description**", placeholder="Provide details about the location and nature of the issue.", height=200)
        
        submitted = st.form_submit_button("Submit Issue", use_container_width=True, type="primary")

        if submitted:
            if not title or not description:
                st.warning("Please fill out both the title and description.", icon="⚠️")
            else:
                df = load_data()
                new_id = df['issue_id'].max() + 1 if not df.empty else 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                image_path = None

                if uploaded_image is not None:
                    image_path = os.path.join(UPLOAD_FOLDER, f"issue_{new_id}_{uploaded_image.name}")
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())

                new_issue = pd.DataFrame([{
                    'issue_id': new_id, 'title': title, 'description': description,
                    'image_path': image_path, 'upvotes': 0, 'status': 'Pending',
                    'submission_date': timestamp, 'resolved_image_path': None, 'resolved_description': None
                }])
                
                df = pd.concat([df, new_issue], ignore_index=True)
                save_data(df)
                st.success("✅ Issue reported successfully! Thank you for your contribution.", icon="🎉")

# --- This is the section to view the dashboard ---
with tab2:
    st.header("Campus Issue Dashboard")
    df = load_data()
    pending_issues = df[df['status'] == 'Pending'].sort_values(by='upvotes', ascending=False)
    
    if pending_issues.empty:
        st.info("No pending issues to show.")
    else:
        num_columns = 3
        cols = st.columns(num_columns)
        for i, (index, row) in enumerate(pending_issues.iterrows()):
            with cols[i % num_columns]:
                with st.container(border=True, height=450):
                    st.subheader(row['title'])
                    if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                        st.image(row['image_path'])
                    
                    issue_id = row['issue_id']
                    upvote_button_disabled = issue_id in st.session_state.upvoted_issues
                    button_label = "Upvoted ✔️" if upvote_button_disabled else f"{int(row['upvotes'])} Upvote 👍"
                    
                    if st.button(button_label, key=f"student_upvote_{issue_id}", use_container_width=True, disabled=upvote_button_disabled):
                        row_index = df.index[df['issue_id'] == issue_id].tolist()[0]
                        df.loc[row_index, 'upvotes'] += 1
                        save_data(df)
                        st.session_state.upvoted_issues.append(issue_id)
                        st.rerun()