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
from datetime import datetime, timezone
import os
import builtins
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import bstack1llll111l1l_opy_, bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lll111l_opy_ import bstack1ll1l11l111_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1l11ll1l_opy_, bstack1lll1ll1ll1_opy_, bstack1lll1ll1111_opy_, bstack1ll1lllll11_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1l1ll11lll1_opy_, bstack1l1l1ll1lll_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1l1l11ll1ll_opy_ = [bstack11111l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤኸ"), bstack11111l_opy_ (u"ࠧࡶࡡࡳࡧࡱࡸࠧኹ"), bstack11111l_opy_ (u"ࠨࡣࡰࡰࡩ࡭࡬ࠨኺ"), bstack11111l_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࠣኻ"), bstack11111l_opy_ (u"ࠣࡲࡤࡸ࡭ࠨኼ")]
bstack1l1l11lllll_opy_ = bstack1l1l1ll1lll_opy_()
bstack1l1l11l1111_opy_ = bstack11111l_opy_ (u"ࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮ࠤኽ")
bstack1l1l1lll1l1_opy_ = {
    bstack11111l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡴࡾࡺࡨࡰࡰ࠱ࡍࡹ࡫࡭ࠣኾ"): bstack1l1l11ll1ll_opy_,
    bstack11111l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡵࡿࡴࡩࡱࡱ࠲ࡕࡧࡣ࡬ࡣࡪࡩࠧ኿"): bstack1l1l11ll1ll_opy_,
    bstack11111l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡶࡹࡵࡪࡲࡲ࠳ࡓ࡯ࡥࡷ࡯ࡩࠧዀ"): bstack1l1l11ll1ll_opy_,
    bstack11111l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡃ࡭ࡣࡶࡷࠧ዁"): bstack1l1l11ll1ll_opy_,
    bstack11111l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡇࡷࡱࡧࡹ࡯࡯࡯ࠤዂ"): bstack1l1l11ll1ll_opy_
    + [
        bstack11111l_opy_ (u"ࠣࡱࡵ࡭࡬࡯࡮ࡢ࡮ࡱࡥࡲ࡫ࠢዃ"),
        bstack11111l_opy_ (u"ࠤ࡮ࡩࡾࡽ࡯ࡳࡦࡶࠦዄ"),
        bstack11111l_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨ࡭ࡳ࡬࡯ࠣዅ"),
        bstack11111l_opy_ (u"ࠦࡰ࡫ࡹࡸࡱࡵࡨࡸࠨ዆"),
        bstack11111l_opy_ (u"ࠧࡩࡡ࡭࡮ࡶࡴࡪࡩࠢ዇"),
        bstack11111l_opy_ (u"ࠨࡣࡢ࡮࡯ࡳࡧࡰࠢወ"),
        bstack11111l_opy_ (u"ࠢࡴࡶࡤࡶࡹࠨዉ"),
        bstack11111l_opy_ (u"ࠣࡵࡷࡳࡵࠨዊ"),
        bstack11111l_opy_ (u"ࠤࡧࡹࡷࡧࡴࡪࡱࡱࠦዋ"),
        bstack11111l_opy_ (u"ࠥࡻ࡭࡫࡮ࠣዌ"),
    ],
    bstack11111l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡲࡧࡩ࡯࠰ࡖࡩࡸࡹࡩࡰࡰࠥው"): [bstack11111l_opy_ (u"ࠧࡹࡴࡢࡴࡷࡴࡦࡺࡨࠣዎ"), bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡷ࡫ࡧࡩ࡭ࡧࡧࠦዏ"), bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡸࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤࠣዐ"), bstack11111l_opy_ (u"ࠣ࡫ࡷࡩࡲࡹࠢዑ")],
    bstack11111l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡦࡳࡳ࡬ࡩࡨ࠰ࡆࡳࡳ࡬ࡩࡨࠤዒ"): [bstack11111l_opy_ (u"ࠥ࡭ࡳࡼ࡯ࡤࡣࡷ࡭ࡴࡴ࡟ࡱࡣࡵࡥࡲࡹࠢዓ"), bstack11111l_opy_ (u"ࠦࡦࡸࡧࡴࠤዔ")],
    bstack11111l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡇ࡫ࡻࡸࡺࡸࡥࡅࡧࡩࠦዕ"): [bstack11111l_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧዖ"), bstack11111l_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣ዗"), bstack11111l_opy_ (u"ࠣࡨࡸࡲࡨࠨዘ"), bstack11111l_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤዙ"), bstack11111l_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧዚ"), bstack11111l_opy_ (u"ࠦ࡮ࡪࡳࠣዛ")],
    bstack11111l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡔࡷࡥࡖࡪࡷࡵࡦࡵࡷࠦዜ"): [bstack11111l_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦዝ"), bstack11111l_opy_ (u"ࠢࡱࡣࡵࡥࡲࠨዞ"), bstack11111l_opy_ (u"ࠣࡲࡤࡶࡦࡳ࡟ࡪࡰࡧࡩࡽࠨዟ")],
    bstack11111l_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡵࡹࡳࡴࡥࡳ࠰ࡆࡥࡱࡲࡉ࡯ࡨࡲࠦዠ"): [bstack11111l_opy_ (u"ࠥࡻ࡭࡫࡮ࠣዡ"), bstack11111l_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࠦዢ")],
    bstack11111l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡳࡡࡳ࡭࠱ࡷࡹࡸࡵࡤࡶࡸࡶࡪࡹ࠮ࡏࡱࡧࡩࡐ࡫ࡹࡸࡱࡵࡨࡸࠨዣ"): [bstack11111l_opy_ (u"ࠨ࡮ࡰࡦࡨࠦዤ"), bstack11111l_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢዥ")],
    bstack11111l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯࡯ࡤࡶࡰ࠴ࡳࡵࡴࡸࡧࡹࡻࡲࡦࡵ࠱ࡑࡦࡸ࡫ࠣዦ"): [bstack11111l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢዧ"), bstack11111l_opy_ (u"ࠥࡥࡷ࡭ࡳࠣየ"), bstack11111l_opy_ (u"ࠦࡰࡽࡡࡳࡩࡶࠦዩ")],
}
_1l1ll111111_opy_ = set()
class bstack1ll1l1111ll_opy_(bstack1ll1l11lll1_opy_):
    bstack1l1l11llll1_opy_ = bstack11111l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡪ࡬ࡥࡳࡴࡨࡨࠧዪ")
    bstack1l1ll1l1111_opy_ = bstack11111l_opy_ (u"ࠨࡉࡏࡈࡒࠦያ")
    bstack1l1l11lll11_opy_ = bstack11111l_opy_ (u"ࠢࡆࡔࡕࡓࡗࠨዬ")
    bstack1l1l1l1l1l1_opy_: Callable
    bstack1l1l1ll11l1_opy_: Callable
    def __init__(self, bstack1ll1ll1lll1_opy_, bstack1ll1l1l1l1l_opy_):
        super().__init__()
        self.bstack1l1lllll11l_opy_ = bstack1ll1l1l1l1l_opy_
        if os.getenv(bstack11111l_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡉࡐࡆࡍ࡟ࡐ࠳࠴࡝ࠧይ"), bstack11111l_opy_ (u"ࠤ࠴ࠦዮ")) != bstack11111l_opy_ (u"ࠥ࠵ࠧዯ") or not self.is_enabled():
            self.logger.warning(bstack11111l_opy_ (u"ࠦࠧደ") + str(self.__class__.__name__) + bstack11111l_opy_ (u"ࠧࠦࡤࡪࡵࡤࡦࡱ࡫ࡤࠣዱ"))
            return
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.PRE), self.bstack1l1lll1llll_opy_)
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST), self.bstack1ll11l11l1l_opy_)
        for event in bstack1ll1l11ll1l_opy_:
            for state in bstack1lll1ll1111_opy_:
                TestFramework.bstack1l1llllll1l_opy_((event, state), self.bstack1l1l11l1l1l_opy_)
        bstack1ll1ll1lll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.POST), self.bstack1l1ll111ll1_opy_)
        self.bstack1l1l1l1l1l1_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1l1l1l1ll_opy_(bstack1ll1l1111ll_opy_.bstack1l1ll1l1111_opy_, self.bstack1l1l1l1l1l1_opy_)
        self.bstack1l1l1ll11l1_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1l1l1l1ll_opy_(bstack1ll1l1111ll_opy_.bstack1l1l11lll11_opy_, self.bstack1l1l1ll11l1_opy_)
        self.bstack1l1l1l111l1_opy_ = builtins.print
        builtins.print = self.bstack1l1l11l1lll_opy_()
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l11l1l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1l1l11l11l1_opy_() and instance:
            bstack1l1l1l1l11l_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack1llll1lll1l_opy_
            if test_framework_state == bstack1ll1l11ll1l_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1ll1l11ll1l_opy_.LOG:
                bstack1l1lll1ll_opy_ = datetime.now()
                entries = f.bstack1l1l111ll1l_opy_(instance, bstack1llll1lll1l_opy_)
                if entries:
                    self.bstack1l1ll11llll_opy_(instance, entries)
                    instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࠨዲ"), datetime.now() - bstack1l1lll1ll_opy_)
                    f.bstack1l1l1llllll_opy_(instance, bstack1llll1lll1l_opy_)
                instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠢࡰ࠳࠴ࡽ࠿ࡵ࡮ࡠࡣ࡯ࡰࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵࡵࠥዳ"), datetime.now() - bstack1l1l1l1l11l_opy_)
                return # bstack1l1l11ll1l1_opy_ not send this event with the bstack1l1l1llll1l_opy_ bstack1l1l1l1111l_opy_
            elif (
                test_framework_state == bstack1ll1l11ll1l_opy_.TEST
                and test_hook_state == bstack1lll1ll1111_opy_.POST
                and not f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1l11l1l_opy_)
            ):
                self.logger.warning(bstack11111l_opy_ (u"ࠣࡦࡵࡳࡵࡶࡩ࡯ࡩࠣࡨࡺ࡫ࠠࡵࡱࠣࡰࡦࡩ࡫ࠡࡱࡩࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࠨዴ") + str(TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1l11l1l_opy_)) + bstack11111l_opy_ (u"ࠤࠥድ"))
                f.bstack1llll1l1lll_opy_(instance, bstack1ll1l1111ll_opy_.bstack1l1l11llll1_opy_, True)
                return # bstack1l1l11ll1l1_opy_ not send this event bstack1l1l1ll111l_opy_ bstack1l1ll11l1l1_opy_
            elif (
                f.bstack1llll111ll1_opy_(instance, bstack1ll1l1111ll_opy_.bstack1l1l11llll1_opy_, False)
                and test_framework_state == bstack1ll1l11ll1l_opy_.LOG_REPORT
                and test_hook_state == bstack1lll1ll1111_opy_.POST
                and f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1l11l1l_opy_)
            ):
                self.logger.warning(bstack11111l_opy_ (u"ࠥ࡭ࡳࡰࡥࡤࡶ࡬ࡲ࡬ࠦࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲࡙ࡋࡓࡕ࠮ࠣࡘࡪࡹࡴࡉࡱࡲ࡯ࡘࡺࡡࡵࡧ࠱ࡔࡔ࡙ࡔࠡࠤዶ") + str(TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1l11l1l_opy_)) + bstack11111l_opy_ (u"ࠦࠧዷ"))
                self.bstack1l1l11l1l1l_opy_(f, instance, (bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST), *args, **kwargs)
            bstack1l1lll1ll_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1l1l1ll1l1l_opy_ = sorted(
                filter(lambda x: x.get(bstack11111l_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣዸ"), None), data.pop(bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨዹ"), {}).values()),
                key=lambda x: x[bstack11111l_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥዺ")],
            )
            if bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_ in data:
                data.pop(bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_)
            data.update({bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣዻ"): bstack1l1l1ll1l1l_opy_})
            instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠤ࡭ࡷࡴࡴ࠺ࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢዼ"), datetime.now() - bstack1l1lll1ll_opy_)
            bstack1l1lll1ll_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1l11ll11l_opy_)
            instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠥ࡮ࡸࡵ࡮࠻ࡱࡱࡣࡦࡲ࡬ࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸࡸࠨዽ"), datetime.now() - bstack1l1lll1ll_opy_)
            self.bstack1l1l1l1111l_opy_(instance, bstack1llll1lll1l_opy_, event_json=event_json)
            instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠦࡴ࠷࠱ࡺ࠼ࡲࡲࡤࡧ࡬࡭ࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡹࠢዾ"), datetime.now() - bstack1l1l1l1l11l_opy_)
    def bstack1l1lll1llll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
        bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack11lll11l11_opy_.value)
        self.bstack1l1lllll11l_opy_.bstack1l1l11l111l_opy_(instance, f, bstack1llll1lll1l_opy_, *args, **kwargs)
        req = self.bstack1l1lllll11l_opy_.bstack1l1ll11111l_opy_(instance, f, bstack1llll1lll1l_opy_, *args, **kwargs)
        self.bstack1l1l1ll1111_opy_(f, instance, req)
        bstack1ll1l111ll1_opy_.end(EVENTS.bstack11lll11l11_opy_.value, bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧዿ"), bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦጀ"), status=True, failure=None, test_name=None)
    def bstack1ll11l11l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        if not f.bstack1llll111ll1_opy_(instance, self.bstack1l1lllll11l_opy_.bstack1l1l11ll111_opy_, False):
            req = self.bstack1l1lllll11l_opy_.bstack1l1ll11111l_opy_(instance, f, bstack1llll1lll1l_opy_, *args, **kwargs)
            self.bstack1l1l1ll1111_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l1ll11ll1l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l1l1ll1111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡔ࡭࡬ࡴࡵ࡯࡮ࡨࠢࡗࡩࡸࡺࡓࡦࡵࡶ࡭ࡴࡴࡅࡷࡧࡱࡸࠥ࡭ࡒࡑࡅࠣࡧࡦࡲ࡬࠻ࠢࡑࡳࠥࡼࡡ࡭࡫ࡧࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡪࡡࡵࡣࠥጁ"))
            return
        bstack1l1lll1ll_opy_ = datetime.now()
        try:
            r = self.bstack1lll1l1l1l1_opy_.TestSessionEvent(req)
            instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡩࡻ࡫࡮ࡵࠤጂ"), datetime.now() - bstack1l1lll1ll_opy_)
            f.bstack1llll1l1lll_opy_(instance, self.bstack1l1lllll11l_opy_.bstack1l1l11ll111_opy_, r.success)
            if not r.success:
                self.logger.info(bstack11111l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦጃ") + str(r) + bstack11111l_opy_ (u"ࠥࠦጄ"))
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤጅ") + str(e) + bstack11111l_opy_ (u"ࠧࠨጆ"))
            traceback.print_exc()
            raise e
    def bstack1l1ll111ll1_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        _driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        _1l1ll111l1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1lll1l11111_opy_.bstack1ll111ll11l_opy_(method_name):
            return
        if f.bstack1ll11l11l11_opy_(*args) == bstack1lll1l11111_opy_.bstack1l1ll111lll_opy_:
            bstack1l1l1l1l11l_opy_ = datetime.now()
            screenshot = result.get(bstack11111l_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧጇ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack11111l_opy_ (u"ࠢࡪࡰࡹࡥࡱ࡯ࡤࠡࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠥ࡯࡭ࡢࡩࡨࠤࡧࡧࡳࡦ࠸࠷ࠤࡸࡺࡲࠣገ"))
                return
            bstack1l1l1l1llll_opy_ = self.bstack1l1ll11l1ll_opy_(instance)
            if bstack1l1l1l1llll_opy_:
                entry = bstack1ll1lllll11_opy_(TestFramework.bstack1l1l1ll11ll_opy_, screenshot)
                self.bstack1l1ll11llll_opy_(bstack1l1l1l1llll_opy_, [entry])
                instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠣࡱ࠴࠵ࡾࡀ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡧࡻࡩࡨࡻࡴࡦࠤጉ"), datetime.now() - bstack1l1l1l1l11l_opy_)
            else:
                self.logger.warning(bstack11111l_opy_ (u"ࠤࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡶࡨࡷࡹࠦࡦࡰࡴࠣࡻ࡭࡯ࡣࡩࠢࡷ࡬࡮ࡹࠠࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠤࡼࡧࡳࠡࡶࡤ࡯ࡪࡴࠠࡣࡻࠣࡨࡷ࡯ࡶࡦࡴࡀࠤࢀࢃࠢጊ").format(instance.ref()))
        event = {}
        bstack1l1l1l1llll_opy_ = self.bstack1l1ll11l1ll_opy_(instance)
        if bstack1l1l1l1llll_opy_:
            self.bstack1l1l1lll111_opy_(event, bstack1l1l1l1llll_opy_)
            if event.get(bstack11111l_opy_ (u"ࠥࡰࡴ࡭ࡳࠣጋ")):
                self.bstack1l1ll11llll_opy_(bstack1l1l1l1llll_opy_, event[bstack11111l_opy_ (u"ࠦࡱࡵࡧࡴࠤጌ")])
            else:
                self.logger.debug(bstack11111l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡱࡵࡧࡴࠢࡩࡳࡷࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡩࡻ࡫࡮ࡵࠤግ"))
    @measure(event_name=EVENTS.bstack1l1ll1l111l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l1ll11llll_opy_(
        self,
        bstack1l1l1l1llll_opy_: bstack1lll1ll1ll1_opy_,
        entries: List[bstack1ll1lllll11_opy_],
    ):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1ll111ll111_opy_)
        req.execution_context.hash = str(bstack1l1l1l1llll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1l1llll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1l1llll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1lllllll1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1l1l111llll_opy_)
            log_entry.uuid = TestFramework.bstack1llll111ll1_opy_(bstack1l1l1l1llll_opy_, TestFramework.bstack1ll11111l11_opy_)
            log_entry.test_framework_state = bstack1l1l1l1llll_opy_.state.name
            log_entry.message = entry.message.encode(bstack11111l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧጎ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11111l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤጏ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll1111ll_opy_
                log_entry.file_path = entry.bstack1l1ll11_opy_
        def bstack1l1l1lll11l_opy_():
            bstack1l1lll1ll_opy_ = datetime.now()
            try:
                self.bstack1lll1l1l1l1_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l1l1ll11ll_opy_:
                    bstack1l1l1l1llll_opy_.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧጐ"), datetime.now() - bstack1l1lll1ll_opy_)
                elif entry.kind == TestFramework.bstack1l1ll11l11l_opy_:
                    bstack1l1l1l1llll_opy_.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨ጑"), datetime.now() - bstack1l1lll1ll_opy_)
                else:
                    bstack1l1l1l1llll_opy_.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡰࡴ࡭ࠢጒ"), datetime.now() - bstack1l1lll1ll_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11111l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤጓ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1lll11l_opy_)
    @measure(event_name=EVENTS.bstack1l1l1l1ll11_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l1l1l1111l_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        event_json=None,
    ):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1ll111ll111_opy_)
        req.test_framework_name = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1lllllll1_opy_)
        req.test_framework_version = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1l111llll_opy_)
        req.test_framework_state = bstack1llll1lll1l_opy_[0].name
        req.test_hook_state = bstack1llll1lll1l_opy_[1].name
        started_at = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1l1l111ll_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1l11lll1l_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1l11ll11l_opy_)).encode(bstack11111l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦጔ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1l1l1lll11l_opy_():
            bstack1l1lll1ll_opy_ = datetime.now()
            try:
                self.bstack1lll1l1l1l1_opy_.TestFrameworkEvent(req)
                instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡩࡻ࡫࡮ࡵࠤጕ"), datetime.now() - bstack1l1lll1ll_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11111l_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧ጖") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllll1l11l_opy_.enqueue(bstack1l1l1lll11l_opy_)
    def bstack1l1ll11l1ll_opy_(self, instance: bstack1llll111l1l_opy_):
        bstack1l1ll11ll11_opy_ = TestFramework.bstack1llll11111l_opy_(instance.context)
        for t in bstack1l1ll11ll11_opy_:
            bstack1l1l1ll1l11_opy_ = TestFramework.bstack1llll111ll1_opy_(t, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
            if any(instance is d[1] for d in bstack1l1l1ll1l11_opy_):
                return t
    def bstack1l1l111l1ll_opy_(self, message):
        self.bstack1l1l1l1l1l1_opy_(message + bstack11111l_opy_ (u"ࠣ࡞ࡱࠦ጗"))
    def log_error(self, message):
        self.bstack1l1l1ll11l1_opy_(message + bstack11111l_opy_ (u"ࠤ࡟ࡲࠧጘ"))
    def bstack1l1l1l1l1ll_opy_(self, level, original_func):
        def bstack1l1l1l11111_opy_(*args):
            try:
                try:
                    return_value = original_func(*args)
                except Exception:
                    return None
                try:
                    if not args or not isinstance(args[0], str) or not args[0].strip():
                        return return_value
                    message = args[0].strip()
                    if bstack11111l_opy_ (u"ࠥࡉࡻ࡫࡮ࡵࡆ࡬ࡷࡵࡧࡴࡤࡪࡨࡶࡒࡵࡤࡶ࡮ࡨࠦጙ") in message or bstack11111l_opy_ (u"ࠦࡠ࡙ࡄࡌࡅࡏࡍࡢࠨጚ") in message or bstack11111l_opy_ (u"ࠧࡡࡗࡦࡤࡇࡶ࡮ࡼࡥࡳࡏࡲࡨࡺࡲࡥ࡞ࠤጛ") in message:
                        return return_value
                    bstack1l1ll11ll11_opy_ = TestFramework.bstack1l1ll1111l1_opy_()
                    if not bstack1l1ll11ll11_opy_:
                        return return_value
                    bstack1l1l1l1llll_opy_ = next(
                        (
                            instance
                            for instance in bstack1l1ll11ll11_opy_
                            if TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11111l11_opy_)
                        ),
                        None,
                    )
                    if not bstack1l1l1l1llll_opy_:
                        return return_value
                    entry = bstack1ll1lllll11_opy_(TestFramework.bstack1l1l111lll1_opy_, message, level)
                    self.bstack1l1ll11llll_opy_(bstack1l1l1l1llll_opy_, [entry])
                except Exception:
                    pass
                return return_value
            except Exception:
                return None
        return bstack1l1l1l11111_opy_
    def bstack1l1l11l1lll_opy_(self):
        def bstack1l1ll11l111_opy_(*args, **kwargs):
            try:
                self.bstack1l1l1l111l1_opy_(*args, **kwargs)
                if not args:
                    return
                message = bstack11111l_opy_ (u"࠭ࠠࠨጜ").join(str(arg) for arg in args)
                if not message.strip():
                    return
                if bstack11111l_opy_ (u"ࠢࡆࡸࡨࡲࡹࡊࡩࡴࡲࡤࡸࡨ࡮ࡥࡳࡏࡲࡨࡺࡲࡥࠣጝ") in message:
                    return
                bstack1l1ll11ll11_opy_ = TestFramework.bstack1l1ll1111l1_opy_()
                if not bstack1l1ll11ll11_opy_:
                    return
                bstack1l1l1l1llll_opy_ = next(
                    (
                        instance
                        for instance in bstack1l1ll11ll11_opy_
                        if TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11111l11_opy_)
                    ),
                    None,
                )
                if not bstack1l1l1l1llll_opy_:
                    return
                entry = bstack1ll1lllll11_opy_(TestFramework.bstack1l1l111lll1_opy_, message, bstack1ll1l1111ll_opy_.bstack1l1ll1l1111_opy_)
                self.bstack1l1ll11llll_opy_(bstack1l1l1l1llll_opy_, [entry])
            except Exception as e:
                try:
                    self.bstack1l1l1l111l1_opy_(bstack1ll1lll1l1l_opy_ (u"ࠣ࡝ࡈࡺࡪࡴࡴࡅ࡫ࡶࡴࡦࡺࡣࡩࡧࡵࡑࡴࡪࡵ࡭ࡧࡠࠤࡑࡵࡧࠡࡥࡤࡴࡹࡻࡲࡦࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࡩࢂࠨጞ"))
                except:
                    pass
        return bstack1l1ll11l111_opy_
    def bstack1l1l1lll111_opy_(self, event: dict, instance=None) -> None:
        global _1l1ll111111_opy_
        levels = [bstack11111l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧጟ"), bstack11111l_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢጠ")]
        bstack1l1l1l11l11_opy_ = bstack11111l_opy_ (u"ࠦࠧጡ")
        if instance is not None:
            try:
                bstack1l1l1l11l11_opy_ = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1ll11111l11_opy_)
            except Exception as e:
                self.logger.warning(bstack11111l_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡻࡵࡪࡦࠣࡪࡷࡵ࡭ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠥጢ").format(e))
        bstack1l1ll111l11_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ጣ")]
                bstack1l1l1lllll1_opy_ = os.path.join(bstack1l1l11lllll_opy_, (bstack1l1l11l1111_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1l1l1lllll1_opy_):
                    self.logger.debug(bstack11111l_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡲࡴࡺࠠࡱࡴࡨࡷࡪࡴࡴࠡࡨࡲࡶࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡗࡩࡸࡺࠠࡢࡰࡧࠤࡇࡻࡩ࡭ࡦࠣࡰࡪࡼࡥ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥጤ").format(bstack1l1l1lllll1_opy_))
                    continue
                file_names = os.listdir(bstack1l1l1lllll1_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1l1l1lllll1_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1l1ll111111_opy_:
                        self.logger.info(bstack11111l_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨጥ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1l1l11l1l11_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1l1l11l1l11_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack11111l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧጦ"):
                                entry = bstack1ll1lllll11_opy_(
                                    kind=bstack11111l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧጧ"),
                                    message=bstack11111l_opy_ (u"ࠦࠧጨ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll1111ll_opy_=file_size,
                                    bstack1l1l1l1l111_opy_=bstack11111l_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧጩ"),
                                    bstack1l1ll11_opy_=os.path.abspath(file_path),
                                    bstack111llll1_opy_=bstack1l1l1l11l11_opy_
                                )
                            elif level == bstack11111l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥጪ"):
                                entry = bstack1ll1lllll11_opy_(
                                    kind=bstack11111l_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤጫ"),
                                    message=bstack11111l_opy_ (u"ࠣࠤጬ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll1111ll_opy_=file_size,
                                    bstack1l1l1l1l111_opy_=bstack11111l_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤጭ"),
                                    bstack1l1ll11_opy_=os.path.abspath(file_path),
                                    bstack1l1l1ll1ll1_opy_=bstack1l1l1l11l11_opy_
                                )
                            bstack1l1ll111l11_opy_.append(entry)
                            _1l1ll111111_opy_.add(abs_path)
                        except Exception as bstack1l1l1l11ll1_opy_:
                            self.logger.error(bstack11111l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡲࡢ࡫ࡶࡩࡩࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡻࡾࠤጮ").format(bstack1l1l1l11ll1_opy_))
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡳࡣ࡬ࡷࡪࡪࠠࡸࡪࡨࡲࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥጯ").format(e))
        event[bstack11111l_opy_ (u"ࠧࡲ࡯ࡨࡵࠥጰ")] = bstack1l1ll111l11_opy_
class bstack1l1l11ll11l_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1l1lll1ll_opy_ = set()
        kwargs[bstack11111l_opy_ (u"ࠨࡳ࡬࡫ࡳ࡯ࡪࡿࡳࠣጱ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1l1l11l1ll1_opy_(obj, self.bstack1l1l1lll1ll_opy_)
def bstack1l1l11l11ll_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1l1l11l1ll1_opy_(obj, bstack1l1l1lll1ll_opy_=None, max_depth=3):
    if bstack1l1l1lll1ll_opy_ is None:
        bstack1l1l1lll1ll_opy_ = set()
    if id(obj) in bstack1l1l1lll1ll_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1l1lll1ll_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1l1l1llll11_opy_ = TestFramework.bstack1l1l1l1lll1_opy_(obj)
    bstack1l1l1l11lll_opy_ = next((k.lower() in bstack1l1l1llll11_opy_.lower() for k in bstack1l1l1lll1l1_opy_.keys()), None)
    if bstack1l1l1l11lll_opy_:
        obj = TestFramework.bstack1l1l111ll11_opy_(obj, bstack1l1l1lll1l1_opy_[bstack1l1l1l11lll_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack11111l_opy_ (u"ࠢࡠࡡࡶࡰࡴࡺࡳࡠࡡࠥጲ")):
            keys = getattr(obj, bstack11111l_opy_ (u"ࠣࡡࡢࡷࡱࡵࡴࡴࡡࡢࠦጳ"), [])
        elif hasattr(obj, bstack11111l_opy_ (u"ࠤࡢࡣࡩ࡯ࡣࡵࡡࡢࠦጴ")):
            keys = getattr(obj, bstack11111l_opy_ (u"ࠥࡣࡤࡪࡩࡤࡶࡢࡣࠧጵ"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack11111l_opy_ (u"ࠦࡤࠨጶ"))}
        if not obj and bstack1l1l1llll11_opy_ == bstack11111l_opy_ (u"ࠧࡶࡡࡵࡪ࡯࡭ࡧ࠴ࡐࡰࡵ࡬ࡼࡕࡧࡴࡩࠤጷ"):
            obj = {bstack11111l_opy_ (u"ࠨࡰࡢࡶ࡫ࠦጸ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1l1l11l11ll_opy_(key) or str(key).startswith(bstack11111l_opy_ (u"ࠢࡠࠤጹ")):
            continue
        if value is not None and bstack1l1l11l11ll_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1l1l11l1ll1_opy_(value, bstack1l1l1lll1ll_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1l1l11l1ll1_opy_(o, bstack1l1l1lll1ll_opy_, max_depth) for o in value]))
    return result or None