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
import time
from bstack_utils.bstack11l1ll1ll1l_opy_ import bstack11l1ll1l1l1_opy_
from bstack_utils.constants import bstack11l11lll1l1_opy_
from bstack_utils.helper import get_host_info, bstack111ll1111ll_opy_
class bstack1111llllll1_opy_:
    bstack1l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡎࡡ࡯ࡦ࡯ࡩࡸࠦࡴࡦࡵࡷࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡷࡪࡶ࡫ࠤࡹ࡮ࡥࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡴࡧࡵࡺࡪࡸ࠮ࠋࠢࠣࠤࠥࠨࠢࠣℍ")
    def __init__(self, config, logger):
        bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡧࡴࡴࡦࡪࡩ࠽ࠤࡩ࡯ࡣࡵ࠮ࠣࡸࡪࡹࡴࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡥࡲࡲ࡫࡯ࡧࠋࠢࠣࠤࠥࠦࠠࠡࠢ࠽ࡴࡦࡸࡡ࡮ࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡡࡶࡸࡷࡧࡴࡦࡩࡼ࠾ࠥࡹࡴࡳ࠮ࠣࡸࡪࡹࡴࠡࡱࡵࡨࡪࡸࡩ࡯ࡩࠣࡷࡹࡸࡡࡵࡧࡪࡽࠥࡴࡡ࡮ࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢℎ")
        self.config = config
        self.logger = logger
        self.bstack1llll111l111_opy_ = bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳ࡸࡶ࡬ࡪࡶ࠰ࡸࡪࡹࡴࡴࠤℏ")
        self.bstack1llll111l1l1_opy_ = None
        self.bstack1llll111ll11_opy_ = 60
        self.bstack1llll11l11l1_opy_ = 5
        self.bstack1llll11l1111_opy_ = 0
    def bstack1111lll11ll_opy_(self, test_files, orchestration_strategy, orchestration_metadata={}):
        bstack1l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡏ࡮ࡪࡶ࡬ࡥࡹ࡫ࡳࠡࡶ࡫ࡩࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡶࡪࡷࡵࡦࡵࡷࠤࡦࡴࡤࠡࡵࡷࡳࡷ࡫ࡳࠡࡶ࡫ࡩࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡳࡳࡱࡲࡩ࡯ࡩ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣℐ")
        self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡋࡱ࡭ࡹ࡯ࡡࡵ࡫ࡱ࡫ࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡻ࡮ࡺࡨࠡࡵࡷࡶࡦࡺࡥࡨࡻ࠽ࠤࢀࢃࠢℑ").format(orchestration_strategy))
        try:
            bstack1llll111l11l_opy_ = []
            bstack1l1l_opy_ (u"ࠥࠦࠧ࡝ࡥࠡࡹ࡬ࡰࡱࠦ࡮ࡰࡶࠣࡪࡪࡺࡣࡩࠢࡪ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡ࡫ࡶࠤࡸࡵࡵࡳࡥࡨࠤ࡮ࡹࠠࡵࡻࡳࡩࠥࡵࡦࠡࡣࡵࡶࡦࡿࠠࡢࡰࡧࠤ࡮ࡺࠧࡴࠢࡨࡰࡪࡳࡥ࡯ࡶࡶࠤࡦࡸࡥࠡࡱࡩࠤࡹࡿࡰࡦࠢࡧ࡭ࡨࡺࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡥࡤࡣࡸࡷࡪࠦࡩ࡯ࠢࡷ࡬ࡦࡺࠠࡤࡣࡶࡩ࠱ࠦࡵࡴࡧࡵࠤ࡭ࡧࡳࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡱࡺࡲࡴࡪ࠯ࡵࡩࡵࡵࠠࡴࡱࡸࡶࡨ࡫ࠠࡸ࡫ࡷ࡬ࠥ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠥ࡯࡮ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠢࠣࠤℒ")
            source = orchestration_metadata[bstack1l1l_opy_ (u"ࠫࡷࡻ࡮ࡠࡵࡰࡥࡷࡺ࡟ࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠪℓ")].get(bstack1l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ℔"), [])
            bstack1llll11l1l1l_opy_ = isinstance(source, list) and all(isinstance(src, dict) and src is not None for src in source) and len(source) > 0
            if orchestration_metadata[bstack1l1l_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬℕ")].get(bstack1l1l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨ№"), False) and not bstack1llll11l1l1l_opy_:
                bstack1llll111l11l_opy_ = bstack111ll1111ll_opy_(source) # bstack1llll111lll1_opy_-repo is handled bstack1llll11l1l11_opy_
            payload = {
                bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢ℗"): [{bstack1l1l_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡐࡢࡶ࡫ࠦ℘"): f} for f in test_files],
                bstack1l1l_opy_ (u"ࠥࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡖࡸࡷࡧࡴࡦࡩࡼࠦℙ"): orchestration_strategy,
                bstack1l1l_opy_ (u"ࠦࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡑࡪࡺࡡࡥࡣࡷࡥࠧℚ"): orchestration_metadata,
                bstack1l1l_opy_ (u"ࠧࡴ࡯ࡥࡧࡌࡲࡩ࡫ࡸࠣℛ"): int(os.environ.get(bstack1l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡔࡏࡅࡇࡢࡍࡓࡊࡅ࡙ࠤℜ")) or bstack1l1l_opy_ (u"ࠢ࠱ࠤℝ")),
                bstack1l1l_opy_ (u"ࠣࡶࡲࡸࡦࡲࡎࡰࡦࡨࡷࠧ℞"): int(os.environ.get(bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡒࡘࡆࡒ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦ℟")) or bstack1l1l_opy_ (u"ࠥ࠵ࠧ℠")),
                bstack1l1l_opy_ (u"ࠦࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠤ℡"): self.config.get(bstack1l1l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ™"), bstack1l1l_opy_ (u"࠭ࠧ℣")),
                bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠥℤ"): self.config.get(bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ℥"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡓࡷࡱࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢΩ"): os.environ.get(bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡔࡘࡒࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠤ℧"), bstack1l1l_opy_ (u"ࠦࠧℨ")),
                bstack1l1l_opy_ (u"ࠧ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠢ℩"): get_host_info(),
                bstack1l1l_opy_ (u"ࠨࡰࡳࡆࡨࡸࡦ࡯࡬ࡴࠤK"): bstack1llll111l11l_opy_
            }
            self.logger.debug(bstack1l1l_opy_ (u"ࠢ࡜ࡵࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࡢࠦࡓࡦࡰࡧ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶ࠾ࠥࢁࡽࠣÅ").format(payload))
            response = bstack11l1ll1l1l1_opy_.bstack1llll1lll1l1_opy_(self.bstack1llll111l111_opy_, payload)
            if response:
                self.bstack1llll111l1l1_opy_ = self._1llll111llll_opy_(response)
                self.logger.debug(bstack1l1l_opy_ (u"ࠣ࡝ࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡣࠠࡔࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠦℬ").format(self.bstack1llll111l1l1_opy_))
            else:
                self.logger.error(bstack1l1l_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤ࡬࡫ࡴࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠯ࠤℭ"))
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡨࡲࡩ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࡀ࠺ࠡࡽࢀࠦ℮").format(e))
    def _1llll111llll_opy_(self, response):
        bstack1l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡹ࡮ࡥࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡁࡑࡋࠣࡶࡪࡹࡰࡰࡰࡶࡩࠥࡧ࡮ࡥࠢࡨࡼࡹࡸࡡࡤࡶࡶࠤࡷ࡫࡬ࡦࡸࡤࡲࡹࠦࡦࡪࡧ࡯ࡨࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦℯ")
        bstack1llll111l1_opy_ = {}
        bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨℰ")] = response.get(bstack1l1l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢℱ"), self.bstack1llll111ll11_opy_)
        bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤℲ")] = response.get(bstack1l1l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮ࠥℳ"), self.bstack1llll11l11l1_opy_)
        bstack1llll11l1lll_opy_ = response.get(bstack1l1l_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡗࡵࡰࠧℴ"))
        bstack1llll111ll1l_opy_ = response.get(bstack1l1l_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷ࡙ࡷࡲࠢℵ"))
        if bstack1llll11l1lll_opy_:
            bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷ࡙ࡷࡲࠢℶ")] = bstack1llll11l1lll_opy_.split(bstack11l11lll1l1_opy_ + bstack1l1l_opy_ (u"ࠧ࠵ࠢℷ"))[1] if bstack11l11lll1l1_opy_ + bstack1l1l_opy_ (u"ࠨ࠯ࠣℸ") in bstack1llll11l1lll_opy_ else bstack1llll11l1lll_opy_
        else:
            bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮ࠥℹ")] = None
        if bstack1llll111ll1l_opy_:
            bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰࠧ℺")] = bstack1llll111ll1l_opy_.split(bstack11l11lll1l1_opy_ + bstack1l1l_opy_ (u"ࠤ࠲ࠦ℻"))[1] if bstack11l11lll1l1_opy_ + bstack1l1l_opy_ (u"ࠥ࠳ࠧℼ") in bstack1llll111ll1l_opy_ else bstack1llll111ll1l_opy_
        else:
            bstack1llll111l1_opy_[bstack1l1l_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣℽ")] = None
        if (
            response.get(bstack1l1l_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨℾ")) is None or
            response.get(bstack1l1l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡉ࡯ࡶࡨࡶࡻࡧ࡬ࠣℿ")) is None or
            response.get(bstack1l1l_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦ⅀")) is None or
            response.get(bstack1l1l_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦ⅁")) is None
        ):
            self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡞ࡴࡷࡵࡣࡦࡵࡶࡣࡸࡶ࡬ࡪࡶࡢࡸࡪࡹࡴࡴࡡࡵࡩࡸࡶ࡯࡯ࡵࡨࡡࠥࡘࡥࡤࡧ࡬ࡺࡪࡪࠠ࡯ࡷ࡯ࡰࠥࡼࡡ࡭ࡷࡨࠬࡸ࠯ࠠࡧࡱࡵࠤࡸࡵ࡭ࡦࠢࡤࡸࡹࡸࡩࡣࡷࡷࡩࡸࠦࡩ࡯ࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡂࡒࡌࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠨ⅂"))
        return bstack1llll111l1_opy_
    def bstack1111llll11l_opy_(self):
        if not self.bstack1llll111l1l1_opy_:
            self.logger.error(bstack1l1l_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡓࡵࠠࡳࡧࡴࡹࡪࡹࡴࠡࡦࡤࡸࡦࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠰ࠥ⅃"))
            return None
        bstack1llll111l1ll_opy_ = None
        test_files = []
        bstack1llll11l111l_opy_ = int(time.time() * 1000) # bstack1llll11l1ll1_opy_ sec
        bstack1llll11l11ll_opy_ = int(self.bstack1llll111l1l1_opy_.get(bstack1l1l_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸࡎࡴࡴࡦࡴࡹࡥࡱࠨ⅄"), self.bstack1llll11l11l1_opy_))
        bstack1llll1111lll_opy_ = int(self.bstack1llll111l1l1_opy_.get(bstack1l1l_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨⅅ"), self.bstack1llll111ll11_opy_)) * 1000
        bstack1llll111ll1l_opy_ = self.bstack1llll111l1l1_opy_.get(bstack1l1l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡕࡳ࡮ࠥⅆ"), None)
        bstack1llll11l1lll_opy_ = self.bstack1llll111l1l1_opy_.get(bstack1l1l_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮ࠥⅇ"), None)
        if bstack1llll11l1lll_opy_ is None and bstack1llll111ll1l_opy_ is None:
            return None
        try:
            while bstack1llll11l1lll_opy_ and (time.time() * 1000 - bstack1llll11l111l_opy_) < bstack1llll1111lll_opy_:
                response = bstack11l1ll1l1l1_opy_.bstack1llll1ll111l_opy_(bstack1llll11l1lll_opy_, {})
                if response and response.get(bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢⅈ")):
                    bstack1llll111l1ll_opy_ = response.get(bstack1l1l_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣⅉ"))
                self.bstack1llll11l1111_opy_ += 1
                if bstack1llll111l1ll_opy_:
                    break
                time.sleep(bstack1llll11l11ll_opy_)
                self.logger.debug(bstack1l1l_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡋ࡫ࡴࡤࡪ࡬ࡲ࡬ࠦ࡯ࡳࡦࡨࡶࡪࡪࠠࡵࡧࡶࡸࡸࠦࡦࡳࡱࡰࠤࡷ࡫ࡳࡶ࡮ࡷࠤ࡚ࡘࡌࠡࡣࡩࡸࡪࡸࠠࡸࡣ࡬ࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࢁࡽࠡࡵࡨࡧࡴࡴࡤࡴ࠰ࠥ⅊").format(bstack1llll11l11ll_opy_))
            if bstack1llll111ll1l_opy_ and not bstack1llll111l1ll_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡌࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡧࡴࡲࡱࠥࡺࡩ࡮ࡧࡲࡹࡹࠦࡕࡓࡎࠥ⅋"))
                response = bstack11l1ll1l1l1_opy_.bstack1llll1ll111l_opy_(bstack1llll111ll1l_opy_, {})
                if response and response.get(bstack1l1l_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦ⅌")):
                    bstack1llll111l1ll_opy_ = response.get(bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧ⅍"))
            if bstack1llll111l1ll_opy_ and len(bstack1llll111l1ll_opy_) > 0:
                for bstack111l1lll1l_opy_ in bstack1llll111l1ll_opy_:
                    file_path = bstack111l1lll1l_opy_.get(bstack1l1l_opy_ (u"ࠢࡧ࡫࡯ࡩࡕࡧࡴࡩࠤⅎ"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll111l1ll_opy_:
                return None
            self.logger.debug(bstack1l1l_opy_ (u"ࠣ࡝ࡪࡩࡹࡕࡲࡥࡧࡵࡩࡩ࡚ࡥࡴࡶࡉ࡭ࡱ࡫ࡳ࡞ࠢࡒࡶࡩ࡫ࡲࡦࡦࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡳࡧࡦࡩ࡮ࡼࡥࡥ࠼ࠣࡿࢂࠨ⅏").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠤ࡞࡫ࡪࡺࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡩࡩࡹࡩࡨࡪࡰࡪࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠼ࠣࡿࢂࠨ⅐").format(e))
            return None
    def bstack1111llll1ll_opy_(self):
        bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳࠡࡶ࡫ࡩࠥࡩ࡯ࡶࡰࡷࠤࡴ࡬ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡇࡐࡊࠢࡦࡥࡱࡲࡳࠡ࡯ࡤࡨࡪ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ⅑")
        return self.bstack1llll11l1111_opy_