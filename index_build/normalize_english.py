from textblob import TextBlob
from textblob import wordnet


ignore_tags = {
    'TO',  # to
    'DT',  # determiner
    'IN',  # preposition/subordinating conjunction 
    'WDT', # wh-determiner which
    'WP ', # wh-pronoun who, what
    'WP$', # possessive wh-pronoun whose
    'WRB', # wh-abverb where, when
    'CC',  # coordinating conjunction
    'POS', # possessive ending parent's
}


def detailed_POS_to_simple_POS(wordnet_pos):
    if wordnet_pos.startswith('N'):
        return wordnet.NOUN
    
    if wordnet_pos.startswith('J'):
        # return wordnet.ADJ    
        return wordnet.VERB
    
    if wordnet_pos.startswith('V'):
        return wordnet.VERB

    if wordnet_pos.startswith('RB'):
        return wordnet.ADV   
        
    return None


def _lemmatize_word(word, pos_tag = 'n', use_verb_if_shorter = True):
    if pos_tag in ignore_tags:
        return None
            
    pos = detailed_POS_to_simple_POS(pos_tag)
    
    if pos:
        lemmatized = word.lemmatize(pos)
        if use_verb_if_shorter and pos != 'v':
            verb_lemmatized = word.lemmatize('v')

            if lemmatized != verb_lemmatized:
                if len(verb_lemmatized) < len(lemmatized):
                    return verb_lemmatized
                    
        return lemmatized.lower()


def _lemmatize_blob(blob_text):
    tb = TextBlob(blob_text)
    lemmatized = []
    
    for w,t in tb.tags:
        l = _lemmatize_word(w,t)
        if l:
            lemmatized.append(l)
    
    return lemmatized


def normalize_word(w):
    return _lemmatize_word(w)

def normalize_text(text):
    return _lemmatize_blob(text)
