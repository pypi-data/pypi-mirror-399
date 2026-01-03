# coding: UTF-8
import sys
bstack111lll1_opy_ = sys.version_info [0] == 2
bstack1ll111_opy_ = 2048
bstack1_opy_ = 7
def bstack1l1l_opy_ (bstack11ll111_opy_):
    global bstack11l111l_opy_
    bstack11llll_opy_ = ord (bstack11ll111_opy_ [-1])
    bstack1ll1l1_opy_ = bstack11ll111_opy_ [:-1]
    bstack111l11_opy_ = bstack11llll_opy_ % len (bstack1ll1l1_opy_)
    bstack1ll1ll_opy_ = bstack1ll1l1_opy_ [:bstack111l11_opy_] + bstack1ll1l1_opy_ [bstack111l11_opy_:]
    if bstack111lll1_opy_:
        bstack11l11l_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll111_opy_ - (bstack1ll1l11_opy_ + bstack11llll_opy_) % bstack1_opy_) for bstack1ll1l11_opy_, char in enumerate (bstack1ll1ll_opy_)])
    else:
        bstack11l11l_opy_ = str () .join ([chr (ord (char) - bstack1ll111_opy_ - (bstack1ll1l11_opy_ + bstack11llll_opy_) % bstack1_opy_) for bstack1ll1l11_opy_, char in enumerate (bstack1ll1ll_opy_)])
    return eval (bstack11l11l_opy_)
class bstack1lllll11_opy_:
    def __init__(self, handler):
        self._1llll1l1ll1l_opy_ = None
        self.handler = handler
        self._1llll1ll1111_opy_ = self.bstack1llll1l1llll_opy_()
        self.patch()
    def patch(self):
        self._1llll1l1ll1l_opy_ = self._1llll1ll1111_opy_.execute
        self._1llll1ll1111_opy_.execute = self.bstack1llll1l1lll1_opy_()
    def bstack1llll1l1lll1_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack1l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࠧₖ"), driver_command, None, this, args)
            response = self._1llll1l1ll1l_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack1l1l_opy_ (u"ࠨࡡࡧࡶࡨࡶࠧₗ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1llll1ll1111_opy_.execute = self._1llll1l1ll1l_opy_
    @staticmethod
    def bstack1llll1l1llll_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver