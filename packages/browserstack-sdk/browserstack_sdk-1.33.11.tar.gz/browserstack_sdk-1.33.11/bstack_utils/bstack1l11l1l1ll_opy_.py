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
import tempfile
import math
from bstack_utils import bstack1lllllll1l_opy_
from bstack_utils.constants import bstack1lllll111l_opy_, bstack11l1l1l1lll_opy_
from bstack_utils.helper import bstack111ll1111ll_opy_, get_host_info
from bstack_utils.bstack11l1ll1ll1l_opy_ import bstack11l1ll1l1l1_opy_
import json
import re
import sys
bstack1111l11111l_opy_ = bstack1l1l_opy_ (u"ࠥࡶࡪࡺࡲࡺࡖࡨࡷࡹࡹࡏ࡯ࡈࡤ࡭ࡱࡻࡲࡦࠤọ")
bstack1111ll1llll_opy_ = bstack1l1l_opy_ (u"ࠦࡦࡨ࡯ࡳࡶࡅࡹ࡮ࡲࡤࡐࡰࡉࡥ࡮ࡲࡵࡳࡧࠥỎ")
bstack1111l11l111_opy_ = bstack1l1l_opy_ (u"ࠧࡸࡵ࡯ࡒࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡋࡧࡩ࡭ࡧࡧࡊ࡮ࡸࡳࡵࠤỏ")
bstack11111lll111_opy_ = bstack1l1l_opy_ (u"ࠨࡲࡦࡴࡸࡲࡕࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡇࡣ࡬ࡰࡪࡪࠢỐ")
bstack1111l11ll11_opy_ = bstack1l1l_opy_ (u"ࠢࡴ࡭࡬ࡴࡋࡲࡡ࡬ࡻࡤࡲࡩࡌࡡࡪ࡮ࡨࡨࠧố")
bstack1111l11l1ll_opy_ = bstack1l1l_opy_ (u"ࠣࡴࡸࡲࡘࡳࡡࡳࡶࡖࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠧỒ")
bstack1111ll11ll1_opy_ = {
    bstack1111l11111l_opy_,
    bstack1111ll1llll_opy_,
    bstack1111l11l111_opy_,
    bstack11111lll111_opy_,
    bstack1111l11ll11_opy_,
    bstack1111l11l1ll_opy_
}
bstack1111l1111ll_opy_ = {bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩồ")}
logger = bstack1lllllll1l_opy_.get_logger(__name__, bstack1lllll111l_opy_)
class bstack1111l1l11l1_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack1111l1lllll_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack111l1111l_opy_:
    _1ll1ll1l1ll_opy_ = None
    def __init__(self, config):
        self.bstack1111ll111ll_opy_ = False
        self.bstack1111ll1ll1l_opy_ = False
        self.bstack11111llll1l_opy_ = False
        self.bstack1111ll1ll11_opy_ = False
        self.bstack1111ll1l11l_opy_ = None
        self.bstack1111l1ll1ll_opy_ = bstack1111l1l11l1_opy_()
        self.bstack1111ll1lll1_opy_ = None
        opts = config.get(bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧỔ"), {})
        self.bstack1111l111lll_opy_ = config.get(bstack1l1l_opy_ (u"ࠫࡸࡳࡡࡳࡶࡖࡩࡱ࡫ࡣࡵ࡫ࡲࡲࡋ࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࡩࡸࡋࡎࡗࠩổ"), bstack1l1l_opy_ (u"ࠧࠨỖ"))
        self.bstack1111l111l1l_opy_ = config.get(bstack1l1l_opy_ (u"࠭ࡳ࡮ࡣࡵࡸࡘ࡫࡬ࡦࡥࡷ࡭ࡴࡴࡆࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࡫ࡳࡄࡎࡌࠫỗ"), bstack1l1l_opy_ (u"ࠢࠣỘ"))
        bstack1111l111l11_opy_ = opts.get(bstack1111l11l1ll_opy_, {})
        bstack1111l1l1l11_opy_ = None
        if bstack1l1l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨộ") in bstack1111l111l11_opy_:
            bstack1111l1ll111_opy_ = bstack1111l111l11_opy_[bstack1l1l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩỚ")]
            if bstack1111l1ll111_opy_ is None or (isinstance(bstack1111l1ll111_opy_, str) and bstack1111l1ll111_opy_.strip() == bstack1l1l_opy_ (u"ࠪࠫớ")) or (isinstance(bstack1111l1ll111_opy_, list) and len(bstack1111l1ll111_opy_) == 0):
                bstack1111l1l1l11_opy_ = []
            elif isinstance(bstack1111l1ll111_opy_, list):
                bstack1111l1l1l11_opy_ = bstack1111l1ll111_opy_
            elif isinstance(bstack1111l1ll111_opy_, str) and bstack1111l1ll111_opy_.strip():
                bstack1111l1l1l11_opy_ = bstack1111l1ll111_opy_
            else:
                logger.warning(bstack1l1l_opy_ (u"ࠦࡎࡴࡶࡢ࡮࡬ࡨࠥࡹ࡯ࡶࡴࡦࡩࠥࡼࡡ࡭ࡷࡨࠤ࡮ࡴࠠࡤࡱࡱࡪ࡮࡭࠺ࠡࡽࢀ࠲ࠥࡊࡥࡧࡣࡸࡰࡹ࡯࡮ࡨࠢࡷࡳࠥ࡫࡭ࡱࡶࡼࠤࡱ࡯ࡳࡵ࠰ࠥỜ").format(bstack1111l1ll111_opy_))
                bstack1111l1l1l11_opy_ = []
        self.__1111l1ll1l1_opy_(
            bstack1111l111l11_opy_.get(bstack1l1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ờ"), False),
            bstack1111l111l11_opy_.get(bstack1l1l_opy_ (u"࠭࡭ࡰࡦࡨࠫỞ"), bstack1l1l_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧở")),
            bstack1111l1l1l11_opy_
        )
        self.__1111l1l1111_opy_(opts.get(bstack1111l11l111_opy_, False))
        self.__1111l111111_opy_(opts.get(bstack11111lll111_opy_, False))
        self.__11111lll1ll_opy_(opts.get(bstack1111l11ll11_opy_, False))
    @classmethod
    def bstack1l1ll1l111_opy_(cls, config=None):
        if cls._1ll1ll1l1ll_opy_ is None and config is not None:
            cls._1ll1ll1l1ll_opy_ = bstack111l1111l_opy_(config)
        return cls._1ll1ll1l1ll_opy_
    @staticmethod
    def bstack111l11l1_opy_(config: dict) -> bool:
        bstack1111l11l11l_opy_ = config.get(bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬỠ"), {}).get(bstack1111l11111l_opy_, {})
        return bstack1111l11l11l_opy_.get(bstack1l1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪỡ"), False)
    @staticmethod
    def bstack1ll111l1l1_opy_(config: dict) -> int:
        bstack1111l11l11l_opy_ = config.get(bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧỢ"), {}).get(bstack1111l11111l_opy_, {})
        retries = 0
        if bstack111l1111l_opy_.bstack111l11l1_opy_(config):
            retries = bstack1111l11l11l_opy_.get(bstack1l1l_opy_ (u"ࠫࡲࡧࡸࡓࡧࡷࡶ࡮࡫ࡳࠨợ"), 1)
        return retries
    @staticmethod
    def bstack11l11l1l1l_opy_(config: dict) -> dict:
        bstack1111l1llll1_opy_ = config.get(bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩỤ"), {})
        return {
            key: value for key, value in bstack1111l1llll1_opy_.items() if key in bstack1111ll11ll1_opy_
        }
    @staticmethod
    def bstack11111llll11_opy_():
        bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡇ࡭࡫ࡣ࡬ࠢ࡬ࡪࠥࡺࡨࡦࠢࡤࡦࡴࡸࡴࠡࡤࡸ࡭ࡱࡪࠠࡧ࡫࡯ࡩࠥ࡫ࡸࡪࡵࡷࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥụ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠢࡢࡤࡲࡶࡹࡥࡢࡶ࡫࡯ࡨࡤࢁࡽࠣỦ").format(os.getenv(bstack1l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨủ")))))
    @staticmethod
    def bstack1111l11lll1_opy_(test_name: str):
        bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡃࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡧࡢࡰࡴࡷࠤࡧࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡧࡻ࡭ࡸࡺࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨỨ")
        bstack1111l1lll1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࡢࡸࡪࡹࡴࡴࡡࡾࢁ࠳ࡺࡸࡵࠤứ").format(os.getenv(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤỪ"))))
        with open(bstack1111l1lll1l_opy_, bstack1l1l_opy_ (u"ࠬࡧࠧừ")) as file:
            file.write(bstack1l1l_opy_ (u"ࠨࡻࡾ࡞ࡱࠦỬ").format(test_name))
    @staticmethod
    def bstack1111l1l1l1l_opy_(framework: str) -> bool:
       return framework.lower() in bstack1111l1111ll_opy_
    @staticmethod
    def bstack11l11l1lll1_opy_(config: dict) -> bool:
        bstack11111ll1lll_opy_ = config.get(bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫử"), {}).get(bstack1111ll1llll_opy_, {})
        return bstack11111ll1lll_opy_.get(bstack1l1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩỮ"), False)
    @staticmethod
    def bstack11l11l11l11_opy_(config: dict, bstack11l11ll11ll_opy_: int = 0) -> int:
        bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡇࡦࡶࠣࡸ࡭࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥࠡࡶ࡫ࡶࡪࡹࡨࡰ࡮ࡧ࠰ࠥࡽࡨࡪࡥ࡫ࠤࡨࡧ࡮ࠡࡤࡨࠤࡦࡴࠠࡢࡤࡶࡳࡱࡻࡴࡦࠢࡱࡹࡲࡨࡥࡳࠢࡲࡶࠥࡧࠠࡱࡧࡵࡧࡪࡴࡴࡢࡩࡨ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡧࡴࡴࡦࡪࡩࠣࠬࡩ࡯ࡣࡵࠫ࠽ࠤ࡙࡮ࡥࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡹࡵࡴࡢ࡮ࡢࡸࡪࡹࡴࡴࠢࠫ࡭ࡳࡺࠩ࠻ࠢࡗ࡬ࡪࠦࡴࡰࡶࡤࡰࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࠩࡴࡨࡵࡺ࡯ࡲࡦࡦࠣࡪࡴࡸࠠࡱࡧࡵࡧࡪࡴࡴࡢࡩࡨ࠱ࡧࡧࡳࡦࡦࠣࡸ࡭ࡸࡥࡴࡪࡲࡰࡩࡹࠩ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡭ࡳࡺ࠺ࠡࡖ࡫ࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢữ")
        bstack11111ll1lll_opy_ = config.get(bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧỰ"), {}).get(bstack1l1l_opy_ (u"ࠫࡦࡨ࡯ࡳࡶࡅࡹ࡮ࡲࡤࡐࡰࡉࡥ࡮ࡲࡵࡳࡧࠪự"), {})
        bstack1111l1l11ll_opy_ = 0
        bstack1111l1lll11_opy_ = 0
        if bstack111l1111l_opy_.bstack11l11l1lll1_opy_(config):
            bstack1111l1lll11_opy_ = bstack11111ll1lll_opy_.get(bstack1l1l_opy_ (u"ࠬࡳࡡࡹࡈࡤ࡭ࡱࡻࡲࡦࡵࠪỲ"), 5)
            if isinstance(bstack1111l1lll11_opy_, str) and bstack1111l1lll11_opy_.endswith(bstack1l1l_opy_ (u"࠭ࠥࠨỳ")):
                try:
                    percentage = int(bstack1111l1lll11_opy_.strip(bstack1l1l_opy_ (u"ࠧࠦࠩỴ")))
                    if bstack11l11ll11ll_opy_ > 0:
                        bstack1111l1l11ll_opy_ = math.ceil((percentage * bstack11l11ll11ll_opy_) / 100)
                    else:
                        raise ValueError(bstack1l1l_opy_ (u"ࠣࡖࡲࡸࡦࡲࠠࡵࡧࡶࡸࡸࠦ࡭ࡶࡵࡷࠤࡧ࡫ࠠࡱࡴࡲࡺ࡮ࡪࡥࡥࠢࡩࡳࡷࠦࡰࡦࡴࡦࡩࡳࡺࡡࡨࡧ࠰ࡦࡦࡹࡥࡥࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࡸ࠴ࠢỵ"))
                except ValueError as e:
                    raise ValueError(bstack1l1l_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫ࠠࡷࡣ࡯ࡹࡪࠦࡦࡰࡴࠣࡱࡦࡾࡆࡢ࡫࡯ࡹࡷ࡫ࡳ࠻ࠢࡾࢁࠧỶ").format(bstack1111l1lll11_opy_)) from e
            else:
                bstack1111l1l11ll_opy_ = int(bstack1111l1lll11_opy_)
        logger.info(bstack1l1l_opy_ (u"ࠥࡑࡦࡾࠠࡧࡣ࡬ࡰࡺࡸࡥࡴࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࠥࡹࡥࡵࠢࡷࡳ࠿ࠦࡻࡾࠢࠫࡪࡷࡵ࡭ࠡࡥࡲࡲ࡫࡯ࡧ࠻ࠢࡾࢁ࠮ࠨỷ").format(bstack1111l1l11ll_opy_, bstack1111l1lll11_opy_))
        return bstack1111l1l11ll_opy_
    def bstack1111ll11l11_opy_(self):
        return self.bstack1111ll1ll11_opy_
    def bstack1111ll11111_opy_(self):
        return self.bstack1111ll1l11l_opy_
    def bstack1111l1l1lll_opy_(self):
        return self.bstack1111ll1lll1_opy_
    def __1111l1ll1l1_opy_(self, enabled, mode, source=None):
        try:
            self.bstack1111ll1ll11_opy_ = bool(enabled)
            if mode not in [bstack1l1l_opy_ (u"ࠫࡷ࡫࡬ࡦࡸࡤࡲࡹࡌࡩࡳࡵࡷࠫỸ"), bstack1l1l_opy_ (u"ࠬࡸࡥ࡭ࡧࡹࡥࡳࡺࡏ࡯࡮ࡼࠫỹ")]:
                logger.warning(bstack1l1l_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡴ࡯ࡤࡶࡹࠦࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠢࡰࡳࡩ࡫ࠠࠨࡽࢀࠫࠥࡶࡲࡰࡸ࡬ࡨࡪࡪ࠮ࠡࡆࡨࡪࡦࡻ࡬ࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࠩࡵࡩࡱ࡫ࡶࡢࡰࡷࡊ࡮ࡸࡳࡵࠩ࠱ࠦỺ").format(mode))
                mode = bstack1l1l_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧỻ")
            self.bstack1111ll1l11l_opy_ = mode
            self.bstack1111ll1lll1_opy_ = []
            if source is None:
                self.bstack1111ll1lll1_opy_ = None
            elif isinstance(source, list):
                self.bstack1111ll1lll1_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack1l1l_opy_ (u"ࠨ࠰࡭ࡷࡴࡴࠧỼ")):
                self.bstack1111ll1lll1_opy_ = self._1111l1l111l_opy_(source)
            self.__1111l111ll1_opy_()
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡶࡱࡦࡸࡴࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࠲ࠦࡥ࡯ࡣࡥࡰࡪࡪ࠺ࠡࡽࢀ࠰ࠥࡳ࡯ࡥࡧ࠽ࠤࢀࢃࠬࠡࡵࡲࡹࡷࡩࡥ࠻ࠢࡾࢁ࠳ࠦࡅࡳࡴࡲࡶ࠿ࠦࡻࡾࠤỽ").format(enabled, mode, source, e))
    def bstack1111ll111l1_opy_(self):
        return self.bstack1111ll111ll_opy_
    def __1111l1l1111_opy_(self, value):
        self.bstack1111ll111ll_opy_ = bool(value)
        self.__1111l111ll1_opy_()
    def bstack1111l11llll_opy_(self):
        return self.bstack1111ll1ll1l_opy_
    def __1111l111111_opy_(self, value):
        self.bstack1111ll1ll1l_opy_ = bool(value)
        self.__1111l111ll1_opy_()
    def bstack11111lll11l_opy_(self):
        return self.bstack11111llll1l_opy_
    def __11111lll1ll_opy_(self, value):
        self.bstack11111llll1l_opy_ = bool(value)
        self.__1111l111ll1_opy_()
    def __1111l111ll1_opy_(self):
        if self.bstack1111ll1ll11_opy_:
            self.bstack1111ll111ll_opy_ = False
            self.bstack1111ll1ll1l_opy_ = False
            self.bstack11111llll1l_opy_ = False
            self.bstack1111l1ll1ll_opy_.enable(bstack1111l11l1ll_opy_)
        elif self.bstack1111ll111ll_opy_:
            self.bstack1111ll1ll1l_opy_ = False
            self.bstack11111llll1l_opy_ = False
            self.bstack1111ll1ll11_opy_ = False
            self.bstack1111l1ll1ll_opy_.enable(bstack1111l11l111_opy_)
        elif self.bstack1111ll1ll1l_opy_:
            self.bstack1111ll111ll_opy_ = False
            self.bstack11111llll1l_opy_ = False
            self.bstack1111ll1ll11_opy_ = False
            self.bstack1111l1ll1ll_opy_.enable(bstack11111lll111_opy_)
        elif self.bstack11111llll1l_opy_:
            self.bstack1111ll111ll_opy_ = False
            self.bstack1111ll1ll1l_opy_ = False
            self.bstack1111ll1ll11_opy_ = False
            self.bstack1111l1ll1ll_opy_.enable(bstack1111l11ll11_opy_)
        else:
            self.bstack1111l1ll1ll_opy_.disable()
    def bstack1lll1ll1l_opy_(self):
        return self.bstack1111l1ll1ll_opy_.bstack1111l1lllll_opy_()
    def bstack1lll11ll11_opy_(self):
        if self.bstack1111l1ll1ll_opy_.bstack1111l1lllll_opy_():
            return self.bstack1111l1ll1ll_opy_.get_name()
        return None
    def _1111l1l111l_opy_(self, bstack1111ll11lll_opy_):
        bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡣࡵࡷࡪࠦࡊࡔࡑࡑࠤࡸࡵࡵࡳࡥࡨࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫࡯࡬ࡦࠢࡤࡲࡩࠦࡦࡰࡴࡰࡥࡹࠦࡩࡵࠢࡩࡳࡷࠦࡳ࡮ࡣࡵࡸࠥࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡴࡱࡸࡶࡨ࡫࡟ࡧ࡫࡯ࡩࡤࡶࡡࡵࡪࠣࠬࡸࡺࡲࠪ࠼ࠣࡔࡦࡺࡨࠡࡶࡲࠤࡹ࡮ࡥࠡࡌࡖࡓࡓࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡦࡪ࡮ࡨࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡲࡩࡴࡶ࠽ࠤࡋࡵࡲ࡮ࡣࡷࡸࡪࡪࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡴࡨࡴࡴࡹࡩࡵࡱࡵࡽࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࡸࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥỾ")
        if not os.path.isfile(bstack1111ll11lll_opy_):
            logger.error(bstack1l1l_opy_ (u"ࠦࡘࡵࡵࡳࡥࡨࠤ࡫࡯࡬ࡦࠢࠪࡿࢂ࠭ࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴ࠯ࠤỿ").format(bstack1111ll11lll_opy_))
            return []
        data = None
        try:
            with open(bstack1111ll11lll_opy_, bstack1l1l_opy_ (u"ࠧࡸࠢἀ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack1l1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡊࡔࡑࡑࠤ࡫ࡸ࡯࡮ࠢࡶࡳࡺࡸࡣࡦࠢࡩ࡭ࡱ࡫ࠠࠨࡽࢀࠫ࠿ࠦࡻࡾࠤἁ").format(bstack1111ll11lll_opy_, e))
            return []
        _1111l1111l1_opy_ = None
        _1111l1ll11l_opy_ = None
        def _1111ll1l111_opy_():
            bstack11111lll1l1_opy_ = {}
            bstack1111ll1111l_opy_ = {}
            try:
                if self.bstack1111l111lll_opy_.startswith(bstack1l1l_opy_ (u"ࠧࡼࠩἂ")) and self.bstack1111l111lll_opy_.endswith(bstack1l1l_opy_ (u"ࠨࡿࠪἃ")):
                    bstack11111lll1l1_opy_ = json.loads(self.bstack1111l111lll_opy_)
                else:
                    bstack11111lll1l1_opy_ = dict(item.split(bstack1l1l_opy_ (u"ࠩ࠽ࠫἄ")) for item in self.bstack1111l111lll_opy_.split(bstack1l1l_opy_ (u"ࠪ࠰ࠬἅ")) if bstack1l1l_opy_ (u"ࠫ࠿࠭ἆ") in item) if self.bstack1111l111lll_opy_ else {}
                if self.bstack1111l111l1l_opy_.startswith(bstack1l1l_opy_ (u"ࠬࢁࠧἇ")) and self.bstack1111l111l1l_opy_.endswith(bstack1l1l_opy_ (u"࠭ࡽࠨἈ")):
                    bstack1111ll1111l_opy_ = json.loads(self.bstack1111l111l1l_opy_)
                else:
                    bstack1111ll1111l_opy_ = dict(item.split(bstack1l1l_opy_ (u"ࠧ࠻ࠩἉ")) for item in self.bstack1111l111l1l_opy_.split(bstack1l1l_opy_ (u"ࠨ࠮ࠪἊ")) if bstack1l1l_opy_ (u"ࠩ࠽ࠫἋ") in item) if self.bstack1111l111l1l_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡳࡥࡷࡹࡩ࡯ࡩࠣࡪࡪࡧࡴࡶࡴࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤࡲࡧࡰࡱ࡫ࡱ࡫ࡸࡀࠠࡼࡿࠥἌ").format(e))
            logger.debug(bstack1l1l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡳࡡࡱࡲ࡬ࡲ࡬ࡹࠠࡧࡴࡲࡱࠥ࡫࡮ࡷ࠼ࠣࡿࢂ࠲ࠠࡄࡎࡌ࠾ࠥࢁࡽࠣἍ").format(bstack11111lll1l1_opy_, bstack1111ll1111l_opy_))
            return bstack11111lll1l1_opy_, bstack1111ll1111l_opy_
        if _1111l1111l1_opy_ is None or _1111l1ll11l_opy_ is None:
            _1111l1111l1_opy_, _1111l1ll11l_opy_ = _1111ll1l111_opy_()
        def bstack11111llllll_opy_(name, bstack1111l11ll1l_opy_):
            if name in _1111l1ll11l_opy_:
                return _1111l1ll11l_opy_[name]
            if name in _1111l1111l1_opy_:
                return _1111l1111l1_opy_[name]
            if bstack1111l11ll1l_opy_.get(bstack1l1l_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠬἎ")):
                return bstack1111l11ll1l_opy_[bstack1l1l_opy_ (u"࠭ࡦࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࠭Ἇ")]
            return None
        if isinstance(data, dict):
            bstack1111ll1l1ll_opy_ = []
            bstack11111lllll1_opy_ = re.compile(bstack1l1l_opy_ (u"ࡲࠨࡠ࡞ࡅ࠲ࡠ࠰࠮࠻ࡢࡡ࠰ࠪࠧἐ"))
            for name, bstack1111l11ll1l_opy_ in data.items():
                if not isinstance(bstack1111l11ll1l_opy_, dict):
                    continue
                url = bstack1111l11ll1l_opy_.get(bstack1l1l_opy_ (u"ࠨࡷࡵࡰࠬἑ"))
                if url is None or (isinstance(url, str) and url.strip() == bstack1l1l_opy_ (u"ࠩࠪἒ")):
                    logger.warning(bstack1l1l_opy_ (u"ࠥࡖࡪࡶ࡯ࡴ࡫ࡷࡳࡷࡿࠠࡖࡔࡏࠤ࡮ࡹࠠ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡨࡲࡶࠥࡹ࡯ࡶࡴࡦࡩࠥ࠭ࡻࡾࠩ࠽ࠤࢀࢃࠢἓ").format(name, bstack1111l11ll1l_opy_))
                    continue
                if not bstack11111lllll1_opy_.match(name):
                    logger.warning(bstack1l1l_opy_ (u"ࠦࡎࡴࡶࡢ࡮࡬ࡨࠥࡹ࡯ࡶࡴࡦࡩࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠢࡩࡳࡷࡳࡡࡵࠢࡩࡳࡷࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣἔ").format(name, bstack1111l11ll1l_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack1l1l_opy_ (u"࡙ࠧ࡯ࡶࡴࡦࡩࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠢࠪࡿࢂ࠭ࠠ࡮ࡷࡶࡸࠥ࡮ࡡࡷࡧࠣࡥࠥࡲࡥ࡯ࡩࡷ࡬ࠥࡨࡥࡵࡹࡨࡩࡳࠦ࠱ࠡࡣࡱࡨࠥ࠹࠰ࠡࡥ࡫ࡥࡷࡧࡣࡵࡧࡵࡷ࠳ࠨἕ").format(name))
                    continue
                bstack1111l11ll1l_opy_ = bstack1111l11ll1l_opy_.copy()
                bstack1111l11ll1l_opy_[bstack1l1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ἖")] = name
                bstack1111l11ll1l_opy_[bstack1l1l_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧ἗")] = bstack11111llllll_opy_(name, bstack1111l11ll1l_opy_)
                if not bstack1111l11ll1l_opy_.get(bstack1l1l_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠨἘ")) or bstack1111l11ll1l_opy_.get(bstack1l1l_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩἙ")) == bstack1l1l_opy_ (u"ࠪࠫἚ"):
                    logger.warning(bstack1l1l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡴ࡯ࡵࠢࡶࡴࡪࡩࡩࡧ࡫ࡨࡨࠥ࡬࡯ࡳࠢࡶࡳࡺࡸࡣࡦࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦἛ").format(name, bstack1111l11ll1l_opy_))
                    continue
                if bstack1111l11ll1l_opy_.get(bstack1l1l_opy_ (u"ࠬࡨࡡࡴࡧࡅࡶࡦࡴࡣࡩࠩἜ")) and bstack1111l11ll1l_opy_[bstack1l1l_opy_ (u"࠭ࡢࡢࡵࡨࡆࡷࡧ࡮ࡤࡪࠪἝ")] == bstack1111l11ll1l_opy_[bstack1l1l_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧ἞")]:
                    logger.warning(bstack1l1l_opy_ (u"ࠣࡈࡨࡥࡹࡻࡲࡦࠢࡥࡶࡦࡴࡣࡩࠢࡤࡲࡩࠦࡢࡢࡵࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡵࡪࡨࠤࡸࡧ࡭ࡦࠢࡩࡳࡷࠦࡳࡰࡷࡵࡧࡪࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣ἟").format(name, bstack1111l11ll1l_opy_))
                    continue
                bstack1111ll1l1ll_opy_.append(bstack1111l11ll1l_opy_)
            return bstack1111ll1l1ll_opy_
        return data
    def bstack1111lllll1l_opy_(self):
        data = {
            bstack1l1l_opy_ (u"ࠩࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠨἠ"): {
                bstack1l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫἡ"): self.bstack1111ll11l11_opy_(),
                bstack1l1l_opy_ (u"ࠫࡲࡵࡤࡦࠩἢ"): self.bstack1111ll11111_opy_(),
                bstack1l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬἣ"): self.bstack1111l1l1lll_opy_()
            }
        }
        return data
    def bstack1111l1l1ll1_opy_(self, config):
        bstack1111l11l1l1_opy_ = {}
        bstack1111l11l1l1_opy_[bstack1l1l_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬἤ")] = {
            bstack1l1l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨἥ"): self.bstack1111ll11l11_opy_(),
            bstack1l1l_opy_ (u"ࠨ࡯ࡲࡨࡪ࠭ἦ"): self.bstack1111ll11111_opy_()
        }
        bstack1111l11l1l1_opy_[bstack1l1l_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡲࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡤ࡬ࡡࡪ࡮ࡨࡨࠬἧ")] = {
            bstack1l1l_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫἨ"): self.bstack1111l11llll_opy_()
        }
        bstack1111l11l1l1_opy_[bstack1l1l_opy_ (u"ࠫࡷࡻ࡮ࡠࡲࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡤ࡬ࡡࡪ࡮ࡨࡨࡤ࡬ࡩࡳࡵࡷࠫἩ")] = {
            bstack1l1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ἢ"): self.bstack1111ll111l1_opy_()
        }
        bstack1111l11l1l1_opy_[bstack1l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡣ࡫ࡧࡩ࡭࡫ࡱ࡫ࡤࡧ࡮ࡥࡡࡩࡰࡦࡱࡹࠨἫ")] = {
            bstack1l1l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨἬ"): self.bstack11111lll11l_opy_()
        }
        if self.bstack111l11l1_opy_(config):
            bstack1111l11l1l1_opy_[bstack1l1l_opy_ (u"ࠨࡴࡨࡸࡷࡿ࡟ࡵࡧࡶࡸࡸࡥ࡯࡯ࡡࡩࡥ࡮ࡲࡵࡳࡧࠪἭ")] = {
                bstack1l1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪἮ"): True,
                bstack1l1l_opy_ (u"ࠪࡱࡦࡾ࡟ࡳࡧࡷࡶ࡮࡫ࡳࠨἯ"): self.bstack1ll111l1l1_opy_(config)
            }
        if self.bstack11l11l1lll1_opy_(config):
            bstack1111l11l1l1_opy_[bstack1l1l_opy_ (u"ࠫࡦࡨ࡯ࡳࡶࡢࡦࡺ࡯࡬ࡥࡡࡲࡲࡤ࡬ࡡࡪ࡮ࡸࡶࡪ࠭ἰ")] = {
                bstack1l1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ἱ"): True,
                bstack1l1l_opy_ (u"࠭࡭ࡢࡺࡢࡪࡦ࡯࡬ࡶࡴࡨࡷࠬἲ"): self.bstack11l11l11l11_opy_(config)
            }
        return bstack1111l11l1l1_opy_
    def bstack11l1l1l1ll_opy_(self, config):
        bstack1l1l_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡵ࡬࡭ࡧࡦࡸࡸࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡦࡾࠦ࡭ࡢ࡭࡬ࡲ࡬ࠦࡡࠡࡥࡤࡰࡱࠦࡴࡰࠢࡷ࡬ࡪࠦࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡣࡷ࡬ࡰࡩ࠳ࡤࡢࡶࡤࠤࡪࡴࡤࡱࡱ࡬ࡲࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡺࡻࡩࡥࠢࠫࡷࡹࡸࠩ࠻ࠢࡗ࡬ࡪࠦࡕࡖࡋࡇࠤࡴ࡬ࠠࡵࡪࡨࠤࡧࡻࡩ࡭ࡦࠣࡸࡴࠦࡣࡰ࡮࡯ࡩࡨࡺࠠࡥࡣࡷࡥࠥ࡬࡯ࡳ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡩ࡯ࡣࡵ࠼ࠣࡖࡪࡹࡰࡰࡰࡶࡩࠥ࡬ࡲࡰ࡯ࠣࡸ࡭࡫ࠠࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡤࡸ࡭ࡱࡪ࠭ࡥࡣࡷࡥࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠬࠡࡱࡵࠤࡓࡵ࡮ࡦࠢ࡬ࡪࠥ࡬ࡡࡪ࡮ࡨࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥἳ")
        if not (config.get(bstack1l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫἴ"), None) in bstack11l1l1l1lll_opy_ and self.bstack1111ll11l11_opy_()):
            return None
        bstack1111ll1l1l1_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧἵ"), None)
        logger.debug(bstack1l1l_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨ࡛ࠥࡕࡊࡆ࠽ࠤࢀࢃࠢἶ").format(bstack1111ll1l1l1_opy_))
        try:
            bstack11l1lll11ll_opy_ = bstack1l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡨࡵࡪ࡮ࡧ࠱ࡩࡧࡴࡢࠤἷ").format(bstack1111ll1l1l1_opy_)
            payload = {
                bstack1l1l_opy_ (u"ࠧࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠥἸ"): config.get(bstack1l1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫἹ"), bstack1l1l_opy_ (u"ࠧࠨἺ")),
                bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠦἻ"): config.get(bstack1l1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬἼ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡔࡸࡲࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣἽ"): os.environ.get(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠥἾ"), bstack1l1l_opy_ (u"ࠧࠨἿ")),
                bstack1l1l_opy_ (u"ࠨ࡮ࡰࡦࡨࡍࡳࡪࡥࡹࠤὀ"): int(os.environ.get(bstack1l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥὁ")) or bstack1l1l_opy_ (u"ࠣ࠲ࠥὂ")),
                bstack1l1l_opy_ (u"ࠤࡷࡳࡹࡧ࡬ࡏࡱࡧࡩࡸࠨὃ"): int(os.environ.get(bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡓ࡙ࡇࡌࡠࡐࡒࡈࡊࡥࡃࡐࡗࡑࡘࠧὄ")) or bstack1l1l_opy_ (u"ࠦ࠶ࠨὅ")),
                bstack1l1l_opy_ (u"ࠧ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠢ὆"): get_host_info(),
            }
            logger.debug(bstack1l1l_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡘ࡫࡮ࡥ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡳࡥࡾࡲ࡯ࡢࡦ࠽ࠤࢀࢃࠢ὇").format(payload))
            response = bstack11l1ll1l1l1_opy_.bstack1111ll11l1l_opy_(bstack11l1lll11ll_opy_, payload)
            if response:
                logger.debug(bstack1l1l_opy_ (u"ࠢ࡜ࡥࡲࡰࡱ࡫ࡣࡵࡄࡸ࡭ࡱࡪࡄࡢࡶࡤࡡࠥࡈࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧὈ").format(response))
                return response
            else:
                logger.error(bstack1l1l_opy_ (u"ࠣ࡝ࡦࡳࡱࡲࡥࡤࡶࡅࡹ࡮ࡲࡤࡅࡣࡷࡥࡢࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄ࠻ࠢࡾࢁࠧὉ").format(bstack1111ll1l1l1_opy_))
                return None
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠤ࡞ࡧࡴࡲ࡬ࡦࡥࡷࡆࡺ࡯࡬ࡥࡆࡤࡸࡦࡣࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡣࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄࠡࡽࢀ࠾ࠥࢁࡽࠣὊ").format(bstack1111ll1l1l1_opy_, e))
            return None