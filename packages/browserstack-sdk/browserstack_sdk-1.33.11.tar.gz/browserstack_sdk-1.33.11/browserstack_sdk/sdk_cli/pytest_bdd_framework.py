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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1lllll1l111_opy_ import bstack1llll11l1l1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11ll1l1l_opy_ import bstack11lllll1111_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1ll1llll111_opy_,
    bstack1lll111l1ll_opy_,
    bstack1ll1ll111l1_opy_,
    bstack11lll1l1l1l_opy_,
    bstack1lll1l11l1l_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1l11lll11_opy_
from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1lll1l11lll_opy_ import bstack1ll1l1ll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1ll1l_opy_ import bstack1lllll1lll1_opy_
bstack1l1l11l1l1l_opy_ = bstack1l1l11lll11_opy_()
bstack1l1l1l1l1l1_opy_ = bstack1l1l_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦᒔ")
bstack1l111l1111l_opy_ = bstack1l1l_opy_ (u"ࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠣᒕ")
bstack11llll11lll_opy_ = bstack1l1l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠧᒖ")
bstack1l11111111l_opy_ = 1.0
_1l1l1l1l111_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack11llllll1ll_opy_ = bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢᒗ")
    bstack11lll1l1ll1_opy_ = bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࠨᒘ")
    bstack1l111l11111_opy_ = bstack1l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤࠣᒙ")
    bstack1l1111lll1l_opy_ = bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣࡸࡺࡡࡳࡶࡨࡨࠧᒚ")
    bstack1l11111ll11_opy_ = bstack1l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟࡭ࡣࡶࡸࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᒛ")
    bstack1l111111l11_opy_: bool
    bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_  = None
    bstack11llll11ll1_opy_ = [
        bstack1ll1llll111_opy_.BEFORE_ALL,
        bstack1ll1llll111_opy_.AFTER_ALL,
        bstack1ll1llll111_opy_.BEFORE_EACH,
        bstack1ll1llll111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11llll1llll_opy_: Dict[str, str],
        bstack1ll11l111ll_opy_: List[str]=[bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤᒜ")],
        bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_ = None,
        bstack1ll1l11111l_opy_=None
    ):
        super().__init__(bstack1ll11l111ll_opy_, bstack11llll1llll_opy_, bstack1lllll1ll1l_opy_)
        self.bstack1l111111l11_opy_ = any(bstack1l1l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥᒝ") in item.lower() for item in bstack1ll11l111ll_opy_)
        self.bstack1ll1l11111l_opy_ = bstack1ll1l11111l_opy_
    def track_event(
        self,
        context: bstack11lll1l1l1l_opy_,
        test_framework_state: bstack1ll1llll111_opy_,
        test_hook_state: bstack1ll1ll111l1_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1ll1llll111_opy_.TEST or test_framework_state in PytestBDDFramework.bstack11llll11ll1_opy_:
            bstack11lllll1111_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1ll1llll111_opy_.NONE:
            self.logger.warning(bstack1l1l_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫ࡤࠡࡥࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࠣᒞ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠣࠤᒟ"))
            return
        if not self.bstack1l111111l11_opy_:
            self.logger.warning(bstack1l1l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠿ࠥᒠ") + str(str(self.bstack1ll11l111ll_opy_)) + bstack1l1l_opy_ (u"ࠥࠦᒡ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1l1l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᒢ") + str(kwargs) + bstack1l1l_opy_ (u"ࠧࠨᒣ"))
            return
        instance = self.__11llll1l11l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1l1l_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡡࡳࡩࡶࡁࠧᒤ") + str(args) + bstack1l1l_opy_ (u"ࠢࠣᒥ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack11llll11ll1_opy_ and test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1lll1l1l11_opy_.value)
                name = str(EVENTS.bstack1lll1l1l11_opy_.name)+bstack1l1l_opy_ (u"ࠣ࠼ࠥᒦ")+str(test_framework_state.name)
                TestFramework.bstack11llll1l1ll_opy_(instance, name, bstack1ll11l111l1_opy_)
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶࠥࡶࡲࡦ࠼ࠣࡿࢂࠨᒧ").format(e))
        try:
            if test_framework_state == bstack1ll1llll111_opy_.TEST:
                if not TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1111ll11l_opy_) and test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__11llll111l1_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack1l1l_opy_ (u"ࠥࡰࡴࡧࡤࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒨ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠦࠧᒩ"))
                if test_hook_state == bstack1ll1ll111l1_opy_.PRE and not TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1l1l11ll1_opy_):
                    TestFramework.bstack1llll1lll11_opy_(instance, TestFramework.bstack1l1l1l11ll1_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__1l1111111l1_opy_(instance, args)
                    self.logger.debug(bstack1l1l_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡴࡶࡤࡶࡹࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒪ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠨࠢᒫ"))
                elif test_hook_state == bstack1ll1ll111l1_opy_.POST and not TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1ll111l11_opy_):
                    TestFramework.bstack1llll1lll11_opy_(instance, TestFramework.bstack1l1ll111l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1l1l_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡨࡲࡩࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒬ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠣࠤᒭ"))
            elif test_framework_state == bstack1ll1llll111_opy_.STEP:
                if test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                    PytestBDDFramework.__11llllll111_opy_(instance, args)
                elif test_hook_state == bstack1ll1ll111l1_opy_.POST:
                    PytestBDDFramework.__1l1111l1111_opy_(instance, args)
            elif test_framework_state == bstack1ll1llll111_opy_.LOG and test_hook_state == bstack1ll1ll111l1_opy_.POST:
                PytestBDDFramework.__1l1111llll1_opy_(instance, *args)
            elif test_framework_state == bstack1ll1llll111_opy_.LOG_REPORT and test_hook_state == bstack1ll1ll111l1_opy_.POST:
                self.__11lllllll11_opy_(instance, *args)
                self.__11lll1llll1_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack11llll11ll1_opy_:
                self.__11lllll1ll1_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥᒮ") + str(instance.ref()) + bstack1l1l_opy_ (u"ࠥࠦᒯ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11lll1lllll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack11llll11ll1_opy_ and test_hook_state == bstack1ll1ll111l1_opy_.POST:
                name = str(EVENTS.bstack1lll1l1l11_opy_.name)+bstack1l1l_opy_ (u"ࠦ࠿ࠨᒰ")+str(test_framework_state.name)
                bstack1ll11l111l1_opy_ = TestFramework.bstack1l1111l1l11_opy_(instance, name)
                bstack1ll1l1ll111_opy_.end(EVENTS.bstack1lll1l1l11_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᒱ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᒲ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢᒳ").format(e))
    def bstack1l1l1ll1111_opy_(self):
        return self.bstack1l111111l11_opy_
    def __1l1111lll11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1l1l_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᒴ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l1ll111l_opy_(rep, [bstack1l1l_opy_ (u"ࠤࡺ࡬ࡪࡴࠢᒵ"), bstack1l1l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᒶ"), bstack1l1l_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦᒷ"), bstack1l1l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᒸ"), bstack1l1l_opy_ (u"ࠨࡳ࡬࡫ࡳࡴࡪࡪࠢᒹ"), bstack1l1l_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨᒺ")])
        return None
    def __11lllllll11_opy_(self, instance: bstack1lll111l1ll_opy_, *args):
        result = self.__1l1111lll11_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll111l_opy_ = None
        if result.get(bstack1l1l_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᒻ"), None) == bstack1l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤᒼ") and len(args) > 1 and getattr(args[1], bstack1l1l_opy_ (u"ࠥࡩࡽࡩࡩ࡯ࡨࡲࠦᒽ"), None) is not None:
            failure = [{bstack1l1l_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧᒾ"): [args[1].excinfo.exconly(), result.get(bstack1l1l_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᒿ"), None)]}]
            bstack1llllll111l_opy_ = bstack1l1l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢᓀ") if bstack1l1l_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥᓁ") in getattr(args[1].excinfo, bstack1l1l_opy_ (u"ࠣࡶࡼࡴࡪࡴࡡ࡮ࡧࠥᓂ"), bstack1l1l_opy_ (u"ࠤࠥᓃ")) else bstack1l1l_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᓄ")
        bstack1l111l111ll_opy_ = result.get(bstack1l1l_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᓅ"), TestFramework.bstack11lll1l1lll_opy_)
        if bstack1l111l111ll_opy_ != TestFramework.bstack11lll1l1lll_opy_:
            TestFramework.bstack1llll1lll11_opy_(instance, TestFramework.bstack1l1ll111l1l_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l1111ll1ll_opy_(instance, {
            TestFramework.bstack1l11l1ll1l1_opy_: failure,
            TestFramework.bstack11lllll111l_opy_: bstack1llllll111l_opy_,
            TestFramework.bstack1l11ll11lll_opy_: bstack1l111l111ll_opy_,
        })
    def __11llll1l11l_opy_(
        self,
        context: bstack11lll1l1l1l_opy_,
        test_framework_state: bstack1ll1llll111_opy_,
        test_hook_state: bstack1ll1ll111l1_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1ll1llll111_opy_.SETUP_FIXTURE:
            instance = self.__11llll1l111_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack11lllllllll_opy_ bstack1l11111l111_opy_ this to be bstack1l1l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᓆ")
            if test_framework_state == bstack1ll1llll111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l111111lll_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1ll1llll111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1l1l_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᓇ"), None), bstack1l1l_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᓈ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1l1l_opy_ (u"ࠣࡰࡲࡨࡪࠨᓉ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack1l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᓊ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1lll1llll11_opy_(target) if target else None
        return instance
    def __11lllll1ll1_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        test_framework_state: bstack1ll1llll111_opy_,
        test_hook_state: bstack1ll1ll111l1_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack11llllll11l_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, PytestBDDFramework.bstack11lll1l1ll1_opy_, {})
        if not key in bstack11llllll11l_opy_:
            bstack11llllll11l_opy_[key] = []
        bstack11lll1l11ll_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, PytestBDDFramework.bstack1l111l11111_opy_, {})
        if not key in bstack11lll1l11ll_opy_:
            bstack11lll1l11ll_opy_[key] = []
        bstack11lll1lll1l_opy_ = {
            PytestBDDFramework.bstack11lll1l1ll1_opy_: bstack11llllll11l_opy_,
            PytestBDDFramework.bstack1l111l11111_opy_: bstack11lll1l11ll_opy_,
        }
        if test_hook_state == bstack1ll1ll111l1_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack1l1l_opy_ (u"ࠥ࡯ࡪࡿࠢᓋ"): key,
                TestFramework.bstack1l1111l1ll1_opy_: uuid4().__str__(),
                TestFramework.bstack11llll11111_opy_: TestFramework.bstack1l11111ll1l_opy_,
                TestFramework.bstack11llll1111l_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11llll1l1l1_opy_: [],
                TestFramework.bstack1l11111l11l_opy_: hook_name,
                TestFramework.bstack11lllll1lll_opy_: bstack1ll1l1ll1ll_opy_.bstack11lll1ll1ll_opy_()
            }
            bstack11llllll11l_opy_[key].append(hook)
            bstack11lll1lll1l_opy_[PytestBDDFramework.bstack1l1111lll1l_opy_] = key
        elif test_hook_state == bstack1ll1ll111l1_opy_.POST:
            bstack11llll1ll11_opy_ = bstack11llllll11l_opy_.get(key, [])
            hook = bstack11llll1ll11_opy_.pop() if bstack11llll1ll11_opy_ else None
            if hook:
                result = self.__1l1111lll11_opy_(*args)
                if result:
                    bstack11lll1lll11_opy_ = result.get(bstack1l1l_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᓌ"), TestFramework.bstack1l11111ll1l_opy_)
                    if bstack11lll1lll11_opy_ != TestFramework.bstack1l11111ll1l_opy_:
                        hook[TestFramework.bstack11llll11111_opy_] = bstack11lll1lll11_opy_
                hook[TestFramework.bstack11lll1l11l1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack11lllll1lll_opy_] = bstack1ll1l1ll1ll_opy_.bstack11lll1ll1ll_opy_()
                self.bstack11lll1ll11l_opy_(hook)
                logs = hook.get(TestFramework.bstack1l1111lllll_opy_, [])
                self.bstack1l1ll11lll1_opy_(instance, logs)
                bstack11lll1l11ll_opy_[key].append(hook)
                bstack11lll1lll1l_opy_[PytestBDDFramework.bstack1l11111ll11_opy_] = key
        TestFramework.bstack1l1111ll1ll_opy_(instance, bstack11lll1lll1l_opy_)
        self.logger.debug(bstack1l1l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡭ࡵ࡯࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࡱࡥࡺࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪ࠽ࡼࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡾࠢ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡀࠦᓍ") + str(bstack11lll1l11ll_opy_) + bstack1l1l_opy_ (u"ࠨࠢᓎ"))
    def __11llll1l111_opy_(
        self,
        context: bstack11lll1l1l1l_opy_,
        test_framework_state: bstack1ll1llll111_opy_,
        test_hook_state: bstack1ll1ll111l1_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l1ll111l_opy_(args[0], [bstack1l1l_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᓏ"), bstack1l1l_opy_ (u"ࠣࡣࡵ࡫ࡳࡧ࡭ࡦࠤᓐ"), bstack1l1l_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤᓑ"), bstack1l1l_opy_ (u"ࠥ࡭ࡩࡹࠢᓒ"), bstack1l1l_opy_ (u"ࠦࡺࡴࡩࡵࡶࡨࡷࡹࠨᓓ"), bstack1l1l_opy_ (u"ࠧࡨࡡࡴࡧ࡬ࡨࠧᓔ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack1l1l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᓕ")) else fixturedef.get(bstack1l1l_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᓖ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1l1l_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࠨᓗ")) else None
        node = request.node if hasattr(request, bstack1l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࠢᓘ")) else None
        target = request.node.nodeid if hasattr(node, bstack1l1l_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᓙ")) else None
        baseid = fixturedef.get(bstack1l1l_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᓚ"), None) or bstack1l1l_opy_ (u"ࠧࠨᓛ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1l1l_opy_ (u"ࠨ࡟ࡱࡻࡩࡹࡳࡩࡩࡵࡧࡰࠦᓜ")):
            target = PytestBDDFramework.__1l1111l111l_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1l1l_opy_ (u"ࠢ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᓝ")) else None
            if target and not TestFramework.bstack1lll1llll11_opy_(target):
                self.__1l111111lll_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1l1l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡦࡸࡧࡦࡶࡀࡿࡹࡧࡲࡨࡧࡷࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡲࡴࡪࡥ࠾ࡽࡱࡳࡩ࡫ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᓞ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠤࠥᓟ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1l1l_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࠣᓠ") + str(target) + bstack1l1l_opy_ (u"ࠦࠧᓡ"))
            return None
        instance = TestFramework.bstack1lll1llll11_opy_(target)
        if not instance:
            self.logger.warning(bstack1l1l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤࡧࡧࡳࡦ࡫ࡧࡁࢀࡨࡡࡴࡧ࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᓢ") + str(target) + bstack1l1l_opy_ (u"ࠨࠢᓣ"))
            return None
        bstack1l11111l1ll_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, PytestBDDFramework.bstack11llllll1ll_opy_, {})
        if os.getenv(bstack1l1l_opy_ (u"ࠢࡔࡆࡎࡣࡈࡒࡉࡠࡈࡏࡅࡌࡥࡆࡊ࡚ࡗ࡙ࡗࡋࡓࠣᓤ"), bstack1l1l_opy_ (u"ࠣ࠳ࠥᓥ")) == bstack1l1l_opy_ (u"ࠤ࠴ࠦᓦ"):
            bstack11llll1lll1_opy_ = bstack1l1l_opy_ (u"ࠥ࠾ࠧᓧ").join((scope, fixturename))
            bstack11llll111ll_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111l1l1l_opy_ = {
                bstack1l1l_opy_ (u"ࠦࡰ࡫ࡹࠣᓨ"): bstack11llll1lll1_opy_,
                bstack1l1l_opy_ (u"ࠧࡺࡡࡨࡵࠥᓩ"): PytestBDDFramework.__11llll11l11_opy_(request.node, scenario),
                bstack1l1l_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫ࠢᓪ"): fixturedef,
                bstack1l1l_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᓫ"): scope,
                bstack1l1l_opy_ (u"ࠣࡶࡼࡴࡪࠨᓬ"): None,
            }
            try:
                if test_hook_state == bstack1ll1ll111l1_opy_.POST and callable(getattr(args[-1], bstack1l1l_opy_ (u"ࠤࡪࡩࡹࡥࡲࡦࡵࡸࡰࡹࠨᓭ"), None)):
                    bstack1l1111l1l1l_opy_[bstack1l1l_opy_ (u"ࠥࡸࡾࡶࡥࠣᓮ")] = TestFramework.bstack1l1l1ll1l11_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                bstack1l1111l1l1l_opy_[bstack1l1l_opy_ (u"ࠦࡺࡻࡩࡥࠤᓯ")] = uuid4().__str__()
                bstack1l1111l1l1l_opy_[PytestBDDFramework.bstack11llll1111l_opy_] = bstack11llll111ll_opy_
            elif test_hook_state == bstack1ll1ll111l1_opy_.POST:
                bstack1l1111l1l1l_opy_[PytestBDDFramework.bstack11lll1l11l1_opy_] = bstack11llll111ll_opy_
            if bstack11llll1lll1_opy_ in bstack1l11111l1ll_opy_:
                bstack1l11111l1ll_opy_[bstack11llll1lll1_opy_].update(bstack1l1111l1l1l_opy_)
                self.logger.debug(bstack1l1l_opy_ (u"ࠧࡻࡰࡥࡣࡷࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࠨᓰ") + str(bstack1l11111l1ll_opy_[bstack11llll1lll1_opy_]) + bstack1l1l_opy_ (u"ࠨࠢᓱ"))
            else:
                bstack1l11111l1ll_opy_[bstack11llll1lll1_opy_] = bstack1l1111l1l1l_opy_
                self.logger.debug(bstack1l1l_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࢁࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࢂࠦࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࠥᓲ") + str(len(bstack1l11111l1ll_opy_)) + bstack1l1l_opy_ (u"ࠣࠤᓳ"))
        TestFramework.bstack1llll1lll11_opy_(instance, PytestBDDFramework.bstack11llllll1ll_opy_, bstack1l11111l1ll_opy_)
        self.logger.debug(bstack1l1l_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡵࡀࡿࡱ࡫࡮ࠩࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶ࠭ࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᓴ") + str(instance.ref()) + bstack1l1l_opy_ (u"ࠥࠦᓵ"))
        return instance
    def __1l111111lll_opy_(
        self,
        context: bstack11lll1l1l1l_opy_,
        test_framework_state: bstack1ll1llll111_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1llll11l1l1_opy_.create_context(target)
        ob = bstack1lll111l1ll_opy_(ctx, self.bstack1ll11l111ll_opy_, self.bstack11llll1llll_opy_, test_framework_state)
        TestFramework.bstack1l1111ll1ll_opy_(ob, {
            TestFramework.bstack1ll11l11lll_opy_: context.test_framework_name,
            TestFramework.bstack1l1l11l11ll_opy_: context.test_framework_version,
            TestFramework.bstack1l1111l11l1_opy_: [],
            PytestBDDFramework.bstack11llllll1ll_opy_: {},
            PytestBDDFramework.bstack1l111l11111_opy_: {},
            PytestBDDFramework.bstack11lll1l1ll1_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll1lll11_opy_(ob, TestFramework.bstack11lllll1l1l_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll1lll11_opy_(ob, TestFramework.bstack1l1llllll1l_opy_, context.platform_index)
        TestFramework.bstack1llll111l11_opy_[ctx.id] = ob
        self.logger.debug(bstack1l1l_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠥࡩࡴࡹ࠰࡬ࡨࡂࢁࡣࡵࡺ࠱࡭ࡩࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࡼࡶࡤࡶ࡬࡫ࡴࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦࡵࡀࠦᓶ") + str(TestFramework.bstack1llll111l11_opy_.keys()) + bstack1l1l_opy_ (u"ࠧࠨᓷ"))
        return ob
    @staticmethod
    def __1l1111111l1_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1l1l_opy_ (u"࠭ࡩࡥࠩᓸ"): id(step),
                bstack1l1l_opy_ (u"ࠧࡵࡧࡻࡸࠬᓹ"): step.name,
                bstack1l1l_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥࠩᓺ"): step.keyword,
            })
        meta = {
            bstack1l1l_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࠪᓻ"): {
                bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨᓼ"): feature.name,
                bstack1l1l_opy_ (u"ࠫࡵࡧࡴࡩࠩᓽ"): feature.filename,
                bstack1l1l_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᓾ"): feature.description
            },
            bstack1l1l_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨᓿ"): {
                bstack1l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᔀ"): scenario.name
            },
            bstack1l1l_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧᔁ"): steps,
            bstack1l1l_opy_ (u"ࠩࡨࡼࡦࡳࡰ࡭ࡧࡶࠫᔂ"): PytestBDDFramework.__1l1111ll111_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l111111ll1_opy_: meta
            }
        )
    def bstack11lll1ll11l_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡴࡲࡧࡪࡹࡳࡦࡵࠣࡸ࡭࡫ࠠࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡵ࡬ࡱ࡮ࡲࡡࡳࠢࡷࡳࠥࡺࡨࡦࠢࡍࡥࡻࡧࠠࡪ࡯ࡳࡰࡪࡳࡥ࡯ࡶࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡘ࡭࡯ࡳࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡄࡪࡨࡧࡰࡹࠠࡵࡪࡨࠤࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣ࡭ࡳࡹࡩࡥࡧࠣࢂ࠴࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠴࡛ࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡊࡴࡸࠠࡦࡣࡦ࡬ࠥ࡬ࡩ࡭ࡧࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠮ࠣࡶࡪࡶ࡬ࡢࡥࡨࡷࠥࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰࠧࠦࡩ࡯ࠢ࡬ࡸࡸࠦࡰࡢࡶ࡫࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡍ࡫ࠦࡡࠡࡨ࡬ࡰࡪࠦࡩ࡯ࠢࡷ࡬ࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡰࡥࡹࡩࡨࡦࡵࠣࡥࠥࡳ࡯ࡥ࡫ࡩ࡭ࡪࡪࠠࡩࡱࡲ࡯࠲ࡲࡥࡷࡧ࡯ࠤ࡫࡯࡬ࡦ࠮ࠣ࡭ࡹࠦࡣࡳࡧࡤࡸࡪࡹࠠࡢࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࠤࡼ࡯ࡴࡩࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡤࡦࡶࡤ࡭ࡱࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡓࡪ࡯࡬ࡰࡦࡸ࡬ࡺ࠮ࠣ࡭ࡹࠦࡰࡳࡱࡦࡩࡸࡹࡥࡴࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡱࡵࡣࡢࡶࡨࡨࠥ࡯࡮ࠡࡊࡲࡳࡰࡒࡥࡷࡧ࡯࠳ࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡦࡾࠦࡲࡦࡲ࡯ࡥࡨ࡯࡮ࡨࠢࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮࠲ࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠤ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡗ࡬ࡪࠦࡣࡳࡧࡤࡸࡪࡪࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡥࡷ࡫ࠠࡢࡦࡧࡩࡩࠦࡴࡰࠢࡷ࡬ࡪࠦࡨࡰࡱ࡮ࠫࡸࠦࠢ࡭ࡱࡪࡷࠧࠦ࡬ࡪࡵࡷ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫࠻ࠢࡗ࡬ࡪࠦࡥࡷࡧࡱࡸࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡺࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࠦࡡ࡯ࡦࠣ࡬ࡴࡵ࡫ࠡ࡫ࡱࡪࡴࡸ࡭ࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭ࡢࡰࡪࡼࡥ࡭ࡡࡩ࡭ࡱ࡫ࡳ࠻ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡔࡦࡺࡨࠡࡱࡥ࡮ࡪࡩࡴࡴࠢࡩࡶࡴࡳࠠࡵࡪࡨࠤ࡙࡫ࡳࡵࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡦࡺ࡯࡬ࡥࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹ࠺ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡓࡥࡹ࡮ࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᔃ")
        global _1l1l1l1l111_opy_
        platform_index = os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᔄ")]
        bstack1l1l1llllll_opy_ = os.path.join(bstack1l1l11l1l1l_opy_, (bstack1l1l1l1l1l1_opy_ + str(platform_index)), bstack1l111l1111l_opy_)
        if not os.path.exists(bstack1l1l1llllll_opy_) or not os.path.isdir(bstack1l1l1llllll_opy_):
            return
        logs = hook.get(bstack1l1l_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᔅ"), [])
        with os.scandir(bstack1l1l1llllll_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1l1l1l111_opy_:
                    self.logger.info(bstack1l1l_opy_ (u"ࠨࡐࡢࡶ࡫ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡽࢀࠦᔆ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1l1l_opy_ (u"ࠢࠣᔇ")
                    log_entry = bstack1lll1l11l1l_opy_(
                        kind=bstack1l1l_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᔈ"),
                        message=bstack1l1l_opy_ (u"ࠤࠥᔉ"),
                        level=bstack1l1l_opy_ (u"ࠥࠦᔊ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll11111l_opy_=entry.stat().st_size,
                        bstack1l1l11l1ll1_opy_=bstack1l1l_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦᔋ"),
                        bstack1lll11_opy_=os.path.abspath(entry.path),
                        bstack1l11111lll1_opy_=hook.get(TestFramework.bstack1l1111l1ll1_opy_)
                    )
                    logs.append(log_entry)
                    _1l1l1l1l111_opy_.add(abs_path)
        platform_index = os.environ[bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᔌ")]
        bstack1l111111l1l_opy_ = os.path.join(bstack1l1l11l1l1l_opy_, (bstack1l1l1l1l1l1_opy_ + str(platform_index)), bstack1l111l1111l_opy_, bstack11llll11lll_opy_)
        if not os.path.exists(bstack1l111111l1l_opy_) or not os.path.isdir(bstack1l111111l1l_opy_):
            self.logger.info(bstack1l1l_opy_ (u"ࠨࡎࡰࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡩࡳࡺࡴࡤࠡࡣࡷ࠾ࠥࢁࡽࠣᔍ").format(bstack1l111111l1l_opy_))
        else:
            self.logger.info(bstack1l1l_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡨࡵࡳࡲࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺ࠼ࠣࡿࢂࠨᔎ").format(bstack1l111111l1l_opy_))
            with os.scandir(bstack1l111111l1l_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1l1l1l111_opy_:
                        self.logger.info(bstack1l1l_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᔏ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1l1l_opy_ (u"ࠤࠥᔐ")
                        log_entry = bstack1lll1l11l1l_opy_(
                            kind=bstack1l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᔑ"),
                            message=bstack1l1l_opy_ (u"ࠦࠧᔒ"),
                            level=bstack1l1l_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤᔓ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll11111l_opy_=entry.stat().st_size,
                            bstack1l1l11l1ll1_opy_=bstack1l1l_opy_ (u"ࠨࡍࡂࡐࡘࡅࡑࡥࡕࡑࡎࡒࡅࡉࠨᔔ"),
                            bstack1lll11_opy_=os.path.abspath(entry.path),
                            bstack1l1l1l1lll1_opy_=hook.get(TestFramework.bstack1l1111l1ll1_opy_)
                        )
                        logs.append(log_entry)
                        _1l1l1l1l111_opy_.add(abs_path)
        hook[bstack1l1l_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᔕ")] = logs
    def bstack1l1ll11lll1_opy_(
        self,
        bstack1l1l1l11lll_opy_: bstack1lll111l1ll_opy_,
        entries: List[bstack1lll1l11l1l_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡕࡈࡗࡘࡏࡏࡏࡡࡌࡈࠧᔖ"))
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1llllll1l_opy_)
        req.execution_context.hash = str(bstack1l1l1l11lll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1l11lll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1l11lll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1ll11l11lll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1l11l11ll_opy_)
            log_entry.uuid = entry.bstack1l11111lll1_opy_ if entry.bstack1l11111lll1_opy_ else TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1ll11l1ll1l_opy_)
            log_entry.test_framework_state = bstack1l1l1l11lll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1l1l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᔗ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᔘ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11111l_opy_
                log_entry.file_path = entry.bstack1lll11_opy_
        def bstack1l1ll11llll_opy_():
            bstack1ll111l1_opy_ = datetime.now()
            try:
                self.bstack1ll1l11111l_opy_.LogCreatedEvent(req)
                bstack1l1l1l11lll_opy_.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣᔙ"), datetime.now() - bstack1ll111l1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1l1l_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡽࢀࠦᔚ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1ll1l_opy_.enqueue(bstack1l1ll11llll_opy_)
    def __11lll1llll1_opy_(self, instance) -> None:
        bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡐࡴࡧࡤࡴࠢࡦࡹࡸࡺ࡯࡮ࠢࡷࡥ࡬ࡹࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡩ࡬ࡺࡪࡴࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡉࡲࡦࡣࡷࡩࡸࠦࡡࠡࡦ࡬ࡧࡹࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣࡸࡪࡹࡴࠡ࡮ࡨࡺࡪࡲࠠࡤࡷࡶࡸࡴࡳࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡻࡳࡵࡱࡰࡘࡦ࡭ࡍࡢࡰࡤ࡫ࡪࡸࠠࡢࡰࡧࠤࡺࡶࡤࡢࡶࡨࡷࠥࡺࡨࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡸࡺࡡࡵࡧࠣࡹࡸ࡯࡮ࡨࠢࡶࡩࡹࡥࡳࡵࡣࡷࡩࡤ࡫࡮ࡵࡴ࡬ࡩࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᔛ")
        bstack11lll1lll1l_opy_ = {bstack1l1l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᔜ"): bstack1ll1l1ll1ll_opy_.bstack11lll1ll1ll_opy_()}
        TestFramework.bstack1l1111ll1ll_opy_(instance, bstack11lll1lll1l_opy_)
    @staticmethod
    def __11llllll111_opy_(instance, args):
        request, bstack1l1111l1lll_opy_ = args
        bstack11llll1ll1l_opy_ = id(bstack1l1111l1lll_opy_)
        bstack11lllllll1l_opy_ = instance.data[TestFramework.bstack1l111111ll1_opy_]
        step = next(filter(lambda st: st[bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫᔝ")] == bstack11llll1ll1l_opy_, bstack11lllllll1l_opy_[bstack1l1l_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔞ")]), None)
        step.update({
            bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᔟ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack11lllllll1l_opy_[bstack1l1l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔠ")]) if st[bstack1l1l_opy_ (u"ࠬ࡯ࡤࠨᔡ")] == step[bstack1l1l_opy_ (u"࠭ࡩࡥࠩᔢ")]), None)
        if index is not None:
            bstack11lllllll1l_opy_[bstack1l1l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᔣ")][index] = step
        instance.data[TestFramework.bstack1l111111ll1_opy_] = bstack11lllllll1l_opy_
    @staticmethod
    def __1l1111l1111_opy_(instance, args):
        bstack1l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡽࡨࡦࡰࠣࡰࡪࡴࠠࡢࡴࡪࡷࠥ࡯ࡳࠡ࠴࠯ࠤ࡮ࡺࠠࡴ࡫ࡪࡲ࡮࡬ࡩࡦࡵࠣࡸ࡭࡫ࡲࡦࠢ࡬ࡷࠥࡴ࡯ࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡤࡶ࡬ࡹࠠࡢࡴࡨࠤ࠲࡛ࠦࡳࡧࡴࡹࡪࡹࡴ࠭ࠢࡶࡸࡪࡶ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡬ࡪࠥࡧࡲࡨࡵࠣࡥࡷ࡫ࠠ࠴ࠢࡷ࡬ࡪࡴࠠࡵࡪࡨࠤࡱࡧࡳࡵࠢࡹࡥࡱࡻࡥࠡ࡫ࡶࠤࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᔤ")
        bstack11lllll11ll_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l1111l1lll_opy_ = args[1]
        bstack11llll1ll1l_opy_ = id(bstack1l1111l1lll_opy_)
        bstack11lllllll1l_opy_ = instance.data[TestFramework.bstack1l111111ll1_opy_]
        step = None
        if bstack11llll1ll1l_opy_ is not None and bstack11lllllll1l_opy_.get(bstack1l1l_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔥ")):
            step = next(filter(lambda st: st[bstack1l1l_opy_ (u"ࠪ࡭ࡩ࠭ᔦ")] == bstack11llll1ll1l_opy_, bstack11lllllll1l_opy_[bstack1l1l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔧ")]), None)
            step.update({
                bstack1l1l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪᔨ"): bstack11lllll11ll_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack1l1l_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ᔩ"): bstack1l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᔪ"),
                bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩᔫ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack1l1l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᔬ"): bstack1l1l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᔭ"),
                })
        index = next((i for i, st in enumerate(bstack11lllllll1l_opy_[bstack1l1l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔮ")]) if st[bstack1l1l_opy_ (u"ࠬ࡯ࡤࠨᔯ")] == step[bstack1l1l_opy_ (u"࠭ࡩࡥࠩᔰ")]), None)
        if index is not None:
            bstack11lllllll1l_opy_[bstack1l1l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᔱ")][index] = step
        instance.data[TestFramework.bstack1l111111ll1_opy_] = bstack11lllllll1l_opy_
    @staticmethod
    def __1l1111ll111_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack1l1l_opy_ (u"ࠨࡥࡤࡰࡱࡹࡰࡦࡥࠪᔲ")):
                examples = list(node.callspec.params[bstack1l1l_opy_ (u"ࠩࡢࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡦࡺࡤࡱࡵࡲࡥࠨᔳ")].values())
            return examples
        except:
            return []
    def bstack1l1ll11l1l1_opy_(self, instance: bstack1lll111l1ll_opy_, bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_]):
        bstack11lllll11l1_opy_ = (
            PytestBDDFramework.bstack1l1111lll1l_opy_
            if bstack1llll1llll1_opy_[1] == bstack1ll1ll111l1_opy_.PRE
            else PytestBDDFramework.bstack1l11111ll11_opy_
        )
        hook = PytestBDDFramework.bstack1l1111111ll_opy_(instance, bstack11lllll11l1_opy_)
        entries = hook.get(TestFramework.bstack11llll1l1l1_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1111l11l1_opy_, []))
        return entries
    def bstack1l1l1ll1l1l_opy_(self, instance: bstack1lll111l1ll_opy_, bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_]):
        bstack11lllll11l1_opy_ = (
            PytestBDDFramework.bstack1l1111lll1l_opy_
            if bstack1llll1llll1_opy_[1] == bstack1ll1ll111l1_opy_.PRE
            else PytestBDDFramework.bstack1l11111ll11_opy_
        )
        PytestBDDFramework.bstack1l111l111l1_opy_(instance, bstack11lllll11l1_opy_)
        TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1111l11l1_opy_, []).clear()
    @staticmethod
    def bstack1l1111111ll_opy_(instance: bstack1lll111l1ll_opy_, bstack11lllll11l1_opy_: str):
        bstack11lll1l1l11_opy_ = (
            PytestBDDFramework.bstack1l111l11111_opy_
            if bstack11lllll11l1_opy_ == PytestBDDFramework.bstack1l11111ll11_opy_
            else PytestBDDFramework.bstack11lll1l1ll1_opy_
        )
        bstack1l11111l1l1_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack11lllll11l1_opy_, None)
        bstack1l1111ll1l1_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack11lll1l1l11_opy_, None) if bstack1l11111l1l1_opy_ else None
        return (
            bstack1l1111ll1l1_opy_[bstack1l11111l1l1_opy_][-1]
            if isinstance(bstack1l1111ll1l1_opy_, dict) and len(bstack1l1111ll1l1_opy_.get(bstack1l11111l1l1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l111l111l1_opy_(instance: bstack1lll111l1ll_opy_, bstack11lllll11l1_opy_: str):
        hook = PytestBDDFramework.bstack1l1111111ll_opy_(instance, bstack11lllll11l1_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11llll1l1l1_opy_, []).clear()
    @staticmethod
    def __1l1111llll1_opy_(instance: bstack1lll111l1ll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1l1l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡦࡳࡷࡪࡳࠣᔴ"), None)):
            return
        if os.getenv(bstack1l1l_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡐࡔࡍࡓࠣᔵ"), bstack1l1l_opy_ (u"ࠧ࠷ࠢᔶ")) != bstack1l1l_opy_ (u"ࠨ࠱ࠣᔷ"):
            PytestBDDFramework.logger.warning(bstack1l1l_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡯࡮ࡨࠢࡦࡥࡵࡲ࡯ࡨࠤᔸ"))
            return
        bstack1l111111111_opy_ = {
            bstack1l1l_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᔹ"): (PytestBDDFramework.bstack1l1111lll1l_opy_, PytestBDDFramework.bstack11lll1l1ll1_opy_),
            bstack1l1l_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦᔺ"): (PytestBDDFramework.bstack1l11111ll11_opy_, PytestBDDFramework.bstack1l111l11111_opy_),
        }
        for when in (bstack1l1l_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᔻ"), bstack1l1l_opy_ (u"ࠦࡨࡧ࡬࡭ࠤᔼ"), bstack1l1l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢᔽ")):
            bstack11llll11l1l_opy_ = args[1].get_records(when)
            if not bstack11llll11l1l_opy_:
                continue
            records = [
                bstack1lll1l11l1l_opy_(
                    kind=TestFramework.bstack1l1l1llll1l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1l1l_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠤᔾ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1l1l_opy_ (u"ࠢࡤࡴࡨࡥࡹ࡫ࡤࠣᔿ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll11l1l_opy_
                if isinstance(getattr(r, bstack1l1l_opy_ (u"ࠣ࡯ࡨࡷࡸࡧࡧࡦࠤᕀ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack1l11111llll_opy_, bstack11lll1l1l11_opy_ = bstack1l111111111_opy_.get(when, (None, None))
            bstack11llllllll1_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack1l11111llll_opy_, None) if bstack1l11111llll_opy_ else None
            bstack1l1111ll1l1_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack11lll1l1l11_opy_, None) if bstack11llllllll1_opy_ else None
            if isinstance(bstack1l1111ll1l1_opy_, dict) and len(bstack1l1111ll1l1_opy_.get(bstack11llllllll1_opy_, [])) > 0:
                hook = bstack1l1111ll1l1_opy_[bstack11llllllll1_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack11llll1l1l1_opy_ in hook:
                    hook[TestFramework.bstack11llll1l1l1_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1111l11l1_opy_, [])
            logs.extend(records)
    @staticmethod
    def __11llll111l1_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l11ll1l1_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__11llllll1l1_opy_(request.node, scenario)
        bstack11lll1ll1l1_opy_ = feature.filename
        if not bstack1l11ll1l1_opy_ or not test_name or not bstack11lll1ll1l1_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll11l1ll1l_opy_: uuid4().__str__(),
            TestFramework.bstack1l1111ll11l_opy_: bstack1l11ll1l1_opy_,
            TestFramework.bstack1ll111l1l1l_opy_: test_name,
            TestFramework.bstack1l1l1111l11_opy_: bstack1l11ll1l1_opy_,
            TestFramework.bstack11lllll1l11_opy_: bstack11lll1ll1l1_opy_,
            TestFramework.bstack1l1111l11ll_opy_: PytestBDDFramework.__11llll11l11_opy_(feature, scenario),
            TestFramework.bstack11lll1ll111_opy_: code,
            TestFramework.bstack1l11ll11lll_opy_: TestFramework.bstack11lll1l1lll_opy_,
            TestFramework.bstack1l111ll1111_opy_: test_name
        }
    @staticmethod
    def __11llllll1l1_opy_(node, scenario):
        if hasattr(node, bstack1l1l_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫᕁ")):
            parts = node.nodeid.rsplit(bstack1l1l_opy_ (u"ࠥ࡟ࠧᕂ"))
            params = parts[-1]
            return bstack1l1l_opy_ (u"ࠦࢀࢃࠠ࡜ࡽࢀࠦᕃ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __11llll11l11_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack1l1l_opy_ (u"ࠬࡺࡡࡨࡵࠪᕄ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack1l1l_opy_ (u"࠭ࡴࡢࡩࡶࠫᕅ")) else [])
    @staticmethod
    def __1l1111l111l_opy_(location):
        return bstack1l1l_opy_ (u"ࠢ࠻࠼ࠥᕆ").join(filter(lambda x: isinstance(x, str), location))