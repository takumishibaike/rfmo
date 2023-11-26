# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 25, 2023
##### Revision: V1.0
##### File : seeded_lda.py

import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import spacy
import nltk
import numpy as np

# Download WordNet data
nltk.download('wordnet')

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\wcpfc')


# Load the CSV file
csv_file_path = '.\\analysis\\WCPFC.csv'
df = pd.read_csv(csv_file_path)
text_data = df['Content']

# Check duplicates
# duplicate_rows = df[df.duplicated('Content')]
# print("Duplicate Rows based on 'Content':")
# print(duplicate_rows)

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Lemmatize the documents
documents_lemmatized = [' '.join([token.lemma_ for token in nlp(doc)]) for doc in text_data]

# Convert text to a bag of words representation
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(documents_lemmatized)

# Set a seed for LDA
lda_seed = 123

# Set seed words for each topic
topic_seed_words = [
    ['vessel', 'fleet'],
    ['science','advice'],
    ['meeting', 'chair', 'committee']
    # Add more seed words for each topic
]

# Initialize the LDA model with seed words
lda = LatentDirichletAllocation(n_components=3, random_state=lda_seed)
lda.components_ = np.zeros((3, X.shape[1]))

# Assign the seed words to the corresponding topics
for topic_idx, words in enumerate(topic_seed_words):
    for word in words:
        word = nlp(word)[0].lemma_
        word_idx = vectorizer.vocabulary_.get(word)
        if word_idx is not None:
            lda.components_[topic_idx, word_idx] = 1.0

# Fit the LDA model
lda.fit(X)

# Print the topics and associated words, including seeded words
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    print(f"Topic #{topic_idx + 1} (Seeded Words: {', '.join(topic_seed_words[topic_idx])}):")
    
    # Extract the top words from the topic
    top_words_idx = topic.argsort()[:-10 - 1:-1]
    top_words = [feature_names[i] for i in top_words_idx]
    
    # Include seeded words in the top words
    top_words_with_seeds = set(top_words).union(set(topic_seed_words[topic_idx]))
    
    print(" ".join(top_words_with_seeds))
    print()

# Transform documents to topic probabilities
doc_topic_probs = lda.transform(X)
print("Document-Topic Probabilities:")
print(doc_topic_probs)



# Save the DataFrame with topic labels to a new CSV file
# df.to_csv('analysis\\output_with_labels.csv', index=False)


