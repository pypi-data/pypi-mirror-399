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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1lllll1ll1l_opy_ import bstack1lllll1lll1_opy_
class bstack1lll11ll111_opy_(abc.ABC):
    bin_session_id: str
    bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_
    def __init__(self):
        self.bstack1ll1l11111l_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1lllll1ll1l_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1ll1lll11l1_opy_(self):
        return (self.bstack1ll1l11111l_opy_ != None and self.bin_session_id != None and self.bstack1lllll1ll1l_opy_ != None)
    def configure(self, bstack1ll1l11111l_opy_, config, bin_session_id: str, bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_):
        self.bstack1ll1l11111l_opy_ = bstack1ll1l11111l_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1lllll1ll1l_opy_ = bstack1lllll1ll1l_opy_
        if self.bin_session_id:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡧࡧࠤࡲࡵࡤࡶ࡮ࡨࠤࢀࡹࡥ࡭ࡨ࠱ࡣࡤࡩ࡬ࡢࡵࡶࡣࡤ࠴࡟ࡠࡰࡤࡱࡪࡥ࡟ࡾ࠼ࠣࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧኮ") + str(self.bin_session_id) + bstack1l1l_opy_ (u"ࠤࠥኯ"))
    def bstack1ll11l1ll11_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack1l1l_opy_ (u"ࠥࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡏࡱࡱࡩࠧኰ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False