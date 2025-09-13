import streamlit as st
import pandas as pd
import os

# --- Configuration ---
CSV_FILE = 'issues.csv'
SOLUTION_FOLDER = 'solutions'
ADMIN_PASSWORD = "admin" # Replace with a more secure method in a real app

# --- Helper Functions ---
def load_data():
    """Loads the issues data from the CSV file."""
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        # This case should ideally be handled by the initialization on the Home page
        return pd.DataFrame()
    return df

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    df.to_csv(CSV_FILE, index=False)

# --- Admin Authentication ---
def check_password():
    """Returns `True` if the user has entered the correct password."""
    if "password_entered" not in st.session_state:
        st.session_state.password_entered = False

    if st.session_state.password_entered:
        return True

    password = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.password_entered = True
            st.rerun()
        else:
            st.error("The password you entered is incorrect.")
    return False

# --- Page Initialization ---
st.set_page_config(page_title="Admin Panel", page_icon="🔑")
st.title("🔑 Admin Panel")

if not check_password():
    st.stop() # Do not render the rest of the page if the password is wrong

# --- Main Admin Interface ---
st.header("Issue Management")

df = load_data()
pending_issues = df[df['status'] == 'Pending'].sort_values(by='upvotes', ascending=False)

if pending_issues.empty:
    st.success("🎉 No pending issues to resolve!")
else:
    st.info(f"You have {len(pending_issues)} pending issues.")
    
    for index, row in pending_issues.iterrows():
        st.subheader(f"Issue #{int(row['issue_id'])}: {row['title']}")
        
        with st.expander("Manage Issue", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Issue Details**")
                st.write(f"**Description:** {row['description']}")
                st.write(f"**Upvotes:** {int(row['upvotes'])}")
                st.write(f"**Submitted:** {row['submission_date']}")
                if pd.notna(row['image_path']) and os.path.exists(str(row['image_path'])):
                    st.image(str(row['image_path']), caption="Student-submitted image")
                else:
                    st.write("No image submitted.")
            
            with col2:
                st.markdown("**Resolve Issue**")
                solution_description = st.text_area("Solution Description", key=f"desc_{row['issue_id']}")
                solution_image = st.file_uploader("Upload Solution Image", type=['png', 'jpg', 'jpeg'], key=f"img_{row['issue_id']}")
                
                if st.button("Mark as Resolved", key=f"resolve_{row['issue_id']}"):
                    if not solution_description:
                        st.warning("Please provide a solution description.")
                    else:
                        solution_image_path = None
                        if solution_image is not None:
                            solution_image_path = os.path.join(SOLUTION_FOLDER, f"solution_{int(row['issue_id'])}_{solution_image.name}")
                            with open(solution_image_path, "wb") as f:
                                f.write(solution_image.getbuffer())
                        
                        # Update the DataFrame
                        df.loc[df['issue_id'] == row['issue_id'], 'status'] = 'Resolved'
                        df.loc[df['issue_id'] == row['issue_id'], 'resolved_description'] = solution_description
                        df.loc[df['issue_id'] == row['issue_id'], 'resolved_image_path'] = solution_image_path
                        
                        save_data(df)
                        st.success(f"Issue #{int(row['issue_id'])} has been marked as resolved!")
                        st.rerun()
        st.markdown("---")