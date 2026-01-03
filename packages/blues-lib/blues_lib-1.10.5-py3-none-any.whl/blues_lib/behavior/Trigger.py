from abc import abstractmethod
from blues_lib.type.output.STDOut import STDOut
from blues_lib.behavior.Behavior import Behavior
from blues_lib.deco.BehaviorSTDOutLog import BehaviorSTDOutLog
from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.types.common import IntervalTime,WaitTime

class Trigger(Behavior):

  @BehaviorSTDOutLog()
  def _invoke(self)->STDOut:
    value = None
    try:
      value = self._trigger()
      value = self._after_invoked(value)
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  @abstractmethod
  def _trigger(self)->any:
    pass
  
  def _wait_interval(self,index:int):
    defualt_value:int = 1
    interval:IntervalTime = self._config.get('interval',defualt_value)
    wait_time:int = 0
    title:str = f'wait to click {index+2}th element'

    if isinstance(interval,list):
      if 0 <= index < len(interval):
        item:WaitTime = interval[index]
        if isinstance(item,list):
          wait_time = item[0]
          title = item[1] or title
        else:
          wait_time = item
      else:
        wait_time = defualt_value
    else:
      wait_time = interval

    if wait_time > 0:
      BluesDateTime.count_down({
        'duration':wait_time,
        'title':title
      })