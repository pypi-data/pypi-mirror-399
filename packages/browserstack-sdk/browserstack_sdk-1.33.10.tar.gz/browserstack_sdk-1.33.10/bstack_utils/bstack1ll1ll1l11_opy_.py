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
import threading
import logging
import bstack_utils.accessibility as bstack1l1l11ll11_opy_
from bstack_utils.helper import bstack11l1l111l_opy_
logger = logging.getLogger(__name__)
def bstack11ll11l1ll_opy_(bstack1ll1l11l11_opy_):
  return True if bstack1ll1l11l11_opy_ in threading.current_thread().__dict__.keys() else False
def bstack1lll1ll11_opy_(context, *args):
    tags = getattr(args[0], bstack11111l_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ៚"), [])
    bstack1llll1ll1l_opy_ = bstack1l1l11ll11_opy_.bstack11llllllll_opy_(tags)
    threading.current_thread().isA11yTest = bstack1llll1ll1l_opy_
    try:
      bstack11ll1l11l_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11l1ll_opy_(bstack11111l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩ៛")) else context.browser
      if bstack11ll1l11l_opy_ and bstack11ll1l11l_opy_.session_id and bstack1llll1ll1l_opy_ and bstack11l1l111l_opy_(
              threading.current_thread(), bstack11111l_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪៜ"), None):
          threading.current_thread().isA11yTest = bstack1l1l11ll11_opy_.bstack11l111l111_opy_(bstack11ll1l11l_opy_, bstack1llll1ll1l_opy_)
    except Exception as e:
       logger.debug(bstack11111l_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡢ࠳࠴ࡽࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥ࠻ࠢࡾࢁࠬ៝").format(str(e)))
def bstack11l1lllll_opy_(bstack11ll1l11l_opy_):
    if bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ៞"), None) and bstack11l1l111l_opy_(
      threading.current_thread(), bstack11111l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭៟"), None) and not bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠨࡣ࠴࠵ࡾࡥࡳࡵࡱࡳࠫ០"), False):
      threading.current_thread().a11y_stop = True
      bstack1l1l11ll11_opy_.bstack11lll11lll_opy_(bstack11ll1l11l_opy_, name=bstack11111l_opy_ (u"ࠤࠥ១"), path=bstack11111l_opy_ (u"ࠥࠦ២"))