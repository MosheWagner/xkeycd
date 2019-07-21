import os
import sys
import json

OUTPUT_FOLDER = 'cache'

MAX_RES = 10

TRANSCRIPT_FACTOR = 3
EXPLANATION_FACTOR = 1


def find_by_keywords(keywords, kw_score_index, num_res = MAX_RES):
    comic_scores = {}
    for kw in keywords:
        if kw not in kw_score_index:
            continue
            
        for comic_id, scores in kw_score_index[kw].iteritems():
            if comic_id not in comic_scores:
                comic_scores[comic_id] = 0
            comic_scores[comic_id] += TRANSCRIPT_FACTOR * scores.get('transcript_score', 0) + EXPLANATION_FACTOR * scores.get('explanation_score', 0)

    return sorted(comic_scores.items(), key=lambda x: x[1])[-num_res : ][::-1]


def main():
    keywords = sys.argv[1:]
    
    kw_score_index = json.loads(open(os.path.join(OUTPUT_FOLDER, 'scores.json'), 'r').read())
    
    res = find_by_keywords(keywords, kw_score_index)
    print res
    



if __name__ == '__main__':
    main()