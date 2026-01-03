import datetime

from collections import OrderedDict, defaultdict


# 返回当前设备的MAC地址，格式为14-B3-1F-09-D5-11
def get_cur_mac_address():
    import uuid
    node = uuid.getnode()
    mac = str.upper(uuid.UUID(int=node).hex[-12:])
    del uuid
    mac = '-'.join([mac[i:i + 2] for i in range(0, len(mac), 2)])
    return mac

# 一个可以使用点操作符访问字典键值的类


class DotDict(dict):
    def __init__(self, _dict=None):
        _dict = _dict if _dict else {}
        super(DotDict, self).__init__(_dict)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return super(DotDict, self).__getattribute__(item)

    def __str__(self):
        result = ['DotDict{']
        for k, v in self.items():
            result.append("\t{!r}:{!r},".format(k, v))
        result.append('}')
        return '\n'.join(result)

# 一个有序的可以使用点操作符访问字典键值的类


class OrderedDotDict(OrderedDict):
    def __init__(self, _dict=None):
        _dict = _dict if _dict else {}
        super(OrderedDotDict, self).__init__(_dict)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return super(OrderedDotDict, self).__getattribute__(item)

    def __str__(self):
        result = [''] * (len(self.items()) + 2)
        result[0] = 'OrderedDotDict{'
        for index, k in enumerate(self.keys(), 1):
            result[index] = "\t{!r}:{!r},".format(k, self[k])
        result[-1] = '}'

        return '\n'.join(result)


class SimpleTimer:
    """
    简单时间计时器最高精度为毫秒(ms)
    eg:
    t = SimpleTimer('your tips',unit='ms')    
    print(t)
    """
    # 毫秒为最小单位
    _unit_maps = {
        'year': ['年', 365 * 24 * 60 * 60 * 1000],
        'mon': ['月', 30 * 24 * 60 * 60 * 1000],
        'day': ['日', 24 * 60 * 60 * 1000],
        'hour': ['时', 60 * 60 * 1000],
        'min': ['分', 60 * 1000],
        'sec': ['秒', 1000],
        'ms': ['毫秒', 1]
    }

    def __init__(self, prompt='', unit='sec', start=True):
        """
        :param prompt: 提示信息,str类型  
        :param unit: 'year','mon','day','hour','min','sec','ms' 
        """
        self.start_time = None
        self.unit = unit
        self.prompt = prompt
        self.elapsed = 0
        self.reset(prompt, unit)
        if start:
            self.start()

    def __str__(self):
        if self.running:
            format_elapsed_time = self.total()
        else:
            format_elapsed_time = self.elapsed
        return self.prompt + ' %d %s' % (format_elapsed_time, self.chs_unit)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def total(self):
        self._raise_not_start()
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - self.start_time)
        divisor = SimpleTimer._unit_maps.get('sec')[1]
        if self.unit in SimpleTimer._unit_maps:
            divisor = SimpleTimer._unit_maps.get(self.unit, ['秒', 1000])[1]
        total_milliseconds = elapsed_time.days * 86400000 + \
            elapsed_time.seconds * 1000 + elapsed_time.microseconds / 1000
        format_elapsed_time = total_milliseconds / divisor
        return format_elapsed_time

    def start(self):
        self._raise_started()
        self.start_time = datetime.datetime.now()

    def stop(self):
        self._raise_not_start()
        self.elapsed += self.total()
        self.start_time = None
        return self.elapsed

    def reset(self, prompt=None, unit=None):
        if prompt is not None:
            self.prompt = prompt
        if unit is not None:
            self.unit = unit
        if self.unit not in SimpleTimer._unit_maps:
            self.unit = 'sec'
        self.elapsed = 0

    def restart(self, prompt=None, unit=None):
        self.reset(prompt=prompt, unit=unit)
        if self.running:
            self.stop()
        self.start()

    def _raise_not_start(self):
        if not self.running:
            raise RuntimeError('Not started')

    def _raise_started(self):
        if self.running:
            raise RuntimeError('Already started')

    @property
    def chs_unit(self):
        unit = SimpleTimer._unit_maps.get(self.unit, '秒')[0]
        return unit

    @property
    def running(self):
        return self.start_time is not None


class FileStrategyLoader:
    """策略加载器"""

    def __init__(self, strategy_path):
        self._strategy_path = strategy_path

    def load(self, scope):
        from .utilfunc import compile_strategy

        with open(self._strategy_path, encoding='utf-8') as f:
            source_code = f.read()

        return compile_strategy(source_code, self._strategy_path, scope)


class StatusCollect:
    """系统状态收集分析器"""
    __state = {}

    def __init__(self, ):
        self.__dict__ = self.__state
        # 实盘回测耗时查询
        self._time = {}
        self._recoder = defaultdict(list)
        self.env = None

    def start_time(self, name, prompt: str, unit='sec'):
        """开始启动一个计时器"""

        if name not in self._time:
            self._time[name] = SimpleTimer(
                prompt=prompt, unit=unit, start=True)
        else:
            t = self._time[name]  # type: SimpleTimer
            t.restart(prompt=prompt, unit=unit)

    def stop_time(self, name, rm=False):
        """结束一个计时器"""

        time_obj = self._time.get(name)  # type: SimpleTimer

        if time_obj is None:
            return 0

        total = time_obj.total()

        if time_obj.running:
            time_obj.stop()

        if rm:
            if name in self._time:
                self._time.pop(name)
            if name in self._recoder:
                self._recoder.pop(name)

        return total

    def use_time(self, name):
        """统计耗时"""

        time_obj = self._time.get(name)  # type: SimpleTimer

        if time_obj is None:
            return 0

        total = time_obj.total()

        return total

    def restart_time(self, name):
        time_obj = self._time.get(name)  # type: SimpleTimer

        if time_obj is None:
            return 0

        time_obj.restart()

    def recoder_once(self, name, tips=None, reset=False):
        t = self._time.get(name)  # type: SimpleTimer
        if t is None:
            return ''
        r = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f') + ' ' + \
            ('' if tips is None else str(tips)) + str(t)
        self._recoder[name].append(r)
        if reset:
            t.reset()
        return r

    def recoder_count(self, name):
        return len(self._recoder.get(name, []))

    def time_object(self, name):
        """获取计时器对象"""

        return self._time.get(name)

    def stat_info(self, name, stop=False):
        """显示当前系统运行状态"""
        t = self._time.get(name)  # type: SimpleTimer
        if t is None:
            return None

        run_mode_name = 'default' if self.env is None else self.env.gv.run_mode_name(
            self.env.smm.cur_run_mode)
        phase_name = 'default' if self.env is None else self.env.gv.phase_name(
            self.env.smm.cur_run_mode_phase)

        s = "\n统计名称：{STATNAME}\n运行模式: {RUNMODE}\n运行阶段: {PHASE}\n运行详情：\n{INFO}\n".format(
            STATNAME=name,
            RUNMODE=run_mode_name,
            INFO='.\n'.join(self._recoder.get(name, [])),
            PHASE=phase_name
        )
        s = '=' * 60 + s + '=' * 60 + '\n'

        if stop:
            self.stop_time(name)

        return s

    def last_info(self, name):
        info = self._recoder.get(name, [])  # type: list
        return info[-1] if info else None

    def clear_info(self, name):
        self._recoder.get(name, []).clear()

    @classmethod
    def instance(cls) -> 'StatusCollect':
        name = 'StatusCollect'
        if name not in cls.__state:
            cls.__state[name] = StatusCollect()

        return cls.__state.get(name)


class RangeRecord:
    def __init__(self):
        self._raw_record = defaultdict(list)
        self._record = defaultdict(list)

    def add_range(self, name, s, e):
        assert s <= e, 'error, {s} > {e}'.format(s=s, e=e)
        self._raw_record[name].append((s, e))
        self._calc_record(name)

    def sub_range(self, name, s, e):
        assert s <= e, 'error, {s} > {e}'.format(s=s, e=e)
        self._raw_record = self.sub_record(self._raw_record[name], s, e)
        self._calc_record(name)

    def record(self, name):
        return self._record.get(name, [])

    def _calc_record(self, name):
        self._record[name].clear()
        self._record[name].extend(self.comb_record(self._raw_record[name]))

    @classmethod
    def _do_increment_func(cls, increment_func, *args):
        if increment_func is None:
            return args[0] + args[1]
        else:
            return increment_func(*args)

    @classmethod
    def diff_record(cls, records, s, e, increment_func=None) -> 'list':
        """ 计算差集, 即没有在集合内的部分
        例子：
            print(RangeRecord.diff_record([(5, 6), (10, 12)], 1, 5)) => [(1, 4)]
            print(RangeRecord.diff_record([(5, 6), (8, 10)], 6, 15))
            print(RangeRecord.diff_record([(5, 9)], 7, 15))
            print(RangeRecord.diff_record([(5, 6)], 7, 8))
            print(RangeRecord.diff_record([(5, 6), (15, 30)], 9, 12))
            print(RangeRecord.diff_record([(5, 6), (15, 30)], 9, 17))
            print(RangeRecord.diff_record([(5, 6), (15, 30)], 9, 35))
            print(RangeRecord.diff_record([(5, 6), (15, 30)], 1, 35))
            print(RangeRecord.diff_record([(5, 6), (8, 30), (34, 38)], 1, 35))
        """
        if len(records) < 1:
            return [(s, e)]

        records = cls.comb_record(records)
        results = []
        ss, ee = s, e

        for idx, item in enumerate(records):
            ss = cls._do_increment_func(
                increment_func, item[1], 1) if item[0] <= ss <= item[1] else ss

            if ss > ee:
                break

            # case1: (1,2) [(3,5)] 全部在左侧
            if ee < item[0]:
                results.append((ss, ee))
                break

            # case2 (4,8) [(2,5)] 部分在右侧
            if ss < item[0] <= ee <= item[1]:
                results.append(
                    (ss, cls._do_increment_func(increment_func, item[0], -1)))
                ss = cls._do_increment_func(increment_func, item[1], 1)

            # case3 (1,3) [(2,5)] 部分在左侧
            if ee > item[1] and ss < item[0]:
                results.append(
                    (ss, cls._do_increment_func(increment_func, item[0], -1)))
                ss = cls._do_increment_func(increment_func, item[1], 1)

        # case4 (8,10) [(1,2)] 全部在右侧
        if records[-1][1] < ss <= e:
            results.append((ss, ee))

        return results

    @classmethod
    def comb_record(cls, records: 'list'):
        """ 合并集合, 将集合中重叠部分合并
        例子：
            print(RangeRecord.comb_record([(0, 5), (0, 5), (3, 8)]))
            print(RangeRecord.comb_record([(0, 5), (7, 9), (6, 8)]))
            print(RangeRecord.comb_record([(0, 5), (7, 9), (9, 9)]))
            print(RangeRecord.comb_record([(0, 5), (7, 9), (9, 10)]))
            print(RangeRecord.comb_record([(0, 5), (6, 6), (8, 8)]))
            print(RangeRecord.comb_record([(0, 5), (6, 6), (8, 8), (8, 9)]))
        """
        result = []
        if len(records) < 1:
            return result
        records.sort(key=lambda x: x[0])
        result = [records[0]]
        for item in records[1:]:  # type:
            if item[0] - 1 <= result[-1][1] < item[1]:
                result[-1] = (result[-1][0], item[1])
            elif item[0] > result[-1][1]:
                result.append(item)

        return result

    @classmethod
    def sub_record(cls, records: 'list', s, e, increment_func=None) -> 'list':
        """ 消除重复集合
            print(RangeRecord.sub_record([(1, 5), (8, 10)], 4, 7))  		=> [(1, 3), (8, 10)]
            print(RangeRecord.sub_record([(1, 5), (8, 10)], 1, 5))			=> [(8, 10)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 0, 1))			=> [(2, 5), (8, 10)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 6, 7))			=> [(2, 5), (8, 10)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 1, 11))			=> []
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 5, 10))			=> [(2, 4)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 10, 30))		=> [(2, 9)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 0, 2))			=> [(3, 5), (8, 10)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 0, 7))			=> [(8, 10)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 0, 8))			=> [(9, 10)]
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 0, 15))			=> []
            print(RangeRecord.sub_record([(2, 5), (8, 10)], 6, 7))          => [(2, 5), (8, 10)]

        """
        results = []
        ss, ee = s, e

        records = cls.comb_record(records)
        for idx, item in enumerate(records):
            # 全部在之外 [8,10] (1,2)
            if ss > ee or ee < item[0]:
                results.extend([i for i in records[idx:]])
                break

            # 起点在 item 左侧
            if ee > item[0] > ss:
                ss = item[0]

            # 起点在 item 右侧
            if ss > item[1]:
                results.append(item)

            # 起点在之内
            if item[0] <= ss <= item[1]:
                _s = cls._do_increment_func(increment_func, ss, -1)
                if item[0] <= _s:
                    results.append((item[0], _s))

                if ee <= item[1]:
                    _e = cls._do_increment_func(increment_func, ee, 1)
                    if _e <= item[1]:
                        results.append((_e, item[1]))
                        ee = cls._do_increment_func(
                            increment_func, item[0], -1)
                ss = records[idx + 1][0] if idx < len(
                    records) - 1 else cls._do_increment_func(increment_func, item[1], 1)

        return results
