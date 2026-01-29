from typing import List, Optional
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateError

from app.models.models import Template
from app.schemas.template import TemplateCreate, TemplateUpdate

class TemplateService:
    def __init__(self, db: Session):
        self.db = db
        # For simplicity, we'll assume templates are loaded from a string.
        # In a real application, you might load them from a file system or database.
        self.jinja_env = Environment(
            loader=FileSystemLoader("."),  # Dummy loader, as content is from DB
            autoescape=select_autoescape(['html', 'xml'])
        )

    def create_template(self, template_in: TemplateCreate) -> Template:
        if not self.validate_template_syntax(template_in.content):
            raise ValueError("Invalid Jinja2 template syntax.")
        db_template = Template(**template_in.dict())
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def get_template(self, template_id: int) -> Optional[Template]:
        return self.db.query(Template).filter(Template.id == template_id).first()

    def get_templates(self, skip: int = 0, limit: int = 100) -> List[Template]:
        return self.db.query(Template).offset(skip).limit(limit).all()

    def get_template_by_type(self, document_type: str) -> Optional[Template]:
        """
        Retrieve the latest active template for a specific document type.
        """
        return (
            self.db.query(Template)
            .filter(Template.document_type == document_type)
            .filter(Template.is_active == True)
            .order_by(Template.updated_at.desc())
            .first()
        )

    def update_template(self, template_id: int, template_in: TemplateUpdate) -> Optional[Template]:
        db_template = self.db.query(Template).filter(Template.id == template_id).first()
        if not db_template:
            return None
        update_data = template_in.dict(exclude_unset=True)
        if "content" in update_data and not self.validate_template_syntax(update_data["content"]):
            raise ValueError("Invalid Jinja2 template syntax.")
        for key, value in update_data.items():
            setattr(db_template, key, value)
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def delete_template(self, template_id: int) -> Optional[Template]:
        db_template = self.db.query(Template).filter(Template.id == template_id).first()
        if not db_template:
            return None
        self.db.delete(db_template)
        self.db.commit()
        return db_template

    def render_template(self, template_id: int, context: dict) -> Optional[str]:
        db_template = self.get_template(template_id)
        if not db_template:
            return None
        try:
            template = self.jinja_env.from_string(db_template.content)
            return template.render(context)
        except TemplateError as e:
            # Log the error for debugging
            print(f"Jinja2 rendering error: {e}")
            return None

    def validate_template_syntax(self, template_content: str) -> bool:
        """
        Validates the Jinja2 syntax of a template.
        """
        try:
            self.jinja_env.from_string(template_content)
            return True
        except TemplateError as e:
            print(f"Jinja2 syntax error: {e}")
            return False

    def clone_template(self, template_id: int, new_name: str, new_version: str = "1.0") -> Optional[Template]:
        original_template = self.get_template(template_id)
        if not original_template:
            return None
        
        cloned_template_in = TemplateCreate(
            name=new_name,
            description=f"Cloned from {original_template.name} (ID: {original_template.id})",
            content=original_template.content,
            document_type=original_template.document_type,
            jurisdiction=original_template.jurisdiction,
            version=new_version,
            author=original_template.author,
            is_active=original_template.is_active
        )
        return self.create_template(cloned_template_in)
