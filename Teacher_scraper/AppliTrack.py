from selenium import webdriver
import requests
from lxml import html,etree
from export import append_to_csv, append_url_to_log,read_log_file
import asyncio
import httpx

semaphore  =  asyncio.Semaphore(5)  
csvName    =  "ApliTrack.csv"


headers ={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7,pa;q=0.6,da;q=0.5,fr;q=0.4',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://www.applitrack.com/wixey/onlineapp/default.aspx',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': '_aeaid=936ef4bf-2155-442d-82d8-bb74e692f724; aelastsite=442Z5IgoaV0oSlKjW%2FvVBh5ChqUvJ%2FOLmQN4RzNLduiBaImk9Cnd2byuMQetMoMC; aelreadersettings=%7B%22c_big%22%3A0%2C%22rg%22%3A0%2C%22memph%22%3A0%2C%22contrast_setting%22%3A0%2C%22colorshift_setting%22%3A0%2C%22text_size_setting%22%3A0%2C%22space_setting%22%3A0%2C%22font_setting%22%3A0%2C%22k%22%3A0%2C%22k_disable_default%22%3A0%2C%22hlt%22%3A0%2C%22disable_animations%22%3A0%2C%22display_alt_desc%22%3A0%7D; _ga=GA1.2.1295788528.1754625280; _gid=GA1.2.1867022033.1754625280; _ga_P69Q4VQ6MR=GS2.2.s1754625280$o1$g0$t1754625280$j60$l0$h0; ARRAppliTrackPHL1516=af815db15532213ec03f742877a2b06362316d9550eef50f5362f71d1fa1536a; ASP.NET_SessionId=131o1pdse4g4egrdra5tdpx3; dtCookie=v_4_srv_7_sn_9EC4928867AE58D146BECD595A64D99A_perc_100000_ol_0_mul_1_app-3A7927f457c7a0685b_0_rcs-3Acss_0; ASPSESSIONIDASDCBCQB=FKGLGONCHBJOFGAOCFALJAGF; aeatstartmessage=true',
}

driver = webdriver.Chrome()
driver.get("https://www.applitrack.com/wixey/onlineapp/default.aspx?all=1")

tree = html.fromstring(driver.page_source)

jobs = []

for job_block in tree.xpath('//ul[@class="postingsList"]'):
    html_str = etree.tostring(job_block, encoding="unicode", pretty_print=True)
    job_block = html.fromstring(html_str)

    job = {}

    job['title'] = job_block.xpath('.//table[@class="title"]//td[@id="wrapword"]/text()')[0].strip()
    
    # Job ID
    job['job_id'] = job_block.xpath('.//span[contains(@class,"title2")]/text()')
    # If job_id not found in text, extract from onclick attribute
    if not job['job_id']:
        onclick = job_block.xpath('.//input[contains(@class,"ApplyButton")]/@onclick')
        if onclick:
            job['job_id'] = onclick[0].split("applyFor('")[1].split("'")[0]
    else:
        job['job_id'] = job['job_id'][0].replace("JobID:", "").strip()

    # Position Type
    job['position_type'] = " ".join(job_block.xpath('.//li[span[text()="Position Type:"]]/span[@class="normal"]/text()')).strip()

    # Date Posted
    job['date_posted'] = job_block.xpath('.//li[span[text()="Date Posted:"]]/span[@class="normal"]/text()')[0].strip()

    # Location
    job['location'] = job_block.xpath('.//li[span[text()="Location:"]]/span[@class="normal"]/text()')[0].strip()

    # Pay Rate (if exists)
    pay_rate = job_block.xpath('.//td[strong[text()="PAY RATE"]]/following-sibling::td/text()')
    job['pay_rate'] = pay_rate[0].strip() if pay_rate else None

    # Apply link
    apply_link = job_block.xpath('.//td[strong[text()="APPLY"]]/following-sibling::td//a/@href')
    job['apply_link'] = apply_link[0] if apply_link else None
    # Job description
    block = job_block.xpath('//span[starts-with(@id, "DescriptionText")]')[0]
    print(block)
    job['position'] = block.xpath('.//tr[td//strong[text()="POSITION"]]/td[2]//text()')
    job['position'] = " ".join(t.strip() for t in job['position'] if t.strip())

    job['location'] = block.xpath('.//tr[td//strong[text()="LOCATION"]]/td[2]//text()')
    job['location'] = " ".join(t.strip() for t in job['location'] if t.strip())
    print( block.xpath('.//tr[td//strong[text()="LOCATION"]]/td[2]//text()'))

    job['pay_rate'] = block.xpath('.//tr[td//strong[text()="PAY RATE"]]/td[2]//text()')
    job['pay_rate'] = " ".join(t.strip() for t in job['pay_rate'] if t.strip())

    job['apply_link'] = block.xpath('.//tr[td//strong[text()="APPLY"]]/td[2]//a/@href')
    job['apply_link'] = job['apply_link'][0] if job['apply_link'] else None

    # Extract all remaining descriptive text (outside the table)
    description_parts = block.xpath('.//span[not(ancestor::table)]/text()')
    job['description'] = " ".join(t.strip() for t in description_parts if t.strip())    

    jobs.append(job)

append_to_csv(jobs,csvName)