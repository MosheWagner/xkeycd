import os
import re
import time
import json
import string
import requests

from multiprocessing import Pool

from normalize_english import normalize_text


EXPLAIN_XKCD_COMIC_URL = "https://www.explainxkcd.com/wiki/index.php/{}"
XKCD = 'https://xkcd.com/{}'
CACHE_FOLDER = 'cache'
OUTPUT_FOLDER = os.path.join('..', 'site')
MIN_KW_LEN = 3


def get_last_xkcd_num():
    html = get_explained_comic_full(1)
    link_to_last = html.split('Latest comic')[0].split('<a href="/wiki/index.php/')[-1].split('"')[0]
    return int(link_to_last)
    

def get_explained_comic_full(comic_id):
    cache_file = os.path.join(CACHE_FOLDER, 'explained_{}.html'.format(comic_id))
    if not os.path.exists(cache_file):
        if not os.path.exists(CACHE_FOLDER):
            os.makedirs(CACHE_FOLDER)
            
        r = requests.get(EXPLAIN_XKCD_COMIC_URL.format(comic_id))
        if '503 Service Unavailable' in r.text:
            time.sleep(10)
            r = requests.get(EXPLAIN_XKCD_COMIC_URL.format(comic_id))
            
        with open(cache_file, 'w') as f:
            f.write(r.text)
            
    return open(cache_file, 'r').read()
    

def clean_char(c):
    if c in string.ascii_letters:
        return c
    if c in [',', '.', '?', '!', '-', '_', "'"]:
        return c
    return ' '
    
    
def strip_first(word):
    while len(word) > 0 and word[0] not in string.ascii_letters:
        word = word[1:]
    return word
    
    
def clean_text(text):
    cleaned_words = ''.join([clean_char(c) for c in text]).split()
    
    return ' '.join([strip_first(cw) for cw in cleaned_words])
    
    
def extract_section_text(html_text, section_name):
    try:
        text = html_text.split('id="{}"'.format(section_name))[1]
        text = text[text.find('>')+1:]
        text = text.split('id=')[0]
        text = text[:text.rfind('<'):]
        
        text = re.sub('<[^<]+?>', '', text) # strip tags
        
        text = text.replace(section_name, '')
        text = text.replace('[edit]', '')
        
        # Filter our non-printable chars:
        return clean_text(text)
    except IndexError:
        return ""
    
def get_xkcd_title(html_text):
    return clean_text(html_text.split('<title>')[1].split(':')[1].split(' - explain xkcd')[0])
    
    
def get_xkcd_tooltip(html_text):
    if 'Title text:</span>' in html_text:
        return clean_text(html_text.split('Title text:</span>')[1].split('</span>')[0])
    return ""
    
    
def parse_explained_comic_html(html_text):
    # We care only about 2 sections:
    #   Explanation
    #   Transcript ( with title and tooltip text(called title text for some reason))

    transcript_text = get_xkcd_title(html_text)
    transcript_text += " " + extract_section_text(html_text, "Transcript")
    transcript_text += " " + get_xkcd_tooltip(html_text)
    

    explanation_text = ""
    explanation_sec_names = ['Explanation', 'Explanations', 'Brief_Explanation', 'Longer_Explanation']
    for exp_sec_name in explanation_sec_names:
        explanation_text += " " + extract_section_text(html_text, exp_sec_name)
    
    assert explanation_text
    
    return explanation_text, transcript_text


def to_freq_dict(keyword_list):
    freq_dict = {}
    for w in keyword_list:
        if w not in freq_dict:
            freq_dict[w] = 0
        freq_dict[w] += 1
    return freq_dict  


def extract_keywords(text):
    return to_freq_dict([kw for kw in normalize_text(text) if len(kw) >= MIN_KW_LEN])


def extract_comic_keywords(explanation_text, transcript_text):
    return extract_keywords(explanation_text), extract_keywords(transcript_text)
    
    
def get_xkcd_keywords(comic_id):
    print('Getting keywords for ', comic_id)
    cache_file = os.path.join(CACHE_FOLDER, 'keywords_{}.json'.format(comic_id))
    if not os.path.exists(cache_file):
        explanation_kw, transcript_kw = extract_comic_keywords(*parse_explained_comic_html(get_explained_comic_full(comic_id)))
        res_json = {'explanation_keywords':explanation_kw, 'transcript_keywords':transcript_kw}
        
        with open(cache_file, 'w') as f:
            f.write(json.dumps(res_json))
            
    return open(cache_file, 'r').read()
    

def t_get_xkcd_keywords(comic_id):
    try:
        get_xkcd_keywords(comic_id)
    except Exception:
        for i in range(1):
            print('Exception while working on :', comic_id)


def get_all_keywords(multi_proc_mode = False):
    comic_ids = range(1, get_last_xkcd_num() + 1)
    
    if multi_proc_mode:
        p = Pool(8)
        p.map(t_get_xkcd_keywords, comic_ids)
    else:
        for i in comic_ids:
            get_xkcd_keywords(i)


def get_xkcd_page(comic_id):
    cache_file = os.path.join(CACHE_FOLDER, 'xkcd_{}.html'.format(comic_id))
    if not os.path.exists(cache_file):
        r = requests.get(XKCD.format(comic_id))
        with open(cache_file, 'w') as f:
            f.write(r.text)
            
    return open(cache_file, 'r').read()
    
    
def get_image_link(comic_id):
    if comic_id == 404:
        return 'https://www.explainxkcd.com/wiki/images/9/92/not_found.png' # :-)
    if comic_id == 1037:
        return 'https://www.explainxkcd.com/wiki/images/f/ff/umwelt_the_void.jpg' # :-)
    xkcd_page = get_xkcd_page(comic_id)
    comic_link = xkcd_page.split('Image URL (for hotlinking/embedding):')[1].split('</a>')[0].split('">')[1].strip()
    return comic_link


def t_get_image_link(comic_id):
    try:
        return get_image_link(comic_id)
    except Exception as e:
        print(repr(e), comic_id)
        

def get_all_comic_links(multi_proc_mode = False):
    json_path = os.path.join(OUTPUT_FOLDER, 'comics_meta.json')
    
    if os.path.exists(json_path):
        return 
        
    links = {}
    comic_ids = range(1, get_last_xkcd_num() + 1)
    
    if multi_proc_mode:
        p = Pool(8)
        p.map(t_get_image_link, comic_ids)
    else:
        for i in comic_ids:
            links[i] = {'image_link' : get_image_link(i)}
            explained_html_text = get_explained_comic_full(i)
            links[i]['title_text'] = get_xkcd_title(explained_html_text)
            links[i]['tooltip'] = get_xkcd_tooltip(explained_html_text)
            
        with open(json_path, 'w') as f:
            f.write(json.dumps(links))


def scrape_all(multi_proc_mode = False):
    print("Extracing XKCD image links")
    if multi_proc_mode:
        get_all_comic_links(True)
    get_all_comic_links(False)
    
    print("Scraping XKCD and ExplainXKCD, and extracting keywords")
    get_all_keywords(multi_proc_mode)

    
    
    
#if __name__ == "__main__":
#    scrape_all()
