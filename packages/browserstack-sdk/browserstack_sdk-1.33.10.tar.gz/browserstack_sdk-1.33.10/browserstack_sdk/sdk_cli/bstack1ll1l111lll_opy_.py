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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
    bstack1llll111l1l_opy_,
)
from bstack_utils.helper import  bstack11l1l111l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1l11ll1l_opy_, bstack1lll1ll1ll1_opy_, bstack1lll1ll1111_opy_, bstack1ll1lllll11_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1llll1ll11_opy_ import bstack11l1llllll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lll111l_opy_ import bstack1ll1l11l111_opy_
from bstack_utils.percy import bstack11l111l1ll_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1lll11l11l1_opy_(bstack1ll1l11lll1_opy_):
    def __init__(self, bstack1l1l1111ll1_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l1l1111ll1_opy_ = bstack1l1l1111ll1_opy_
        self.percy = bstack11l111l1ll_opy_()
        self.bstack1l11lll11_opy_ = bstack11l1llllll_opy_()
        self.bstack1l1l111111l_opy_()
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l1l111l1l1_opy_)
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST), self.bstack1ll11l11l1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll11l1ll_opy_(self, instance: bstack1llll111l1l_opy_, driver: object):
        bstack1l1ll11ll11_opy_ = TestFramework.bstack1llll11111l_opy_(instance.context)
        for t in bstack1l1ll11ll11_opy_:
            bstack1l1l1ll1l11_opy_ = TestFramework.bstack1llll111ll1_opy_(t, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
            if any(instance is d[1] for d in bstack1l1l1ll1l11_opy_) or instance == driver:
                return t
    def bstack1l1l111l1l1_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1lll1l11111_opy_.bstack1ll111ll11l_opy_(method_name):
                return
            platform_index = f.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1ll111ll111_opy_, 0)
            bstack1l1l1l1llll_opy_ = self.bstack1l1ll11l1ll_opy_(instance, driver)
            bstack1l1l1111lll_opy_ = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1l1111l11_opy_, None)
            if not bstack1l1l1111lll_opy_:
                self.logger.debug(bstack11111l_opy_ (u"ࠣࡱࡱࡣࡵࡸࡥࡠࡧࡻࡩࡨࡻࡴࡦ࠼ࠣࡶࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡡࡴࠢࡶࡩࡸࡹࡩࡰࡰࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡽࡪࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠣጺ"))
                return
            driver_command = f.bstack1ll11l11l11_opy_(*args)
            for command in bstack1l1lll11_opy_:
                if command == driver_command:
                    self.bstack1ll1ll111l_opy_(driver, platform_index)
            bstack1l1l11lll_opy_ = self.percy.bstack1l1ll11l_opy_()
            if driver_command in bstack1l1l111111_opy_[bstack1l1l11lll_opy_]:
                self.bstack1l11lll11_opy_.bstack1llll1l1l1_opy_(bstack1l1l1111lll_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠤࡲࡲࡤࡶࡲࡦࡡࡨࡼࡪࡩࡵࡵࡧ࠽ࠤࡪࡸࡲࡰࡴࠥጻ"), e)
    def bstack1ll11l11l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
        bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l1l1ll1l11_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧጼ") + str(kwargs) + bstack11111l_opy_ (u"ࠦࠧጽ"))
            return
        if len(bstack1l1l1ll1l11_opy_) > 1:
            self.logger.debug(bstack11111l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦࡻ࡭ࡧࡱࠬࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢጾ") + str(kwargs) + bstack11111l_opy_ (u"ࠨࠢጿ"))
        bstack1l1l111l11l_opy_, bstack1l1l1111l1l_opy_ = bstack1l1l1ll1l11_opy_[0]
        driver = bstack1l1l111l11l_opy_()
        if not driver:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣፀ") + str(kwargs) + bstack11111l_opy_ (u"ࠣࠤፁ"))
            return
        bstack1l1l111l111_opy_ = {
            TestFramework.bstack1ll111111l1_opy_: bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺࠠ࡯ࡣࡰࡩࠧፂ"),
            TestFramework.bstack1ll11111l11_opy_: bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࠡࡷࡸ࡭ࡩࠨፃ"),
            TestFramework.bstack1l1l1111l11_opy_: bstack11111l_opy_ (u"ࠦࡹ࡫ࡳࡵࠢࡵࡩࡷࡻ࡮ࠡࡰࡤࡱࡪࠨፄ")
        }
        bstack1l11llllll1_opy_ = { key: f.bstack1llll111ll1_opy_(instance, key) for key in bstack1l1l111l111_opy_ }
        bstack1l11lllllll_opy_ = [key for key, value in bstack1l11llllll1_opy_.items() if not value]
        if bstack1l11lllllll_opy_:
            for key in bstack1l11lllllll_opy_:
                self.logger.debug(bstack11111l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࠣፅ") + str(key) + bstack11111l_opy_ (u"ࠨࠢፆ"))
            return
        platform_index = f.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1ll111ll111_opy_, 0)
        if self.bstack1l1l1111ll1_opy_.percy_capture_mode == bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤፇ"):
            bstack11l1l1l111_opy_ = bstack1l11llllll1_opy_.get(TestFramework.bstack1l1l1111l11_opy_) + bstack11111l_opy_ (u"ࠣ࠯ࡷࡩࡸࡺࡣࡢࡵࡨࠦፈ")
            bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack1l1l1111111_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack11l1l1l111_opy_,
                bstack1l111lll11_opy_=bstack1l11llllll1_opy_[TestFramework.bstack1ll111111l1_opy_],
                bstack1l11l1llll_opy_=bstack1l11llllll1_opy_[TestFramework.bstack1ll11111l11_opy_],
                bstack11llll11ll_opy_=platform_index
            )
            bstack1ll1l111ll1_opy_.end(EVENTS.bstack1l1l1111111_opy_.value, bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤፉ"), bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠥ࠾ࡪࡴࡤࠣፊ"), True, None, None, None, None, test_name=bstack11l1l1l111_opy_)
    def bstack1ll1ll111l_opy_(self, driver, platform_index):
        if self.bstack1l11lll11_opy_.bstack1l1111l11l_opy_() is True or self.bstack1l11lll11_opy_.capturing() is True:
            return
        self.bstack1l11lll11_opy_.bstack1l111l11ll_opy_()
        while not self.bstack1l11lll11_opy_.bstack1l1111l11l_opy_():
            bstack1l1l1111lll_opy_ = self.bstack1l11lll11_opy_.bstack1l1ll1l1_opy_()
            self.bstack1l1l11ll1l_opy_(driver, bstack1l1l1111lll_opy_, platform_index)
        self.bstack1l11lll11_opy_.bstack11l1ll11l1_opy_()
    def bstack1l1l11ll1l_opy_(self, driver, bstack1ll11l11l1_opy_, platform_index, test=None):
        from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
        bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack1l1l1ll1l_opy_.value)
        if test != None:
            bstack1l111lll11_opy_ = getattr(test, bstack11111l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩፋ"), None)
            bstack1l11l1llll_opy_ = getattr(test, bstack11111l_opy_ (u"ࠬࡻࡵࡪࡦࠪፌ"), None)
            PercySDK.screenshot(driver, bstack1ll11l11l1_opy_, bstack1l111lll11_opy_=bstack1l111lll11_opy_, bstack1l11l1llll_opy_=bstack1l11l1llll_opy_, bstack11llll11ll_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack1ll11l11l1_opy_)
        bstack1ll1l111ll1_opy_.end(EVENTS.bstack1l1l1ll1l_opy_.value, bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨፍ"), bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧፎ"), True, None, None, None, None, test_name=bstack1ll11l11l1_opy_)
    def bstack1l1l111111l_opy_(self):
        os.environ[bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞࠭ፏ")] = str(self.bstack1l1l1111ll1_opy_.success)
        os.environ[bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭ፐ")] = str(self.bstack1l1l1111ll1_opy_.percy_capture_mode)
        self.percy.bstack1l1l11111ll_opy_(self.bstack1l1l1111ll1_opy_.is_percy_auto_enabled)
        self.percy.bstack1l1l11111l1_opy_(self.bstack1l1l1111ll1_opy_.percy_build_id)