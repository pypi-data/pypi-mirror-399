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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1llll1ll1l1_opy_,
    bstack1llll111l1l_opy_,
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1ll1ll11ll1_opy_(bstack1llll1ll1l1_opy_):
    bstack1l111l1llll_opy_ = bstack11111l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝ࠨᑳ")
    bstack1l11lllll11_opy_ = bstack11111l_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᑴ")
    bstack1l11llll111_opy_ = bstack11111l_opy_ (u"ࠣࡪࡸࡦࡤࡻࡲ࡭ࠤᑵ")
    bstack1l11llll11l_opy_ = bstack11111l_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᑶ")
    bstack1l111l1ll1l_opy_ = bstack11111l_opy_ (u"ࠥࡻ࠸ࡩࡥࡹࡧࡦࡹࡹ࡫ࡳࡤࡴ࡬ࡴࡹࠨᑷ")
    bstack1l111l11lll_opy_ = bstack11111l_opy_ (u"ࠦࡼ࠹ࡣࡦࡺࡨࡧࡺࡺࡥࡴࡥࡵ࡭ࡵࡺࡡࡴࡻࡱࡧࠧᑸ")
    NAME = bstack11111l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᑹ")
    bstack1l111l1lll1_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll11ll111_opy_: Any
    bstack1l111l1l11l_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack11111l_opy_ (u"ࠨ࡬ࡢࡷࡱࡧ࡭ࠨᑺ"), bstack11111l_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࠣᑻ"), bstack11111l_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥᑼ"), bstack11111l_opy_ (u"ࠤࡦࡰࡴࡹࡥࠣᑽ"), bstack11111l_opy_ (u"ࠥࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠧᑾ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack1llll11llll_opy_(methods)
    def bstack1llll11lll1_opy_(self, instance: bstack1llll111l1l_opy_, method_name: str, bstack1llll1llll1_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1llll11l111_opy_(
        self,
        target: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1llll11l11l_opy_, bstack1l111l1ll11_opy_ = bstack1llll1lll1l_opy_
        bstack1l111l1l1l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_)
        if bstack1l111l1l1l1_opy_ in bstack1ll1ll11ll1_opy_.bstack1l111l1lll1_opy_:
            bstack1l111l11ll1_opy_ = None
            for callback in bstack1ll1ll11ll1_opy_.bstack1l111l1lll1_opy_[bstack1l111l1l1l1_opy_]:
                try:
                    bstack1l111l1l111_opy_ = callback(self, target, exec, bstack1llll1lll1l_opy_, result, *args, **kwargs)
                    if bstack1l111l11ll1_opy_ == None:
                        bstack1l111l11ll1_opy_ = bstack1l111l1l111_opy_
                except Exception as e:
                    self.logger.error(bstack11111l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠣ࡭ࡳࡼ࡯࡬࡫ࡱ࡫ࠥࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࠤᑿ") + str(e) + bstack11111l_opy_ (u"ࠧࠨᒀ"))
                    traceback.print_exc()
            if bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.PRE and callable(bstack1l111l11ll1_opy_):
                return bstack1l111l11ll1_opy_
            elif bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.POST and bstack1l111l11ll1_opy_:
                return bstack1l111l11ll1_opy_
    def bstack1llll1111ll_opy_(
        self, method_name, previous_state: bstack1lllll11111_opy_, *args, **kwargs
    ) -> bstack1lllll11111_opy_:
        if method_name == bstack11111l_opy_ (u"࠭࡬ࡢࡷࡱࡧ࡭࠭ᒁ") or method_name == bstack11111l_opy_ (u"ࠧࡤࡱࡱࡲࡪࡩࡴࠨᒂ") or method_name == bstack11111l_opy_ (u"ࠨࡰࡨࡻࡤࡶࡡࡨࡧࠪᒃ"):
            return bstack1lllll11111_opy_.bstack1llll111lll_opy_
        if method_name == bstack11111l_opy_ (u"ࠩࡧ࡭ࡸࡶࡡࡵࡥ࡫ࠫᒄ"):
            return bstack1lllll11111_opy_.bstack1llll1l111l_opy_
        if method_name == bstack11111l_opy_ (u"ࠪࡧࡱࡵࡳࡦࠩᒅ"):
            return bstack1lllll11111_opy_.QUIT
        return bstack1lllll11111_opy_.NONE
    @staticmethod
    def bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_]):
        return bstack11111l_opy_ (u"ࠦ࠿ࠨᒆ").join((bstack1lllll11111_opy_(bstack1llll1lll1l_opy_[0]).name, bstack1llll1l1l1l_opy_(bstack1llll1lll1l_opy_[1]).name))
    @staticmethod
    def bstack1l1llllll1l_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_], callback: Callable):
        bstack1l111l1l1l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_)
        if not bstack1l111l1l1l1_opy_ in bstack1ll1ll11ll1_opy_.bstack1l111l1lll1_opy_:
            bstack1ll1ll11ll1_opy_.bstack1l111l1lll1_opy_[bstack1l111l1l1l1_opy_] = []
        bstack1ll1ll11ll1_opy_.bstack1l111l1lll1_opy_[bstack1l111l1l1l1_opy_].append(callback)
    @staticmethod
    def bstack1ll111ll11l_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1ll11l111ll_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1l1llll111l_opy_(instance: bstack1llll111l1l_opy_, default_value=None):
        return bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l11llll11l_opy_, default_value)
    @staticmethod
    def bstack1l1ll1l1l1l_opy_(instance: bstack1llll111l1l_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll1111ll11_opy_(instance: bstack1llll111l1l_opy_, default_value=None):
        return bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l11llll111_opy_, default_value)
    @staticmethod
    def bstack1ll11l11l11_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1llll1l11_opy_(method_name: str, *args):
        if not bstack1ll1ll11ll1_opy_.bstack1ll111ll11l_opy_(method_name):
            return False
        if not bstack1ll1ll11ll1_opy_.bstack1l111l1ll1l_opy_ in bstack1ll1ll11ll1_opy_.bstack1l11l1l111l_opy_(*args):
            return False
        bstack1l1lll11111_opy_ = bstack1ll1ll11ll1_opy_.bstack1l1lll1l1l1_opy_(*args)
        return bstack1l1lll11111_opy_ and bstack11111l_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᒇ") in bstack1l1lll11111_opy_ and bstack11111l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᒈ") in bstack1l1lll11111_opy_[bstack11111l_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᒉ")]
    @staticmethod
    def bstack1l1lll1lll1_opy_(method_name: str, *args):
        if not bstack1ll1ll11ll1_opy_.bstack1ll111ll11l_opy_(method_name):
            return False
        if not bstack1ll1ll11ll1_opy_.bstack1l111l1ll1l_opy_ in bstack1ll1ll11ll1_opy_.bstack1l11l1l111l_opy_(*args):
            return False
        bstack1l1lll11111_opy_ = bstack1ll1ll11ll1_opy_.bstack1l1lll1l1l1_opy_(*args)
        return (
            bstack1l1lll11111_opy_
            and bstack11111l_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᒊ") in bstack1l1lll11111_opy_
            and bstack11111l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡣࡳ࡫ࡳࡸࠧᒋ") in bstack1l1lll11111_opy_[bstack11111l_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᒌ")]
        )
    @staticmethod
    def bstack1l11l1l111l_opy_(*args):
        return str(bstack1ll1ll11ll1_opy_.bstack1ll11l11l11_opy_(*args)).lower()