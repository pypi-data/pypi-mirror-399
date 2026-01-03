import time

from blues_lib.behavior.Trigger import Trigger
from blues_lib.util.Clipboard import Clipboard

class Keyboard(Trigger):

  def _trigger(self)->str:
    key:str = self._config.get('key')
    value:str = self._config.get('value')
    kwargs = self._get_kwargs(['loc_or_elem','parent_loc_or_elem'])
    
    actions:list[str] = ['select','focus','copy','cut','clear','enter','f12']

    if key == 'paste':
      self._paste(kwargs,value)
    elif key == 'paste_after':
      self._paste(kwargs,value,True)
    elif key == 'esc':
      self._browser.action.keyboard.esc()
    elif key in actions:
      func = getattr(self._browser.action.keyboard,key)
      func(**kwargs)

  def _paste(self,kwargs:dict,value:str,after:bool=False):
    if value:
      Clipboard.copy(value) # write to clipboard
    time.sleep(0.2)
    # write to the input
    if after:
      self._browser.action.keyboard.paste_after(**kwargs)
    else:
      self._browser.action.keyboard.paste(**kwargs)

