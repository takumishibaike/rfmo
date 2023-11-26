# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.0
##### File : lda.py

import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\wcpfc')

# Load the CSV file
csv_file_path = 'WCPFC.csv'
df = pd.read_csv(csv_file_path)
text_data = df['Content']

# Preprocess the text data using CountVectorizer
vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
X = vectorizer.fit_transform(text_data)

# Define the range of topics to search
param_grid = {'n_components': range(5, 16)}

# Initialize an empty dictionary to store the top words for each n_components
top_words_per_topic = {}

# Perform GridSearch to find the best number of topics
lda = LatentDirichletAllocation(random_state=42)
grid_search = GridSearchCV(lda, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X)

# Get the best model
best_lda_model = grid_search.best_estimator_

# Display the best parameters and corresponding score
print("Best Parameters: ", grid_search.best_params_)
print("Best Log Likelihood Score: ", grid_search.best_score_)

# Print the top words for each topic in the best model
feature_names = vectorizer.get_feature_names_out()
print("\nTop words for the best-fit model:")
for topic_idx, topic in enumerate(best_lda_model.components_):
    top_words_idx = topic.argsort()[:-10 - 1:-1]  # Display top 10 words for each topic
    top_words = [feature_names[i] for i in top_words_idx]
    print(f"Topic #{topic_idx + 1}: {', '.join(top_words)}")

# After finding the best model, iterate through each value of n_components and print the associated words for each topic
for n_components in param_grid['n_components']:
    lda = LatentDirichletAllocation(n_components=n_components, random_state=42)
    lda.fit(X)
    
    # Get the top words for each topic
    feature_names = vectorizer.get_feature_names_out()
    top_words_per_topic[n_components] = [
        [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]] for topic in lda.components_
    ]

    # Display the top words for each topic
    print(f"\nTop words for {n_components} topics:")
    for topic_idx, top_words in enumerate(top_words_per_topic[n_components]):
        print(f"Topic #{topic_idx + 1}: {', '.join(top_words)}")

# Specify your preferred LDA model with a specific number of topics
num_topics = 5  # Change this to the number of topics in your preferred model
preferred_lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
preferred_lda_model.fit(X)

# Assign topics to documents based on the preferred model
topic_assignments = preferred_lda_model.transform(X)

# Add a new column to the DataFrame to store the assigned topic for each document
df['Assigned_Topic'] = topic_assignments.argmax(axis=1)

# Save the DataFrame with assigned topics to a new CSV file
output_csv_path = 'lda_output.csv'
df.to_csv(output_csv_path, index=False)
