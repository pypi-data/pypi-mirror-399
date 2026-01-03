from selenium.webdriver.remote.webelement import WebElement
from blues_lib.behavior.Bean import Bean

class Length(Bean):

  def _get(self)->int:
    kwargs = self._get_kwargs(['loc_or_elem','parent_loc_or_elem','timeout'])
    eles:list[WebElement] = self._browser.waiter.querier.query_all(**kwargs)
    return len(eles) if eles else 0
