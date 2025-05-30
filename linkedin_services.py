import requests
import re
import time
import random # Ensure random is imported
from urllib.parse import quote, urlencode
from datetime import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def parse_linkedin_html(html_content, location_fallback): # Name matches your single file
    jobs = []
    try:
        # from bs4 import BeautifulSoup # Moved to top-level import
        soup = BeautifulSoup(html_content, 'html.parser')
        job_cards = soup.find_all(['div', 'li'], class_=[
            re.compile(r'job-search-card', re.I),
            re.compile(r'base-card', re.I),
            re.compile(r'job-result-card', re.I), 
            re.compile(r'job-card-container', re.I) 
        ])
        
        if not job_cards: 
            job_cards = soup.select('ul.jobs-search__results-list > li') or \
                        soup.select('div.job-search-results > ul > li')

        print(f"🔍 Found {len(job_cards)} potential job elements in HTML snippet (linkedin_services.py)")
        
        parsed_urls_on_page = set()

        for card in job_cards[:15]: 
            try:
                title_elem = card.find('a', href=re.compile(r'/jobs/view/'))
                if not title_elem:
                    title_elem = card.find(['h3', 'h2'], class_=re.compile(r'base-search-card__title', re.I))

                company_elem = card.find(['h4','a'], class_=re.compile(r'base-search-card__subtitle', re.I))
                if not company_elem:
                     company_elem = card.find(class_=re.compile(r'job-card-container__company-name', re.I))


                location_elem = card.find(class_=re.compile(r'job-search-card__location', re.I))
                job_location_text = location_elem.get_text(strip=True) if location_elem else location_fallback
                
                description_elem = card.find(class_=re.compile(r'job-search-card__snippet|base-search-card__snippet', re.I))
                job_description_text = description_elem.get_text(strip=True) if description_elem else None

                if title_elem and company_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    
                    # Simpler URL extraction logic from your original
                    job_url_final = ''
                    if title_elem.name == 'a' and title_elem.get('href'):
                        job_url_final = title_elem.get('href')
                    else:
                        link_in_card = card.find('a', href=re.compile(r'/jobs/view/'))
                        if link_in_card:
                            job_url_final = link_in_card.get('href','')
                    
                    if not job_url_final: 
                        url_container = card.find(class_=re.compile(r'base-card__full-link', re.I))
                        if url_container and url_container.get('href'):
                            job_url_final = url_container.get('href')
                    
                    if job_url_final.startswith('/'): 
                        job_url_final = f"https://www.linkedin.com{job_url_final.split('?')[0]}"
                    elif "linkedin.com/jobs/view/" not in job_url_final:
                        continue 

                    job_url_final = job_url_final.split('?')[0] 

                    if title and company and job_url_final and job_url_final not in parsed_urls_on_page:
                        parsed_urls_on_page.add(job_url_final)
                        
                        final_description = job_description_text if job_description_text else \
                                            f"Details for {title} at {company} available on LinkedIn. Please visit the job URL for the full description."

                        job = {
                            'title': title, 'company': company, 'location': job_location_text,
                            'description': final_description,
                            'url': job_url_final, 'source': 'LinkedIn',
                            'posted_date': datetime.now().strftime('%Y-%m-%d'), 
                            'salary': 'Not specified' 
                        }
                        jobs.append(job)
            except Exception as e:
                # print(f"Error parsing individual job card: {e}")
                continue
    except ImportError:
        raise Exception("BeautifulSoup not installed. Run: pip install beautifulsoup4 lxml")
    except Exception as e:
        raise Exception(f"HTML parsing error: {e}")
    return jobs


def search_linkedin_jobs(cv_analysis, location, bright_data_config_passed, max_results=25): # Renamed param
    print(f"🔍 Searching LinkedIn for: {cv_analysis.get('current_role', 'Professional')} in {location} (linkedin_services.py)")
    
    jobs = []
    all_job_urls = set()
    
    search_terms = []
    current_role = cv_analysis.get('current_role', '')
    if current_role:
        search_terms.append(current_role)
    
    target_titles = cv_analysis.get('target_job_titles', [])
    search_terms.extend(target_titles[:5])
    
    skills = cv_analysis.get('technical_skills', [])
    if current_role and skills:
        for skill in skills[:2]:
            if skill and len(skill) > 2: # Make sure skill is not empty and has reasonable length
                skill_clean = skill.strip()
                if skill_clean.lower() not in current_role.lower(): # Avoid "Python Python Developer"
                    search_terms.append(f"{skill_clean} {current_role}")
                    search_terms.append(f"{skill_clean} Engineer") 
    
    search_terms = list(dict.fromkeys([term.strip() for term in search_terms if term and len(term.strip()) > 3]))
    print(f"🎯 Smart search terms: {search_terms}")
    
    # Use the passed config
    if not bright_data_config_passed['password'] or bright_data_config_passed['password'] == 'YOUR_BRIGHTDATA_PASSWORD_PLACEHOLDER_FROM_APP_PY': # Use a distinct placeholder if needed
        raise Exception("Bright Data password not configured or is placeholder. Update in .env (BRIGHTDATA_ACTUAL_PASSWORD).")

    try:
        proxy_url = f"http://{bright_data_config_passed['username']}-country-us:{bright_data_config_passed['password']}@{bright_data_config_passed['host']}:{bright_data_config_passed['port']}"
        proxies = {'http': proxy_url, 'https': proxy_url}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # ... (rest of headers from your working file)
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Cache-Control': 'max-age=0'
        }
        
        print(f"🌐 Using proxy: {bright_data_config_passed['username'].split('-zone-')[0]}-country-us@{bright_data_config_passed['host']}:{bright_data_config_passed['port']}")
        
        session = requests.Session()
        session.verify = False 
        session.headers.update(headers)
        
        # from requests.adapters import HTTPAdapter # Moved to top
        # from urllib3.util.retry import Retry # Moved to top
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # This try-except is for the proxy test itself
        try:
            test_response = session.get("https://httpbin.org/ip", proxies=proxies, timeout=15)
            print(f"🔧 Proxy test: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print(f"✅ Proxy working! IP: {test_response.json().get('origin', 'unknown')}")
                
                for i_term, search_term in enumerate(search_terms[:6]): 
                    if len(jobs) >= max_results * 2: break
                    print(f"\n🔍 Search {i_term+1}: '{search_term}' in {location}")
                    
                    for page_num in range(0, 3): 
                        if len(jobs) >= max_results * 2: break
                        
                        linkedin_params = {
                            'keywords': search_term, 'location': location,
                            'trk': 'public_jobs_jobs-search-bar_search-submit',
                            'position': 1, 'pageNum': page_num, 'start': page_num * 25
                        }
                        linkedin_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?" + urlencode(linkedin_params)
                        
                        # This try-except is for individual LinkedIn requests
                        try:
                            response = session.get(linkedin_url, proxies=proxies, timeout=30, allow_redirects=True)
                            print(f"📡 LinkedIn response for page {page_num + 1} of '{search_term}': {response.status_code}")
                            
                            if response.status_code == 200:
                                linkedin_jobs_page = parse_linkedin_html(response.text, location) # Call the correct parse function
                                new_jobs_count = 0
                                for job_item in linkedin_jobs_page:
                                    if job_item['url'] not in all_job_urls:
                                        all_job_urls.add(job_item['url'])
                                        jobs.append(job_item)
                                        new_jobs_count += 1
                                
                                print(f"✅ Added {new_jobs_count} new jobs from page {page_num + 1} (total unique: {len(jobs)})")
                                if not new_jobs_count and page_num > 0: 
                                    print("   No new jobs found on this page, moving to next search term.")
                                    break 
                            else:
                                print(f"❌ LinkedIn returned status: {response.status_code}. Content: {response.text[:200]}")
                                break # Break from pages loop for this search term
                        except requests.exceptions.ProxyError as e_proxy:
                            print(f"❌ Proxy error for LinkedIn: {e_proxy}")
                            # Depending on severity, you might want to break all searches or just this term
                            raise Exception("LinkedIn proxy error. Check proxy or network.") # Re-raise to stop
                        except requests.exceptions.RequestException as e_req:
                            print(f"❌ Network error during LinkedIn search: {e_req}")
                            break # Break from pages loop for this search term
                        time.sleep(random.uniform(3, 6)) 
                    time.sleep(random.uniform(5, 10)) # Between search terms
            else: # Proxy test failed
                raise Exception(f"Proxy test failed with status: {test_response.status_code}. Response: {test_response.text[:200]}")
        except Exception as e_proxy_setup: # Catches proxy test failure or session setup issues
            print(f"Proxy connection or setup error: {e_proxy_setup}")
            raise # Re-raise to indicate failure to the main app
            
    except Exception as e_main_search: # Catches errors from the overall search logic
        print(f"General LinkedIn search error: {e_main_search}")
        # Depending on how you want to handle this, you could return empty list or re-raise
        # For now, re-raising to make it clear in app.py that the search failed.
        raise Exception(f"LinkedIn search process failed: {e_main_search}")
    
    print(f"\n📊 Total jobs found before AI scoring: {len(jobs)}")
    return jobs[:max_results * 2]