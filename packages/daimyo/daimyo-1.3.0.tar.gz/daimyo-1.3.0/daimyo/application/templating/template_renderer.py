"""Template rendering service using Jinja2."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, StrictUndefined, UndefinedError

from daimyo.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from daimyo.domain import Category, MergedScope

logger = get_logger(__name__)

TEMPLATE_PATTERN = re.compile(r"\{\{.*?\}\}|\{%.*?%\}")


class TemplateRenderer:
    """Renders Jinja2 templates in rule text with strict undefined checking.

    Features:
    - Strict mode: Raises TemplateRenderingError if variable is undefined
    - Auto-detection: Only processes strings with {{ }} or {% %} syntax
    - Rich context: Provides config, scope metadata, category info
    """

    def __init__(self, settings: Any):
        """Initialize renderer with Dynaconf settings.

        :param settings: Dynaconf settings object
        :type settings: Any
        """
        self.settings = settings

        self.env = Environment(
            undefined=StrictUndefined,
            autoescape=False,
        )

    def needs_rendering(self, text: str) -> bool:
        """Check if text contains template syntax.

        :param text: Text to check
        :type text: str
        :returns: True if text contains {{ }} or {% %}
        :rtype: bool
        """
        return bool(TEMPLATE_PATTERN.search(text))

    def render_rule_text(
        self,
        text: str,
        scope: MergedScope,
        category: Category | None = None,
    ) -> str:
        """Render a rule text template.

        :param text: Rule text (may contain templates)
        :type text: str
        :param scope: Merged scope for context
        :type scope: MergedScope
        :param category: Optional category for context
        :type category: Category | None
        :returns: Rendered text
        :rtype: str
        :raises TemplateRenderingError: If template variable is undefined
        """
        if not self.needs_rendering(text):
            return text

        context = self._build_context(scope, category)

        try:
            template = self.env.from_string(text)
            result = template.render(context)
            logger.debug(f"Rendered template: {text[:50]}... → {result[:50]}...")
            return result

        except UndefinedError as e:
            from daimyo.domain import TemplateRenderingError

            match = re.search(r"'([^']+)' is undefined", str(e))
            variable_name = match.group(1) if match else "unknown"

            context_info = f"scope '{scope.metadata.name}'"
            if category:
                context_info += f", category '{category.key}'"

            raise TemplateRenderingError(
                template_text=text,
                variable_name=variable_name,
                context_info=context_info,
            ) from e

    def render_category_when(
        self,
        when_text: str,
        scope: MergedScope,
        category: Category,
    ) -> str:
        """Render a category 'when' description template.

        :param when_text: Category when description
        :type when_text: str
        :param scope: Merged scope for context
        :type scope: MergedScope
        :param category: Category for context
        :type category: Category
        :returns: Rendered when description
        :rtype: str
        :raises TemplateRenderingError: If template variable is undefined
        """
        return self.render_rule_text(when_text, scope, category)

    def _build_context(
        self,
        scope: MergedScope,
        category: Category | None = None,
    ) -> dict[str, Any]:
        """Build Jinja2 context dictionary.

        :param scope: Merged scope
        :type scope: MergedScope
        :param category: Optional category
        :type category: Category | None
        :returns: Context dictionary for template rendering
        :rtype: dict[str, Any]
        """
        context: dict[str, Any] = {}

        for key, value in self.settings.as_dict().items():
            if isinstance(value, (str, int, bool, float, type(None))):
                context[key] = value

        context["scope"] = {
            "name": scope.metadata.name,
            "description": scope.metadata.description,
            "tags": scope.metadata.tags,
            "sources": scope.sources,
        }

        if category:
            context["category"] = {
                "key": str(category.key),
                "when": category.when,
            }

        return context


__all__ = ["TemplateRenderer"]
