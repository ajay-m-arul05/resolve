import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Resolve - College Issue Dashboard",
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

# Initialize session state for upvoting to prevent multiple votes per session
if 'upvoted_issues' not in st.session_state:
    st.session_state.upvoted_issues = []


# --- Main Page UI ---
st.title("🏫 Resolve: College Issue Dashboard")
st.markdown("A platform to report, track, and resolve campus issues. Upvote the issues that matter most to you!")
st.markdown("---")

# --- Main Dashboard with Tabs ---
tab1, tab2 = st.tabs(["⏳ Pending Issues", "✅ Resolved Issues"])

# Load data once
df = load_data()

# --- Tab 1: Pending Issues ---
with tab1:
    st.header("Issues Awaiting Action")
    
    pending_issues = df[df['status'] == 'Pending'].sort_values(by='upvotes', ascending=False)
    
    if pending_issues.empty:
        st.info("No pending issues at the moment. Great!")
    else:
        for index, row in pending_issues.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{row['title']}**")
                    st.caption(f"Submitted on: {row['submission_date']}")
                    if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                        st.image(row['image_path'], width=300)
                    with st.expander("See Details"):
                        st.write(row['description'])
                        
                with col2:
                    st.metric(label="Upvotes", value=int(row['upvotes']))
                    issue_id = row['issue_id']
                    
                    # Upvote button logic
                    if st.button("Upvote 👍", key=f"upvote_{issue_id}", disabled=(issue_id in st.session_state.upvoted_issues)):
                        # Find the index of the row to update
                        row_index = df.index[df['issue_id'] == issue_id].tolist()[0]
                        df.loc[row_index, 'upvotes'] += 1
                        save_data(df)
                        st.session_state.upvoted_issues.append(issue_id)
                        st.rerun()

# --- Tab 2: Resolved Issues ---
with tab2:
    st.header("Issues That Have Been Resolved")
    
    resolved_issues = df[df['status'] == 'Resolved'].sort_values(by='submission_date', ascending=False)

    if resolved_issues.empty:
        st.info("No issues have been resolved yet.")
    else:
        for index, row in resolved_issues.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['title']}**")
                st.caption(f"Submitted on: {row['submission_date']}")
                st.success("Status: Resolved")
                
                with st.expander("View Details and Solution"):
                    # Original Issue
                    st.markdown("**Original Issue:**")
                    st.write(row['description'])
                    if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                        st.image(row['image_path'], caption="Image provided by student")
                    
                    st.markdown("---")
                    
                    # Admin's Solution
                    st.markdown("**Admin's Solution:**")
                    st.write(row['resolved_description'])
                    if pd.notna(row['resolved_image_path']) and os.path.exists(row['resolved_image_path']):
                        st.image(row['resolved_image_path'], caption="Image of the solution")

st.sidebar.success("Select a page above to begin.")