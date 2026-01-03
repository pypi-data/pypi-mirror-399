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
import re
from enum import Enum
bstack11llll1l1_opy_ = {
  bstack1l1l_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭៸"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࠩ៹"),
  bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ៺"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡫ࡦࡻࠪ៻"),
  bstack1l1l_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫ៼"): bstack1l1l_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭៽"),
  bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ៾"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫࡟ࡸ࠵ࡦࠫ៿"),
  bstack1l1l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ᠀"): bstack1l1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࠧ᠁"),
  bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ᠂"): bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧ᠃"),
  bstack1l1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ᠄"): bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ᠅"),
  bstack1l1l_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪ᠆"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡩ࡫ࡢࡶࡩࠪ᠇"),
  bstack1l1l_opy_ (u"࠭ࡣࡰࡰࡶࡳࡱ࡫ࡌࡰࡩࡶࠫ᠈"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰࡰࡶࡳࡱ࡫ࠧ᠉"),
  bstack1l1l_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭᠊"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭᠋"),
  bstack1l1l_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧ᠌"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧ᠍"),
  bstack1l1l_opy_ (u"ࠬࡼࡩࡥࡧࡲࠫ᠎"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡼࡩࡥࡧࡲࠫ᠏"),
  bstack1l1l_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭᠐"): bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭᠑"),
  bstack1l1l_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩ᠒"): bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩ᠓"),
  bstack1l1l_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩ᠔"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩ᠕"),
  bstack1l1l_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨ᠖"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨ᠗"),
  bstack1l1l_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪ᠘"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫ᠙"),
  bstack1l1l_opy_ (u"ࠪࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩ᠚"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩ᠛"),
  bstack1l1l_opy_ (u"ࠬ࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪ᠜"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪ᠝"),
  bstack1l1l_opy_ (u"ࠧ࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧ᠞"): bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧ᠟"),
  bstack1l1l_opy_ (u"ࠩࡶࡩࡳࡪࡋࡦࡻࡶࠫᠠ"): bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡳࡪࡋࡦࡻࡶࠫᠡ"),
  bstack1l1l_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ᠢ"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ᠣ"),
  bstack1l1l_opy_ (u"࠭ࡨࡰࡵࡷࡷࠬᠤ"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡨࡰࡵࡷࡷࠬᠥ"),
  bstack1l1l_opy_ (u"ࠨࡤࡩࡧࡦࡩࡨࡦࠩᠦ"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡩࡧࡦࡩࡨࡦࠩᠧ"),
  bstack1l1l_opy_ (u"ࠪࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫᠨ"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫᠩ"),
  bstack1l1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨᠪ"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨᠫ"),
  bstack1l1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫᠬ"): bstack1l1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨᠭ"),
  bstack1l1l_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭ᠮ"): bstack1l1l_opy_ (u"ࠪࡶࡪࡧ࡬ࡠ࡯ࡲࡦ࡮ࡲࡥࠨᠯ"),
  bstack1l1l_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫᠰ"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᠱ"),
  bstack1l1l_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭ᠲ"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭ᠳ"),
  bstack1l1l_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩᠴ"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩᠵ"),
  bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡌࡲࡸ࡫ࡣࡶࡴࡨࡇࡪࡸࡴࡴࠩᠶ"): bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡗࡸࡲࡃࡦࡴࡷࡷࠬᠷ"),
  bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᠸ"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᠹ"),
  bstack1l1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧᠺ"): bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡱࡸࡶࡨ࡫ࠧᠻ"),
  bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫᠼ"): bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫᠽ"),
  bstack1l1l_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ᠾ"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ᠿ"),
  bstack1l1l_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪ࡙ࡩ࡮ࠩᡀ"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡥ࡯ࡣࡥࡰࡪ࡙ࡩ࡮ࠩᡁ"),
  bstack1l1l_opy_ (u"ࠨࡵ࡬ࡱࡔࡶࡴࡪࡱࡱࡷࠬᡂ"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵ࡬ࡱࡔࡶࡴࡪࡱࡱࡷࠬᡃ"),
  bstack1l1l_opy_ (u"ࠪࡹࡵࡲ࡯ࡢࡦࡐࡩࡩ࡯ࡡࠨᡄ"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡵࡲ࡯ࡢࡦࡐࡩࡩ࡯ࡡࠨᡅ"),
  bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᡆ"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᡇ"),
  bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᡈ"): bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᡉ")
}
bstack11l1l1l1l1l_opy_ = [
  bstack1l1l_opy_ (u"ࠩࡲࡷࠬᡊ"),
  bstack1l1l_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᡋ"),
  bstack1l1l_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᡌ"),
  bstack1l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᡍ"),
  bstack1l1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪᡎ"),
  bstack1l1l_opy_ (u"ࠧࡳࡧࡤࡰࡒࡵࡢࡪ࡮ࡨࠫᡏ"),
  bstack1l1l_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᡐ"),
]
bstack11lll1111l_opy_ = {
  bstack1l1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫᡑ"): [bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫᡒ"), bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡙ࡘࡋࡒࡠࡐࡄࡑࡊ࠭ᡓ")],
  bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᡔ"): bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡃࡄࡇࡖࡗࡤࡑࡅ࡚ࠩᡕ"),
  bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪᡖ"): bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡎࡂࡏࡈࠫᡗ"),
  bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᡘ"): bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡖࡔࡐࡅࡄࡖࡢࡒࡆࡓࡅࠨᡙ"),
  bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᡚ"): bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧᡛ"),
  bstack1l1l_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ᡜ"): bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡂࡔࡄࡐࡑࡋࡌࡔࡡࡓࡉࡗࡥࡐࡍࡃࡗࡊࡔࡘࡍࠨᡝ"),
  bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬᡞ"): bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒࠧᡟ"),
  bstack1l1l_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᡠ"): bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࡡࡗࡉࡘ࡚ࡓࠨᡡ"),
  bstack1l1l_opy_ (u"ࠬࡧࡰࡱࠩᡢ"): [bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡐࡑࡡࡌࡈࠬᡣ"), bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡑࡒࠪᡤ")],
  bstack1l1l_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪᡥ"): bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡕࡇࡏࡤࡒࡏࡈࡎࡈ࡚ࡊࡒࠧᡦ"),
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᡧ"): bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᡨ"),
  bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩᡩ"): [bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡓࡇ࡙ࡅࡓࡘࡄࡆࡎࡒࡉࡕ࡛ࠪᡪ"), bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡗࡋࡐࡐࡔࡗࡍࡓࡍࠧᡫ")],
  bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᡬ"): bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡘࡖࡇࡕࡓࡄࡃࡏࡉࠬᡭ"),
  bstack1l1l_opy_ (u"ࠪࡷࡲࡧࡲࡵࡕࡨࡰࡪࡩࡴࡪࡱࡱࡊࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࡨࡷࡊࡔࡖࠨᡮ"): bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡓࡗࡉࡈࡆࡕࡗࡖࡆ࡚ࡉࡐࡐࡢࡗࡒࡇࡒࡕࡡࡖࡉࡑࡋࡃࡕࡋࡒࡒࡤࡌࡅࡂࡖࡘࡖࡊࡥࡂࡓࡃࡑࡇࡍࡋࡓࠨᡯ")
}
bstack11l1l111l_opy_ = {
  bstack1l1l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᡰ"): [bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡴࡢࡲࡦࡳࡥࠨᡱ"), bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡵࡒࡦࡳࡥࠨᡲ")],
  bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫᡳ"): [bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡠ࡭ࡨࡽࠬᡴ"), bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬᡵ")],
  bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᡶ"): bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᡷ"),
  bstack1l1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫᡸ"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ᡹"),
  bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ᡺"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ᡻"),
  bstack1l1l_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ᡼"): [bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡴࡵࡶࠧ᡽"), bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫ᡾")],
  bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ᡿"): bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࠬᢀ"),
  bstack1l1l_opy_ (u"ࠨࡴࡨࡶࡺࡴࡔࡦࡵࡷࡷࠬᢁ"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡴࡨࡶࡺࡴࡔࡦࡵࡷࡷࠬᢂ"),
  bstack1l1l_opy_ (u"ࠪࡥࡵࡶࠧᢃ"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡵࡶࠧᢄ"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᢅ"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᢆ"),
  bstack1l1l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᢇ"): bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᢈ"),
  bstack1l1l_opy_ (u"ࠤࡶࡱࡦࡸࡴࡔࡧ࡯ࡩࡨࡺࡩࡰࡰࡉࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࡧࡶࡇࡑࡏࠢᢉ"): bstack1l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠴ࡳ࡮ࡣࡵࡸࡘ࡫࡬ࡦࡥࡷ࡭ࡴࡴࡆࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࡫ࡳࠣᢊ"),
}
bstack1l1llll1_opy_ = {
  bstack1l1l_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧᢋ"): bstack1l1l_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᢌ"),
  bstack1l1l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᢍ"): [bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᢎ"), bstack1l1l_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫᢏ")],
  bstack1l1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧᢐ"): bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨᢑ"),
  bstack1l1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨᢒ"): bstack1l1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬᢓ"),
  bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᢔ"): [bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨᢕ"), bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡱࡥࡲ࡫ࠧᢖ")],
  bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᢗ"): bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᢘ"),
  bstack1l1l_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨᢙ"): bstack1l1l_opy_ (u"ࠬࡸࡥࡢ࡮ࡢࡱࡴࡨࡩ࡭ࡧࠪᢚ"),
  bstack1l1l_opy_ (u"࠭ࡡࡱࡲ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᢛ"): [bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡱࡲ࡬ࡹࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᢜ"), bstack1l1l_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᢝ")],
  bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡰࡵࡋࡱࡷࡪࡩࡵࡳࡧࡆࡩࡷࡺࡳࠨᢞ"): [bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡖࡷࡱࡉࡥࡳࡶࡶࠫᢟ"), bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡗࡸࡲࡃࡦࡴࡷࠫᢠ")]
}
bstack11llllll1_opy_ = [
  bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡎࡴࡳࡦࡥࡸࡶࡪࡉࡥࡳࡶࡶࠫᢡ"),
  bstack1l1l_opy_ (u"࠭ࡰࡢࡩࡨࡐࡴࡧࡤࡔࡶࡵࡥࡹ࡫ࡧࡺࠩᢢ"),
  bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࠭ᢣ"),
  bstack1l1l_opy_ (u"ࠨࡵࡨࡸ࡜࡯࡮ࡥࡱࡺࡖࡪࡩࡴࠨᢤ"),
  bstack1l1l_opy_ (u"ࠩࡷ࡭ࡲ࡫࡯ࡶࡶࡶࠫᢥ"),
  bstack1l1l_opy_ (u"ࠪࡷࡹࡸࡩࡤࡶࡉ࡭ࡱ࡫ࡉ࡯ࡶࡨࡶࡦࡩࡴࡢࡤ࡬ࡰ࡮ࡺࡹࠨᢦ"),
  bstack1l1l_opy_ (u"ࠫࡺࡴࡨࡢࡰࡧࡰࡪࡪࡐࡳࡱࡰࡴࡹࡈࡥࡩࡣࡹ࡭ࡴࡸࠧᢧ"),
  bstack1l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᢨ"),
  bstack1l1l_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶᢩࠫ"),
  bstack1l1l_opy_ (u"ࠧ࡮ࡵ࠽ࡩࡩ࡭ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᢪ"),
  bstack1l1l_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᢫"),
  bstack1l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪ᢬"),
]
bstack111111l1l_opy_ = [
  bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ᢭"),
  bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ᢮"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ᢯"),
  bstack1l1l_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ᢰ"),
  bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪᢱ"),
  bstack1l1l_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪᢲ"),
  bstack1l1l_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬᢳ"),
  bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧᢴ"),
  bstack1l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧᢵ"),
  bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪᢶ"),
  bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪᢷ"),
  bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࠧᢸ"),
  bstack1l1l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵࠪᢹ"),
  bstack1l1l_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡖࡤ࡫ࠬᢺ"),
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᢻ"),
  bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᢼ"),
  bstack1l1l_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩᢽ"),
  bstack1l1l_opy_ (u"࠭ࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢ࠵ࠬᢾ"),
  bstack1l1l_opy_ (u"ࠧࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣ࠷࠭ᢿ"),
  bstack1l1l_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠹ࠧᣀ"),
  bstack1l1l_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠴ࠨᣁ"),
  bstack1l1l_opy_ (u"ࠪࡇ࡚࡙ࡔࡐࡏࡢࡘࡆࡍ࡟࠶ࠩᣂ"),
  bstack1l1l_opy_ (u"ࠫࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࠸ࠪᣃ"),
  bstack1l1l_opy_ (u"ࠬࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࠺ࠫᣄ"),
  bstack1l1l_opy_ (u"࠭ࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢ࠼ࠬᣅ"),
  bstack1l1l_opy_ (u"ࠧࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣ࠾࠭ᣆ"),
  bstack1l1l_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧᣇ"),
  bstack1l1l_opy_ (u"ࠩࡳࡩࡷࡩࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᣈ"),
  bstack1l1l_opy_ (u"ࠪࡴࡪࡸࡣࡺࡅࡤࡴࡹࡻࡲࡦࡏࡲࡨࡪ࠭ᣉ"),
  bstack1l1l_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡻࡴࡰࡅࡤࡴࡹࡻࡲࡦࡎࡲ࡫ࡸ࠭ᣊ"),
  bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩᣋ"),
  bstack1l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᣌ"),
  bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫᣍ"),
  bstack1l1l_opy_ (u"ࠨࡪࡸࡦࡗ࡫ࡧࡪࡱࡱࠫᣎ")
]
bstack11l1l11l1ll_opy_ = [
  bstack1l1l_opy_ (u"ࠩࡸࡴࡱࡵࡡࡥࡏࡨࡨ࡮ࡧࠧᣏ"),
  bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬᣐ"),
  bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧᣑ"),
  bstack1l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᣒ"),
  bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡔࡷ࡯࡯ࡳ࡫ࡷࡽࠬᣓ"),
  bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪᣔ"),
  bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡔࡢࡩࠪᣕ"),
  bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᣖ"),
  bstack1l1l_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᣗ"),
  bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᣘ"),
  bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᣙ"),
  bstack1l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࠬᣚ"),
  bstack1l1l_opy_ (u"ࠧࡰࡵࠪᣛ"),
  bstack1l1l_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫᣜ"),
  bstack1l1l_opy_ (u"ࠩ࡫ࡳࡸࡺࡳࠨᣝ"),
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯ࡘࡣ࡬ࡸࠬᣞ"),
  bstack1l1l_opy_ (u"ࠫࡷ࡫ࡧࡪࡱࡱࠫᣟ"),
  bstack1l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡽࡳࡳ࡫ࠧᣠ"),
  bstack1l1l_opy_ (u"࠭࡭ࡢࡥ࡫࡭ࡳ࡫ࠧᣡ"),
  bstack1l1l_opy_ (u"ࠧࡳࡧࡶࡳࡱࡻࡴࡪࡱࡱࠫᣢ"),
  bstack1l1l_opy_ (u"ࠨ࡫ࡧࡰࡪ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᣣ"),
  bstack1l1l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡑࡵ࡭ࡪࡴࡴࡢࡶ࡬ࡳࡳ࠭ᣤ"),
  bstack1l1l_opy_ (u"ࠪࡺ࡮ࡪࡥࡰࠩᣥ"),
  bstack1l1l_opy_ (u"ࠫࡳࡵࡐࡢࡩࡨࡐࡴࡧࡤࡕ࡫ࡰࡩࡴࡻࡴࠨᣦ"),
  bstack1l1l_opy_ (u"ࠬࡨࡦࡤࡣࡦ࡬ࡪ࠭ᣧ"),
  bstack1l1l_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬᣨ"),
  bstack1l1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡓࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫᣩ"),
  bstack1l1l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡔࡧࡱࡨࡐ࡫ࡹࡴࠩᣪ"),
  bstack1l1l_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭ᣫ"),
  bstack1l1l_opy_ (u"ࠪࡲࡴࡖࡩࡱࡧ࡯࡭ࡳ࡫ࠧᣬ"),
  bstack1l1l_opy_ (u"ࠫࡨ࡮ࡥࡤ࡭ࡘࡖࡑ࠭ᣭ"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧᣮ"),
  bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹࡉ࡯ࡰ࡭࡬ࡩࡸ࠭ᣯ"),
  bstack1l1l_opy_ (u"ࠧࡤࡣࡳࡸࡺࡸࡥࡄࡴࡤࡷ࡭࠭ᣰ"),
  bstack1l1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬᣱ"),
  bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࡯ࡵ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩᣲ"),
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࡖࡦࡴࡶ࡭ࡴࡴࠧᣳ"),
  bstack1l1l_opy_ (u"ࠫࡳࡵࡂ࡭ࡣࡱ࡯ࡕࡵ࡬࡭࡫ࡱ࡫ࠬᣴ"),
  bstack1l1l_opy_ (u"ࠬࡳࡡࡴ࡭ࡖࡩࡳࡪࡋࡦࡻࡶࠫᣵ"),
  bstack1l1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡒ࡯ࡨࡵࠪ᣶"),
  bstack1l1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡉࡥࠩ᣷"),
  bstack1l1l_opy_ (u"ࠨࡦࡨࡨ࡮ࡩࡡࡵࡧࡧࡈࡪࡼࡩࡤࡧࠪ᣸"),
  bstack1l1l_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡒࡤࡶࡦࡳࡳࠨ᣹"),
  bstack1l1l_opy_ (u"ࠪࡴ࡭ࡵ࡮ࡦࡐࡸࡱࡧ࡫ࡲࠨ᣺"),
  bstack1l1l_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡑࡵࡧࡴࠩ᣻"),
  bstack1l1l_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰࡒ࡯ࡨࡵࡒࡴࡹ࡯࡯࡯ࡵࠪ᣼"),
  bstack1l1l_opy_ (u"࠭ࡣࡰࡰࡶࡳࡱ࡫ࡌࡰࡩࡶࠫ᣽"),
  bstack1l1l_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ᣾"),
  bstack1l1l_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡍࡱࡪࡷࠬ᣿"),
  bstack1l1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡄ࡬ࡳࡲ࡫ࡴࡳ࡫ࡦࠫᤀ"),
  bstack1l1l_opy_ (u"ࠪࡺ࡮ࡪࡥࡰࡘ࠵ࠫᤁ"),
  bstack1l1l_opy_ (u"ࠫࡲ࡯ࡤࡔࡧࡶࡷ࡮ࡵ࡮ࡊࡰࡶࡸࡦࡲ࡬ࡂࡲࡳࡷࠬᤂ"),
  bstack1l1l_opy_ (u"ࠬ࡫ࡳࡱࡴࡨࡷࡸࡵࡓࡦࡴࡹࡩࡷ࠭ᤃ"),
  bstack1l1l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡍࡱࡪࡷࠬᤄ"),
  bstack1l1l_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡅࡧࡴࠬᤅ"),
  bstack1l1l_opy_ (u"ࠨࡶࡨࡰࡪࡳࡥࡵࡴࡼࡐࡴ࡭ࡳࠨᤆ"),
  bstack1l1l_opy_ (u"ࠩࡶࡽࡳࡩࡔࡪ࡯ࡨ࡛࡮ࡺࡨࡏࡖࡓࠫᤇ"),
  bstack1l1l_opy_ (u"ࠪ࡫ࡪࡵࡌࡰࡥࡤࡸ࡮ࡵ࡮ࠨᤈ"),
  bstack1l1l_opy_ (u"ࠫ࡬ࡶࡳࡍࡱࡦࡥࡹ࡯࡯࡯ࠩᤉ"),
  bstack1l1l_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰࡖࡲࡰࡨ࡬ࡰࡪ࠭ᤊ"),
  bstack1l1l_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭ᤋ"),
  bstack1l1l_opy_ (u"ࠧࡧࡱࡵࡧࡪࡉࡨࡢࡰࡪࡩࡏࡧࡲࠨᤌ"),
  bstack1l1l_opy_ (u"ࠨࡺࡰࡷࡏࡧࡲࠨᤍ"),
  bstack1l1l_opy_ (u"ࠩࡻࡱࡽࡐࡡࡳࠩᤎ"),
  bstack1l1l_opy_ (u"ࠪࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩᤏ"),
  bstack1l1l_opy_ (u"ࠫࡲࡧࡳ࡬ࡄࡤࡷ࡮ࡩࡁࡶࡶ࡫ࠫᤐ"),
  bstack1l1l_opy_ (u"ࠬࡽࡳࡍࡱࡦࡥࡱ࡙ࡵࡱࡲࡲࡶࡹ࠭ᤑ"),
  bstack1l1l_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡃࡰࡴࡶࡖࡪࡹࡴࡳ࡫ࡦࡸ࡮ࡵ࡮ࡴࠩᤒ"),
  bstack1l1l_opy_ (u"ࠧࡢࡲࡳ࡚ࡪࡸࡳࡪࡱࡱࠫᤓ"),
  bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡶࡴࡊࡰࡶࡩࡨࡻࡲࡦࡅࡨࡶࡹࡹࠧᤔ"),
  bstack1l1l_opy_ (u"ࠩࡵࡩࡸ࡯ࡧ࡯ࡃࡳࡴࠬᤕ"),
  bstack1l1l_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡳ࡯࡭ࡢࡶ࡬ࡳࡳࡹࠧᤖ"),
  bstack1l1l_opy_ (u"ࠫࡨࡧ࡮ࡢࡴࡼࠫᤗ"),
  bstack1l1l_opy_ (u"ࠬ࡬ࡩࡳࡧࡩࡳࡽ࠭ᤘ"),
  bstack1l1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ᤙ"),
  bstack1l1l_opy_ (u"ࠧࡪࡧࠪᤚ"),
  bstack1l1l_opy_ (u"ࠨࡧࡧ࡫ࡪ࠭ᤛ"),
  bstack1l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩᤜ"),
  bstack1l1l_opy_ (u"ࠪࡵࡺ࡫ࡵࡦࠩᤝ"),
  bstack1l1l_opy_ (u"ࠫ࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ᤞ"),
  bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡕࡷࡳࡷ࡫ࡃࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳ࠭᤟"),
  bstack1l1l_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡉࡡ࡮ࡧࡵࡥࡎࡳࡡࡨࡧࡌࡲ࡯࡫ࡣࡵ࡫ࡲࡲࠬᤠ"),
  bstack1l1l_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡍࡱࡪࡷࡊࡾࡣ࡭ࡷࡧࡩࡍࡵࡳࡵࡵࠪᤡ"),
  bstack1l1l_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸࡏ࡮ࡤ࡮ࡸࡨࡪࡎ࡯ࡴࡶࡶࠫᤢ"),
  bstack1l1l_opy_ (u"ࠩࡸࡴࡩࡧࡴࡦࡃࡳࡴࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭ᤣ"),
  bstack1l1l_opy_ (u"ࠪࡶࡪࡹࡥࡳࡸࡨࡈࡪࡼࡩࡤࡧࠪᤤ"),
  bstack1l1l_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫᤥ"),
  bstack1l1l_opy_ (u"ࠬࡹࡥ࡯ࡦࡎࡩࡾࡹࠧᤦ"),
  bstack1l1l_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡖࡡࡴࡵࡦࡳࡩ࡫ࠧᤧ"),
  bstack1l1l_opy_ (u"ࠧࡶࡲࡧࡥࡹ࡫ࡉࡰࡵࡇࡩࡻ࡯ࡣࡦࡕࡨࡸࡹ࡯࡮ࡨࡵࠪᤨ"),
  bstack1l1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡂࡷࡧ࡭ࡴࡏ࡮࡫ࡧࡦࡸ࡮ࡵ࡮ࠨᤩ"),
  bstack1l1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡃࡳࡴࡱ࡫ࡐࡢࡻࠪᤪ"),
  bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫᤫ"),
  bstack1l1l_opy_ (u"ࠫࡼࡪࡩࡰࡕࡨࡶࡻ࡯ࡣࡦࠩ᤬"),
  bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ᤭"),
  bstack1l1l_opy_ (u"࠭ࡰࡳࡧࡹࡩࡳࡺࡃࡳࡱࡶࡷࡘ࡯ࡴࡦࡖࡵࡥࡨࡱࡩ࡯ࡩࠪ᤮"),
  bstack1l1l_opy_ (u"ࠧࡩ࡫ࡪ࡬ࡈࡵ࡮ࡵࡴࡤࡷࡹ࠭᤯"),
  bstack1l1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡑࡴࡨࡪࡪࡸࡥ࡯ࡥࡨࡷࠬᤰ"),
  bstack1l1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡕ࡬ࡱࠬᤱ"),
  bstack1l1l_opy_ (u"ࠪࡷ࡮ࡳࡏࡱࡶ࡬ࡳࡳࡹࠧᤲ"),
  bstack1l1l_opy_ (u"ࠫࡷ࡫࡭ࡰࡸࡨࡍࡔ࡙ࡁࡱࡲࡖࡩࡹࡺࡩ࡯ࡩࡶࡐࡴࡩࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠩᤳ"),
  bstack1l1l_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧᤴ"),
  bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᤵ"),
  bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᤶ"),
  bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧᤷ"),
  bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫᤸ"),
  bstack1l1l_opy_ (u"ࠪࡴࡦ࡭ࡥࡍࡱࡤࡨࡘࡺࡲࡢࡶࡨ࡫ࡾ᤹࠭"),
  bstack1l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪ᤺"),
  bstack1l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡲࡹࡹࡹ᤻ࠧ"),
  bstack1l1l_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩ᤼")
]
bstack11lll1111_opy_ = {
  bstack1l1l_opy_ (u"ࠧࡷࠩ᤽"): bstack1l1l_opy_ (u"ࠨࡸࠪ᤾"),
  bstack1l1l_opy_ (u"ࠩࡩࠫ᤿"): bstack1l1l_opy_ (u"ࠪࡪࠬ᥀"),
  bstack1l1l_opy_ (u"ࠫ࡫ࡵࡲࡤࡧࠪ᥁"): bstack1l1l_opy_ (u"ࠬ࡬࡯ࡳࡥࡨࠫ᥂"),
  bstack1l1l_opy_ (u"࠭࡯࡯࡮ࡼࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ᥃"): bstack1l1l_opy_ (u"ࠧࡰࡰ࡯ࡽࡆࡻࡴࡰ࡯ࡤࡸࡪ࠭᥄"),
  bstack1l1l_opy_ (u"ࠨࡨࡲࡶࡨ࡫࡬ࡰࡥࡤࡰࠬ᥅"): bstack1l1l_opy_ (u"ࠩࡩࡳࡷࡩࡥ࡭ࡱࡦࡥࡱ࠭᥆"),
  bstack1l1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࡪࡲࡷࡹ࠭᥇"): bstack1l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡋࡳࡸࡺࠧ᥈"),
  bstack1l1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࡴࡴࡸࡴࠨ᥉"): bstack1l1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡕࡵࡲࡵࠩ᥊"),
  bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡻࡳࡦࡴࠪ᥋"): bstack1l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵࠫ᥌"),
  bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡱࡣࡶࡷࠬ᥍"): bstack1l1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭᥎"),
  bstack1l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡳࡶࡴࡾࡹࡩࡱࡶࡸࠬ᥏"): bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡊࡲࡷࡹ࠭ᥐ"),
  bstack1l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡳࡳࡷࡺࠧᥑ"): bstack1l1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡖࡲࡰࡺࡼࡔࡴࡸࡴࠨᥒ"),
  bstack1l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡰࡳࡱࡻࡽࡺࡹࡥࡳࠩᥓ"): bstack1l1l_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡕࡴࡧࡵࠫᥔ"),
  bstack1l1l_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡳࡶࡴࡾࡹࡶࡵࡨࡶࠬᥕ"): bstack1l1l_opy_ (u"ࠫ࠲ࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᥖ"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡲࡤࡷࡸ࠭ᥗ"): bstack1l1l_opy_ (u"࠭࠭࡭ࡱࡦࡥࡱࡖࡲࡰࡺࡼࡔࡦࡹࡳࠨᥘ"),
  bstack1l1l_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡰࡳࡱࡻࡽࡵࡧࡳࡴࠩᥙ"): bstack1l1l_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡑࡴࡲࡼࡾࡖࡡࡴࡵࠪᥚ"),
  bstack1l1l_opy_ (u"ࠩࡥ࡭ࡳࡧࡲࡺࡲࡤࡸ࡭࠭ᥛ"): bstack1l1l_opy_ (u"ࠪࡦ࡮ࡴࡡࡳࡻࡳࡥࡹ࡮ࠧᥜ"),
  bstack1l1l_opy_ (u"ࠫࡵࡧࡣࡧ࡫࡯ࡩࠬᥝ"): bstack1l1l_opy_ (u"ࠬ࠳ࡰࡢࡥ࠰ࡪ࡮ࡲࡥࠨᥞ"),
  bstack1l1l_opy_ (u"࠭ࡰࡢࡥ࠰ࡪ࡮ࡲࡥࠨᥟ"): bstack1l1l_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪᥠ"),
  bstack1l1l_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫᥡ"): bstack1l1l_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬᥢ"),
  bstack1l1l_opy_ (u"ࠪࡰࡴ࡭ࡦࡪ࡮ࡨࠫᥣ"): bstack1l1l_opy_ (u"ࠫࡱࡵࡧࡧ࡫࡯ࡩࠬᥤ"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧᥥ"): bstack1l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᥦ"),
  bstack1l1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࠭ࡳࡧࡳࡩࡦࡺࡥࡳࠩᥧ"): bstack1l1l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡓࡧࡳࡩࡦࡺࡥࡳࠩᥨ")
}
bstack11l1l1lll1l_opy_ = bstack1l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲࡫࡮ࡺࡨࡶࡤ࠱ࡧࡴࡳ࠯ࡱࡧࡵࡧࡾ࠵ࡣ࡭࡫࠲ࡶࡪࡲࡥࡢࡵࡨࡷ࠴ࡲࡡࡵࡧࡶࡸ࠴ࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠢᥩ")
bstack11l1l11ll11_opy_ = bstack1l1l_opy_ (u"ࠥ࠳ࡵ࡫ࡲࡤࡻ࠲࡬ࡪࡧ࡬ࡵࡪࡦ࡬ࡪࡩ࡫ࠣᥪ")
bstack1ll1lll1_opy_ = bstack1l1l_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴࡫ࡤࡴ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡹࡥ࡯ࡦࡢࡷࡩࡱ࡟ࡦࡸࡨࡲࡹࡹࠢᥫ")
bstack1llll11111_opy_ = bstack1l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡨࡶࡤ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ᥬ")
bstack1l1ll1ll_opy_ = bstack1l1l_opy_ (u"࠭ࡨࡵࡶࡳ࠾࠴࠵ࡨࡶࡤ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࡀ࠸࠱࠱ࡺࡨ࠴࡮ࡵࡣࠩᥭ")
bstack1l1l1llll_opy_ = bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡪࡸࡦ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡰࡨࡼࡹࡥࡨࡶࡤࡶࠫ᥮")
bstack1l1ll1l1l_opy_ = {
  bstack1l1l_opy_ (u"ࠨࡦࡨࡪࡦࡻ࡬ࡵࠩ᥯"): bstack1l1l_opy_ (u"ࠩ࡫ࡹࡧ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩᥰ"),
  bstack1l1l_opy_ (u"ࠪࡹࡸ࠳ࡥࡢࡵࡷࠫᥱ"): bstack1l1l_opy_ (u"ࠫ࡭ࡻࡢ࠮ࡷࡶࡩ࠲ࡵ࡮࡭ࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠭ᥲ"),
  bstack1l1l_opy_ (u"ࠬࡻࡳࠨᥳ"): bstack1l1l_opy_ (u"࠭ࡨࡶࡤ࠰ࡹࡸ࠳࡯࡯࡮ࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠧᥴ"),
  bstack1l1l_opy_ (u"ࠧࡦࡷࠪ᥵"): bstack1l1l_opy_ (u"ࠨࡪࡸࡦ࠲࡫ࡵ࠮ࡱࡱࡰࡾ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ᥶"),
  bstack1l1l_opy_ (u"ࠩ࡬ࡲࠬ᥷"): bstack1l1l_opy_ (u"ࠪ࡬ࡺࡨ࠭ࡢࡲࡶ࠱ࡴࡴ࡬ࡺ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬ᥸"),
  bstack1l1l_opy_ (u"ࠫࡦࡻࠧ᥹"): bstack1l1l_opy_ (u"ࠬ࡮ࡵࡣ࠯ࡤࡴࡸ࡫࠭ࡰࡰ࡯ࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨ᥺")
}
bstack11l1l1ll111_opy_ = {
  bstack1l1l_opy_ (u"࠭ࡣࡳ࡫ࡷ࡭ࡨࡧ࡬ࠨ᥻"): 50,
  bstack1l1l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭᥼"): 40,
  bstack1l1l_opy_ (u"ࠨࡹࡤࡶࡳ࡯࡮ࡨࠩ᥽"): 30,
  bstack1l1l_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧ᥾"): 20,
  bstack1l1l_opy_ (u"ࠪࡨࡪࡨࡵࡨࠩ᥿"): 10
}
bstack1lllll111l_opy_ = bstack11l1l1ll111_opy_[bstack1l1l_opy_ (u"ࠫ࡮ࡴࡦࡰࠩᦀ")]
bstack11ll1ll1_opy_ = bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠲ࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࠫᦁ")
bstack1l11l11l1l_opy_ = bstack1l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲ࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࠫᦂ")
bstack11l1l1lll_opy_ = bstack1l1l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴࠭ᦃ")
bstack1l11l1ll_opy_ = bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧᦄ")
bstack1l1lll1ll_opy_ = bstack1l1l_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡴࡾࡺࡥࡴࡶࠣࡥࡳࡪࠠࡱࡻࡷࡩࡸࡺ࠭ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡳࡥࡨࡱࡡࡨࡧࡶ࠲ࠥࡦࡰࡪࡲࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡵࡿࡴࡦࡵࡷࠤࡵࡿࡴࡦࡵࡷ࠱ࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡦࠧᦅ")
bstack11l1111l11_opy_ = {
  bstack1l1l_opy_ (u"ࠪࡗࡉࡑ࠭ࡈࡇࡑ࠱࠵࠶࠵ࠨᦆ"): bstack1l1l_opy_ (u"ࠫ࠯࠰ࠪࠡ࡝ࡖࡈࡐ࠳ࡇࡆࡐ࠰࠴࠵࠻࡝ࠡࡢࡳࡽࡹ࡫ࡳࡵ࠯ࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡤࠥ࡯ࡳࠡ࡫ࡱࡷࡹࡧ࡬࡭ࡧࡧࠤ࡮ࡴࠠࡺࡱࡸࡶࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶ࠱ࠤ࡙࡮ࡩࡴࠢࡰࡥࡾࠦࡣࡢࡷࡶࡩࠥࡩ࡯࡯ࡨ࡯࡭ࡨࡺࡳࠡࡹ࡬ࡸ࡭ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯࡙ࠥࡄࡌ࠰ࠣࡔࡱ࡫ࡡࡴࡧࠣࡹࡳ࡯࡮ࡴࡶࡤࡰࡱࠦࡩࡵࠢࡸࡷ࡮ࡴࡧ࠻ࠢࡳ࡭ࡵࠦࡵ࡯࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡳࡥࡷࡧ࡬࡭ࡧ࡯ࠤ࠯࠰ࠪࠨᦇ")
}
bstack11l11lllll1_opy_ = [bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭ᦈ"), bstack1l1l_opy_ (u"࡙࠭ࡐࡗࡕࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭ᦉ")]
bstack11l1l11ll1l_opy_ = [bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪᦊ"), bstack1l1l_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪᦋ")]
bstack11ll1l111l_opy_ = re.compile(bstack1l1l_opy_ (u"ࠩࡡ࡟ࡡࡢࡷ࠮࡟࠮࠾࠳࠰ࠤࠨᦌ"))
bstack1l111l1l_opy_ = [
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࡎࡢ࡯ࡨࠫᦍ"),
  bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᦎ"),
  bstack1l1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩᦏ"),
  bstack1l1l_opy_ (u"࠭࡮ࡦࡹࡆࡳࡲࡳࡡ࡯ࡦࡗ࡭ࡲ࡫࡯ࡶࡶࠪᦐ"),
  bstack1l1l_opy_ (u"ࠧࡢࡲࡳࠫᦑ"),
  bstack1l1l_opy_ (u"ࠨࡷࡧ࡭ࡩ࠭ᦒ"),
  bstack1l1l_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫᦓ"),
  bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡧࠪᦔ"),
  bstack1l1l_opy_ (u"ࠫࡴࡸࡩࡦࡰࡷࡥࡹ࡯࡯࡯ࠩᦕ"),
  bstack1l1l_opy_ (u"ࠬࡧࡵࡵࡱ࡚ࡩࡧࡼࡩࡦࡹࠪᦖ"),
  bstack1l1l_opy_ (u"࠭࡮ࡰࡔࡨࡷࡪࡺࠧᦗ"), bstack1l1l_opy_ (u"ࠧࡧࡷ࡯ࡰࡗ࡫ࡳࡦࡶࠪᦘ"),
  bstack1l1l_opy_ (u"ࠨࡥ࡯ࡩࡦࡸࡓࡺࡵࡷࡩࡲࡌࡩ࡭ࡧࡶࠫᦙ"),
  bstack1l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡕ࡫ࡰ࡭ࡳ࡭ࡳࠨᦚ"),
  bstack1l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡓࡩࡷ࡬࡯ࡳ࡯ࡤࡲࡨ࡫ࡌࡰࡩࡪ࡭ࡳ࡭ࠧᦛ"),
  bstack1l1l_opy_ (u"ࠫࡴࡺࡨࡦࡴࡄࡴࡵࡹࠧᦜ"),
  bstack1l1l_opy_ (u"ࠬࡶࡲࡪࡰࡷࡔࡦ࡭ࡥࡔࡱࡸࡶࡨ࡫ࡏ࡯ࡈ࡬ࡲࡩࡌࡡࡪ࡮ࡸࡶࡪ࠭ᦝ"),
  bstack1l1l_opy_ (u"࠭ࡡࡱࡲࡄࡧࡹ࡯ࡶࡪࡶࡼࠫᦞ"), bstack1l1l_opy_ (u"ࠧࡢࡲࡳࡔࡦࡩ࡫ࡢࡩࡨࠫᦟ"), bstack1l1l_opy_ (u"ࠨࡣࡳࡴ࡜ࡧࡩࡵࡃࡦࡸ࡮ࡼࡩࡵࡻࠪᦠ"), bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࡝ࡡࡪࡶࡓࡥࡨࡱࡡࡨࡧࠪᦡ"), bstack1l1l_opy_ (u"ࠪࡥࡵࡶࡗࡢ࡫ࡷࡈࡺࡸࡡࡵ࡫ࡲࡲࠬᦢ"),
  bstack1l1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡖࡪࡧࡤࡺࡖ࡬ࡱࡪࡵࡵࡵࠩᦣ"),
  bstack1l1l_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡘࡪࡹࡴࡑࡣࡦ࡯ࡦ࡭ࡥࡴࠩᦤ"),
  bstack1l1l_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡃࡰࡸࡨࡶࡦ࡭ࡥࠨᦥ"), bstack1l1l_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡄࡱࡹࡩࡷࡧࡧࡦࡇࡱࡨࡎࡴࡴࡦࡰࡷࠫᦦ"),
  bstack1l1l_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡆࡨࡺ࡮ࡩࡥࡓࡧࡤࡨࡾ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᦧ"),
  bstack1l1l_opy_ (u"ࠩࡤࡨࡧࡖ࡯ࡳࡶࠪᦨ"),
  bstack1l1l_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡈࡪࡼࡩࡤࡧࡖࡳࡨࡱࡥࡵࠩᦩ"),
  bstack1l1l_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡎࡴࡳࡵࡣ࡯ࡰ࡙࡯࡭ࡦࡱࡸࡸࠬᦪ"),
  bstack1l1l_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡏ࡮ࡴࡶࡤࡰࡱࡖࡡࡵࡪࠪᦫ"),
  bstack1l1l_opy_ (u"࠭ࡡࡷࡦࠪ᦬"), bstack1l1l_opy_ (u"ࠧࡢࡸࡧࡐࡦࡻ࡮ࡤࡪࡗ࡭ࡲ࡫࡯ࡶࡶࠪ᦭"), bstack1l1l_opy_ (u"ࠨࡣࡹࡨࡗ࡫ࡡࡥࡻࡗ࡭ࡲ࡫࡯ࡶࡶࠪ᦮"), bstack1l1l_opy_ (u"ࠩࡤࡺࡩࡇࡲࡨࡵࠪ᦯"),
  bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡋࡦࡻࡶࡸࡴࡸࡥࠨᦰ"), bstack1l1l_opy_ (u"ࠫࡰ࡫ࡹࡴࡶࡲࡶࡪࡖࡡࡵࡪࠪᦱ"), bstack1l1l_opy_ (u"ࠬࡱࡥࡺࡵࡷࡳࡷ࡫ࡐࡢࡵࡶࡻࡴࡸࡤࠨᦲ"),
  bstack1l1l_opy_ (u"࠭࡫ࡦࡻࡄࡰ࡮ࡧࡳࠨᦳ"), bstack1l1l_opy_ (u"ࠧ࡬ࡧࡼࡔࡦࡹࡳࡸࡱࡵࡨࠬᦴ"),
  bstack1l1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡅࡹࡧࡦࡹࡹࡧࡢ࡭ࡧࠪᦵ"), bstack1l1l_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡂࡴࡪࡷࠬᦶ"), bstack1l1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡇࡻࡩࡨࡻࡴࡢࡤ࡯ࡩࡉ࡯ࡲࠨᦷ"), bstack1l1l_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡆ࡬ࡷࡵ࡭ࡦࡏࡤࡴࡵ࡯࡮ࡨࡈ࡬ࡰࡪ࠭ᦸ"), bstack1l1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵ࡙ࡸ࡫ࡓࡺࡵࡷࡩࡲࡋࡸࡦࡥࡸࡸࡦࡨ࡬ࡦࠩᦹ"),
  bstack1l1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡕࡵࡲࡵࠩᦺ"), bstack1l1l_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡖ࡯ࡳࡶࡶࠫᦻ"),
  bstack1l1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡄࡪࡵࡤࡦࡱ࡫ࡂࡶ࡫࡯ࡨࡈ࡮ࡥࡤ࡭ࠪᦼ"),
  bstack1l1l_opy_ (u"ࠩࡤࡹࡹࡵࡗࡦࡤࡹ࡭ࡪࡽࡔࡪ࡯ࡨࡳࡺࡺࠧᦽ"),
  bstack1l1l_opy_ (u"ࠪ࡭ࡳࡺࡥ࡯ࡶࡄࡧࡹ࡯࡯࡯ࠩᦾ"), bstack1l1l_opy_ (u"ࠫ࡮ࡴࡴࡦࡰࡷࡇࡦࡺࡥࡨࡱࡵࡽࠬᦿ"), bstack1l1l_opy_ (u"ࠬ࡯࡮ࡵࡧࡱࡸࡋࡲࡡࡨࡵࠪᧀ"), bstack1l1l_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡧ࡬ࡊࡰࡷࡩࡳࡺࡁࡳࡩࡸࡱࡪࡴࡴࡴࠩᧁ"),
  bstack1l1l_opy_ (u"ࠧࡥࡱࡱࡸࡘࡺ࡯ࡱࡃࡳࡴࡔࡴࡒࡦࡵࡨࡸࠬᧂ"),
  bstack1l1l_opy_ (u"ࠨࡷࡱ࡭ࡨࡵࡤࡦࡍࡨࡽࡧࡵࡡࡳࡦࠪᧃ"), bstack1l1l_opy_ (u"ࠩࡵࡩࡸ࡫ࡴࡌࡧࡼࡦࡴࡧࡲࡥࠩᧄ"),
  bstack1l1l_opy_ (u"ࠪࡲࡴ࡙ࡩࡨࡰࠪᧅ"),
  bstack1l1l_opy_ (u"ࠫ࡮࡭࡮ࡰࡴࡨ࡙ࡳ࡯࡭ࡱࡱࡵࡸࡦࡴࡴࡗ࡫ࡨࡻࡸ࠭ᧆ"),
  bstack1l1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇ࡮ࡥࡴࡲ࡭ࡩ࡝ࡡࡵࡥ࡫ࡩࡷࡹࠧᧇ"),
  bstack1l1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᧈ"),
  bstack1l1l_opy_ (u"ࠧࡳࡧࡦࡶࡪࡧࡴࡦࡅ࡫ࡶࡴࡳࡥࡅࡴ࡬ࡺࡪࡸࡓࡦࡵࡶ࡭ࡴࡴࡳࠨᧉ"),
  bstack1l1l_opy_ (u"ࠨࡰࡤࡸ࡮ࡼࡥࡘࡧࡥࡗࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠧ᧊"),
  bstack1l1l_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡖࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡖࡡࡵࡪࠪ᧋"),
  bstack1l1l_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡗࡵ࡫ࡥࡥࠩ᧌"),
  bstack1l1l_opy_ (u"ࠫ࡬ࡶࡳࡆࡰࡤࡦࡱ࡫ࡤࠨ᧍"),
  bstack1l1l_opy_ (u"ࠬ࡯ࡳࡉࡧࡤࡨࡱ࡫ࡳࡴࠩ᧎"),
  bstack1l1l_opy_ (u"࠭ࡡࡥࡤࡈࡼࡪࡩࡔࡪ࡯ࡨࡳࡺࡺࠧ᧏"),
  bstack1l1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࡫ࡓࡤࡴ࡬ࡴࡹ࠭᧐"),
  bstack1l1l_opy_ (u"ࠨࡵ࡮࡭ࡵࡊࡥࡷ࡫ࡦࡩࡎࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡡࡵ࡫ࡲࡲࠬ᧑"),
  bstack1l1l_opy_ (u"ࠩࡤࡹࡹࡵࡇࡳࡣࡱࡸࡕ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮ࡴࠩ᧒"),
  bstack1l1l_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡒࡦࡺࡵࡳࡣ࡯ࡓࡷ࡯ࡥ࡯ࡶࡤࡸ࡮ࡵ࡮ࠨ᧓"),
  bstack1l1l_opy_ (u"ࠫࡸࡿࡳࡵࡧࡰࡔࡴࡸࡴࠨ᧔"),
  bstack1l1l_opy_ (u"ࠬࡸࡥ࡮ࡱࡷࡩࡆࡪࡢࡉࡱࡶࡸࠬ᧕"),
  bstack1l1l_opy_ (u"࠭ࡳ࡬࡫ࡳ࡙ࡳࡲ࡯ࡤ࡭ࠪ᧖"), bstack1l1l_opy_ (u"ࠧࡶࡰ࡯ࡳࡨࡱࡔࡺࡲࡨࠫ᧗"), bstack1l1l_opy_ (u"ࠨࡷࡱࡰࡴࡩ࡫ࡌࡧࡼࠫ᧘"),
  bstack1l1l_opy_ (u"ࠩࡤࡹࡹࡵࡌࡢࡷࡱࡧ࡭࠭᧙"),
  bstack1l1l_opy_ (u"ࠪࡷࡰ࡯ࡰࡍࡱࡪࡧࡦࡺࡃࡢࡲࡷࡹࡷ࡫ࠧ᧚"),
  bstack1l1l_opy_ (u"ࠫࡺࡴࡩ࡯ࡵࡷࡥࡱࡲࡏࡵࡪࡨࡶࡕࡧࡣ࡬ࡣࡪࡩࡸ࠭᧛"),
  bstack1l1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪ࡝ࡩ࡯ࡦࡲࡻࡆࡴࡩ࡮ࡣࡷ࡭ࡴࡴࠧ᧜"),
  bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨ࡙ࡵ࡯࡭ࡵ࡙ࡩࡷࡹࡩࡰࡰࠪ᧝"),
  bstack1l1l_opy_ (u"ࠧࡦࡰࡩࡳࡷࡩࡥࡂࡲࡳࡍࡳࡹࡴࡢ࡮࡯ࠫ᧞"),
  bstack1l1l_opy_ (u"ࠨࡧࡱࡷࡺࡸࡥࡘࡧࡥࡺ࡮࡫ࡷࡴࡊࡤࡺࡪࡖࡡࡨࡧࡶࠫ᧟"), bstack1l1l_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࡇࡩࡻࡺ࡯ࡰ࡮ࡶࡔࡴࡸࡴࠨ᧠"), bstack1l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧ࡚ࡩࡧࡼࡩࡦࡹࡇࡩࡹࡧࡩ࡭ࡵࡆࡳࡱࡲࡥࡤࡶ࡬ࡳࡳ࠭᧡"),
  bstack1l1l_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡅࡵࡶࡳࡄࡣࡦ࡬ࡪࡒࡩ࡮࡫ࡷࠫ᧢"),
  bstack1l1l_opy_ (u"ࠬࡩࡡ࡭ࡧࡱࡨࡦࡸࡆࡰࡴࡰࡥࡹ࠭᧣"),
  bstack1l1l_opy_ (u"࠭ࡢࡶࡰࡧࡰࡪࡏࡤࠨ᧤"),
  bstack1l1l_opy_ (u"ࠧ࡭ࡣࡸࡲࡨ࡮ࡔࡪ࡯ࡨࡳࡺࡺࠧ᧥"),
  bstack1l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࡖࡩࡷࡼࡩࡤࡧࡶࡉࡳࡧࡢ࡭ࡧࡧࠫ᧦"), bstack1l1l_opy_ (u"ࠩ࡯ࡳࡨࡧࡴࡪࡱࡱࡗࡪࡸࡶࡪࡥࡨࡷࡆࡻࡴࡩࡱࡵ࡭ࡿ࡫ࡤࠨ᧧"),
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯ࡂࡥࡦࡩࡵࡺࡁ࡭ࡧࡵࡸࡸ࠭᧨"), bstack1l1l_opy_ (u"ࠫࡦࡻࡴࡰࡆ࡬ࡷࡲ࡯ࡳࡴࡃ࡯ࡩࡷࡺࡳࠨ᧩"),
  bstack1l1l_opy_ (u"ࠬࡴࡡࡵ࡫ࡹࡩࡎࡴࡳࡵࡴࡸࡱࡪࡴࡴࡴࡎ࡬ࡦࠬ᧪"),
  bstack1l1l_opy_ (u"࠭࡮ࡢࡶ࡬ࡺࡪ࡝ࡥࡣࡖࡤࡴࠬ᧫"),
  bstack1l1l_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࡉ࡯࡫ࡷ࡭ࡦࡲࡕࡳ࡮ࠪ᧬"), bstack1l1l_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡂ࡮࡯ࡳࡼࡖ࡯ࡱࡷࡳࡷࠬ᧭"), bstack1l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡋࡪࡲࡴࡸࡥࡇࡴࡤࡹࡩ࡝ࡡࡳࡰ࡬ࡲ࡬࠭᧮"), bstack1l1l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࡒࡴࡪࡴࡌࡪࡰ࡮ࡷࡎࡴࡂࡢࡥ࡮࡫ࡷࡵࡵ࡯ࡦࠪ᧯"),
  bstack1l1l_opy_ (u"ࠫࡰ࡫ࡥࡱࡍࡨࡽࡈ࡮ࡡࡪࡰࡶࠫ᧰"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯࡭ࡿࡧࡢ࡭ࡧࡖࡸࡷ࡯࡮ࡨࡵࡇ࡭ࡷ࠭᧱"),
  bstack1l1l_opy_ (u"࠭ࡰࡳࡱࡦࡩࡸࡹࡁࡳࡩࡸࡱࡪࡴࡴࡴࠩ᧲"),
  bstack1l1l_opy_ (u"ࠧࡪࡰࡷࡩࡷࡑࡥࡺࡆࡨࡰࡦࡿࠧ᧳"),
  bstack1l1l_opy_ (u"ࠨࡵ࡫ࡳࡼࡏࡏࡔࡎࡲ࡫ࠬ᧴"),
  bstack1l1l_opy_ (u"ࠩࡶࡩࡳࡪࡋࡦࡻࡖࡸࡷࡧࡴࡦࡩࡼࠫ᧵"),
  bstack1l1l_opy_ (u"ࠪࡻࡪࡨ࡫ࡪࡶࡕࡩࡸࡶ࡯࡯ࡵࡨࡘ࡮ࡳࡥࡰࡷࡷࠫ᧶"), bstack1l1l_opy_ (u"ࠫࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡘࡣ࡬ࡸ࡙࡯࡭ࡦࡱࡸࡸࠬ᧷"),
  bstack1l1l_opy_ (u"ࠬࡸࡥ࡮ࡱࡷࡩࡉ࡫ࡢࡶࡩࡓࡶࡴࡾࡹࠨ᧸"),
  bstack1l1l_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡇࡳࡺࡰࡦࡉࡽ࡫ࡣࡶࡶࡨࡊࡷࡵ࡭ࡉࡶࡷࡴࡸ࠭᧹"),
  bstack1l1l_opy_ (u"ࠧࡴ࡭࡬ࡴࡑࡵࡧࡄࡣࡳࡸࡺࡸࡥࠨ᧺"),
  bstack1l1l_opy_ (u"ࠨࡹࡨࡦࡰ࡯ࡴࡅࡧࡥࡹ࡬ࡖࡲࡰࡺࡼࡔࡴࡸࡴࠨ᧻"),
  bstack1l1l_opy_ (u"ࠩࡩࡹࡱࡲࡃࡰࡰࡷࡩࡽࡺࡌࡪࡵࡷࠫ᧼"),
  bstack1l1l_opy_ (u"ࠪࡻࡦ࡯ࡴࡇࡱࡵࡅࡵࡶࡓࡤࡴ࡬ࡴࡹ࠭᧽"),
  bstack1l1l_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࡈࡵ࡮࡯ࡧࡦࡸࡗ࡫ࡴࡳ࡫ࡨࡷࠬ᧾"),
  bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡐࡤࡱࡪ࠭᧿"),
  bstack1l1l_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡙ࡓࡍࡅࡨࡶࡹ࠭ᨀ"),
  bstack1l1l_opy_ (u"ࠧࡵࡣࡳ࡛࡮ࡺࡨࡔࡪࡲࡶࡹࡖࡲࡦࡵࡶࡈࡺࡸࡡࡵ࡫ࡲࡲࠬᨁ"),
  bstack1l1l_opy_ (u"ࠨࡵࡦࡥࡱ࡫ࡆࡢࡥࡷࡳࡷ࠭ᨂ"),
  bstack1l1l_opy_ (u"ࠩࡺࡨࡦࡒ࡯ࡤࡣ࡯ࡔࡴࡸࡴࠨᨃ"),
  bstack1l1l_opy_ (u"ࠪࡷ࡭ࡵࡷ࡙ࡥࡲࡨࡪࡒ࡯ࡨࠩᨄ"),
  bstack1l1l_opy_ (u"ࠫ࡮ࡵࡳࡊࡰࡶࡸࡦࡲ࡬ࡑࡣࡸࡷࡪ࠭ᨅ"),
  bstack1l1l_opy_ (u"ࠬࡾࡣࡰࡦࡨࡇࡴࡴࡦࡪࡩࡉ࡭ࡱ࡫ࠧᨆ"),
  bstack1l1l_opy_ (u"࠭࡫ࡦࡻࡦ࡬ࡦ࡯࡮ࡑࡣࡶࡷࡼࡵࡲࡥࠩᨇ"),
  bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡔࡷ࡫ࡢࡶ࡫࡯ࡸ࡜ࡊࡁࠨᨈ"),
  bstack1l1l_opy_ (u"ࠨࡲࡵࡩࡻ࡫࡮ࡵ࡙ࡇࡅࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠩᨉ"),
  bstack1l1l_opy_ (u"ࠩࡺࡩࡧࡊࡲࡪࡸࡨࡶࡆ࡭ࡥ࡯ࡶࡘࡶࡱ࠭ᨊ"),
  bstack1l1l_opy_ (u"ࠪ࡯ࡪࡿࡣࡩࡣ࡬ࡲࡕࡧࡴࡩࠩᨋ"),
  bstack1l1l_opy_ (u"ࠫࡺࡹࡥࡏࡧࡺ࡛ࡉࡇࠧᨌ"),
  bstack1l1l_opy_ (u"ࠬࡽࡤࡢࡎࡤࡹࡳࡩࡨࡕ࡫ࡰࡩࡴࡻࡴࠨᨍ"), bstack1l1l_opy_ (u"࠭ࡷࡥࡣࡆࡳࡳࡴࡥࡤࡶ࡬ࡳࡳ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᨎ"),
  bstack1l1l_opy_ (u"ࠧࡹࡥࡲࡨࡪࡕࡲࡨࡋࡧࠫᨏ"), bstack1l1l_opy_ (u"ࠨࡺࡦࡳࡩ࡫ࡓࡪࡩࡱ࡭ࡳ࡭ࡉࡥࠩᨐ"),
  bstack1l1l_opy_ (u"ࠩࡸࡴࡩࡧࡴࡦࡦ࡚ࡈࡆࡈࡵ࡯ࡦ࡯ࡩࡎࡪࠧᨑ"),
  bstack1l1l_opy_ (u"ࠪࡶࡪࡹࡥࡵࡑࡱࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡲࡵࡑࡱࡰࡾ࠭ᨒ"),
  bstack1l1l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨ࡙࡯࡭ࡦࡱࡸࡸࡸ࠭ᨓ"),
  bstack1l1l_opy_ (u"ࠬࡽࡤࡢࡕࡷࡥࡷࡺࡵࡱࡔࡨࡸࡷ࡯ࡥࡴࠩᨔ"), bstack1l1l_opy_ (u"࠭ࡷࡥࡣࡖࡸࡦࡸࡴࡶࡲࡕࡩࡹࡸࡹࡊࡰࡷࡩࡷࡼࡡ࡭ࠩᨕ"),
  bstack1l1l_opy_ (u"ࠧࡤࡱࡱࡲࡪࡩࡴࡉࡣࡵࡨࡼࡧࡲࡦࡍࡨࡽࡧࡵࡡࡳࡦࠪᨖ"),
  bstack1l1l_opy_ (u"ࠨ࡯ࡤࡼ࡙ࡿࡰࡪࡰࡪࡊࡷ࡫ࡱࡶࡧࡱࡧࡾ࠭ᨗ"),
  bstack1l1l_opy_ (u"ࠩࡶ࡭ࡲࡶ࡬ࡦࡋࡶ࡚࡮ࡹࡩࡣ࡮ࡨࡇ࡭࡫ࡣ࡬ᨘࠩ"),
  bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡃࡢࡴࡷ࡬ࡦ࡭ࡥࡔࡵ࡯ࠫᨙ"),
  bstack1l1l_opy_ (u"ࠫࡸ࡮࡯ࡶ࡮ࡧ࡙ࡸ࡫ࡓࡪࡰࡪࡰࡪࡺ࡯࡯ࡖࡨࡷࡹࡓࡡ࡯ࡣࡪࡩࡷ࠭ᨚ"),
  bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡍ࡜ࡊࡐࠨᨛ"),
  bstack1l1l_opy_ (u"࠭ࡡ࡭࡮ࡲࡻ࡙ࡵࡵࡤࡪࡌࡨࡊࡴࡲࡰ࡮࡯ࠫ᨜"),
  bstack1l1l_opy_ (u"ࠧࡪࡩࡱࡳࡷ࡫ࡈࡪࡦࡧࡩࡳࡇࡰࡪࡒࡲࡰ࡮ࡩࡹࡆࡴࡵࡳࡷ࠭᨝"),
  bstack1l1l_opy_ (u"ࠨ࡯ࡲࡧࡰࡒ࡯ࡤࡣࡷ࡭ࡴࡴࡁࡱࡲࠪ᨞"),
  bstack1l1l_opy_ (u"ࠩ࡯ࡳ࡬ࡩࡡࡵࡈࡲࡶࡲࡧࡴࠨ᨟"), bstack1l1l_opy_ (u"ࠪࡰࡴ࡭ࡣࡢࡶࡉ࡭ࡱࡺࡥࡳࡕࡳࡩࡨࡹࠧᨠ"),
  bstack1l1l_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡇࡩࡱࡧࡹࡂࡦࡥࠫᨡ"),
  bstack1l1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡏࡤࡍࡱࡦࡥࡹࡵࡲࡂࡷࡷࡳࡨࡵ࡭ࡱ࡮ࡨࡸ࡮ࡵ࡮ࠨᨢ")
]
bstack11lll111l_opy_ = bstack1l1l_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡲ࡬࠱ࡨࡲ࡯ࡶࡦ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠴ࡻࡰ࡭ࡱࡤࡨࠬᨣ")
bstack111l1lll_opy_ = [bstack1l1l_opy_ (u"ࠧ࠯ࡣࡳ࡯ࠬᨤ"), bstack1l1l_opy_ (u"ࠨ࠰ࡤࡥࡧ࠭ᨥ"), bstack1l1l_opy_ (u"ࠩ࠱࡭ࡵࡧࠧᨦ")]
bstack1ll11lll1l_opy_ = [bstack1l1l_opy_ (u"ࠪ࡭ࡩ࠭ᨧ"), bstack1l1l_opy_ (u"ࠫࡵࡧࡴࡩࠩᨨ"), bstack1l1l_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡤ࡯ࡤࠨᨩ"), bstack1l1l_opy_ (u"࠭ࡳࡩࡣࡵࡩࡦࡨ࡬ࡦࡡ࡬ࡨࠬᨪ")]
bstack1l1ll111ll_opy_ = {
  bstack1l1l_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᨫ"): bstack1l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᨬ"),
  bstack1l1l_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࡒࡴࡹ࡯࡯࡯ࡵࠪᨭ"): bstack1l1l_opy_ (u"ࠪࡱࡴࢀ࠺ࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨᨮ"),
  bstack1l1l_opy_ (u"ࠫࡪࡪࡧࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᨯ"): bstack1l1l_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᨰ"),
  bstack1l1l_opy_ (u"࠭ࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᨱ"): bstack1l1l_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᨲ"),
  bstack1l1l_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡐࡲࡷ࡭ࡴࡴࡳࠨᨳ"): bstack1l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪᨴ")
}
bstack1lll11llll_opy_ = [
  bstack1l1l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᨵ"),
  bstack1l1l_opy_ (u"ࠫࡲࡵࡺ࠻ࡨ࡬ࡶࡪ࡬࡯ࡹࡑࡳࡸ࡮ࡵ࡮ࡴࠩᨶ"),
  bstack1l1l_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᨷ"),
  bstack1l1l_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬᨸ"),
  bstack1l1l_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯࠮ࡰࡲࡷ࡭ࡴࡴࡳࠨᨹ"),
]
bstack1l1lllll1l_opy_ = bstack111111l1l_opy_ + bstack11l1l11l1ll_opy_ + bstack1l111l1l_opy_
bstack11l111ll_opy_ = [
  bstack1l1l_opy_ (u"ࠨࡠ࡯ࡳࡨࡧ࡬ࡩࡱࡶࡸࠩ࠭ᨺ"),
  bstack1l1l_opy_ (u"ࠩࡡࡦࡸ࠳࡬ࡰࡥࡤࡰ࠳ࡩ࡯࡮ࠦࠪᨻ"),
  bstack1l1l_opy_ (u"ࠪࡢ࠶࠸࠷࠯ࠩᨼ"),
  bstack1l1l_opy_ (u"ࠫࡣ࠷࠰࠯ࠩᨽ"),
  bstack1l1l_opy_ (u"ࠬࡤ࠱࠸࠴࠱࠵ࡠ࠼࠭࠺࡟࠱ࠫᨾ"),
  bstack1l1l_opy_ (u"࠭࡞࠲࠹࠵࠲࠷ࡡ࠰࠮࠻ࡠ࠲ࠬᨿ"),
  bstack1l1l_opy_ (u"ࠧ࡟࠳࠺࠶࠳࠹࡛࠱࠯࠴ࡡ࠳࠭ᩀ"),
  bstack1l1l_opy_ (u"ࠨࡠ࠴࠽࠷࠴࠱࠷࠺࠱ࠫᩁ")
]
bstack11l1lll11l1_opy_ = bstack1l1l_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡥࡵ࡯࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪᩂ")
bstack1l1l1l1l_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠯ࡷ࠳࠲ࡩࡻ࡫࡮ࡵࠩᩃ")
bstack1llll1l1l_opy_ = [ bstack1l1l_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᩄ") ]
bstack11lll11lll_opy_ = [ bstack1l1l_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨࠫᩅ") ]
bstack111lll11_opy_ = [bstack1l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪᩆ")]
bstack1llll1l1ll_opy_ = [ bstack1l1l_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧᩇ") ]
bstack11l1lll1_opy_ = bstack1l1l_opy_ (u"ࠨࡕࡇࡏࡘ࡫ࡴࡶࡲࠪᩈ")
bstack1l1lll11ll_opy_ = bstack1l1l_opy_ (u"ࠩࡖࡈࡐ࡚ࡥࡴࡶࡄࡸࡹ࡫࡭ࡱࡶࡨࡨࠬᩉ")
bstack1l1l1l11l_opy_ = bstack1l1l_opy_ (u"ࠪࡗࡉࡑࡔࡦࡵࡷࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠧᩊ")
bstack1llll11l_opy_ = bstack1l1l_opy_ (u"ࠫ࠹࠴࠰࠯࠲ࠪᩋ")
bstack1l1ll1lll1_opy_ = [
  bstack1l1l_opy_ (u"ࠬࡋࡒࡓࡡࡉࡅࡎࡒࡅࡅࠩᩌ"),
  bstack1l1l_opy_ (u"࠭ࡅࡓࡔࡢࡘࡎࡓࡅࡅࡡࡒ࡙࡙࠭ᩍ"),
  bstack1l1l_opy_ (u"ࠧࡆࡔࡕࡣࡇࡒࡏࡄࡍࡈࡈࡤࡈ࡙ࡠࡅࡏࡍࡊࡔࡔࠨᩎ"),
  bstack1l1l_opy_ (u"ࠨࡇࡕࡖࡤࡔࡅࡕ࡙ࡒࡖࡐࡥࡃࡉࡃࡑࡋࡊࡊࠧᩏ"),
  bstack1l1l_opy_ (u"ࠩࡈࡖࡗࡥࡓࡐࡅࡎࡉ࡙ࡥࡎࡐࡖࡢࡇࡔࡔࡎࡆࡅࡗࡉࡉ࠭ᩐ"),
  bstack1l1l_opy_ (u"ࠪࡉࡗࡘ࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡈࡒࡏࡔࡇࡇࠫᩑ"),
  bstack1l1l_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡘࡅࡔࡇࡗࠫᩒ"),
  bstack1l1l_opy_ (u"ࠬࡋࡒࡓࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡒࡆࡈࡘࡗࡊࡊࠧᩓ"),
  bstack1l1l_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡂࡄࡒࡖ࡙ࡋࡄࠨᩔ"),
  bstack1l1l_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡈࡄࡍࡑࡋࡄࠨᩕ"),
  bstack1l1l_opy_ (u"ࠨࡇࡕࡖࡤࡔࡁࡎࡇࡢࡒࡔ࡚࡟ࡓࡇࡖࡓࡑ࡜ࡅࡅࠩᩖ"),
  bstack1l1l_opy_ (u"ࠩࡈࡖࡗࡥࡁࡅࡆࡕࡉࡘ࡙࡟ࡊࡐ࡙ࡅࡑࡏࡄࠨᩗ"),
  bstack1l1l_opy_ (u"ࠪࡉࡗࡘ࡟ࡂࡆࡇࡖࡊ࡙ࡓࡠࡗࡑࡖࡊࡇࡃࡉࡃࡅࡐࡊ࠭ᩘ"),
  bstack1l1l_opy_ (u"ࠫࡊࡘࡒࡠࡖࡘࡒࡓࡋࡌࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬᩙ"),
  bstack1l1l_opy_ (u"ࠬࡋࡒࡓࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡔࡊࡏࡈࡈࡤࡕࡕࡕࠩᩚ"),
  bstack1l1l_opy_ (u"࠭ࡅࡓࡔࡢࡗࡔࡉࡋࡔࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭ᩛ"),
  bstack1l1l_opy_ (u"ࠧࡆࡔࡕࡣࡘࡕࡃࡌࡕࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡉࡑࡖࡘࡤ࡛ࡎࡓࡇࡄࡇࡍࡇࡂࡍࡇࠪᩜ"),
  bstack1l1l_opy_ (u"ࠨࡇࡕࡖࡤࡖࡒࡐ࡚࡜ࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡈࡄࡍࡑࡋࡄࠨᩝ"),
  bstack1l1l_opy_ (u"ࠩࡈࡖࡗࡥࡎࡂࡏࡈࡣࡓࡕࡔࡠࡔࡈࡗࡔࡒࡖࡆࡆࠪᩞ"),
  bstack1l1l_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡃࡐࡉࡤࡘࡅࡔࡑࡏ࡙࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩ᩟"),
  bstack1l1l_opy_ (u"ࠫࡊࡘࡒࡠࡏࡄࡒࡉࡇࡔࡐࡔ࡜ࡣࡕࡘࡏ࡙࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆ᩠ࠪ"),
]
bstack11llll1l_opy_ = bstack1l1l_opy_ (u"ࠬ࠴࠯ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡡࡳࡶ࡬ࡪࡦࡩࡴࡴ࠱ࠪᩡ")
bstack1l1l1ll11_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"࠭ࡾࠨᩢ")), bstack1l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᩣ"), bstack1l1l_opy_ (u"ࠨ࠰ࡥࡷࡹࡧࡣ࡬࠯ࡦࡳࡳ࡬ࡩࡨ࠰࡭ࡷࡴࡴࠧᩤ"))
bstack11ll11l11ll_opy_ = bstack1l1l_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡡࡱ࡫ࠪᩥ")
bstack11l11lll1ll_opy_ = [ bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪᩦ"), bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪᩧ"), bstack1l1l_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫᩨ"), bstack1l1l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ᩩ")]
bstack1l1ll1ll1_opy_ = [ bstack1l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧᩪ"), bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧᩫ"), bstack1l1l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨᩬ"), bstack1l1l_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪᩭ") ]
bstack111llllll1_opy_ = [ bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪᩮ") ]
bstack11l1l1l1lll_opy_ = [ bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬᩯ") ]
bstack111l111ll_opy_ = 360
bstack11l1lll111l_opy_ = bstack1l1l_opy_ (u"ࠨࡡࡱࡲ࠰ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࠨᩰ")
bstack11l11llll11_opy_ = bstack1l1l_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡦ࠱ࡤࡴ࡮࠵ࡶ࠲࠱࡬ࡷࡸࡻࡥࡴࠤᩱ")
bstack11l1l1l11ll_opy_ = bstack1l1l_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡥࡵ࡯࠯ࡷ࠳࠲࡭ࡸࡹࡵࡦࡵ࠰ࡷࡺࡳ࡭ࡢࡴࡼࠦᩲ")
bstack11l1llll11l_opy_ = bstack1l1l_opy_ (u"ࠤࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡸࡪࡹࡴࡴࠢࡤࡶࡪࠦࡳࡶࡲࡳࡳࡷࡺࡥࡥࠢࡲࡲࠥࡕࡓࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࠨࡷࠥࡧ࡮ࡥࠢࡤࡦࡴࡼࡥࠡࡨࡲࡶࠥࡇ࡮ࡥࡴࡲ࡭ࡩࠦࡤࡦࡸ࡬ࡧࡪࡹ࠮ࠣᩳ")
bstack11ll11l1111_opy_ = bstack1l1l_opy_ (u"ࠥ࠵࠶࠴࠰ࠣᩴ")
bstack1111l1l11l_opy_ = {
  bstack1l1l_opy_ (u"ࠫࡕࡇࡓࡔࠩ᩵"): bstack1l1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ᩶"),
  bstack1l1l_opy_ (u"࠭ࡆࡂࡋࡏࠫ᩷"): bstack1l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ᩸"),
  bstack1l1l_opy_ (u"ࠨࡕࡎࡍࡕ࠭᩹"): bstack1l1l_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ᩺")
}
bstack1l1ll111l_opy_ = [
  bstack1l1l_opy_ (u"ࠥ࡫ࡪࡺࠢ᩻"),
  bstack1l1l_opy_ (u"ࠦ࡬ࡵࡂࡢࡥ࡮ࠦ᩼"),
  bstack1l1l_opy_ (u"ࠧ࡭࡯ࡇࡱࡵࡻࡦࡸࡤࠣ᩽"),
  bstack1l1l_opy_ (u"ࠨࡲࡦࡨࡵࡩࡸ࡮ࠢ᩾"),
  bstack1l1l_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨ᩿"),
  bstack1l1l_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧ᪀"),
  bstack1l1l_opy_ (u"ࠤࡶࡹࡧࡳࡩࡵࡇ࡯ࡩࡲ࡫࡮ࡵࠤ᪁"),
  bstack1l1l_opy_ (u"ࠥࡷࡪࡴࡤࡌࡧࡼࡷ࡙ࡵࡅ࡭ࡧࡰࡩࡳࡺࠢ᪂"),
  bstack1l1l_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡂࡥࡷ࡭ࡻ࡫ࡅ࡭ࡧࡰࡩࡳࡺࠢ᪃"),
  bstack1l1l_opy_ (u"ࠧࡩ࡬ࡦࡣࡵࡉࡱ࡫࡭ࡦࡰࡷࠦ᪄"),
  bstack1l1l_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࡹࠢ᪅"),
  bstack1l1l_opy_ (u"ࠢࡦࡺࡨࡧࡺࡺࡥࡔࡥࡵ࡭ࡵࡺࠢ᪆"),
  bstack1l1l_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࡃࡶࡽࡳࡩࡓࡤࡴ࡬ࡴࡹࠨ᪇"),
  bstack1l1l_opy_ (u"ࠤࡦࡰࡴࡹࡥࠣ᪈"),
  bstack1l1l_opy_ (u"ࠥࡵࡺ࡯ࡴࠣ᪉"),
  bstack1l1l_opy_ (u"ࠦࡵ࡫ࡲࡧࡱࡵࡱ࡙ࡵࡵࡤࡪࡄࡧࡹ࡯࡯࡯ࠤ᪊"),
  bstack1l1l_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲࡓࡵ࡭ࡶ࡬ࡘࡴࡻࡣࡩࠤ᪋"),
  bstack1l1l_opy_ (u"ࠨࡳࡩࡣ࡮ࡩࠧ᪌"),
  bstack1l1l_opy_ (u"ࠢࡤ࡮ࡲࡷࡪࡇࡰࡱࠤ᪍")
]
bstack11l11lll111_opy_ = [
  bstack1l1l_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࠢ᪎"),
  bstack1l1l_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨ᪏"),
  bstack1l1l_opy_ (u"ࠥࡥࡺࡺ࡯ࠣ᪐"),
  bstack1l1l_opy_ (u"ࠦࡲࡧ࡮ࡶࡣ࡯ࠦ᪑"),
  bstack1l1l_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢ᪒")
]
bstack11l111l11_opy_ = {
  bstack1l1l_opy_ (u"ࠨࡣ࡭࡫ࡦ࡯ࠧ᪓"): [bstack1l1l_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨ᪔")],
  bstack1l1l_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧ᪕"): [bstack1l1l_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨ᪖")],
  bstack1l1l_opy_ (u"ࠥࡥࡺࡺ࡯ࠣ᪗"): [bstack1l1l_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡆ࡮ࡨࡱࡪࡴࡴࠣ᪘"), bstack1l1l_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡃࡦࡸ࡮ࡼࡥࡆ࡮ࡨࡱࡪࡴࡴࠣ᪙"), bstack1l1l_opy_ (u"ࠨࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠥ᪚"), bstack1l1l_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨ᪛")],
  bstack1l1l_opy_ (u"ࠣ࡯ࡤࡲࡺࡧ࡬ࠣ᪜"): [bstack1l1l_opy_ (u"ࠤࡰࡥࡳࡻࡡ࡭ࠤ᪝")],
  bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡤࡣࡶࡩࠧ᪞"): [bstack1l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨ᪟")],
}
bstack11l1l111ll1_opy_ = {
  bstack1l1l_opy_ (u"ࠧࡩ࡬ࡪࡥ࡮ࡉࡱ࡫࡭ࡦࡰࡷࠦ᪠"): bstack1l1l_opy_ (u"ࠨࡣ࡭࡫ࡦ࡯ࠧ᪡"),
  bstack1l1l_opy_ (u"ࠢࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠦ᪢"): bstack1l1l_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧ᪣"),
  bstack1l1l_opy_ (u"ࠤࡶࡩࡳࡪࡋࡦࡻࡶࡘࡴࡋ࡬ࡦ࡯ࡨࡲࡹࠨ᪤"): bstack1l1l_opy_ (u"ࠥࡷࡪࡴࡤࡌࡧࡼࡷࠧ᪥"),
  bstack1l1l_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡂࡥࡷ࡭ࡻ࡫ࡅ࡭ࡧࡰࡩࡳࡺࠢ᪦"): bstack1l1l_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࠢᪧ"),
  bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ᪨"): bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤ᪩")
}
bstack111l11l111_opy_ = {
  bstack1l1l_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡃࡏࡐࠬ᪪"): bstack1l1l_opy_ (u"ࠩࡖࡹ࡮ࡺࡥࠡࡕࡨࡸࡺࡶࠧ᪫"),
  bstack1l1l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭᪬"): bstack1l1l_opy_ (u"ࠫࡘࡻࡩࡵࡧࠣࡘࡪࡧࡲࡥࡱࡺࡲࠬ᪭"),
  bstack1l1l_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠪ᪮"): bstack1l1l_opy_ (u"࠭ࡔࡦࡵࡷࠤࡘ࡫ࡴࡶࡲࠪ᪯"),
  bstack1l1l_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫ᪰"): bstack1l1l_opy_ (u"ࠨࡖࡨࡷࡹࠦࡔࡦࡣࡵࡨࡴࡽ࡮ࠨ᪱")
}
bstack11l1l1ll1l1_opy_ = 65536
bstack11l1l1l1ll1_opy_ = bstack1l1l_opy_ (u"ࠩ࠱࠲࠳ࡡࡔࡓࡗࡑࡇࡆ࡚ࡅࡅ࡟ࠪ᪲")
bstack11l1l1lll11_opy_ = [
      bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ᪳"), bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ᪴"), bstack1l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ᪵"), bstack1l1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻ᪶ࠪ"), bstack1l1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴ᪷ࠩ"),
      bstack1l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵ᪸ࠫ"), bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷ᪹ࠬ"), bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡕࡴࡧࡵ᪺ࠫ"), bstack1l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡑࡣࡶࡷࠬ᪻"),
      bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࡐࡤࡱࡪ࠭᪼"), bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ᪽"), bstack1l1l_opy_ (u"ࠧࡢࡷࡷ࡬࡙ࡵ࡫ࡦࡰࠪ᪾")
    ]
bstack11l1l1111l1_opy_= {
  bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰᪿࠬ"): bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱᫀ࠭"),
  bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ᫁"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ᫂"),
  bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶ᫃ࠫ"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵ᫄ࠪ"),
  bstack1l1l_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ᫅"): bstack1l1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᫆"),
  bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ᫇"): bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭᫈"),
  bstack1l1l_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭᫉"): bstack1l1l_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲ᫊ࠧ"),
  bstack1l1l_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩ᫋"): bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪᫌ"),
  bstack1l1l_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬᫍ"): bstack1l1l_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ᫎ"),
  bstack1l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭᫏"): bstack1l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ᫐"),
  bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪ᫑"): bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠫ᫒"),
  bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ᫓"): bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ᫔"),
  bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࠩ᫕"): bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡓࡧࡳࡳࡷࡺࡩ࡯ࡩࠪ᫖"),
  bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ᫗"): bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᫘"),
  bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬ࡕࡰࡵ࡫ࡲࡲࡸ࠭᫙"): bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࠧ᫚"),
  bstack1l1l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵࠪ᫛"): bstack1l1l_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠫ᫜"),
  bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᫝"): bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭᫞"),
  bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᫟"): bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᫠"),
  bstack1l1l_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫ᫡"): bstack1l1l_opy_ (u"ࠨࡴࡨࡶࡺࡴࡔࡦࡵࡷࡷࠬ᫢"),
  bstack1l1l_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ᫣"): bstack1l1l_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ᫤"),
  bstack1l1l_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᫥"): bstack1l1l_opy_ (u"ࠬࡶࡥࡳࡥࡼࡓࡵࡺࡩࡰࡰࡶࠫ᫦"),
  bstack1l1l_opy_ (u"࠭ࡰࡦࡴࡦࡽࡈࡧࡰࡵࡷࡵࡩࡒࡵࡤࡦࠩ᫧"): bstack1l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾࡉࡡࡱࡶࡸࡶࡪࡓ࡯ࡥࡧࠪ᫨"),
  bstack1l1l_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡃࡸࡸࡴࡉࡡࡱࡶࡸࡶࡪࡒ࡯ࡨࡵࠪ᫩"): bstack1l1l_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫ᫪"),
  bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ᫫"): bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ᫬"),
  bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬ᫭"): bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭᫮"),
  bstack1l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ᫯"): bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ᫰"),
  bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᫱"): bstack1l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᫲"),
  bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨ᫳"): bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᫴"),
  bstack1l1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭᫵"): bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧ᫶")
}
bstack11l1l1ll1ll_opy_ = [bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ᫷"), bstack1l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ᫸")]
bstack1111l1ll1_opy_ = (bstack1l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥ᫹"),)
bstack11l11llllll_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠰ࡸ࠴࠳ࡺࡶࡤࡢࡶࡨࡣࡨࡲࡩࠨ᫺")
bstack11l11l1l1_opy_ = bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡡࡶࡶࡲࡱࡦࡺࡥ࠮ࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩ࠴ࡼ࠱࠰ࡩࡵ࡭ࡩࡹ࠯ࠣ᫻")
bstack1lll1111ll_opy_ = bstack1l1l_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࡨࡴ࡬ࡨ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡦࡤࡷ࡭ࡨ࡯ࡢࡴࡧ࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࠧ᫼")
bstack11l1ll1l1_opy_ = bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡣࡸࡸࡴࡳࡡࡵࡧ࠰ࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫࠯ࡷ࠳࠲ࡦࡺ࡯࡬ࡥࡵ࠱࡮ࡸࡵ࡮ࠣ᫽")
class EVENTS(Enum):
  bstack11l1l11llll_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡵ࠱࠲ࡻ࠽ࡴࡷ࡯࡮ࡵ࠯ࡥࡹ࡮ࡲࡤ࡭࡫ࡱ࡯ࠬ᫾")
  bstack1ll1l1l1l_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡣ࡭ࡧࡤࡲࡺࡶࠧ᫿") # final bstack11l1l11l1l1_opy_
  bstack11l1l11lll1_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡴࡧࡱࡨࡱࡵࡧࡴࠩᬀ")
  bstack111ll1l1_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩ࠿ࡶࡲࡪࡰࡷ࠱ࡧࡻࡩ࡭ࡦ࡯࡭ࡳࡱࠧᬁ") #shift post bstack11l1l1111ll_opy_
  bstack11lll11l1_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠾ࡵࡸࡩ࡯ࡶ࠰ࡦࡺ࡯࡬ࡥ࡮࡬ࡲࡰ࠭ᬂ") #shift post bstack11l1l1111ll_opy_
  bstack11l1l1l111l_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡸࡪࡹࡴࡩࡷࡥࠫᬃ") #shift
  bstack11l1l1llll1_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡵ࡫ࡲࡤࡻ࠽ࡨࡴࡽ࡮࡭ࡱࡤࡨࠬᬄ") #shift
  bstack11ll111l1_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦ࠼࡫ࡹࡧ࠳࡭ࡢࡰࡤ࡫ࡪࡳࡥ࡯ࡶࠪᬅ")
  bstack1ll11111l1l_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡡ࠲࠳ࡼ࠾ࡸࡧࡶࡦ࠯ࡵࡩࡸࡻ࡬ࡵࡵࠪᬆ")
  bstack1lll11l111_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡢ࠳࠴ࡽ࠿ࡪࡲࡪࡸࡨࡶ࠲ࡶࡥࡳࡨࡲࡶࡲࡹࡣࡢࡰࠪᬇ")
  bstack1l1l11l1l1_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡣࡸࡸࡴࡳࡡࡵࡧ࠽ࡰࡴࡩࡡ࡭ࠩᬈ") #shift
  bstack1111l1111_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥ࠻ࡣࡳࡴ࠲ࡻࡰ࡭ࡱࡤࡨࠬᬉ") #shift
  bstack11l1llll_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿ࡩࡩ࠮ࡣࡵࡸ࡮࡬ࡡࡤࡶࡶࠫᬊ")
  bstack1lllll11l_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡦ࠷࠱ࡺ࠼ࡪࡩࡹ࠳ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠳ࡲࡦࡵࡸࡰࡹࡹ࠭ࡴࡷࡰࡱࡦࡸࡹࠨᬋ") #shift
  bstack111l1ll1l_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡧ࠱࠲ࡻ࠽࡫ࡪࡺ࠭ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࠭ࡳࡧࡶࡹࡱࡺࡳࠨᬌ") #shift
  bstack11l1l1l1111_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡰࡦࡴࡦࡽࠬᬍ") #shift
  bstack1l1l1111ll1_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡧࡵࡧࡾࡀࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪᬎ")
  bstack1l11l1l11l_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡣࡸࡸࡴࡳࡡࡵࡧ࠽ࡷࡪࡹࡳࡪࡱࡱ࠱ࡸࡺࡡࡵࡷࡶࠫᬏ") #shift
  bstack1ll1llll1l_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠾࡭ࡻࡢ࠮࡯ࡤࡲࡦ࡭ࡥ࡮ࡧࡱࡸࠬᬐ")
  bstack11l11ll1lll_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡴࡷࡵࡸࡺ࠯ࡶࡩࡹࡻࡰࠨᬑ") #shift
  bstack1l1l1l111_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡸ࡫ࡴࡶࡲࠪᬒ")
  bstack11l11llll1l_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡶࡥࡳࡥࡼ࠾ࡸࡴࡡࡱࡵ࡫ࡳࡹ࠭ᬓ") # not bstack11l1l1l1l11_opy_ in python
  bstack11l1l111ll_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡤࡳ࡫ࡹࡩࡷࡀࡱࡶ࡫ࡷࠫᬔ") # used in bstack11l11lll11l_opy_
  bstack1l11l11lll_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡥࡴ࡬ࡺࡪࡸ࠺ࡨࡧࡷࠫᬕ") # used in bstack11l11lll11l_opy_
  bstack1lll1l1l11_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡪࡲࡳࡰ࠭ᬖ")
  bstack1ll1l111ll_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠾ࡸ࡫ࡳࡴ࡫ࡲࡲ࠲ࡴࡡ࡮ࡧࠪᬗ")
  bstack1l1l11ll_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿ࡹࡥࡴࡵ࡬ࡳࡳ࠳ࡡ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠪᬘ") #
  bstack11l1ll11l_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡴ࠷࠱ࡺ࠼ࡧࡶ࡮ࡼࡥࡳ࠯ࡷࡥࡰ࡫ࡓࡤࡴࡨࡩࡳ࡙ࡨࡰࡶࠪᬙ")
  bstack1lllllll1_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡶࡥࡳࡥࡼ࠾ࡦࡻࡴࡰ࠯ࡦࡥࡵࡺࡵࡳࡧࠪᬚ")
  bstack1l1l11l11l_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡰࡳࡧ࠰ࡸࡪࡹࡴࠨᬛ")
  bstack1llll111l_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡱࡶࡸ࠲ࡺࡥࡴࡶࠪᬜ")
  bstack111l1l11l_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡦࡵ࡭ࡻ࡫ࡲ࠻ࡲࡵࡩ࠲࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡢࡶ࡬ࡳࡳ࠭ᬝ") #shift
  bstack1ll1l1l1l1_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡧࡶ࡮ࡼࡥࡳ࠼ࡳࡳࡸࡺ࠭ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡤࡸ࡮ࡵ࡮ࠨᬞ") #shift
  bstack11l1l11l11l_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࠮ࡥࡤࡴࡹࡻࡲࡦࠩᬟ")
  bstack11l1l111111_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡩࡥ࡮ࡨ࠱ࡹ࡯࡭ࡦࡱࡸࡸࠬᬠ")
  bstack1lll111l11l_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡩ࡬ࡪ࠼ࡶࡸࡦࡸࡴࠨᬡ")
  bstack11l1l11111l_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡣ࡭࡫࠽ࡨࡴࡽ࡮࡭ࡱࡤࡨࠬᬢ")
  bstack11l1l111l1l_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡤ࡮࡬࠾ࡨ࡮ࡥࡤ࡭࠰ࡹࡵࡪࡡࡵࡧࠪᬣ")
  bstack1lll11ll11l_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡥ࡯࡭࠿ࡵ࡮࠮ࡤࡲࡳࡹࡹࡴࡳࡣࡳࠫᬤ")
  bstack1lll1ll1l11_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡦࡰ࡮ࡀ࡯࡯࠯ࡦࡳࡳࡴࡥࡤࡶࠪᬥ")
  bstack1ll1llll11l_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡧࡱ࡯࠺ࡰࡰ࠰ࡷࡹࡵࡰࠨᬦ")
  bstack1lll1l1l11l_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡸࡺࡡࡳࡶࡅ࡭ࡳ࡙ࡥࡴࡵ࡬ࡳࡳ࠭ᬧ")
  bstack1lll111lll1_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡩ࡯࡯ࡰࡨࡧࡹࡈࡩ࡯ࡕࡨࡷࡸ࡯࡯࡯ࠩᬨ")
  bstack11l1l111l11_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡤࡳ࡫ࡹࡩࡷࡏ࡮ࡪࡶࠪᬩ")
  bstack11l1l1l11l1_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡧ࡫ࡱࡨࡓ࡫ࡡࡳࡧࡶࡸࡍࡻࡢࠨᬪ")
  bstack1l11l11l1l1_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡉ࡯࡫ࡷࠫᬫ")
  bstack1l11l11ll1l_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡔࡶࡤࡶࡹ࠭ᬬ")
  bstack1l1lllll1l1_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡆࡳࡳ࡬ࡩࡨࠩᬭ")
  bstack11l1l11l111_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡇࡴࡴࡦࡪࡩࠪᬮ")
  bstack1l1lll11l1l_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡩࡔࡧ࡯ࡪࡍ࡫ࡡ࡭ࡕࡷࡩࡵ࠭ᬯ")
  bstack1l1ll1lllll_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡀࡡࡪࡕࡨࡰ࡫ࡎࡥࡢ࡮ࡊࡩࡹࡘࡥࡴࡷ࡯ࡸࠬᬰ")
  bstack1l1l1ll11l1_opy_ = bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࠺ࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡅࡷࡧࡱࡸࠬᬱ")
  bstack1l1ll11l11l_opy_ = bstack1l1l_opy_ (u"ࠫࡸࡪ࡫࠻ࡶࡨࡷࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡋࡶࡦࡰࡷࠫᬲ")
  bstack1l1l1l1111l_opy_ = bstack1l1l_opy_ (u"ࠬࡹࡤ࡬࠼ࡦࡰ࡮ࡀ࡬ࡰࡩࡆࡶࡪࡧࡴࡦࡦࡈࡺࡪࡴࡴࠨᬳ")
  bstack11l1l1ll11l_opy_ = bstack1l1l_opy_ (u"࠭ࡳࡥ࡭࠽ࡧࡱ࡯࠺ࡦࡰࡴࡹࡪࡻࡥࡕࡧࡶࡸࡊࡼࡥ࡯ࡶ᬴ࠪ")
  bstack1l111llllll_opy_ = bstack1l1l_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡖࡸࡴࡶࠧᬵ")
  bstack1ll1lll1l1l_opy_ = bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠿ࡵ࡮ࡔࡶࡲࡴࠬᬶ")
class STAGE(Enum):
  bstack1l1ll1l1ll_opy_ = bstack1l1l_opy_ (u"ࠩࡶࡸࡦࡸࡴࠨᬷ")
  END = bstack1l1l_opy_ (u"ࠪࡩࡳࡪࠧᬸ")
  bstack11lll1l1_opy_ = bstack1l1l_opy_ (u"ࠫࡸ࡯࡮ࡨ࡮ࡨࠫᬹ")
bstack11ll111l_opy_ = {
  bstack1l1l_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࠬᬺ"): bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ᬻ"),
  bstack1l1l_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࠭ࡃࡆࡇࠫᬼ"): bstack1l1l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪᬽ")
}
PLAYWRIGHT_HUB_URL = bstack1l1l_opy_ (u"ࠤࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠦᬾ")
bstack1ll1111llll_opy_ = 98
bstack1ll111ll1l1_opy_ = 100
bstack11111111l1_opy_ = {
  bstack1l1l_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࠩᬿ"): bstack1l1l_opy_ (u"ࠫ࠲࠳ࡲࡦࡴࡸࡲࡸ࠭ᭀ"),
  bstack1l1l_opy_ (u"ࠬࡪࡥ࡭ࡣࡼࠫᭁ"): bstack1l1l_opy_ (u"࠭࠭࠮ࡴࡨࡶࡺࡴࡳ࠮ࡦࡨࡰࡦࡿࠧᭂ"),
  bstack1l1l_opy_ (u"ࠧࡳࡧࡵࡹࡳ࠳ࡤࡦ࡮ࡤࡽࠬᭃ"): 0
}
bstack11l11lll1l1_opy_ = bstack1l1l_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡦࡳࡱࡲࡥࡤࡶࡲࡶ࠲ࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭᭄ࠣ")
bstack11l1l111lll_opy_ = bstack1l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡹࡵࡲ࡯ࡢࡦ࠰ࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࠨᭅ")
bstack11ll1111ll_opy_ = bstack1l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࠡࡔࡈࡔࡔࡘࡔࡊࡐࡊࠤࡆࡔࡄࠡࡃࡑࡅࡑ࡟ࡔࡊࡅࡖࠦᭆ")