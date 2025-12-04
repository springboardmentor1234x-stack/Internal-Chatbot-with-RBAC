import re
import string
import nltk
from nltk.corpus import stopwords

ENGLISH_STOP_WORDS = set(stopwords.words('english'))

def replace_hyphens_with_spaces(text):
    return re.sub(r'-', ' ', text)

def remove_markdown_headings(text):
    pattern = r'^#+\s*'
    return re.sub(pattern, '', text, flags=re.MULTILINE)

def remove_separators(text):
    pattern = r'^-+$'
    return re.sub(pattern, '', text, flags=re.MULTILINE)

def remove_punctuation(text):
    punctuations_to_remove = string.punctuation.replace('%', '')
    translator = str.maketrans('', '', punctuations_to_remove)
    return text.translate(translator)

def remove_stop_words(text):
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word.lower() not in ENGLISH_STOP_WORDS]
    return ' '.join(filtered_tokens)

def normalize_whitespace(text):
    temp_text = re.sub(r'\s+', ' ', text)
    return temp_text.strip()

def comprehensive_normalization(text):
    text = remove_markdown_headings(text)
    text = remove_separators(text)
    text = replace_hyphens_with_spaces(text)
    text = remove_punctuation(text)
    text = remove_stop_words(text)
    text = normalize_whitespace(text)
    return text

raw_text = "\n# Financial Report for FinSolve Technologies Inc. - 2024\n\nExecutive Summary:\n-------------------------------------------\n2024 marked a year of both opportunity and challenge for FinSolve Technologies. Despite a robust revenue increase, we saw significant pressure in certain expense categories, notably vendor-related costs and software subscriptions. However, these pressures were balanced by cost-saving measures in operational efficiency, strong gross margin performance, and strategic investment in growth areas. The company is well-positioned to continue scaling its core offerings, but focused attention on cost optimization will be essential for maintaining profitability in the coming years.\n\nYear-Over-Year (YoY) Analysis:\n-------------------------------------------\nFinSolve Technologies's revenue grew by 25% in 2024, driven largely by the global expansion of its services, especially in Asia and Europe. This was accompanied by a 10% increase in vendor-related expenses, impacting overall profit margins. While gross profit increased by 25%, reflecting higher operational efficiency, **net income** saw a more modest increase of 12%. This suggests that while revenue growth is strong, controlling vendor costs and maintaining healthy cash flows remain key to long-term profitability.\n\nExpense Breakdown by Category:\n-------------------------------------------\n"
normalized_output = comprehensive_normalization(raw_text)

print("\n--- FINAL NORMALIZED OUTPUT (Complete Pipeline) ---")
print(normalized_output)
normalized_output = comprehensive_normalization(raw_text)

