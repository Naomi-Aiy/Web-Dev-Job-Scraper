from flask import Flask, jsonify, render_template #flask is used to create web app
from bs4 import BeautifulSoup
import requests
import re


app = Flask(__name__) #creatinf flask app

#loading html page
@app.route('/') #defining url endpoint
def index(): #whenever someone goes to root / this function will tell flask to find index.html and use it
    return render_template('index.html')

#defining route for jobs data
@app.route('/jobs') #another endpoint

def find_jobs():#function for scraping jobs 
    #request library requests information from a specific website
    html_text= requests.get('https://www.jobbank.gc.ca/jobsearch/jobsearch?fcid=5741&fcid=5753&fcid=12348&fcid=12351&fcid=20945&fcid=24755&fcid=296544&fcid=296623&fn21=21233&fn21=21234&fn21=22220&term=web&sort=D&fprov=ON').text #requesting from specific website and getting html text

    soup = BeautifulSoup(html_text, 'lxml') #instance of b4 soup
    jobs=soup.find_all('article', class_ = 'action-buttons') #action-buttons is the name of the class for any jobs on the page i requested

    jobs_list = [] #creating dictionary

    for job in jobs: #iterating through jobs list
        location_parts = job.find('li', class_= 'location').text.split()
        location = " ".join(location_parts[1:]) 
        
        #getting n defining the variables needed
        job_name = re.sub(r'\s+', ' ', job.find('span', class_='noctitle').text).title().strip()#matching white space sequence, eplace with normal space, then removing leading.triling spaces
        company_name = job.find('li', class_= 'business').text #getting company name, its inside a li tag and the name of the tag is business
        salary = job.find('li', class_= 'salary').text.split()[-2]
        date_posted = job.find('li', class_ = 'date').text.strip()
        relative_link = job.find('a')['href']
        full_url = "https://www.jobbank.gc.ca" + relative_link
        
        #dictionary for each job and adding it to jobs list
        jobs_list.append({
            'job_name': job_name,
            'company_name': company_name,
            'salary': salary,
            'date_posted': date_posted,
            'location': location,
            'url': full_url
        })

    return jsonify(jobs_list) #converts python list into json so js in html can read it

#checking if file is run directly, if so then starts flas server in debug mode
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