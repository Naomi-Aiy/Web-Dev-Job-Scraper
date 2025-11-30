from flask import Flask, jsonify, render_template
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__) #creatinf flask app

def scrape_workopolis():
    # selenium stuff
    # Set up Chrome options 
    options = Options()
    options.add_argument("--headless=new")   # modern headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # initializing driver 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get('https://www.workopolis.com/search?q=web+developer&l=ontario')  # opening page
    html_text = driver.page_source  # getting html

    soup = BeautifulSoup(html_text, 'lxml')  # instance of b4 soup
    jobs_html = soup.find_all('li', class_='css-0')  # action-buttons is the name of the class for any jobs on the page i requested

    driver.quit()

    jobs_list = []

    for job in jobs_html:  # iterating through jobs list

        # getting and defining the variables needed
        h2 = job.find('h2', class_='chakra-text css-8rdtm5')
        job_name = ''
        if h2:
            a_tag = h2.find('a')
            if a_tag:
                job_name = re.sub(r'\s+', ' ', a_tag.text).strip()

        # company
        company_span = job.find('span', attrs={'data-testid': 'companyName'})
        company_name = re.sub(r'\s+', ' ', company_span.text).strip() if company_span else 'N/A'

        # salary
        salary_p = job.find('p', class_='chakra-text css-1g1y608')
        salary = re.sub(r'\s+', ' ', salary_p.text).strip() if salary_p else 'N/A'

        # date posted
        date_p = job.find('p', class_='chakra-text css-5yilgw')
        if date_p:
            date_str = date_p.text.strip()
            if date_str.endswith('d'):  # e.g., '5d'
                days_ago = int(date_str[:-1])
                actual_date = datetime.today() - timedelta(days=days_ago)
                date_posted = actual_date.strftime("%B, %d")  # e.g., 'November, 10'
            elif date_str.endswith('h'):  # e.g., '6h'
                date_posted = datetime.today().strftime("%B, %d")
            else:
                date_posted = date_str
        else:
            date_posted = 'N/A'

        # location
        location_p = job.find('p', class_='chakra-text css-1g6x9n1')
        location = re.sub(r'\s+', ' ', location_p.text).strip() if location_p else 'N/A'

        # url
        a_tag_url = job.find('a', class_='chakra-button css-1i0mgad')
        relative_link = a_tag_url['href'] if a_tag_url else ''
        full_url = f"https://www.workopolis.com{relative_link}" if relative_link else 'N/A'

        # adding to list
        if job_name and company_name != 'N/A':
            jobs_list.append({
            'job_name': job_name,
            'company_name': company_name,
            'salary': salary,
            'date_posted': date_posted,
            'location': location,
            'url': full_url,
            'source': 'Workopolis'
    })

    return jobs_list

def scrape_jobbank():
    # request library requests information from a specific website
    html_text = requests.get(
        'https://www.jobbank.gc.ca/jobsearch/jobsearch?fcid=5741&fcid=5753&fcid=12348&fcid=12351&fcid=20945&fcid=24755&fcid=296544&fcid=296623&fn21=21233&fn21=21234&fn21=22220&term=web&sort=D&fprov=ON'
    ).text  # requesting from specific website and getting html text

    soup = BeautifulSoup(html_text, 'lxml')  # instance of b4 soup
    jobs_html = soup.find_all('article', class_='action-buttons')  # action-buttons is the name of the class for any jobs on the page i requested
    jobs_list = []  # creating dictionary

    for job in jobs_html:  # iterating through jobs list
        location_parts = job.find('li', class_='location').text.split()
        location = " ".join(location_parts[1:]) if location_parts else 'N/A'
        job_name = re.sub(r'\s+', ' ', job.find('span', class_='noctitle').text).title().strip() if job.find('span', class_='noctitle') else 'N/A'
        company_name = job.find('li', class_='business').text if job.find('li', class_='business') else 'N/A'
        salary = job.find('li', class_='salary').text.split()[-2] if job.find('li', class_='salary') else 'N/A'
        date_posted = job.find('li', class_='date').text.strip() if job.find('li', class_='date') else 'N/A'
        relative_link = job.find('a')['href'] if job.find('a') else ''
        full_url = "https://www.jobbank.gc.ca" + relative_link if relative_link else 'N/A'

        # dictionary for each job and adding it to jobs list
        jobs_list.append({
            'job_name': job_name,
            'company_name': company_name,
            'salary': salary,
            'date_posted': date_posted,
            'location': location,
            'url': full_url,
            'source': 'Job Bank'
        })

    return jobs_list

#flask routes
@app.route('/')  # defining url endpoint
def index():  # whenever someone goes to root / this function will tell flask to find index.html and use it
    return render_template('index.html')

@app.route('/jobs')  # another endpoint
def find_jobs():
    workopolis_jobs = scrape_workopolis()  # get Workopolis jobs
    jobbank_jobs = scrape_jobbank()        # get Job Bank jobs
    combined_jobs = workopolis_jobs + jobbank_jobs  # combine both lists
    return jsonify(combined_jobs)  # converts python list into json so js in html can read it

# checking if file is run directly, if so then starts flask server in debug mode
if __name__ == '__main__':
    app.run(debug=True)

#if __name__ == '__main__': #checking if being run directly
#    while True:
#        find_jobs()
#        time_wait=10
#        print(f'Waiting {time_wait} minutes. . .')
#        time.sleep(time_wait * 60) #allows program to wait every 10 minutes
        
#to run open terminal and input "python main.py" , no quotation marks
#cls to clear terminal