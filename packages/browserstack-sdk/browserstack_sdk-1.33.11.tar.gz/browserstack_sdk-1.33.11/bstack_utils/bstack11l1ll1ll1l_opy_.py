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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
from bstack_utils.constants import bstack11l11lll1l1_opy_
logger = logging.getLogger(__name__)
class bstack11l1ll1l1l1_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1llll1ll11l1_opy_ = urljoin(builder, bstack1l1l_opy_ (u"ࠧࡪࡵࡶࡹࡪࡹࠧ⁋"))
        if params:
            bstack1llll1ll11l1_opy_ += bstack1l1l_opy_ (u"ࠣࡁࡾࢁࠧ⁌").format(urlencode({bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⁍"): params.get(bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⁎"))}))
        return bstack11l1ll1l1l1_opy_.bstack1llll1ll1l1l_opy_(bstack1llll1ll11l1_opy_)
    @staticmethod
    def bstack11l1ll1l11l_opy_(builder,params=None):
        bstack1llll1ll11l1_opy_ = urljoin(builder, bstack1l1l_opy_ (u"ࠫ࡮ࡹࡳࡶࡧࡶ࠱ࡸࡻ࡭࡮ࡣࡵࡽࠬ⁏"))
        if params:
            bstack1llll1ll11l1_opy_ += bstack1l1l_opy_ (u"ࠧࡅࡻࡾࠤ⁐").format(urlencode({bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⁑"): params.get(bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⁒"))}))
        return bstack11l1ll1l1l1_opy_.bstack1llll1ll1l1l_opy_(bstack1llll1ll11l1_opy_)
    @staticmethod
    def bstack1llll1ll1l1l_opy_(bstack1llll1lll11l_opy_):
        bstack1llll1ll1ll1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭⁓"), os.environ.get(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭⁔"), bstack1l1l_opy_ (u"ࠪࠫ⁕")))
        headers = {bstack1l1l_opy_ (u"ࠫࡆࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ⁖"): bstack1l1l_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ⁗").format(bstack1llll1ll1ll1_opy_)}
        response = requests.get(bstack1llll1lll11l_opy_, headers=headers)
        bstack1llll1lll111_opy_ = {}
        try:
            bstack1llll1lll111_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡌࡖࡓࡓࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ⁘").format(e))
            pass
        if bstack1llll1lll111_opy_ is not None:
            bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ⁙")] = response.headers.get(bstack1l1l_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩ⁚"), str(int(datetime.now().timestamp() * 1000)))
            bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ⁛")] = response.status_code
        return bstack1llll1lll111_opy_
    @staticmethod
    def bstack1llll1lll1l1_opy_(bstack1llll1ll11ll_opy_, data):
        logger.debug(bstack1l1l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡓࡧࡴࡹࡪࡹࡴࠡࡨࡲࡶࠥࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡕࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࠧ⁜"))
        return bstack11l1ll1l1l1_opy_.bstack1llll1ll1l11_opy_(bstack1l1l_opy_ (u"ࠫࡕࡕࡓࡕࠩ⁝"), bstack1llll1ll11ll_opy_, data=data)
    @staticmethod
    def bstack1llll1ll111l_opy_(bstack1llll1ll11ll_opy_, data):
        logger.debug(bstack1l1l_opy_ (u"ࠧࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡕࡩࡶࡻࡥࡴࡶࠣࡪࡴࡸࠠࡨࡧࡷࡘࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡷࠧ⁞"))
        res = bstack11l1ll1l1l1_opy_.bstack1llll1ll1l11_opy_(bstack1l1l_opy_ (u"࠭ࡇࡆࡖࠪ "), bstack1llll1ll11ll_opy_, data=data)
        return res
    @staticmethod
    def bstack1llll1ll1l11_opy_(method, bstack1llll1ll11ll_opy_, data=None, params=None, extra_headers=None):
        bstack1llll1ll1ll1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⁠"), bstack1l1l_opy_ (u"ࠨࠩ⁡"))
        headers = {
            bstack1l1l_opy_ (u"ࠩࡤࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ⁢"): bstack1l1l_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࡿࢂ࠭⁣").format(bstack1llll1ll1ll1_opy_),
            bstack1l1l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ⁤"): bstack1l1l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ⁥"),
            bstack1l1l_opy_ (u"࠭ࡁࡤࡥࡨࡴࡹ࠭⁦"): bstack1l1l_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ⁧")
        }
        if extra_headers:
            headers.update(extra_headers)
        url = bstack11l11lll1l1_opy_ + bstack1l1l_opy_ (u"ࠣ࠱ࠥ⁨") + bstack1llll1ll11ll_opy_.lstrip(bstack1l1l_opy_ (u"ࠩ࠲ࠫ⁩"))
        try:
            if method == bstack1l1l_opy_ (u"ࠪࡋࡊ࡚ࠧ⁪"):
                response = requests.get(url, headers=headers, params=params, json=data)
            elif method == bstack1l1l_opy_ (u"ࠫࡕࡕࡓࡕࠩ⁫"):
                response = requests.post(url, headers=headers, json=data)
            elif method == bstack1l1l_opy_ (u"ࠬࡖࡕࡕࠩ⁬"):
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(bstack1l1l_opy_ (u"ࠨࡕ࡯ࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤࡍ࡚ࡔࡑࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠣࡿࢂࠨ⁭").format(method))
            logger.debug(bstack1l1l_opy_ (u"ࠢࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡳࡧࡴࡹࡪࡹࡴࠡ࡯ࡤࡨࡪࠦࡴࡰࠢࡘࡖࡑࡀࠠࡼࡿࠣࡻ࡮ࡺࡨࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠢࡾࢁࠧ⁮").format(url, method))
            bstack1llll1lll111_opy_ = {}
            try:
                bstack1llll1lll111_opy_ = response.json()
            except Exception as e:
                logger.debug(bstack1l1l_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡎࡘࡕࡎࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠠ࠮ࠢࡾࢁࠧ⁯").format(e, response.text))
            if bstack1llll1lll111_opy_ is not None:
                bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ⁰")] = response.headers.get(
                    bstack1l1l_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫⁱ"), str(int(datetime.now().timestamp() * 1000))
                )
                bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⁲")] = response.status_code
            return bstack1llll1lll111_opy_
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠧࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࠥࡸࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࡀࠠࡼࡿࠣ࠱ࠥࢁࡽࠣ⁳").format(e, url))
            return None
    @staticmethod
    def bstack11l11l11ll1_opy_(bstack1llll1lll11l_opy_, data):
        bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡗࡪࡴࡤࡴࠢࡤࠤࡕ࡛ࡔࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳࠥࡹࡴࡰࡴࡨࠤࡹ࡮ࡥࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ⁴")
        bstack1llll1ll1ll1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⁵"), bstack1l1l_opy_ (u"ࠨࠩ⁶"))
        headers = {
            bstack1l1l_opy_ (u"ࠩࡤࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ⁷"): bstack1l1l_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࡿࢂ࠭⁸").format(bstack1llll1ll1ll1_opy_),
            bstack1l1l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ⁹"): bstack1l1l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ⁺")
        }
        response = requests.put(bstack1llll1lll11l_opy_, headers=headers, json=data)
        bstack1llll1lll111_opy_ = {}
        try:
            bstack1llll1lll111_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡌࡖࡓࡓࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ⁻").format(e))
            pass
        logger.debug(bstack1l1l_opy_ (u"ࠢࡓࡧࡴࡹࡪࡹࡴࡖࡶ࡬ࡰࡸࡀࠠࡱࡷࡷࡣ࡫ࡧࡩ࡭ࡧࡧࡣࡹ࡫ࡳࡵࡵࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ⁼").format(bstack1llll1lll111_opy_))
        if bstack1llll1lll111_opy_ is not None:
            bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩ⁽")] = response.headers.get(
                bstack1l1l_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ⁾"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪⁿ")] = response.status_code
        return bstack1llll1lll111_opy_
    @staticmethod
    def bstack11l11l1l1l1_opy_(bstack1llll1lll11l_opy_):
        bstack1l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡕࡨࡲࡩࡹࠠࡢࠢࡊࡉ࡙ࠦࡲࡦࡳࡸࡩࡸࡺࠠࡵࡱࠣ࡫ࡪࡺࠠࡵࡪࡨࠤࡨࡵࡵ࡯ࡶࠣࡳ࡫ࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤ₀")
        bstack1llll1ll1ll1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ₁"), bstack1l1l_opy_ (u"࠭ࠧ₂"))
        headers = {
            bstack1l1l_opy_ (u"ࠧࡢࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧ₃"): bstack1l1l_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࡽࢀࠫ₄").format(bstack1llll1ll1ll1_opy_),
            bstack1l1l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨ₅"): bstack1l1l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭₆")
        }
        response = requests.get(bstack1llll1lll11l_opy_, headers=headers)
        bstack1llll1lll111_opy_ = {}
        try:
            bstack1llll1lll111_opy_ = response.json()
            logger.debug(bstack1l1l_opy_ (u"ࠦࡗ࡫ࡱࡶࡧࡶࡸ࡚ࡺࡩ࡭ࡵ࠽ࠤ࡬࡫ࡴࡠࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠨ₇").format(bstack1llll1lll111_opy_))
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡤࡶࡸ࡫ࠠࡋࡕࡒࡒࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠤ࠲ࠦࡻࡾࠤ₈").format(e, response.text))
            pass
        if bstack1llll1lll111_opy_ is not None:
            bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧ₉")] = response.headers.get(
                bstack1l1l_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ₊"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1lll111_opy_[bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ₋")] = response.status_code
        return bstack1llll1lll111_opy_
    @staticmethod
    def bstack1111ll11l1l_opy_(bstack11l1lll11ll_opy_, payload):
        bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡍࡢ࡭ࡨࡷࠥࡧࠠࡑࡑࡖࡘࠥࡸࡥࡲࡷࡨࡷࡹࠦࡴࡰࠢࡷ࡬ࡪࠦࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡣࡷ࡬ࡰࡩ࠳ࡤࡢࡶࡤࠤࡪࡴࡤࡱࡱ࡬ࡲࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠠࠩࡵࡷࡶ࠮ࡀࠠࡕࡪࡨࠤࡆࡖࡉࠡࡧࡱࡨࡵࡵࡩ࡯ࡶࠣࡴࡦࡺࡨ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡱࡣࡼࡰࡴࡧࡤࠡࠪࡧ࡭ࡨࡺࠩ࠻ࠢࡗ࡬ࡪࠦࡲࡦࡳࡸࡩࡸࡺࠠࡱࡣࡼࡰࡴࡧࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡨ࡮ࡩࡴ࠻ࠢࡕࡩࡸࡶ࡯࡯ࡵࡨࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡁࡑࡋ࠯ࠤࡴࡸࠠࡏࡱࡱࡩࠥ࡯ࡦࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨ₌")
        try:
            url = bstack1l1l_opy_ (u"ࠥࡿࢂ࠵ࡻࡾࠤ₍").format(bstack11l11lll1l1_opy_, bstack11l1lll11ll_opy_)
            bstack1llll1ll1ll1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ₎"), bstack1l1l_opy_ (u"ࠬ࠭₏"))
            headers = {
                bstack1l1l_opy_ (u"࠭ࡡࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭ₐ"): bstack1l1l_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪₑ").format(bstack1llll1ll1ll1_opy_),
                bstack1l1l_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧₒ"): bstack1l1l_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬₓ")
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            bstack1llll1ll1lll_opy_ = [200, 202]
            if response.status_code in bstack1llll1ll1lll_opy_:
                return response.json()
            else:
                logger.error(bstack1l1l_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡣࡰ࡮࡯ࡩࡨࡺࠠࡣࡷ࡬ࡰࡩࠦࡤࡢࡶࡤ࠲࡙ࠥࡴࡢࡶࡸࡷ࠿ࠦࡻࡾ࠮ࠣࡖࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤₔ").format(
                    response.status_code, response.text))
                return None
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡴࡹࡴࡠࡥࡲࡰࡱ࡫ࡣࡵࡡࡥࡹ࡮ࡲࡤࡠࡦࡤࡸࡦࡀࠠࡼࡿࠥₕ").format(e))
            return None