import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get the environment variables
dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')

# Establish a connection to the database
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host
)

# Create a cursor object
cur = conn.cursor()

# Define the URL
base_url = "http://books.toscrape.com"
catalog_url = base_url

# Create a session
s = requests.Session()

# Make a request to the catalog
r = s.get(catalog_url)

# Create soup object
soup = BeautifulSoup(r.text, 'html.parser')

# Find book containers
book_containers = soup.find_all('article', class_='product_pod')

# Loop over the books and save the titles, UPCs, and stock levels
for book in book_containers:
    # Get title
    title = book.find('h3').find('a').get('title')

    # Get book URL
    book_url = book.find('h3').find('a').get('href')
    book_url = base_url + '/' + book_url

    # Make a request to the book's page
    r = s.get(book_url)

    # Create soup object for the book's page
    book_soup = BeautifulSoup(r.text, 'html.parser')

    # Get UPC
    upc = book_soup.find('table', class_='table table-striped').find_all('tr')[0].find('td').text

    # Get stock
    stock = book_soup.find('table', class_='table table-striped').find_all('tr')[5].find('td').text
    # Extract the number from the string (it's in the format 'In stock (14 copies available)')
    stock = int(stock.split('(')[1].split(' ')[0])

    # Insert the data into the database
    cur.execute("INSERT INTO books (title, upc, stock) VALUES (%s, %s, %s)", (title, upc, stock))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
