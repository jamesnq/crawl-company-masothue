from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from googlesearch import search
import requests
import random
from concurrent.futures import ThreadPoolExecutor
import socket

def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'\s+', ' ', text).strip()
    return text

def extract_tax_code_from_title(title):
    # Extract tax code from title like "2803139732 - CÔNG TY TNHH XÂY DỰNG..."
    match = re.match(r'^(\d+)', title)
    if match:
        return match.group(1)
    return None

def extract_contact_from_text(text, content_div):
    # Extract phone numbers
    phone_patterns = [
        r'(?:(?:\+|00)84|0)\s*[1-9](?:[\s.-]*\d{2}){4}',  # Vietnamese phone numbers
        r'\d{10}',  # Standard 10-digit format
        r'(?:(?:\+|00)84|0)\d{9}'  # Vietnamese format with country code
    ]
    
    # Look for phone numbers near specific labels
    phone_labels = [
        'Điện thoại',
        'Tel',
        'Phone',
        'Di động',
        'Số điện thoại',
        'Liên hệ',
        'Hotline'
    ]
    
    # First try to find phone numbers near labels
    for label in phone_labels:
        label_elem = content_div.find(string=re.compile(label, re.IGNORECASE))
        if label_elem:
            # Check the text after the label
            next_elem = label_elem.find_next()
            if next_elem:
                next_text = next_elem.get_text()
                for pattern in phone_patterns:
                    phones = re.findall(pattern, next_text)
                    if phones:
                        return [re.sub(r'[\s.-]', '', phone) for phone in phones]
            
            # Check the parent element's text
            parent = label_elem.parent
            if parent:
                parent_text = parent.get_text()
                for pattern in phone_patterns:
                    phones = re.findall(pattern, parent_text)
                    if phones:
                        return [re.sub(r'[\s.-]', '', phone) for phone in phones]
    
    # If no phone found near labels, try the provided text
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            cleaned_phones = [re.sub(r'[\s.-]', '', phone) for phone in phones]
            # Validate phone numbers (must be 10 digits for Vietnamese numbers)
            valid_phones = [p for p in cleaned_phones if len(p) == 10 and p.startswith(('0', '84'))]
            if valid_phones:
                return valid_phones
    
    return []

def extract_representative(text):
    if 'Ngoài ra' in text:
        return text.split('Ngoài ra')[0].strip()
    return text

def find_company_contact_info(company_name):
    try:
        # Suppress SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Clean and prepare company name for search
        # search_name = company_name.lower()
        # search_name = search_name.replace('công ty cổ phần', '')
        # search_name = search_name.replace('công ty tnhh', '')
        # search_name = search_name.replace('công ty', '')
        # search_name = search_name.replace('tm dv', '')
        # search_name = search_name.replace('xây dựng', '')
        # search_name = search_name.replace('địa ốc', '')
        # search_name = ' '.join(search_name.split())  # Remove extra spaces

        # # Extract main company identifiers
        # name_parts = search_name.split()
        # company_identifiers = [part for part in name_parts if len(part) > 2]

        # # Search queries with company registration number if available
        # queries = [
        #     f'"{company_name}" official website vietnam',
        #     f'"{search_name}" company website vietnam',
        #     f'"{" ".join(company_identifiers)}" business website vietnam'
        # ]

        found_website = None
        found_email = None

        # skip_domains = [
        #     # Social media
        #     'facebook.com', 'linkedin.com', 'youtube.com', 'twitter.com', 'instagram.com', 'tiktok.com',
        #     # Business directories
        #     'masothue.com', 'yellowpages', 'trangvangvietnam.com', 'doanhnghievietnam.vn', 'vietnamyp.com',
        #     'vietnambiz.vn', 'thongtincongty.com', 'pantado.com', 'vietnam-ete.com.vn',
        #     'infodoanhnghiep.com', 'vietnamcompanies.com', 'congtydoanhnghiep.com',
        #     'asadavietnam.vn', 'thongtin.co', 'vietnamnet.vn', 'vnexpress.net',
        #     # E-commerce
        #     'shopee.vn', 'lazada.vn', 'tiki.vn', 'sendo.vn',
        #     # Others
        #     'blogspot.com', 'wordpress.com', '24h.com.vn', 'news.zing.vn'
        # ]

        # def is_valid_domain(domain, company_identifiers):
        #     # Skip if domain contains any of the skip domains
        #     if any(skip in domain.lower() for skip in skip_domains):
        #         return False
                
        #     # Get the main part of the domain (without .com, .vn, etc)
        #     main_domain = domain.split('.')[0].lower()
            
        #     # Check if domain matches company identifiers exactly
        #     domain_parts = set(main_domain.split('-'))
        #     company_parts = set(company_identifiers)
            
        #     # The domain should contain all company identifiers in sequence
        #     company_sequence = ''.join(company_identifiers)
        #     domain_normalized = main_domain.replace('-', '')
            
        #     return company_sequence.lower() in domain_normalized.lower()

        # # First, find the company website
        # for query in queries:
        #     try:
        #         search_results = search(query, num_results=10, lang="vi")
                
        #         for url in search_results:
        #             try:
        #                 # Extract and clean domain
        #                 domain = extract_domain(url)
        #                 if not domain:
        #                     continue
                            
        #                 # Strict domain validation
        #                 if not is_valid_domain(domain, company_identifiers):
        #                     continue
                            
        #                 # Verify the website is accessible
        #                 try:
        #                     response = requests.get(f'https://{domain}', timeout=5, verify=False, 
        #                         headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
                            
        #                     if response.status_code == 200:
        #                         found_website = f'https://{domain}'
                                
        #                         # Now search for email only on the found website
        #                         soup = BeautifulSoup(response.text, 'html.parser')
        #                         text = soup.get_text().lower()
                                
        #                         # Look for email patterns
        #                         email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        #                         emails = re.findall(email_pattern, text)
                                
        #                         for email in emails:
        #                             # Only consider emails from the same domain
        #                             email_domain = email.split('@')[1].lower()
        #                             if domain.lower() in email_domain:
        #                                 # Prioritize business emails
        #                                 if any(word in email.lower() for word in ['info', 'contact', 'support', 'sales', 'admin']):
        #                                     found_email = email
        #                                     break
        #                                 # Take the first valid email if no business email is found
        #                                 if not found_email:
        #                                     found_email = email
                                
        #                         break
        #                 except:
        #                     continue
                            
        #             except Exception as e:
        #                 continue
                        
        #         if found_website:
        #             break
                    
        #     except Exception as e:
        #         continue

        return found_website or "Chưa cung cấp", found_email or "Chưa cung cấp"
        
    except Exception as e:
        return "Chưa cung cấp", "Chưa cung cấp"

def extract_industry(text):
    if isinstance(text, list):
        # If it's a list of industries, take the first one as main
        main_text = text[0] if text else ""
    else:
        main_text = text
        
    if 'Chi tiết:' in main_text:
        main_industry = main_text.split('Chi tiết:')[0].strip()
        details = 'Chi tiết: ' + main_text.split('Chi tiết:')[1].strip()
        return main_industry, details
    return main_text, ''

def scrape_masothue(company_name=None, url=None):
    try:
        if not company_name and not url:
            raise ValueError("Either company_name or url must be provided")
            
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        # Initialize the driver with service
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        try:
            if company_name:
                # Go to the main page
                driver.get("https://masothue.com/")
                time.sleep(2)
                
                # Find and fill the search input (try different selectors)
                try:
                    search_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                    )
                except:
                    try:
                        search_input = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".search-box input"))
                        )
                    except:
                        search_input = wait.until(
                            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Tìm kiếm']"))
                        )
                
                search_input.clear()
                time.sleep(1)
                search_input.send_keys(company_name)
                time.sleep(1)
                
                # Try to find and click the search button first
                try:
                    search_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-box button[type='submit']"))
                    )
                    search_button.click()
                except:
                    # If no button found, try pressing Enter
                    search_input.send_keys(Keys.RETURN)
                
                time.sleep(3)
                
                # Wait for and get the first result (try different selectors)
                try:
                    first_result = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".tax-listing .tax a"))
                    )
                except:
                    try:
                        first_result = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".tax a"))
                        )
                    except:
                        first_result = wait.until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'tax')]//a"))
                        )
                
                url = first_result.get_attribute('href')
                driver.get(url)
            else:
                driver.get(url)
            
            time.sleep(2)
            
            # Wait for content to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Get the page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            info = {}
            
            # Try to get tax code from title first
            title = driver.title
            if title:
                tax_code = extract_tax_code_from_title(title)
                if tax_code:
                    info['ma_so_thue'] = tax_code
            
            # Find the main content div that contains the company information
            content_div = soup.find('div', {'class': 'content'})
            if not content_div:
                content_div = soup
            
            # Extract other company information
            nganh_nghe = []
            nganh_nghe_chinh = None
            
            def extract_activities_from_text(text):
                activities = []
                # Try different patterns
                patterns = [
                    r'([^.;()]+?)\s*\((\d{4})\)',  # Name (Code)
                    r'(\d{4})[:\s-]+([^.;()]+)',   # Code: Name
                    r'(\d{4})\s*-?\s*([^.;()]+)',  # Code - Name
                    r'([^.;()]+?)[:\s-]+(\d{4})',  # Name: Code
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        if pattern == patterns[0]:  # Name (Code)
                            activity_name = clean_text(match.group(1))
                            activity_code = match.group(2)
                        elif pattern in [patterns[1], patterns[2]]:  # Code: Name or Code - Name
                            activity_name = clean_text(match.group(2))
                            activity_code = match.group(1)
                        else:  # Name: Code
                            activity_name = clean_text(match.group(1))
                            activity_code = match.group(2)
                            
                        if activity_name and activity_code:
                            activities.append((activity_name, activity_code))
                
                return activities
            
            # First try: Look for table containing business activities
            business_tables = soup.find_all('table')
            for business_table in business_tables:
                rows = business_table.find_all('tr')
                
                # Check if this table has business activities by looking at headers
                header_row = rows[0] if rows else None
                if header_row:
                    header_cells = header_row.find_all(['td', 'th'])
                    header_texts = [cell.get_text().strip().lower() for cell in header_cells]
                    
                    # Check if this is a business activity table
                    if any('mã' in text or 'ngành' in text for text in header_texts):
                        # Process data rows
                        for row in rows[1:]:  # Skip header row
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:  # Need at least 2 cells for code and name
                                code = clean_text(cells[0].get_text())
                                name = clean_text(cells[1].get_text())
                                
                                # Validate code is 4 digits
                                if re.match(r'^\d{4}$', code):
                                    activity = f"{name} ({code})"
                                    if activity not in nganh_nghe:
                                        nganh_nghe.append(activity)
                                        if code == "4669":
                                            nganh_nghe_chinh = activity
            
            # If no results from table, try other approaches
            if not nganh_nghe:
                # Look for business activity section using various patterns
                business_section_patterns = [
                    r'Ngành,?\s*nghề kinh doanh',
                    r'Lĩnh vực kinh doanh',
                    r'Ngành nghề chính',
                    r'Hoạt động kinh doanh',
                    r'Ngành nghề',
                    r'NGÀNH NGHỀ'
                ]
                
                for pattern in business_section_patterns:
                    business_sections = soup.find_all(string=re.compile(pattern, re.IGNORECASE))
                    for business_section in business_sections:
                        # Get the parent element and its siblings
                        parent = business_section.parent
                        if parent:
                            # Look in parent and next siblings
                            elements_to_check = [parent] + list(parent.find_next_siblings())
                            for element in elements_to_check:
                                # Check element's text and all child elements
                                for text_element in element.stripped_strings:
                                    activities = extract_activities_from_text(text_element)
                                    for activity_name, activity_code in activities:
                                        activity = f"{activity_name} ({activity_code})"
                                        if activity not in nganh_nghe:
                                            nganh_nghe.append(activity)
                                            if activity_code == "4669":
                                                nganh_nghe_chinh = activity
                
                # If still no results, look for elements with specific tags
                if not nganh_nghe:
                    for tag in ['strong', 'b', 'span', 'div', 'p']:
                        elements = soup.find_all(tag)
                        for element in elements:
                            text = element.get_text().strip()
                            activities = extract_activities_from_text(text)
                            for activity_name, activity_code in activities:
                                activity = f"{activity_name} ({activity_code})"
                                if activity not in nganh_nghe:
                                    nganh_nghe.append(activity)
                                    if activity_code == "4669":
                                        nganh_nghe_chinh = activity
            
            # Clean up the results
            nganh_nghe = [act for act in nganh_nghe if act and not act.startswith('Ngành')]
            nganh_nghe = list(dict.fromkeys(nganh_nghe))  # Remove duplicates while preserving order
            
            # Clean up activities
            cleaned_activities = []
            for act in nganh_nghe:
                # Remove common prefixes and clean up
                act = re.sub(r'^[-\d\s.:]+', '', act).strip()
                act = re.sub(r'^Ngành,?\s*nghề\s+(?:kinh doanh\s+)?chính:\s*', '', act, flags=re.IGNORECASE).strip()
                act = re.sub(r'^\d+\.\s*', '', act).strip()  # Remove leading numbers
                
                # Extract activity name and code
                match = re.search(r'(.*?)\s*\((\d{4})\)', act)
                if match:
                    activity_name = clean_text(match.group(1))
                    activity_code = match.group(2)
                    
                    # Validate activity code length
                    if len(activity_code) != 4:
                        continue
                        
                    # Skip if activity name is too short or contains invalid patterns
                    if (len(activity_name) < 3 or 
                        'cập nhật' in activity_name.lower() or
                        'ẩn thông tin' in activity_name.lower() or
                        'lần cuối' in activity_name.lower() or
                        'thông tin' in activity_name.lower() or
                        re.search(r'\d{4}-\d{2}-\d{2}', activity_name)):  # Skip dates
                        continue
                    
                    # Skip common invalid patterns
                    invalid_patterns = [
                        r'^\d+$',  # Just numbers
                        r'^[a-zA-Z0-9\s]{1,2}$',  # Very short alphanumeric
                        r'^\W+$',  # Just special characters
                    ]
                    if any(re.match(p, activity_name) for p in invalid_patterns):
                        continue
                    
                    # Reconstruct activity with clean name and code
                    act = f"{activity_name} ({activity_code})"
                    if act:
                        cleaned_activities.append(act)
            
            nganh_nghe = cleaned_activities
            
            # If we found any business activities, add them to info
            if nganh_nghe:
                info['nganh_nghe'] = nganh_nghe
                if nganh_nghe_chinh:
                    info['nganh_nghe_chinh'] = nganh_nghe_chinh
            
            # Extract phone numbers
            phone_numbers = []
            for text in content_div.stripped_strings:
                phones = extract_contact_from_text(text, content_div)
                phone_numbers.extend(phones)
            
            if phone_numbers:
                info['so_dien_thoai'] = phone_numbers[0]
            else:
                info['so_dien_thoai'] = "Chưa cung cấp"
            
            for text in content_div.stripped_strings:
                if 'Người đại diện' in text and 'nguoi_dai_dien' not in info:
                    try:
                        nguoi_dai_dien = extract_representative(text.split('Người đại diện')[1].strip(':').strip())
                        if nguoi_dai_dien:
                            info['nguoi_dai_dien'] = nguoi_dai_dien
                    except:
                        pass
                        
                if 'Địa chỉ' in text and 'dia_chi' not in info:
                    try:
                        dia_chi = text.split('Địa chỉ')[1].strip(':').strip()
                        if dia_chi:
                            info['dia_chi'] = dia_chi
                    except:
                        pass
            
            # If we still don't have some information, try finding it in elements
            if not info.get('nguoi_dai_dien'):
                nguoi_dai_dien_elem = soup.find(string=re.compile('Người đại diện'))
                if nguoi_dai_dien_elem and nguoi_dai_dien_elem.find_next():
                    info['nguoi_dai_dien'] = extract_representative(clean_text(nguoi_dai_dien_elem.find_next().get_text()))
            
            if not info.get('dia_chi'):
                dia_chi_elem = soup.find(string=re.compile('Địa chỉ'))
                if dia_chi_elem and dia_chi_elem.find_next():
                    info['dia_chi'] = clean_text(dia_chi_elem.find_next().get_text())
            
            # Find company contact info from Google
            if 'ma_so_thue' in info:
                website, email = find_company_contact_info(company_name or info.get('ten_cong_ty', ''))
                info['website'] = website if website != "Chưa cung cấp" else "Chưa cung cấp"
                info['email'] = email if email != "Chưa cung cấp" else "Chưa cung cấp"
            
            return info
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error scraping masothue.com: {str(e)}")
        return None

def extract_domain(url):
    try:
        # Remove protocol and www
        domain = url.lower().replace('https://', '').replace('http://', '').replace('www.', '')
        # Get domain without path
        domain = domain.split('/')[0]
        return domain
    except:
        return ""

def print_company_info(info, company_name):
    print("\nThông tin doanh nghiệp:")
    print("-" * 50)
    print(f"Tên công ty: {company_name}")
    print(f"Mã số thuế: {info.get('ma_so_thue', 'Chưa cung cấp')}")
    
    # Handle industry information
    if info.get('nganh_nghe'):
        main_industry, details = extract_industry(info['nganh_nghe'])
        print(f"Ngành nghề chính: {main_industry}")
        if details:
            print(details)
    
    print(f"Người đại diện: {info.get('nguoi_dai_dien', 'Chưa cung cấp')}")
    print(f"Địa chỉ: {info.get('dia_chi', 'Chưa cung cấp')}")
    print(f"Số điện thoại: {info.get('so_dien_thoai', 'Chưa cung cấp')}")
    
    website, email = find_company_contact_info(company_name)
    print(f"Email: {email}")
    print(f"Website: {website}")
    print("-" * 50)

def main():
    import sys
    import time
    
    start_time = time.time()
    
    # Default company name if none provided
    default_company = "CÔNG TY TNHH THƯƠNG MẠI TỔNG HỢP VIỆT XANH"
    
    # Get company name from command line argument if provided, otherwise use default
    company_name = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else default_company
    
    info = scrape_masothue(company_name=company_name)
    
    if info:
        print_company_info(info, company_name)
    else:
        print("\nKhông tìm thấy thông tin doanh nghiệp")
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nThời gian thực thi: {execution_time:.2f} giây")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(main)