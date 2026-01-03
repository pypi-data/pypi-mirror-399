from blues_lib.behavior.write.Write import Write

class WritePara(Write):

  _set_keys = ['loc_or_elem','value','LF_count','parent_loc_or_elem','timeout']

  def _set(self)->any:
    kwargs = self._get_kwargs(self._set_keys)
    clearable:bool = self._config.get('clearable',False)
    if self._to_be_visible():
      if clearable:
        return self._browser.element.input.write_para(**kwargs)
      else:
        return self._browser.element.input.append_para(**kwargs)