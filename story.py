import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
import re
import mysql.connector


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

                if h2_text.lower() == "introduction" or h2_text.lower() == "key highlights:" or h2_text.lower() == "conclusion":
                    continue

                if h2_text.lower() == "faqs:" or h2_text.lower() == "frequently asked questions" or h2_text.lower() == "frequently asked questions (faqs)" or h2_text.lower() == "frequently asked questions (faq)" or h2_text.lower() == "faq (frequently asked questions)":
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


def extract_drname(url):


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
            return "no link found"

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")

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
                return None

        else:
            print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

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
  2. Generate up to five headings based on the given text. Feel free to create fewer if only three headings seem appropriate.
  3. For each heading you create, write a description of 10 to 20 words, strictly don't write large descriptions.
  4. Finally, provide your response in the format of a Python dictionary, where each heading corresponds to its respective description, For example this is the ideal format : "{ideal_format}" this is just an example don't read it as reference only take it as a response format example, strictly return response in this pattern only
'''

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
        try:
            response_dict = eval(response)
            response_dict["section_dump"] = scrap_dict[heading]
            # print(response_dict)
            # print(type(response_dict))
        except Exception as e:
            continue

        
        response_dict["title"] = heading  
           
        responses_list.append(response_dict)
        # print("1")
        # print(heading)
        # print(type(response))
        
    return responses_list

def save_data_to_mysql(data_list):


    for data in data_list:
        conn = None
        cursor = None
        try:
            table = "stories"
            conn = mysql.connector.connect(
                host="srv1258.hstgr.io",
                user="u100889959_magicbytes",
                password="Magicbyte@49",
                database="u100889959_magicbytes"
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

def improve_story_title(heading, main_title):
 
    prompt = f'''You are an SEO expert: 
    
    - Gain a thorough understanding of the primary keyword addressed in the title: Title: {main_title}.
    - Ensure that the heading "{heading}" aligns with the main topic keyword; if not, rephrase it using the main title keyword.
    - If the heading already includes the main title keyword, retain it without modification. 
    - Also the output should only contains the output; no explanation should be there.
    '''

    

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.2,
    )
    generated_text = response['choices'][0]['text']
    return (generated_text).strip()

def main_format(scrap_result, url):

    responses = generate_responses(scrap_result)
    # st.write(responses)
    new_list = []
    for section in responses:
        
        response_dict = {}
        response_dict['title'] = section['title']
        response_dict['section_dump'] = section['section_dump']
        response_dict['Title_Image'] = scrape_title_img(url)
        response_dict['Reviewed_by'] = extract_drname(url)
        response_dict['slug'] = slug_creater(section['title'])
        response_dict['target_page1'] = url
        section.popitem()
        section.popitem()
        for index, (heading2, description2) in enumerate(section.items()):
            keyword = generate_keyword(heading2)
            heading1 = f"heading{index + 1}"
            description1 = f"description{index + 1}"
            image = f"image{index+1}"
            response_dict[heading1] = heading2
            response_dict[description1] = description2
            response_dict[image] = images(keyword)

        new_list.append(response_dict)
    return new_list        


# responses = generate_responses(result)
# print(responses)

def main():
    st.title("PharmEasy Story Creater")

    # Sidebar
    st.sidebar.header("Settings")
    webpage_url = st.sidebar.text_input("Enter Webpage URL:")
    user_api_key =  st.sidebar.text_input("Enter Your OPENAI API Key", type="password")
    openai.api_key = user_api_key

    if st.sidebar.button("Extract Data"):
        result = extract_data_from_webpage(webpage_url)

        if result:
            st.success("Data extraction successful!")
            # st.write(result)

            
            responses = main_format(result, webpage_url)
            st.write("Generated Responses:")
            st.write(responses)
            save_data_to_mysql(responses)
        else:
            st.error("Data extraction failed.")

if __name__ == '__main__':
    main()
