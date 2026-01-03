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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1lllll11l1l_opy_,
)
from bstack_utils.helper import  bstack11llll11ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1lll111l1ll_opy_, bstack1ll1ll111l1_opy_, bstack1lll1l11l1l_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1l111llll1_opy_ import bstack11l1ll11ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllll11_opy_ import bstack1ll11lll1ll_opy_
from bstack_utils.percy import bstack111111l1_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1lll1lll111_opy_(bstack1lll11ll111_opy_):
    def __init__(self, bstack1l11lllll11_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l11lllll11_opy_ = bstack1l11lllll11_opy_
        self.percy = bstack111111l1_opy_()
        self.bstack11l1lllll_opy_ = bstack11l1ll11ll_opy_()
        self.bstack1l1l11111l1_opy_()
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11lllll1l_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), self.bstack1ll111l1111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l111ll11_opy_(self, instance: bstack1lllll11l1l_opy_, driver: object):
        bstack1l1l1lllll1_opy_ = TestFramework.bstack1llll11llll_opy_(instance.context)
        for t in bstack1l1l1lllll1_opy_:
            bstack1l1l11lll1l_opy_ = TestFramework.bstack1llll1l11ll_opy_(t, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
            if any(instance is d[1] for d in bstack1l1l11lll1l_opy_) or instance == driver:
                return t
    def bstack1l11lllll1l_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1ll1lll1lll_opy_.bstack1l1lll1l1l1_opy_(method_name):
                return
            platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_, 0)
            bstack1l1l1l11lll_opy_ = self.bstack1l1l111ll11_opy_(instance, driver)
            bstack1l1l1111111_opy_ = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1l1111l11_opy_, None)
            if not bstack1l1l1111111_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠣࡱࡱࡣࡵࡸࡥࡠࡧࡻࡩࡨࡻࡴࡦ࠼ࠣࡶࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡡࡴࠢࡶࡩࡸࡹࡩࡰࡰࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡽࡪࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠣፁ"))
                return
            driver_command = f.bstack1ll111ll111_opy_(*args)
            for command in bstack1l1ll111l_opy_:
                if command == driver_command:
                    self.bstack1l11l111l_opy_(driver, platform_index)
            bstack1l11l111ll_opy_ = self.percy.bstack1lll11lll1_opy_()
            if driver_command in bstack11l111l11_opy_[bstack1l11l111ll_opy_]:
                self.bstack11l1lllll_opy_.bstack11ll1l111_opy_(bstack1l1l1111111_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠤࡲࡲࡤࡶࡲࡦࡡࡨࡼࡪࡩࡵࡵࡧ࠽ࠤࡪࡸࡲࡰࡴࠥፂ"), e)
    def bstack1ll111l1111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
        bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l1l11lll1l_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧፃ") + str(kwargs) + bstack1l1l_opy_ (u"ࠦࠧፄ"))
            return
        if len(bstack1l1l11lll1l_opy_) > 1:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦࡻ࡭ࡧࡱࠬࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢፅ") + str(kwargs) + bstack1l1l_opy_ (u"ࠨࠢፆ"))
        bstack1l11lllllll_opy_, bstack1l1l111111l_opy_ = bstack1l1l11lll1l_opy_[0]
        driver = bstack1l11lllllll_opy_()
        if not driver:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣፇ") + str(kwargs) + bstack1l1l_opy_ (u"ࠣࠤፈ"))
            return
        bstack1l1l1111l1l_opy_ = {
            TestFramework.bstack1ll111l1l1l_opy_: bstack1l1l_opy_ (u"ࠤࡷࡩࡸࡺࠠ࡯ࡣࡰࡩࠧፉ"),
            TestFramework.bstack1ll11l1ll1l_opy_: bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࠡࡷࡸ࡭ࡩࠨፊ"),
            TestFramework.bstack1l1l1111l11_opy_: bstack1l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࠢࡵࡩࡷࡻ࡮ࠡࡰࡤࡱࡪࠨፋ")
        }
        bstack1l1l11111ll_opy_ = { key: f.bstack1llll1l11ll_opy_(instance, key) for key in bstack1l1l1111l1l_opy_ }
        bstack1l1l111l111_opy_ = [key for key, value in bstack1l1l11111ll_opy_.items() if not value]
        if bstack1l1l111l111_opy_:
            for key in bstack1l1l111l111_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࠣፌ") + str(key) + bstack1l1l_opy_ (u"ࠨࠢፍ"))
            return
        platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_, 0)
        if self.bstack1l11lllll11_opy_.percy_capture_mode == bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤፎ"):
            bstack1ll1l1l11l_opy_ = bstack1l1l11111ll_opy_.get(TestFramework.bstack1l1l1111l11_opy_) + bstack1l1l_opy_ (u"ࠣ࠯ࡷࡩࡸࡺࡣࡢࡵࡨࠦፏ")
            bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1l1l1111ll1_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack1ll1l1l11l_opy_,
                bstack1l1l11l111_opy_=bstack1l1l11111ll_opy_[TestFramework.bstack1ll111l1l1l_opy_],
                bstack11l1111lll_opy_=bstack1l1l11111ll_opy_[TestFramework.bstack1ll11l1ll1l_opy_],
                bstack1ll11l1111_opy_=platform_index
            )
            bstack1ll1l1ll111_opy_.end(EVENTS.bstack1l1l1111ll1_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤፐ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠥ࠾ࡪࡴࡤࠣፑ"), True, None, None, None, None, test_name=bstack1ll1l1l11l_opy_)
    def bstack1l11l111l_opy_(self, driver, platform_index):
        if self.bstack11l1lllll_opy_.bstack1ll1l11l_opy_() is True or self.bstack11l1lllll_opy_.capturing() is True:
            return
        self.bstack11l1lllll_opy_.bstack1l11l1l111_opy_()
        while not self.bstack11l1lllll_opy_.bstack1ll1l11l_opy_():
            bstack1l1l1111111_opy_ = self.bstack11l1lllll_opy_.bstack1ll11l11l_opy_()
            self.bstack1ll111lll_opy_(driver, bstack1l1l1111111_opy_, platform_index)
        self.bstack11l1lllll_opy_.bstack1111ll11l_opy_()
    def bstack1ll111lll_opy_(self, driver, bstack11ll1ll1ll_opy_, platform_index, test=None):
        from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
        bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1lllllll1_opy_.value)
        if test != None:
            bstack1l1l11l111_opy_ = getattr(test, bstack1l1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩፒ"), None)
            bstack11l1111lll_opy_ = getattr(test, bstack1l1l_opy_ (u"ࠬࡻࡵࡪࡦࠪፓ"), None)
            PercySDK.screenshot(driver, bstack11ll1ll1ll_opy_, bstack1l1l11l111_opy_=bstack1l1l11l111_opy_, bstack11l1111lll_opy_=bstack11l1111lll_opy_, bstack1ll11l1111_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack11ll1ll1ll_opy_)
        bstack1ll1l1ll111_opy_.end(EVENTS.bstack1lllllll1_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨፔ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧፕ"), True, None, None, None, None, test_name=bstack11ll1ll1ll_opy_)
    def bstack1l1l11111l1_opy_(self):
        os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞࠭ፖ")] = str(self.bstack1l11lllll11_opy_.success)
        os.environ[bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭ፗ")] = str(self.bstack1l11lllll11_opy_.percy_capture_mode)
        self.percy.bstack1l1l1111lll_opy_(self.bstack1l11lllll11_opy_.is_percy_auto_enabled)
        self.percy.bstack1l11llllll1_opy_(self.bstack1l11lllll11_opy_.percy_build_id)