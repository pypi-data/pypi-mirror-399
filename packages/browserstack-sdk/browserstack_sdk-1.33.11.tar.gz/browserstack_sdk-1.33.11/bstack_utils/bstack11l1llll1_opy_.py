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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1ll1ll1l_opy_ import bstack11l1ll1l1l1_opy_
from bstack_utils.constants import *
import json
class bstack1lll111l1l_opy_:
    def __init__(self, bstack1l111l1l11_opy_, bstack11l1ll1ll11_opy_):
        self.bstack1l111l1l11_opy_ = bstack1l111l1l11_opy_
        self.bstack11l1ll1ll11_opy_ = bstack11l1ll1ll11_opy_
        self.bstack11l1ll1l1ll_opy_ = None
    def __call__(self):
        bstack11l1ll1lll1_opy_ = {}
        while True:
            self.bstack11l1ll1l1ll_opy_ = bstack11l1ll1lll1_opy_.get(
                bstack1l1l_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧៗ"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1ll1llll_opy_ = self.bstack11l1ll1l1ll_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1ll1llll_opy_ > 0:
                sleep(bstack11l1ll1llll_opy_ / 1000)
            params = {
                bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ៘"): self.bstack1l111l1l11_opy_,
                bstack1l1l_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ៙"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1lll1111_opy_ = bstack1l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦ៚") + bstack11l1lll111l_opy_ + bstack1l1l_opy_ (u"ࠥ࠳ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱ࡫࠲ࡺ࠶࠵ࠢ៛")
            if self.bstack11l1ll1ll11_opy_.lower() == bstack1l1l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࡷࠧៜ"):
                bstack11l1ll1lll1_opy_ = bstack11l1ll1l1l1_opy_.results(bstack11l1lll1111_opy_, params)
            else:
                bstack11l1ll1lll1_opy_ = bstack11l1ll1l1l1_opy_.bstack11l1ll1l11l_opy_(bstack11l1lll1111_opy_, params)
            if str(bstack11l1ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ៝"), bstack1l1l_opy_ (u"࠭࠲࠱࠲ࠪ៞"))) != bstack1l1l_opy_ (u"ࠧ࠵࠲࠷ࠫ៟"):
                break
        return bstack11l1ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠨࡦࡤࡸࡦ࠭០"), bstack11l1ll1lll1_opy_)