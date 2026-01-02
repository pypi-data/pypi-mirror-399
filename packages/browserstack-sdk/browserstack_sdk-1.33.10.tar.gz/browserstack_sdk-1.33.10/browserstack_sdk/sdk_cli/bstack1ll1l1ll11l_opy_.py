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
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1ll1l11ll1l_opy_,
    bstack1lll1ll1ll1_opy_,
    bstack1lll1ll1111_opy_,
    bstack1l1111ll1l1_opy_,
    bstack1ll1lllll11_opy_,
)
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from datetime import datetime, timezone
from typing import List, Dict, Any
import traceback
from bstack_utils.helper import bstack1l1l1ll1lll_opy_
from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll1l1l1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1lll1l1lll1_opy_ import bstack1ll1l1l111l_opy_
from bstack_utils.bstack111l1ll111_opy_ import bstack11l11ll11l_opy_
bstack1l1l11lllll_opy_ = bstack1l1l1ll1lll_opy_()
bstack11lll1l1ll1_opy_ = 1.0
bstack1l1l11l1111_opy_ = bstack11111l_opy_ (u"ࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣᕀ")
bstack11lll1l11ll_opy_ = bstack11111l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᕁ")
bstack11lll11llll_opy_ = bstack11111l_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᕂ")
bstack11lll11lll1_opy_ = bstack11111l_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᕃ")
bstack11lll1l1111_opy_ = bstack11111l_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᕄ")
_1l1ll111111_opy_ = set()
class bstack1ll1l1ll111_opy_(TestFramework):
    bstack1l111l111ll_opy_ = bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨᕅ")
    bstack1l111111lll_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࠧᕆ")
    bstack1l1111111ll_opy_ = bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᕇ")
    bstack11lll1l1l1l_opy_ = bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࠦᕈ")
    bstack11llll11ll1_opy_ = bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᕉ")
    bstack11llll1111l_opy_: bool
    bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_  = None
    bstack1lll1l1l1l1_opy_ = None
    bstack1l1111l1111_opy_ = [
        bstack1ll1l11ll1l_opy_.BEFORE_ALL,
        bstack1ll1l11ll1l_opy_.AFTER_ALL,
        bstack1ll1l11ll1l_opy_.BEFORE_EACH,
        bstack1ll1l11ll1l_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lllll11ll_opy_: Dict[str, str],
        bstack1l1llll11ll_opy_: List[str]=[bstack11111l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᕊ")],
        bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_=None,
        bstack1lll1l1l1l1_opy_=None
    ):
        super().__init__(bstack1l1llll11ll_opy_, bstack11lllll11ll_opy_, bstack1lllll1l11l_opy_)
        self.bstack11llll1111l_opy_ = any(bstack11111l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᕋ") in item.lower() for item in bstack1l1llll11ll_opy_)
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
        if test_framework_state == bstack1ll1l11ll1l_opy_.TEST or test_framework_state in bstack1ll1l1ll111_opy_.bstack1l1111l1111_opy_:
            bstack1l111111l1l_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1ll1l11ll1l_opy_.NONE:
            self.logger.warning(bstack11111l_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡪࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࠢᕌ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠢࠣᕍ"))
            return
        if not self.bstack11llll1111l_opy_:
            self.logger.warning(bstack11111l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠾ࠤᕎ") + str(str(self.bstack1l1llll11ll_opy_)) + bstack11111l_opy_ (u"ࠤࠥᕏ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11111l_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᕐ") + str(kwargs) + bstack11111l_opy_ (u"ࠦࠧᕑ"))
            return
        instance = self.__1l1111l11l1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11111l_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡧࡲࡨࡵࡀࠦᕒ") + str(args) + bstack11111l_opy_ (u"ࠨࠢᕓ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1ll1l1ll111_opy_.bstack1l1111l1111_opy_ and test_hook_state == bstack1lll1ll1111_opy_.PRE:
                bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack1l1l1111l_opy_.value)
                name = str(EVENTS.bstack1l1l1111l_opy_.name)+bstack11111l_opy_ (u"ࠢ࠻ࠤᕔ")+str(test_framework_state.name)
                TestFramework.bstack11lll1ll1l1_opy_(instance, name, bstack1l1lll1ll1l_opy_)
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࠥ࡫ࡲࡳࡱࡵࠤࡵࡸࡥ࠻ࠢࡾࢁࠧᕕ").format(e))
        try:
            if not TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack11llll1llll_opy_) and test_hook_state == bstack1lll1ll1111_opy_.PRE:
                test = bstack1ll1l1ll111_opy_.__11llll1l111_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack11111l_opy_ (u"ࠤ࡯ࡳࡦࡪࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕖ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠥࠦᕗ"))
            if test_framework_state == bstack1ll1l11ll1l_opy_.TEST:
                if test_hook_state == bstack1lll1ll1111_opy_.PRE and not TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1l111ll_opy_):
                    TestFramework.bstack1llll1l1lll_opy_(instance, TestFramework.bstack1l1l1l111ll_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11111l_opy_ (u"ࠦࡸ࡫ࡴࠡࡶࡨࡷࡹ࠳ࡳࡵࡣࡵࡸࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕘ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠧࠨᕙ"))
                elif test_hook_state == bstack1lll1ll1111_opy_.POST and not TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l11lll1l_opy_):
                    TestFramework.bstack1llll1l1lll_opy_(instance, TestFramework.bstack1l1l11lll1l_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11111l_opy_ (u"ࠨࡳࡦࡶࠣࡸࡪࡹࡴ࠮ࡧࡱࡨࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕚ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠢࠣᕛ"))
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG and test_hook_state == bstack1lll1ll1111_opy_.POST:
                bstack1ll1l1ll111_opy_.__11llll1lll1_opy_(instance, *args)
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG_REPORT and test_hook_state == bstack1lll1ll1111_opy_.POST:
                self.__11lll1l1lll_opy_(instance, *args)
                self.__1l11111lll1_opy_(instance)
            elif test_framework_state in bstack1ll1l1ll111_opy_.bstack1l1111l1111_opy_:
                self.__1l11111llll_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11111l_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᕜ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠤࠥᕝ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11lll1l1l11_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1ll1l1ll111_opy_.bstack1l1111l1111_opy_ and test_hook_state == bstack1lll1ll1111_opy_.POST:
                name = str(EVENTS.bstack1l1l1111l_opy_.name)+bstack11111l_opy_ (u"ࠥ࠾ࠧᕞ")+str(test_framework_state.name)
                bstack1l1lll1ll1l_opy_ = TestFramework.bstack1l1111ll111_opy_(instance, name)
                bstack1ll1l111ll1_opy_.end(EVENTS.bstack1l1l1111l_opy_.value, bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᕟ"), bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᕠ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᕡ").format(e))
    def bstack1l1l11l11l1_opy_(self):
        return self.bstack11llll1111l_opy_
    def __1l1111ll11l_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11111l_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᕢ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l111ll11_opy_(rep, [bstack11111l_opy_ (u"ࠣࡹ࡫ࡩࡳࠨᕣ"), bstack11111l_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᕤ"), bstack11111l_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥᕥ"), bstack11111l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᕦ"), bstack11111l_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠨᕧ"), bstack11111l_opy_ (u"ࠨ࡬ࡰࡰࡪࡶࡪࡶࡲࡵࡧࡻࡸࠧᕨ")])
        return None
    def __11lll1l1lll_opy_(self, instance: bstack1lll1ll1ll1_opy_, *args):
        result = self.__1l1111ll11l_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll1111_opy_ = None
        if result.get(bstack11111l_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᕩ"), None) == bstack11111l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣᕪ") and len(args) > 1 and getattr(args[1], bstack11111l_opy_ (u"ࠤࡨࡼࡨ࡯࡮ࡧࡱࠥᕫ"), None) is not None:
            failure = [{bstack11111l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᕬ"): [args[1].excinfo.exconly(), result.get(bstack11111l_opy_ (u"ࠦࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠥᕭ"), None)]}]
            bstack1llllll1111_opy_ = bstack11111l_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨᕮ") if bstack11111l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᕯ") in getattr(args[1].excinfo, bstack11111l_opy_ (u"ࠢࡵࡻࡳࡩࡳࡧ࡭ࡦࠤᕰ"), bstack11111l_opy_ (u"ࠣࠤᕱ")) else bstack11111l_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᕲ")
        bstack1l111l11l11_opy_ = result.get(bstack11111l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᕳ"), TestFramework.bstack1l111111111_opy_)
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
            target = None # bstack11lllllll1l_opy_ bstack1l111111l11_opy_ this to be bstack11111l_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᕴ")
            if test_framework_state == bstack1ll1l11ll1l_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__11lll1ll111_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11111l_opy_ (u"ࠧࡴ࡯ࡥࡧࠥᕵ"), None), bstack11111l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᕶ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11111l_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᕷ"), None):
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
        bstack11lllll1ll1_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack1ll1l1ll111_opy_.bstack1l111111lll_opy_, {})
        if not key in bstack11lllll1ll1_opy_:
            bstack11lllll1ll1_opy_[key] = []
        bstack1l1111llll1_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack1ll1l1ll111_opy_.bstack1l1111111ll_opy_, {})
        if not key in bstack1l1111llll1_opy_:
            bstack1l1111llll1_opy_[key] = []
        bstack1l11111111l_opy_ = {
            bstack1ll1l1ll111_opy_.bstack1l111111lll_opy_: bstack11lllll1ll1_opy_,
            bstack1ll1l1ll111_opy_.bstack1l1111111ll_opy_: bstack1l1111llll1_opy_,
        }
        if test_hook_state == bstack1lll1ll1111_opy_.PRE:
            hook = {
                bstack11111l_opy_ (u"ࠣ࡭ࡨࡽࠧᕸ"): key,
                TestFramework.bstack1l1111l111l_opy_: uuid4().__str__(),
                TestFramework.bstack1l1111l11ll_opy_: TestFramework.bstack1l11111l1ll_opy_,
                TestFramework.bstack1l111l1111l_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11lll1ll1ll_opy_: [],
                TestFramework.bstack1l11111l11l_opy_: args[1] if len(args) > 1 else bstack11111l_opy_ (u"ࠩࠪᕹ"),
                TestFramework.bstack1l11111ll1l_opy_: bstack1ll1l1l111l_opy_.bstack1l1111l1l1l_opy_()
            }
            bstack11lllll1ll1_opy_[key].append(hook)
            bstack1l11111111l_opy_[bstack1ll1l1ll111_opy_.bstack11lll1l1l1l_opy_] = key
        elif test_hook_state == bstack1lll1ll1111_opy_.POST:
            bstack1l11111ll11_opy_ = bstack11lllll1ll1_opy_.get(key, [])
            hook = bstack1l11111ll11_opy_.pop() if bstack1l11111ll11_opy_ else None
            if hook:
                result = self.__1l1111ll11l_opy_(*args)
                if result:
                    bstack1l111l11111_opy_ = result.get(bstack11111l_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᕺ"), TestFramework.bstack1l11111l1ll_opy_)
                    if bstack1l111l11111_opy_ != TestFramework.bstack1l11111l1ll_opy_:
                        hook[TestFramework.bstack1l1111l11ll_opy_] = bstack1l111l11111_opy_
                hook[TestFramework.bstack11llll1l1l1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l11111ll1l_opy_]= bstack1ll1l1l111l_opy_.bstack1l1111l1l1l_opy_()
                self.bstack1l1111lll1l_opy_(hook)
                logs = hook.get(TestFramework.bstack1l1111l1lll_opy_, [])
                if logs: self.bstack1l1ll11llll_opy_(instance, logs)
                bstack1l1111llll1_opy_[key].append(hook)
                bstack1l11111111l_opy_[bstack1ll1l1ll111_opy_.bstack11llll11ll1_opy_] = key
        TestFramework.bstack1l1111lll11_opy_(instance, bstack1l11111111l_opy_)
        self.logger.debug(bstack11111l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢ࡬ࡴࡵ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡰ࡫ࡹࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࡃࡻࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪࡽࠡࡪࡲࡳࡰࡹ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥ࠿ࠥᕻ") + str(bstack1l1111llll1_opy_) + bstack11111l_opy_ (u"ࠧࠨᕼ"))
    def __1l1111l1l11_opy_(
        self,
        context: bstack1l1111ll1l1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        test_hook_state: bstack1lll1ll1111_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l111ll11_opy_(args[0], [bstack11111l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᕽ"), bstack11111l_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣᕾ"), bstack11111l_opy_ (u"ࠣࡲࡤࡶࡦࡳࡳࠣᕿ"), bstack11111l_opy_ (u"ࠤ࡬ࡨࡸࠨᖀ"), bstack11111l_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧᖁ"), bstack11111l_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᖂ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack11111l_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᖃ")) else fixturedef.get(bstack11111l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᖄ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11111l_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࠧᖅ")) else None
        node = request.node if hasattr(request, bstack11111l_opy_ (u"ࠣࡰࡲࡨࡪࠨᖆ")) else None
        target = request.node.nodeid if hasattr(node, bstack11111l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᖇ")) else None
        baseid = fixturedef.get(bstack11111l_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᖈ"), None) or bstack11111l_opy_ (u"ࠦࠧᖉ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11111l_opy_ (u"ࠧࡥࡰࡺࡨࡸࡲࡨ࡯ࡴࡦ࡯ࠥᖊ")):
            target = bstack1ll1l1ll111_opy_.__11lll1lllll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11111l_opy_ (u"ࠨ࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠣᖋ")) else None
            if target and not TestFramework.bstack1lllll11l1l_opy_(target):
                self.__11lll1ll111_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11111l_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡱࡳࡩ࡫࠽ࡼࡰࡲࡨࡪࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᖌ") + str(test_hook_state) + bstack11111l_opy_ (u"ࠣࠤᖍ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11111l_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡨ࡬ࡼࡹࡻࡲࡦࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࠥ࡫ࡶࡦࡰࡷࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡨࡪ࡬࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡦࡨࡪࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᖎ") + str(target) + bstack11111l_opy_ (u"ࠥࠦᖏ"))
            return None
        instance = TestFramework.bstack1lllll11l1l_opy_(target)
        if not instance:
            self.logger.warning(bstack11111l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡦࡦࡹࡥࡪࡦࡀࡿࡧࡧࡳࡦ࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᖐ") + str(target) + bstack11111l_opy_ (u"ࠧࠨᖑ"))
            return None
        bstack11lllllllll_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, bstack1ll1l1ll111_opy_.bstack1l111l111ll_opy_, {})
        if os.getenv(bstack11111l_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡌࡉ࡙ࡖࡘࡖࡊ࡙ࠢᖒ"), bstack11111l_opy_ (u"ࠢ࠲ࠤᖓ")) == bstack11111l_opy_ (u"ࠣ࠳ࠥᖔ"):
            bstack11llll1ll1l_opy_ = bstack11111l_opy_ (u"ࠤ࠽ࠦᖕ").join((scope, fixturename))
            bstack11llllll1ll_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111ll1ll_opy_ = {
                bstack11111l_opy_ (u"ࠥ࡯ࡪࡿࠢᖖ"): bstack11llll1ll1l_opy_,
                bstack11111l_opy_ (u"ࠦࡹࡧࡧࡴࠤᖗ"): bstack1ll1l1ll111_opy_.__11lll1ll11l_opy_(request.node),
                bstack11111l_opy_ (u"ࠧ࡬ࡩࡹࡶࡸࡶࡪࠨᖘ"): fixturedef,
                bstack11111l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᖙ"): scope,
                bstack11111l_opy_ (u"ࠢࡵࡻࡳࡩࠧᖚ"): None,
            }
            try:
                if test_hook_state == bstack1lll1ll1111_opy_.POST and callable(getattr(args[-1], bstack11111l_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᖛ"), None)):
                    bstack1l1111ll1ll_opy_[bstack11111l_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᖜ")] = TestFramework.bstack1l1l1l1lll1_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1ll1111_opy_.PRE:
                bstack1l1111ll1ll_opy_[bstack11111l_opy_ (u"ࠥࡹࡺ࡯ࡤࠣᖝ")] = uuid4().__str__()
                bstack1l1111ll1ll_opy_[bstack1ll1l1ll111_opy_.bstack1l111l1111l_opy_] = bstack11llllll1ll_opy_
            elif test_hook_state == bstack1lll1ll1111_opy_.POST:
                bstack1l1111ll1ll_opy_[bstack1ll1l1ll111_opy_.bstack11llll1l1l1_opy_] = bstack11llllll1ll_opy_
            if bstack11llll1ll1l_opy_ in bstack11lllllllll_opy_:
                bstack11lllllllll_opy_[bstack11llll1ll1l_opy_].update(bstack1l1111ll1ll_opy_)
                self.logger.debug(bstack11111l_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࠧᖞ") + str(bstack11lllllllll_opy_[bstack11llll1ll1l_opy_]) + bstack11111l_opy_ (u"ࠧࠨᖟ"))
            else:
                bstack11lllllllll_opy_[bstack11llll1ll1l_opy_] = bstack1l1111ll1ll_opy_
                self.logger.debug(bstack11111l_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࢀࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࢁࠥࡺࡲࡢࡥ࡮ࡩࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࠤᖠ") + str(len(bstack11lllllllll_opy_)) + bstack11111l_opy_ (u"ࠢࠣᖡ"))
        TestFramework.bstack1llll1l1lll_opy_(instance, bstack1ll1l1ll111_opy_.bstack1l111l111ll_opy_, bstack11lllllllll_opy_)
        self.logger.debug(bstack11111l_opy_ (u"ࠣࡵࡤࡺࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࡾࡰࡪࡴࠨࡵࡴࡤࡧࡰ࡫ࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠬࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᖢ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠤࠥᖣ"))
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
            bstack1ll1l1ll111_opy_.bstack1l111l111ll_opy_: {},
            bstack1ll1l1ll111_opy_.bstack1l1111111ll_opy_: {},
            bstack1ll1l1ll111_opy_.bstack1l111111lll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll1l1lll_opy_(ob, TestFramework.bstack11llll11lll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll1l1lll_opy_(ob, TestFramework.bstack1ll111ll111_opy_, context.platform_index)
        TestFramework.bstack1lll1llllll_opy_[ctx.id] = ob
        self.logger.debug(bstack11111l_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡨࡺࡸ࠯࡫ࡧࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࡻࡵࡣࡵ࡫ࡪࡺࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥᖤ") + str(TestFramework.bstack1lll1llllll_opy_.keys()) + bstack11111l_opy_ (u"ࠦࠧᖥ"))
        return ob
    def bstack1l1l111ll1l_opy_(self, instance: bstack1lll1ll1ll1_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_]):
        bstack11lllll1lll_opy_ = (
            bstack1ll1l1ll111_opy_.bstack11lll1l1l1l_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1ll1111_opy_.PRE
            else bstack1ll1l1ll111_opy_.bstack11llll11ll1_opy_
        )
        hook = bstack1ll1l1ll111_opy_.bstack1l111l11l1l_opy_(instance, bstack11lllll1lll_opy_)
        entries = hook.get(TestFramework.bstack11lll1ll1ll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack11llll1l1ll_opy_, []))
        return entries
    def bstack1l1l1llllll_opy_(self, instance: bstack1lll1ll1ll1_opy_, bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_]):
        bstack11lllll1lll_opy_ = (
            bstack1ll1l1ll111_opy_.bstack11lll1l1l1l_opy_
            if bstack1llll1lll1l_opy_[1] == bstack1lll1ll1111_opy_.PRE
            else bstack1ll1l1ll111_opy_.bstack11llll11ll1_opy_
        )
        bstack1ll1l1ll111_opy_.bstack1l1111lllll_opy_(instance, bstack11lllll1lll_opy_)
        TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack11llll1l1ll_opy_, []).clear()
    def bstack1l1111lll1l_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11111l_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡷ࡮ࡳࡩ࡭ࡣࡵࠤࡹࡵࠠࡵࡪࡨࠤࡏࡧࡶࡢࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡦࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡱࡪࡺࡨࡰࡦ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡆ࡬ࡪࡩ࡫ࡴࠢࡷ࡬ࡪࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡯࡮ࡴ࡫ࡧࡩࠥࢄ࠯࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠯ࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡌ࡯ࡳࠢࡨࡥࡨ࡮ࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡪࡲࡳࡰࡥ࡬ࡦࡸࡨࡰࡤ࡬ࡩ࡭ࡧࡶ࠰ࠥࡸࡥࡱ࡮ࡤࡧࡪࡹࠠࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦࠥࡽࡩࡵࡪࠣࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢࠡ࡫ࡱࠤ࡮ࡺࡳࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡏࡦࠡࡣࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡲࡧࡴࡤࡪࡨࡷࠥࡧࠠ࡮ࡱࡧ࡭࡫࡯ࡥࡥࠢ࡫ࡳࡴࡱ࠭࡭ࡧࡹࡩࡱࠦࡦࡪ࡮ࡨ࠰ࠥ࡯ࡴࠡࡥࡵࡩࡦࡺࡥࡴࠢࡤࠤࡑࡵࡧࡆࡰࡷࡶࡾࠦ࡯ࡣ࡬ࡨࡧࡹࠦࡷࡪࡶ࡫ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡕ࡬ࡱ࡮ࡲࡡࡳ࡮ࡼ࠰ࠥ࡯ࡴࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦ࡬ࡰࡥࡤࡸࡪࡪࠠࡪࡰࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱ࠵ࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡨࡹࠡࡴࡨࡴࡱࡧࡣࡪࡰࡪࠤࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰ࠴ࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤ࡙࡮ࡥࠡࡥࡵࡩࡦࡺࡥࡥࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࡷࠥࡧࡲࡦࠢࡤࡨࡩ࡫ࡤࠡࡶࡲࠤࡹ࡮ࡥࠡࡪࡲࡳࡰ࠭ࡳࠡࠤ࡯ࡳ࡬ࡹࠢࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭࠽ࠤ࡙࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴ࡭ࡳࠡࡣࡱࡨࠥ࡮࡯ࡰ࡭ࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡩࡱࡲ࡯ࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠽ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡖࡡࡵࡪࠣࡳࡧࡰࡥࡤࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡕࡧࡴࡩࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᖦ")
        global _1l1ll111111_opy_
        platform_index = os.environ[bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᖧ")]
        bstack1l1l1lllll1_opy_ = os.path.join(bstack1l1l11lllll_opy_, (bstack1l1l11l1111_opy_ + str(platform_index)), bstack11lll11lll1_opy_)
        if not os.path.exists(bstack1l1l1lllll1_opy_) or not os.path.isdir(bstack1l1l1lllll1_opy_):
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷࡷࠥࡺ࡯ࠡࡲࡵࡳࡨ࡫ࡳࡴࠢࡾࢁࠧᖨ").format(bstack1l1l1lllll1_opy_))
            return
        logs = hook.get(bstack11111l_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨᖩ"), [])
        with os.scandir(bstack1l1l1lllll1_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll111111_opy_:
                    self.logger.info(bstack11111l_opy_ (u"ࠤࡓࡥࡹ࡮ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤࢀࢃࠢᖪ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11111l_opy_ (u"ࠥࠦᖫ")
                    log_entry = bstack1ll1lllll11_opy_(
                        kind=bstack11111l_opy_ (u"࡙ࠦࡋࡓࡕࡡࡄࡘ࡙ࡇࡃࡉࡏࡈࡒ࡙ࠨᖬ"),
                        message=bstack11111l_opy_ (u"ࠧࠨᖭ"),
                        level=bstack11111l_opy_ (u"ࠨࠢᖮ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll1111ll_opy_=entry.stat().st_size,
                        bstack1l1l1l1l111_opy_=bstack11111l_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢᖯ"),
                        bstack1l1ll11_opy_=os.path.abspath(entry.path),
                        bstack11lllll1111_opy_=hook.get(TestFramework.bstack1l1111l111l_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll111111_opy_.add(abs_path)
        platform_index = os.environ[bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᖰ")]
        bstack11lllll1l1l_opy_ = os.path.join(bstack1l1l11lllll_opy_, (bstack1l1l11l1111_opy_ + str(platform_index)), bstack11lll11lll1_opy_, bstack11lll1l1111_opy_)
        if not os.path.exists(bstack11lllll1l1l_opy_) or not os.path.isdir(bstack11lllll1l1l_opy_):
            self.logger.info(bstack11111l_opy_ (u"ࠤࡑࡳࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡬࡯ࡶࡰࡧࠤࡦࡺ࠺ࠡࡽࢀࠦᖱ").format(bstack11lllll1l1l_opy_))
        else:
            self.logger.info(bstack11111l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᖲ").format(bstack11lllll1l1l_opy_))
            with os.scandir(bstack11lllll1l1l_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll111111_opy_:
                        self.logger.info(bstack11111l_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤᖳ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11111l_opy_ (u"ࠧࠨᖴ")
                        log_entry = bstack1ll1lllll11_opy_(
                            kind=bstack11111l_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᖵ"),
                            message=bstack11111l_opy_ (u"ࠢࠣᖶ"),
                            level=bstack11111l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧᖷ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll1111ll_opy_=entry.stat().st_size,
                            bstack1l1l1l1l111_opy_=bstack11111l_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᖸ"),
                            bstack1l1ll11_opy_=os.path.abspath(entry.path),
                            bstack1l1l1ll1ll1_opy_=hook.get(TestFramework.bstack1l1111l111l_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll111111_opy_.add(abs_path)
        hook[bstack11111l_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᖹ")] = logs
    def bstack1l1ll11llll_opy_(
        self,
        bstack1l1l1l1llll_opy_: bstack1lll1ll1ll1_opy_,
        entries: List[bstack1ll1lllll11_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11111l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡘࡋࡓࡔࡋࡒࡒࡤࡏࡄࠣᖺ"))
        req.platform_index = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1ll111ll111_opy_)
        req.execution_context.hash = str(bstack1l1l1l1llll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1l1llll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1l1llll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1lllllll1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1l111llll_opy_)
            log_entry.uuid = entry.bstack11lllll1111_opy_
            log_entry.test_framework_state = bstack1l1l1l1llll_opy_.state.name
            log_entry.message = entry.message.encode(bstack11111l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᖻ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            log_entry.level = bstack11111l_opy_ (u"ࠨࠢᖼ")
            if entry.kind == bstack11111l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᖽ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll1111ll_opy_
                log_entry.file_path = entry.bstack1l1ll11_opy_
        def bstack1l1l1lll11l_opy_():
            bstack1l1lll1ll_opy_ = datetime.now()
            try:
                self.bstack1lll1l1l1l1_opy_.LogCreatedEvent(req)
                bstack1l1l1l1llll_opy_.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧᖾ"), datetime.now() - bstack1l1lll1ll_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11111l_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࢁࡽࠣᖿ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1lll11l_opy_)
    def __1l11111lll1_opy_(self, instance) -> None:
        bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡍࡱࡤࡨࡸࠦࡣࡶࡵࡷࡳࡲࠦࡴࡢࡩࡶࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡹ࡫ࡳࡵࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡶࡪࡧࡴࡦࡵࠣࡥࠥࡪࡩࡤࡶࠣࡧࡴࡴࡴࡢ࡫ࡱ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡲࡥࡷࡧ࡯ࠤࡨࡻࡳࡵࡱࡰࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࡥࠢࡩࡶࡴࡳࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡸࡷࡹࡵ࡭ࡕࡣࡪࡑࡦࡴࡡࡨࡧࡵࠤࡦࡴࡤࠡࡷࡳࡨࡦࡺࡥࡴࠢࡷ࡬ࡪࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠡࡵࡷࡥࡹ࡫ࠠࡶࡵ࡬ࡲ࡬ࠦࡳࡦࡶࡢࡷࡹࡧࡴࡦࡡࡨࡲࡹࡸࡩࡦࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣᗀ")
        bstack1l11111111l_opy_ = {bstack11111l_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰࡣࡲ࡫ࡴࡢࡦࡤࡸࡦࠨᗁ"): bstack1ll1l1l111l_opy_.bstack1l1111l1l1l_opy_()}
        from browserstack_sdk.sdk_cli.test_framework import TestFramework
        TestFramework.bstack1l1111lll11_opy_(instance, bstack1l11111111l_opy_)
    @staticmethod
    def bstack1l111l11l1l_opy_(instance: bstack1lll1ll1ll1_opy_, bstack11lllll1lll_opy_: str):
        bstack11llllll11l_opy_ = (
            bstack1ll1l1ll111_opy_.bstack1l1111111ll_opy_
            if bstack11lllll1lll_opy_ == bstack1ll1l1ll111_opy_.bstack11llll11ll1_opy_
            else bstack1ll1l1ll111_opy_.bstack1l111111lll_opy_
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
        hook = bstack1ll1l1ll111_opy_.bstack1l111l11l1l_opy_(instance, bstack11lllll1lll_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11lll1ll1ll_opy_, []).clear()
    @staticmethod
    def __11llll1lll1_opy_(instance: bstack1lll1ll1ll1_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11111l_opy_ (u"ࠧ࡭ࡥࡵࡡࡵࡩࡨࡵࡲࡥࡵࠥᗂ"), None)):
            return
        if os.getenv(bstack11111l_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡒࡏࡈࡕࠥᗃ"), bstack11111l_opy_ (u"ࠢ࠲ࠤᗄ")) != bstack11111l_opy_ (u"ࠣ࠳ࠥᗅ"):
            bstack1ll1l1ll111_opy_.logger.warning(bstack11111l_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡪࡰࡪࠤࡨࡧࡰ࡭ࡱࡪࠦᗆ"))
            return
        bstack11llll11l1l_opy_ = {
            bstack11111l_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᗇ"): (bstack1ll1l1ll111_opy_.bstack11lll1l1l1l_opy_, bstack1ll1l1ll111_opy_.bstack1l111111lll_opy_),
            bstack11111l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨᗈ"): (bstack1ll1l1ll111_opy_.bstack11llll11ll1_opy_, bstack1ll1l1ll111_opy_.bstack1l1111111ll_opy_),
        }
        for when in (bstack11111l_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦᗉ"), bstack11111l_opy_ (u"ࠨࡣࡢ࡮࡯ࠦᗊ"), bstack11111l_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᗋ")):
            bstack11llll1ll11_opy_ = args[1].get_records(when)
            if not bstack11llll1ll11_opy_:
                continue
            records = [
                bstack1ll1lllll11_opy_(
                    kind=TestFramework.bstack1l1l111lll1_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11111l_opy_ (u"ࠣ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨࠦᗌ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11111l_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡦࠥᗍ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll1ll11_opy_
                if isinstance(getattr(r, bstack11111l_opy_ (u"ࠥࡱࡪࡹࡳࡢࡩࡨࠦᗎ"), None), str) and r.message.strip()
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
    def __11llll1l111_opy_(test) -> Dict[str, Any]:
        bstack111lll11_opy_ = bstack1ll1l1ll111_opy_.__11lll1lllll_opy_(test.location) if hasattr(test, bstack11111l_opy_ (u"ࠦࡱࡵࡣࡢࡶ࡬ࡳࡳࠨᗏ")) else getattr(test, bstack11111l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᗐ"), None)
        test_name = test.name if hasattr(test, bstack11111l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᗑ")) else None
        bstack11lll1lll1l_opy_ = test.fspath.strpath if hasattr(test, bstack11111l_opy_ (u"ࠢࡧࡵࡳࡥࡹ࡮ࠢᗒ")) and test.fspath else None
        if not bstack111lll11_opy_ or not test_name or not bstack11lll1lll1l_opy_:
            return None
        code = None
        if hasattr(test, bstack11111l_opy_ (u"ࠣࡱࡥ࡮ࠧᗓ")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack11lll1l11l1_opy_ = []
        try:
            bstack11lll1l11l1_opy_ = bstack11l11ll11l_opy_.bstack1111lll1ll_opy_(test)
        except:
            bstack1ll1l1ll111_opy_.logger.warning(bstack11111l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡸࡪࡹࡴࠡࡵࡦࡳࡵ࡫ࡳ࠭ࠢࡷࡩࡸࡺࠠࡴࡥࡲࡴࡪࡹࠠࡸ࡫࡯ࡰࠥࡨࡥࠡࡴࡨࡷࡴࡲࡶࡦࡦࠣ࡭ࡳࠦࡃࡍࡋࠥᗔ"))
        return {
            TestFramework.bstack1ll11111l11_opy_: uuid4().__str__(),
            TestFramework.bstack11llll1llll_opy_: bstack111lll11_opy_,
            TestFramework.bstack1ll111111l1_opy_: test_name,
            TestFramework.bstack1l1l1111l11_opy_: getattr(test, bstack11111l_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᗕ"), None),
            TestFramework.bstack11llll1l11l_opy_: bstack11lll1lll1l_opy_,
            TestFramework.bstack11llll111l1_opy_: bstack1ll1l1ll111_opy_.__11lll1ll11l_opy_(test),
            TestFramework.bstack11lllll11l1_opy_: code,
            TestFramework.bstack1l11l1ll1l1_opy_: TestFramework.bstack1l111111111_opy_,
            TestFramework.bstack1l111lll11l_opy_: bstack111lll11_opy_,
            TestFramework.bstack11lll1l111l_opy_: bstack11lll1l11l1_opy_
        }
    @staticmethod
    def __11lll1ll11l_opy_(test) -> List[str]:
        markers = []
        current = test
        while current:
            own_markers = getattr(current, bstack11111l_opy_ (u"ࠦࡴࡽ࡮ࡠ࡯ࡤࡶࡰ࡫ࡲࡴࠤᗖ"), [])
            markers.extend([getattr(m, bstack11111l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᗗ"), None) for m in own_markers if getattr(m, bstack11111l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᗘ"), None)])
            current = getattr(current, bstack11111l_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢᗙ"), None)
        return markers
    @staticmethod
    def __11lll1lllll_opy_(location):
        return bstack11111l_opy_ (u"ࠣ࠼࠽ࠦᗚ").join(filter(lambda x: isinstance(x, str), location))