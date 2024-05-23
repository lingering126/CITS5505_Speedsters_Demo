import re

def strip_html(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def truncate_words(text, num_words):
    """Truncate text to the first `num_words` words."""
    words = text.split()
    if len(words) > num_words:
        return ' '.join(words[:num_words]) + '...'
    return ' '.join(words)
