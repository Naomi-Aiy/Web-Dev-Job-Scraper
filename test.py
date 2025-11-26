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

#selenium stuff
# Set up Chrome options 
options = Options()
options.headless = True  # run in background without opening browser
# initializing  driver 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get('https://www.workopolis.com/search?q=web+developer&l=ontario')#opening page
html_text= html = driver.page_source #getting html


soup = BeautifulSoup(html_text, 'lxml') #instance of b4 soup
jobs=soup.find_all('li', class_ = 'css-0') #action-buttons is the name of the class for any jobs on the page i requested

for job in jobs: #iterating through jobs list

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
            date_posted = actual_date.strftime("%B, %d")  # e.g., 'November 10'
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


    print('--------------------------')
    print(job_name)
    print(company_name)
    print(salary)
    print(date_posted)
    print(location)
    print(full_url)



#checking if file is run directly, if so then starts flas server in debug mode

#if __name__ == '__main__': #checking if being run directly
#    while True:
#        find_jobs()
#        time_wait=10
#        print(f'Waiting {time_wait} minutes. . .')
#        time.sleep(time_wait * 60) #allows program to wait every 10 minutes
        
#to run open terminal and input "python main.py" , no quotation marks
#cls to clear terminal