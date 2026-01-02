import pytest
import logging
from pathlib import Path

from pydantic import BaseModel
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(name)-12s: %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

from webtestpilot import WebTestPilot, Config, Session, Step


class TestCase(BaseModel):
    name: str
    steps: list[Step]


class JSONFile(pytest.File):
    def collect(self):
        name = self.path.name
        return [JSONItem.from_parent(self, name=name)]


class JSONItem(pytest.Item):
    def __init__(self, name, parent: JSONFile):
        super().__init__(name, parent)
        self.path: Path = Path(parent.path)
        self.url = self.parent.config.getoption("--url")
        self.cdp_endpoint = self.parent.config.getoption("--cdp-endpoint")

    def runtest(self):
        test_case = TestCase.model_validate_json(self.path.open("r", encoding="utf-8").read())
        logger.info(f"Name: {test_case.name} ({len(test_case.steps)} Steps)")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(self.cdp_endpoint)
            context = browser.contexts[0] if browser.contexts else browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()
            page.goto(self.url, timeout=0)

            config = Config.load()
            session = Session(page=page, config=config)

            steps = [
                step if i == len(steps) - 1
                else step.copy(update={"expectation": ""})
                for i, step in enumerate(test_case.steps)
            ]
            WebTestPilot.run(session=session, steps=steps, assertion=True)

    def repr_failure(self, excinfo):
        return f"Test {self.name} failed: {excinfo.value}"

    def reportinfo(self):
        return str(self.path), 0, f"Test: {self.name}"


def pytest_addoption(parser):
    parser.addoption(
        "--url",
        action="store",
        required=True,
        help="Base URL to use for JSON tests (required)",
    )
    parser.addoption(
        "--cdp-endpoint",
        action="store",
        default="http://localhost:9222",
        help="CDP endpoint for connecting to the browser (default: http://localhost:9222)",
    )


def pytest_configure(config):
    config.option.log_cli = True
    config.option.log_cli_level = "INFO"


def pytest_collect_file(file_path: Path, parent) -> JSONFile | None:
    if file_path.suffix.lower().lstrip(".") == "json":
        return JSONFile.from_parent(parent=parent, path=file_path)
    return None


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        if isinstance(item, JSONItem):
            item._nodeid = item.path.name