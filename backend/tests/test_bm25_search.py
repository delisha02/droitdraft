import pytest
from datetime import datetime
from app.utils.text_preprocessing import TextPreprocessor
from app.agents.legal_research.bm25_engine import BM25Engine
from app.agents.legal_research.document_store import DocumentStore
from app.agents.legal_research.bm25_indexer import BM25Indexer
from app.agents.legal_research.query_processor import QueryProcessor
import os

# --- Fixtures ---

@pytest.fixture(scope="module")
def text_preprocessor():
    return TextPreprocessor()

@pytest.fixture(scope="module")
def sample_documents():
    return [
        {"id": "doc1", "content": "This is a legal document specifically about contract law. It discusses various aspects of contract formation and breach. See 123 U.S. 456.", "metadata": {"jurisdiction": "US", "date": "2023-01-01"}},
        {"id": "doc2", "content": "Another document discussing tort law and negligence. See 789 F.3d 123.", "metadata": {"jurisdiction": "US", "date": "2023-02-01"}},
        {"id": "doc3", "content": "A document primarily on property in the UK. It discusses land ownership and deeds. No citations here.", "metadata": {"jurisdiction": "UK", "date": "2023-03-01"}},
        {"id": "doc4", "content": "Contract dispute resolution. This document mentions 123 U.S. 456 again.", "metadata": {"jurisdiction": "US", "date": "2023-01-15"}},
    ]

@pytest.fixture(scope="module")
def document_store(sample_documents):
    store = DocumentStore()
    store.add_documents(sample_documents)
    return store

@pytest.fixture(scope="module")
def bm25_indexer(document_store):
    # Temporarily remove index persistence for debugging
    indexer = BM25Indexer(document_store, index_path="temp_index.pkl") # index_path is now a dummy
    indexer.bm25_engine._build_index() # Directly build the index in memory
    return indexer

@pytest.fixture
def query_processor():
    return QueryProcessor()

# --- TextPreprocessor Tests ---

def test_text_preprocessor_tokenize(text_preprocessor):
    text = "Hello, world! This is a test. See 123 U.S. 456."
    tokens = text_preprocessor.tokenize(text)
    assert "hello" in tokens
    assert "world" in tokens
    assert "123 U.S. 456" in tokens # Citation preserved
    assert "," in tokens # Commas are now preserved as tokens

def test_text_preprocessor_remove_stop_words(text_preprocessor):
    tokens = ["this", "is", "a", "test", "document", "the"]
    filtered_tokens = text_preprocessor.remove_stop_words(tokens)
    assert "this" not in filtered_tokens
    assert "document" in filtered_tokens

def test_text_preprocessor_stem_and_lemmatize(text_preprocessor):
    tokens = ["running", "runs", "ran", "better", "laws"]
    processed_tokens = text_preprocessor.stem_and_lemmatize(tokens)
    assert "run" in processed_tokens
    assert "law" in processed_tokens
    assert "better" in processed_tokens # Lemmatizer might not change this without context

def test_text_preprocessor_preprocess(text_preprocessor):
    text = "The quick brown fox jumps over the lazy dog. Legal case 123 U.S. 456."
    processed_tokens = text_preprocessor.preprocess(text)
    assert "quick" in processed_tokens
    assert "brown" in processed_tokens
    assert "fox" in processed_tokens
    assert "jump" in processed_tokens # Stemmed
    assert "lazi" in processed_tokens # Stemmed
    assert "dog" in processed_tokens
    assert "legal" in processed_tokens
    assert "case" in processed_tokens
    assert "123 U.S. 456" in processed_tokens
    assert "the" not in processed_tokens # Stop word removed

# --- BM25Indexer Tests ---

def test_bm25_indexer_search(bm25_indexer):
    results = bm25_indexer.search("contract law", top_n=2)
    assert len(results) == 2
    assert results[0]["document"]["id"] == "doc1" # Assuming doc1 is most relevant
    assert results[0]["score"] > results[1]["score"]

def test_bm25_indexer_no_results(bm25_indexer):
    results = bm25_indexer.search("nonexistent term")
    assert len(results) == 0

# --- QueryProcessor Tests ---

def test_query_processor_parse_simple_query(query_processor):
    query = "contract law"
    parsed = query_processor.parse_query(query)
    assert parsed == {"operator": "AND", "terms": ["contract", "law"]}

def test_query_processor_parse_phrase_query(query_processor):
    query = '"contract law" AND negligence'
    parsed = query_processor.parse_query(query)
    assert parsed == {"operator": "AND", "terms": ['"contract law"', "negligence"]}

def test_query_processor_parse_or_query(query_processor):
    query = "contract OR tort"
    parsed = query_processor.parse_query(query)
    assert parsed == {"operator": "OR", "terms": ["contract", "tort"]}

def test_query_processor_parse_not_query(query_processor):
    query = "contract NOT breach"
    parsed = query_processor.parse_query(query)
    assert parsed == {"operator": "AND", "terms": ["contract", {"operator": "NOT", "term": "breach"}]}

def test_query_processor_extract_keywords(query_processor):
    parsed_query = {"operator": "AND", "terms": [{"operator": "AND", "terms": ["contract", {"operator": "OR", "terms": ["tort", "negligence"]}, '"legal precedent"', {"operator": "NOT", "term": "breach"}]}]}
    keywords = query_processor.extract_keywords(parsed_query)
    assert "contract" in keywords
    assert "tort" in keywords
    assert "negligence" in keywords
    assert "legal precedent" in keywords
    assert "breach" in keywords
