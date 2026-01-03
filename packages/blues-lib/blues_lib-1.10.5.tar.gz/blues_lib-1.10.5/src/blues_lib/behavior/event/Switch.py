from blues_lib.behavior.Trigger import Trigger

class Switch(Trigger):

  def _trigger(self)->bool:
    '''
    switch to the specified window handle
    @returns {bool}
    '''
    try:
      if not self._browser:
        return True

      handle:str = self._config.get('handle')
      if handle == 'default' or not handle:
        self._browser.interactor.window.switch_to_default()
      elif handle=='latest':
        self._browser.interactor.window.switch_to_latest()
      elif handle=='prev':
        self._browser.interactor.window.switch_to_prev()
      elif handle=='next':
        self._browser.interactor.window.switch_to_next()
      else:
        self._browser.interactor.window.switch_to(handle)
      return True
    except Exception as e: 
      return False