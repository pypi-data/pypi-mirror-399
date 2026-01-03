from blues_lib.behavior.Bean import Bean

class Value(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['loc_or_elem','parent_loc_or_elem','timeout'])
    return self._browser.element.info.get_value(**kwargs)
  
  def _set(self):
    selector:str = self._config.get('loc_or_elem')
    value:str = self._config.get('value','')
    entity = {
      'value':value,
    }
    if self._to_be_presence():
      return self._browser.script.javascript.attr(selector,entity)
