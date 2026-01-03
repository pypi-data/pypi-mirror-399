import time,random
from abc import abstractmethod

from blues_lib.type.executor.Executor import Executor
from blues_lib.model.Model import Model
from blues_lib.type.output.STDOut import STDOut
from blues_lib.sele.browser.Browser import Browser
from blues_lib.hook.behavior.BehaviorHook import BehaviorHook 
from blues_lib.schema.SchemaValidator import SchemaValidator
from blues_lib.types.common import WaitTime
from blues_lib.util.BluesDateTime import BluesDateTime

class Behavior(Executor):
  def __init__(self,model:Model,browser:Browser=None)->None:
    super().__init__()

    self._validate(model.config)

    self._model = model 
    self._meta = model.meta
    self._bizdata = model.bizdata
    self._config = model.config
    self._browser = browser
    
  def execute(self)->STDOut:
    skip = self._config.get('skip',False)
    if skip:
      return STDOut(200,f'skip the behavior, the skip is True')

    self._wait('wait_before') 
    output:STDOut = self._invoke()
    self._wait('wait_after')
    return output
  
  @abstractmethod
  def _invoke(self):
    pass
  
  def _wait(self,key:str):
    wait_time:WaitTime = self._config.get(key)
    if not wait_time:
      return
    
    if isinstance(wait_time,list):
      if len(wait_time) == 2:
        second = wait_time[0]
        title = wait_time[1]
      elif len(wait_time) == 3:
        second = random.randint(wait_time[0],wait_time[1])
        title = wait_time[2]
    else:
      second = wait_time
      title = key
      
    BluesDateTime.count_down({
      'duration':second,
      'title':title
    })
  
  def _validate(self,instance:str):
    tpl_path = 'except.input.behavior'
    stat,message = SchemaValidator.validate_with_template(instance,tpl_path)
    if not stat:
      raise ValueError(f'behavior config error: {message}')

  def _get_kwargs(self,keys:list[str],config=None)->dict:
    '''
    Extract specified keys from configuration dictionary
    @param {list[str]} keys: list of keys to extract from config
    @param {dict} config: optional config dict to merge with self._config (config takes precedence)
    @return {dict}: dictionary containing only the specified keys and their values
    '''
    conf = {**self._config,**config} if config else self._config
    # must remove the attr that value is None
    key_conf = {}
    for key in keys:
      if key in conf:
        key_conf[key] = conf.get(key)
    return key_conf

  def _to_be_clickable(self)->bool:

    kwargs = self._get_kwargs(['loc_or_elem','timeout'])
    # scroll the element into view, avoid the element is covered by other elements
    return self._browser.waiter.ec.to_be_clickable(**kwargs)

  def _to_be_visible(self)->bool:
    kwargs = self._get_kwargs(['loc_or_elem','timeout'])
    return self._browser.waiter.ec.to_be_visible(**kwargs)

  def _to_be_presence(self)->bool:
    kwargs = self._get_kwargs(['loc_or_elem','timeout'])
    return self._browser.waiter.ec.to_be_presence(**kwargs)

  def _scroll(self):
    kwargs = self._get_kwargs(['loc_or_elem','parent_loc_or_elem'])
    scroll = self._config.get('scroll',False)
    if scroll:
      self._browser.action.wheel.scroll_element_to_center(**kwargs)
      time.sleep(0.1)

  def _after_invoked(self,value:any)->any:
    # 在getter后调用，用于处理获取到的值
    hook_defs:list[dict[str,any]] = self._config.get('after_invoked')
    if not hook_defs:
      return value
    
    options = {'value':value}
    BehaviorHook(hook_defs,options).execute()
    return options.get('value')