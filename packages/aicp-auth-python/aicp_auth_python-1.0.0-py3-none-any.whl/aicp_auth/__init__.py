"""
AICP Auth Library - Biblioteca de autenticação e autorização para Keycloak

Esta biblioteca fornece funcionalidades de autenticação e autorização para aplicações
Python, com suporte a Keycloak, JWT tokens e controle de acesso baseado em roles.

Uso on-premise:
    Para uso em soluções on-premise, esta biblioteca pode ser importada diretamente
    para lidar com instâncias Keycloak locais.
"""

from .client import KeycloakClient
from .types import AuthConfig, User, Permission, TokenInfo, AuthContext, MiddlewareOptions
from .exceptions import (
    AuthLibError, TokenVerificationError, InvalidTokenError,
    TokenExpiredError, InvalidAudienceError, InvalidIssuerError,
    PermissionDeniedError, RoleDeniedError, ConfigurationError, JWKSError
)
from .middleware import AuthMiddleware, flask_auth_middleware, fastapi_auth_middleware

__version__ = "1.0.0"
__author__ = "AI Cockpit Team"
__email__ = "team@ai-cockpit.com"

__all__ = [
    # Classes principais
    "KeycloakClient",
    "AuthMiddleware",
    
    # Tipos
    "AuthConfig",
    "User", 
    "Permission",
    "TokenInfo",
    "AuthContext",
    "MiddlewareOptions",
    
    # Exceções
    "AuthLibError",
    "TokenVerificationError",
    "InvalidTokenError",
    "TokenExpiredError",
    "InvalidAudienceError",
    "InvalidIssuerError",
    "PermissionDeniedError",
    "RoleDeniedError",
    "ConfigurationError",
    "JWKSError",
    
    # Funções de middleware
    "flask_auth_middleware",
    "fastapi_auth_middleware",
]
