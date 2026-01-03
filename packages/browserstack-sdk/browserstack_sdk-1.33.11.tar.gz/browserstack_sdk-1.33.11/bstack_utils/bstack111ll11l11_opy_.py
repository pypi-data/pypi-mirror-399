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
import os
import threading
from bstack_utils.helper import bstack1l1l1111l1_opy_
from bstack_utils.constants import bstack11l11lll1ll_opy_, EVENTS, STAGE
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
logger = get_logger(__name__)
class bstack1l1ll11111_opy_:
    bstack1lllll11111l_opy_ = None
    @classmethod
    def bstack11l111llll_opy_(cls):
        if cls.on() and os.getenv(bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠣ⊚")):
            logger.info(
                bstack1l1l_opy_ (u"࡛ࠫ࡯ࡳࡪࡶࠣ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃࠠࡵࡱࠣࡺ࡮࡫ࡷࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡳࡳࡷࡺࠬࠡ࡫ࡱࡷ࡮࡭ࡨࡵࡵ࠯ࠤࡦࡴࡤࠡ࡯ࡤࡲࡾࠦ࡭ࡰࡴࡨࠤࡩ࡫ࡢࡶࡩࡪ࡭ࡳ࡭ࠠࡪࡰࡩࡳࡷࡳࡡࡵ࡫ࡲࡲࠥࡧ࡬࡭ࠢࡤࡸࠥࡵ࡮ࡦࠢࡳࡰࡦࡩࡥࠢ࡞ࡱࠫ⊛").format(os.getenv(bstack1l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠥ⊜"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⊝"), None) is None or os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⊞")] == bstack1l1l_opy_ (u"ࠣࡰࡸࡰࡱࠨ⊟"):
            return False
        return True
    @classmethod
    def bstack1lll1ll1ll11_opy_(cls, bs_config, framework=bstack1l1l_opy_ (u"ࠤࠥ⊠")):
        bstack11l1ll1111l_opy_ = False
        for fw in bstack11l11lll1ll_opy_:
            if fw in framework:
                bstack11l1ll1111l_opy_ = True
        return bstack1l1l1111l1_opy_(bs_config.get(bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ⊡"), bstack11l1ll1111l_opy_))
    @classmethod
    def bstack1lll1l1lll1l_opy_(cls, framework):
        return framework in bstack11l11lll1ll_opy_
    @classmethod
    def bstack1lll1ll1llll_opy_(cls, bs_config, framework):
        return cls.bstack1lll1ll1ll11_opy_(bs_config, framework) is True and cls.bstack1lll1l1lll1l_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⊢"), None)
    @staticmethod
    def bstack111ll111l1_opy_():
        if getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⊣"), None):
            return {
                bstack1l1l_opy_ (u"࠭ࡴࡺࡲࡨࠫ⊤"): bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࠬ⊥"),
                bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⊦"): getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭⊧"), None)
            }
        if getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⊨"), None):
            return {
                bstack1l1l_opy_ (u"ࠫࡹࡿࡰࡦࠩ⊩"): bstack1l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ⊪"),
                bstack1l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⊫"): getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⊬"), None)
            }
        return None
    @staticmethod
    def bstack1lll1l1llll1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1l1ll11111_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack1111llll1l_opy_(test, hook_name=None):
        bstack1lll1l1ll1l1_opy_ = test.parent
        if hook_name in [bstack1l1l_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸ࠭⊭"), bstack1l1l_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪ⊮"), bstack1l1l_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ⊯"), bstack1l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭⊰")]:
            bstack1lll1l1ll1l1_opy_ = test
        scope = []
        while bstack1lll1l1ll1l1_opy_ is not None:
            scope.append(bstack1lll1l1ll1l1_opy_.name)
            bstack1lll1l1ll1l1_opy_ = bstack1lll1l1ll1l1_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1lll1l1lll11_opy_(hook_type):
        if hook_type == bstack1l1l_opy_ (u"ࠧࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠥ⊱"):
            return bstack1l1l_opy_ (u"ࠨࡓࡦࡶࡸࡴࠥ࡮࡯ࡰ࡭ࠥ⊲")
        elif hook_type == bstack1l1l_opy_ (u"ࠢࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠦ⊳"):
            return bstack1l1l_opy_ (u"ࠣࡖࡨࡥࡷࡪ࡯ࡸࡰࠣ࡬ࡴࡵ࡫ࠣ⊴")
    @staticmethod
    def bstack1lll1l1ll1ll_opy_(bstack11ll111ll_opy_):
        try:
            if not bstack1l1ll11111_opy_.on():
                return bstack11ll111ll_opy_
            if os.environ.get(bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔࠢ⊵"), None) == bstack1l1l_opy_ (u"ࠥࡸࡷࡻࡥࠣ⊶"):
                tests = os.environ.get(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࡡࡗࡉࡘ࡚ࡓࠣ⊷"), None)
                if tests is None or tests == bstack1l1l_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ⊸"):
                    return bstack11ll111ll_opy_
                bstack11ll111ll_opy_ = tests.split(bstack1l1l_opy_ (u"࠭ࠬࠨ⊹"))
                return bstack11ll111ll_opy_
        except Exception as exc:
            logger.debug(bstack1l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡲࡦࡴࡸࡲࠥ࡮ࡡ࡯ࡦ࡯ࡩࡷࡀࠠࠣ⊺") + str(str(exc)) + bstack1l1l_opy_ (u"ࠣࠤ⊻"))
        return bstack11ll111ll_opy_