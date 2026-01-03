from blues_lib.behavior.Bean import Bean

class Html(Bean):

  def _get(self)->str:
    selector:str = self._config.get('loc_or_elem')
    parent_selector:str = self._config.get('parent_loc_or_elem')
    return self._browser.script.javascript.html(selector,parent_selector)

  def _set(self):
    selector:str = self._config.get('loc_or_elem')
    parent_selector:str = self._config.get('parent_loc_or_elem')
    value:str = self._config.get('value','')
    if self._to_be_presence():
      return self._browser.script.javascript.html(selector,value,parent_selector)