# coding: UTF-8
import sys
bstack1l1ll_opy_ = sys.version_info [0] == 2
bstack1l11lll_opy_ = 2048
bstack1lll11l_opy_ = 7
def bstack11111l_opy_ (bstack1lllll1l_opy_):
    global bstack1ll1111_opy_
    bstack11l1111_opy_ = ord (bstack1lllll1l_opy_ [-1])
    bstack11ll11l_opy_ = bstack1lllll1l_opy_ [:-1]
    bstack11l11l1_opy_ = bstack11l1111_opy_ % len (bstack11ll11l_opy_)
    bstack11l11ll_opy_ = bstack11ll11l_opy_ [:bstack11l11l1_opy_] + bstack11ll11l_opy_ [bstack11l11l1_opy_:]
    if bstack1l1ll_opy_:
        bstack111l1l1_opy_ = unicode () .join ([unichr (ord (char) - bstack1l11lll_opy_ - (bstack1ll1l1_opy_ + bstack11l1111_opy_) % bstack1lll11l_opy_) for bstack1ll1l1_opy_, char in enumerate (bstack11l11ll_opy_)])
    else:
        bstack111l1l1_opy_ = str () .join ([chr (ord (char) - bstack1l11lll_opy_ - (bstack1ll1l1_opy_ + bstack11l1111_opy_) % bstack1lll11l_opy_) for bstack1ll1l1_opy_, char in enumerate (bstack11l11ll_opy_)])
    return eval (bstack111l1l1_opy_)
class bstack11l1l11l11_opy_:
    def __init__(self, handler):
        self._1llll1l1llll_opy_ = None
        self.handler = handler
        self._1llll1ll11l1_opy_ = self.bstack1llll1ll1111_opy_()
        self.patch()
    def patch(self):
        self._1llll1l1llll_opy_ = self._1llll1ll11l1_opy_.execute
        self._1llll1ll11l1_opy_.execute = self.bstack1llll1ll111l_opy_()
    def bstack1llll1ll111l_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack11111l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࠧ₏"), driver_command, None, this, args)
            response = self._1llll1l1llll_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack11111l_opy_ (u"ࠨࡡࡧࡶࡨࡶࠧₐ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1llll1ll11l1_opy_.execute = self._1llll1l1llll_opy_
    @staticmethod
    def bstack1llll1ll1111_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver