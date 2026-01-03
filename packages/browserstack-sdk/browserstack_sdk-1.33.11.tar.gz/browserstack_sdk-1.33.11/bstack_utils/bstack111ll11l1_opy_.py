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
from bstack_utils.constants import bstack11l1lll11l1_opy_
def bstack1l11llll1_opy_(bstack11l1lll11ll_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack1ll1lll111_opy_
    host = bstack1ll1lll111_opy_(cli.config, [bstack1l1l_opy_ (u"ࠤࡤࡴ࡮ࡹࠢ៓"), bstack1l1l_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ។"), bstack1l1l_opy_ (u"ࠦࡦࡶࡩࠣ៕")], bstack11l1lll11l1_opy_)
    return bstack1l1l_opy_ (u"ࠬࢁࡽ࠰ࡽࢀࠫ៖").format(host, bstack11l1lll11ll_opy_)