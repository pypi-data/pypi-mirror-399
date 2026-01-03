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
import re
from typing import List, Dict, Any
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
logger = get_logger(__name__)
class bstack1ll1l1ll1ll_opy_:
    bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡇࡺࡹࡴࡰ࡯ࡗࡥ࡬ࡓࡡ࡯ࡣࡪࡩࡷࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡳࠡࡷࡷ࡭ࡱ࡯ࡴࡺࠢࡰࡩࡹ࡮࡯ࡥࡵࠣࡸࡴࠦࡳࡦࡶࠣࡥࡳࡪࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࠢࡦࡹࡸࡺ࡯࡮ࠢࡷࡥ࡬ࠦ࡭ࡦࡶࡤࡨࡦࡺࡡ࠯ࠌࠣࠤࠥࠦࡉࡵࠢࡰࡥ࡮ࡴࡴࡢ࡫ࡱࡷࠥࡺࡷࡰࠢࡶࡩࡵࡧࡲࡢࡶࡨࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳ࡫ࡨࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠠ࡭ࡧࡹࡩࡱࠦࡡ࡯ࡦࠣࡦࡺ࡯࡬ࡥࠢ࡯ࡩࡻ࡫࡬ࠡࡥࡸࡷࡹࡵ࡭ࠡࡶࡤ࡫ࡸ࠴ࠊࠡࠢࠣࠤࡊࡧࡣࡩࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤࡪࡴࡴࡳࡻࠣ࡭ࡸࠦࡥࡹࡲࡨࡧࡹ࡫ࡤࠡࡶࡲࠤࡧ࡫ࠠࡴࡶࡵࡹࡨࡺࡵࡳࡧࡧࠤࡦࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡ࡭ࡨࡽ࠿ࠦࡻࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡦࡪࡧ࡯ࡨࡤࡺࡹࡱࡧࠥ࠾ࠥࠨ࡭ࡶ࡮ࡷ࡭ࡤࡪࡲࡰࡲࡧࡳࡼࡴࠢ࠭ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡷࡣ࡯ࡹࡪࡹࠢ࠻ࠢ࡞ࡰ࡮ࡹࡴࠡࡱࡩࠤࡹࡧࡧࠡࡸࡤࡰࡺ࡫ࡳ࡞ࠌࠣࠤࠥࠦࠠࠡࠢࢀࠎࠥࠦࠠࠡࠤࠥࠦᙌ")
    _11ll1ll1ll1_opy_: Dict[str, Dict[str, Any]] = {}
    _11ll1lll1l1_opy_: Dict[str, Dict[str, Any]] = {}
    @staticmethod
    def set_custom_tag(bstack1ll11lllll_opy_: str, key_value: str, bstack11ll1lll111_opy_: bool = False) -> None:
        if not bstack1ll11lllll_opy_ or not key_value or bstack1ll11lllll_opy_.strip() == bstack1l1l_opy_ (u"ࠦࠧᙍ") or key_value.strip() == bstack1l1l_opy_ (u"ࠧࠨᙎ"):
            logger.error(bstack1l1l_opy_ (u"ࠨ࡫ࡦࡻࡢࡲࡦࡳࡥࠡࡣࡱࡨࠥࡱࡥࡺࡡࡹࡥࡱࡻࡥࠡ࡯ࡸࡷࡹࠦࡢࡦࠢࡱࡳࡳ࠳࡮ࡶ࡮࡯ࠤࡦࡴࡤࠡࡰࡲࡲ࠲࡫࡭ࡱࡶࡼࠦᙏ"))
        values: List[str] = bstack1ll1l1ll1ll_opy_.bstack11ll1llllll_opy_(key_value)
        bstack11ll1lll1ll_opy_ = {bstack1l1l_opy_ (u"ࠢࡧ࡫ࡨࡰࡩࡥࡴࡺࡲࡨࠦᙐ"): bstack1l1l_opy_ (u"ࠣ࡯ࡸࡰࡹ࡯࡟ࡥࡴࡲࡴࡩࡵࡷ࡯ࠤᙑ"), bstack1l1l_opy_ (u"ࠤࡹࡥࡱࡻࡥࡴࠤᙒ"): values}
        bstack11ll1lll11l_opy_ = bstack1ll1l1ll1ll_opy_._11ll1lll1l1_opy_ if bstack11ll1lll111_opy_ else bstack1ll1l1ll1ll_opy_._11ll1ll1ll1_opy_
        if bstack1ll11lllll_opy_ in bstack11ll1lll11l_opy_:
            bstack11ll1lllll1_opy_ = bstack11ll1lll11l_opy_[bstack1ll11lllll_opy_]
            bstack11ll1ll1lll_opy_ = bstack11ll1lllll1_opy_.get(bstack1l1l_opy_ (u"ࠥࡺࡦࡲࡵࡦࡵࠥᙓ"), [])
            for val in values:
                if val not in bstack11ll1ll1lll_opy_:
                    bstack11ll1ll1lll_opy_.append(val)
            bstack11ll1lllll1_opy_[bstack1l1l_opy_ (u"ࠦࡻࡧ࡬ࡶࡧࡶࠦᙔ")] = bstack11ll1ll1lll_opy_
        else:
            bstack11ll1lll11l_opy_[bstack1ll11lllll_opy_] = bstack11ll1lll1ll_opy_
    @staticmethod
    def bstack11lll1ll1ll_opy_() -> Dict[str, Dict[str, Any]]:
        return bstack1ll1l1ll1ll_opy_._11ll1ll1ll1_opy_
    @staticmethod
    def bstack11ll1llll1l_opy_() -> Dict[str, Dict[str, Any]]:
        return bstack1ll1l1ll1ll_opy_._11ll1lll1l1_opy_
    @staticmethod
    def bstack11ll1llllll_opy_(bstack11ll1llll11_opy_: str) -> List[str]:
        bstack1l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡖࡴࡱ࡯ࡴࡴࠢࡷ࡬ࡪࠦࡩ࡯ࡲࡸࡸࠥࡹࡴࡳ࡫ࡱ࡫ࠥࡨࡹࠡࡥࡲࡱࡲࡧࡳࠡࡹ࡫࡭ࡱ࡫ࠠࡳࡧࡶࡴࡪࡩࡴࡪࡰࡪࠤࡩࡵࡵࡣ࡮ࡨ࠱ࡶࡻ࡯ࡵࡧࡧࠤࡸࡻࡢࡴࡶࡵ࡭ࡳ࡭ࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡊࡴࡸࠠࡦࡺࡤࡱࡵࡲࡥ࠻ࠢࠪࡥ࠱ࠦࠢࡣ࠮ࡦࠦ࠱ࠦࡤࠨࠢ࠰ࡂࠥࡡࠧࡢࠩ࠯ࠤࠬࡨࠬࡤࠩ࠯ࠤࠬࡪࠧ࡞ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᙕ")
        pattern = re.compile(bstack1l1l_opy_ (u"ࡸࠧࠣࠪ࡞ࡢࠧࡣࠪࠪࠤࡿࠬࡠࡤࠬ࡞࠭ࠬࠫᙖ"))
        result = []
        for match in pattern.finditer(bstack11ll1llll11_opy_):
            if match.group(1) is not None:
                result.append(match.group(1).strip())
            elif match.group(2) is not None:
                result.append(match.group(2).strip())
        return result
    def __new__(cls, *args, **kwargs):
        raise Exception(bstack1l1l_opy_ (u"ࠢࡖࡶ࡬ࡰ࡮ࡺࡹࠡࡥ࡯ࡥࡸࡹࠠࡴࡪࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡧ࡫ࠠࡪࡰࡶࡸࡦࡴࡴࡪࡣࡷࡩࡩࠨᙗ"))