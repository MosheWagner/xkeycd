import os
import sys
import json

OUTPUT_FOLDER = '..'

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
    score_path = os.path.join(OUTPUT_FOLDER, 'scores.json')
    
    if not os.path.exists(score_path):
        from scrape import scrape_all
        from keyword_score import create_score_index
        scrape_all()
        create_score_index()
    
    keywords = sys.argv[1:]
    
    kw_score_index = json.loads(open(score_path, 'r').read())
    
    res = find_by_keywords(keywords, kw_score_index)
    print res


if __name__ == '__main__':
    main()