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
import re
from bstack_utils.bstack1l11llll_opy_ import bstack1lllll1l11ll_opy_
from bstack_utils.bstack111111l1l1_opy_ import bstack1llllll1ll1_opy_
def bstack1lllll11lll1_opy_(fixture_name):
    if fixture_name.startswith(bstack11111l_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ ")):
        return bstack11111l_opy_ (u"࠭ࡳࡦࡶࡸࡴ࠲࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧ​")
    elif fixture_name.startswith(bstack11111l_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ‌")):
        return bstack11111l_opy_ (u"ࠨࡵࡨࡸࡺࡶ࠭࡮ࡱࡧࡹࡱ࡫ࠧ‍")
    elif fixture_name.startswith(bstack11111l_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ‎")):
        return bstack11111l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲ࠲࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧ‏")
    elif fixture_name.startswith(bstack11111l_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ‐")):
        return bstack11111l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࠭࡮ࡱࡧࡹࡱ࡫ࠧ‑")
def bstack1lllll1l1111_opy_(fixture_name):
    return bool(re.match(bstack11111l_opy_ (u"࠭࡞ࡠࡺࡸࡲ࡮ࡺ࡟ࠩࡵࡨࡸࡺࡶࡼࡵࡧࡤࡶࡩࡵࡷ࡯ࠫࡢࠬ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࢂ࡭ࡰࡦࡸࡰࡪ࠯࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠ࠰࠭ࠫ‒"), fixture_name))
def bstack1lllll1l11l1_opy_(fixture_name):
    return bool(re.match(bstack11111l_opy_ (u"ࠧ࡟ࡡࡻࡹࡳ࡯ࡴࡠࠪࡶࡩࡹࡻࡰࡽࡶࡨࡥࡷࡪ࡯ࡸࡰࠬࡣࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࠴ࠪࠨ–"), fixture_name))
def bstack1lllll11l1ll_opy_(fixture_name):
    return bool(re.match(bstack11111l_opy_ (u"ࠨࡠࡢࡼࡺࡴࡩࡵࡡࠫࡷࡪࡺࡵࡱࡾࡷࡩࡦࡸࡤࡰࡹࡱ࠭ࡤࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࠴ࠪࠨ—"), fixture_name))
def bstack1lllll11l11l_opy_(fixture_name):
    if fixture_name.startswith(bstack11111l_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ―")):
        return bstack11111l_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡩࡹࡳࡩࡴࡪࡱࡱࠫ‖"), bstack11111l_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ‗")
    elif fixture_name.startswith(bstack11111l_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡹࡥࡵࡷࡳࡣࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ‘")):
        return bstack11111l_opy_ (u"࠭ࡳࡦࡶࡸࡴ࠲ࡳ࡯ࡥࡷ࡯ࡩࠬ’"), bstack11111l_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏࠫ‚")
    elif fixture_name.startswith(bstack11111l_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭‛")):
        return bstack11111l_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭“"), bstack11111l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ”")
    elif fixture_name.startswith(bstack11111l_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ„")):
        return bstack11111l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࠭࡮ࡱࡧࡹࡱ࡫ࠧ‟"), bstack11111l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩ†")
    return None, None
def bstack1lllll11ll1l_opy_(hook_name):
    if hook_name in [bstack11111l_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭‡"), bstack11111l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ•")]:
        return hook_name.capitalize()
    return hook_name
def bstack1lllll11llll_opy_(hook_name):
    if hook_name in [bstack11111l_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࠪ‣"), bstack11111l_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩ․")]:
        return bstack11111l_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ‥")
    elif hook_name in [bstack11111l_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲࡵࡤࡶ࡮ࡨࠫ…"), bstack11111l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠫ‧")]:
        return bstack11111l_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏࠫ ")
    elif hook_name in [bstack11111l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬ "), bstack11111l_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲ࡫ࡴࡩࡱࡧࠫ‪")]:
        return bstack11111l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ‫")
    elif hook_name in [bstack11111l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭‬"), bstack11111l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸ࠭‭")]:
        return bstack11111l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩ‮")
    return hook_name
def bstack1lllll11l111_opy_(node, scenario):
    if hasattr(node, bstack11111l_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩ ")):
        parts = node.nodeid.rsplit(bstack11111l_opy_ (u"ࠣ࡝ࠥ‰"))
        params = parts[-1]
        return bstack11111l_opy_ (u"ࠤࡾࢁࠥࡡࡻࡾࠤ‱").format(scenario.name, params)
    return scenario.name
def bstack1lllll11l1l1_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack11111l_opy_ (u"ࠪࡧࡦࡲ࡬ࡴࡲࡨࡧࠬ′")):
            examples = list(node.callspec.params[bstack11111l_opy_ (u"ࠫࡤࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡨࡼࡦࡳࡰ࡭ࡧࠪ″")].values())
        return examples
    except:
        return []
def bstack1lllll1l111l_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1lllll1l1l11_opy_(report):
    try:
        status = bstack11111l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ‴")
        if report.passed or (report.failed and hasattr(report, bstack11111l_opy_ (u"ࠨࡷࡢࡵࡻࡪࡦ࡯࡬ࠣ‵"))):
            status = bstack11111l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ‶")
        elif report.skipped:
            status = bstack11111l_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ‷")
        bstack1lllll1l11ll_opy_(status)
    except:
        pass
def bstack1lll1l111_opy_(status):
    try:
        bstack1lllll11ll11_opy_ = bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ‸")
        if status == bstack11111l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ‹"):
            bstack1lllll11ll11_opy_ = bstack11111l_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ›")
        elif status == bstack11111l_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭※"):
            bstack1lllll11ll11_opy_ = bstack11111l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ‼")
        bstack1lllll1l11ll_opy_(bstack1lllll11ll11_opy_)
    except:
        pass
def bstack1lllll1l1l1l_opy_(item=None, report=None, summary=None, extra=None):
    return
def bstack1ll1l11ll_opy_():
    bstack11111l_opy_ (u"ࠢࠣࠤࡆ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡵࡿࡴࡦࡵࡷ࠱ࡵࡧࡲࡢ࡮࡯ࡩࡱࠦࡩࡴࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠥࡧ࡮ࡥࠢࡵࡩࡹࡻࡲ࡯ࠢࡗࡶࡺ࡫ࠠࡪࡨࠣࡪࡴࡻ࡮ࡥ࠮ࠣࡊࡦࡲࡳࡦࠢࡲࡸ࡭࡫ࡲࡸ࡫ࡶࡩࠧࠨࠢ‽")
    return bstack1llllll1ll1_opy_(bstack11111l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡲࡤࡶࡦࡲ࡬ࡦ࡮ࠪ‾"))