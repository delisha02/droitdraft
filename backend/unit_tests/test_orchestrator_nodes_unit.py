import asyncio
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace


class _FakeDB:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _FakeFact:
    def __init__(self, issue=None):
        self.issue = issue


class _FakeFactStructurer:
    def __init__(self, issue="Dishonour of cheque under NI Act"):
        self._issue = issue

    def structure_facts(self, extracted_entities, document_id, document_type):
        return _FakeFact(issue=self._issue)


def _load_agent_nodes_module():
    module_path = Path(__file__).resolve().parents[1] / "app" / "agents" / "orchestrator" / "agent_nodes.py"

    # Build lightweight stub modules needed by imports in agent_nodes.py
    app_mod = ModuleType("app")
    api_mod = ModuleType("app.api")
    deps_mod = ModuleType("app.api.deps")
    crud_mod = ModuleType("app.crud")

    template_obj = SimpleNamespace(content="Template body", title="Template title")

    def _get_db():
        db = _FakeDB()
        yield db

    deps_mod.get_db = _get_db
    crud_mod.template = SimpleNamespace(get=lambda db, id: template_obj)

    doc_gen_pkg = ModuleType("app.agents.document_generator")
    assembly_mod = ModuleType("app.agents.document_generator.assembly_engine")
    assembly_mod.assembly_engine = SimpleNamespace(assemble_document=None)

    ik_pkg = ModuleType("app.integrations.indiankanoon")
    ik_client_mod = ModuleType("app.integrations.indiankanoon.client")
    ik_query_mod = ModuleType("app.integrations.indiankanoon.query_builder")
    ik_client_mod.IndianKanoonClient = object
    ik_query_mod.IndianKanoonQueryBuilder = lambda q: q

    doc_proc_pkg = ModuleType("app.agents.document_processor")
    ner_mod = ModuleType("app.agents.document_processor.ner_engine")
    fact_mod = ModuleType("app.agents.document_processor.fact_structurer")
    ner_mod.extract_entities = lambda q: {"query": q}
    fact_mod.FactStructurer = _FakeFactStructurer

    orchestrator_pkg = ModuleType("app.agents.orchestrator")
    state_mod = ModuleType("app.agents.orchestrator.state_manager")
    state_mod.DroitAgentState = dict

    schemas_pkg = ModuleType("app.schemas")
    case_fact_mod = ModuleType("app.schemas.case_facts")
    case_fact_mod.CaseFact = _FakeFact

    api_mod.deps = deps_mod
    app_mod.api = api_mod
    app_mod.crud = crud_mod

    modules = {
        "app": app_mod,
        "app.api": api_mod,
        "app.api.deps": deps_mod,
        "app.crud": crud_mod,
        "app.agents": ModuleType("app.agents"),
        "app.agents.orchestrator": orchestrator_pkg,
        "app.agents.orchestrator.state_manager": state_mod,
        "app.agents.document_generator": doc_gen_pkg,
        "app.agents.document_generator.assembly_engine": assembly_mod,
        "app.integrations": ModuleType("app.integrations"),
        "app.integrations.indiankanoon": ik_pkg,
        "app.integrations.indiankanoon.client": ik_client_mod,
        "app.integrations.indiankanoon.query_builder": ik_query_mod,
        "app.agents.document_processor": doc_proc_pkg,
        "app.agents.document_processor.ner_engine": ner_mod,
        "app.agents.document_processor.fact_structurer": fact_mod,
        "app.schemas": schemas_pkg,
        "app.schemas.case_facts": case_fact_mod,
    }

    old = {name: sys.modules.get(name) for name in modules}
    try:
        sys.modules.update(modules)
        spec = importlib.util.spec_from_file_location("agent_nodes_under_test", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module
    finally:
        for name, previous in old.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def test_document_processor_requires_template_id():
    module = _load_agent_nodes_module()

    state = {"query": "Draft a legal notice"}
    try:
        asyncio.run(module.document_processor_node(state))
        assert False, "Expected ValueError for missing template_id"
    except ValueError as exc:
        assert "Template ID is missing" in str(exc)


def test_document_processor_derives_research_query_from_structured_facts():
    module = _load_agent_nodes_module()

    state = {"query": "Draft a legal notice", "template_id": 12}
    updated = asyncio.run(module.document_processor_node(state))

    assert updated["template_id"] == 12
    assert updated["research_query"] == "Dishonour of cheque under NI Act"


def test_get_template_node_sets_template_fields_and_closes_db():
    module = _load_agent_nodes_module()

    fake_db = _FakeDB()

    def _get_db():
        yield fake_db

    module.deps.get_db = _get_db
    module.crud.template = SimpleNamespace(get=lambda db, id: SimpleNamespace(content="Body", title="Notice"))

    state = {"template_id": 42}
    updated = asyncio.run(module.get_template_node(state))

    assert updated["template_content"] == "Body"
    assert updated["document_title"] == "Notice"
    assert fake_db.closed is True
