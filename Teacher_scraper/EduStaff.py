import httpx
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
import html
import json
from export import append_to_csv, append_url_to_log,read_log_file

headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7,pa;q=0.6,da;q=0.5,fr;q=0.4',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://account.edustaff.org',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://account.edustaff.org/jobs/',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'x-csrftoken': 'undefined',
    'x-user-mask-token': '',
     'cookie': '_ga=GA1.1.1482405158.1754625187; _gcl_au=1.1.2027019628.1754625187; _fbp=fb.1.1754625187546.980695592657404232; calltrk_referrer=https%3A//mail.google.com/; calltrk_landing=https%3A//account.edustaff.org/jobs/%3Fdistance%3D25%26; __hstc=213643979.da35f4c1e9530c2819e3eaa4bd423f78.1754696159079.1754696159079.1754696159079.1; hubspotutk=da35f4c1e9530c2819e3eaa4bd423f78; _clck=23aupx%7C2%7Cfyb%7C0%7C2046; _clsk=1pt1ie0%7C1754759656861%7C6%7C1%7Ck.clarity.ms%2Fcollect; _ga_HY9X17ZB4J=GS2.1.s1754759364$o4$g1$t1754759657$j60$l0$h0',
}
state_codes = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]



async def getNumberofpages(lat,long,client):
    search_query = {
    'operationName': 'JobPostings',
    'variables': {
        'pageNum': 1,
        'consortiumIds': [],
        'organizationIds': [],
        'positionIds': [],
        'userLatitude': lat,
        'userLongitude': long,
        'maxDistance': 25,
        'pageSize': 25,
        'paginate': True,
    },
    'query': 'query JobPostings($paginate: Boolean, $pageSize: Int, $pageNum: Int, $search: String, $stateIds: [ID!], $consortiumIds: [ID!], $organizationIds: [ID!], $positionIds: [ID!], $userLatitude: Decimal, $userLongitude: Decimal, $postalCodeId: ID, $maxDistance: Int) {\n  anonymousQuery {\n    id\n    jobPostings(\n      paginate: $paginate\n      pageSize: $pageSize\n      pageNum: $pageNum\n      fullTextSearch: $search\n      stateIds: $stateIds\n      consortiumIds: $consortiumIds\n      organizationIds: $organizationIds\n      positionIds: $positionIds\n      userLatitude: $userLatitude\n      userLongitude: $userLongitude\n      postalCodeId: $postalCodeId\n      maxDistance: $maxDistance\n    ) {\n      objectList {\n        ...JobPostingDetails\n        locations(\n          userLatitude: $userLatitude\n          userLongitude: $userLongitude\n          postalCodeId: $postalCodeId\n        ) {\n          id\n          city\n          distanceFromUser\n          stateProvince {\n            id\n            abbreviation\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      pageInfo {\n        numPages\n        objectCount\n        hasNext\n        hasOtherPages\n        nextPageNumber\n        hasPrevious\n        previousPageNumber\n        startIndex\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment JobPostingDetails on PublicJobPostingDetailsType {\n  id\n  name\n  positionPaycodeName(includeReferenceId: false)\n  hasOwnJobPosting\n  isClosed\n  jobPostingSlug\n  jobPostingPayRate\n  jobPostingPayRateIsHourly\n  jobPostingPositionPayRange {\n    min\n    max\n    __typename\n  }\n  organization {\n    id\n    name\n    fullName\n    hideLocationOnJobBoard\n    mailingAddress {\n      id\n      city\n      stateProvince {\n        id\n        name\n        abbreviation\n        __typename\n      }\n      __typename\n    }\n    organizationTypes {\n      objectList {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    consortium {\n      id\n      __typename\n    }\n    __typename\n  }\n  position {\n    id\n    name\n    __typename\n  }\n  organizationPositionId\n  __typename\n}\n',
}
    response = await client.post('https://account.edustaff.org/graphql-anonymous/', headers=headers, json=search_query)  
    pageInfo = response.json()['data']['anonymousQuery']['jobPostings']['pageInfo']
    numPages = pageInfo['numPages']
    return numPages 

async def GeJobDetail(lat,long,client):



    numberofPPages = await getNumberofpages(lat,long,client)
    print(f"Total pages found: {numberofPPages}")

    search_query = {
    'operationName': 'JobPostings',
    'variables': {
        'pageNum': 1,
        'consortiumIds': [],
        'organizationIds': [],
        'positionIds': [],
        'userLatitude': lat,
        'userLongitude': long,
        'maxDistance': 25,
        'pageSize': 25,
        'paginate': True,
    },
    'query': 'query JobPostings($paginate: Boolean, $pageSize: Int, $pageNum: Int, $search: String, $stateIds: [ID!], $consortiumIds: [ID!], $organizationIds: [ID!], $positionIds: [ID!], $userLatitude: Decimal, $userLongitude: Decimal, $postalCodeId: ID, $maxDistance: Int) {\n  anonymousQuery {\n    id\n    jobPostings(\n      paginate: $paginate\n      pageSize: $pageSize\n      pageNum: $pageNum\n      fullTextSearch: $search\n      stateIds: $stateIds\n      consortiumIds: $consortiumIds\n      organizationIds: $organizationIds\n      positionIds: $positionIds\n      userLatitude: $userLatitude\n      userLongitude: $userLongitude\n      postalCodeId: $postalCodeId\n      maxDistance: $maxDistance\n    ) {\n      objectList {\n        ...JobPostingDetails\n        locations(\n          userLatitude: $userLatitude\n          userLongitude: $userLongitude\n          postalCodeId: $postalCodeId\n        ) {\n          id\n          city\n          distanceFromUser\n          stateProvince {\n            id\n            abbreviation\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      pageInfo {\n        numPages\n        objectCount\n        hasNext\n        hasOtherPages\n        nextPageNumber\n        hasPrevious\n        previousPageNumber\n        startIndex\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment JobPostingDetails on PublicJobPostingDetailsType {\n  id\n  name\n  positionPaycodeName(includeReferenceId: false)\n  hasOwnJobPosting\n  isClosed\n  jobPostingSlug\n  jobPostingPayRate\n  jobPostingPayRateIsHourly\n  jobPostingPositionPayRange {\n    min\n    max\n    __typename\n  }\n  organization {\n    id\n    name\n    fullName\n    hideLocationOnJobBoard\n    mailingAddress {\n      id\n      city\n      stateProvince {\n        id\n        name\n        abbreviation\n        __typename\n      }\n      __typename\n    }\n    organizationTypes {\n      objectList {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    consortium {\n      id\n      __typename\n    }\n    __typename\n  }\n  position {\n    id\n    name\n    __typename\n  }\n  organizationPositionId\n  __typename\n}\n',
}    
    
    normalized_jobs = []
  
    for i in range(1, numberofPPages + 1):
        search_query['variables']['pageNum'] = i
        response = await client.post('https://account.edustaff.org/graphql-anonymous/', headers=headers, json=search_query)
        jobs = response.json()['data']['anonymousQuery']['jobPostings']['objectList']
        
        # getNumberofpages


        for job in jobs:
                    if job["jobPostingPayRate"] is None:
                        pay = 0.0
                    else:
                        pay = float(job["jobPostingPayRate"])

                    normalized_={
                        "job_id": job["id"],
                        "title": job["name"],
                        "organization": job["organization"]["name"],
                        "position": job["position"]["name"],
                        "city": job["organization"]["mailingAddress"]["city"],
                        "state": job["organization"]["mailingAddress"]["stateProvince"]["abbreviation"],
                        "pay_rate": pay ,
                        "is_hourly": job["jobPostingPayRateIsHourly"],
                        "job_url": f"https://account.edustaff.org/job/{job['jobPostingSlug']}"
                    }
                    json_ = {
                            'operationName': 'JobDescription',
                            'variables': {
                                'paycodeId': job["id"],
                            },
                            'query': 'query JobDescription($paycodeId: ID!) {\n  anonymousQuery {\n    id\n    jobDescription(paycodeId: $paycodeId) {\n      id\n      sections {\n        id\n        category {\n          id\n          name\n          __typename\n        }\n        contents {\n          id\n          value\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
                        }

                    desc_response = await client.post('https://account.edustaff.org/graphql-anonymous/', headers=headers, json=json_)
            
                    desc_sections = desc_response.json()['data']['anonymousQuery']['jobDescription']['sections']

                    # Clean and join text from all sections
                    plain_text_description = []
                    for section in desc_sections:
                        for content in section.get("contents", []):
                            raw_html = content.get("value", "")
                            soup = BeautifulSoup(raw_html, "html.parser")
                            clean_text = html.unescape(soup.get_text(separator="\n", strip=True))
                            plain_text_description.append(clean_text)

                    normalized_['description'] = "\n\n".join(plain_text_description)

                    normalized_jobs.append(normalized_)
    if len(jobs):
         append_to_csv(normalized_jobs,"EduStaff.csv")
    return jobs

async def fetch_statecodes(state_code, client):
    json_data = {
    'operationName': 'LocationsAutocomplete',
    'variables': {
        'search': state_code,
    },
    'query': 'query LocationsAutocomplete($search: String, $limit: Int) {\n  anonymousQuery {\n    id\n    locationAutocompleteSuggestions(search: $search, limit: $limit) {\n      id\n      displayName\n      lat\n      lng\n      stateProvince {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
}

    response = await client.post('https://account.edustaff.org/graphql-anonymous/', headers=headers, json=json_data)
   
    data = response.json()['data']['anonymousQuery']

    locationAutocompleteSuggestions = data['locationAutocompleteSuggestions']
    all_urls =[]
    for obj in locationAutocompleteSuggestions:
        
        all_urls.append({
            "lat": obj['lat'],
            "lng": obj['lng']
        })
    print(f"Fetched {len(all_urls)} URLs for state code {state_code}")

    return all_urls

semaphore  =  asyncio.Semaphore(10) 
async def scrape_job_details(lat, long, client):
    async with semaphore:
        return await GeJobDetail(lat, long, client)

async def main():
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = []
        for state_code in state_codes:
            tasks.append(fetch_statecodes(state_code, client))
        results = await asyncio.gather(*tasks)
    
      
    results = [item for sublist in results for item in sublist]
    print(f"Fetched {len(results)} URLs for all state codes")
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = []
        for obj in results:
            lat = obj['lat']
            long = obj['lng']
            tasks.append(scrape_job_details(lat,long,client))
            
        job_data = await asyncio.gather(*tasks)
    job_data = [item for sublist in job_data for item in sublist]
    print(f"Fetched {len(job_data)} job details")

asyncio.run(main())