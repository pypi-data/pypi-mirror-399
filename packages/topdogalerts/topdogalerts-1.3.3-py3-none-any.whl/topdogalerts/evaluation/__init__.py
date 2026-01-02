# topdogalerts/evaluation/__init__.py
"""
Trigger evaluation module for topdogalerts.

Provides two evaluation methods:
- boolean-expression: Boolean expression parsing and evaluation for trigger matching
- semantic-embedding: Sentence-transformer cosine similarity for semantic matching
"""
from .evaluator import evaluate
from .expression_ast import BinaryOp, Expression, Literal, UnaryOp, Variable
from .expression_evaluator import (
    ExpressionEvaluationError,
    ExpressionEvaluator,
    evaluate_expression,
    validate_expression,
)
from .expression_parser import (
    ExpressionParseError,
    Parser,
    Tokenizer,
    parse_expression,
)
from .semantic_evaluator import (
    SemanticEvaluationError,
    encode_text,
    compute_max_similarity,
    evaluate_semantic_trigger,
    clear_keyword_cache,
)

__all__ = [
    # Main entry point
    "evaluate",
    # Expression evaluation (boolean)
    "evaluate_expression",
    "validate_expression",
    "ExpressionEvaluator",
    "ExpressionEvaluationError",
    # Expression parsing
    "parse_expression",
    "Parser",
    "Tokenizer",
    "ExpressionParseError",
    # AST nodes
    "Expression",
    "Literal",
    "Variable",
    "BinaryOp",
    "UnaryOp",
    # Semantic evaluation
    "encode_text",
    "compute_max_similarity",
    "evaluate_semantic_trigger",
    "clear_keyword_cache",
    "SemanticEvaluationError",
]
