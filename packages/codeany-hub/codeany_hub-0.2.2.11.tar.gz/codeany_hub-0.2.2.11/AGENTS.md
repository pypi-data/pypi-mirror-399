# AGENTS.md

> **Role**: expert Software Engineer specializing in Python SDK development.
> **Goal**: Maintain and improve the `codeany-hub` Python SDK with high standards of reliability and stability.

## ⚡ Commands

Use these commands to validate your work. **Always** run tests before submitting changes.

```bash
# Install dependencies (ensure runtime and tooling deps)
pip install -r requirements.txt
pip install -e ".[dev]"

# Run full test suite (Lint + Pytest)
./scripts/run_tests.sh

# Run specific tests
pytest tests/test_tasks_client.py

# Format code
ruff format .

# Check types
mypy src/codeany_hub
```

## 🌟 Golden Rules & Boundaries

1.  **Preserve public API stability**: Never introduce breaking changes without an explicit migration note and version bump.
2.  **Prefer additions over modifications**: When backend behavior expands, add new optional arguments or models instead of altering existing ones.
3.  **Keep models tolerant**: All Pydantic models must inherit from `TolerantModel` (`extra="allow"`). Unknown fields should never break deserialization.
4.  **Document reasoning**: When decisions are non-trivial, add succinct comments or docstrings explaining the trade-offs.
5.  **Never commit secrets** (API keys, tokens).
6.  **No print statements** in library code; use `logging` or `warnings`.

## 🏗️ Project Structure

- `src/codeany_hub/clients/`: API Client definitions (e.g., `tasks.py`, `competitions.py`).
- `src/codeany_hub/models/`: Pydantic V2 models. **Must** inherit from `TolerantModel`.
- `src/codeany_hub/core/`: Transport, Auth, and Error handling utilities.
- `tests/`: Pytest suite using `httpx_mock`.
- `docs/`: Markdown documentation (MkDocs compatible).

## � Code Patterns

- **Transport pattern**: Reuse `codeany_hub.core.transport.Transport` for all outbound HTTP calls. Authentication refresh must always flow through `AuthStrategy`.
- **Error handling**: Wrap every HTTP call with `raise_for_response`. Resource clients should avoid try/except unless they augment context.
- **Pagination**: Return `Page[T]` models for paginated endpoints.
- **Filters**: Builder APIs must be chainable, immutable, and convert cleanly to query dictionaries via `.to_params()`.
- **Streaming endpoints**: Use `Transport.stream(...)` to inherit retry/auth logic.
- **Hub identifiers**: Backend routers expect `hub_name` (slug). Models should normalise slug/name, and clients must never rely on integer IDs for hub lookup.

## 🔄 Workflow Expectations

1.  **Plan before acting**: Outline the intended change (file list, new APIs, risks) and get user confirmation when the scope is ambiguous.
2.  **Use apply_patch where practical**: Limit full file rewrites to generated or brand-new files.
3.  **Validate format and style**: Prefer `scripts/run_tests.sh` before handing work back.
4.  **Surface risks early**: Highlight edge cases and missing test coverage in the final summary.
5.  **Keep docs aligned**: Update `README.md` and `docs/` whenever you add or change public SDK behaviour.

## 🚀 Release Checklist

Before cutting a new release:
1. Update `pyproject.toml` version.
2. Review `CHANGELOG.md` (create if missing).
3. Run `scripts/run_tests.sh` and integration tests.
4. Tag the release and publish to PyPI via `hatch build && twine upload dist/*`.

## 🧪 Testing

- **Mock External Calls**: Use `httpx_mock`. Never hit real APIs in unit tests.
- **Coverage**: Add tests for every new method or edge case.
- **If unsure**: Suggest tests or mocks whenever adding new request flows that rely on HTTP side effects.
