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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack1111lllll11_opy_ import bstack1111llllll1_opy_
from bstack_utils.bstack1l11l1l1ll_opy_ import bstack111l1111l_opy_
from bstack_utils.helper import bstack1l1l1111l1_opy_
import json
class bstack11ll11l11l_opy_:
    _1ll1ll1l1ll_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack1111lll111l_opy_ = bstack1111llllll1_opy_(self.config, logger)
        self.bstack1l11l1l1ll_opy_ = bstack111l1111l_opy_.bstack1l1ll1l111_opy_(config=self.config)
        self.bstack1111lll1lll_opy_ = {}
        self.bstack111111llll_opy_ = False
        self.bstack1111lll1l1l_opy_ = (
            self.__1111llll111_opy_()
            and self.bstack1l11l1l1ll_opy_ is not None
            and self.bstack1l11l1l1ll_opy_.bstack1lll1ll1l_opy_()
            and config.get(bstack1l1l_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨằ"), None) is not None
            and config.get(bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧẲ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1l1ll1l111_opy_(cls, config, logger):
        if cls._1ll1ll1l1ll_opy_ is None and config is not None:
            cls._1ll1ll1l1ll_opy_ = bstack11ll11l11l_opy_(config, logger)
        return cls._1ll1ll1l1ll_opy_
    def bstack1lll1ll1l_opy_(self):
        bstack1l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡇࡳࠥࡴ࡯ࡵࠢࡤࡴࡵࡲࡹࠡࡶࡨࡷࡹࠦ࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡹ࡫ࡩࡳࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡕ࠱࠲ࡻࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡩࡳࡧࡢ࡭ࡧࡧࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡒࡶࡩ࡫ࡲࡪࡰࡪࠤ࡮ࡹࠠ࡯ࡱࡷࠤࡪࡴࡡࡣ࡮ࡨࡨࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠡ࡫ࡶࠤࡓࡵ࡮ࡦࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠣ࡭ࡸࠦࡎࡰࡰࡨࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣẳ")
        return self.bstack1111lll1l1l_opy_ and self.bstack1111lll1l11_opy_()
    def bstack1111lll1l11_opy_(self):
        bstack1111lll11l1_opy_ = os.getenv(bstack1l1l_opy_ (u"࠭ࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࡡࡘࡗࡊࡊࠧẴ"), self.config.get(bstack1l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪẵ"), None))
        return bstack1111lll11l1_opy_ in bstack11l1l1l1lll_opy_
    def __1111llll111_opy_(self):
        bstack11l1ll1111l_opy_ = False
        for fw in bstack11l11lll1ll_opy_:
            if fw in self.config.get(bstack1l1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫẶ"), bstack1l1l_opy_ (u"ࠩࠪặ")):
                bstack11l1ll1111l_opy_ = True
        return bstack1l1l1111l1_opy_(self.config.get(bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧẸ"), bstack11l1ll1111l_opy_))
    def bstack1111lll1111_opy_(self):
        return (not self.bstack1lll1ll1l_opy_() and
                self.bstack1l11l1l1ll_opy_ is not None and self.bstack1l11l1l1ll_opy_.bstack1lll1ll1l_opy_())
    def bstack1111llll1l1_opy_(self):
        if not self.bstack1111lll1111_opy_():
            return
        if self.config.get(bstack1l1l_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩẹ"), None) is None or self.config.get(bstack1l1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨẺ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack1l1l_opy_ (u"ࠨࡔࡦࡵࡷࠤࡗ࡫࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡥࡤࡲࠬࡺࠠࡸࡱࡵ࡯ࠥࡧࡳࠡࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠤࡴࡸࠠࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠥ࡯ࡳࠡࡰࡸࡰࡱ࠴ࠠࡑ࡮ࡨࡥࡸ࡫ࠠࡴࡧࡷࠤࡦࠦ࡮ࡰࡰ࠰ࡲࡺࡲ࡬ࠡࡸࡤࡰࡺ࡫࠮ࠣẻ"))
        if not self.__1111llll111_opy_():
            self.logger.info(bstack1l1l_opy_ (u"ࠢࡕࡧࡶࡸࠥࡘࡥࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡦࡥࡳ࠭ࡴࠡࡹࡲࡶࡰࠦࡡࡴࠢࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࠢ࡬ࡷࠥࡪࡩࡴࡣࡥࡰࡪࡪ࠮ࠡࡒ࡯ࡩࡦࡹࡥࠡࡧࡱࡥࡧࡲࡥࠡ࡫ࡷࠤ࡫ࡸ࡯࡮ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠥ࡬ࡩ࡭ࡧ࠱ࠦẼ"))
    def bstack1111lll1ll1_opy_(self):
        return self.bstack111111llll_opy_
    def bstack111111111l_opy_(self, bstack1111lllllll_opy_):
        self.bstack111111llll_opy_ = bstack1111lllllll_opy_
        self.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡥࡥࠤẽ"), bstack1111lllllll_opy_)
    def bstack1llllllll11_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡞ࡶࡪࡵࡲࡥࡧࡵࡣࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫ࡳ࡞ࠢࡑࡳࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡳࡶࡴࡼࡩࡥࡧࡧࠤ࡫ࡵࡲࠡࡱࡵࡨࡪࡸࡩ࡯ࡩ࠱ࠦẾ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack1l11l1l1ll_opy_.bstack1111lllll1l_opy_()
            if self.bstack1l11l1l1ll_opy_ is not None:
                orchestration_strategy = self.bstack1l11l1l1ll_opy_.bstack1lll11ll11_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack1l1l_opy_ (u"ࠥࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡹࡸࡡࡵࡧࡪࡽࠥ࡯ࡳࠡࡐࡲࡲࡪ࠴ࠠࡄࡣࡱࡲࡴࡺࠠࡱࡴࡲࡧࡪ࡫ࡤࠡࡹ࡬ࡸ࡭ࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠳ࠨế"))
                return None
            self.logger.info(bstack1l1l_opy_ (u"ࠦࡗ࡫࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡽࡩࡵࡪࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡹࡸࡡࡵࡧࡪࡽ࠿ࠦࡻࡾࠤỀ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack1l1l_opy_ (u"࡛ࠧࡳࡪࡰࡪࠤࡈࡒࡉࠡࡨ࡯ࡳࡼࠦࡦࡰࡴࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴ࠮ࠣề"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack1l1l_opy_ (u"ࠨࡕࡴ࡫ࡱ࡫ࠥࡹࡤ࡬ࠢࡩࡰࡴࡽࠠࡧࡱࡵࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࠤỂ"))
                self.bstack1111lll111l_opy_.bstack1111lll11ll_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack1111lll111l_opy_.bstack1111llll11l_opy_()
            if not ordered_test_files:
                return None
            self.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠢࡶࡲ࡯ࡳࡦࡪࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡇࡴࡻ࡮ࡵࠤể"), len(test_files))
            self.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠣࡰࡲࡨࡪࡏ࡮ࡥࡧࡻࠦỄ"), int(os.environ.get(bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡐࡒࡈࡊࡥࡉࡏࡆࡈ࡜ࠧễ")) or bstack1l1l_opy_ (u"ࠥ࠴ࠧỆ")))
            self.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠦࡹࡵࡴࡢ࡮ࡑࡳࡩ࡫ࡳࠣệ"), int(os.environ.get(bstack1l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡆࡓ࡚ࡔࡔࠣỈ")) or bstack1l1l_opy_ (u"ࠨ࠱ࠣỉ")))
            self.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠢࡥࡱࡺࡲࡱࡵࡡࡥࡧࡧࡘࡪࡹࡴࡇ࡫࡯ࡩࡸࡉ࡯ࡶࡰࡷࠦỊ"), len(ordered_test_files))
            self.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠣࡵࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࡆࡖࡉࡄࡣ࡯ࡰࡈࡵࡵ࡯ࡶࠥị"), self.bstack1111lll111l_opy_.bstack1111llll1ll_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡞ࡶࡪࡵࡲࡥࡧࡵࡣࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫ࡳ࡞ࠢࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡨࡲࡡࡴࡵࡨࡷ࠿ࠦࡻࡾࠤỌ").format(e))
        return None
    def bstack1lllllllll1_opy_(self, key, value):
        self.bstack1111lll1lll_opy_[key] = value
    def bstack1ll1l11ll1_opy_(self):
        return self.bstack1111lll1lll_opy_