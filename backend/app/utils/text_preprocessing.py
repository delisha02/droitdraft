import re
from typing import List
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download NLTK data if not already present
try:
    stopwords.words('english')
except LookupError:
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

class TextPreprocessor:
    """
    Handles text preprocessing for legal documents.
    """

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add/remove legally significant stop words if necessary
        # Example: self.stop_words.discard('court')
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.citation_pattern = r'\b\d+\s[A-Z][\w\.]*\s\d+\b' # Store citation pattern

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text, preserving legal citations and converting to lowercase.
        """
        # Split the text by the citation pattern, keeping the citations
        parts = re.split(f'({self.citation_pattern})', text)
        
        final_tokens = []
        for part in parts:
            if re.match(self.citation_pattern, part):
                # For citations, add them as a single token without lowercasing
                final_tokens.append(part)
            else:
                # For other parts of the text, tokenize and lowercase individual tokens
                final_tokens.extend([token.lower() for token in word_tokenize(part)])
                
        return final_tokens

    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Removes common stop words, preserving legally significant ones.
        """
        cleaned_tokens = []
        for word in tokens:
            if re.match(self.citation_pattern, word):
                cleaned_tokens.append(word)
            elif word not in self.stop_words:
                cleaned_tokens.append(word)
        return cleaned_tokens

    def stem_and_lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Applies stemming and lemmatization to tokens.
        """
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) if not re.match(self.citation_pattern, word) else word for word in tokens]
        stemmed_tokens = [self.stemmer.stem(word) if not re.match(self.citation_pattern, word) else word for word in lemmatized_tokens]
        return stemmed_tokens

    def _remove_punctuation(self, tokens: List[str]) -> List[str]:
        """
        Removes punctuation from tokens, preserving citations.
        """
        cleaned_tokens = []
        for token in tokens:
            if re.match(self.citation_pattern, token):
                cleaned_tokens.append(token)
            else:
                # Only remove punctuation if it's not part of a citation
                cleaned_tokens.append(re.sub(r'[^\w\s]', '', token))
        return [token for token in cleaned_tokens if token]

    def preprocess(self, text: str) -> List[str]:
        """
        Applies full preprocessing pipeline to a given text.
        """
        tokens = self.tokenize(text)
        tokens = self._remove_punctuation(tokens)
        tokens = self.remove_stop_words(tokens)
        # tokens = self.stem_and_lemmatize(tokens) # Temporarily disable stemming and lemmatization
        return tokens
