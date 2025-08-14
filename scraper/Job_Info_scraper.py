import requests
from bs4 import BeautifulSoup
import csv
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
}
# make a csv file 

csv_file = open("Jobs_staffz_website.csv","w",newline ="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Job Title","Job URL","Date of Upload","Job Location","Pay rate discription"])
page_number = 1
base_line = "https://staffez.org/job-search/"
url = "https://staffez.org/job-search/"
while True: 
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"lxml")
    Job_box = soup.find_all("div",class_="job-result")
    status = response.status_code 
    if status != 200:
        print(f"Lack of server of website {status}")
        break
    if "No Jobs Found" in response.text:
        print(f"Pages are at their limit page no {page_number}")
        break 
    else:
        for job in Job_box:
            Header_of_jobs = job.find("div",class_="job-result-title")
            job_title = Header_of_jobs.find("h2").find("a").text
            job_urls = Header_of_jobs.find("h2").find("a")["href"]
            job_date_of_establishment = Header_of_jobs.find("div").text
            summery_div = job.find("div",class_="job-result-teaser")
            summery_list = [para.get_text(strip = True) for para in summery_div.find_all("p") if para.get_text(strip=True)] 
            Job_summery = ' '.join(summery_list)
            job_result_customer = job.find("div",class_="job-result-customer")
            job_place_name = job_result_customer.find("p").text 
            csv_writer.writerow([job_title,job_urls,job_date_of_establishment,job_place_name,Job_summery])
    print(f"Scrap pages : {page_number}")
    print(f"URL : {url}") 
    url = f"{base_line}?sf_paged={page_number+1}"
    page_number = page_number + 1
csv_file.close()