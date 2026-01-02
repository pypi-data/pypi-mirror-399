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
from bstack_utils.constants import bstack11l1lll1l11_opy_
def bstack11l111l11_opy_(bstack11l1lll1l1l_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack1111l1ll_opy_
    host = bstack1111l1ll_opy_(cli.config, [bstack11111l_opy_ (u"ࠤࡤࡴ࡮ࡹࠢ៌"), bstack11111l_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ៍"), bstack11111l_opy_ (u"ࠦࡦࡶࡩࠣ៎")], bstack11l1lll1l11_opy_)
    return bstack11111l_opy_ (u"ࠬࢁࡽ࠰ࡽࢀࠫ៏").format(host, bstack11l1lll1l1l_opy_)