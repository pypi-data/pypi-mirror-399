from blues_lib.behavior.Trigger import Trigger
from blues_lib.util.BluesDateTime import BluesDateTime

class Quit(Trigger):

  def _trigger(self)->bool:
    '''
    quit the browser after the wait time
    @returns {bool}
    '''
    try:
      if self._browser:
        self._browser.quit()
      return True
    except Exception as e:
      return False
