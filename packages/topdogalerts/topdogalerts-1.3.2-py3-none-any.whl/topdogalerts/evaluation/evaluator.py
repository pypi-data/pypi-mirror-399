# topdogalerts/evaluation/evaluator.py
"""
Trigger evaluation logic for topdogalerts.

Evaluates event attributes against trigger conditions using either:
- boolean-expression: Traditional boolean expression parsing
- semantic-embedding: Sentence-transformer cosine similarity matching
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping

from ..models import EventTrigger, EventType
from ..managers import fetch_event_type, fetch_event_triggers_for_eventtype
from .expression_evaluator import (
    evaluate_expression,
    ExpressionEvaluationError,
)
from .expression_parser import ExpressionParseError

logger = logging.getLogger(__name__)

# Columns on EventTrigger that expressions are allowed to reference
TRIGGER_VALUE_FIELDS = (
    "number_value1",
    "number_value2",
    "number_value3",
    "number_value4",
    "string_value1",
    "string_value2",
    "string_value3",
    "string_value4",
    "datetime_value1",
    "datetime_value2",
)


def evaluate(
    attributes: Mapping[str, Any],
    eventtype_id: str,
) -> List[str]:
    """
    Evaluate an event's attributes against all triggers for the given event type.

    Dispatches to the appropriate evaluation method based on EventType.evaluation_method:
    - 'boolean-expression' (default): Traditional boolean expression evaluation
    - 'semantic-embedding': Sentence-transformer cosine similarity matching

    For boolean-expression, the trigger_expression in the EventType defines a boolean expression:

        product == string_value1 AND timeframe == string_value2 AND (
            (string_value3 == "up" AND prev_rsi < number_value1 AND rsi >= number_value1) OR
            (string_value3 == "down" AND prev_rsi > number_value1 AND rsi <= number_value1)
        )

    Variables in the expression can reference:
        - Event attributes: product, timeframe, rsi, prev_rsi, etc.
        - Trigger values: string_value1, number_value1, etc.

    For semantic-embedding, triggers use:
        - string_value1: Comma-separated keywords/phrases
        - number_value1: Similarity threshold (0-100 percentage)

    Attributes must include 'content_embedding_string' (text to encode) for semantic matching.

    Args:
        attributes: The event attributes to evaluate (matches attribute_schema).
        eventtype_id: The ID of the event type to evaluate against.

    Returns:
        List of trigger IDs (as strings) whose conditions are satisfied.
    """
    # Load the EventType to determine evaluation method
    event_type = fetch_event_type(eventtype_id)
    evaluation_method = event_type.evaluation_method or "boolean-expression"

    if evaluation_method == "semantic-embedding":
        return _evaluate_semantic(attributes, event_type)
    else:
        return _evaluate_boolean_expression(attributes, event_type)


def _evaluate_boolean_expression(
    attributes: Mapping[str, Any],
    event_type: EventType,
) -> List[str]:
    """
    Evaluate using traditional boolean expression matching.

    Args:
        attributes: The event attributes to evaluate.
        event_type: The EventType containing the trigger expression.

    Returns:
        List of matching trigger IDs.
    """
    trigger_expression = event_type.trigger_expression
    if not trigger_expression:
        logger.warning(
            f"EventType {event_type.id} has no trigger_expression, skipping evaluation"
        )
        return []

    # Fetch all triggers for this event type
    triggers = fetch_event_triggers_for_eventtype(event_type.id)

    matching_trigger_ids: List[str] = []

    for trigger in triggers:
        # Skip disabled triggers
        if trigger.enabled is False:
            continue

        if _trigger_matches_event(attributes, trigger, trigger_expression):
            matching_trigger_ids.append(trigger.id)

    return matching_trigger_ids


def _evaluate_semantic(
    attributes: Mapping[str, Any],
    event_type: EventType,
) -> List[str]:
    """
    Evaluate using semantic embedding similarity.

    Triggers for semantic evaluation use:
        - string_value1: Comma-separated keywords/phrases
        - number_value1: Similarity threshold (0-100 percentage)

    Args:
        attributes: Must include 'content_embedding_string' (text to encode).
        event_type: The EventType to evaluate against.

    Returns:
        List of matching trigger IDs.
    """
    from .semantic_evaluator import (
        encode_text,
        evaluate_semantic_trigger,
        SemanticEvaluationError,
    )

    content_embedding_string = attributes.get("content_embedding_string")
    if not content_embedding_string:
        logger.warning(
            f"EventType {event_type.id} uses semantic-embedding but "
            "attributes missing 'content_embedding_string'"
        )
        return []

    # Compute embedding from the content string
    logger.debug(f"Content for semantic evaluation: '{content_embedding_string[:100]}...'")
    try:
        content_embedding = encode_text(content_embedding_string)
    except SemanticEvaluationError as e:
        logger.error(f"Failed to compute embedding: {e}")
        return []

    # Fetch all triggers for this event type
    triggers = fetch_event_triggers_for_eventtype(event_type.id)

    matching_trigger_ids: List[str] = []

    for trigger in triggers:
        # Skip disabled triggers
        if trigger.enabled is False:
            continue

        keywords_csv = trigger.string_value1
        threshold_percent = trigger.number_value1

        if not keywords_csv:
            logger.warning(
                f"Trigger {trigger.id} has no keywords (string_value1) - "
                "this trigger will never fire"
            )
            continue

        if threshold_percent is None:
            logger.warning(
                f"Trigger {trigger.id} has no threshold (number_value1) - "
                "this trigger will never fire"
            )
            continue

        try:
            logger.debug(f"Evaluating trigger {trigger.id}")
            if evaluate_semantic_trigger(
                content_embedding, keywords_csv, float(threshold_percent)
            ):
                matching_trigger_ids.append(trigger.id)
        except SemanticEvaluationError as e:
            logger.error(f"Semantic evaluation error for trigger {trigger.id}: {e}")
        except Exception as e:
            logger.exception(
                f"Unexpected error in semantic evaluation for trigger {trigger.id}: {e}"
            )

    return matching_trigger_ids


def _trigger_matches_event(
    attributes: Mapping[str, Any],
    trigger: EventTrigger,
    trigger_expression: str,
) -> bool:
    """
    Check if a trigger matches the event attributes using the expression.

    Args:
        attributes: The event attributes to evaluate.
        trigger: The trigger to evaluate against.
        trigger_expression: The boolean expression from EventType.

    Returns:
        True if the expression evaluates to True, False otherwise.
    """
    # Build trigger values dict from the trigger's value columns
    trigger_values = _build_trigger_values(trigger)

    try:
        return evaluate_expression(
            trigger_expression,
            dict(attributes),
            trigger_values,
        )
    except ExpressionParseError as e:
        # Malformed expression - this is a configuration error
        logger.error(
            f"Expression parse error for trigger {trigger.id}: {e}. "
            f"Expression: {trigger_expression!r}"
        )
        return False
    except ExpressionEvaluationError as e:
        # Evaluation failed - likely a typo in variable name or type mismatch
        logger.error(
            f"Expression evaluation error for trigger {trigger.id}: {e}. "
            f"Attributes: {list(attributes.keys())}, "
            f"Trigger values: {list(trigger_values.keys())}"
        )
        return False
    except Exception as e:
        # Unexpected error
        logger.exception(
            f"Unexpected error evaluating trigger {trigger.id}: {e}. "
            f"Expression: {trigger_expression!r}"
        )
        return False


def _build_trigger_values(trigger: EventTrigger) -> Dict[str, Any]:
    """
    Extract trigger values from an EventTrigger instance.

    Returns a dict with all non-None value fields.
    """
    values: Dict[str, Any] = {}
    for field in TRIGGER_VALUE_FIELDS:
        value = getattr(trigger, field, None)
        if value is not None:
            values[field] = value
    return values
