# -*- coding: utf-8 -*-

import os
from ..language import text
from .. import udefs

#################################
# 错误类

class AtraderError(Exception):
    """At 错误基类"""

    def __init__(self, *args, file=None, line=None, type_='s'):
        """
        :param args: 位置参数
        :param file: str,文件路径
        :param line: int, 错误行号
        :param type_: str, 's':系统日志, 'u': 用户日志, 'b': 系统/用户日志
        """
        self.file = file
        self.line = line
        self.level = type_
        super(AtraderError, self).__init__(*args)

    def __str__(self):
        s1 = '' if self.file is None else 'file:%s-' % self.file
        s2 = '' if self.file is None else 'line:%s-' % self.line
        return '%s%s%s:%s' % (self.__class__.__name__, s1, s2, ','.join([str(arg) for arg in self.args]))


class InvalidParamError(AtraderError):
    """参数错误"""
    pass


class NotSupportError(AtraderError):
    """不支持的异常, eg: 当前不支持的频数"""
    pass


class AtReturnError(AtraderError):
    """ATCore 返回的异常"""
    pass


class AtModeError(AtraderError):
    """模式不支持异常, eg: 回测模式时不能运行在实盘模式"""
    pass


class VersionError(AtraderError):
    """ATCore 和 atrader 版本信息"""
    pass


class NetWorkError(AtraderError):
    """网络通讯错误"""
    pass


class AtDataError(AtraderError):
    """获取的数据异常"""
    pass


class RunOnPhaseError(AtraderError):
    """运行在错误阶段, 比如函数只能运行在: 用户初始化阶段, 否则报错"""
    pass


class DataLoadError(AtraderError):
    """加载数据失败, eg: 加载 mat 文件失败"""
    pass


class UnExpectError(AtraderError):
    """未期望的异常, 正常情况下不应该出现错误. eg: 在类似 if-elif-else 分支中出现不当的条件"""
    pass


class StrategyCompileError(AtraderError):
    """编译错误"""
    pass


#################################
# 警告类


class AtraderWarning(Warning):
    """At 警告"""

    def __init__(self, *args, file=None, line=None):
        """
        :param args: 位置参数
        :param file: str,文件路径
        :param line: int, 错误行号
        """
        self.file = file
        self.line = line
        super(AtraderWarning, self).__init__(*args)

    def __str__(self):
        s1 = '' if self.file is None else 'file:%s-' % self.file
        s2 = '' if self.file is None else 'line:%s-' % self.line
        return '%s%s%s:%s' % (self.__class__.__name__, s1, s2, ','.join([str(arg) for arg in self.args]))


class InvalidParamWarning(AtraderWarning):
    """参数无效警告"""

    def __init__(self, *args, file=None, line=None):
        self.file = file
        self.line = line
        super(InvalidParamWarning, self).__init__(*args)


class DeprecatedWarning(AtraderWarning):
    """函数废弃警告"""

    def __init__(self, *args, file=None, line=None):
        self.file = file
        self.line = line
        super(DeprecatedWarning, self).__init__(*args)


#################################
# 接口函数

def raise_bultin_error(type_, line_num=None, file_name=None):
    """raise UnExpectError

    :param type_: str, 见 if 条件
    :param line_num: 错误行号
    :param file_name: 错误文件名称
    """

    if type_ == 'need3mode':
        raise AtModeError(text.ERROR_NOT3MODE)
    elif type_ == 'targettype':
        raise UnExpectError('not support target type, expect (TARGETTYPE_STOCK, TARGETTYPE_FUTURE)')
    elif type_ == 'offsetflag':
        raise UnExpectError('not support position effect, expect (PositionEffect_Open, PositionEffect_Close)')
    elif type_ == 'orderact':
        raise UnExpectError('not support orderact type, expect (OrderAct_Buy, OrderAct_Sell)')
    elif type_ == 'orderctg':
        raise UnExpectError('not support orderctg type, expect (OrderCtg_Limit, OrderCtg_Market)')
    elif type_ == 'stopgap':
        raise UnExpectError('not support stopgap type, expect (OrderStop_StopGap_Point, OrderStop_StopGap_Percent)')
    elif type_ == 'stopordertype':
        raise UnExpectError('not support stoporder type, expect (StopOrderType_Loss, StopOrderType_Profit, StopOrderType_Trailing)')
    elif type_ == 'runmode':
        raise UnExpectError('not support run mode expect (BackTest, RealTrade and Replay)')
    elif type_ == 'fq':
        raise UnExpectError('not support FQ type, expect(NA,FWard,BWard),NA:不复权,FWard:前复权,BWard:后复权')
    elif type_ == 'kfrequency':
        raise UnExpectError('not support KFrequency type, expect(min,day,sec,tick)')
    elif type_ == 'not_mode_func':
        raise UnExpectError('not a validate mode function')
    else:
        pass


def check_at_return_error(err, prefix=None, detail=None, suffix=None, isfile=False, error='raise'):
    """如果 AT 返回信息包含错误, 则抛出 AT 返回的错误信息, 否则什么也不做

    :param err: None or str, 错误信息
    :param prefix: None or str, 如果含有错误, 加在抛出错误信息头部的其他详细信息
    :param detail: None or str, 如果含有错误, detail 不为 None, 使用 detail 作为错误描述信息, 否则使用内部错误描述信息
    :param suffix: None or str, 如果包含错误, 加在抛出错误信息尾部的其他详细信息
    :param isfile: bool, True, 检查文件是否存在, 不存在抛出异常, 否则不做操作
    :param error: str, 支持: `raise`, `ignore`, 如果含有错误, 且 error 为 'raise'
    :return: 包含 3 种情况::

        | 当含有模式错误且 error 为 'raise' 时, 抛出 `AtReturnError`
        | 当含有模式错误且 error 不为 'raise' 时, 返回错误信息
        | 其他情况返回 None

    **example**

    假设 *at_return* 为 at 返回的值

    >>> at_return = 'Error_Sid'
    >>> check_at_return_error(at_return, suffix='Get K data error!')

    """

    inner = None
    prefix = '' if prefix is None else prefix
    suffix = '' if suffix is None else suffix
    comma_prefix = ',' if prefix else ''
    comma_suffix = ',' if suffix else ''
    if err is not None:
        err = str.lower(err)

    if err is None:
        inner = text.ERROR_NONE if detail is None else detail
    elif err == udefs.ATCORE_NO_DATA_RIGHT:
        inner = text.ERROR_DATA_NORIGHT if detail is None else detail
    elif err == udefs.ATCORE_ERROR_DATA:
        inner = text.ERROR_DATA if detail is None else detail
    elif err == udefs.ATCORE_ERROR_DATE:
        inner = text.ERROR_DATE if detail is None else detail
    elif err == udefs.ATCORE_ERROR_FILE:
        inner = text.ERROR_FILE if detail is None else detail
    elif err == udefs.ATCORE_ERROR_SID:
        inner = text.ERROR_SECURITY if detail is None else detail
    elif isfile and not os.path.exists(err):
        inner = text.ERROR_NOT_EXIST if detail is None else detail

    if inner is not None and error == 'raise':
        raise AtReturnError('{prefix}{comma_prefix}{error}{comma_suffix}{suffix}'.format(
            prefix=prefix,
            comma_prefix=comma_prefix,
            error=inner,
            comma_suffix=comma_suffix,
            suffix=comma_suffix))
    inner = err if inner is None else inner

    return inner
