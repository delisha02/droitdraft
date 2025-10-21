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
        """
        query_string = query_string.strip()
        if not query_string:
            return {"operator": "AND", "terms": []}

        # Step 1: Tokenize the query, separating terms, phrases, and operators
        # This regex captures quoted phrases, NOT, AND, OR, or any sequence of non-whitespace characters
        # re.IGNORECASE makes operators case-insensitive
        tokens = [m.group(0) for m in re.finditer(r'"[^"]*"|NOT|AND|OR|\S+', query_string, re.IGNORECASE)]

        # Step 2: Process NOT operators (highest precedence)
        # NOT applies to the immediately following term/phrase
        not_processed_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.upper() == "NOT":
                if i + 1 < len(tokens):
                    not_processed_tokens.append({"operator": "NOT", "term": tokens[i+1]})
                    i += 1 # Skip the next token as it's consumed by NOT
                else:
                    # Handle dangling NOT: treat as a regular term if nothing follows
                    not_processed_tokens.append(token)
            else:
                not_processed_tokens.append(token)
            i += 1
        tokens = not_processed_tokens

        # Step 3: Process AND operators (higher precedence than OR)
        # This step groups terms connected by AND.
        and_processed_tokens = []
        i = 0
        while i < len(tokens):
            term = tokens[i]
            if i + 1 < len(tokens) and isinstance(tokens[i+1], str) and tokens[i+1].upper() == "AND":
                # Found an AND, group the current term with the next one
                if isinstance(term, dict) and term.get("operator") == "AND":
                    # If the current term is already an AND group, extend it
                    and_processed_tokens.append(term)
                else:
                    and_processed_tokens.append(term)
                i += 2 # Skip the AND and the next term, which will be handled in the next iteration
            else:
                and_processed_tokens.append(term)
                i += 1
        tokens = and_processed_tokens

        # Step 4: Process OR operators (lower precedence)
        # This step groups the results of AND operations connected by OR.
        or_processed_tokens = []
        current_or_group = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if isinstance(token, str) and token.upper() == "OR":
                # If we encounter an OR, and we have a current group, add it to or_processed_tokens
                if current_or_group:
                    or_processed_tokens.append(self._simplify_group(current_or_group, "AND")) # Implicit AND for terms within the OR group
                current_or_group = [] # Reset for the next OR group
            else:
                current_or_group.append(token)
            i += 1
        if current_or_group:
            or_processed_tokens.append(self._simplify_group(current_or_group, "AND"))

        if len(or_processed_tokens) == 1:
            tokens = or_processed_tokens[0]
        elif len(or_processed_tokens) > 1:
            tokens = {"operator": "OR", "terms": or_processed_tokens}
        else:
            tokens = {"operator": "AND", "terms": []} # Default for empty query

        # Step 5: Final simplification
        if isinstance(tokens, dict) and tokens.get("operator") == "AND" and len(tokens.get("terms", [])) == 1:
            return tokens["terms"][0]
        return tokens

    def _simplify_group(self, group: List[Any], default_operator: str) -> Dict[str, Any]:
        """
        Simplifies a list of terms/groups into a single dictionary with a default operator.
        If the group contains only one item, it returns that item directly.
        """
        if len(group) == 1:
            return group[0]
        else:
            return {"operator": default_operator, "terms": group}

    def extract_keywords(self, parsed_query: Dict[str, Any]) -> List[str]:
        """
        Extracts all keywords from a parsed query, including terms within phrase queries.
        """
        keywords = []
        if isinstance(parsed_query, str):
            # Remove quotes from phrase queries for keyword extraction
            if parsed_query.startswith('"') and parsed_query.endswith('"'):
                keywords.append(parsed_query[1:-1])
            else:
                keywords.append(parsed_query)
        elif isinstance(parsed_query, dict):
            operator = parsed_query.get("operator")
            terms = parsed_query.get("terms", [])

            if operator == "NOT":
                term = parsed_query.get("term")
                if term: # Ensure term is not None
                    if isinstance(term, str) and term.startswith('"') and term.endswith('"'):
                        keywords.append(term[1:-1])
                    else:
                        keywords.append(term)
            else:
                for term_item in terms:
                    keywords.extend(self.extract_keywords(term_item)) # Recursive call
        return keywords
