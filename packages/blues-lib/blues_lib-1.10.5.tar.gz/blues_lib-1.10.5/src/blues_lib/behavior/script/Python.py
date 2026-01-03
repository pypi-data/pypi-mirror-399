from blues_lib.behavior.Trigger import Trigger

class Python(Trigger):

  def _trigger(self)->any:
    script = self._config.get('script')
    return self._browser.script.python.execute(script)
