import logging
import datetime
import builtins
import dqtrader_rs

_logger = None


# 解析参数
class MillisecondFormatter(logging.Formatter):
    def format(self, record):
        s = super().format(record)
        old_time = self.formatTime(record, self.datefmt)
        new_time = datetime.datetime.fromtimestamp(record.created).strftime(
            '%Y-%m-%d %H:%M:%S.{:03d}'.format(int(record.msecs)))
        return s.replace(old_time, new_time)


class XportLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        format_str = '%(asctime)s  %(levelname)s {} %(filename)s %(lineno)d: %(message)s'.format("dqtrader")
        self.formatter = MillisecondFormatter(format_str)

    def emit(self, record):
        log_entry = self.format(record)
        dqtrader_rs.log.output(log_entry)


def init():
    global _logger
    if _logger is not None:
        return
    TRACE_LEVEL_NUM = 5
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, message, args, **kws)

    #
    logging.Logger.trace = trace
    logger = logging.getLogger('xport')
    log_level = dqtrader_rs.log.level().upper()
    #
    if log_level == "TRACE":
        logger.setLevel(TRACE_LEVEL_NUM)
    elif log_level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif log_level == "INFO":
        logger.setLevel(logging.INFO)
    elif log_level == "WARN":
        logger.setLevel(logging.WARNING)
    elif log_level == "ERROR":
        logger.setLevel(logging.ERROR)
        #
    xport_log_handler = XportLogHandler()
    logger.addHandler(xport_log_handler)
    _logger = logger


def get_logger() -> logging.Logger:
    global _logger
    return _logger
