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
import re
import matplotlib.pyplot as plt

# Download WordNet data
nltk.download('wordnet')

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\wcpfc')

# Load the CSV file
csv_file_path = '.\\analysis\\wcpfc.csv'
df = pd.read_csv(csv_file_path)

# Remove rows with empty text
df = df[df['content'].str.strip() != '']

# Check duplicates
# duplicate_rows = df[df.duplicated('Content')]
# print("Duplicate Rows based on 'Content':")
# print(duplicate_rows)

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Check the data type of each element in 'text_data'
for i, doc in enumerate(df['content']):
    if not isinstance(doc, str):
        print(f"Document at index {i} is of type {type(doc)}. Converting to string.")
        df.at[i, 'content'] = str(doc)

# Lemmatize the documents
df['content_lemmatized'] = [' '.join([token.lemma_ for token in nlp(doc)]) for doc in df['content']]
df['content_lemmatized'] = [re.sub(r'[,.;:\-]', '', doc) for doc in df['content_lemmatized']]
df['content_lemmatized'] = [' '.join(doc.split()) for doc in df['content_lemmatized']]

# Convert text to a bag of words representation
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['content_lemmatized'])

# Set a seed for LDA
lda_seed = 123

# Set seed words for each topic along with labels
topic_seed_words = [
    {'words': ['reference', 'control', 'MSE'], 'label': 'Harvest Strategy'},
    {'words': ['bycatch', 'shark', 'turtle'], 'label': 'Bycatch'},
    {'words': ['transparency', 'transshipment', 'IUU'], 'label': 'Fleet Transparency'}
    # Add more seed words for each topic along with labels
]

# Add a residual category for words not in the seed words
all_words = set(vectorizer.get_feature_names_out())
seed_words = set(word for words in topic_seed_words for word in words)
residual_words = list(all_words - seed_words)

# Add a residual topic with some weight
num_topics = len(topic_seed_words) + 1  # Including the residual category

# Initialize the LDA model with seed words
lda = LatentDirichletAllocation(n_components=num_topics, random_state=lda_seed)
lda.fit(X)

# Fit the LDA model
df['topic_distribution'] = lda.transform(X).argmax(axis=1)


# Attach topic labels to the original DataFrame
topic_labels = []
for idx, row in df.iterrows():
    doc_topics = lda.transform(vectorizer.transform([row['content_lemmatized']])).argmax(axis=1)
    if doc_topics[0] < len(topic_seed_words):
        label = topic_seed_words[doc_topics[0]]['label']
    else:
        label = 'Residual'
    topic_labels.append(label)

df['topic_label'] = topic_labels

# Save the DataFrame with topic labels as a CSV file
columns_to_save = ['document', 'number', 'content', 'content_lemmatized', 'topic_label']
df[columns_to_save].to_csv('.\\analysis\\letters_with_labels.csv', index=False)

# Print the topics and associated words, including seeded words and labels
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    # Ensure the topic index is within the range of topic_seed_words
    if topic_idx < len(topic_seed_words):
        label = topic_seed_words[topic_idx]['label']
        print(f"Topic #{topic_idx} ({label}):")
    else:
        print(f"Residual Topic:")

    # Extract the top words from the topic
    top_words_idx = topic.argsort()[:-10 - 1:-1]
    top_words = [feature_names[i] for i in top_words_idx]

    # Include seeded words in the top words
    if topic_idx < len(topic_seed_words):
        top_words_with_seeds = set(top_words).union(set(topic_seed_words[topic_idx]['words']))
    else:
        top_words_with_seeds = set(top_words)

    print(" ".join(top_words_with_seeds))
    print()

# Calculate topic distribution by document
topic_distribution_by_meeting = df.groupby('document')['topic_distribution'].value_counts(normalize=True).unstack()
print("Topic Distribution by Meeting:")

for meeting, ratios in topic_distribution_by_meeting.iterrows():
    print(f"\n{meeting}:")
    for topic_idx, topic_info in enumerate(topic_seed_words):
        label = topic_info['label']
        ratio = ratios.get(topic_idx, 0)
        print(f"  {label}: {ratio:.2%}")


# Calculate the total topic distribution
total_topic_distribution = df['topic_distribution'].value_counts(normalize=True).sort_index()
print("Total Topic Distribution:")
for topic_idx, topic_info in enumerate(topic_seed_words):
    label = topic_info['label']
    ratio = total_topic_distribution[topic_idx]
    print(f"{label}: {ratio:.2%}")


# Calculate topic distribution by meeting for chart
topic_distribution_by_meeting = df.groupby(['document', 'topic_label']).size().unstack(fill_value=0)
topic_distribution_by_meeting_percentage = topic_distribution_by_meeting.div(topic_distribution_by_meeting.sum(axis=1), axis=0) * 100

# Plot 100% stacked bar chart
fig, ax = plt.subplots(figsize=(10, 6))
topic_distribution_by_meeting_percentage.plot(kind='bar', stacked=True, ax=ax)

# Add labels and legend
ax.set_ylabel('Percentage')
ax.set_xlabel('Meeting')
ax.set_title('Topic Distribution by Meeting')
ax.legend(title='Topic', bbox_to_anchor=(1, 1))

# Save the figure as PNG with specified dimensions
plt.savefig('topic_distribution_chart.png', dpi=300, bbox_inches='tight')  # Adjust the file name and DPI as needed

# Show the plot
plt.show()