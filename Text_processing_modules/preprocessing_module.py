"""
Requires: NLTK (install with pip install nltk), spaCy (pip install spacy)
         and the appropriate spaCy model (e.g. python -m spacy download es_core_news_sm)
"""

import os
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import spacy
from spacy.cli.download import download

def load_stopwords(lang='english', file_path=None):
    """
    Carga stopwords. 
    Si `file_path` está dado, usa ese archivo.
    Si no, intenta cargar automáticamente según lang.
    """
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(w.strip() for w in f if w.strip())
    
    # Path automático por idioma
    default_files = {
        'spanish': 'stoplist_spanish.txt',
        'english': 'stoplist_english.txt'
    }
    default_file = default_files.get(lang)
    
    if default_file and os.path.exists(default_file):
        with open(default_file, 'r', encoding='utf-8') as f:
            return set(w.strip() for w in f if w.strip())
    
    # Fallback a nltk si no hay archivo local
    try:
        return set(stopwords.words(lang))
    except LookupError:
        nltk.download('stopwords')
        return set(stopwords.words(lang))


def preprocess(text, stopwords_path=None, lang='english'):
    text = text.lower()

    # Choose language resources
    if lang not in ['spanish', 'english']:
        lang = 'english'
    model_name = 'es_core_news_sm' if lang == 'spanish' else 'en_core_web_sm'

    # Tokenize
    try:
        tokens = word_tokenize(text, language=lang)
    except LookupError:
        nltk.download('punkt')
        tokens = word_tokenize(text, language=lang)

    # Remove stopwords and non-alpha
    stop_words = load_stopwords(lang, stopwords_path)
    filtered = [t for t in tokens if t.isalpha() and t not in stop_words]

    # Stemming
    stemmer = SnowballStemmer(lang)
    stems = [stemmer.stem(t) for t in filtered]

    # Lemmatization (spaCy required)
    try:
        nlp = spacy.load(model_name)
    except OSError:
        from spacy.cli.download import download
        download(model_name)
        nlp = spacy.load(model_name)
    doc = nlp(' '.join(filtered))
    lemmas = [token.lemma_ for token in doc if token.lemma_]

    # Union de lemmas y stems
    tokens_final = lemmas + stems

    # Bag of words: conteo de cada término normalizado
    bow = {}
    for token in tokens_final:
        bow[token] = bow.get(token, 0) + 1
    return bow

def preprocess_batch(texts, stopwords_path=None, lang='english'):
    texts = [text.lower() for text in texts]  
    
    # Cargar modelo una vez
    model_name = 'es_core_news_sm' if lang == 'spanish' else 'en_core_web_sm'
    try:
        nlp = spacy.load(model_name, disable=['parser', 'ner'])
    except OSError:
        download(model_name)
        nlp = spacy.load(model_name, disable=['parser', 'ner'])
    
    # Load stopwords once
    stop_set = load_stopwords(lang, stopwords_path)
    stemmer = SnowballStemmer(lang)  # Create stemmer once
    
    # Process all texts in batches
    docs = nlp.pipe(texts, batch_size=50)
    all_bows = []
    
    for doc in docs:
        tokens = []
        lemmas = []
        for token in doc:
            if token.is_alpha and token.text not in stop_set:
                tokens.append(token.text)
                lemmas.append(token.lemma_)
        
        stems = [stemmer.stem(t) for t in tokens]  # Batch stemming
        tokens_final = lemmas + stems
        
        # Create BoW
        bow = {}
        for token in tokens_final:
            bow[token] = bow.get(token, 0) + 1
        all_bows.append(bow)
    
    return all_bows