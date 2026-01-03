

from dqtrader.tframe.language.chinese import text


class DQTraderError(Exception):
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
        super(DQTraderError, self).__init__(*args)

    def __str__(self):
        s1 = '' if self.file is None else 'file:%s-' % self.file
        s2 = '' if self.file is None else 'line:%s-' % self.line
        return '%s%s%s:%s' % (self.__class__.__name__, s1, s2, ','.join([str(arg) for arg in self.args]))


class NotSupportError(DQTraderError):
    """不支持的异常, eg: 当前不支持的频数"""
    pass


class DQTraderWarning(Warning):
    """At 警告"""

    def __init__(self, *args, file=None, line=None):
        """
        :param args: 位置参数
        :param file: str,文件路径
        :param line: int, 错误行号
        """
        self.file = file
        self.line = line
        super(DQTraderWarning, self).__init__(*args)

    def __str__(self):
        s1 = '' if self.file is None else 'file:%s-' % self.file
        s2 = '' if self.file is None else 'line:%s-' % self.line
        return '%s%s%s:%s' % (self.__class__.__name__, s1, s2, ','.join([str(arg) for arg in self.args]))
    


class InvalidParamWarning(DQTraderWarning):
    """参数无效警告"""

    def __init__(self, *args, file=None, line=None):
        self.file = file
        self.line = line
        super(InvalidParamWarning, self).__init__(*args)

class DQTModeError(DQTraderError):
    """模式不支持异常, eg: 回测模式时不能运行在实盘模式"""
    pass

class UnExpectError(DQTraderError):
    """未期望的异常, 正常情况下不应该出现错误. eg: 在类似 if-elif-else 分支中出现不当的条件"""
    pass


def raise_bultin_error(type_, line_num=None, file_name=None):
    """raise UnExpectError

    :param type_: str, 见 if 条件
    :param line_num: 错误行号
    :param file_name: 错误文件名称
    """

    if type_ == 'need3mode':
        raise DQTModeError(text.ERROR_NOT3MODE)
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