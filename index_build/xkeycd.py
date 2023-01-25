import os
import sys
import json
import glob
import argparse

CACHE_FOLDER = 'cache'
OUTPUT_FOLDER = os.path.join('..', 'site')


MAX_RES = 10

TRANSCRIPT_FACTOR = 3
EXPLANATION_FACTOR = 1


def try_del(file_path):
    try:
        os.remove(file_path)
    except (OSError, AssertionError) as e:
        assert 'The system cannot find the file' in repr(e) or 'No such file' in repr(e), 'Error removing file {} - {}'.format(file_path, repr(e))
    

def find_by_keywords(keywords, kw_score_index, num_res = MAX_RES):
    comic_scores = {}
    for kw in keywords:
        if kw not in kw_score_index:
            continue
            
        for comic_id, scores in kw_score_index[kw].items():
            if comic_id not in comic_scores:
                comic_scores[comic_id] = 0
            comic_scores[comic_id] += TRANSCRIPT_FACTOR * scores.get('transcript_score', 0) + EXPLANATION_FACTOR * scores.get('explanation_score', 0)

    return sorted(comic_scores.items(), key=lambda x: x[1])[-num_res : ][::-1]


def main():
    parser = argparse.ArgumentParser(description='Search XCKD by keywords')
    
    parser.add_argument('--keywords', '-k', metavar='k', nargs='+', help='keywords to search by')
    parser.add_argument('--rebuild', dest='rebuild', help='Rebuild the search index from scratch', action="store_true", default=False)
    parser.add_argument('--update', dest='update', help='Update the search index to include the new comics', action="store_true", default=False)
    parser.add_argument('--multi', dest='multi', help='Rebuild/Update the index with multiprocessing', action="store_true", default=False)

    args = parser.parse_args()

    if args.rebuild:
        keyword_jsons = glob.glob(os.path.join(CACHE_FOLDER, '*.json'))
        for f in keyword_jsons:
            try_del(f)
            
    if args.update or args.rebuild:
        try_del(os.path.join(OUTPUT_FOLDER, 'scores.json'))
        try_del(os.path.join(OUTPUT_FOLDER, 'comics_meta.json'))
        try_del(os.path.join(CACHE_FOLDER, 'explained_1.html')) # This one is used to get the comic count :-)
        
        from scrape import scrape_all
        from keyword_score import create_score_index
        scrape_all(args.multi)
        create_score_index()
        
    score_path = os.path.join(OUTPUT_FOLDER, 'scores.json')
    
    if not os.path.exists(score_path):
        raise Exception("Can't find keyword scores index file!")

    keywords = args.keywords
    if keywords:
        kw_score_index = json.loads(open(score_path, 'r').read())
        
        res = find_by_keywords(keywords, kw_score_index)


if __name__ == '__main__':
    main()