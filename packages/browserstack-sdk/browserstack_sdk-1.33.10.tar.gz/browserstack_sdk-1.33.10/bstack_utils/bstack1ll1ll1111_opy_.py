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
import tempfile
import math
from bstack_utils import bstack1l1llll1_opy_
from bstack_utils.constants import bstack111111111_opy_, bstack11l1l1l1111_opy_
from bstack_utils.helper import bstack111lllllll1_opy_, get_host_info
from bstack_utils.bstack11l1lll11ll_opy_ import bstack11l1ll1lll1_opy_
import json
import re
import sys
bstack1111l11ll1l_opy_ = bstack11111l_opy_ (u"ࠥࡶࡪࡺࡲࡺࡖࡨࡷࡹࡹࡏ࡯ࡈࡤ࡭ࡱࡻࡲࡦࠤỆ")
bstack1111ll11l1l_opy_ = bstack11111l_opy_ (u"ࠦࡦࡨ࡯ࡳࡶࡅࡹ࡮ࡲࡤࡐࡰࡉࡥ࡮ࡲࡵࡳࡧࠥệ")
bstack1111ll1ll1l_opy_ = bstack11111l_opy_ (u"ࠧࡸࡵ࡯ࡒࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡋࡧࡩ࡭ࡧࡧࡊ࡮ࡸࡳࡵࠤỈ")
bstack1111ll1llll_opy_ = bstack11111l_opy_ (u"ࠨࡲࡦࡴࡸࡲࡕࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡇࡣ࡬ࡰࡪࡪࠢỉ")
bstack1111ll11111_opy_ = bstack11111l_opy_ (u"ࠢࡴ࡭࡬ࡴࡋࡲࡡ࡬ࡻࡤࡲࡩࡌࡡࡪ࡮ࡨࡨࠧỊ")
bstack1111lll111l_opy_ = bstack11111l_opy_ (u"ࠣࡴࡸࡲࡘࡳࡡࡳࡶࡖࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠧị")
bstack1111l111l1l_opy_ = {
    bstack1111l11ll1l_opy_,
    bstack1111ll11l1l_opy_,
    bstack1111ll1ll1l_opy_,
    bstack1111ll1llll_opy_,
    bstack1111ll11111_opy_,
    bstack1111lll111l_opy_
}
bstack1111ll111l1_opy_ = {bstack11111l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩỌ")}
logger = bstack1l1llll1_opy_.get_logger(__name__, bstack111111111_opy_)
class bstack11111llll11_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack1111ll1l1ll_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack1l11ll1111_opy_:
    _1ll1lll1ll1_opy_ = None
    def __init__(self, config):
        self.bstack1111l11ll11_opy_ = False
        self.bstack1111l1l1l11_opy_ = False
        self.bstack1111l1111ll_opy_ = False
        self.bstack1111ll11ll1_opy_ = False
        self.bstack1111l1l111l_opy_ = None
        self.bstack1111l1l1ll1_opy_ = bstack11111llll11_opy_()
        self.bstack1111l11l111_opy_ = None
        opts = config.get(bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧọ"), {})
        self.bstack1111l111l11_opy_ = config.get(bstack11111l_opy_ (u"ࠫࡸࡳࡡࡳࡶࡖࡩࡱ࡫ࡣࡵ࡫ࡲࡲࡋ࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࡩࡸࡋࡎࡗࠩỎ"), bstack11111l_opy_ (u"ࠧࠨỏ"))
        self.bstack1111l1ll1ll_opy_ = config.get(bstack11111l_opy_ (u"࠭ࡳ࡮ࡣࡵࡸࡘ࡫࡬ࡦࡥࡷ࡭ࡴࡴࡆࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࡫ࡳࡄࡎࡌࠫỐ"), bstack11111l_opy_ (u"ࠢࠣố"))
        bstack1111l1ll111_opy_ = opts.get(bstack1111lll111l_opy_, {})
        bstack1111l1ll11l_opy_ = None
        if bstack11111l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨỒ") in bstack1111l1ll111_opy_:
            bstack1111l1ll1l1_opy_ = bstack1111l1ll111_opy_[bstack11111l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩồ")]
            if bstack1111l1ll1l1_opy_ is None or (isinstance(bstack1111l1ll1l1_opy_, str) and bstack1111l1ll1l1_opy_.strip() == bstack11111l_opy_ (u"ࠪࠫỔ")) or (isinstance(bstack1111l1ll1l1_opy_, list) and len(bstack1111l1ll1l1_opy_) == 0):
                bstack1111l1ll11l_opy_ = []
            elif isinstance(bstack1111l1ll1l1_opy_, list):
                bstack1111l1ll11l_opy_ = bstack1111l1ll1l1_opy_
            elif isinstance(bstack1111l1ll1l1_opy_, str) and bstack1111l1ll1l1_opy_.strip():
                bstack1111l1ll11l_opy_ = bstack1111l1ll1l1_opy_
            else:
                logger.warning(bstack11111l_opy_ (u"ࠦࡎࡴࡶࡢ࡮࡬ࡨࠥࡹ࡯ࡶࡴࡦࡩࠥࡼࡡ࡭ࡷࡨࠤ࡮ࡴࠠࡤࡱࡱࡪ࡮࡭࠺ࠡࡽࢀ࠲ࠥࡊࡥࡧࡣࡸࡰࡹ࡯࡮ࡨࠢࡷࡳࠥ࡫࡭ࡱࡶࡼࠤࡱ࡯ࡳࡵ࠰ࠥổ").format(bstack1111l1ll1l1_opy_))
                bstack1111l1ll11l_opy_ = []
        self.__1111l111111_opy_(
            bstack1111l1ll111_opy_.get(bstack11111l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ỗ"), False),
            bstack1111l1ll111_opy_.get(bstack11111l_opy_ (u"࠭࡭ࡰࡦࡨࠫỗ"), bstack11111l_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧỘ")),
            bstack1111l1ll11l_opy_
        )
        self.__1111ll1111l_opy_(opts.get(bstack1111ll1ll1l_opy_, False))
        self.__1111ll1ll11_opy_(opts.get(bstack1111ll1llll_opy_, False))
        self.__1111ll1lll1_opy_(opts.get(bstack1111ll11111_opy_, False))
    @classmethod
    def bstack1llll1lll_opy_(cls, config=None):
        if cls._1ll1lll1ll1_opy_ is None and config is not None:
            cls._1ll1lll1ll1_opy_ = bstack1l11ll1111_opy_(config)
        return cls._1ll1lll1ll1_opy_
    @staticmethod
    def bstack1l1l1l1l11_opy_(config: dict) -> bool:
        bstack11111lllll1_opy_ = config.get(bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬộ"), {}).get(bstack1111l11ll1l_opy_, {})
        return bstack11111lllll1_opy_.get(bstack11111l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪỚ"), False)
    @staticmethod
    def bstack111lll111_opy_(config: dict) -> int:
        bstack11111lllll1_opy_ = config.get(bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧớ"), {}).get(bstack1111l11ll1l_opy_, {})
        retries = 0
        if bstack1l11ll1111_opy_.bstack1l1l1l1l11_opy_(config):
            retries = bstack11111lllll1_opy_.get(bstack11111l_opy_ (u"ࠫࡲࡧࡸࡓࡧࡷࡶ࡮࡫ࡳࠨỜ"), 1)
        return retries
    @staticmethod
    def bstack1l1l1lll11_opy_(config: dict) -> dict:
        bstack1111l1l11ll_opy_ = config.get(bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩờ"), {})
        return {
            key: value for key, value in bstack1111l1l11ll_opy_.items() if key in bstack1111l111l1l_opy_
        }
    @staticmethod
    def bstack1111l11lll1_opy_():
        bstack11111l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡇ࡭࡫ࡣ࡬ࠢ࡬ࡪࠥࡺࡨࡦࠢࡤࡦࡴࡸࡴࠡࡤࡸ࡭ࡱࡪࠠࡧ࡫࡯ࡩࠥ࡫ࡸࡪࡵࡷࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥỞ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠢࡢࡤࡲࡶࡹࡥࡢࡶ࡫࡯ࡨࡤࢁࡽࠣở").format(os.getenv(bstack11111l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨỠ")))))
    @staticmethod
    def bstack1111ll1l1l1_opy_(test_name: str):
        bstack11111l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡃࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡧࡢࡰࡴࡷࠤࡧࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡧࡻ࡭ࡸࡺࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨỡ")
        bstack1111ll1l111_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࡢࡸࡪࡹࡴࡴࡡࡾࢁ࠳ࡺࡸࡵࠤỢ").format(os.getenv(bstack11111l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤợ"))))
        with open(bstack1111ll1l111_opy_, bstack11111l_opy_ (u"ࠬࡧࠧỤ")) as file:
            file.write(bstack11111l_opy_ (u"ࠨࡻࡾ࡞ࡱࠦụ").format(test_name))
    @staticmethod
    def bstack1111l1lllll_opy_(framework: str) -> bool:
       return framework.lower() in bstack1111ll111l1_opy_
    @staticmethod
    def bstack11l11l11l1l_opy_(config: dict) -> bool:
        bstack1111l1lll1l_opy_ = config.get(bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫỦ"), {}).get(bstack1111ll11l1l_opy_, {})
        return bstack1111l1lll1l_opy_.get(bstack11111l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩủ"), False)
    @staticmethod
    def bstack11l11l1ll1l_opy_(config: dict, bstack11l11ll1lll_opy_: int = 0) -> int:
        bstack11111l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡇࡦࡶࠣࡸ࡭࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥࠡࡶ࡫ࡶࡪࡹࡨࡰ࡮ࡧ࠰ࠥࡽࡨࡪࡥ࡫ࠤࡨࡧ࡮ࠡࡤࡨࠤࡦࡴࠠࡢࡤࡶࡳࡱࡻࡴࡦࠢࡱࡹࡲࡨࡥࡳࠢࡲࡶࠥࡧࠠࡱࡧࡵࡧࡪࡴࡴࡢࡩࡨ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡧࡴࡴࡦࡪࡩࠣࠬࡩ࡯ࡣࡵࠫ࠽ࠤ࡙࡮ࡥࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡹࡵࡴࡢ࡮ࡢࡸࡪࡹࡴࡴࠢࠫ࡭ࡳࡺࠩ࠻ࠢࡗ࡬ࡪࠦࡴࡰࡶࡤࡰࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࠩࡴࡨࡵࡺ࡯ࡲࡦࡦࠣࡪࡴࡸࠠࡱࡧࡵࡧࡪࡴࡴࡢࡩࡨ࠱ࡧࡧࡳࡦࡦࠣࡸ࡭ࡸࡥࡴࡪࡲࡰࡩࡹࠩ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡭ࡳࡺ࠺ࠡࡖ࡫ࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢỨ")
        bstack1111l1lll1l_opy_ = config.get(bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧứ"), {}).get(bstack11111l_opy_ (u"ࠫࡦࡨ࡯ࡳࡶࡅࡹ࡮ࡲࡤࡐࡰࡉࡥ࡮ࡲࡵࡳࡧࠪỪ"), {})
        bstack1111l11111l_opy_ = 0
        bstack1111l1llll1_opy_ = 0
        if bstack1l11ll1111_opy_.bstack11l11l11l1l_opy_(config):
            bstack1111l1llll1_opy_ = bstack1111l1lll1l_opy_.get(bstack11111l_opy_ (u"ࠬࡳࡡࡹࡈࡤ࡭ࡱࡻࡲࡦࡵࠪừ"), 5)
            if isinstance(bstack1111l1llll1_opy_, str) and bstack1111l1llll1_opy_.endswith(bstack11111l_opy_ (u"࠭ࠥࠨỬ")):
                try:
                    percentage = int(bstack1111l1llll1_opy_.strip(bstack11111l_opy_ (u"ࠧࠦࠩử")))
                    if bstack11l11ll1lll_opy_ > 0:
                        bstack1111l11111l_opy_ = math.ceil((percentage * bstack11l11ll1lll_opy_) / 100)
                    else:
                        raise ValueError(bstack11111l_opy_ (u"ࠣࡖࡲࡸࡦࡲࠠࡵࡧࡶࡸࡸࠦ࡭ࡶࡵࡷࠤࡧ࡫ࠠࡱࡴࡲࡺ࡮ࡪࡥࡥࠢࡩࡳࡷࠦࡰࡦࡴࡦࡩࡳࡺࡡࡨࡧ࠰ࡦࡦࡹࡥࡥࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࡸ࠴ࠢỮ"))
                except ValueError as e:
                    raise ValueError(bstack11111l_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫ࠠࡷࡣ࡯ࡹࡪࠦࡦࡰࡴࠣࡱࡦࡾࡆࡢ࡫࡯ࡹࡷ࡫ࡳ࠻ࠢࡾࢁࠧữ").format(bstack1111l1llll1_opy_)) from e
            else:
                bstack1111l11111l_opy_ = int(bstack1111l1llll1_opy_)
        logger.info(bstack11111l_opy_ (u"ࠥࡑࡦࡾࠠࡧࡣ࡬ࡰࡺࡸࡥࡴࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࠥࡹࡥࡵࠢࡷࡳ࠿ࠦࡻࡾࠢࠫࡪࡷࡵ࡭ࠡࡥࡲࡲ࡫࡯ࡧ࠻ࠢࡾࢁ࠮ࠨỰ").format(bstack1111l11111l_opy_, bstack1111l1llll1_opy_))
        return bstack1111l11111l_opy_
    def bstack11111llllll_opy_(self):
        return self.bstack1111ll11ll1_opy_
    def bstack1111l1l1lll_opy_(self):
        return self.bstack1111l1l111l_opy_
    def bstack1111l1l1111_opy_(self):
        return self.bstack1111l11l111_opy_
    def __1111l111111_opy_(self, enabled, mode, source=None):
        try:
            self.bstack1111ll11ll1_opy_ = bool(enabled)
            if mode not in [bstack11111l_opy_ (u"ࠫࡷ࡫࡬ࡦࡸࡤࡲࡹࡌࡩࡳࡵࡷࠫự"), bstack11111l_opy_ (u"ࠬࡸࡥ࡭ࡧࡹࡥࡳࡺࡏ࡯࡮ࡼࠫỲ")]:
                logger.warning(bstack11111l_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡴ࡯ࡤࡶࡹࠦࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠢࡰࡳࡩ࡫ࠠࠨࡽࢀࠫࠥࡶࡲࡰࡸ࡬ࡨࡪࡪ࠮ࠡࡆࡨࡪࡦࡻ࡬ࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࠩࡵࡩࡱ࡫ࡶࡢࡰࡷࡊ࡮ࡸࡳࡵࠩ࠱ࠦỳ").format(mode))
                mode = bstack11111l_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧỴ")
            self.bstack1111l1l111l_opy_ = mode
            self.bstack1111l11l111_opy_ = []
            if source is None:
                self.bstack1111l11l111_opy_ = None
            elif isinstance(source, list):
                self.bstack1111l11l111_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack11111l_opy_ (u"ࠨ࠰࡭ࡷࡴࡴࠧỵ")):
                self.bstack1111l11l111_opy_ = self._11111lll11l_opy_(source)
            self.__1111ll1l11l_opy_()
        except Exception as e:
            logger.error(bstack11111l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡶࡱࡦࡸࡴࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࠲ࠦࡥ࡯ࡣࡥࡰࡪࡪ࠺ࠡࡽࢀ࠰ࠥࡳ࡯ࡥࡧ࠽ࠤࢀࢃࠬࠡࡵࡲࡹࡷࡩࡥ࠻ࠢࡾࢁ࠳ࠦࡅࡳࡴࡲࡶ࠿ࠦࡻࡾࠤỶ").format(enabled, mode, source, e))
    def bstack1111l11l1l1_opy_(self):
        return self.bstack1111l11ll11_opy_
    def __1111ll1111l_opy_(self, value):
        self.bstack1111l11ll11_opy_ = bool(value)
        self.__1111ll1l11l_opy_()
    def bstack1111l1lll11_opy_(self):
        return self.bstack1111l1l1l11_opy_
    def __1111ll1ll11_opy_(self, value):
        self.bstack1111l1l1l11_opy_ = bool(value)
        self.__1111ll1l11l_opy_()
    def bstack1111l111lll_opy_(self):
        return self.bstack1111l1111ll_opy_
    def __1111ll1lll1_opy_(self, value):
        self.bstack1111l1111ll_opy_ = bool(value)
        self.__1111ll1l11l_opy_()
    def __1111ll1l11l_opy_(self):
        if self.bstack1111ll11ll1_opy_:
            self.bstack1111l11ll11_opy_ = False
            self.bstack1111l1l1l11_opy_ = False
            self.bstack1111l1111ll_opy_ = False
            self.bstack1111l1l1ll1_opy_.enable(bstack1111lll111l_opy_)
        elif self.bstack1111l11ll11_opy_:
            self.bstack1111l1l1l11_opy_ = False
            self.bstack1111l1111ll_opy_ = False
            self.bstack1111ll11ll1_opy_ = False
            self.bstack1111l1l1ll1_opy_.enable(bstack1111ll1ll1l_opy_)
        elif self.bstack1111l1l1l11_opy_:
            self.bstack1111l11ll11_opy_ = False
            self.bstack1111l1111ll_opy_ = False
            self.bstack1111ll11ll1_opy_ = False
            self.bstack1111l1l1ll1_opy_.enable(bstack1111ll1llll_opy_)
        elif self.bstack1111l1111ll_opy_:
            self.bstack1111l11ll11_opy_ = False
            self.bstack1111l1l1l11_opy_ = False
            self.bstack1111ll11ll1_opy_ = False
            self.bstack1111l1l1ll1_opy_.enable(bstack1111ll11111_opy_)
        else:
            self.bstack1111l1l1ll1_opy_.disable()
    def bstack11ll1111_opy_(self):
        return self.bstack1111l1l1ll1_opy_.bstack1111ll1l1ll_opy_()
    def bstack11l111l11l_opy_(self):
        if self.bstack1111l1l1ll1_opy_.bstack1111ll1l1ll_opy_():
            return self.bstack1111l1l1ll1_opy_.get_name()
        return None
    def _11111lll11l_opy_(self, bstack1111l1111l1_opy_):
        bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡣࡵࡷࡪࠦࡊࡔࡑࡑࠤࡸࡵࡵࡳࡥࡨࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫࡯࡬ࡦࠢࡤࡲࡩࠦࡦࡰࡴࡰࡥࡹࠦࡩࡵࠢࡩࡳࡷࠦࡳ࡮ࡣࡵࡸࠥࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡴࡱࡸࡶࡨ࡫࡟ࡧ࡫࡯ࡩࡤࡶࡡࡵࡪࠣࠬࡸࡺࡲࠪ࠼ࠣࡔࡦࡺࡨࠡࡶࡲࠤࡹ࡮ࡥࠡࡌࡖࡓࡓࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡦࡪ࡮ࡨࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡲࡩࡴࡶ࠽ࠤࡋࡵࡲ࡮ࡣࡷࡸࡪࡪࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡴࡨࡴࡴࡹࡩࡵࡱࡵࡽࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࡸࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥỷ")
        if not os.path.isfile(bstack1111l1111l1_opy_):
            logger.error(bstack11111l_opy_ (u"ࠦࡘࡵࡵࡳࡥࡨࠤ࡫࡯࡬ࡦࠢࠪࡿࢂ࠭ࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴ࠯ࠤỸ").format(bstack1111l1111l1_opy_))
            return []
        data = None
        try:
            with open(bstack1111l1111l1_opy_, bstack11111l_opy_ (u"ࠧࡸࠢỹ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack11111l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡊࡔࡑࡑࠤ࡫ࡸ࡯࡮ࠢࡶࡳࡺࡸࡣࡦࠢࡩ࡭ࡱ࡫ࠠࠨࡽࢀࠫ࠿ࠦࡻࡾࠤỺ").format(bstack1111l1111l1_opy_, e))
            return []
        _1111l11llll_opy_ = None
        _11111lll1ll_opy_ = None
        def _1111l1l11l1_opy_():
            bstack11111lll1l1_opy_ = {}
            bstack1111l1l1l1l_opy_ = {}
            try:
                if self.bstack1111l111l11_opy_.startswith(bstack11111l_opy_ (u"ࠧࡼࠩỻ")) and self.bstack1111l111l11_opy_.endswith(bstack11111l_opy_ (u"ࠨࡿࠪỼ")):
                    bstack11111lll1l1_opy_ = json.loads(self.bstack1111l111l11_opy_)
                else:
                    bstack11111lll1l1_opy_ = dict(item.split(bstack11111l_opy_ (u"ࠩ࠽ࠫỽ")) for item in self.bstack1111l111l11_opy_.split(bstack11111l_opy_ (u"ࠪ࠰ࠬỾ")) if bstack11111l_opy_ (u"ࠫ࠿࠭ỿ") in item) if self.bstack1111l111l11_opy_ else {}
                if self.bstack1111l1ll1ll_opy_.startswith(bstack11111l_opy_ (u"ࠬࢁࠧἀ")) and self.bstack1111l1ll1ll_opy_.endswith(bstack11111l_opy_ (u"࠭ࡽࠨἁ")):
                    bstack1111l1l1l1l_opy_ = json.loads(self.bstack1111l1ll1ll_opy_)
                else:
                    bstack1111l1l1l1l_opy_ = dict(item.split(bstack11111l_opy_ (u"ࠧ࠻ࠩἂ")) for item in self.bstack1111l1ll1ll_opy_.split(bstack11111l_opy_ (u"ࠨ࠮ࠪἃ")) if bstack11111l_opy_ (u"ࠩ࠽ࠫἄ") in item) if self.bstack1111l1ll1ll_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack11111l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡳࡥࡷࡹࡩ࡯ࡩࠣࡪࡪࡧࡴࡶࡴࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤࡲࡧࡰࡱ࡫ࡱ࡫ࡸࡀࠠࡼࡿࠥἅ").format(e))
            logger.debug(bstack11111l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡳࡡࡱࡲ࡬ࡲ࡬ࡹࠠࡧࡴࡲࡱࠥ࡫࡮ࡷ࠼ࠣࡿࢂ࠲ࠠࡄࡎࡌ࠾ࠥࢁࡽࠣἆ").format(bstack11111lll1l1_opy_, bstack1111l1l1l1l_opy_))
            return bstack11111lll1l1_opy_, bstack1111l1l1l1l_opy_
        if _1111l11llll_opy_ is None or _11111lll1ll_opy_ is None:
            _1111l11llll_opy_, _11111lll1ll_opy_ = _1111l1l11l1_opy_()
        def bstack1111lll1111_opy_(name, bstack1111ll11l11_opy_):
            if name in _11111lll1ll_opy_:
                return _11111lll1ll_opy_[name]
            if name in _1111l11llll_opy_:
                return _1111l11llll_opy_[name]
            if bstack1111ll11l11_opy_.get(bstack11111l_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠬἇ")):
                return bstack1111ll11l11_opy_[bstack11111l_opy_ (u"࠭ࡦࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࠭Ἀ")]
            return None
        if isinstance(data, dict):
            bstack1111l11l11l_opy_ = []
            bstack11111llll1l_opy_ = re.compile(bstack11111l_opy_ (u"ࡲࠨࡠ࡞ࡅ࠲ࡠ࠰࠮࠻ࡢࡡ࠰ࠪࠧἉ"))
            for name, bstack1111ll11l11_opy_ in data.items():
                if not isinstance(bstack1111ll11l11_opy_, dict):
                    continue
                url = bstack1111ll11l11_opy_.get(bstack11111l_opy_ (u"ࠨࡷࡵࡰࠬἊ"))
                if url is None or (isinstance(url, str) and url.strip() == bstack11111l_opy_ (u"ࠩࠪἋ")):
                    logger.warning(bstack11111l_opy_ (u"ࠥࡖࡪࡶ࡯ࡴ࡫ࡷࡳࡷࡿࠠࡖࡔࡏࠤ࡮ࡹࠠ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡨࡲࡶࠥࡹ࡯ࡶࡴࡦࡩࠥ࠭ࡻࡾࠩ࠽ࠤࢀࢃࠢἌ").format(name, bstack1111ll11l11_opy_))
                    continue
                if not bstack11111llll1l_opy_.match(name):
                    logger.warning(bstack11111l_opy_ (u"ࠦࡎࡴࡶࡢ࡮࡬ࡨࠥࡹ࡯ࡶࡴࡦࡩࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠢࡩࡳࡷࡳࡡࡵࠢࡩࡳࡷࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣἍ").format(name, bstack1111ll11l11_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack11111l_opy_ (u"࡙ࠧ࡯ࡶࡴࡦࡩࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠢࠪࡿࢂ࠭ࠠ࡮ࡷࡶࡸࠥ࡮ࡡࡷࡧࠣࡥࠥࡲࡥ࡯ࡩࡷ࡬ࠥࡨࡥࡵࡹࡨࡩࡳࠦ࠱ࠡࡣࡱࡨࠥ࠹࠰ࠡࡥ࡫ࡥࡷࡧࡣࡵࡧࡵࡷ࠳ࠨἎ").format(name))
                    continue
                bstack1111ll11l11_opy_ = bstack1111ll11l11_opy_.copy()
                bstack1111ll11l11_opy_[bstack11111l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫἏ")] = name
                bstack1111ll11l11_opy_[bstack11111l_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧἐ")] = bstack1111lll1111_opy_(name, bstack1111ll11l11_opy_)
                if not bstack1111ll11l11_opy_.get(bstack11111l_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠨἑ")) or bstack1111ll11l11_opy_.get(bstack11111l_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩἒ")) == bstack11111l_opy_ (u"ࠪࠫἓ"):
                    logger.warning(bstack11111l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡴ࡯ࡵࠢࡶࡴࡪࡩࡩࡧ࡫ࡨࡨࠥ࡬࡯ࡳࠢࡶࡳࡺࡸࡣࡦࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦἔ").format(name, bstack1111ll11l11_opy_))
                    continue
                if bstack1111ll11l11_opy_.get(bstack11111l_opy_ (u"ࠬࡨࡡࡴࡧࡅࡶࡦࡴࡣࡩࠩἕ")) and bstack1111ll11l11_opy_[bstack11111l_opy_ (u"࠭ࡢࡢࡵࡨࡆࡷࡧ࡮ࡤࡪࠪ἖")] == bstack1111ll11l11_opy_[bstack11111l_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧ἗")]:
                    logger.warning(bstack11111l_opy_ (u"ࠣࡈࡨࡥࡹࡻࡲࡦࠢࡥࡶࡦࡴࡣࡩࠢࡤࡲࡩࠦࡢࡢࡵࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡵࡪࡨࠤࡸࡧ࡭ࡦࠢࡩࡳࡷࠦࡳࡰࡷࡵࡧࡪࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣἘ").format(name, bstack1111ll11l11_opy_))
                    continue
                bstack1111l11l11l_opy_.append(bstack1111ll11l11_opy_)
            return bstack1111l11l11l_opy_
        return data
    def bstack1111llll11l_opy_(self):
        data = {
            bstack11111l_opy_ (u"ࠩࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠨἙ"): {
                bstack11111l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫἚ"): self.bstack11111llllll_opy_(),
                bstack11111l_opy_ (u"ࠫࡲࡵࡤࡦࠩἛ"): self.bstack1111l1l1lll_opy_(),
                bstack11111l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬἜ"): self.bstack1111l1l1111_opy_()
            }
        }
        return data
    def bstack1111l111ll1_opy_(self, config):
        bstack1111ll111ll_opy_ = {}
        bstack1111ll111ll_opy_[bstack11111l_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬἝ")] = {
            bstack11111l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨ἞"): self.bstack11111llllll_opy_(),
            bstack11111l_opy_ (u"ࠨ࡯ࡲࡨࡪ࠭἟"): self.bstack1111l1l1lll_opy_()
        }
        bstack1111ll111ll_opy_[bstack11111l_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡲࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡤ࡬ࡡࡪ࡮ࡨࡨࠬἠ")] = {
            bstack11111l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫἡ"): self.bstack1111l1lll11_opy_()
        }
        bstack1111ll111ll_opy_[bstack11111l_opy_ (u"ࠫࡷࡻ࡮ࡠࡲࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡤ࡬ࡡࡪ࡮ࡨࡨࡤ࡬ࡩࡳࡵࡷࠫἢ")] = {
            bstack11111l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ἣ"): self.bstack1111l11l1l1_opy_()
        }
        bstack1111ll111ll_opy_[bstack11111l_opy_ (u"࠭ࡳ࡬࡫ࡳࡣ࡫ࡧࡩ࡭࡫ࡱ࡫ࡤࡧ࡮ࡥࡡࡩࡰࡦࡱࡹࠨἤ")] = {
            bstack11111l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨἥ"): self.bstack1111l111lll_opy_()
        }
        if self.bstack1l1l1l1l11_opy_(config):
            bstack1111ll111ll_opy_[bstack11111l_opy_ (u"ࠨࡴࡨࡸࡷࡿ࡟ࡵࡧࡶࡸࡸࡥ࡯࡯ࡡࡩࡥ࡮ࡲࡵࡳࡧࠪἦ")] = {
                bstack11111l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪἧ"): True,
                bstack11111l_opy_ (u"ࠪࡱࡦࡾ࡟ࡳࡧࡷࡶ࡮࡫ࡳࠨἨ"): self.bstack111lll111_opy_(config)
            }
        if self.bstack11l11l11l1l_opy_(config):
            bstack1111ll111ll_opy_[bstack11111l_opy_ (u"ࠫࡦࡨ࡯ࡳࡶࡢࡦࡺ࡯࡬ࡥࡡࡲࡲࡤ࡬ࡡࡪ࡮ࡸࡶࡪ࠭Ἡ")] = {
                bstack11111l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ἢ"): True,
                bstack11111l_opy_ (u"࠭࡭ࡢࡺࡢࡪࡦ࡯࡬ࡶࡴࡨࡷࠬἫ"): self.bstack11l11l1ll1l_opy_(config)
            }
        return bstack1111ll111ll_opy_
    def bstack1lll11l1_opy_(self, config):
        bstack11111l_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡵ࡬࡭ࡧࡦࡸࡸࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡦࡾࠦ࡭ࡢ࡭࡬ࡲ࡬ࠦࡡࠡࡥࡤࡰࡱࠦࡴࡰࠢࡷ࡬ࡪࠦࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡣࡷ࡬ࡰࡩ࠳ࡤࡢࡶࡤࠤࡪࡴࡤࡱࡱ࡬ࡲࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡺࡻࡩࡥࠢࠫࡷࡹࡸࠩ࠻ࠢࡗ࡬ࡪࠦࡕࡖࡋࡇࠤࡴ࡬ࠠࡵࡪࡨࠤࡧࡻࡩ࡭ࡦࠣࡸࡴࠦࡣࡰ࡮࡯ࡩࡨࡺࠠࡥࡣࡷࡥࠥ࡬࡯ࡳ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡩ࡯ࡣࡵ࠼ࠣࡖࡪࡹࡰࡰࡰࡶࡩࠥ࡬ࡲࡰ࡯ࠣࡸ࡭࡫ࠠࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡤࡸ࡭ࡱࡪ࠭ࡥࡣࡷࡥࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠬࠡࡱࡵࠤࡓࡵ࡮ࡦࠢ࡬ࡪࠥ࡬ࡡࡪ࡮ࡨࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥἬ")
        if not (config.get(bstack11111l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫἭ"), None) in bstack11l1l1l1111_opy_ and self.bstack11111llllll_opy_()):
            return None
        bstack1111l11l1ll_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧἮ"), None)
        logger.debug(bstack11111l_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨ࡛ࠥࡕࡊࡆ࠽ࠤࢀࢃࠢἯ").format(bstack1111l11l1ll_opy_))
        try:
            bstack11l1lll1l1l_opy_ = bstack11111l_opy_ (u"ࠦࡹ࡫ࡳࡵࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡨࡵࡪ࡮ࡧ࠱ࡩࡧࡴࡢࠤἰ").format(bstack1111l11l1ll_opy_)
            payload = {
                bstack11111l_opy_ (u"ࠧࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠥἱ"): config.get(bstack11111l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫἲ"), bstack11111l_opy_ (u"ࠧࠨἳ")),
                bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠦἴ"): config.get(bstack11111l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬἵ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡔࡸࡲࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣἶ"): os.environ.get(bstack11111l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠥἷ"), bstack11111l_opy_ (u"ࠧࠨἸ")),
                bstack11111l_opy_ (u"ࠨ࡮ࡰࡦࡨࡍࡳࡪࡥࡹࠤἹ"): int(os.environ.get(bstack11111l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥἺ")) or bstack11111l_opy_ (u"ࠣ࠲ࠥἻ")),
                bstack11111l_opy_ (u"ࠤࡷࡳࡹࡧ࡬ࡏࡱࡧࡩࡸࠨἼ"): int(os.environ.get(bstack11111l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡓ࡙ࡇࡌࡠࡐࡒࡈࡊࡥࡃࡐࡗࡑࡘࠧἽ")) or bstack11111l_opy_ (u"ࠦ࠶ࠨἾ")),
                bstack11111l_opy_ (u"ࠧ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠢἿ"): get_host_info(),
            }
            logger.debug(bstack11111l_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡘ࡫࡮ࡥ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡳࡥࡾࡲ࡯ࡢࡦ࠽ࠤࢀࢃࠢὀ").format(payload))
            response = bstack11l1ll1lll1_opy_.bstack1111ll11lll_opy_(bstack11l1lll1l1l_opy_, payload)
            if response:
                logger.debug(bstack11111l_opy_ (u"ࠢ࡜ࡥࡲࡰࡱ࡫ࡣࡵࡄࡸ࡭ࡱࡪࡄࡢࡶࡤࡡࠥࡈࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧὁ").format(response))
                return response
            else:
                logger.error(bstack11111l_opy_ (u"ࠣ࡝ࡦࡳࡱࡲࡥࡤࡶࡅࡹ࡮ࡲࡤࡅࡣࡷࡥࡢࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄ࠻ࠢࡾࢁࠧὂ").format(bstack1111l11l1ll_opy_))
                return None
        except Exception as e:
            logger.error(bstack11111l_opy_ (u"ࠤ࡞ࡧࡴࡲ࡬ࡦࡥࡷࡆࡺ࡯࡬ࡥࡆࡤࡸࡦࡣࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡣࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄࠡࡽࢀ࠾ࠥࢁࡽࠣὃ").format(bstack1111l11l1ll_opy_, e))
            return None