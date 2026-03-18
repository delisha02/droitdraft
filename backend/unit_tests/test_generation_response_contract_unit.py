from datetime import datetime
import importlib.util
from pathlib import Path
import sys
from types import ModuleType


class _BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


_pydantic_stub = ModuleType("pydantic")
_pydantic_stub.BaseModel = _BaseModel
_old_pydantic = sys.modules.get("pydantic")
sys.modules["pydantic"] = _pydantic_stub

_DOC_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "app" / "schemas" / "document.py"
_SPEC = importlib.util.spec_from_file_location("document_schema_under_test", _DOC_SCHEMA_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
GeneratedDocumentResponse = _MODULE.GeneratedDocumentResponse

if _old_pydantic is None:
    sys.modules.pop("pydantic", None)
else:
    sys.modules["pydantic"] = _old_pydantic


def test_generated_document_response_defaults_retrieval_sources_to_empty_list():
    model = GeneratedDocumentResponse(
        id=1,
        title="Draft",
        content="Body",
        owner_id=10,
        created_at=datetime.utcnow(),
        updated_at=None,
    )

    assert model.retrieval_sources == []


def test_generated_document_response_preserves_retrieval_source_contract_shape():
    model = GeneratedDocumentResponse(
        id=2,
        title="Draft 2",
        content="Body",
        owner_id=10,
        created_at=datetime.utcnow(),
        updated_at=None,
        retrieval_sources=[
            {"title": "Case A", "source": "SCC", "url": "https://example.test/case-a", "id": "abc"}
        ],
    )

    assert isinstance(model.retrieval_sources, list)
    assert model.retrieval_sources[0]["title"] == "Case A"
    assert "source" in model.retrieval_sources[0]
