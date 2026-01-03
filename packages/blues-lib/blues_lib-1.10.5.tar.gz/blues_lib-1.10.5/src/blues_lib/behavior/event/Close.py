from blues_lib.behavior.Trigger import Trigger

class Close(Trigger):

  def _trigger(self)->bool:
    '''
    close the specified window handle
    @returns {bool}
    '''
    try:
      if not self._browser:
        return True

      current_handle:str = self._browser.interactor.window.get_handle()
      handles:list[str] = self._browser.interactor.window.get_handles()
      handle:str = self._config.get('handle')
      if handle == 'others':
        self._close_others(current_handle,handles)
      elif handle == current_handle or handle=='current' or not handle:
        self._close_current(current_handle,handles)
      else:
        self._close_handle(current_handle,handles,handle)
      return True
    except Exception as e: 
      return False
    
  def _close_current(self,current_handle:str,handles:list[str]):
    self._browser.interactor.navi.close()
    for handle in handles:
      if handle != current_handle:
        print('--xx',handle)
        self._browser.interactor.window.switch_to(handle)
      
  def _close_handle(self,current_handle:str,handles:list[str],handle:str):
    if handle in handles:
      self._browser.interactor.window.switch_to(handle)
      self._browser.interactor.navi.close()
      self._browser.interactor.window.switch_to(current_handle)
      
  def _close_others(self,current_handle:str,handles:list[str]):
    for handle in handles:
      if handle != current_handle:
        self._browser.interactor.window.switch_to(handle)
        self._browser.interactor.navi.close()
    self._browser.interactor.window.switch_to(current_handle)
