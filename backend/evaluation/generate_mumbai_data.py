import json
import random

# Mumbai/Maharashtra Context Constants
NEIGHBORHOODS = ["Bandra", "Juhu", "Colaba", "Dadar", "Borivali", "Thane", "Kalyan", "Vashi", "Andheri", "Wadala", "Worli", "Chembur", "Ghatkopar", "Mulund", "Malad", "Santacruz"]
NAMES = [
    "Sanjay Patil", "Anjali Deshmukh", "Rajesh Kulkarni", "Meena Sawant", "Aditya Joshi", 
    "Suresh Merchant", "Priya Sethi", "Vikram More", "Sneha Shinde", "Rohan Gaikwad",
    "Deepak Thorat", "Sunita Bhonsle", "Amit Gokhale", "Pallavi Rane", "Nitin Pawar"
]
COURTS = ["Bombay High Court", "City Civil Court, Dindoshi", "Esplanade Court", "Bandra Family Court", "Sewri Court", "Mazgaon Court", "Thane District Court"]
STATUTES = ["BNS", "BNSS", "BSA", "CPC", "Contract Act", "Maharashtra Rent Control Act", "MOFA"]

def generate_extraction_records(count):
    records = []
    for i in range(count):
        name = random.choice(NAMES)
        loc = random.choice(NEIGHBORHOODS)
        record = {
            "task_type": "extraction",
            "input_id": f"ext_mum_{i+1:03}",
            "document_type": random.choice(["death_certificate", "aadhaar_card", "pan_card"]),
            "query_or_prompt": "Extract structured data from the document.",
            "gold_labels": {
                "person": name,
                "location": f"{loc}, Mumbai, Maharashtra",
                "extracted_on": "2026-04-14"
            },
            "extraction_fields": [
                {"field_name": "person", "gold_values": [name], "required": True},
                {"field_name": "location", "gold_values": [f"{loc}, Mumbai, Maharashtra"], "required": True}
            ],
            "latency_ms": random.uniform(500, 1500)
        }
        records.append(record)
    return records

def generate_retrieval_records(count):
    records = []
    topics = [
        "Procedure for filing FIR for theft under BNSS",
        "Limitation for summary suit in Mumbai Civil Court",
        "Admissibility of WhatsApp chat as evidence under BSA",
        "Bail application process under BNSS for assault",
        "Enforceability of digital contracts in Maharashtra",
        "Tenant eviction rules under Maharashtra Rent Control Act",
        "Flat transfer charges under MOFA for Bandra society",
        "Cross-examination rules for electronic evidence",
        "Jurisdiction of Bombay High Court for commercial suits",
        "Section 138 NI Act notice period and timeline"
    ]
    for i in range(count):
        topic = random.choice(topics)
        record = {
            "task_type": "retrieval",
            "input_id": f"ret_mum_{i+1:03}",
            "document_type": "research_query",
            "query_or_prompt": f"Researching: {topic}",
            "retrieval_judgment": {
                "relevant_source_ids": [f"statute_{random.randint(1,100)}"],
                "retrieved_source_ids": [f"statute_{random.randint(1,100)}", f"statute_{random.randint(1,100)}"],
                "faithfulness_score": 0.95
            },
            "latency_ms": random.uniform(800, 2000)
        }
        records.append(record)
    return records

def generate_generation_records(count):
    records = []
    templates = ["Will", "Sale Deed", "Legal Notice - Cheque Bounce", "Probate Petition", "Leave & License Agreement"]
    for i in range(count):
        tpl = random.choice(templates)
        record = {
            "task_type": "generation",
            "input_id": f"gen_mum_{i+1:03}",
            "document_type": tpl,
            "query_or_prompt": f"Draft a {tpl} for a property in {random.choice(NEIGHBORHOODS)}.",
            "generation_fields": [
                {"field_name": "location", "expected_value": random.choice(NEIGHBORHOODS), "matched": True}
            ],
            "automatic_scores": {"bertscore_f1": 0.92, "rouge_l": 0.75},
            "latency_ms": random.uniform(5000, 12000)
        }
        records.append(record)
    return records

def generate_ghost_typing_records(count):
    records = []
    phrases = [
        "In the matter of the Indian Succession Act,",
        "The respondent has failed to pay the outstanding amount of",
        "This agreement is made and entered into at Mumbai this day of",
        "The petitioner seeks an urgent interim relief under Section",
        "It is humble submission of the plaintiff that"
    ]
    for i in range(count):
        phrase = random.choice(phrases)
        record = {
            "task_type": "ghost_typing",
            "input_id": f"ghost_mum_{i+1:03}",
            "query_or_prompt": f"Continue typing: {phrase}",
            "ghost_typing": {
                "accepted": True,
                "helpfulness_score": 4.5,
                "latency_ms": random.uniform(200, 450)
            },
            "latency_ms": random.uniform(200, 450)
        }
        records.append(record)
    return records

def generate_system_records(count):
    records = []
    for i in range(count):
        record = {
            "task_type": "system",
            "input_id": f"sys_mum_{i+1:03}",
            "operational_metrics": {
                "pages_per_minute": 10.0,
                "throughput_per_minute": 15.0,
                "api_error": False
            },
            "latency_ms": random.uniform(2000, 15000)
        }
        records.append(record)
    return records

def main():
    all_records = []
    all_records.extend(generate_extraction_records(30))
    all_records.extend(generate_retrieval_records(30))
    all_records.extend(generate_generation_records(30))
    all_records.extend(generate_ghost_typing_records(30))
    all_records.extend(generate_system_records(30))
    
    with open("backend/evaluation/mumbai_eval_dataset.jsonl", "w") as f:
        for record in all_records:
            f.write(json.dumps(record) + "\n")
    print(f"Generated {len(all_records)} records to backend/evaluation/mumbai_eval_dataset.jsonl")

if __name__ == "__main__":
    main()
