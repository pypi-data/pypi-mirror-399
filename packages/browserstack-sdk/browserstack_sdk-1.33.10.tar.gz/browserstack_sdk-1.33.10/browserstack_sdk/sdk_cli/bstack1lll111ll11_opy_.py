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
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
    bstack1llll111l1l_opy_,
    bstack1lllll1l111_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1ll11lll1_opy_, bstack1l1ll1111l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_, bstack1lll1ll1ll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1llll11l_opy_ import bstack1ll1ll11ll1_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1ll11l_opy_ import bstack1l1ll1l1ll1_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack1l11llll_opy_ import bstack1l1111ll11_opy_, bstack1l1111l1l1_opy_, bstack11l11111l_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1lll11111ll_opy_(bstack1l1ll1l1ll1_opy_):
    bstack1l11l1ll1ll_opy_ = bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡩࡸࡩࡷࡧࡵࡷࠧ፰")
    bstack1l1l1l1ll1l_opy_ = bstack11111l_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨ፱")
    bstack1l11ll1l11l_opy_ = bstack11111l_opy_ (u"ࠣࡰࡲࡲࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥ፲")
    bstack1l11ll111ll_opy_ = bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤ፳")
    bstack1l11l1ll11l_opy_ = bstack11111l_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡡࡵࡩ࡫ࡹࠢ፴")
    bstack1l1l11ll111_opy_ = bstack11111l_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡦࡶࡪࡧࡴࡦࡦࠥ፵")
    bstack1l11ll1111l_opy_ = bstack11111l_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡲࡦࡳࡥࠣ፶")
    bstack1l11ll1l1l1_opy_ = bstack11111l_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡸࡺࡡࡵࡷࡶࠦ፷")
    def __init__(self):
        super().__init__(bstack1l1ll1l11ll_opy_=self.bstack1l11l1ll1ll_opy_, frameworks=[bstack1lll1l11111_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.BEFORE_EACH, bstack1lll1ll1111_opy_.POST), self.bstack1l11ll11l1l_opy_)
        if bstack1l1ll1111l_opy_():
            TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST), self.bstack1l1lll1llll_opy_)
        else:
            TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.PRE), self.bstack1l1lll1llll_opy_)
        TestFramework.bstack1l1llllll1l_opy_((bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST), self.bstack1ll11l11l1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11ll11l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11ll11111_opy_ = self.bstack1l11l1lll11_opy_(instance.context)
        if not bstack1l11ll11111_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡴࡧࡷࡣࡦࡩࡴࡪࡸࡨࡣࡵࡧࡧࡦ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧ፸") + str(bstack1llll1lll1l_opy_) + bstack11111l_opy_ (u"ࠣࠤ፹"))
            return
        f.bstack1llll1l1lll_opy_(instance, bstack1lll11111ll_opy_.bstack1l1l1l1ll1l_opy_, bstack1l11ll11111_opy_)
    def bstack1l11l1lll11_opy_(self, context: bstack1lllll1l111_opy_, bstack1l11l1llll1_opy_= True):
        if bstack1l11l1llll1_opy_:
            bstack1l11ll11111_opy_ = self.bstack1l1ll1ll1ll_opy_(context, reverse=True)
        else:
            bstack1l11ll11111_opy_ = self.bstack1l1ll1ll111_opy_(context, reverse=True)
        return [f for f in bstack1l11ll11111_opy_ if f[1].state != bstack1lllll11111_opy_.QUIT]
    def bstack1l1lll1llll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll11l1l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not bstack1l1ll11lll1_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧ፺") + str(kwargs) + bstack11111l_opy_ (u"ࠥࠦ፻"))
            return
        bstack1l11ll11111_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1lll11111ll_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l11ll11111_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ፼") + str(kwargs) + bstack11111l_opy_ (u"ࠧࠨ፽"))
            return
        if len(bstack1l11ll11111_opy_) > 1:
            self.logger.debug(
                bstack1ll1lll1l1l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣ፾"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l1l_opy_ = bstack1l11ll11111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ፿") + str(kwargs) + bstack11111l_opy_ (u"ࠣࠤᎀ"))
            return
        bstack1l1l1ll11l_opy_ = getattr(args[0], bstack11111l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᎁ"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠣᎂ")).get(bstack11111l_opy_ (u"ࠦࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨᎃ")):
            try:
                page.evaluate(bstack11111l_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨᎄ"),
                            bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪᎅ") + json.dumps(
                                bstack1l1l1ll11l_opy_) + bstack11111l_opy_ (u"ࠢࡾࡿࠥᎆ"))
            except Exception as e:
                self.logger.debug(bstack11111l_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨᎇ"), e)
    def bstack1ll11l11l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll11l1l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not bstack1l1ll11lll1_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎈ") + str(kwargs) + bstack11111l_opy_ (u"ࠥࠦᎉ"))
            return
        bstack1l11ll11111_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1lll11111ll_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l11ll11111_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᎊ") + str(kwargs) + bstack11111l_opy_ (u"ࠧࠨᎋ"))
            return
        if len(bstack1l11ll11111_opy_) > 1:
            self.logger.debug(
                bstack1ll1lll1l1l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᎌ"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l1l_opy_ = bstack1l11ll11111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack11111l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᎍ") + str(kwargs) + bstack11111l_opy_ (u"ࠣࠤᎎ"))
            return
        status = f.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l11l1ll1l1_opy_, None)
        if not status:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᎏ") + str(bstack1llll1lll1l_opy_) + bstack11111l_opy_ (u"ࠥࠦ᎐"))
            return
        bstack1l11l1lll1l_opy_ = {bstack11111l_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦ᎑"): status.lower()}
        bstack1l11ll1l111_opy_ = f.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l11ll11lll_opy_, None)
        if status.lower() == bstack11111l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ᎒") and bstack1l11ll1l111_opy_ is not None:
            bstack1l11l1lll1l_opy_[bstack11111l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭᎓")] = bstack1l11ll1l111_opy_[0][bstack11111l_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪ᎔")][0] if isinstance(bstack1l11ll1l111_opy_, list) else str(bstack1l11ll1l111_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨ᎕")).get(bstack11111l_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨ᎖")):
            try:
                page.evaluate(
                        bstack11111l_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ᎗"),
                        bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࠩ᎘")
                        + json.dumps(bstack1l11l1lll1l_opy_)
                        + bstack11111l_opy_ (u"ࠧࢃࠢ᎙")
                    )
            except Exception as e:
                self.logger.debug(bstack11111l_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣࡿࢂࠨ᎚"), e)
    def bstack1l1l11l111l_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll11l1l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if not bstack1l1ll11lll1_opy_:
            self.logger.debug(
                bstack1ll1lll1l1l_opy_ (u"ࠢ࡮ࡣࡵ࡯ࡤࡵ࠱࠲ࡻࡢࡷࡾࡴࡣ࠻ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣ᎛"))
            return
        bstack1l11ll11111_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1lll11111ll_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l11ll11111_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦ᎜") + str(kwargs) + bstack11111l_opy_ (u"ࠤࠥ᎝"))
            return
        if len(bstack1l11ll11111_opy_) > 1:
            self.logger.debug(
                bstack1ll1lll1l1l_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࢁ࡬ࡦࡰࠫࡴࡦ࡭ࡥࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࡿࡰࡽࡡࡳࡩࡶࢁࠧ᎞"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l1l_opy_ = bstack1l11ll11111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack11111l_opy_ (u"ࠦࡲࡧࡲ࡬ࡡࡲ࠵࠶ࡿ࡟ࡴࡻࡱࡧ࠿ࠦ࡮ࡰࠢࡳࡥ࡬࡫ࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦ᎟") + str(kwargs) + bstack11111l_opy_ (u"ࠧࠨᎠ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack11111l_opy_ (u"ࠨࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࡙ࡹ࡯ࡥ࠽ࠦᎡ") + str(timestamp)
        try:
            page.evaluate(
                bstack11111l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣᎢ"),
                bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭Ꭳ").format(
                    json.dumps(
                        {
                            bstack11111l_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤᎤ"): bstack11111l_opy_ (u"ࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧᎥ"),
                            bstack11111l_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢᎦ"): {
                                bstack11111l_opy_ (u"ࠧࡺࡹࡱࡧࠥᎧ"): bstack11111l_opy_ (u"ࠨࡁ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠥᎨ"),
                                bstack11111l_opy_ (u"ࠢࡥࡣࡷࡥࠧᎩ"): data,
                                bstack11111l_opy_ (u"ࠣ࡮ࡨࡺࡪࡲࠢᎪ"): bstack11111l_opy_ (u"ࠤࡧࡩࡧࡻࡧࠣᎫ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦ࡯࠲࠳ࡼࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡾࢁࠧᎬ"), e)
    def bstack1l1ll11111l_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        f: TestFramework,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11ll11l1l_opy_(f, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
        if f.bstack1llll111ll1_opy_(instance, bstack1lll11111ll_opy_.bstack1l1l11ll111_opy_, False):
            return
        self.bstack1l1lll1l1ll_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1ll111ll111_opy_)
        req.test_framework_name = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1lllllll1_opy_)
        req.test_framework_version = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1l1l111llll_opy_)
        req.test_framework_state = bstack1llll1lll1l_opy_[0].name
        req.test_hook_state = bstack1llll1lll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll111ll1_opy_(instance, TestFramework.bstack1ll11111l11_opy_)
        for bstack1l11l1lllll_opy_ in bstack1ll1ll11ll1_opy_.bstack1lll1llllll_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack11111l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠥᎭ")
                if bstack1l1ll11lll1_opy_
                else bstack11111l_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠦᎮ")
            )
            session.ref = bstack1l11l1lllll_opy_.ref()
            session.hub_url = bstack1ll1ll11ll1_opy_.bstack1llll111ll1_opy_(bstack1l11l1lllll_opy_, bstack1ll1ll11ll1_opy_.bstack1l11llll111_opy_, bstack11111l_opy_ (u"ࠨࠢᎯ"))
            session.framework_name = bstack1l11l1lllll_opy_.framework_name
            session.framework_version = bstack1l11l1lllll_opy_.framework_version
            session.framework_session_id = bstack1ll1ll11ll1_opy_.bstack1llll111ll1_opy_(bstack1l11l1lllll_opy_, bstack1ll1ll11ll1_opy_.bstack1l11lllll11_opy_, bstack11111l_opy_ (u"ࠢࠣᎰ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11l1lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs
    ):
        bstack1l11ll11111_opy_ = f.bstack1llll111ll1_opy_(instance, bstack1lll11111ll_opy_.bstack1l1l1l1ll1l_opy_, [])
        if not bstack1l11ll11111_opy_:
            self.logger.debug(bstack11111l_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡲࡴࠦࡰࡢࡩࡨࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᎱ") + str(kwargs) + bstack11111l_opy_ (u"ࠤࠥᎲ"))
            return
        if len(bstack1l11ll11111_opy_) > 1:
            self.logger.debug(bstack11111l_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࢁ࡬ࡦࡰࠫࡴࡦ࡭ࡥࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎳ") + str(kwargs) + bstack11111l_opy_ (u"ࠦࠧᎴ"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l1l_opy_ = bstack1l11ll11111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack11111l_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡴࡦ࡭ࡥࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎵ") + str(kwargs) + bstack11111l_opy_ (u"ࠨࠢᎶ"))
            return
        return page
    def bstack1ll11111ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l11ll11l11_opy_ = {}
        for bstack1l11l1lllll_opy_ in bstack1ll1ll11ll1_opy_.bstack1lll1llllll_opy_.values():
            caps = bstack1ll1ll11ll1_opy_.bstack1llll111ll1_opy_(bstack1l11l1lllll_opy_, bstack1ll1ll11ll1_opy_.bstack1l11llll11l_opy_, bstack11111l_opy_ (u"ࠢࠣᎷ"))
        bstack1l11ll11l11_opy_[bstack11111l_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪࠨᎸ")] = caps.get(bstack11111l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࠥᎹ"), bstack11111l_opy_ (u"ࠥࠦᎺ"))
        bstack1l11ll11l11_opy_[bstack11111l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥᎻ")] = caps.get(bstack11111l_opy_ (u"ࠧࡵࡳࠣᎼ"), bstack11111l_opy_ (u"ࠨࠢᎽ"))
        bstack1l11ll11l11_opy_[bstack11111l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤᎾ")] = caps.get(bstack11111l_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧᎿ"), bstack11111l_opy_ (u"ࠤࠥᏀ"))
        bstack1l11ll11l11_opy_[bstack11111l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦᏁ")] = caps.get(bstack11111l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨᏂ"), bstack11111l_opy_ (u"ࠧࠨᏃ"))
        return bstack1l11ll11l11_opy_
    def bstack1l1llll1lll_opy_(self, page: object, bstack1l1llll1111_opy_, args={}):
        try:
            bstack1l11ll11ll1_opy_ = bstack11111l_opy_ (u"ࠨࠢࠣࠪࡩࡹࡳࡩࡴࡪࡱࡱࠤ࠭࠴࠮࠯ࡤࡶࡸࡦࡩ࡫ࡔࡦ࡮ࡅࡷ࡭ࡳࠪࠢࡾࡿࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡳࡧࡷࡹࡷࡴࠠ࡯ࡧࡺࠤࡕࡸ࡯࡮࡫ࡶࡩ࠭࠮ࡲࡦࡵࡲࡰࡻ࡫ࠬࠡࡴࡨ࡮ࡪࡩࡴࠪࠢࡀࡂࠥࢁࡻࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡣࡵࡷࡥࡨࡱࡓࡥ࡭ࡄࡶ࡬ࡹ࠮ࡱࡷࡶ࡬࠭ࡸࡥࡴࡱ࡯ࡺࡪ࠯࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡼࡨࡱࡣࡧࡵࡤࡺࡿࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࡽࠪ࠽ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࢀ࠭࠭ࢁࡡࡳࡩࡢ࡮ࡸࡵ࡮ࡾࠫࠥࠦࠧᏄ")
            bstack1l1llll1111_opy_ = bstack1l1llll1111_opy_.replace(bstack11111l_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᏅ"), bstack11111l_opy_ (u"ࠣࡤࡶࡸࡦࡩ࡫ࡔࡦ࡮ࡅࡷ࡭ࡳࠣᏆ"))
            script = bstack1l11ll11ll1_opy_.format(fn_body=bstack1l1llll1111_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack11111l_opy_ (u"ࠤࡤ࠵࠶ࡿ࡟ࡴࡥࡵ࡭ࡵࡺ࡟ࡦࡺࡨࡧࡺࡺࡥ࠻ࠢࡈࡶࡷࡵࡲࠡࡧࡻࡩࡨࡻࡴࡪࡰࡪࠤࡹ࡮ࡥࠡࡣ࠴࠵ࡾࠦࡳࡤࡴ࡬ࡴࡹ࠲ࠠࠣᏇ") + str(e) + bstack11111l_opy_ (u"ࠥࠦᏈ"))