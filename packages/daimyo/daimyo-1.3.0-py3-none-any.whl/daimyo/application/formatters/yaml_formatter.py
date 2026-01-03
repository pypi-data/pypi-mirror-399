"""YAML multi-document formatter for server federation."""

from typing import TYPE_CHECKING, Any

import yaml

from daimyo.domain import Category, MergedScope, RuleSet

if TYPE_CHECKING:
    from daimyo.application.templating import TemplateRenderer


class YamlMultiDocFormatter:
    """Format merged scope as multi-document YAML.

    Output contains 3 YAML documents separated by '---':
    1. Metadata document
    2. Commandments document
    3. Suggestions document

    This format is useful for server federation where a server needs to
    parse and overlay rules from another server.
    """

    def __init__(self, template_renderer: "TemplateRenderer | None" = None):
        """Initialize formatter.

        :param template_renderer: Optional template renderer
        :type template_renderer: TemplateRenderer | None
        """
        self.template_renderer = template_renderer

    def format(self, scope: MergedScope) -> str:
        """Format merged scope as multi-document YAML.

        :param scope: The merged scope to format
        :type scope: MergedScope
        :returns: Multi-document YAML string
        :rtype: str
        """
        documents = []

        metadata_doc = {
            "metadata": {
                "name": scope.metadata.name,
                "description": scope.metadata.description,
                "parent": scope.metadata.parent,
                "tags": scope.metadata.tags,
                "sources": scope.sources,
            }
        }
        documents.append(metadata_doc)

        commandments_doc = {"commandments": self._format_ruleset(scope.commandments, scope)}
        documents.append(commandments_doc)

        suggestions_doc = {"suggestions": self._format_ruleset(scope.suggestions, scope)}
        documents.append(suggestions_doc)

        yaml_parts = []
        for doc in documents:
            yaml_str = yaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False)
            yaml_parts.append(yaml_str)

        return "---\n".join(yaml_parts)

    def _render_text(self, text: str, scope: MergedScope, category: Category | None = None) -> str:
        """Render text template if renderer available."""
        if self.template_renderer:
            return self.template_renderer.render_rule_text(text, scope, category)
        return text

    def _format_ruleset(self, ruleset: RuleSet, scope: MergedScope) -> dict[str, Any]:
        """Format a ruleset as nested dictionary.

        :param ruleset: The ruleset to format
        :type ruleset: RuleSet
        :param scope: Scope for template rendering
        :type scope: MergedScope
        :returns: Nested dictionary representation
        :rtype: Dict[str, Any]
        """
        result: dict[str, Any] = {}

        for category in ruleset.categories.values():
            parts = category.key.parts
            current = result

            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    rendered_when = self._render_text(category.when, scope, category)
                    rendered_rules = [
                        self._render_text(rule.text, scope, category) for rule in category.rules
                    ]

                    current[part] = {
                        "when": rendered_when,
                        "ruleset": rendered_rules,
                    }
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

        return result


__all__ = ["YamlMultiDocFormatter"]
