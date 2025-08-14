from selenium import webdriver
import requests
from lxml import html
from export import append_to_csv, append_url_to_log,read_log_file
import asyncio
import httpx

semaphore  =  asyncio.Semaphore(5)  # limit concurrency
csvName    =  "Ameris1.csv"


headers ={
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7,pa;q=0.6,da;q=0.5,fr;q=0.4',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'cookie': 'cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _gcl_au=1.1.432599046.1754321365; _ga=GA1.1.1179130534.1754321365; _hjSessionUser_5193068=eyJpZCI6ImRjYjQ5OTRjLWIzMDEtNWUxMC04ZTg0LWZlMzQzZTI0YTlkNyIsImNyZWF0ZWQiOjE3NTQzMjEzNjUxNTYsImV4aXN0aW5nIjp0cnVlfQ==; __cf_bm=bU7jL85m4KWnSyYTnAMVMtP51VKPKAGT0IN14PVARK8-1754580881-1.0.1.1-HVB7NQ_1YXG5qtWi5pBmK1neNVIp2ZK0LwmkNVGr9WTpWYQ0FB69JrT6pk.8g3aEH_rg.1v7PNiEcdGYFdeFRYTF_wW_gUisgiKAgmqLqzQ; _hjSession_5193068=eyJpZCI6IjNkYTcxMDhlLTc0M2YtNDU3MC05MzVlLWE5Y2Y1N2E5ODExOCIsImMiOjE3NTQ1ODA4ODI1ODcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _ga_VXQ1RVF43Q=GS2.1.s1754580882$o4$g1$t1754581074$j58$l0$h0; _ga_M62ZMX1YLR=GS2.1.s1754580882$o4$g1$t1754581074$j58$l0$h0; _ga_11HW8H5P6P=GS2.1.s1754580882$o4$g1$t1754581074$j58$l0$h0; _ga_2FZ13PQBLQ=GS2.1.s1754580882$o4$g1$t1754581074$j58$l0$h0',
}
params = {
    '_category': 'education',
}

s = requests.Session()
s.headers.update(headers)

response = s.get('https://careers.amergis.com/',params=params)
print(f"Status Code: {response.status_code}")
driver = webdriver.Chrome()
driver.get("https://careers.amergis.com/?_category=education")

open("output.html", "w").write(response.text)

tree = html.fromstring(driver.page_source)
lastpage =tree.xpath('//a[contains(@class, "facetwp-page") and contains(@class, "last")]')[0]
total_pages = int(lastpage.text_content().strip())
print(f"Total pages found: {total_pages}")
driver.quit()


BASE_URL = "https://careers.amergis.com/?_category=education&_paged="

async def fetch_page(client, page, retries=10):
    url = f"{BASE_URL}{page}"
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url)
            tree = html.fromstring(response.text)
            urls = tree.xpath('//a[@class="maxim_jobs_job_title"]/@href')
            print(f"Fetched page {page} with {len(urls)} jobs")
            return urls
        except Exception as e:
            print(f"Attempt {attempt} failed to fetch page {page}: {e}")
            await asyncio.sleep(1)  # short delay before retry
    print(f"❌ Failed to fetch page {page} after {retries} attempts.")
    return []

JobURLS = []

async def fetch_job_details(client, job_url):
    for attempt in range(1, 6):
        try:
            resp = await client.get(job_url, timeout=10)
            print(f"Fetching job details from {job_url} - Status Code: {resp.status_code}")
            tree = html.fromstring(resp.text)
            data = {

                "JobTitle": tree.xpath('string(//div[contains(@class, "job_details_title_column_customs")]//h1/span)').strip(),

                "Location": tree.xpath('string(//div[contains(@class, "fl-visible-mobile")]//div[contains(@class, "fl-rich-text")]/p/span[1])').strip(),

                "Category": tree.xpath('string(//div[contains(@class, "job_details_title_column_customs")]//p[span[contains(text(), "Category")]]/span)').strip(),

                "EducationLevel": tree.xpath('string(//p[contains(@class, "education_level_customn")])').strip(),

                "EmploymentType": tree.xpath('string(//div[contains(@class, "job_details_title_column_customs")]//p[span[contains(text(), "Contract")]]/span)').strip(),

                "ExperienceLevel": tree.xpath('string(//p[contains(@class, "experiance_level_customn")])').strip(),

                "Industry": tree.xpath('string(//p[contains(@class, "industry_customn")])').strip(),

                "ContracDuration": tree.xpath('string(//p[span[contains(text(), "Contract Duration")]]/span)').strip(),

                "Shift": tree.xpath('string(//p[span[contains(text(), "Work Setting")]]/span)').strip(),

                "Compensation": tree.xpath('string(//p[span[contains(text(), "Est. Pay")]]/span)').strip(),

                "JobType": tree.xpath('string(//p[contains(@class, "employment_type_customn")])').strip(),
            
                "PostedDate": tree.xpath('string(//p[span[contains(text(), "Posted Date:")]]/span)').strip(),

                "JobDescription": tree.xpath('string(//*[@id="fl-main-content"]/div/div/div/div/div[3]/div[1]/div/div[1]/div/div)').strip(),

                "JobURL": job_url
            }

            return data
        except Exception as e:
            print(f"Attempt {attempt} failed to fetch job details from {job_url}: {e}")
            await asyncio.sleep(1)
    
async def fetch_and_save_job(client, job_url):
    job_data = await fetch_job_details(client, job_url)  # your async fetch function
    
    if job_data:
        append_to_csv([job_data], csvName)  # Append one job record immediately
        append_url_to_log(job_url)  # Log the URL to avoid re-fetching
        print(f"Saved job: {job_data['JobTitle']}")


async def fetch_and_save_job_limited(client, job_url):
    async with semaphore:
        return await fetch_and_save_job(client, job_url)
    
async def fetch_page_limited(client, page):
    async with semaphore:
        return await fetch_page(client, page)

async def main():
    print(f"Total pages: {total_pages}")
    
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch_page_limited(client, page) for page in range(1, total_pages + 1)]
        results = await asyncio.gather(*tasks)

    # Flatten the list of lists from all pages
    JobURLS = [url for sublist in results for url in sublist]
   
    JobURLS = list(set(JobURLS) - set(read_log_file('log.txt')))
    print(f"{len(JobURLS)} new job URLs to scrape (excluding already scraped)")
    print(f"Collected {len(JobURLS)} job URLs")

    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch_and_save_job_limited(client, url) for url in JobURLS]
        results = await asyncio.gather(*tasks)

    # Filter out failed (None) results
    jobs_data = [job for job in results if job]

    print(f"Scraped {len(jobs_data)} job details")
    if jobs_data:
        print(jobs_data[0])


asyncio.run(main())
