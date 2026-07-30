import math

from calculator import SafeEvaluator


def test_scientific_functions_evaluate():
    evaluator = SafeEvaluator()
    assert evaluator.visit(__import__('ast').parse('sin(0)', mode='eval')) == 0.0
    assert evaluator.visit(__import__('ast').parse('cos(0)', mode='eval')) == 1.0
    assert evaluator.visit(__import__('ast').parse('sqrt(16)', mode='eval')) == 4.0
    assert evaluator.visit(__import__('ast').parse('pi', mode='eval')) == math.pi
