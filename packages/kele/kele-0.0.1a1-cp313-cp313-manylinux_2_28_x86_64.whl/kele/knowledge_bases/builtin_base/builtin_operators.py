from typing import TypeGuard

from kele.syntax import Operator, Constant, Variable, FlatCompoundTerm
from kele.knowledge_bases.builtin_base.builtin_concepts import COMPLEX_NUMBER_CONCEPT, EQUATION_CONCEPT


def _is_constant(x: Constant | Variable) -> TypeGuard[Constant]:
    return isinstance(x, Constant)


def _unpack2_numbers(term: FlatCompoundTerm):  # type: ignore[no-untyped-def]  # noqa: ANN202
    a0, a1 = term.arguments
    if not _is_constant(a0) or not _is_constant(a1):
        raise TypeError(f"This operator expects Constant arguments, got{[str(a0), str(a1)]} .")
    return a0.symbol, a1.symbol


def _unpack1_number(term: FlatCompoundTerm):  # type: ignore[no-untyped-def]  # noqa: ANN202
    a0 = term.arguments[0]
    if not _is_constant(a0):
        raise TypeError("This operator expects a Constant argument, not a Variable.")
    return a0.symbol


def _plus(term: FlatCompoundTerm) -> Constant:
    v0, v1 = _unpack2_numbers(term)
    return Constant(v0 + v1, COMPLEX_NUMBER_CONCEPT)


arithmetic_plus_op = Operator(
    name="arithmetic_plus_op",
    input_concepts=[COMPLEX_NUMBER_CONCEPT, COMPLEX_NUMBER_CONCEPT],
    output_concept=COMPLEX_NUMBER_CONCEPT,
    implement_func=_plus,
)


def _minus(term: FlatCompoundTerm) -> Constant:
    v0, v1 = _unpack2_numbers(term)
    return Constant(v0 - v1, COMPLEX_NUMBER_CONCEPT)


arithmetic_minus_op = Operator(
    name="arithmetic_minus_op",
    input_concepts=[COMPLEX_NUMBER_CONCEPT, COMPLEX_NUMBER_CONCEPT],
    output_concept=COMPLEX_NUMBER_CONCEPT,
    implement_func=_minus,
)


def _times(term: FlatCompoundTerm) -> Constant:
    v0, v1 = _unpack2_numbers(term)
    return Constant(v0 * v1, COMPLEX_NUMBER_CONCEPT)


arithmetic_times_op = Operator(
    name="arithmetic_times_op",
    input_concepts=[COMPLEX_NUMBER_CONCEPT, COMPLEX_NUMBER_CONCEPT],
    output_concept=COMPLEX_NUMBER_CONCEPT,
    implement_func=_times,
)


def _divide(term: FlatCompoundTerm) -> Constant:
    v0, v1 = _unpack2_numbers(term)
    if v1 == 0:
        raise ZeroDivisionError("Division by zero in arithmetic_divide_op.")
    return Constant(v0 / v1, COMPLEX_NUMBER_CONCEPT)


arithmetic_divide_op = Operator(
    name="arithmetic_divide_op",
    input_concepts=[COMPLEX_NUMBER_CONCEPT, COMPLEX_NUMBER_CONCEPT],
    output_concept=COMPLEX_NUMBER_CONCEPT,
    implement_func=_divide,
)


def _negate(term: FlatCompoundTerm) -> Constant:
    v0 = _unpack1_number(term)
    return Constant(-v0, COMPLEX_NUMBER_CONCEPT)


arithmetic_negate_op = Operator(
    name="arithmetic_negate_op",
    input_concepts=[COMPLEX_NUMBER_CONCEPT],
    output_concept=COMPLEX_NUMBER_CONCEPT,
    implement_func=_negate,
)

get_arithmetic_equation_op = Operator("get_arithmetic_equation_op", [COMPLEX_NUMBER_CONCEPT, COMPLEX_NUMBER_CONCEPT], EQUATION_CONCEPT)

# Example Operators
example_operator_1 = Operator(
    name="parent_example",
    input_concepts=['Person_Example', 'Person_Example'],  # example_concept_1在builtin_concepts.py中定义
    # 我们在此处模拟“使用者自行声明本体的场景”，且concept和operator分别放置于两个文件内。此时系统无法直接定位到builtin_concepts.py
    # 的父目录，所以要么使用者使用字符串使用concept，要么需要自行控制sys.path或concept相关声明文件的位置，使得导入可以顺利进行。
    output_concept='Person_Example',
)
example_operator_2 = Operator(
    name="color_of_example",
    input_concepts=['Object_Example'],
    output_concept='Color_Example',
)
