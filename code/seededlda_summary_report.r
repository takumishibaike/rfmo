library(readxl)
library(dplyr)
require(quanteda)
require(seededlda)
library(stringr)
library(ggplot2)
library(tidyr)

setwd("C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\wcpfc")

rm(list=ls()) 

df <- read.csv(".\\analysis\\wcpfc.csv", header = TRUE)

df <- df %>%
  filter(str_detect(document, "^WCPFC[3-9]|^WCPFC1[0-6]")) 

df <- df %>%
  mutate(content = tolower(content),                             # Convert to lowercase
         content = str_replace_all(content, "[[:punct:]]", " "), # Remove punctuation
         content = str_squish(content))                         # Remove extra whitespace

df <- df %>%
  mutate(meeting = str_extract(document, "WCPFC\\d+")) %>%
  filter(nchar(content) >= 70)

dict <- list(strategy = c('mse','hcr*','trp','strategy','limit','target'),
             bycatch = c('bycatch','shark','turtle','seabird','mammal'),
             transparency = c('vms','iuu','ais','cds','transparency'),
             governance = c('right', 'small', 'island','sids')
)

dict <- dictionary(dict)

corp <- as.character(df$content)
toks <- tokens(corp, remove_punct = TRUE, remove_symbols = TRUE, remove_number = TRUE) %>%
  tokens_select(min_nchar = 2) %>%
  tokens_compound(dict) # for multi-word expressions
dfmt <- dfm(toks) %>%
  dfm_remove(stopwords('en')) %>%
  dfm_trim(min_termfreq = 0.90, termfreq_type = 'quantile',
           max_docfreq = 0.2, docfreq_type = 'prop')

set.seed(1234)
slda <- textmodel_seededlda(dfmt, dict, residual = TRUE, verbose=TRUE)
print(terms(slda, 10))
table(topics(slda))

# Write out terms for later review
# write.csv(terms(slda, 100), ".\\analysis\\keywords_frame.csv")

df <- cbind(df, topics(slda))
colnames(df)[5] <- "topic"

# Handle NA values
df$topic[is.na(df$topic)] <- "other"

# Write out labeled data for later review
#write.csv(df, ".\\analysis\\letters_with_labels.csv", fileEncoding = "UTF-8")

# Extract numeric part for ordering
df <- df %>%
  mutate(meeting_number = as.numeric(str_extract(meeting, "\\d+")))

# Create ordered factor for meetings
df <- df %>%
  mutate(meeting = factor(meeting, levels = unique(meeting[order(meeting_number)])))

# Standardize topic distribution by document length
document_topic_distribution <- df %>%
  group_by(document, topic) %>%
  summarize(count = n(), .groups = 'drop') %>%
  group_by(document) %>%
  mutate(document_percentage = count / sum(count)) %>%
  ungroup()

document_topic_summary <- document_topic_distribution %>%
  group_by(document, topic) %>%
  summarize(normalized_percentage = sum(document_percentage), .groups = 'drop')

# Create a wide format data frame with documents as rows and topics as columns
wide_topic_distribution <- document_topic_summary %>%
  pivot_wider(names_from = topic, values_from = normalized_percentage, values_fill = 0)

# Convert the wide format data to a long format for ggplot
long_topic_distribution <- wide_topic_distribution %>%
  pivot_longer(cols = -document, 
               names_to = "topic", 
               values_to = "normalized_percentage") %>%
  # Extract meeting numbers and set the meeting factor levels
  mutate(meeting_number = as.numeric(str_extract(document, "\\d+")),
         document = factor(document, levels = unique(document[order(meeting_number)])))

long_topic_distribution$normalized_percentage <- long_topic_distribution$normalized_percentage*100

# Create the stacked bar chart, ordering by meeting factor levels
p <- ggplot(long_topic_distribution, aes(x = document, y = normalized_percentage, fill = topic)) +
  geom_bar(stat = "identity") +
  labs(x = "Meeting", y = "Ratio of Topics (%)", title = "Topic Distribution by Meeting") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) 
p
#ggsave("wcpfc_reports.png", plot = p, width = 7, height = 5, dpi = 300)
