# -*- coding: utf-8 -*-
# author: 王树根
# email: wsg1107556314@163.com
# date: 2025/12/16 22:45
import time

from .datetime import Timer
from .printext import it_print


class _FailureRetry(Exception):
  pass


class RateLimiter(object):

  def __init__(
    self, qps, patience=1, cooldown=None,
    fn=None, check_fn=None, except_fn=None):
    """
    初始化限流器
    :param qps: 每秒最大请求数
    :param patience: 最大重试次数
    :param cooldown: 冷却时间
    :param fn: 限流器执行的函数
    :param check_fn: 检查执行函数结果的函数
    :param except_fn: 异常结果处理函数
    """
    self.qps = qps
    self.interval = 1 / qps
    self.patience = patience
    self.cooldown = cooldown
    self.timer = Timer()
    self.closure_fn = fn
    self.check_fn = check_fn
    self.except_fn = except_fn

  def _invoke(self, *args, **kwargs):
    elapsed = self.timer.elapsed
    if elapsed < self.interval:
      time.sleep(self.interval - elapsed)
    self.timer.reset()
    return self.closure_fn(*args, **kwargs)

  def forward(self, *args, **kwargs):
    patience, ret = self.patience, None
    while patience > 0:
      try:
        if patience < self.patience:
          it_print(
            'retry invoking count down from {a} to {b} ...'
            .format(a=self.patience, b=patience), device=2
          )
        ret = self._invoke(*args, **kwargs)
        if self.check_fn is not None and not self.check_fn(ret):
          raise _FailureRetry("-- Rater Limiter Failure Retry --")
        break
      except Exception as e:
        if not (self.except_fn is None or isinstance(e, _FailureRetry)):
          self.except_fn(e)
        if self.cooldown is not None:
          time.sleep(self.cooldown)
        patience -= 1
    return ret

  def __call__(self, *args, **kwargs):
    return self.forward(*args, **kwargs)
