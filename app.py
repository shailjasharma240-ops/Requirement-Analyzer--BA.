import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI-Powered Requirements Analyzer", layout="wide")

st.title("AI-Powered Requirements Analyzer")
st.write("Convert messy stakeholder notes into clean BRD, Requirements, User Stories & Conflicts.")

# Sidebar - API Key
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password", help="Get free key from console.groq.com")
st.sidebar.write("Model: openai/gpt-oss-120b (Locked)")
st.sidebar.write("Cost: 100% Free - Groq Free Tier")

# Sample Data - Hospital
st.subheader("1. Input Messy Requirements")

sample_data = """MEETING NOTES:
Dr. Mehta said 10-12 patients out of 40-50 do not show up daily. Ramesh said 2 patients were given same slot once. Priya said app should be in Hindi, elderly cannot use English app. Mrs. Verma said launch in 2 months, budget limited. Dr. Mehta said patient data must be secure. Insurance point was missed.

EMAIL FROM ADMIN:
Patient should book online. Payment UPI and Card both. Reminder 1 day before and same day morning. Admin should add/remove doctor. App should be fast, should not hang. Language English or Hindi? Let's decide later. Also add AI chatbot? Cost?

【entity-WHATSAPP¦canonical_name=WhatsApp】 CHAT:
Patient paid but booking not confirmed, money deducted. Duplicate booking with same name. Keep 2 slots reserved for emergency. What if no internet? Daily report needed in Excel - how many came, cancelled, collection.

CALL TRANSCRIPT:
Normal patient 10 min, new patient 15-20 min. If patient >10 min late then unclear. Cancellation up to 2 hours before full refund, after that 50% or no refund? Ask Verma ji. Doctor wants notifications on 【entity-WhatsApp¦canonical_name=WhatsApp】, not SMS.
"""

if st.button("Load Hospital Sample Data"):
    st.session_state["messy_input"] = sample_data

messy_input = st.text_area(
    "Paste messy notes here (Meeting / Email / 【entity-WhatsApp¦canonical_name=WhatsApp】 / Call)",
    value=st.session_state.get("messy_input", ""),
    height=250
)

# Master Prompt - Version 2 (Your BA Brain)
MASTER_PROMPT = """
You are a Senior Business Analyst with 10 years experience.

From the messy notes below, do:
1. Write Problem Statement in 4 lines
2. Extract 8 Functional Requirements (FR) with ID, Priority High/Medium/Low
3. Extract 4 Non-Functional Requirements (NFR)
4. Create 5 User Stories in format: As a [user], I want [feature] so that [benefit]
5. Find 3 Conflicts
6. Find 3 Missing Info - mark as [NEEDS CLARIFICATION] - Do NOT assume.

Strict Rules:
1. Do NOT merge 2 different requirements into 1. Example: Admin managing doctors is DIFFERENT from Doctor managing own availability. List them separately.
2. Capture ALL business rules with numbers: Appointment duration, Late arrival rule, Cancellation window, Emergency slot count. If a number is missing, mark as [NEEDS CLARIFICATION].
3. Check for Scope vs Time vs Budget conflict: If any new feature like AI Chatbot is requested, compare it with 2-month deadline and limited budget and flag as Conflict if it does not fit.
"""

# Analyze Button - Part 2 Real AI Connection
if st.button("Analyze Requirements"):
    if not api_key:
        st.error("Please enter Groq API Key in sidebar.")
    elif not messy_input:
        st.error("Please paste requirements or load sample data.")
    else:
        try:
            with st.spinner("Analyzing with AI... Finding requirements, conflicts & missing info... This takes 10-20 seconds."):
                client = Groq(api_key=api_key)

                full_prompt = MASTER_PROMPT + "\n\nMessy Notes:\n" + messy_input

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": "You are a Senior Business Analyst."},
                        {"role": "user", "content": full_prompt}
                    ]
                )

                result = response.choices[0].message.content

                # Save for Part 3 Export
                st.session_state["ai_result"] = result

                st.success("Analysis Complete!")
                st.subheader("2. AI Analysis Result")
                st.markdown(result)

                # Download as Text - Simple Export for Part 2
                st.download_button(
                    label="Download Full Report as .txt",
                    data=result,
                    file_name="BRD-Analysis.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Check if your Groq API Key is correct. If you see Quota error, wait 60 seconds and try again. Free tier has limit.")
