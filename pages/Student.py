import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
CSV_FILE = 'issues.csv'
UPLOAD_FOLDER = 'uploads'

# --- Helper Functions ---
def load_data():
    """Loads the issues data from the CSV file."""
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            'issue_id', 'title', 'description', 'image_path', 'upvotes',
            'status', 'submission_date', 'resolved_image_path', 'resolved_description'
        ])
    return df

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    df.to_csv(CSV_FILE, index=False)

# --- Page Initialization ---
st.set_page_config(page_title="Student Dashboard", page_icon="👨‍🎓")
st.title("👨‍🎓 Student Dashboard")

# Initialize session state for upvoting to prevent multiple votes per session
if 'upvoted_issues' not in st.session_state:
    st.session_state.upvoted_issues = []

# --- Main UI Tabs ---
tab1, tab2 = st.tabs(["📢 Report an Issue", "📊 Dashboard"])

# --- Tab 1: Report an Issue ---
with tab1:
    st.header("Report a New Issue")
    st.markdown("Found something that needs attention? Let us know!")

    with st.form("issue_form", clear_on_submit=True):
        title = st.text_input("Issue Title", placeholder="e.g., Broken Window in Library")
        description = st.text_area("Description", placeholder="Provide details about the location and nature of the issue.")
        uploaded_image = st.file_uploader("Upload an Image (Optional)", type=['png', 'jpg', 'jpeg'])
        submitted = st.form_submit_button("Submit Issue")

        if submitted:
            if not title or not description:
                st.warning("Please fill out both the title and description.")
            else:
                df = load_data()
                new_id = df['issue_id'].max() + 1 if not df.empty else 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                image_path = None

                if uploaded_image is not None:
                    # Save the uploaded file
                    image_path = os.path.join(UPLOAD_FOLDER, f"issue_{new_id}_{uploaded_image.name}")
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())

                new_issue = pd.DataFrame([{
                    'issue_id': new_id,
                    'title': title,
                    'description': description,
                    'image_path': image_path,
                    'upvotes': 0,
                    'status': 'Pending',
                    'submission_date': timestamp,
                    'resolved_image_path': None,
                    'resolved_description': None
                }])
                
                df = pd.concat([df, new_issue], ignore_index=True)
                save_data(df)
                st.success("✅ Issue reported successfully!")

# --- Tab 2: Dashboard ---
with tab2:
    st.header("Issue Dashboard")
    
    # Load and filter data
    df = load_data()
    pending_issues = df[df['status'] == 'Pending'].sort_values(by='upvotes', ascending=False)
    resolved_issues = df[df['status'] == 'Resolved']

    # Sub-tabs for Pending and Resolved issues
    sub_tab1, sub_tab2 = st.tabs(["⏳ Pending Issues", "✅ Resolved Issues"])

    with sub_tab1:
        st.subheader(f"Total Pending Issues: {len(pending_issues)}")
        if pending_issues.empty:
            st.info("No pending issues at the moment. Great!")
        else:
            for index, row in pending_issues.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row['title']}**")
                        st.caption(f"Submitted on: {row['submission_date']}")
                        with st.expander("Details"):
                            st.write(row['description'])
                            if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                                st.image(row['image_path'])
                    with col2:
                        st.metric(label="Upvotes", value=int(row['upvotes']))
                        # Upvote button logic
                        issue_id = row['issue_id']
                        if st.button(f"Upvote 👍", key=f"upvote_{issue_id}", disabled=(issue_id in st.session_state.upvoted_issues)):
                            df.loc[df['issue_id'] == issue_id, 'upvotes'] += 1
                            save_data(df)
                            st.session_state.upvoted_issues.append(issue_id)
                            st.rerun()

    with sub_tab2:
        st.subheader(f"Total Resolved Issues: {len(resolved_issues)}")
        if resolved_issues.empty:
            st.info("No issues have been resolved yet.")
        else:
            for index, row in resolved_issues.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['title']}**")
                    st.caption(f"Submitted on: {row['submission_date']}")
                    st.success("Status: Resolved")
                    with st.expander("View Details and Solution"):
                        st.markdown("**Original Issue:**")
                        st.write(row['description'])
                        if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                            st.image(row['image_path'], caption="Image provided by student")
                        
                        st.markdown("---")
                        st.markdown("**Admin's Solution:**")
                        st.write(row['resolved_description'])
                        if pd.notna(row['resolved_image_path']) and os.path.exists(row['resolved_image_path']):
                            st.image(row['resolved_image_path'], caption="Image of the solution")