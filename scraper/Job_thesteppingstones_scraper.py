from bs4 import BeautifulSoup
import csv
import requests

def transfer_of_data_in_csv_file(url):
    response = requests.get(url)
    source = BeautifulSoup(response.text,"lxml")
    jobs_box = source.find_all("div",class_="job-box")
    for job in jobs_box:
        Job_title = job.find("h2").find("span",class_="job-title").find("a").get_text(strip = True) 
        Job_url = job.find("h2").find("span",class_="job-title").find("a")["href"]
        job_pay_rate = job.find("div",class_="job-sector-fade").find("div",class_="job-text").get_text(strip = True)
        job_category = job.find_all("div",class_="job-text")
        job_category_list = [a_tag.get_text(strip=True)for jc in job_category if (a_tag := jc.find("a"))and "https://jobs.thesteppingstonesgroup.com/jobs/categories/" in a_tag.get("href", "")]
        job_category_text = " ".join(job_category_list)
        job_summery = job.find("div",class_="fade-text").get_text(strip = True)
        csv_writer.writerow([Job_title,Job_url,job_pay_rate,job_category_text,job_summery])
csv_file = open("csv_File_job.csv","+w",newline="",encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Job Title","Job URL","Job Pay Rate","Job Category","Job Summery"])
page = 1
base_url = "https://jobs.thesteppingstonesgroup.com/jobs"
url = "https://jobs.thesteppingstonesgroup.com/jobs"
while True:
    response = requests.get(url)
    status = response.status_code
    if status != 200:
        print(f"Website error : {status}")
        break
    if "Sorry, we currently have no matching vacancies for your search criteria." in response.text:
        print("No more pages found.")
        break
    transfer_of_data_in_csv_file(url)
    url = f"{base_url}?page={page}"
    print(f"Scraped Page : {page}")
    print(f"URL : {url}")
    page += 1