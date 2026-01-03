from blues_lib.behavior.Bean import Bean

class Screenshot(Bean):

  def _get(self)->any:
    if self._config.get('loc_or_elem'):
      kwargs = self._get_kwargs(['loc_or_elem','file','parent_loc_or_elem','timeout'])
      if self._to_be_presence():
        return self._browser.element.shot.screenshot(**kwargs)
    else:
      file = self._config.get('file','')
      return self._browser.interactor.window.screenshot(file)
