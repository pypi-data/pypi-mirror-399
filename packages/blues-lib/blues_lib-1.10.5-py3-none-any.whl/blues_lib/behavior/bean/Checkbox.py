from typing import Any

from blues_lib.behavior.Bean import Bean

class Checkbox(Bean):

  def _set(self)->Any:
    kwargs = self._get_kwargs(['loc_or_elem','parent_loc_or_elem','timeout'])
    value = self._config.get('value')
    by:str = self._config.get('by') or 'no'
    if not value:
      return False

    eles:list[WebElement] = self._browser.waiter.querier.query_all(**kwargs)
    if not eles:
      return False

    values:list[int] = value if isinstance(value,list) else [value] # start from 1
    if by=='no':
      self._set_by_no(values,eles)
    elif by=='index':
      self._set_by_index(values,eles)
    elif by=='value':
      self._set_by_value(values,eles)
    else:
      return False
    return True

  def _set_by_no(self,values,eles):
    for no in values:
      no = int(no)
      if no>0 and no<=len(eles):
        eles[no-1].click()

  def _set_by_index(self,values,eles):
    for index in values:
      index = int(index)
      if index>=0 and index<len(eles):
        eles[index].click()
        
  def _set_by_value(self,values,eles):
    for ele in eles:
      if ele.get_attribute('value') in values:
        ele.click()
