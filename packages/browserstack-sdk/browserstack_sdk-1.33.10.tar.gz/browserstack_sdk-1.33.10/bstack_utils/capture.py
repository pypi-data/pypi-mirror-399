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
import builtins
import logging
class bstack111l1l1lll_opy_:
    def __init__(self, handler):
        self._11l1ll11l1l_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1ll1l111_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack11111l_opy_ (u"ࠫ࡮ࡴࡦࡰࠩ៣"), bstack11111l_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫ៤"), bstack11111l_opy_ (u"࠭ࡷࡢࡴࡱ࡭ࡳ࡭ࠧ៥"), bstack11111l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭៦")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1ll11l11_opy_
        self._11l1ll11ll1_opy_()
    def _11l1ll11l11_opy_(self, *args, **kwargs):
        self._11l1ll11l1l_opy_(*args, **kwargs)
        message = bstack11111l_opy_ (u"ࠨࠢࠪ៧").join(map(str, args)) + bstack11111l_opy_ (u"ࠩ࡟ࡲࠬ៨")
        self._11l1ll11lll_opy_(bstack11111l_opy_ (u"ࠪࡍࡓࡌࡏࠨ៩"), message)
    def _11l1ll11lll_opy_(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack11111l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ៪"): level, bstack11111l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭៫"): msg})
    def _11l1ll11ll1_opy_(self):
        for level, bstack11l1ll1l1l1_opy_ in self._11l1ll1l111_opy_.items():
            setattr(logging, level, self._11l1ll1l11l_opy_(level, bstack11l1ll1l1l1_opy_))
    def _11l1ll1l11l_opy_(self, level, bstack11l1ll1l1l1_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1ll1l1l1_opy_(msg, *args, **kwargs)
            self._11l1ll11lll_opy_(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1ll11l1l_opy_
        for level, bstack11l1ll1l1l1_opy_ in self._11l1ll1l111_opy_.items():
            setattr(logging, level, bstack11l1ll1l1l1_opy_)