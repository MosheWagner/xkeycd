import os
import re
import json
import string
import requests

from multiprocessing import Pool

from normalize_english import normalize_text


EXPLAIN_XKCD_COMIC_URL = "https://www.explainxkcd.com/wiki/index.php/{}"
XKCD = 'https://xkcd.com/{}'
OUTPUT_FOLDER = 'cache'
MIN_KW_LEN = 3


def get_last_xkcd_num():
    html = get_explained_comic_full(1)
    link_to_last = html.split('Latest comic')[0].split('<a href="/wiki/index.php/')[-1].split('"')[0]
    return int(link_to_last)
    

def get_explained_comic_full(comic_id):
    cache_file = os.path.join(OUTPUT_FOLDER, 'explained_{}.html'.format(comic_id))
    if not os.path.exists(cache_file):
        r = requests.get(EXPLAIN_XKCD_COMIC_URL.format(comic_id))
        with open(cache_file, 'w') as f:
            f.write(r.content)
            
    return open(cache_file, 'r').read()
    
    
def extract_section_text(html_text, section_name):
    text = html_text.split('id="{}"'.format(section_name))[1]
    text = text[text.find('>')+1:]
    text = text.split('id=')[0]
    text = text[:text.rfind('<'):]
    
    text = re.sub('<[^<]+?>', '', text) # strip tags
    
    text = text.replace(section_name, '')
    text = text.replace('[edit]', '')
    
    # Filter our non-printable chars:
    
    return ''.join([t for t in text if t in string.printable])
    
    
def parse_explained_comic_html(html_text):
    # We care only about 2 sections:
    #   Explanation
    #   Transcript ( + the title text)

    explanation_text = ""
    explanation_sec_names = ['Explanation', 'Explanations', 'Brief_Explanation', 'Longer_Explanation']
    for exp_sec_name in explanation_sec_names:
        try:
            explanation_text += " " + extract_section_text(html_text, exp_sec_name)
        except IndexError:
            pass
    
    assert explanation_text
    
    try:
        transcript_text = extract_section_text(html_text, "Transcript")
    except IndexError:
        transcript_text = ""
        
    if 'Title text:</span>' in html_text:
        transcript_text += " " + ''.join([t for t in html_text.split('Title text:</span>')[1].split('</span>')[0] if t in string.printable])
    
    #print "Tanscript: ", transcript_text
    #print "explanation_text: ", explanation_text
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
    cache_file = os.path.join(OUTPUT_FOLDER, 'keywords_{}.json'.format(comic_id))
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

def get_all_keywords():
    comics = range(1, get_last_xkcd_num())
    
    for i in comics:
        get_xkcd_keywords(i)

    #p = Pool(16)
    #p.map(t_get_xkcd_keywords, comics)


def get_xkcd_page(comic_id):
    cache_file = os.path.join(OUTPUT_FOLDER, 'xkcd_{}.html'.format(comic_id))
    if not os.path.exists(cache_file):
        r = requests.get(XKCD.format(comic_id))
        with open(cache_file, 'w') as f:
            f.write(r.content)
            
    return open(cache_file, 'r').read()
    
    
def get_image_link(comic_id):
    xkcd_page = get_xkcd_page(comic_id)
    comic_link = xkcd_page.split('Image URL (for hotlinking/embedding):')[1].split('\n')[0].strip()
    # print comic_link
    return comic_link

def t_get_image_link(comic_id):
    try:
        return get_image_link(comic_id)
    except Exception as e:
        print repr(e), comic_id
        
        

def get_all_comic_links():
    links = {}
    comic_ids = range(1, get_last_xkcd_num())
    
    #p = Pool(16)
    #p.map(t_get_image_link, comic_ids)
    
    for i in comic_ids:
        links[i] = t_get_image_link(i)
        print i, links[i]
        
    with open(os.path.join(OUTPUT_FOLDER, 'comic_images.json'), 'w') as f:
        f.write(json.dumps(links))

if __name__ == "__main__":
    get_all_comic_links()
    # get_all_keywords()
