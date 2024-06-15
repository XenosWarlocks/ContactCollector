import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def visit_website(base_url):
    try:
        # Send a request to the base URL
        response = requests.get(base_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <li> tags with the class 'crossroad-links__item'
            li_tags = soup.find_all('li', class_='crossroad-links__item')

            for li in li_tags:
                # Find the <a> tag within the <li> tag
                a_tag = li.find('a')

                if a_tag and 'href' in a_tag.attrs:
                    # Extract the href attribute
                    href = a_tag['href']

                    # Split the href by '-' and take the last two values
                    parts = href.split('-')

                    if len(parts) >= 2:
                        # Get the last two parts and capitalize the first letter
                        last_two_parts = [part.capitalize() for part in parts[-2:]]
                        name = ' '.join(last_two_parts)
                        print(name)

                        # Write the name to the names.txt file
                        with open('names.txt', 'a') as name_file:
                            name_file.write(name + '\n')

                        # Construct the full URL using urljoin
                        full_url = urljoin(base_url, href)

                        # Visit the constructed URL to extract phone numbers
                        visit_constructed_url(full_url)

                    else:
                        print(f"Insufficient parts in href '{href}'")
        else:
            print(f"Failed to retrieve the website. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_phone_number(td):
    # Find the <a> tag within the <td> tag with 'href' attribute starting with 'tel:'
    a_tag_tel = td.find('a', href=True, attrs={'href': lambda x: x and x.startswith('tel:')})

    if a_tag_tel:
        # Extract the phone number after 'tel:'
        phone_number = a_tag_tel['href'].split('tel:')[-1]
        print(f"Phone number found: {phone_number}")

        # Write the phone number to the phone_numbers.txt file
        with open('phone_numbers.txt', 'a') as phone_file:
            phone_file.write(phone_number + '\n')

def visit_constructed_url(url):
    try:
        # Send a request to the constructed URL
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Visiting URL: {url}")

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the <table> tag with the class 'table-vcard'
            table = soup.find('table', class_='table-vcard')

            if table:
                # Find all <tr> tags within the table body
                rows = table.find_all('tr')

                for row in rows:
                    # Find all <th> and <td> tags within the row
                    th = row.find('th')
                    td = row.find('td')

                    if th and td:
                        # Check if the <th> tag contains 'Phone'
                        if 'Phone' in th.text:
                            # Extract phone number
                            extract_phone_number(td)
            else:
                print("No table with class 'table-vcard' found.")
        else:
            print(f"Failed to retrieve the constructed URL. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while visiting the constructed URL: {e}")

# Get the base website URL from the user
base_website_url = input("Please enter the base website URL: ")

# Visit the provided base website
visit_website(base_website_url)

