import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Resolve ",
    page_icon="🏫",
    layout="wide"
)

# --- Helper Functions ---
def initialize_app():
    """Creates necessary folders and the CSV file if they don't exist."""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('solutions'):
        os.makedirs('solutions')

    if not os.path.exists('issues.csv'):
        df = pd.DataFrame(columns=[
            'issue_id', 'title', 'description', 'image_path', 'upvotes',
            'status', 'submission_date', 'resolved_image_path', 'resolved_description'
        ])
        df.to_csv('issues.csv', index=False)

def load_data():
    """Loads issue data from the CSV file."""
    try:
        df = pd.read_csv('issues.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()
    return df

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    df.to_csv('issues.csv', index=False)

# --- App Initialization ---
initialize_app()
if 'upvoted_issues' not in st.session_state:
    st.session_state.upvoted_issues = []


# --- Header and Metrics ---
st.title("🏫 Resolve: Your Campus Issue Hub")
st.markdown("Voice your concerns, see real-time progress, and help improve our campus together.")

df = load_data()
pending_count = len(df[df['status'] == 'Pending'])
resolved_count = len(df[df['status'] == 'Resolved'])
total_upvotes = int(df['upvotes'].sum())

col1, col2, col3 = st.columns(3)
col1.metric("⏳ Pending Issues", pending_count)
col2.metric("✅ Resolved Issues", resolved_count)
col3.metric("👍 Total Upvotes", total_upvotes)

st.markdown("---")


# --- Main Dashboard with Tabs ---
tab1, tab2 = st.tabs(["**🔥 Hot Issues (Pending)**", "**✨ Recently Resolved**"])

with tab1:
    st.header("Issues Awaiting Action")
    pending_issues = df[df['status'] == 'Pending'].sort_values(by='upvotes', ascending=False)
    
    if pending_issues.empty:
        st.info("No pending issues at the moment. Great!")
    else:
        # Create a grid of columns
        num_columns = 3
        cols = st.columns(num_columns)
        for i, (index, row) in enumerate(pending_issues.iterrows()):
            with cols[i % num_columns]:
                with st.container(border=True, height=450):
                    st.subheader(row['title'])
                    if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                        st.image(row['image_path'])
                    
                    # Upvote section
                    issue_id = row['issue_id']
                    upvote_button_disabled = issue_id in st.session_state.upvoted_issues
                    button_label = "Upvoted ✔️" if upvote_button_disabled else f"{int(row['upvotes'])} Upvote 👍"
                    
                    if st.button(button_label, key=f"upvote_{issue_id}", use_container_width=True, disabled=upvote_button_disabled):
                        row_index = df.index[df['issue_id'] == issue_id].tolist()[0]
                        df.loc[row_index, 'upvotes'] += 1
                        save_data(df)
                        st.session_state.upvoted_issues.append(issue_id)
                        st.rerun()

with tab2:
    st.header("Issues That Have Been Resolved")
    resolved_issues = df[df['status'] == 'Resolved'].sort_values(by='submission_date', ascending=False)

    if resolved_issues.empty:
        st.info("No issues have been resolved yet.")
    else:
        for index, row in resolved_issues.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(row['title'])
                    st.caption(f"Resolved on: {pd.to_datetime(row['submission_date']).strftime('%d %b %Y')}")
                    with st.expander("Show Details and Solution"):
                        st.markdown("**Original Issue:**")
                        st.write(row['description'])
                        if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                            st.image(row['image_path'], caption="Image provided by student")
                        
                        st.markdown("---")
                        st.markdown("**Admin's Solution:**")
                        st.write(row['resolved_description'])
                        if pd.notna(row['resolved_image_path']) and os.path.exists(row['resolved_image_path']):
                            st.image(row['resolved_image_path'], caption="Image of the solution")
                with col2:
                    st.success("✅ Resolved", icon="🎉")