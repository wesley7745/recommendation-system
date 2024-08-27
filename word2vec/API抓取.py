import base64
import requests
import pprint
import json
import math
from flatten_json import flatten
import pandas as pd
import time

class UdemyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = 'https://www.udemy.com/api-2.0/courses/'

    def get_auth_string(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_string_encoded = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {auth_string_encoded}"
# def call_api(self, search_term, catergory, subcategory, language , start_page=1, level=None):
    def call_api(self, search_term, catergory, subcategory, language , start_page=1, level=None):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.get_auth_string(),
            "Content-Type": "application/json"
        }

        all_results = []
        for language in languages:
            params = {
                'page': start_page,
                'page_size': 100,
                'search': search_term,
                'language': language,
                'catergory': catergory,
                'subcategory': subcategory
            }

            if level and level != 'all':
                params['instructional_level'] = level
            
            while True:
                response = requests.get(self.base_url, headers=headers, params=params)
                
                if response.status_code == 404:
                    print(f"Page not found: {response.url}")
                    break
                
                response.raise_for_status()
                response_json = response.json()
                for result in response_json['results']:
                    result['course_level'] = level if level else 'all'
                    result['course_language'] = language
                all_results.extend(response_json['results'])

                total_results = response_json.get('count', 0)
                total_pages = math.ceil(total_results / params['page_size'])

                print(f"Total Result for {language}, Level {level}: {total_results}, Current page: {params['page']}")

                params['page'] += 1

                if params['page'] > total_pages:
                    break

        return all_results

    def flatten_results(self, response_json):
        flattened_results = [flatten(result) for result in response_json]
        return flattened_results

    def print_results(self, result):
        pprint.pprint(result)

    def save_to_excel(self, results, filename='UdemyCourses_HR1.xlsx'):
        df = pd.DataFrame(results)
        df.drop_duplicates(subset=['id'], inplace=True)  # 去重，保留每個 `course_id` 的第一條記錄
        df.to_excel(filename, index=False)

    def save_to_local_file(self, response, filename='response.json'):
        with open(filename, 'w') as f:
            json.dump(response, f)

    def read_from_local_file(self, filename='response.json'):
        with open(filename, 'r') as f:
            response = json.load(f)
        return response

# 設定關鍵字
search_keyword = 'Generative AI'

client_id = 'dzfgQWJeWrmUesYxFztc6ouB2wAgYOsVauqdOq1M'
client_secret = '2gDKjI3fO7zU1mirxsYU4Ux8Dd3ij08bGrl1zWm5LOYJG0UZsqG1lu30mthYPRs4mZRI3VK9uiV4RHhPsADaLvr6L2c8Qrjsggw9t4v8dM96bGN9bWQRLToeXyZjBl1M'
udemy = UdemyAPI(client_id, client_secret)

# 設定語言和課程級別
languages = ['zh', 'en']
levels = ['all', 'beginner', 'intermediate', 'expert']
catergory = ['Development']
subcategory = ['No-Code Development']

# catergory = ['Development']
# subcategory = ['Data Science', 'Database Design & Development', 'Software Testing', 'No-Code Development']
all_results = []

# 針對上述設定語言及課程級別分別 call API
for language in languages:
    for level in levels:
        response = udemy.call_api(search_keyword, catergory=catergory, subcategory=subcategory, language=language, start_page=1, level=level)
        # response = udemy.call_api(search_keyword, catergory=catergory, language=language, start_page=1, level=level)
        # response = udemy.call_api(catergory=catergory, language=language, subcategory=subcategory, start_page=1, level=level)
        all_results.extend(response)
        time.sleep(1)

udemy.save_to_local_file(all_results, 'UdemyCoursesResponse.json')

response = udemy.read_from_local_file('UdemyCoursesResponse.json')

if response:
    result = udemy.flatten_results(response)
    udemy.print_results(result)
    udemy.save_to_excel(result, 'UdemyCourses_hrAI2.xlsx')

print("成功")

