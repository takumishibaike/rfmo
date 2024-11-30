# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.4
##### File : bert_topic_cmm.py

import pandas as pd
import re
import nltk
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import os

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\cmm')
os.environ["OMP_NUM_THREADS"] = "10"

# Load data
file_path = '.\\analysis\\cmm_wcpfc.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Extract text content
nltk.download('stopwords')

def clean_text(text):
    # Lowercase text
    text = text.lower()
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove special characters and digits
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # List of custom words to remove
    custom_words_to_remove = set(['shall', 'measure', 'measures'])
    
    # Combine stopwords and custom words to remove
    words_to_remove = custom_words_to_remove
    
    # Filter words: remove stopwords and custom words
    text = ' '.join([word for word in text.split() if word not in words_to_remove])
    
    return text

data['cleaned_content'] = data['content'].apply(clean_text)
texts = data['cleaned_content'].dropna().tolist()

# Configure BERTopic with trigram support
vectorizer = CountVectorizer(ngram_range=(1, 3), stop_words='english')  # 1-3 grams for more flexibility
topic_model = BERTopic(vectorizer_model=vectorizer, verbose=True)

# Fit BERTopic and transform texts
original_topics, probs = topic_model.fit_transform(texts)

# Save the original topic labels to the DataFrame
data['original_topic'] = original_topics

# Get the original topic information
original_topics_info = topic_model.get_topic_info()

# Save the original topics info to a CSV
original_topics_file_path = '.\\analysis\\bertopic_original_topics_info.csv'
original_topics_info.to_csv(original_topics_file_path, index=False)

# Reduce the number of topics (e.g., to 10 topics)
reduced_topic_model = topic_model.reduce_topics(texts, nr_topics=20)

# Get the reduced topic labels and assign them back to the data
reduced_topics = reduced_topic_model.transform(texts)[0]
data['reduced_topic'] = reduced_topics

# Get the reduced topic information
reduced_topics_info = reduced_topic_model.get_topic_info()

# Save the reduced topics info to a CSV
reduced_topics_file_path = '.\\analysis\\bertopic_reduced_topics_info.csv'
reduced_topics_info.to_csv(reduced_topics_file_path, index=False)

# Save the DataFrame with both original and reduced topic labels
output_file_path = '.\\analysis\\cmm_wcpfc_with_bertopic_topics.csv'
data.to_csv(output_file_path, index=False)

print(f"Original topic information saved to {original_topics_file_path}")
print(f"Reduced topic information saved to {reduced_topics_file_path}")
print(f"Processed data saved to {output_file_path}")

from IPython.display import display
fig = topic_model.visualize_barchart(top_n_topics=10)  # Replace with your `topic_model`
plot(fig)
