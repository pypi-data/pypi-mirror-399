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
def bstack11111l1l1l_opy_(package_name):
    bstack1l1l_opy_ (u"ࠥࠦࠧࡉࡨࡦࡥ࡮ࠤ࡮࡬ࠠࡢࠢࡳࡥࡨࡱࡡࡨࡧࠣ࡭ࡸࠦࡩ࡯ࡵࡷࡥࡱࡲࡥࡥࠢ࡬ࡲࠥࡺࡨࡦࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺࠊࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡵࡧࡣ࡬ࡣࡪࡩࡤࡴࡡ࡮ࡧ࠽ࠤࡓࡧ࡭ࡦࠢࡲࡪࠥࡺࡨࡦࠢࡳࡥࡨࡱࡡࡨࡧࠣࡸࡴࠦࡣࡩࡧࡦ࡯ࠥ࠮ࡥ࠯ࡩ࠱࠰ࠥ࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡢࡴࡤࡰࡱ࡫࡬ࠨࠫࠍࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡦࡴࡵ࡬࠻ࠢࡗࡶࡺ࡫ࠠࡪࡨࠣࡴࡦࡩ࡫ࡢࡩࡨࠤ࡮ࡹࠠࡪࡰࡶࡸࡦࡲ࡬ࡦࡦ࠯ࠤࡋࡧ࡬ࡴࡧࠣࡳࡹ࡮ࡥࡳࡹ࡬ࡷࡪࠐࠠࠡࠢࠣࠦࠧࠨὋ")
    try:
        import importlib
        import importlib.util
        if hasattr(importlib.util, bstack1l1l_opy_ (u"ࠫ࡫࡯࡮ࡥࡡࡶࡴࡪࡩࠧὌ")):
            bstack11111ll1ll1_opy_ = importlib.util.find_spec(package_name)
            return bstack11111ll1ll1_opy_ is not None and bstack11111ll1ll1_opy_.loader is not None
        elif hasattr(importlib, bstack1l1l_opy_ (u"ࠬ࡬ࡩ࡯ࡦࡢࡰࡴࡧࡤࡦࡴࠪὍ")):
            bstack11111ll1l1l_opy_ = importlib.find_loader(package_name)
            return bstack11111ll1l1l_opy_ is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        pass
    return False