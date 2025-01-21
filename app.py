import streamlit as st
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
from rss_parser import parse_rss_feed
from stylesheet_generator import generate_stylesheet

def get_rss_feed(publication_url):
    """Fetch RSS feed from a Substack publication URL."""
    # Clean the URL
    publication_url = publication_url.rstrip('/')
    
    # Try different RSS feed URL patterns
    feed_urls = [
        f"{publication_url}/feed",  # Standard pattern
        f"{publication_url}/rss",   # Alternative pattern
        f"https://{publication_url.split('/')[-1]}.substack.com/feed"  # Convert custom domain to substack.com
    ]
    
    last_error = None
    for feed_url in feed_urls:
        try:
            response = requests.get(feed_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            last_error = e
            continue
    
    # If we get here, none of the URLs worked
    raise Exception(f"Could not fetch RSS feed. Please ensure this is a valid Substack publication URL. Last error: {last_error}")

def main():
    st.title("Substack Stylesheet Generator")
    
    # User input for Substack URL
    publication_url = st.text_input(
        "Enter Substack Publication URL",
        placeholder="https://example.substack.com"
    )
    
    # Default prompt text
    default_prompt = """You are an expert ghostwriter who manages a team of junior ghostwriters. 
I am going to give you a bunch of sample content from a client you are working with, 
and I want you to extract a stylesheet. It should be something you can give to your 
junior ghostwriters so they can reliably produce content that sounds exactly like 
the client's voice. Pay attention to tone, style, and sentence construction. 
Avoid giving overly specific examples from one piece, as those might be over-applied. 
Instead, provide multiple examples that highlight a clear style or tone.

Here is the sample content:

"""
    
    # Text area for the user to adjust the prompt
    user_prompt = st.text_area(
        "Adjust Prompt (Optional)",
        value=default_prompt,
        height=150
    )
    
    # Create two columns for the buttons
    col1, col2 = st.columns(2)
    with col1:
        # Disable the button if publication_url is empty
        generate_with_claude = st.button("Generate with Claude", key="generate_with_claude", disabled=not publication_url)
    
    with col2:
        # Disable the button if publication_url is empty
        generate_with_gpt = st.button("Generate with GPT", key="generate_with_gpt", disabled=not publication_url)
    
    # Variable to hold the generated stylesheet
    stylesheet = None
    
    if publication_url:
    
        if generate_with_gpt:  # Check if the GPT button was clicked
            ai_choice = "gpt"
            try:
                with st.spinner("Fetching RSS feed..."):
                    rss_content = get_rss_feed(publication_url)
                
                with st.spinner("Parsing content..."):
                    publication_data = parse_rss_feed(rss_content)
                
                with st.spinner("Generating stylesheet..."):
                    stylesheet = generate_stylesheet(publication_data, ai_choice)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
        elif generate_with_claude:  # Check if the Claude button was clicked
            ai_choice = "claude"
            try:
                with st.spinner("Fetching RSS feed..."):
                    rss_feed = get_rss_feed(publication_url)
                
                with st.spinner("Parsing content..."):
                    publication_data = parse_rss_feed(rss_feed)
                
                with st.spinner("Generating stylesheet..."):
                    stylesheet = generate_stylesheet(publication_data, ai_choice)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Display the generated stylesheet with markdown formatting
    if stylesheet:
        st.markdown(stylesheet)
        
        # Add download button
        st.download_button(
            label="Download Stylesheet",
            data=stylesheet,
            file_name="publication_style.txt",
            mime="text/plain"
        )
        
    
    

if __name__ == "__main__":
    main()
