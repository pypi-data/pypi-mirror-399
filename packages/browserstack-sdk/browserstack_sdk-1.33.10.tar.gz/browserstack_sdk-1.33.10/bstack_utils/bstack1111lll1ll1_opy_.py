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
import time
from bstack_utils.bstack11l1lll11ll_opy_ import bstack11l1ll1lll1_opy_
from bstack_utils.constants import bstack11l1l1l11ll_opy_
from bstack_utils.helper import get_host_info, bstack111lllllll1_opy_
class bstack1111lll11ll_opy_:
    bstack11111l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡎࡡ࡯ࡦ࡯ࡩࡸࠦࡴࡦࡵࡷࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡷࡪࡶ࡫ࠤࡹ࡮ࡥࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡴࡧࡵࡺࡪࡸ࠮ࠋࠢࠣࠤࠥࠨࠢࠣ℆")
    def __init__(self, config, logger):
        bstack11111l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡧࡴࡴࡦࡪࡩ࠽ࠤࡩ࡯ࡣࡵ࠮ࠣࡸࡪࡹࡴࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡥࡲࡲ࡫࡯ࡧࠋࠢࠣࠤࠥࠦࠠࠡࠢ࠽ࡴࡦࡸࡡ࡮ࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡡࡶࡸࡷࡧࡴࡦࡩࡼ࠾ࠥࡹࡴࡳ࠮ࠣࡸࡪࡹࡴࠡࡱࡵࡨࡪࡸࡩ࡯ࡩࠣࡷࡹࡸࡡࡵࡧࡪࡽࠥࡴࡡ࡮ࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢℇ")
        self.config = config
        self.logger = logger
        self.bstack1llll11l111l_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳ࡸࡶ࡬ࡪࡶ࠰ࡸࡪࡹࡴࡴࠤ℈")
        self.bstack1llll11l1l11_opy_ = None
        self.bstack1llll11ll11l_opy_ = 60
        self.bstack1llll11l11ll_opy_ = 5
        self.bstack1llll111ll11_opy_ = 0
    def bstack1111lll11l1_opy_(self, test_files, orchestration_strategy, orchestration_metadata={}):
        bstack11111l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡏ࡮ࡪࡶ࡬ࡥࡹ࡫ࡳࠡࡶ࡫ࡩࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡶࡪࡷࡵࡦࡵࡷࠤࡦࡴࡤࠡࡵࡷࡳࡷ࡫ࡳࠡࡶ࡫ࡩࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡳࡳࡱࡲࡩ࡯ࡩ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣ℉")
        self.logger.debug(bstack11111l_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡋࡱ࡭ࡹ࡯ࡡࡵ࡫ࡱ࡫ࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡻ࡮ࡺࡨࠡࡵࡷࡶࡦࡺࡥࡨࡻ࠽ࠤࢀࢃࠢℊ").format(orchestration_strategy))
        try:
            bstack1llll11ll111_opy_ = []
            bstack11111l_opy_ (u"ࠥࠦࠧ࡝ࡥࠡࡹ࡬ࡰࡱࠦ࡮ࡰࡶࠣࡪࡪࡺࡣࡩࠢࡪ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡ࡫ࡶࠤࡸࡵࡵࡳࡥࡨࠤ࡮ࡹࠠࡵࡻࡳࡩࠥࡵࡦࠡࡣࡵࡶࡦࡿࠠࡢࡰࡧࠤ࡮ࡺࠧࡴࠢࡨࡰࡪࡳࡥ࡯ࡶࡶࠤࡦࡸࡥࠡࡱࡩࠤࡹࡿࡰࡦࠢࡧ࡭ࡨࡺࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡥࡤࡣࡸࡷࡪࠦࡩ࡯ࠢࡷ࡬ࡦࡺࠠࡤࡣࡶࡩ࠱ࠦࡵࡴࡧࡵࠤ࡭ࡧࡳࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡱࡺࡲࡴࡪ࠯ࡵࡩࡵࡵࠠࡴࡱࡸࡶࡨ࡫ࠠࡸ࡫ࡷ࡬ࠥ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠥ࡯࡮ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠢࠣࠤℋ")
            source = orchestration_metadata[bstack11111l_opy_ (u"ࠫࡷࡻ࡮ࡠࡵࡰࡥࡷࡺ࡟ࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠪℌ")].get(bstack11111l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬℍ"), [])
            bstack1llll11l1l1l_opy_ = isinstance(source, list) and all(isinstance(src, dict) and src is not None for src in source) and len(source) > 0
            if orchestration_metadata[bstack11111l_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬℎ")].get(bstack11111l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨℏ"), False) and not bstack1llll11l1l1l_opy_:
                bstack1llll11ll111_opy_ = bstack111lllllll1_opy_(source) # bstack1llll111l11l_opy_-repo is handled bstack1llll11l1111_opy_
            payload = {
                bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢℐ"): [{bstack11111l_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡐࡢࡶ࡫ࠦℑ"): f} for f in test_files],
                bstack11111l_opy_ (u"ࠥࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡖࡸࡷࡧࡴࡦࡩࡼࠦℒ"): orchestration_strategy,
                bstack11111l_opy_ (u"ࠦࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡑࡪࡺࡡࡥࡣࡷࡥࠧℓ"): orchestration_metadata,
                bstack11111l_opy_ (u"ࠧࡴ࡯ࡥࡧࡌࡲࡩ࡫ࡸࠣ℔"): int(os.environ.get(bstack11111l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡔࡏࡅࡇࡢࡍࡓࡊࡅ࡙ࠤℕ")) or bstack11111l_opy_ (u"ࠢ࠱ࠤ№")),
                bstack11111l_opy_ (u"ࠣࡶࡲࡸࡦࡲࡎࡰࡦࡨࡷࠧ℗"): int(os.environ.get(bstack11111l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡒࡘࡆࡒ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦ℘")) or bstack11111l_opy_ (u"ࠥ࠵ࠧℙ")),
                bstack11111l_opy_ (u"ࠦࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠤℚ"): self.config.get(bstack11111l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪℛ"), bstack11111l_opy_ (u"࠭ࠧℜ")),
                bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠥℝ"): self.config.get(bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ℞"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡓࡷࡱࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢ℟"): os.environ.get(bstack11111l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡔࡘࡒࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠤ℠"), bstack11111l_opy_ (u"ࠦࠧ℡")),
                bstack11111l_opy_ (u"ࠧ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠢ™"): get_host_info(),
                bstack11111l_opy_ (u"ࠨࡰࡳࡆࡨࡸࡦ࡯࡬ࡴࠤ℣"): bstack1llll11ll111_opy_
            }
            self.logger.debug(bstack11111l_opy_ (u"ࠢ࡜ࡵࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࡢࠦࡓࡦࡰࡧ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶ࠾ࠥࢁࡽࠣℤ").format(payload))
            response = bstack11l1ll1lll1_opy_.bstack1llll1lll1ll_opy_(self.bstack1llll11l111l_opy_, payload)
            if response:
                self.bstack1llll11l1l11_opy_ = self._1llll111ll1l_opy_(response)
                self.logger.debug(bstack11111l_opy_ (u"ࠣ࡝ࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡣࠠࡔࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠦ℥").format(self.bstack1llll11l1l11_opy_))
            else:
                self.logger.error(bstack11111l_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤ࡬࡫ࡴࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠯ࠤΩ"))
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡨࡲࡩ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࡀ࠺ࠡࡽࢀࠦ℧").format(e))
    def _1llll111ll1l_opy_(self, response):
        bstack11111l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡹ࡮ࡥࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡁࡑࡋࠣࡶࡪࡹࡰࡰࡰࡶࡩࠥࡧ࡮ࡥࠢࡨࡼࡹࡸࡡࡤࡶࡶࠤࡷ࡫࡬ࡦࡸࡤࡲࡹࠦࡦࡪࡧ࡯ࡨࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦℨ")
        bstack11l1l1l11l_opy_ = {}
        bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨ℩")] = response.get(bstack11111l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢK"), self.bstack1llll11ll11l_opy_)
        bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤÅ")] = response.get(bstack11111l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮ࠥℬ"), self.bstack1llll11l11ll_opy_)
        bstack1llll111lll1_opy_ = response.get(bstack11111l_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡗࡵࡰࠧℭ"))
        bstack1llll111l1ll_opy_ = response.get(bstack11111l_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷ࡙ࡷࡲࠢ℮"))
        if bstack1llll111lll1_opy_:
            bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷ࡙ࡷࡲࠢℯ")] = bstack1llll111lll1_opy_.split(bstack11l1l1l11ll_opy_ + bstack11111l_opy_ (u"ࠧ࠵ࠢℰ"))[1] if bstack11l1l1l11ll_opy_ + bstack11111l_opy_ (u"ࠨ࠯ࠣℱ") in bstack1llll111lll1_opy_ else bstack1llll111lll1_opy_
        else:
            bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮ࠥℲ")] = None
        if bstack1llll111l1ll_opy_:
            bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰࠧℳ")] = bstack1llll111l1ll_opy_.split(bstack11l1l1l11ll_opy_ + bstack11111l_opy_ (u"ࠤ࠲ࠦℴ"))[1] if bstack11l1l1l11ll_opy_ + bstack11111l_opy_ (u"ࠥ࠳ࠧℵ") in bstack1llll111l1ll_opy_ else bstack1llll111l1ll_opy_
        else:
            bstack11l1l1l11l_opy_[bstack11111l_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣℶ")] = None
        if (
            response.get(bstack11111l_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨℷ")) is None or
            response.get(bstack11111l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡉ࡯ࡶࡨࡶࡻࡧ࡬ࠣℸ")) is None or
            response.get(bstack11111l_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦℹ")) is None or
            response.get(bstack11111l_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦ℺")) is None
        ):
            self.logger.debug(bstack11111l_opy_ (u"ࠤ࡞ࡴࡷࡵࡣࡦࡵࡶࡣࡸࡶ࡬ࡪࡶࡢࡸࡪࡹࡴࡴࡡࡵࡩࡸࡶ࡯࡯ࡵࡨࡡࠥࡘࡥࡤࡧ࡬ࡺࡪࡪࠠ࡯ࡷ࡯ࡰࠥࡼࡡ࡭ࡷࡨࠬࡸ࠯ࠠࡧࡱࡵࠤࡸࡵ࡭ࡦࠢࡤࡸࡹࡸࡩࡣࡷࡷࡩࡸࠦࡩ࡯ࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡂࡒࡌࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠨ℻"))
        return bstack11l1l1l11l_opy_
    def bstack1111lll1l1l_opy_(self):
        if not self.bstack1llll11l1l11_opy_:
            self.logger.error(bstack11111l_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡓࡵࠠࡳࡧࡴࡹࡪࡹࡴࠡࡦࡤࡸࡦࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠰ࠥℼ"))
            return None
        bstack1llll11l11l1_opy_ = None
        test_files = []
        bstack1llll11l1ll1_opy_ = int(time.time() * 1000) # bstack1llll11l1lll_opy_ sec
        bstack1llll111l1l1_opy_ = int(self.bstack1llll11l1l11_opy_.get(bstack11111l_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸࡎࡴࡴࡦࡴࡹࡥࡱࠨℽ"), self.bstack1llll11l11ll_opy_))
        bstack1llll111llll_opy_ = int(self.bstack1llll11l1l11_opy_.get(bstack11111l_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨℾ"), self.bstack1llll11ll11l_opy_)) * 1000
        bstack1llll111l1ll_opy_ = self.bstack1llll11l1l11_opy_.get(bstack11111l_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡕࡳ࡮ࠥℿ"), None)
        bstack1llll111lll1_opy_ = self.bstack1llll11l1l11_opy_.get(bstack11111l_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮ࠥ⅀"), None)
        if bstack1llll111lll1_opy_ is None and bstack1llll111l1ll_opy_ is None:
            return None
        try:
            while bstack1llll111lll1_opy_ and (time.time() * 1000 - bstack1llll11l1ll1_opy_) < bstack1llll111llll_opy_:
                response = bstack11l1ll1lll1_opy_.bstack1llll1ll11ll_opy_(bstack1llll111lll1_opy_, {})
                if response and response.get(bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢ⅁")):
                    bstack1llll11l11l1_opy_ = response.get(bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ⅂"))
                self.bstack1llll111ll11_opy_ += 1
                if bstack1llll11l11l1_opy_:
                    break
                time.sleep(bstack1llll111l1l1_opy_)
                self.logger.debug(bstack11111l_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡋ࡫ࡴࡤࡪ࡬ࡲ࡬ࠦ࡯ࡳࡦࡨࡶࡪࡪࠠࡵࡧࡶࡸࡸࠦࡦࡳࡱࡰࠤࡷ࡫ࡳࡶ࡮ࡷࠤ࡚ࡘࡌࠡࡣࡩࡸࡪࡸࠠࡸࡣ࡬ࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࢁࡽࠡࡵࡨࡧࡴࡴࡤࡴ࠰ࠥ⅃").format(bstack1llll111l1l1_opy_))
            if bstack1llll111l1ll_opy_ and not bstack1llll11l11l1_opy_:
                self.logger.debug(bstack11111l_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡌࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡧࡴࡲࡱࠥࡺࡩ࡮ࡧࡲࡹࡹࠦࡕࡓࡎࠥ⅄"))
                response = bstack11l1ll1lll1_opy_.bstack1llll1ll11ll_opy_(bstack1llll111l1ll_opy_, {})
                if response and response.get(bstack11111l_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦⅅ")):
                    bstack1llll11l11l1_opy_ = response.get(bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧⅆ"))
            if bstack1llll11l11l1_opy_ and len(bstack1llll11l11l1_opy_) > 0:
                for bstack111l1ll1l1_opy_ in bstack1llll11l11l1_opy_:
                    file_path = bstack111l1ll1l1_opy_.get(bstack11111l_opy_ (u"ࠢࡧ࡫࡯ࡩࡕࡧࡴࡩࠤⅇ"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll11l11l1_opy_:
                return None
            self.logger.debug(bstack11111l_opy_ (u"ࠣ࡝ࡪࡩࡹࡕࡲࡥࡧࡵࡩࡩ࡚ࡥࡴࡶࡉ࡭ࡱ࡫ࡳ࡞ࠢࡒࡶࡩ࡫ࡲࡦࡦࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡳࡧࡦࡩ࡮ࡼࡥࡥ࠼ࠣࡿࢂࠨⅈ").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠤ࡞࡫ࡪࡺࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡩࡩࡹࡩࡨࡪࡰࡪࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠼ࠣࡿࢂࠨⅉ").format(e))
            return None
    def bstack111l111111l_opy_(self):
        bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳࠡࡶ࡫ࡩࠥࡩ࡯ࡶࡰࡷࠤࡴ࡬ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡇࡐࡊࠢࡦࡥࡱࡲࡳࠡ࡯ࡤࡨࡪ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ⅊")
        return self.bstack1llll111ll11_opy_