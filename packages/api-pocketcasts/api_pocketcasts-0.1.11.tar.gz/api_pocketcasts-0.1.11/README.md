
# Pocket Casts Python API Client

A robust, fully tested, and well-documented Python client for the Pocket Casts API. Supports synchronous usage, secure in-memory authentication, and a standardized error handling model.


## Features

- Synchronous API client
- Secure authentication (tokens/credentials only in memory)
- Standardized error structure (`code`, `message`, `details`)
- Extensible data models using `attrs`
- Full unit and integration test coverage
- Python 3.7+ support
- No persistent storage or database layer


## Data Models

All data models are defined using the `attrs` library for consistency and reliability. For details and examples, see [API Reference](docs/usage.md) and [data-model.md](reference/data-model.md).


## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/yfhyou/api_pocketcasts.git
cd api_pocketcasts
pip install -e .
```

Dependencies are managed in `pyproject.toml`.
## Usage

```python
from api_pocketcasts.client import PocketCastsClient
client = PocketCastsClient()
user = client.login_pocket_casts("your@email.com", "yourpassword")
print(user.email, user.access_token)
```

See [Usage Guide](docs/usage.md) for more examples, including async usage and error handling.

## Error Handling

All API errors use a standardized structure:

- `code`: Short error code (e.g., `auth_error`)
- `message`: Human-readable error message
- `details`: Additional error context (dict)

Example:

```python
from api_pocketcasts.exceptions import PocketCastsAuthError
try:
	user = client.login_pocket_casts("bad@example.com", "wrong")
except PocketCastsAuthError as e:
	print(f"Error code: {e.code}")
	print(f"Message: {e.message}")
	print(f"Details: {e.details}")
```

See [docs/usage.md](docs/usage.md#error-handling) for details.

## Documentation

- [Usage Guide](docs/usage.md)
- [API Reference](reference/data-model.md)
- [Endpoints](reference/endpoints.md)
- [Feature Plan](reference/plan.md)



## Testing & Test Documentation Standards

All tests are written using `pytest` and follow these documentation standards:

- **Module-Level Docstring**: Each test file should begin with a docstring describing the overall purpose of the test suite, what is covered, and any setup/teardown requirements.
- **Function Docstrings**: Every test function must have a concise docstring explaining the scenario being tested, what is simulated, and the expected outcome.
- **Descriptive Test Names**: Test function names should clearly state what is being tested and under what condition (e.g., `test_login_generic_http_error`).
- **pytest Markers**: Use markers like `@pytest.mark.unit` or `@pytest.mark.integration` to categorize tests.
- **No Redundant Comments**: Avoid comments that simply restate the function name or docstring.

**Example:**

```python
"""
Unit tests for Pocket Casts API authentication and token refresh logic.

This test suite covers error handling, edge cases, and expected behaviors for:
- User login (including HTTP errors, malformed responses, timeouts, and invalid credentials)
- Token refresh (success, malformed response, unexpected errors, and empty tokens)
"""

@pytest.mark.unit
def test_login_generic_http_error(monkeypatch):
	"""
	Simulate a generic HTTP 500 error during login.
	Ensures PocketCastsAuthError is raised when the API returns a server error.
	"""
	# ...test code...
```

This approach ensures tests are self-explanatory, maintainable, and easy for contributors to understand.


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing, coding standards, and submitting issues or pull requests.



## License

See [LICENSE](LICENSE) for license information.