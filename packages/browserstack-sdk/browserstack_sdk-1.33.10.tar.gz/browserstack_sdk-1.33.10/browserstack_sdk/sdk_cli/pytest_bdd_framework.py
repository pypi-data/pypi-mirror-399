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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1lll1lll1ll_opy_ import bstack1llll1l11ll_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l1l11l11_opy_ import bstack1l111111l1l_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1ll1l11ll1l_opy_,
    bstack1lll1ll1ll1_opy_,
    bstack1lll1ll1111_opy_,
    bstack1l1111ll1l1_opy_,
    bstack1ll1lllll11_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1l1ll1lll_opy_
from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1lll1l1lll1_opy_ import bstack1ll1l1l111l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll1l1l1_opy_
bstack1l1l11lllll_opy_ = bstack1l1l1ll1lll_opy_()
bstack1l1l11l1111_opy_ = bstack11111l_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦᒍ")
bstack11llllllll1_opy_ = bstack11111l_opy_ (u"ࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠣᒎ")
bstack11llll11l11_opy_ = bstack11111l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠧᒏ")
bstack11lll1l1ll1_opy_ = 1.0
_1l1ll111111_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1l111l111ll_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢᒐ")
    bstack1l111111lll_opy_ = bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࠨᒑ")
    bstack1l1111111ll_opy_ = bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤࠣᒒ")
    bstack11lll1l1l1l_opy_ = bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣࡸࡺࡡࡳࡶࡨࡨࠧᒓ")
    bstack11llll11ll1_opy_ = bstack11111l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟࡭ࡣࡶࡸࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᒔ")
    bstack11llll1111l_opy_: bool
    bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_  = None
    bstack1l1111l1111_opy_ = [
        bstack1ll1l11ll1l_opy_.BEFORE_ALL,
        bstack1ll1l11ll1l_opy_.AFTER_ALL,
        bstack1ll1l11ll1l_opy_.BEFORE_EACH,
        bstack1ll1l11ll1l_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lllll11ll_opy_: Dict[str, str],
        bstack1l1llll11ll_opy_: List[str]=[bstack11111l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤᒕ")],
        bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_ = None,
        bstack1lll1l1l1l1_opy_=None
    ):
        super().__init__(bstack1l1llll11ll_opy_, bstack11lllll11ll_opy_, bstack1lllll1l11l_opy_)
        self.bstack11llll1111l_opy_ = any(bstack11111l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥᒖ") in item.lower() for item in bstack1l1llll11ll_opy_)
        self.bstack1lll1l1l1l1_opy_ = bstack1lll1l1l1l1_opy_
    def track_event(
        self,
        context: bstack1l1111ll1l1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        test_hook_state: bstack1lll1ll1111_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1ll1l11ll1l_opy_.TEST or test_framework_state in PytestBDDFramework.bstack1l1111l1111_opy_:
            bstack1l111111l1l_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1ll1l11ll1l_opy_.NONE:
            self.logger.warning(bstack11111l_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫ࡤࠡࡥࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࠣᒗ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠣࠤᒘ"))
            return
        if not self.bstack11llll1111l_opy_:
            self.logger.warning(bstack11111l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠿ࠥᒙ") + str(str(self.bstack1l1llll11ll_opy_)) + bstack11111l_opy_ (u"ࠥࠦᒚ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11111l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᒛ") + str(kwargs) + bstack11111l_opy_ (u"ࠧࠨᒜ"))
            return
        instance = self.__1l1111l11l1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11111l_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡡࡳࡩࡶࡁࠧᒝ") + str(args) + bstack11111l_opy_ (u"ࠢࠣᒞ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l1111l1111_opy_ and test_hook_state == bstack1lll1ll1111_opy_.PRE:
                bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack1l1l1111l_opy_.value)
                name = str(EVENTS.bstack1l1l1111l_opy_.name)+bstack11111l_opy_ (u"ࠣ࠼ࠥᒟ")+str(test_framework_state.name)
                TestFramework.bstack11lll1ll1l1_opy_(instance, name, bstack1l1lll1ll1l_opy_)
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶࠥࡶࡲࡦ࠼ࠣࡿࢂࠨᒠ").format(e))
        try:
            if test_framework_state == bstack1ll1l11ll1l_opy_.TEST:
                if not TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack11llll1llll_opy_) and test_hook_state == bstack1lll1ll1111_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__11llll1l111_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack11111l_opy_ (u"ࠥࡰࡴࡧࡤࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒡ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠦࠧᒢ"))
                if test_hook_state == bstack1lll1ll1111_opy_.PRE and not TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1l111ll_opy_):
                    TestFramework.bstack1llll1l1lll_opy_(instance, TestFramework.bstack1l1l1l111ll_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__11llllll111_opy_(instance, args)
                    self.logger.debug(bstack11111l_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡴࡶࡤࡶࡹࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒣ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠨࠢᒤ"))
                elif test_hook_state == bstack1lll1ll1111_opy_.POST and not TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l11lll1l_opy_):
                    TestFramework.bstack1llll1l1lll_opy_(instance, TestFramework.bstack1l1l11lll1l_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11111l_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡨࡲࡩࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒥ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠣࠤᒦ"))
            elif test_framework_state == bstack1ll1l11ll1l_opy_.STEP:
                if test_hook_state == bstack1lll1ll1111_opy_.PRE:
                    PytestBDDFramework.__1l1111l1ll1_opy_(instance, args)
                elif test_hook_state == bstack1lll1ll1111_opy_.POST:
                    PytestBDDFramework.__11lll1lll11_opy_(instance, args)
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG and test_hook_state == bstack1lll1ll1111_opy_.POST:
                PytestBDDFramework.__11llll1lll1_opy_(instance, *args)
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG_REPORT and test_hook_state == bstack1lll1ll1111_opy_.POST:
                self.__11lll1l1lll_opy_(instance, *args)
                self.__1l11111lll1_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack1l1111l1111_opy_:
                self.__1l11111llll_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥᒧ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠥࠦᒨ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11lll1l1l11_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l1111l1111_opy_ and test_hook_state == bstack1lll1ll1111_opy_.POST:
                name = str(EVENTS.bstack1l1l1111l_opy_.name)+bstack11111l_opy_ (u"ࠦ࠿ࠨᒩ")+str(test_framework_state.name)
                bstack1l1lll1ll1l_opy_ = TestFramework.bstack1l1111ll111_opy_(instance, name)
                bstack1ll1l111ll1_opy_.end(EVENTS.bstack1l1l1111l_opy_.value, bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᒪ"), bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᒫ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢᒬ").format(e))
    def bstack1l1l11l11l1_opy_(self):
        return self.bstack11llll1111l_opy_
    def __1l1111ll11l_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11111l_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᒭ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l111ll11_opy_(rep, [bstack11111l_opy_ (u"ࠤࡺ࡬ࡪࡴࠢᒮ"), bstack11111l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᒯ"), bstack11111l_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦᒰ"), bstack11111l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᒱ"), bstack11111l_opy_ (u"ࠨࡳ࡬࡫ࡳࡴࡪࡪࠢᒲ"), bstack11111l_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨᒳ")])
        return None
    def __11lll1l1lll_opy_(self, instance: bstack1lll1ll1ll1_opy_, *args):
        result = self.__1l1111ll11l_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll1111_opy_ = None
        if result.get(bstack11111l_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᒴ"), None) == bstack11111l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤᒵ") and len(args) > 1 and getattr(args[1], bstack11111l_opy_ (u"ࠥࡩࡽࡩࡩ࡯ࡨࡲࠦᒶ"), None) is not None:
            failure = [{bstack11111l_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧᒷ"): [args[1].excinfo.exconly(), result.get(bstack11111l_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᒸ"), None)]}]
            bstack1llllll1111_opy_ = bstack11111l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢᒹ") if bstack11111l_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥᒺ") in getattr(args[1].excinfo, bstack11111l_opy_ (u"ࠣࡶࡼࡴࡪࡴࡡ࡮ࡧࠥᒻ"), bstack11111l_opy_ (u"ࠤࠥᒼ")) else bstack11111l_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᒽ")
        bstack1l111l11l11_opy_ = result.get(bstack11111l_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᒾ"), TestFramework.bstack1l111111111_opy_)
        if bstack1l111l11l11_opy_ != TestFramework.bstack1l111111111_opy_:
            TestFramework.bstack1llll1l1lll_opy_(instance, TestFramework.bstack1l1l1l11l1l_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l1111lll11_opy_(instance, {
            TestFramework.bstack1l11ll11lll_opy_: failure,
            TestFramework.bstack1l111111ll1_opy_: bstack1llllll1111_opy_,
            TestFramework.bstack1l11l1ll1l1_opy_: bstack1l111l11l11_opy_,
        })
    def __1l1111l11l1_opy_(
        self,
        context: bstack1l1111ll1l1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        test_hook_state: bstack1lll1ll1111_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1ll1l11ll1l_opy_.SETUP_FIXTURE:
            instance = self.__1l1111l1l11_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack11lllllll1l_opy_ bstack1l111111l11_opy_ this to be bstack11111l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᒿ")
            if test_framework_state == bstack1ll1l11ll1l_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__11lll1ll111_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11111l_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᓀ"), None), bstack11111l_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᓁ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11111l_opy_ (u"ࠣࡰࡲࡨࡪࠨᓂ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack11111l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᓃ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1lllll11l1l_opy_(target) if target else None
        return instance
    def __1l11111llll_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        test_hook_state: bstack1lll1ll1111_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack11lllll1ll1_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, PytestBDDFramework.bstack1l111111lll_opy_, {})
        if not key in bstack11lllll1ll1_opy_:
            bstack11lllll1ll1_opy_[key] = []
        bstack1l1111llll1_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, PytestBDDFramework.bstack1l1111111ll_opy_, {})
        if not key in bstack1l1111llll1_opy_:
            bstack1l1111llll1_opy_[key] = []
        bstack1l11111111l_opy_ = {
            PytestBDDFramework.bstack1l111111lll_opy_: bstack11lllll1ll1_opy_,
            PytestBDDFramework.bstack1l1111111ll_opy_: bstack1l1111llll1_opy_,
        }
        if test_hook_state == bstack1lll1ll1111_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack11111l_opy_ (u"ࠥ࡯ࡪࡿࠢᓄ"): key,
                TestFramework.bstack1l1111l111l_opy_: uuid4().__str__(),
                TestFramework.bstack1l1111l11ll_opy_: TestFramework.bstack1l11111l1ll_opy_,
                TestFramework.bstack1l111l1111l_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11lll1ll1ll_opy_: [],
                TestFramework.bstack1l11111l11l_opy_: hook_name,
                TestFramework.bstack1l11111ll1l_opy_: bstack1ll1l1l111l_opy_.bstack1l1111l1l1l_opy_()
            }
            bstack11lllll1ll1_opy_[key].append(hook)
            bstack1l11111111l_opy_[PytestBDDFramework.bstack11lll1l1l1l_opy_] = key
        elif test_hook_state == bstack1lll1ll1111_opy_.POST:
            bstack1l11111ll11_opy_ = bstack11lllll1ll1_opy_.get(key, [])
            hook = bstack1l11111ll11_opy_.pop() if bstack1l11111ll11_opy_ else None
            if hook:
                result = self.__1l1111ll11l_opy_(*args)
                if result:
                    bstack1l111l11111_opy_ = result.get(bstack11111l_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᓅ"), TestFramework.bstack1l11111l1ll_opy_)
                    if bstack1l111l11111_opy_ != TestFramework.bstack1l11111l1ll_opy_:
                        hook[TestFramework.bstack1l1111l11ll_opy_] = bstack1l111l11111_opy_
                hook[TestFramework.bstack11llll1l1l1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l11111ll1l_opy_] = bstack1ll1l1l111l_opy_.bstack1l1111l1l1l_opy_()
                self.bstack1l1111lll1l_opy_(hook)
                logs = hook.get(TestFramework.bstack1l1111l1lll_opy_, [])
                self.bstack1l1ll11llll_opy_(instance, logs)
                bstack1l1111llll1_opy_[key].append(hook)
                bstack1l11111111l_opy_[PytestBDDFramework.bstack11llll11ll1_opy_] = key
        TestFramework.bstack1l1111lll11_opy_(instance, bstack1l11111111l_opy_)
        self.logger.debug(bstack11111l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡭ࡵ࡯࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࡱࡥࡺࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪ࠽ࡼࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡾࠢ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡀࠦᓆ") + str(bstack1l1111llll1_opy_) + bstack11111l_opy_ (u"ࠨࠢᓇ"))
    def __1l1111l1l11_opy_(
        self,
        context: bstack1l1111ll1l1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        test_hook_state: bstack1lll1ll1111_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l111ll11_opy_(args[0], [bstack11111l_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᓈ"), bstack11111l_opy_ (u"ࠣࡣࡵ࡫ࡳࡧ࡭ࡦࠤᓉ"), bstack11111l_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤᓊ"), bstack11111l_opy_ (u"ࠥ࡭ࡩࡹࠢᓋ"), bstack11111l_opy_ (u"ࠦࡺࡴࡩࡵࡶࡨࡷࡹࠨᓌ"), bstack11111l_opy_ (u"ࠧࡨࡡࡴࡧ࡬ࡨࠧᓍ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack11111l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᓎ")) else fixturedef.get(bstack11111l_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᓏ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11111l_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࠨᓐ")) else None
        node = request.node if hasattr(request, bstack11111l_opy_ (u"ࠤࡱࡳࡩ࡫ࠢᓑ")) else None
        target = request.node.nodeid if hasattr(node, bstack11111l_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᓒ")) else None
        baseid = fixturedef.get(bstack11111l_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᓓ"), None) or bstack11111l_opy_ (u"ࠧࠨᓔ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11111l_opy_ (u"ࠨ࡟ࡱࡻࡩࡹࡳࡩࡩࡵࡧࡰࠦᓕ")):
            target = PytestBDDFramework.__11lll1lllll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11111l_opy_ (u"ࠢ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᓖ")) else None
            if target and not TestFramework.bstack1lllll11l1l_opy_(target):
                self.__11lll1ll111_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11111l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡦࡸࡧࡦࡶࡀࡿࡹࡧࡲࡨࡧࡷࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡲࡴࡪࡥ࠾ࡽࡱࡳࡩ࡫ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᓗ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠤࠥᓘ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11111l_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࠣᓙ") + str(target) + bstack11111l_opy_ (u"ࠦࠧᓚ"))
            return None
        instance = TestFramework.bstack1lllll11l1l_opy_(target)
        if not instance:
            self.logger.warning(bstack11111l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤࡧࡧࡳࡦ࡫ࡧࡁࢀࡨࡡࡴࡧ࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᓛ") + str(target) + bstack11111l_opy_ (u"ࠨࠢᓜ"))
            return None
        bstack11lllllllll_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, PytestBDDFramework.bstack1l111l111ll_opy_, {})
        if os.getenv(bstack11111l_opy_ (u"ࠢࡔࡆࡎࡣࡈࡒࡉࡠࡈࡏࡅࡌࡥࡆࡊ࡚ࡗ࡙ࡗࡋࡓࠣᓝ"), bstack11111l_opy_ (u"ࠣ࠳ࠥᓞ")) == bstack11111l_opy_ (u"ࠤ࠴ࠦᓟ"):
            bstack11llll1ll1l_opy_ = bstack11111l_opy_ (u"ࠥ࠾ࠧᓠ").join((scope, fixturename))
            bstack11llllll1ll_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111ll1ll_opy_ = {
                bstack11111l_opy_ (u"ࠦࡰ࡫ࡹࠣᓡ"): bstack11llll1ll1l_opy_,
                bstack11111l_opy_ (u"ࠧࡺࡡࡨࡵࠥᓢ"): PytestBDDFramework.__11lll1ll11l_opy_(request.node, scenario),
                bstack11111l_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫ࠢᓣ"): fixturedef,
                bstack11111l_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᓤ"): scope,
                bstack11111l_opy_ (u"ࠣࡶࡼࡴࡪࠨᓥ"): None,
            }
            try:
                if test_hook_state == bstack1lll1ll1111_opy_.POST and callable(getattr(args[-1], bstack11111l_opy_ (u"ࠤࡪࡩࡹࡥࡲࡦࡵࡸࡰࡹࠨᓦ"), None)):
                    bstack1l1111ll1ll_opy_[bstack11111l_opy_ (u"ࠥࡸࡾࡶࡥࠣᓧ")] = TestFramework.bstack1l1l1l1lll1_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1ll1111_opy_.PRE:
                bstack1l1111ll1ll_opy_[bstack11111l_opy_ (u"ࠦࡺࡻࡩࡥࠤᓨ")] = uuid4().__str__()
                bstack1l1111ll1ll_opy_[PytestBDDFramework.bstack1l111l1111l_opy_] = bstack11llllll1ll_opy_
            elif test_hook_state == bstack1lll1ll1111_opy_.POST:
                bstack1l1111ll1ll_opy_[PytestBDDFramework.bstack11llll1l1l1_opy_] = bstack11llllll1ll_opy_
            if bstack11llll1ll1l_opy_ in bstack11lllllllll_opy_:
                bstack11lllllllll_opy_[bstack11llll1ll1l_opy_].update(bstack1l1111ll1ll_opy_)
                self.logger.debug(bstack11111l_opy_ (u"ࠧࡻࡰࡥࡣࡷࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࠨᓩ") + str(bstack11lllllllll_opy_[bstack11llll1ll1l_opy_]) + bstack11111l_opy_ (u"ࠨࠢᓪ"))
            else:
                bstack11lllllllll_opy_[bstack11llll1ll1l_opy_] = bstack1l1111ll1ll_opy_
                self.logger.debug(bstack11111l_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࢁࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࢂࠦࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࠥᓫ") + str(len(bstack11lllllllll_opy_)) + bstack11111l_opy_ (u"ࠣࠤᓬ"))
        TestFramework.bstack1llll1l1lll_opy_(instance, PytestBDDFramework.bstack1l111l111ll_opy_, bstack11lllllllll_opy_)
        self.logger.debug(bstack11111l_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡵࡀࡿࡱ࡫࡮ࠩࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶ࠭ࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᓭ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠥࠦᓮ"))
        return instance
    def __11lll1ll111_opy_(
        self,
        context: bstack1l1111ll1l1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1llll1l11ll_opy_.create_context(target)
        ob = bstack1lll1ll1ll1_opy_(ctx, self.bstack1l1llll11ll_opy_, self.bstack11lllll11ll_opy_, test_framework_state)
        TestFramework.bstack1l1111lll11_opy_(ob, {
            TestFramework.bstack1l1lllllll1_opy_: context.test_framework_name,
            TestFramework.bstack1l1l111llll_opy_: context.test_framework_version,
            TestFramework.bstack11llll1l1ll_opy_: [],
            PytestBDDFramework.bstack1l111l111ll_opy_: {},
            PytestBDDFramework.bstack1l1111111ll_opy_: {},
            PytestBDDFramework.bstack1l111111lll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll1l1lll_opy_(ob, TestFramework.bstack11llll11lll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll1l1lll_opy_(ob, TestFramework.bstack1ll111ll111_opy_, context.platform_index)
        TestFramework.bstack1lll1llllll_opy_[ctx.id] = ob
        self.logger.debug(bstack11111l_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠥࡩࡴࡹ࠰࡬ࡨࡂࢁࡣࡵࡺ࠱࡭ࡩࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࡼࡶࡤࡶ࡬࡫ࡴࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦࡵࡀࠦᓯ") + str(TestFramework.bstack1lll1llllll_opy_.keys()) + bstack11111l_opy_ (u"ࠧࠨᓰ"))
        return ob
    @staticmethod
    def __11llllll111_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11111l_opy_ (u"࠭ࡩࡥࠩᓱ"): id(step),
                bstack11111l_opy_ (u"ࠧࡵࡧࡻࡸࠬᓲ"): step.name,
                bstack11111l_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥࠩᓳ"): step.keyword,
            })
        meta = {
            bstack11111l_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࠪᓴ"): {
                bstack11111l_opy_ (u"ࠪࡲࡦࡳࡥࠨᓵ"): feature.name,
                bstack11111l_opy_ (u"ࠫࡵࡧࡴࡩࠩᓶ"): feature.filename,
                bstack11111l_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᓷ"): feature.description
            },
            bstack11111l_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨᓸ"): {
                bstack11111l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᓹ"): scenario.name
            },
            bstack11111l_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧᓺ"): steps,
            bstack11111l_opy_ (u"ࠩࡨࡼࡦࡳࡰ࡭ࡧࡶࠫᓻ"): PytestBDDFramework.__11lllll111l_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l111l111l1_opy_: meta
            }
        )
    def bstack1l1111lll1l_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡴࡲࡧࡪࡹࡳࡦࡵࠣࡸ࡭࡫ࠠࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡵ࡬ࡱ࡮ࡲࡡࡳࠢࡷࡳࠥࡺࡨࡦࠢࡍࡥࡻࡧࠠࡪ࡯ࡳࡰࡪࡳࡥ࡯ࡶࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡘ࡭࡯ࡳࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡄࡪࡨࡧࡰࡹࠠࡵࡪࡨࠤࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣ࡭ࡳࡹࡩࡥࡧࠣࢂ࠴࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠴࡛ࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡊࡴࡸࠠࡦࡣࡦ࡬ࠥ࡬ࡩ࡭ࡧࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠮ࠣࡶࡪࡶ࡬ࡢࡥࡨࡷࠥࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰࠧࠦࡩ࡯ࠢ࡬ࡸࡸࠦࡰࡢࡶ࡫࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡍ࡫ࠦࡡࠡࡨ࡬ࡰࡪࠦࡩ࡯ࠢࡷ࡬ࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡰࡥࡹࡩࡨࡦࡵࠣࡥࠥࡳ࡯ࡥ࡫ࡩ࡭ࡪࡪࠠࡩࡱࡲ࡯࠲ࡲࡥࡷࡧ࡯ࠤ࡫࡯࡬ࡦ࠮ࠣ࡭ࡹࠦࡣࡳࡧࡤࡸࡪࡹࠠࡢࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࠤࡼ࡯ࡴࡩࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡤࡦࡶࡤ࡭ࡱࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡓࡪ࡯࡬ࡰࡦࡸ࡬ࡺ࠮ࠣ࡭ࡹࠦࡰࡳࡱࡦࡩࡸࡹࡥࡴࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡱࡵࡣࡢࡶࡨࡨࠥ࡯࡮ࠡࡊࡲࡳࡰࡒࡥࡷࡧ࡯࠳ࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡦࡾࠦࡲࡦࡲ࡯ࡥࡨ࡯࡮ࡨࠢࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮࠲ࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠤ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡗ࡬ࡪࠦࡣࡳࡧࡤࡸࡪࡪࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡥࡷ࡫ࠠࡢࡦࡧࡩࡩࠦࡴࡰࠢࡷ࡬ࡪࠦࡨࡰࡱ࡮ࠫࡸࠦࠢ࡭ࡱࡪࡷࠧࠦ࡬ࡪࡵࡷ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫࠻ࠢࡗ࡬ࡪࠦࡥࡷࡧࡱࡸࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡺࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࠦࡡ࡯ࡦࠣ࡬ࡴࡵ࡫ࠡ࡫ࡱࡪࡴࡸ࡭ࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭ࡢࡰࡪࡼࡥ࡭ࡡࡩ࡭ࡱ࡫ࡳ࠻ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡔࡦࡺࡨࠡࡱࡥ࡮ࡪࡩࡴࡴࠢࡩࡶࡴࡳࠠࡵࡪࡨࠤ࡙࡫ࡳࡵࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡦࡺ࡯࡬ࡥࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹ࠺ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡓࡥࡹ࡮ࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᓼ")
        global _1l1ll111111_opy_
        platform_index = os.environ[bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᓽ")]
        bstack1l1l1lllll1_opy_ = os.path.join(bstack1l1l11lllll_opy_, (bstack1l1l11l1111_opy_ + str(platform_index)), bstack11llllllll1_opy_)
        if not os.path.exists(bstack1l1l1lllll1_opy_) or not os.path.isdir(bstack1l1l1lllll1_opy_):
            return
        logs = hook.get(bstack11111l_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᓾ"), [])
        with os.scandir(bstack1l1l1lllll1_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll111111_opy_:
                    self.logger.info(bstack11111l_opy_ (u"ࠨࡐࡢࡶ࡫ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡽࢀࠦᓿ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11111l_opy_ (u"ࠢࠣᔀ")
                    log_entry = bstack1ll1lllll11_opy_(
                        kind=bstack11111l_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᔁ"),
                        message=bstack11111l_opy_ (u"ࠤࠥᔂ"),
                        level=bstack11111l_opy_ (u"ࠥࠦᔃ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll1111ll_opy_=entry.stat().st_size,
                        bstack1l1l1l1l111_opy_=bstack11111l_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦᔄ"),
                        bstack1l1ll11_opy_=os.path.abspath(entry.path),
                        bstack11lllll1111_opy_=hook.get(TestFramework.bstack1l1111l111l_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll111111_opy_.add(abs_path)
        platform_index = os.environ[bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᔅ")]
        bstack11lllll1l1l_opy_ = os.path.join(bstack1l1l11lllll_opy_, (bstack1l1l11l1111_opy_ + str(platform_index)), bstack11llllllll1_opy_, bstack11llll11l11_opy_)
        if not os.path.exists(bstack11lllll1l1l_opy_) or not os.path.isdir(bstack11lllll1l1l_opy_):
            self.logger.info(bstack11111l_opy_ (u"ࠨࡎࡰࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡩࡳࡺࡴࡤࠡࡣࡷ࠾ࠥࢁࡽࠣᔆ").format(bstack11lllll1l1l_opy_))
        else:
            self.logger.info(bstack11111l_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡨࡵࡳࡲࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺ࠼ࠣࡿࢂࠨᔇ").format(bstack11lllll1l1l_opy_))
            with os.scandir(bstack11lllll1l1l_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll111111_opy_:
                        self.logger.info(bstack11111l_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᔈ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11111l_opy_ (u"ࠤࠥᔉ")
                        log_entry = bstack1ll1lllll11_opy_(
                            kind=bstack11111l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᔊ"),
                            message=bstack11111l_opy_ (u"ࠦࠧᔋ"),
                            level=bstack11111l_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤᔌ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll1111ll_opy_=entry.stat().st_size,
                            bstack1l1l1l1l111_opy_=bstack11111l_opy_ (u"ࠨࡍࡂࡐࡘࡅࡑࡥࡕࡑࡎࡒࡅࡉࠨᔍ"),
                            bstack1l1ll11_opy_=os.path.abspath(entry.path),
                            bstack1l1l1ll1ll1_opy_=hook.get(TestFramework.bstack1l1111l111l_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll111111_opy_.add(abs_path)
        hook[bstack11111l_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᔎ")] = logs
    def bstack1l1ll11llll_opy_(
        self,
        bstack1l1l1l1llll_opy_: bstack1lll1ll1ll1_opy_,
        entries: List[bstack1ll1lllll11_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11111l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡕࡈࡗࡘࡏࡏࡏࡡࡌࡈࠧᔏ"))
        req.platform_index = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1ll111ll111_opy_)
        req.execution_context.hash = str(bstack1l1l1l1llll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1l1llll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1l1llll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1lllllll1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1l111llll_opy_)
            log_entry.uuid = entry.bstack11lllll1111_opy_ if entry.bstack11lllll1111_opy_ else TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1ll11111l11_opy_)
            log_entry.test_framework_state = bstack1l1l1l1llll_opy_.state.name
            log_entry.message = entry.message.encode(bstack11111l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᔐ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11111l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᔑ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll1111ll_opy_
                log_entry.file_path = entry.bstack1l1ll11_opy_
        def bstack1l1l1lll11l_opy_():
            bstack1l1lll1ll_opy_ = datetime.now()
            try:
                self.bstack1lll1l1l1l1_opy_.LogCreatedEvent(req)
                bstack1l1l1l1llll_opy_.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣᔒ"), datetime.now() - bstack1l1lll1ll_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11111l_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡽࢀࠦᔓ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1lll11l_opy_)
    def __1l11111lll1_opy_(self, instance) -> None:
        bstack11111l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡐࡴࡧࡤࡴࠢࡦࡹࡸࡺ࡯࡮ࠢࡷࡥ࡬ࡹࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡩ࡬ࡺࡪࡴࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡉࡲࡦࡣࡷࡩࡸࠦࡡࠡࡦ࡬ࡧࡹࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣࡸࡪࡹࡴࠡ࡮ࡨࡺࡪࡲࠠࡤࡷࡶࡸࡴࡳࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡻࡳࡵࡱࡰࡘࡦ࡭ࡍࡢࡰࡤ࡫ࡪࡸࠠࡢࡰࡧࠤࡺࡶࡤࡢࡶࡨࡷࠥࡺࡨࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡸࡺࡡࡵࡧࠣࡹࡸ࡯࡮ࡨࠢࡶࡩࡹࡥࡳࡵࡣࡷࡩࡤ࡫࡮ࡵࡴ࡬ࡩࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᔔ")
        bstack1l11111111l_opy_ = {bstack11111l_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᔕ"): bstack1ll1l1l111l_opy_.bstack1l1111l1l1l_opy_()}
        TestFramework.bstack1l1111lll11_opy_(instance, bstack1l11111111l_opy_)
    @staticmethod
    def __1l1111l1ll1_opy_(instance, args):
        request, bstack1l11111l111_opy_ = args
        bstack11lllllll11_opy_ = id(bstack1l11111l111_opy_)
        bstack1l11111l1l1_opy_ = instance.data[TestFramework.bstack1l111l111l1_opy_]
        step = next(filter(lambda st: st[bstack11111l_opy_ (u"ࠨ࡫ࡧࠫᔖ")] == bstack11lllllll11_opy_, bstack1l11111l1l1_opy_[bstack11111l_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔗ")]), None)
        step.update({
            bstack11111l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᔘ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1l11111l1l1_opy_[bstack11111l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔙ")]) if st[bstack11111l_opy_ (u"ࠬ࡯ࡤࠨᔚ")] == step[bstack11111l_opy_ (u"࠭ࡩࡥࠩᔛ")]), None)
        if index is not None:
            bstack1l11111l1l1_opy_[bstack11111l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᔜ")][index] = step
        instance.data[TestFramework.bstack1l111l111l1_opy_] = bstack1l11111l1l1_opy_
    @staticmethod
    def __11lll1lll11_opy_(instance, args):
        bstack11111l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡽࡨࡦࡰࠣࡰࡪࡴࠠࡢࡴࡪࡷࠥ࡯ࡳࠡ࠴࠯ࠤ࡮ࡺࠠࡴ࡫ࡪࡲ࡮࡬ࡩࡦࡵࠣࡸ࡭࡫ࡲࡦࠢ࡬ࡷࠥࡴ࡯ࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡤࡶ࡬ࡹࠠࡢࡴࡨࠤ࠲࡛ࠦࡳࡧࡴࡹࡪࡹࡴ࠭ࠢࡶࡸࡪࡶ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡬ࡪࠥࡧࡲࡨࡵࠣࡥࡷ࡫ࠠ࠴ࠢࡷ࡬ࡪࡴࠠࡵࡪࡨࠤࡱࡧࡳࡵࠢࡹࡥࡱࡻࡥࠡ࡫ࡶࠤࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᔝ")
        bstack11lllll1l11_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l11111l111_opy_ = args[1]
        bstack11lllllll11_opy_ = id(bstack1l11111l111_opy_)
        bstack1l11111l1l1_opy_ = instance.data[TestFramework.bstack1l111l111l1_opy_]
        step = None
        if bstack11lllllll11_opy_ is not None and bstack1l11111l1l1_opy_.get(bstack11111l_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔞ")):
            step = next(filter(lambda st: st[bstack11111l_opy_ (u"ࠪ࡭ࡩ࠭ᔟ")] == bstack11lllllll11_opy_, bstack1l11111l1l1_opy_[bstack11111l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔠ")]), None)
            step.update({
                bstack11111l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪᔡ"): bstack11lllll1l11_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack11111l_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ᔢ"): bstack11111l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᔣ"),
                bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩᔤ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack11111l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᔥ"): bstack11111l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᔦ"),
                })
        index = next((i for i, st in enumerate(bstack1l11111l1l1_opy_[bstack11111l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᔧ")]) if st[bstack11111l_opy_ (u"ࠬ࡯ࡤࠨᔨ")] == step[bstack11111l_opy_ (u"࠭ࡩࡥࠩᔩ")]), None)
        if index is not None:
            bstack1l11111l1l1_opy_[bstack11111l_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᔪ")][index] = step
        instance.data[TestFramework.bstack1l111l111l1_opy_] = bstack1l11111l1l1_opy_
    @staticmethod
    def __11lllll111l_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack11111l_opy_ (u"ࠨࡥࡤࡰࡱࡹࡰࡦࡥࠪᔫ")):
                examples = list(node.callspec.params[bstack11111l_opy_ (u"ࠩࡢࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡦࡺࡤࡱࡵࡲࡥࠨᔬ")].values())
            return examples
        except:
            return []
    def bstack1l1l111ll1l_opy_(self, instance: bstack1lll1ll1ll1_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_]):
        bstack11lllll1lll_opy_ = (
            PytestBDDFramework.bstack11lll1l1l1l_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1ll1111_opy_.PRE
            else PytestBDDFramework.bstack11llll11ll1_opy_
        )
        hook = PytestBDDFramework.bstack1l111l11l1l_opy_(instance, bstack11lllll1lll_opy_)
        entries = hook.get(TestFramework.bstack11lll1ll1ll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack11llll1l1ll_opy_, []))
        return entries
    def bstack1l1l1llllll_opy_(self, instance: bstack1lll1ll1ll1_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_]):
        bstack11lllll1lll_opy_ = (
            PytestBDDFramework.bstack11lll1l1l1l_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1ll1111_opy_.PRE
            else PytestBDDFramework.bstack11llll11ll1_opy_
        )
        PytestBDDFramework.bstack1l1111lllll_opy_(instance, bstack11lllll1lll_opy_)
        TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack11llll1l1ll_opy_, []).clear()
    @staticmethod
    def bstack1l111l11l1l_opy_(instance: bstack1lll1ll1ll1_opy_, bstack11lllll1lll_opy_: str):
        bstack11llllll11l_opy_ = (
            PytestBDDFramework.bstack1l1111111ll_opy_
            if bstack11lllll1lll_opy_ == PytestBDDFramework.bstack11llll11ll1_opy_
            else PytestBDDFramework.bstack1l111111lll_opy_
        )
        bstack11llllll1l1_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack11lllll1lll_opy_, None)
        bstack11llll11111_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack11llllll11l_opy_, None) if bstack11llllll1l1_opy_ else None
        return (
            bstack11llll11111_opy_[bstack11llllll1l1_opy_][-1]
            if isinstance(bstack11llll11111_opy_, dict) and len(bstack11llll11111_opy_.get(bstack11llllll1l1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l1111lllll_opy_(instance: bstack1lll1ll1ll1_opy_, bstack11lllll1lll_opy_: str):
        hook = PytestBDDFramework.bstack1l111l11l1l_opy_(instance, bstack11lllll1lll_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11lll1ll1ll_opy_, []).clear()
    @staticmethod
    def __11llll1lll1_opy_(instance: bstack1lll1ll1ll1_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11111l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡦࡳࡷࡪࡳࠣᔭ"), None)):
            return
        if os.getenv(bstack11111l_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡐࡔࡍࡓࠣᔮ"), bstack11111l_opy_ (u"ࠧ࠷ࠢᔯ")) != bstack11111l_opy_ (u"ࠨ࠱ࠣᔰ"):
            PytestBDDFramework.logger.warning(bstack11111l_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡯࡮ࡨࠢࡦࡥࡵࡲ࡯ࡨࠤᔱ"))
            return
        bstack11llll11l1l_opy_ = {
            bstack11111l_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᔲ"): (PytestBDDFramework.bstack11lll1l1l1l_opy_, PytestBDDFramework.bstack1l111111lll_opy_),
            bstack11111l_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦᔳ"): (PytestBDDFramework.bstack11llll11ll1_opy_, PytestBDDFramework.bstack1l1111111ll_opy_),
        }
        for when in (bstack11111l_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᔴ"), bstack11111l_opy_ (u"ࠦࡨࡧ࡬࡭ࠤᔵ"), bstack11111l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢᔶ")):
            bstack11llll1ll11_opy_ = args[1].get_records(when)
            if not bstack11llll1ll11_opy_:
                continue
            records = [
                bstack1ll1lllll11_opy_(
                    kind=TestFramework.bstack1l1l111lll1_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11111l_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠤᔷ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11111l_opy_ (u"ࠢࡤࡴࡨࡥࡹ࡫ࡤࠣᔸ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll1ll11_opy_
                if isinstance(getattr(r, bstack11111l_opy_ (u"ࠣ࡯ࡨࡷࡸࡧࡧࡦࠤᔹ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack11llll111ll_opy_, bstack11llllll11l_opy_ = bstack11llll11l1l_opy_.get(when, (None, None))
            bstack1l1111111l1_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack11llll111ll_opy_, None) if bstack11llll111ll_opy_ else None
            bstack11llll11111_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack11llllll11l_opy_, None) if bstack1l1111111l1_opy_ else None
            if isinstance(bstack11llll11111_opy_, dict) and len(bstack11llll11111_opy_.get(bstack1l1111111l1_opy_, [])) > 0:
                hook = bstack11llll11111_opy_[bstack1l1111111l1_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack11lll1ll1ll_opy_ in hook:
                    hook[TestFramework.bstack11lll1ll1ll_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack11llll1l1ll_opy_, [])
            logs.extend(records)
    @staticmethod
    def __11llll1l111_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack111lll11_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__11lll1llll1_opy_(request.node, scenario)
        bstack11lll1lll1l_opy_ = feature.filename
        if not bstack111lll11_opy_ or not test_name or not bstack11lll1lll1l_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll11111l11_opy_: uuid4().__str__(),
            TestFramework.bstack11llll1llll_opy_: bstack111lll11_opy_,
            TestFramework.bstack1ll111111l1_opy_: test_name,
            TestFramework.bstack1l1l1111l11_opy_: bstack111lll11_opy_,
            TestFramework.bstack11llll1l11l_opy_: bstack11lll1lll1l_opy_,
            TestFramework.bstack11llll111l1_opy_: PytestBDDFramework.__11lll1ll11l_opy_(feature, scenario),
            TestFramework.bstack11lllll11l1_opy_: code,
            TestFramework.bstack1l11l1ll1l1_opy_: TestFramework.bstack1l111111111_opy_,
            TestFramework.bstack1l111lll11l_opy_: test_name
        }
    @staticmethod
    def __11lll1llll1_opy_(node, scenario):
        if hasattr(node, bstack11111l_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫᔺ")):
            parts = node.nodeid.rsplit(bstack11111l_opy_ (u"ࠥ࡟ࠧᔻ"))
            params = parts[-1]
            return bstack11111l_opy_ (u"ࠦࢀࢃࠠ࡜ࡽࢀࠦᔼ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __11lll1ll11l_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack11111l_opy_ (u"ࠬࡺࡡࡨࡵࠪᔽ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack11111l_opy_ (u"࠭ࡴࡢࡩࡶࠫᔾ")) else [])
    @staticmethod
    def __11lll1lllll_opy_(location):
        return bstack11111l_opy_ (u"ࠢ࠻࠼ࠥᔿ").join(filter(lambda x: isinstance(x, str), location))