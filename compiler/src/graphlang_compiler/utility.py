from typing import Iterable, Union

import shortuuid

from graphlang_compiler.eval_result import EvalResult


def some_util(*results: Union[EvalResult, Iterable[EvalResult]]):
    expressions, binds = [], {}

    for result in results:
        if isinstance(result, Iterable):
            sub_expressions = []

            for sub_result in result:
                sub_result: EvalResult
                sub_expressions.append(sub_result.expression)
                binds.update(sub_result.binds)

            expressions += (sub_expressions)
        else:
            expressions.append(result.expression)
            binds.update(result.binds)

    return [binds] + expressions


def unique_name():
    return f'u{shortuuid.uuid()[:12]}'
