import json
import os
import sys
from sqlalchemy.orm import Session

# Add the backend directory to sys.path to allow importing 'app'
sys.path.append(os.getcwd())

from app.db.database import SessionLocal, engine
from app.models.models import Template, Base

def seed_templates():
    # Ensure tables are created (though they should be via migrations)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    seeds_path = os.path.join(os.path.dirname(__file__), "..", "app", "seeds", "maharashtra_templates.json")
    
    with open(seeds_path, "r", encoding="utf-8") as f:
        templates_data = json.load(f)
    
    for template_data in templates_data:
        # Check if template already exists
        db_template = db.query(Template).filter(Template.name == template_data["name"]).first()
        if db_template:
            print(f"Updating existing template: {template_data['name']}")
            for key, value in template_data.items():
                setattr(db_template, key, value)
        else:
            print(f"Seeding new template: {template_data['name']}")
            db_template = Template(**template_data)
            db.add(db_template)
    
    db.commit()
    db.close()
    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed_templates()
