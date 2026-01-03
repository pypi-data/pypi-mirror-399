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
import json
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll11lllll_opy_, bstack1l1lll1l_opy_, get_host_info, bstack11l111l11ll_opy_, \
 bstack1l11ll1l11_opy_, bstack11llll11ll_opy_, error_handler, bstack11l111l1ll1_opy_, bstack1111lllll_opy_
import bstack_utils.accessibility as bstack1lllllll11_opy_
from bstack_utils.bstack1l11l1l1ll_opy_ import bstack111l1111l_opy_
from bstack_utils.bstack111ll11l11_opy_ import bstack1l1ll11111_opy_
from bstack_utils.percy import bstack111111l1_opy_
from bstack_utils.config import Config
bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
logger = logging.getLogger(__name__)
percy = bstack111111l1_opy_()
@error_handler(class_method=False)
def bstack1llll111111l_opy_(bs_config, bstack1l11l1111l_opy_):
  try:
    data = {
        bstack1l1l_opy_ (u"ࠬ࡬࡯ࡳ࡯ࡤࡸࠬ≏"): bstack1l1l_opy_ (u"࠭ࡪࡴࡱࡱࠫ≐"),
        bstack1l1l_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡠࡰࡤࡱࡪ࠭≑"): bs_config.get(bstack1l1l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭≒"), bstack1l1l_opy_ (u"ࠩࠪ≓")),
        bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ≔"): bs_config.get(bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ≕"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ≖"): bs_config.get(bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ≗")),
        bstack1l1l_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ≘"): bs_config.get(bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫ≙"), bstack1l1l_opy_ (u"ࠩࠪ≚")),
        bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ≛"): bstack1111lllll_opy_(),
        bstack1l1l_opy_ (u"ࠫࡹࡧࡧࡴࠩ≜"): bstack11l111l11ll_opy_(bs_config),
        bstack1l1l_opy_ (u"ࠬ࡮࡯ࡴࡶࡢ࡭ࡳ࡬࡯ࠨ≝"): get_host_info(),
        bstack1l1l_opy_ (u"࠭ࡣࡪࡡ࡬ࡲ࡫ࡵࠧ≞"): bstack1l1lll1l_opy_(),
        bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡲࡶࡰࡢ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ≟"): os.environ.get(bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧ≠")),
        bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࡡࡷࡩࡸࡺࡳࡠࡴࡨࡶࡺࡴࠧ≡"): os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࠨ≢"), False),
        bstack1l1l_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࡤࡩ࡯࡯ࡶࡵࡳࡱ࠭≣"): bstack11ll11lllll_opy_(),
        bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ≤"): bstack1lll1ll1l11l_opy_(bs_config),
        bstack1l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡧࡩࡹࡧࡩ࡭ࡵࠪ≥"): bstack1lll1ll1l111_opy_(bstack1l11l1111l_opy_),
        bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࡠ࡯ࡤࡴࠬ≦"): bstack1lll1ll1111l_opy_(bs_config, bstack1l11l1111l_opy_.get(bstack1l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡺࡹࡥࡥࠩ≧"), bstack1l1l_opy_ (u"ࠩࠪ≨"))),
        bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ≩"): bstack1l11ll1l11_opy_(bs_config),
        bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠩ≪"): bstack1lll1ll11l1l_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack1l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡳࡥࡾࡲ࡯ࡢࡦࠣࡪࡴࡸࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࠣࡿࢂࠨ≫").format(str(error)))
    return None
def bstack1lll1ll1l111_opy_(framework):
  return {
    bstack1l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡐࡤࡱࡪ࠭≬"): framework.get(bstack1l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࠨ≭"), bstack1l1l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴࠨ≮")),
    bstack1l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ≯"): framework.get(bstack1l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ≰")),
    bstack1l1l_opy_ (u"ࠫࡸࡪ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ≱"): framework.get(bstack1l1l_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ≲")),
    bstack1l1l_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨ≳"): bstack1l1l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ≴"),
    bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ≵"): framework.get(bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ≶"))
  }
def bstack1lll1ll11l1l_opy_(bs_config):
  bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨࠥࡹࡴࡢࡴࡷ࠲ࠏࠦࠠࠣࠤࠥ≷")
  if not bs_config:
    return {}
  bstack1111l1llll1_opy_ = bstack111l1111l_opy_(bs_config).bstack1111l1l1ll1_opy_(bs_config)
  return bstack1111l1llll1_opy_
def bstack11lll1ll_opy_(bs_config, framework):
  bstack1l11l1l1l_opy_ = False
  bstack1lll1l1ll_opy_ = False
  bstack1lll1ll11ll1_opy_ = False
  if bstack1l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ≸") in bs_config:
    bstack1lll1ll11ll1_opy_ = True
  elif bstack1l1l_opy_ (u"ࠬࡧࡰࡱࠩ≹") in bs_config:
    bstack1l11l1l1l_opy_ = True
  else:
    bstack1lll1l1ll_opy_ = True
  bstack1l1ll11l1l_opy_ = {
    bstack1l1l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭≺"): bstack1l1ll11111_opy_.bstack1lll1ll1ll11_opy_(bs_config, framework),
    bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ≻"): bstack1lllllll11_opy_.bstack1ll1lll1l_opy_(bs_config),
    bstack1l1l_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧ≼"): bs_config.get(bstack1l1l_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ≽"), False),
    bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ≾"): bstack1lll1l1ll_opy_,
    bstack1l1l_opy_ (u"ࠫࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠪ≿"): bstack1l11l1l1l_opy_,
    bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩ⊀"): bstack1lll1ll11ll1_opy_
  }
  return bstack1l1ll11l1l_opy_
@error_handler(class_method=False)
def bstack1lll1ll1l11l_opy_(bs_config):
  try:
    bstack1lll1l1lllll_opy_ = json.loads(os.getenv(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ⊁"), bstack1l1l_opy_ (u"ࠧࡼࡿࠪ⊂")))
    bstack1lll1l1lllll_opy_ = bstack1lll1ll11lll_opy_(bs_config, bstack1lll1l1lllll_opy_)
    return {
        bstack1l1l_opy_ (u"ࠨࡵࡨࡸࡹ࡯࡮ࡨࡵࠪ⊃"): bstack1lll1l1lllll_opy_
    }
  except Exception as error:
    logger.error(bstack1l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡷࡪࡺࡴࡪࡰࡪࡷࠥ࡬࡯ࡳࠢࡗࡩࡸࡺࡈࡶࡤ࠽ࠤࠥࢁࡽࠣ⊄").format(str(error)))
    return {}
def bstack1lll1ll11lll_opy_(bs_config, bstack1lll1l1lllll_opy_):
  if ((bstack1l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ⊅") in bs_config or not bstack1l11ll1l11_opy_(bs_config)) and bstack1lllllll11_opy_.bstack1ll1lll1l_opy_(bs_config)):
    bstack1lll1l1lllll_opy_[bstack1l1l_opy_ (u"ࠦ࡮ࡴࡣ࡭ࡷࡧࡩࡊࡴࡣࡰࡦࡨࡨࡊࡾࡴࡦࡰࡶ࡭ࡴࡴࠢ⊆")] = True
  return bstack1lll1l1lllll_opy_
def bstack1lll1lll11ll_opy_(array, bstack1lll1ll11l11_opy_, bstack1lll1ll111ll_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1ll11l11_opy_]
    result[key] = o[bstack1lll1ll111ll_opy_]
  return result
def bstack1lll1ll1ll1l_opy_(bstack11111ll1_opy_=bstack1l1l_opy_ (u"ࠬ࠭⊇")):
  bstack1lll1ll11111_opy_ = bstack1lllllll11_opy_.on()
  bstack1lll1ll111l1_opy_ = bstack1l1ll11111_opy_.on()
  bstack1lll1ll1l1ll_opy_ = percy.bstack1l1l11111l_opy_()
  if bstack1lll1ll1l1ll_opy_ and not bstack1lll1ll111l1_opy_ and not bstack1lll1ll11111_opy_:
    return bstack11111ll1_opy_ not in [bstack1l1l_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪ⊈"), bstack1l1l_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ⊉")]
  elif bstack1lll1ll11111_opy_ and not bstack1lll1ll111l1_opy_:
    return bstack11111ll1_opy_ not in [bstack1l1l_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⊊"), bstack1l1l_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⊋"), bstack1l1l_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧ⊌")]
  return bstack1lll1ll11111_opy_ or bstack1lll1ll111l1_opy_ or bstack1lll1ll1l1ll_opy_
@error_handler(class_method=False)
def bstack1lll1lllll11_opy_(bstack11111ll1_opy_, test=None):
  bstack1lll1ll1l1l1_opy_ = bstack1lllllll11_opy_.on()
  if not bstack1lll1ll1l1l1_opy_ or bstack11111ll1_opy_ not in [bstack1l1l_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⊍")] or test == None:
    return None
  return {
    bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⊎"): bstack1lll1ll1l1l1_opy_ and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ⊏"), None) == True and bstack1lllllll11_opy_.bstack1l111lll_opy_(test[bstack1l1l_opy_ (u"ࠧࡵࡣࡪࡷࠬ⊐")])
  }
def bstack1lll1ll1111l_opy_(bs_config, framework):
  bstack1l11l1l1l_opy_ = False
  bstack1lll1l1ll_opy_ = False
  bstack1lll1ll11ll1_opy_ = False
  if bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ⊑") in bs_config:
    bstack1lll1ll11ll1_opy_ = True
  elif bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࠭⊒") in bs_config:
    bstack1l11l1l1l_opy_ = True
  else:
    bstack1lll1l1ll_opy_ = True
  bstack1l1ll11l1l_opy_ = {
    bstack1l1l_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⊓"): bstack1l1ll11111_opy_.bstack1lll1ll1ll11_opy_(bs_config, framework),
    bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ⊔"): bstack1lllllll11_opy_.bstack1l11llll_opy_(bs_config),
    bstack1l1l_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫ⊕"): bs_config.get(bstack1l1l_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ⊖"), False),
    bstack1l1l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩ⊗"): bstack1lll1l1ll_opy_,
    bstack1l1l_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ⊘"): bstack1l11l1l1l_opy_,
    bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭⊙"): bstack1lll1ll11ll1_opy_
  }
  return bstack1l1ll11l1l_opy_