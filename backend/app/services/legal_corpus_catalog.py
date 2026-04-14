import re
from typing import Iterable


def normalize_legal_title(value: str) -> str:
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


LEGAL_RESEARCH_ACT_CATALOG = [
    {
        "name": "Bhartiya Nyaya Sanhita (BNS)",
        "aliases": ["bns", "bharatiya nyaya sanhita", "bhartiya nyaya sanhita"],
        "search_query": "\"Bhartiya Nyaya Sanhita\" bare act",
        "tid": 149679501,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Core criminal substantive law.",
    },
    {
        "name": "Bhartiya Nagarik Suraksha Sanhita (BNSS)",
        "aliases": ["bnss", "bharatiya nagarik suraksha sanhita", "bhartiya nagarik suraksha sanhita"],
        "search_query": "\"Bhartiya Nagarik Suraksha Sanhita\" bare act",
        "tid": 91117739,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Core criminal procedure.",
    },
    {
        "name": "Bhartiya Sakshya Adhiniyam (BSA)",
        "aliases": ["bsa", "bharatiya sakshya adhiniyam", "bhartiya sakshya adhiniyam"],
        "search_query": "\"Bhartiya Sakshya Adhiniyam\" bare act",
        "tid": 70224818,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Current evidence law.",
    },
    {
        "name": "Code of Civil Procedure, 1908",
        "aliases": ["cpc", "code of civil procedure", "core of civil procedure", "core of civil prodecure", "civil procedure code"],
        "search_query": "\"Code of Civil Procedure\" bare act",
        "tid": 161831507,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Essential for civil litigation.",
    },
    {
        "name": "Indian Contract Act, 1872",
        "aliases": ["indian contract act", "indian contract"],
        "search_query": "\"Indian Contract Act\" bare act",
        "tid": 171398,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Core commercial agreement statute.",
    },
    {
        "name": "Indian Succession Act, 1925",
        "aliases": ["indian succession act", "succession act"],
        "search_query": "\"Indian Succession Act\" bare act",
        "tid": 1450343,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Wills, probate, and succession.",
    },
    {
        "name": "Registration Act, 1908",
        "aliases": ["registration act"],
        "search_query": "\"Registration Act\" bare act",
        "tid": 1489134,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Registration of instruments.",
    },
    {
        "name": "Maharashtra Rent Control Act, 1999",
        "aliases": ["maharashtra rent control act", "rent control act"],
        "search_query": "\"Maharashtra Rent Control Act\" bare act",
        "tid": 196692406,
        "doc_type": "statute",
        "jurisdiction": "Maharashtra",
        "priority": "Priority 1",
        "notes": "Critical for tenancy disputes.",
    },
    {
        "name": "Maharashtra Co-operative Societies Act",
        "aliases": ["maharashtra co operative societies act", "maharashtra cooperative societies act"],
        "search_query": "\"Maharashtra Co-operative Societies Act\" bare act",
        "tid": 34627769,
        "doc_type": "statute",
        "jurisdiction": "Maharashtra",
        "priority": "Priority 1",
        "notes": "Housing society and redevelopment matters.",
    },
    {
        "name": "Specific Relief Act, 1963",
        "aliases": ["specific relief act"],
        "search_query": "\"Specific Relief Act\" bare act",
        "tid": 1671917,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Enforceability and injunction reliefs.",
    },
    {
        "name": "Transfer of Property Act, 1882",
        "aliases": ["transfer of property act"],
        "search_query": "\"Transfer of Property Act\" bare act",
        "tid": 515323,
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 1",
        "notes": "Property transfers, leases, and conveyancing.",
    },
    {
        "name": "Indian Evidence Act, 1872",
        "aliases": ["indian evidence act", "indian evidence", "evidence act"],
        "search_query": "\"Indian Evidence Act\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 2",
        "notes": "Legacy evidence law still cited in older precedents.",
    },
    {
        "name": "Negotiable Instruments Act, 1881",
        "aliases": ["negotiable instruments act", "ni act", "negotiable instrument act"],
        "search_query": "\"Negotiable Instruments Act\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 2",
        "notes": "Section 138 cheque dishonour matters.",
    },
    {
        "name": "Arbitration and Conciliation Act, 1996",
        "aliases": ["arbitration and conciliation act", "arbitration act"],
        "search_query": "\"Arbitration and Conciliation Act\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 2",
        "notes": "Commercial dispute resolution.",
    },
    {
        "name": "Limitation Act, 1963",
        "aliases": ["limitation act"],
        "search_query": "\"Limitation Act\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 2",
        "notes": "Time-bar and limitation periods.",
    },
    {
        "name": "Companies Act, 2013",
        "aliases": ["companies act", "companies act 2013"],
        "search_query": "\"Companies Act, 2013\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 2",
        "notes": "Corporate transactions and governance.",
    },
    {
        "name": "Indian Partnership Act, 1932",
        "aliases": ["indian partnership act", "partnership act"],
        "search_query": "\"Indian Partnership Act\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 2",
        "notes": "Partnership firms and disputes.",
    },
    {
        "name": "Industrial Disputes Act, 1947",
        "aliases": ["labour act", "labor act", "industrial disputes act"],
        "search_query": "\"Industrial Disputes Act\" bare act",
        "doc_type": "statute",
        "jurisdiction": "India",
        "priority": "Priority 3",
        "notes": "Working assumption for the user-requested labour act.",
    },
    {
        "name": "Bombay High Court (Original Side) Rules",
        "aliases": ["high court original side rule", "high court original side rules", "bombay high court original side rules"],
        "search_query": "\"Bombay High Court Original Side Rules\"",
        "doc_type": "rule",
        "jurisdiction": "Maharashtra",
        "priority": "Priority 2",
        "notes": "Procedural rules for Bombay High Court original side filings.",
    },
]


def get_legal_research_act_catalog() -> list[dict]:
    return [dict(item) for item in LEGAL_RESEARCH_ACT_CATALOG]


def match_catalog_entries(requested_names: Iterable[str]) -> tuple[list[dict], list[str]]:
    catalog = get_legal_research_act_catalog()
    indexed: dict[str, dict] = {}
    for entry in catalog:
        candidates = [entry["name"], *entry.get("aliases", [])]
        for candidate in candidates:
            indexed[normalize_legal_title(candidate)] = entry

    selected: list[dict] = []
    unresolved: list[str] = []
    seen_names: set[str] = set()
    for requested_name in requested_names:
        normalized = normalize_legal_title(requested_name)
        entry = indexed.get(normalized)
        if not entry:
            unresolved.append(requested_name)
            continue
        if entry["name"] in seen_names:
            continue
        selected.append(dict(entry))
        seen_names.add(entry["name"])
    return selected, unresolved
