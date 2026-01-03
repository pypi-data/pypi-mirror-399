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
import atexit
import shlex
import signal
import yaml
import socket
import datetime
import string
import random
import collections.abc
import traceback
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from browserstack_sdk.bstack111llll1ll_opy_ import bstack11l111111l_opy_
from browserstack_sdk.bstack11l1l11l1l_opy_ import *
import time
import requests
from bstack_utils.constants import EVENTS, STAGE, bstack1l1l1llll_opy_
from bstack_utils.messages import bstack1ll1l111_opy_, bstack11l1l1111_opy_, bstack111ll111_opy_, bstack11lllll11l_opy_, bstack11l1l1l1_opy_, bstack1lllll1lll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
from bstack_utils.helper import bstack1l11l1ll1l_opy_
from browserstack_sdk.bstack1ll1l11lll_opy_ import bstack11l1l11ll1_opy_
logger = get_logger(__name__)
def bstack1l111ll1l1_opy_():
  global CONFIG
  headers = {
        bstack1l1l_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack1l1l_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack1l11l1ll1l_opy_(CONFIG, bstack1l1l1llll_opy_)
  try:
    response = requests.get(bstack1l1l1llll_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack1l1lll111l_opy_ = response.json()[bstack1l1l_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack1ll1l111_opy_.format(response.json()))
      return bstack1l1lll111l_opy_
    else:
      logger.debug(bstack11l1l1111_opy_.format(bstack1l1l_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack11l1l1111_opy_.format(e))
def bstack1llll1l111_opy_(hub_url):
  global CONFIG
  url = bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack1l1l_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack1l1l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack1l1l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack1l11l1ll1l_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack111ll111_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack11lllll11l_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack1ll1llll1l_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack111l1l111_opy_():
  try:
    global bstack11ll1lll1l_opy_
    global CONFIG
    if bstack1l1l_opy_ (u"ࠫ࡭ࡻࡢࡓࡧࡪ࡭ࡴࡴࠧࡾ") in CONFIG and CONFIG[bstack1l1l_opy_ (u"ࠬ࡮ࡵࡣࡔࡨ࡫࡮ࡵ࡮ࠨࡿ")]:
      from bstack_utils.constants import bstack1l1ll1l1l_opy_
      bstack1lll1lll1l_opy_ = CONFIG[bstack1l1l_opy_ (u"࠭ࡨࡶࡤࡕࡩ࡬࡯࡯࡯ࠩࢀ")]
      if bstack1lll1lll1l_opy_ in bstack1l1ll1l1l_opy_:
        bstack11ll1lll1l_opy_ = bstack1l1ll1l1l_opy_[bstack1lll1lll1l_opy_]
        logger.debug(bstack11l1l1l1_opy_.format(bstack11ll1lll1l_opy_))
        return
      else:
        logger.debug(bstack1l1l_opy_ (u"ࠢࡉࡷࡥࠤࡰ࡫ࡹࠡࠩࡾࢁࠬࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࡎࡕࡃࡡࡘࡖࡑࡥࡍࡂࡒ࠯ࠤ࡫ࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦ࡯ࡱࡶ࡬ࡱࡦࡲࠠࡩࡷࡥࠤࡩ࡫ࡴࡦࡥࡷ࡭ࡴࡴࠢࢁ").format(bstack1lll1lll1l_opy_))
    bstack1l1lll111l_opy_ = bstack1l111ll1l1_opy_()
    bstack1l1111lll_opy_ = []
    results = []
    for bstack1ll1ll1lll_opy_ in bstack1l1lll111l_opy_:
      bstack1l1111lll_opy_.append(bstack11l1l11ll1_opy_(target=bstack1llll1l111_opy_,args=(bstack1ll1ll1lll_opy_,)))
    for t in bstack1l1111lll_opy_:
      t.start()
    for t in bstack1l1111lll_opy_:
      results.append(t.join())
    bstack1l11l1111_opy_ = {}
    for item in results:
      hub_url = item[bstack1l1l_opy_ (u"ࠨࡪࡸࡦࡤࡻࡲ࡭ࠩࢂ")]
      latency = item[bstack1l1l_opy_ (u"ࠩ࡯ࡥࡹ࡫࡮ࡤࡻࠪࢃ")]
      bstack1l11l1111_opy_[hub_url] = latency
    bstack1l11lll1l1_opy_ = min(bstack1l11l1111_opy_, key= lambda x: bstack1l11l1111_opy_[x])
    bstack11ll1lll1l_opy_ = bstack1l11lll1l1_opy_
    logger.debug(bstack11l1l1l1_opy_.format(bstack1l11lll1l1_opy_))
  except Exception as e:
    logger.debug(bstack1lllll1lll_opy_.format(e))
from browserstack_sdk.bstack111l11ll1_opy_ import *
from browserstack_sdk.bstack1ll1l11lll_opy_ import *
from browserstack_sdk.bstack11ll11l1l1_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack11ll111l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack1l1l111lll_opy_():
    global bstack11ll1lll1l_opy_
    try:
        bstack1ll11l11ll_opy_ = bstack1l111ll1ll_opy_()
        bstack1l1111l111_opy_(bstack1ll11l11ll_opy_)
        hub_url = bstack1ll11l11ll_opy_.get(bstack1l1l_opy_ (u"ࠥࡹࡷࡲࠢࢄ"), bstack1l1l_opy_ (u"ࠦࠧࢅ"))
        if hub_url.endswith(bstack1l1l_opy_ (u"ࠬ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ࢆ")):
            hub_url = hub_url.rsplit(bstack1l1l_opy_ (u"࠭࠯ࡸࡦ࠲࡬ࡺࡨࠧࢇ"), 1)[0]
        if hub_url.startswith(bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࠨ࢈")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack1l1l_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࠪࢉ")):
            hub_url = hub_url[8:]
        bstack11ll1lll1l_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack1l111ll1ll_opy_():
    global CONFIG
    bstack1l111l11_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢊ"), {}).get(bstack1l1l_opy_ (u"ࠪ࡫ࡷ࡯ࡤࡏࡣࡰࡩࠬࢋ"), bstack1l1l_opy_ (u"ࠫࡓࡕ࡟ࡈࡔࡌࡈࡤࡔࡁࡎࡇࡢࡔࡆ࡙ࡓࡆࡆࠪࢌ"))
    if not isinstance(bstack1l111l11_opy_, str):
        raise ValueError(bstack1l1l_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡌࡸࡩࡥࠢࡱࡥࡲ࡫ࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡣࠣࡺࡦࡲࡩࡥࠢࡶࡸࡷ࡯࡮ࡨࠤࢍ"))
    try:
        bstack1ll11l11ll_opy_ = bstack1ll1l1l1ll_opy_(bstack1l111l11_opy_)
        return bstack1ll11l11ll_opy_
    except Exception as e:
        logger.error(bstack1l1l_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧࢎ").format(str(e)))
        return {}
def bstack1ll1l1l1ll_opy_(bstack1l111l11_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ࢏")] or not CONFIG[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ࢐")]:
            raise ValueError(bstack1l1l_opy_ (u"ࠤࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠤࡴࡸࠠࡢࡥࡦࡩࡸࡹࠠ࡬ࡧࡼࠦ࢑"))
        url = bstack11l11l1l1_opy_ + bstack1l111l11_opy_
        auth = (CONFIG[bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ࢒")], CONFIG[bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ࢓")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack1111l1l11_opy_ = json.loads(response.text)
            return bstack1111l1l11_opy_
    except ValueError as ve:
        logger.error(bstack1l1l_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧ࢔").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack1l1l_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡪࡶ࡮ࡪࠠࡥࡧࡷࡥ࡮ࡲࡳࠡ࠼ࠣࡿࢂࠨ࢕").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack1l1111l111_opy_(bstack1l11lllll1_opy_):
    global CONFIG
    if bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ࢖") not in CONFIG or str(CONFIG[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬࢗ")]).lower() == bstack1l1l_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ࢘"):
        CONFIG[bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭࢙ࠩ")] = False
    elif bstack1l1l_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥ࢚ࠩ") in bstack1l11lllll1_opy_:
        bstack1l111ll111_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴ࢛ࠩ"), {})
        logger.debug(bstack1l1l_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡸࡪࡵࡷ࡭ࡳ࡭ࠠ࡭ࡱࡦࡥࡱࠦ࡯ࡱࡶ࡬ࡳࡳࡹ࠺ࠡࠧࡶࠦ࢜"), bstack1l111ll111_opy_)
        bstack111l1l1l_opy_ = bstack1l11lllll1_opy_.get(bstack1l1l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡒࡦࡲࡨࡥࡹ࡫ࡲࡴࠤ࢝"), [])
        bstack1l1l11lll1_opy_ = bstack1l1l_opy_ (u"ࠣ࠮ࠥ࢞").join(bstack111l1l1l_opy_)
        logger.debug(bstack1l1l_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡅࡸࡷࡹࡵ࡭ࠡࡴࡨࡴࡪࡧࡴࡦࡴࠣࡷࡹࡸࡩ࡯ࡩ࠽ࠤࠪࡹࠢ࢟"), bstack1l1l11lll1_opy_)
        bstack111ll1l11_opy_ = {
            bstack1l1l_opy_ (u"ࠥࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧࢠ"): bstack1l1l_opy_ (u"ࠦࡦࡺࡳ࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠥࢡ"),
            bstack1l1l_opy_ (u"ࠧ࡬࡯ࡳࡥࡨࡐࡴࡩࡡ࡭ࠤࢢ"): bstack1l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦࢣ"),
            bstack1l1l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࠭ࡳࡧࡳࡩࡦࡺࡥࡳࠤࢤ"): bstack1l1l11lll1_opy_
        }
        bstack1l111ll111_opy_.update(bstack111ll1l11_opy_)
        logger.debug(bstack1l1l_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡖࡲࡧࡥࡹ࡫ࡤࠡ࡮ࡲࡧࡦࡲࠠࡰࡲࡷ࡭ࡴࡴࡳ࠻ࠢࠨࡷࠧࢥ"), bstack1l111ll111_opy_)
        CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")] = bstack1l111ll111_opy_
        logger.debug(bstack1l1l_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡉ࡭ࡳࡧ࡬ࠡࡅࡒࡒࡋࡏࡇ࠻ࠢࠨࡷࠧࢧ"), CONFIG)
def bstack11l1lll11l_opy_():
    bstack1ll11l11ll_opy_ = bstack1l111ll1ll_opy_()
    if not bstack1ll11l11ll_opy_[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡖࡴ࡯ࠫࢨ")]:
      raise ValueError(bstack1l1l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡗࡵࡰࠥ࡯ࡳࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡩࡶࡴࡳࠠࡨࡴ࡬ࡨࠥࡪࡥࡵࡣ࡬ࡰࡸ࠴ࠢࢩ"))
    return bstack1ll11l11ll_opy_[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡘࡶࡱ࠭ࢪ")] + bstack1l1l_opy_ (u"ࠧࡀࡥࡤࡴࡸࡃࠧࢫ")
@measure(event_name=EVENTS.bstack111ll1l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack11l1111111_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack1l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪࢬ")], CONFIG[bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࢭ")])
        url = bstack11l1ll1l1_opy_
        logger.debug(bstack1l1l_opy_ (u"ࠥࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡶࡴࡳࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡔࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠣࡅࡕࡏࠢࢮ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack1l1l_opy_ (u"ࠦࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠥࢯ"): bstack1l1l_opy_ (u"ࠧࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠣࢰ")})
            if response.status_code == 200:
                bstack1ll1l1ll_opy_ = json.loads(response.text)
                bstack1111ll11_opy_ = bstack1ll1l1ll_opy_.get(bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠭ࢱ"), [])
                if bstack1111ll11_opy_:
                    bstack11l1lll1l_opy_ = bstack1111ll11_opy_[0]
                    build_hashed_id = bstack11l1lll1l_opy_.get(bstack1l1l_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪࢲ"))
                    bstack11111111_opy_ = bstack1lll1111ll_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack11111111_opy_])
                    logger.info(bstack111lll111_opy_.format(bstack11111111_opy_))
                    bstack111l1ll11_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫࢳ")]
                    if bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࢴ") in CONFIG:
                      bstack111l1ll11_opy_ += bstack1l1l_opy_ (u"ࠪࠤࠬࢵ") + CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࢶ")]
                    if bstack111l1ll11_opy_ != bstack11l1lll1l_opy_.get(bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢷ")):
                      logger.debug(bstack1lll1lllll_opy_.format(bstack11l1lll1l_opy_.get(bstack1l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫࢸ")), bstack111l1ll11_opy_))
                    return result
                else:
                    logger.debug(bstack1l1l_opy_ (u"ࠢࡂࡖࡖࠤ࠿ࠦࡎࡰࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠱ࠦࢹ"))
            else:
                logger.debug(bstack1l1l_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢺ"))
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡶࠤ࠿ࠦࡻࡾࠤࢻ").format(str(e)))
    else:
        logger.debug(bstack1l1l_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡆࡓࡓࡌࡉࡈࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡶࡩࡹ࠴ࠠࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢼ"))
    return [None, None]
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack111l111l_opy_ import bstack111l111l_opy_, bstack11l111111_opy_, bstack1l1lllll1_opy_, bstack11lll1l1l1_opy_
from bstack_utils.measure import bstack1ll111ll11_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack1l111llll1_opy_ import bstack11l1ll11ll_opy_
from bstack_utils.messages import *
from bstack_utils import bstack1lllllll1l_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1ll1ll11_opy_, bstack11l11llll_opy_, bstack1ll1lll111_opy_, bstack11llll11ll_opy_, \
  bstack1l11ll1l11_opy_, \
  Notset, bstack1llll11l1_opy_, \
  bstack1ll11llll_opy_, bstack1ll111111l_opy_, bstack1l11111l11_opy_, bstack1l1lll1l_opy_, bstack11ll111l11_opy_, bstack111ll1111_opy_, \
  bstack11llll11l1_opy_, \
  bstack11ll1ll1l_opy_, bstack11ll11ll11_opy_, bstack1ll1ll111_opy_, bstack111llll1_opy_, \
  bstack11ll11lll_opy_, bstack1lllll1l1l_opy_, bstack1l1l1111l1_opy_, bstack11ll1l1l1_opy_, bstack11llll1ll1_opy_
from bstack_utils.bstack111ll11l1_opy_ import bstack1l11llll1_opy_
from bstack_utils.bstack1l1l111ll_opy_ import bstack1l111111ll_opy_, bstack1l1ll11l11_opy_
from bstack_utils.bstack11ll1lll1_opy_ import bstack1lllll11_opy_
from bstack_utils.bstack1l1l1ll1_opy_ import bstack11ll11111_opy_, bstack1l11l111l1_opy_
from bstack_utils.bstack111111lll_opy_ import bstack111111lll_opy_
from bstack_utils.bstack11l1llll1_opy_ import bstack1lll111l1l_opy_
from bstack_utils.proxy import bstack11l1111ll_opy_, bstack1l11l1ll1l_opy_, bstack1l11ll1ll_opy_, bstack1l1l1l1l1_opy_
from bstack_utils.bstack111111l11_opy_ import bstack1l1l111l1_opy_, bstack1111l11l_opy_
import bstack_utils.bstack1lll1l1111_opy_ as bstack1ll11ll1l_opy_
import bstack_utils.bstack1ll11l1l11_opy_ as bstack11ll111ll1_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.utils.bstack1l11ll1l1l_opy_ import bstack1l1111llll_opy_
from bstack_utils.bstack1l11l1l1ll_opy_ import bstack111l1111l_opy_
from bstack_utils.bstack111ll1ll_opy_ import bstack1l11l111_opy_
if os.getenv(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡉࡑࡒࡏࡘ࠭ࢽ")):
  cli.bstack1l1l11ll11_opy_()
else:
  os.environ[bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡊࡒࡓࡐ࡙ࠧࢾ")] = bstack1l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫࢿ")
bstack11l11ll11l_opy_ = bstack1l1l_opy_ (u"ࠧࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠠࠡ࡫ࡩࠬࡵࡧࡧࡦࠢࡀࡁࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠠࡼ࡞ࡱࠤࠥࠦࡴࡳࡻࡾࡠࡳࠦࡣࡰࡰࡶࡸࠥ࡬ࡳࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࡡ࠭ࡦࡴ࡞ࠪ࠭ࡀࡢ࡮ࠡࠢࠣࠤࠥ࡬ࡳ࠯ࡣࡳࡴࡪࡴࡤࡇ࡫࡯ࡩࡘࡿ࡮ࡤࠪࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠬࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡳࡣ࡮ࡴࡤࡦࡺࠬࠤ࠰ࠦࠢ࠻ࠤࠣ࠯ࠥࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࠬࡦࡽࡡࡪࡶࠣࡲࡪࡽࡐࡢࡩࡨ࠶࠳࡫ࡶࡢ࡮ࡸࡥࡹ࡫ࠨࠣࠪࠬࠤࡂࡄࠠࡼࡿࠥ࠰ࠥࡢࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡨࡧࡷࡗࡪࡹࡳࡪࡱࡱࡈࡪࡺࡡࡪ࡮ࡶࠦࢂࡢࠧࠪࠫࠬ࡟ࠧ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠣ࡟ࠬࠤ࠰ࠦࠢ࠭࡞࡟ࡲࠧ࠯࡜࡯ࠢࠣࠤࠥࢃࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡽ࡝ࡰࠣࠤ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠧࣀ")
bstack11111l111_opy_ = bstack1l1l_opy_ (u"ࠨ࡞ࡱ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࡢ࡮ࡤࡱࡱࡷࡹࠦࡢࡴࡶࡤࡧࡰࡥࡰࡢࡶ࡫ࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳࡞࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠴ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡶ࡟ࡪࡰࡧࡩࡽࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠴ࡠࡠࡳࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡹ࡬ࡪࡥࡨࠬ࠵࠲ࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࠬࡠࡳࡩ࡯࡯ࡵࡷࠤ࡮ࡳࡰࡰࡴࡷࡣࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴ࠵ࡡࡥࡷࡹࡧࡣ࡬ࠢࡀࠤࡷ࡫ࡱࡶ࡫ࡵࡩ࠭ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ࠭ࡀࡢ࡮ࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻ࡝ࡰ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࡡࡴࡴࡳࡻࠣࡿࡡࡴࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࡞ࡱࠤࠥࢃࠠࡤࡣࡷࡧ࡭࠮ࡥࡹࠫࠣࡿࡡࡴࠠࠡࠢࠣࢁࡡࡴࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽ࡟ࡲࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࡠࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠦࡾࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪࡿࡣ࠰ࡡࡴࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࡢ࡮ࠡࠢࢀ࠭ࡡࡴࡽ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠧࣁ")
from ._version import __version__
bstack111111ll_opy_ = None
CONFIG = {}
bstack1l1ll1ll11_opy_ = {}
bstack11l11l11l_opy_ = {}
bstack1lll1lll1_opy_ = None
bstack11l111ll1_opy_ = None
bstack11ll11ll_opy_ = None
bstack1ll1ll1l11_opy_ = -1
bstack1l1l11ll1_opy_ = 0
bstack1ll1l11l1l_opy_ = bstack1lllll111l_opy_
bstack111111111_opy_ = 1
bstack1l1ll11lll_opy_ = False
bstack1ll1ll111l_opy_ = False
bstack1lll1l11l1_opy_ = bstack1l1l_opy_ (u"ࠩࠪࣂ")
bstack1lllll1ll1_opy_ = bstack1l1l_opy_ (u"ࠪࠫࣃ")
bstack11l11l11l1_opy_ = False
bstack1l1lll11l1_opy_ = True
bstack1l111lll1l_opy_ = bstack1l1l_opy_ (u"ࠫࠬࣄ")
bstack1l11l11l_opy_ = []
bstack1l111l1ll_opy_ = threading.Lock()
bstack1l11lll111_opy_ = threading.Lock()
bstack11ll1lll1l_opy_ = bstack1l1l_opy_ (u"ࠬ࠭ࣅ")
bstack11ll1l11ll_opy_ = False
bstack11llllll_opy_ = None
bstack1ll11l11_opy_ = None
bstack11l1l1111l_opy_ = None
bstack1111l1ll_opy_ = -1
bstack1l11l11l1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"࠭ࡾࠨࣆ")), bstack1l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧࣇ"), bstack1l1l_opy_ (u"ࠨ࠰ࡵࡳࡧࡵࡴ࠮ࡴࡨࡴࡴࡸࡴ࠮ࡪࡨࡰࡵ࡫ࡲ࠯࡬ࡶࡳࡳ࠭ࣈ"))
bstack11l11111l1_opy_ = 0
bstack1lll111l_opy_ = 0
bstack1ll1111l11_opy_ = []
bstack1l1l11llll_opy_ = []
bstack1lll111ll_opy_ = []
bstack1lll11111l_opy_ = []
bstack1l1l111l11_opy_ = bstack1l1l_opy_ (u"ࠩࠪࣉ")
bstack11l1lll1l1_opy_ = bstack1l1l_opy_ (u"ࠪࠫ࣊")
bstack1l1lllll_opy_ = False
bstack1l1l1l11l1_opy_ = False
bstack11l11l1ll_opy_ = {}
bstack1l1llll1ll_opy_ = {}
bstack111ll1l1l_opy_ = None
bstack11l1lll111_opy_ = None
bstack11ll1l1lll_opy_ = None
bstack1llll1111_opy_ = None
bstack1l1111l1l1_opy_ = None
bstack1lll1ll11l_opy_ = None
bstack1l1llll11_opy_ = None
bstack1l1l1l1l11_opy_ = None
bstack1lll1ll111_opy_ = None
bstack11lll11l1l_opy_ = None
bstack1l11lll1ll_opy_ = None
bstack1ll1l1ll1l_opy_ = None
bstack111llll111_opy_ = None
bstack11l1lllll1_opy_ = None
bstack1l1ll11ll1_opy_ = None
bstack1l111l111_opy_ = None
bstack1ll11l11l1_opy_ = None
bstack11l111l1l_opy_ = None
bstack111lll1ll_opy_ = None
bstack11l1lll1ll_opy_ = None
bstack1lll111lll_opy_ = None
bstack1111l1l1_opy_ = None
bstack1l1l1lll1l_opy_ = None
thread_local = threading.local()
bstack1l1l1ll111_opy_ = False
bstack11l11ll11_opy_ = bstack1l1l_opy_ (u"ࠦࠧ࣋")
logger = bstack1lllllll1l_opy_.get_logger(__name__, bstack1ll1l11l1l_opy_)
bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
percy = bstack111111l1_opy_()
bstack11l1lllll_opy_ = bstack11l1ll11ll_opy_()
bstack1lll11l1l1_opy_ = bstack11ll11l1l1_opy_()
def bstack11111lll1_opy_():
  global CONFIG
  global bstack1l1lllll_opy_
  global bstack1l1ll1l1_opy_
  testContextOptions = bstack11ll111l1l_opy_(CONFIG)
  if bstack1l11ll1l11_opy_(CONFIG):
    if (bstack1l1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ࣌") in testContextOptions and str(testContextOptions[bstack1l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ࣍")]).lower() == bstack1l1l_opy_ (u"ࠧࡵࡴࡸࡩࠬ࣎")):
      bstack1l1lllll_opy_ = True
    bstack1l1ll1l1_opy_.bstack1ll11ll11l_opy_(testContextOptions.get(bstack1l1l_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷ࣏ࠬ"), False))
  else:
    bstack1l1lllll_opy_ = True
    bstack1l1ll1l1_opy_.bstack1ll11ll11l_opy_(True)
def bstack11ll11l1ll_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1llllll1l1_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack11l1l11l1_opy_():
  global bstack1l1llll1ll_opy_
  args = sys.argv
  for i in range(len(args)):
    if bstack1l1l_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡦࡳࡳ࡬ࡩࡨࡨ࡬ࡰࡪࠨ࣐") == args[i].lower() or bstack1l1l_opy_ (u"ࠥ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡮ࡧ࡫ࡪ࣑ࠦ") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      bstack1l1llll1ll_opy_[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨ࣒")] = path
      return path
  return None
bstack11ll1111l_opy_ = re.compile(bstack1l1l_opy_ (u"ࡷࠨ࠮ࠫࡁ࡟ࠨࢀ࠮࠮ࠫࡁࠬࢁ࠳࠰࠿࣓ࠣ"))
def bstack111l1l11_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack11ll1111l_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack1l1l_opy_ (u"ࠨࠤࡼࠤࣔ") + group + bstack1l1l_opy_ (u"ࠢࡾࠤࣕ"), os.environ.get(group))
  return value
def bstack11l11l11_opy_():
  global bstack1l1l1lll1l_opy_
  if bstack1l1l1lll1l_opy_ is None:
        bstack1l1l1lll1l_opy_ = bstack11l1l11l1_opy_()
  bstack11ll1l1ll1_opy_ = bstack1l1l1lll1l_opy_
  if bstack11ll1l1ll1_opy_ and os.path.exists(os.path.abspath(bstack11ll1l1ll1_opy_)):
    fileName = bstack11ll1l1ll1_opy_
  if bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࣖ") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࡠࡈࡌࡐࡊ࠭ࣗ")])) and not bstack1l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡏࡣࡰࡩࠬࣘ") in locals():
    fileName = os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨࣙ")]
  if bstack1l1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡑࡥࡲ࡫ࠧࣚ") in locals():
    bstack1lll11_opy_ = os.path.abspath(fileName)
  else:
    bstack1lll11_opy_ = bstack1l1l_opy_ (u"࠭ࠧࣛ")
  bstack1lll11lll_opy_ = os.getcwd()
  bstack1l1111l11_opy_ = bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪࣜ")
  bstack111l1111_opy_ = bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺࡣࡰࡰࠬࣝ")
  while (not os.path.exists(bstack1lll11_opy_)) and bstack1lll11lll_opy_ != bstack1l1l_opy_ (u"ࠤࠥࣞ"):
    bstack1lll11_opy_ = os.path.join(bstack1lll11lll_opy_, bstack1l1111l11_opy_)
    if not os.path.exists(bstack1lll11_opy_):
      bstack1lll11_opy_ = os.path.join(bstack1lll11lll_opy_, bstack111l1111_opy_)
    if bstack1lll11lll_opy_ != os.path.dirname(bstack1lll11lll_opy_):
      bstack1lll11lll_opy_ = os.path.dirname(bstack1lll11lll_opy_)
    else:
      bstack1lll11lll_opy_ = bstack1l1l_opy_ (u"ࠥࠦࣟ")
  bstack1l1l1lll1l_opy_ = bstack1lll11_opy_ if os.path.exists(bstack1lll11_opy_) else None
  return bstack1l1l1lll1l_opy_
def bstack1llllll1ll_opy_(config):
    if bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫ࣠") in config:
      config[bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ࣡")] = config[bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬࠭࣢")]
    if bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࣣࠧ") in config:
      config[bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬࣤ")] = config[bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣥ")]
def bstack1ll1llllll_opy_():
  bstack1lll11_opy_ = bstack11l11l11_opy_()
  if not os.path.exists(bstack1lll11_opy_):
    bstack1ll1llll11_opy_(
      bstack1l11llll11_opy_.format(os.getcwd()))
  try:
    with open(bstack1lll11_opy_, bstack1l1l_opy_ (u"ࠪࡶࣦࠬ")) as stream:
      yaml.add_implicit_resolver(bstack1l1l_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࣧ"), bstack11ll1111l_opy_)
      yaml.add_constructor(bstack1l1l_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࣨ"), bstack111l1l11_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      bstack1llllll1ll_opy_(config)
      return config
  except:
    with open(bstack1lll11_opy_, bstack1l1l_opy_ (u"࠭ࡲࠨࣩ")) as stream:
      try:
        config = yaml.safe_load(stream)
        bstack1llllll1ll_opy_(config)
        return config
      except yaml.YAMLError as exc:
        bstack1ll1llll11_opy_(bstack11l1l11l_opy_.format(str(exc)))
def bstack1l11l1ll11_opy_(config):
  bstack1ll1l1lll_opy_ = bstack1lll11111_opy_(config)
  for option in list(bstack1ll1l1lll_opy_):
    if option.lower() in bstack11lll1111_opy_ and option != bstack11lll1111_opy_[option.lower()]:
      bstack1ll1l1lll_opy_[bstack11lll1111_opy_[option.lower()]] = bstack1ll1l1lll_opy_[option]
      del bstack1ll1l1lll_opy_[option]
  return config
def bstack1lllll1ll_opy_():
  global bstack11l11l11l_opy_
  for key, bstack1l11l11ll1_opy_ in bstack11lll1111l_opy_.items():
    if isinstance(bstack1l11l11ll1_opy_, list):
      for var in bstack1l11l11ll1_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack11l11l11l_opy_[key] = os.environ[var]
          break
    elif bstack1l11l11ll1_opy_ in os.environ and os.environ[bstack1l11l11ll1_opy_] and str(os.environ[bstack1l11l11ll1_opy_]).strip():
      bstack11l11l11l_opy_[key] = os.environ[bstack1l11l11ll1_opy_]
  if bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ࣪") in os.environ:
    bstack11l11l11l_opy_[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ࣫")] = {}
    bstack11l11l11l_opy_[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭࣬")][bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ࣭ࠬ")] = os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࣮࠭")]
def bstack1l1l1lll11_opy_():
  global bstack1l1ll1ll11_opy_
  global bstack1l111lll1l_opy_
  global bstack1l1llll1ll_opy_
  bstack1ll11l1lll_opy_ = []
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) - 1 and bstack1l1l_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ࣯").lower() == val.lower():
      bstack1l1ll1ll11_opy_[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࣰࠪ")] = {}
      bstack1l1ll1ll11_opy_[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࣱࠫ")][bstack1l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣲࠪ")] = sys.argv[idx + 1]
      bstack1ll11l1lll_opy_.extend([idx, idx + 1])
      break
  for key, bstack1ll11ll1l1_opy_ in bstack11l1l111l_opy_.items():
    if isinstance(bstack1ll11ll1l1_opy_, list):
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        for var in bstack1ll11ll1l1_opy_:
          if bstack1l1l_opy_ (u"ࠩ࠰࠱ࠬࣳ") + var.lower() == val.lower() and key not in bstack1l1ll1ll11_opy_:
            bstack1l1ll1ll11_opy_[key] = sys.argv[idx + 1]
            bstack1l111lll1l_opy_ += bstack1l1l_opy_ (u"ࠪࠤ࠲࠳ࠧࣴ") + var + bstack1l1l_opy_ (u"ࠫࠥ࠭ࣵ") + shlex.quote(sys.argv[idx + 1])
            bstack11llll1ll1_opy_(bstack1l1llll1ll_opy_, key, sys.argv[idx + 1])
            bstack1ll11l1lll_opy_.extend([idx, idx + 1])
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        if bstack1l1l_opy_ (u"ࠬ࠳࠭ࠨࣶ") + bstack1ll11ll1l1_opy_.lower() == val.lower() and key not in bstack1l1ll1ll11_opy_:
          bstack1l1ll1ll11_opy_[key] = sys.argv[idx + 1]
          bstack1l111lll1l_opy_ += bstack1l1l_opy_ (u"࠭ࠠ࠮࠯ࠪࣷ") + bstack1ll11ll1l1_opy_ + bstack1l1l_opy_ (u"ࠧࠡࠩࣸ") + shlex.quote(sys.argv[idx + 1])
          bstack11llll1ll1_opy_(bstack1l1llll1ll_opy_, key, sys.argv[idx + 1])
          bstack1ll11l1lll_opy_.extend([idx, idx + 1])
  for idx in sorted(set(bstack1ll11l1lll_opy_), reverse=True):
    if idx < len(sys.argv):
      del sys.argv[idx]
def bstack1l1llll11l_opy_(config):
  bstack1l111ll11_opy_ = config.keys()
  for bstack1l11ll1lll_opy_, bstack11l1l1l1l1_opy_ in bstack11llll1l1_opy_.items():
    if bstack11l1l1l1l1_opy_ in bstack1l111ll11_opy_:
      config[bstack1l11ll1lll_opy_] = config[bstack11l1l1l1l1_opy_]
      del config[bstack11l1l1l1l1_opy_]
  for bstack1l11ll1lll_opy_, bstack11l1l1l1l1_opy_ in bstack1l1llll1_opy_.items():
    if isinstance(bstack11l1l1l1l1_opy_, list):
      for bstack1ll111llll_opy_ in bstack11l1l1l1l1_opy_:
        if bstack1ll111llll_opy_ in bstack1l111ll11_opy_:
          config[bstack1l11ll1lll_opy_] = config[bstack1ll111llll_opy_]
          del config[bstack1ll111llll_opy_]
          break
    elif bstack11l1l1l1l1_opy_ in bstack1l111ll11_opy_:
      config[bstack1l11ll1lll_opy_] = config[bstack11l1l1l1l1_opy_]
      del config[bstack11l1l1l1l1_opy_]
  for bstack1ll111llll_opy_ in list(config):
    for bstack1l1ll1l11_opy_ in bstack1l1lllll1l_opy_:
      if bstack1ll111llll_opy_.lower() == bstack1l1ll1l11_opy_.lower() and bstack1ll111llll_opy_ != bstack1l1ll1l11_opy_:
        config[bstack1l1ll1l11_opy_] = config[bstack1ll111llll_opy_]
        del config[bstack1ll111llll_opy_]
  bstack1llll1ll11_opy_ = [{}]
  if not config.get(bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣹࠫ")):
    config[bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࣺࠬ")] = [{}]
  bstack1llll1ll11_opy_ = config[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣻ")]
  for platform in bstack1llll1ll11_opy_:
    for bstack1ll111llll_opy_ in list(platform):
      for bstack1l1ll1l11_opy_ in bstack1l1lllll1l_opy_:
        if bstack1ll111llll_opy_.lower() == bstack1l1ll1l11_opy_.lower() and bstack1ll111llll_opy_ != bstack1l1ll1l11_opy_:
          platform[bstack1l1ll1l11_opy_] = platform[bstack1ll111llll_opy_]
          del platform[bstack1ll111llll_opy_]
  for bstack1l11ll1lll_opy_, bstack11l1l1l1l1_opy_ in bstack1l1llll1_opy_.items():
    for platform in bstack1llll1ll11_opy_:
      if isinstance(bstack11l1l1l1l1_opy_, list):
        for bstack1ll111llll_opy_ in bstack11l1l1l1l1_opy_:
          if bstack1ll111llll_opy_ in platform:
            platform[bstack1l11ll1lll_opy_] = platform[bstack1ll111llll_opy_]
            del platform[bstack1ll111llll_opy_]
            break
      elif bstack11l1l1l1l1_opy_ in platform:
        platform[bstack1l11ll1lll_opy_] = platform[bstack11l1l1l1l1_opy_]
        del platform[bstack11l1l1l1l1_opy_]
  for bstack11l111l1l1_opy_ in bstack1l1ll111ll_opy_:
    if bstack11l111l1l1_opy_ in config:
      if not bstack1l1ll111ll_opy_[bstack11l111l1l1_opy_] in config:
        config[bstack1l1ll111ll_opy_[bstack11l111l1l1_opy_]] = {}
      config[bstack1l1ll111ll_opy_[bstack11l111l1l1_opy_]].update(config[bstack11l111l1l1_opy_])
      del config[bstack11l111l1l1_opy_]
  for platform in bstack1llll1ll11_opy_:
    for bstack11l111l1l1_opy_ in bstack1l1ll111ll_opy_:
      if bstack11l111l1l1_opy_ in list(platform):
        if not bstack1l1ll111ll_opy_[bstack11l111l1l1_opy_] in platform:
          platform[bstack1l1ll111ll_opy_[bstack11l111l1l1_opy_]] = {}
        platform[bstack1l1ll111ll_opy_[bstack11l111l1l1_opy_]].update(platform[bstack11l111l1l1_opy_])
        del platform[bstack11l111l1l1_opy_]
  config = bstack1l11l1ll11_opy_(config)
  return config
def bstack1l1l11ll1l_opy_(config):
  global bstack1lllll1ll1_opy_
  bstack1ll111l11_opy_ = False
  if bstack1l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨࣼ") in config and str(config[bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩࣽ")]).lower() != bstack1l1l_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣾ"):
    if bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫࣿ") not in config or str(config[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬऀ")]).lower() == bstack1l1l_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨँ"):
      config[bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩं")] = False
    else:
      bstack1ll11l11ll_opy_ = bstack1l111ll1ll_opy_()
      if bstack1l1l_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥࠩः") in bstack1ll11l11ll_opy_:
        if not bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
          config[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
        config[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")][bstack1l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪइ")] = bstack1l1l_opy_ (u"ࠩࡤࡸࡸ࠳ࡲࡦࡲࡨࡥࡹ࡫ࡲࠨई")
        bstack1ll111l11_opy_ = True
        bstack1lllll1ll1_opy_ = config[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")].get(bstack1l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ऊ"))
  if bstack1l11ll1l11_opy_(config) and bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩऋ") in config and str(config[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪऌ")]).lower() != bstack1l1l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ऍ") and not bstack1ll111l11_opy_:
    if not bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬऎ") in config:
      config[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")] = {}
    if not config[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧऐ")].get(bstack1l1l_opy_ (u"ࠫࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠨऑ")) and not bstack1l1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ") in config[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪओ")]:
      bstack1111lllll_opy_ = datetime.datetime.now()
      bstack1111ll1ll_opy_ = bstack1111lllll_opy_.strftime(bstack1l1l_opy_ (u"ࠧࠦࡦࡢࠩࡧࡥࠥࡉࠧࡐࠫऔ"))
      hostname = socket.gethostname()
      bstack11ll111lll_opy_ = bstack1l1l_opy_ (u"ࠨࠩक").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1l1l_opy_ (u"ࠩࡾࢁࡤࢁࡽࡠࡽࢀࠫख").format(bstack1111ll1ll_opy_, hostname, bstack11ll111lll_opy_)
      config[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧग")][bstack1l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")] = identifier
    bstack1lllll1ll1_opy_ = config[bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩङ")].get(bstack1l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच"))
  return config
def bstack1111l1lll_opy_():
  bstack1l11111111_opy_ =  bstack1l1lll1l_opy_()[bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷ࠭छ")]
  return bstack1l11111111_opy_ if bstack1l11111111_opy_ else -1
def bstack1111llll_opy_(bstack1l11111111_opy_):
  global CONFIG
  if not bstack1l1l_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪज") in CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ")]:
    return
  CONFIG[bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")] = CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")].replace(
    bstack1l1l_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧठ"),
    str(bstack1l11111111_opy_)
  )
def bstack1l1l1l1lll_opy_():
  global CONFIG
  if not bstack1l1l_opy_ (u"࠭ࠤࡼࡆࡄࡘࡊࡥࡔࡊࡏࡈࢁࠬड") in CONFIG[bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩढ")]:
    return
  bstack1111lllll_opy_ = datetime.datetime.now()
  bstack1111ll1ll_opy_ = bstack1111lllll_opy_.strftime(bstack1l1l_opy_ (u"ࠨࠧࡧ࠱ࠪࡨ࠭ࠦࡊ࠽ࠩࡒ࠭ण"))
  CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")] = CONFIG[bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬथ")].replace(
    bstack1l1l_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪद"),
    bstack1111ll1ll_opy_
  )
def bstack1l1llllll_opy_():
  global CONFIG
  if bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧध") in CONFIG and not bool(CONFIG[bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]):
    del CONFIG[bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऩ")]
    return
  if not bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪप") in CONFIG:
    CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫफ")] = bstack1l1l_opy_ (u"ࠪࠧࠩࢁࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࢂ࠭ब")
  if bstack1l1l_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪभ") in CONFIG[bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]:
    bstack1l1l1l1lll_opy_()
    os.environ[bstack1l1l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪय")] = CONFIG[bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩर")]
  if not bstack1l1l_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪऱ") in CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫल")]:
    return
  bstack1l11111111_opy_ = bstack1l1l_opy_ (u"ࠪࠫळ")
  bstack1lll111111_opy_ = bstack1111l1lll_opy_()
  if bstack1lll111111_opy_ != -1:
    bstack1l11111111_opy_ = bstack1l1l_opy_ (u"ࠫࡈࡏࠠࠨऴ") + str(bstack1lll111111_opy_)
  if bstack1l11111111_opy_ == bstack1l1l_opy_ (u"ࠬ࠭व"):
    bstack1ll1ll1l1l_opy_ = bstack1l1lll11_opy_(CONFIG[bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩश")])
    if bstack1ll1ll1l1l_opy_ != -1:
      bstack1l11111111_opy_ = str(bstack1ll1ll1l1l_opy_)
  if bstack1l11111111_opy_:
    bstack1111llll_opy_(bstack1l11111111_opy_)
    os.environ[bstack1l1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫष")] = CONFIG[bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪस")]
def bstack111l1llll_opy_(bstack11l1l1l11l_opy_, bstack1l111l11ll_opy_, path):
  bstack1l111lll11_opy_ = {
    bstack1l1l_opy_ (u"ࠩ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ह"): bstack1l111l11ll_opy_
  }
  if os.path.exists(path):
    bstack11ll1l1111_opy_ = json.load(open(path, bstack1l1l_opy_ (u"ࠪࡶࡧ࠭ऺ")))
  else:
    bstack11ll1l1111_opy_ = {}
  bstack11ll1l1111_opy_[bstack11l1l1l11l_opy_] = bstack1l111lll11_opy_
  with open(path, bstack1l1l_opy_ (u"ࠦࡼ࠱ࠢऻ")) as outfile:
    json.dump(bstack11ll1l1111_opy_, outfile)
def bstack1l1lll11_opy_(bstack11l1l1l11l_opy_):
  bstack11l1l1l11l_opy_ = str(bstack11l1l1l11l_opy_)
  bstack1l11lll11l_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠬࢄ़ࠧ")), bstack1l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ऽ"))
  try:
    if not os.path.exists(bstack1l11lll11l_opy_):
      os.makedirs(bstack1l11lll11l_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠧࡿࠩा")), bstack1l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨि"), bstack1l1l_opy_ (u"ࠩ࠱ࡦࡺ࡯࡬ࡥ࠯ࡱࡥࡲ࡫࠭ࡤࡣࡦ࡬ࡪ࠴ࡪࡴࡱࡱࠫी"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1l1l_opy_ (u"ࠪࡻࠬु")):
        pass
      with open(file_path, bstack1l1l_opy_ (u"ࠦࡼ࠱ࠢू")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1l1l_opy_ (u"ࠬࡸࠧृ")) as bstack11llll1111_opy_:
      bstack11l1ll1ll_opy_ = json.load(bstack11llll1111_opy_)
    if bstack11l1l1l11l_opy_ in bstack11l1ll1ll_opy_:
      bstack1ll1ll1ll_opy_ = bstack11l1ll1ll_opy_[bstack11l1l1l11l_opy_][bstack1l1l_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪॄ")]
      bstack1l1lll111_opy_ = int(bstack1ll1ll1ll_opy_) + 1
      bstack111l1llll_opy_(bstack11l1l1l11l_opy_, bstack1l1lll111_opy_, file_path)
      return bstack1l1lll111_opy_
    else:
      bstack111l1llll_opy_(bstack11l1l1l11l_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warning(bstack1l1ll11l_opy_.format(str(e)))
    return -1
def bstack1ll1111ll1_opy_(config):
  if not config[bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩॅ")] or not config[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫॆ")]:
    return True
  else:
    return False
def bstack111l1lll1_opy_(config, index=0):
  global bstack11l11l11l1_opy_
  bstack11l111ll11_opy_ = {}
  caps = bstack111111l1l_opy_ + bstack11llllll1_opy_
  if config.get(bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭े"), False):
    bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧै")] = True
    bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨॉ")] = config.get(bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩॊ"), {})
  if bstack11l11l11l1_opy_:
    caps += bstack1l111l1l_opy_
  for key in config:
    if key in caps + [bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩो")]:
      continue
    bstack11l111ll11_opy_[key] = config[key]
  if bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ") in config:
    for bstack11111llll_opy_ in config[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶ्ࠫ")][index]:
      if bstack11111llll_opy_ in caps:
        continue
      bstack11l111ll11_opy_[bstack11111llll_opy_] = config[bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॎ")][index][bstack11111llll_opy_]
  bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠪ࡬ࡴࡹࡴࡏࡣࡰࡩࠬॏ")] = socket.gethostname()
  if bstack1l1l_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬॐ") in bstack11l111ll11_opy_:
    del (bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭॑")])
  return bstack11l111ll11_opy_
def bstack11l1llll11_opy_(config):
  global bstack11l11l11l1_opy_
  bstack11ll1llll1_opy_ = {}
  caps = bstack11llllll1_opy_
  if bstack11l11l11l1_opy_:
    caps += bstack1l111l1l_opy_
  for key in caps:
    if key in config:
      bstack11ll1llll1_opy_[key] = config[key]
  return bstack11ll1llll1_opy_
def bstack1111l11l1_opy_(bstack11l111ll11_opy_, bstack11ll1llll1_opy_):
  bstack11ll1lllll_opy_ = {}
  for key in bstack11l111ll11_opy_.keys():
    if key in bstack11llll1l1_opy_:
      bstack11ll1lllll_opy_[bstack11llll1l1_opy_[key]] = bstack11l111ll11_opy_[key]
    else:
      bstack11ll1lllll_opy_[key] = bstack11l111ll11_opy_[key]
  for key in bstack11ll1llll1_opy_:
    if key in bstack11llll1l1_opy_:
      bstack11ll1lllll_opy_[bstack11llll1l1_opy_[key]] = bstack11ll1llll1_opy_[key]
    else:
      bstack11ll1lllll_opy_[key] = bstack11ll1llll1_opy_[key]
  return bstack11ll1lllll_opy_
def bstack1l111lll1_opy_(config, index=0):
  global bstack11l11l11l1_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack1lllll1l11_opy_ = bstack1ll1ll11_opy_(bstack11ll1l111l_opy_, config, logger)
  bstack11ll1llll1_opy_ = bstack11l1llll11_opy_(config)
  bstack1ll111l1ll_opy_ = bstack11llllll1_opy_
  bstack1ll111l1ll_opy_ += bstack1lll11llll_opy_
  bstack11ll1llll1_opy_ = update(bstack11ll1llll1_opy_, bstack1lllll1l11_opy_)
  if bstack11l11l11l1_opy_:
    bstack1ll111l1ll_opy_ += bstack1l111l1l_opy_
  if bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ॒ࠩ") in config:
    if bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ॓") in config[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
      caps[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧॕ")] = config[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॗ")]
    if bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭क़") in config[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index]:
      caps[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨग़")] = str(config[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫज़")][index][bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪड़")])
    bstack1l1l1llll1_opy_ = bstack1ll1ll11_opy_(bstack11ll1l111l_opy_, config[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ढ़")][index], logger)
    bstack1ll111l1ll_opy_ += list(bstack1l1l1llll1_opy_.keys())
    for bstack1l1l1ll11l_opy_ in bstack1ll111l1ll_opy_:
      if bstack1l1l1ll11l_opy_ in config[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧफ़")][index]:
        if bstack1l1l1ll11l_opy_ == bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧय़"):
          try:
            bstack1l1l1llll1_opy_[bstack1l1l1ll11l_opy_] = str(config[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॠ")][index][bstack1l1l1ll11l_opy_] * 1.0)
          except:
            bstack1l1l1llll1_opy_[bstack1l1l1ll11l_opy_] = str(config[bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪॡ")][index][bstack1l1l1ll11l_opy_])
        else:
          bstack1l1l1llll1_opy_[bstack1l1l1ll11l_opy_] = config[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫॢ")][index][bstack1l1l1ll11l_opy_]
        del (config[bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॣ")][index][bstack1l1l1ll11l_opy_])
    bstack11ll1llll1_opy_ = update(bstack11ll1llll1_opy_, bstack1l1l1llll1_opy_)
  bstack11l111ll11_opy_ = bstack111l1lll1_opy_(config, index)
  for bstack1ll111llll_opy_ in bstack11llllll1_opy_ + list(bstack1lllll1l11_opy_.keys()):
    if bstack1ll111llll_opy_ in bstack11l111ll11_opy_:
      bstack11ll1llll1_opy_[bstack1ll111llll_opy_] = bstack11l111ll11_opy_[bstack1ll111llll_opy_]
      del (bstack11l111ll11_opy_[bstack1ll111llll_opy_])
  if bstack1llll11l1_opy_(config):
    bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ।")] = True
    caps.update(bstack11ll1llll1_opy_)
    caps[bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ॥")] = bstack11l111ll11_opy_
  else:
    bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬ०")] = False
    caps.update(bstack1111l11l1_opy_(bstack11l111ll11_opy_, bstack11ll1llll1_opy_))
    if bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ१") in caps:
      caps[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ२")] = caps[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭३")]
      del (caps[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ४")])
    if bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ५") in caps:
      caps[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭६")] = caps[bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭७")]
      del (caps[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ८")])
  return caps
def bstack111lll11ll_opy_():
  global bstack11ll1lll1l_opy_
  global CONFIG
  if bstack1llllll1l1_opy_() <= version.parse(bstack1l1l_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ९")):
    if bstack11ll1lll1l_opy_ != bstack1l1l_opy_ (u"ࠨࠩ॰"):
      return bstack1l1l_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥॱ") + bstack11ll1lll1l_opy_ + bstack1l1l_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢॲ")
    return bstack1l1ll1ll_opy_
  if bstack11ll1lll1l_opy_ != bstack1l1l_opy_ (u"ࠫࠬॳ"):
    return bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢॴ") + bstack11ll1lll1l_opy_ + bstack1l1l_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢॵ")
  return bstack1llll11111_opy_
def bstack111l11ll_opy_(options):
  return hasattr(options, bstack1l1l_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨॶ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack11ll1ll11l_opy_(options, bstack11ll1l1ll_opy_):
  for bstack11ll1lll11_opy_ in bstack11ll1l1ll_opy_:
    if bstack11ll1lll11_opy_ in [bstack1l1l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॷ"), bstack1l1l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ॸ")]:
      continue
    if bstack11ll1lll11_opy_ in options._experimental_options:
      options._experimental_options[bstack11ll1lll11_opy_] = update(options._experimental_options[bstack11ll1lll11_opy_],
                                                         bstack11ll1l1ll_opy_[bstack11ll1lll11_opy_])
    else:
      options.add_experimental_option(bstack11ll1lll11_opy_, bstack11ll1l1ll_opy_[bstack11ll1lll11_opy_])
  if bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack11ll1l1ll_opy_:
    for arg in bstack11ll1l1ll_opy_[bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
    del (bstack11ll1l1ll_opy_[bstack1l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪॻ")])
  if bstack1l1l_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪॼ") in bstack11ll1l1ll_opy_:
    for ext in bstack11ll1l1ll_opy_[bstack1l1l_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫॽ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack11ll1l1ll_opy_[bstack1l1l_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬॾ")])
def bstack111lllll1l_opy_(options, bstack111lllll_opy_):
  if bstack1l1l_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॿ") in bstack111lllll_opy_:
    for bstack1ll11lll1_opy_ in bstack111lllll_opy_[bstack1l1l_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩঀ")]:
      if bstack1ll11lll1_opy_ in options._preferences:
        options._preferences[bstack1ll11lll1_opy_] = update(options._preferences[bstack1ll11lll1_opy_], bstack111lllll_opy_[bstack1l1l_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪঁ")][bstack1ll11lll1_opy_])
      else:
        options.set_preference(bstack1ll11lll1_opy_, bstack111lllll_opy_[bstack1l1l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫং")][bstack1ll11lll1_opy_])
  if bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫঃ") in bstack111lllll_opy_:
    for arg in bstack111lllll_opy_[bstack1l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      options.add_argument(arg)
def bstack1l111111l_opy_(options, bstack11ll11ll1l_opy_):
  if bstack1l1l_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࠩঅ") in bstack11ll11ll1l_opy_:
    options.use_webview(bool(bstack11ll11ll1l_opy_[bstack1l1l_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࠪআ")]))
  bstack11ll1ll11l_opy_(options, bstack11ll11ll1l_opy_)
def bstack1ll1ll1l_opy_(options, bstack1ll1l11l1_opy_):
  for bstack111l11lll_opy_ in bstack1ll1l11l1_opy_:
    if bstack111l11lll_opy_ in [bstack1l1l_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧই"), bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ")]:
      continue
    options.set_capability(bstack111l11lll_opy_, bstack1ll1l11l1_opy_[bstack111l11lll_opy_])
  if bstack1l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪউ") in bstack1ll1l11l1_opy_:
    for arg in bstack1ll1l11l1_opy_[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡶࠫঊ")]:
      options.add_argument(arg)
  if bstack1l1l_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫঋ") in bstack1ll1l11l1_opy_:
    options.bstack111llllll_opy_(bool(bstack1ll1l11l1_opy_[bstack1l1l_opy_ (u"ࠨࡶࡨࡧ࡭ࡴ࡯࡭ࡱࡪࡽࡕࡸࡥࡷ࡫ࡨࡻࠬঌ")]))
def bstack11l111lll_opy_(options, bstack11l1ll1l11_opy_):
  for bstack1ll1ll1l1_opy_ in bstack11l1ll1l11_opy_:
    if bstack1ll1ll1l1_opy_ in [bstack1l1l_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭঍"), bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ঎")]:
      continue
    options._options[bstack1ll1ll1l1_opy_] = bstack11l1ll1l11_opy_[bstack1ll1ll1l1_opy_]
  if bstack1l1l_opy_ (u"ࠫࡦࡪࡤࡪࡶ࡬ࡳࡳࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨএ") in bstack11l1ll1l11_opy_:
    for bstack1ll11lll11_opy_ in bstack11l1ll1l11_opy_[bstack1l1l_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঐ")]:
      options.bstack1l1lll1l1l_opy_(
        bstack1ll11lll11_opy_, bstack11l1ll1l11_opy_[bstack1l1l_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ঑")][bstack1ll11lll11_opy_])
  if bstack1l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬ঒") in bstack11l1ll1l11_opy_:
    for arg in bstack11l1ll1l11_opy_[bstack1l1l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ও")]:
      options.add_argument(arg)
def bstack1ll1111l1l_opy_(options, caps):
  if not hasattr(options, bstack1l1l_opy_ (u"ࠩࡎࡉ࡞࠭ঔ")):
    return
  if options.KEY == bstack1l1l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨক"):
    options = bstack1lllllll11_opy_.bstack11111lll_opy_(bstack1ll1lllll_opy_=options, config=CONFIG)
  if options.KEY == bstack1l1l_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩখ") and options.KEY in caps:
    bstack11ll1ll11l_opy_(options, caps[bstack1l1l_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪগ")])
  elif options.KEY == bstack1l1l_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫঘ") and options.KEY in caps:
    bstack111lllll1l_opy_(options, caps[bstack1l1l_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬঙ")])
  elif options.KEY == bstack1l1l_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩচ") and options.KEY in caps:
    bstack1ll1ll1l_opy_(options, caps[bstack1l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪছ")])
  elif options.KEY == bstack1l1l_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫজ") and options.KEY in caps:
    bstack1l111111l_opy_(options, caps[bstack1l1l_opy_ (u"ࠫࡲࡹ࠺ࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬঝ")])
  elif options.KEY == bstack1l1l_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫঞ") and options.KEY in caps:
    bstack11l111lll_opy_(options, caps[bstack1l1l_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬট")])
def bstack1l11l11l11_opy_(caps):
  global bstack11l11l11l1_opy_
  if isinstance(os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨঠ")), str):
    bstack11l11l11l1_opy_ = eval(os.getenv(bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩড")))
  if bstack11l11l11l1_opy_:
    if bstack11ll11l1ll_opy_() < version.parse(bstack1l1l_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨঢ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1l1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪণ")
    if bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩত") in caps:
      browser = caps[bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪথ")]
    elif bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧদ") in caps:
      browser = caps[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨধ")]
    browser = str(browser).lower()
    if browser == bstack1l1l_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨন") or browser == bstack1l1l_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ঩"):
      browser = bstack1l1l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪপ")
    if browser == bstack1l1l_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬফ"):
      browser = bstack1l1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬব")
    if browser not in [bstack1l1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ভ"), bstack1l1l_opy_ (u"ࠧࡦࡦࡪࡩࠬম"), bstack1l1l_opy_ (u"ࠨ࡫ࡨࠫয"), bstack1l1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩর"), bstack1l1l_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ঱")]:
      return None
    try:
      package = bstack1l1l_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ল").format(browser)
      name = bstack1l1l_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭঳")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack111l11ll_opy_(options):
        return None
      for bstack1ll111llll_opy_ in caps.keys():
        options.set_capability(bstack1ll111llll_opy_, caps[bstack1ll111llll_opy_])
      bstack1ll1111l1l_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack11l1l1ll_opy_(options, bstack11lll1ll11_opy_):
  if not bstack111l11ll_opy_(options):
    return
  for bstack1ll111llll_opy_ in bstack11lll1ll11_opy_.keys():
    if bstack1ll111llll_opy_ in bstack1lll11llll_opy_:
      continue
    if bstack1ll111llll_opy_ in options._caps and type(options._caps[bstack1ll111llll_opy_]) in [dict, list]:
      options._caps[bstack1ll111llll_opy_] = update(options._caps[bstack1ll111llll_opy_], bstack11lll1ll11_opy_[bstack1ll111llll_opy_])
    else:
      options.set_capability(bstack1ll111llll_opy_, bstack11lll1ll11_opy_[bstack1ll111llll_opy_])
  bstack1ll1111l1l_opy_(options, bstack11lll1ll11_opy_)
  if bstack1l1l_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬ঴") in options._caps:
    if options._caps[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ঵")] and options._caps[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭শ")].lower() != bstack1l1l_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪষ"):
      del options._caps[bstack1l1l_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩস")]
def bstack1l1lll1ll1_opy_(proxy_config):
  if bstack1l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨহ") in proxy_config:
    proxy_config[bstack1l1l_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧ঺")] = proxy_config[bstack1l1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ঻")]
    del (proxy_config[bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼ়ࠫ")])
  if bstack1l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫঽ") in proxy_config and proxy_config[bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬা")].lower() != bstack1l1l_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪি"):
    proxy_config[bstack1l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧী")] = bstack1l1l_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬু")
  if bstack1l1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫূ") in proxy_config:
    proxy_config[bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪৃ")] = bstack1l1l_opy_ (u"ࠨࡲࡤࡧࠬৄ")
  return proxy_config
def bstack111llll1l1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ৅") in config:
    return proxy
  config[bstack1l1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ৆")] = bstack1l1lll1ll1_opy_(config[bstack1l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪে")])
  if proxy == None:
    proxy = Proxy(config[bstack1l1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫৈ")])
  return proxy
def bstack1l1l111l1l_opy_(self):
  global CONFIG
  global bstack1ll1l1ll1l_opy_
  try:
    proxy = bstack1l11ll1ll_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack1l1l_opy_ (u"࠭࠮ࡱࡣࡦࠫ৉")):
        proxies = bstack11l1111ll_opy_(proxy, bstack111lll11ll_opy_())
        if len(proxies) > 0:
          protocol, bstack11l11l111l_opy_ = proxies.popitem()
          if bstack1l1l_opy_ (u"ࠢ࠻࠱࠲ࠦ৊") in bstack11l11l111l_opy_:
            return bstack11l11l111l_opy_
          else:
            return bstack1l1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤো") + bstack11l11l111l_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨৌ").format(str(e)))
  return bstack1ll1l1ll1l_opy_(self)
def bstack11l1111l1_opy_():
  global CONFIG
  return bstack1l1l1l1l1_opy_(CONFIG) and bstack111ll1111_opy_() and bstack1llllll1l1_opy_() >= version.parse(bstack1llll11l_opy_)
def bstack1ll11ll1ll_opy_():
  global CONFIG
  return (bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ্࠭") in CONFIG or bstack1l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨৎ") in CONFIG) and bstack11llll11l1_opy_()
def bstack1lll11111_opy_(config):
  bstack1ll1l1lll_opy_ = {}
  if bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৏") in config:
    bstack1ll1l1lll_opy_ = config[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ৐")]
  if bstack1l1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৑") in config:
    bstack1ll1l1lll_opy_ = config[bstack1l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ৒")]
  proxy = bstack1l11ll1ll_opy_(config)
  if proxy:
    if proxy.endswith(bstack1l1l_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ৓")) and os.path.isfile(proxy):
      bstack1ll1l1lll_opy_[bstack1l1l_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭৔")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack1l1l_opy_ (u"ࠫ࠳ࡶࡡࡤࠩ৕")):
        proxies = bstack1l11l1ll1l_opy_(config, bstack111lll11ll_opy_())
        if len(proxies) > 0:
          protocol, bstack11l11l111l_opy_ = proxies.popitem()
          if bstack1l1l_opy_ (u"ࠧࡀ࠯࠰ࠤ৖") in bstack11l11l111l_opy_:
            parsed_url = urlparse(bstack11l11l111l_opy_)
          else:
            parsed_url = urlparse(protocol + bstack1l1l_opy_ (u"ࠨ࠺࠰࠱ࠥৗ") + bstack11l11l111l_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1ll1l1lll_opy_[bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡎ࡯ࡴࡶࠪ৘")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1ll1l1lll_opy_[bstack1l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫ৙")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1ll1l1lll_opy_[bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ৚")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1ll1l1lll_opy_[bstack1l1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭৛")] = str(parsed_url.password)
  return bstack1ll1l1lll_opy_
def bstack11ll111l1l_opy_(config):
  if bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠩড়") in config:
    return config[bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪঢ়")]
  return {}
def bstack1llll111ll_opy_(caps):
  global bstack1lllll1ll1_opy_
  if bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ৞") in caps:
    caps[bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨয়")][bstack1l1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧৠ")] = True
    if bstack1lllll1ll1_opy_:
      caps[bstack1l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪৡ")][bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬৢ")] = bstack1lllll1ll1_opy_
  else:
    caps[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩৣ")] = True
    if bstack1lllll1ll1_opy_:
      caps[bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭৤")] = bstack1lllll1ll1_opy_
@measure(event_name=EVENTS.bstack1l1l11l1l1_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1ll111l11l_opy_():
  global CONFIG
  if not bstack1l11ll1l11_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ৥") in CONFIG and bstack1l1l1111l1_opy_(CONFIG[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ০")]):
    if (
      bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ১") in CONFIG
      and bstack1l1l1111l1_opy_(CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭২")].get(bstack1l1l_opy_ (u"ࠪࡷࡰ࡯ࡰࡃ࡫ࡱࡥࡷࡿࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡣࡷ࡭ࡴࡴࠧ৩")))
    ):
      logger.debug(bstack1l1l_opy_ (u"ࠦࡑࡵࡣࡢ࡮ࠣࡦ࡮ࡴࡡࡳࡻࠣࡲࡴࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡣࡶࠤࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࡪࡴࡡࡣ࡮ࡨࡨࠧ৪"))
      return
    bstack1ll1l1lll_opy_ = bstack1lll11111_opy_(CONFIG)
    bstack1lll1l11l_opy_(CONFIG[bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ৫")], bstack1ll1l1lll_opy_)
def bstack1lll1l11l_opy_(key, bstack1ll1l1lll_opy_):
  global bstack111111ll_opy_
  logger.info(bstack1l1l11111_opy_)
  try:
    bstack111111ll_opy_ = Local()
    bstack1l11l1lll_opy_ = {bstack1l1l_opy_ (u"࠭࡫ࡦࡻࠪ৬"): key}
    bstack1l11l1lll_opy_.update(bstack1ll1l1lll_opy_)
    logger.debug(bstack1l11lll1l_opy_.format(str(bstack1l11l1lll_opy_)).replace(key, bstack1l1l_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫ৭")))
    bstack111111ll_opy_.start(**bstack1l11l1lll_opy_)
    if bstack111111ll_opy_.isRunning():
      logger.info(bstack11llll1l11_opy_)
  except Exception as e:
    bstack1ll1llll11_opy_(bstack11ll1l1l11_opy_.format(str(e)))
def bstack1lll11l1ll_opy_():
  global bstack111111ll_opy_
  if bstack111111ll_opy_.isRunning():
    logger.info(bstack1lll1llll_opy_)
    bstack111111ll_opy_.stop()
  bstack111111ll_opy_ = None
def bstack1l111l1lll_opy_(bstack1l1l1111ll_opy_=[]):
  global CONFIG
  bstack11l11lllll_opy_ = []
  bstack1l1lll11l_opy_ = [bstack1l1l_opy_ (u"ࠨࡱࡶࠫ৮"), bstack1l1l_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬ৯"), bstack1l1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧৰ"), bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ৱ"), bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ৲"), bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ৳")]
  try:
    for err in bstack1l1l1111ll_opy_:
      bstack11l1l111_opy_ = {}
      for k in bstack1l1lll11l_opy_:
        val = CONFIG[bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ৴")][int(err[bstack1l1l_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ৵")])].get(k)
        if val:
          bstack11l1l111_opy_[k] = val
      if(err[bstack1l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ৶")] != bstack1l1l_opy_ (u"ࠪࠫ৷")):
        bstack11l1l111_opy_[bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡵࠪ৸")] = {
          err[bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ৹")]: err[bstack1l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ৺")]
        }
        bstack11l11lllll_opy_.append(bstack11l1l111_opy_)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡳࡷࡳࡡࡵࡶ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࠺ࠡࠩ৻") + str(e))
  finally:
    return bstack11l11lllll_opy_
def bstack1lll1l1lll_opy_(file_name):
  bstack11l11lll11_opy_ = []
  try:
    bstack1lll111ll1_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack1lll111ll1_opy_):
      with open(bstack1lll111ll1_opy_) as f:
        bstack1111l1l1l_opy_ = json.load(f)
        bstack11l11lll11_opy_ = bstack1111l1l1l_opy_
      os.remove(bstack1lll111ll1_opy_)
    return bstack11l11lll11_opy_
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪ࡮ࡴࡤࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣࡰ࡮ࡹࡴ࠻ࠢࠪৼ") + str(e))
    return bstack11l11lll11_opy_
def bstack1l1l1lll_opy_():
  try:
      from bstack_utils.constants import bstack1ll1lll1_opy_, EVENTS
      from bstack_utils.helper import bstack11l11llll_opy_, get_host_info, bstack1l1ll1l1_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack111lllll11_opy_ = os.path.join(os.getcwd(), bstack1l1l_opy_ (u"ࠩ࡯ࡳ࡬࠭৽"), bstack1l1l_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭৾"))
      lock = FileLock(bstack111lllll11_opy_+bstack1l1l_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ৿"))
      def bstack1lll1111_opy_():
          try:
              with lock:
                  with open(bstack111lllll11_opy_, bstack1l1l_opy_ (u"ࠧࡸࠢ਀"), encoding=bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧਁ")) as file:
                      data = json.load(file)
                      config = {
                          bstack1l1l_opy_ (u"ࠢࡩࡧࡤࡨࡪࡸࡳࠣਂ"): {
                              bstack1l1l_opy_ (u"ࠣࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠢਃ"): bstack1l1l_opy_ (u"ࠤࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠧ਄"),
                          }
                      }
                      bstack1ll111ll_opy_ = datetime.utcnow()
                      bstack1111lllll_opy_ = bstack1ll111ll_opy_.strftime(bstack1l1l_opy_ (u"ࠥࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨ࡙࡙ࠣࡉࠢਅ"))
                      bstack1l11ll1l1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩਆ")) if os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪਇ")) else bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣਈ"))
                      payload = {
                          bstack1l1l_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠦਉ"): bstack1l1l_opy_ (u"ࠣࡵࡧ࡯ࡤ࡫ࡶࡦࡰࡷࡷࠧਊ"),
                          bstack1l1l_opy_ (u"ࠤࡧࡥࡹࡧࠢ਋"): {
                              bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡺࡻࡩࡥࠤ਌"): bstack1l11ll1l1_opy_,
                              bstack1l1l_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡨࡤࡪࡡࡺࠤ਍"): bstack1111lllll_opy_,
                              bstack1l1l_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࠤ਎"): bstack1l1l_opy_ (u"ࠨࡓࡅࡍࡉࡩࡦࡺࡵࡳࡧࡓࡩࡷ࡬࡯ࡳ࡯ࡤࡲࡨ࡫ࠢਏ"),
                              bstack1l1l_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡪࡴࡱࡱࠦਐ"): {
                                  bstack1l1l_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࡵࠥ਑"): data,
                                  bstack1l1l_opy_ (u"ࠤࡶࡨࡰࡘࡵ࡯ࡋࡧࠦ਒"): bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧਓ"))
                              },
                              bstack1l1l_opy_ (u"ࠦࡺࡹࡥࡳࡡࡧࡥࡹࡧࠢਔ"): bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠧࡻࡳࡦࡴࡑࡥࡲ࡫ࠢਕ")),
                              bstack1l1l_opy_ (u"ࠨࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠤਖ"): get_host_info()
                          }
                      }
                      bstack1l11lllll_opy_ = bstack1ll1lll111_opy_(cli.config, [bstack1l1l_opy_ (u"ࠢࡢࡲ࡬ࡷࠧਗ"), bstack1l1l_opy_ (u"ࠣࡧࡧࡷࡎࡴࡳࡵࡴࡸࡱࡪࡴࡴࡢࡶ࡬ࡳࡳࠨਘ"), bstack1l1l_opy_ (u"ࠤࡤࡴ࡮ࠨਙ")], bstack1ll1lll1_opy_)
                      response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"ࠥࡔࡔ࡙ࡔࠣਚ"), bstack1l11lllll_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack1l1l_opy_ (u"ࠦࡉࡧࡴࡢࠢࡶࡩࡳࡺࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡴࡰࠢࡾࢁࠥࡽࡩࡵࡪࠣࡨࡦࡺࡡࠡࡽࢀࠦਛ").format(bstack1ll1lll1_opy_, payload))
                      else:
                          logger.debug(bstack1l1l_opy_ (u"ࠧࡘࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡦࡰࡴࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡩࡧࡴࡢࠢࡾࢁࠧਜ").format(bstack1ll1lll1_opy_, payload))
          except Exception as e:
              logger.debug(bstack1l1l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡳࡪࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠࡼࡿࠥਝ").format(e))
      bstack1lll1111_opy_()
      bstack1ll111111l_opy_(bstack111lllll11_opy_, logger)
  except:
    pass
def bstack111ll11ll_opy_():
  global bstack11l11ll11_opy_
  global bstack1l11l11l_opy_
  global bstack1ll1111l11_opy_
  global bstack1l1l11llll_opy_
  global bstack1lll111ll_opy_
  global bstack11l1lll1l1_opy_
  global CONFIG
  bstack111lllllll_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਞ"))
  if bstack111lllllll_opy_ in [bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧਟ"), bstack1l1l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨਠ")]:
    bstack1llll11l11_opy_()
  percy.shutdown()
  if bstack11l11ll11_opy_:
    logger.warning(bstack1l1ll111l1_opy_.format(str(bstack11l11ll11_opy_)))
  else:
    try:
      bstack11ll1l1111_opy_ = bstack1ll11llll_opy_(bstack1l1l_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩਡ"), logger)
      if bstack11ll1l1111_opy_.get(bstack1l1l_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩਢ")) and bstack11ll1l1111_opy_.get(bstack1l1l_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪਣ")).get(bstack1l1l_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨਤ")):
        logger.warning(bstack1l1ll111l1_opy_.format(str(bstack11ll1l1111_opy_[bstack1l1l_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬਥ")][bstack1l1l_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪਦ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack111l111l_opy_.invoke(bstack11l111111_opy_.bstack1llll11l1l_opy_)
  logger.info(bstack11l1l1l111_opy_)
  global bstack111111ll_opy_
  if bstack111111ll_opy_:
    bstack1lll11l1ll_opy_()
  try:
    with bstack1l111l1ll_opy_:
      bstack111lll1lll_opy_ = bstack1l11l11l_opy_.copy()
    for driver in bstack111lll1lll_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1ll1l1l1_opy_)
  if bstack11l1lll1l1_opy_ == bstack1l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨਧ"):
    bstack1lll111ll_opy_ = bstack1lll1l1lll_opy_(bstack1l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਨ"))
  if bstack11l1lll1l1_opy_ == bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ਩") and len(bstack1l1l11llll_opy_) == 0:
    bstack1l1l11llll_opy_ = bstack1lll1l1lll_opy_(bstack1l1l_opy_ (u"ࠬࡶࡷࡠࡲࡼࡸࡪࡹࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪਪ"))
    if len(bstack1l1l11llll_opy_) == 0:
      bstack1l1l11llll_opy_ = bstack1lll1l1lll_opy_(bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬਫ"))
  bstack1l11l1l1_opy_ = bstack1l1l_opy_ (u"ࠧࠨਬ")
  if len(bstack1ll1111l11_opy_) > 0:
    bstack1l11l1l1_opy_ = bstack1l111l1lll_opy_(bstack1ll1111l11_opy_)
  elif len(bstack1l1l11llll_opy_) > 0:
    bstack1l11l1l1_opy_ = bstack1l111l1lll_opy_(bstack1l1l11llll_opy_)
  elif len(bstack1lll111ll_opy_) > 0:
    bstack1l11l1l1_opy_ = bstack1l111l1lll_opy_(bstack1lll111ll_opy_)
  elif len(bstack1lll11111l_opy_) > 0:
    bstack1l11l1l1_opy_ = bstack1l111l1lll_opy_(bstack1lll11111l_opy_)
  if bool(bstack1l11l1l1_opy_):
    bstack1l11llll1l_opy_(bstack1l11l1l1_opy_)
  else:
    bstack1l11llll1l_opy_()
  bstack1ll111111l_opy_(bstack1l1l1ll11_opy_, logger)
  if bstack111lllllll_opy_ not in [bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩਭ")]:
    bstack1l1l1lll_opy_()
  bstack1lllllll1l_opy_.bstack1llll11lll_opy_(CONFIG)
  if len(bstack1lll111ll_opy_) > 0:
    sys.exit(len(bstack1lll111ll_opy_))
def bstack1ll11l1l1l_opy_(bstack1ll11llll1_opy_, frame):
  global bstack1l1ll1l1_opy_
  logger.error(bstack1111ll111_opy_)
  bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬਮ"), bstack1ll11llll1_opy_)
  if hasattr(signal, bstack1l1l_opy_ (u"ࠪࡗ࡮࡭࡮ࡢ࡮ࡶࠫਯ")):
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫਰ"), signal.Signals(bstack1ll11llll1_opy_).name)
  else:
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ਱"), bstack1l1l_opy_ (u"࠭ࡓࡊࡉࡘࡒࡐࡔࡏࡘࡐࠪਲ"))
  if cli.is_running():
    bstack111l111l_opy_.invoke(bstack11l111111_opy_.bstack1llll11l1l_opy_)
  bstack111lllllll_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਲ਼"))
  if bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ਴") and not cli.is_enabled(CONFIG):
    bstack11l1llllll_opy_.stop(bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩਵ")))
  bstack111ll11ll_opy_()
  sys.exit(1)
def bstack1ll1llll11_opy_(err):
  logger.critical(bstack1l1l1l1ll_opy_.format(str(err)))
  bstack1l11llll1l_opy_(bstack1l1l1l1ll_opy_.format(str(err)), True)
  atexit.unregister(bstack111ll11ll_opy_)
  bstack1llll11l11_opy_()
  sys.exit(1)
def bstack1l1111ll_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1l11llll1l_opy_(message, True)
  atexit.unregister(bstack111ll11ll_opy_)
  bstack1llll11l11_opy_()
  sys.exit(1)
def bstack11l11l1l_opy_():
  global CONFIG
  global bstack1l1ll1ll11_opy_
  global bstack11l11l11l_opy_
  global bstack1l1lll11l1_opy_
  CONFIG = bstack1ll1llllll_opy_()
  load_dotenv(CONFIG.get(bstack1l1l_opy_ (u"ࠪࡩࡳࡼࡆࡪ࡮ࡨࠫਸ਼")))
  bstack1lllll1ll_opy_()
  bstack1l1l1lll11_opy_()
  CONFIG = bstack1l1llll11l_opy_(CONFIG)
  update(CONFIG, bstack11l11l11l_opy_)
  update(CONFIG, bstack1l1ll1ll11_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack1l1l11ll1l_opy_(CONFIG)
  bstack1l1lll11l1_opy_ = bstack1l11ll1l11_opy_(CONFIG)
  os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧ਷")] = bstack1l1lll11l1_opy_.__str__().lower()
  bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ਸ"), bstack1l1lll11l1_opy_)
  if (bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩਹ") in CONFIG and bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ਺") in bstack1l1ll1ll11_opy_) or (
          bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ਻") in CONFIG and bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ਼ࠬ") not in bstack11l11l11l_opy_):
    if os.getenv(bstack1l1l_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ਽")):
      CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ਾ")] = os.getenv(bstack1l1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩਿ"))
    else:
      if not CONFIG.get(bstack1l1l_opy_ (u"ࠨࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠤੀ"), bstack1l1l_opy_ (u"ࠢࠣੁ")) in bstack1111l1ll1_opy_:
        bstack1l1llllll_opy_()
  elif (bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫੂ") not in CONFIG and bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ੃") in CONFIG) or (
          bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭੄") in bstack11l11l11l_opy_ and bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ੅") not in bstack1l1ll1ll11_opy_):
    del (CONFIG[bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ੆")])
  if bstack1ll1111ll1_opy_(CONFIG):
    bstack1ll1llll11_opy_(bstack1l1l1l1l1l_opy_)
  Config.bstack1l1ll1l111_opy_().bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠨࡵࡴࡧࡵࡒࡦࡳࡥࠣੇ"), CONFIG[bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩੈ")])
  bstack1ll1l1ll1_opy_()
  bstack11l1l1l1l_opy_()
  if bstack11l11l11l1_opy_ and not CONFIG.get(bstack1l1l_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦ੉"), bstack1l1l_opy_ (u"ࠤࠥ੊")) in bstack1111l1ll1_opy_:
    CONFIG[bstack1l1l_opy_ (u"ࠪࡥࡵࡶࠧੋ")] = bstack1l11ll11l1_opy_(CONFIG)
    logger.info(bstack1l1l1l1111_opy_.format(CONFIG[bstack1l1l_opy_ (u"ࠫࡦࡶࡰࠨੌ")]))
  if not bstack1l1lll11l1_opy_:
    CONFIG[bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ੍")] = [{}]
def bstack111lll11l_opy_(config, bstack11ll11ll1_opy_):
  global CONFIG
  global bstack11l11l11l1_opy_
  CONFIG = config
  bstack11l11l11l1_opy_ = bstack11ll11ll1_opy_
def bstack11l1l1l1l_opy_():
  global CONFIG
  global bstack11l11l11l1_opy_
  if bstack1l1l_opy_ (u"࠭ࡡࡱࡲࠪ੎") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack11l11l11ll_opy_)
    bstack11l11l11l1_opy_ = True
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭੏"), True)
def bstack1l11ll11l1_opy_(config):
  bstack1l1111ll1_opy_ = bstack1l1l_opy_ (u"ࠨࠩ੐")
  app = config[bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࠭ੑ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack111l1lll_opy_:
      if os.path.exists(app):
        bstack1l1111ll1_opy_ = bstack1l1111l1l_opy_(config, app)
      elif bstack1l1lll1111_opy_(app):
        bstack1l1111ll1_opy_ = app
      else:
        bstack1ll1llll11_opy_(bstack11lll111ll_opy_.format(app))
    else:
      if bstack1l1lll1111_opy_(app):
        bstack1l1111ll1_opy_ = app
      elif os.path.exists(app):
        bstack1l1111ll1_opy_ = bstack1l1111l1l_opy_(app)
      else:
        bstack1ll1llll11_opy_(bstack1llllllll_opy_)
  else:
    if len(app) > 2:
      bstack1ll1llll11_opy_(bstack11111l11_opy_)
    elif len(app) == 2:
      if bstack1l1l_opy_ (u"ࠪࡴࡦࡺࡨࠨ੒") in app and bstack1l1l_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧ੓") in app:
        if os.path.exists(app[bstack1l1l_opy_ (u"ࠬࡶࡡࡵࡪࠪ੔")]):
          bstack1l1111ll1_opy_ = bstack1l1111l1l_opy_(config, app[bstack1l1l_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ੕")], app[bstack1l1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ੖")])
        else:
          bstack1ll1llll11_opy_(bstack11lll111ll_opy_.format(app))
      else:
        bstack1ll1llll11_opy_(bstack11111l11_opy_)
    else:
      for key in app:
        if key in bstack1ll11lll1l_opy_:
          if key == bstack1l1l_opy_ (u"ࠨࡲࡤࡸ࡭࠭੗"):
            if os.path.exists(app[key]):
              bstack1l1111ll1_opy_ = bstack1l1111l1l_opy_(config, app[key])
            else:
              bstack1ll1llll11_opy_(bstack11lll111ll_opy_.format(app))
          else:
            bstack1l1111ll1_opy_ = app[key]
        else:
          bstack1ll1llll11_opy_(bstack11ll1111_opy_)
  return bstack1l1111ll1_opy_
def bstack1l1lll1111_opy_(bstack1l1111ll1_opy_):
  import re
  bstack11l1llll1l_opy_ = re.compile(bstack1l1l_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤ੘"))
  bstack11ll1111l1_opy_ = re.compile(bstack1l1l_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫ࠱࡞ࡥ࠲ࢀࡁ࠮࡜࠳࠱࠾ࡢ࡟࠯࡞࠰ࡡ࠯ࠪࠢਖ਼"))
  if bstack1l1l_opy_ (u"ࠫࡧࡹ࠺࠰࠱ࠪਗ਼") in bstack1l1111ll1_opy_ or re.fullmatch(bstack11l1llll1l_opy_, bstack1l1111ll1_opy_) or re.fullmatch(bstack11ll1111l1_opy_, bstack1l1111ll1_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack1111l1111_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1l1111l1l_opy_(config, path, bstack1lll11ll_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1l1l_opy_ (u"ࠬࡸࡢࠨਜ਼")).read()).hexdigest()
  bstack1ll1lll1ll_opy_ = bstack11l11ll1l_opy_(md5_hash)
  bstack1l1111ll1_opy_ = None
  if bstack1ll1lll1ll_opy_:
    logger.info(bstack1l11111ll_opy_.format(bstack1ll1lll1ll_opy_, md5_hash))
    return bstack1ll1lll1ll_opy_
  bstack1ll111l1_opy_ = datetime.datetime.now()
  bstack111ll111l_opy_ = MultipartEncoder(
    fields={
      bstack1l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࠫੜ"): (os.path.basename(path), open(os.path.abspath(path), bstack1l1l_opy_ (u"ࠧࡳࡤࠪ੝")), bstack1l1l_opy_ (u"ࠨࡶࡨࡼࡹ࠵ࡰ࡭ࡣ࡬ࡲࠬਫ਼")),
      bstack1l1l_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ੟"): bstack1lll11ll_opy_
    }
  )
  response = requests.post(bstack11lll111l_opy_, data=bstack111ll111l_opy_,
                           headers={bstack1l1l_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ੠"): bstack111ll111l_opy_.content_type},
                           auth=(config[bstack1l1l_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭੡")], config[bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ੢")]))
  try:
    res = json.loads(response.text)
    bstack1l1111ll1_opy_ = res[bstack1l1l_opy_ (u"࠭ࡡࡱࡲࡢࡹࡷࡲࠧ੣")]
    logger.info(bstack1l11ll11ll_opy_.format(bstack1l1111ll1_opy_))
    bstack1l1llll1l1_opy_(md5_hash, bstack1l1111ll1_opy_)
    cli.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴ࠿ࡻࡰ࡭ࡱࡤࡨࡤࡧࡰࡱࠤ੤"), datetime.datetime.now() - bstack1ll111l1_opy_)
  except ValueError as err:
    bstack1ll1llll11_opy_(bstack11lll1llll_opy_.format(str(err)))
  return bstack1l1111ll1_opy_
def bstack1ll1l1ll1_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack111111111_opy_
  bstack1lll111l11_opy_ = 1
  bstack11lllll111_opy_ = 1
  if bstack1l1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੥") in CONFIG:
    bstack11lllll111_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ੦")]
  else:
    bstack11lllll111_opy_ = bstack1ll1ll11l1_opy_(framework_name, args) or 1
  if bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭੧") in CONFIG:
    bstack1lll111l11_opy_ = len(CONFIG[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੨")])
  bstack111111111_opy_ = int(bstack11lllll111_opy_) * int(bstack1lll111l11_opy_)
def bstack1ll1ll11l1_opy_(framework_name, args):
  if framework_name == bstack1l11l11l1l_opy_ and args and bstack1l1l_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ੩") in args:
      bstack1lll1lll_opy_ = args.index(bstack1l1l_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫ੪"))
      return int(args[bstack1lll1lll_opy_ + 1]) or 1
  return 1
def bstack11l11ll1l_opy_(md5_hash):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠢࡱࡳࡹࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡥࡥࡸ࡯ࡣࠡࡨ࡬ࡰࡪࠦ࡯ࡱࡧࡵࡥࡹ࡯࡯࡯ࡵࠪ੫"))
    bstack11ll11l1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠨࢀࠪ੬")), bstack1l1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ੭"), bstack1l1l_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ੮"))
    if os.path.exists(bstack11ll11l1_opy_):
      try:
        bstack1ll11lll_opy_ = json.load(open(bstack11ll11l1_opy_, bstack1l1l_opy_ (u"ࠫࡷࡨࠧ੯")))
        if md5_hash in bstack1ll11lll_opy_:
          bstack11ll1l1l_opy_ = bstack1ll11lll_opy_[md5_hash]
          bstack11lllllll1_opy_ = datetime.datetime.now()
          bstack1l11l1l11_opy_ = datetime.datetime.strptime(bstack11ll1l1l_opy_[bstack1l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨੰ")], bstack1l1l_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪੱ"))
          if (bstack11lllllll1_opy_ - bstack1l11l1l11_opy_).days > 30:
            return None
          elif version.parse(str(__version__)) > version.parse(bstack11ll1l1l_opy_[bstack1l1l_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬੲ")]):
            return None
          return bstack11ll1l1l_opy_[bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫੳ")]
      except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡐࡈ࠺ࠦࡨࡢࡵ࡫ࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂ࠭ੴ").format(str(e)))
    return None
  bstack11ll11l1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠪࢂࠬੵ")), bstack1l1l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ੶"), bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭੷"))
  lock_file = bstack11ll11l1_opy_ + bstack1l1l_opy_ (u"࠭࠮࡭ࡱࡦ࡯ࠬ੸")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack11ll11l1_opy_):
        with open(bstack11ll11l1_opy_, bstack1l1l_opy_ (u"ࠧࡳࠩ੹")) as f:
          content = f.read().strip()
          if content:
            bstack1ll11lll_opy_ = json.loads(content)
            if md5_hash in bstack1ll11lll_opy_:
              bstack11ll1l1l_opy_ = bstack1ll11lll_opy_[md5_hash]
              bstack11lllllll1_opy_ = datetime.datetime.now()
              bstack1l11l1l11_opy_ = datetime.datetime.strptime(bstack11ll1l1l_opy_[bstack1l1l_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ੺")], bstack1l1l_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭੻"))
              if (bstack11lllllll1_opy_ - bstack1l11l1l11_opy_).days > 30:
                return None
              elif version.parse(str(__version__)) > version.parse(bstack11ll1l1l_opy_[bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ੼")]):
                return None
              return bstack11ll1l1l_opy_[bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧ੽")]
      return None
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧࠡࡨࡲࡶࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮࠺ࠡࡽࢀࠫ੾").format(str(e)))
    return None
def bstack1l1llll1l1_opy_(md5_hash, bstack1l1111ll1_opy_):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ੿"))
    bstack1l11lll11l_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠧࡿࠩ઀")), bstack1l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨઁ"))
    if not os.path.exists(bstack1l11lll11l_opy_):
      os.makedirs(bstack1l11lll11l_opy_)
    bstack11ll11l1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠩࢁࠫં")), bstack1l1l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪઃ"), bstack1l1l_opy_ (u"ࠫࡦࡶࡰࡖࡲ࡯ࡳࡦࡪࡍࡅ࠷ࡋࡥࡸ࡮࠮࡫ࡵࡲࡲࠬ઄"))
    bstack1l1l111ll1_opy_ = {
      bstack1l1l_opy_ (u"ࠬ࡯ࡤࠨઅ"): bstack1l1111ll1_opy_,
      bstack1l1l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩઆ"): datetime.datetime.strftime(datetime.datetime.now(), bstack1l1l_opy_ (u"ࠧࠦࡦ࠲ࠩࡲ࠵࡚ࠥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫઇ")),
      bstack1l1l_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ઈ"): str(__version__)
    }
    try:
      bstack1ll11lll_opy_ = {}
      if os.path.exists(bstack11ll11l1_opy_):
        bstack1ll11lll_opy_ = json.load(open(bstack11ll11l1_opy_, bstack1l1l_opy_ (u"ࠩࡵࡦࠬઉ")))
      bstack1ll11lll_opy_[md5_hash] = bstack1l1l111ll1_opy_
      with open(bstack11ll11l1_opy_, bstack1l1l_opy_ (u"ࠥࡻ࠰ࠨઊ")) as outfile:
        json.dump(bstack1ll11lll_opy_, outfile)
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡪࡡࡵ࡫ࡱ࡫ࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮ࠠࡧ࡫࡯ࡩ࠿ࠦࡻࡾࠩઋ").format(str(e)))
    return
  bstack1l11lll11l_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠬࢄࠧઌ")), bstack1l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ઍ"))
  if not os.path.exists(bstack1l11lll11l_opy_):
    os.makedirs(bstack1l11lll11l_opy_)
  bstack11ll11l1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠧࡿࠩ઎")), bstack1l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨએ"), bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪઐ"))
  lock_file = bstack11ll11l1_opy_ + bstack1l1l_opy_ (u"ࠪ࠲ࡱࡵࡣ࡬ࠩઑ")
  bstack1l1l111ll1_opy_ = {
    bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧ઒"): bstack1l1111ll1_opy_,
    bstack1l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨઓ"): datetime.datetime.strftime(datetime.datetime.now(), bstack1l1l_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪઔ")),
    bstack1l1l_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬક"): str(__version__)
  }
  try:
    with FileLock(lock_file, timeout=10):
      bstack1ll11lll_opy_ = {}
      if os.path.exists(bstack11ll11l1_opy_):
        with open(bstack11ll11l1_opy_, bstack1l1l_opy_ (u"ࠨࡴࠪખ")) as f:
          content = f.read().strip()
          if content:
            bstack1ll11lll_opy_ = json.loads(content)
      bstack1ll11lll_opy_[md5_hash] = bstack1l1l111ll1_opy_
      with open(bstack11ll11l1_opy_, bstack1l1l_opy_ (u"ࠤࡺࠦગ")) as outfile:
        json.dump(bstack1ll11lll_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡭ࡹ࡮ࠠࡧ࡫࡯ࡩࠥࡲ࡯ࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡑࡉ࠻ࠠࡩࡣࡶ࡬ࠥࡻࡰࡥࡣࡷࡩ࠿ࠦࡻࡾࠩઘ").format(str(e)))
def bstack1l11111ll1_opy_(self):
  return
def bstack1l1l11l1_opy_(self):
  return
def bstack1lllll111_opy_():
  global bstack11l1l1111l_opy_
  bstack11l1l1111l_opy_ = True
@measure(event_name=EVENTS.bstack11l1l111ll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11l1111l1l_opy_(self):
  global bstack1lll1l11l1_opy_
  global bstack1lll1lll1_opy_
  global bstack11l1lll111_opy_
  try:
    if bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫઙ") in bstack1lll1l11l1_opy_ and self.session_id != None and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩચ"), bstack1l1l_opy_ (u"࠭ࠧછ")) != bstack1l1l_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨજ"):
      bstack11l11l1111_opy_ = bstack1l1l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨઝ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩઞ")
      if bstack11l11l1111_opy_ == bstack1l1l_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪટ"):
        bstack11ll11lll_opy_(logger)
      if self != None:
        bstack11ll11111_opy_(self, bstack11l11l1111_opy_, bstack1l1l_opy_ (u"ࠫ࠱ࠦࠧઠ").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack1l1l_opy_ (u"ࠬ࠭ડ")
    if bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ઢ") in bstack1lll1l11l1_opy_ and getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ણ"), None):
      bstack1l11111l1_opy_.bstack1ll1lllll1_opy_(self, bstack11l11l1ll_opy_, logger, wait=True)
    if bstack1l1l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨત") in bstack1lll1l11l1_opy_:
      if not threading.currentThread().behave_test_status:
        bstack11ll11111_opy_(self, bstack1l1l_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤથ"))
      bstack11ll111ll1_opy_.bstack111l1l1ll_opy_(self)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦદ") + str(e))
  bstack11l1lll111_opy_(self)
  self.session_id = None
def bstack11llll111_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1ll11111_opy_
    global bstack1lll1l11l1_opy_
    command_executor = kwargs.get(bstack1l1l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧધ"), bstack1l1l_opy_ (u"ࠬ࠭ન"))
    bstack11l1ll1l_opy_ = False
    if type(command_executor) == str and bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ઩") in command_executor:
      bstack11l1ll1l_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪપ") in str(getattr(command_executor, bstack1l1l_opy_ (u"ࠨࡡࡸࡶࡱ࠭ફ"), bstack1l1l_opy_ (u"ࠩࠪબ"))):
      bstack11l1ll1l_opy_ = True
    else:
      kwargs = bstack1lllllll11_opy_.bstack11111lll_opy_(bstack1ll1lllll_opy_=kwargs, config=CONFIG)
      return bstack111ll1l1l_opy_(self, *args, **kwargs)
    if bstack11l1ll1l_opy_:
      bstack1l1ll11l1l_opy_ = bstack1ll11ll1l_opy_.bstack11lll1ll_opy_(CONFIG, bstack1lll1l11l1_opy_)
      if kwargs.get(bstack1l1l_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫભ")):
        kwargs[bstack1l1l_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬમ")] = bstack1ll11111_opy_(kwargs[bstack1l1l_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭ય")], bstack1lll1l11l1_opy_, CONFIG, bstack1l1ll11l1l_opy_)
      elif kwargs.get(bstack1l1l_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ર")):
        kwargs[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ઱")] = bstack1ll11111_opy_(kwargs[bstack1l1l_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨલ")], bstack1lll1l11l1_opy_, CONFIG, bstack1l1ll11l1l_opy_)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤળ").format(str(e)))
  return bstack111ll1l1l_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack1ll1l1l1l1_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1lllll11ll_opy_(self, command_executor=bstack1l1l_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦ઴"), *args, **kwargs):
  global bstack1lll1lll1_opy_
  global bstack1l11l11l_opy_
  bstack1llll11ll1_opy_ = bstack11llll111_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack1l1ll11111_opy_.on():
    return bstack1llll11ll1_opy_
  try:
    logger.debug(bstack1l1l_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨવ").format(str(command_executor)))
    logger.debug(bstack1l1l_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧશ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩષ") in command_executor._url:
      bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨસ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫહ") in command_executor):
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ઺"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack111lll111l_opy_ = getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ઻"), None)
  bstack1l1lll1lll_opy_ = {}
  if self.capabilities is not None:
    bstack1l1lll1lll_opy_[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧ઼ࠪ")] = self.capabilities.get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪઽ"))
    bstack1l1lll1lll_opy_[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨા")] = self.capabilities.get(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨિ"))
    bstack1l1lll1lll_opy_[bstack1l1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩી")] = self.capabilities.get(bstack1l1l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧુ"))
  if CONFIG.get(bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૂ"), False) and bstack1lllllll11_opy_.bstack1lll11l1l_opy_(bstack1l1lll1lll_opy_):
    threading.current_thread().a11yPlatform = True
  if bstack1l1l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫૃ") in bstack1lll1l11l1_opy_ or bstack1l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫૄ") in bstack1lll1l11l1_opy_:
    bstack11l1llllll_opy_.bstack111ll1llll_opy_(self)
  if bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ૅ") in bstack1lll1l11l1_opy_ and bstack111lll111l_opy_ and bstack111lll111l_opy_.get(bstack1l1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ૆"), bstack1l1l_opy_ (u"ࠨࠩે")) == bstack1l1l_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪૈ"):
    bstack11l1llllll_opy_.bstack111ll1llll_opy_(self)
  bstack1lll1lll1_opy_ = self.session_id
  with bstack1l111l1ll_opy_:
    bstack1l11l11l_opy_.append(self)
  return bstack1llll11ll1_opy_
def bstack11ll1l11l1_opy_(args):
  return bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫૉ") in str(args)
def bstack11ll1ll11_opy_(self, driver_command, *args, **kwargs):
  global bstack11l1lll1ll_opy_
  global bstack1l1l1ll111_opy_
  bstack11l11ll1_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ૊"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫો"), None)
  bstack1lllllllll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ૌ"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮્ࠩ"), None)
  bstack1ll11l1l1_opy_ = getattr(self, bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ૎"), None) != None and getattr(self, bstack1l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ૏"), None) == True
  if not bstack1l1l1ll111_opy_ and bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૐ") in CONFIG and CONFIG[bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ૑")] == True and bstack111111lll_opy_.bstack1ll1l1111_opy_(driver_command) and (bstack1ll11l1l1_opy_ or bstack11l11ll1_opy_ or bstack1lllllllll_opy_) and not bstack11ll1l11l1_opy_(args):
    try:
      bstack1l1l1ll111_opy_ = True
      logger.debug(bstack1l1l_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࢀࢃࠧ૒").format(driver_command))
      logger.debug(perform_scan(self, driver_command=driver_command))
    except Exception as err:
      logger.debug(bstack1l1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡩࡷ࡬࡯ࡳ࡯ࠣࡷࡨࡧ࡮ࠡࡽࢀࠫ૓").format(str(err)))
    bstack1l1l1ll111_opy_ = False
  response = bstack11l1lll1ll_opy_(self, driver_command, *args, **kwargs)
  if (bstack1l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭૔") in str(bstack1lll1l11l1_opy_).lower() or bstack1l1l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ૕") in str(bstack1lll1l11l1_opy_).lower()) and bstack1l1ll11111_opy_.on():
    try:
      if driver_command == bstack1l1l_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭૖"):
        bstack11l1llllll_opy_.bstack1ll11l111l_opy_({
            bstack1l1l_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩ૗"): response[bstack1l1l_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪ૘")],
            bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ૙"): bstack11l1llllll_opy_.current_test_uuid() if bstack11l1llllll_opy_.current_test_uuid() else bstack1l1ll11111_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack111l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack111lll1ll1_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1lll1lll1_opy_
  global bstack1ll1ll1l11_opy_
  global bstack11ll11ll_opy_
  global bstack1l1ll11lll_opy_
  global bstack1ll1ll111l_opy_
  global bstack1lll1l11l1_opy_
  global bstack111ll1l1l_opy_
  global bstack1l11l11l_opy_
  global bstack1111l1ll_opy_
  global bstack11l11l1ll_opy_
  if os.getenv(bstack1l1l_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ૚")) is not None and bstack1lllllll11_opy_.bstack1l11llll_opy_(CONFIG) is None:
    CONFIG[bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ૛")] = True
  CONFIG[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ૜")] = str(bstack1lll1l11l1_opy_) + str(__version__)
  bstack1l11111l_opy_ = os.environ[bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ૝")]
  bstack1l1ll11l1l_opy_ = bstack1ll11ll1l_opy_.bstack11lll1ll_opy_(CONFIG, bstack1lll1l11l1_opy_)
  CONFIG[bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭૞")] = bstack1l11111l_opy_
  CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭૟")] = bstack1l1ll11l1l_opy_
  if CONFIG.get(bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬૠ"),bstack1l1l_opy_ (u"࠭ࠧૡ")) and bstack1l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ૢ") in bstack1lll1l11l1_opy_:
    CONFIG[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨૣ")].pop(bstack1l1l_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ૤"), None)
    CONFIG[bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ૥")].pop(bstack1l1l_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩ૦"), None)
  command_executor = bstack111lll11ll_opy_()
  logger.debug(bstack1ll1lll11l_opy_.format(command_executor))
  proxy = bstack111llll1l1_opy_(CONFIG, proxy)
  bstack1111lll1l_opy_ = 0 if bstack1ll1ll1l11_opy_ < 0 else bstack1ll1ll1l11_opy_
  try:
    if bstack1l1ll11lll_opy_ is True:
      bstack1111lll1l_opy_ = int(multiprocessing.current_process().name)
    elif bstack1ll1ll111l_opy_ is True:
      bstack1111lll1l_opy_ = int(threading.current_thread().name)
  except:
    bstack1111lll1l_opy_ = 0
  bstack11lll1ll11_opy_ = bstack1l111lll1_opy_(CONFIG, bstack1111lll1l_opy_)
  logger.debug(bstack1l11ll1ll1_opy_.format(str(bstack11lll1ll11_opy_)))
  if bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ૧") in CONFIG and bstack1l1l1111l1_opy_(CONFIG[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ૨")]):
    bstack1llll111ll_opy_(bstack11lll1ll11_opy_)
  if bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1111lll1l_opy_) and bstack1lllllll11_opy_.bstack1111ll1l_opy_(bstack11lll1ll11_opy_, options, desired_capabilities, CONFIG):
    threading.current_thread().a11yPlatform = True
    if (cli.accessibility is None or not cli.accessibility.is_enabled()):
      bstack1lllllll11_opy_.set_capabilities(bstack11lll1ll11_opy_, CONFIG)
  if desired_capabilities:
    bstack1lll1l1ll1_opy_ = bstack1l1llll11l_opy_(desired_capabilities)
    bstack1lll1l1ll1_opy_[bstack1l1l_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ૩")] = bstack1llll11l1_opy_(CONFIG)
    bstack1lll1111l1_opy_ = bstack1l111lll1_opy_(bstack1lll1l1ll1_opy_)
    if bstack1lll1111l1_opy_:
      bstack11lll1ll11_opy_ = update(bstack1lll1111l1_opy_, bstack11lll1ll11_opy_)
    desired_capabilities = None
  if options:
    bstack11l1l1ll_opy_(options, bstack11lll1ll11_opy_)
  if not options:
    options = bstack1l11l11l11_opy_(bstack11lll1ll11_opy_)
  bstack11l11l1ll_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૪"))[bstack1111lll1l_opy_]
  if proxy and bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ૫")):
    options.proxy(proxy)
  if options and bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ૬")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1llllll1l1_opy_() < version.parse(bstack1l1l_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪ૭")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11lll1ll11_opy_)
  logger.info(bstack11l1111ll1_opy_)
  bstack1ll111ll11_opy_.end(EVENTS.bstack1l1l1l111_opy_.value, EVENTS.bstack1l1l1l111_opy_.value + bstack1l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ૮"), EVENTS.bstack1l1l1l111_opy_.value + bstack1l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ૯"), status=True, failure=None, test_name=bstack11ll11ll_opy_)
  if bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡲࡵࡳ࡫࡯࡬ࡦࠩ૰") in kwargs:
    del kwargs[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡳࡶࡴ࡬ࡩ࡭ࡧࠪ૱")]
  try:
    if bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ૲")):
      bstack111ll1l1l_opy_(self, command_executor=command_executor,
                options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
    elif bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ૳")):
      bstack111ll1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities, options=options,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠫ࠷࠴࠵࠴࠰࠳ࠫ૴")):
      bstack111ll1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    else:
      bstack111ll1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive)
  except Exception as bstack1llll1l11l_opy_:
    logger.error(bstack1l11l11ll_opy_.format(bstack1l1l_opy_ (u"ࠬࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠫ૵"), str(bstack1llll1l11l_opy_)))
    raise bstack1llll1l11l_opy_
  if bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1111lll1l_opy_) and bstack1lllllll11_opy_.bstack1111ll1l_opy_(self.caps, options, desired_capabilities):
    if CONFIG[bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨ૶")][bstack1l1l_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭૷")] == True:
      threading.current_thread().appA11yPlatform = True
      if cli.accessibility is None or not cli.accessibility.is_enabled():
        bstack1lllllll11_opy_.set_capabilities(bstack11lll1ll11_opy_, CONFIG)
  try:
    bstack11llllll1l_opy_ = bstack1l1l_opy_ (u"ࠨࠩ૸")
    if bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠩ࠷࠲࠵࠴࠰ࡣ࠳ࠪૹ")):
      if self.caps is not None:
        bstack11llllll1l_opy_ = self.caps.get(bstack1l1l_opy_ (u"ࠥࡳࡵࡺࡩ࡮ࡣ࡯ࡌࡺࡨࡕࡳ࡮ࠥૺ"))
    else:
      if self.capabilities is not None:
        bstack11llllll1l_opy_ = self.capabilities.get(bstack1l1l_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦૻ"))
    if bstack11llllll1l_opy_:
      bstack1ll1ll111_opy_(bstack11llllll1l_opy_)
      if bstack1llllll1l1_opy_() <= version.parse(bstack1l1l_opy_ (u"ࠬ࠹࠮࠲࠵࠱࠴ࠬૼ")):
        self.command_executor._url = bstack1l1l_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢ૽") + bstack11ll1lll1l_opy_ + bstack1l1l_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦ૾")
      else:
        self.command_executor._url = bstack1l1l_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ૿") + bstack11llllll1l_opy_ + bstack1l1l_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ଀")
      logger.debug(bstack11l1ll1lll_opy_.format(bstack11llllll1l_opy_))
    else:
      logger.debug(bstack1l1l1ll1l_opy_.format(bstack1l1l_opy_ (u"ࠥࡓࡵࡺࡩ࡮ࡣ࡯ࠤࡍࡻࡢࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧࠦଁ")))
  except Exception as e:
    logger.debug(bstack1l1l1ll1l_opy_.format(e))
  if bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪଂ") in bstack1lll1l11l1_opy_:
    bstack11ll1ll1l1_opy_(bstack1ll1ll1l11_opy_, bstack1111l1ll_opy_)
  bstack1lll1lll1_opy_ = self.session_id
  if bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬଃ") in bstack1lll1l11l1_opy_ or bstack1l1l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭଄") in bstack1lll1l11l1_opy_ or bstack1l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ଅ") in bstack1lll1l11l1_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack111lll111l_opy_ = getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩଆ"), None)
  if bstack1l1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩଇ") in bstack1lll1l11l1_opy_ or bstack1l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩଈ") in bstack1lll1l11l1_opy_:
    bstack11l1llllll_opy_.bstack111ll1llll_opy_(self)
  if bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫଉ") in bstack1lll1l11l1_opy_ and bstack111lll111l_opy_ and bstack111lll111l_opy_.get(bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬଊ"), bstack1l1l_opy_ (u"࠭ࠧଋ")) == bstack1l1l_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨଌ"):
    bstack11l1llllll_opy_.bstack111ll1llll_opy_(self)
  with bstack1l111l1ll_opy_:
    bstack1l11l11l_opy_.append(self)
  if bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ଍") in CONFIG and bstack1l1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ଎") in CONFIG[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଏ")][bstack1111lll1l_opy_]:
    bstack11ll11ll_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଐ")][bstack1111lll1l_opy_][bstack1l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ଑")]
  logger.debug(bstack1lll1l111_opy_.format(bstack1lll1lll1_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack11l1lll11l_opy_
    def bstack1111l11ll_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack11ll1l11ll_opy_
      if(bstack1l1l_opy_ (u"ࠨࡩ࡯ࡦࡨࡼ࠳ࡰࡳࠣ଒") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠧࡿࠩଓ")), bstack1l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨଔ"), bstack1l1l_opy_ (u"ࠩ࠱ࡷࡪࡹࡳࡪࡱࡱ࡭ࡩࡹ࠮ࡵࡺࡷࠫକ")), bstack1l1l_opy_ (u"ࠪࡻࠬଖ")) as fp:
          fp.write(bstack1l1l_opy_ (u"ࠦࠧଗ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1l1l_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢଘ")))):
          with open(args[1], bstack1l1l_opy_ (u"࠭ࡲࠨଙ")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1l1l_opy_ (u"ࠧࡢࡵࡼࡲࡨࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡡࡱࡩࡼࡖࡡࡨࡧࠫࡧࡴࡴࡴࡦࡺࡷ࠰ࠥࡶࡡࡨࡧࠣࡁࠥࡼ࡯ࡪࡦࠣ࠴࠮࠭ଚ") in line), None)
            if index is not None:
                lines.insert(index+2, bstack11l11ll11l_opy_)
            if bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬଛ") in CONFIG and str(CONFIG[bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ଜ")]).lower() != bstack1l1l_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩଝ"):
                bstack11l11ll111_opy_ = bstack11l1lll11l_opy_()
                bstack11111l111_opy_ = bstack1l1l_opy_ (u"ࠫࠬ࠭ࠊ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠍࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠶ࡡࡀࠐࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠷࡝࠼ࠌࡦࡳࡳࡹࡴࠡࡲࡢ࡭ࡳࡪࡥࡹࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠷ࡣ࠻ࠋࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯ࡵ࡯࡭ࡨ࡫ࠨ࠱࠮ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸࠯࠻ࠋࡥࡲࡲࡸࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯ࠥࡃࠠࡳࡧࡴࡹ࡮ࡸࡥࠩࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨࠩ࠼ࠌ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱ࠮ࡤࡪࡵࡳࡲ࡯ࡵ࡮࠰࡯ࡥࡺࡴࡣࡩࠢࡀࠤࡦࡹࡹ࡯ࡥࠣࠬࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶ࠭ࠥࡃ࠾ࠡࡽࡾࠎࠥࠦ࡬ࡦࡶࠣࡧࡦࡶࡳ࠼ࠌࠣࠤࡹࡸࡹࠡࡽࡾࠎࠥࠦࠠࠡࡥࡤࡴࡸࠦ࠽ࠡࡌࡖࡓࡓ࠴ࡰࡢࡴࡶࡩ࠭ࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠬ࠿ࠏࠦࠠࡾࡿࠣࡧࡦࡺࡣࡩࠢࠫࡩࡽ࠯ࠠࡼࡽࠍࠤࠥࠦࠠࡤࡱࡱࡷࡴࡲࡥ࠯ࡧࡵࡶࡴࡸࠨࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠼ࠥ࠰ࠥ࡫ࡸࠪ࠽ࠍࠤࠥࢃࡽࠋࠢࠣࡶࡪࡺࡵࡳࡰࠣࡥࡼࡧࡩࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱ࠮ࡤࡪࡵࡳࡲ࡯ࡵ࡮࠰ࡦࡳࡳࡴࡥࡤࡶࠫࡿࢀࠐࠠࠡࠢࠣࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺ࠺ࠡࠩࡾࡧࡩࡶࡕࡳ࡮ࢀࠫࠥ࠱ࠠࡦࡰࡦࡳࡩ࡫ࡕࡓࡋࡆࡳࡲࡶ࡯࡯ࡧࡱࡸ࠭ࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡣࡢࡲࡶ࠭࠮࠲ࠊࠡࠢࠣࠤ࠳࠴࠮࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠊࠡࠢࢀࢁ࠮ࡁࠊࡾࡿ࠾ࠎ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠊࠨࠩࠪଞ").format(bstack11l11ll111_opy_=bstack11l11ll111_opy_)
            lines.insert(1, bstack11111l111_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1l1l_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢଟ")), bstack1l1l_opy_ (u"࠭ࡷࠨଠ")) as bstack1111lll11_opy_:
              bstack1111lll11_opy_.writelines(lines)
        CONFIG[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩଡ")] = str(bstack1lll1l11l1_opy_) + str(__version__)
        bstack1l11111l_opy_ = os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ଢ")]
        bstack1l1ll11l1l_opy_ = bstack1ll11ll1l_opy_.bstack11lll1ll_opy_(CONFIG, bstack1lll1l11l1_opy_)
        CONFIG[bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬଣ")] = bstack1l11111l_opy_
        CONFIG[bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬତ")] = bstack1l1ll11l1l_opy_
        bstack1111lll1l_opy_ = 0 if bstack1ll1ll1l11_opy_ < 0 else bstack1ll1ll1l11_opy_
        try:
          if bstack1l1ll11lll_opy_ is True:
            bstack1111lll1l_opy_ = int(multiprocessing.current_process().name)
          elif bstack1ll1ll111l_opy_ is True:
            bstack1111lll1l_opy_ = int(threading.current_thread().name)
        except:
          bstack1111lll1l_opy_ = 0
        CONFIG[bstack1l1l_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦଥ")] = False
        CONFIG[bstack1l1l_opy_ (u"ࠧ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦଦ")] = True
        bstack11lll1ll11_opy_ = bstack1l111lll1_opy_(CONFIG, bstack1111lll1l_opy_)
        logger.debug(bstack1l11ll1ll1_opy_.format(str(bstack11lll1ll11_opy_)))
        if CONFIG.get(bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪଧ")):
          bstack1llll111ll_opy_(bstack11lll1ll11_opy_)
        if bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪନ") in CONFIG and bstack1l1l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭଩") in CONFIG[bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬପ")][bstack1111lll1l_opy_]:
          bstack11ll11ll_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଫ")][bstack1111lll1l_opy_][bstack1l1l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩବ")]
        args.append(os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠬࢄࠧଭ")), bstack1l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ମ"), bstack1l1l_opy_ (u"ࠧ࠯ࡵࡨࡷࡸ࡯࡯࡯࡫ࡧࡷ࠳ࡺࡸࡵࠩଯ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11lll1ll11_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1l1l_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥର"))
      bstack11ll1l11ll_opy_ = True
      return bstack1l1ll11ll1_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack11lll111_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1ll1ll1l11_opy_
    global bstack11ll11ll_opy_
    global bstack1l1ll11lll_opy_
    global bstack1ll1ll111l_opy_
    global bstack1lll1l11l1_opy_
    CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ଱")] = str(bstack1lll1l11l1_opy_) + str(__version__)
    bstack1l11111l_opy_ = os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨଲ")]
    bstack1l1ll11l1l_opy_ = bstack1ll11ll1l_opy_.bstack11lll1ll_opy_(CONFIG, bstack1lll1l11l1_opy_)
    CONFIG[bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧଳ")] = bstack1l11111l_opy_
    CONFIG[bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧ଴")] = bstack1l1ll11l1l_opy_
    bstack1111lll1l_opy_ = 0 if bstack1ll1ll1l11_opy_ < 0 else bstack1ll1ll1l11_opy_
    try:
      if bstack1l1ll11lll_opy_ is True:
        bstack1111lll1l_opy_ = int(multiprocessing.current_process().name)
      elif bstack1ll1ll111l_opy_ is True:
        bstack1111lll1l_opy_ = int(threading.current_thread().name)
    except:
      bstack1111lll1l_opy_ = 0
    CONFIG[bstack1l1l_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧଵ")] = True
    bstack11lll1ll11_opy_ = bstack1l111lll1_opy_(CONFIG, bstack1111lll1l_opy_)
    logger.debug(bstack1l11ll1ll1_opy_.format(str(bstack11lll1ll11_opy_)))
    if CONFIG.get(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫଶ")):
      bstack1llll111ll_opy_(bstack11lll1ll11_opy_)
    if bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଷ") in CONFIG and bstack1l1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧସ") in CONFIG[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ହ")][bstack1111lll1l_opy_]:
      bstack11ll11ll_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ଺")][bstack1111lll1l_opy_][bstack1l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ଻")]
    import urllib
    import json
    if bstack1l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧ଼ࠪ") in CONFIG and str(CONFIG[bstack1l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫଽ")]).lower() != bstack1l1l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧା"):
        bstack1l1111ll11_opy_ = bstack11l1lll11l_opy_()
        bstack11l11ll111_opy_ = bstack1l1111ll11_opy_ + urllib.parse.quote(json.dumps(bstack11lll1ll11_opy_))
    else:
        bstack11l11ll111_opy_ = bstack1l1l_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫି") + urllib.parse.quote(json.dumps(bstack11lll1ll11_opy_))
    browser = self.connect(bstack11l11ll111_opy_)
    return browser
except Exception as e:
    pass
def bstack11l1ll11l1_opy_():
    global bstack11ll1l11ll_opy_
    global bstack1lll1l11l1_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack111l11l11_opy_
        global bstack1l1ll1l1_opy_
        if not bstack1l1lll11l1_opy_:
          global bstack1111l1l1_opy_
          if not bstack1111l1l1_opy_:
            from bstack_utils.helper import bstack11111l1ll_opy_, bstack1l1ll1lll_opy_, bstack11lllll1ll_opy_
            bstack1111l1l1_opy_ = bstack11111l1ll_opy_()
            bstack1l1ll1lll_opy_(bstack1lll1l11l1_opy_)
            bstack1l1ll11l1l_opy_ = bstack1ll11ll1l_opy_.bstack11lll1ll_opy_(CONFIG, bstack1lll1l11l1_opy_)
            bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠥࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡑࡔࡒࡈ࡚ࡉࡔࡠࡏࡄࡔࠧୀ"), bstack1l1ll11l1l_opy_)
          BrowserType.connect = bstack111l11l11_opy_
          return
        BrowserType.launch = bstack11lll111_opy_
        bstack11ll1l11ll_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1111l11ll_opy_
      bstack11ll1l11ll_opy_ = True
    except Exception as e:
      pass
def bstack11l11l1ll1_opy_(context, bstack1l11l1llll_opy_):
  try:
    context.page.evaluate(bstack1l1l_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧୁ"), bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠩୂ")+ json.dumps(bstack1l11l1llll_opy_) + bstack1l1l_opy_ (u"ࠨࡽࡾࠤୃ"))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢࡾࢁ࠿ࠦࡻࡾࠤୄ").format(str(e), traceback.format_exc()))
def bstack1ll11111ll_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1l1l_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ୅"), bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ୆") + json.dumps(message) + bstack1l1l_opy_ (u"ࠪ࠰ࠧࡲࡥࡷࡧ࡯ࠦ࠿࠭େ") + json.dumps(level) + bstack1l1l_opy_ (u"ࠫࢂࢃࠧୈ"))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡣࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠥࢁࡽ࠻ࠢࡾࢁࠧ୉").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack1l11l11lll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1l1111111_opy_(self, url):
  global bstack11l1lllll1_opy_
  try:
    bstack11l11111_opy_(url)
  except Exception as err:
    logger.debug(bstack1l111lllll_opy_.format(str(err)))
  try:
    bstack11l1lllll1_opy_(self, url)
  except Exception as e:
    try:
      bstack11lll11l_opy_ = str(e)
      if any(err_msg in bstack11lll11l_opy_ for err_msg in bstack1l1ll1lll1_opy_):
        bstack11l11111_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l111lllll_opy_.format(str(err)))
    raise e
def bstack1l1ll1l1l1_opy_(self):
  global bstack1ll11l11_opy_
  bstack1ll11l11_opy_ = self
  return
def bstack11ll11l1l_opy_(self):
  global bstack11llllll_opy_
  bstack11llllll_opy_ = self
  return
def bstack1lll1llll1_opy_(test_name, bstack1l1l1lllll_opy_):
  global CONFIG
  if percy.bstack1l1l11111l_opy_() == bstack1l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦ୊"):
    bstack1l1l1ll1ll_opy_ = os.path.relpath(bstack1l1l1lllll_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack1l1l1ll1ll_opy_)
    bstack1l1l1l11_opy_ = suite_name + bstack1l1l_opy_ (u"ࠢ࠮ࠤୋ") + test_name
    threading.current_thread().percySessionName = bstack1l1l1l11_opy_
def bstack11llll1lll_opy_(self, test, *args, **kwargs):
  global bstack11ll1l1lll_opy_
  test_name = None
  bstack1l1l1lllll_opy_ = None
  if test:
    test_name = str(test.name)
    bstack1l1l1lllll_opy_ = str(test.source)
  bstack1lll1llll1_opy_(test_name, bstack1l1l1lllll_opy_)
  bstack11ll1l1lll_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack1l1l11ll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1lllll1l1_opy_(driver, bstack1l1l1l11_opy_):
  if not bstack1l1lllll_opy_ and bstack1l1l1l11_opy_:
      bstack1l1111l11l_opy_ = {
          bstack1l1l_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨୌ"): bstack1l1l_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧ୍ࠪ"),
          bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭୎"): {
              bstack1l1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ୏"): bstack1l1l1l11_opy_
          }
      }
      bstack1ll1llll1_opy_ = bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ୐").format(json.dumps(bstack1l1111l11l_opy_))
      driver.execute_script(bstack1ll1llll1_opy_)
  if bstack11l111ll1_opy_:
      bstack1ll111111_opy_ = {
          bstack1l1l_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭୑"): bstack1l1l_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ୒"),
          bstack1l1l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ୓"): {
              bstack1l1l_opy_ (u"ࠩࡧࡥࡹࡧࠧ୔"): bstack1l1l1l11_opy_ + bstack1l1l_opy_ (u"ࠪࠤࡵࡧࡳࡴࡧࡧࠥࠬ୕"),
              bstack1l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪୖ"): bstack1l1l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪୗ")
          }
      }
      if bstack11l111ll1_opy_.status == bstack1l1l_opy_ (u"࠭ࡐࡂࡕࡖࠫ୘"):
          bstack11lll11ll1_opy_ = bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬ୙").format(json.dumps(bstack1ll111111_opy_))
          driver.execute_script(bstack11lll11ll1_opy_)
          bstack11ll11111_opy_(driver, bstack1l1l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ୚"))
      elif bstack11l111ll1_opy_.status == bstack1l1l_opy_ (u"ࠩࡉࡅࡎࡒࠧ୛"):
          reason = bstack1l1l_opy_ (u"ࠥࠦଡ଼")
          bstack1l11l1lll1_opy_ = bstack1l1l1l11_opy_ + bstack1l1l_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠬଢ଼")
          if bstack11l111ll1_opy_.message:
              reason = str(bstack11l111ll1_opy_.message)
              bstack1l11l1lll1_opy_ = bstack1l11l1lll1_opy_ + bstack1l1l_opy_ (u"ࠬࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࠬ୞") + reason
          bstack1ll111111_opy_[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩୟ")] = {
              bstack1l1l_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ୠ"): bstack1l1l_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧୡ"),
              bstack1l1l_opy_ (u"ࠩࡧࡥࡹࡧࠧୢ"): bstack1l11l1lll1_opy_
          }
          bstack11lll11ll1_opy_ = bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨୣ").format(json.dumps(bstack1ll111111_opy_))
          driver.execute_script(bstack11lll11ll1_opy_)
          bstack11ll11111_opy_(driver, bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ୤"), reason)
          bstack1lllll1l1l_opy_(reason, str(bstack11l111ll1_opy_), str(bstack1ll1ll1l11_opy_), logger)
@measure(event_name=EVENTS.bstack11l1ll11l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1lll1l1l1l_opy_(driver, test):
  if percy.bstack1l1l11111l_opy_() == bstack1l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥ୥") and percy.bstack1lll11lll1_opy_() == bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ୦"):
      bstack1ll1l1l11l_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ୧"), None)
      bstack1ll111lll_opy_(driver, bstack1ll1l1l11l_opy_, test)
  if (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ୨"), None) and
      bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ୩"), None)) or (
      bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ୪"), None) and
      bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭୫"), None)):
      logger.info(bstack1l1l_opy_ (u"ࠧࡇࡵࡵࡱࡰࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠣࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡧࡱࡵࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡷࡱࡨࡪࡸࡷࡢࡻ࠱ࠤࠧ୬"))
      bstack1lllllll11_opy_.bstack11llll1ll_opy_(driver, name=test.name, path=test.source)
def bstack1l1llll1l_opy_(test, bstack1l1l1l11_opy_):
    try:
      bstack1ll111l1_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack1l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ୭")] = bstack1l1l1l11_opy_
      if bstack11l111ll1_opy_:
        if bstack11l111ll1_opy_.status == bstack1l1l_opy_ (u"ࠧࡑࡃࡖࡗࠬ୮"):
          data[bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ୯")] = bstack1l1l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ୰")
        elif bstack11l111ll1_opy_.status == bstack1l1l_opy_ (u"ࠪࡊࡆࡏࡌࠨୱ"):
          data[bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ୲")] = bstack1l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ୳")
          if bstack11l111ll1_opy_.message:
            data[bstack1l1l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭୴")] = str(bstack11l111ll1_opy_.message)
      user = CONFIG[bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ୵")]
      key = CONFIG[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ୶")]
      host = bstack1ll1lll111_opy_(cli.config, [bstack1l1l_opy_ (u"ࠤࡤࡴ࡮ࡹࠢ୷"), bstack1l1l_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ୸"), bstack1l1l_opy_ (u"ࠦࡦࡶࡩࠣ୹")], bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࠨ୺"))
      url = bstack1l1l_opy_ (u"࠭ࡻࡾ࠱ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠳ࡸ࡫ࡳࡴ࡫ࡲࡲࡸ࠵ࡻࡾ࠰࡭ࡷࡴࡴࠧ୻").format(host, bstack1lll1lll1_opy_)
      headers = {
        bstack1l1l_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡶࡼࡴࡪ࠭୼"): bstack1l1l_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ୽"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers, auth=(user, key))
        cli.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺ࡶࡲࡧࡥࡹ࡫࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡳࡵࡣࡷࡹࡸࠨ୾"), datetime.datetime.now() - bstack1ll111l1_opy_)
    except Exception as e:
      logger.error(bstack1ll111ll1l_opy_.format(str(e)))
def bstack1ll1l1ll11_opy_(test, bstack1l1l1l11_opy_):
  global CONFIG
  global bstack11llllll_opy_
  global bstack1ll11l11_opy_
  global bstack1lll1lll1_opy_
  global bstack11l111ll1_opy_
  global bstack11ll11ll_opy_
  global bstack1llll1111_opy_
  global bstack1l1111l1l1_opy_
  global bstack1lll1ll11l_opy_
  global bstack1lll111lll_opy_
  global bstack1l11l11l_opy_
  global bstack11l11l1ll_opy_
  global bstack1l11lll111_opy_
  try:
    if not bstack1lll1lll1_opy_:
      with bstack1l11lll111_opy_:
        bstack11l1l1ll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠪࢂࠬ୿")), bstack1l1l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ஀"), bstack1l1l_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧ஁"))
        if os.path.exists(bstack11l1l1ll1_opy_):
          with open(bstack11l1l1ll1_opy_, bstack1l1l_opy_ (u"࠭ࡲࠨஂ")) as f:
            content = f.read().strip()
            if content:
              bstack11lll11111_opy_ = json.loads(bstack1l1l_opy_ (u"ࠢࡼࠤஃ") + content + bstack1l1l_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪ஄") + bstack1l1l_opy_ (u"ࠤࢀࠦஅ"))
              bstack1lll1lll1_opy_ = bstack11lll11111_opy_.get(str(threading.get_ident()))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡵࡩࡦࡪࡩ࡯ࡩࠣࡷࡪࡹࡳࡪࡱࡱࠤࡎࡊࡳࠡࡨ࡬ࡰࡪࡀࠠࠨஆ") + str(e))
  if bstack1l11l11l_opy_:
    with bstack1l111l1ll_opy_:
      bstack1llllll1l_opy_ = bstack1l11l11l_opy_.copy()
    for driver in bstack1llllll1l_opy_:
      if bstack1lll1lll1_opy_ == driver.session_id:
        if test:
          bstack1lll1l1l1l_opy_(driver, test)
        bstack1lllll1l1_opy_(driver, bstack1l1l1l11_opy_)
  elif bstack1lll1lll1_opy_:
    bstack1l1llll1l_opy_(test, bstack1l1l1l11_opy_)
  if bstack11llllll_opy_:
    bstack1l1111l1l1_opy_(bstack11llllll_opy_)
  if bstack1ll11l11_opy_:
    bstack1lll1ll11l_opy_(bstack1ll11l11_opy_)
  if bstack11l1l1111l_opy_:
    bstack1lll111lll_opy_()
def bstack1l1lll1l1_opy_(self, test, *args, **kwargs):
  bstack1l1l1l11_opy_ = None
  if test:
    bstack1l1l1l11_opy_ = str(test.name)
  bstack1ll1l1ll11_opy_(test, bstack1l1l1l11_opy_)
  bstack1llll1111_opy_(self, test, *args, **kwargs)
def bstack1l1111l1_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1l1llll11_opy_
  global CONFIG
  global bstack1l11l11l_opy_
  global bstack1lll1lll1_opy_
  global bstack1l11lll111_opy_
  bstack1ll1ll11ll_opy_ = None
  try:
    if bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪஇ"), None) or bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧஈ"), None):
      try:
        if not bstack1lll1lll1_opy_:
          bstack11l1l1ll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"࠭ࡾࠨஉ")), bstack1l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧஊ"), bstack1l1l_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ஋"))
          with bstack1l11lll111_opy_:
            if os.path.exists(bstack11l1l1ll1_opy_):
              with open(bstack11l1l1ll1_opy_, bstack1l1l_opy_ (u"ࠩࡵࠫ஌")) as f:
                content = f.read().strip()
                if content:
                  bstack11lll11111_opy_ = json.loads(bstack1l1l_opy_ (u"ࠥࡿࠧ஍") + content + bstack1l1l_opy_ (u"ࠫࠧࡾࠢ࠻ࠢࠥࡽࠧ࠭எ") + bstack1l1l_opy_ (u"ࠧࢃࠢஏ"))
                  bstack1lll1lll1_opy_ = bstack11lll11111_opy_.get(str(threading.get_ident()))
      except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡸࡥࡢࡦ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࡶࠤ࡫࡯࡬ࡦࠢ࡬ࡲࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࠬஐ") + str(e))
      if bstack1l11l11l_opy_:
        with bstack1l111l1ll_opy_:
          bstack1llllll1l_opy_ = bstack1l11l11l_opy_.copy()
        for driver in bstack1llllll1l_opy_:
          if bstack1lll1lll1_opy_ == driver.session_id:
            bstack1ll1ll11ll_opy_ = driver
    bstack1l1llll111_opy_ = bstack1lllllll11_opy_.bstack1l111lll_opy_(test.tags)
    if bstack1ll1ll11ll_opy_:
      threading.current_thread().isA11yTest = bstack1lllllll11_opy_.bstack1l1111111l_opy_(bstack1ll1ll11ll_opy_, bstack1l1llll111_opy_)
      threading.current_thread().isAppA11yTest = bstack1lllllll11_opy_.bstack1l1111111l_opy_(bstack1ll1ll11ll_opy_, bstack1l1llll111_opy_)
    else:
      threading.current_thread().isA11yTest = bstack1l1llll111_opy_
      threading.current_thread().isAppA11yTest = bstack1l1llll111_opy_
  except:
    pass
  bstack1l1llll11_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack11l111ll1_opy_
  try:
    bstack11l111ll1_opy_ = self._test
  except:
    bstack11l111ll1_opy_ = self.test
def bstack1l11ll111_opy_():
  global bstack1l11l11l1_opy_
  try:
    if os.path.exists(bstack1l11l11l1_opy_):
      os.remove(bstack1l11l11l1_opy_)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡧࡩࡱ࡫ࡴࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪ஑") + str(e))
def bstack1lll111l1_opy_():
  global bstack1l11l11l1_opy_
  bstack11ll1l1111_opy_ = {}
  lock_file = bstack1l11l11l1_opy_ + bstack1l1l_opy_ (u"ࠨ࠰࡯ࡳࡨࡱࠧஒ")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡬ࡰࡥ࡮ࠤࡳࡵࡴࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨ࠰ࠥࡻࡳࡪࡰࡪࠤࡧࡧࡳࡪࡥࠣࡪ࡮ࡲࡥࠡࡱࡳࡩࡷࡧࡴࡪࡱࡱࡷࠬஓ"))
    try:
      if not os.path.isfile(bstack1l11l11l1_opy_):
        with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠪࡻࠬஔ")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1l11l11l1_opy_):
        with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠫࡷ࠭க")) as f:
          content = f.read().strip()
          if content:
            bstack11ll1l1111_opy_ = json.loads(content)
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡤࡨ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ஖") + str(e))
    return bstack11ll1l1111_opy_
  try:
    os.makedirs(os.path.dirname(bstack1l11l11l1_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      if not os.path.isfile(bstack1l11l11l1_opy_):
        with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"࠭ࡷࠨ஗")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1l11l11l1_opy_):
        with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠧࡳࠩ஘")) as f:
          content = f.read().strip()
          if content:
            bstack11ll1l1111_opy_ = json.loads(content)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪࡧࡤࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪங") + str(e))
  finally:
    return bstack11ll1l1111_opy_
def bstack11ll1ll1l1_opy_(platform_index, item_index):
  global bstack1l11l11l1_opy_
  lock_file = bstack1l11l11l1_opy_ + bstack1l1l_opy_ (u"ࠩ࠱ࡰࡴࡩ࡫ࠨச")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1l1l_opy_ (u"ࠪࡪ࡮ࡲࡥ࡭ࡱࡦ࡯ࠥࡴ࡯ࡵࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩ࠱ࠦࡵࡴ࡫ࡱ࡫ࠥࡨࡡࡴ࡫ࡦࠤ࡫࡯࡬ࡦࠢࡲࡴࡪࡸࡡࡵ࡫ࡲࡲࡸ࠭஛"))
    try:
      bstack11ll1l1111_opy_ = {}
      if os.path.exists(bstack1l11l11l1_opy_):
        with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠫࡷ࠭ஜ")) as f:
          content = f.read().strip()
          if content:
            bstack11ll1l1111_opy_ = json.loads(content)
      bstack11ll1l1111_opy_[item_index] = platform_index
      with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠧࡽࠢ஝")) as outfile:
        json.dump(bstack11ll1l1111_opy_, outfile)
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡹࡵ࡭ࡹ࡯࡮ࡨࠢࡷࡳࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫஞ") + str(e))
    return
  try:
    os.makedirs(os.path.dirname(bstack1l11l11l1_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      bstack11ll1l1111_opy_ = {}
      if os.path.exists(bstack1l11l11l1_opy_):
        with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠧࡳࠩட")) as f:
          content = f.read().strip()
          if content:
            bstack11ll1l1111_opy_ = json.loads(content)
      bstack11ll1l1111_opy_[item_index] = platform_index
      with open(bstack1l11l11l1_opy_, bstack1l1l_opy_ (u"ࠣࡹࠥ஠")) as outfile:
        json.dump(bstack11ll1l1111_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡼࡸࡩࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ஡") + str(e))
def bstack1ll1111lll_opy_(bstack11l1l11111_opy_):
  global CONFIG
  bstack1lll1ll1ll_opy_ = bstack1l1l_opy_ (u"ࠪࠫ஢")
  if not bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧண") in CONFIG:
    logger.info(bstack1l1l_opy_ (u"ࠬࡔ࡯ࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠤࡵࡧࡳࡴࡧࡧࠤࡺࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢࡵࡩࡵࡵࡲࡵࠢࡩࡳࡷࠦࡒࡰࡤࡲࡸࠥࡸࡵ࡯ࠩத"))
  try:
    platform = CONFIG[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ஥")][bstack11l1l11111_opy_]
    if bstack1l1l_opy_ (u"ࠧࡰࡵࠪ஦") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1l1l_opy_ (u"ࠨࡱࡶࠫ஧")]) + bstack1l1l_opy_ (u"ࠩ࠯ࠤࠬந")
    if bstack1l1l_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ன") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1l1l_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧப")]) + bstack1l1l_opy_ (u"ࠬ࠲ࠠࠨ஫")
    if bstack1l1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪ஬") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1l1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ஭")]) + bstack1l1l_opy_ (u"ࠨ࠮ࠣࠫம")
    if bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫய") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬர")]) + bstack1l1l_opy_ (u"ࠫ࠱ࠦࠧற")
    if bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪல") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫள")]) + bstack1l1l_opy_ (u"ࠧ࠭ࠢࠪழ")
    if bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩவ") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪஶ")]) + bstack1l1l_opy_ (u"ࠪ࠰ࠥ࠭ஷ")
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠫࡘࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡷࡹࡸࡩ࡯ࡩࠣࡪࡴࡸࠠࡳࡧࡳࡳࡷࡺࠠࡨࡧࡱࡩࡷࡧࡴࡪࡱࡱࠫஸ") + str(e))
  finally:
    if bstack1lll1ll1ll_opy_[len(bstack1lll1ll1ll_opy_) - 2:] == bstack1l1l_opy_ (u"ࠬ࠲ࠠࠨஹ"):
      bstack1lll1ll1ll_opy_ = bstack1lll1ll1ll_opy_[:-2]
    return bstack1lll1ll1ll_opy_
def bstack1l111l1l1_opy_(path, bstack1lll1ll1ll_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack11l1ll111_opy_ = ET.parse(path)
    bstack111l1l1l1_opy_ = bstack11l1ll111_opy_.getroot()
    bstack11lll11ll_opy_ = None
    for suite in bstack111l1l1l1_opy_.iter(bstack1l1l_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬ஺")):
      if bstack1l1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧ஻") in suite.attrib:
        suite.attrib[bstack1l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭஼")] += bstack1l1l_opy_ (u"ࠩࠣࠫ஽") + bstack1lll1ll1ll_opy_
        bstack11lll11ll_opy_ = suite
    bstack1111111l_opy_ = None
    for robot in bstack111l1l1l1_opy_.iter(bstack1l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩா")):
      bstack1111111l_opy_ = robot
    bstack1l111l11l_opy_ = len(bstack1111111l_opy_.findall(bstack1l1l_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪி")))
    if bstack1l111l11l_opy_ == 1:
      bstack1111111l_opy_.remove(bstack1111111l_opy_.findall(bstack1l1l_opy_ (u"ࠬࡹࡵࡪࡶࡨࠫீ"))[0])
      bstack1llll111_opy_ = ET.Element(bstack1l1l_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬு"), attrib={bstack1l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬூ"): bstack1l1l_opy_ (u"ࠨࡕࡸ࡭ࡹ࡫ࡳࠨ௃"), bstack1l1l_opy_ (u"ࠩ࡬ࡨࠬ௄"): bstack1l1l_opy_ (u"ࠪࡷ࠵࠭௅")})
      bstack1111111l_opy_.insert(1, bstack1llll111_opy_)
      bstack1llll1l1l1_opy_ = None
      for suite in bstack1111111l_opy_.iter(bstack1l1l_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪெ")):
        bstack1llll1l1l1_opy_ = suite
      bstack1llll1l1l1_opy_.append(bstack11lll11ll_opy_)
      bstack11l1l1lll1_opy_ = None
      for status in bstack11lll11ll_opy_.iter(bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬே")):
        bstack11l1l1lll1_opy_ = status
      bstack1llll1l1l1_opy_.append(bstack11l1l1lll1_opy_)
    bstack11l1ll111_opy_.write(path)
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠫை") + str(e))
def bstack11l1ll1111_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack11l111l1l_opy_
  global CONFIG
  if bstack1l1l_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࡰࡢࡶ࡫ࠦ௉") in options:
    del options[bstack1l1l_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࡱࡣࡷ࡬ࠧொ")]
  bstack1l111lll11_opy_ = bstack1lll111l1_opy_()
  for item_id in bstack1l111lll11_opy_.keys():
    path = os.path.join(outs_dir, str(item_id), bstack1l1l_opy_ (u"ࠩࡲࡹࡹࡶࡵࡵ࠰ࡻࡱࡱ࠭ோ"))
    bstack1l111l1l1_opy_(path, bstack1ll1111lll_opy_(bstack1l111lll11_opy_[item_id]))
  bstack1l11ll111_opy_()
  return bstack11l111l1l_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1lll1l11ll_opy_(self, ff_profile_dir):
  global bstack1l1l1l1l11_opy_
  if not ff_profile_dir:
    return None
  return bstack1l1l1l1l11_opy_(self, ff_profile_dir)
def bstack11ll1l11l_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack1lllll1ll1_opy_
  bstack1ll1l1lll1_opy_ = []
  if bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ௌ") in CONFIG:
    bstack1ll1l1lll1_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹ்ࠧ")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࠨ௎")],
      pabot_args[bstack1l1l_opy_ (u"ࠨࡶࡦࡴࡥࡳࡸ࡫ࠢ௏")],
      argfile,
      pabot_args.get(bstack1l1l_opy_ (u"ࠢࡩ࡫ࡹࡩࠧௐ")),
      pabot_args[bstack1l1l_opy_ (u"ࠣࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠦ௑")],
      platform[0],
      bstack1lllll1ll1_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1l1l_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡪ࡮ࡲࡥࡴࠤ௒")] or [(bstack1l1l_opy_ (u"ࠥࠦ௓"), None)]
    for platform in enumerate(bstack1ll1l1lll1_opy_)
  ]
def bstack11l111l111_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1ll1lll11_opy_=bstack1l1l_opy_ (u"ࠫࠬ௔")):
  global bstack11lll11l1l_opy_
  self.platform_index = platform_index
  self.bstack11l11l111_opy_ = bstack1ll1lll11_opy_
  bstack11lll11l1l_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack111lllll1_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1l11lll1ll_opy_
  global bstack1l111lll1l_opy_
  bstack1l1lllll11_opy_ = copy.deepcopy(item)
  if not bstack1l1l_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ௕") in item.options:
    bstack1l1lllll11_opy_.options[bstack1l1l_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ௖")] = []
  bstack1ll1ll1ll1_opy_ = bstack1l1lllll11_opy_.options[bstack1l1l_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩௗ")].copy()
  for v in bstack1l1lllll11_opy_.options[bstack1l1l_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௘")]:
    if bstack1l1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡒࡏࡅ࡙ࡌࡏࡓࡏࡌࡒࡉࡋࡘࠨ௙") in v:
      bstack1ll1ll1ll1_opy_.remove(v)
    if bstack1l1l_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕࠪ௚") in v:
      bstack1ll1ll1ll1_opy_.remove(v)
    if bstack1l1l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡈࡊࡌࡌࡐࡅࡄࡐࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨ௛") in v:
      bstack1ll1ll1ll1_opy_.remove(v)
  bstack1ll1ll1ll1_opy_.insert(0, bstack1l1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛࠾ࢀࢃࠧ௜").format(bstack1l1lllll11_opy_.platform_index))
  bstack1ll1ll1ll1_opy_.insert(0, bstack1l1l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡊࡅࡇࡎࡒࡇࡆࡒࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔ࠽ࡿࢂ࠭௝").format(bstack1l1lllll11_opy_.bstack11l11l111_opy_))
  bstack1l1lllll11_opy_.options[bstack1l1l_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩ௞")] = bstack1ll1ll1ll1_opy_
  if bstack1l111lll1l_opy_:
    bstack1l1lllll11_opy_.options[bstack1l1l_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௟")].insert(0, bstack1l1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔ࠼ࡾࢁࠬ௠").format(bstack1l111lll1l_opy_))
  return bstack1l11lll1ll_opy_(caller_id, datasources, is_last, bstack1l1lllll11_opy_, outs_dir)
def bstack1l11111lll_opy_(command, item_index):
  try:
    if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࠫ௡")):
      os.environ[bstack1l1l_opy_ (u"ࠫࡈ࡛ࡒࡓࡇࡑࡘࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡅࡃࡗࡅࠬ௢")] = json.dumps(CONFIG[bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ௣")][item_index % bstack1l1l11ll1_opy_])
    global bstack1l111lll1l_opy_
    if bstack1l111lll1l_opy_:
      command[0] = command[0].replace(bstack1l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ௤"), bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡳࡥ࡭ࠣࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠤ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾࠠࠨ௥") + str(item_index % bstack1l1l11ll1_opy_) + bstack1l1l_opy_ (u"ࠨࠢ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣ࡮ࡺࡥ࡮ࡡ࡬ࡲࡩ࡫ࡸࠡࠩ௦") + str(
        item_index) + bstack1l1l_opy_ (u"ࠩࠣࠫ௧") + bstack1l111lll1l_opy_, 1)
    else:
      command[0] = command[0].replace(bstack1l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ௨"),
                                      bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡷࡩࡱࠠࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠡ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࠤࠬ௩") +  str(item_index % bstack1l1l11ll1_opy_) + bstack1l1l_opy_ (u"ࠬࠦ࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠ࡫ࡷࡩࡲࡥࡩ࡯ࡦࡨࡼࠥ࠭௪") + str(item_index), 1)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡳ࡯ࡥ࡫ࡩࡽ࡮ࡴࡧࠡࡥࡲࡱࡲࡧ࡮ࡥࠢࡩࡳࡷࠦࡰࡢࡤࡲࡸࠥࡸࡵ࡯࠼ࠣࡿࢂ࠭௫").format(str(e)))
def bstack1l1l1lll1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1lll1ll111_opy_
  try:
    bstack1l11111lll_opy_(command, item_index)
    return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡥࡧࡵࡴࠡࡴࡸࡲ࠿ࠦࡻࡾࠩ௬").format(str(e)))
    raise e
def bstack1l1l11l11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1lll1ll111_opy_
  try:
    bstack1l11111lll_opy_(command, item_index)
    return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡦࡨ࡯ࡵࠢࡵࡹࡳࠦ࠲࠯࠳࠶࠾ࠥࢁࡽࠨ௭").format(str(e)))
    try:
      return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
    except Exception as e2:
      logger.error(bstack1l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣ࠶࠳࠷࠳ࠡࡨࡤࡰࡱࡨࡡࡤ࡭࠽ࠤࢀࢃࠧ௮").format(str(e2)))
      raise e
def bstack1ll11l111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1lll1ll111_opy_
  try:
    bstack1l11111lll_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤࡷࡻ࡮ࠡ࠴࠱࠵࠺ࡀࠠࡼࡿࠪ௯").format(str(e)))
    try:
      return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
    except Exception as e2:
      logger.error(bstack1l1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡤࡲࡸࠥ࠸࠮࠲࠷ࠣࡪࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࡻࡾࠩ௰").format(str(e2)))
      raise e
def _11lll1l111_opy_(bstack1l111l1l1l_opy_, item_index, process_timeout, sleep_before_start, bstack1ll1l11111_opy_):
  bstack1l11111lll_opy_(bstack1l111l1l1l_opy_, item_index)
  if process_timeout is None:
    process_timeout = 3600
  if sleep_before_start and sleep_before_start > 0:
    time.sleep(min(sleep_before_start, 5))
  return process_timeout
def bstack1ll1111l1_opy_(command, bstack1l11llllll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1lll1ll111_opy_
  global bstack1l1llll1ll_opy_
  global bstack1l111lll1l_opy_
  try:
    for env_name, bstack11ll11l11_opy_ in bstack1l1llll1ll_opy_.items():
      os.environ[env_name] = bstack11ll11l11_opy_
    bstack1l111lll1l_opy_ = bstack1l1l_opy_ (u"ࠧࠨ௱")
    bstack1l11111lll_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    if sleep_before_start and sleep_before_start > 0:
      time.sleep(min(sleep_before_start, 5))
    return bstack1lll1ll111_opy_(command, bstack1l11llllll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡦࡴࡺࠠࡳࡷࡱࠤ࠺࠴࠰࠻ࠢࡾࢁࠬ௲").format(str(e)))
    try:
      return bstack1lll1ll111_opy_(command, bstack1l11llllll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack1l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡥࡧࡵࡴࠡࡨࡤࡰࡱࡨࡡࡤ࡭࠽ࠤࢀࢃࠧ௳").format(str(e2)))
      raise e
def bstack1l1ll11l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1lll1ll111_opy_
  try:
    process_timeout = _11lll1l111_opy_(command, item_index, process_timeout, sleep_before_start, bstack1l1l_opy_ (u"ࠨ࠶࠱࠶ࠬ௴"))
    return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣࡶࡺࡴࠠ࠵࠰࠵࠾ࠥࢁࡽࠨ௵").format(str(e)))
    try:
      return bstack1lll1ll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪ௶").format(str(e2)))
      raise e
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack1l1111lll1_opy_(self, runner, quiet=False, capture=True):
  global bstack111lll11l1_opy_
  bstack1l111llll_opy_ = bstack111lll11l1_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack1l1l_opy_ (u"ࠫࡪࡾࡣࡦࡲࡷ࡭ࡴࡴ࡟ࡢࡴࡵࠫ௷")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1l1l_opy_ (u"ࠬ࡫ࡸࡤࡡࡷࡶࡦࡩࡥࡣࡣࡦ࡯ࡤࡧࡲࡳࠩ௸")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1l111llll_opy_
def bstack1l11ll111l_opy_(runner, hook_name, context, element, bstack1l11l1l1l1_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack1lll11l1l1_opy_.bstack11l1ll1l1l_opy_(hook_name, element)
    bstack1l11l1l1l1_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack1lll11l1l1_opy_.bstack11l111l1_opy_(element)
      if hook_name not in [bstack1l1l_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠪ௹"), bstack1l1l_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠪ௺")] and args and hasattr(args[0], bstack1l1l_opy_ (u"ࠨࡧࡵࡶࡴࡸ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠨ௻")):
        args[0].error_message = bstack1l1l_opy_ (u"ࠩࠪ௼")
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡨࡢࡰࡧࡰࡪࠦࡨࡰࡱ࡮ࡷࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥ࠻ࠢࡾࢁࠬ௽").format(str(e)))
@measure(event_name=EVENTS.bstack1lll1l1l11_opy_, stage=STAGE.bstack11lll1l1_opy_, hook_type=bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡅࡱࡲࠢ௾"), bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11l111l1ll_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    if runner.hooks.get(bstack1l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠤ௿")).__name__ != bstack1l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࡢࡨࡪ࡬ࡡࡶ࡮ࡷࡣ࡭ࡵ࡯࡬ࠤఀ"):
      bstack1l11ll111l_opy_(runner, name, context, runner, bstack1l11l1l1l1_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack11llll111l_opy_(bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ఁ")) else context.browser
      runner.driver_initialised = bstack1l1l_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧం")
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡧࡶ࡮ࡼࡥࡳࠢ࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡷࡪࠦࡡࡵࡶࡵ࡭ࡧࡻࡴࡦ࠼ࠣࡿࢂ࠭ః").format(str(e)))
def bstack11l1l11l11_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    bstack1l11ll111l_opy_(runner, name, context, context.feature, bstack1l11l1l1l1_opy_, *args)
    try:
      if not bstack1l1lllll_opy_:
        bstack1ll1ll11ll_opy_ = threading.current_thread().bstackSessionDriver if bstack11llll111l_opy_(bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩఄ")) else context.browser
        if is_driver_active(bstack1ll1ll11ll_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣ࡫࡫ࡡࡵࡷࡵࡩࠧఅ")
          bstack1l11l1llll_opy_ = str(runner.feature.name)
          bstack11l11l1ll1_opy_(context, bstack1l11l1llll_opy_)
          bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪఆ") + json.dumps(bstack1l11l1llll_opy_) + bstack1l1l_opy_ (u"࠭ࡽࡾࠩఇ"))
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡩࡩࡦࡺࡵࡳࡧ࠽ࠤࢀࢃࠧఈ").format(str(e)))
def bstack11l1ll11_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    if hasattr(context, bstack1l1l_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪఉ")):
        bstack1lll11l1l1_opy_.start_test(context)
    target = context.scenario if hasattr(context, bstack1l1l_opy_ (u"ࠩࡶࡧࡪࡴࡡࡳ࡫ࡲࠫఊ")) else context.feature
    bstack1l11ll111l_opy_(runner, name, context, target, bstack1l11l1l1l1_opy_, *args)
@measure(event_name=EVENTS.bstack1l1l11l11l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1ll11l1ll_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    if len(context.scenario.tags) == 0: bstack1lll11l1l1_opy_.start_test(context)
    bstack1l11ll111l_opy_(runner, name, context, context.scenario, bstack1l11l1l1l1_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack11ll111ll1_opy_.bstack1l1ll11ll_opy_(context, *args)
    try:
      bstack1ll1ll11ll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩఋ"), context.browser)
      if is_driver_active(bstack1ll1ll11ll_opy_):
        bstack11l1llllll_opy_.bstack111ll1llll_opy_(bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪఌ"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack1l1l_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢ఍")
        if (not bstack1l1lllll_opy_):
          scenario_name = args[0].name
          feature_name = bstack1l11l1llll_opy_ = str(runner.feature.name)
          bstack1l11l1llll_opy_ = feature_name + bstack1l1l_opy_ (u"࠭ࠠ࠮ࠢࠪఎ") + scenario_name
          if runner.driver_initialised == bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤఏ"):
            bstack11l11l1ll1_opy_(context, bstack1l11l1llll_opy_)
            bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭ఐ") + json.dumps(bstack1l11l1llll_opy_) + bstack1l1l_opy_ (u"ࠩࢀࢁࠬ఑"))
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢ࡬ࡲࠥࡨࡥࡧࡱࡵࡩࠥࡹࡣࡦࡰࡤࡶ࡮ࡵ࠺ࠡࡽࢀࠫఒ").format(str(e)))
@measure(event_name=EVENTS.bstack1lll1l1l11_opy_, stage=STAGE.bstack11lll1l1_opy_, hook_type=bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡗࡹ࡫ࡰࠣఓ"), bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11l11l1lll_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    bstack1l11ll111l_opy_(runner, name, context, args[0], bstack1l11l1l1l1_opy_, *args)
    try:
      bstack1ll1ll11ll_opy_ = threading.current_thread().bstackSessionDriver if bstack11llll111l_opy_(bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫఔ")) else context.browser
      if is_driver_active(bstack1ll1ll11ll_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack1l1l_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦక")
        bstack1lll11l1l1_opy_.bstack1l11ll11l_opy_(args[0])
        if runner.driver_initialised == bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧఖ"):
          feature_name = bstack1l11l1llll_opy_ = str(runner.feature.name)
          bstack1l11l1llll_opy_ = feature_name + bstack1l1l_opy_ (u"ࠨࠢ࠰ࠤࠬగ") + context.scenario.name
          bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧఘ") + json.dumps(bstack1l11l1llll_opy_) + bstack1l1l_opy_ (u"ࠪࢁࢂ࠭ఙ"))
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣ࡭ࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡵࡧࡳ࠾ࠥࢁࡽࠨచ").format(str(e)))
@measure(event_name=EVENTS.bstack1lll1l1l11_opy_, stage=STAGE.bstack11lll1l1_opy_, hook_type=bstack1l1l_opy_ (u"ࠧࡧࡦࡵࡧࡵࡗࡹ࡫ࡰࠣఛ"), bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11llll11_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
  bstack1lll11l1l1_opy_.bstack1llll1ll_opy_(args[0])
  try:
    step_status = args[0].status.name
    bstack1ll1ll11ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬజ") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack1ll1ll11ll_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack1l1l_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧఝ")
        feature_name = bstack1l11l1llll_opy_ = str(runner.feature.name)
        bstack1l11l1llll_opy_ = feature_name + bstack1l1l_opy_ (u"ࠨࠢ࠰ࠤࠬఞ") + context.scenario.name
        bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧట") + json.dumps(bstack1l11l1llll_opy_) + bstack1l1l_opy_ (u"ࠪࢁࢂ࠭ఠ"))
    if str(step_status).lower() == bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫడ"):
      bstack11l11l1l11_opy_ = bstack1l1l_opy_ (u"ࠬ࠭ఢ")
      bstack1ll1l11ll_opy_ = bstack1l1l_opy_ (u"࠭ࠧణ")
      bstack1lll1ll1_opy_ = bstack1l1l_opy_ (u"ࠧࠨత")
      try:
        import traceback
        bstack11l11l1l11_opy_ = runner.exception.__class__.__name__
        bstack1l1ll1ll1l_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1ll1l11ll_opy_ = bstack1l1l_opy_ (u"ࠨࠢࠪథ").join(bstack1l1ll1ll1l_opy_)
        bstack1lll1ll1_opy_ = bstack1l1ll1ll1l_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l1l11lll_opy_.format(str(e)))
      bstack11l11l1l11_opy_ += bstack1lll1ll1_opy_
      bstack1ll11111ll_opy_(context, json.dumps(str(args[0].name) + bstack1l1l_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣద") + str(bstack1ll1l11ll_opy_)),
                          bstack1l1l_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤధ"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱࠤన"):
        bstack1l11l111l1_opy_(getattr(context, bstack1l1l_opy_ (u"ࠬࡶࡡࡨࡧࠪ఩"), None), bstack1l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨప"), bstack11l11l1l11_opy_)
        bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬఫ") + json.dumps(str(args[0].name) + bstack1l1l_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢబ") + str(bstack1ll1l11ll_opy_)) + bstack1l1l_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡦࡴࡵࡳࡷࠨࡽࡾࠩభ"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣమ"):
        bstack11ll11111_opy_(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫయ"), bstack1l1l_opy_ (u"࡙ࠧࡣࡦࡰࡤࡶ࡮ࡵࠠࡧࡣ࡬ࡰࡪࡪࠠࡸ࡫ࡷ࡬࠿ࠦ࡜࡯ࠤర") + str(bstack11l11l1l11_opy_))
    else:
      bstack1ll11111ll_opy_(context, bstack1l1l_opy_ (u"ࠨࡐࡢࡵࡶࡩࡩࠧࠢఱ"), bstack1l1l_opy_ (u"ࠢࡪࡰࡩࡳࠧల"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࠨళ"):
        bstack1l11l111l1_opy_(getattr(context, bstack1l1l_opy_ (u"ࠩࡳࡥ࡬࡫ࠧఴ"), None), bstack1l1l_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥవ"))
      bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩశ") + json.dumps(str(args[0].name) + bstack1l1l_opy_ (u"ࠧࠦ࠭ࠡࡒࡤࡷࡸ࡫ࡤࠢࠤష")) + bstack1l1l_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦ࡮ࡴࡦࡰࠤࢀࢁࠬస"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧహ"):
        bstack11ll11111_opy_(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ఺"))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡳࡵࡧࡳ࠾ࠥࢁࡽࠨ఻").format(str(e)))
  bstack1l11ll111l_opy_(runner, name, context, args[0], bstack1l11l1l1l1_opy_, *args)
@measure(event_name=EVENTS.bstack1llll111l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1llllll11l_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
  bstack1lll11l1l1_opy_.end_test(args[0])
  try:
    bstack1l111111_opy_ = args[0].status.name
    bstack1ll1ll11ll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳ఼ࠩ"), context.browser)
    bstack11ll111ll1_opy_.bstack111l1l1ll_opy_(bstack1ll1ll11ll_opy_)
    if str(bstack1l111111_opy_).lower() == bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫఽ"):
      bstack11l11l1l11_opy_ = bstack1l1l_opy_ (u"ࠬ࠭ా")
      bstack1ll1l11ll_opy_ = bstack1l1l_opy_ (u"࠭ࠧి")
      bstack1lll1ll1_opy_ = bstack1l1l_opy_ (u"ࠧࠨీ")
      try:
        import traceback
        bstack11l11l1l11_opy_ = runner.exception.__class__.__name__
        bstack1l1ll1ll1l_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1ll1l11ll_opy_ = bstack1l1l_opy_ (u"ࠨࠢࠪు").join(bstack1l1ll1ll1l_opy_)
        bstack1lll1ll1_opy_ = bstack1l1ll1ll1l_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l1l11lll_opy_.format(str(e)))
      bstack11l11l1l11_opy_ += bstack1lll1ll1_opy_
      bstack1ll11111ll_opy_(context, json.dumps(str(args[0].name) + bstack1l1l_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣూ") + str(bstack1ll1l11ll_opy_)),
                          bstack1l1l_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤృ"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨౄ") or runner.driver_initialised == bstack1l1l_opy_ (u"ࠬ࡯࡮ࡴࡶࡨࡴࠬ౅"):
        bstack1l11l111l1_opy_(getattr(context, bstack1l1l_opy_ (u"࠭ࡰࡢࡩࡨࠫె"), None), bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢే"), bstack11l11l1l11_opy_)
        bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ై") + json.dumps(str(args[0].name) + bstack1l1l_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣ౉") + str(bstack1ll1l11ll_opy_)) + bstack1l1l_opy_ (u"ࠪ࠰ࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣࡧࡵࡶࡴࡸࠢࡾࡿࠪొ"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨో") or runner.driver_initialised == bstack1l1l_opy_ (u"ࠬ࡯࡮ࡴࡶࡨࡴࠬౌ"):
        bstack11ll11111_opy_(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ్࠭"), bstack1l1l_opy_ (u"ࠢࡔࡥࡨࡲࡦࡸࡩࡰࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦ౎") + str(bstack11l11l1l11_opy_))
    else:
      bstack1ll11111ll_opy_(context, bstack1l1l_opy_ (u"ࠣࡒࡤࡷࡸ࡫ࡤࠢࠤ౏"), bstack1l1l_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢ౐"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧ౑") or runner.driver_initialised == bstack1l1l_opy_ (u"ࠫ࡮ࡴࡳࡵࡧࡳࠫ౒"):
        bstack1l11l111l1_opy_(getattr(context, bstack1l1l_opy_ (u"ࠬࡶࡡࡨࡧࠪ౓"), None), bstack1l1l_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨ౔"))
      bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ౕࠬ") + json.dumps(str(args[0].name) + bstack1l1l_opy_ (u"ࠣࠢ࠰ࠤࡕࡧࡳࡴࡧࡧౖࠥࠧ")) + bstack1l1l_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧࢃࡽࠨ౗"))
      if runner.driver_initialised == bstack1l1l_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧౘ") or runner.driver_initialised == bstack1l1l_opy_ (u"ࠫ࡮ࡴࡳࡵࡧࡳࠫౙ"):
        bstack11ll11111_opy_(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧౚ"))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡ࡫ࡱࠤࡦ࡬ࡴࡦࡴࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨ౛").format(str(e)))
  bstack1l11ll111l_opy_(runner, name, context, context.scenario, bstack1l11l1l1l1_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack1l11lll11_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    target = context.scenario if hasattr(context, bstack1l1l_opy_ (u"ࠧࡴࡥࡨࡲࡦࡸࡩࡰࠩ౜")) else context.feature
    bstack1l11ll111l_opy_(runner, name, context, target, bstack1l11l1l1l1_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack11lll1l1l_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    try:
      bstack1ll1ll11ll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧౝ"), context.browser)
      bstack11llllllll_opy_ = bstack1l1l_opy_ (u"ࠩࠪ౞")
      if context.failed is True:
        bstack11ll1lll_opy_ = []
        bstack1ll1l1l111_opy_ = []
        bstack1lll11ll1l_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack11ll1lll_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack1l1ll1ll1l_opy_ = traceback.format_tb(exc_tb)
            bstack11ll1l11_opy_ = bstack1l1l_opy_ (u"ࠪࠤࠬ౟").join(bstack1l1ll1ll1l_opy_)
            bstack1ll1l1l111_opy_.append(bstack11ll1l11_opy_)
            bstack1lll11ll1l_opy_.append(bstack1l1ll1ll1l_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l1l11lll_opy_.format(str(e)))
        bstack11l11l1l11_opy_ = bstack1l1l_opy_ (u"ࠫࠬౠ")
        for i in range(len(bstack11ll1lll_opy_)):
          bstack11l11l1l11_opy_ += bstack11ll1lll_opy_[i] + bstack1lll11ll1l_opy_[i] + bstack1l1l_opy_ (u"ࠬࡢ࡮ࠨౡ")
        bstack11llllllll_opy_ = bstack1l1l_opy_ (u"࠭ࠠࠨౢ").join(bstack1ll1l1l111_opy_)
        if runner.driver_initialised in [bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠣౣ"), bstack1l1l_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧ౤")]:
          bstack1ll11111ll_opy_(context, bstack11llllllll_opy_, bstack1l1l_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ౥"))
          bstack1l11l111l1_opy_(getattr(context, bstack1l1l_opy_ (u"ࠪࡴࡦ࡭ࡥࠨ౦"), None), bstack1l1l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ౧"), bstack11l11l1l11_opy_)
          bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ౨") + json.dumps(bstack11llllllll_opy_) + bstack1l1l_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭౩"))
          bstack11ll11111_opy_(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ౪"), bstack1l1l_opy_ (u"ࠣࡕࡲࡱࡪࠦࡳࡤࡧࡱࡥࡷ࡯࡯ࡴࠢࡩࡥ࡮ࡲࡥࡥ࠼ࠣࡠࡳࠨ౫") + str(bstack11l11l1l11_opy_))
          bstack1llll1111l_opy_ = bstack111llll1_opy_(bstack11llllllll_opy_, runner.feature.name, logger)
          if (bstack1llll1111l_opy_ != None):
            bstack1lll11111l_opy_.append(bstack1llll1111l_opy_)
      else:
        if runner.driver_initialised in [bstack1l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠥ౬"), bstack1l1l_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡥࡱࡲࠢ౭")]:
          bstack1ll11111ll_opy_(context, bstack1l1l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩ࠿ࠦࠢ౮") + str(runner.feature.name) + bstack1l1l_opy_ (u"ࠧࠦࡰࡢࡵࡶࡩࡩࠧࠢ౯"), bstack1l1l_opy_ (u"ࠨࡩ࡯ࡨࡲࠦ౰"))
          bstack1l11l111l1_opy_(getattr(context, bstack1l1l_opy_ (u"ࠧࡱࡣࡪࡩࠬ౱"), None), bstack1l1l_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ౲"))
          bstack1ll1ll11ll_opy_.execute_script(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ౳") + json.dumps(bstack1l1l_opy_ (u"ࠥࡊࡪࡧࡴࡶࡴࡨ࠾ࠥࠨ౴") + str(runner.feature.name) + bstack1l1l_opy_ (u"ࠦࠥࡶࡡࡴࡵࡨࡨࠦࠨ౵")) + bstack1l1l_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣࡿࢀࠫ౶"))
          bstack11ll11111_opy_(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭౷"))
          bstack1llll1111l_opy_ = bstack111llll1_opy_(bstack11llllllll_opy_, runner.feature.name, logger)
          if (bstack1llll1111l_opy_ != None):
            bstack1lll11111l_opy_.append(bstack1llll1111l_opy_)
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡱࡦࡸ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢ࡬ࡲࠥࡧࡦࡵࡧࡵࠤ࡫࡫ࡡࡵࡷࡵࡩ࠿ࠦࡻࡾࠩ౸").format(str(e)))
    bstack1l11ll111l_opy_(runner, name, context, context.feature, bstack1l11l1l1l1_opy_, *args)
@measure(event_name=EVENTS.bstack1lll1l1l11_opy_, stage=STAGE.bstack11lll1l1_opy_, hook_type=bstack1l1l_opy_ (u"ࠣࡣࡩࡸࡪࡸࡁ࡭࡮ࠥ౹"), bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1l111l1ll1_opy_(runner, name, context, bstack1l11l1l1l1_opy_, *args):
    bstack1l11ll111l_opy_(runner, name, context, runner, bstack1l11l1l1l1_opy_, *args)
def bstack1ll111lll1_opy_(self, name, context, *args):
  try:
    if bstack1l1lll11l1_opy_:
      platform_index = int(threading.current_thread()._name) % bstack1l1l11ll1_opy_
      bstack111l1ll1_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ౺")][platform_index]
      os.environ[bstack1l1l_opy_ (u"ࠪࡇ࡚ࡘࡒࡆࡐࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡄࡂࡖࡄࠫ౻")] = json.dumps(bstack111l1ll1_opy_)
    global bstack1l11l1l1l1_opy_
    if not hasattr(self, bstack1l1l_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࡹࡥࡥࠩ౼")):
      self.driver_initialised = None
    bstack1l1111ll1l_opy_ = {
        bstack1l1l_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠩ౽"): bstack11l111l1ll_opy_,
        bstack1l1l_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡦࡦࡣࡷࡹࡷ࡫ࠧ౾"): bstack11l1l11l11_opy_,
        bstack1l1l_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡵࡣࡪࠫ౿"): bstack11l1ll11_opy_,
        bstack1l1l_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪಀ"): bstack1ll11l1ll_opy_,
        bstack1l1l_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠧಁ"): bstack11l11l1lll_opy_,
        bstack1l1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡸࡪࡶࠧಂ"): bstack11llll11_opy_,
        bstack1l1l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬಃ"): bstack1llllll11l_opy_,
        bstack1l1l_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡹࡧࡧࠨ಄"): bstack1l11lll11_opy_,
        bstack1l1l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤ࡬ࡥࡢࡶࡸࡶࡪ࠭ಅ"): bstack11lll1l1l_opy_,
        bstack1l1l_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠪಆ"): bstack1l111l1ll1_opy_
    }
    handler = bstack1l1111ll1l_opy_.get(name, bstack1l11l1l1l1_opy_)
    try:
      handler(self, name, context, bstack1l11l1l1l1_opy_, *args)
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡦࡪ࡮ࡡࡷࡧࠣ࡬ࡴࡵ࡫ࠡࡪࡤࡲࡩࡲࡥࡳࠢࡾࢁ࠿ࠦࡻࡾࠩಇ").format(name, str(e)))
    if name in [bstack1l1l_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩಈ"), bstack1l1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫಉ"), bstack1l1l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡥࡱࡲࠧಊ")]:
      try:
        bstack1ll1ll11ll_opy_ = threading.current_thread().bstackSessionDriver if bstack11llll111l_opy_(bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫಋ")) else context.browser
        bstack11lll1lll1_opy_ = (
          (name == bstack1l1l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠩಌ") and self.driver_initialised == bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠦ಍")) or
          (name == bstack1l1l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥࠨಎ") and self.driver_initialised == bstack1l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠥಏ")) or
          (name == bstack1l1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫಐ") and self.driver_initialised in [bstack1l1l_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨ಑"), bstack1l1l_opy_ (u"ࠧ࡯࡮ࡴࡶࡨࡴࠧಒ")]) or
          (name == bstack1l1l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡴࡦࡲࠪಓ") and self.driver_initialised == bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧಔ"))
        )
        if bstack11lll1lll1_opy_:
          self.driver_initialised = None
          if bstack1ll1ll11ll_opy_ and hasattr(bstack1ll1ll11ll_opy_, bstack1l1l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠬಕ")):
            try:
              bstack1ll1ll11ll_opy_.quit()
            except Exception as e:
              logger.debug(bstack1l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡳࡸ࡭ࡹࡺࡩ࡯ࡩࠣࡨࡷ࡯ࡶࡦࡴࠣ࡭ࡳࠦࡢࡦࡪࡤࡺࡪࠦࡨࡰࡱ࡮࠾ࠥࢁࡽࠨಖ").format(str(e)))
      except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡧࡦࡵࡧࡵࠤ࡭ࡵ࡯࡬ࠢࡦࡰࡪࡧ࡮ࡶࡲࠣࡪࡴࡸࠠࡼࡿ࠽ࠤࢀࢃࠧಗ").format(name, str(e)))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠫࡈࡸࡩࡵ࡫ࡦࡥࡱࠦࡥࡳࡴࡲࡶࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥࠡࡴࡸࡲࠥ࡮࡯ࡰ࡭ࠣࡿࢂࡀࠠࡼࡿࠪಘ").format(name, str(e)))
    try:
      bstack1l11l1l1l1_opy_(self, name, context, *args)
    except Exception as e2:
      logger.debug(bstack1l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡲࡶ࡮࡭ࡩ࡯ࡣ࡯ࠤࡧ࡫ࡨࡢࡸࡨࠤ࡭ࡵ࡯࡬ࠢࡾࢁ࠿ࠦࡻࡾࠩಙ").format(name, str(e2)))
def bstack1llll1lll_opy_(config, startdir):
  return bstack1l1l_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷࡀࠠࡼ࠲ࢀࠦಚ").format(bstack1l1l_opy_ (u"ࠢࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠨಛ"))
notset = Notset()
def bstack1l1ll1111l_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1l111l111_opy_
  if str(name).lower() == bstack1l1l_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨಜ"):
    return bstack1l1l_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣಝ")
  else:
    return bstack1l111l111_opy_(self, name, default, skip)
def bstack11111l1l1_opy_(item, when):
  global bstack1ll11l11l1_opy_
  try:
    bstack1ll11l11l1_opy_(item, when)
  except Exception as e:
    pass
def bstack1lll1l11_opy_():
  return
def bstack11l11lll1l_opy_(type, name, status, reason, bstack1l111111l1_opy_, bstack11l11lll_opy_):
  bstack1l1111l11l_opy_ = {
    bstack1l1l_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪಞ"): type,
    bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧಟ"): {}
  }
  if type == bstack1l1l_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧಠ"):
    bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಡ")][bstack1l1l_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ಢ")] = bstack1l111111l1_opy_
    bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫಣ")][bstack1l1l_opy_ (u"ࠩࡧࡥࡹࡧࠧತ")] = json.dumps(str(bstack11l11lll_opy_))
  if type == bstack1l1l_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫಥ"):
    bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧದ")][bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪಧ")] = name
  if type == bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩನ"):
    bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ಩")][bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨಪ")] = status
    if status == bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩಫ"):
      bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಬ")][bstack1l1l_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫಭ")] = json.dumps(str(reason))
  bstack1ll1llll1_opy_ = bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪಮ").format(json.dumps(bstack1l1111l11l_opy_))
  return bstack1ll1llll1_opy_
def bstack1ll1ll1111_opy_(driver_command, response):
    if driver_command == bstack1l1l_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪಯ"):
        bstack11l1llllll_opy_.bstack1ll11l111l_opy_({
            bstack1l1l_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭ರ"): response[bstack1l1l_opy_ (u"ࠨࡸࡤࡰࡺ࡫ࠧಱ")],
            bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩಲ"): bstack11l1llllll_opy_.current_test_uuid()
        })
def bstack1l1llllll1_opy_(item, call, rep):
  global bstack111lll1ll_opy_
  global bstack1l11l11l_opy_
  global bstack1l1lllll_opy_
  name = bstack1l1l_opy_ (u"ࠪࠫಳ")
  try:
    if rep.when == bstack1l1l_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ಴"):
      bstack1lll1lll1_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack1l1lllll_opy_:
          name = str(rep.nodeid)
          bstack11ll1llll_opy_ = bstack11l11lll1l_opy_(bstack1l1l_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ವ"), name, bstack1l1l_opy_ (u"࠭ࠧಶ"), bstack1l1l_opy_ (u"ࠧࠨಷ"), bstack1l1l_opy_ (u"ࠨࠩಸ"), bstack1l1l_opy_ (u"ࠩࠪಹ"))
          threading.current_thread().bstack1llll1llll_opy_ = name
          for driver in bstack1l11l11l_opy_:
            if bstack1lll1lll1_opy_ == driver.session_id:
              driver.execute_script(bstack11ll1llll_opy_)
      except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ಺").format(str(e)))
      try:
        bstack1l1l111l1_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack1l1l_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ಻"):
          status = bstack1l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨ಼ࠬ") if rep.outcome.lower() == bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ಽ") else bstack1l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧಾ")
          reason = bstack1l1l_opy_ (u"ࠨࠩಿ")
          if status == bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩೀ"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack1l1l_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨು") if status == bstack1l1l_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫೂ") else bstack1l1l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫೃ")
          data = name + bstack1l1l_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨೄ") if status == bstack1l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ೅") else name + bstack1l1l_opy_ (u"ࠨࠢࡩࡥ࡮ࡲࡥࡥࠣࠣࠫೆ") + reason
          bstack1ll111l1l_opy_ = bstack11l11lll1l_opy_(bstack1l1l_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫೇ"), bstack1l1l_opy_ (u"ࠪࠫೈ"), bstack1l1l_opy_ (u"ࠫࠬ೉"), bstack1l1l_opy_ (u"ࠬ࠭ೊ"), level, data)
          for driver in bstack1l11l11l_opy_:
            if bstack1lll1lll1_opy_ == driver.session_id:
              driver.execute_script(bstack1ll111l1l_opy_)
      except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡴࡴࡴࡦࡺࡷࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪೋ").format(str(e)))
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽࢀࠫೌ").format(str(e)))
  bstack111lll1ll_opy_(item, call, rep)
def bstack1ll111lll_opy_(driver, bstack11ll1ll1ll_opy_, test=None):
  global bstack1ll1ll1l11_opy_
  if test != None:
    bstack1l1l11l111_opy_ = getattr(test, bstack1l1l_opy_ (u"ࠨࡰࡤࡱࡪ್࠭"), None)
    bstack11l1111lll_opy_ = getattr(test, bstack1l1l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ೎"), None)
    PercySDK.screenshot(driver, bstack11ll1ll1ll_opy_, bstack1l1l11l111_opy_=bstack1l1l11l111_opy_, bstack11l1111lll_opy_=bstack11l1111lll_opy_, bstack1ll11l1111_opy_=bstack1ll1ll1l11_opy_)
  else:
    PercySDK.screenshot(driver, bstack11ll1ll1ll_opy_)
@measure(event_name=EVENTS.bstack1lllllll1_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1l11l111l_opy_(driver):
  if bstack11l1lllll_opy_.bstack1ll1l11l_opy_() is True or bstack11l1lllll_opy_.capturing() is True:
    return
  bstack11l1lllll_opy_.bstack1l11l1l111_opy_()
  while not bstack11l1lllll_opy_.bstack1ll1l11l_opy_():
    bstack11lll111l1_opy_ = bstack11l1lllll_opy_.bstack1ll11l11l_opy_()
    bstack1ll111lll_opy_(driver, bstack11lll111l1_opy_)
  bstack11l1lllll_opy_.bstack1111ll11l_opy_()
def bstack1lll1lll11_opy_(sequence, driver_command, response = None, bstack1l1l111l_opy_ = None, args = None):
    try:
      if sequence != bstack1l1l_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪ೏"):
        return
      if percy.bstack1l1l11111l_opy_() == bstack1l1l_opy_ (u"ࠦ࡫ࡧ࡬ࡴࡧࠥ೐"):
        return
      bstack11lll111l1_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ೑"), None)
      for command in bstack1l1ll111l_opy_:
        if command == driver_command:
          with bstack1l111l1ll_opy_:
            bstack1llllll1l_opy_ = bstack1l11l11l_opy_.copy()
          for driver in bstack1llllll1l_opy_:
            bstack1l11l111l_opy_(driver)
      bstack1l11l111ll_opy_ = percy.bstack1lll11lll1_opy_()
      if driver_command in bstack11l111l11_opy_[bstack1l11l111ll_opy_]:
        bstack11l1lllll_opy_.bstack11ll1l111_opy_(bstack11lll111l1_opy_, driver_command)
    except Exception as e:
      pass
def bstack1ll11111l_opy_(framework_name):
  if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥ࡭ࡰࡦࡢࡧࡦࡲ࡬ࡦࡦࠪ೒")):
      return
  bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ೓"), True)
  global bstack1lll1l11l1_opy_
  global bstack11ll1l11ll_opy_
  global bstack1l1l1l11l1_opy_
  bstack1lll1l11l1_opy_ = framework_name
  logger.info(bstack11111111l_opy_.format(bstack1lll1l11l1_opy_.split(bstack1l1l_opy_ (u"ࠨ࠯ࠪ೔"))[0]))
  bstack11111lll1_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1l1lll11l1_opy_:
      Service.start = bstack1l11111ll1_opy_
      Service.stop = bstack1l1l11l1_opy_
      webdriver.Remote.get = bstack1l1111111_opy_
      WebDriver.quit = bstack11l1111l1l_opy_
      webdriver.Remote.__init__ = bstack111lll1ll1_opy_
    if not bstack1l1lll11l1_opy_:
        webdriver.Remote.__init__ = bstack1lllll11ll_opy_
    WebDriver.getAccessibilityResults = getAccessibilityResults
    WebDriver.get_accessibility_results = getAccessibilityResults
    WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
    WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
    WebDriver.performScan = perform_scan
    WebDriver.perform_scan = perform_scan
    WebDriver.execute = bstack11ll1ll11_opy_
    bstack11ll1l11ll_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack1l1lll11l1_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack1lllll111_opy_
  except Exception as e:
    pass
  bstack11l1ll11l1_opy_()
  if not bstack11ll1l11ll_opy_:
    bstack1l1111ll_opy_(bstack1l1l_opy_ (u"ࠤࡓࡥࡨࡱࡡࡨࡧࡶࠤࡳࡵࡴࠡ࡫ࡱࡷࡹࡧ࡬࡭ࡧࡧࠦೕ"), bstack11l1111l_opy_)
  if bstack11l1111l1_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      if hasattr(RemoteConnection, bstack1l1l_opy_ (u"ࠪࡣ࡬࡫ࡴࡠࡲࡵࡳࡽࡿ࡟ࡶࡴ࡯ࠫೖ")) and callable(getattr(RemoteConnection, bstack1l1l_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬ೗"))):
        RemoteConnection._get_proxy_url = bstack1l1l111l1l_opy_
      else:
        from selenium.webdriver.remote.client_config import ClientConfig
        ClientConfig.get_proxy_url = bstack1l1l111l1l_opy_
    except Exception as e:
      logger.error(bstack11l11111l_opy_.format(str(e)))
  if bstack1ll11ll1ll_opy_():
    bstack11ll1ll1l_opy_(CONFIG, logger)
  if (bstack1l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ೘") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1l1l11111l_opy_() == bstack1l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦ೙"):
          bstack1lllll11_opy_(bstack1lll1lll11_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1lll1l11ll_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack11ll11l1l_opy_
      except Exception as e:
        logger.warning(bstack1111ll1l1_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1l1ll1l1l1_opy_
      except Exception as e:
        logger.debug(bstack1ll1l1111l_opy_ + str(e))
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack1111ll1l1_opy_)
    Output.start_test = bstack11llll1lll_opy_
    Output.end_test = bstack1l1lll1l1_opy_
    TestStatus.__init__ = bstack1l1111l1_opy_
    QueueItem.__init__ = bstack11l111l111_opy_
    pabot._create_items = bstack11ll1l11l_opy_
    try:
      from pabot import __version__ as bstack1ll1l11l11_opy_
      if version.parse(bstack1ll1l11l11_opy_) >= version.parse(bstack1l1l_opy_ (u"ࠧ࠶࠰࠳࠲࠵࠭೚")):
        pabot._run = bstack1ll1111l1_opy_
      elif version.parse(bstack1ll1l11l11_opy_) >= version.parse(bstack1l1l_opy_ (u"ࠨ࠶࠱࠶࠳࠶ࠧ೛")):
        pabot._run = bstack1l1ll11l1_opy_
      elif version.parse(bstack1ll1l11l11_opy_) >= version.parse(bstack1l1l_opy_ (u"ࠩ࠵࠲࠶࠻࠮࠱ࠩ೜")):
        pabot._run = bstack1ll11l111_opy_
      elif version.parse(bstack1ll1l11l11_opy_) >= version.parse(bstack1l1l_opy_ (u"ࠪ࠶࠳࠷࠳࠯࠲ࠪೝ")):
        pabot._run = bstack1l1l11l11_opy_
      else:
        pabot._run = bstack1l1l1lll1_opy_
    except Exception as e:
      pabot._run = bstack1l1l1lll1_opy_
    pabot._create_command_for_execution = bstack111lllll1_opy_
    pabot._report_results = bstack11l1ll1111_opy_
  if bstack1l1l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫೞ") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack11l1l11ll_opy_)
    Runner.run_hook = bstack1ll111lll1_opy_
    Step.run = bstack1l1111lll1_opy_
  if bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ೟") in str(framework_name).lower():
    if not bstack1l1lll11l1_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1llll1lll_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1lll1l11_opy_
      Config.getoption = bstack1l1ll1111l_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack1l1llllll1_opy_
    except Exception as e:
      pass
def bstack1lll11l1_opy_():
  global CONFIG
  if bstack1l1l_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ೠ") in CONFIG and int(CONFIG[bstack1l1l_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧೡ")]) > 1:
    logger.warning(bstack1l1111l1ll_opy_)
def bstack11lll1ll1_opy_(arg, bstack11lllll1l1_opy_, bstack11l11lll11_opy_=None):
  global CONFIG
  global bstack11ll1lll1l_opy_
  global bstack11l11l11l1_opy_
  global bstack1l1lll11l1_opy_
  global bstack1l1ll1l1_opy_
  bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨೢ")
  if bstack11lllll1l1_opy_ and isinstance(bstack11lllll1l1_opy_, str):
    bstack11lllll1l1_opy_ = eval(bstack11lllll1l1_opy_)
  CONFIG = bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩೣ")]
  bstack11ll1lll1l_opy_ = bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫ೤")]
  bstack11l11l11l1_opy_ = bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭೥")]
  bstack1l1lll11l1_opy_ = bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨ೦")]
  bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ೧"), bstack1l1lll11l1_opy_)
  os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ೨")] = bstack111lllllll_opy_
  os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠧ೩")] = json.dumps(CONFIG)
  os.environ[bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡊࡘࡆࡤ࡛ࡒࡍࠩ೪")] = bstack11ll1lll1l_opy_
  os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫ೫")] = str(bstack11l11l11l1_opy_)
  os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔ࡞࡚ࡅࡔࡖࡢࡔࡑ࡛ࡇࡊࡐࠪ೬")] = str(True)
  if bstack1l11111l11_opy_(arg, [bstack1l1l_opy_ (u"ࠬ࠳࡮ࠨ೭"), bstack1l1l_opy_ (u"࠭࠭࠮ࡰࡸࡱࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧ೮")]) != -1:
    os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡂࡔࡄࡐࡑࡋࡌࠨ೯")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1l1l11l1l_opy_)
    return
  bstack1111111l1_opy_()
  global bstack111111111_opy_
  global bstack1ll1ll1l11_opy_
  global bstack1lllll1ll1_opy_
  global bstack1l111lll1l_opy_
  global bstack1l1l11llll_opy_
  global bstack1l1l1l11l1_opy_
  global bstack1l1ll11lll_opy_
  arg.append(bstack1l1l_opy_ (u"ࠣ࠯࡚ࠦ೰"))
  arg.append(bstack1l1l_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡦ࠼ࡐࡳࡩࡻ࡬ࡦࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡭ࡲࡶ࡯ࡳࡶࡨࡨ࠿ࡶࡹࡵࡧࡶࡸ࠳ࡖࡹࡵࡧࡶࡸ࡜ࡧࡲ࡯࡫ࡱ࡫ࠧೱ"))
  arg.append(bstack1l1l_opy_ (u"ࠥ࠱࡜ࠨೲ"))
  arg.append(bstack1l1l_opy_ (u"ࠦ࡮࡭࡮ࡰࡴࡨ࠾࡙࡮ࡥࠡࡪࡲࡳࡰ࡯࡭ࡱ࡮ࠥೳ"))
  global bstack111ll1l1l_opy_
  global bstack11l1lll111_opy_
  global bstack11l1lll1ll_opy_
  global bstack1l1llll11_opy_
  global bstack1l1l1l1l11_opy_
  global bstack11lll11l1l_opy_
  global bstack1l11lll1ll_opy_
  global bstack111llll111_opy_
  global bstack11l1lllll1_opy_
  global bstack1ll1l1ll1l_opy_
  global bstack1l111l111_opy_
  global bstack1ll11l11l1_opy_
  global bstack111lll1ll_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack111ll1l1l_opy_ = webdriver.Remote.__init__
    bstack11l1lll111_opy_ = WebDriver.quit
    bstack111llll111_opy_ = WebDriver.close
    bstack11l1lllll1_opy_ = WebDriver.get
    bstack11l1lll1ll_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack1l1l1l1l1_opy_(CONFIG) and bstack111ll1111_opy_():
    if bstack1llllll1l1_opy_() < version.parse(bstack1llll11l_opy_):
      logger.error(bstack11lll1lll_opy_.format(bstack1llllll1l1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack1l1l_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭೴")) and callable(getattr(RemoteConnection, bstack1l1l_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ೵"))):
          bstack1ll1l1ll1l_opy_ = RemoteConnection._get_proxy_url
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          bstack1ll1l1ll1l_opy_ = ClientConfig.get_proxy_url
      except Exception as e:
        logger.error(bstack11l11111l_opy_.format(str(e)))
  try:
    from _pytest.config import Config
    bstack1l111l111_opy_ = Config.getoption
    from _pytest import runner
    bstack1ll11l11l1_opy_ = runner._update_current_test_var
  except Exception as e:
    logger.warning(bstack1l1l_opy_ (u"ࠢࠦࡵ࠽ࠤࠪࡹࠢ೶"), bstack1l1lll1ll_opy_, str(e))
  try:
    from pytest_bdd import reporting
    bstack111lll1ll_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack1l1l_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩ೷"))
  bstack1lllll1ll1_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭೸"), {}).get(bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ೹"))
  bstack1l1ll11lll_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack1llll1lll1_opy_():
      bstack111l111l_opy_.invoke(bstack11l111111_opy_.CONNECT, bstack11lll1l1l1_opy_())
    platform_index = int(os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ೺"), bstack1l1l_opy_ (u"ࠬ࠶ࠧ೻")))
  else:
    bstack1ll11111l_opy_(bstack1l11l1ll_opy_)
  os.environ[bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧ೼")] = CONFIG[bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ೽")]
  os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫ೾")] = CONFIG[bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ೿")]
  os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ഀ")] = bstack1l1lll11l1_opy_.__str__()
  from _pytest.config import main as bstack11ll11lll1_opy_
  bstack11llllll11_opy_ = []
  try:
    exit_code = bstack11ll11lll1_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack111ll1lll_opy_()
    if bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴࠨഁ") in multiprocessing.current_process().__dict__.keys():
      for bstack11ll11111l_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack11llllll11_opy_.append(bstack11ll11111l_opy_)
    try:
      bstack1l1ll1llll_opy_ = (bstack11llllll11_opy_, int(exit_code))
      bstack11l11lll11_opy_.append(bstack1l1ll1llll_opy_)
    except:
      bstack11l11lll11_opy_.append((bstack11llllll11_opy_, exit_code))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack11llllll11_opy_.append({bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪം"): bstack1l1l_opy_ (u"࠭ࡐࡳࡱࡦࡩࡸࡹࠠࠨഃ") + os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧഄ")), bstack1l1l_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧഅ"): traceback.format_exc(), bstack1l1l_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨആ"): int(os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪഇ")))})
    bstack11l11lll11_opy_.append((bstack11llllll11_opy_, 1))
def mod_behave_main(args, retries):
  try:
    from behave.configuration import Configuration
    from behave.__main__ import run_behave
    from browserstack_sdk.bstack_behave_runner import BehaveRunner
    config = Configuration(args)
    config.update_userdata({bstack1l1l_opy_ (u"ࠦࡷ࡫ࡴࡳ࡫ࡨࡷࠧഈ"): str(retries)})
    return run_behave(config, runner_class=BehaveRunner)
  except Exception as e:
    bstack1l1l1111_opy_ = e.__class__.__name__
    print(bstack1l1l_opy_ (u"ࠧࠫࡳ࠻ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡴࡸࡲࡳ࡯࡮ࡨࠢࡥࡩ࡭ࡧࡶࡦࠢࡷࡩࡸࡺࠠࠦࡵࠥഉ") % (bstack1l1l1111_opy_, e))
    return 1
def bstack11l11ll1l1_opy_(arg):
  global bstack1lll111l_opy_
  bstack1ll11111l_opy_(bstack11l1l1lll_opy_)
  os.environ[bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧഊ")] = str(bstack11l11l11l1_opy_)
  retries = bstack111l1111l_opy_.bstack1ll111l1l1_opy_(CONFIG)
  status_code = 0
  if bstack111l1111l_opy_.bstack111l11l1_opy_(CONFIG):
    status_code = mod_behave_main(arg, retries)
  else:
    from behave.__main__ import main as bstack1111lll1_opy_
    status_code = bstack1111lll1_opy_(arg)
  if status_code != 0:
    bstack1lll111l_opy_ = status_code
def bstack1lll1ll1l1_opy_():
  logger.info(bstack11l1l1llll_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1l1l_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭ഋ"), help=bstack1l1l_opy_ (u"ࠨࡉࡨࡲࡪࡸࡡࡵࡧࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡦࡳࡳ࡬ࡩࡨࠩഌ"))
  parser.add_argument(bstack1l1l_opy_ (u"ࠩ࠰ࡹࠬ഍"), bstack1l1l_opy_ (u"ࠪ࠱࠲ࡻࡳࡦࡴࡱࡥࡲ࡫ࠧഎ"), help=bstack1l1l_opy_ (u"ࠫ࡞ࡵࡵࡳࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡷࡶࡩࡷࡴࡡ࡮ࡧࠪഏ"))
  parser.add_argument(bstack1l1l_opy_ (u"ࠬ࠳࡫ࠨഐ"), bstack1l1l_opy_ (u"࠭࠭࠮࡭ࡨࡽࠬ഑"), help=bstack1l1l_opy_ (u"࡚ࠧࡱࡸࡶࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡦࡩࡣࡦࡵࡶࠤࡰ࡫ࡹࠨഒ"))
  parser.add_argument(bstack1l1l_opy_ (u"ࠨ࠯ࡩࠫഓ"), bstack1l1l_opy_ (u"ࠩ࠰࠱࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧഔ"), help=bstack1l1l_opy_ (u"ࠪ࡝ࡴࡻࡲࠡࡶࡨࡷࡹࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩക"))
  bstack1ll1l111l1_opy_ = parser.parse_args()
  try:
    bstack1l1l1l1ll1_opy_ = bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱࡫ࡪࡴࡥࡳ࡫ࡦ࠲ࡾࡳ࡬࠯ࡵࡤࡱࡵࡲࡥࠨഖ")
    if bstack1ll1l111l1_opy_.framework and bstack1ll1l111l1_opy_.framework not in (bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬഗ"), bstack1l1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠹ࠧഘ")):
      bstack1l1l1l1ll1_opy_ = bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠰ࡼࡱࡱ࠴ࡳࡢ࡯ࡳࡰࡪ࠭ങ")
    bstack11l1l11lll_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l1l1ll1_opy_)
    bstack11ll11l111_opy_ = open(bstack11l1l11lll_opy_, bstack1l1l_opy_ (u"ࠨࡴࠪച"))
    bstack1ll1l1l11_opy_ = bstack11ll11l111_opy_.read()
    bstack11ll11l111_opy_.close()
    if bstack1ll1l111l1_opy_.username:
      bstack1ll1l1l11_opy_ = bstack1ll1l1l11_opy_.replace(bstack1l1l_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠩഛ"), bstack1ll1l111l1_opy_.username)
    if bstack1ll1l111l1_opy_.key:
      bstack1ll1l1l11_opy_ = bstack1ll1l1l11_opy_.replace(bstack1l1l_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬജ"), bstack1ll1l111l1_opy_.key)
    if bstack1ll1l111l1_opy_.framework:
      bstack1ll1l1l11_opy_ = bstack1ll1l1l11_opy_.replace(bstack1l1l_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬഝ"), bstack1ll1l111l1_opy_.framework)
    file_name = bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨഞ")
    file_path = os.path.abspath(file_name)
    bstack1lllll1111_opy_ = open(file_path, bstack1l1l_opy_ (u"࠭ࡷࠨട"))
    bstack1lllll1111_opy_.write(bstack1ll1l1l11_opy_)
    bstack1lllll1111_opy_.close()
    logger.info(bstack11lll1l11_opy_)
    try:
      os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩഠ")] = bstack1ll1l111l1_opy_.framework if bstack1ll1l111l1_opy_.framework != None else bstack1l1l_opy_ (u"ࠣࠤഡ")
      config = yaml.safe_load(bstack1ll1l1l11_opy_)
      config[bstack1l1l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩഢ")] = bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠰ࡷࡪࡺࡵࡱࠩണ")
      bstack11ll1ll111_opy_(bstack11l1lll1_opy_, config)
    except Exception as e:
      logger.debug(bstack1111111ll_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack111111ll1_opy_.format(str(e)))
def bstack11ll1ll111_opy_(bstack11111ll1_opy_, config, bstack11ll1l1l1l_opy_={}):
  global bstack1l1lll11l1_opy_
  global bstack11l1lll1l1_opy_
  global bstack1l1ll1l1_opy_
  if not config:
    return
  bstack1ll1lll1l1_opy_ = bstack1llll1l1ll_opy_ if not bstack1l1lll11l1_opy_ else (
    bstack11lll11lll_opy_ if bstack1l1l_opy_ (u"ࠫࡦࡶࡰࠨത") in config else (
        bstack111lll11_opy_ if config.get(bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩഥ")) else bstack1llll1l1l_opy_
    )
)
  bstack1l11l1l1l_opy_ = False
  bstack1lll1l1ll_opy_ = False
  if bstack1l1lll11l1_opy_ is True:
      if bstack1l1l_opy_ (u"࠭ࡡࡱࡲࠪദ") in config:
          bstack1l11l1l1l_opy_ = True
      else:
          bstack1lll1l1ll_opy_ = True
  bstack1l1ll11l1l_opy_ = bstack1ll11ll1l_opy_.bstack11lll1ll_opy_(config, bstack11l1lll1l1_opy_)
  bstack111llll11_opy_ = bstack1l1ll11l11_opy_()
  data = {
    bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩധ"): config[bstack1l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪന")],
    bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬഩ"): config[bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭പ")],
    bstack1l1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨഫ"): bstack11111ll1_opy_,
    bstack1l1l_opy_ (u"ࠬࡪࡥࡵࡧࡦࡸࡪࡪࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩബ"): os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨഭ"), bstack11l1lll1l1_opy_),
    bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩമ"): bstack1l1l111l11_opy_,
    bstack1l1l_opy_ (u"ࠨࡱࡳࡸ࡮ࡳࡡ࡭ࡡ࡫ࡹࡧࡥࡵࡳ࡮ࠪയ"): bstack11ll11ll11_opy_(),
    bstack1l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬര"): {
      bstack1l1l_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨറ"): str(config[bstack1l1l_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫല")]) if bstack1l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬള") in config else bstack1l1l_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴࠢഴ"),
      bstack1l1l_opy_ (u"ࠧ࡭ࡣࡱ࡫ࡺࡧࡧࡦࡘࡨࡶࡸ࡯࡯࡯ࠩവ"): sys.version,
      bstack1l1l_opy_ (u"ࠨࡴࡨࡪࡪࡸࡲࡦࡴࠪശ"): bstack1ll1ll11l_opy_(os.environ.get(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫഷ"), bstack11l1lll1l1_opy_)),
      bstack1l1l_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࠬസ"): bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫഹ"),
      bstack1l1l_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ഺ"): bstack1ll1lll1l1_opy_,
      bstack1l1l_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺ࡟࡮ࡣࡳ഻ࠫ"): bstack1l1ll11l1l_opy_,
      bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡠࡷࡸ࡭ࡩ഼࠭"): os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ഽ")],
      bstack1l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬാ"): os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬി"), bstack11l1lll1l1_opy_),
      bstack1l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧീ"): bstack1l111111ll_opy_(os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧു"), bstack11l1lll1l1_opy_)),
      bstack1l1l_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬൂ"): bstack111llll11_opy_.get(bstack1l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬൃ")),
      bstack1l1l_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧൄ"): bstack111llll11_opy_.get(bstack1l1l_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪ൅")),
      bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭െ"): config[bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧേ")] if config[bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨൈ")] else bstack1l1l_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴࠢ൉"),
      bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩൊ"): str(config[bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪോ")]) if bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫൌ") in config else bstack1l1l_opy_ (u"ࠥࡹࡳࡱ࡮ࡰࡹࡱ്ࠦ"),
      bstack1l1l_opy_ (u"ࠫࡴࡹࠧൎ"): sys.platform,
      bstack1l1l_opy_ (u"ࠬ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠧ൏"): socket.gethostname(),
      bstack1l1l_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨ൐"): bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩ൑"))
    }
  }
  if not bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠨࡵࡧ࡯ࡐ࡯࡬࡭ࡕ࡬࡫ࡳࡧ࡬ࠨ൒")) is None:
    data[bstack1l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬ൓")][bstack1l1l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡒ࡫ࡴࡢࡦࡤࡸࡦ࠭ൔ")] = {
      bstack1l1l_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫൕ"): bstack1l1l_opy_ (u"ࠬࡻࡳࡦࡴࡢ࡯࡮ࡲ࡬ࡦࡦࠪൖ"),
      bstack1l1l_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱ࠭ൗ"): bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠧࡴࡦ࡮ࡏ࡮ࡲ࡬ࡔ࡫ࡪࡲࡦࡲࠧ൘")),
      bstack1l1l_opy_ (u"ࠨࡵ࡬࡫ࡳࡧ࡬ࡏࡷࡰࡦࡪࡸࠧ൙"): bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬ൚"))
    }
  if bstack11111ll1_opy_ == bstack1l1l1l11l_opy_:
    data[bstack1l1l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡳࡶࡴࡶࡥࡳࡶ࡬ࡩࡸ࠭൛")][bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡆࡳࡳ࡬ࡩࡨࠩ൜")] = bstack11ll1l1l1_opy_(config)
    data[bstack1l1l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൝")][bstack1l1l_opy_ (u"࠭ࡩࡴࡒࡨࡶࡨࡿࡁࡶࡶࡲࡉࡳࡧࡢ࡭ࡧࡧࠫ൞")] = percy.bstack11l111l11l_opy_
    data[bstack1l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪൟ")][bstack1l1l_opy_ (u"ࠨࡲࡨࡶࡨࡿࡂࡶ࡫࡯ࡨࡎࡪࠧൠ")] = percy.percy_build_id
  if not bstack111l1111l_opy_.bstack11l11l1l1l_opy_(CONFIG):
    data[bstack1l1l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬൡ")][bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠧൢ")] = bstack111l1111l_opy_.bstack11l11l1l1l_opy_(CONFIG)
  bstack11lllll11_opy_ = bstack11ll11l11l_opy_.bstack1l1ll1l111_opy_(CONFIG, logger)
  bstack1l11l1l1ll_opy_ = bstack111l1111l_opy_.bstack1l1ll1l111_opy_(config=CONFIG)
  if bstack11lllll11_opy_ is not None and bstack1l11l1l1ll_opy_ is not None and bstack1l11l1l1ll_opy_.bstack1lll1ll1l_opy_():
    data[bstack1l1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧൣ")][bstack1l11l1l1ll_opy_.bstack1lll11ll11_opy_()] = bstack11lllll11_opy_.bstack1ll1l11ll1_opy_()
  update(data[bstack1l1l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൤")], bstack11ll1l1l1l_opy_)
  try:
    response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"࠭ࡐࡐࡕࡗࠫ൥"), bstack1l11llll1_opy_(bstack1l1l1l1l_opy_), data, {
      bstack1l1l_opy_ (u"ࠧࡢࡷࡷ࡬ࠬ൦"): (config[bstack1l1l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ൧")], config[bstack1l1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ൨")])
    })
    if response:
      logger.debug(bstack11lllll1l_opy_.format(bstack11111ll1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack11lll1l11l_opy_.format(str(e)))
def bstack1ll1ll11l_opy_(framework):
  return bstack1l1l_opy_ (u"ࠥࡿࢂ࠳ࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢ൩").format(str(framework), __version__) if framework else bstack1l1l_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࡾࢁࠧ൪").format(
    __version__)
def bstack1111111l1_opy_():
  global CONFIG
  global bstack1ll1l11l1l_opy_
  if bool(CONFIG):
    return
  try:
    bstack11l11l1l_opy_()
    logger.debug(bstack1ll11ll111_opy_.format(str(CONFIG)))
    bstack1ll1l11l1l_opy_ = bstack1lllllll1l_opy_.configure_logger(CONFIG, bstack1ll1l11l1l_opy_)
    bstack11111lll1_opy_()
  except Exception as e:
    logger.error(bstack1l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࡺࡶࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࠤ൫") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1l11lll1_opy_
  atexit.register(bstack111ll11ll_opy_)
  signal.signal(signal.SIGINT, bstack1ll11l1l1l_opy_)
  signal.signal(signal.SIGTERM, bstack1ll11l1l1l_opy_)
def bstack1l11lll1_opy_(exctype, value, traceback):
  global bstack1l11l11l_opy_
  try:
    for driver in bstack1l11l11l_opy_:
      bstack11ll11111_opy_(driver, bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭൬"), bstack1l1l_opy_ (u"ࠢࡔࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥ൭") + str(value))
  except Exception:
    pass
  logger.info(bstack1ll11l1l_opy_)
  bstack1l11llll1l_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1l11llll1l_opy_(message=bstack1l1l_opy_ (u"ࠨࠩ൮"), bstack1lll11ll1_opy_ = False):
  global CONFIG
  bstack1ll11ll1_opy_ = bstack1l1l_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡇࡻࡧࡪࡶࡴࡪࡱࡱࠫ൯") if bstack1lll11ll1_opy_ else bstack1l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ൰")
  try:
    if message:
      bstack11ll1l1l1l_opy_ = {
        bstack1ll11ll1_opy_ : str(message)
      }
      bstack11ll1ll111_opy_(bstack1l1l1l11l_opy_, CONFIG, bstack11ll1l1l1l_opy_)
    else:
      bstack11ll1ll111_opy_(bstack1l1l1l11l_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1ll1111111_opy_.format(str(e)))
def bstack1111l111_opy_(bstack1l1ll111_opy_, size):
  bstack111lll1l1_opy_ = []
  while len(bstack1l1ll111_opy_) > size:
    bstack11l1ll111l_opy_ = bstack1l1ll111_opy_[:size]
    bstack111lll1l1_opy_.append(bstack11l1ll111l_opy_)
    bstack1l1ll111_opy_ = bstack1l1ll111_opy_[size:]
  bstack111lll1l1_opy_.append(bstack1l1ll111_opy_)
  return bstack111lll1l1_opy_
def bstack1ll1l111l_opy_(args):
  if bstack1l1l_opy_ (u"ࠫ࠲ࡳࠧ൱") in args and bstack1l1l_opy_ (u"ࠬࡶࡤࡣࠩ൲") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack1l1l1l111_opy_, stage=STAGE.bstack1l1ll1l1ll_opy_)
def run_on_browserstack(bstack1l111l1111_opy_=None, bstack11l11lll11_opy_=None, bstack11l11ll1ll_opy_=False):
  global CONFIG
  global bstack11ll1lll1l_opy_
  global bstack11l11l11l1_opy_
  global bstack11l1lll1l1_opy_
  global bstack1l1ll1l1_opy_
  bstack111lllllll_opy_ = bstack1l1l_opy_ (u"࠭ࠧ൳")
  bstack1ll111111l_opy_(bstack1l1l1ll11_opy_, logger)
  if bstack1l111l1111_opy_ and isinstance(bstack1l111l1111_opy_, str):
    bstack1l111l1111_opy_ = eval(bstack1l111l1111_opy_)
  if bstack1l111l1111_opy_:
    CONFIG = bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠧࡄࡑࡑࡊࡎࡍࠧ൴")]
    bstack11ll1lll1l_opy_ = bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠨࡊࡘࡆࡤ࡛ࡒࡍࠩ൵")]
    bstack11l11l11l1_opy_ = bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠩࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫ൶")]
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬ൷"), bstack11l11l11l1_opy_)
    bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ൸")
  bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧ൹"), uuid4().__str__())
  logger.info(bstack1l1l_opy_ (u"࠭ࡓࡅࡍࠣࡶࡺࡴࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡹ࡬ࡸ࡭ࠦࡩࡥ࠼ࠣࠫൺ") + bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩൻ")));
  logger.debug(bstack1l1l_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࡀࠫർ") + bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫൽ")))
  if not bstack11l11ll1ll_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1l1l11l1l_opy_)
      return
    if sys.argv[1] == bstack1l1l_opy_ (u"ࠪ࠱࠲ࡼࡥࡳࡵ࡬ࡳࡳ࠭ൾ") or sys.argv[1] == bstack1l1l_opy_ (u"ࠫ࠲ࡼࠧൿ"):
      logger.info(bstack1l1l_opy_ (u"ࠬࡈࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡕࡿࡴࡩࡱࡱࠤࡘࡊࡋࠡࡸࡾࢁࠬ඀").format(__version__))
      return
    if sys.argv[1] == bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬඁ"):
      bstack1lll1ll1l1_opy_()
      return
  args = sys.argv
  bstack1111111l1_opy_()
  global bstack111111111_opy_
  global bstack1l1l11ll1_opy_
  global bstack1l1ll11lll_opy_
  global bstack1ll1ll111l_opy_
  global bstack1ll1ll1l11_opy_
  global bstack1lllll1ll1_opy_
  global bstack1l111lll1l_opy_
  global bstack1ll1111l11_opy_
  global bstack1l1l11llll_opy_
  global bstack1l1l1l11l1_opy_
  global bstack11l11111l1_opy_
  bstack1l1l11ll1_opy_ = len(CONFIG.get(bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪං"), []))
  if not bstack111lllllll_opy_:
    if args[1] == bstack1l1l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨඃ") or args[1] == bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯࠵ࠪ඄"):
      bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪඅ")
      args = args[2:]
    elif args[1] == bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪආ"):
      bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫඇ")
      args = args[2:]
    elif args[1] == bstack1l1l_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬඈ"):
      bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ඉ")
      args = args[2:]
    elif args[1] == bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩඊ"):
      bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪඋ")
      args = args[2:]
    elif args[1] == bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪඌ"):
      bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫඍ")
      args = args[2:]
    elif args[1] == bstack1l1l_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬඎ"):
      bstack111lllllll_opy_ = bstack1l1l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ඏ")
      args = args[2:]
    else:
      if not bstack1l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඐ") in CONFIG or str(CONFIG[bstack1l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫඑ")]).lower() in [bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩඒ"), bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫඓ")]:
        bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫඔ")
        args = args[1:]
      elif str(CONFIG[bstack1l1l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨඕ")]).lower() == bstack1l1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬඖ"):
        bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭඗")
        args = args[1:]
      elif str(CONFIG[bstack1l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ඘")]).lower() == bstack1l1l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ඙"):
        bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩක")
        args = args[1:]
      elif str(CONFIG[bstack1l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧඛ")]).lower() == bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬග"):
        bstack111lllllll_opy_ = bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ඝ")
        args = args[1:]
      elif str(CONFIG[bstack1l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඞ")]).lower() == bstack1l1l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨඟ"):
        bstack111lllllll_opy_ = bstack1l1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩච")
        args = args[1:]
      else:
        os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬඡ")] = bstack111lllllll_opy_
        bstack1ll1llll11_opy_(bstack1l1ll1l11l_opy_)
  os.environ[bstack1l1l_opy_ (u"ࠫࡋࡘࡁࡎࡇ࡚ࡓࡗࡑ࡟ࡖࡕࡈࡈࠬජ")] = bstack111lllllll_opy_
  bstack11l1lll1l1_opy_ = bstack111lllllll_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack1ll1111ll_opy_ = bstack11ll111l_opy_[bstack1l1l_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘ࠲ࡈࡄࡅࠩඣ")] if bstack111lllllll_opy_ == bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ඤ") and bstack11ll111l11_opy_() else bstack111lllllll_opy_
      bstack111l111l_opy_.invoke(bstack11l111111_opy_.bstack1llll1ll1l_opy_, bstack1l1lllll1_opy_(
        sdk_version=__version__,
        path_config=bstack11l11l11_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack1ll1111ll_opy_,
        frameworks=[bstack1ll1111ll_opy_],
        framework_versions={
          bstack1ll1111ll_opy_: bstack1l111111ll_opy_(bstack1l1l_opy_ (u"ࠧࡓࡱࡥࡳࡹ࠭ඥ") if bstack111lllllll_opy_ in [bstack1l1l_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧඦ"), bstack1l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨට"), bstack1l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫඨ")] else bstack111lllllll_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࠨඩ"), None):
        CONFIG[bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢඪ")] = cli.config.get(bstack1l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣණ"), None)
    except Exception as e:
      bstack111l111l_opy_.invoke(bstack11l111111_opy_.bstack111ll1ll1_opy_, e.__traceback__, 1)
    if bstack11l11l11l1_opy_:
      CONFIG[bstack1l1l_opy_ (u"ࠢࡢࡲࡳࠦඬ")] = cli.config[bstack1l1l_opy_ (u"ࠣࡣࡳࡴࠧත")]
      logger.info(bstack1l1l1l1111_opy_.format(CONFIG[bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࠭ථ")]))
  else:
    bstack111l111l_opy_.clear()
  global bstack1l1ll11ll1_opy_
  global bstack1111l1l1_opy_
  if bstack1l111l1111_opy_:
    try:
      bstack1ll111l1_opy_ = datetime.datetime.now()
      os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬද")] = bstack111lllllll_opy_
      bstack11ll1ll111_opy_(bstack1l1lll11ll_opy_, CONFIG)
      cli.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼ࡶࡨࡰࡥࡴࡦࡵࡷࡣࡦࡺࡴࡦ࡯ࡳࡸࡪࡪࠢධ"), datetime.datetime.now() - bstack1ll111l1_opy_)
    except Exception as e:
      logger.debug(bstack1l111l111l_opy_.format(str(e)))
  global bstack111ll1l1l_opy_
  global bstack11l1lll111_opy_
  global bstack11ll1l1lll_opy_
  global bstack1llll1111_opy_
  global bstack1lll1ll11l_opy_
  global bstack1l1111l1l1_opy_
  global bstack1l1llll11_opy_
  global bstack1l1l1l1l11_opy_
  global bstack1lll1ll111_opy_
  global bstack11lll11l1l_opy_
  global bstack1l11lll1ll_opy_
  global bstack111llll111_opy_
  global bstack1l11l1l1l1_opy_
  global bstack111lll11l1_opy_
  global bstack11l1lllll1_opy_
  global bstack1ll1l1ll1l_opy_
  global bstack1l111l111_opy_
  global bstack1ll11l11l1_opy_
  global bstack11l111l1l_opy_
  global bstack111lll1ll_opy_
  global bstack11l1lll1ll_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack111ll1l1l_opy_ = webdriver.Remote.__init__
    bstack11l1lll111_opy_ = WebDriver.quit
    bstack111llll111_opy_ = WebDriver.close
    bstack11l1lllll1_opy_ = WebDriver.get
    bstack11l1lll1ll_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1l1ll11ll1_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack11111l1ll_opy_
    bstack1111l1l1_opy_ = bstack11111l1ll_opy_()
  except Exception as e:
    pass
  try:
    global bstack1lll111lll_opy_
    from QWeb.keywords import browser
    bstack1lll111lll_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack1l1l1l1l1_opy_(CONFIG) and bstack111ll1111_opy_():
    if bstack1llllll1l1_opy_() < version.parse(bstack1llll11l_opy_):
      logger.error(bstack11lll1lll_opy_.format(bstack1llllll1l1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack1l1l_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭න")) and callable(getattr(RemoteConnection, bstack1l1l_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ඲"))):
          RemoteConnection._get_proxy_url = bstack1l1l111l1l_opy_
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          ClientConfig.get_proxy_url = bstack1l1l111l1l_opy_
      except Exception as e:
        logger.error(bstack11l11111l_opy_.format(str(e)))
  if not CONFIG.get(bstack1l1l_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩඳ"), False) and not bstack1l111l1111_opy_:
    logger.info(bstack1llll11ll_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬප") in CONFIG and str(CONFIG[bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ඵ")]).lower() != bstack1l1l_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩබ"):
      bstack1l1l111lll_opy_()
    elif bstack111lllllll_opy_ != bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫභ") or (bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬම") and not bstack1l111l1111_opy_):
      bstack111l1l111_opy_()
  if (bstack111lllllll_opy_ in [bstack1l1l_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬඹ"), bstack1l1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ය"), bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩර")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1lll1l11ll_opy_
        bstack1l1111l1l1_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warning(bstack1111ll1l1_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1lll1ll11l_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1ll1l1111l_opy_ + str(e))
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack1111ll1l1_opy_)
    if bstack111lllllll_opy_ != bstack1l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪ඼"):
      bstack1l11ll111_opy_()
    bstack11ll1l1lll_opy_ = Output.start_test
    bstack1llll1111_opy_ = Output.end_test
    bstack1l1llll11_opy_ = TestStatus.__init__
    bstack1lll1ll111_opy_ = pabot._run
    bstack11lll11l1l_opy_ = QueueItem.__init__
    bstack1l11lll1ll_opy_ = pabot._create_command_for_execution
    bstack11l111l1l_opy_ = pabot._report_results
  if bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪල"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack11l1l11ll_opy_)
    bstack1l11l1l1l1_opy_ = Runner.run_hook
    bstack111lll11l1_opy_ = Step.run
  if bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ඾"):
    try:
      from _pytest.config import Config
      bstack1l111l111_opy_ = Config.getoption
      from _pytest import runner
      bstack1ll11l11l1_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warning(bstack1l1l_opy_ (u"ࠧࠫࡳ࠻ࠢࠨࡷࠧ඿"), bstack1l1lll1ll_opy_, str(e))
    try:
      from pytest_bdd import reporting
      bstack111lll1ll_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹࡵࠠࡳࡷࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࡹࠧව"))
    if bstack1111l11l_opy_():
      logger.warning(bstack11l1111l11_opy_[bstack1l1l_opy_ (u"ࠧࡔࡆࡎ࠱ࡌࡋࡎ࠮࠲࠳࠹ࠬශ")])
  try:
    framework_name = bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧෂ") if bstack111lllllll_opy_ in [bstack1l1l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨස"), bstack1l1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩහ"), bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬළ")] else bstack1l11ll11_opy_(bstack111lllllll_opy_)
    bstack1l11l1111l_opy_ = {
      bstack1l1l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪ࠭ෆ"): bstack1l1l_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠳ࡣࡶࡥࡸࡱࡧ࡫ࡲࠨ෇") if bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ෈") and bstack11ll111l11_opy_() else framework_name,
      bstack1l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ෉"): bstack1l111111ll_opy_(framework_name),
      bstack1l1l_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴ්ࠧ"): __version__,
      bstack1l1l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡵࡴࡧࡧࠫ෋"): bstack111lllllll_opy_
    }
    if bstack111lllllll_opy_ in bstack1l1ll1ll1_opy_ + bstack111llllll1_opy_:
      if bstack1lllllll11_opy_.bstack1ll1lll1l_opy_(CONFIG):
        if bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ෌") in CONFIG:
          os.environ[bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭෍")] = os.getenv(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ෎"), json.dumps(CONFIG[bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧා")]))
          CONFIG[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨැ")].pop(bstack1l1l_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧෑ"), None)
          CONFIG[bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪි")].pop(bstack1l1l_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩී"), None)
        bstack1l11l1111l_opy_[bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬු")] = {
          bstack1l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ෕"): bstack1l1l_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩූ"),
          bstack1l1l_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩ෗"): str(bstack1llllll1l1_opy_())
        }
    if bstack111lllllll_opy_ not in [bstack1l1l_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪෘ")] and not cli.is_running():
      bstack11l1l111l1_opy_, bstack1llll111l1_opy_ = bstack11l1llllll_opy_.launch(CONFIG, bstack1l11l1111l_opy_)
      if bstack1llll111l1_opy_.get(bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪෙ")) is not None and bstack1lllllll11_opy_.bstack1l11llll_opy_(CONFIG) is None:
        value = bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫේ")].get(bstack1l1l_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ෛ"))
        if value is not None:
            CONFIG[bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ො")] = value
        else:
          logger.debug(bstack1l1l_opy_ (u"ࠢࡏࡱࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡨࡦࡺࡡࠡࡨࡲࡹࡳࡪࠠࡪࡰࠣࡶࡪࡹࡰࡰࡰࡶࡩࠧෝ"))
  except Exception as e:
    logger.debug(bstack1l11l11ll_opy_.format(bstack1l1l_opy_ (u"ࠨࡖࡨࡷࡹࡎࡵࡣࠩෞ"), str(e)))
  if bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩෟ"):
    bstack1l1ll11lll_opy_ = True
    if bstack1l111l1111_opy_ and bstack11l11ll1ll_opy_:
      bstack1lllll1ll1_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ෠"), {}).get(bstack1l1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭෡"))
      bstack1ll11111l_opy_(bstack11ll1ll1_opy_)
    elif bstack1l111l1111_opy_:
      bstack1lllll1ll1_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ෢"), {}).get(bstack1l1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ෣"))
      global bstack1l11l11l_opy_
      try:
        if bstack1ll1l111l_opy_(bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ෤")]) and multiprocessing.current_process().name == bstack1l1l_opy_ (u"ࠨ࠲ࠪ෥"):
          bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෦")].remove(bstack1l1l_opy_ (u"ࠪ࠱ࡲ࠭෧"))
          bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෨")].remove(bstack1l1l_opy_ (u"ࠬࡶࡤࡣࠩ෩"))
          bstack1l111l1111_opy_[bstack1l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෪")] = bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ෫")][0]
          with open(bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ෬")], bstack1l1l_opy_ (u"ࠩࡵࠫ෭")) as f:
            bstack11l1l1ll1l_opy_ = f.read()
          bstack1llllll11_opy_ = bstack1l1l_opy_ (u"ࠥࠦࠧ࡬ࡲࡰ࡯ࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡨࡰࠦࡩ࡮ࡲࡲࡶࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡦ࠽ࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡ࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡾࡪ࠮ࡻࡾࠫ࠾ࠤ࡫ࡸ࡯࡮ࠢࡳࡨࡧࠦࡩ࡮ࡲࡲࡶࡹࠦࡐࡥࡤ࠾ࠤࡴ࡭࡟ࡥࡤࠣࡁࠥࡖࡤࡣ࠰ࡧࡳࡤࡨࡲࡦࡣ࡮࠿ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡦࡨࡪࠥࡳ࡯ࡥࡡࡥࡶࡪࡧ࡫ࠩࡵࡨࡰ࡫࠲ࠠࡢࡴࡪ࠰ࠥࡺࡥ࡮ࡲࡲࡶࡦࡸࡹࠡ࠿ࠣ࠴࠮ࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡺࡲࡺ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡥࡷ࡭ࠠ࠾ࠢࡶࡸࡷ࠮ࡩ࡯ࡶࠫࡥࡷ࡭ࠩࠬ࠳࠳࠭ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡩࡽࡩࡥࡱࡶࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡡࡴࠢࡨ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡶࡡࡴࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡱࡪࡣࡩࡨࠨࡴࡧ࡯ࡪ࠱ࡧࡲࡨ࠮ࡷࡩࡲࡶ࡯ࡳࡣࡵࡽ࠮ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡓࡨࡧ࠴ࡤࡰࡡࡥࠤࡂࠦ࡭ࡰࡦࡢࡦࡷ࡫ࡡ࡬ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡖࡤࡣ࠰ࡧࡳࡤࡨࡲࡦࡣ࡮ࠤࡂࠦ࡭ࡰࡦࡢࡦࡷ࡫ࡡ࡬ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡖࡤࡣࠪࠬ࠲ࡸ࡫ࡴࡠࡶࡵࡥࡨ࡫ࠨࠪ࡞ࡱࠦࠧࠨ෮").format(str(bstack1l111l1111_opy_))
          bstack1lll1l1l1_opy_ = bstack1llllll11_opy_ + bstack11l1l1ll1l_opy_
          bstack1ll1l1llll_opy_ = bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෯")] + bstack1l1l_opy_ (u"ࠬࡥࡢࡴࡶࡤࡧࡰࡥࡴࡦ࡯ࡳ࠲ࡵࡿࠧ෰")
          with open(bstack1ll1l1llll_opy_, bstack1l1l_opy_ (u"࠭ࡷࠨ෱")):
            pass
          with open(bstack1ll1l1llll_opy_, bstack1l1l_opy_ (u"ࠢࡸ࠭ࠥෲ")) as f:
            f.write(bstack1lll1l1l1_opy_)
          import subprocess
          bstack11lllllll_opy_ = subprocess.run([bstack1l1l_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࠣෳ"), bstack1ll1l1llll_opy_])
          if os.path.exists(bstack1ll1l1llll_opy_):
            os.unlink(bstack1ll1l1llll_opy_)
          os._exit(bstack11lllllll_opy_.returncode)
        else:
          if bstack1ll1l111l_opy_(bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෴")]):
            bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෵")].remove(bstack1l1l_opy_ (u"ࠫ࠲ࡳࠧ෶"))
            bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෷")].remove(bstack1l1l_opy_ (u"࠭ࡰࡥࡤࠪ෸"))
            bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ෹")] = bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ෺")][0]
          bstack1ll11111l_opy_(bstack11ll1ll1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෻")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack1l1l_opy_ (u"ࠪࡣࡤࡴࡡ࡮ࡧࡢࡣࠬ෼")] = bstack1l1l_opy_ (u"ࠫࡤࡥ࡭ࡢ࡫ࡱࡣࡤ࠭෽")
          mod_globals[bstack1l1l_opy_ (u"ࠬࡥ࡟ࡧ࡫࡯ࡩࡤࡥࠧ෾")] = os.path.abspath(bstack1l111l1111_opy_[bstack1l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෿")])
          exec(open(bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ฀")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack1l1l_opy_ (u"ࠨࡅࡤࡹ࡬࡮ࡴࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥࢁࡽࠨก").format(str(e)))
          for driver in bstack1l11l11l_opy_:
            bstack11l11lll11_opy_.append({
              bstack1l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧข"): bstack1l111l1111_opy_[bstack1l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฃ")],
              bstack1l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪค"): str(e),
              bstack1l1l_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫฅ"): multiprocessing.current_process().name
            })
            bstack11ll11111_opy_(driver, bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ฆ"), bstack1l1l_opy_ (u"ࠢࡔࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥง") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1l11l11l_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack11l11l11l1_opy_, CONFIG, logger)
      bstack1ll111l11l_opy_()
      bstack1lll11l1_opy_()
      percy.bstack1ll11111l1_opy_()
      bstack11lllll1l1_opy_ = {
        bstack1l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫจ"): args[0],
        bstack1l1l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩฉ"): CONFIG,
        bstack1l1l_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫช"): bstack11ll1lll1l_opy_,
        bstack1l1l_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ซ"): bstack11l11l11l1_opy_
      }
      if bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨฌ") in CONFIG:
        bstack11l11lll1_opy_ = bstack11l111111l_opy_(args, logger, CONFIG, bstack1l1lll11l1_opy_, bstack1l1l11ll1_opy_)
        bstack1ll1111l11_opy_ = bstack11l11lll1_opy_.bstack1lll11l11l_opy_(run_on_browserstack, bstack11lllll1l1_opy_, bstack1ll1l111l_opy_(args))
      else:
        if bstack1ll1l111l_opy_(args):
          bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩญ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack11lllll1l1_opy_,))
          test.start()
          test.join()
        else:
          bstack1ll11111l_opy_(bstack11ll1ll1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack1l1l_opy_ (u"ࠧࡠࡡࡱࡥࡲ࡫࡟ࡠࠩฎ")] = bstack1l1l_opy_ (u"ࠨࡡࡢࡱࡦ࡯࡮ࡠࡡࠪฏ")
          mod_globals[bstack1l1l_opy_ (u"ࠩࡢࡣ࡫࡯࡬ࡦࡡࡢࠫฐ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩฑ") or bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪฒ"):
    percy.init(bstack11l11l11l1_opy_, CONFIG, logger)
    percy.bstack1ll11111l1_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack1111ll1l1_opy_)
    bstack1ll111l11l_opy_()
    bstack1ll11111l_opy_(bstack1l11l11l1l_opy_)
    if bstack1l1lll11l1_opy_:
      bstack1ll1l1ll1_opy_(bstack1l11l11l1l_opy_, args)
      if bstack1l1l_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪณ") in args:
        i = args.index(bstack1l1l_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫด"))
        args.pop(i)
        args.pop(i)
      if bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪต") not in CONFIG:
        CONFIG[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫถ")] = [{}]
        bstack1l1l11ll1_opy_ = 1
      if bstack111111111_opy_ == 0:
        bstack111111111_opy_ = 1
      args.insert(0, str(bstack111111111_opy_))
      args.insert(0, str(bstack1l1l_opy_ (u"ࠩ࠰࠱ࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧท")))
    if bstack11l1llllll_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack111llll1l_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack1l1lll1l11_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack1l1l_opy_ (u"ࠥࡖࡔࡈࡏࡕࡡࡒࡔ࡙ࡏࡏࡏࡕࠥธ"),
        ).parse_args(bstack111llll1l_opy_)
        bstack11111l1l_opy_ = args.index(bstack111llll1l_opy_[0]) if len(bstack111llll1l_opy_) > 0 else len(args)
        args.insert(bstack11111l1l_opy_, str(bstack1l1l_opy_ (u"ࠫ࠲࠳࡬ࡪࡵࡷࡩࡳ࡫ࡲࠨน")))
        args.insert(bstack11111l1l_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡸ࡯ࡣࡱࡷࡣࡱ࡯ࡳࡵࡧࡱࡩࡷ࠴ࡰࡺࠩบ"))))
        if bstack111l1111l_opy_.bstack111l11l1_opy_(CONFIG):
          args.insert(bstack11111l1l_opy_, str(bstack1l1l_opy_ (u"࠭࠭࠮࡮࡬ࡷࡹ࡫࡮ࡦࡴࠪป")))
          args.insert(bstack11111l1l_opy_ + 1, str(bstack1l1l_opy_ (u"ࠧࡓࡧࡷࡶࡾࡌࡡࡪ࡮ࡨࡨ࠿ࢁࡽࠨผ").format(bstack111l1111l_opy_.bstack1ll111l1l1_opy_(CONFIG))))
        if bstack1l1l1111l1_opy_(os.environ.get(bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓ࠭ฝ"))) and str(os.environ.get(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔ࡟ࡕࡇࡖࡘࡘ࠭พ"), bstack1l1l_opy_ (u"ࠪࡲࡺࡲ࡬ࠨฟ"))) != bstack1l1l_opy_ (u"ࠫࡳࡻ࡬࡭ࠩภ"):
          for bstack11lll1ll1l_opy_ in bstack1l1lll1l11_opy_:
            args.remove(bstack11lll1ll1l_opy_)
          test_files = os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࡢࡘࡊ࡙ࡔࡔࠩม")).split(bstack1l1l_opy_ (u"࠭ࠬࠨย"))
          for bstack11111ll1l_opy_ in test_files:
            args.append(bstack11111ll1l_opy_)
      except Exception as e:
        logger.error(bstack1l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡧࡴࡵࡣࡦ࡬࡮ࡴࡧࠡ࡮࡬ࡷࡹ࡫࡮ࡦࡴࠣࡪࡴࡸࠠࡼࡿ࠱ࠤࡊࡸࡲࡰࡴࠣ࠱ࠥࢁࡽࠣร").format(bstack11ll1111ll_opy_, e))
    pabot.main(args)
  elif bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩฤ"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack1111ll1l1_opy_)
    for a in args:
      if bstack1l1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡒࡏࡅ࡙ࡌࡏࡓࡏࡌࡒࡉࡋࡘࠨล") in a:
        bstack1ll1ll1l11_opy_ = int(a.split(bstack1l1l_opy_ (u"ࠪ࠾ࠬฦ"))[1])
      if bstack1l1l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡈࡊࡌࡌࡐࡅࡄࡐࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨว") in a:
        bstack1lllll1ll1_opy_ = str(a.split(bstack1l1l_opy_ (u"ࠬࡀࠧศ"))[1])
      if bstack1l1l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡉࡌࡊࡃࡕࡋࡘ࠭ษ") in a:
        bstack1l111lll1l_opy_ = str(a.split(bstack1l1l_opy_ (u"ࠧ࠻ࠩส"))[1])
    bstack1ll11ll11_opy_ = None
    bstack1l111ll1l_opy_ = None
    if bstack1l1l_opy_ (u"ࠨ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢ࡭ࡹ࡫࡭ࡠ࡫ࡱࡨࡪࡾࠧห") in args:
      i = args.index(bstack1l1l_opy_ (u"ࠩ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣ࡮ࡺࡥ࡮ࡡ࡬ࡲࡩ࡫ࡸࠨฬ"))
      args.pop(i)
      bstack1ll11ll11_opy_ = args.pop(i)
    if bstack1l1l_opy_ (u"ࠪ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽ࠭อ") in args:
      i = args.index(bstack1l1l_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾࠧฮ"))
      args.pop(i)
      bstack1l111ll1l_opy_ = args.pop(i)
    if bstack1ll11ll11_opy_ is not None:
      global bstack1111l1ll_opy_
      bstack1111l1ll_opy_ = bstack1ll11ll11_opy_
    if bstack1l111ll1l_opy_ is not None and int(bstack1ll1ll1l11_opy_) < 0:
      bstack1ll1ll1l11_opy_ = int(bstack1l111ll1l_opy_)
    bstack1ll11111l_opy_(bstack1l11l11l1l_opy_)
    run_cli(args)
    if bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵࠩฯ") in multiprocessing.current_process().__dict__.keys():
      for bstack11ll11111l_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack11l11lll11_opy_.append(bstack11ll11111l_opy_)
  elif bstack111lllllll_opy_ == bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ะ"):
    bstack11l1lll11_opy_ = bstack1l11111l1_opy_(args, logger, CONFIG, bstack1l1lll11l1_opy_)
    bstack11l1lll11_opy_.bstack111l111l1_opy_()
    bstack1ll111l11l_opy_()
    bstack1ll1ll111l_opy_ = True
    bstack1l1l1l11l1_opy_ = bstack11l1lll11_opy_.bstack111lll1l_opy_()
    bstack11l1lll11_opy_.bstack11lllll1l1_opy_(bstack1l1lllll_opy_)
    bstack11l1lll11_opy_.bstack1111llll1_opy_()
    bstack1l11l111_opy_(bstack111lllllll_opy_, CONFIG, bstack11l1lll11_opy_.bstack11l11llll1_opy_())
    bstack1lll1l111l_opy_ = bstack11l1lll11_opy_.bstack1lll11l11l_opy_(bstack11lll1ll1_opy_, {
      bstack1l1l_opy_ (u"ࠧࡉࡗࡅࡣ࡚ࡘࡌࠨั"): bstack11ll1lll1l_opy_,
      bstack1l1l_opy_ (u"ࠨࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪา"): bstack11l11l11l1_opy_,
      bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠬำ"): bstack1l1lll11l1_opy_
    })
    try:
      bstack11llllll11_opy_, bstack1l1l1l11ll_opy_ = map(list, zip(*bstack1lll1l111l_opy_))
      bstack1l1l11llll_opy_ = bstack11llllll11_opy_[0]
      for status_code in bstack1l1l1l11ll_opy_:
        if status_code != 0:
          bstack11l11111l1_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack1l1l_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡢࡸࡨࠤࡪࡸࡲࡰࡴࡶࠤࡦࡴࡤࠡࡵࡷࡥࡹࡻࡳࠡࡥࡲࡨࡪ࠴ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࠾ࠥࢁࡽࠣิ").format(str(e)))
  elif bstack111lllllll_opy_ == bstack1l1l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫี"):
    try:
      from behave.__main__ import main as bstack1111lll1_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1l1111ll_opy_(e, bstack11l1l11ll_opy_)
    bstack1ll111l11l_opy_()
    bstack1ll1ll111l_opy_ = True
    bstack1l1l111111_opy_ = 1
    if bstack1l1l_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬึ") in CONFIG:
      bstack1l1l111111_opy_ = CONFIG[bstack1l1l_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ื")]
    if bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵุࠪ") in CONFIG:
      bstack11l111lll1_opy_ = int(bstack1l1l111111_opy_) * int(len(CONFIG[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶูࠫ")]))
    else:
      bstack11l111lll1_opy_ = int(bstack1l1l111111_opy_)
    config = Configuration(args)
    bstack1l1lllllll_opy_ = config.paths
    if len(bstack1l1lllllll_opy_) == 0:
      import glob
      pattern = bstack1l1l_opy_ (u"ࠩ࠭࠮࠴࠰࠮ࡧࡧࡤࡸࡺࡸࡥࠨฺ")
      bstack11ll111111_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack11ll111111_opy_)
      config = Configuration(args)
      bstack1l1lllllll_opy_ = config.paths
    bstack11ll111ll_opy_ = [os.path.normpath(item) for item in bstack1l1lllllll_opy_]
    bstack1l111ll1_opy_ = [os.path.normpath(item) for item in args]
    bstack11l1ll1ll1_opy_ = [item for item in bstack1l111ll1_opy_ if item not in bstack11ll111ll_opy_]
    import platform as pf
    if pf.system().lower() == bstack1l1l_opy_ (u"ࠪࡻ࡮ࡴࡤࡰࡹࡶࠫ฻"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack11ll111ll_opy_ = [str(PurePosixPath(PureWindowsPath(bstack111l11111_opy_)))
                    for bstack111l11111_opy_ in bstack11ll111ll_opy_]
    bstack1l1ll1111_opy_ = []
    for spec in bstack11ll111ll_opy_:
      bstack11l111ll1l_opy_ = []
      bstack11l111ll1l_opy_ += bstack11l1ll1ll1_opy_
      bstack11l111ll1l_opy_.append(spec)
      bstack1l1ll1111_opy_.append(bstack11l111ll1l_opy_)
    execution_items = []
    for bstack11l111ll1l_opy_ in bstack1l1ll1111_opy_:
      if bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ฼") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ฽")]):
          item = {}
          item[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࠪ฾")] = bstack1l1l_opy_ (u"ࠧࠡࠩ฿").join(bstack11l111ll1l_opy_)
          item[bstack1l1l_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧเ")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack1l1l_opy_ (u"ࠩࡤࡶ࡬࠭แ")] = bstack1l1l_opy_ (u"ࠪࠤࠬโ").join(bstack11l111ll1l_opy_)
        item[bstack1l1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪใ")] = 0
        execution_items.append(item)
    bstack1l11ll1111_opy_ = bstack1111l111_opy_(execution_items, bstack11l111lll1_opy_)
    for execution_item in bstack1l11ll1111_opy_:
      bstack11ll11llll_opy_ = []
      for item in execution_item:
        bstack11ll11llll_opy_.append(bstack11l1l11ll1_opy_(name=str(item[bstack1l1l_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫไ")]),
                                             target=bstack11l11ll1l1_opy_,
                                             args=(item[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࠪๅ")],)))
      for t in bstack11ll11llll_opy_:
        t.start()
      for t in bstack11ll11llll_opy_:
        t.join()
  else:
    bstack1ll1llll11_opy_(bstack1l1ll1l11l_opy_)
  if not bstack1l111l1111_opy_:
    bstack1llll11l11_opy_()
    if(bstack111lllllll_opy_ in [bstack1l1l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧๆ"), bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ็")]):
      bstack1l1l1lll_opy_()
  bstack1lllllll1l_opy_.bstack1lllll11l1_opy_()
def browserstack_initialize(bstack1llll1l1_opy_=None):
  logger.info(bstack1l1l_opy_ (u"ࠩࡕࡹࡳࡴࡩ࡯ࡩࠣࡗࡉࡑࠠࡸ࡫ࡷ࡬ࠥࡧࡲࡨࡵ࠽ࠤ่ࠬ") + str(bstack1llll1l1_opy_))
  run_on_browserstack(bstack1llll1l1_opy_, None, True)
@measure(event_name=EVENTS.bstack1ll1l1l1l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1llll11l11_opy_():
  global CONFIG
  global bstack11l1lll1l1_opy_
  global bstack11l11111l1_opy_
  global bstack1lll111l_opy_
  global bstack1l1ll1l1_opy_
  bstack1l1111llll_opy_.bstack1lll1ll11_opy_()
  if cli.is_running():
    bstack111l111l_opy_.invoke(bstack11l111111_opy_.bstack1llll11l1l_opy_)
  else:
    bstack1l11l1l1ll_opy_ = bstack111l1111l_opy_.bstack1l1ll1l111_opy_(config=CONFIG)
    bstack1l11l1l1ll_opy_.bstack11l1l1l1ll_opy_(CONFIG)
  if bstack11l1lll1l1_opy_ == bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ้ࠪ"):
    if not cli.is_enabled(CONFIG):
      bstack11l1llllll_opy_.stop()
  else:
    bstack11l1llllll_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack1l1ll11111_opy_.bstack11l111llll_opy_()
  if bstack1l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ๊") in CONFIG and str(CONFIG[bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦ๋ࠩ")]).lower() != bstack1l1l_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬ์"):
    hashed_id, bstack11111111_opy_ = bstack11l1111111_opy_()
  else:
    hashed_id, bstack11111111_opy_ = get_build_link()
  bstack1l1l1l111l_opy_(hashed_id)
  logger.info(bstack1l1l_opy_ (u"ࠧࡔࡆࡎࠤࡷࡻ࡮ࠡࡧࡱࡨࡪࡪࠠࡧࡱࡵࠤ࡮ࡪ࠺ࠨํ") + bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠪ๎"), bstack1l1l_opy_ (u"ࠩࠪ๏")) + bstack1l1l_opy_ (u"ࠪ࠰ࠥࡺࡥࡴࡶ࡫ࡹࡧࠦࡩࡥ࠼ࠣࠫ๐") + os.getenv(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ๑"), bstack1l1l_opy_ (u"ࠬ࠭๒")))
  if hashed_id is not None and bstack1111l1lll_opy_() != -1:
    sessions = bstack1ll111l111_opy_(hashed_id)
    bstack1ll1111l_opy_(sessions, bstack11111111_opy_)
  if bstack11l1lll1l1_opy_ == bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭๓") and bstack11l11111l1_opy_ != 0:
    sys.exit(bstack11l11111l1_opy_)
  if bstack11l1lll1l1_opy_ == bstack1l1l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ๔") and bstack1lll111l_opy_ != 0:
    sys.exit(bstack1lll111l_opy_)
def bstack1l1l1l111l_opy_(new_id):
    global bstack1l1l111l11_opy_
    bstack1l1l111l11_opy_ = new_id
def bstack1l11ll11_opy_(bstack11lll1l1ll_opy_):
  if bstack11lll1l1ll_opy_:
    return bstack11lll1l1ll_opy_.capitalize()
  else:
    return bstack1l1l_opy_ (u"ࠨࠩ๕")
@measure(event_name=EVENTS.bstack1ll1l111ll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11lllll1_opy_(bstack1l11ll1l_opy_):
  if bstack1l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ๖") in bstack1l11ll1l_opy_ and bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ๗")] != bstack1l1l_opy_ (u"ࠫࠬ๘"):
    return bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ๙")]
  else:
    bstack1l1l1l11_opy_ = bstack1l1l_opy_ (u"ࠨࠢ๚")
    if bstack1l1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ๛") in bstack1l11ll1l_opy_ and bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ๜")] != None:
      bstack1l1l1l11_opy_ += bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩ๝")] + bstack1l1l_opy_ (u"ࠥ࠰ࠥࠨ๞")
      if bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠫࡴࡹࠧ๟")] == bstack1l1l_opy_ (u"ࠧ࡯࡯ࡴࠤ๠"):
        bstack1l1l1l11_opy_ += bstack1l1l_opy_ (u"ࠨࡩࡐࡕࠣࠦ๡")
      bstack1l1l1l11_opy_ += (bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫ๢")] or bstack1l1l_opy_ (u"ࠨࠩ๣"))
      return bstack1l1l1l11_opy_
    else:
      bstack1l1l1l11_opy_ += bstack1l11ll11_opy_(bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪ๤")]) + bstack1l1l_opy_ (u"ࠥࠤࠧ๥") + (
              bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭๦")] or bstack1l1l_opy_ (u"ࠬ࠭๧")) + bstack1l1l_opy_ (u"ࠨࠬࠡࠤ๨")
      if bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠧࡰࡵࠪ๩")] == bstack1l1l_opy_ (u"࡙ࠣ࡬ࡲࡩࡵࡷࡴࠤ๪"):
        bstack1l1l1l11_opy_ += bstack1l1l_opy_ (u"ࠤ࡚࡭ࡳࠦࠢ๫")
      bstack1l1l1l11_opy_ += bstack1l11ll1l_opy_[bstack1l1l_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ๬")] or bstack1l1l_opy_ (u"ࠫࠬ๭")
      return bstack1l1l1l11_opy_
@measure(event_name=EVENTS.bstack1l11l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11lll11l11_opy_(bstack11l11111ll_opy_):
  if bstack11l11111ll_opy_ == bstack1l1l_opy_ (u"ࠧࡪ࡯࡯ࡧࠥ๮"):
    return bstack1l1l_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡩࡵࡩࡪࡴ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡩࡵࡩࡪࡴࠢ࠿ࡅࡲࡱࡵࡲࡥࡵࡧࡧࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩ๯")
  elif bstack11l11111ll_opy_ == bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ๰"):
    return bstack1l1l_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡶࡪࡪ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡴࡨࡨࠧࡄࡆࡢ࡫࡯ࡩࡩࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫ๱")
  elif bstack11l11111ll_opy_ == bstack1l1l_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ๲"):
    return bstack1l1l_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿࡭ࡲࡦࡧࡱ࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧ࡭ࡲࡦࡧࡱࠦࡃࡖࡡࡴࡵࡨࡨࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪ๳")
  elif bstack11l11111ll_opy_ == bstack1l1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥ๴"):
    return bstack1l1l_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡳࡧࡧ࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧࡸࡥࡥࠤࡁࡉࡷࡸ࡯ࡳ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧ๵")
  elif bstack11l11111ll_opy_ == bstack1l1l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ๶"):
    return bstack1l1l_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࠦࡩࡪࡧ࠳࠳࠸࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࠨ࡫ࡥࡢ࠵࠵࠺ࠧࡄࡔࡪ࡯ࡨࡳࡺࡺ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ๷")
  elif bstack11l11111ll_opy_ == bstack1l1l_opy_ (u"ࠣࡴࡸࡲࡳ࡯࡮ࡨࠤ๸"):
    return bstack1l1l_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࡧࡲࡡࡤ࡭࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡧࡲࡡࡤ࡭ࠥࡂࡗࡻ࡮࡯࡫ࡱ࡫ࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪ๹")
  else:
    return bstack1l1l_opy_ (u"ࠪࡀࡹࡪࠠࡢ࡮࡬࡫ࡳࡃࠢࡤࡧࡱࡸࡪࡸࠢࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡢ࡭ࡣࡦ࡯ࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡢ࡭ࡣࡦ࡯ࠧࡄࠧ๺") + bstack1l11ll11_opy_(
      bstack11l11111ll_opy_) + bstack1l1l_opy_ (u"ࠫࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪ๻")
def bstack1111l111l_opy_(session):
  return bstack1l1l_opy_ (u"ࠬࡂࡴࡳࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡵࡳࡼࠨ࠾࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠢࡶࡩࡸࡹࡩࡰࡰ࠰ࡲࡦࡳࡥࠣࡀ࠿ࡥࠥ࡮ࡲࡦࡨࡀࠦࢀࢃࠢࠡࡶࡤࡶ࡬࡫ࡴ࠾ࠤࡢࡦࡱࡧ࡮࡬ࠤࡁࡿࢂࡂ࠯ࡢࡀ࠿࠳ࡹࡪ࠾ࡼࡿࡾࢁࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿ࡸࡩࠦࡡ࡭࡫ࡪࡲࡂࠨࡣࡦࡰࡷࡩࡷࠨࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࡄࡻࡾ࠾࠲ࡸࡩࡄ࠼࠰ࡶࡵࡂࠬ๼").format(
    session[bstack1l1l_opy_ (u"࠭ࡰࡶࡤ࡯࡭ࡨࡥࡵࡳ࡮ࠪ๽")], bstack11lllll1_opy_(session), bstack11lll11l11_opy_(session[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡳࡵࡣࡷࡹࡸ࠭๾")]),
    bstack11lll11l11_opy_(session[bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ๿")]),
    bstack1l11ll11_opy_(session[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪ຀")] or session[bstack1l1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪກ")] or bstack1l1l_opy_ (u"ࠫࠬຂ")) + bstack1l1l_opy_ (u"ࠧࠦࠢ຃") + (session[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨຄ")] or bstack1l1l_opy_ (u"ࠧࠨ຅")),
    session[bstack1l1l_opy_ (u"ࠨࡱࡶࠫຆ")] + bstack1l1l_opy_ (u"ࠤࠣࠦງ") + session[bstack1l1l_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧຈ")], session[bstack1l1l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭ຉ")] or bstack1l1l_opy_ (u"ࠬ࠭ຊ"),
    session[bstack1l1l_opy_ (u"࠭ࡣࡳࡧࡤࡸࡪࡪ࡟ࡢࡶࠪ຋")] if session[bstack1l1l_opy_ (u"ࠧࡤࡴࡨࡥࡹ࡫ࡤࡠࡣࡷࠫຌ")] else bstack1l1l_opy_ (u"ࠨࠩຍ"))
@measure(event_name=EVENTS.bstack11l1llll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1ll1111l_opy_(sessions, bstack11111111_opy_):
  try:
    bstack1l11111l1l_opy_ = bstack1l1l_opy_ (u"ࠤࠥຎ")
    if not os.path.exists(bstack11llll1l_opy_):
      os.mkdir(bstack11llll1l_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l_opy_ (u"ࠪࡥࡸࡹࡥࡵࡵ࠲ࡶࡪࡶ࡯ࡳࡶ࠱࡬ࡹࡳ࡬ࠨຏ")), bstack1l1l_opy_ (u"ࠫࡷ࠭ຐ")) as f:
      bstack1l11111l1l_opy_ = f.read()
    bstack1l11111l1l_opy_ = bstack1l11111l1l_opy_.replace(bstack1l1l_opy_ (u"ࠬࢁࠥࡓࡇࡖ࡙ࡑ࡚ࡓࡠࡅࡒ࡙ࡓ࡚ࠥࡾࠩຑ"), str(len(sessions)))
    bstack1l11111l1l_opy_ = bstack1l11111l1l_opy_.replace(bstack1l1l_opy_ (u"࠭ࡻࠦࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠩࢂ࠭ຒ"), bstack11111111_opy_)
    bstack1l11111l1l_opy_ = bstack1l11111l1l_opy_.replace(bstack1l1l_opy_ (u"ࠧࡼࠧࡅ࡙ࡎࡒࡄࡠࡐࡄࡑࡊࠫࡽࠨຓ"),
                                              sessions[0].get(bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟࡯ࡣࡰࡩࠬດ")) if sessions[0] else bstack1l1l_opy_ (u"ࠩࠪຕ"))
    with open(os.path.join(bstack11llll1l_opy_, bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠯ࡵࡩࡵࡵࡲࡵ࠰࡫ࡸࡲࡲࠧຖ")), bstack1l1l_opy_ (u"ࠫࡼ࠭ທ")) as stream:
      stream.write(bstack1l11111l1l_opy_.split(bstack1l1l_opy_ (u"ࠬࢁࠥࡔࡇࡖࡗࡎࡕࡎࡔࡡࡇࡅ࡙ࡇࠥࡾࠩຘ"))[0])
      for session in sessions:
        stream.write(bstack1111l111l_opy_(session))
      stream.write(bstack1l11111l1l_opy_.split(bstack1l1l_opy_ (u"࠭ࡻࠦࡕࡈࡗࡘࡏࡏࡏࡕࡢࡈࡆ࡚ࡁࠦࡿࠪນ"))[1])
    logger.info(bstack1l1l_opy_ (u"ࠧࡈࡧࡱࡩࡷࡧࡴࡦࡦࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡥࡹ࡮ࡲࡤࠡࡣࡵࡸ࡮࡬ࡡࡤࡶࡶࠤࡦࡺࠠࡼࡿࠪບ").format(bstack11llll1l_opy_));
  except Exception as e:
    logger.debug(bstack1l111ll11l_opy_.format(str(e)))
def bstack1ll111l111_opy_(hashed_id):
  global CONFIG
  try:
    bstack1ll111l1_opy_ = datetime.datetime.now()
    host = bstack1l1l_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠳ࡣ࡭ࡱࡸࡨ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨປ") if bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࠭ຜ") in CONFIG else bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡶࡩ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫຝ")
    user = CONFIG[bstack1l1l_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ພ")]
    key = CONFIG[bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨຟ")]
    bstack1ll111ll1_opy_ = bstack1l1l_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩࠬຠ") if bstack1l1l_opy_ (u"ࠧࡢࡲࡳࠫມ") in CONFIG else (bstack1l1l_opy_ (u"ࠨࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩࠬຢ") if CONFIG.get(bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭ຣ")) else bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ຤"))
    host = bstack1ll1lll111_opy_(cli.config, [bstack1l1l_opy_ (u"ࠦࡦࡶࡩࡴࠤລ"), bstack1l1l_opy_ (u"ࠧࡧࡰࡱࡃࡸࡸࡴࡳࡡࡵࡧࠥ຦"), bstack1l1l_opy_ (u"ࠨࡡࡱ࡫ࠥວ")], host) if bstack1l1l_opy_ (u"ࠧࡢࡲࡳࠫຨ") in CONFIG else bstack1ll1lll111_opy_(cli.config, [bstack1l1l_opy_ (u"ࠣࡣࡳ࡭ࡸࠨຩ"), bstack1l1l_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶࡨࠦສ"), bstack1l1l_opy_ (u"ࠥࡥࡵ࡯ࠢຫ")], host)
    url = bstack1l1l_opy_ (u"ࠫࢀࢃ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂ࠵ࡳࡦࡵࡶ࡭ࡴࡴࡳ࠯࡬ࡶࡳࡳ࠭ຬ").format(host, bstack1ll111ll1_opy_, hashed_id)
    headers = {
      bstack1l1l_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫອ"): bstack1l1l_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩຮ"),
    }
    proxies = bstack1l11l1ll1l_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies, auth=(user, key))
    if response.json():
      cli.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴ࠿࡭ࡥࡵࡡࡶࡩࡸࡹࡩࡰࡰࡶࡣࡱ࡯ࡳࡵࠤຯ"), datetime.datetime.now() - bstack1ll111l1_opy_)
      return list(map(lambda session: session[bstack1l1l_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ະ")], response.json()))
  except Exception as e:
    logger.debug(bstack1llll1ll1_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack11lll11l1_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def get_build_link():
  global CONFIG
  global bstack1l1l111l11_opy_
  try:
    if bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬັ") in CONFIG:
      bstack1ll111l1_opy_ = datetime.datetime.now()
      host = bstack1l1l_opy_ (u"ࠪࡥࡵ࡯࠭ࡤ࡮ࡲࡹࡩ࠭າ") if bstack1l1l_opy_ (u"ࠫࡦࡶࡰࠨຳ") in CONFIG else bstack1l1l_opy_ (u"ࠬࡧࡰࡪࠩິ")
      user = CONFIG[bstack1l1l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨີ")]
      key = CONFIG[bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪຶ")]
      bstack1ll111ll1_opy_ = bstack1l1l_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧື") if bstack1l1l_opy_ (u"ࠩࡤࡴࡵຸ࠭") in CONFIG else bstack1l1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩູࠬ")
      url = bstack1l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࢁࡽ࠻ࡽࢀࡄࢀࢃ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠴ࡪࡴࡱࡱ຺ࠫ").format(user, key, host, bstack1ll111ll1_opy_)
      if cli.is_enabled(CONFIG):
        bstack11111111_opy_, hashed_id = cli.bstack111l11l1l_opy_()
        logger.info(bstack111lll111_opy_.format(bstack11111111_opy_))
        return [hashed_id, bstack11111111_opy_]
      else:
        headers = {
          bstack1l1l_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫົ"): bstack1l1l_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩຼ"),
        }
        if bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩຽ") in CONFIG:
          params = {bstack1l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭຾"): CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ຿")], bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ເ"): CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ແ")]}
        else:
          params = {bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪໂ"): CONFIG[bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩໃ")]}
        proxies = bstack1l11l1ll1l_opy_(CONFIG, url)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        if response.json():
          bstack11llll11l_opy_ = response.json()[0][bstack1l1l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡧࡻࡩ࡭ࡦࠪໄ")]
          if bstack11llll11l_opy_:
            bstack11111111_opy_ = bstack11llll11l_opy_[bstack1l1l_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣࡠࡷࡵࡰࠬ໅")].split(bstack1l1l_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤ࠯ࡥࡹ࡮ࡲࡤࠨໆ"))[0] + bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡵ࠲ࠫ໇") + bstack11llll11l_opy_[
              bstack1l1l_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪ່ࠧ")]
            logger.info(bstack111lll111_opy_.format(bstack11111111_opy_))
            bstack1l1l111l11_opy_ = bstack11llll11l_opy_[bstack1l1l_opy_ (u"ࠬ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ້")]
            bstack111l1ll11_opy_ = CONFIG[bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦ໊ࠩ")]
            if bstack1l1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ໋ࠩ") in CONFIG:
              bstack111l1ll11_opy_ += bstack1l1l_opy_ (u"ࠨࠢࠪ໌") + CONFIG[bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫໍ")]
            if bstack111l1ll11_opy_ != bstack11llll11l_opy_[bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ໎")]:
              logger.debug(bstack1lll1lllll_opy_.format(bstack11llll11l_opy_[bstack1l1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ໏")], bstack111l1ll11_opy_))
            cli.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࡫ࡪࡺ࡟ࡣࡷ࡬ࡰࡩࡥ࡬ࡪࡰ࡮ࠦ໐"), datetime.datetime.now() - bstack1ll111l1_opy_)
            return [bstack11llll11l_opy_[bstack1l1l_opy_ (u"࠭ࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩ໑")], bstack11111111_opy_]
    else:
      logger.warning(bstack11111l11l_opy_)
  except Exception as e:
    logger.debug(bstack1llll1l11_opy_.format(str(e)))
  return [None, None]
def bstack11l11111_opy_(url, bstack111lll1l1l_opy_=False):
  global CONFIG
  global bstack11l11ll11_opy_
  if not bstack11l11ll11_opy_:
    hostname = bstack1l1l1111l_opy_(url)
    is_private = bstack11111ll11_opy_(hostname)
    if (bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ໒") in CONFIG and not bstack1l1l1111l1_opy_(CONFIG[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ໓")])) and (is_private or bstack111lll1l1l_opy_):
      bstack11l11ll11_opy_ = hostname
def bstack1l1l1111l_opy_(url):
  return urlparse(url).hostname
def bstack11111ll11_opy_(hostname):
  for bstack1l111l11l1_opy_ in bstack11l111ll_opy_:
    regex = re.compile(bstack1l111l11l1_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack11llll111l_opy_(bstack1ll11lllll_opy_):
  return True if bstack1ll11lllll_opy_ in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack111l1ll1l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack1ll1ll1l11_opy_
  bstack1lll11l11_opy_ = not (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩ࡬ࡷࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭໔"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ໕"), None))
  bstack1ll11l1ll1_opy_ = getattr(driver, bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫ໖"), None) != True
  bstack1lllllllll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬ࡯ࡳࡂࡲࡳࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ໗"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡡࡱࡲࡄ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ໘"), None)
  if bstack1lllllllll_opy_:
    if not bstack1ll1llll_opy_():
      logger.warning(bstack1l1l_opy_ (u"ࠢࡏࡱࡷࠤࡦࡴࠠࡂࡲࡳࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡪࡺࡲࡪࡧࡹࡩࠥࡇࡰࡱࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵ࠱ࠦ໙"))
      return {}
    logger.debug(bstack1l1l_opy_ (u"ࠨࡒࡨࡶ࡫ࡵࡲ࡮࡫ࡱ࡫ࠥࡹࡣࡢࡰࠣࡦࡪ࡬࡯ࡳࡧࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠬ໚"))
    logger.debug(perform_scan(driver, driver_command=bstack1l1l_opy_ (u"ࠩࡨࡼࡪࡩࡵࡵࡧࡖࡧࡷ࡯ࡰࡵࠩ໛")))
    results = bstack1l11l11111_opy_(bstack1l1l_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡶࠦໜ"))
    if results is not None and results.get(bstack1l1l_opy_ (u"ࠦ࡮ࡹࡳࡶࡧࡶࠦໝ")) is not None:
        return results[bstack1l1l_opy_ (u"ࠧ࡯ࡳࡴࡷࡨࡷࠧໞ")]
    logger.error(bstack1l1l_opy_ (u"ࠨࡎࡰࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡕࡩࡸࡻ࡬ࡵࡵࠣࡻࡪࡸࡥࠡࡨࡲࡹࡳࡪ࠮ࠣໟ"))
    return []
  if not bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1ll1ll1l11_opy_) or (bstack1ll11l1ll1_opy_ and bstack1lll11l11_opy_):
    logger.warning(bstack1l1l_opy_ (u"ࠢࡏࡱࡷࠤࡦࡴࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡣࡢࡰࡱࡳࡹࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴ࠰ࠥ໠"))
    return {}
  try:
    logger.debug(bstack1l1l_opy_ (u"ࠨࡒࡨࡶ࡫ࡵࡲ࡮࡫ࡱ࡫ࠥࡹࡣࡢࡰࠣࡦࡪ࡬࡯ࡳࡧࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠬ໡"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack111111lll_opy_.bstack1l11l1ll1_opy_)
    return results
  except Exception:
    logger.error(bstack1l1l_opy_ (u"ࠤࡑࡳࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡷࡦࡴࡨࠤ࡫ࡵࡵ࡯ࡦ࠱ࠦ໢"))
    return {}
@measure(event_name=EVENTS.bstack1lllll11l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack1ll1ll1l11_opy_
  bstack1lll11l11_opy_ = not (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠪ࡭ࡸࡇ࠱࠲ࡻࡗࡩࡸࡺࠧ໣"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ໤"), None))
  bstack1ll11l1ll1_opy_ = getattr(driver, bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡆ࠷࠱ࡺࡕ࡫ࡳࡺࡲࡤࡔࡥࡤࡲࠬ໥"), None) != True
  bstack1lllllllll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭໦"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ໧"), None)
  if bstack1lllllllll_opy_:
    if not bstack1ll1llll_opy_():
      logger.warning(bstack1l1l_opy_ (u"ࠣࡐࡲࡸࠥࡧ࡮ࠡࡃࡳࡴࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡁࡱࡲࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡸࡻ࡭࡮ࡣࡵࡽ࠳ࠨ໨"))
      return {}
    logger.debug(bstack1l1l_opy_ (u"ࠩࡓࡩࡷ࡬࡯ࡳ࡯࡬ࡲ࡬ࠦࡳࡤࡣࡱࠤࡧ࡫ࡦࡰࡴࡨࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡳࡶ࡯ࡰࡥࡷࡿࠧ໩"))
    logger.debug(perform_scan(driver, driver_command=bstack1l1l_opy_ (u"ࠪࡩࡽ࡫ࡣࡶࡶࡨࡗࡨࡸࡩࡱࡶࠪ໪")))
    results = bstack1l11l11111_opy_(bstack1l1l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࡗࡺࡳ࡭ࡢࡴࡼࠦ໫"))
    if results is not None and results.get(bstack1l1l_opy_ (u"ࠧࡹࡵ࡮࡯ࡤࡶࡾࠨ໬")) is not None:
        return results[bstack1l1l_opy_ (u"ࠨࡳࡶ࡯ࡰࡥࡷࡿࠢ໭")]
    logger.error(bstack1l1l_opy_ (u"ࠢࡏࡱࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡖࡪࡹࡵ࡭ࡶࡶࠤࡘࡻ࡭࡮ࡣࡵࡽࠥࡽࡡࡴࠢࡩࡳࡺࡴࡤ࠯ࠤ໮"))
    return {}
  if not bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1ll1ll1l11_opy_) or (bstack1ll11l1ll1_opy_ and bstack1lll11l11_opy_):
    logger.warning(bstack1l1l_opy_ (u"ࠣࡐࡲࡸࠥࡧ࡮ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡤࡣࡱࡲࡴࡺࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡷࡺࡳ࡭ࡢࡴࡼ࠲ࠧ໯"))
    return {}
  try:
    logger.debug(bstack1l1l_opy_ (u"ࠩࡓࡩࡷ࡬࡯ࡳ࡯࡬ࡲ࡬ࠦࡳࡤࡣࡱࠤࡧ࡫ࡦࡰࡴࡨࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡳࡶ࡯ࡰࡥࡷࡿࠧ໰"))
    logger.debug(perform_scan(driver))
    bstack1llllll111_opy_ = driver.execute_async_script(bstack111111lll_opy_.bstack11llll1l1l_opy_)
    return bstack1llllll111_opy_
  except Exception:
    logger.error(bstack1l1l_opy_ (u"ࠥࡒࡴࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡳࡶ࡯ࡰࡥࡷࡿࠠࡸࡣࡶࠤ࡫ࡵࡵ࡯ࡦ࠱ࠦ໱"))
    return {}
def bstack1ll1llll_opy_():
  global CONFIG
  global bstack1ll1ll1l11_opy_
  bstack111lll1111_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫ࡮ࡹࡁࡱࡲࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ໲"), None) and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ໳"), None)
  if not bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1ll1ll1l11_opy_) or not bstack111lll1111_opy_:
        logger.warning(bstack1l1l_opy_ (u"ࠨࡎࡰࡶࠣࡥࡳࠦࡁࡱࡲࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢࡦࡥࡳࡴ࡯ࡵࠢࡵࡩࡹࡸࡩࡦࡸࡨࠤࡷ࡫ࡳࡶ࡮ࡷࡷ࠳ࠨ໴"))
        return False
  return True
def bstack1l11l11111_opy_(result_type):
    bstack1l111l1l11_opy_ = bstack11l1llllll_opy_.current_test_uuid() if bstack11l1llllll_opy_.current_test_uuid() else bstack1l1ll11111_opy_.current_hook_uuid()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(bstack1lll111l1l_opy_(bstack1l111l1l11_opy_, result_type))
        try:
            return future.result(timeout=bstack111l111ll_opy_)
        except TimeoutError:
            logger.error(bstack1l1l_opy_ (u"ࠢࡕ࡫ࡰࡩࡴࡻࡴࠡࡣࡩࡸࡪࡸࠠࡼࡿࡶࠤࡼ࡮ࡩ࡭ࡧࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡘࡥࡴࡷ࡯ࡸࡸࠨ໵").format(bstack111l111ll_opy_))
        except Exception as ex:
            logger.debug(bstack1l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡳࡧࡷࡶ࡮࡫ࡶࡪࡰࡪࠤࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࢁࡽ࠯ࠢࡈࡶࡷࡵࡲࠡ࠯ࠣࡿࢂࠨ໶").format(result_type, str(ex)))
    return {}
@measure(event_name=EVENTS.bstack1lll11l111_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack1ll1ll1l11_opy_
  bstack1lll11l11_opy_ = not (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩ࡬ࡷࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭໷"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ໸"), None))
  bstack1l1l1ll1l1_opy_ = not (bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫ࡮ࡹࡁࡱࡲࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ໹"), None) and bstack11llll11ll_opy_(
          threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ໺"), None))
  bstack1ll11l1ll1_opy_ = getattr(driver, bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭໻"), None) != True
  if not bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1ll1ll1l11_opy_) or (bstack1ll11l1ll1_opy_ and bstack1lll11l11_opy_ and bstack1l1l1ll1l1_opy_):
    logger.warning(bstack1l1l_opy_ (u"ࠢࡏࡱࡷࠤࡦࡴࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡣࡢࡰࡱࡳࡹࠦࡲࡶࡰࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡨࡧ࡮࠯ࠤ໼"))
    return {}
  try:
    bstack1llllllll1_opy_ = bstack1l1l_opy_ (u"ࠨࡣࡳࡴࠬ໽") in CONFIG and CONFIG.get(bstack1l1l_opy_ (u"ࠩࡤࡴࡵ࠭໾"), bstack1l1l_opy_ (u"ࠪࠫ໿"))
    session_id = getattr(driver, bstack1l1l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠨༀ"), None)
    if not session_id:
      logger.warning(bstack1l1l_opy_ (u"ࠧࡔ࡯ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡌࡈࠥ࡬࡯ࡶࡰࡧࠤ࡫ࡵࡲࠡࡦࡵ࡭ࡻ࡫ࡲࠣ༁"))
      return {bstack1l1l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ༂"): bstack1l1l_opy_ (u"ࠢࡏࡱࠣࡷࡪࡹࡳࡪࡱࡱࠤࡎࡊࠠࡧࡱࡸࡲࡩࠨ༃")}
    if bstack1llllllll1_opy_:
      try:
        bstack111ll11l_opy_ = {
              bstack1l1l_opy_ (u"ࠨࡶ࡫ࡎࡼࡺࡔࡰ࡭ࡨࡲࠬ༄"): os.environ.get(bstack1l1l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ༅"), os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ༆"), bstack1l1l_opy_ (u"ࠫࠬ༇"))),
              bstack1l1l_opy_ (u"ࠬࡺࡨࡕࡧࡶࡸࡗࡻ࡮ࡖࡷ࡬ࡨࠬ༈"): bstack11l1llllll_opy_.current_test_uuid() if bstack11l1llllll_opy_.current_test_uuid() else bstack1l1ll11111_opy_.current_hook_uuid(),
              bstack1l1l_opy_ (u"࠭ࡡࡶࡶ࡫ࡌࡪࡧࡤࡦࡴࠪ༉"): os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ༊")),
              bstack1l1l_opy_ (u"ࠨࡵࡦࡥࡳ࡚ࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ་"): str(int(datetime.datetime.now().timestamp() * 1000)),
              bstack1l1l_opy_ (u"ࠩࡷ࡬ࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧ༌"): os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ།"), bstack1l1l_opy_ (u"ࠫࠬ༎")),
              bstack1l1l_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬ༏"): kwargs.get(bstack1l1l_opy_ (u"࠭ࡤࡳ࡫ࡹࡩࡷࡥࡣࡰ࡯ࡰࡥࡳࡪࠧ༐"), None) or bstack1l1l_opy_ (u"ࠧࠨ༑")
          }
        if not hasattr(thread_local, bstack1l1l_opy_ (u"ࠨࡤࡤࡷࡪࡥࡡࡱࡲࡢࡥ࠶࠷ࡹࡠࡵࡦࡶ࡮ࡶࡴࠨ༒")):
            scripts = {bstack1l1l_opy_ (u"ࠩࡶࡧࡦࡴࠧ༓"): bstack111111lll_opy_.perform_scan}
            thread_local.base_app_a11y_script = scripts
        bstack111llll11l_opy_ = copy.deepcopy(thread_local.base_app_a11y_script)
        bstack111llll11l_opy_[bstack1l1l_opy_ (u"ࠪࡷࡨࡧ࡮ࠨ༔")] = bstack111llll11l_opy_[bstack1l1l_opy_ (u"ࠫࡸࡩࡡ࡯ࠩ༕")] % json.dumps(bstack111ll11l_opy_)
        bstack111111lll_opy_.bstack11l1l1l11_opy_(bstack111llll11l_opy_)
        bstack111111lll_opy_.store()
        bstack11l1l1ll11_opy_ = driver.execute_script(bstack111111lll_opy_.perform_scan)
      except Exception as bstack111lll1l11_opy_:
        logger.info(bstack1l1l_opy_ (u"ࠧࡇࡰࡱ࡫ࡸࡱࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࠧ༖") + str(bstack111lll1l11_opy_))
        bstack11l1l1ll11_opy_ = {bstack1l1l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ༗"): str(bstack111lll1l11_opy_)}
    else:
      bstack11l1l1ll11_opy_ = driver.execute_async_script(bstack111111lll_opy_.perform_scan, {bstack1l1l_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪ༘ࠧ"): kwargs.get(bstack1l1l_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࡠࡥࡲࡱࡲࡧ࡮ࡥ༙ࠩ"), None) or bstack1l1l_opy_ (u"ࠩࠪ༚")})
    return bstack11l1l1ll11_opy_
  except Exception as err:
    logger.error(bstack1l1l_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡲࡶࡰࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡨࡧ࡮࠯ࠢࡾࢁࠧ༛").format(str(err)))
    return {}