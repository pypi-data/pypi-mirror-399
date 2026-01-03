"""Domain layer - core business models and logic."""

from .exceptions import (
    CircularDependencyError,
    DaimyoError,
    FormatterError,
    InheritanceDepthExceededError,
    InvalidCategoryError,
    InvalidScopeError,
    RemoteScopeUnavailableError,
    RemoteServerError,
    ScopeMergingError,
    ScopeNotFoundError,
    TemplateRenderingError,
    YAMLParseError,
)
from .models import (
    Category,
    CategoryKey,
    MergedScope,
    Rule,
    RuleSet,
    RuleType,
    Scope,
    ScopeMetadata,
)
from .protocols import FormatterProtocol, RemoteScopeClient, ScopeRepository

__all__ = [
    "Rule",
    "RuleType",
    "Category",
    "CategoryKey",
    "RuleSet",
    "Scope",
    "ScopeMetadata",
    "MergedScope",
    "DaimyoError",
    "ScopeNotFoundError",
    "InvalidScopeError",
    "CircularDependencyError",
    "InheritanceDepthExceededError",
    "RemoteServerError",
    "RemoteScopeUnavailableError",
    "ScopeMergingError",
    "FormatterError",
    "InvalidCategoryError",
    "TemplateRenderingError",
    "YAMLParseError",
    "ScopeRepository",
    "RemoteScopeClient",
    "FormatterProtocol",
]
