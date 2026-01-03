from blues_lib.behavior.Bean import Bean

class Attr(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['loc_or_elem','key','parent_loc_or_elem','timeout'])
    return self._browser.element.info.get_attr(**kwargs)

  def _set(self):
    """
    Set the attribute(s) of the element(s) selected by the selector.
    This method refers to the jQuery attr method. It determines the final parameter format by judging the type of input parameters.

    Steps:
    1. Get the selector, key, and value from the configuration.
    2. Determine the attribute(s) to be set based on the type of key and value.
    3. If there are attributes to be set, call the JavaScript method to set them.
    """
    selector:str = self._config.get('loc_or_elem')
    if entity := self._get_value_entity():
      if self._to_be_presence():
        return self._browser.script.javascript.attr(selector,entity)
