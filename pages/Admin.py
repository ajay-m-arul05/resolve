import streamlit as st
import pandas as pd
import os

# --- Configuration & Helpers ---
CSV_FILE = 'issues.csv'
SOLUTION_FOLDER = 'solutions'
ADMIN_PASSWORD = "admin" 

def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        return pd.DataFrame()
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# --- Admin Authentication ---
def check_password():
    if "password_entered" not in st.session_state:
        st.session_state.password_entered = False

    if st.session_state.password_entered:
        return True

    st.header("🔑 Admin Login")
    password = st.text_input("Enter Admin Password", type="password")
    if st.button("Login", use_container_width=True):
        if password == ADMIN_PASSWORD:
            st.session_state.password_entered = True
            st.rerun()
        else:
            st.error("The password you entered is incorrect.", icon="🚨")
    return False

# --- Page Initialization ---
st.set_page_config(page_title="Admin Panel", page_icon="🔑", layout="wide")

if not check_password():
    st.stop() 

# --- Main Admin Interface ---
st.title("🔑 Admin Control Panel")
st.markdown("Manage and resolve student-reported issues from this dashboard.")

df = load_data()
pending_issues = df[df['status'] == 'Pending'].sort_values(by='upvotes', ascending=False)

st.header(f"Prioritized Issue List ({len(pending_issues)} Pending)")

if pending_issues.empty:
    st.success("🎉 All issues have been resolved! Great work.", icon="✅")
else:
    for index, row in pending_issues.iterrows():
        with st.container(border=True):
            st.subheader(f"#{int(row['issue_id'])}: {row['title']}")
            
            col1, col2 = st.columns(2)
            
            with col1: # Issue Details
                st.markdown("**Issue Details**")
                st.write(f"**Upvotes:** {int(row['upvotes'])} 👍")
                st.write(f"**Submitted:** {row['submission_date']}")
                st.write(f"**Description:** {row['description']}")
                if pd.notna(row['image_path']) and os.path.exists(str(row['image_path'])):
                    st.image(str(row['image_path']), caption="Student-submitted image")
                else:
                    st.write("No image submitted.")
            
            with col2: # Resolution Form
                st.markdown("**Resolve This Issue**")
                solution_description = st.text_area("Solution Description", key=f"desc_{row['issue_id']}", height=150)
                solution_image = st.file_uploader("Upload Solution Image", type=['png', 'jpg', 'jpeg'], key=f"img_{row['issue_id']}")
                
                if st.button("Mark as Resolved", key=f"resolve_{row['issue_id']}", use_container_width=True, type="primary"):
                    if not solution_description:
                        st.warning("Please provide a solution description.", icon="⚠️")
                    else:
                        solution_image_path = None
                        if solution_image is not None:
                            solution_image_path = os.path.join(SOLUTION_FOLDER, f"solution_{int(row['issue_id'])}_{solution_image.name}")
                            with open(solution_image_path, "wb") as f:
                                f.write(solution_image.getbuffer())
                        
                        df.loc[df['issue_id'] == row['issue_id'], 'status'] = 'Resolved'
                        df.loc[df['issue_id'] == row['issue_id'], 'resolved_description'] = solution_description
                        df.loc[df['issue_id'] == row['issue_id'], 'resolved_image_path'] = solution_image_path
                        
                        save_data(df)
                        st.toast(f"Issue #{int(row['issue_id'])} resolved!", icon="🎉")
                        st.rerun()