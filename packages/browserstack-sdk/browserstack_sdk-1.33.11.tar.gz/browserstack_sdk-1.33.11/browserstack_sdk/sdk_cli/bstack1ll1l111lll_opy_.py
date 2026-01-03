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
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1lllll11l1l_opy_,
    bstack1llll111lll_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l111l1l1_opy_, bstack11ll111l11_opy_
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_, bstack1lll111l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11llll1l_opy_ import bstack1ll1l1lllll_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1l1l11_opy_ import bstack1l1ll1l1ll1_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack1l1l1ll1_opy_ import bstack11l11lll1l_opy_, bstack11ll11111_opy_, bstack1l11l111l1_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1lll11l1l1l_opy_(bstack1l1ll1l1ll1_opy_):
    bstack1l11l1lll11_opy_ = bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡩࡸࡩࡷࡧࡵࡷࠧ፷")
    bstack1l1l11lllll_opy_ = bstack1l1l_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨ፸")
    bstack1l11l1llll1_opy_ = bstack1l1l_opy_ (u"ࠣࡰࡲࡲࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥ፹")
    bstack1l11l1l1lll_opy_ = bstack1l1l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤ፺")
    bstack1l11ll11111_opy_ = bstack1l1l_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡡࡵࡩ࡫ࡹࠢ፻")
    bstack1l1l111ll1l_opy_ = bstack1l1l_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡦࡶࡪࡧࡴࡦࡦࠥ፼")
    bstack1l11l1ll111_opy_ = bstack1l1l_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡲࡦࡳࡥࠣ፽")
    bstack1l11ll11l11_opy_ = bstack1l1l_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡸࡺࡡࡵࡷࡶࠦ፾")
    def __init__(self):
        super().__init__(bstack1l1ll1l111l_opy_=self.bstack1l11l1lll11_opy_, frameworks=[bstack1ll1lll1lll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.BEFORE_EACH, bstack1ll1ll111l1_opy_.POST), self.bstack1l11l1lll1l_opy_)
        if bstack11ll111l11_opy_():
            TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), self.bstack1ll11111l11_opy_)
        else:
            TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.PRE), self.bstack1ll11111l11_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), self.bstack1ll111l1111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1lll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11ll1l111_opy_ = self.bstack1l11ll111l1_opy_(instance.context)
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡴࡧࡷࡣࡦࡩࡴࡪࡸࡨࡣࡵࡧࡧࡦ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧ፿") + str(bstack1llll1llll1_opy_) + bstack1l1l_opy_ (u"ࠣࠤᎀ"))
            return
        f.bstack1llll1lll11_opy_(instance, bstack1lll11l1l1l_opy_.bstack1l1l11lllll_opy_, bstack1l11ll1l111_opy_)
    def bstack1l11ll111l1_opy_(self, context: bstack1llll111lll_opy_, bstack1l11ll1111l_opy_= True):
        if bstack1l11ll1111l_opy_:
            bstack1l11ll1l111_opy_ = self.bstack1l1ll1l1111_opy_(context, reverse=True)
        else:
            bstack1l11ll1l111_opy_ = self.bstack1l1ll1lll1l_opy_(context, reverse=True)
        return [f for f in bstack1l11ll1l111_opy_ if f[1].state != bstack1llll11ll11_opy_.QUIT]
    def bstack1ll11111l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lll1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        if not bstack1l1l111l1l1_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎁ") + str(kwargs) + bstack1l1l_opy_ (u"ࠥࠦᎂ"))
            return
        bstack1l11ll1l111_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1lll11l1l1l_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᎃ") + str(kwargs) + bstack1l1l_opy_ (u"ࠧࠨᎄ"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(
                bstack1lll1l111ll_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᎅ"))
        bstack1l11l1lllll_opy_, bstack1l1l111111l_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11l1lllll_opy_()
        if not page:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᎆ") + str(kwargs) + bstack1l1l_opy_ (u"ࠣࠤᎇ"))
            return
        bstack1l1l1l11_opy_ = getattr(args[0], bstack1l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᎈ"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠣᎉ")).get(bstack1l1l_opy_ (u"ࠦࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨᎊ")):
            try:
                page.evaluate(bstack1l1l_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨᎋ"),
                            bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪᎌ") + json.dumps(
                                bstack1l1l1l11_opy_) + bstack1l1l_opy_ (u"ࠢࡾࡿࠥᎍ"))
            except Exception as e:
                self.logger.debug(bstack1l1l_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨᎎ"), e)
    def bstack1ll111l1111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lll1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        if not bstack1l1l111l1l1_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎏ") + str(kwargs) + bstack1l1l_opy_ (u"ࠥࠦ᎐"))
            return
        bstack1l11ll1l111_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1lll11l1l1l_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ᎑") + str(kwargs) + bstack1l1l_opy_ (u"ࠧࠨ᎒"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(
                bstack1lll1l111ll_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣ᎓"))
        bstack1l11l1lllll_opy_, bstack1l1l111111l_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11l1lllll_opy_()
        if not page:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ᎔") + str(kwargs) + bstack1l1l_opy_ (u"ࠣࠤ᎕"))
            return
        status = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l11ll11lll_opy_, None)
        if not status:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧ᎖") + str(bstack1llll1llll1_opy_) + bstack1l1l_opy_ (u"ࠥࠦ᎗"))
            return
        bstack1l11ll11ll1_opy_ = {bstack1l1l_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦ᎘"): status.lower()}
        bstack1l11ll111ll_opy_ = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l11l1ll1l1_opy_, None)
        if status.lower() == bstack1l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ᎙") and bstack1l11ll111ll_opy_ is not None:
            bstack1l11ll11ll1_opy_[bstack1l1l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭᎚")] = bstack1l11ll111ll_opy_[0][bstack1l1l_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪ᎛")][0] if isinstance(bstack1l11ll111ll_opy_, list) else str(bstack1l11ll111ll_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨ᎜")).get(bstack1l1l_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨ᎝")):
            try:
                page.evaluate(
                        bstack1l1l_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ᎞"),
                        bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࠩ᎟")
                        + json.dumps(bstack1l11ll11ll1_opy_)
                        + bstack1l1l_opy_ (u"ࠧࢃࠢᎠ")
                    )
            except Exception as e:
                self.logger.debug(bstack1l1l_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣࡿࢂࠨᎡ"), e)
    def bstack1l1ll111ll1_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lll1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        if not bstack1l1l111l1l1_opy_:
            self.logger.debug(
                bstack1lll1l111ll_opy_ (u"ࠢ࡮ࡣࡵ࡯ࡤࡵ࠱࠲ࡻࡢࡷࡾࡴࡣ࠻ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᎢ"))
            return
        bstack1l11ll1l111_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1lll11l1l1l_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎣ") + str(kwargs) + bstack1l1l_opy_ (u"ࠤࠥᎤ"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(
                bstack1lll1l111ll_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࢁ࡬ࡦࡰࠫࡴࡦ࡭ࡥࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࡿࡰࡽࡡࡳࡩࡶࢁࠧᎥ"))
        bstack1l11l1lllll_opy_, bstack1l1l111111l_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11l1lllll_opy_()
        if not page:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡲࡧࡲ࡬ࡡࡲ࠵࠶ࡿ࡟ࡴࡻࡱࡧ࠿ࠦ࡮ࡰࠢࡳࡥ࡬࡫ࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎦ") + str(kwargs) + bstack1l1l_opy_ (u"ࠧࠨᎧ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack1l1l_opy_ (u"ࠨࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࡙ࡹ࡯ࡥ࠽ࠦᎨ") + str(timestamp)
        try:
            page.evaluate(
                bstack1l1l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣᎩ"),
                bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭Ꭺ").format(
                    json.dumps(
                        {
                            bstack1l1l_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤᎫ"): bstack1l1l_opy_ (u"ࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧᎬ"),
                            bstack1l1l_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢᎭ"): {
                                bstack1l1l_opy_ (u"ࠧࡺࡹࡱࡧࠥᎮ"): bstack1l1l_opy_ (u"ࠨࡁ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠥᎯ"),
                                bstack1l1l_opy_ (u"ࠢࡥࡣࡷࡥࠧᎰ"): data,
                                bstack1l1l_opy_ (u"ࠣ࡮ࡨࡺࡪࡲࠢᎱ"): bstack1l1l_opy_ (u"ࠤࡧࡩࡧࡻࡧࠣᎲ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦ࡯࠲࠳ࡼࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡾࢁࠧᎳ"), e)
    def bstack1l1l111l11l_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lll1l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        if f.bstack1llll1l11ll_opy_(instance, bstack1lll11l1l1l_opy_.bstack1l1l111ll1l_opy_, False):
            return
        self.bstack1ll11l1ll11_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1llllll1l_opy_)
        req.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l11lll_opy_)
        req.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1l11l11ll_opy_)
        req.test_framework_state = bstack1llll1llll1_opy_[0].name
        req.test_hook_state = bstack1llll1llll1_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
        for bstack1l11l1ll11l_opy_ in bstack1ll1l1lllll_opy_.bstack1llll111l11_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack1l1l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠥᎴ")
                if bstack1l1l111l1l1_opy_
                else bstack1l1l_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠦᎵ")
            )
            session.ref = bstack1l11l1ll11l_opy_.ref()
            session.hub_url = bstack1ll1l1lllll_opy_.bstack1llll1l11ll_opy_(bstack1l11l1ll11l_opy_, bstack1ll1l1lllll_opy_.bstack1l11lll1111_opy_, bstack1l1l_opy_ (u"ࠨࠢᎶ"))
            session.framework_name = bstack1l11l1ll11l_opy_.framework_name
            session.framework_version = bstack1l11l1ll11l_opy_.framework_version
            session.framework_session_id = bstack1ll1l1lllll_opy_.bstack1llll1l11ll_opy_(bstack1l11l1ll11l_opy_, bstack1ll1l1lllll_opy_.bstack1l11lll1l11_opy_, bstack1l1l_opy_ (u"ࠢࠣᎷ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11l1l11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs
    ):
        bstack1l11ll1l111_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1lll11l1l1l_opy_.bstack1l1l11lllll_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᎸ") + str(kwargs) + bstack1l1l_opy_ (u"ࠤࠥᎹ"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࢁ࡬ࡦࡰࠫࡴࡦ࡭ࡥࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎺ") + str(kwargs) + bstack1l1l_opy_ (u"ࠦࠧᎻ"))
        bstack1l11l1lllll_opy_, bstack1l1l111111l_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11l1lllll_opy_()
        if not page:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡴࡦ࡭ࡥࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎼ") + str(kwargs) + bstack1l1l_opy_ (u"ࠨࠢᎽ"))
            return
        return page
    def bstack1l1llll1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l11ll11l1l_opy_ = {}
        for bstack1l11l1ll11l_opy_ in bstack1ll1l1lllll_opy_.bstack1llll111l11_opy_.values():
            caps = bstack1ll1l1lllll_opy_.bstack1llll1l11ll_opy_(bstack1l11l1ll11l_opy_, bstack1ll1l1lllll_opy_.bstack1l11llll1ll_opy_, bstack1l1l_opy_ (u"ࠢࠣᎾ"))
        bstack1l11ll11l1l_opy_[bstack1l1l_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪࠨᎿ")] = caps.get(bstack1l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࠥᏀ"), bstack1l1l_opy_ (u"ࠥࠦᏁ"))
        bstack1l11ll11l1l_opy_[bstack1l1l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥᏂ")] = caps.get(bstack1l1l_opy_ (u"ࠧࡵࡳࠣᏃ"), bstack1l1l_opy_ (u"ࠨࠢᏄ"))
        bstack1l11ll11l1l_opy_[bstack1l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤᏅ")] = caps.get(bstack1l1l_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧᏆ"), bstack1l1l_opy_ (u"ࠤࠥᏇ"))
        bstack1l11ll11l1l_opy_[bstack1l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦᏈ")] = caps.get(bstack1l1l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨᏉ"), bstack1l1l_opy_ (u"ࠧࠨᏊ"))
        return bstack1l11ll11l1l_opy_
    def bstack1ll1111111l_opy_(self, page: object, bstack1ll111111l1_opy_, args={}):
        try:
            bstack1l11l1ll1ll_opy_ = bstack1l1l_opy_ (u"ࠨࠢࠣࠪࡩࡹࡳࡩࡴࡪࡱࡱࠤ࠭࠴࠮࠯ࡤࡶࡸࡦࡩ࡫ࡔࡦ࡮ࡅࡷ࡭ࡳࠪࠢࡾࡿࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡳࡧࡷࡹࡷࡴࠠ࡯ࡧࡺࠤࡕࡸ࡯࡮࡫ࡶࡩ࠭࠮ࡲࡦࡵࡲࡰࡻ࡫ࠬࠡࡴࡨ࡮ࡪࡩࡴࠪࠢࡀࡂࠥࢁࡻࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡣࡵࡷࡥࡨࡱࡓࡥ࡭ࡄࡶ࡬ࡹ࠮ࡱࡷࡶ࡬࠭ࡸࡥࡴࡱ࡯ࡺࡪ࠯࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡼࡨࡱࡣࡧࡵࡤࡺࡿࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࡽࠪ࠽ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࢀ࠭࠭ࢁࡡࡳࡩࡢ࡮ࡸࡵ࡮ࡾࠫࠥࠦࠧᏋ")
            bstack1ll111111l1_opy_ = bstack1ll111111l1_opy_.replace(bstack1l1l_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᏌ"), bstack1l1l_opy_ (u"ࠣࡤࡶࡸࡦࡩ࡫ࡔࡦ࡮ࡅࡷ࡭ࡳࠣᏍ"))
            script = bstack1l11l1ll1ll_opy_.format(fn_body=bstack1ll111111l1_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠤࡤ࠵࠶ࡿ࡟ࡴࡥࡵ࡭ࡵࡺ࡟ࡦࡺࡨࡧࡺࡺࡥ࠻ࠢࡈࡶࡷࡵࡲࠡࡧࡻࡩࡨࡻࡴࡪࡰࡪࠤࡹ࡮ࡥࠡࡣ࠴࠵ࡾࠦࡳࡤࡴ࡬ࡴࡹ࠲ࠠࠣᏎ") + str(e) + bstack1l1l_opy_ (u"ࠥࠦᏏ"))