from app.services.legal_corpus_catalog import get_legal_research_act_catalog

catalog = get_legal_research_act_catalog()
target_acts = ['bnss', 'succession', 'negotiable', 'civil procedure', 'rent control']

for act in catalog:
    name = act['name'].lower()
    if any(t in name for t in target_acts):
        tid = act.get('tid', 'NO TID')
        print(f"{act['name']}: tid={tid}")

# Also show acts without tid
print("\nActs without tid:")
for act in catalog:
    if 'tid' not in act:
        print(f"  {act['name']}")
