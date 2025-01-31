import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Define the base URLs
BASE_URL = "http://tasi.org/en/member/index_member_02.asp"
DETAIL_URL_TEMPLATE = "http://tasi.org/en/member/index_member_02.asp?F={}"

def fetch_member_details(detail_url):
    """
    Fetch detailed information from the provided member detail URL.

    Args:
        detail_url (str): The URL to fetch details from.

    Returns:
        dict: A dictionary containing the member details.
    """
    try:
        response = requests.get(detail_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract details
        person_in_charge = soup.find(text="Person in charge:").find_next("td").get_text(strip=True) if soup.find(text="Person in charge:") else None
        position = soup.find(text="Position:").find_next("td").get_text(strip=True) if soup.find(text="Position:") else None
        address = soup.find(text="Address:").find_next("td").get_text(strip=True) if soup.find(text="Address:") else None
        tel = soup.find(text="Tel:").find_next("td").get_text(strip=True) if soup.find(text="Tel:") else None
        web = soup.find(text="Web:").find_next("td").get_text(strip=True) if soup.find(text="Web:") else None
        email = soup.find(text="E-mail:").find_next("td").get_text(strip=True) if soup.find(text="E-mail:") else None
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else None

        return {
            "Title": title,
            "Person in charge": person_in_charge,
            "Position": position,
            "Address": address,
            "Tel": tel,
            "Web": web,
            "E-mail": email,
        }
    except Exception as e:
        st.error(f"Error fetching details from {detail_url}: {e}")
        return None

def scrape_data():
    """
    Scrape data from the main page and fetch details for each member.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data.
    """
    try:
        # Request the main page
        response = requests.get(BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all <LI> tags within <DIV class="DATA">
        data_div = soup.find("div", class_="DATA")
        if not data_div:
            st.error("No data found on the page.")
            return pd.DataFrame()

        li_tags = data_div.find_all("li")
        if not li_tags:
            st.error("No list items found in the data div.")
            return pd.DataFrame()

        # List to hold all scraped data
        all_data = []

        # Process each <LI> tag
        for li in li_tags:
            href = li.find("a")["href"]
            if not href:
                continue

            # Construct the detail URL
            detail_url = DETAIL_URL_TEMPLATE.format(href)

            # Fetch member details
            member_details = fetch_member_details(detail_url)
            if member_details:
                all_data.append(member_details)

        # Convert list of dictionaries to DataFrame
        return pd.DataFrame(all_data)

    except Exception as e:
        st.error(f"Error scraping data: {e}")
        return pd.DataFrame()

# Streamlit app
st.title("TASI Member Data Scraper")

st.write("This app scrapes member data from the TASI website and exports it as a CSV file.")

if st.button("Start Scraping"):
    with st.spinner("Scraping data... This may take a while."):
        data = scrape_data()
        if not data.empty:
            # Display data and allow CSV download
            st.success("Scraping completed!")
            st.write(data)
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="tasi_member_data.csv",
                mime="text/csv"
            )
        else:
            st.error("No data scraped.")
