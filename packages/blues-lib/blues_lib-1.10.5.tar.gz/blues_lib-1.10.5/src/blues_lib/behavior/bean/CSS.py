import sys,os,re
from typing import Any

from blues_lib.behavior.Bean import Bean

class CSS(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['loc_or_elem','key','parent_loc_or_elem','timeout'])
    return self._browser.element.info.get_css(**kwargs)
  
  def _set(self):
    selector = self._config.get('loc_or_elem')
    parent_selector = self._config.get('parent_loc_or_elem')
    if entity := self._get_value_entity():
      if self._to_be_presence():
        return self._browser.script.javascript.css(selector,entity,parent_selector)
