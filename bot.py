import streamlit as st
import os
import time
from dotenv import load_dotenv
import google.generativeai as generativeai
from rapid import fetch_product_details, convert_to_inr, extract_price, extract_relevant_offers  # Import from rapid.py

# Sidebar Component
def st_sidebar():
    with st.sidebar:
        st.title("AI Chatbot")
        st.text("Feel free to ask me anything!")
        rate = st.slider("How much do you rate our App?", 0, 5, 0, step=1)
        if rate > 0:
            st.write("Thank you for your feedback! 😊")
        # Mode selection for chatbot or product bot
        mode = st.radio("Select Mode", ["Chatbot", "Product Bot"])
        return mode

# Function to display chat messages with improved UI
def display_message(role, text):
    """Display messages with distinct styles for User and Bot."""
    
    if role == "user":
        color = "#0d6efd"  # Blue for user
        align = "right"
    else:
        color = "#198754"  # Green for bot
        align = "left"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: {align}; margin: 5px 0;">
            <div style="background-color: {color}; color: white; padding: 12px; 
                        border-radius: 10px; max-width: 70%; font-size: 16px;">
                <strong>{role.upper()}:</strong> {text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Chat Session Management for chatbot mode
def session(session_key, user_prompt):
    """Handle chat session and display user & bot messages properly."""
    
    for message in st.session_state[session_key].history:
        role = "user" if message.role == "user" else "assistant"
        message_text = message.parts[0].text
        display_message(role, message_text)

    if user_prompt:
        display_message("user", user_prompt)

        # AI Response
        try:
            response = st.session_state[session_key].send_message(user_prompt)
            if response.candidates:
                assistant_text = response.candidates[0].content.parts[0].text
                display_message("assistant", assistant_text)
            else:
                st.error("No valid response from AI.")
        except Exception as e:
            st.error(f"Error during AI response: {e}")

# Product Bot to fetch product details
def product_bot():
    """Handle product-related queries and display product details."""
    product_name = st.text_input("Enter the name of the product:")
    
    if product_name:
        with st.spinner("Fetching product details..."):
            product_details = fetch_product_details(product_name)
            if product_details:
                for product in product_details:
                    st.markdown(f"**Product Name:** {product['name']}")
                    st.markdown(f"**Price:** ₹{product['price_in_inr']}")
                    st.markdown(f"**Offers:** {product['offers']}")
                    st.markdown(f"[Buy here]({product['url']})")
                    st.markdown("-" * 50)
            else:
                st.write("No product details found.")

# Main Function
def main():
    load_dotenv()
    st.set_page_config(
        page_title="AI Chatbot",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🤖 AI ChatBot using Google Gemini")

    # Load API key and configure Generative AI
    Google_API_KEY = os.getenv("GOOGLE_API_KEY")
    generativeai.configure(api_key=Google_API_KEY)
    llm = generativeai.GenerativeModel("gemini-1.5-flash")
    mode = st_sidebar()

    # Initialize chat session
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = llm.start_chat(history=[])

    # If in chatbot mode, proceed with Gemini chatbot logic
    if mode == "Chatbot":
        user_prompt = st.chat_input("Ask me anything...")
        if user_prompt:
            session("chat_session", user_prompt=user_prompt)
        
    # If in product bot mode, fetch product details
    elif mode == "Product Bot":
        product_bot()

# Run the main function
if __name__ == "__main__":
    main()
