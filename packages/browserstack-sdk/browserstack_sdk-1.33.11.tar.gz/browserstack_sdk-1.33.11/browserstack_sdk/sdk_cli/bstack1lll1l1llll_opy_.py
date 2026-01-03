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
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1ll1llll111_opy_,
    bstack1lll111l1ll_opy_,
    bstack1ll1ll111l1_opy_,
    bstack11lll1l1l1l_opy_,
    bstack1lll1l11l1l_opy_,
)
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from datetime import datetime, timezone
from typing import List, Dict, Any
import traceback
from bstack_utils.helper import bstack1l1l11lll11_opy_
from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.bstack1lllll1ll1l_opy_ import bstack1lllll1lll1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1lll1l11lll_opy_ import bstack1ll1l1ll1ll_opy_
from bstack_utils.bstack111ll11l11_opy_ import bstack1l1ll11111_opy_
bstack1l1l11l1l1l_opy_ = bstack1l1l11lll11_opy_()
bstack1l11111111l_opy_ = 1.0
bstack1l1l1l1l1l1_opy_ = bstack1l1l_opy_ (u"ࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣᕇ")
bstack11lll11ll11_opy_ = bstack1l1l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᕈ")
bstack11lll11lll1_opy_ = bstack1l1l_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᕉ")
bstack11lll11ll1l_opy_ = bstack1l1l_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᕊ")
bstack11lll1l111l_opy_ = bstack1l1l_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᕋ")
_1l1l1l1l111_opy_ = set()
class bstack1ll1ll11lll_opy_(TestFramework):
    bstack11llllll1ll_opy_ = bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨᕌ")
    bstack11lll1l1ll1_opy_ = bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࠧᕍ")
    bstack1l111l11111_opy_ = bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᕎ")
    bstack1l1111lll1l_opy_ = bstack1l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࠦᕏ")
    bstack1l11111ll11_opy_ = bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᕐ")
    bstack1l111111l11_opy_: bool
    bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_  = None
    bstack1ll1l11111l_opy_ = None
    bstack11llll11ll1_opy_ = [
        bstack1ll1llll111_opy_.BEFORE_ALL,
        bstack1ll1llll111_opy_.AFTER_ALL,
        bstack1ll1llll111_opy_.BEFORE_EACH,
        bstack1ll1llll111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11llll1llll_opy_: Dict[str, str],
        bstack1ll11l111ll_opy_: List[str]=[bstack1l1l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᕑ")],
        bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_=None,
        bstack1ll1l11111l_opy_=None
    ):
        super().__init__(bstack1ll11l111ll_opy_, bstack11llll1llll_opy_, bstack1lllll1ll1l_opy_)
        self.bstack1l111111l11_opy_ = any(bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᕒ") in item.lower() for item in bstack1ll11l111ll_opy_)
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
        if test_framework_state == bstack1ll1llll111_opy_.TEST or test_framework_state in bstack1ll1ll11lll_opy_.bstack11llll11ll1_opy_:
            bstack11lllll1111_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1ll1llll111_opy_.NONE:
            self.logger.warning(bstack1l1l_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡪࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࠢᕓ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠢࠣᕔ"))
            return
        if not self.bstack1l111111l11_opy_:
            self.logger.warning(bstack1l1l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠾ࠤᕕ") + str(str(self.bstack1ll11l111ll_opy_)) + bstack1l1l_opy_ (u"ࠤࠥᕖ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1l1l_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᕗ") + str(kwargs) + bstack1l1l_opy_ (u"ࠦࠧᕘ"))
            return
        instance = self.__11llll1l11l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡧࡲࡨࡵࡀࠦᕙ") + str(args) + bstack1l1l_opy_ (u"ࠨࠢᕚ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1ll1ll11lll_opy_.bstack11llll11ll1_opy_ and test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1lll1l1l11_opy_.value)
                name = str(EVENTS.bstack1lll1l1l11_opy_.name)+bstack1l1l_opy_ (u"ࠢ࠻ࠤᕛ")+str(test_framework_state.name)
                TestFramework.bstack11llll1l1ll_opy_(instance, name, bstack1ll11l111l1_opy_)
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࠥ࡫ࡲࡳࡱࡵࠤࡵࡸࡥ࠻ࠢࡾࢁࠧᕜ").format(e))
        try:
            if not TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1111ll11l_opy_) and test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                test = bstack1ll1ll11lll_opy_.__11llll111l1_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡯ࡳࡦࡪࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕝ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠥࠦᕞ"))
            if test_framework_state == bstack1ll1llll111_opy_.TEST:
                if test_hook_state == bstack1ll1ll111l1_opy_.PRE and not TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1l1l11ll1_opy_):
                    TestFramework.bstack1llll1lll11_opy_(instance, TestFramework.bstack1l1l1l11ll1_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1l1l_opy_ (u"ࠦࡸ࡫ࡴࠡࡶࡨࡷࡹ࠳ࡳࡵࡣࡵࡸࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕟ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠧࠨᕠ"))
                elif test_hook_state == bstack1ll1ll111l1_opy_.POST and not TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1ll111l11_opy_):
                    TestFramework.bstack1llll1lll11_opy_(instance, TestFramework.bstack1l1ll111l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1l1l_opy_ (u"ࠨࡳࡦࡶࠣࡸࡪࡹࡴ࠮ࡧࡱࡨࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕡ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠢࠣᕢ"))
            elif test_framework_state == bstack1ll1llll111_opy_.LOG and test_hook_state == bstack1ll1ll111l1_opy_.POST:
                bstack1ll1ll11lll_opy_.__1l1111llll1_opy_(instance, *args)
            elif test_framework_state == bstack1ll1llll111_opy_.LOG_REPORT and test_hook_state == bstack1ll1ll111l1_opy_.POST:
                self.__11lllllll11_opy_(instance, *args)
                self.__11lll1llll1_opy_(instance)
            elif test_framework_state in bstack1ll1ll11lll_opy_.bstack11llll11ll1_opy_:
                self.__11lllll1ll1_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᕣ") + str(instance.ref()) + bstack1l1l_opy_ (u"ࠤࠥᕤ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11lll1lllll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1ll1ll11lll_opy_.bstack11llll11ll1_opy_ and test_hook_state == bstack1ll1ll111l1_opy_.POST:
                name = str(EVENTS.bstack1lll1l1l11_opy_.name)+bstack1l1l_opy_ (u"ࠥ࠾ࠧᕥ")+str(test_framework_state.name)
                bstack1ll11l111l1_opy_ = TestFramework.bstack1l1111l1l11_opy_(instance, name)
                bstack1ll1l1ll111_opy_.end(EVENTS.bstack1lll1l1l11_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᕦ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᕧ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᕨ").format(e))
    def bstack1l1l1ll1111_opy_(self):
        return self.bstack1l111111l11_opy_
    def __1l1111lll11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1l1l_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᕩ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l1ll111l_opy_(rep, [bstack1l1l_opy_ (u"ࠣࡹ࡫ࡩࡳࠨᕪ"), bstack1l1l_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᕫ"), bstack1l1l_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥᕬ"), bstack1l1l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᕭ"), bstack1l1l_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠨᕮ"), bstack1l1l_opy_ (u"ࠨ࡬ࡰࡰࡪࡶࡪࡶࡲࡵࡧࡻࡸࠧᕯ")])
        return None
    def __11lllllll11_opy_(self, instance: bstack1lll111l1ll_opy_, *args):
        result = self.__1l1111lll11_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll111l_opy_ = None
        if result.get(bstack1l1l_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᕰ"), None) == bstack1l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣᕱ") and len(args) > 1 and getattr(args[1], bstack1l1l_opy_ (u"ࠤࡨࡼࡨ࡯࡮ࡧࡱࠥᕲ"), None) is not None:
            failure = [{bstack1l1l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᕳ"): [args[1].excinfo.exconly(), result.get(bstack1l1l_opy_ (u"ࠦࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠥᕴ"), None)]}]
            bstack1llllll111l_opy_ = bstack1l1l_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨᕵ") if bstack1l1l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᕶ") in getattr(args[1].excinfo, bstack1l1l_opy_ (u"ࠢࡵࡻࡳࡩࡳࡧ࡭ࡦࠤᕷ"), bstack1l1l_opy_ (u"ࠣࠤᕸ")) else bstack1l1l_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᕹ")
        bstack1l111l111ll_opy_ = result.get(bstack1l1l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᕺ"), TestFramework.bstack11lll1l1lll_opy_)
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
            target = None # bstack11lllllllll_opy_ bstack1l11111l111_opy_ this to be bstack1l1l_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᕻ")
            if test_framework_state == bstack1ll1llll111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l111111lll_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1ll1llll111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1l1l_opy_ (u"ࠧࡴ࡯ࡥࡧࠥᕼ"), None), bstack1l1l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᕽ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1l1l_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᕾ"), None):
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
        bstack11llllll11l_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack1ll1ll11lll_opy_.bstack11lll1l1ll1_opy_, {})
        if not key in bstack11llllll11l_opy_:
            bstack11llllll11l_opy_[key] = []
        bstack11lll1l11ll_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack1ll1ll11lll_opy_.bstack1l111l11111_opy_, {})
        if not key in bstack11lll1l11ll_opy_:
            bstack11lll1l11ll_opy_[key] = []
        bstack11lll1lll1l_opy_ = {
            bstack1ll1ll11lll_opy_.bstack11lll1l1ll1_opy_: bstack11llllll11l_opy_,
            bstack1ll1ll11lll_opy_.bstack1l111l11111_opy_: bstack11lll1l11ll_opy_,
        }
        if test_hook_state == bstack1ll1ll111l1_opy_.PRE:
            hook = {
                bstack1l1l_opy_ (u"ࠣ࡭ࡨࡽࠧᕿ"): key,
                TestFramework.bstack1l1111l1ll1_opy_: uuid4().__str__(),
                TestFramework.bstack11llll11111_opy_: TestFramework.bstack1l11111ll1l_opy_,
                TestFramework.bstack11llll1111l_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11llll1l1l1_opy_: [],
                TestFramework.bstack1l11111l11l_opy_: args[1] if len(args) > 1 else bstack1l1l_opy_ (u"ࠩࠪᖀ"),
                TestFramework.bstack11lllll1lll_opy_: bstack1ll1l1ll1ll_opy_.bstack11lll1ll1ll_opy_()
            }
            bstack11llllll11l_opy_[key].append(hook)
            bstack11lll1lll1l_opy_[bstack1ll1ll11lll_opy_.bstack1l1111lll1l_opy_] = key
        elif test_hook_state == bstack1ll1ll111l1_opy_.POST:
            bstack11llll1ll11_opy_ = bstack11llllll11l_opy_.get(key, [])
            hook = bstack11llll1ll11_opy_.pop() if bstack11llll1ll11_opy_ else None
            if hook:
                result = self.__1l1111lll11_opy_(*args)
                if result:
                    bstack11lll1lll11_opy_ = result.get(bstack1l1l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᖁ"), TestFramework.bstack1l11111ll1l_opy_)
                    if bstack11lll1lll11_opy_ != TestFramework.bstack1l11111ll1l_opy_:
                        hook[TestFramework.bstack11llll11111_opy_] = bstack11lll1lll11_opy_
                hook[TestFramework.bstack11lll1l11l1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack11lllll1lll_opy_]= bstack1ll1l1ll1ll_opy_.bstack11lll1ll1ll_opy_()
                self.bstack11lll1ll11l_opy_(hook)
                logs = hook.get(TestFramework.bstack1l1111lllll_opy_, [])
                if logs: self.bstack1l1ll11lll1_opy_(instance, logs)
                bstack11lll1l11ll_opy_[key].append(hook)
                bstack11lll1lll1l_opy_[bstack1ll1ll11lll_opy_.bstack1l11111ll11_opy_] = key
        TestFramework.bstack1l1111ll1ll_opy_(instance, bstack11lll1lll1l_opy_)
        self.logger.debug(bstack1l1l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢ࡬ࡴࡵ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡰ࡫ࡹࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࡃࡻࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪࡽࠡࡪࡲࡳࡰࡹ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥ࠿ࠥᖂ") + str(bstack11lll1l11ll_opy_) + bstack1l1l_opy_ (u"ࠧࠨᖃ"))
    def __11llll1l111_opy_(
        self,
        context: bstack11lll1l1l1l_opy_,
        test_framework_state: bstack1ll1llll111_opy_,
        test_hook_state: bstack1ll1ll111l1_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l1ll111l_opy_(args[0], [bstack1l1l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᖄ"), bstack1l1l_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣᖅ"), bstack1l1l_opy_ (u"ࠣࡲࡤࡶࡦࡳࡳࠣᖆ"), bstack1l1l_opy_ (u"ࠤ࡬ࡨࡸࠨᖇ"), bstack1l1l_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧᖈ"), bstack1l1l_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᖉ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack1l1l_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᖊ")) else fixturedef.get(bstack1l1l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᖋ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1l1l_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࠧᖌ")) else None
        node = request.node if hasattr(request, bstack1l1l_opy_ (u"ࠣࡰࡲࡨࡪࠨᖍ")) else None
        target = request.node.nodeid if hasattr(node, bstack1l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᖎ")) else None
        baseid = fixturedef.get(bstack1l1l_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᖏ"), None) or bstack1l1l_opy_ (u"ࠦࠧᖐ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1l1l_opy_ (u"ࠧࡥࡰࡺࡨࡸࡲࡨ࡯ࡴࡦ࡯ࠥᖑ")):
            target = bstack1ll1ll11lll_opy_.__1l1111l111l_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1l1l_opy_ (u"ࠨ࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠣᖒ")) else None
            if target and not TestFramework.bstack1lll1llll11_opy_(target):
                self.__1l111111lll_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1l1l_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡱࡳࡩ࡫࠽ࡼࡰࡲࡨࡪࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᖓ") + str(test_hook_state) + bstack1l1l_opy_ (u"ࠣࠤᖔ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1l1l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡨ࡬ࡼࡹࡻࡲࡦࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࠥ࡫ࡶࡦࡰࡷࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡨࡪ࡬࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡦࡨࡪࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᖕ") + str(target) + bstack1l1l_opy_ (u"ࠥࠦᖖ"))
            return None
        instance = TestFramework.bstack1lll1llll11_opy_(target)
        if not instance:
            self.logger.warning(bstack1l1l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡦࡦࡹࡥࡪࡦࡀࡿࡧࡧࡳࡦ࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᖗ") + str(target) + bstack1l1l_opy_ (u"ࠧࠨᖘ"))
            return None
        bstack1l11111l1ll_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, bstack1ll1ll11lll_opy_.bstack11llllll1ll_opy_, {})
        if os.getenv(bstack1l1l_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡌࡉ࡙ࡖࡘࡖࡊ࡙ࠢᖙ"), bstack1l1l_opy_ (u"ࠢ࠲ࠤᖚ")) == bstack1l1l_opy_ (u"ࠣ࠳ࠥᖛ"):
            bstack11llll1lll1_opy_ = bstack1l1l_opy_ (u"ࠤ࠽ࠦᖜ").join((scope, fixturename))
            bstack11llll111ll_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111l1l1l_opy_ = {
                bstack1l1l_opy_ (u"ࠥ࡯ࡪࡿࠢᖝ"): bstack11llll1lll1_opy_,
                bstack1l1l_opy_ (u"ࠦࡹࡧࡧࡴࠤᖞ"): bstack1ll1ll11lll_opy_.__11llll11l11_opy_(request.node),
                bstack1l1l_opy_ (u"ࠧ࡬ࡩࡹࡶࡸࡶࡪࠨᖟ"): fixturedef,
                bstack1l1l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᖠ"): scope,
                bstack1l1l_opy_ (u"ࠢࡵࡻࡳࡩࠧᖡ"): None,
            }
            try:
                if test_hook_state == bstack1ll1ll111l1_opy_.POST and callable(getattr(args[-1], bstack1l1l_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᖢ"), None)):
                    bstack1l1111l1l1l_opy_[bstack1l1l_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᖣ")] = TestFramework.bstack1l1l1ll1l11_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1ll1ll111l1_opy_.PRE:
                bstack1l1111l1l1l_opy_[bstack1l1l_opy_ (u"ࠥࡹࡺ࡯ࡤࠣᖤ")] = uuid4().__str__()
                bstack1l1111l1l1l_opy_[bstack1ll1ll11lll_opy_.bstack11llll1111l_opy_] = bstack11llll111ll_opy_
            elif test_hook_state == bstack1ll1ll111l1_opy_.POST:
                bstack1l1111l1l1l_opy_[bstack1ll1ll11lll_opy_.bstack11lll1l11l1_opy_] = bstack11llll111ll_opy_
            if bstack11llll1lll1_opy_ in bstack1l11111l1ll_opy_:
                bstack1l11111l1ll_opy_[bstack11llll1lll1_opy_].update(bstack1l1111l1l1l_opy_)
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࠧᖥ") + str(bstack1l11111l1ll_opy_[bstack11llll1lll1_opy_]) + bstack1l1l_opy_ (u"ࠧࠨᖦ"))
            else:
                bstack1l11111l1ll_opy_[bstack11llll1lll1_opy_] = bstack1l1111l1l1l_opy_
                self.logger.debug(bstack1l1l_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࢀࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࢁࠥࡺࡲࡢࡥ࡮ࡩࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࠤᖧ") + str(len(bstack1l11111l1ll_opy_)) + bstack1l1l_opy_ (u"ࠢࠣᖨ"))
        TestFramework.bstack1llll1lll11_opy_(instance, bstack1ll1ll11lll_opy_.bstack11llllll1ll_opy_, bstack1l11111l1ll_opy_)
        self.logger.debug(bstack1l1l_opy_ (u"ࠣࡵࡤࡺࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࡾࡰࡪࡴࠨࡵࡴࡤࡧࡰ࡫ࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠬࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᖩ") + str(instance.ref()) + bstack1l1l_opy_ (u"ࠤࠥᖪ"))
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
            bstack1ll1ll11lll_opy_.bstack11llllll1ll_opy_: {},
            bstack1ll1ll11lll_opy_.bstack1l111l11111_opy_: {},
            bstack1ll1ll11lll_opy_.bstack11lll1l1ll1_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll1lll11_opy_(ob, TestFramework.bstack11lllll1l1l_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll1lll11_opy_(ob, TestFramework.bstack1l1llllll1l_opy_, context.platform_index)
        TestFramework.bstack1llll111l11_opy_[ctx.id] = ob
        self.logger.debug(bstack1l1l_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡨࡺࡸ࠯࡫ࡧࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࡻࡵࡣࡵ࡫ࡪࡺࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥᖫ") + str(TestFramework.bstack1llll111l11_opy_.keys()) + bstack1l1l_opy_ (u"ࠦࠧᖬ"))
        return ob
    def bstack1l1ll11l1l1_opy_(self, instance: bstack1lll111l1ll_opy_, bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_]):
        bstack11lllll11l1_opy_ = (
            bstack1ll1ll11lll_opy_.bstack1l1111lll1l_opy_
            if bstack1llll1llll1_opy_[1] == bstack1ll1ll111l1_opy_.PRE
            else bstack1ll1ll11lll_opy_.bstack1l11111ll11_opy_
        )
        hook = bstack1ll1ll11lll_opy_.bstack1l1111111ll_opy_(instance, bstack11lllll11l1_opy_)
        entries = hook.get(TestFramework.bstack11llll1l1l1_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1111l11l1_opy_, []))
        return entries
    def bstack1l1l1ll1l1l_opy_(self, instance: bstack1lll111l1ll_opy_, bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_]):
        bstack11lllll11l1_opy_ = (
            bstack1ll1ll11lll_opy_.bstack1l1111lll1l_opy_
            if bstack1llll1llll1_opy_[1] == bstack1ll1ll111l1_opy_.PRE
            else bstack1ll1ll11lll_opy_.bstack1l11111ll11_opy_
        )
        bstack1ll1ll11lll_opy_.bstack1l111l111l1_opy_(instance, bstack11lllll11l1_opy_)
        TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1111l11l1_opy_, []).clear()
    def bstack11lll1ll11l_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1l1l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡷ࡮ࡳࡩ࡭ࡣࡵࠤࡹࡵࠠࡵࡪࡨࠤࡏࡧࡶࡢࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡦࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡱࡪࡺࡨࡰࡦ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡆ࡬ࡪࡩ࡫ࡴࠢࡷ࡬ࡪࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡯࡮ࡴ࡫ࡧࡩࠥࢄ࠯࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠯ࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡌ࡯ࡳࠢࡨࡥࡨ࡮ࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡪࡲࡳࡰࡥ࡬ࡦࡸࡨࡰࡤ࡬ࡩ࡭ࡧࡶ࠰ࠥࡸࡥࡱ࡮ࡤࡧࡪࡹࠠࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦࠥࡽࡩࡵࡪࠣࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢࠡ࡫ࡱࠤ࡮ࡺࡳࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡏࡦࠡࡣࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡲࡧࡴࡤࡪࡨࡷࠥࡧࠠ࡮ࡱࡧ࡭࡫࡯ࡥࡥࠢ࡫ࡳࡴࡱ࠭࡭ࡧࡹࡩࡱࠦࡦࡪ࡮ࡨ࠰ࠥ࡯ࡴࠡࡥࡵࡩࡦࡺࡥࡴࠢࡤࠤࡑࡵࡧࡆࡰࡷࡶࡾࠦ࡯ࡣ࡬ࡨࡧࡹࠦࡷࡪࡶ࡫ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡕ࡬ࡱ࡮ࡲࡡࡳ࡮ࡼ࠰ࠥ࡯ࡴࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦ࡬ࡰࡥࡤࡸࡪࡪࠠࡪࡰࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱ࠵ࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡨࡹࠡࡴࡨࡴࡱࡧࡣࡪࡰࡪࠤࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰ࠴ࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤ࡙࡮ࡥࠡࡥࡵࡩࡦࡺࡥࡥࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࡷࠥࡧࡲࡦࠢࡤࡨࡩ࡫ࡤࠡࡶࡲࠤࡹ࡮ࡥࠡࡪࡲࡳࡰ࠭ࡳࠡࠤ࡯ࡳ࡬ࡹࠢࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭࠽ࠤ࡙࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴ࡭ࡳࠡࡣࡱࡨࠥ࡮࡯ࡰ࡭ࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡩࡱࡲ࡯ࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠽ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡖࡡࡵࡪࠣࡳࡧࡰࡥࡤࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡕࡧࡴࡩࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᖭ")
        global _1l1l1l1l111_opy_
        platform_index = os.environ[bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᖮ")]
        bstack1l1l1llllll_opy_ = os.path.join(bstack1l1l11l1l1l_opy_, (bstack1l1l1l1l1l1_opy_ + str(platform_index)), bstack11lll11ll1l_opy_)
        if not os.path.exists(bstack1l1l1llllll_opy_) or not os.path.isdir(bstack1l1l1llllll_opy_):
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷࡷࠥࡺ࡯ࠡࡲࡵࡳࡨ࡫ࡳࡴࠢࡾࢁࠧᖯ").format(bstack1l1l1llllll_opy_))
            return
        logs = hook.get(bstack1l1l_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨᖰ"), [])
        with os.scandir(bstack1l1l1llllll_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1l1l1l111_opy_:
                    self.logger.info(bstack1l1l_opy_ (u"ࠤࡓࡥࡹ࡮ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤࢀࢃࠢᖱ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1l1l_opy_ (u"ࠥࠦᖲ")
                    log_entry = bstack1lll1l11l1l_opy_(
                        kind=bstack1l1l_opy_ (u"࡙ࠦࡋࡓࡕࡡࡄࡘ࡙ࡇࡃࡉࡏࡈࡒ࡙ࠨᖳ"),
                        message=bstack1l1l_opy_ (u"ࠧࠨᖴ"),
                        level=bstack1l1l_opy_ (u"ࠨࠢᖵ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll11111l_opy_=entry.stat().st_size,
                        bstack1l1l11l1ll1_opy_=bstack1l1l_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢᖶ"),
                        bstack1lll11_opy_=os.path.abspath(entry.path),
                        bstack1l11111lll1_opy_=hook.get(TestFramework.bstack1l1111l1ll1_opy_)
                    )
                    logs.append(log_entry)
                    _1l1l1l1l111_opy_.add(abs_path)
        platform_index = os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᖷ")]
        bstack1l111111l1l_opy_ = os.path.join(bstack1l1l11l1l1l_opy_, (bstack1l1l1l1l1l1_opy_ + str(platform_index)), bstack11lll11ll1l_opy_, bstack11lll1l111l_opy_)
        if not os.path.exists(bstack1l111111l1l_opy_) or not os.path.isdir(bstack1l111111l1l_opy_):
            self.logger.info(bstack1l1l_opy_ (u"ࠤࡑࡳࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡬࡯ࡶࡰࡧࠤࡦࡺ࠺ࠡࡽࢀࠦᖸ").format(bstack1l111111l1l_opy_))
        else:
            self.logger.info(bstack1l1l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᖹ").format(bstack1l111111l1l_opy_))
            with os.scandir(bstack1l111111l1l_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1l1l1l111_opy_:
                        self.logger.info(bstack1l1l_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤᖺ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1l1l_opy_ (u"ࠧࠨᖻ")
                        log_entry = bstack1lll1l11l1l_opy_(
                            kind=bstack1l1l_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᖼ"),
                            message=bstack1l1l_opy_ (u"ࠢࠣᖽ"),
                            level=bstack1l1l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧᖾ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll11111l_opy_=entry.stat().st_size,
                            bstack1l1l11l1ll1_opy_=bstack1l1l_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᖿ"),
                            bstack1lll11_opy_=os.path.abspath(entry.path),
                            bstack1l1l1l1lll1_opy_=hook.get(TestFramework.bstack1l1111l1ll1_opy_)
                        )
                        logs.append(log_entry)
                        _1l1l1l1l111_opy_.add(abs_path)
        hook[bstack1l1l_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᗀ")] = logs
    def bstack1l1ll11lll1_opy_(
        self,
        bstack1l1l1l11lll_opy_: bstack1lll111l1ll_opy_,
        entries: List[bstack1lll1l11l1l_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡘࡋࡓࡔࡋࡒࡒࡤࡏࡄࠣᗁ"))
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1llllll1l_opy_)
        req.execution_context.hash = str(bstack1l1l1l11lll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1l11lll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1l11lll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1ll11l11lll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1l11l11ll_opy_)
            log_entry.uuid = entry.bstack1l11111lll1_opy_
            log_entry.test_framework_state = bstack1l1l1l11lll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1l1l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᗂ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            log_entry.level = bstack1l1l_opy_ (u"ࠨࠢᗃ")
            if entry.kind == bstack1l1l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᗄ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11111l_opy_
                log_entry.file_path = entry.bstack1lll11_opy_
        def bstack1l1ll11llll_opy_():
            bstack1ll111l1_opy_ = datetime.now()
            try:
                self.bstack1ll1l11111l_opy_.LogCreatedEvent(req)
                bstack1l1l1l11lll_opy_.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧᗅ"), datetime.now() - bstack1ll111l1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1l1l_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࢁࡽࠣᗆ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1ll1l_opy_.enqueue(bstack1l1ll11llll_opy_)
    def __11lll1llll1_opy_(self, instance) -> None:
        bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡍࡱࡤࡨࡸࠦࡣࡶࡵࡷࡳࡲࠦࡴࡢࡩࡶࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡹ࡫ࡳࡵࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡶࡪࡧࡴࡦࡵࠣࡥࠥࡪࡩࡤࡶࠣࡧࡴࡴࡴࡢ࡫ࡱ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡲࡥࡷࡧ࡯ࠤࡨࡻࡳࡵࡱࡰࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࡥࠢࡩࡶࡴࡳࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡸࡷࡹࡵ࡭ࡕࡣࡪࡑࡦࡴࡡࡨࡧࡵࠤࡦࡴࡤࠡࡷࡳࡨࡦࡺࡥࡴࠢࡷ࡬ࡪࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠡࡵࡷࡥࡹ࡫ࠠࡶࡵ࡬ࡲ࡬ࠦࡳࡦࡶࡢࡷࡹࡧࡴࡦࡡࡨࡲࡹࡸࡩࡦࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣᗇ")
        bstack11lll1lll1l_opy_ = {bstack1l1l_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰࡣࡲ࡫ࡴࡢࡦࡤࡸࡦࠨᗈ"): bstack1ll1l1ll1ll_opy_.bstack11lll1ll1ll_opy_()}
        from browserstack_sdk.sdk_cli.test_framework import TestFramework
        TestFramework.bstack1l1111ll1ll_opy_(instance, bstack11lll1lll1l_opy_)
    @staticmethod
    def bstack1l1111111ll_opy_(instance: bstack1lll111l1ll_opy_, bstack11lllll11l1_opy_: str):
        bstack11lll1l1l11_opy_ = (
            bstack1ll1ll11lll_opy_.bstack1l111l11111_opy_
            if bstack11lllll11l1_opy_ == bstack1ll1ll11lll_opy_.bstack1l11111ll11_opy_
            else bstack1ll1ll11lll_opy_.bstack11lll1l1ll1_opy_
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
        hook = bstack1ll1ll11lll_opy_.bstack1l1111111ll_opy_(instance, bstack11lllll11l1_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11llll1l1l1_opy_, []).clear()
    @staticmethod
    def __1l1111llll1_opy_(instance: bstack1lll111l1ll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1l1l_opy_ (u"ࠧ࡭ࡥࡵࡡࡵࡩࡨࡵࡲࡥࡵࠥᗉ"), None)):
            return
        if os.getenv(bstack1l1l_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡒࡏࡈࡕࠥᗊ"), bstack1l1l_opy_ (u"ࠢ࠲ࠤᗋ")) != bstack1l1l_opy_ (u"ࠣ࠳ࠥᗌ"):
            bstack1ll1ll11lll_opy_.logger.warning(bstack1l1l_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡪࡰࡪࠤࡨࡧࡰ࡭ࡱࡪࠦᗍ"))
            return
        bstack1l111111111_opy_ = {
            bstack1l1l_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᗎ"): (bstack1ll1ll11lll_opy_.bstack1l1111lll1l_opy_, bstack1ll1ll11lll_opy_.bstack11lll1l1ll1_opy_),
            bstack1l1l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨᗏ"): (bstack1ll1ll11lll_opy_.bstack1l11111ll11_opy_, bstack1ll1ll11lll_opy_.bstack1l111l11111_opy_),
        }
        for when in (bstack1l1l_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦᗐ"), bstack1l1l_opy_ (u"ࠨࡣࡢ࡮࡯ࠦᗑ"), bstack1l1l_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᗒ")):
            bstack11llll11l1l_opy_ = args[1].get_records(when)
            if not bstack11llll11l1l_opy_:
                continue
            records = [
                bstack1lll1l11l1l_opy_(
                    kind=TestFramework.bstack1l1l1llll1l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1l1l_opy_ (u"ࠣ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨࠦᗓ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1l1l_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡦࠥᗔ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll11l1l_opy_
                if isinstance(getattr(r, bstack1l1l_opy_ (u"ࠥࡱࡪࡹࡳࡢࡩࡨࠦᗕ"), None), str) and r.message.strip()
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
    def __11llll111l1_opy_(test) -> Dict[str, Any]:
        bstack1l11ll1l1_opy_ = bstack1ll1ll11lll_opy_.__1l1111l111l_opy_(test.location) if hasattr(test, bstack1l1l_opy_ (u"ࠦࡱࡵࡣࡢࡶ࡬ࡳࡳࠨᗖ")) else getattr(test, bstack1l1l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᗗ"), None)
        test_name = test.name if hasattr(test, bstack1l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᗘ")) else None
        bstack11lll1ll1l1_opy_ = test.fspath.strpath if hasattr(test, bstack1l1l_opy_ (u"ࠢࡧࡵࡳࡥࡹ࡮ࠢᗙ")) and test.fspath else None
        if not bstack1l11ll1l1_opy_ or not test_name or not bstack11lll1ll1l1_opy_:
            return None
        code = None
        if hasattr(test, bstack1l1l_opy_ (u"ࠣࡱࡥ࡮ࠧᗚ")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack11lll1l1111_opy_ = []
        try:
            bstack11lll1l1111_opy_ = bstack1l1ll11111_opy_.bstack1111llll1l_opy_(test)
        except:
            bstack1ll1ll11lll_opy_.logger.warning(bstack1l1l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡸࡪࡹࡴࠡࡵࡦࡳࡵ࡫ࡳ࠭ࠢࡷࡩࡸࡺࠠࡴࡥࡲࡴࡪࡹࠠࡸ࡫࡯ࡰࠥࡨࡥࠡࡴࡨࡷࡴࡲࡶࡦࡦࠣ࡭ࡳࠦࡃࡍࡋࠥᗛ"))
        return {
            TestFramework.bstack1ll11l1ll1l_opy_: uuid4().__str__(),
            TestFramework.bstack1l1111ll11l_opy_: bstack1l11ll1l1_opy_,
            TestFramework.bstack1ll111l1l1l_opy_: test_name,
            TestFramework.bstack1l1l1111l11_opy_: getattr(test, bstack1l1l_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᗜ"), None),
            TestFramework.bstack11lllll1l11_opy_: bstack11lll1ll1l1_opy_,
            TestFramework.bstack1l1111l11ll_opy_: bstack1ll1ll11lll_opy_.__11llll11l11_opy_(test),
            TestFramework.bstack11lll1ll111_opy_: code,
            TestFramework.bstack1l11ll11lll_opy_: TestFramework.bstack11lll1l1lll_opy_,
            TestFramework.bstack1l111ll1111_opy_: bstack1l11ll1l1_opy_,
            TestFramework.bstack11lll11llll_opy_: bstack11lll1l1111_opy_
        }
    @staticmethod
    def __11llll11l11_opy_(test) -> List[str]:
        markers = []
        current = test
        while current:
            own_markers = getattr(current, bstack1l1l_opy_ (u"ࠦࡴࡽ࡮ࡠ࡯ࡤࡶࡰ࡫ࡲࡴࠤᗝ"), [])
            markers.extend([getattr(m, bstack1l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᗞ"), None) for m in own_markers if getattr(m, bstack1l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᗟ"), None)])
            current = getattr(current, bstack1l1l_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢᗠ"), None)
        return markers
    @staticmethod
    def __1l1111l111l_opy_(location):
        return bstack1l1l_opy_ (u"ࠣ࠼࠽ࠦᗡ").join(filter(lambda x: isinstance(x, str), location))