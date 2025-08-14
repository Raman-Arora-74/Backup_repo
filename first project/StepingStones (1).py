from selenium import webdriver
import requests
from lxml import html
from export import append_to_csv, append_url_to_log,read_log_file
import asyncio
import httpx
import json

semaphore  =  asyncio.Semaphore(5)  # limit concurrency
csvName    =  "steppingStones1.csv"


import requests

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=0, i',
    'referer': 'https://jobs.thesteppingstonesgroup.com/',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-storage-access': 'active',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'x-browser-channel': 'stable',
    'x-browser-copyright': 'Copyright 2025 Google LLC. All rights reserved.',
    'x-browser-validation': 'XPdmRdCCj2OkELQ2uovjJFk6aKA=',
    'x-browser-year': '2025',
    'x-client-data': 'CIe2yQEIorbJAQipncoBCP/0ygEIlKHLAQiFoM0BCICEzwEY4eLOAQ==',
    # 'cookie': '__Secure-3PAPISID=NjRuxDMB2mJXv65e/AFMjBAU4wP05OEzTs; __Secure-3PSID=g.a0000AjBBP9dhpZLnDb100rrMlpyFoSaIml2I_8EjBzFSCGo5GJiYtBrJE15jhFVLNgQVZDamQACgYKAd4SARcSFQHGX2MibChUeRMuADmuMGcVNuwRKhoVAUF8yKpHJzxfacdJWNvP7PXvATrK0076; __Secure-3PSIDTS=sidts-CjAB5H03P_iMnUJdqb7_Nt2ZG4rtzJw_b9J0KIQ2mu9hgEhgqrhB_NXOvZSgxo6gGcAQAA; NID=525=Gw-Jegs9d6N59utqRAwJtuPJceLkFMG-dbRNi_QIxF3FCTOGddKIjxWMIR0_fOabDxxZIia7wjpdZNl44hhbQo1hyIoNLGIrulQvh2n1eKSVIHz9iuHqe-JAamawoRhkuznIR92qPopLa0TN3xf9qsFGGE2nvTNLaWEARdQKyLjBZnpo9YAqQypinBUv_TRot0cUr24MUl7lrqmNIJ8-PGOzxSSAYqOCM_pcUCvjAu5DVEEBOGjF6uRC0ZesGHu17V2UuVutoUETcyKFYjUWrvsALPyTFG8Tj1rBqgrggQHJsjzn2I2Y_J9LYprPkg_6EWQvBhZsMXU4uOL_FhKNCm65MsUzlkJ6xHoQKYKQE-gBg0htU_sOl71lFWvYCnFVD3J2C8NfVRTGsb2tWJCFbW9WYptmggtHbpTbBZSHzgTXZimd0domucngiSWK1mt0EPpeD8VKwLcICPb-iMbPkkyhR990uQVnV9LWR7GO6IXlF8OCwNsDXwTULumby1GXSmH0ulp-1EML9CdI-JEHt5dEUx7yELK88xTOzE5Iwl4URouoxLuERMnpiIlcZIalNpz7NNiCoQSVLMYL2Zo8N-nlnH5lYrR7Tzp8pACH_lEqRBGVTFSHd6uboxbSHW3RK-o6dXBP6kRwfmQ8dAF8XJVAmqnWntgwymaSsGkPZkV0-1oktzSqeVqlxRjie_SPnIbETTrTqRl3eJPCm79pToLkr8jqQOx41WZQDEBybO_YOLez2M1Y7YzY-LVIucp2uVsZ69E6knHG1tK_v4klhcoR7rXo7PPQFJ3KbttC3B2s0edpxwBeDmq9yu31kvX82S5kMKab80sXg2lut7C1aghbuglkkbAOqxbZ_1jU7R-2_AWUm2FBL-oLKF0Ou_kS2OXy53fZ05QeIW8KcD6GJUptIV63yREZsk-qrzSIRRb2dAaZL10XHJ0Jl4fcR_BusoVvwvV4vbAZ4mtjgDGwef9bL0QI1-11H7We9sps3IZbrcFK32UfjgK1V6rsXtmiUL91rYdtn3E4X-slSqimPz9S8_u6GFNC09S2CcmnEzzSZM-quf-G27gHgep37V8ArHYrf3dFM6jPbGBuOPq7jk71x6tv8rBtKZnEzga0gPxsFryPre77o8GGf5U9qUMc0x_KCXJEEFYr21bxXDK4yyUGKiPRY6A3xIam6bLxYqBJ8n6fBotftIfvrgMXTYSz1W2vyIVI-I9wjaseFmDEEdmM6SN2A56rPFpD5jBDXUQA5zxoUn2h_5Z53PPDptEumPdQh6mEFZSFVkUyEO301-Ol8IkcU0l3CaPScpKod-Q94I-Zn9pAsishMEtYXp6ofHwb2B51oHNwCz4eNnJZOKE1ifIwomuJVI2aHKgLeZZMQ1TmMK9aAsyUQ632dXu0gqaJtRAm5bUzNdxnutg7Tw5VRk3MCwz-9MDPSNpjlwN_lV55a3TASR_aHCMJZjWo4LKc2smDPL9yNhrEBbeuwXW6UboHPILILdkM_1qUsAcTSVhvhSbo95K9xCORxCnd31wmmVru6yR3KVqqndaIi27R7YI3PnOE7BBLm_1L7hs_Aw8iBxNm99RapHMXK_L47d611tTh2KjlptwqQh-mpTssb3AzeYhkiUqQSMsd8JzZhpBi8S9_kGnX7PzYKDaxNIAe-xGxkVPGW740feJaO53JVDRJjGmvFqinzfFnBayE5uwrMrxtM2vH2aR_KIb5ci65NO7fOoM29GFoNuYHD2aSrPtoVv7_jAn2PGORa1U9dyp338ieOw; __Secure-3PSIDCC=AKEyXzWluo_D0QuWxUxF19sBez7lNzrA0he3JFwu1M9oqOZctWwe87ILk5S45M_37fcqFyLNEKg',
}

s = requests.Session()
s.headers.update(headers)

response = s.get('https://jobs.thesteppingstonesgroup.com/jobs')
print(f"Status Code: {response.status_code}")

open("output.html", "w",encoding="utf-8").write(response.text)

tree = html.fromstring(response.text)
lastpage =tree.xpath('//a[@class="page-link"]')
total_pages = int(lastpage[-2].text_content().strip())
print(f"Total pages found: {total_pages}")


BASE_URL = "https://jobs.thesteppingstonesgroup.com/jobs?page="

async def fetch_page(client, page, retries=10):
    url = f"{BASE_URL}{page}"
    url = f"{BASE_URL}{page}"
    for attempt in range(1, retries + 1):
        try:
            print(f"Fetching page {page}...{url}")
            response = await client.get(url)
            tree = html.fromstring(response.text)
            open("job_details.html", "w", encoding="utf-8").write(response.text)
            urls = tree.xpath('//div[@class="job-search__jobs-list__rightSide"]/p/a/@href')
            print(f"Fetched page {page} with {len(urls)} jobs")
            return urls
        except Exception as e:
            print(f"Attempt {attempt} failed to fetch page {page}: {e}")
            await asyncio.sleep(1) 
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
            location_list = [location for location in tree.xpath('(string//div[@class="loc-text"]/a[contains(@href ,"/jobs/locations/")])')]
            data  = {           
                    "title": tree.xpath('string(//h1/span)').strip(),
                    "salary": tree.xpath('string(//span[@style="font-size: 12px;"]/strong[contains(text(),"Pay")])').strip(),                  
                    "location": ", ".join(location_list),
                    "category": tree.xpath('string(//div[@class="loc-text"]/a[contains(@href,"/jobs/categories/")]').strip(),
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


