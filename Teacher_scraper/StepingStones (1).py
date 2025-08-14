from selenium import webdriver
import requests
from lxml import html
from export import append_to_csv, append_url_to_log,read_log_file
import asyncio
import httpx
import json

semaphore  =  asyncio.Semaphore(20)  # limit concurrency
csvName    =  "steppingStones1.csv"


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
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
     'cookie': '_ga=GA1.1.592098283.1754794142; _gcl_au=1.1.260113923.1754794143; _RCRTX03=938b8888759411f0816e1963dd517150c35e33b5e9534af38bad57df3ef12db3; _RCRTX03-samesite=938b8888759411f0816e1963dd517150c35e33b5e9534af38bad57df3ef12db3; _fbp=fb.1.1754794144184.443998404289526057; fpestid=nrpaPGkPj-gj7Yk1xTbGBZE43kPZ1WdKM6GlHVJydVDrPlH-wAFmbHrYIXOlsFuCjmUreg; XSRF-TOKEN=eyJpdiI6Ik5TRU1nMnpueXlTOGVQQzMzWmcwU2c9PSIsInZhbHVlIjoiQWtiS3h5L25hcSs1Q1dQc2h1ejloREp3OEF6WlllK2wwQWVnVEUvNzJPSTM5MzVCc29zQ1ExaE5aWWh5MTg1Tk5ONnVZampENy8wbG9TUTNrWlZraHFhZDFpdkhCalJTOGxXQlNxNE82ekhqSHA2L2xiaDlwUDF5Vnp5bzhWeEYiLCJtYWMiOiJlM2ZmMmMzNmRlZTcwNDFiM2E0YTRhNjg4MmM1OTIyODQ0ZWZhYjg0Nzg5MGZjYzA1OGY3M2YwMGVhY2Q5MzA5IiwidGFnIjoiIn0%3D; fusion_laravel_session=QPkmOJ2pqHvIMuACJtxNsNF6IFi3lq5TputxYoi0; _ga_5Z4WC03XDQ=GS2.1.s1754926647$o2$g0$t1754926647$j60$l0$h0; mp_59722e790c35c1bb4b5c217702adb1c3_mixpanel=%7B%22distinct_id%22%3A%20%2219891e1ac54845-059cd452ddba79-26011051-1fa400-19891e1ac55164b%22%2C%22%24device_id%22%3A%20%2219891e1ac54845-059cd452ddba79-26011051-1fa400-19891e1ac55164b%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D; _ga_GFMXXQWJG7=GS2.1.s1754926648$o2$g0$t1754926648$j60$l0$h0',
}

s = requests.Session()
s.headers.update(headers)

response = s.get('https://jobs.thesteppingstonesgroup.com/jobs')
print(f"Status Code: {response.status_code}")

open("output.html", "w",encoding="utf-8").write(response.text)

tree = html.fromstring(response.text)
lastpage =tree.xpath('//a[@class="page-link"]')
print(f"Last page found: {lastpage}")
# print html of lastpage
print(html.tostring(lastpage[-2], pretty_print=True, encoding='unicode'))
total_pages = int(lastpage[-2].text_content().strip())
print(f"Total pages found: {total_pages}")


BASE_URL = "https://jobs.thesteppingstonesgroup.com/jobs?page="

async def fetch_page(client, page, retries=10):
    url = f"{BASE_URL}{page}"
    for attempt in range(1, retries + 1):


        try:
            print(f"Fetching page {page}...{url}")
            response = await client.get(url)
            tree = html.fromstring(response.text)
            urls = tree.xpath('//a[contains(@href,"jobs/details/")]/@href')
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
            open("job_details.html", "w", encoding="utf-8").write(resp.text)
            data  = {           
                    "title": tree.xpath('string(//h1[@role="heading"]/span[@class="job-title"])').strip(),
                    "salary": tree.xpath('string(//div[@aria-label[contains(., "Salary")]]/div[@class="loc-text"])').strip(),
                    "location": " ".join(tree.xpath('//div[@aria-label[contains(., "Jobs location")]]/div[@class="loc-text"]/a/text()')).strip() or None,
                    "category": tree.xpath('string(//div[@aria-label[contains(., "Jobs category")]]/div[@class="loc-text"]/a/text())').strip(),
                    "description": tree.xpath('string(//div[@class="job-description-content"])').strip().replace("\t","").replace("\n\n","").strip(" "),
                    "joburl": job_url
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
        open("job.json", "w", encoding="utf-8").write(json.dumps(job_data, ensure_ascii=False, indent=4))


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
