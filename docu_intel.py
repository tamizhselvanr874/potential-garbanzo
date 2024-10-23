import streamlit as st  
from azure.ai.formrecognizer import DocumentAnalysisClient  
from azure.core.credentials import AzureKeyCredential  
from azure.core.exceptions import HttpResponseError  
import re  
  
# Azure Form Recognizer setup  
form_recognizer_endpoint = "https://patentocr.cognitiveservices.azure.com/"  
form_recognizer_api_key = "cd6b8996d93447be88d995729c924bcb"  
  
# Initialize session state variables  
if 'application_number' not in st.session_state:  
    st.session_state.application_number = None  
if 'conflict_keyword' not in st.session_state:  
    st.session_state.conflict_keyword = None  
  
# Function to extract application number and conflict keyword from Office Action  
def validate_office_action(uploaded_file):  
    if not uploaded_file:  
        st.error("No file uploaded.")  
        return False, None, None  
  
    try:  
        file_content = uploaded_file.read()  
  
        document_analysis_client = DocumentAnalysisClient(  
            endpoint=form_recognizer_endpoint,  
            credential=AzureKeyCredential(form_recognizer_api_key),  
        )  
  
        poller = document_analysis_client.begin_analyze_document(  
            "prebuilt-document", document=file_content  
        )  
  
        result = poller.result()  
  
        application_number = None  
        conflict_keyword = None  
        summary_found = False  
  
        for page in result.pages:  
            for line in page.lines:  
                content = line.content.lower()  
  
                if "application no" in content or "control number" in content:  
                    application_number = line.content.split()[-1]  
  
                if "office action summary" in content:  
                    summary_found = True  
  
                if "rejected" in content and "102(a)(1)" in content:  
                    match = re.search(r"by (\w+)", line.content)  
                    if match:  
                        conflict_keyword = match.group(1)  
  
        if application_number and summary_found:  
            return True, application_number, conflict_keyword  
  
        st.error("The uploaded document is not a valid Office Action.")  
        return False, None, None  
  
    except HttpResponseError as e:  
        st.error(f"Failed to analyze the document: {e.message}")  
        return False, None, None  
  
# Function to validate referenced documents using conflict keyword  
def validate_referenced_document(uploaded_file, conflict_keyword):  
    if not uploaded_file:  
        st.error("No file uploaded.")  
        return False  
  
    try:  
        file_content = uploaded_file.read()  
  
        document_analysis_client = DocumentAnalysisClient(  
            endpoint=form_recognizer_endpoint,  
            credential=AzureKeyCredential(form_recognizer_api_key),  
        )  
  
        poller = document_analysis_client.begin_analyze_document(  
            "prebuilt-document", document=file_content  
        )  
  
        result = poller.result()  
  
        for page in result.pages:  
            for line in page.lines:  
                if conflict_keyword and conflict_keyword.lower() in line.content.lower():  
                    st.success(f"Referenced document validated successfully with keyword '{conflict_keyword}'!")  
                    return True  
  
        st.error(f"The document does not contain the expected keyword: {conflict_keyword}.")  
        return False  
  
    except HttpResponseError as e:  
        st.error(f"Failed to analyze the document: {e.message}")  
        return False  
  
# Function to validate application as filed  
def validate_application_as_filed(uploaded_file, expected_application_number):  
    if not uploaded_file:  
        st.error("No file uploaded.")  
        return False  
  
    try:  
        file_content = uploaded_file.read()  
  
        document_analysis_client = DocumentAnalysisClient(  
            endpoint=form_recognizer_endpoint,  
            credential=AzureKeyCredential(form_recognizer_api_key),  
        )  
  
        poller = document_analysis_client.begin_analyze_document(  
            "prebuilt-document", document=file_content  
        )  
  
        result = poller.result()  
  
        for page in result.pages:  
            for line in page.lines:  
                if expected_application_number in line.content:  
                    st.success("Application as Filed validated successfully!")  
                    return True  
  
        st.error(f"The document does not contain the expected application number: {expected_application_number}.")  
        return False  
  
    except HttpResponseError as e:  
        st.error(f"Failed to analyze the document: {e.message}")  
        return False  
  
# Function to validate pending claims  
def validate_pending_claims(uploaded_file, expected_application_number):  
    if not uploaded_file:  
        st.error("No file uploaded.")  
        return False  
  
    try:  
        file_content = uploaded_file.read()  
  
        document_analysis_client = DocumentAnalysisClient(  
            endpoint=form_recognizer_endpoint,  
            credential=AzureKeyCredential(form_recognizer_api_key),  
        )  
  
        poller = document_analysis_client.begin_analyze_document(  
            "prebuilt-document", document=file_content  
        )  
  
        result = poller.result()  
  
        for page in result.pages:  
            for line in page.lines:  
                if expected_application_number in line.content:  
                    st.success("Pending claims document validated successfully!")  
                    return True  
  
        st.error(f"The document does not contain the expected application number: {expected_application_number}.")  
        return False  
  
    except HttpResponseError as e:  
        st.error(f"Failed to analyze the document: {e.message}")  
        return False  
  
# Step 1: Office Action  
st.header("Step 1: Office Action")  
uploaded_examiner_file = st.file_uploader("Upload Examiner Document", type=["pdf", "docx"])  
if st.button("Validate Office Action"):  
    if uploaded_examiner_file:  
        is_valid, application_number, conflict_keyword = validate_office_action(uploaded_examiner_file)  
        if is_valid:  
            st.session_state.application_number = application_number  
            st.session_state.conflict_keyword = conflict_keyword  
            st.success("Office Action validated successfully!")  
        else:  
            st.warning("Please upload a valid Office Action document.")  
  
# Step 2: Referenced Documents - Failed
if st.session_state.application_number:  
    st.header("Step 2: Referenced Documents")  
    uploaded_ref_file = st.file_uploader("Upload Referenced Document", type=["pdf"])  
    if st.button("Validate Referenced Document"):  
        if uploaded_ref_file:  
            if validate_referenced_document(uploaded_ref_file, st.session_state.conflict_keyword):  
                st.success("Referenced document validated successfully!")  
            else:  
                st.warning(f"Please upload the correct referenced document containing keyword: {st.session_state.conflict_keyword}.")  
  
# Step 3: Application as Filed  
if st.session_state.application_number:  
    st.header("Step 3: Application as Filed")  
    uploaded_filed_app = st.file_uploader("Upload Application as Filed", type=["pdf"])  
    if st.button("Validate Application as Filed"):  
        if uploaded_filed_app:  
            if validate_application_as_filed(uploaded_filed_app, st.session_state.application_number):  
                st.success("Application as Filed validated successfully!")  
            else:  
                st.warning(f"Please upload the correct application document containing application number: {st.session_state.application_number}.")  
  
# Step 4: Pending Claims  
if st.session_state.application_number:  
    st.header("Step 4: Pending Claims")  
    uploaded_pending_claims_file = st.file_uploader("Upload Pending Claims Document", type=["pdf", "docx"])  
    if st.button("Validate Pending Claims"):  
        if uploaded_pending_claims_file:  
            if validate_pending_claims(uploaded_pending_claims_file, st.session_state.application_number):  
                st.success("Pending claims document validated successfully!")  
            else:  
                st.warning(f"Please upload the correct pending claims document containing application number: {st.session_state.application_number}.")  
