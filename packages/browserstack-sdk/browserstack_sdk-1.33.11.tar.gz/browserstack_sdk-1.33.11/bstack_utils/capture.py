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
import builtins
import logging
class bstack111ll11111_opy_:
    def __init__(self, handler):
        self._11l1ll11ll1_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1ll1l111_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack1l1l_opy_ (u"ࠫ࡮ࡴࡦࡰࠩ៪"), bstack1l1l_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫ៫"), bstack1l1l_opy_ (u"࠭ࡷࡢࡴࡱ࡭ࡳ࡭ࠧ៬"), bstack1l1l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭៭")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1ll111l1_opy_
        self._11l1ll111ll_opy_()
    def _11l1ll111l1_opy_(self, *args, **kwargs):
        self._11l1ll11ll1_opy_(*args, **kwargs)
        message = bstack1l1l_opy_ (u"ࠨࠢࠪ៮").join(map(str, args)) + bstack1l1l_opy_ (u"ࠩ࡟ࡲࠬ៯")
        self._11l1ll11lll_opy_(bstack1l1l_opy_ (u"ࠪࡍࡓࡌࡏࠨ៰"), message)
    def _11l1ll11lll_opy_(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack1l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ៱"): level, bstack1l1l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭៲"): msg})
    def _11l1ll111ll_opy_(self):
        for level, bstack11l1ll11l11_opy_ in self._11l1ll1l111_opy_.items():
            setattr(logging, level, self._11l1ll11l1l_opy_(level, bstack11l1ll11l11_opy_))
    def _11l1ll11l1l_opy_(self, level, bstack11l1ll11l11_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1ll11l11_opy_(msg, *args, **kwargs)
            self._11l1ll11lll_opy_(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1ll11ll1_opy_
        for level, bstack11l1ll11l11_opy_ in self._11l1ll1l111_opy_.items():
            setattr(logging, level, bstack11l1ll11l11_opy_)