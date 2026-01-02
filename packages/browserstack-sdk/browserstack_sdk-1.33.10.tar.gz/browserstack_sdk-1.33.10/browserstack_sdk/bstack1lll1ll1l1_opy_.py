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
import multiprocessing
import os
import json
from time import sleep
import time
import bstack_utils.accessibility as bstack1l1l11ll11_opy_
from browserstack_sdk.bstack1l1lllllll_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack11llllll1l_opy_, bstack111111ll1l_opy_
from bstack_utils.bstack1ll1ll1111_opy_ import bstack1l11ll1111_opy_
from bstack_utils.constants import bstack1llllll1lll_opy_
from bstack_utils.bstack1ll1llllll_opy_ import bstack11ll11ll1l_opy_
from bstack_utils.bstack111111l1l1_opy_ import bstack1llllll1ll1_opy_
class bstack1lllll1l1_opy_:
    def __init__(self, args, logger, bstack1lllllll1ll_opy_, bstack11111l11l1_opy_):
        self.args = args
        self.logger = logger
        self.bstack1lllllll1ll_opy_ = bstack1lllllll1ll_opy_
        self.bstack11111l11l1_opy_ = bstack11111l11l1_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack1l1l111l11_opy_ = []
        self.bstack11111111ll_opy_ = []
        self.bstack1lll1111l_opy_ = []
        self.bstack11111l111l_opy_ = self.bstack1l1llll11_opy_()
        self.bstack1l1l1l11l1_opy_ = -1
    def bstack1ll11l1lll_opy_(self, bstack1111111111_opy_):
        self.parse_args()
        self.bstack1llllll1l1l_opy_()
        self.bstack111111lll1_opy_(bstack1111111111_opy_)
        self.bstack1llllllllll_opy_()
    def bstack1l11ll1lll_opy_(self):
        bstack1ll1llllll_opy_ = bstack11ll11ll1l_opy_.bstack1llll1lll_opy_(self.bstack1lllllll1ll_opy_, self.logger)
        if bstack1ll1llllll_opy_ is None:
            self.logger.warn(bstack11111l_opy_ (u"ࠥࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣ࡬ࡦࡴࡤ࡭ࡧࡵࠤ࡮ࡹࠠ࡯ࡱࡷࠤ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥࡥ࠰ࠣࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠳ࠨ႕"))
            return
        bstack11111l1l1l_opy_ = False
        bstack1ll1llllll_opy_.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠦࡪࡴࡡࡣ࡮ࡨࡨࠧ႖"), bstack1ll1llllll_opy_.bstack11ll1111_opy_())
        start_time = time.time()
        if bstack1ll1llllll_opy_.bstack11ll1111_opy_():
            test_files = self.bstack11111111l1_opy_()
            bstack11111l1l1l_opy_ = True
            bstack1lllllll1l1_opy_ = bstack1ll1llllll_opy_.bstack1111111lll_opy_(test_files)
            if bstack1lllllll1l1_opy_:
                self.bstack1l1l111l11_opy_ = [os.path.normpath(item) for item in bstack1lllllll1l1_opy_]
                self.__111111l1ll_opy_()
                bstack1ll1llllll_opy_.bstack1lllllllll1_opy_(bstack11111l1l1l_opy_)
                self.logger.info(bstack11111l_opy_ (u"࡚ࠧࡥࡴࡶࡶࠤࡷ࡫࡯ࡳࡦࡨࡶࡪࡪࠠࡶࡵ࡬ࡲ࡬ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡀࠠࡼࡿࠥ႗").format(self.bstack1l1l111l11_opy_))
            else:
                self.logger.info(bstack11111l_opy_ (u"ࠨࡎࡰࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࠦࡷࡦࡴࡨࠤࡷ࡫࡯ࡳࡦࡨࡶࡪࡪࠠࡣࡻࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦ႘"))
        bstack1ll1llllll_opy_.bstack111111111l_opy_(bstack11111l_opy_ (u"ࠢࡵ࡫ࡰࡩ࡙ࡧ࡫ࡦࡰࡗࡳࡆࡶࡰ࡭ࡻࠥ႙"), int((time.time() - start_time) * 1000)) # bstack1111111ll1_opy_ to bstack11111ll111_opy_
    def __111111l1ll_opy_(self):
        bstack11111l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡱ࡮ࡤࡧࡪࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮ࡳࠡ࡫ࡱࠤࡈࡒࡉࠡࡨ࡯ࡥ࡬ࡹࠠࡸ࡫ࡷ࡬ࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵࡧࡧࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮ࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡪࡸࡶࡦࡴࠣࡶࡪࡺࡵࡳࡰࡶࠤࡷ࡫࡯ࡳࡦࡨࡶࡪࡪࠠࡧ࡫࡯ࡩࠥࡴࡡ࡮ࡧࡶ࠰ࠥࡧ࡮ࡥࠢࡺࡩࠥࡹࡩ࡮ࡲ࡯ࡽࠥࡻࡰࡥࡣࡷࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࡴࡩࡧࠣࡇࡑࡏࠠࡢࡴࡪࡷࠥࡺ࡯ࠡࡷࡶࡩࠥࡺࡨࡰࡵࡨࠤ࡫࡯࡬ࡦࡵ࠱ࠤ࡚ࡹࡥࡳࠩࡶࠤ࡫࡯࡬ࡵࡧࡵ࡭ࡳ࡭ࠠࡧ࡮ࡤ࡫ࡸࠦࠨ࠮࡯࠯ࠤ࠲ࡱࠩࠡࡴࡨࡱࡦ࡯࡮ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡬ࡲࡹࡧࡣࡵࠢࡤࡲࡩࠦࡷࡪ࡮࡯ࠤࡧ࡫ࠠࡢࡲࡳࡰ࡮࡫ࡤࠡࡰࡤࡸࡺࡸࡡ࡭࡮ࡼࠤࡩࡻࡲࡪࡰࡪࠤࡵࡿࡴࡦࡵࡷࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨႚ")
        try:
            if not self.bstack1l1l111l11_opy_:
                self.logger.debug(bstack11111l_opy_ (u"ࠤࡑࡳࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡴࡦࡺࡨࠡࡶࡲࠤࡸ࡫ࡴࠣႛ"))
                return
            bstack111111llll_opy_ = []
            for flag in self.bstack11111111ll_opy_:
                if flag.startswith(bstack11111l_opy_ (u"ࠪ࠱ࠬႜ")):
                    bstack111111llll_opy_.append(flag)
                    continue
                bstack111111ll11_opy_ = False
                if bstack11111l_opy_ (u"ࠫ࠿ࡀࠧႝ") in flag:
                    bstack1111111l1l_opy_ = flag.split(bstack11111l_opy_ (u"ࠬࡀ࠺ࠨ႞"), 1)[0]
                    if os.path.exists(bstack1111111l1l_opy_):
                        bstack111111ll11_opy_ = True
                elif os.path.exists(flag):
                    if os.path.isdir(flag) or (os.path.isfile(flag) and flag.endswith(bstack11111l_opy_ (u"࠭࠮ࡱࡻࠪ႟"))):
                        bstack111111ll11_opy_ = True
                if not bstack111111ll11_opy_:
                    bstack111111llll_opy_.append(flag)
            bstack111111llll_opy_.extend(self.bstack1l1l111l11_opy_)
            self.bstack11111111ll_opy_ = bstack111111llll_opy_
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡥࡥࠢࡶࡩࡱ࡫ࡣࡵࡱࡵࡷ࠿ࠦࡻࡾࠤႠ").format(str(e)))
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack11111l11ll_opy_():
        return bstack1llllll1ll1_opy_(bstack11111l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࠪႡ"))
    def bstack1111111l11_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack1l1l1l11l1_opy_ = -1
        if self.bstack11111l11l1_opy_ and bstack11111l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩႢ") in self.bstack1lllllll1ll_opy_:
            self.bstack1l1l1l11l1_opy_ = int(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪႣ")])
        try:
            bstack111111l11l_opy_ = [bstack11111l_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭Ⴄ"), bstack11111l_opy_ (u"ࠬ࠳࠭ࡱ࡮ࡸ࡫࡮ࡴࡳࠨႥ"), bstack11111l_opy_ (u"࠭࠭ࡱࠩႦ")]
            if self.bstack1l1l1l11l1_opy_ >= 0:
                bstack111111l11l_opy_.extend([bstack11111l_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨႧ"), bstack11111l_opy_ (u"ࠨ࠯ࡱࠫႨ")])
            for arg in bstack111111l11l_opy_:
                self.bstack1111111l11_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack1llllll1l1l_opy_(self):
        bstack11111111ll_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack11111111ll_opy_ = bstack11111111ll_opy_
        return self.bstack11111111ll_opy_
    def bstack11ll11ll_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            if not self.bstack11111l11ll_opy_():
                self.logger.warning(bstack111111ll1l_opy_)
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warning(bstack11111l_opy_ (u"ࠤࠨࡷ࠿ࠦࠥࡴࠤႩ"), bstack11llllll1l_opy_, str(e))
    def bstack111111lll1_opy_(self, bstack1111111111_opy_):
        bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
        if bstack1111111111_opy_:
            self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠪ࠱࠲ࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧႪ"))
            self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"࡙ࠫࡸࡵࡦࠩႫ"))
        if bstack11l11l1lll_opy_.bstack111111l111_opy_():
            self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠬ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫႬ"))
            self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"࠭ࡔࡳࡷࡨࠫႭ"))
        self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠧ࠮ࡲࠪႮ"))
        self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡰ࡭ࡷࡪ࡭ࡳ࠭Ⴏ"))
        self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠩ࠰࠱ࡩࡸࡩࡷࡧࡵࠫႰ"))
        self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪႱ"))
        if self.bstack1l1l1l11l1_opy_ > 1:
            self.bstack11111111ll_opy_.append(bstack11111l_opy_ (u"ࠫ࠲ࡴࠧႲ"))
            self.bstack11111111ll_opy_.append(str(self.bstack1l1l1l11l1_opy_))
    def bstack1llllllllll_opy_(self):
        if bstack1l11ll1111_opy_.bstack1l1l1l1l11_opy_(self.bstack1lllllll1ll_opy_):
             self.bstack11111111ll_opy_ += [
                bstack1llllll1lll_opy_.get(bstack11111l_opy_ (u"ࠬࡸࡥࡳࡷࡱࠫႳ")), str(bstack1l11ll1111_opy_.bstack111lll111_opy_(self.bstack1lllllll1ll_opy_)),
                bstack1llllll1lll_opy_.get(bstack11111l_opy_ (u"࠭ࡤࡦ࡮ࡤࡽࠬႴ")), str(bstack1llllll1lll_opy_.get(bstack11111l_opy_ (u"ࠧࡳࡧࡵࡹࡳ࠳ࡤࡦ࡮ࡤࡽࠬႵ")))
            ]
    def bstack11111l1111_opy_(self):
        bstack1lll1111l_opy_ = []
        for spec in self.bstack1l1l111l11_opy_:
            bstack11lll11ll_opy_ = [spec]
            bstack11lll11ll_opy_ += self.bstack11111111ll_opy_
            bstack1lll1111l_opy_.append(bstack11lll11ll_opy_)
        self.bstack1lll1111l_opy_ = bstack1lll1111l_opy_
        return bstack1lll1111l_opy_
    def bstack1l1llll11_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack11111l111l_opy_ = True
            return True
        except Exception as e:
            self.bstack11111l111l_opy_ = False
        return self.bstack11111l111l_opy_
    def bstack11lll1111l_opy_(self):
        bstack11111l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡍࡥࡵࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡴࡸࡲࡳ࡯࡮ࡨࠢࡷ࡬ࡪࡳࠠࡶࡵ࡬ࡲ࡬ࠦࡰࡺࡶࡨࡷࡹࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡯࡮ࡵ࠼ࠣࡘ࡭࡫ࠠࡵࡱࡷࡥࡱࠦ࡮ࡶ࡯ࡥࡩࡷࠦ࡯ࡧࠢࡷࡩࡸࡺࡳࠡࡥࡲࡰࡱ࡫ࡣࡵࡧࡧ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤႶ")
        try:
            from browserstack_sdk.bstack1111l111ll_opy_ import bstack11111ll1ll_opy_
            bstack1llllllll11_opy_ = bstack11111ll1ll_opy_(bstack11111ll1l1_opy_=self.bstack11111111ll_opy_)
            if not bstack1llllllll11_opy_.get(bstack11111l_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪႷ"), False):
                self.logger.error(bstack11111l_opy_ (u"ࠥࡘࡪࡹࡴࠡࡥࡲࡹࡳࡺࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧ࠾ࠥࢁࡽࠣႸ").format(bstack1llllllll11_opy_.get(bstack11111l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪႹ"), bstack11111l_opy_ (u"࡛ࠬ࡮࡬ࡰࡲࡻࡳࠦࡥࡳࡴࡲࡶࠬႺ"))))
                return 0
            count = bstack1llllllll11_opy_.get(bstack11111l_opy_ (u"࠭ࡣࡰࡷࡱࡸࠬႻ"), 0)
            self.logger.info(bstack11111l_opy_ (u"ࠢࡕࡱࡷࡥࡱࠦࡴࡦࡵࡷࡷࠥࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤ࠻ࠢࡾࢁࠧႼ").format(count))
            return count
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡦࡳࡺࡴࡴ࠻ࠢࡾࢁࠧႽ").format(e))
            return 0
    def bstack111111l11_opy_(self, bstack1lllllll11l_opy_, bstack1ll11l1lll_opy_):
        bstack1ll11l1lll_opy_[bstack11111l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩႾ")] = self.bstack1lllllll1ll_opy_
        multiprocessing.set_start_method(bstack11111l_opy_ (u"ࠪࡷࡵࡧࡷ࡯ࠩႿ"))
        bstack1l11llll1_opy_ = []
        manager = multiprocessing.Manager()
        bstack11111l1l11_opy_ = manager.list()
        if bstack11111l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧჀ") in self.bstack1lllllll1ll_opy_:
            for index, platform in enumerate(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨჁ")]):
                bstack1l11llll1_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack1lllllll11l_opy_,
                                                            args=(self.bstack11111111ll_opy_, bstack1ll11l1lll_opy_, bstack11111l1l11_opy_)))
            bstack11111l1lll_opy_ = len(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩჂ")])
        else:
            bstack1l11llll1_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack1lllllll11l_opy_,
                                                        args=(self.bstack11111111ll_opy_, bstack1ll11l1lll_opy_, bstack11111l1l11_opy_)))
            bstack11111l1lll_opy_ = 1
        i = 0
        for t in bstack1l11llll1_opy_:
            os.environ[bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧჃ")] = str(i)
            if bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫჄ") in self.bstack1lllllll1ll_opy_:
                os.environ[bstack11111l_opy_ (u"ࠩࡆ࡙ࡗࡘࡅࡏࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡊࡁࡕࡃࠪჅ")] = json.dumps(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭჆")][i % bstack11111l1lll_opy_])
            i += 1
            t.start()
        for t in bstack1l11llll1_opy_:
            t.join()
        return list(bstack11111l1l11_opy_)
    @staticmethod
    def bstack1ll1ll1l_opy_(driver, bstack1lllllll111_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack11111l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡹ࡫࡭ࠨჇ"), None)
        if item and getattr(item, bstack11111l_opy_ (u"ࠬࡥࡡ࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡦࡥࡸ࡫ࠧ჈"), None) and not getattr(item, bstack11111l_opy_ (u"࠭࡟ࡢ࠳࠴ࡽࡤࡹࡴࡰࡲࡢࡨࡴࡴࡥࠨ჉"), False):
            logger.info(
                bstack11111l_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡵ࡮ࠡࡪࡤࡷࠥ࡫࡮ࡥࡧࡧ࠲ࠥࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡩࡳࡷࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡴࡦࡵࡷ࡭ࡳ࡭ࠠࡪࡵࠣࡹࡳࡪࡥࡳࡹࡤࡽ࠳ࠨ჊"))
            bstack11111l1ll1_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1l1l11ll11_opy_.bstack11lll11lll_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)
    def bstack11111111l1_opy_(self):
        bstack11111l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࠦࡴࡩࡧࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡶࡲࠤࡧ࡫ࠠࡦࡺࡨࡧࡺࡺࡥࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢ჋")
        try:
            from browserstack_sdk.bstack1111l111ll_opy_ import bstack11111ll1ll_opy_
            bstack1llllllll1l_opy_ = bstack11111ll1ll_opy_(bstack11111ll1l1_opy_=self.bstack11111111ll_opy_)
            if not bstack1llllllll1l_opy_.get(bstack11111l_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ჌"), False):
                self.logger.error(bstack11111l_opy_ (u"ࠥࡘࡪࡹࡴࠡࡨ࡬ࡰࡪࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࢀࢃࠢჍ").format(bstack1llllllll1l_opy_.get(bstack11111l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ჎"), bstack11111l_opy_ (u"࡛ࠬ࡮࡬ࡰࡲࡻࡳࠦࡥࡳࡴࡲࡶࠬ჏"))))
                return []
            test_files = bstack1llllllll1l_opy_.get(bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡫࡯࡬ࡦࡵࠪა"), [])
            count = bstack1llllllll1l_opy_.get(bstack11111l_opy_ (u"ࠧࡤࡱࡸࡲࡹ࠭ბ"), 0)
            self.logger.debug(bstack11111l_opy_ (u"ࠣࡅࡲࡰࡱ࡫ࡣࡵࡧࡧࠤࢀࢃࠠࡵࡧࡶࡸࡸࠦࡩ࡯ࠢࡾࢁࠥ࡬ࡩ࡭ࡧࡶࠦგ").format(count, len(test_files)))
            return test_files
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡪࡵࡳ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࡀࠠࡼࡿࠥდ").format(e))
            return []