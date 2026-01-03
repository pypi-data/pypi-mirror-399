import time
from selenium.webdriver.remote.webelement import WebElement
from blues_lib.behavior.Trigger import Trigger
from blues_lib.types.common import LocOrElems

class Click(Trigger):

  def _trigger(self)->int:
    loc_or_elems:LocOrElems = self._config.get('loc_or_elems')
    if loc_or_elems:
      return self._multi_click(loc_or_elems)
    else:
      return self._click() 
  
  def _multi_click(self,loc_or_elems:LocOrElems)->int:
    index = 0
    if isinstance(loc_or_elems,str):
      items = self._get_eles(loc_or_elems)
    else:
      items = loc_or_elems
    for loc_or_elem in items:
      self._config['loc_or_elem'] = loc_or_elem
      self._click()
      if index<len(items)-1:
        self._wait_interval(index)
      index += 1
    return index
  
  def _get_eles(self,locator:str)->list[WebElement]:
    kwargs:dict = self._get_kwargs(['parent_loc_or_elem','timeout'])
    kwargs['loc_or_elem'] = locator
    return self._browser.waiter.querier.query_all(**kwargs)

  def _click(self):
    kwargs:dict = self._get_kwargs(['loc_or_elem','parent_loc_or_elem','timeout'])
    if self._is_clickable():
      self._scroll()
      time.sleep(0.2) # 有时状态判断成功，但实际还需要等待一些
      return self._browser.action.mouse.click(**kwargs)

  def _is_clickable(self)->bool:
    loc_or_elem = self._config.get('loc_or_elem')
    if isinstance(loc_or_elem,WebElement):
      return True
    else:
      return self._to_be_clickable()
