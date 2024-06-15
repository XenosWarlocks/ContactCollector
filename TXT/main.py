import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os

class ContactScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_departments = set()      # Track visited departments to avoid duplicates
        self.processed_names = set()          # Track processed names to avoid duplicates
        self.processed_phone_numbers = set()  # Track processed phone numbers to avoid duplicates

        # Initialize the CSV file and write the headers if the file doesn't exist
        if not os.path.exists('contacts.csv'):
            with open('contacts.csv', 'w', newline='') as csvfile:
                fieldnames = ['Name', 'Phone Number']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

        # Ensure that the text files exist, create them if they don't
        for filename in ['names.txt', 'phone_numbers.txt', 'emails.txt', 'departments.txt']:
            if not os.path.exists(filename):
                open(filename, 'w').close()

    def visit_website(self):
        try:
            response = requests.get(self.base_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                li_tags = soup.find_all('li', class_='crossroad-links__item')
                for li in li_tags:
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        full_url = urljoin(self.base_url, href)
                        self.visit_department_url(full_url)
            else:
                print(f"Failed to retrieve the website. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def visit_department_url(self, department_url):
        try:
            response = requests.get(department_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                department_name = department_url.split('/')[-1]
                if department_url not in self.visited_departments:
                    print(f"Visiting Department URL: {department_url}")
                    self.visited_departments.add(department_url)

                    # Write the department name and URL to the departments.txt file
                    with open('departments.txt', 'a') as dept_file:
                        dept_file.write(f"{department_name} - {department_url}\n")

                    li_tags = soup.find_all('li', class_='crossroad-links__item')
                    for li in li_tags:
                        a_tag = li.find('a')
                        if a_tag and 'href' in a_tag.attrs:
                            href = a_tag['href']
                            parts = href.split('-')
                            if len(parts) >= 2:
                                last_two_parts = [part.capitalize() for part in parts[-2:]]
                                name = ' '.join(last_two_parts)

                                if name not in self.processed_names:
                                    print(f"Found Name: {name}")
                                    self.processed_names.add(name)

                                    # Write the name to the names.txt file
                                    with open('names.txt', 'a') as name_file:
                                        name_file.write(name + '\n')

                                    full_url = urljoin(department_url, href)
                                    self.visit_profile_url(full_url, name)
            else:
                print(f"Failed to retrieve the department URL. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while visiting the department URL: {e}")

    def visit_profile_url(self, profile_url, name):
        try:
            response = requests.get(profile_url)
            if response.status_code == 200:
                print(f"Visiting Profile URL: {profile_url}")
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', class_='table-vcard')

                if table:
                    phone_number_found = False
                    rows = table.find_all('tr')
                    for row in rows:
                        th = row.find('th')
                        td = row.find('td')
                        if th and td:
                            if 'Phone' in th.text:
                                phone_number = self.extract_phone_number(td)
                                if phone_number and phone_number not in self.processed_phone_numbers:
                                    print(f"Phone number found: {phone_number}")
                                    self.processed_phone_numbers.add(phone_number)

                                    # Write the phone number to the phone_numbers.txt file
                                    with open('phone_numbers.txt', 'a') as phone_file:
                                        phone_file.write(phone_number + '\n')

                                    self.write_to_csv(name, phone_number)
                                    phone_number_found = True
                            elif 'E‑mail' in th.text:
                                self.extract_email_address(td)
                    if not phone_number_found:
                        print(f"No phone number found for {name}. Recording '-'")
                        self.write_to_csv(name, '-')
                        # Write '-' to the phone_numbers.txt file to indicate no phone number found
                        with open('phone_numbers.txt', 'a') as phone_file:
                            phone_file.write('-' + '\n')
                else:
                    print("No table with class 'table-vcard' found.")
            else:
                print(f"Failed to retrieve the profile URL. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while visiting the profile URL: {e}")

    def extract_phone_number(self, td):
        a_tag_tel = td.find('a', href=True, attrs={'href': lambda x: x and x.startswith('tel:')})
        if a_tag_tel:
            phone_number = a_tag_tel['href'].split('tel:')[-1]
            return phone_number
        return None

    def extract_email_address(self, td):
        a_tag_mailto = td.find('a', href=True, attrs={'href': lambda x: x and x.startswith('mailto:')})
        if a_tag_mailto:
            email_address = a_tag_mailto['href'].split('mailto:')[-1]
            print(f"Email address found: {email_address}")
            with open('emails.txt', 'a') as email_file:
                email_file.write(email_address + '\n')

    def write_to_csv(self, name, phone_number):
        # Write the name and phone number to the CSV file
        with open('contacts.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([name, phone_number])

# Example usage:
base_website_url = input("Please enter the base website URL: ")
scraper = ContactScraper(base_website_url)
scraper.visit_website()

