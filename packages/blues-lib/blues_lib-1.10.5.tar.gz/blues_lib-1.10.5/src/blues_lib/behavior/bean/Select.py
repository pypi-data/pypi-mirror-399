import sys,os,re
from typing import Any

from blues_lib.behavior.Bean import Bean

class Select(Bean):

  def _set(self)->Any:
    kwargs = self._get_kwargs(['loc_or_elem','value','parent_loc_or_elem','timeout'])
    if self._to_be_presence():
      return self._browser.element.select.select_by_value_or_text(**kwargs)
