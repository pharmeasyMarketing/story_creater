# using as of march without automated images

import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
import re
import mysql.connector
import pandas as pd
import random
import time
import json
from PIL import Image
import http.client
import io
from tempfile import NamedTemporaryFile
import pytz
from datetime import datetime


@st.cache_data(show_spinner=False)
def med_extract(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        h1_heading = soup.find('h1').text if soup.find('h1') else None

        content = ''
        for element in soup.find_all(True, recursive=False):
            if element.get('class') and 'MedicineFAQs_contentWrapper__S9C0g' in element.get('class'):
                break
            content += element.get_text(separator='\n') + '\n'

        result_dict = {h1_heading: content.strip()}

        return result_dict
    else:
        print(f"Error: Unable to fetch the page. Status code: {response.status_code}")
        return None

def extract_data_from_webpage(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        site_content_div = soup.find('div', class_='site-content')

        if site_content_div:
            h2_tags = site_content_div.find_all('h2')

            data_dict = {}

            for index, h2_tag in enumerate(h2_tags):
                h2_text = h2_tag.get_text().strip()

                if h2_text.lower() == "introduction" or h2_text.lower() == "key highlights:" or h2_text.lower() == "conclusion" or h2_text.lower() == "introduction:" or h2_text.lower() == "this might be related & helpful!": 
                    continue

                if h2_text.lower() == "faqs:" or h2_text.lower() == "frequently asked questions" or h2_text.lower() == "frequently asked questions (faqs)" or h2_text.lower() == "frequently asked questions (faq)" or h2_text.lower() == "faq (frequently asked questions)" or h2_text.lower() == "frequently asked questions:":
                    break

                next_sibling = h2_tag.find_next_sibling()

                text_after_h2 = ""

                while next_sibling and next_sibling.name != 'h2':
                    if next_sibling.name == 'div' and 'two_col_right' in next_sibling.get('class', []):
                        break

                    text_after_h2 += next_sibling.get_text(separator=' ', strip=True)

                    next_sibling = next_sibling.find_next_sibling()

                data_dict[h2_text] = text_after_h2.strip()

            return data_dict
        else:
            print("Error: 'site-content' div not found.")
            return None
    else:
        print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
        return None

def extract_idetifier(url):
    pattern = r'pharmeasy\.in/([^/]+)'
    match = re.search(pattern, url)
    if match:
        result_text = match.group(1)
        return result_text
    else:
        return None

@st.cache_data(show_spinner=False)
def extract_data(url):
    identifier = extract_idetifier(url)
    if identifier == 'online-medicine-order':
        data_dict = med_extract(url)
    elif identifier == 'blog':
        data_dict = extract_data_from_webpage(url)
    elif identifier == 'health_care':
        pass
    else:
        st.write("something wrong with url") 

    return data_dict           

def scrape_medauthor_name(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        author_tag = soup.find('p', class_='AuthorCard_name__l51df')
        if author_tag:
            author_name = author_tag.get_text(strip=True)
            return author_name
        else:
            print("Author tag not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def extract_drname(url):
    if extract_idetifier(url) == "blog":


        class_name = "box_des box_des_one d_f"

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve the content from {url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        div_tag = soup.find('div', class_=class_name)

        if div_tag:
            a_tag = div_tag.find('a')
            if a_tag:
                a_tag_text = a_tag.get_text(strip=True)
                return a_tag_text
            else:
                print(f"No <a> tag found inside <div> tag with class '{class_name}' on {url}")
                return None
        else:
            print(f"No <div> tag with class '{class_name}' found on {url}")
            return None
        
    elif extract_idetifier(url) == "online-medicine-order":
        return scrape_medauthor_name(url)

    else:
        return "Dr. Nikita Toshi"    

def scrape_image_src_med(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        img_tag = soup.find('img', class_='ProductImageCarousel_productImage__yzafa')

        if img_tag:
            img_src = img_tag.get('src')
            return img_src
        else:
            print("Image tag not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def images(query):

    api_token = "v2/SUM3NWxYTnJNZmxCcVNMZTI0d1NZT0djZnZLRDdPYWEvNDE1MTIxMjc1L2N1c3RvbWVyLzQvVWREanhyUVVQVWJWWThQMzcwU3dSdFFqUWxkLWJxV05HZVZCcVlzQXo2R056QjJHMkxNLVY0QTdFVXdBdVkwdWt0ZF9BZU9vRUJQREZ4SVNnZHVORURwSWdqeTNIemo2RW9JVjZmWWZrWmFMelVTdWNIakVmZzV5NmNZa3ZVUnRTd19udmU5aXdJaEFSd0JoT0MwR3QwSFhYazVrcEdDcFhpRF9WN0Z2NHpYSVVhRDRRV1NGSWptNURSeFRDWlY4NVowQms2QmZyMEZRd0tTbXk2Z091US90ckltcU1Sc1JvN1FpWENOejVabmdB"

    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    query_params = {
        "query": query,
        "image_type": ["photo"],
        "orientation": "vertical",
        # "people_number": 3,  # You can adjust this as needed
        "page": 3,  # Adjust the page number if you want more results
        "per_page": 1  # Adjust the number of results per page
        # "width": width,
        # "height": height
    }

    api_url = "https://api.shutterstock.com/v2/images/search"

    try:
        response = requests.get(api_url, params=query_params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad requests

        data = response.json()
        # print(data)
        if data.get("data", []):
            image_url = data["data"][0].get("assets", {}).get("preview", {}).get("url", "")
            return image_url
        else:
            return fallback_images()

    except Exception as e:
        return fallback_images()
        
   

def slug_creater(sentence):
    cleaned_sentence = re.sub(r'[^\w\s]', '', sentence)

    words = cleaned_sentence.lower().split()

    hyphenated_sentence = "-".join(words)

    return hyphenated_sentence

def generate_keyword(heading):
   
    prompt = f'''Extract the main keyword from the following heading:
    "{heading}"
    '''
    prompt += '''Provide a short and clear response focusing on the main keyword in the given heading. Provide only the main keyword from the given heading.
    '''

    

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.2,
    )

    generated_text = response['choices'][0]['text']
    
    return (generated_text).strip()

def scrape_title_img(url):
    if extract_idetifier(url) == 'blog':

        img_class = "img-responsive border_r4 postthumbnail_image wp-post-image"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                img_tag = soup.find('img', class_=img_class)

                if img_tag:
                    img_link = img_tag.get('src')
                    return img_link
                else:
                    print(f"No image found with class: {img_class}")
                    return fallback_images()

            else:
                print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
                return fallback_images()

        except Exception as e:
            print(f"Error: {e}")
            return fallback_images()
        
    if extract_idetifier(url) == 'online-medicine-order':
        return med_img_fallback()
    

def improve_med_title(title):
    prompt = f'''Given the heading:
    "{title}"

Please provide a brief and clear response by extracting the main keyword from the given heading. For example, if the title is "Ecosprin 75mg Strip Of 14 Tablets," respond with something like "Know more about Ecosprin 75mg tablet" Avoid including additional information like "Main keyword: Ecosprin 75mg" only return the main keyword without extra details.
'''


    

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.2,
    )

    generated_text = response['choices'][0]['text']
    
    return (generated_text).strip()

@st.cache_data(show_spinner=False)
def generate_responses(scrap_dict):
    ideal_format = {
  "Possible Side Effects": "Gargling with salt water can have potential side effects, including dehydration, high sodium intake, and softening of tooth enamel.",
  "When to Avoid Gargling Salt Water": "People who have difficulty gargling or who need to limit their sodium intake for health reasons should consult with their healthcare provider before gargling with salt water. ",
  "Precautions to Take": "To minimize the risks associated with gargling salt water, it is important to take certain precautions. ",
  "Dehydration": "One of the potential risks of gargling with salt water is dehydration. Consuming large amounts of salt water can lead to dehydration",
  "High Blood Pressure and Cardiovascular Disease": "Another potential risk of gargling with salt water is the intake of high sodium"
}

    responses_list = []
    for heading in scrap_dict:
        text_to_sent = scrap_dict[heading]

        
        prompt = f'''Imagine you are a medical professional. Follow these steps:
  1. Carefully read the provided text: "{text_to_sent}".
  2. Generate up to ten headings based on the given text. Feel free to create fewer if only three headings seem appropriate.
  3. For each heading you create, write a description of 20 to 30 words, strictly don't write large descriptions.
  4. Finally, provide your response in the format of a Python dictionary, where each heading corresponds to its respective description, For example this is the ideal format : "{ideal_format}" this is just an example don't read it as reference only take it as a response format example, strictly return response in this pattern only
'''
        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                    "role": "system",
                    "content":  prompt,
                    },
                
                ],
                max_tokens=2000,
                n=5,
                stop=None,
                temperature=0.2,
            )
            response = gpt_response["choices"][0]["message"]["content"].strip()
            response = response
        # print(type(response))
        # print(response)

        except Exception as e:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {
                    "role": "system",
                    "content":  prompt,
                    },
                
                ],
                max_tokens=7000,
                n=1,
                stop=None,
                temperature=0.2,
            )
            response = gpt_response["choices"][0]["message"]["content"].strip()
            response = response

        response_dict = {}
        try:
            response_dict = eval(response)
            response_dict["section_dump"] = scrap_dict[heading]
            # print(response_dict)
            # print(type(response_dict))
        except Exception as e:
            response_dict["section_dump"] = scrap_dict[heading]

            continue

        
        response_dict["title"] = heading 
            
           
        responses_list.append(response_dict)
        # print("1")
        # print(heading)
        # print(type(response))
        
    return responses_list


def scrap_url_title(url):
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the first h1 tag
            first_h1_tag = soup.find('h1')

            # Extract and return the text content of the first h1 tag
            if first_h1_tag:
                return first_h1_tag.get_text()
            else:
                print("No <h1> tag found on the webpage.")
                return None

        else:
            print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def scrape_h1_text(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            h1_tag = soup.find('h1')

            if h1_tag:
                return h1_tag.text.strip()
            else:
                return "No H1 tag found on the page."

        else:
            return f"Failed to retrieve the page. Status code: {response.status_code}"

    except Exception as e:
        return f"An error occurred: {str(e)}"


def improve_story_title(heading, url):
    main_title = scrape_h1_text(url)
    if main_title.lower() in heading.lower():
        return heading

    prompt = f'''As an SEO expert, your goal is to optimize the heading for search engines.

- Begin by thoroughly understanding the primary topic (the topic that the title is talking about) addressed in the title: Title: {main_title}.
- Evaluate the alignment of the heading "{heading}" with the main topic keyword; if it doesn't align, rephrase it using the main title keyword.
- Ensure that the output contains only the improved title without any additional explanation, and there should be only a single output.
- the heading should be in under 15 words.
- the improved heading should only be related to current heading. it should not include any extra context, but only the main topic.
For the given heading "{heading}" and main title "{main_title}", create an improved title that aligns with the main title keyword.
- strictly do not add things like "Improved Title: "Pomegranate Uses for Health" simple return main title that you created in this, thot should be "Pomegranate uses for health" only take this as an example.

'''
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=15,
        temperature=0.5,
    )
    generated_text = response['choices'][0]['text']
    return generated_text.strip()

def blog_slug_trimming(url):
    # Define the regex pattern
    pattern = r'/blog/([^/]+)'

    # Use re.search to find the match
    match = re.search(pattern, url)

    # Check if a match is found
    if match:
        # Extract the part after 'blog/'
        blog_part = match.group(1)
        return blog_part
    else:
        return None
          

def fallback_images():
    images_list = [
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2025006328-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_1739736104-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2036645162-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_1966439416-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_339708269-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2294489191-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2259314129-1.jpg",
    "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2200138025-1.jpg"
]
    random_choice = random.choices(images_list)
    # print(type(random_choice))
    random_choice_str = random_choice[0]
    # print(type(random_choice_str))
    return random_choice_str


def med_img_fallback():
    images_list = [
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_1169699956-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_1463056853-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_376019317-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2195278149-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2153117043-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2243874667-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_725473423-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_294860387-1.jpg",
        "https://pharmeasy.in/story/wp-content/uploads/2023/12/shutterstock_2297314893-1.jpg"
    ]

    random_choice = random.choices(images_list)
    random_choice_str = random_choice[0]
    return random_choice_str
# responses = generate_responses(result)
# print(responses)

# -------------------------------- midjouney images start --------------------------------------------

# BASE_URL = "https://api.thenextleg.io/v2"
# AUTH_TOKEN = "65f250e1-1499-4c2f-967a-8251c7d05ad8"
# AUTH_HEADERS = {
#     "Authorization": f"Bearer {AUTH_TOKEN}",
#     "Content-Type": "application/json",
# }


def sleeep(milliseconds):
    time.sleep(milliseconds / 1000)

# @st.cache_data(show_spinner=False)
# def fetch_to_completion(message_id, retry_count, max_retry=20):
#     image_res = requests.get(f"{BASE_URL}/message/{message_id}", headers=AUTH_HEADERS)
#     image_response_data = image_res.json()

#     if image_response_data["progress"] == 100:
#         return image_response_data

#     if image_response_data["progress"] == "incomplete":
#         raise Exception("Image generation failed")

#     if retry_count > max_retry:
#         raise Exception("Max retries exceeded")

#     # if image_response_data["progress"] and image_response_data["progressImageUrl"]:
#     #     print("---------------------")
#     #     print(f'Progress: {image_response_data["progress"]}%')
#     #     print(f'Progress Image Url: {image_response_data["progressImageUrl"]}')
#     #     print("---------------------")

#     sleep(10000)
#     return fetch_to_completion(message_id, retry_count + 1)

# @st.cache_data(show_spinner=False)
# def generate_image(prompt):
#     try:
#         image_res = requests.post(
#             f"{BASE_URL}/imagine", headers=AUTH_HEADERS, json={"msg": prompt}
#         )
#         image_res.raise_for_status()  # Check for HTTP errors

#         image_response_data = image_res.json()
#         message_id = image_response_data.get("messageId")

#         if message_id:
#             completed_image_data = fetch_to_completion(message_id, 0)

#             image_urls = completed_image_data['response']['imageUrls']
#             return image_urls
#         else:
#             print("Error: 'messageId' not found in API response")

#     except requests.exceptions.RequestException as e:
#         print(f"Error making API request: {e}")
    # try:
    #     image_res = requests.post(
    #         f"{BASE_URL}/imagine", headers=AUTH_HEADERS, json={"msg": prompt}
    #     )
    #     image_response_data = image_res.json()

    #     completed_image_data = fetch_to_completion(image_response_data["messageId"], 0)

    #     # variation_res = requests.post(
    #     #     f"{BASE_URL}/button",
    #     #     headers=AUTH_HEADERS,
    #     #     json={
    #     #         "button": "V1",
    #     #         "buttonMessageId": completed_image_data["response"]["buttonMessageId"],
    #     #     },
    #     # )
    #     # variation_response_data = variation_res.json()
    #     # completed_variation_data = fetch_to_completion(
    #     #     variation_response_data["messageId"], 0
    #     # )
    #     image_urls = completed_image_data['response']['imageUrls']
    #     return image_urls

    # except requests.exceptions.RequestException as e:
    #     # print(f"Error making API request: {e}")
    #     return "image not found"
def send_request(method, path, body=None, headers={}):
    conn = http.client.HTTPSConnection("demo.imagineapi.dev")
    conn.request(method, path, body=json.dumps(body) if body else None, headers=headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    conn.close()
    return data

def generate_image(prompt):
    data = {
        "prompt": prompt,
    }

    headers = {
        'Authorization': 'Bearer MIgP1r88ut2WSx-uygNvM_ThK9YmjwKf',  # <<<< TODO: remember to change this
        'Content-Type': 'application/json'
    }

    prompt_response_data = send_request('POST', '/items/images/', data, headers)

    def check_image_status():
        response_data = send_request('GET', f"/items/images/{prompt_response_data['data']['id']}", headers=headers)
        if response_data['data']['status'] in ['completed', 'failed']:
            # pprint.pp(response_data['data']['upscaled_urls'])
            url_list = response_data['data']['upscaled_urls']
            return True, url_list
        else:
            return False, []

    while True:
        completed, url_list = check_image_status()
        if completed:
            return url_list
        time.sleep(5)

@st.cache_data(show_spinner=False)
def generate_image_prompt(main_title, sub_title):

    prompt = f'''
    main title = "{main_title}"
    subtitle = "{sub_title}" 

    Need a detailed prompt for midjourney AI service to portray a central idea depicted by the combination of above titles which would be related to healthcare, the image needs to be photorealistic, including real people or real objects. Don't directly quote any of the above titles in the prompt. Make sure that the prompt excludes any form of suggestions to insert text, be it infographics, bullets, lists, headings, subheadings, words, signatures, or logos, allowing the image to speak for itself. Directly just output the exact prompt in plain text, no other detail or explanation is needed.
    '''
    # prompt = f" Imagine operating an online platform focused on delivering healthcare information through blogs. To enhance the content, I aim to generate images using AI. Your task is to formulate a prompt that effectively conveys the need for generating images related to healthcare information on the platform. Please craft a suitable prompt using the given description: '{desc}'."
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content":  prompt,
            },
                
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.2,
        )
    
    response = gpt_response["choices"][0]["message"]["content"].strip()
    response = response
    return response
@st.cache_data(show_spinner=False)

def retreive_img_bytes(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return response.content
        else:
            return 
    except Exception as e:
        return 

@st.cache_data(show_spinner=False)
def post_image_wordpress(username, password, site_url, binary_data):
    auth = (username, password)
    image_extension = "jpg"  # Change to the appropriate image extension
    
    with NamedTemporaryFile(delete=False, mode="wb", suffix=f".{image_extension}") as temp_file:
        temp_file.write(binary_data)
        temp_file_path = temp_file.name

    media_endpoint = f"{site_url}/wp-json/wp/v2/media"
    headers = {
        'Content-Disposition': f'attachment; filename=image.{image_extension}',
    }

    files = {'file': (f'image.{image_extension}', open(temp_file_path, 'rb'))}

    try:
        response = requests.post(media_endpoint, auth=auth, headers=headers, files=files)

        if response.status_code == 201:
            media_data = response.json()
            media_id = media_data['id']
            media_url = media_data['guid']['rendered']
            
            # print(f"Image uploaded successfully. Media ID: {media_id}")
            # print(f"Media URL: {media_url}")
            return media_url
        else:
            print(f"Failed to upload image. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    # finally:
    #     os.remove(temp_file_path)

@st.cache_data(show_spinner=False)
def generate_final_wordressl_ink(main_title, sub_title):
    image_prompt = (generate_image_prompt(main_title, sub_title))
    print(image_prompt)
    image_url_list = generate_image(image_prompt + " --aspect 9:16 --no text, heading, watermark, words, letters, typography, slogans, signature ")
    # print("image generated")
    # image_url = random.choice(image_url_list)
    wordpress_img_url_list = []
    if image_url_list is None:
        print("image url list none")
        return 0
    else:
        # print("else")
        for image_url in image_url_list:
            # print("byte generation")
            binary_data = retreive_img_bytes(image_url)
            username = 'sarthak'
            password = 'uwrM 9UeW QF0n 5wGw nlWk Ye55'
            site_url = 'https://pharmeasy.in/story'
            try:
                wordpress_img_url = post_image_wordpress(username, password, site_url, binary_data)
                wordpress_img_url_list.append(wordpress_img_url)
            except:
                wordpress_img_url_list.append("image not found something went wrong")

            # print("genetation done and saved to wordpress")
        # wordpress_img_url_list = [link + ".webp" for link in wordpress_img_url_list]
        new_wordpress_img_url_list = []
        for link in wordpress_img_url_list:
            try:
                link = link + ".webp"
                new_wordpress_img_url_list.append(link)
            except:
                new_wordpress_img_url_list.append("image not found")
                
        return new_wordpress_img_url_list

# ---------------------------------midjourney imag end ---------------------------------
def extract_drname_link(url):
    class_name = "box_des box_des_one d_f"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the content from {url}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    div_tag = soup.find('div', class_=class_name)

    if div_tag:
        a_tag = div_tag.find('a')
        if a_tag:
            
            a_link = a_tag.get('href')
            return a_link
        else:
            print(f"No <a> tag found inside <div> tag with class '{class_name}' on {url}")
            return "https://pharmeasy.in/legal/editorial-policy"
    else:
        print(f"No <div> tag with class '{class_name}' found on {url}")
        return "https://pharmeasy.in/legal/editorial-policy"    

def published_time():
    current_time = datetime.now()

    # Convert current time to a specific timezone
    timezone = pytz.timezone('Asia/Kolkata')
    current_time = timezone.localize(current_time)

    # Format the current time
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    return formatted_time
@st.cache_data(show_spinner=False)
def main_format(scrap_result, url):

    responses = generate_responses(scrap_result)
    # st.write(responses)
    new_list = []
    for section in responses:
        if extract_idetifier(url) == "online-medicine-order":
            response_dict = {}
            response_dict['title'] = section['title']
            response_dict['section_dump'] = section['section_dump']
            response_dict['Title_Image'] = med_img_fallback()
            response_dict['Reviewed_by'] = scrape_medauthor_name(url)
            response_dict['slug'] = slug_creater(section['title'])
            response_dict['target_page1'] = url
            response_dict['page_type'] = 'medicine'
            response_dict['status'] = 'draft'
            
            section.popitem()
            section.popitem()
            for index, (heading2, description2) in enumerate(section.items()):
                # keyword = generate_keyword(heading2)
                heading1 = f"heading{index + 1}"
                description1 = f"description{index + 1}"
                image = f"image{index+1}"
                response_dict[heading1] = heading2
                response_dict[description1] = description2
                response_dict[image] = med_img_fallback()

        if extract_idetifier(url) == 'blog':
            response_dict = {}
            response_dict['title'] = section['title']
            title = section['title']
            Blog_Source_Title = scrap_url_title(url)
            response_dict['Blog_Source_Title'] = Blog_Source_Title
            response_dict['identifier'] = title + Blog_Source_Title

            response_dict['section_dump'] = section['section_dump']
            response_dict['Title_Image'] = scrape_title_img(url)
            response_dict['Reviewed_by'] = extract_drname(url)
            response_dict['slug'] = slug_creater(section['title'])
            response_dict['target_page1'] = blog_slug_trimming(url)
            response_dict['page_type'] = 'blog'
            response_dict['status'] = 'draft'
            response_dict['reviewer_link'] = extract_drname_link(url)
            response_dict['published_on'] = published_time()
            response_dict['modified_on'] = published_time()
            section.popitem()
            section.popitem()
            for index, (heading2, description2) in enumerate(section.items()):
                # keyword = generate_keyword(heading2)
                if index + 1 >= 11 :
                    break
                heading1 = f"heading{index + 1}"
                description1 = f"description{index + 1}"
                image_dump = f"image{index+1}_dump"
                image = f"image{index+1}"
                response_dict[heading1] = heading2
                response_dict[description1] = description2
                response_dict[image] = " "
                response_dict[image_dump] = " "
                # image_url_list = generate_final_wordressl_ink(title, heading2)
                # if image_url_list == 0:
                #     response_dict[image] = "Image not found"
                #     response_dict[image_dump] = "image not found something went wrong"
                # else:    
                #     response_dict[image] = random.choice(image_url_list)
                #     response_dict[image_dump] = ','.join(image_url_list)
                st.write(f"Slide {index + 1} created")    
                
                


        new_list.append(response_dict)
        st.write(new_list)
        save_data_to_mysql(new_list)
        new_list = []
        sleeep(5000)
    return new_list  

@st.cache_data(show_spinner=False)
def bulk_upload(urls_list):
    for i in range(0,len(urls_list)): 

        result = extract_data(urls_list[i])

        if result:
            st.success("Data extraction successful!")
                            
            responses = main_format(result, urls_list[i])
            # st.write("Generated Responses:")
            # st.write(responses)
                        

            # save_data_to_mysql(responses)
        else:
            st.error("Data extraction failed.")
            time.sleep(10)                

@st.cache_data(show_spinner=False)
def save_data_to_mysql(data_list):

    for data in data_list:
          
        conn = None
        cursor = None
        try:
            table = "stories"
            conn = mysql.connector.connect(
                host="srv1116.hstgr.io",
                user="u914396707_story",
                password="Hostinger@123.",
                database="u914396707_story"
            )

            cursor = conn.cursor()

            insert_query = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['%s']*len(data))})"

            values = tuple(data.values())
            cursor.execute(insert_query, values)

            conn.commit()

            st.write("Data successfully inserted into the database!")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()                      

def main():
    # st.set_theme("dark")

    st.title("PharmEasy Story Creator")

    # Sidebar
    st.sidebar.header("Settings")
    # webpage_url = st.sidebar.text_input("Enter Webpage URL:")
    openai_key = st.sidebar.text_input("Enter your open Ai key", type = "password")

    file = st.sidebar.file_uploader("Upload a CSV file containing Blog and Med PDP urls in URLs coloumn for bulk upload", type=["csv"])
    if st.sidebar.button("Create Stories"):
        if openai_key:
            openai.api_key = openai_key

            if file is not None:
                df = pd.read_csv(file)
    
                urls_list = df['URLs'].tolist()
    
    
                with st.spinner("Processing data..."):
                    st.write("Running ....")
                    bulk_upload(urls_list)
                st.success("Process Done")                
    # else:
    #     st.write("Upload CSV file in correct format")

if __name__ == '__main__':
    main()
