# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:30
from six.moves import xrange

from .collection import Iterable
from .printext import it_print
from .printext import print_json
from .stringext import from_json


def contain_keys(data, *keys):
  """
  检测字典data中是否包含指定的所有键
  :param data: 数据
  :param keys: 键集
  :return: 若data包含keys中所有键则返回True, 否则返回False
  """
  if len(keys) == 1:
    keys = keys[0]

  if not isinstance(keys, Iterable):
    return False

  for key in keys:
    if key not in data:
      return False
  return True


def in_range(num, range_from, range_to):
  """
  检测数字是否在范围[range_from, range_to]内
  :param num: 待检测数值
  :param range_from: 起始范围
  :param range_to: 结束范围
  :return: 若num在范围内返回True, 否则返回False
  """
  return num in xrange(range_from, range_to + 1)


def criteria_satisfy(criteria, text_or_obj, trace=False, trace_fn=None):
  """
  验证条件是否满足
  :param criteria: 条件列表
  :param text_or_obj: 被测试对象
  :param trace: 是否追踪不满足条件对象
  :param trace_fn: 追踪处理函数
  :return: 若符合返回True, 不符合返回False
  """
  if len(criteria) > 0:
    if isinstance(text_or_obj, str):
      obj = from_json(text_or_obj)
    else:
      obj = text_or_obj
    for criterion in criteria:
      try:
        if eval(criterion):
          continue
      except KeyError as e:
        if isinstance(obj, (dict, list)):
          print_json(obj)
        else:
          it_print(obj)
        raise e
      if trace:
        if trace_fn is None:
          value = obj
        else:
          value = trace_fn(obj)
        it_print('{c} not satisfy {v}'.format(c=criterion, v=value))
      return False
  return True
