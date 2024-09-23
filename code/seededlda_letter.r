library(readxl)
library(dplyr)
require(quanteda)
require(seededlda)
library(stringr)
library(ggplot2)
library(tidyr)

setwd("C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\rfmo")

rm(list=ls()) 

df <- read.csv(".\\analysis\\coded_advocacy_letters.csv", header = TRUE)

df <- df %>%
  mutate(content = tolower(content),                             # Convert to lowercase
         content = str_replace_all(content, "[[:punct:]]", " "), # Remove punctuation
         content = str_squish(content))                         # Remove extra whitespace

df <- df %>%
  mutate(meeting = str_extract(document, "WCPFC\\d+")) %>%
  filter(nchar(content) >= 60)

#dict <- list(harvest_strategy = c('harvest','mse','hcr*','trp','strateg*','limit*','target*','referenc*'),
#             fishing_mortality = c('mortality','overfishing','catch','quota'),
#             fleet_capacity = c('capacity','overcapacity','effort*','closure'),
#             scientific_advice = c('scienti*','science','listen*','advice'),
#             precautionary_approach = c('precautionary','follow','pa','approach'),
#             bycatch = c('bycatch','shark*','turtle*','seabird*','mammal*','juvenile','billfish','longline','fad*'),
#             fleet_transparency = c('vms','iuu','ais','cds','transparency','transshipment'),
#             governance = c('right*', 'small', 'island*','sids','allocation'),
#             data_research = c('data','stock','assessment*','research','collaboration','tagging'),
#             session = c('session','december','regular','meeting','wcpfc*')
#)

dict <- list(strategy = c('mse','hcr*','trp','strateg*','limit*','target*','control','harvest','capacity','mortality','overcapacity'),
             bycatch = c('bycatch','shark*','turtle*','seabird*','mammal*','juvenile','billfish','longline','fad*','retention'),
             transparency = c('vms','iuu','ais','cds','transparen*','unreported'),
             equity = c('right*', 'small', 'island*','sids','allocation','developing','burden','ffa'),
             session = c('session*','december','regular','meeting*','wcpfc*','chair*')
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


df <- cbind(df, topics(slda))
colnames(df)[5] <- "topic"

# Handle NA values
df$topic[is.na(df$topic)] <- "other"

# Write out labeled data for later review
write.csv(df, ".\\analysis\\letters_with_labels_four.csv", fileEncoding = "UTF-8")

# Extract numeric part for ordering
df <- df %>%
  mutate(meeting_number = as.numeric(str_extract(meeting, "\\d+")))

# Create ordered factor for meetings
df <- df %>%
  mutate(meeting = factor(meeting, levels = unique(meeting[order(meeting_number)])))

# Filter out "other" and "session" topics before processing
df <- df %>%
  filter(!topic %in% c("other", "session"))

# Treat the presence of topics in a document as ratio
document_topic_distribution <- df %>%
  group_by(document, topic) %>%
  summarize(count = n(), .groups = 'drop') %>%
  group_by(document) %>%
  mutate(document_percentage = count / sum(count)) %>%
  ungroup()

# Treat the presence of topics in a document as binary
#document_topic_distribution <- df %>%
#  group_by(document, topic) %>%
#  summarize(present = ifelse(n() > 0, 1, 0), .groups = 'drop') %>%
#  group_by(document) %>%
#  mutate(document_percentage = present / sum(present)) %>%
#  ungroup()

document_topic_summary <- document_topic_distribution %>%
  group_by(document, topic) %>%
  summarize(normalized_percentage = sum(document_percentage), .groups = 'drop')

# Create a wide format data frame with documents as rows and topics as columns
wide_topic_distribution <- document_topic_summary %>%
  pivot_wider(names_from = topic, values_from = normalized_percentage, values_fill = 0)

# Calculate the distribution of topics by meeting
wide_topic_distribution <- wide_topic_distribution %>%
  mutate(meeting = str_extract(document, "WCPFC\\d+")) # Extract meeting identifier

# Calculate average ratios by meeting
average_ratios_by_meeting <- wide_topic_distribution %>%
  group_by(meeting) %>%
  summarize(across(-document, mean, na.rm = TRUE), .groups = 'drop')


# Transform the average ratios data frame to long format
long_average_ratios <- average_ratios_by_meeting %>%
  pivot_longer(cols = -meeting, names_to = "topic", values_to = "average_ratio")

# Extract numeric part for ordering
long_average_ratios <- long_average_ratios %>%
  mutate(meeting_number = as.numeric(str_extract(meeting, "\\d+")),
         meeting = factor(meeting, levels = unique(meeting[order(meeting_number)])))

#topic_order <- c("data_research", 
#                 "governance", 
#                 "fleet_transparency", 
#                 "bycatch", 
#                 "precautionary_approach", 
#                 "scientific_advice", 
#                 "fleet_capacity", 
#                 "fishing_mortality", 
#                 "harvest_strategy")

# Reorder the factor levels for 'topic' based on the specified order
#long_average_ratios <- long_average_ratios %>%
#  mutate(topic = factor(topic, levels = topic_order))

# Create the stacked bar chart
p <- ggplot(long_average_ratios, aes(x = meeting, y = average_ratio, fill = topic)) +
  geom_bar(stat = "identity") +
  labs(x = "WCPFC Meeting",
       y = "Ratio of Topics (%)",
       fill = "Topic") +
  theme_minimal() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

p
#ggsave("wcpfc_letters.png", plot = p, width = 7, height = 5, dpi = 300)
