"""JSON formatter for API responses."""

from typing import TYPE_CHECKING, Any

from daimyo.domain import Category, MergedScope, RuleSet

if TYPE_CHECKING:
    from daimyo.application.templating import TemplateRenderer


class JsonFormatter:
    """Format merged scope as JSON.

    Output contains structured JSON with metadata, commandments, and suggestions.
    """

    def __init__(self, template_renderer: "TemplateRenderer | None" = None):
        """Initialize formatter.

        :param template_renderer: Optional template renderer
        :type template_renderer: TemplateRenderer | None
        """
        self.template_renderer = template_renderer

    def format(self, scope: MergedScope) -> dict[str, Any]:
        """Format merged scope as JSON-serializable dictionary.

        :param scope: The merged scope to format
        :type scope: MergedScope
        :returns: Dictionary ready for JSON serialization
        :rtype: Dict[str, Any]
        """
        return {
            "metadata": {
                "name": scope.metadata.name,
                "description": scope.metadata.description,
                "parent": scope.metadata.parent,
                "tags": scope.metadata.tags,
                "sources": scope.sources,
            },
            "commandments": self._format_ruleset(scope.commandments, scope),
            "suggestions": self._format_ruleset(scope.suggestions, scope),
        }

    def _render_text(self, text: str, scope: MergedScope, category: Category | None = None) -> str:
        """Render text template if renderer available."""
        if self.template_renderer:
            return self.template_renderer.render_rule_text(text, scope, category)
        return text

    def _format_ruleset(self, ruleset: RuleSet, scope: MergedScope) -> dict[str, dict[str, Any]]:
        """Format a ruleset as flat dictionary with category keys.

        :param ruleset: The ruleset to format
        :type ruleset: RuleSet
        :param scope: Scope for template rendering
        :type scope: MergedScope
        :returns: Dictionary mapping category keys to their data
        :rtype: Dict[str, Dict[str, Any]]
        """
        result = {}

        for category in ruleset.categories.values():
            rendered_when = self._render_text(category.when, scope, category)
            rendered_rules = [
                self._render_text(rule.text, scope, category) for rule in category.rules
            ]

            result[str(category.key)] = {
                "when": rendered_when,
                "rules": rendered_rules,
            }

        return result


__all__ = ["JsonFormatter"]
