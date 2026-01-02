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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
    bstack1llll1ll1l1_opy_,
    bstack1llll111l1l_opy_,
    bstack1lllll1l111_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_, bstack1lll1ll1ll1_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1ll11l_opy_ import bstack1l1ll1l1ll1_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1ll11lll1_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1ll1l11l111_opy_(bstack1l1ll1l1ll1_opy_):
    bstack1l11l1ll1ll_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡪࡲࡪࡸࡨࡶࡸࠨᐠ")
    bstack1l1l1l1ll1l_opy_ = bstack11111l_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࡹࠢᐡ")
    bstack1l11ll1l11l_opy_ = bstack11111l_opy_ (u"ࠤࡱࡳࡳࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦᐢ")
    bstack1l11ll111ll_opy_ = bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥᐣ")
    bstack1l11l1ll11l_opy_ = bstack11111l_opy_ (u"ࠦࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡢࡶࡪ࡬ࡳࠣᐤ")
    bstack1l1l11ll111_opy_ = bstack11111l_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡧࡷ࡫ࡡࡵࡧࡧࠦᐥ")
    bstack1l11ll1111l_opy_ = bstack11111l_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡳࡧ࡭ࡦࠤᐦ")
    bstack1l11ll1l1l1_opy_ = bstack11111l_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡹࡴࡢࡶࡸࡷࠧᐧ")
    def __init__(self):
        super().__init__(bstack1l1ll1l11ll_opy_=self.bstack1l11l1ll1ll_opy_, frameworks=[bstack1lll1l11111_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.BEFORE_EACH, bstack1lll1ll1111_opy_.POST), self.bstack1l111ll111l_opy_)
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.PRE), self.bstack1l1lll1llll_opy_)
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST), self.bstack1ll11l11l1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l111ll111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l1ll1l11_opy_ = self.bstack1l111llll11_opy_(instance.context)
        if not bstack1l1l1ll1l11_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦᐨ") + str(bstack1llll1lll1l_opy_) + bstack11111l_opy_ (u"ࠤࠥᐩ"))
        f.bstack1llll1l1lll_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, bstack1l1l1ll1l11_opy_)
        bstack1l111ll1l11_opy_ = self.bstack1l111llll11_opy_(instance.context, bstack1l111ll1l1l_opy_=False)
        f.bstack1llll1l1lll_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l11l_opy_, bstack1l111ll1l11_opy_)
    def bstack1l1lll1llll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1111l_opy_, False):
            self.__1l111ll1lll_opy_(f,instance,bstack1llll1lll1l_opy_)
    def bstack1ll11l11l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1111l_opy_, False):
            self.__1l111ll1lll_opy_(f, instance, bstack1llll1lll1l_opy_)
        if not f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l1l1_opy_, False):
            self.__1l111lll111_opy_(f, instance, bstack1llll1lll1l_opy_)
    def bstack1l111ll11ll_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1l1ll1l1l1l_opy_(instance):
            return
        if f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l1l1_opy_, False):
            return
        driver.execute_script(
            bstack11111l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠣᐪ").format(
                json.dumps(
                    {
                        bstack11111l_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦᐫ"): bstack11111l_opy_ (u"ࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣᐬ"),
                        bstack11111l_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤᐭ"): {bstack11111l_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᐮ"): result},
                    }
                )
            )
        )
        f.bstack1llll1l1lll_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l1l1_opy_, True)
    def bstack1l111llll11_opy_(self, context: bstack1lllll1l111_opy_, bstack1l111ll1l1l_opy_= True):
        if bstack1l111ll1l1l_opy_:
            bstack1l1l1ll1l11_opy_ = self.bstack1l1ll1ll1ll_opy_(context, reverse=True)
        else:
            bstack1l1l1ll1l11_opy_ = self.bstack1l1ll1ll111_opy_(context, reverse=True)
        return [f for f in bstack1l1l1ll1l11_opy_ if f[1].state != bstack1lllll11111_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1l1111111l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def __1l111lll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨᐯ")).get(bstack11111l_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨᐰ")):
            bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
            if not bstack1l1l1ll1l11_opy_:
                self.logger.debug(bstack11111l_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨᐱ") + str(bstack1llll1lll1l_opy_) + bstack11111l_opy_ (u"ࠦࠧᐲ"))
                return
            driver = bstack1l1l1ll1l11_opy_[0][0]()
            status = f.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l11l1ll1l1_opy_, None)
            if not status:
                self.logger.debug(bstack11111l_opy_ (u"ࠧࡹࡥࡵࡡࡤࡧࡹ࡯ࡶࡦࡡࡧࡶ࡮ࡼࡥࡳࡵ࠽ࠤࡳࡵࠠࡴࡶࡤࡸࡺࡹࠠࡧࡱࡵࠤࡹ࡫ࡳࡵ࠮ࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢᐳ") + str(bstack1llll1lll1l_opy_) + bstack11111l_opy_ (u"ࠨࠢᐴ"))
                return
            bstack1l11l1lll1l_opy_ = {bstack11111l_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᐵ"): status.lower()}
            bstack1l11ll1l111_opy_ = f.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l11ll11lll_opy_, None)
            if status.lower() == bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᐶ") and bstack1l11ll1l111_opy_ is not None:
                bstack1l11l1lll1l_opy_[bstack11111l_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩᐷ")] = bstack1l11ll1l111_opy_[0][bstack11111l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᐸ")][0] if isinstance(bstack1l11ll1l111_opy_, list) else str(bstack1l11ll1l111_opy_)
            driver.execute_script(
                bstack11111l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤᐹ").format(
                    json.dumps(
                        {
                            bstack11111l_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧᐺ"): bstack11111l_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤᐻ"),
                            bstack11111l_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᐼ"): bstack1l11l1lll1l_opy_,
                        }
                    )
                )
            )
            f.bstack1llll1l1lll_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l1l1_opy_, True)
    @measure(event_name=EVENTS.bstack1lll1lll1l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def __1l111ll1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨᐽ")).get(bstack11111l_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦᐾ")):
            test_name = f.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l111lll11l_opy_, None)
            if not test_name:
                self.logger.debug(bstack11111l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡳࡧ࡭ࡦࠤᐿ"))
                return
            bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
            if not bstack1l1l1ll1l11_opy_:
                self.logger.debug(bstack11111l_opy_ (u"ࠦࡸ࡫ࡴࡠࡣࡦࡸ࡮ࡼࡥࡠࡦࡵ࡭ࡻ࡫ࡲࡴ࠼ࠣࡲࡴࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡸࡪࡹࡴ࠭ࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨᑀ") + str(bstack1llll1lll1l_opy_) + bstack11111l_opy_ (u"ࠧࠨᑁ"))
                return
            for bstack1l1l111l11l_opy_, bstack1l111lll1l1_opy_ in bstack1l1l1ll1l11_opy_:
                if not bstack1lll1l11111_opy_.bstack1l1ll1l1l1l_opy_(bstack1l111lll1l1_opy_):
                    continue
                driver = bstack1l1l111l11l_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack11111l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠦᑂ").format(
                        json.dumps(
                            {
                                bstack11111l_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢᑃ"): bstack11111l_opy_ (u"ࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤᑄ"),
                                bstack11111l_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧᑅ"): {bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣᑆ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1llll1l1lll_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1111l_opy_, True)
    def bstack1l1l11l111l_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        bstack1l1l1ll1l11_opy_ = [d for d, _ in f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])]
        if not bstack1l1l1ll1l11_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡵࡨࡷࡸ࡯࡯࡯ࡵࠣࡸࡴࠦ࡬ࡪࡰ࡮ࠦᑇ"))
            return
        if not bstack1l1ll11lll1_opy_():
            self.logger.debug(bstack11111l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥᑈ"))
            return
        for bstack1l111ll11l1_opy_ in bstack1l1l1ll1l11_opy_:
            driver = bstack1l111ll11l1_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack11111l_opy_ (u"ࠨࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࡙ࡹ࡯ࡥ࠽ࠦᑉ") + str(timestamp)
            driver.execute_script(
                bstack11111l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠧᑊ").format(
                    json.dumps(
                        {
                            bstack11111l_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࠣᑋ"): bstack11111l_opy_ (u"ࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦᑌ"),
                            bstack11111l_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨᑍ"): {
                                bstack11111l_opy_ (u"ࠦࡹࡿࡰࡦࠤᑎ"): bstack11111l_opy_ (u"ࠧࡇ࡮࡯ࡱࡷࡥࡹ࡯࡯࡯ࠤᑏ"),
                                bstack11111l_opy_ (u"ࠨࡤࡢࡶࡤࠦᑐ"): data,
                                bstack11111l_opy_ (u"ࠢ࡭ࡧࡹࡩࡱࠨᑑ"): bstack11111l_opy_ (u"ࠣࡦࡨࡦࡺ࡭ࠢᑒ")
                            }
                        }
                    )
                )
            )
    def bstack1l1ll11111l_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111ll111l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        keys = [
            bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_,
            bstack1ll1l11l111_opy_.bstack1l11ll1l11l_opy_,
        ]
        bstack1l1l1ll1l11_opy_ = []
        for key in keys:
            bstack1l1l1ll1l11_opy_.extend(f.bstack1llll111ll1_opy_(instance, key, []))
        if not bstack1l1l1ll1l11_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡹࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪࡰࡧࠤࡦࡴࡹࠡࡵࡨࡷࡸ࡯࡯࡯ࡵࠣࡸࡴࠦ࡬ࡪࡰ࡮ࠦᑓ"))
            return
        if f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l11ll111_opy_, False):
            self.logger.debug(bstack11111l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡈࡈࡔࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡦࡶࡪࡧࡴࡦࡦࠥᑔ"))
            return
        self.bstack1l1lll1l1ll_opy_()
        bstack1l1lll1ll_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1ll111ll111_opy_)
        req.test_framework_name = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1lllllll1_opy_)
        req.test_framework_version = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1l111llll_opy_)
        req.test_framework_state = bstack1llll1lll1l_opy_[0].name
        req.test_hook_state = bstack1llll1lll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1ll11111l11_opy_)
        for bstack1l1l111l11l_opy_, driver in bstack1l1l1ll1l11_opy_:
            try:
                webdriver = bstack1l1l111l11l_opy_()
                if webdriver is None:
                    self.logger.debug(bstack11111l_opy_ (u"ࠦ࡜࡫ࡢࡅࡴ࡬ࡺࡪࡸࠠࡪࡰࡶࡸࡦࡴࡣࡦࠢ࡬ࡷࠥࡔ࡯࡯ࡧࠣࠬࡷ࡫ࡦࡦࡴࡨࡲࡨ࡫ࠠࡦࡺࡳ࡭ࡷ࡫ࡤࠪࠤᑕ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack11111l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠦᑖ")
                    if bstack1lll1l11111_opy_.bstack1llll111ll1_opy_(driver, bstack1lll1l11111_opy_.bstack1l111lll1ll_opy_, False)
                    else bstack11111l_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴ࡟ࡨࡴ࡬ࡨࠧᑗ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1lll1l11111_opy_.bstack1llll111ll1_opy_(driver, bstack1lll1l11111_opy_.bstack1l11llll111_opy_, bstack11111l_opy_ (u"ࠢࠣᑘ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1lll1l11111_opy_.bstack1llll111ll1_opy_(driver, bstack1lll1l11111_opy_.bstack1l11lllll11_opy_, bstack11111l_opy_ (u"ࠣࠤᑙ"))
                caps = None
                if hasattr(webdriver, bstack11111l_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᑚ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack11111l_opy_ (u"ࠥࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤࡩ࡯ࡲࡦࡥࡷࡰࡾࠦࡦࡳࡱࡰࠤࡩࡸࡩࡷࡧࡵ࠲ࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᑛ"))
                    except Exception as e:
                        self.logger.debug(bstack11111l_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡨࡧࡷࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡪࡷࡵ࡭ࠡࡦࡵ࡭ࡻ࡫ࡲ࠯ࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹ࠺ࠡࠤᑜ") + str(e) + bstack11111l_opy_ (u"ࠧࠨᑝ"))
                try:
                    bstack1l111ll1ll1_opy_ = json.dumps(caps).encode(bstack11111l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᑞ")) if caps else bstack1l111ll1111_opy_ (u"ࠢࡼࡿࠥᑟ")
                    req.capabilities = bstack1l111ll1ll1_opy_
                except Exception as e:
                    self.logger.debug(bstack11111l_opy_ (u"ࠣࡩࡨࡸࡤࡩࡢࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥ࡯ࡦࠣࡷࡪࡸࡩࡢ࡮࡬ࡾࡪࠦࡣࡢࡲࡶࠤ࡫ࡵࡲࠡࡴࡨࡵࡺ࡫ࡳࡵ࠼ࠣࠦᑠ") + str(e) + bstack11111l_opy_ (u"ࠤࠥᑡ"))
            except Exception as e:
                self.logger.error(bstack11111l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡤࡳ࡫ࡹࡩࡷࠦࡩࡵࡧࡰ࠾ࠥࠨᑢ") + str(str(e)) + bstack11111l_opy_ (u"ࠦࠧᑣ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11111ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l1ll11lll1_opy_() and len(bstack1l1l1ll1l11_opy_) == 0:
            bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l11l_opy_, [])
        if not bstack1l1l1ll1l11_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᑤ") + str(kwargs) + bstack11111l_opy_ (u"ࠨࠢᑥ"))
            return {}
        if len(bstack1l1l1ll1l11_opy_) > 1:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᑦ") + str(kwargs) + bstack11111l_opy_ (u"ࠣࠤᑧ"))
            return {}
        bstack1l1l111l11l_opy_, bstack1l1l1111l1l_opy_ = bstack1l1l1ll1l11_opy_[0]
        driver = bstack1l1l111l11l_opy_()
        if not driver:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᑨ") + str(kwargs) + bstack11111l_opy_ (u"ࠥࠦᑩ"))
            return {}
        capabilities = f.bstack1llll111ll1_opy_(bstack1l1l1111l1l_opy_, bstack1lll1l11111_opy_.bstack1l11llll11l_opy_)
        if not capabilities:
            self.logger.debug(bstack11111l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡨࡲࡹࡳࡪࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᑪ") + str(kwargs) + bstack11111l_opy_ (u"ࠧࠨᑫ"))
            return {}
        return capabilities.get(bstack11111l_opy_ (u"ࠨࡡ࡭ࡹࡤࡽࡸࡓࡡࡵࡥ࡫ࠦᑬ"), {})
    def bstack1ll11l1lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l1ll11lll1_opy_() and len(bstack1l1l1ll1l11_opy_) == 0:
            bstack1l1l1ll1l11_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1ll1l11l111_opy_.bstack1l11ll1l11l_opy_, [])
        if not bstack1l1l1ll1l11_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᑭ") + str(kwargs) + bstack11111l_opy_ (u"ࠣࠤᑮ"))
            return
        if len(bstack1l1l1ll1l11_opy_) > 1:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀࡲࡥ࡯ࠪࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷ࠮ࢃࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᑯ") + str(kwargs) + bstack11111l_opy_ (u"ࠥࠦᑰ"))
        bstack1l1l111l11l_opy_, bstack1l1l1111l1l_opy_ = bstack1l1l1ll1l11_opy_[0]
        driver = bstack1l1l111l11l_opy_()
        if not driver:
            self.logger.debug(bstack11111l_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡪࡲࡪࡸࡨࡶ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᑱ") + str(kwargs) + bstack11111l_opy_ (u"ࠧࠨᑲ"))
            return
        return driver