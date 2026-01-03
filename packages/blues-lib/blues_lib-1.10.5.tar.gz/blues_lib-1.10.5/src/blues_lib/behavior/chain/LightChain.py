from blues_lib.behavior.Trigger import Trigger
from blues_lib.model.Model import Model
from blues_lib.behavior.BhvExecutor import BhvExecutor
from blues_lib.types.common import LightBhvList,LightBhvItem

class LightChain(Trigger):
  # light weight chain, only support core attributes
  def _trigger(self)->int:
    light_bhvs:LightBhvList = self._config.get('bhv_chain')
    if not light_bhvs:
      return 0
    
    index = 0
    for light_bhv in light_bhvs:
      self._trigger_bhv(light_bhv)
      if index<len(light_bhvs)-1:
        self._wait_interval(index)
      index += 1
    return index
  
  def _trigger_bhv(self,light_bhv:LightBhvItem)->int:
    bhv_list = light_bhv + [None] * (3 - len(light_bhv))
    meta = {
      '_kind':bhv_list[0],
      'loc_or_elem':bhv_list[1],
      'value':bhv_list[2],
    }
    self._padd_default_attr(meta)
    model = Model(meta)
    return BhvExecutor(model,self._browser).execute()
  
  def _padd_default_attr(self,meta:dict):
    if meta.get('_kind') == 'write_text':
      meta['clearable'] = True