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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1lll11ll_opy_ import bstack11l1ll1lll1_opy_
from bstack_utils.constants import *
import json
class bstack1ll1ll1ll1_opy_:
    def __init__(self, bstack111llll1_opy_, bstack11l1lll111l_opy_):
        self.bstack111llll1_opy_ = bstack111llll1_opy_
        self.bstack11l1lll111l_opy_ = bstack11l1lll111l_opy_
        self.bstack11l1ll1ll1l_opy_ = None
    def __call__(self):
        bstack11l1ll1l1ll_opy_ = {}
        while True:
            self.bstack11l1ll1ll1l_opy_ = bstack11l1ll1l1ll_opy_.get(
                bstack11111l_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧ័"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1ll1llll_opy_ = self.bstack11l1ll1ll1l_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1ll1llll_opy_ > 0:
                sleep(bstack11l1ll1llll_opy_ / 1000)
            params = {
                bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ៑"): self.bstack111llll1_opy_,
                bstack11111l_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳ្ࠫ"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1lll11l1_opy_ = bstack11111l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦ៓") + bstack11l1ll1ll11_opy_ + bstack11111l_opy_ (u"ࠥ࠳ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱ࡫࠲ࡺ࠶࠵ࠢ។")
            if self.bstack11l1lll111l_opy_.lower() == bstack11111l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࡷࠧ៕"):
                bstack11l1ll1l1ll_opy_ = bstack11l1ll1lll1_opy_.results(bstack11l1lll11l1_opy_, params)
            else:
                bstack11l1ll1l1ll_opy_ = bstack11l1ll1lll1_opy_.bstack11l1lll1111_opy_(bstack11l1lll11l1_opy_, params)
            if str(bstack11l1ll1l1ll_opy_.get(bstack11111l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ៖"), bstack11111l_opy_ (u"࠭࠲࠱࠲ࠪៗ"))) != bstack11111l_opy_ (u"ࠧ࠵࠲࠷ࠫ៘"):
                break
        return bstack11l1ll1l1ll_opy_.get(bstack11111l_opy_ (u"ࠨࡦࡤࡸࡦ࠭៙"), bstack11l1ll1l1ll_opy_)