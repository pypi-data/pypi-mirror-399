from typing import TypeAlias,Any
from selenium.webdriver.remote.webelement import WebElement

LocOrElem: TypeAlias = str | WebElement | None
LocOrElems: TypeAlias = str | list[str] | list[WebElement] | None

WaitTime: TypeAlias = int | float | tuple[int | float, str] | tuple[int | float, int | float, str] | None
IntervalTime: TypeAlias = int | float | list[int | float] | list[int | float | tuple[int | float, str]] | None

LightBhvItem: TypeAlias = tuple[str,str,Any|None]
LightBhvList: TypeAlias = list[LightBhvItem] | None