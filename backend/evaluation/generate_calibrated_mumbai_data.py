import json
import random

# Real Ground Truth from Death-Certificate.pdf
DEATH_CERT_TEXT = """मृताचे नाव / NAME OF DECEASED : MR. SANJAY VIJAYNATH UPADHYAY पुरष / MALE
मृयू दनांक / DATE OF DEATH: 29-01-2016 मृयू ठकाण / PLACE OF DEATH: BOMBAY HOSPITAL
पा / ADDRESS: AUDUMBER APT., A/206, SHANKAR PAWSHE RD., SAI BABA NAGAR, KATEMANIVALY, KALYAN, THANE"""

REAL_NAME = "MR. SANJAY VIJAYNATH UPADHYAY"
REAL_LOC = "BOMBAY HOSPITAL"

# Calibrated Statutory References (Civil/Property Scope Only)
STATUTES = [
    {"query": "Transfer of property by sale under Transfer of Property Act", "id": "Transfer of Property Act, 1882_54"},
    {"query": "Requirements for a valid Will under Indian Succession Act", "id": "Indian Succession Act, 1925_63"},
    {"query": "Procedure for Probate of a Will", "id": "Indian Succession Act, 1925_222"},
    {"query": "Specific performance of contract under Specific Relief Act", "id": "Specific Relief Act, 1963_10"},
    {"query": "Summary suit procedure under Code of Civil Procedure (CPC)", "id": "Code of Civil Procedure, 1908_Unknown"},
    {"query": "Notice period for cheque bounce under NI Act", "id": "Negotiable Instruments Act, 1881_138"},
    {"query": "Transfer of property by gift under Transfer of Property Act, 1882", "id": "Transfer of Property Act, 1882_122"},
    {"query": "Grounds for eviction under Maharashtra Rent Control Act", "id": "Maharashtra Rent Control Act, 1999_16"},
    {"query": "Registration of documents under Registration Act", "id": "Registration Act, 1908_17"},
    {"query": "Period of limitation for recovery of money", "id": "Limitation Act, 1963_Unknown"}
]

def generate_calibrated_extraction(count):
    records = []
    # Mix of real PDF data and high-fidelity synthetic data
    for i in range(count):
        if i == 0: # The Real PDF
            record = {
                "task_type": "extraction",
                "input_id": f"ext_real_001",
                "document_type": "death_certificate",
                "query_or_prompt": DEATH_CERT_TEXT,
                "gold_labels": {"person": REAL_NAME, "location": REAL_LOC},
                "extraction_fields": [
                    {"field_name": "person", "gold_values": [REAL_NAME], "required": True},
                    {"field_name": "location", "gold_values": [REAL_LOC], "required": True}
                ]
            }
        else: # High-fidelity synthetic (Sale Deed / Will)
            name = f"Advocate {random.randint(100, 999)}"
            loc = "Marine Drive, Mumbai"
            text = f"This DEED OF SALE is made at Mumbai on this day between {name} residing at {loc}..."
            record = {
                "task_type": "extraction",
                "input_id": f"ext_cal_{i+1:03}",
                "document_type": "sale_deed",
                "query_or_prompt": text,
                "gold_labels": {"person": name, "location": loc},
                "extraction_fields": [
                    {"field_name": "person", "gold_values": [name], "required": True},
                    {"field_name": "location", "gold_values": [loc], "required": True}
                ]
            }
        records.append(record)
    return records

def generate_calibrated_retrieval(count):
    records = []
    for i in range(count):
        template = random.choice(STATUTES)
        record = {
            "task_type": "retrieval",
            "input_id": f"ret_cal_{i+1:03}",
            "query_or_prompt": template["query"],
            "retrieval_judgment": {
                "relevant_source_ids": [template["id"]],
                "expected_no_answer": False
            }
        }
        records.append(record)
    return records

def generate_calibrated_generation(count):
    records = []
    for i in range(count):
        record = {
            "task_type": "generation",
            "input_id": f"gen_cal_{i+1:03}",
            "query_or_prompt": f"Draft a legal notice for a cheque bounce under Section 138 of NI Act for a client in Mumbai.",
            "generation_fields": [
                {"field_name": "location", "expected_value": "Mumbai", "matched": True}
            ]
        }
        records.append(record)
    return records

def main():

    # Increase to 100 per task type
    all_records = []
    all_records.extend(generate_calibrated_extraction(100))
    all_records.extend(generate_calibrated_retrieval(100))
    all_records.extend(generate_calibrated_generation(100))
    # Add 100 ghost_typing and 100 system records
    for i in range(100):
        all_records.append({"task_type": "ghost_typing", "input_id": f"ghost_cal_{i+1:03}", "query_or_prompt": "In the matter of"})
    for i in range(100):
        all_records.append({"task_type": "system", "input_id": f"sys_cal_{i+1:03}"})

    # Example: Add negative samples for retrieval (no answer expected)
    for i in range(10):
        all_records.append({
            "task_type": "retrieval",
            "input_id": f"ret_neg_{i+1:03}",
            "query_or_prompt": f"Unanswerable query example {i+1}",
            "retrieval_judgment": {
                "relevant_source_ids": [],
                "expected_no_answer": True
            }
        })

    # Reminder: Review gold_labels for accuracy before running evaluation
    
    import os
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mumbai_calibrated_dataset.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Generated {len(all_records)} calibrated records to backend/evaluation/mumbai_calibrated_dataset.jsonl")

if __name__ == "__main__":
    main()
