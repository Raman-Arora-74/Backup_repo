import httpx 
from lxml import html 
import requests 
import json 
from export import * 
import asyncio 
import requests

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

session = requests.session()
session.headers.update(headers)
response = session.get("https://jobs.thesteppingstonesgroup.com/jobs")
print(f"Status : {response.status_code}")
open("StepingStones.html","w",encoding='utf-8').write(response.text)
tree = html.fromstring(response.text)
lastpage = tree.xpath('//a[@class = "page-link"]')
totel_page = int(lastpage[-2].text_content().strip())

BASE_URL = "https://jobs.thesteppingstonesgroup.com/jobs?page="

async def fatch_page(client,page,retries=10):
    url = f"{BASE_URL}{page}"
    for retry in range(1,retries+1):
        try:
            print(f"Fetching page {page}....{url}")
            await response = client.get(url)
            tree = html.fromstring(response.text)
            urls = tree.xpath('//a[contains(@href,"/jobs/details/")]/@href')
            print(f"Fatched page {page} URL {url}")
            return urls 
        except Exception as e:
            print(f"Attempts {retry} Page : {page} URL : {url} ")
            await asyncio.sleep(1)
    print(f"Failed to Fetch page {page} after {retry}")
    return []

async def fetch_job_details(client, job_url):
    job_url = job_url
    for attempt in range(1, 6):
        try:
            resp = await client.get(job_url, timeout=10)
            print(f"Fetching job details from {job_url} - Status Code: {resp.status_code}")
            tree = html.fromstring(resp.text)
            data  = {
                "Title":tree.xpath('//h1/span').strip(),
                "Salary":tree.xpath('string()'),
                "Location":tree.xpath('string(//div[@class="loc-text"]/a[contains(@href,"/jobs/categories/")])').strip()
            }

            return data
        except Exception as e:
            print(f"URL IN JOB DETAILS : {job_url}")
            print(f"Attempt {attempt} failed to fetch job details from {job_url}: {e}")
            await asyncio.sleep(1)
