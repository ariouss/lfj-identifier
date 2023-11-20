import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def create_session(proxies):
    connector = aiohttp.TCPConnector(limit_per_host=10)
    session = aiohttp.ClientSession(connector=connector)
    session.proxies = proxies
    return session


async def rotate_proxy(session, proxies):
    current_proxy = proxies.pop(0)
    proxies.append(current_proxy)
    session.proxies = proxies


async def scrape_linkedin_jobs(query, proxies):
    base_url = f"https://www.linkedin.com/jobs/search/?keywords={query}"

    async with await create_session(proxies) as session:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.linkedin.com/",
                "Connection": "keep-alive",
            }

            async with session.get(base_url, headers=headers, timeout=5) as response:
                response.raise_for_status()

                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')

                    jobs = soup.find_all('li', class_='job-result-card')

                    for job in jobs:
                        title = job.find('span', class_='screen-reader-text').text.strip()
                        company = job.find('a', class_='result-card__subtitle-link').text.strip()
                        location = job.find('span', class_='job-result-card__location').text.strip()

                        print(f"Title: {title}\nCompany: {company}\nLocation: {location}\n---\n")

                    await rotate_proxy(session, proxies)

                    await asyncio.sleep(2)

        except aiohttp.ClientError as err:
            print(f"Something went wrong: {err}")

proxies = ["http://45.56.119.212:8015", "http://50.218.57.69:80", "http://36.92.193.189:80"]
asyncio.run(scrape_linkedin_jobs("campaign", proxies))
