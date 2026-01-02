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
import requests
import logging
import threading
import bstack_utils.constants as bstack11ll11ll1l1_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll11l11l1_opy_ as bstack11ll11l111l_opy_, EVENTS
from bstack_utils.bstack11ll11111_opy_ import bstack11ll11111_opy_
from bstack_utils.helper import bstack111l1l11_opy_, bstack1111ll1ll1_opy_, bstack1l1ll11l1l_opy_, bstack11ll111l1ll_opy_, \
  bstack11l1llll1ll_opy_, bstack1lllll11l1_opy_, get_host_info, bstack11ll111l11l_opy_, bstack111ll1lll_opy_, error_handler, bstack11ll1l11l11_opy_, bstack11ll1111l11_opy_, bstack11l1l111l_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1l1llll1_opy_ import get_logger
from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
logger = get_logger(__name__)
bstack1ll11ll1l1_opy_ = bstack1ll1l111ll1_opy_()
@error_handler(class_method=False)
def _11ll1l11111_opy_(driver, bstack1lllllll111_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack11111l_opy_ (u"࠭࡯ࡴࡡࡱࡥࡲ࡫ࠧᙹ"): caps.get(bstack11111l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭ᙺ"), None),
        bstack11111l_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᙻ"): bstack1lllllll111_opy_.get(bstack11111l_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᙼ"), None),
        bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩᙽ"): caps.get(bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᙾ"), None),
        bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᙿ"): caps.get(bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ "), None)
    }
  except Exception as error:
    logger.debug(bstack11111l_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲࠡ࠼ࠣࠫᚁ") + str(error))
  return response
def on():
    if os.environ.get(bstack11111l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᚂ"), None) is None or os.environ[bstack11111l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᚃ")] == bstack11111l_opy_ (u"ࠥࡲࡺࡲ࡬ࠣᚄ"):
        return False
    return True
def bstack1l11111l1l_opy_(config):
  return config.get(bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚅ"), False) or any([p.get(bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᚆ"), False) == True for p in config.get(bstack11111l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᚇ"), [])])
def bstack11l1ll1lll_opy_(config, bstack1l11l111ll_opy_):
  try:
    bstack11ll111111l_opy_ = config.get(bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᚈ"), False)
    if int(bstack1l11l111ll_opy_) < len(config.get(bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᚉ"), [])) and config[bstack11111l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᚊ")][bstack1l11l111ll_opy_]:
      bstack11ll111ll1l_opy_ = config[bstack11111l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᚋ")][bstack1l11l111ll_opy_].get(bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚌ"), None)
    else:
      bstack11ll111ll1l_opy_ = config.get(bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᚍ"), None)
    if bstack11ll111ll1l_opy_ != None:
      bstack11ll111111l_opy_ = bstack11ll111ll1l_opy_
    bstack11ll111ll11_opy_ = os.getenv(bstack11111l_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᚎ")) is not None and len(os.getenv(bstack11111l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᚏ"))) > 0 and os.getenv(bstack11111l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᚐ")) != bstack11111l_opy_ (u"ࠩࡱࡹࡱࡲࠧᚑ")
    return bstack11ll111111l_opy_ and bstack11ll111ll11_opy_
  except Exception as error:
    logger.debug(bstack11111l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡹࡩࡷ࡯ࡦࡺ࡫ࡱ࡫ࠥࡺࡨࡦࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡩࡸࡹࡩࡰࡰࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠ࠻ࠢࠪᚒ") + str(error))
  return False
def bstack11llllllll_opy_(test_tags):
  bstack1l1llll1l1l_opy_ = os.getenv(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᚓ"))
  if bstack1l1llll1l1l_opy_ is None:
    return True
  bstack1l1llll1l1l_opy_ = json.loads(bstack1l1llll1l1l_opy_)
  try:
    include_tags = bstack1l1llll1l1l_opy_[bstack11111l_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᚔ")] if bstack11111l_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᚕ") in bstack1l1llll1l1l_opy_ and isinstance(bstack1l1llll1l1l_opy_[bstack11111l_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᚖ")], list) else []
    exclude_tags = bstack1l1llll1l1l_opy_[bstack11111l_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᚗ")] if bstack11111l_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᚘ") in bstack1l1llll1l1l_opy_ and isinstance(bstack1l1llll1l1l_opy_[bstack11111l_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᚙ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack11111l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡹࡥࡱ࡯ࡤࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡩࡳࡷࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡢࡦࡨࡲࡶࡪࠦࡳࡤࡣࡱࡲ࡮ࡴࡧ࠯ࠢࡈࡶࡷࡵࡲࠡ࠼ࠣࠦᚚ") + str(error))
  return False
def bstack11ll11l11ll_opy_(config, bstack11ll1111ll1_opy_, bstack11ll11lllll_opy_, bstack11ll111llll_opy_):
  bstack11ll11llll1_opy_ = bstack11ll111l1ll_opy_(config)
  bstack11ll11l1l11_opy_ = bstack11l1llll1ll_opy_(config)
  if bstack11ll11llll1_opy_ is None or bstack11ll11l1l11_opy_ is None:
    logger.error(bstack11111l_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡳࡷࡱࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠾ࠥࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡡࡶࡶ࡫ࡩࡳࡺࡩࡤࡣࡷ࡭ࡴࡴࠠࡵࡱ࡮ࡩࡳ࠭᚛"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ᚜"), bstack11111l_opy_ (u"ࠧࡼࡿࠪ᚝")))
    data = {
        bstack11111l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭᚞"): config[bstack11111l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧ᚟")],
        bstack11111l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ᚠ"): config.get(bstack11111l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᚡ"), os.path.basename(os.getcwd())),
        bstack11111l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡘ࡮ࡳࡥࠨᚢ"): bstack111l1l11_opy_(),
        bstack11111l_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫᚣ"): config.get(bstack11111l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᚤ"), bstack11111l_opy_ (u"ࠨࠩᚥ")),
        bstack11111l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩᚦ"): {
            bstack11111l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡔࡡ࡮ࡧࠪᚧ"): bstack11ll1111ll1_opy_,
            bstack11111l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧᚨ"): bstack11ll11lllll_opy_,
            bstack11111l_opy_ (u"ࠬࡹࡤ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩᚩ"): __version__,
            bstack11111l_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨᚪ"): bstack11111l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧᚫ"),
            bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᚬ"): bstack11111l_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࠫᚭ"),
            bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪᚮ"): bstack11ll111llll_opy_
        },
        bstack11111l_opy_ (u"ࠫࡸ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭ᚯ"): settings,
        bstack11111l_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳࡉ࡯࡯ࡶࡵࡳࡱ࠭ᚰ"): bstack11ll111l11l_opy_(),
        bstack11111l_opy_ (u"࠭ࡣࡪࡋࡱࡪࡴ࠭ᚱ"): bstack1lllll11l1_opy_(),
        bstack11111l_opy_ (u"ࠧࡩࡱࡶࡸࡎࡴࡦࡰࠩᚲ"): get_host_info(),
        bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᚳ"): bstack1l1ll11l1l_opy_(config)
    }
    headers = {
        bstack11111l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨᚴ"): bstack11111l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ᚵ"),
    }
    config = {
        bstack11111l_opy_ (u"ࠫࡦࡻࡴࡩࠩᚶ"): (bstack11ll11llll1_opy_, bstack11ll11l1l11_opy_),
        bstack11111l_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭ᚷ"): headers
    }
    response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"࠭ࡐࡐࡕࡗࠫᚸ"), bstack11ll11l111l_opy_ + bstack11111l_opy_ (u"ࠧ࠰ࡸ࠵࠳ࡹ࡫ࡳࡵࡡࡵࡹࡳࡹࠧᚹ"), data, config)
    bstack11ll11ll111_opy_ = response.json()
    if bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᚺ")]:
      parsed = json.loads(os.getenv(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᚻ"), bstack11111l_opy_ (u"ࠪࡿࢂ࠭ᚼ")))
      parsed[bstack11111l_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᚽ")] = bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠬࡪࡡࡵࡣࠪᚾ")][bstack11111l_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᚿ")]
      os.environ[bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨᛀ")] = json.dumps(parsed)
      bstack11ll11111_opy_.bstack1lllll1ll1_opy_(bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠨࡦࡤࡸࡦ࠭ᛁ")][bstack11111l_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪᛂ")])
      bstack11ll11111_opy_.bstack11ll1l111ll_opy_(bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠪࡨࡦࡺࡡࠨᛃ")][bstack11111l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭ᛄ")])
      bstack11ll11111_opy_.store()
      return bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠬࡪࡡࡵࡣࠪᛅ")][bstack11111l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࡚࡯࡬ࡧࡱࠫᛆ")], bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠧࡥࡣࡷࡥࠬᛇ")][bstack11111l_opy_ (u"ࠨ࡫ࡧࠫᛈ")]
    else:
      logger.error(bstack11111l_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡷࡻ࡮࡯࡫ࡱ࡫ࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠻ࠢࠪᛉ") + bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᛊ")])
      if bstack11ll11ll111_opy_[bstack11111l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᛋ")] == bstack11111l_opy_ (u"ࠬࡏ࡮ࡷࡣ࡯࡭ࡩࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡰࡢࡵࡶࡩࡩ࠴ࠧᛌ"):
        for bstack11l1llllll1_opy_ in bstack11ll11ll111_opy_[bstack11111l_opy_ (u"࠭ࡥࡳࡴࡲࡶࡸ࠭ᛍ")]:
          logger.error(bstack11l1llllll1_opy_[bstack11111l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᛎ")])
      return None, None
  except Exception as error:
    logger.error(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡶࡺࡴࠠࡧࡱࡵࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠺ࠡࠤᛏ") +  str(error))
    return None, None
def bstack11ll11l1ll1_opy_():
  if os.getenv(bstack11111l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᛐ")) is None:
    return {
        bstack11111l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪᛑ"): bstack11111l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᛒ"),
        bstack11111l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᛓ"): bstack11111l_opy_ (u"࠭ࡂࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠࡩࡣࡧࠤ࡫ࡧࡩ࡭ࡧࡧ࠲ࠬᛔ")
    }
  data = {bstack11111l_opy_ (u"ࠧࡦࡰࡧࡘ࡮ࡳࡥࠨᛕ"): bstack111l1l11_opy_()}
  headers = {
      bstack11111l_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨᛖ"): bstack11111l_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࠪᛗ") + os.getenv(bstack11111l_opy_ (u"ࠥࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠣᛘ")),
      bstack11111l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪᛙ"): bstack11111l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨᛚ")
  }
  response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"࠭ࡐࡖࡖࠪᛛ"), bstack11ll11l111l_opy_ + bstack11111l_opy_ (u"ࠧ࠰ࡶࡨࡷࡹࡥࡲࡶࡰࡶ࠳ࡸࡺ࡯ࡱࠩᛜ"), data, { bstack11111l_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡴࠩᛝ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack11111l_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࡚ࠥࡥࡴࡶࠣࡖࡺࡴࠠ࡮ࡣࡵ࡯ࡪࡪࠠࡢࡵࠣࡧࡴࡳࡰ࡭ࡧࡷࡩࡩࠦࡡࡵࠢࠥᛞ") + bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"ࠪ࡞ࠬᛟ"))
      return {bstack11111l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᛠ"): bstack11111l_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ᛡ"), bstack11111l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᛢ"): bstack11111l_opy_ (u"ࠧࠨᛣ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡨࡵ࡭ࡱ࡮ࡨࡸ࡮ࡵ࡮ࠡࡱࡩࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡕࡧࡶࡸࠥࡘࡵ࡯࠼ࠣࠦᛤ") + str(error))
    return {
        bstack11111l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩᛥ"): bstack11111l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᛦ"),
        bstack11111l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᛧ"): str(error)
    }
def bstack11ll11l1l1l_opy_(bstack11l1lllllll_opy_):
    return re.match(bstack11111l_opy_ (u"ࡷ࠭࡞࡝ࡦ࠮ࠬࡡ࠴࡜ࡥ࠭ࠬࡃࠩ࠭ᛨ"), bstack11l1lllllll_opy_.strip()) is not None
def bstack1111lllll_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11ll11lll1l_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11ll11lll1l_opy_ = desired_capabilities
        else:
          bstack11ll11lll1l_opy_ = {}
        bstack1ll1111l1ll_opy_ = (bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᛩ"), bstack11111l_opy_ (u"ࠧࠨᛪ")).lower() or caps.get(bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧ᛫"), bstack11111l_opy_ (u"ࠩࠪ᛬")).lower())
        if bstack1ll1111l1ll_opy_ == bstack11111l_opy_ (u"ࠪ࡭ࡴࡹࠧ᛭"):
            return True
        if bstack1ll1111l1ll_opy_ == bstack11111l_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࠬᛮ"):
            bstack1l1llllll11_opy_ = str(float(caps.get(bstack11111l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧᛯ")) or bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᛰ"), {}).get(bstack11111l_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪᛱ"),bstack11111l_opy_ (u"ࠨࠩᛲ"))))
            if bstack1ll1111l1ll_opy_ == bstack11111l_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࠪᛳ") and int(bstack1l1llllll11_opy_.split(bstack11111l_opy_ (u"ࠪ࠲ࠬᛴ"))[0]) < float(bstack11ll11111l1_opy_):
                logger.warning(str(bstack11ll11l1111_opy_))
                return False
            return True
        bstack1ll1111llll_opy_ = caps.get(bstack11111l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᛵ"), {}).get(bstack11111l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩᛶ"), caps.get(bstack11111l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ᛷ"), bstack11111l_opy_ (u"ࠧࠨᛸ")))
        if bstack1ll1111llll_opy_:
            logger.warning(bstack11111l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡆࡨࡷࡰࡺ࡯ࡱࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧ᛹"))
            return False
        browser = caps.get(bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ᛺"), bstack11111l_opy_ (u"ࠪࠫ᛻")).lower() or bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ᛼"), bstack11111l_opy_ (u"ࠬ࠭᛽")).lower()
        if browser != bstack11111l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭᛾"):
            logger.warning(bstack11111l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥ᛿"))
            return False
        browser_version = caps.get(bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᜀ")) or caps.get(bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫᜁ")) or bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᜂ")) or bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᜃ"), {}).get(bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᜄ")) or bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᜅ"), {}).get(bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᜆ"))
        bstack1ll11l1ll1l_opy_ = bstack11ll11ll1l1_opy_.bstack1l1llllllll_opy_
        bstack11ll111l1l1_opy_ = False
        if config is not None:
          bstack11ll111l1l1_opy_ = bstack11111l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᜇ") in config and str(config[bstack11111l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ᜈ")]).lower() != bstack11111l_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩᜉ")
        if os.environ.get(bstack11111l_opy_ (u"ࠫࡎ࡙࡟ࡏࡑࡑࡣࡇ࡙ࡔࡂࡅࡎࡣࡎࡔࡆࡓࡃࡢࡅ࠶࠷࡙ࡠࡕࡈࡗࡘࡏࡏࡏࠩᜊ"), bstack11111l_opy_ (u"ࠬ࠭ᜋ")).lower() == bstack11111l_opy_ (u"࠭ࡴࡳࡷࡨࠫᜌ") or bstack11ll111l1l1_opy_:
          bstack1ll11l1ll1l_opy_ = bstack11ll11ll1l1_opy_.bstack1ll1111l11l_opy_
        if browser_version and browser_version != bstack11111l_opy_ (u"ࠧ࡭ࡣࡷࡩࡸࡺࠧᜍ") and int(browser_version.split(bstack11111l_opy_ (u"ࠨ࠰ࠪᜎ"))[0]) <= bstack1ll11l1ll1l_opy_:
          logger.warning(bstack1ll1lll1l1l_opy_ (u"ࠩࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡺࡪࡸࡳࡪࡱࡱࠤ࡬ࡸࡥࡢࡶࡨࡶࠥࡺࡨࡢࡰࠣࡿࡲ࡯࡮ࡠࡣ࠴࠵ࡾࡥࡳࡶࡲࡳࡳࡷࡺࡥࡥࡡࡦ࡬ࡷࡵ࡭ࡦࡡࡹࡩࡷࡹࡩࡰࡰࢀ࠲ࠬᜏ"))
          return False
        if not options:
          bstack1ll11l1111l_opy_ = caps.get(bstack11111l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᜐ")) or bstack11ll11lll1l_opy_.get(bstack11111l_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᜑ"), {})
          if bstack11111l_opy_ (u"ࠬ࠳࠭ࡩࡧࡤࡨࡱ࡫ࡳࡴࠩᜒ") in bstack1ll11l1111l_opy_.get(bstack11111l_opy_ (u"࠭ࡡࡳࡩࡶࠫᜓ"), []):
              logger.warning(bstack11111l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡱࡳࡹࠦࡲࡶࡰࠣࡳࡳࠦ࡬ࡦࡩࡤࡧࡾࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠠࡔࡹ࡬ࡸࡨ࡮ࠠࡵࡱࠣࡲࡪࡽࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫ࠠࡰࡴࠣࡥࡻࡵࡩࡥࠢࡸࡷ࡮ࡴࡧࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠤ᜔"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡷࡣ࡯࡭ࡩࡧࡴࡦࠢࡤ࠵࠶ࡿࠠࡴࡷࡳࡴࡴࡸࡴࠡ࠼᜕ࠥ") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1ll1l111l1l_opy_ = config.get(bstack11111l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᜖"), {})
    bstack1ll1l111l1l_opy_[bstack11111l_opy_ (u"ࠪࡥࡺࡺࡨࡕࡱ࡮ࡩࡳ࠭᜗")] = os.getenv(bstack11111l_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ᜘"))
    bstack11ll11111ll_opy_ = json.loads(os.getenv(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭᜙"), bstack11111l_opy_ (u"࠭ࡻࡾࠩ᜚"))).get(bstack11111l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ᜛"))
    if not config[bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪ᜜")].get(bstack11111l_opy_ (u"ࠤࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠣ᜝")):
      if bstack11111l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ᜞") in caps:
        caps[bstack11111l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᜟ")][bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᜠ")] = bstack1ll1l111l1l_opy_
        caps[bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᜡ")][bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᜢ")][bstack11111l_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᜣ")] = bstack11ll11111ll_opy_
      else:
        caps[bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᜤ")] = bstack1ll1l111l1l_opy_
        caps[bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᜥ")][bstack11111l_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᜦ")] = bstack11ll11111ll_opy_
  except Exception as error:
    logger.debug(bstack11111l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶ࠲ࠥࡋࡲࡳࡱࡵ࠾ࠥࠨᜧ") +  str(error))
def bstack11l111l111_opy_(driver, bstack11ll1l11l1l_opy_):
  try:
    setattr(driver, bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭ᜨ"), True)
    session = driver.session_id
    if session:
      bstack11ll111lll1_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11ll111lll1_opy_ = False
      bstack11ll111lll1_opy_ = url.scheme in [bstack11111l_opy_ (u"ࠢࡩࡶࡷࡴࠧᜩ"), bstack11111l_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᜪ")]
      if bstack11ll111lll1_opy_:
        if bstack11ll1l11l1l_opy_:
          logger.info(bstack11111l_opy_ (u"ࠤࡖࡩࡹࡻࡰࠡࡨࡲࡶࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡨࡢࡵࠣࡷࡹࡧࡲࡵࡧࡧ࠲ࠥࡇࡵࡵࡱࡰࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡧ࡫ࡧࡪࡰࠣࡱࡴࡳࡥ࡯ࡶࡤࡶ࡮ࡲࡹ࠯ࠤᜫ"))
      return bstack11ll1l11l1l_opy_
  except Exception as e:
    logger.error(bstack11111l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡦࡸࡴࡪࡰࡪࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡦࡥࡳࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨ࠾ࠥࠨᜬ") + str(e))
    return False
def bstack11lll11lll_opy_(driver, name, path):
  try:
    bstack1ll11111lll_opy_ = {
        bstack11111l_opy_ (u"ࠫࡹ࡮ࡔࡦࡵࡷࡖࡺࡴࡕࡶ࡫ࡧࠫᜭ"): threading.current_thread().current_test_uuid,
        bstack11111l_opy_ (u"ࠬࡺࡨࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᜮ"): os.environ.get(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᜯ"), bstack11111l_opy_ (u"ࠧࠨᜰ")),
        bstack11111l_opy_ (u"ࠨࡶ࡫ࡎࡼࡺࡔࡰ࡭ࡨࡲࠬᜱ"): os.environ.get(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭ᜲ"), bstack11111l_opy_ (u"ࠪࠫᜳ"))
    }
    bstack1l1lll1ll1l_opy_ = bstack1ll11ll1l1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack1l1l1lllll_opy_.value)
    logger.debug(bstack11111l_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡢࡸ࡬ࡲ࡬ࠦࡲࡦࡵࡸࡰࡹࡹ᜴ࠧ"))
    try:
      if (bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠬ࡯ࡳࡂࡲࡳࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ᜵"), None) and bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"࠭ࡡࡱࡲࡄ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᜶"), None)):
        scripts = {bstack11111l_opy_ (u"ࠧࡴࡥࡤࡲࠬ᜷"): bstack11ll11111_opy_.perform_scan}
        bstack11l1lllll11_opy_ = json.loads(scripts[bstack11111l_opy_ (u"ࠣࡵࡦࡥࡳࠨ᜸")].replace(bstack11111l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧ᜹"), bstack11111l_opy_ (u"ࠥࠦ᜺")))
        bstack11l1lllll11_opy_[bstack11111l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ᜻")][bstack11111l_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬ᜼")] = None
        scripts[bstack11111l_opy_ (u"ࠨࡳࡤࡣࡱࠦ᜽")] = bstack11111l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࠥ᜾") + json.dumps(bstack11l1lllll11_opy_)
        bstack11ll11111_opy_.bstack1lllll1ll1_opy_(scripts)
        bstack11ll11111_opy_.store()
        logger.debug(driver.execute_script(bstack11ll11111_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack11ll11111_opy_.perform_scan, {bstack11111l_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࠣ᜿"): name}))
      bstack1ll11ll1l1_opy_.end(EVENTS.bstack1l1l1lllll_opy_.value, bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᝀ"), bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᝁ"), True, None)
    except Exception as error:
      bstack1ll11ll1l1_opy_.end(EVENTS.bstack1l1l1lllll_opy_.value, bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᝂ"), bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᝃ"), False, str(error))
    bstack1l1lll1ll1l_opy_ = bstack1ll11ll1l1_opy_.bstack11ll1111lll_opy_(EVENTS.bstack1ll111l1111_opy_.value)
    bstack1ll11ll1l1_opy_.mark(bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᝄ"))
    try:
      if (bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧᝅ"), None) and bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᝆ"), None)):
        scripts = {bstack11111l_opy_ (u"ࠩࡶࡧࡦࡴࠧᝇ"): bstack11ll11111_opy_.perform_scan}
        bstack11l1lllll11_opy_ = json.loads(scripts[bstack11111l_opy_ (u"ࠥࡷࡨࡧ࡮ࠣᝈ")].replace(bstack11111l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࠢᝉ"), bstack11111l_opy_ (u"ࠧࠨᝊ")))
        bstack11l1lllll11_opy_[bstack11111l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩᝋ")][bstack11111l_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪࠧᝌ")] = None
        scripts[bstack11111l_opy_ (u"ࠣࡵࡦࡥࡳࠨᝍ")] = bstack11111l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧᝎ") + json.dumps(bstack11l1lllll11_opy_)
        bstack11ll11111_opy_.bstack1lllll1ll1_opy_(scripts)
        bstack11ll11111_opy_.store()
        logger.debug(driver.execute_script(bstack11ll11111_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack11ll11111_opy_.bstack11ll1l111l1_opy_, bstack1ll11111lll_opy_))
      bstack1ll11ll1l1_opy_.end(bstack1l1lll1ll1l_opy_, bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᝏ"), bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᝐ"),True, None)
    except Exception as error:
      bstack1ll11ll1l1_opy_.end(bstack1l1lll1ll1l_opy_, bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᝑ"), bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᝒ"),False, str(error))
    logger.info(bstack11111l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠥᝓ"))
  except Exception as bstack1ll1111l111_opy_:
    logger.error(bstack11111l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥ࠻ࠢࠥ᝔") + str(path) + bstack11111l_opy_ (u"ࠤࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠦ᝕") + str(bstack1ll1111l111_opy_))
def bstack11ll11ll11l_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack11111l_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ᝖")) and str(caps.get(bstack11111l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥ᝗"))).lower() == bstack11111l_opy_ (u"ࠧࡧ࡮ࡥࡴࡲ࡭ࡩࠨ᝘"):
        bstack1l1llllll11_opy_ = caps.get(bstack11111l_opy_ (u"ࠨࡡࡱࡲ࡬ࡹࡲࡀࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣ᝙")) or caps.get(bstack11111l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤ᝚"))
        if bstack1l1llllll11_opy_ and int(str(bstack1l1llllll11_opy_)) < bstack11ll11111l1_opy_:
            return False
    return True
def bstack111lll1l1_opy_(config):
  if bstack11111l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ᝛") in config:
        return config[bstack11111l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ᝜")]
  for platform in config.get(bstack11111l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭᝝"), []):
      if bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ᝞") in platform:
          return platform[bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ᝟")]
  return None
def bstack1lll1l111l_opy_(bstack1ll11lll_opy_):
  try:
    browser_name = bstack1ll11lll_opy_[bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟࡯ࡣࡰࡩࠬᝠ")]
    browser_version = bstack1ll11lll_opy_[bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᝡ")]
    chrome_options = bstack1ll11lll_opy_[bstack11111l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩᝢ")]
    try:
        bstack11ll11ll1ll_opy_ = int(browser_version.split(bstack11111l_opy_ (u"ࠩ࠱ࠫᝣ"))[0])
    except ValueError as e:
        logger.error(bstack11111l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡥࡲࡲࡻ࡫ࡲࡵ࡫ࡱ࡫ࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠢᝤ") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack11111l_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫᝥ")):
        logger.warning(bstack11111l_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣᝦ"))
        return False
    if bstack11ll11ll1ll_opy_ < bstack11ll11ll1l1_opy_.bstack1ll1111l11l_opy_:
        logger.warning(bstack1ll1lll1l1l_opy_ (u"࠭ࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡶࡪࡷࡵࡪࡴࡨࡷࠥࡉࡨࡳࡱࡰࡩࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡻࡄࡑࡑࡗ࡙ࡇࡎࡕࡕ࠱ࡑࡎࡔࡉࡎࡗࡐࡣࡓࡕࡎࡠࡄࡖࡘࡆࡉࡋࡠࡋࡑࡊࡗࡇ࡟ࡂ࠳࠴࡝ࡤ࡙ࡕࡑࡒࡒࡖ࡙ࡋࡄࡠࡅࡋࡖࡔࡓࡅࡠࡘࡈࡖࡘࡏࡏࡏࡿࠣࡳࡷࠦࡨࡪࡩ࡫ࡩࡷ࠴ࠧᝧ"))
        return False
    if chrome_options and any(bstack11111l_opy_ (u"ࠧ࠮࠯࡫ࡩࡦࡪ࡬ࡦࡵࡶࠫᝨ") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack11111l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡲࡴࡺࠠࡳࡷࡱࠤࡴࡴࠠ࡭ࡧࡪࡥࡨࡿࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠡࡕࡺ࡭ࡹࡩࡨࠡࡶࡲࠤࡳ࡫ࡷࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥࠡࡱࡵࠤࡦࡼ࡯ࡪࡦࠣࡹࡸ࡯࡮ࡨࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠥᝩ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack11111l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡨ࡮ࡥࡤ࡭࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡵࡸࡴࡵࡵࡲࡵࠢࡩࡳࡷࠦ࡬ࡰࡥࡤࡰࠥࡉࡨࡳࡱࡰࡩ࠿ࠦࠢᝪ") + str(e))
    return False
def bstack11ll111111_opy_(bstack1l1lll11l1_opy_, config):
    try:
      bstack1ll111l111l_opy_ = bstack11111l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᝫ") in config and config[bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᝬ")] == True
      bstack11ll111l1l1_opy_ = bstack11111l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ᝭") in config and str(config[bstack11111l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪᝮ")]).lower() != bstack11111l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ᝯ")
      if not (bstack1ll111l111l_opy_ and (not bstack1l1ll11l1l_opy_(config) or bstack11ll111l1l1_opy_)):
        return bstack1l1lll11l1_opy_
      bstack11ll1l1111l_opy_ = bstack11ll11111_opy_.bstack11ll111l111_opy_
      if bstack11ll1l1111l_opy_ is None:
        logger.debug(bstack11111l_opy_ (u"ࠣࡉࡲࡳ࡬ࡲࡥࠡࡥ࡫ࡶࡴࡳࡥࠡࡱࡳࡸ࡮ࡵ࡮ࡴࠢࡤࡶࡪࠦࡎࡰࡰࡨࠦᝰ"))
        return bstack1l1lll11l1_opy_
      bstack11ll1111111_opy_ = int(str(bstack11ll1111l11_opy_()).split(bstack11111l_opy_ (u"ࠩ࠱ࠫ᝱"))[0])
      logger.debug(bstack11111l_opy_ (u"ࠥࡗࡪࡲࡥ࡯࡫ࡸࡱࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡤࡦࡶࡨࡧࡹ࡫ࡤ࠻ࠢࠥᝲ") + str(bstack11ll1111111_opy_) + bstack11111l_opy_ (u"ࠦࠧᝳ"))
      if bstack11ll1111111_opy_ == 3 and isinstance(bstack1l1lll11l1_opy_, dict) and bstack11111l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ᝴") in bstack1l1lll11l1_opy_ and bstack11ll1l1111l_opy_ is not None:
        if bstack11111l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ᝵") not in bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᝶")]:
          bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ᝷")][bstack11111l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᝸")] = {}
        if bstack11111l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ᝹") in bstack11ll1l1111l_opy_:
          if bstack11111l_opy_ (u"ࠫࡦࡸࡧࡴࠩ᝺") not in bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ᝻")][bstack11111l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ᝼")]:
            bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᝽")][bstack11111l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᝾")][bstack11111l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ᝿")] = []
          for arg in bstack11ll1l1111l_opy_[bstack11111l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨក")]:
            if arg not in bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫខ")][bstack11111l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪគ")][bstack11111l_opy_ (u"࠭ࡡࡳࡩࡶࠫឃ")]:
              bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧង")][bstack11111l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ច")][bstack11111l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧឆ")].append(arg)
        if bstack11111l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧជ") in bstack11ll1l1111l_opy_:
          if bstack11111l_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨឈ") not in bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬញ")][bstack11111l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫដ")]:
            bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧឋ")][bstack11111l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ឌ")][bstack11111l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ឍ")] = []
          for ext in bstack11ll1l1111l_opy_[bstack11111l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧណ")]:
            if ext not in bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫត")][bstack11111l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪថ")][bstack11111l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪទ")]:
              bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧធ")][bstack11111l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ន")][bstack11111l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ប")].append(ext)
        if bstack11111l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩផ") in bstack11ll1l1111l_opy_:
          if bstack11111l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪព") not in bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬភ")][bstack11111l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫម")]:
            bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧយ")][bstack11111l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭រ")][bstack11111l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨល")] = {}
          bstack11ll1l11l11_opy_(bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪវ")][bstack11111l_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩឝ")][bstack11111l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫឞ")],
                    bstack11ll1l1111l_opy_[bstack11111l_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬស")])
        os.environ[bstack11111l_opy_ (u"ࠧࡊࡕࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘࡋࡓࡔࡋࡒࡒࠬហ")] = bstack11111l_opy_ (u"ࠨࡶࡵࡹࡪ࠭ឡ")
        return bstack1l1lll11l1_opy_
      else:
        chrome_options = None
        if isinstance(bstack1l1lll11l1_opy_, ChromeOptions):
          chrome_options = bstack1l1lll11l1_opy_
        elif isinstance(bstack1l1lll11l1_opy_, dict):
          for value in bstack1l1lll11l1_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1l1lll11l1_opy_, dict):
            bstack1l1lll11l1_opy_[bstack11111l_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪអ")] = chrome_options
          else:
            bstack1l1lll11l1_opy_ = chrome_options
        if bstack11ll1l1111l_opy_ is not None:
          if bstack11111l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨឣ") in bstack11ll1l1111l_opy_:
                bstack11l1lllll1l_opy_ = chrome_options.arguments or []
                new_args = bstack11ll1l1111l_opy_[bstack11111l_opy_ (u"ࠫࡦࡸࡧࡴࠩឤ")]
                for arg in new_args:
                    if arg not in bstack11l1lllll1l_opy_:
                        chrome_options.add_argument(arg)
          if bstack11111l_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩឥ") in bstack11ll1l1111l_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack11111l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪឦ"), [])
                bstack11ll11lll11_opy_ = bstack11ll1l1111l_opy_[bstack11111l_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫឧ")]
                for extension in bstack11ll11lll11_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack11111l_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧឨ") in bstack11ll1l1111l_opy_:
                bstack11ll11l1lll_opy_ = chrome_options.experimental_options.get(bstack11111l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨឩ"), {})
                bstack11ll1111l1l_opy_ = bstack11ll1l1111l_opy_[bstack11111l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩឪ")]
                bstack11ll1l11l11_opy_(bstack11ll11l1lll_opy_, bstack11ll1111l1l_opy_)
                chrome_options.add_experimental_option(bstack11111l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪឫ"), bstack11ll11l1lll_opy_)
        os.environ[bstack11111l_opy_ (u"ࠬࡏࡓࡠࡐࡒࡒࡤࡈࡓࡕࡃࡆࡏࡤࡏࡎࡇࡔࡄࡣࡆ࠷࠱࡚ࡡࡖࡉࡘ࡙ࡉࡐࡐࠪឬ")] = bstack11111l_opy_ (u"࠭ࡴࡳࡷࡨࠫឭ")
        return bstack1l1lll11l1_opy_
    except Exception as e:
      logger.error(bstack11111l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡧࡤࡥ࡫ࡱ࡫ࠥࡴ࡯࡯࠯ࡅࡗࠥ࡯࡮ࡧࡴࡤࠤࡦ࠷࠱ࡺࠢࡦ࡬ࡷࡵ࡭ࡦࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࠧឮ") + str(e))
      return bstack1l1lll11l1_opy_