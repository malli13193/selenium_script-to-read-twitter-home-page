from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uuid
from pymongo import MongoClient
from datetime import datetime
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# Configure ChromeDriver path
CHROME_DRIVER_PATH = r'C:\Users\bhanu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['twitter_trends']
collection = db['trends']

# Function to fetch trending topics
def fetch_trending_topics():
    unique_id = str(uuid.uuid4())
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # ProxyMesh configuration
    proxy_username = 'malli13193'
    proxy_password = 'Mallika@123'
    proxy_host = 'us-ca.proxymesh.com'
    proxy_port = 31280
    proxy = f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    chrome_options.add_argument(f'--proxy-server={proxy}')

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get('https://twitter.com/login')

    # Log in to Twitter
    username = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'session[username_or_email]')))
    password = driver.find_element(By.NAME, 'session[password]')
    username.send_keys('mallikarjunareddykanala2003@gmail.com')
    password.send_keys('Mallika@123')
    password.submit()

    WebDriverWait(driver, 10).until(EC.url_contains('twitter.com/home'))
    time.sleep(5)

    trending_topics = driver.find_elements(By.XPATH, '//section[@aria-labelledby="accessible-list-0"]//span')
    trends = [trending_topics[i].text for i in range(5)]

    ip_address = requests.get('https://api.ipify.org').text
    end_time = datetime.now()

    record = {
        "unique_id": unique_id,
        "trend1": trends[0],
        "trend2": trends[1],
        "trend3": trends[2],
        "trend4": trends[3],
        "trend5": trends[4],
        "end_time": end_time,
        "ip_address": ip_address
    }

    collection.insert_one(record)
    driver.quit()
    return record

# Flask routes
@app.route('/')
def index():
    return render_template_string('''
    <html>
        <body>
            <button onclick="window.location.href='/run-script'">Click here to run the script</button>
        </body>
    </html>
    ''')

@app.route('/run-script')
def run_script():
    record = fetch_trending_topics()
    return render_template_string('''
    <html>
        <body>
            <p>These are the most happening topics as on {{ end_time }}:</p>
            <ul>
                <li>{{ trend1 }}</li>
                <li>{{ trend2 }}</li>
                <li>{{ trend3 }}</li>
                <li>{{ trend4 }}</li>
                <li>{{ trend5 }}</li>
            </ul>
            <p>The IP address used for this query was {{ ip_address }}.</p>
            <p>Here’s a JSON extract of this record from the MongoDB:</p>
            <pre>{{ record }}</pre>
            <button onclick="window.location.href='/run-script'">Click here to run the query again</button>
        </body>
    </html>
    ''', **record)

if __name__ == '__main__':
    app.run(debug=True)
