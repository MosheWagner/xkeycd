import os
import re
import json
import string
import requests

from multiprocessing import Pool

from normalize_english import normalize_text


EXPLAIN_XKCD_COMIC_URL = "https://www.explainxkcd.com/wiki/index.php/{}"
XKCD = 'https://xkcd.com/{}'
CACHE_FOLDER = 'cache'
OUTPUT_FOLDER = '..'
MIN_KW_LEN = 3


def get_last_xkcd_num():
    html = get_explained_comic_full(1)
    link_to_last = html.split('Latest comic')[0].split('<a href="/wiki/index.php/')[-1].split('"')[0]
    return int(link_to_last)
    

def get_explained_comic_full(comic_id):
    cache_file = os.path.join(CACHE_FOLDER, 'explained_{}.html'.format(comic_id))
    if not os.path.exists(cache_file):
        r = requests.get(EXPLAIN_XKCD_COMIC_URL.format(comic_id))
        with open(cache_file, 'w') as f:
            f.write(r.content)
            
    return open(cache_file, 'r').read()
    

def clean_char(c):
    if c in string.ascii_letters:
        return c
    if c in [',', '.', '?', '!', '-', '_']:
        return c
    return ' '
    
    
def clean_text(text):
    return ''.join([clean_char(c) for c in text])
    
    
def extract_section_text(html_text, section_name):
    text = html_text.split('id="{}"'.format(section_name))[1]
    text = text[text.find('>')+1:]
    text = text.split('id=')[0]
    text = text[:text.rfind('<'):]
    
    text = re.sub('<[^<]+?>', '', text) # strip tags
    
    text = text.replace(section_name, '')
    text = text.replace('[edit]', '')
    
    # Filter our non-printable chars:
    
    return clean_text(text)
    
    
def parse_explained_comic_html(html_text):
    # We care only about 2 sections:
    #   Explanation
    #   Transcript ( with title and tooltip text(called title text for some reason))

    transcript_text = clean_text(html_text.split('<title>')[1].split(':')[1].split(' - explain xkcd')[0])
    try:
        transcript_text += " " + extract_section_text(html_text, "Transcript")
    except IndexError:
        pass
        
    if 'Title text:</span>' in html_text:
        transcript_text += " " + clean_text(html_text.split('Title text:</span>')[1].split('</span>')[0])
    

    explanation_text = ""
    explanation_sec_names = ['Explanation', 'Explanations', 'Brief_Explanation', 'Longer_Explanation']
    for exp_sec_name in explanation_sec_names:
        try:
            explanation_text += " " + extract_section_text(html_text, exp_sec_name)
        except IndexError:
            pass
    
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
    print 'Getting keywords for ', comic_id
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
            print 'Exception while working on :', comic_id


def get_all_keywords(multi_thread_mode = False):
    comic_ids = range(1, get_last_xkcd_num())
    
    if multi_thread_mode:
        p = Pool(16)
        p.map(t_get_xkcd_keywords, comic_ids)
    else:
        for i in comic_ids:
            get_xkcd_keywords(i)


def get_xkcd_page(comic_id):
    cache_file = os.path.join(CACHE_FOLDER, 'xkcd_{}.html'.format(comic_id))
    if not os.path.exists(cache_file):
        r = requests.get(XKCD.format(comic_id))
        with open(cache_file, 'w') as f:
            f.write(r.content)
            
    return open(cache_file, 'r').read()
    
    
def get_image_link(comic_id):
    if comic_id == 404:
        return 'https://www.explainxkcd.com/wiki/images/9/92/not_found.png' # :-)
    if comic_id == 1037:
        return 'https://www.explainxkcd.com/wiki/images/f/ff/umwelt_the_void.jpg' # :-)
    
    xkcd_page = get_xkcd_page(comic_id)
    comic_link = xkcd_page.split('Image URL (for hotlinking/embedding):')[1].split('\n')[0].strip()
    return comic_link


def t_get_image_link(comic_id):
    try:
        return get_image_link(comic_id)
    except Exception as e:
        print repr(e), comic_id
        

def get_all_comic_links(multi_thread_mode = False):
    json_path = os.path.join(OUTPUT_FOLDER, 'comic_images.json')
    
    if os.path.exists(json_path):
        return 
        
    links = {}
    comic_ids = range(1, get_last_xkcd_num())
    
    if multi_thread_mode:
        p = Pool(16)
        p.map(t_get_image_link, comic_ids)
    else:
        for i in comic_ids:
            links[i] = get_image_link(i)
            print i, links[i]
            
        with open(json_path, 'w') as f:
            f.write(json.dumps(links))


def scrape_all():
    
    # Get everything into our donwload cache, then run nicely so that the final data is nice
    print "Extracing XKCD image links"
    get_all_comic_links(True)
    get_all_comic_links(False)
    print "Scraping XKCD and ExplainXKCD, and extracting keywords"
    get_all_keywords(True)
    get_all_keywords(False)
    
    
    
#if __name__ == "__main__":
#    scrape_all()
