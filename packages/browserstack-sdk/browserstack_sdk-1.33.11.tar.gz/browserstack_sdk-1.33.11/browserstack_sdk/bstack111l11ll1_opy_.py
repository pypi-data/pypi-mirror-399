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
import multiprocessing
import os
import json
from time import sleep
import time
import bstack_utils.accessibility as bstack1lllllll11_opy_
from browserstack_sdk.bstack1ll1l11lll_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack1l1lll1ll_opy_, bstack11111l11l1_opy_
from bstack_utils.bstack1l11l1l1ll_opy_ import bstack111l1111l_opy_
from bstack_utils.constants import bstack11111111l1_opy_
from bstack_utils.bstack11lllll11_opy_ import bstack11ll11l11l_opy_
from bstack_utils.bstack111111l111_opy_ import bstack11111l1l1l_opy_
class bstack1l11111l1_opy_:
    def __init__(self, args, logger, bstack11111111ll_opy_, bstack1lllllll1ll_opy_):
        self.args = args
        self.logger = logger
        self.bstack11111111ll_opy_ = bstack11111111ll_opy_
        self.bstack1lllllll1ll_opy_ = bstack1lllllll1ll_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack11ll111ll_opy_ = []
        self.bstack1111111ll1_opy_ = []
        self.bstack1l1ll1111_opy_ = []
        self.bstack1lllllll1l1_opy_ = self.bstack111lll1l_opy_()
        self.bstack1l1l111111_opy_ = -1
    def bstack11lllll1l1_opy_(self, bstack1llllll1lll_opy_):
        self.parse_args()
        self.bstack11111l1111_opy_()
        self.bstack11111l1l11_opy_(bstack1llllll1lll_opy_)
        self.bstack11111l1ll1_opy_()
    def bstack1111llll1_opy_(self):
        bstack11lllll11_opy_ = bstack11ll11l11l_opy_.bstack1l1ll1l111_opy_(self.bstack11111111ll_opy_, self.logger)
        if bstack11lllll11_opy_ is None:
            self.logger.warn(bstack1l1l_opy_ (u"ࠥࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣ࡬ࡦࡴࡤ࡭ࡧࡵࠤ࡮ࡹࠠ࡯ࡱࡷࠤ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥࡥ࠰ࠣࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠳ࠨ႕"))
            return
        bstack111111llll_opy_ = False
        bstack11lllll11_opy_.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠦࡪࡴࡡࡣ࡮ࡨࡨࠧ႖"), bstack11lllll11_opy_.bstack1lll1ll1l_opy_())
        start_time = time.time()
        if bstack11lllll11_opy_.bstack1lll1ll1l_opy_():
            test_files = self.bstack11111l11ll_opy_()
            bstack111111llll_opy_ = True
            bstack1llllllllll_opy_ = bstack11lllll11_opy_.bstack1llllllll11_opy_(test_files)
            if bstack1llllllllll_opy_:
                self.bstack11ll111ll_opy_ = [os.path.normpath(item) for item in bstack1llllllllll_opy_]
                self.__11111l1lll_opy_()
                bstack11lllll11_opy_.bstack111111111l_opy_(bstack111111llll_opy_)
                self.logger.info(bstack1l1l_opy_ (u"࡚ࠧࡥࡴࡶࡶࠤࡷ࡫࡯ࡳࡦࡨࡶࡪࡪࠠࡶࡵ࡬ࡲ࡬ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡀࠠࡼࡿࠥ႗").format(self.bstack11ll111ll_opy_))
            else:
                self.logger.info(bstack1l1l_opy_ (u"ࠨࡎࡰࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࠦࡷࡦࡴࡨࠤࡷ࡫࡯ࡳࡦࡨࡶࡪࡪࠠࡣࡻࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦ႘"))
        bstack11lllll11_opy_.bstack1lllllllll1_opy_(bstack1l1l_opy_ (u"ࠢࡵ࡫ࡰࡩ࡙ࡧ࡫ࡦࡰࡗࡳࡆࡶࡰ࡭ࡻࠥ႙"), int((time.time() - start_time) * 1000)) # bstack111111l1l1_opy_ to bstack11111l111l_opy_
    def __11111l1lll_opy_(self):
        bstack1l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡱ࡮ࡤࡧࡪࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮ࡳࠡ࡫ࡱࠤࡈࡒࡉࠡࡨ࡯ࡥ࡬ࡹࠠࡸ࡫ࡷ࡬ࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵࡧࡧࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮ࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡪࡸࡶࡦࡴࠣࡶࡪࡺࡵࡳࡰࡶࠤࡷ࡫࡯ࡳࡦࡨࡶࡪࡪࠠࡧ࡫࡯ࡩࠥࡴࡡ࡮ࡧࡶ࠰ࠥࡧ࡮ࡥࠢࡺࡩࠥࡹࡩ࡮ࡲ࡯ࡽࠥࡻࡰࡥࡣࡷࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࡴࡩࡧࠣࡇࡑࡏࠠࡢࡴࡪࡷࠥࡺ࡯ࠡࡷࡶࡩࠥࡺࡨࡰࡵࡨࠤ࡫࡯࡬ࡦࡵ࠱ࠤ࡚ࡹࡥࡳࠩࡶࠤ࡫࡯࡬ࡵࡧࡵ࡭ࡳ࡭ࠠࡧ࡮ࡤ࡫ࡸࠦࠨ࠮࡯࠯ࠤ࠲ࡱࠩࠡࡴࡨࡱࡦ࡯࡮ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡬ࡲࡹࡧࡣࡵࠢࡤࡲࡩࠦࡷࡪ࡮࡯ࠤࡧ࡫ࠠࡢࡲࡳࡰ࡮࡫ࡤࠡࡰࡤࡸࡺࡸࡡ࡭࡮ࡼࠤࡩࡻࡲࡪࡰࡪࠤࡵࡿࡴࡦࡵࡷࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨႚ")
        try:
            if not self.bstack11ll111ll_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠤࡑࡳࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡴࡦࡺࡨࠡࡶࡲࠤࡸ࡫ࡴࠣႛ"))
                return
            bstack1111111l11_opy_ = []
            for flag in self.bstack1111111ll1_opy_:
                if flag.startswith(bstack1l1l_opy_ (u"ࠪ࠱ࠬႜ")):
                    bstack1111111l11_opy_.append(flag)
                    continue
                bstack111111ll1l_opy_ = False
                if bstack1l1l_opy_ (u"ࠫ࠿ࡀࠧႝ") in flag:
                    bstack111111l11l_opy_ = flag.split(bstack1l1l_opy_ (u"ࠬࡀ࠺ࠨ႞"), 1)[0]
                    if os.path.exists(bstack111111l11l_opy_):
                        bstack111111ll1l_opy_ = True
                elif os.path.exists(flag):
                    if os.path.isdir(flag) or (os.path.isfile(flag) and flag.endswith(bstack1l1l_opy_ (u"࠭࠮ࡱࡻࠪ႟"))):
                        bstack111111ll1l_opy_ = True
                if not bstack111111ll1l_opy_:
                    bstack1111111l11_opy_.append(flag)
            bstack1111111l11_opy_.extend(self.bstack11ll111ll_opy_)
            self.bstack1111111ll1_opy_ = bstack1111111l11_opy_
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡥࡥࠢࡶࡩࡱ࡫ࡣࡵࡱࡵࡷ࠿ࠦࡻࡾࠤႠ").format(str(e)))
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack1111111l1l_opy_():
        return bstack11111l1l1l_opy_(bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࠪႡ"))
    def bstack1llllll1ll1_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack1l1l111111_opy_ = -1
        if self.bstack1lllllll1ll_opy_ and bstack1l1l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩႢ") in self.bstack11111111ll_opy_:
            self.bstack1l1l111111_opy_ = int(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪႣ")])
        try:
            bstack1111111111_opy_ = [bstack1l1l_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭Ⴄ"), bstack1l1l_opy_ (u"ࠬ࠳࠭ࡱ࡮ࡸ࡫࡮ࡴࡳࠨႥ"), bstack1l1l_opy_ (u"࠭࠭ࡱࠩႦ")]
            if self.bstack1l1l111111_opy_ >= 0:
                bstack1111111111_opy_.extend([bstack1l1l_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨႧ"), bstack1l1l_opy_ (u"ࠨ࠯ࡱࠫႨ")])
            for arg in bstack1111111111_opy_:
                self.bstack1llllll1ll1_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack11111l1111_opy_(self):
        bstack1111111ll1_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack1111111ll1_opy_ = bstack1111111ll1_opy_
        return self.bstack1111111ll1_opy_
    def bstack111l111l1_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            if not self.bstack1111111l1l_opy_():
                self.logger.warning(bstack11111l11l1_opy_)
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warning(bstack1l1l_opy_ (u"ࠤࠨࡷ࠿ࠦࠥࡴࠤႩ"), bstack1l1lll1ll_opy_, str(e))
    def bstack11111l1l11_opy_(self, bstack1llllll1lll_opy_):
        bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
        if bstack1llllll1lll_opy_:
            self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠪ࠱࠲ࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧႪ"))
            self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"࡙ࠫࡸࡵࡦࠩႫ"))
        if bstack1l1ll1l1_opy_.bstack1llllll1l1l_opy_():
            self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠬ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫႬ"))
            self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"࠭ࡔࡳࡷࡨࠫႭ"))
        self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠧ࠮ࡲࠪႮ"))
        self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡰ࡭ࡷࡪ࡭ࡳ࠭Ⴏ"))
        self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠩ࠰࠱ࡩࡸࡩࡷࡧࡵࠫႰ"))
        self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪႱ"))
        if self.bstack1l1l111111_opy_ > 1:
            self.bstack1111111ll1_opy_.append(bstack1l1l_opy_ (u"ࠫ࠲ࡴࠧႲ"))
            self.bstack1111111ll1_opy_.append(str(self.bstack1l1l111111_opy_))
    def bstack11111l1ll1_opy_(self):
        if bstack111l1111l_opy_.bstack111l11l1_opy_(self.bstack11111111ll_opy_):
             self.bstack1111111ll1_opy_ += [
                bstack11111111l1_opy_.get(bstack1l1l_opy_ (u"ࠬࡸࡥࡳࡷࡱࠫႳ")), str(bstack111l1111l_opy_.bstack1ll111l1l1_opy_(self.bstack11111111ll_opy_)),
                bstack11111111l1_opy_.get(bstack1l1l_opy_ (u"࠭ࡤࡦ࡮ࡤࡽࠬႴ")), str(bstack11111111l1_opy_.get(bstack1l1l_opy_ (u"ࠧࡳࡧࡵࡹࡳ࠳ࡤࡦ࡮ࡤࡽࠬႵ")))
            ]
    def bstack111111lll1_opy_(self):
        bstack1l1ll1111_opy_ = []
        for spec in self.bstack11ll111ll_opy_:
            bstack11l111ll1l_opy_ = [spec]
            bstack11l111ll1l_opy_ += self.bstack1111111ll1_opy_
            bstack1l1ll1111_opy_.append(bstack11l111ll1l_opy_)
        self.bstack1l1ll1111_opy_ = bstack1l1ll1111_opy_
        return bstack1l1ll1111_opy_
    def bstack111lll1l_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack1lllllll1l1_opy_ = True
            return True
        except Exception as e:
            self.bstack1lllllll1l1_opy_ = False
        return self.bstack1lllllll1l1_opy_
    def bstack11l11llll1_opy_(self):
        bstack1l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡍࡥࡵࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡴࡸࡲࡳ࡯࡮ࡨࠢࡷ࡬ࡪࡳࠠࡶࡵ࡬ࡲ࡬ࠦࡰࡺࡶࡨࡷࡹࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡯࡮ࡵ࠼ࠣࡘ࡭࡫ࠠࡵࡱࡷࡥࡱࠦ࡮ࡶ࡯ࡥࡩࡷࠦ࡯ࡧࠢࡷࡩࡸࡺࡳࠡࡥࡲࡰࡱ࡫ࡣࡵࡧࡧ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤႶ")
        try:
            from browserstack_sdk.bstack1111l1111l_opy_ import bstack11111lll1l_opy_
            bstack111111l1ll_opy_ = bstack11111lll1l_opy_(bstack1111l11l11_opy_=self.bstack1111111ll1_opy_)
            if not bstack111111l1ll_opy_.get(bstack1l1l_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪႷ"), False):
                self.logger.error(bstack1l1l_opy_ (u"ࠥࡘࡪࡹࡴࠡࡥࡲࡹࡳࡺࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧ࠾ࠥࢁࡽࠣႸ").format(bstack111111l1ll_opy_.get(bstack1l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪႹ"), bstack1l1l_opy_ (u"࡛ࠬ࡮࡬ࡰࡲࡻࡳࠦࡥࡳࡴࡲࡶࠬႺ"))))
                return 0
            count = bstack111111l1ll_opy_.get(bstack1l1l_opy_ (u"࠭ࡣࡰࡷࡱࡸࠬႻ"), 0)
            self.logger.info(bstack1l1l_opy_ (u"ࠢࡕࡱࡷࡥࡱࠦࡴࡦࡵࡷࡷࠥࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤ࠻ࠢࡾࢁࠧႼ").format(count))
            return count
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡦࡳࡺࡴࡴ࠻ࠢࡾࢁࠧႽ").format(e))
            return 0
    def bstack1lll11l11l_opy_(self, bstack11111ll111_opy_, bstack11lllll1l1_opy_):
        bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩႾ")] = self.bstack11111111ll_opy_
        multiprocessing.set_start_method(bstack1l1l_opy_ (u"ࠪࡷࡵࡧࡷ࡯ࠩႿ"))
        bstack11ll11llll_opy_ = []
        manager = multiprocessing.Manager()
        bstack1lllllll111_opy_ = manager.list()
        if bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧჀ") in self.bstack11111111ll_opy_:
            for index, platform in enumerate(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨჁ")]):
                bstack11ll11llll_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack11111ll111_opy_,
                                                            args=(self.bstack1111111ll1_opy_, bstack11lllll1l1_opy_, bstack1lllllll111_opy_)))
            bstack1llllllll1l_opy_ = len(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩჂ")])
        else:
            bstack11ll11llll_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack11111ll111_opy_,
                                                        args=(self.bstack1111111ll1_opy_, bstack11lllll1l1_opy_, bstack1lllllll111_opy_)))
            bstack1llllllll1l_opy_ = 1
        i = 0
        for t in bstack11ll11llll_opy_:
            os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧჃ")] = str(i)
            if bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫჄ") in self.bstack11111111ll_opy_:
                os.environ[bstack1l1l_opy_ (u"ࠩࡆ࡙ࡗࡘࡅࡏࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡊࡁࡕࡃࠪჅ")] = json.dumps(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭჆")][i % bstack1llllllll1l_opy_])
            i += 1
            t.start()
        for t in bstack11ll11llll_opy_:
            t.join()
        return list(bstack1lllllll111_opy_)
    @staticmethod
    def bstack1ll1lllll1_opy_(driver, bstack1lllllll11l_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡹ࡫࡭ࠨჇ"), None)
        if item and getattr(item, bstack1l1l_opy_ (u"ࠬࡥࡡ࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡦࡥࡸ࡫ࠧ჈"), None) and not getattr(item, bstack1l1l_opy_ (u"࠭࡟ࡢ࠳࠴ࡽࡤࡹࡴࡰࡲࡢࡨࡴࡴࡥࠨ჉"), False):
            logger.info(
                bstack1l1l_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡵ࡮ࠡࡪࡤࡷࠥ࡫࡮ࡥࡧࡧ࠲ࠥࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡩࡳࡷࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡴࡦࡵࡷ࡭ࡳ࡭ࠠࡪࡵࠣࡹࡳࡪࡥࡳࡹࡤࡽ࠳ࠨ჊"))
            bstack1111111lll_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1lllllll11_opy_.bstack11llll1ll_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)
    def bstack11111l11ll_opy_(self):
        bstack1l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࠦࡴࡩࡧࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡶࡲࠤࡧ࡫ࠠࡦࡺࡨࡧࡺࡺࡥࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢ჋")
        try:
            from browserstack_sdk.bstack1111l1111l_opy_ import bstack11111lll1l_opy_
            bstack111111ll11_opy_ = bstack11111lll1l_opy_(bstack1111l11l11_opy_=self.bstack1111111ll1_opy_)
            if not bstack111111ll11_opy_.get(bstack1l1l_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ჌"), False):
                self.logger.error(bstack1l1l_opy_ (u"ࠥࡘࡪࡹࡴࠡࡨ࡬ࡰࡪࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࢀࢃࠢჍ").format(bstack111111ll11_opy_.get(bstack1l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ჎"), bstack1l1l_opy_ (u"࡛ࠬ࡮࡬ࡰࡲࡻࡳࠦࡥࡳࡴࡲࡶࠬ჏"))))
                return []
            test_files = bstack111111ll11_opy_.get(bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡫࡯࡬ࡦࡵࠪა"), [])
            count = bstack111111ll11_opy_.get(bstack1l1l_opy_ (u"ࠧࡤࡱࡸࡲࡹ࠭ბ"), 0)
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡅࡲࡰࡱ࡫ࡣࡵࡧࡧࠤࢀࢃࠠࡵࡧࡶࡸࡸࠦࡩ࡯ࠢࡾࢁࠥ࡬ࡩ࡭ࡧࡶࠦგ").format(count, len(test_files)))
            return test_files
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡪࡵࡳ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࡀࠠࡼࡿࠥდ").format(e))
            return []