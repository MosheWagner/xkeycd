import os
import json

GLOBAL_FREQ_DECAY_FACTOR = 2
LOCAL_FREQ_EXP_FACTOR = 3

OUTPUT_FOLDER = 'cache'

# Sum all word_freqs
# Word score = word_count_in_comic / word_count_total (so uniqe words have a higher score)
# Build reverse index - keyword: (comic, exp_score, trans_score)
# 

def get_comic_count():
    return 2177 # TODO: Fix this


def load_freq_dicts():
    d = {}
    keyword_files = [(int(f.split('_')[1].split('.')[0]), os.path.join(OUTPUT_FOLDER, f)) for f in os.listdir(OUTPUT_FOLDER) if 'keywords_' in f and f.endswith('.json')]
    for i, f in keyword_files:
        d[i] = json.loads(open(f, 'r').read())
    
    return d    


def sum_global_word_freq(comic_keyword_dicts):
    freq_dict = {}
    
    for comic_id, keywords in comic_keyword_dicts.iteritems():
        exp_kw = keywords['explanation_keywords']
        trans_kw = keywords['transcript_keywords']
        
        for kw, count in exp_kw.iteritems():
            if kw not in freq_dict:
                freq_dict[kw] = 0
            freq_dict[kw] += count

        for kw, count in trans_kw.iteritems():
            if kw not in freq_dict:
                freq_dict[kw] = 0
            freq_dict[kw] += count
            
    return freq_dict
    

def get_word_score(local_word_freq, global_word_freq):
    return (float(local_word_freq) ** LOCAL_FREQ_EXP_FACTOR) / (float(global_word_freq) ** GLOBAL_FREQ_DECAY_FACTOR)


def build_reverse_index(comic_keyword_dicts, global_freq_dict):
    keyword_dict = {}

    for comic_id, keywords in comic_keyword_dicts.iteritems():
        exp_kw = keywords['explanation_keywords']
        trans_kw = keywords['transcript_keywords']
        
        for kw, count in exp_kw.iteritems():
            if kw not in keyword_dict:
                keyword_dict[kw] = {}
            if comic_id not in keyword_dict[kw]:
                keyword_dict[kw][comic_id] = {}
            if 'explanation_score' not in keyword_dict[kw][comic_id]:
                keyword_dict[kw][comic_id]['explanation_score'] = 0
                
            keyword_dict[kw][comic_id]['explanation_score'] = get_word_score(count, global_freq_dict[kw])
            
        for kw, count in trans_kw.iteritems():
            if kw not in keyword_dict:
                keyword_dict[kw] = {}
            if comic_id not in keyword_dict[kw]:
                keyword_dict[kw][comic_id] = {}
            if 'transcript_score' not in keyword_dict[kw][comic_id]:
                keyword_dict[kw][comic_id]['transcript_score'] = 0
                
            keyword_dict[kw][comic_id]['transcript_score'] = get_word_score(count, global_freq_dict[kw])    
            
    return keyword_dict
    
    
def build_score_index():
    comic_keyword_dicts = load_freq_dicts()
    global_freq_dict = sum_global_word_freq(comic_keyword_dicts)
    return build_reverse_index(comic_keyword_dicts, global_freq_dict)
    

    
if __name__ == "__main__":
    scores = build_score_index()
    with open(os.path.join(OUTPUT_FOLDER, 'scores.json'), 'w') as f:
        f.write(json.dumps(scores))
        
    
