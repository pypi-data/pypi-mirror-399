# Authentication

The Codeany SDK supports flexible authentication strategies suitable for local development, CI/CD pipelines, and deployed applications.

## Authentication Strategies

### Simple JWT
Uses a username and password to obtain a JWT pair (access/refresh tokens). Best for personal use or scripts running on behalf of a user.

### Hub Login
Authenticates specifically against a Hub's identity provider. Required when accessing hub-specific resources that demand hub membership context.

## Environment Configuration

The easiest way to configure the client is via environment variables.

```bash
# Core
export CODEANY_BASE_URL="https://hub.codeany.dev"
export CODEANY_AUTH="simple_jwt"  # or "hub_login", "none"

# Credentials
export CODEANY_USERNAME="myuser"
export CODEANY_PASSWORD="mypassword"
export CODEANY_HUB="my-hub"       # Required format for hub_login

# Optional
export CODEANY_TOKEN_STORE_PATH=".codeany-tokens.json"
export CODEANY_TIMEOUT=30
export CODEANY_RETRIES=3
```

Then instantiate the client without arguments:

```python
from codeany_hub import CodeanyClient

client = CodeanyClient.from_env()
```

## Manual Instantiation

You can explicitly configure the client in code.

### Using Simple JWT

```python
from codeany_hub import CodeanyClient

client = CodeanyClient.with_simple_jwt(
    base_url="https://hub.codeany.dev",
    username="alice",
    password="secure_password"
)
```

### Using Hub Login

```python
client = CodeanyClient.with_hub_login(
    base_url="https://hub.codeany.dev",
    hub="awesome-hub",
    username="bob",
    password="secure_password"
)
```

### Async Client

The `AsyncCodeanyClient` supports the same factory methods.

```python
from codeany_hub import AsyncCodeanyClient

async_client = await AsyncCodeanyClient.from_env()
# or
async_client = await AsyncCodeanyClient.with_simple_jwt(...)
```

## Token Management

By default, the SDK uses an `InMemoryTokenStore`. Tokens are lost when the process exits.

To persist tokens across runs (avoiding repeated logins), use a `FileTokenStore`:

```python
from codeany_hub.core import FileTokenStore

store = FileTokenStore("tokens.json")

client = CodeanyClient.with_simple_jwt(
    ...,
    token_store=store
)
```

When using `from_env()`, set `CODEANY_TOKEN_STORE_PATH` to enable file persistence automatically.
