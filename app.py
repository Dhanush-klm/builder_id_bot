import streamlit as st
import pandas as pd
import json
import io
import os

def clean_filename(filename):
    # Remove the file extension
    return os.path.splitext(filename)[0]

def process_file(file, job_id):
    # Determine file type and read accordingly
    if file.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file)
    elif file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        return None  # Unsupported file type
    
    if 'job_id' not in df.columns:
        return None
    
    # Convert job_id column to string to ensure correct matching
    df['job_id'] = df['job_id'].astype(str)
    
    # Find exact match for job_id
    matching_row = df[df['job_id'] == str(job_id)]
    
    if matching_row.empty:
        return None
    
    # Get column names as comma-separated string
    columns = ", ".join(df.columns)
    
    return {
        'file_name': clean_filename(file.name),
        'columns': columns,
        'matched_data': matching_row.iloc[0].to_dict()
    }

st.title('Excel and CSV File Processor')

uploaded_files = st.file_uploader("Choose Excel or CSV files", accept_multiple_files=True, type=['xlsx', 'xls', 'csv'])
job_id = st.text_input("Enter Job ID")

if st.button('Process Files'):
    if not uploaded_files:
        st.error("Please upload at least one Excel or CSV file.")
    elif not job_id:
        st.error("Please enter a Job ID.")
    else:
        results = []
        for file in uploaded_files:
            result = process_file(file, job_id)
            if result:
                results.append(result)
        
        if results:
            st.success(f"Found matching job_id in {len(results)} file(s)")
            
            # Display file names as comma-separated list
            file_names = ", ".join([result['file_name'] for result in results])
            st.subheader("Matched Files:")
            st.write(file_names)
            
            for result in results:
                st.subheader(f"Results for: {result['file_name']}")
                st.write(f"Column names: {result['columns']}")
                st.json(result['matched_data'])
                st.write("---")
            
            # Prepare JSON output
            json_output = {
                "matched_files": file_names,
                "results": results
            }
            
            # Provide download option
            json_string = json.dumps(json_output, indent=2)
            json_bytes = json_string.encode('utf-8')
            buf = io.BytesIO(json_bytes)
            st.download_button(
                label="Download JSON",
                data=buf,
                file_name="results.json",
                mime="application/json"
            )
        else:
            st.warning(f"No matching job_id {job_id} found in any of the uploaded files")

st.sidebar.header("Instructions")
st.sidebar.info(
    "1. Upload one or more Excel (.xlsx, .xls) or CSV files using the file uploader.\n"
    "2. Enter the exact Job ID you want to search for.\n"
    "3. Click 'Process Files' to search for the Job ID in all uploaded files.\n"
    "4. Results will display matched file names (without extensions) as a comma-separated list, followed by details for each file.\n"
    "5. You can download all results as a single JSON file."
)