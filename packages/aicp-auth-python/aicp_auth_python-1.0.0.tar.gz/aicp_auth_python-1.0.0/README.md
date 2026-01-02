# aicp-auth-python

Biblioteca de autenticação e autorização para Keycloak - Python

## Instalação

```bash
pip install aicp-auth-python
```

## Uso

### Flask

```python
from aicp_auth import flask_auth_middleware, AuthConfig

config = AuthConfig(
    url="https://keycloak.example.com",
    realm="my-realm",
    client_id="my-client"
)

@app.route('/api/protected')
@flask_auth_middleware(config)
def protected_route():
    return {'user': g.user.__dict__}
```

### FastAPI

```python
from aicp_auth import fastapi_auth_middleware, AuthConfig, User

config = AuthConfig(
    url="https://keycloak.example.com",
    realm="my-realm",
    client_id="my-client"
)

get_current_user = fastapi_auth_middleware(config)

@app.get('/api/protected')
def protected_route(user: User = Depends(get_current_user)):
    return {'user': user.__dict__}
```

## Documentação Completa

Veja a [documentação principal](../../README.md) para mais detalhes.

