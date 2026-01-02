"""Strategy enumerations for prompt handling."""


class DelimitingStrategy(str):
    """Enumeration of delimiting strategies for prompt templates."""

    NONE = "none"
    MARKDOWN = "markdown"
    XML = "xml"
    MARKER = "marker"
    ANGLE_BRACKETS = "angle_brackets"


class DefenseStrategy(str):
    """Enumeration of defense strategies for prompt templates."""

    PERPLEXITY_CHECK = "perplexity_check"
    CLASSIFY_INTENT = "classify_intent"
    REWRITE = "rewrite"
