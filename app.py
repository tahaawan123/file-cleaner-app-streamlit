import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Initialize session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = {}

# Page Configuration
st.set_page_config(page_title="📊 Data Sweeper Pro", page_icon="🫉", layout="wide")
st.title("📊 Data Sweeper Pro 🏆✨")
st.markdown("🔍 *Advanced file processing with persistent state management* 🖥️💾")

# Function to process files
def process_file(file):
    file_id = f"{file.name}_{file.size}"
    if file_id not in st.session_state.processed_files:
        st.session_state.processed_files[file_id] = {
            'df': None, 'cleaned': False, 'converted': False, 'to_delete': False, 'original_name': file.name
        }
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            st.session_state.processed_files[file_id]['df'] = df
        except Exception as e:
            st.error(f"❌ Error loading {file.name}: {str(e)}")
            st.session_state.processed_files[file_id]['to_delete'] = True

# File Uploader
uploaded_files = st.file_uploader("💄 Upload Files (CSV/XLSX) 📂📊", type=["csv", "xlsx"], accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        process_file(file)

# Processed Files Display
deleted_files = []
for file_id, file_data in st.session_state.processed_files.items():
    if file_data['to_delete']:
        deleted_files.append(file_id)
        continue
    
    with st.expander(f"📝 {file_data['original_name']} 📜✨", expanded=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**File ID:** `{file_id}` 🏷️")
        with col2:
            if st.button(f"🗑️ Delete ❌", key=f"del_{file_id}"):
                st.session_state.processed_files[file_id]['to_delete'] = True
                st.rerun()
        
        if file_data['df'] is not None:
            df = file_data['df']
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("📏 Rows", df.shape[0])
            m_col2.metric("📐 Columns", df.shape[1])
            m_col3.metric("🚨 Missing Values", df.isna().sum().sum())
            
            rows_to_display = st.selectbox("👀 Select number of rows to display:", [5, 10, 25, 50, 100], index=1, key=f"rows_{file_id}")
            st.subheader("🫄 Cleaning Tools 🧼✨")
            
            clean_col1, clean_col2 = st.columns(2)
            if clean_col1.button(f"🫉 Remove Duplicates 🗑️", key=f"dup_{file_id}"):
                df = df.drop_duplicates()
                st.session_state.processed_files[file_id]['df'] = df
                st.success("✅ Duplicates removed!")
                
            if clean_col2.button(f"🔧 Fill Missing Values 🛠️", key=f"fill_{file_id}"):
                numeric_cols = df.select_dtypes(include='number').columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.session_state.processed_files[file_id]['df'] = df
                st.success("✅ Missing values filled!")
                
            selected_columns = st.multiselect("📌 Select columns to keep:", df.columns, default=df.columns.tolist(), key=f"cols_{file_id}")
            df = df[selected_columns]
            st.session_state.processed_files[file_id]['df'] = df
            
            st.subheader("🔍 Data Preview 🕵️‍♂️")
            st.dataframe(df.head(rows_to_display), use_container_width=True)
            
            st.subheader("🔄 Format Conversion 🔄")
            conv_col1, conv_col2 = st.columns([3, 1])
            conversion_format = conv_col1.radio("🎯 Select output format:", ["CSV", "Excel"], horizontal=True, key=f"conv_{file_id}")
            
            if conv_col2.button(f"⚡ Convert 🔃", key=f"conv_btn_{file_id}"):
                buffer = BytesIO()
                try:
                    mime_type, ext = ("text/csv", ".csv") if conversion_format == "CSV" else ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")
                    if conversion_format == "CSV":
                        df.to_csv(buffer, index=False)
                    else:
                        df.to_excel(buffer, index=False)
                    buffer.seek(0)
                    st.session_state.processed_files[file_id]['converted'] = True
                    st.success("🎉 Conversion successful!")
                    st.download_button(label=f"⏬ Download {conversion_format} 📥", data=buffer, file_name=f"converted_{file_data['original_name']}{ext}", mime=mime_type, key=f"dn_{file_id}")
                except Exception as e:
                    st.error(f"⚠️ Conversion failed: {str(e)}")

# Cleanup Deleted Files
for file_id in deleted_files:
    del st.session_state.processed_files[file_id]

if not st.session_state.processed_files:
    st.info("ℹ️ No files currently uploaded. Add files to begin processing. 📂")
else:
    st.balloons()
    st.success(f"✅ Active files: {len(st.session_state.processed_files)} 🎉")