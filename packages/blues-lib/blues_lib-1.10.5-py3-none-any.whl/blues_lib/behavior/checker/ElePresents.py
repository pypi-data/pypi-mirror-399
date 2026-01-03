from blues_lib.behavior.Trigger import Trigger

class ElePresents(Trigger):

  def _trigger(self)->bool:
    '''
    check if the element is present in the page
    @returns {bool}
    '''
    loc_or_elem:str = self._config.get('loc_or_elem')
    wait_time:int = self._config.get('wait_time',3)
    return bool(self._browser.waiter.ec.to_be_presence(loc_or_elem,wait_time))
