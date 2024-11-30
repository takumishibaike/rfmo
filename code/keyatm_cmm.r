library(readxl)
library(dplyr)
library(quanteda)
library(keyATM)
library(stringr)
library(ggplot2)
library(tidyr)

setwd("C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\cmm")
rm(list = ls()) 

# Load the data
df <- read.csv(".\\analysis\\cmm_wcpfc.csv", header = TRUE)

# Extract the year from the CMM column
df <- df %>%
  mutate(Year = as.numeric(sub("^(\\d{4}).*", "\\1", document)))

# Aggregate the number of sections per year
sections_per_year <- df %>%
  group_by(Year) %>%
  summarize(Section_Count = n()) %>%
  arrange(Year)

# Plot the data
p <- ggplot(sections_per_year, aes(x = Year, y = Section_Count)) +
  geom_bar(stat = "identity", fill = "gray60", color = "black") +
  theme_minimal(base_size = 14) +
  theme(panel.grid.minor = element_blank(),
        axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(x = "Year", y = "Number of Items in CMMs")

print(p)

# Count the number of unique CMMs adopted each year

cmm_count_per_year <- df %>%
  group_by(Year) %>%
  summarize(CMM_Count = n_distinct(document)) %>%
  arrange(Year)

p <- ggplot(cmm_count_per_year, aes(x = Year, y = CMM_Count)) +
  geom_bar(stat = "identity", fill = "gray60", color = "black") +
  theme_minimal(base_size = 14) +
  theme(panel.grid.minor = element_blank(),
        axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(x = "Year", y = "Number of CMMs")

print(p)

# Filter for specific documents and preprocess text
df <- df %>%
  mutate(
    content = tolower(content),                             # Convert to lowercase
    content = str_replace_all(content, "[[:punct:]]", " "), # Remove punctuation
    content = str_replace_all(content, "\\b\\d+\\b", " "),  # Remove numeric values
    content = str_remove_all(content, "\\b(?:the|and|or|but|with|to|from|for|of|in|on|at|by|as|an|a|shall|this|that|its|their)\\b"), # Remove common stopwords
    content = str_remove_all(content, "\\b(?:shall|that|this|its|their|cmm|cmms)\\b"), # Remove common stopwords
    content = str_squish(content)                           # Remove extra whitespace
  )

# Tokenize and preprocess
corp <- df$content
toks <- tokens(corp, remove_punct = TRUE, remove_symbols = TRUE, remove_numbers = TRUE) %>%
  tokens_select(min_nchar = 3)

# Construct a document-feature matrix
data_dfm <- dfm(toks) %>%
  dfm_trim(min_termfreq = 5, min_docfreq = 2)
ncol(data_dfm)  # the number of unique words

# Create a document-object for keyATM
doc <- keyATM_read(texts = data_dfm)
summary(doc) # Warning shows if there is a content with 0 word


# Define keywords
keywords <- list(
  strategy = c('mse', 'hcr', 'trp', 'strategy', 'limit', 'target', 'control', 'harvest', 'capacity', 'mortality', 'overcapacity'),
  bycatch = c('bycatch', 'shark', 'turtle', 'seabird', 'mammal', 'juvenile', 'billfish', 'longline', 'fads', 'retention'),
  transparency = c('vms', 'iuu', 'ais', 'cds', 'transparency','unreported'),
  equity = c('rights', 'small', 'island', 'sids', 'allocation', 'developing','burden','ffa')
)

# Check the frequency of keywords
key_viz <- visualize_keywords(docs = doc, keywords = keywords)
key_viz

# Run keyATM model
out <- keyATM(
  docs              = doc,    # text input
  no_keyword_topics = 1,              # number of topics without keywords
  keywords          = keywords,       # keywords
  model             = "base",         # select the model
  options           = list(seed = 1234)
)

saveRDS(out, file = "SAVENAME.rds")
out <- readRDS(file = "SAVENAME.rds")

top_words(out)
plot_topicprop(out, show_topic = 1:5)

# Extract topic terms and proportions
topic_terms <- keyATM_keywords(keyATM_result)
topic_proportions <- keyATM_topic_proportion(keyATM_result)

# Add topics back to the original data
df <- cbind(df, topics = apply(topic_proportions, 1, function(x) names(x)[which.max(x)]))

# Replace NA topics with "other"
df$topics[is.na(df$topics)] <- "other"

# Save labeled data for later review
write.csv(df, ".\\analysis\\summary_with_labels.csv", fileEncoding = "UTF-8")

# Prepare data for plotting
df <- df %>%
  mutate(meeting_number = as.numeric(str_extract(meeting, "\\d+")),
         meeting = factor(meeting, levels = unique(meeting[order(meeting_number)])))

# Filter out "other" and "session" topics before processing
df <- df %>%
  filter(!topics %in% c("other", "session"))

# Standardize topic distribution by document length
document_topic_distribution <- df %>%
  group_by(document, topics) %>%
  summarize(count = n(), .groups = 'drop') %>%
  group_by(document) %>%
  mutate(document_percentage = count / sum(count)) %>%
  ungroup()

document_topic_summary <- document_topic_distribution %>%
  group_by(document, topics) %>%
  summarize(normalized_percentage = sum(document_percentage), .groups = 'drop')

# Create a wide format data frame with documents as rows and topics as columns
wide_topic_distribution <- document_topic_summary %>%
  pivot_wider(names_from = topics, values_from = normalized_percentage, values_fill = 0)

# Convert the wide format data to a long format for ggplot
long_topic_distribution <- wide_topic_distribution %>%
  pivot_longer(cols = -document, 
               names_to = "topic", 
               values_to = "normalized_percentage") %>%
  # Extract meeting numbers and set the meeting factor levels
  mutate(meeting_number = as.numeric(str_extract(document, "\\d+")),
         document = factor(document, levels = unique(document[order(meeting_number)])))

long_topic_distribution$normalized_percentage <- long_topic_distribution$normalized_percentage * 100

# Plot the stacked bar chart, ordering by meeting factor levels
p <- ggplot(long_topic_distribution, aes(x = document, y = normalized_percentage, fill = topic)) +
  geom_bar(stat = "identity") +
  labs(x = "WCPFC Meeting", y = "Ratio of Topics (%)") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) 

p
# ggsave("wcpfc_reports.png", plot = p, width = 7, height = 5, dpi = 300)
