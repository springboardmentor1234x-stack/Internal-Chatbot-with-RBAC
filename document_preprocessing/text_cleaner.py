"""
Text Cleaner - Clean and normalize document text
Handles whitespace, special characters, encoding issues
"""

import re
import unicodedata


class TextCleaner:
    """Clean and normalize text content"""
    
    def __init__(self):
        # Patterns for cleaning
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.multiple_spaces = re.compile(r'\s+')
        self.multiple_newlines = re.compile(r'\n{3,}')
        
    def normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters"""
        # Normalize to NFKC form (canonical decomposition + canonical composition)
        text = unicodedata.normalize('NFKC', text)
        return text
    
    def remove_special_chars(self, text: str, keep_basic_punctuation: bool = True) -> str:
        """
        Remove special characters while keeping important punctuation
        """
        if keep_basic_punctuation:
            # Keep: letters, numbers, basic punctuation (.,!?;:-()")
            text = re.sub(r'[^\w\s.,!?;:()\-"\'\n\$%]', ' ', text)
        else:
            # Keep only alphanumeric and spaces
            text = re.sub(r'[^\w\s]', ' ', text)
        
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace - collapse multiple spaces, clean newlines
        """
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Collapse multiple spaces to single space
        text = self.multiple_spaces.sub(' ', text)
        
        # Reduce multiple newlines to max 2
        text = self.multiple_newlines.sub('\n\n', text)
        
        # Remove spaces at start/end of lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        return self.url_pattern.sub('', text)
    
    def mask_emails(self, text: str, mask: str = '[EMAIL]') -> str:
        """Mask email addresses for privacy"""
        return self.email_pattern.sub(mask, text)
    
    def fix_encoding_issues(self, text: str) -> str:
        """Fix common encoding issues"""
        # Common replacements
        replacements = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Horizontal ellipsis
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def clean_text(self, 
                   text: str,
                   normalize_unicode: bool = True,
                   remove_urls: bool = False,
                   mask_emails: bool = False,
                   remove_special_chars: bool = False,
                   normalize_whitespace: bool = True) -> str:
        """
        Complete text cleaning pipeline
        
        Args:
            text: Input text
            normalize_unicode: Normalize unicode characters
            remove_urls: Remove URLs
            mask_emails: Mask email addresses
            remove_special_chars: Remove special characters
            normalize_whitespace: Normalize whitespace
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Apply cleaning steps
        if normalize_unicode:
            text = self.normalize_unicode(text)
        
        text = self.fix_encoding_issues(text)
        
        if remove_urls:
            text = self.remove_urls(text)
        
        if mask_emails:
            text = self.mask_emails(text)
        
        if remove_special_chars:
            text = self.remove_special_chars(text)
        
        if normalize_whitespace:
            text = self.normalize_whitespace(text)
        
        return text


def main():
    """Test the text cleaner"""
    print("=" * 60)
    print("TEXT CLEANER TEST")
    print("=" * 60)
    
    cleaner = TextCleaner()
    
    # Test cases
    test_texts = [
        "Hello   World!  Multiple    spaces.",
        "Check out https://example.com for more info",
        "Contact us at test@example.com or admin@test.org",
        "Special chars: @#$%^&*()  and unicode: café, naïve",
        "Lots\n\n\n\n\nof\n\n\n\nnewlines",
        "Em dash— and 'smart quotes' everywhere"
    ]
    
    print("\nTest Results:")
    print("-" * 60)
    
    for i, text in enumerate(test_texts, 1):
        cleaned = cleaner.clean_text(
            text,
            remove_urls=True,
            mask_emails=True,
            normalize_whitespace=True
        )
        print(f"\n{i}. Original: {text}")
        print(f"   Cleaned:  {cleaned}")
    
    print("\n" + "=" * 60)
    print("✅ Text cleaning complete")


if __name__ == "__main__":
    main()
