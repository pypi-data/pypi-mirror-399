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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
from bstack_utils.constants import bstack11l1l1l11ll_opy_
logger = logging.getLogger(__name__)
class bstack11l1ll1lll1_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1llll1lll111_opy_ = urljoin(builder, bstack11111l_opy_ (u"ࠧࡪࡵࡶࡹࡪࡹࠧ⁄"))
        if params:
            bstack1llll1lll111_opy_ += bstack11111l_opy_ (u"ࠣࡁࡾࢁࠧ⁅").format(urlencode({bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⁆"): params.get(bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⁇"))}))
        return bstack11l1ll1lll1_opy_.bstack1llll1ll1ll1_opy_(bstack1llll1lll111_opy_)
    @staticmethod
    def bstack11l1lll1111_opy_(builder,params=None):
        bstack1llll1lll111_opy_ = urljoin(builder, bstack11111l_opy_ (u"ࠫ࡮ࡹࡳࡶࡧࡶ࠱ࡸࡻ࡭࡮ࡣࡵࡽࠬ⁈"))
        if params:
            bstack1llll1lll111_opy_ += bstack11111l_opy_ (u"ࠧࡅࡻࡾࠤ⁉").format(urlencode({bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⁊"): params.get(bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⁋"))}))
        return bstack11l1ll1lll1_opy_.bstack1llll1ll1ll1_opy_(bstack1llll1lll111_opy_)
    @staticmethod
    def bstack1llll1ll1ll1_opy_(bstack1llll1ll1l1l_opy_):
        bstack1llll1llll11_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭⁌"), os.environ.get(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭⁍"), bstack11111l_opy_ (u"ࠪࠫ⁎")))
        headers = {bstack11111l_opy_ (u"ࠫࡆࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ⁏"): bstack11111l_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ⁐").format(bstack1llll1llll11_opy_)}
        response = requests.get(bstack1llll1ll1l1l_opy_, headers=headers)
        bstack1llll1lll11l_opy_ = {}
        try:
            bstack1llll1lll11l_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡌࡖࡓࡓࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ⁑").format(e))
            pass
        if bstack1llll1lll11l_opy_ is not None:
            bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ⁒")] = response.headers.get(bstack11111l_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩ⁓"), str(int(datetime.now().timestamp() * 1000)))
            bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ⁔")] = response.status_code
        return bstack1llll1lll11l_opy_
    @staticmethod
    def bstack1llll1lll1ll_opy_(bstack1llll1lll1l1_opy_, data):
        logger.debug(bstack11111l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡓࡧࡴࡹࡪࡹࡴࠡࡨࡲࡶࠥࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡕࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࠧ⁕"))
        return bstack11l1ll1lll1_opy_.bstack1llll1ll1l11_opy_(bstack11111l_opy_ (u"ࠫࡕࡕࡓࡕࠩ⁖"), bstack1llll1lll1l1_opy_, data=data)
    @staticmethod
    def bstack1llll1ll11ll_opy_(bstack1llll1lll1l1_opy_, data):
        logger.debug(bstack11111l_opy_ (u"ࠧࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡕࡩࡶࡻࡥࡴࡶࠣࡪࡴࡸࠠࡨࡧࡷࡘࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡷࠧ⁗"))
        res = bstack11l1ll1lll1_opy_.bstack1llll1ll1l11_opy_(bstack11111l_opy_ (u"࠭ࡇࡆࡖࠪ⁘"), bstack1llll1lll1l1_opy_, data=data)
        return res
    @staticmethod
    def bstack1llll1ll1l11_opy_(method, bstack1llll1lll1l1_opy_, data=None, params=None, extra_headers=None):
        bstack1llll1llll11_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⁙"), bstack11111l_opy_ (u"ࠨࠩ⁚"))
        headers = {
            bstack11111l_opy_ (u"ࠩࡤࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ⁛"): bstack11111l_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࡿࢂ࠭⁜").format(bstack1llll1llll11_opy_),
            bstack11111l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ⁝"): bstack11111l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ⁞"),
            bstack11111l_opy_ (u"࠭ࡁࡤࡥࡨࡴࡹ࠭ "): bstack11111l_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ⁠")
        }
        if extra_headers:
            headers.update(extra_headers)
        url = bstack11l1l1l11ll_opy_ + bstack11111l_opy_ (u"ࠣ࠱ࠥ⁡") + bstack1llll1lll1l1_opy_.lstrip(bstack11111l_opy_ (u"ࠩ࠲ࠫ⁢"))
        try:
            if method == bstack11111l_opy_ (u"ࠪࡋࡊ࡚ࠧ⁣"):
                response = requests.get(url, headers=headers, params=params, json=data)
            elif method == bstack11111l_opy_ (u"ࠫࡕࡕࡓࡕࠩ⁤"):
                response = requests.post(url, headers=headers, json=data)
            elif method == bstack11111l_opy_ (u"ࠬࡖࡕࡕࠩ⁥"):
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(bstack11111l_opy_ (u"ࠨࡕ࡯ࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤࡍ࡚ࡔࡑࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠣࡿࢂࠨ⁦").format(method))
            logger.debug(bstack11111l_opy_ (u"ࠢࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡳࡧࡴࡹࡪࡹࡴࠡ࡯ࡤࡨࡪࠦࡴࡰࠢࡘࡖࡑࡀࠠࡼࡿࠣࡻ࡮ࡺࡨࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠢࡾࢁࠧ⁧").format(url, method))
            bstack1llll1lll11l_opy_ = {}
            try:
                bstack1llll1lll11l_opy_ = response.json()
            except Exception as e:
                logger.debug(bstack11111l_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡎࡘࡕࡎࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠠ࠮ࠢࡾࢁࠧ⁨").format(e, response.text))
            if bstack1llll1lll11l_opy_ is not None:
                bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ⁩")] = response.headers.get(
                    bstack11111l_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫ⁪"), str(int(datetime.now().timestamp() * 1000))
                )
                bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⁫")] = response.status_code
            return bstack1llll1lll11l_opy_
        except Exception as e:
            logger.error(bstack11111l_opy_ (u"ࠧࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࠥࡸࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࡀࠠࡼࡿࠣ࠱ࠥࢁࡽࠣ⁬").format(e, url))
            return None
    @staticmethod
    def bstack11l11l1l1ll_opy_(bstack1llll1ll1l1l_opy_, data):
        bstack11111l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡗࡪࡴࡤࡴࠢࡤࠤࡕ࡛ࡔࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳࠥࡹࡴࡰࡴࡨࠤࡹ࡮ࡥࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ⁭")
        bstack1llll1llll11_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⁮"), bstack11111l_opy_ (u"ࠨࠩ⁯"))
        headers = {
            bstack11111l_opy_ (u"ࠩࡤࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ⁰"): bstack11111l_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࡿࢂ࠭ⁱ").format(bstack1llll1llll11_opy_),
            bstack11111l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ⁲"): bstack11111l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ⁳")
        }
        response = requests.put(bstack1llll1ll1l1l_opy_, headers=headers, json=data)
        bstack1llll1lll11l_opy_ = {}
        try:
            bstack1llll1lll11l_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡌࡖࡓࡓࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ⁴").format(e))
            pass
        logger.debug(bstack11111l_opy_ (u"ࠢࡓࡧࡴࡹࡪࡹࡴࡖࡶ࡬ࡰࡸࡀࠠࡱࡷࡷࡣ࡫ࡧࡩ࡭ࡧࡧࡣࡹ࡫ࡳࡵࡵࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ⁵").format(bstack1llll1lll11l_opy_))
        if bstack1llll1lll11l_opy_ is not None:
            bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩ⁶")] = response.headers.get(
                bstack11111l_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ⁷"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⁸")] = response.status_code
        return bstack1llll1lll11l_opy_
    @staticmethod
    def bstack11l11l11ll1_opy_(bstack1llll1ll1l1l_opy_):
        bstack11111l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡕࡨࡲࡩࡹࠠࡢࠢࡊࡉ࡙ࠦࡲࡦࡳࡸࡩࡸࡺࠠࡵࡱࠣ࡫ࡪࡺࠠࡵࡪࡨࠤࡨࡵࡵ࡯ࡶࠣࡳ࡫ࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤ⁹")
        bstack1llll1llll11_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⁺"), bstack11111l_opy_ (u"࠭ࠧ⁻"))
        headers = {
            bstack11111l_opy_ (u"ࠧࡢࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧ⁼"): bstack11111l_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࡽࢀࠫ⁽").format(bstack1llll1llll11_opy_),
            bstack11111l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨ⁾"): bstack11111l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ⁿ")
        }
        response = requests.get(bstack1llll1ll1l1l_opy_, headers=headers)
        bstack1llll1lll11l_opy_ = {}
        try:
            bstack1llll1lll11l_opy_ = response.json()
            logger.debug(bstack11111l_opy_ (u"ࠦࡗ࡫ࡱࡶࡧࡶࡸ࡚ࡺࡩ࡭ࡵ࠽ࠤ࡬࡫ࡴࡠࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠨ₀").format(bstack1llll1lll11l_opy_))
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡤࡶࡸ࡫ࠠࡋࡕࡒࡒࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠤ࠲ࠦࡻࡾࠤ₁").format(e, response.text))
            pass
        if bstack1llll1lll11l_opy_ is not None:
            bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧ₂")] = response.headers.get(
                bstack11111l_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ₃"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1lll11l_opy_[bstack11111l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ₄")] = response.status_code
        return bstack1llll1lll11l_opy_
    @staticmethod
    def bstack1111ll11lll_opy_(bstack11l1lll1l1l_opy_, payload):
        bstack11111l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡍࡢ࡭ࡨࡷࠥࡧࠠࡑࡑࡖࡘࠥࡸࡥࡲࡷࡨࡷࡹࠦࡴࡰࠢࡷ࡬ࡪࠦࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡣࡷ࡬ࡰࡩ࠳ࡤࡢࡶࡤࠤࡪࡴࡤࡱࡱ࡬ࡲࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠠࠩࡵࡷࡶ࠮ࡀࠠࡕࡪࡨࠤࡆࡖࡉࠡࡧࡱࡨࡵࡵࡩ࡯ࡶࠣࡴࡦࡺࡨ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡱࡣࡼࡰࡴࡧࡤࠡࠪࡧ࡭ࡨࡺࠩ࠻ࠢࡗ࡬ࡪࠦࡲࡦࡳࡸࡩࡸࡺࠠࡱࡣࡼࡰࡴࡧࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡨ࡮ࡩࡴ࠻ࠢࡕࡩࡸࡶ࡯࡯ࡵࡨࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡁࡑࡋ࠯ࠤࡴࡸࠠࡏࡱࡱࡩࠥ࡯ࡦࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨ₅")
        try:
            url = bstack11111l_opy_ (u"ࠥࡿࢂ࠵ࡻࡾࠤ₆").format(bstack11l1l1l11ll_opy_, bstack11l1lll1l1l_opy_)
            bstack1llll1llll11_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ₇"), bstack11111l_opy_ (u"ࠬ࠭₈"))
            headers = {
                bstack11111l_opy_ (u"࠭ࡡࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭₉"): bstack11111l_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪ₊").format(bstack1llll1llll11_opy_),
                bstack11111l_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧ₋"): bstack11111l_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ₌")
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            bstack1llll1ll1lll_opy_ = [200, 202]
            if response.status_code in bstack1llll1ll1lll_opy_:
                return response.json()
            else:
                logger.error(bstack11111l_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡣࡰ࡮࡯ࡩࡨࡺࠠࡣࡷ࡬ࡰࡩࠦࡤࡢࡶࡤ࠲࡙ࠥࡴࡢࡶࡸࡷ࠿ࠦࡻࡾ࠮ࠣࡖࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ₍").format(
                    response.status_code, response.text))
                return None
        except Exception as e:
            logger.error(bstack11111l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡴࡹࡴࡠࡥࡲࡰࡱ࡫ࡣࡵࡡࡥࡹ࡮ࡲࡤࡠࡦࡤࡸࡦࡀࠠࡼࡿࠥ₎").format(e))
            return None