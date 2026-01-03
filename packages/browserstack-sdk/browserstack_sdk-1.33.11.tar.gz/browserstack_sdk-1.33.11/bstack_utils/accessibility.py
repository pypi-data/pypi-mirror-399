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
import requests
import logging
import threading
import bstack_utils.constants as bstack11l1lllll1l_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll11l11ll_opy_ as bstack11ll11l1lll_opy_, EVENTS
from bstack_utils.bstack111111lll_opy_ import bstack111111lll_opy_
from bstack_utils.helper import bstack1111lllll_opy_, bstack1111llll11_opy_, bstack1l11ll1l11_opy_, bstack11ll1l111l1_opy_, \
  bstack11ll1l11111_opy_, bstack1l1lll1l_opy_, get_host_info, bstack11ll11lllll_opy_, bstack11l11llll_opy_, error_handler, bstack11ll1111l1l_opy_, bstack11ll11l11l1_opy_, bstack11llll11ll_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
logger = get_logger(__name__)
bstack1ll111ll11_opy_ = bstack1ll1l1ll111_opy_()
@error_handler(class_method=False)
def _11ll1l1111l_opy_(driver, bstack1lllllll11l_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack1l1l_opy_ (u"࠭࡯ࡴࡡࡱࡥࡲ࡫ࠧ "): caps.get(bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭ᚁ"), None),
        bstack1l1l_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᚂ"): bstack1lllllll11l_opy_.get(bstack1l1l_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᚃ"), None),
        bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩᚄ"): caps.get(bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᚅ"), None),
        bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᚆ"): caps.get(bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᚇ"), None)
    }
  except Exception as error:
    logger.debug(bstack1l1l_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲࠡ࠼ࠣࠫᚈ") + str(error))
  return response
def on():
    if os.environ.get(bstack1l1l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᚉ"), None) is None or os.environ[bstack1l1l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᚊ")] == bstack1l1l_opy_ (u"ࠥࡲࡺࡲ࡬ࠣᚋ"):
        return False
    return True
def bstack1ll1lll1l_opy_(config):
  return config.get(bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚌ"), False) or any([p.get(bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᚍ"), False) == True for p in config.get(bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᚎ"), [])])
def bstack1l1l11l1ll_opy_(config, bstack1111lll1l_opy_):
  try:
    bstack11l1llll1ll_opy_ = config.get(bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᚏ"), False)
    if int(bstack1111lll1l_opy_) < len(config.get(bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᚐ"), [])) and config[bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᚑ")][bstack1111lll1l_opy_]:
      bstack11ll111ll11_opy_ = config[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᚒ")][bstack1111lll1l_opy_].get(bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚓ"), None)
    else:
      bstack11ll111ll11_opy_ = config.get(bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᚔ"), None)
    if bstack11ll111ll11_opy_ != None:
      bstack11l1llll1ll_opy_ = bstack11ll111ll11_opy_
    bstack11ll11l1ll1_opy_ = os.getenv(bstack1l1l_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᚕ")) is not None and len(os.getenv(bstack1l1l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᚖ"))) > 0 and os.getenv(bstack1l1l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᚗ")) != bstack1l1l_opy_ (u"ࠩࡱࡹࡱࡲࠧᚘ")
    return bstack11l1llll1ll_opy_ and bstack11ll11l1ll1_opy_
  except Exception as error:
    logger.debug(bstack1l1l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡹࡩࡷ࡯ࡦࡺ࡫ࡱ࡫ࠥࡺࡨࡦࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡩࡸࡹࡩࡰࡰࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠ࠻ࠢࠪᚙ") + str(error))
  return False
def bstack1l111lll_opy_(test_tags):
  bstack1ll1111l1l1_opy_ = os.getenv(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᚚ"))
  if bstack1ll1111l1l1_opy_ is None:
    return True
  bstack1ll1111l1l1_opy_ = json.loads(bstack1ll1111l1l1_opy_)
  try:
    include_tags = bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪ᚛")] if bstack1l1l_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫ᚜") in bstack1ll1111l1l1_opy_ and isinstance(bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ᚝")], list) else []
    exclude_tags = bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭᚞")] if bstack1l1l_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ᚟") in bstack1ll1111l1l1_opy_ and isinstance(bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᚠ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡹࡥࡱ࡯ࡤࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡩࡳࡷࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡢࡦࡨࡲࡶࡪࠦࡳࡤࡣࡱࡲ࡮ࡴࡧ࠯ࠢࡈࡶࡷࡵࡲࠡ࠼ࠣࠦᚡ") + str(error))
  return False
def bstack11ll111l1ll_opy_(config, bstack11ll11ll111_opy_, bstack11ll11ll1ll_opy_, bstack11ll1111lll_opy_):
  bstack11ll111l1l1_opy_ = bstack11ll1l111l1_opy_(config)
  bstack11ll111l111_opy_ = bstack11ll1l11111_opy_(config)
  if bstack11ll111l1l1_opy_ is None or bstack11ll111l111_opy_ is None:
    logger.error(bstack1l1l_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡳࡷࡱࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠾ࠥࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡡࡶࡶ࡫ࡩࡳࡺࡩࡤࡣࡷ࡭ࡴࡴࠠࡵࡱ࡮ࡩࡳ࠭ᚢ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᚣ"), bstack1l1l_opy_ (u"ࠧࡼࡿࠪᚤ")))
    data = {
        bstack1l1l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᚥ"): config[bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᚦ")],
        bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ᚧ"): config.get(bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᚨ"), os.path.basename(os.getcwd())),
        bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡘ࡮ࡳࡥࠨᚩ"): bstack1111lllll_opy_(),
        bstack1l1l_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫᚪ"): config.get(bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᚫ"), bstack1l1l_opy_ (u"ࠨࠩᚬ")),
        bstack1l1l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩᚭ"): {
            bstack1l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡔࡡ࡮ࡧࠪᚮ"): bstack11ll11ll111_opy_,
            bstack1l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧᚯ"): bstack11ll11ll1ll_opy_,
            bstack1l1l_opy_ (u"ࠬࡹࡤ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩᚰ"): __version__,
            bstack1l1l_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨᚱ"): bstack1l1l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧᚲ"),
            bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᚳ"): bstack1l1l_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࠫᚴ"),
            bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪᚵ"): bstack11ll1111lll_opy_
        },
        bstack1l1l_opy_ (u"ࠫࡸ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭ᚶ"): settings,
        bstack1l1l_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳࡉ࡯࡯ࡶࡵࡳࡱ࠭ᚷ"): bstack11ll11lllll_opy_(),
        bstack1l1l_opy_ (u"࠭ࡣࡪࡋࡱࡪࡴ࠭ᚸ"): bstack1l1lll1l_opy_(),
        bstack1l1l_opy_ (u"ࠧࡩࡱࡶࡸࡎࡴࡦࡰࠩᚹ"): get_host_info(),
        bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᚺ"): bstack1l11ll1l11_opy_(config)
    }
    headers = {
        bstack1l1l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨᚻ"): bstack1l1l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ᚼ"),
    }
    config = {
        bstack1l1l_opy_ (u"ࠫࡦࡻࡴࡩࠩᚽ"): (bstack11ll111l1l1_opy_, bstack11ll111l111_opy_),
        bstack1l1l_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭ᚾ"): headers
    }
    response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"࠭ࡐࡐࡕࡗࠫᚿ"), bstack11ll11l1lll_opy_ + bstack1l1l_opy_ (u"ࠧ࠰ࡸ࠵࠳ࡹ࡫ࡳࡵࡡࡵࡹࡳࡹࠧᛀ"), data, config)
    bstack11ll1111l11_opy_ = response.json()
    if bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᛁ")]:
      parsed = json.loads(os.getenv(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᛂ"), bstack1l1l_opy_ (u"ࠪࡿࢂ࠭ᛃ")))
      parsed[bstack1l1l_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᛄ")] = bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠬࡪࡡࡵࡣࠪᛅ")][bstack1l1l_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᛆ")]
      os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨᛇ")] = json.dumps(parsed)
      bstack111111lll_opy_.bstack11l1l1l11_opy_(bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠨࡦࡤࡸࡦ࠭ᛈ")][bstack1l1l_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪᛉ")])
      bstack111111lll_opy_.bstack11ll11llll1_opy_(bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠪࡨࡦࡺࡡࠨᛊ")][bstack1l1l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭ᛋ")])
      bstack111111lll_opy_.store()
      return bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠬࡪࡡࡵࡣࠪᛌ")][bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࡚࡯࡬ࡧࡱࠫᛍ")], bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠧࡥࡣࡷࡥࠬᛎ")][bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫᛏ")]
    else:
      logger.error(bstack1l1l_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡷࡻ࡮࡯࡫ࡱ࡫ࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠻ࠢࠪᛐ") + bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᛑ")])
      if bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᛒ")] == bstack1l1l_opy_ (u"ࠬࡏ࡮ࡷࡣ࡯࡭ࡩࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡰࡢࡵࡶࡩࡩ࠴ࠧᛓ"):
        for bstack11ll111lll1_opy_ in bstack11ll1111l11_opy_[bstack1l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࡸ࠭ᛔ")]:
          logger.error(bstack11ll111lll1_opy_[bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᛕ")])
      return None, None
  except Exception as error:
    logger.error(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡶࡺࡴࠠࡧࡱࡵࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠺ࠡࠤᛖ") +  str(error))
    return None, None
def bstack11ll11l1l11_opy_():
  if os.getenv(bstack1l1l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᛗ")) is None:
    return {
        bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪᛘ"): bstack1l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᛙ"),
        bstack1l1l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᛚ"): bstack1l1l_opy_ (u"࠭ࡂࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠࡩࡣࡧࠤ࡫ࡧࡩ࡭ࡧࡧ࠲ࠬᛛ")
    }
  data = {bstack1l1l_opy_ (u"ࠧࡦࡰࡧࡘ࡮ࡳࡥࠨᛜ"): bstack1111lllll_opy_()}
  headers = {
      bstack1l1l_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨᛝ"): bstack1l1l_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࠪᛞ") + os.getenv(bstack1l1l_opy_ (u"ࠥࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠣᛟ")),
      bstack1l1l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪᛠ"): bstack1l1l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨᛡ")
  }
  response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"࠭ࡐࡖࡖࠪᛢ"), bstack11ll11l1lll_opy_ + bstack1l1l_opy_ (u"ࠧ࠰ࡶࡨࡷࡹࡥࡲࡶࡰࡶ࠳ࡸࡺ࡯ࡱࠩᛣ"), data, { bstack1l1l_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡴࠩᛤ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack1l1l_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࡚ࠥࡥࡴࡶࠣࡖࡺࡴࠠ࡮ࡣࡵ࡯ࡪࡪࠠࡢࡵࠣࡧࡴࡳࡰ࡭ࡧࡷࡩࡩࠦࡡࡵࠢࠥᛥ") + bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠪ࡞ࠬᛦ"))
      return {bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᛧ"): bstack1l1l_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ᛨ"), bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᛩ"): bstack1l1l_opy_ (u"ࠧࠨᛪ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡨࡵ࡭ࡱ࡮ࡨࡸ࡮ࡵ࡮ࠡࡱࡩࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡕࡧࡶࡸࠥࡘࡵ࡯࠼ࠣࠦ᛫") + str(error))
    return {
        bstack1l1l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ᛬"): bstack1l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ᛭"),
        bstack1l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᛮ"): str(error)
    }
def bstack11ll1l111ll_opy_(bstack11ll111l11l_opy_):
    return re.match(bstack1l1l_opy_ (u"ࡷ࠭࡞࡝ࡦ࠮ࠬࡡ࠴࡜ࡥ࠭ࠬࡃࠩ࠭ᛯ"), bstack11ll111l11l_opy_.strip()) is not None
def bstack1111ll1l_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11ll111111l_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11ll111111l_opy_ = desired_capabilities
        else:
          bstack11ll111111l_opy_ = {}
        bstack1l1llllllll_opy_ = (bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᛰ"), bstack1l1l_opy_ (u"ࠧࠨᛱ")).lower() or caps.get(bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧᛲ"), bstack1l1l_opy_ (u"ࠩࠪᛳ")).lower())
        if bstack1l1llllllll_opy_ == bstack1l1l_opy_ (u"ࠪ࡭ࡴࡹࠧᛴ"):
            return True
        if bstack1l1llllllll_opy_ == bstack1l1l_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࠬᛵ"):
            bstack1ll111l11ll_opy_ = str(float(caps.get(bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧᛶ")) or bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᛷ"), {}).get(bstack1l1l_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪᛸ"),bstack1l1l_opy_ (u"ࠨࠩ᛹"))))
            if bstack1l1llllllll_opy_ == bstack1l1l_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࠪ᛺") and int(bstack1ll111l11ll_opy_.split(bstack1l1l_opy_ (u"ࠪ࠲ࠬ᛻"))[0]) < float(bstack11ll11l1111_opy_):
                logger.warning(str(bstack11l1llll11l_opy_))
                return False
            return True
        bstack1l1lll1ll1l_opy_ = caps.get(bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ᛼"), {}).get(bstack1l1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩ᛽"), caps.get(bstack1l1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭᛾"), bstack1l1l_opy_ (u"ࠧࠨ᛿")))
        if bstack1l1lll1ll1l_opy_:
            logger.warning(bstack1l1l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡆࡨࡷࡰࡺ࡯ࡱࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧᜀ"))
            return False
        browser = caps.get(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᜁ"), bstack1l1l_opy_ (u"ࠪࠫᜂ")).lower() or bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᜃ"), bstack1l1l_opy_ (u"ࠬ࠭ᜄ")).lower()
        if browser != bstack1l1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ᜅ"):
            logger.warning(bstack1l1l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥᜆ"))
            return False
        browser_version = caps.get(bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᜇ")) or caps.get(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫᜈ")) or bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᜉ")) or bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᜊ"), {}).get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᜋ")) or bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᜌ"), {}).get(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᜍ"))
        bstack1ll11111lll_opy_ = bstack11l1lllll1l_opy_.bstack1ll1111llll_opy_
        bstack11l1llllll1_opy_ = False
        if config is not None:
          bstack11l1llllll1_opy_ = bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᜎ") in config and str(config[bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ᜏ")]).lower() != bstack1l1l_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩᜐ")
        if os.environ.get(bstack1l1l_opy_ (u"ࠫࡎ࡙࡟ࡏࡑࡑࡣࡇ࡙ࡔࡂࡅࡎࡣࡎࡔࡆࡓࡃࡢࡅ࠶࠷࡙ࡠࡕࡈࡗࡘࡏࡏࡏࠩᜑ"), bstack1l1l_opy_ (u"ࠬ࠭ᜒ")).lower() == bstack1l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫᜓ") or bstack11l1llllll1_opy_:
          bstack1ll11111lll_opy_ = bstack11l1lllll1l_opy_.bstack1ll111ll1l1_opy_
        if browser_version and browser_version != bstack1l1l_opy_ (u"ࠧ࡭ࡣࡷࡩࡸࡺ᜔ࠧ") and int(browser_version.split(bstack1l1l_opy_ (u"ࠨ࠰᜕ࠪ"))[0]) <= bstack1ll11111lll_opy_:
          logger.warning(bstack1lll1l111ll_opy_ (u"ࠩࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡺࡪࡸࡳࡪࡱࡱࠤ࡬ࡸࡥࡢࡶࡨࡶࠥࡺࡨࡢࡰࠣࡿࡲ࡯࡮ࡠࡣ࠴࠵ࡾࡥࡳࡶࡲࡳࡳࡷࡺࡥࡥࡡࡦ࡬ࡷࡵ࡭ࡦࡡࡹࡩࡷࡹࡩࡰࡰࢀ࠲ࠬ᜖"))
          return False
        if not options:
          bstack1l1lllll111_opy_ = caps.get(bstack1l1l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ᜗")) or bstack11ll111111l_opy_.get(bstack1l1l_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᜘"), {})
          if bstack1l1l_opy_ (u"ࠬ࠳࠭ࡩࡧࡤࡨࡱ࡫ࡳࡴࠩ᜙") in bstack1l1lllll111_opy_.get(bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫ᜚"), []):
              logger.warning(bstack1l1l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡱࡳࡹࠦࡲࡶࡰࠣࡳࡳࠦ࡬ࡦࡩࡤࡧࡾࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠠࡔࡹ࡬ࡸࡨ࡮ࠠࡵࡱࠣࡲࡪࡽࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫ࠠࡰࡴࠣࡥࡻࡵࡩࡥࠢࡸࡷ࡮ࡴࡧࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠤ᜛"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡷࡣ࡯࡭ࡩࡧࡴࡦࠢࡤ࠵࠶ࡿࠠࡴࡷࡳࡴࡴࡸࡴࠡ࠼ࠥ᜜") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1ll1lll1l11_opy_ = config.get(bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᜝"), {})
    bstack1ll1lll1l11_opy_[bstack1l1l_opy_ (u"ࠪࡥࡺࡺࡨࡕࡱ࡮ࡩࡳ࠭᜞")] = os.getenv(bstack1l1l_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᜟ"))
    bstack11ll11ll11l_opy_ = json.loads(os.getenv(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ᜠ"), bstack1l1l_opy_ (u"࠭ࡻࡾࠩᜡ"))).get(bstack1l1l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᜢ"))
    if not config[bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᜣ")].get(bstack1l1l_opy_ (u"ࠤࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠣᜤ")):
      if bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᜥ") in caps:
        caps[bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᜦ")][bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᜧ")] = bstack1ll1lll1l11_opy_
        caps[bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᜨ")][bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᜩ")][bstack1l1l_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᜪ")] = bstack11ll11ll11l_opy_
      else:
        caps[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᜫ")] = bstack1ll1lll1l11_opy_
        caps[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᜬ")][bstack1l1l_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᜭ")] = bstack11ll11ll11l_opy_
  except Exception as error:
    logger.debug(bstack1l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶ࠲ࠥࡋࡲࡳࡱࡵ࠾ࠥࠨᜮ") +  str(error))
def bstack1l1111111l_opy_(driver, bstack11ll11111l1_opy_):
  try:
    setattr(driver, bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭ᜯ"), True)
    session = driver.session_id
    if session:
      bstack11l1llll1l1_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11l1llll1l1_opy_ = False
      bstack11l1llll1l1_opy_ = url.scheme in [bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴࠧᜰ"), bstack1l1l_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᜱ")]
      if bstack11l1llll1l1_opy_:
        if bstack11ll11111l1_opy_:
          logger.info(bstack1l1l_opy_ (u"ࠤࡖࡩࡹࡻࡰࠡࡨࡲࡶࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡨࡢࡵࠣࡷࡹࡧࡲࡵࡧࡧ࠲ࠥࡇࡵࡵࡱࡰࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡧ࡫ࡧࡪࡰࠣࡱࡴࡳࡥ࡯ࡶࡤࡶ࡮ࡲࡹ࠯ࠤᜲ"))
      return bstack11ll11111l1_opy_
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡦࡸࡴࡪࡰࡪࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡦࡥࡳࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨ࠾ࠥࠨᜳ") + str(e))
    return False
def bstack11llll1ll_opy_(driver, name, path):
  try:
    bstack1l1llll1lll_opy_ = {
        bstack1l1l_opy_ (u"ࠫࡹ࡮ࡔࡦࡵࡷࡖࡺࡴࡕࡶ࡫ࡧ᜴ࠫ"): threading.current_thread().current_test_uuid,
        bstack1l1l_opy_ (u"ࠬࡺࡨࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪ᜵"): os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ᜶"), bstack1l1l_opy_ (u"ࠧࠨ᜷")),
        bstack1l1l_opy_ (u"ࠨࡶ࡫ࡎࡼࡺࡔࡰ࡭ࡨࡲࠬ᜸"): os.environ.get(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭᜹"), bstack1l1l_opy_ (u"ࠪࠫ᜺"))
    }
    bstack1ll11l111l1_opy_ = bstack1ll111ll11_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1lll11l111_opy_.value)
    logger.debug(bstack1l1l_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡢࡸ࡬ࡲ࡬ࠦࡲࡦࡵࡸࡰࡹࡹࠧ᜻"))
    try:
      if (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬ࡯ࡳࡂࡲࡳࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ᜼"), None) and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡡࡱࡲࡄ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᜽"), None)):
        scripts = {bstack1l1l_opy_ (u"ࠧࡴࡥࡤࡲࠬ᜾"): bstack111111lll_opy_.perform_scan}
        bstack11ll11111ll_opy_ = json.loads(scripts[bstack1l1l_opy_ (u"ࠣࡵࡦࡥࡳࠨ᜿")].replace(bstack1l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧᝀ"), bstack1l1l_opy_ (u"ࠥࠦᝁ")))
        bstack11ll11111ll_opy_[bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᝂ")][bstack1l1l_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬᝃ")] = None
        scripts[bstack1l1l_opy_ (u"ࠨࡳࡤࡣࡱࠦᝄ")] = bstack1l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࠥᝅ") + json.dumps(bstack11ll11111ll_opy_)
        bstack111111lll_opy_.bstack11l1l1l11_opy_(scripts)
        bstack111111lll_opy_.store()
        logger.debug(driver.execute_script(bstack111111lll_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack111111lll_opy_.perform_scan, {bstack1l1l_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࠣᝆ"): name}))
      bstack1ll111ll11_opy_.end(EVENTS.bstack1lll11l111_opy_.value, bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᝇ"), bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᝈ"), True, None)
    except Exception as error:
      bstack1ll111ll11_opy_.end(EVENTS.bstack1lll11l111_opy_.value, bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᝉ"), bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᝊ"), False, str(error))
    bstack1ll11l111l1_opy_ = bstack1ll111ll11_opy_.bstack11l1lllllll_opy_(EVENTS.bstack1ll11111l1l_opy_.value)
    bstack1ll111ll11_opy_.mark(bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᝋ"))
    try:
      if (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧᝌ"), None) and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᝍ"), None)):
        scripts = {bstack1l1l_opy_ (u"ࠩࡶࡧࡦࡴࠧᝎ"): bstack111111lll_opy_.perform_scan}
        bstack11ll11111ll_opy_ = json.loads(scripts[bstack1l1l_opy_ (u"ࠥࡷࡨࡧ࡮ࠣᝏ")].replace(bstack1l1l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࠢᝐ"), bstack1l1l_opy_ (u"ࠧࠨᝑ")))
        bstack11ll11111ll_opy_[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩᝒ")][bstack1l1l_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪࠧᝓ")] = None
        scripts[bstack1l1l_opy_ (u"ࠣࡵࡦࡥࡳࠨ᝔")] = bstack1l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧ᝕") + json.dumps(bstack11ll11111ll_opy_)
        bstack111111lll_opy_.bstack11l1l1l11_opy_(scripts)
        bstack111111lll_opy_.store()
        logger.debug(driver.execute_script(bstack111111lll_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack111111lll_opy_.bstack11ll11l1l1l_opy_, bstack1l1llll1lll_opy_))
      bstack1ll111ll11_opy_.end(bstack1ll11l111l1_opy_, bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥ᝖"), bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠦ࠿࡫࡮ࡥࠤ᝗"),True, None)
    except Exception as error:
      bstack1ll111ll11_opy_.end(bstack1ll11l111l1_opy_, bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ᝘"), bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ᝙"),False, str(error))
    logger.info(bstack1l1l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠥ᝚"))
  except Exception as bstack1l1lllll1ll_opy_:
    logger.error(bstack1l1l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥ࠻ࠢࠥ᝛") + str(path) + bstack1l1l_opy_ (u"ࠤࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠦ᝜") + str(bstack1l1lllll1ll_opy_))
def bstack11ll1111ll1_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack1l1l_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ᝝")) and str(caps.get(bstack1l1l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥ᝞"))).lower() == bstack1l1l_opy_ (u"ࠧࡧ࡮ࡥࡴࡲ࡭ࡩࠨ᝟"):
        bstack1ll111l11ll_opy_ = caps.get(bstack1l1l_opy_ (u"ࠨࡡࡱࡲ࡬ࡹࡲࡀࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣᝠ")) or caps.get(bstack1l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤᝡ"))
        if bstack1ll111l11ll_opy_ and int(str(bstack1ll111l11ll_opy_)) < bstack11ll11l1111_opy_:
            return False
    return True
def bstack1l11llll_opy_(config):
  if bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᝢ") in config:
        return config[bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᝣ")]
  for platform in config.get(bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᝤ"), []):
      if bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᝥ") in platform:
          return platform[bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᝦ")]
  return None
def bstack1lll11l1l_opy_(bstack1l1lll1lll_opy_):
  try:
    browser_name = bstack1l1lll1lll_opy_[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟࡯ࡣࡰࡩࠬᝧ")]
    browser_version = bstack1l1lll1lll_opy_[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᝨ")]
    chrome_options = bstack1l1lll1lll_opy_[bstack1l1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩᝩ")]
    try:
        bstack11ll11ll1l1_opy_ = int(browser_version.split(bstack1l1l_opy_ (u"ࠩ࠱ࠫᝪ"))[0])
    except ValueError as e:
        logger.error(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡥࡲࡲࡻ࡫ࡲࡵ࡫ࡱ࡫ࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠢᝫ") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack1l1l_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫᝬ")):
        logger.warning(bstack1l1l_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣ᝭"))
        return False
    if bstack11ll11ll1l1_opy_ < bstack11l1lllll1l_opy_.bstack1ll111ll1l1_opy_:
        logger.warning(bstack1lll1l111ll_opy_ (u"࠭ࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡶࡪࡷࡵࡪࡴࡨࡷࠥࡉࡨࡳࡱࡰࡩࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡻࡄࡑࡑࡗ࡙ࡇࡎࡕࡕ࠱ࡑࡎࡔࡉࡎࡗࡐࡣࡓࡕࡎࡠࡄࡖࡘࡆࡉࡋࡠࡋࡑࡊࡗࡇ࡟ࡂ࠳࠴࡝ࡤ࡙ࡕࡑࡒࡒࡖ࡙ࡋࡄࡠࡅࡋࡖࡔࡓࡅࡠࡘࡈࡖࡘࡏࡏࡏࡿࠣࡳࡷࠦࡨࡪࡩ࡫ࡩࡷ࠴ࠧᝮ"))
        return False
    if chrome_options and any(bstack1l1l_opy_ (u"ࠧ࠮࠯࡫ࡩࡦࡪ࡬ࡦࡵࡶࠫᝯ") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack1l1l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡲࡴࡺࠠࡳࡷࡱࠤࡴࡴࠠ࡭ࡧࡪࡥࡨࡿࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠡࡕࡺ࡭ࡹࡩࡨࠡࡶࡲࠤࡳ࡫ࡷࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥࠡࡱࡵࠤࡦࡼ࡯ࡪࡦࠣࡹࡸ࡯࡮ࡨࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠥᝰ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡨ࡮ࡥࡤ࡭࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡵࡸࡴࡵࡵࡲࡵࠢࡩࡳࡷࠦ࡬ࡰࡥࡤࡰࠥࡉࡨࡳࡱࡰࡩ࠿ࠦࠢ᝱") + str(e))
    return False
def bstack11111lll_opy_(bstack1ll1lllll_opy_, config):
    try:
      bstack1ll111l1l11_opy_ = bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᝲ") in config and config[bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᝳ")] == True
      bstack11l1llllll1_opy_ = bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ᝴") in config and str(config[bstack1l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ᝵")]).lower() != bstack1l1l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭᝶")
      if not (bstack1ll111l1l11_opy_ and (not bstack1l11ll1l11_opy_(config) or bstack11l1llllll1_opy_)):
        return bstack1ll1lllll_opy_
      bstack11ll111ll1l_opy_ = bstack111111lll_opy_.bstack11l1lllll11_opy_
      if bstack11ll111ll1l_opy_ is None:
        logger.debug(bstack1l1l_opy_ (u"ࠣࡉࡲࡳ࡬ࡲࡥࠡࡥ࡫ࡶࡴࡳࡥࠡࡱࡳࡸ࡮ࡵ࡮ࡴࠢࡤࡶࡪࠦࡎࡰࡰࡨࠦ᝷"))
        return bstack1ll1lllll_opy_
      bstack11ll1111111_opy_ = int(str(bstack11ll11l11l1_opy_()).split(bstack1l1l_opy_ (u"ࠩ࠱ࠫ᝸"))[0])
      logger.debug(bstack1l1l_opy_ (u"ࠥࡗࡪࡲࡥ࡯࡫ࡸࡱࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡤࡦࡶࡨࡧࡹ࡫ࡤ࠻ࠢࠥ᝹") + str(bstack11ll1111111_opy_) + bstack1l1l_opy_ (u"ࠦࠧ᝺"))
      if bstack11ll1111111_opy_ == 3 and isinstance(bstack1ll1lllll_opy_, dict) and bstack1l1l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ᝻") in bstack1ll1lllll_opy_ and bstack11ll111ll1l_opy_ is not None:
        if bstack1l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ᝼") not in bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᝽")]:
          bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ᝾")][bstack1l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᝿")] = {}
        if bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨក") in bstack11ll111ll1l_opy_:
          if bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩខ") not in bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬគ")][bstack1l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫឃ")]:
            bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧង")][bstack1l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ច")][bstack1l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧឆ")] = []
          for arg in bstack11ll111ll1l_opy_[bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨជ")]:
            if arg not in bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫឈ")][bstack1l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪញ")][bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫដ")]:
              bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧឋ")][bstack1l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ឌ")][bstack1l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧឍ")].append(arg)
        if bstack1l1l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧណ") in bstack11ll111ll1l_opy_:
          if bstack1l1l_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨត") not in bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬថ")][bstack1l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫទ")]:
            bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧធ")][bstack1l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ន")][bstack1l1l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ប")] = []
          for ext in bstack11ll111ll1l_opy_[bstack1l1l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧផ")]:
            if ext not in bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫព")][bstack1l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪភ")][bstack1l1l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪម")]:
              bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧយ")][bstack1l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭រ")][bstack1l1l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ល")].append(ext)
        if bstack1l1l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩវ") in bstack11ll111ll1l_opy_:
          if bstack1l1l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪឝ") not in bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬឞ")][bstack1l1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫស")]:
            bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧហ")][bstack1l1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ឡ")][bstack1l1l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨអ")] = {}
          bstack11ll1111l1l_opy_(bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪឣ")][bstack1l1l_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩឤ")][bstack1l1l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫឥ")],
                    bstack11ll111ll1l_opy_[bstack1l1l_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬឦ")])
        os.environ[bstack1l1l_opy_ (u"ࠧࡊࡕࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘࡋࡓࡔࡋࡒࡒࠬឧ")] = bstack1l1l_opy_ (u"ࠨࡶࡵࡹࡪ࠭ឨ")
        return bstack1ll1lllll_opy_
      else:
        chrome_options = None
        if isinstance(bstack1ll1lllll_opy_, ChromeOptions):
          chrome_options = bstack1ll1lllll_opy_
        elif isinstance(bstack1ll1lllll_opy_, dict):
          for value in bstack1ll1lllll_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1ll1lllll_opy_, dict):
            bstack1ll1lllll_opy_[bstack1l1l_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪឩ")] = chrome_options
          else:
            bstack1ll1lllll_opy_ = chrome_options
        if bstack11ll111ll1l_opy_ is not None:
          if bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨឪ") in bstack11ll111ll1l_opy_:
                bstack11ll11lll11_opy_ = chrome_options.arguments or []
                new_args = bstack11ll111ll1l_opy_[bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩឫ")]
                for arg in new_args:
                    if arg not in bstack11ll11lll11_opy_:
                        chrome_options.add_argument(arg)
          if bstack1l1l_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩឬ") in bstack11ll111ll1l_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack1l1l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪឭ"), [])
                bstack11ll11l111l_opy_ = bstack11ll111ll1l_opy_[bstack1l1l_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫឮ")]
                for extension in bstack11ll11l111l_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack1l1l_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧឯ") in bstack11ll111ll1l_opy_:
                bstack11ll111llll_opy_ = chrome_options.experimental_options.get(bstack1l1l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨឰ"), {})
                bstack11ll11lll1l_opy_ = bstack11ll111ll1l_opy_[bstack1l1l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩឱ")]
                bstack11ll1111l1l_opy_(bstack11ll111llll_opy_, bstack11ll11lll1l_opy_)
                chrome_options.add_experimental_option(bstack1l1l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪឲ"), bstack11ll111llll_opy_)
        os.environ[bstack1l1l_opy_ (u"ࠬࡏࡓࡠࡐࡒࡒࡤࡈࡓࡕࡃࡆࡏࡤࡏࡎࡇࡔࡄࡣࡆ࠷࠱࡚ࡡࡖࡉࡘ࡙ࡉࡐࡐࠪឳ")] = bstack1l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫ឴")
        return bstack1ll1lllll_opy_
    except Exception as e:
      logger.error(bstack1l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡧࡤࡥ࡫ࡱ࡫ࠥࡴ࡯࡯࠯ࡅࡗࠥ࡯࡮ࡧࡴࡤࠤࡦ࠷࠱ࡺࠢࡦ࡬ࡷࡵ࡭ࡦࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࠧ឵") + str(e))
      return bstack1ll1lllll_opy_