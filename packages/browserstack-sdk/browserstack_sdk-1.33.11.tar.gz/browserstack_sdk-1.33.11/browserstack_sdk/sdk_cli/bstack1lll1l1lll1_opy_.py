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
from datetime import datetime, timezone
import os
import builtins
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1lllll11l1l_opy_, bstack1llll11ll11_opy_, bstack1llll1ll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllll11_opy_ import bstack1ll11lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1lll111l1ll_opy_, bstack1ll1ll111l1_opy_, bstack1lll1l11l1l_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1l1l111l1l1_opy_, bstack1l1l11lll11_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1l1l1l1ll11_opy_ = [bstack1l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ኿"), bstack1l1l_opy_ (u"ࠧࡶࡡࡳࡧࡱࡸࠧዀ"), bstack1l1l_opy_ (u"ࠨࡣࡰࡰࡩ࡭࡬ࠨ዁"), bstack1l1l_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࠣዂ"), bstack1l1l_opy_ (u"ࠣࡲࡤࡸ࡭ࠨዃ")]
bstack1l1l11l1l1l_opy_ = bstack1l1l11lll11_opy_()
bstack1l1l1l1l1l1_opy_ = bstack1l1l_opy_ (u"ࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮ࠤዄ")
bstack1l1l11ll1ll_opy_ = {
    bstack1l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡴࡾࡺࡨࡰࡰ࠱ࡍࡹ࡫࡭ࠣዅ"): bstack1l1l1l1ll11_opy_,
    bstack1l1l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡵࡿࡴࡩࡱࡱ࠲ࡕࡧࡣ࡬ࡣࡪࡩࠧ዆"): bstack1l1l1l1ll11_opy_,
    bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡶࡹࡵࡪࡲࡲ࠳ࡓ࡯ࡥࡷ࡯ࡩࠧ዇"): bstack1l1l1l1ll11_opy_,
    bstack1l1l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡃ࡭ࡣࡶࡷࠧወ"): bstack1l1l1l1ll11_opy_,
    bstack1l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡇࡷࡱࡧࡹ࡯࡯࡯ࠤዉ"): bstack1l1l1l1ll11_opy_
    + [
        bstack1l1l_opy_ (u"ࠣࡱࡵ࡭࡬࡯࡮ࡢ࡮ࡱࡥࡲ࡫ࠢዊ"),
        bstack1l1l_opy_ (u"ࠤ࡮ࡩࡾࡽ࡯ࡳࡦࡶࠦዋ"),
        bstack1l1l_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨ࡭ࡳ࡬࡯ࠣዌ"),
        bstack1l1l_opy_ (u"ࠦࡰ࡫ࡹࡸࡱࡵࡨࡸࠨው"),
        bstack1l1l_opy_ (u"ࠧࡩࡡ࡭࡮ࡶࡴࡪࡩࠢዎ"),
        bstack1l1l_opy_ (u"ࠨࡣࡢ࡮࡯ࡳࡧࡰࠢዏ"),
        bstack1l1l_opy_ (u"ࠢࡴࡶࡤࡶࡹࠨዐ"),
        bstack1l1l_opy_ (u"ࠣࡵࡷࡳࡵࠨዑ"),
        bstack1l1l_opy_ (u"ࠤࡧࡹࡷࡧࡴࡪࡱࡱࠦዒ"),
        bstack1l1l_opy_ (u"ࠥࡻ࡭࡫࡮ࠣዓ"),
    ],
    bstack1l1l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡲࡧࡩ࡯࠰ࡖࡩࡸࡹࡩࡰࡰࠥዔ"): [bstack1l1l_opy_ (u"ࠧࡹࡴࡢࡴࡷࡴࡦࡺࡨࠣዕ"), bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡷ࡫ࡧࡩ࡭ࡧࡧࠦዖ"), bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡸࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤࠣ዗"), bstack1l1l_opy_ (u"ࠣ࡫ࡷࡩࡲࡹࠢዘ")],
    bstack1l1l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡦࡳࡳ࡬ࡩࡨ࠰ࡆࡳࡳ࡬ࡩࡨࠤዙ"): [bstack1l1l_opy_ (u"ࠥ࡭ࡳࡼ࡯ࡤࡣࡷ࡭ࡴࡴ࡟ࡱࡣࡵࡥࡲࡹࠢዚ"), bstack1l1l_opy_ (u"ࠦࡦࡸࡧࡴࠤዛ")],
    bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡇ࡫ࡻࡸࡺࡸࡥࡅࡧࡩࠦዜ"): [bstack1l1l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧዝ"), bstack1l1l_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣዞ"), bstack1l1l_opy_ (u"ࠣࡨࡸࡲࡨࠨዟ"), bstack1l1l_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤዠ"), bstack1l1l_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧዡ"), bstack1l1l_opy_ (u"ࠦ࡮ࡪࡳࠣዢ")],
    bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡔࡷࡥࡖࡪࡷࡵࡦࡵࡷࠦዣ"): [bstack1l1l_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦዤ"), bstack1l1l_opy_ (u"ࠢࡱࡣࡵࡥࡲࠨዥ"), bstack1l1l_opy_ (u"ࠣࡲࡤࡶࡦࡳ࡟ࡪࡰࡧࡩࡽࠨዦ")],
    bstack1l1l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡵࡹࡳࡴࡥࡳ࠰ࡆࡥࡱࡲࡉ࡯ࡨࡲࠦዧ"): [bstack1l1l_opy_ (u"ࠥࡻ࡭࡫࡮ࠣየ"), bstack1l1l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࠦዩ")],
    bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡳࡡࡳ࡭࠱ࡷࡹࡸࡵࡤࡶࡸࡶࡪࡹ࠮ࡏࡱࡧࡩࡐ࡫ࡹࡸࡱࡵࡨࡸࠨዪ"): [bstack1l1l_opy_ (u"ࠨ࡮ࡰࡦࡨࠦያ"), bstack1l1l_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢዬ")],
    bstack1l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯࡯ࡤࡶࡰ࠴ࡳࡵࡴࡸࡧࡹࡻࡲࡦࡵ࠱ࡑࡦࡸ࡫ࠣይ"): [bstack1l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢዮ"), bstack1l1l_opy_ (u"ࠥࡥࡷ࡭ࡳࠣዯ"), bstack1l1l_opy_ (u"ࠦࡰࡽࡡࡳࡩࡶࠦደ")],
}
_1l1l1l1l111_opy_ = set()
class bstack1ll1l111l1l_opy_(bstack1lll11ll111_opy_):
    bstack1l1l11l1lll_opy_ = bstack1l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡪ࡬ࡥࡳࡴࡨࡨࠧዱ")
    bstack1l1l1ll1lll_opy_ = bstack1l1l_opy_ (u"ࠨࡉࡏࡈࡒࠦዲ")
    bstack1l1l1ll11ll_opy_ = bstack1l1l_opy_ (u"ࠢࡆࡔࡕࡓࡗࠨዳ")
    bstack1l1l11ll111_opy_: Callable
    bstack1l1l11llll1_opy_: Callable
    def __init__(self, bstack1lll11ll1ll_opy_, bstack1lll1l1111l_opy_):
        super().__init__()
        self.bstack1ll11l1lll1_opy_ = bstack1lll1l1111l_opy_
        if os.getenv(bstack1l1l_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡉࡐࡆࡍ࡟ࡐ࠳࠴࡝ࠧዴ"), bstack1l1l_opy_ (u"ࠤ࠴ࠦድ")) != bstack1l1l_opy_ (u"ࠥ࠵ࠧዶ") or not self.is_enabled():
            self.logger.warning(bstack1l1l_opy_ (u"ࠦࠧዷ") + str(self.__class__.__name__) + bstack1l1l_opy_ (u"ࠧࠦࡤࡪࡵࡤࡦࡱ࡫ࡤࠣዸ"))
            return
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.PRE), self.bstack1ll11111l11_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), self.bstack1ll111l1111_opy_)
        for event in bstack1ll1llll111_opy_:
            for state in bstack1ll1ll111l1_opy_:
                TestFramework.bstack1l1lllllll1_opy_((event, state), self.bstack1l1l1lll111_opy_)
        bstack1lll11ll1ll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.POST), self.bstack1l1l1lll11l_opy_)
        self.bstack1l1l11ll111_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1ll11l1ll_opy_(bstack1ll1l111l1l_opy_.bstack1l1l1ll1lll_opy_, self.bstack1l1l11ll111_opy_)
        self.bstack1l1l11llll1_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1ll11l1ll_opy_(bstack1ll1l111l1l_opy_.bstack1l1l1ll11ll_opy_, self.bstack1l1l11llll1_opy_)
        self.bstack1l1l111llll_opy_ = builtins.print
        builtins.print = self.bstack1l1l11l1l11_opy_()
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l1lll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1l1l1ll1111_opy_() and instance:
            bstack1l1l11ll11l_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack1llll1llll1_opy_
            if test_framework_state == bstack1ll1llll111_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1ll1llll111_opy_.LOG:
                bstack1ll111l1_opy_ = datetime.now()
                entries = f.bstack1l1ll11l1l1_opy_(instance, bstack1llll1llll1_opy_)
                if entries:
                    self.bstack1l1ll11lll1_opy_(instance, entries)
                    instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࠨዹ"), datetime.now() - bstack1ll111l1_opy_)
                    f.bstack1l1l1ll1l1l_opy_(instance, bstack1llll1llll1_opy_)
                instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠢࡰ࠳࠴ࡽ࠿ࡵ࡮ࡠࡣ࡯ࡰࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵࡵࠥዺ"), datetime.now() - bstack1l1l11ll11l_opy_)
                return # bstack1l1l1l111ll_opy_ not send this event with the bstack1l1l1l11l11_opy_ bstack1l1ll11ll11_opy_
            elif (
                test_framework_state == bstack1ll1llll111_opy_.TEST
                and test_hook_state == bstack1ll1ll111l1_opy_.POST
                and not f.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1ll111l1l_opy_)
            ):
                self.logger.warning(bstack1l1l_opy_ (u"ࠣࡦࡵࡳࡵࡶࡩ࡯ࡩࠣࡨࡺ࡫ࠠࡵࡱࠣࡰࡦࡩ࡫ࠡࡱࡩࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࠨዻ") + str(TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1ll111l1l_opy_)) + bstack1l1l_opy_ (u"ࠤࠥዼ"))
                f.bstack1llll1lll11_opy_(instance, bstack1ll1l111l1l_opy_.bstack1l1l11l1lll_opy_, True)
                return # bstack1l1l1l111ll_opy_ not send this event bstack1l1l111l1ll_opy_ bstack1l1l11ll1l1_opy_
            elif (
                f.bstack1llll1l11ll_opy_(instance, bstack1ll1l111l1l_opy_.bstack1l1l11l1lll_opy_, False)
                and test_framework_state == bstack1ll1llll111_opy_.LOG_REPORT
                and test_hook_state == bstack1ll1ll111l1_opy_.POST
                and f.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1ll111l1l_opy_)
            ):
                self.logger.warning(bstack1l1l_opy_ (u"ࠥ࡭ࡳࡰࡥࡤࡶ࡬ࡲ࡬ࠦࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲࡙ࡋࡓࡕ࠮ࠣࡘࡪࡹࡴࡉࡱࡲ࡯ࡘࡺࡡࡵࡧ࠱ࡔࡔ࡙ࡔࠡࠤዽ") + str(TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1l1ll111l1l_opy_)) + bstack1l1l_opy_ (u"ࠦࠧዾ"))
                self.bstack1l1l1lll111_opy_(f, instance, (bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), *args, **kwargs)
            bstack1ll111l1_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1l1ll11l111_opy_ = sorted(
                filter(lambda x: x.get(bstack1l1l_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣዿ"), None), data.pop(bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨጀ"), {}).values()),
                key=lambda x: x[bstack1l1l_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥጁ")],
            )
            if bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_ in data:
                data.pop(bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_)
            data.update({bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣጂ"): bstack1l1ll11l111_opy_})
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤ࡭ࡷࡴࡴ࠺ࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢጃ"), datetime.now() - bstack1ll111l1_opy_)
            bstack1ll111l1_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1l1l111l1_opy_)
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠥ࡮ࡸࡵ࡮࠻ࡱࡱࡣࡦࡲ࡬ࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸࡸࠨጄ"), datetime.now() - bstack1ll111l1_opy_)
            self.bstack1l1ll11ll11_opy_(instance, bstack1llll1llll1_opy_, event_json=event_json)
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠦࡴ࠷࠱ࡺ࠼ࡲࡲࡤࡧ࡬࡭ࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡹࠢጅ"), datetime.now() - bstack1l1l11ll11l_opy_)
    def bstack1ll11111l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
        bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1l1l11ll_opy_.value)
        self.bstack1ll11l1lll1_opy_.bstack1l1ll111ll1_opy_(instance, f, bstack1llll1llll1_opy_, *args, **kwargs)
        req = self.bstack1ll11l1lll1_opy_.bstack1l1l111l11l_opy_(instance, f, bstack1llll1llll1_opy_, *args, **kwargs)
        self.bstack1l1l1l11l1l_opy_(f, instance, req)
        bstack1ll1l1ll111_opy_.end(EVENTS.bstack1l1l11ll_opy_.value, bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧጆ"), bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦጇ"), status=True, failure=None, test_name=None)
    def bstack1ll111l1111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        if not f.bstack1llll1l11ll_opy_(instance, self.bstack1ll11l1lll1_opy_.bstack1l1l111ll1l_opy_, False):
            req = self.bstack1ll11l1lll1_opy_.bstack1l1l111l11l_opy_(instance, f, bstack1llll1llll1_opy_, *args, **kwargs)
            self.bstack1l1l1l11l1l_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l1ll11l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l1l1l11l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡔ࡭࡬ࡴࡵ࡯࡮ࡨࠢࡗࡩࡸࡺࡓࡦࡵࡶ࡭ࡴࡴࡅࡷࡧࡱࡸࠥ࡭ࡒࡑࡅࠣࡧࡦࡲ࡬࠻ࠢࡑࡳࠥࡼࡡ࡭࡫ࡧࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡪࡡࡵࡣࠥገ"))
            return
        bstack1ll111l1_opy_ = datetime.now()
        try:
            r = self.bstack1ll1l11111l_opy_.TestSessionEvent(req)
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡩࡻ࡫࡮ࡵࠤጉ"), datetime.now() - bstack1ll111l1_opy_)
            f.bstack1llll1lll11_opy_(instance, self.bstack1ll11l1lll1_opy_.bstack1l1l111ll1l_opy_, r.success)
            if not r.success:
                self.logger.info(bstack1l1l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦጊ") + str(r) + bstack1l1l_opy_ (u"ࠥࠦጋ"))
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤጌ") + str(e) + bstack1l1l_opy_ (u"ࠧࠨግ"))
            traceback.print_exc()
            raise e
    def bstack1l1l1lll11l_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        _driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        _1l1l1l1l1ll_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1ll1lll1lll_opy_.bstack1l1lll1l1l1_opy_(method_name):
            return
        if f.bstack1ll111ll111_opy_(*args) == bstack1ll1lll1lll_opy_.bstack1l1ll111111_opy_:
            bstack1l1l11ll11l_opy_ = datetime.now()
            screenshot = result.get(bstack1l1l_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧጎ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack1l1l_opy_ (u"ࠢࡪࡰࡹࡥࡱ࡯ࡤࠡࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠥ࡯࡭ࡢࡩࡨࠤࡧࡧࡳࡦ࠸࠷ࠤࡸࡺࡲࠣጏ"))
                return
            bstack1l1l1l11lll_opy_ = self.bstack1l1l111ll11_opy_(instance)
            if bstack1l1l1l11lll_opy_:
                entry = bstack1lll1l11l1l_opy_(TestFramework.bstack1l1l1l1llll_opy_, screenshot)
                self.bstack1l1ll11lll1_opy_(bstack1l1l1l11lll_opy_, [entry])
                instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠣࡱ࠴࠵ࡾࡀ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡧࡻࡩࡨࡻࡴࡦࠤጐ"), datetime.now() - bstack1l1l11ll11l_opy_)
            else:
                self.logger.warning(bstack1l1l_opy_ (u"ࠤࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡶࡨࡷࡹࠦࡦࡰࡴࠣࡻ࡭࡯ࡣࡩࠢࡷ࡬࡮ࡹࠠࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠤࡼࡧࡳࠡࡶࡤ࡯ࡪࡴࠠࡣࡻࠣࡨࡷ࡯ࡶࡦࡴࡀࠤࢀࢃࠢ጑").format(instance.ref()))
        event = {}
        bstack1l1l1l11lll_opy_ = self.bstack1l1l111ll11_opy_(instance)
        if bstack1l1l1l11lll_opy_:
            self.bstack1l1l1l1l11l_opy_(event, bstack1l1l1l11lll_opy_)
            if event.get(bstack1l1l_opy_ (u"ࠥࡰࡴ࡭ࡳࠣጒ")):
                self.bstack1l1ll11lll1_opy_(bstack1l1l1l11lll_opy_, event[bstack1l1l_opy_ (u"ࠦࡱࡵࡧࡴࠤጓ")])
            else:
                self.logger.debug(bstack1l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡱࡵࡧࡴࠢࡩࡳࡷࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡩࡻ࡫࡮ࡵࠤጔ"))
    @measure(event_name=EVENTS.bstack1l1l1l1111l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l1ll11lll1_opy_(
        self,
        bstack1l1l1l11lll_opy_: bstack1lll111l1ll_opy_,
        entries: List[bstack1lll1l11l1l_opy_],
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1llllll1l_opy_)
        req.execution_context.hash = str(bstack1l1l1l11lll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1l11lll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1l11lll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1ll11l11lll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1l1l11l11ll_opy_)
            log_entry.uuid = TestFramework.bstack1llll1l11ll_opy_(bstack1l1l1l11lll_opy_, TestFramework.bstack1ll11l1ll1l_opy_)
            log_entry.test_framework_state = bstack1l1l1l11lll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧጕ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1l1l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤ጖"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11111l_opy_
                log_entry.file_path = entry.bstack1lll11_opy_
        def bstack1l1ll11llll_opy_():
            bstack1ll111l1_opy_ = datetime.now()
            try:
                self.bstack1ll1l11111l_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l1l1l1llll_opy_:
                    bstack1l1l1l11lll_opy_.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧ጗"), datetime.now() - bstack1ll111l1_opy_)
                elif entry.kind == TestFramework.bstack1l1ll1111ll_opy_:
                    bstack1l1l1l11lll_opy_.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨጘ"), datetime.now() - bstack1ll111l1_opy_)
                else:
                    bstack1l1l1l11lll_opy_.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡰࡴ࡭ࠢጙ"), datetime.now() - bstack1ll111l1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1l1l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤጚ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllll1ll1l_opy_.enqueue(bstack1l1ll11llll_opy_)
    @measure(event_name=EVENTS.bstack1l1l1ll11l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l1ll11ll11_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        event_json=None,
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1llllll1l_opy_)
        req.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l11lll_opy_)
        req.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1l11l11ll_opy_)
        req.test_framework_state = bstack1llll1llll1_opy_[0].name
        req.test_hook_state = bstack1llll1llll1_opy_[1].name
        started_at = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1l1l11ll1_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1ll111l11_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1l1l111l1_opy_)).encode(bstack1l1l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦጛ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1l1ll11llll_opy_():
            bstack1ll111l1_opy_ = datetime.now()
            try:
                self.bstack1ll1l11111l_opy_.TestFrameworkEvent(req)
                instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡩࡻ࡫࡮ࡵࠤጜ"), datetime.now() - bstack1ll111l1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1l1l_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧጝ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllll1ll1l_opy_.enqueue(bstack1l1ll11llll_opy_)
    def bstack1l1l111ll11_opy_(self, instance: bstack1lllll11l1l_opy_):
        bstack1l1l1lllll1_opy_ = TestFramework.bstack1llll11llll_opy_(instance.context)
        for t in bstack1l1l1lllll1_opy_:
            bstack1l1l11lll1l_opy_ = TestFramework.bstack1llll1l11ll_opy_(t, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
            if any(instance is d[1] for d in bstack1l1l11lll1l_opy_):
                return t
    def bstack1l1l11l11l1_opy_(self, message):
        self.bstack1l1l11ll111_opy_(message + bstack1l1l_opy_ (u"ࠣ࡞ࡱࠦጞ"))
    def log_error(self, message):
        self.bstack1l1l11llll1_opy_(message + bstack1l1l_opy_ (u"ࠤ࡟ࡲࠧጟ"))
    def bstack1l1ll11l1ll_opy_(self, level, original_func):
        def bstack1l1ll11ll1l_opy_(*args):
            try:
                try:
                    return_value = original_func(*args)
                except Exception:
                    return None
                try:
                    if not args or not isinstance(args[0], str) or not args[0].strip():
                        return return_value
                    message = args[0].strip()
                    if bstack1l1l_opy_ (u"ࠥࡉࡻ࡫࡮ࡵࡆ࡬ࡷࡵࡧࡴࡤࡪࡨࡶࡒࡵࡤࡶ࡮ࡨࠦጠ") in message or bstack1l1l_opy_ (u"ࠦࡠ࡙ࡄࡌࡅࡏࡍࡢࠨጡ") in message or bstack1l1l_opy_ (u"ࠧࡡࡗࡦࡤࡇࡶ࡮ࡼࡥࡳࡏࡲࡨࡺࡲࡥ࡞ࠤጢ") in message:
                        return return_value
                    bstack1l1l1lllll1_opy_ = TestFramework.bstack1l1l11l111l_opy_()
                    if not bstack1l1l1lllll1_opy_:
                        return return_value
                    bstack1l1l1l11lll_opy_ = next(
                        (
                            instance
                            for instance in bstack1l1l1lllll1_opy_
                            if TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
                        ),
                        None,
                    )
                    if not bstack1l1l1l11lll_opy_:
                        return return_value
                    entry = bstack1lll1l11l1l_opy_(TestFramework.bstack1l1l1llll1l_opy_, message, level)
                    self.bstack1l1ll11lll1_opy_(bstack1l1l1l11lll_opy_, [entry])
                except Exception:
                    pass
                return return_value
            except Exception:
                return None
        return bstack1l1ll11ll1l_opy_
    def bstack1l1l11l1l11_opy_(self):
        def bstack1l1l111lll1_opy_(*args, **kwargs):
            try:
                self.bstack1l1l111llll_opy_(*args, **kwargs)
                if not args:
                    return
                message = bstack1l1l_opy_ (u"࠭ࠠࠨጣ").join(str(arg) for arg in args)
                if not message.strip():
                    return
                if bstack1l1l_opy_ (u"ࠢࡆࡸࡨࡲࡹࡊࡩࡴࡲࡤࡸࡨ࡮ࡥࡳࡏࡲࡨࡺࡲࡥࠣጤ") in message:
                    return
                bstack1l1l1lllll1_opy_ = TestFramework.bstack1l1l11l111l_opy_()
                if not bstack1l1l1lllll1_opy_:
                    return
                bstack1l1l1l11lll_opy_ = next(
                    (
                        instance
                        for instance in bstack1l1l1lllll1_opy_
                        if TestFramework.bstack1llll1l1l11_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
                    ),
                    None,
                )
                if not bstack1l1l1l11lll_opy_:
                    return
                entry = bstack1lll1l11l1l_opy_(TestFramework.bstack1l1l1llll1l_opy_, message, bstack1ll1l111l1l_opy_.bstack1l1l1ll1lll_opy_)
                self.bstack1l1ll11lll1_opy_(bstack1l1l1l11lll_opy_, [entry])
            except Exception as e:
                try:
                    self.bstack1l1l111llll_opy_(bstack1lll1l111ll_opy_ (u"ࠣ࡝ࡈࡺࡪࡴࡴࡅ࡫ࡶࡴࡦࡺࡣࡩࡧࡵࡑࡴࡪࡵ࡭ࡧࡠࠤࡑࡵࡧࠡࡥࡤࡴࡹࡻࡲࡦࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࡩࢂࠨጥ"))
                except:
                    pass
        return bstack1l1l111lll1_opy_
    def bstack1l1l1l1l11l_opy_(self, event: dict, instance=None) -> None:
        global _1l1l1l1l111_opy_
        levels = [bstack1l1l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧጦ"), bstack1l1l_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢጧ")]
        bstack1l1l1l11111_opy_ = bstack1l1l_opy_ (u"ࠦࠧጨ")
        if instance is not None:
            try:
                bstack1l1l1l11111_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
            except Exception as e:
                self.logger.warning(bstack1l1l_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡻࡵࡪࡦࠣࡪࡷࡵ࡭ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠥጩ").format(e))
        bstack1l1l1l1ll1l_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ጪ")]
                bstack1l1l1llllll_opy_ = os.path.join(bstack1l1l11l1l1l_opy_, (bstack1l1l1l1l1l1_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1l1l1llllll_opy_):
                    self.logger.debug(bstack1l1l_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡲࡴࡺࠠࡱࡴࡨࡷࡪࡴࡴࠡࡨࡲࡶࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡗࡩࡸࡺࠠࡢࡰࡧࠤࡇࡻࡩ࡭ࡦࠣࡰࡪࡼࡥ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥጫ").format(bstack1l1l1llllll_opy_))
                    continue
                file_names = os.listdir(bstack1l1l1llllll_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1l1l1llllll_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1l1l1l1l111_opy_:
                        self.logger.info(bstack1l1l_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨጬ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1l1l11l1111_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1l1l11l1111_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack1l1l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧጭ"):
                                entry = bstack1lll1l11l1l_opy_(
                                    kind=bstack1l1l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧጮ"),
                                    message=bstack1l1l_opy_ (u"ࠦࠧጯ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll11111l_opy_=file_size,
                                    bstack1l1l11l1ll1_opy_=bstack1l1l_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧጰ"),
                                    bstack1lll11_opy_=os.path.abspath(file_path),
                                    bstack1l111l1l11_opy_=bstack1l1l1l11111_opy_
                                )
                            elif level == bstack1l1l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥጱ"):
                                entry = bstack1lll1l11l1l_opy_(
                                    kind=bstack1l1l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤጲ"),
                                    message=bstack1l1l_opy_ (u"ࠣࠤጳ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll11111l_opy_=file_size,
                                    bstack1l1l11l1ll1_opy_=bstack1l1l_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤጴ"),
                                    bstack1lll11_opy_=os.path.abspath(file_path),
                                    bstack1l1l1l1lll1_opy_=bstack1l1l1l11111_opy_
                                )
                            bstack1l1l1l1ll1l_opy_.append(entry)
                            _1l1l1l1l111_opy_.add(abs_path)
                        except Exception as bstack1l1l1llll11_opy_:
                            self.logger.error(bstack1l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡲࡢ࡫ࡶࡩࡩࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡻࡾࠤጵ").format(bstack1l1l1llll11_opy_))
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡳࡣ࡬ࡷࡪࡪࠠࡸࡪࡨࡲࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥጶ").format(e))
        event[bstack1l1l_opy_ (u"ࠧࡲ࡯ࡨࡵࠥጷ")] = bstack1l1l1l1ll1l_opy_
class bstack1l1l1l111l1_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1ll1111l1_opy_ = set()
        kwargs[bstack1l1l_opy_ (u"ࠨࡳ࡬࡫ࡳ࡯ࡪࡿࡳࠣጸ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1l1l1lll1l1_opy_(obj, self.bstack1l1ll1111l1_opy_)
def bstack1l1ll111lll_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1l1l1lll1l1_opy_(obj, bstack1l1ll1111l1_opy_=None, max_depth=3):
    if bstack1l1ll1111l1_opy_ is None:
        bstack1l1ll1111l1_opy_ = set()
    if id(obj) in bstack1l1ll1111l1_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1ll1111l1_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1l1l1lll1ll_opy_ = TestFramework.bstack1l1l1ll1l11_opy_(obj)
    bstack1l1l1ll1ll1_opy_ = next((k.lower() in bstack1l1l1lll1ll_opy_.lower() for k in bstack1l1l11ll1ll_opy_.keys()), None)
    if bstack1l1l1ll1ll1_opy_:
        obj = TestFramework.bstack1l1l1ll111l_opy_(obj, bstack1l1l11ll1ll_opy_[bstack1l1l1ll1ll1_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack1l1l_opy_ (u"ࠢࡠࡡࡶࡰࡴࡺࡳࡠࡡࠥጹ")):
            keys = getattr(obj, bstack1l1l_opy_ (u"ࠣࡡࡢࡷࡱࡵࡴࡴࡡࡢࠦጺ"), [])
        elif hasattr(obj, bstack1l1l_opy_ (u"ࠤࡢࡣࡩ࡯ࡣࡵࡡࡢࠦጻ")):
            keys = getattr(obj, bstack1l1l_opy_ (u"ࠥࡣࡤࡪࡩࡤࡶࡢࡣࠧጼ"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack1l1l_opy_ (u"ࠦࡤࠨጽ"))}
        if not obj and bstack1l1l1lll1ll_opy_ == bstack1l1l_opy_ (u"ࠧࡶࡡࡵࡪ࡯࡭ࡧ࠴ࡐࡰࡵ࡬ࡼࡕࡧࡴࡩࠤጾ"):
            obj = {bstack1l1l_opy_ (u"ࠨࡰࡢࡶ࡫ࠦጿ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1l1ll111lll_opy_(key) or str(key).startswith(bstack1l1l_opy_ (u"ࠢࡠࠤፀ")):
            continue
        if value is not None and bstack1l1ll111lll_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1l1l1lll1l1_opy_(value, bstack1l1ll1111l1_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1l1l1lll1l1_opy_(o, bstack1l1ll1111l1_opy_, max_depth) for o in value]))
    return result or None