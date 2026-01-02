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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack1111lll1ll1_opy_ import bstack1111lll11ll_opy_
from bstack_utils.bstack1ll1ll1111_opy_ import bstack1l11ll1111_opy_
from bstack_utils.helper import bstack1lll11ll11_opy_
import json
class bstack11ll11ll1l_opy_:
    _1ll1lll1ll1_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack1111lllllll_opy_ = bstack1111lll11ll_opy_(self.config, logger)
        self.bstack1ll1ll1111_opy_ = bstack1l11ll1111_opy_.bstack1llll1lll_opy_(config=self.config)
        self.bstack1111llllll1_opy_ = {}
        self.bstack11111l1l1l_opy_ = False
        self.bstack1111lllll11_opy_ = (
            self.__1111lll1lll_opy_()
            and self.bstack1ll1ll1111_opy_ is not None
            and self.bstack1ll1ll1111_opy_.bstack11ll1111_opy_()
            and config.get(bstack11111l_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨẪ"), None) is not None
            and config.get(bstack11111l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧẫ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1llll1lll_opy_(cls, config, logger):
        if cls._1ll1lll1ll1_opy_ is None and config is not None:
            cls._1ll1lll1ll1_opy_ = bstack11ll11ll1l_opy_(config, logger)
        return cls._1ll1lll1ll1_opy_
    def bstack11ll1111_opy_(self):
        bstack11111l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡇࡳࠥࡴ࡯ࡵࠢࡤࡴࡵࡲࡹࠡࡶࡨࡷࡹࠦ࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡹ࡫ࡩࡳࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡕ࠱࠲ࡻࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡩࡳࡧࡢ࡭ࡧࡧࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡒࡶࡩ࡫ࡲࡪࡰࡪࠤ࡮ࡹࠠ࡯ࡱࡷࠤࡪࡴࡡࡣ࡮ࡨࡨࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠡ࡫ࡶࠤࡓࡵ࡮ࡦࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠣ࡭ࡸࠦࡎࡰࡰࡨࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣẬ")
        return self.bstack1111lllll11_opy_ and self.bstack111l1111111_opy_()
    def bstack111l1111111_opy_(self):
        bstack1111llll111_opy_ = os.getenv(bstack11111l_opy_ (u"࠭ࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࡡࡘࡗࡊࡊࠧậ"), self.config.get(bstack11111l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪẮ"), None))
        return bstack1111llll111_opy_ in bstack11l1l1l1111_opy_
    def __1111lll1lll_opy_(self):
        bstack11l1ll111ll_opy_ = False
        for fw in bstack11l1l11111l_opy_:
            if fw in self.config.get(bstack11111l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫắ"), bstack11111l_opy_ (u"ࠩࠪẰ")):
                bstack11l1ll111ll_opy_ = True
        return bstack1lll11ll11_opy_(self.config.get(bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧằ"), bstack11l1ll111ll_opy_))
    def bstack1111llll1ll_opy_(self):
        return (not self.bstack11ll1111_opy_() and
                self.bstack1ll1ll1111_opy_ is not None and self.bstack1ll1ll1111_opy_.bstack11ll1111_opy_())
    def bstack1111lll1l11_opy_(self):
        if not self.bstack1111llll1ll_opy_():
            return
        if self.config.get(bstack11111l_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩẲ"), None) is None or self.config.get(bstack11111l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨẳ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack11111l_opy_ (u"ࠨࡔࡦࡵࡷࠤࡗ࡫࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡥࡤࡲࠬࡺࠠࡸࡱࡵ࡯ࠥࡧࡳࠡࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠤࡴࡸࠠࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠥ࡯ࡳࠡࡰࡸࡰࡱ࠴ࠠࡑ࡮ࡨࡥࡸ࡫ࠠࡴࡧࡷࠤࡦࠦ࡮ࡰࡰ࠰ࡲࡺࡲ࡬ࠡࡸࡤࡰࡺ࡫࠮ࠣẴ"))
        if not self.__1111lll1lll_opy_():
            self.logger.info(bstack11111l_opy_ (u"ࠢࡕࡧࡶࡸࠥࡘࡥࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡦࡥࡳ࠭ࡴࠡࡹࡲࡶࡰࠦࡡࡴࠢࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࠢ࡬ࡷࠥࡪࡩࡴࡣࡥࡰࡪࡪ࠮ࠡࡒ࡯ࡩࡦࡹࡥࠡࡧࡱࡥࡧࡲࡥࠡ࡫ࡷࠤ࡫ࡸ࡯࡮ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠥ࡬ࡩ࡭ࡧ࠱ࠦẵ"))
    def bstack1111llll1l1_opy_(self):
        return self.bstack11111l1l1l_opy_
    def bstack1lllllllll1_opy_(self, bstack1111lllll1l_opy_):
        self.bstack11111l1l1l_opy_ = bstack1111lllll1l_opy_
        self.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡥࡥࠤẶ"), bstack1111lllll1l_opy_)
    def bstack1111111lll_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack11111l_opy_ (u"ࠤ࡞ࡶࡪࡵࡲࡥࡧࡵࡣࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫ࡳ࡞ࠢࡑࡳࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡳࡶࡴࡼࡩࡥࡧࡧࠤ࡫ࡵࡲࠡࡱࡵࡨࡪࡸࡩ࡯ࡩ࠱ࠦặ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack1ll1ll1111_opy_.bstack1111llll11l_opy_()
            if self.bstack1ll1ll1111_opy_ is not None:
                orchestration_strategy = self.bstack1ll1ll1111_opy_.bstack11l111l11l_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack11111l_opy_ (u"ࠥࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡹࡸࡡࡵࡧࡪࡽࠥ࡯ࡳࠡࡐࡲࡲࡪ࠴ࠠࡄࡣࡱࡲࡴࡺࠠࡱࡴࡲࡧࡪ࡫ࡤࠡࡹ࡬ࡸ࡭ࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠳ࠨẸ"))
                return None
            self.logger.info(bstack11111l_opy_ (u"ࠦࡗ࡫࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡽࡩࡵࡪࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡹࡸࡡࡵࡧࡪࡽ࠿ࠦࡻࡾࠤẹ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack11111l_opy_ (u"࡛ࠧࡳࡪࡰࡪࠤࡈࡒࡉࠡࡨ࡯ࡳࡼࠦࡦࡰࡴࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴ࠮ࠣẺ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack11111l_opy_ (u"ࠨࡕࡴ࡫ࡱ࡫ࠥࡹࡤ࡬ࠢࡩࡰࡴࡽࠠࡧࡱࡵࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࠤẻ"))
                self.bstack1111lllllll_opy_.bstack1111lll11l1_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack1111lllllll_opy_.bstack1111lll1l1l_opy_()
            if not ordered_test_files:
                return None
            self.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠢࡶࡲ࡯ࡳࡦࡪࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡇࡴࡻ࡮ࡵࠤẼ"), len(test_files))
            self.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠣࡰࡲࡨࡪࡏ࡮ࡥࡧࡻࠦẽ"), int(os.environ.get(bstack11111l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡐࡒࡈࡊࡥࡉࡏࡆࡈ࡜ࠧẾ")) or bstack11111l_opy_ (u"ࠥ࠴ࠧế")))
            self.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠦࡹࡵࡴࡢ࡮ࡑࡳࡩ࡫ࡳࠣỀ"), int(os.environ.get(bstack11111l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡆࡓ࡚ࡔࡔࠣề")) or bstack11111l_opy_ (u"ࠨ࠱ࠣỂ")))
            self.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠢࡥࡱࡺࡲࡱࡵࡡࡥࡧࡧࡘࡪࡹࡴࡇ࡫࡯ࡩࡸࡉ࡯ࡶࡰࡷࠦể"), len(ordered_test_files))
            self.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠣࡵࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࡆࡖࡉࡄࡣ࡯ࡰࡈࡵࡵ࡯ࡶࠥỄ"), self.bstack1111lllllll_opy_.bstack111l111111l_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠤ࡞ࡶࡪࡵࡲࡥࡧࡵࡣࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫ࡳ࡞ࠢࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡨࡲࡡࡴࡵࡨࡷ࠿ࠦࡻࡾࠤễ").format(e))
        return None
    def bstack111111111l_opy_(self, key, value):
        self.bstack1111llllll1_opy_[key] = value
    def bstack11l1l11ll1_opy_(self):
        return self.bstack1111llllll1_opy_