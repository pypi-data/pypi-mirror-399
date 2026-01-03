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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1llll1ll1ll_opy_,
    bstack1lllll11l1l_opy_,
    bstack1llll111lll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_, bstack1lll111l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1l1l11_opy_ import bstack1l1ll1l1ll1_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l111l1l1_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1ll11lll1ll_opy_(bstack1l1ll1l1ll1_opy_):
    bstack1l11l1lll11_opy_ = bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡪࡲࡪࡸࡨࡶࡸࠨᐧ")
    bstack1l1l11lllll_opy_ = bstack1l1l_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࡹࠢᐨ")
    bstack1l11l1llll1_opy_ = bstack1l1l_opy_ (u"ࠤࡱࡳࡳࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦᐩ")
    bstack1l11l1l1lll_opy_ = bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥᐪ")
    bstack1l11ll11111_opy_ = bstack1l1l_opy_ (u"ࠦࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡢࡶࡪ࡬ࡳࠣᐫ")
    bstack1l1l111ll1l_opy_ = bstack1l1l_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡧࡷ࡫ࡡࡵࡧࡧࠦᐬ")
    bstack1l11l1ll111_opy_ = bstack1l1l_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡳࡧ࡭ࡦࠤᐭ")
    bstack1l11ll11l11_opy_ = bstack1l1l_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡹࡴࡢࡶࡸࡷࠧᐮ")
    def __init__(self):
        super().__init__(bstack1l1ll1l111l_opy_=self.bstack1l11l1lll11_opy_, frameworks=[bstack1ll1lll1lll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.BEFORE_EACH, bstack1ll1ll111l1_opy_.POST), self.bstack1l111ll1l1l_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.PRE), self.bstack1ll11111l11_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), self.bstack1ll111l1111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l111ll1l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l11lll1l_opy_ = self.bstack1l111lll11l_opy_(instance.context)
        if not bstack1l1l11lll1l_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦᐯ") + str(bstack1llll1llll1_opy_) + bstack1l1l_opy_ (u"ࠤࠥᐰ"))
        f.bstack1llll1lll11_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, bstack1l1l11lll1l_opy_)
        bstack1l111ll1ll1_opy_ = self.bstack1l111lll11l_opy_(instance.context, bstack1l111ll1l11_opy_=False)
        f.bstack1llll1lll11_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11l1llll1_opy_, bstack1l111ll1ll1_opy_)
    def bstack1ll11111l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll1l1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        if not f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11l1ll111_opy_, False):
            self.__1l111l1lll1_opy_(f,instance,bstack1llll1llll1_opy_)
    def bstack1ll111l1111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll1l1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        if not f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11l1ll111_opy_, False):
            self.__1l111l1lll1_opy_(f, instance, bstack1llll1llll1_opy_)
        if not f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11ll11l11_opy_, False):
            self.__1l111lll111_opy_(f, instance, bstack1llll1llll1_opy_)
    def bstack1l111ll11ll_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1l1ll1l11l1_opy_(instance):
            return
        if f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11ll11l11_opy_, False):
            return
        driver.execute_script(
            bstack1l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠣᐱ").format(
                json.dumps(
                    {
                        bstack1l1l_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦᐲ"): bstack1l1l_opy_ (u"ࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣᐳ"),
                        bstack1l1l_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤᐴ"): {bstack1l1l_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᐵ"): result},
                    }
                )
            )
        )
        f.bstack1llll1lll11_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11ll11l11_opy_, True)
    def bstack1l111lll11l_opy_(self, context: bstack1llll111lll_opy_, bstack1l111ll1l11_opy_= True):
        if bstack1l111ll1l11_opy_:
            bstack1l1l11lll1l_opy_ = self.bstack1l1ll1l1111_opy_(context, reverse=True)
        else:
            bstack1l1l11lll1l_opy_ = self.bstack1l1ll1lll1l_opy_(context, reverse=True)
        return [f for f in bstack1l1l11lll1l_opy_ if f[1].state != bstack1llll11ll11_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1l11l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1l111lll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨᐶ")).get(bstack1l1l_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨᐷ")):
            bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
            if not bstack1l1l11lll1l_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨᐸ") + str(bstack1llll1llll1_opy_) + bstack1l1l_opy_ (u"ࠦࠧᐹ"))
                return
            driver = bstack1l1l11lll1l_opy_[0][0]()
            status = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l11ll11lll_opy_, None)
            if not status:
                self.logger.debug(bstack1l1l_opy_ (u"ࠧࡹࡥࡵࡡࡤࡧࡹ࡯ࡶࡦࡡࡧࡶ࡮ࡼࡥࡳࡵ࠽ࠤࡳࡵࠠࡴࡶࡤࡸࡺࡹࠠࡧࡱࡵࠤࡹ࡫ࡳࡵ࠮ࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢᐺ") + str(bstack1llll1llll1_opy_) + bstack1l1l_opy_ (u"ࠨࠢᐻ"))
                return
            bstack1l11ll11ll1_opy_ = {bstack1l1l_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᐼ"): status.lower()}
            bstack1l11ll111ll_opy_ = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l11l1ll1l1_opy_, None)
            if status.lower() == bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᐽ") and bstack1l11ll111ll_opy_ is not None:
                bstack1l11ll11ll1_opy_[bstack1l1l_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩᐾ")] = bstack1l11ll111ll_opy_[0][bstack1l1l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᐿ")][0] if isinstance(bstack1l11ll111ll_opy_, list) else str(bstack1l11ll111ll_opy_)
            driver.execute_script(
                bstack1l1l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤᑀ").format(
                    json.dumps(
                        {
                            bstack1l1l_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧᑁ"): bstack1l1l_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤᑂ"),
                            bstack1l1l_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᑃ"): bstack1l11ll11ll1_opy_,
                        }
                    )
                )
            )
            f.bstack1llll1lll11_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11ll11l11_opy_, True)
    @measure(event_name=EVENTS.bstack1ll1l111ll_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1l111l1lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨᑄ")).get(bstack1l1l_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦᑅ")):
            test_name = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l111ll1111_opy_, None)
            if not test_name:
                self.logger.debug(bstack1l1l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡳࡧ࡭ࡦࠤᑆ"))
                return
            bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
            if not bstack1l1l11lll1l_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡸ࡫ࡴࡠࡣࡦࡸ࡮ࡼࡥࡠࡦࡵ࡭ࡻ࡫ࡲࡴ࠼ࠣࡲࡴࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡸࡪࡹࡴ࠭ࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨᑇ") + str(bstack1llll1llll1_opy_) + bstack1l1l_opy_ (u"ࠧࠨᑈ"))
                return
            for bstack1l11lllllll_opy_, bstack1l111l1llll_opy_ in bstack1l1l11lll1l_opy_:
                if not bstack1ll1lll1lll_opy_.bstack1l1ll1l11l1_opy_(bstack1l111l1llll_opy_):
                    continue
                driver = bstack1l11lllllll_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack1l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠦᑉ").format(
                        json.dumps(
                            {
                                bstack1l1l_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢᑊ"): bstack1l1l_opy_ (u"ࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤᑋ"),
                                bstack1l1l_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧᑌ"): {bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᑍ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1llll1lll11_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11l1ll111_opy_, True)
    def bstack1l1ll111ll1_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll1l1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        bstack1l1l11lll1l_opy_ = [d for d, _ in f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])]
        if not bstack1l1l11lll1l_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡵࡨࡷࡸ࡯࡯࡯ࡵࠣࡸࡴࠦ࡬ࡪࡰ࡮ࠦᑎ"))
            return
        if not bstack1l1l111l1l1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥᑏ"))
            return
        for bstack1l111ll11l1_opy_ in bstack1l1l11lll1l_opy_:
            driver = bstack1l111ll11l1_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack1l1l_opy_ (u"ࠨࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࡙ࡹ࡯ࡥ࠽ࠦᑐ") + str(timestamp)
            driver.execute_script(
                bstack1l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠧᑑ").format(
                    json.dumps(
                        {
                            bstack1l1l_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࠣᑒ"): bstack1l1l_opy_ (u"ࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦᑓ"),
                            bstack1l1l_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨᑔ"): {
                                bstack1l1l_opy_ (u"ࠦࡹࡿࡰࡦࠤᑕ"): bstack1l1l_opy_ (u"ࠧࡇ࡮࡯ࡱࡷࡥࡹ࡯࡯࡯ࠤᑖ"),
                                bstack1l1l_opy_ (u"ࠨࡤࡢࡶࡤࠦᑗ"): data,
                                bstack1l1l_opy_ (u"ࠢ࡭ࡧࡹࡩࡱࠨᑘ"): bstack1l1l_opy_ (u"ࠣࡦࡨࡦࡺ࡭ࠢᑙ")
                            }
                        }
                    )
                )
            )
    def bstack1l1l111l11l_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll1l1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        keys = [
            bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_,
            bstack1ll11lll1ll_opy_.bstack1l11l1llll1_opy_,
        ]
        bstack1l1l11lll1l_opy_ = []
        for key in keys:
            bstack1l1l11lll1l_opy_.extend(f.bstack1llll1l11ll_opy_(instance, key, []))
        if not bstack1l1l11lll1l_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡹࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪࡰࡧࠤࡦࡴࡹࠡࡵࡨࡷࡸ࡯࡯࡯ࡵࠣࡸࡴࠦ࡬ࡪࡰ࡮ࠦᑚ"))
            return
        if f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l111ll1l_opy_, False):
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡈࡈࡔࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡦࡶࡪࡧࡴࡦࡦࠥᑛ"))
            return
        self.bstack1ll11l1ll11_opy_()
        bstack1ll111l1_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1llllll1l_opy_)
        req.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l11lll_opy_)
        req.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1l11l11ll_opy_)
        req.test_framework_state = bstack1llll1llll1_opy_[0].name
        req.test_hook_state = bstack1llll1llll1_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
        for bstack1l11lllllll_opy_, driver in bstack1l1l11lll1l_opy_:
            try:
                webdriver = bstack1l11lllllll_opy_()
                if webdriver is None:
                    self.logger.debug(bstack1l1l_opy_ (u"ࠦ࡜࡫ࡢࡅࡴ࡬ࡺࡪࡸࠠࡪࡰࡶࡸࡦࡴࡣࡦࠢ࡬ࡷࠥࡔ࡯࡯ࡧࠣࠬࡷ࡫ࡦࡦࡴࡨࡲࡨ࡫ࠠࡦࡺࡳ࡭ࡷ࡫ࡤࠪࠤᑜ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack1l1l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠦᑝ")
                    if bstack1ll1lll1lll_opy_.bstack1llll1l11ll_opy_(driver, bstack1ll1lll1lll_opy_.bstack1l111ll1lll_opy_, False)
                    else bstack1l1l_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴ࡟ࡨࡴ࡬ࡨࠧᑞ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1ll1lll1lll_opy_.bstack1llll1l11ll_opy_(driver, bstack1ll1lll1lll_opy_.bstack1l11lll1111_opy_, bstack1l1l_opy_ (u"ࠢࠣᑟ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1ll1lll1lll_opy_.bstack1llll1l11ll_opy_(driver, bstack1ll1lll1lll_opy_.bstack1l11lll1l11_opy_, bstack1l1l_opy_ (u"ࠣࠤᑠ"))
                caps = None
                if hasattr(webdriver, bstack1l1l_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᑡ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack1l1l_opy_ (u"ࠥࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤࡩ࡯ࡲࡦࡥࡷࡰࡾࠦࡦࡳࡱࡰࠤࡩࡸࡩࡷࡧࡵ࠲ࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᑢ"))
                    except Exception as e:
                        self.logger.debug(bstack1l1l_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡨࡧࡷࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡪࡷࡵ࡭ࠡࡦࡵ࡭ࡻ࡫ࡲ࠯ࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹ࠺ࠡࠤᑣ") + str(e) + bstack1l1l_opy_ (u"ࠧࠨᑤ"))
                try:
                    bstack1l111lll1l1_opy_ = json.dumps(caps).encode(bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᑥ")) if caps else bstack1l111ll111l_opy_ (u"ࠢࡼࡿࠥᑦ")
                    req.capabilities = bstack1l111lll1l1_opy_
                except Exception as e:
                    self.logger.debug(bstack1l1l_opy_ (u"ࠣࡩࡨࡸࡤࡩࡢࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥ࡯ࡦࠣࡷࡪࡸࡩࡢ࡮࡬ࡾࡪࠦࡣࡢࡲࡶࠤ࡫ࡵࡲࠡࡴࡨࡵࡺ࡫ࡳࡵ࠼ࠣࠦᑧ") + str(e) + bstack1l1l_opy_ (u"ࠤࠥᑨ"))
            except Exception as e:
                self.logger.error(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡤࡳ࡫ࡹࡩࡷࠦࡩࡵࡧࡰ࠾ࠥࠨᑩ") + str(str(e)) + bstack1l1l_opy_ (u"ࠦࠧᑪ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l1l111l1l1_opy_() and len(bstack1l1l11lll1l_opy_) == 0:
            bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11l1llll1_opy_, [])
        if not bstack1l1l11lll1l_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᑫ") + str(kwargs) + bstack1l1l_opy_ (u"ࠨࠢᑬ"))
            return {}
        if len(bstack1l1l11lll1l_opy_) > 1:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᑭ") + str(kwargs) + bstack1l1l_opy_ (u"ࠣࠤᑮ"))
            return {}
        bstack1l11lllllll_opy_, bstack1l1l111111l_opy_ = bstack1l1l11lll1l_opy_[0]
        driver = bstack1l11lllllll_opy_()
        if not driver:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᑯ") + str(kwargs) + bstack1l1l_opy_ (u"ࠥࠦᑰ"))
            return {}
        capabilities = f.bstack1llll1l11ll_opy_(bstack1l1l111111l_opy_, bstack1ll1lll1lll_opy_.bstack1l11llll1ll_opy_)
        if not capabilities:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡨࡲࡹࡳࡪࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᑱ") + str(kwargs) + bstack1l1l_opy_ (u"ࠧࠨᑲ"))
            return {}
        return capabilities.get(bstack1l1l_opy_ (u"ࠨࡡ࡭ࡹࡤࡽࡸࡓࡡࡵࡥ࡫ࠦᑳ"), {})
    def bstack1ll11l1l11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l1l111l1l1_opy_() and len(bstack1l1l11lll1l_opy_) == 0:
            bstack1l1l11lll1l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11l1llll1_opy_, [])
        if not bstack1l1l11lll1l_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᑴ") + str(kwargs) + bstack1l1l_opy_ (u"ࠣࠤᑵ"))
            return
        if len(bstack1l1l11lll1l_opy_) > 1:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀࡲࡥ࡯ࠪࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷ࠮ࢃࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᑶ") + str(kwargs) + bstack1l1l_opy_ (u"ࠥࠦᑷ"))
        bstack1l11lllllll_opy_, bstack1l1l111111l_opy_ = bstack1l1l11lll1l_opy_[0]
        driver = bstack1l11lllllll_opy_()
        if not driver:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡪࡲࡪࡸࡨࡶ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᑸ") + str(kwargs) + bstack1l1l_opy_ (u"ࠧࠨᑹ"))
            return
        return driver