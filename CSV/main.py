
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import csv

# Base URL for the faculty of law
base_url = "https://www.muni.cz/en/about-us/organizational-structure/faculty-of-law"

# Function to visit and scrape a department page
def visit_department_page(department_url):
    try:
        response = requests.get(department_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <li> tags with the class 'crossroad-links__item'
            li_tags = soup.find_all('li', class_='crossroad-links__item')

            for li in li_tags:
                a_tag = li.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    parts = href.split('-')

                    if len(parts) >= 2:
                        last_two_parts = parts[-2:]
                        print(f"Found contact: {last_two_parts}")

                        full_url = urljoin(base_url, href)
                        visit_individual_page(full_url, last_two_parts)
        else:
            print(f"Failed to retrieve the department page. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while visiting the department page: {e}")

# Function to extract email address from a table cell
def extract_email_address(td):
    a_tag_mailto = td.find('a', href=True, attrs={'href': lambda x: x and x.startswith('mailto:')})
    if a_tag_mailto:
        email_address = a_tag_mailto['href'].split('mailto:')[-1]
        return email_address
    return None

# Function to extract phone number from a table cell
def extract_phone_number(td):
    a_tag_tel = td.find('a', href=True, attrs={'href': lambda x: x and x.startswith('tel:')})
    if a_tag_tel:
        phone_number = a_tag_tel['href'].split('tel:')[-1]
        return phone_number
    return None

# Function to visit individual contact page and extract details
def visit_individual_page(url, name_parts):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Visiting URL: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='table-vcard')

            name = ' '.join(part.capitalize() for part in name_parts)
            email = None
            phone = None

            if table:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        if 'E‑mail' in th.text:
                            email = extract_email_address(td)
                        elif 'Phone' in th.text:
                            phone = extract_phone_number(td)
            
            if email:
                print(f"Email address found for {name}: {email}")
                save_to_csv(name, email, 'contacts_emails.csv')
            else:
                print(f"No email address found for {name}")

            if phone:
                print(f"Phone number found for {name}: {phone}")
                save_to_csv(name, phone, 'contacts_phones.csv')
            else:
                print(f"No phone number found for {name}")

            # Handle pagination if there's any
            next_link = soup.find('a', text='Next')
            if next_link and 'href' in next_link.attrs:
                next_page_url = urljoin(url, next_link['href'])
                time.sleep(random.uniform(1, 3))  # Adding a random delay
                visit_individual_page(next_page_url, name_parts)
        else:
            print(f"Failed to retrieve the individual's page. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while visiting the individual's page: {e}")

# Function to save extracted data to a CSV file
def save_to_csv(name, contact, filename):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name, contact])

# Function to scrape the faculty page and find department links
def scrape_faculty_page(base_url):
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <li> tags with the class 'crossroad-links__item'
            li_tags = soup.find_all('li', class_='crossroad-links__item')

            for li in li_tags:
                a_tag = li.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    # Check if the link is for a department
                    if 'faculty-of-law' in href:
                        department_url = urljoin(base_url, href)
                        print(f"Found department URL: {department_url}")
                        time.sleep(random.uniform(1, 3))  # Adding a random delay
                        visit_department_page(department_url)
        else:
            print(f"Failed to retrieve the faculty page. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while scraping the faculty page: {e}")

# Start scraping from the faculty page
scrape_faculty_page(base_url)

