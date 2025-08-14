from selenium import webdriver
import requests
from lxml import html
from export import append_to_csv, append_url_to_log,read_log_file
import asyncio
import httpx

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7,pa;q=0.6,da;q=0.5,fr;q=0.4',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.mykelly.com/find-jobs/education-jobs/',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'cookie': '_fbp=fb.1.1754155506449.375545769541710850; _gcl_au=1.1.1951109968.1754155509; _ga=GA1.1.1226420487.1754155509; CookieConsent={stamp:%27H1pPN3MHCmYT8jbf+zMX4Nzu/Zsaoh/wJG9FOj8LR0I+u0X96pmSxQ==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1754155519372%2Cregion:%27ca%27}; _ccid=17541555314949g0ktb4c0; handl_landing_page=https%3A%2F%2F_%2Fjob-search%2F%3F_category%3Deducation; user_agent=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F139.0.0.0%20Safari%2F537.36; HandLtestDomainName=HandLtestDomainValue; handlID=332983042149; organic_source=; organic_source_str=Direct; traffic_source=Direct; user_agent=Mozilla/5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit/537.36%20(KHTML%2C%20like%20Gecko)%20Chrome/139.0.0.0%20Safari/537.36; GAMKJCID=GA1.1.1226420487.1754155509; handl_original_ref=https://www.mykelly.com/job-search/?_category=education&_paged=2; handl_ref=https%3A%2F%2Fwww.mykelly.com%2Fjob-search%2F%3F_category%3Deducation%26_paged%3D109; organic_source=https%3A%2F%2Fwww.mykelly.com%2Fjob-search%2F%3F_category%3Deducation%26_paged%3D109; handl_ip=2604%3A3d09%3Ae290%3Ad200%3Ad4bc%3Ad953%3A72ba%3A46d7%2C%2064.252.69.210; handl_url_base=https%3A%2F%2F_%2Fjob%2F9674829-reading-school-district-substitute-teacher-reading-pa-united-states%2F; handl_url=https%3A%2F%2F_%2Fjob%2F9674829-reading-school-district-substitute-teacher-reading-pa-united-states%2F; handl_ref_domain=www.mykelly.com; handl_url_base=https://www.mykelly.com/find-jobs/education-jobs/; handl_url=https://www.mykelly.com/find-jobs/education-jobs/; handl_ref=https://www.mykelly.com/find-jobs/; _uetsid=f1b954a0733411f080939bb29daa41dd; _uetvid=a1cc5f306fc511f080a415b0d2369297; _ga_2LH0GGL3VF=GS2.1.s1754533167$o2$g1$t1754535010$j27$l0$h1154868303',
}

params = {
    '_category': 'education',
}

s = requests.Session()
s.headers.update(headers)

driver = webdriver.Chrome()
response = s.get('https://www.mykelly.com/job-search/',params=params)
print(f"Status Code: {response.status_code}")

open("output.html", "w").write(response.text)
driver.get("https://www.mykelly.com/job-search/?_category=education")

tree = html.fromstring(driver.page_source)

lastpage =tree.xpath('//a[contains(@class, "facetwp-page") and contains(@class, "last")]')[0]
total_pages = int(lastpage.text_content().strip())
driver.quit()

BASE_URL = "https://www.mykelly.com/job-search/?_category=education&_paged="

async def fetch_page(client, page, retries=10):
    url = f"{BASE_URL}{page}"
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url)
            tree = html.fromstring(response.text)
            urls = tree.xpath('//a[contains(@href, "mykelly.com/job/")]/@href')
            print(f"Fetched page {page} with {len(urls)} jobs")
            return urls
        except Exception as e:
            print(f"Attempt {attempt} failed to fetch page {page}: {e}")
            await asyncio.sleep(1)  # short delay before retry
    print(f"❌ Failed to fetch page {page} after {retries} attempts.")
    return []

JobURLS = []
async def fetch_job_details(client, job_url):
   
    resp = await client.get(job_url, timeout=10)
    print(f"Fetching job details from {job_url} - Status Code: {resp.status_code}")
    tree = html.fromstring(resp.text)
    data = {
        "JobTitle": tree.xpath('string(//h2[contains(@class, "mykelly_jd_job_title")])').strip(),
        "Location": tree.xpath('string(//p[contains(@class, "job_location_customn")])').strip(),
        "Category": tree.xpath('string(//p[contains(@class, "category_customn")])').strip(),
        "EducationLevel": tree.xpath('string(//p[contains(@class, "education_level_customn")])').strip(),
        "EmploymentType": tree.xpath('string(//p[contains(@class, "employment_type_customn")])').strip(),
        "ExperienceLevel": tree.xpath('string(//p[contains(@class, "experiance_level_customn")])').strip(),
        "Industry": tree.xpath('string(//p[contains(@class, "industry_customn")])').strip(),
        "Shift": tree.xpath('string(//p[contains(@class, "shift_customn")])').strip(),
        "Compensation": tree.xpath('string(//p[contains(@class, "salary_customn")])').strip(),
        "JobType": tree.xpath('string(//p[contains(@class, "employment_type_customn")])').strip(),
        "JobDescription": tree.xpath('string(//div[contains(@class, "mykelly_jd_job_description")])').strip(),
        "JobURL": job_url,
    }
    return data
    
async def fetch_and_save_job(client, job_url):
    job_data = await fetch_job_details(client, job_url)  # your async fetch function
    
    if job_data:
        append_to_csv([job_data], 'jobs1.csv')  # Append one job record immediately
        append_url_to_log(job_url)  # Log the URL to avoid re-fetching
        print(f"Saved job: {job_data['JobTitle']}")


semaphore = asyncio.Semaphore(5)  # limit concurrency

async def fetch_and_save_job_limited(client, job_url):
    async with semaphore:
        return await fetch_and_save_job(client, job_url)
    
async def main():
    print(f"Total pages: {total_pages}")
    
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch_page(client, page) for page in range(1, total_pages + 1)]
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
