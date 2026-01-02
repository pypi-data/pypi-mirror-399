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
import json
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll111l1ll_opy_, bstack11l1llll1ll_opy_, bstack111ll1lll_opy_, error_handler, bstack111lll11l1l_opy_, bstack11l11111lll_opy_, bstack111l1ll1111_opy_, bstack111l1l11_opy_, bstack11l1l111l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1llll1lllll1_opy_ import bstack1lllll1111ll_opy_
import bstack_utils.bstack1lll1lllll_opy_ as bstack1l11lllll_opy_
from bstack_utils.bstack111l1ll111_opy_ import bstack11l11ll11l_opy_
import bstack_utils.accessibility as bstack1l1l11ll11_opy_
from bstack_utils.bstack11ll11111_opy_ import bstack11ll11111_opy_
from bstack_utils.bstack111l1ll1l1_opy_ import bstack1111ll1l1l_opy_
from bstack_utils.constants import bstack11ll11l11_opy_
bstack1lll1lll1111_opy_ = bstack11111l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡩ࡯࡭࡮ࡨࡧࡹࡵࡲ࠮ࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫ⅋")
logger = logging.getLogger(__name__)
class bstack11l1ll1l1l_opy_:
    bstack1llll1lllll1_opy_ = None
    bs_config = None
    bstack1l11111l_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1l1l1ll1_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def launch(cls, bs_config, bstack1l11111l_opy_):
        cls.bs_config = bs_config
        cls.bstack1l11111l_opy_ = bstack1l11111l_opy_
        try:
            cls.bstack1lll1ll1llll_opy_()
            bstack11ll11llll1_opy_ = bstack11ll111l1ll_opy_(bs_config)
            bstack11ll11l1l11_opy_ = bstack11l1llll1ll_opy_(bs_config)
            data = bstack1l11lllll_opy_.bstack1llll11111l1_opy_(bs_config, bstack1l11111l_opy_)
            config = {
                bstack11111l_opy_ (u"ࠬࡧࡵࡵࡪࠪ⅌"): (bstack11ll11llll1_opy_, bstack11ll11l1l11_opy_),
                bstack11111l_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧ⅍"): cls.default_headers()
            }
            response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"ࠧࡑࡑࡖࡘࠬⅎ"), cls.request_url(bstack11111l_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠲࠰ࡤࡸ࡭ࡱࡪࡳࠨ⅏")), data, config)
            if response.status_code != 200:
                bstack11l1l1l11l_opy_ = response.json()
                if bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ⅐")] == False:
                    cls.bstack1lll1lll1l11_opy_(bstack11l1l1l11l_opy_)
                    return
                cls.bstack1llll1111l11_opy_(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⅑")])
                cls.bstack1llll111l111_opy_(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ⅒")])
                return None
            bstack1lll1llll111_opy_ = cls.bstack1llll1111l1l_opy_(response)
            return bstack1lll1llll111_opy_, response.json()
        except Exception as error:
            logger.error(bstack11111l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡥࡹ࡮ࡲࡤࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࡼࡿࠥ⅓").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1lll1lllllll_opy_=None):
        if not bstack11l11ll11l_opy_.on() and not bstack1l1l11ll11_opy_.on():
            return
        if os.environ.get(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⅔")) == bstack11111l_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ⅕") or os.environ.get(bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭⅖")) == bstack11111l_opy_ (u"ࠤࡱࡹࡱࡲࠢ⅗"):
            logger.error(bstack11111l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡴࡶࠠࡣࡷ࡬ࡰࡩࠦࡲࡦࡳࡸࡩࡸࡺࠠࡵࡱࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡡࡶࡶ࡫ࡩࡳࡺࡩࡤࡣࡷ࡭ࡴࡴࠠࡵࡱ࡮ࡩࡳ࠭⅘"))
            return {
                bstack11111l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⅙"): bstack11111l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ⅚"),
                bstack11111l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⅛"): bstack11111l_opy_ (u"ࠧࡕࡱ࡮ࡩࡳ࠵ࡢࡶ࡫࡯ࡨࡎࡊࠠࡪࡵࠣࡹࡳࡪࡥࡧ࡫ࡱࡩࡩ࠲ࠠࡣࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡ࡯࡬࡫࡭ࡺࠠࡩࡣࡹࡩࠥ࡬ࡡࡪ࡮ࡨࡨࠬ⅜")
            }
        try:
            cls.bstack1llll1lllll1_opy_.shutdown()
            data = {
                bstack11111l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⅝"): bstack111l1l11_opy_()
            }
            if not bstack1lll1lllllll_opy_ is None:
                data[bstack11111l_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡲ࡫ࡴࡢࡦࡤࡸࡦ࠭⅞")] = [{
                    bstack11111l_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪ⅟"): bstack11111l_opy_ (u"ࠫࡺࡹࡥࡳࡡ࡮࡭ࡱࡲࡥࡥࠩⅠ"),
                    bstack11111l_opy_ (u"ࠬࡹࡩࡨࡰࡤࡰࠬⅡ"): bstack1lll1lllllll_opy_
                }]
            config = {
                bstack11111l_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧⅢ"): cls.default_headers()
            }
            bstack11l1lll1l1l_opy_ = bstack11111l_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠷࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡹࡵࡰࠨⅣ").format(os.environ[bstack11111l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨⅤ")])
            bstack1llll11111ll_opy_ = cls.request_url(bstack11l1lll1l1l_opy_)
            response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"ࠩࡓ࡙࡙࠭Ⅵ"), bstack1llll11111ll_opy_, data, config)
            if not response.ok:
                raise Exception(bstack11111l_opy_ (u"ࠥࡗࡹࡵࡰࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡱࡳࡹࠦ࡯࡬ࠤⅦ"))
        except Exception as error:
            logger.error(bstack11111l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࡀࠠࠣⅧ") + str(error))
            return {
                bstack11111l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬⅨ"): bstack11111l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬⅩ"),
                bstack11111l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨⅪ"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll1111l1l_opy_(cls, response):
        bstack11l1l1l11l_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1lll1llll111_opy_ = {}
        if bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠨ࡬ࡺࡸࠬⅫ")) is None:
            os.environ[bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭Ⅼ")] = bstack11111l_opy_ (u"ࠪࡲࡺࡲ࡬ࠨⅭ")
        else:
            os.environ[bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨⅮ")] = bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠬࡰࡷࡵࠩⅯ"), bstack11111l_opy_ (u"࠭࡮ࡶ࡮࡯ࠫⅰ"))
        os.environ[bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬⅱ")] = bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪⅲ"), bstack11111l_opy_ (u"ࠩࡱࡹࡱࡲࠧⅳ"))
        logger.info(bstack11111l_opy_ (u"ࠪࡘࡪࡹࡴࡩࡷࡥࠤࡸࡺࡡࡳࡶࡨࡨࠥࡽࡩࡵࡪࠣ࡭ࡩࡀࠠࠨⅴ") + os.getenv(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩⅵ")));
        if bstack11l11ll11l_opy_.bstack1lll1llll1ll_opy_(cls.bs_config, cls.bstack1l11111l_opy_.get(bstack11111l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡷࡶࡩࡩ࠭ⅶ"), bstack11111l_opy_ (u"࠭ࠧⅷ"))) is True:
            bstack1llll1llll11_opy_, build_hashed_id, bstack1lll1llll1l1_opy_ = cls.bstack1lll1lll11l1_opy_(bstack11l1l1l11l_opy_)
            if bstack1llll1llll11_opy_ != None and build_hashed_id != None:
                bstack1lll1llll111_opy_[bstack11111l_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧⅸ")] = {
                    bstack11111l_opy_ (u"ࠨ࡬ࡺࡸࡤࡺ࡯࡬ࡧࡱࠫⅹ"): bstack1llll1llll11_opy_,
                    bstack11111l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫⅺ"): build_hashed_id,
                    bstack11111l_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡡࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧⅻ"): bstack1lll1llll1l1_opy_
                }
            else:
                bstack1lll1llll111_opy_[bstack11111l_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫⅼ")] = {}
        else:
            bstack1lll1llll111_opy_[bstack11111l_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬⅽ")] = {}
        bstack1lll1lll1lll_opy_, build_hashed_id = cls.bstack1lll1llllll1_opy_(bstack11l1l1l11l_opy_)
        if bstack1lll1lll1lll_opy_ != None and build_hashed_id != None:
            bstack1lll1llll111_opy_[bstack11111l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ⅾ")] = {
                bstack11111l_opy_ (u"ࠧࡢࡷࡷ࡬ࡤࡺ࡯࡬ࡧࡱࠫⅿ"): bstack1lll1lll1lll_opy_,
                bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪↀ"): build_hashed_id,
            }
        else:
            bstack1lll1llll111_opy_[bstack11111l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩↁ")] = {}
        if bstack1lll1llll111_opy_[bstack11111l_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪↂ")].get(bstack11111l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭Ↄ")) != None or bstack1lll1llll111_opy_[bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬↄ")].get(bstack11111l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨↅ")) != None:
            cls.bstack1llll1111lll_opy_(bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠧ࡫ࡹࡷࠫↆ")), bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪↇ")))
        return bstack1lll1llll111_opy_
    @classmethod
    def bstack1lll1lll11l1_opy_(cls, bstack11l1l1l11l_opy_):
        if bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩↈ")) == None:
            cls.bstack1llll1111l11_opy_()
            return [None, None, None]
        if bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ↉")][bstack11111l_opy_ (u"ࠫࡸࡻࡣࡤࡧࡶࡷࠬ↊")] != True:
            cls.bstack1llll1111l11_opy_(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ↋")])
            return [None, None, None]
        logger.debug(bstack11111l_opy_ (u"࠭ࡻࡾࠢࡅࡹ࡮ࡲࡤࠡࡥࡵࡩࡦࡺࡩࡰࡰࠣࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠡࠨ↌").format(bstack11ll11l11_opy_))
        os.environ[bstack11111l_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡇࡔࡓࡐࡍࡇࡗࡉࡉ࠭↍")] = bstack11111l_opy_ (u"ࠨࡶࡵࡹࡪ࠭↎")
        if bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠩ࡭ࡻࡹ࠭↏")):
            os.environ[bstack11111l_opy_ (u"ࠪࡇࡗࡋࡄࡆࡐࡗࡍࡆࡒࡓࡠࡈࡒࡖࡤࡉࡒࡂࡕࡋࡣࡗࡋࡐࡐࡔࡗࡍࡓࡍࠧ←")] = json.dumps({
                bstack11111l_opy_ (u"ࠫࡺࡹࡥࡳࡰࡤࡱࡪ࠭↑"): bstack11ll111l1ll_opy_(cls.bs_config),
                bstack11111l_opy_ (u"ࠬࡶࡡࡴࡵࡺࡳࡷࡪࠧ→"): bstack11l1llll1ll_opy_(cls.bs_config)
            })
        if bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ↓")):
            os.environ[bstack11111l_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭↔")] = bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ↕")]
        if bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ↖")].get(bstack11111l_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ↗"), {}).get(bstack11111l_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨ↘")):
            os.environ[bstack11111l_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡄࡐࡑࡕࡗࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࡘ࠭↙")] = str(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭↚")][bstack11111l_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨ↛")][bstack11111l_opy_ (u"ࠨࡣ࡯ࡰࡴࡽ࡟ࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬ↜")])
        else:
            os.environ[bstack11111l_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡁࡍࡎࡒ࡛ࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࡕࠪ↝")] = bstack11111l_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ↞")
        return [bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠫ࡯ࡽࡴࠨ↟")], bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ↠")], os.environ[bstack11111l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ↡")]]
    @classmethod
    def bstack1lll1llllll1_opy_(cls, bstack11l1l1l11l_opy_):
        if bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ↢")) == None:
            cls.bstack1llll111l111_opy_()
            return [None, None]
        if bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ↣")][bstack11111l_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ↤")] != True:
            cls.bstack1llll111l111_opy_(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ↥")])
            return [None, None]
        if bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ↦")].get(bstack11111l_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭↧")):
            logger.debug(bstack11111l_opy_ (u"࠭ࡔࡦࡵࡷࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡇࡻࡩ࡭ࡦࠣࡧࡷ࡫ࡡࡵ࡫ࡲࡲ࡙ࠥࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭ࠣࠪ↨"))
            parsed = json.loads(os.getenv(bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ↩"), bstack11111l_opy_ (u"ࠨࡽࢀࠫ↪")))
            capabilities = bstack1l11lllll_opy_.bstack1llll1111111_opy_(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ↫")][bstack11111l_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ↬")][bstack11111l_opy_ (u"ࠫࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪ↭")], bstack11111l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ↮"), bstack11111l_opy_ (u"࠭ࡶࡢ࡮ࡸࡩࠬ↯"))
            bstack1lll1lll1lll_opy_ = capabilities[bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡔࡰ࡭ࡨࡲࠬ↰")]
            os.environ[bstack11111l_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭↱")] = bstack1lll1lll1lll_opy_
            if bstack11111l_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶࡨࠦ↲") in bstack11l1l1l11l_opy_ and bstack11l1l1l11l_opy_.get(bstack11111l_opy_ (u"ࠥࡥࡵࡶ࡟ࡢࡷࡷࡳࡲࡧࡴࡦࠤ↳")) is None:
                parsed[bstack11111l_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬ↴")] = capabilities[bstack11111l_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭↵")]
            os.environ[bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ↶")] = json.dumps(parsed)
            scripts = bstack1l11lllll_opy_.bstack1llll1111111_opy_(bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ↷")][bstack11111l_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩ↸")][bstack11111l_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪ↹")], bstack11111l_opy_ (u"ࠪࡲࡦࡳࡥࠨ↺"), bstack11111l_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࠬ↻"))
            bstack11ll11111_opy_.bstack1lllll1ll1_opy_(scripts)
            commands = bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ↼")][bstack11111l_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧ↽")][bstack11111l_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࡴࡖࡲ࡛ࡷࡧࡰࠨ↾")].get(bstack11111l_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࠪ↿"))
            bstack11ll11111_opy_.bstack11ll1l111ll_opy_(commands)
            bstack11ll111l111_opy_ = capabilities.get(bstack11111l_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ⇀"))
            bstack11ll11111_opy_.bstack11l1llll111_opy_(bstack11ll111l111_opy_)
            bstack11ll11111_opy_.store()
        return [bstack1lll1lll1lll_opy_, bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ⇁")]]
    @classmethod
    def bstack1llll1111l11_opy_(cls, response=None):
        os.environ[bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ⇂")] = bstack11111l_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ⇃")
        os.environ[bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⇄")] = bstack11111l_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ⇅")
        os.environ[bstack11111l_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡈࡕࡍࡑࡎࡈࡘࡊࡊࠧ⇆")] = bstack11111l_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ⇇")
        os.environ[bstack11111l_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩ⇈")] = bstack11111l_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ⇉")
        os.environ[bstack11111l_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡄࡐࡑࡕࡗࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࡘ࠭⇊")] = bstack11111l_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦ⇋")
        cls.bstack1lll1lll1l11_opy_(response, bstack11111l_opy_ (u"ࠢࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠢ⇌"))
        return [None, None, None]
    @classmethod
    def bstack1llll111l111_opy_(cls, response=None):
        os.environ[bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭⇍")] = bstack11111l_opy_ (u"ࠩࡱࡹࡱࡲࠧ⇎")
        os.environ[bstack11111l_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ⇏")] = bstack11111l_opy_ (u"ࠫࡳࡻ࡬࡭ࠩ⇐")
        os.environ[bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⇑")] = bstack11111l_opy_ (u"࠭࡮ࡶ࡮࡯ࠫ⇒")
        cls.bstack1lll1lll1l11_opy_(response, bstack11111l_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠢ⇓"))
        return [None, None, None]
    @classmethod
    def bstack1llll1111lll_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ⇔")] = jwt
        os.environ[bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ⇕")] = build_hashed_id
    @classmethod
    def bstack1lll1lll1l11_opy_(cls, response=None, product=bstack11111l_opy_ (u"ࠥࠦ⇖")):
        if response == None or response.get(bstack11111l_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫ⇗")) == None:
            logger.error(product + bstack11111l_opy_ (u"ࠧࠦࡂࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠢ⇘"))
            return
        for error in response[bstack11111l_opy_ (u"࠭ࡥࡳࡴࡲࡶࡸ࠭⇙")]:
            bstack111lll11111_opy_ = error[bstack11111l_opy_ (u"ࠧ࡬ࡧࡼࠫ⇚")]
            error_message = error[bstack11111l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⇛")]
            if error_message:
                if bstack111lll11111_opy_ == bstack11111l_opy_ (u"ࠤࡈࡖࡗࡕࡒࡠࡃࡆࡇࡊ࡙ࡓࡠࡆࡈࡒࡎࡋࡄࠣ⇜"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack11111l_opy_ (u"ࠥࡈࡦࡺࡡࠡࡷࡳࡰࡴࡧࡤࠡࡶࡲࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࠦ⇝") + product + bstack11111l_opy_ (u"ࠦࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡪࡵࡦࠢࡷࡳࠥࡹ࡯࡮ࡧࠣࡩࡷࡸ࡯ࡳࠤ⇞"))
    @classmethod
    def bstack1lll1ll1llll_opy_(cls):
        if cls.bstack1llll1lllll1_opy_ is not None:
            return
        cls.bstack1llll1lllll1_opy_ = bstack1lllll1111ll_opy_(cls.bstack1lll1lll111l_opy_)
        cls.bstack1llll1lllll1_opy_.start()
    @classmethod
    def bstack1111lllll1_opy_(cls):
        if cls.bstack1llll1lllll1_opy_ is None:
            return
        cls.bstack1llll1lllll1_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1lll111l_opy_(cls, bstack1111l1ll11_opy_, event_url=bstack11111l_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫ⇟")):
        config = {
            bstack11111l_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧ⇠"): cls.default_headers()
        }
        logger.debug(bstack11111l_opy_ (u"ࠢࡱࡱࡶࡸࡤࡪࡡࡵࡣ࠽ࠤࡘ࡫࡮ࡥ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡸࡴࠦࡴࡦࡵࡷ࡬ࡺࡨࠠࡧࡱࡵࠤࡪࡼࡥ࡯ࡶࡶࠤࢀࢃࠢ⇡").format(bstack11111l_opy_ (u"ࠨ࠮ࠣࠫ⇢").join([event[bstack11111l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭⇣")] for event in bstack1111l1ll11_opy_])))
        response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"ࠪࡔࡔ࡙ࡔࠨ⇤"), cls.request_url(event_url), bstack1111l1ll11_opy_, config)
        bstack11ll11ll111_opy_ = response.json()
    @classmethod
    def bstack1ll1l1llll_opy_(cls, bstack1111l1ll11_opy_, event_url=bstack11111l_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡧࡧࡴࡤࡪࠪ⇥")):
        logger.debug(bstack11111l_opy_ (u"ࠧࡹࡥ࡯ࡦࡢࡨࡦࡺࡡ࠻ࠢࡄࡸࡹ࡫࡭ࡱࡶ࡬ࡲ࡬ࠦࡴࡰࠢࡤࡨࡩࠦࡤࡢࡶࡤࠤࡹࡵࠠࡣࡣࡷࡧ࡭ࠦࡷࡪࡶ࡫ࠤࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥ࠻ࠢࡾࢁࠧ⇦").format(bstack1111l1ll11_opy_[bstack11111l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ⇧")]))
        if not bstack1l11lllll_opy_.bstack1lll1lll11ll_opy_(bstack1111l1ll11_opy_[bstack11111l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⇨")]):
            logger.debug(bstack11111l_opy_ (u"ࠣࡵࡨࡲࡩࡥࡤࡢࡶࡤ࠾ࠥࡔ࡯ࡵࠢࡤࡨࡩ࡯࡮ࡨࠢࡧࡥࡹࡧࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ⇩").format(bstack1111l1ll11_opy_[bstack11111l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭⇪")]))
            return
        bstack1ll11ll11l_opy_ = bstack1l11lllll_opy_.bstack1llll111111l_opy_(bstack1111l1ll11_opy_[bstack11111l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⇫")], bstack1111l1ll11_opy_.get(bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳ࠭⇬")))
        if bstack1ll11ll11l_opy_ != None:
            if bstack1111l1ll11_opy_.get(bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ⇭")) != None:
                bstack1111l1ll11_opy_[bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ⇮")][bstack11111l_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࡠ࡯ࡤࡴࠬ⇯")] = bstack1ll11ll11l_opy_
            else:
                bstack1111l1ll11_opy_[bstack11111l_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭⇰")] = bstack1ll11ll11l_opy_
        if event_url == bstack11111l_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨ⇱"):
            cls.bstack1lll1ll1llll_opy_()
            logger.debug(bstack11111l_opy_ (u"ࠥࡷࡪࡴࡤࡠࡦࡤࡸࡦࡀࠠࡂࡦࡧ࡭ࡳ࡭ࠠࡥࡣࡷࡥࠥࡺ࡯ࠡࡤࡤࡸࡨ࡮ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ⇲").format(bstack1111l1ll11_opy_[bstack11111l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⇳")]))
            cls.bstack1llll1lllll1_opy_.add(bstack1111l1ll11_opy_)
        elif event_url == bstack11111l_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪ⇴"):
            cls.bstack1lll1lll111l_opy_([bstack1111l1ll11_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack1l111111l_opy_(cls, logs):
        for log in logs:
            bstack1lll1lll1ll1_opy_ = {
                bstack11111l_opy_ (u"࠭࡫ࡪࡰࡧࠫ⇵"): bstack11111l_opy_ (u"ࠧࡕࡇࡖࡘࡤࡒࡏࡈࠩ⇶"),
                bstack11111l_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ⇷"): log[bstack11111l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ⇸")],
                bstack11111l_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭⇹"): log[bstack11111l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ⇺")],
                bstack11111l_opy_ (u"ࠬ࡮ࡴࡵࡲࡢࡶࡪࡹࡰࡰࡰࡶࡩࠬ⇻"): {},
                bstack11111l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⇼"): log[bstack11111l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⇽")],
            }
            if bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⇾") in log:
                bstack1lll1lll1ll1_opy_[bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⇿")] = log[bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ∀")]
            elif bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ∁") in log:
                bstack1lll1lll1ll1_opy_[bstack11111l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ∂")] = log[bstack11111l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭∃")]
            cls.bstack1ll1l1llll_opy_({
                bstack11111l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ∄"): bstack11111l_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬ∅"),
                bstack11111l_opy_ (u"ࠩ࡯ࡳ࡬ࡹࠧ∆"): [bstack1lll1lll1ll1_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1lllll11_opy_(cls, steps):
        bstack1llll1111ll1_opy_ = []
        for step in steps:
            bstack1lll1lll1l1l_opy_ = {
                bstack11111l_opy_ (u"ࠪ࡯࡮ࡴࡤࠨ∇"): bstack11111l_opy_ (u"࡙ࠫࡋࡓࡕࡡࡖࡘࡊࡖࠧ∈"),
                bstack11111l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ∉"): step[bstack11111l_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ∊")],
                bstack11111l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ∋"): step[bstack11111l_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ∌")],
                bstack11111l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ∍"): step[bstack11111l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ∎")],
                bstack11111l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭∏"): step[bstack11111l_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧ∐")]
            }
            if bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭∑") in step:
                bstack1lll1lll1l1l_opy_[bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ−")] = step[bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ∓")]
            elif bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ∔") in step:
                bstack1lll1lll1l1l_opy_[bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ∕")] = step[bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ∖")]
            bstack1llll1111ll1_opy_.append(bstack1lll1lll1l1l_opy_)
        cls.bstack1ll1l1llll_opy_({
            bstack11111l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ∗"): bstack11111l_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪ∘"),
            bstack11111l_opy_ (u"ࠧ࡭ࡱࡪࡷࠬ∙"): bstack1llll1111ll1_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack1l1l111l1_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l11l11l1l_opy_(cls, screenshot):
        cls.bstack1ll1l1llll_opy_({
            bstack11111l_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ√"): bstack11111l_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭∛"),
            bstack11111l_opy_ (u"ࠪࡰࡴ࡭ࡳࠨ∜"): [{
                bstack11111l_opy_ (u"ࠫࡰ࡯࡮ࡥࠩ∝"): bstack11111l_opy_ (u"࡚ࠬࡅࡔࡖࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࠧ∞"),
                bstack11111l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ∟"): datetime.datetime.utcnow().isoformat() + bstack11111l_opy_ (u"࡛ࠧࠩ∠"),
                bstack11111l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ∡"): screenshot[bstack11111l_opy_ (u"ࠩ࡬ࡱࡦ࡭ࡥࠨ∢")],
                bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ∣"): screenshot[bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ∤")]
            }]
        }, event_url=bstack11111l_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪ∥"))
    @classmethod
    @error_handler(class_method=True)
    def bstack1l111l1ll_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1ll1l1llll_opy_({
            bstack11111l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ∦"): bstack11111l_opy_ (u"ࠧࡄࡄࡗࡗࡪࡹࡳࡪࡱࡱࡇࡷ࡫ࡡࡵࡧࡧࠫ∧"),
            bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ∨"): {
                bstack11111l_opy_ (u"ࠤࡸࡹ࡮ࡪࠢ∩"): cls.current_test_uuid(),
                bstack11111l_opy_ (u"ࠥ࡭ࡳࡺࡥࡨࡴࡤࡸ࡮ࡵ࡮ࡴࠤ∪"): cls.bstack111l1l1l1l_opy_(driver)
            }
        })
    @classmethod
    def bstack111l1ll11l_opy_(cls, event: str, bstack1111l1ll11_opy_: bstack1111ll1l1l_opy_):
        bstack1111ll1lll_opy_ = {
            bstack11111l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ∫"): event,
            bstack1111l1ll11_opy_.bstack1111ll11l1_opy_(): bstack1111l1ll11_opy_.bstack111l11l1ll_opy_(event)
        }
        cls.bstack1ll1l1llll_opy_(bstack1111ll1lll_opy_)
        result = getattr(bstack1111l1ll11_opy_, bstack11111l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ∬"), None)
        if event == bstack11111l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ∭"):
            threading.current_thread().bstackTestMeta = {bstack11111l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ∮"): bstack11111l_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩ∯")}
        elif event == bstack11111l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ∰"):
            threading.current_thread().bstackTestMeta = {bstack11111l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ∱"): getattr(result, bstack11111l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ∲"), bstack11111l_opy_ (u"ࠬ࠭∳"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ∴"), None) is None or os.environ[bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ∵")] == bstack11111l_opy_ (u"ࠣࡰࡸࡰࡱࠨ∶")) and (os.environ.get(bstack11111l_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ∷"), None) is None or os.environ[bstack11111l_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ∸")] == bstack11111l_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ∹")):
            return False
        return True
    @staticmethod
    def bstack1lll1llll11l_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11l1ll1l1l_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack11111l_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫ∺"): bstack11111l_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩ∻"),
            bstack11111l_opy_ (u"࡙ࠧ࠯ࡅࡗ࡙ࡇࡃࡌ࠯ࡗࡉࡘ࡚ࡏࡑࡕࠪ∼"): bstack11111l_opy_ (u"ࠨࡶࡵࡹࡪ࠭∽")
        }
        if os.environ.get(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭∾"), None):
            headers[bstack11111l_opy_ (u"ࠪࡅࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪ∿")] = bstack11111l_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࢀࢃࠧ≀").format(os.environ[bstack11111l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠤ≁")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack11111l_opy_ (u"࠭ࡻࡾ࠱ࡾࢁࠬ≂").format(bstack1lll1lll1111_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack11111l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ≃"), None)
    @staticmethod
    def bstack111l1l1l1l_opy_(driver):
        return {
            bstack111lll11l1l_opy_(): bstack11l11111lll_opy_(driver)
        }
    @staticmethod
    def bstack1lll1lllll1l_opy_(exception_info, report):
        return [{bstack11111l_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫ≄"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1llllll1111_opy_(typename):
        if bstack11111l_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࠧ≅") in typename:
            return bstack11111l_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࡋࡲࡳࡱࡵࠦ≆")
        return bstack11111l_opy_ (u"࡚ࠦࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠧ≇")