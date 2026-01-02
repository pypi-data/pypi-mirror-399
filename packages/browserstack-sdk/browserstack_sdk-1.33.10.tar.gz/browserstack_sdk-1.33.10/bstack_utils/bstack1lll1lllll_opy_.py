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
import os
import json
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll111l11l_opy_, bstack1lllll11l1_opy_, get_host_info, bstack111ll1111l1_opy_, \
 bstack1l1ll11l1l_opy_, bstack11l1l111l_opy_, error_handler, bstack111l1ll1111_opy_, bstack111l1l11_opy_
import bstack_utils.accessibility as bstack1l1l11ll11_opy_
from bstack_utils.bstack1ll1ll1111_opy_ import bstack1l11ll1111_opy_
from bstack_utils.bstack111l1ll111_opy_ import bstack11l11ll11l_opy_
from bstack_utils.percy import bstack11l111l1ll_opy_
from bstack_utils.config import Config
bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
logger = logging.getLogger(__name__)
percy = bstack11l111l1ll_opy_()
@error_handler(class_method=False)
def bstack1llll11111l1_opy_(bs_config, bstack1l11111l_opy_):
  try:
    data = {
        bstack11111l_opy_ (u"ࠬ࡬࡯ࡳ࡯ࡤࡸࠬ≈"): bstack11111l_opy_ (u"࠭ࡪࡴࡱࡱࠫ≉"),
        bstack11111l_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡠࡰࡤࡱࡪ࠭≊"): bs_config.get(bstack11111l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭≋"), bstack11111l_opy_ (u"ࠩࠪ≌")),
        bstack11111l_opy_ (u"ࠪࡲࡦࡳࡥࠨ≍"): bs_config.get(bstack11111l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ≎"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack11111l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ≏"): bs_config.get(bstack11111l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ≐")),
        bstack11111l_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ≑"): bs_config.get(bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫ≒"), bstack11111l_opy_ (u"ࠩࠪ≓")),
        bstack11111l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ≔"): bstack111l1l11_opy_(),
        bstack11111l_opy_ (u"ࠫࡹࡧࡧࡴࠩ≕"): bstack111ll1111l1_opy_(bs_config),
        bstack11111l_opy_ (u"ࠬ࡮࡯ࡴࡶࡢ࡭ࡳ࡬࡯ࠨ≖"): get_host_info(),
        bstack11111l_opy_ (u"࠭ࡣࡪࡡ࡬ࡲ࡫ࡵࠧ≗"): bstack1lllll11l1_opy_(),
        bstack11111l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡲࡶࡰࡢ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ≘"): os.environ.get(bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧ≙")),
        bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࡡࡷࡩࡸࡺࡳࡠࡴࡨࡶࡺࡴࠧ≚"): os.environ.get(bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࠨ≛"), False),
        bstack11111l_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࡤࡩ࡯࡯ࡶࡵࡳࡱ࠭≜"): bstack11ll111l11l_opy_(),
        bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ≝"): bstack1lll1ll11l11_opy_(bs_config),
        bstack11111l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡧࡩࡹࡧࡩ࡭ࡵࠪ≞"): bstack1lll1ll1l111_opy_(bstack1l11111l_opy_),
        bstack11111l_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࡠ࡯ࡤࡴࠬ≟"): bstack1lll1ll1l1ll_opy_(bs_config, bstack1l11111l_opy_.get(bstack11111l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡺࡹࡥࡥࠩ≠"), bstack11111l_opy_ (u"ࠩࠪ≡"))),
        bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ≢"): bstack1l1ll11l1l_opy_(bs_config),
        bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠩ≣"): bstack1lll1ll1ll1l_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack11111l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡳࡥࡾࡲ࡯ࡢࡦࠣࡪࡴࡸࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࠣࡿࢂࠨ≤").format(str(error)))
    return None
def bstack1lll1ll1l111_opy_(framework):
  return {
    bstack11111l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡐࡤࡱࡪ࠭≥"): framework.get(bstack11111l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࠨ≦"), bstack11111l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴࠨ≧")),
    bstack11111l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ≨"): framework.get(bstack11111l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ≩")),
    bstack11111l_opy_ (u"ࠫࡸࡪ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ≪"): framework.get(bstack11111l_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ≫")),
    bstack11111l_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨ≬"): bstack11111l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ≭"),
    bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ≮"): framework.get(bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ≯"))
  }
def bstack1lll1ll1ll1l_opy_(bs_config):
  bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨࠥࡹࡴࡢࡴࡷ࠲ࠏࠦࠠࠣࠤࠥ≰")
  if not bs_config:
    return {}
  bstack1111l1l11ll_opy_ = bstack1l11ll1111_opy_(bs_config).bstack1111l111ll1_opy_(bs_config)
  return bstack1111l1l11ll_opy_
def bstack1ll111111l_opy_(bs_config, framework):
  bstack1ll1111ll_opy_ = False
  bstack1l1lllll1l_opy_ = False
  bstack1lll1ll1ll11_opy_ = False
  if bstack11111l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ≱") in bs_config:
    bstack1lll1ll1ll11_opy_ = True
  elif bstack11111l_opy_ (u"ࠬࡧࡰࡱࠩ≲") in bs_config:
    bstack1ll1111ll_opy_ = True
  else:
    bstack1l1lllll1l_opy_ = True
  bstack1ll11ll11l_opy_ = {
    bstack11111l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭≳"): bstack11l11ll11l_opy_.bstack1lll1ll11l1l_opy_(bs_config, framework),
    bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ≴"): bstack1l1l11ll11_opy_.bstack1l11111l1l_opy_(bs_config),
    bstack11111l_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧ≵"): bs_config.get(bstack11111l_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ≶"), False),
    bstack11111l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ≷"): bstack1l1lllll1l_opy_,
    bstack11111l_opy_ (u"ࠫࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠪ≸"): bstack1ll1111ll_opy_,
    bstack11111l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩ≹"): bstack1lll1ll1ll11_opy_
  }
  return bstack1ll11ll11l_opy_
@error_handler(class_method=False)
def bstack1lll1ll11l11_opy_(bs_config):
  try:
    bstack1lll1ll111l1_opy_ = json.loads(os.getenv(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ≺"), bstack11111l_opy_ (u"ࠧࡼࡿࠪ≻")))
    bstack1lll1ll111l1_opy_ = bstack1lll1ll111ll_opy_(bs_config, bstack1lll1ll111l1_opy_)
    return {
        bstack11111l_opy_ (u"ࠨࡵࡨࡸࡹ࡯࡮ࡨࡵࠪ≼"): bstack1lll1ll111l1_opy_
    }
  except Exception as error:
    logger.error(bstack11111l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡷࡪࡺࡴࡪࡰࡪࡷࠥ࡬࡯ࡳࠢࡗࡩࡸࡺࡈࡶࡤ࠽ࠤࠥࢁࡽࠣ≽").format(str(error)))
    return {}
def bstack1lll1ll111ll_opy_(bs_config, bstack1lll1ll111l1_opy_):
  if ((bstack11111l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ≾") in bs_config or not bstack1l1ll11l1l_opy_(bs_config)) and bstack1l1l11ll11_opy_.bstack1l11111l1l_opy_(bs_config)):
    bstack1lll1ll111l1_opy_[bstack11111l_opy_ (u"ࠦ࡮ࡴࡣ࡭ࡷࡧࡩࡊࡴࡣࡰࡦࡨࡨࡊࡾࡴࡦࡰࡶ࡭ࡴࡴࠢ≿")] = True
  return bstack1lll1ll111l1_opy_
def bstack1llll1111111_opy_(array, bstack1lll1ll1l11l_opy_, bstack1lll1ll1lll1_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1ll1l11l_opy_]
    result[key] = o[bstack1lll1ll1lll1_opy_]
  return result
def bstack1lll1lll11ll_opy_(bstack1l111l1lll_opy_=bstack11111l_opy_ (u"ࠬ࠭⊀")):
  bstack1lll1ll11ll1_opy_ = bstack1l1l11ll11_opy_.on()
  bstack1lll1ll1111l_opy_ = bstack11l11ll11l_opy_.on()
  bstack1lll1ll1l1l1_opy_ = percy.bstack11l11l1111_opy_()
  if bstack1lll1ll1l1l1_opy_ and not bstack1lll1ll1111l_opy_ and not bstack1lll1ll11ll1_opy_:
    return bstack1l111l1lll_opy_ not in [bstack11111l_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪ⊁"), bstack11111l_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ⊂")]
  elif bstack1lll1ll11ll1_opy_ and not bstack1lll1ll1111l_opy_:
    return bstack1l111l1lll_opy_ not in [bstack11111l_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⊃"), bstack11111l_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⊄"), bstack11111l_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧ⊅")]
  return bstack1lll1ll11ll1_opy_ or bstack1lll1ll1111l_opy_ or bstack1lll1ll1l1l1_opy_
@error_handler(class_method=False)
def bstack1llll111111l_opy_(bstack1l111l1lll_opy_, test=None):
  bstack1lll1ll11lll_opy_ = bstack1l1l11ll11_opy_.on()
  if not bstack1lll1ll11lll_opy_ or bstack1l111l1lll_opy_ not in [bstack11111l_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⊆")] or test == None:
    return None
  return {
    bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⊇"): bstack1lll1ll11lll_opy_ and bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ⊈"), None) == True and bstack1l1l11ll11_opy_.bstack11llllllll_opy_(test[bstack11111l_opy_ (u"ࠧࡵࡣࡪࡷࠬ⊉")])
  }
def bstack1lll1ll1l1ll_opy_(bs_config, framework):
  bstack1ll1111ll_opy_ = False
  bstack1l1lllll1l_opy_ = False
  bstack1lll1ll1ll11_opy_ = False
  if bstack11111l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ⊊") in bs_config:
    bstack1lll1ll1ll11_opy_ = True
  elif bstack11111l_opy_ (u"ࠩࡤࡴࡵ࠭⊋") in bs_config:
    bstack1ll1111ll_opy_ = True
  else:
    bstack1l1lllll1l_opy_ = True
  bstack1ll11ll11l_opy_ = {
    bstack11111l_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⊌"): bstack11l11ll11l_opy_.bstack1lll1ll11l1l_opy_(bs_config, framework),
    bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ⊍"): bstack1l1l11ll11_opy_.bstack111lll1l1_opy_(bs_config),
    bstack11111l_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫ⊎"): bs_config.get(bstack11111l_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ⊏"), False),
    bstack11111l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩ⊐"): bstack1l1lllll1l_opy_,
    bstack11111l_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ⊑"): bstack1ll1111ll_opy_,
    bstack11111l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭⊒"): bstack1lll1ll1ll11_opy_
  }
  return bstack1ll11ll11l_opy_