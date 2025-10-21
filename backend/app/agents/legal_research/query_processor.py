from typing import List, Dict, Any
import re

class QueryProcessor:
    """
    Processes user queries for BM25 search, handling boolean operators and phrase queries.
    """

    def __init__(self):
        pass

    def parse_query(self, query_string: str) -> Dict[str, Any]:
        """
        Parses a query string into a structured format, identifying key terms,
        boolean operators (AND, OR, NOT), and phrase queries.

        Args:
            query_string: The raw query string from the user.

        Returns:
            A dictionary representing the parsed query, e.g.,
            {"operator": "AND", "terms": ["term1", {"operator": "OR", "terms": ["term2", "term3"]}, "\"phrase query\""]}
        """
        # Normalize query string: replace multiple spaces, trim
        query_string = re.sub(r'\s+', ' ', query_string).strip()

        # Tokenize by words and quoted phrases
        # This regex captures either a quoted string (group 1) or a non-whitespace word (group 2)
        tokens = [m.group(1) or m.group(2) for m in re.finditer(r'"([^"]*)"|(\S+)', query_string)]

        # Simple state machine for parsing
        parsed_query = {"operator": "AND", "terms": []}
        current_group = []
        current_boolean_op = "AND"

        i = 0 # Initialize i
        while i < len(tokens):
            token = tokens[i]
            upper_token = token.upper()

            if upper_token == "AND":
                if current_group:
                    parsed_query["terms"].append({"operator": current_boolean_op, "terms": current_group})
                current_group = []
                current_boolean_op = "AND"
            elif upper_token == "OR":
                if current_group:
                    parsed_query["terms"].append({"operator": current_boolean_op, "terms": current_group})
                current_group = []
                current_boolean_op = "OR"
            elif upper_token == "NOT":
                # NOT applies to the next term
                if i + 1 < len(tokens):
                    next_term = tokens[i+1]
                    current_group.append({"operator": "NOT", "term": next_term})
                    i += 1 # Skip next token as it's consumed by NOT
                else:
                    # Handle malformed query: NOT at the end
                    pass # Or raise an error
            else:
                current_group.append(token)
            i += 1

        if current_group:
            parsed_query["terms"].append({"operator": current_boolean_op, "terms": current_group})

        # Simplify if only one top-level group
        if len(parsed_query["terms"]) == 1 and isinstance(parsed_query["terms"][0], dict):
            return parsed_query["terms"][0]
        # If no operators found, treat all as AND terms
        if not parsed_query["terms"] and query_string:
            return {"operator": "AND", "terms": [{"operator": "AND", "terms": [t for t in tokens if t.upper() not in ["AND", "OR", "NOT"]]}] }
        elif not parsed_query["terms"]:
            return {"operator": "AND", "terms": []}

        return parsed_query

    def extract_keywords(self, parsed_query: Dict[str, Any]) -> List[str]:
        """
        Extracts all keywords from a parsed query, including terms within phrase queries.
        """
        keywords = []
        for term_item in parsed_query.get("terms", []):
            if isinstance(term_item, dict):
                if "operator" in term_item and "terms" in term_item:
                    # Handle nested boolean operations
                    keywords.extend(self.extract_keywords(term_item))
                elif "operator" in term_item and term_item["operator"] == "NOT" and "term" in term_item:
                    # Handle NOT operator's term
                    keywords.append(term_item["term"])
            else:
                # Remove quotes from phrase queries for keyword extraction
                if isinstance(term_item, str) and term_item.startswith('"') and term_item.endswith('"'):
                    keywords.append(term_item[1:-1])
                else:
                    keywords.append(term_item)
        return keywords
