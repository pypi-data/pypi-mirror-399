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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll1l1l1_opy_
class bstack1ll1l11lll1_opy_(abc.ABC):
    bin_session_id: str
    bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_
    def __init__(self):
        self.bstack1lll1l1l1l1_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1lllll1l11l_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1lll111lll1_opy_(self):
        return (self.bstack1lll1l1l1l1_opy_ != None and self.bin_session_id != None and self.bstack1lllll1l11l_opy_ != None)
    def configure(self, bstack1lll1l1l1l1_opy_, config, bin_session_id: str, bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_):
        self.bstack1lll1l1l1l1_opy_ = bstack1lll1l1l1l1_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1lllll1l11l_opy_ = bstack1lllll1l11l_opy_
        if self.bin_session_id:
            self.logger.debug(bstack11111l_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡧࡧࠤࡲࡵࡤࡶ࡮ࡨࠤࢀࡹࡥ࡭ࡨ࠱ࡣࡤࡩ࡬ࡢࡵࡶࡣࡤ࠴࡟ࡠࡰࡤࡱࡪࡥ࡟ࡾ࠼ࠣࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧኧ") + str(self.bin_session_id) + bstack11111l_opy_ (u"ࠤࠥከ"))
    def bstack1l1lll1l1ll_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack11111l_opy_ (u"ࠥࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡏࡱࡱࡩࠧኩ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False