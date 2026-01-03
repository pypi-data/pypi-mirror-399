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
import bstack_utils.accessibility as bstack1lllllll11_opy_
from bstack_utils.helper import bstack11llll11ll_opy_
logger = logging.getLogger(__name__)
def bstack11llll111l_opy_(bstack1ll11lllll_opy_):
  return True if bstack1ll11lllll_opy_ in threading.current_thread().__dict__.keys() else False
def bstack1l1ll11ll_opy_(context, *args):
    tags = getattr(args[0], bstack1l1l_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ១"), [])
    bstack1l1llll111_opy_ = bstack1lllllll11_opy_.bstack1l111lll_opy_(tags)
    threading.current_thread().isA11yTest = bstack1l1llll111_opy_
    try:
      bstack1ll1ll11ll_opy_ = threading.current_thread().bstackSessionDriver if bstack11llll111l_opy_(bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩ២")) else context.browser
      if bstack1ll1ll11ll_opy_ and bstack1ll1ll11ll_opy_.session_id and bstack1l1llll111_opy_ and bstack11llll11ll_opy_(
              threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ៣"), None):
          threading.current_thread().isA11yTest = bstack1lllllll11_opy_.bstack1l1111111l_opy_(bstack1ll1ll11ll_opy_, bstack1l1llll111_opy_)
    except Exception as e:
       logger.debug(bstack1l1l_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡢ࠳࠴ࡽࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥ࠻ࠢࡾࢁࠬ៤").format(str(e)))
def bstack111l1l1ll_opy_(bstack1ll1ll11ll_opy_):
    if bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ៥"), None) and bstack11llll11ll_opy_(
      threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭៦"), None) and not bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡣ࠴࠵ࡾࡥࡳࡵࡱࡳࠫ៧"), False):
      threading.current_thread().a11y_stop = True
      bstack1lllllll11_opy_.bstack11llll1ll_opy_(bstack1ll1ll11ll_opy_, name=bstack1l1l_opy_ (u"ࠤࠥ៨"), path=bstack1l1l_opy_ (u"ࠥࠦ៩"))