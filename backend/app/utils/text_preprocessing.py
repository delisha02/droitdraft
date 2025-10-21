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

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text, preserving legal citations.
        """
        # Regex to identify legal citations (e.g., 123 U.S. 456, 12 F.3d 345)
        # This is a simplified regex and might need to be more robust for real-world legal texts.
        citation_pattern = r'\b\d+\s[A-Z]+\.?\s\d+\b'
        
        # Find all citations first
        citations = re.findall(citation_pattern, text)
        
        # Replace citations with a unique placeholder to prevent tokenization
        placeholder_map = {citation: f"__CITATION_{i}__" for i, citation in enumerate(citations)}
        processed_text = text
        for citation, placeholder in placeholder_map.items():
            processed_text = processed_text.replace(citation, placeholder)

        # Tokenize the rest of the text
        tokens = word_tokenize(processed_text.lower())

        # Replace placeholders back with original citations, ensuring case is preserved for citations
        final_tokens = []
        for token in tokens:
            replaced = False
            for original_citation, placeholder in placeholder_map.items():
                if token == placeholder.lower():
                    final_tokens.append(original_citation)
                    replaced = True
                    break
            if not replaced:
                final_tokens.append(token)
                
        return final_tokens

    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Removes common stop words, preserving legally significant ones.
        """
        return [word for word in tokens if word not in self.stop_words]

    def stem_and_lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Applies stemming and lemmatization to tokens.
        """
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        stemmed_tokens = [self.stemmer.stem(word) for word in lemmatized_tokens]
        return stemmed_tokens

    def preprocess(self, text: str) -> List[str]:
        """
        Applies full preprocessing pipeline to a given text.
        """
        tokens = self.tokenize(text)
        tokens = self.remove_stop_words(tokens)
        tokens = self.stem_and_lemmatize(tokens)
        return tokens
