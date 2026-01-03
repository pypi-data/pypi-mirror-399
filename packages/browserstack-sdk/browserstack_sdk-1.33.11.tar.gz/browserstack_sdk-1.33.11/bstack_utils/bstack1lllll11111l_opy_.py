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
import threading
import logging
logger = logging.getLogger(__name__)
bstack1lllll1111ll_opy_ = 1000
bstack1llll1llll1l_opy_ = 2
class bstack1lllll1111l1_opy_:
    def __init__(self, handler, bstack1lllll111l1l_opy_=bstack1lllll1111ll_opy_, bstack1llll1lll1ll_opy_=bstack1llll1llll1l_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1lllll111l1l_opy_ = bstack1lllll111l1l_opy_
        self.bstack1llll1lll1ll_opy_ = bstack1llll1lll1ll_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1lllll1l11l_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1lllll111l11_opy_()
    def bstack1lllll111l11_opy_(self):
        self.bstack1lllll1l11l_opy_ = threading.Event()
        def bstack1llll1lllll1_opy_():
            self.bstack1lllll1l11l_opy_.wait(self.bstack1llll1lll1ll_opy_)
            if not self.bstack1lllll1l11l_opy_.is_set():
                self.bstack1llll1llllll_opy_()
        self.timer = threading.Thread(target=bstack1llll1lllll1_opy_, daemon=True)
        self.timer.start()
    def bstack1lllll111111_opy_(self):
        try:
            if self.bstack1lllll1l11l_opy_ and not self.bstack1lllll1l11l_opy_.is_set():
                self.bstack1lllll1l11l_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠩ࡞ࡷࡹࡵࡰࡠࡶ࡬ࡱࡪࡸ࡝ࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥ࠭⁆") + (str(e) or bstack1l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡩ࡯࡯ࡸࡨࡶࡹ࡫ࡤࠡࡶࡲࠤࡸࡺࡲࡪࡰࡪࠦ⁇")))
        finally:
            self.timer = None
    def bstack1llll1llll11_opy_(self):
        if self.timer:
            self.bstack1lllll111111_opy_()
        self.bstack1lllll111l11_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1lllll111l1l_opy_:
                threading.Thread(target=self.bstack1llll1llllll_opy_).start()
    def bstack1llll1llllll_opy_(self, source = bstack1l1l_opy_ (u"ࠫࠬ⁈")):
        with self.lock:
            if not self.queue:
                self.bstack1llll1llll11_opy_()
                return
            data = self.queue[:self.bstack1lllll111l1l_opy_]
            del self.queue[:self.bstack1lllll111l1l_opy_]
        self.handler(data)
        if source != bstack1l1l_opy_ (u"ࠬࡹࡨࡶࡶࡧࡳࡼࡴࠧ⁉"):
            self.bstack1llll1llll11_opy_()
    def shutdown(self):
        self.bstack1lllll111111_opy_()
        while self.queue:
            self.bstack1llll1llllll_opy_(source=bstack1l1l_opy_ (u"࠭ࡳࡩࡷࡷࡨࡴࡽ࡮ࠨ⁊"))