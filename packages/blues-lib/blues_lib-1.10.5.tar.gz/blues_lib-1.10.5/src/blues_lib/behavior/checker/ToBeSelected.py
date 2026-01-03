from blues_lib.behavior.Trigger import Trigger

class ToBeSelected(Trigger):

  def _trigger(self)->bool:
    '''
    if the current url is equal to the expected url
    @returns {bool}
    '''
    kwargs = self._get_kwargs(['loc_or_elem','timeout'])
    return self._browser.waiter.ec.to_be_selected(**kwargs)
