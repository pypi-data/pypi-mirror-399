#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from .exceptions import StrategyCompileError
from ..language import text


def compile_strategy(source_code, strategy, scope):
    """编译用户策略，生成包含策略代码的可执行域
    :param source_code: 策略源码
    :param strategy: 策略文件名
    :param scope: dict, 策略代码上下文
    :return: scope, 其中包含策略必须函数, 如:'init', 'on_data'
    :raise StrategyCompileError
    """

    try:
        code = compile(source_code, strategy, 'exec')
        exec(code, scope)
        return scope
    except Exception as e:
        raise StrategyCompileError(text.ERROR_COMPILE_STRATEGY) from e

def exit_wrapper(exit_code=0):
    try:
        sys.exit(exit_code)
    except NameError:
        pass
