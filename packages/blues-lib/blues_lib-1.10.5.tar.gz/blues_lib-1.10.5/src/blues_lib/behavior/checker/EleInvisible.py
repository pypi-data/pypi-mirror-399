from blues_lib.behavior.Trigger import Trigger

class EleInvisible(Trigger):

  def _trigger(self)->bool:
    '''
    check if the element is present in the page
    @returns {bool}
    '''
    loc_or_elem:str = self._config.get('loc_or_elem')
    wait_time:int = self._config.get('wait_time',3)
    return self._browser.waiter.ec.to_be_invisible(loc_or_elem,wait_time)
