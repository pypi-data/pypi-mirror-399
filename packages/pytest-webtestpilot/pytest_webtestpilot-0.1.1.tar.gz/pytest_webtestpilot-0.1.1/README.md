# pytest-webtestpilot 

pytest-webtestpilot is a pytest plugin that lets you run WebTestPilot test cases directly with pytest, enabling automated end-to-end testing of your web applications.

## Installation

```bash
pip install pytest-webtestpilot
```

## Usage

1. **Write Test Cases (`.json` Files)**

    Each test case is written as a JSON file describing user actions and expected outcomes. Example:

    ```json
    {
        "name": "Login and check dashboard",
        "steps": [
            {
                "action": "Click the login button",
                "expectation": "The dashboard page is displayed"
            },
            {
                "action": "Click the profile icon",
                "expectation": "User profile menu appears"
            }
        ]
    }
    ```

2. **Run Tests with Pytest**
    Use the following command to execute your test cases:

    ```bash
    uv run pytest [path to .json files or folders] -v --url [website URL]
    ```

    Example:

    ```bash
    uv run pytest tests/ -v --url https://example.com
    ```