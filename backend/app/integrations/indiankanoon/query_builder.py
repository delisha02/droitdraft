
from typing import List, Optional

class IndianKanoonQueryBuilder:
    def __init__(self, query: str):
        self.query = query
        self.filters = {}

    def with_doctypes(self, doctypes: List[str]) -> 'IndianKanoonQueryBuilder':
        self.filters["doctypes"] = ",".join(doctypes)
        return self

    def with_from_date(self, from_date: str) -> 'IndianKanoonQueryBuilder':
        self.filters["fromdate"] = from_date
        return self

    def with_to_date(self, to_date: str) -> 'IndianKanoonQueryBuilder':
        self.filters["todate"] = to_date
        return self

    def build(self) -> str:
        query_parts = [self.query]
        for key, value in self.filters.items():
            query_parts.append(f"{key}:{value}")
        return " ".join(query_parts)
