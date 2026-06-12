# mon_preprocessing.py
import random
import re
import pandas as pd
import spacy
import numpy as np

# Configuration de votre graine aléatoire et spaCy d'origine
random.seed(42)
NLP_MODEL = "en_core_web_sm"
try:
    nlp = spacy.load(NLP_MODEL)
except OSError:
    import spacy.cli
    spacy.cli.download(NLP_MODEL)

def ner_anonymization(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    doc = nlp(text)
    target_labels = {'PERSON', 'ORG', 'GPE'}
    entities = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
    text_chars = list(text)
    for ent in entities:
        if ent.label_ in target_labels:
            text_chars[ent.start_char:ent.end_char] = list(ent.label_)
    return "".join(text_chars)

def compress_sentence_loops(text):
    if not text: return ""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences: return text
    cleaned, i = [], 0
    while i < len(sentences):
        found_loop = False
        for size in range(1, 5):
            if i + size * 2 <= len(sentences):
                if sentences[i:i+size] == sentences[i+size:i+size*2]:
                    count = 2
                    while i + size * (count + 1) <= len(sentences):
                        if sentences[i+size*count : i+size*(count+1)] == sentences[i:i+size]: count += 1
                        else: break
                    cleaned.extend(sentences[i:i+size])
                    i += size * count
                    found_loop = True
                    break
        if not found_loop:
            cleaned.append(sentences[i])
            i += 1
    return " ".join(cleaned)

def compress_word_loops(text):
    words = text.split()
    if not words: return text
    cleaned, i = [], 0
    while i < len(words):
        found_loop = False
        for size in range(1, 5):
            if i + size * 2 <= len(words):
                if words[i:i+size] == words[i+size:i+size*2]:
                    count = 2
                    while i + size * (count + 1) <= len(words):
                        if words[i+size*count : i+size*(count+1)] == words[i:i+size]: count += 1
                        else: break
                    cleaned.extend(words[i:i+size])
                    i += size * count
                    found_loop = True
                    break
        if not found_loop:
            cleaned.append(words[i])
            i += 1
    return " ".join(cleaned)

def clean_text_unified(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    text = ner_anonymization(text)
    text = text.replace("\\n", " ").replace("\n", " ").replace("\r", " ")
    text = re.sub(r"[‘’'’`´]", "'", text)
    text = re.sub(r'[“”""«»]', "'", text)
    text = compress_sentence_loops(text)
    text = compress_word_loops(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def pipeline_clean_transformer(X):
    """Fonction passerelle requise par scikit-learn pour le format d'entrée."""
    if isinstance(X, pd.DataFrame):
        col = 'text' if 'text' in X.columns else X.columns
        return pd.DataFrame(X[col].astype(str).apply(clean_text_unified))
    elif isinstance(X, pd.Series):
        return pd.Series(X.astype(str).apply(clean_text_unified))
    else:
        return np.array([clean_text_unified(str(item)) for item in X])
