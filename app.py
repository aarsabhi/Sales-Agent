import streamlit as st
import pandas as pd
from azure_openai import generate_pitch, summarize_call, estimate_cost
from analytics import get_kpi_dataframe
from crm_integration import fetch_customer_profile

st.set_page_config(page_title="GenAI Sales Assistant", layout="wide")

# Sidebar controls
st.sidebar.title("🧠 Smart Controls")
tone = st.sidebar.selectbox("Pitch Tone", ["Formal", "Friendly", "Urgent"])
output_channel = st.sidebar.selectbox("Output Channel", ["Email", "Call Script", "LinkedIn", "Chatbot"])

st.sidebar.markdown("---")
st.sidebar.title("⚙️ Smart Model Parameters")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max Tokens", 128, 2048, 512)
top_p = st.sidebar.slider("Top P", 0.0, 1.0, 1.0)

st.sidebar.markdown("---")
view = st.sidebar.radio("Smart Analytics View", ["KPIs", "Raw Data"])

# Main panel tabs
st.title("🤖 GenAI-powered Sales Assistant")
tabs = st.tabs(["Pitch Generator", "Call Summary", "Analytics"])

# Pitch Generator Tab
with tabs[0]:
    st.header("Personalized Pitch Generator")
    fetch_crm = st.checkbox("Fetch from CRM", value=False)
    profile_input = ""
    if fetch_crm:
        from crm_integration import list_customers, fetch_last_interaction, fetch_all_interactions
        customers = list_customers()
        customer_options = {f"{c['customer_id']} - {c['name']} ({c['company']}) - {c['needs']}": c['customer_id'] for c in customers}
        selected = st.selectbox("Select Customer", ["-- Select --"] + list(customer_options.keys()))
        last_interaction = None
        all_interactions = []
        if selected != "-- Select --":
            crm_id = customer_options[selected]
            profile_input = fetch_customer_profile(crm_id)
            last_interaction = fetch_last_interaction(crm_id)
            all_interactions = fetch_all_interactions(crm_id)
            st.success("Profile loaded.")
            st.text_area("Profile", value=profile_input, height=150, key="crm_profile")
            if last_interaction:
                st.markdown(f"""
                <div style='background-color:#f6f6fa; border-radius:8px; padding:12px; margin-bottom:8px;'>
                    <b>Last Interaction</b><br>
                    <b>Date:</b> {last_interaction['date']}<br>
                    <b>Type:</b> {last_interaction['interaction_type']}<br>
                    <b>Status:</b> <span style='color:#0072C6'>{last_interaction['status']}</span><br>
                    <b>Summary:</b> {last_interaction['summary']}
                </div>
                """, unsafe_allow_html=True)
                # Smart suggestions
                smart_options = []
                status = last_interaction['status'].lower()
                summary = last_interaction['summary'].lower()
                # Advanced smart options with context-aware actions
                if "awaiting" in status or "follow-up" in status:
                    smart_options = ["Schedule a call", "Mark as closed"]
                elif "demo" in summary or "demo" in status:
                    smart_options = ["Send demo materials", "Schedule next meeting", "Mark as closed"]
                elif "closed won" in status:
                    smart_options = ["Send congratulations email", "Archive customer", "Start new opportunity"]
                elif "closed lost" in status or "lost" in summary:
                    smart_options = ["Send lost deal email", "Schedule feedback call", "Start new opportunity"]
                else:
                    smart_options = ["Schedule a call", "Mark as closed"]
                st.markdown("<b>Smart Suggestions for Next Steps:</b>", unsafe_allow_html=True)
                chosen_action = st.selectbox("Choose a Smart Decision", ["-- Select --"] + smart_options, key="action_select")
                action_result = ""
                custom_message = ""
                if chosen_action and chosen_action != "-- Select --":
                    from crm_integration import add_interaction
                    # Map action to interaction_type and status
                    if "congratulations" in chosen_action.lower():
                        interaction_type = "Email"
                        status = "Closed won"
                        smart_action_type = "congratulations"
                    elif "lost deal" in chosen_action.lower():
                        interaction_type = "Email"
                        status = "Closed lost"
                        smart_action_type = "lost_deal"
                    elif "email" in chosen_action.lower():
                        interaction_type = "Email"
                        status = "Awaiting response"
                        smart_action_type = "followup"
                    elif "call" in chosen_action.lower():
                        interaction_type = "Call"
                        status = "Follow-up required"
                        smart_action_type = "call"
                    elif "demo" in chosen_action.lower():
                        interaction_type = "Demo"
                        status = "Demo scheduled"
                        smart_action_type = "demo"
                    elif "closed" in chosen_action.lower():
                        interaction_type = "Update"
                        status = "Closed won"
                        smart_action_type = "closed"
                    elif "archive" in chosen_action.lower():
                        interaction_type = "Update"
                        status = "Archived"
                        smart_action_type = "archive"
                    elif "opportunity" in chosen_action.lower():
                        interaction_type = "Update"
                        status = "New opportunity"
                        smart_action_type = "opportunity"
                    else:
                        interaction_type = "Update"
                        status = chosen_action
                        smart_action_type = "other"
                    st.info(f"You chose: {chosen_action}. You can add a personal touch to this smart action.")
                    custom_message = st.text_area("Add a custom message or details (optional):", key="custom_msg_area")
                    if st.button(f"Generate Smart Message & Log Action", key="log_action_btn"):
                        # Use LLM to generate a personalized message for the chosen action
                        try:
                            context = f"Customer Profile:\n{profile_input}\nLast Interaction: {last_interaction['summary']} (Status: {last_interaction['status']})"
                            # Smart prompt based on action
                            if smart_action_type == "congratulations":
                                prompt = f"You are a sales assistant. Write a warm, professional congratulations email to the customer for winning the deal. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "lost_deal":
                                prompt = f"You are a sales assistant. Write a polite, empathetic email to the customer after losing the deal, offering to stay in touch and requesting feedback. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "followup":
                                prompt = f"You are a sales assistant. Write a follow-up email regarding the previous discussion. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "call":
                                prompt = f"You are a sales assistant. Write a call script or call scheduling message for the customer. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "demo":
                                prompt = f"You are a sales assistant. Write a message about demo materials or scheduling a demo. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "closed":
                                prompt = f"You are a sales assistant. Write a message confirming the deal closure. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "archive":
                                prompt = f"You are a sales assistant. Write a message to archive the customer and thank them for their engagement. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            elif smart_action_type == "opportunity":
                                prompt = f"You are a sales assistant. Write a message to start a new opportunity with the customer. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            else:
                                prompt = f"You are a sales assistant. Write a message for the action: '{chosen_action}'. {f'Personal note: {custom_message}' if custom_message else ''}\n\n{context}"
                            # Securely retrieve credentials from st.secrets
                            az_key = st.secrets.get("AZURE_OPENAI_KEY", "")
                            az_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
                            az_deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
                            smart_message, _ = generate_pitch(prompt, tone, output_channel, az_key, az_endpoint, az_deployment, temperature, max_tokens, top_p)
                        except Exception as e:
                            smart_message = f"[Error generating smart message: {e}]"
                        st.success("Smart message generated and CRM updated!")
                        st.text_area("Generated Smart Message", value=smart_message, height=180, key="smart_msg_out")
                        # Log the actual smart message in CRM
                        new_summary = f"{chosen_action}: {smart_message}"
                        add_interaction(crm_id, new_summary, interaction_type, status)
                        st.rerun()
            if all_interactions:
                with st.expander("Show All Previous Interactions"):
                    for i in all_interactions:
                        st.markdown(f"""
                        <div style='background-color:#fcfcfc; border-radius:6px; padding:8px; margin-bottom:4px;'>
                            <b>Date:</b> {i['date']} | <b>Type:</b> {i['interaction_type']} | <b>Status:</b> <span style='color:#0072C6'>{i['status']}</span><br>
                            <b>Summary:</b> {i['summary']}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Select a customer to load their profile.")
    else:
        profile_input = st.text_area("Enter Customer Profile or Paste CRM Data:")
        last_interaction = None
    prompt_preview = st.expander("Prompt Preview")
    with prompt_preview:
        st.write(f"**Tone:** {tone}\n**Channel:** {output_channel}\n**Profile:**\n{profile_input}")
        if fetch_crm and last_interaction:
            st.write(f"**Last Interaction:** {last_interaction['summary']} (Status: {last_interaction['status']})")
    if st.button("Generate Smart Pitch"):
        with st.spinner("Generating smart pitch..."):
            try:
                # Securely retrieve credentials from st.secrets
                az_key = st.secrets.get("AZURE_OPENAI_KEY", "")
                az_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
                az_deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
                # Pass last interaction context if available
                interaction_context = f"\nLast Interaction: {last_interaction['summary']} (Status: {last_interaction['status']})" if fetch_crm and last_interaction else ""
                pitch, usage = generate_pitch(profile_input + interaction_context, tone, output_channel, az_key, az_endpoint, az_deployment, temperature, max_tokens, top_p)
                st.success("Smart pitch generated!")
                st.text_area("Generated Smart Pitch", value=pitch, height=200)
                st.caption(f"Estimated Cost: ${estimate_cost(usage):.4f}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Call Summary Tab
with tabs[1]:
    st.header("Call Transcript Summarization & Sentiment")
    uploaded = st.file_uploader("Upload Call Transcript (.txt)", type=["txt"])
    if uploaded and st.button("Summarize Smart Call"):
        with st.spinner("Summarizing call and analyzing sentiment..."):
            try:
                # Securely retrieve credentials from st.secrets
                az_key = st.secrets.get("AZURE_OPENAI_KEY", "")
                az_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
                az_deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
                transcript = uploaded.read().decode("utf-8")
                summary, sentiment, highlights, usage = summarize_call(transcript, az_key, az_endpoint, az_deployment, temperature, max_tokens, top_p)
                st.success("Smart summary generated!")
                st.markdown(f"**Executive Summary:**\n{summary}")
                st.markdown(f"**Sentiment:** {sentiment}")
                st.markdown(f"**Key Takeaways:**\n{highlights}")
                st.caption(f"Estimated Cost: ${estimate_cost(usage):.4f}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Analytics Tab
with tabs[2]:
    st.header("Analytics Dashboard")
    try:
        df = get_kpi_dataframe(view)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
