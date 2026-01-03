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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll1ll1ll_opy_,
    bstack1lllll11l1l_opy_,
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1ll1l1lllll_opy_(bstack1llll1ll1ll_opy_):
    bstack1l111l1l11l_opy_ = bstack1l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝ࠨᑺ")
    bstack1l11lll1l11_opy_ = bstack1l1l_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᑻ")
    bstack1l11lll1111_opy_ = bstack1l1l_opy_ (u"ࠣࡪࡸࡦࡤࡻࡲ࡭ࠤᑼ")
    bstack1l11llll1ll_opy_ = bstack1l1l_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᑽ")
    bstack1l111l11ll1_opy_ = bstack1l1l_opy_ (u"ࠥࡻ࠸ࡩࡥࡹࡧࡦࡹࡹ࡫ࡳࡤࡴ࡬ࡴࡹࠨᑾ")
    bstack1l111l11l1l_opy_ = bstack1l1l_opy_ (u"ࠦࡼ࠹ࡣࡦࡺࡨࡧࡺࡺࡥࡴࡥࡵ࡭ࡵࡺࡡࡴࡻࡱࡧࠧᑿ")
    NAME = bstack1l1l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᒀ")
    bstack1l111l11l11_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll1ll1l1l_opy_: Any
    bstack1l111l1ll1l_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack1l1l_opy_ (u"ࠨ࡬ࡢࡷࡱࡧ࡭ࠨᒁ"), bstack1l1l_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࠣᒂ"), bstack1l1l_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥᒃ"), bstack1l1l_opy_ (u"ࠤࡦࡰࡴࡹࡥࠣᒄ"), bstack1l1l_opy_ (u"ࠥࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠧᒅ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack1llll1l1lll_opy_(methods)
    def bstack1llll1lll1l_opy_(self, instance: bstack1lllll11l1l_opy_, method_name: str, bstack1lllll111l1_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1llll1lllll_opy_(
        self,
        target: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1llll11l11l_opy_, bstack1l111l1l1l1_opy_ = bstack1llll1llll1_opy_
        bstack1l111l1l111_opy_ = bstack1ll1l1lllll_opy_.bstack1l111l11lll_opy_(bstack1llll1llll1_opy_)
        if bstack1l111l1l111_opy_ in bstack1ll1l1lllll_opy_.bstack1l111l11l11_opy_:
            bstack1l111l1ll11_opy_ = None
            for callback in bstack1ll1l1lllll_opy_.bstack1l111l11l11_opy_[bstack1l111l1l111_opy_]:
                try:
                    bstack1l111l1l1ll_opy_ = callback(self, target, exec, bstack1llll1llll1_opy_, result, *args, **kwargs)
                    if bstack1l111l1ll11_opy_ == None:
                        bstack1l111l1ll11_opy_ = bstack1l111l1l1ll_opy_
                except Exception as e:
                    self.logger.error(bstack1l1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠣ࡭ࡳࡼ࡯࡬࡫ࡱ࡫ࠥࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࠤᒆ") + str(e) + bstack1l1l_opy_ (u"ࠧࠨᒇ"))
                    traceback.print_exc()
            if bstack1l111l1l1l1_opy_ == bstack1llll1ll111_opy_.PRE and callable(bstack1l111l1ll11_opy_):
                return bstack1l111l1ll11_opy_
            elif bstack1l111l1l1l1_opy_ == bstack1llll1ll111_opy_.POST and bstack1l111l1ll11_opy_:
                return bstack1l111l1ll11_opy_
    def bstack1lllll1111l_opy_(
        self, method_name, previous_state: bstack1llll11ll11_opy_, *args, **kwargs
    ) -> bstack1llll11ll11_opy_:
        if method_name == bstack1l1l_opy_ (u"࠭࡬ࡢࡷࡱࡧ࡭࠭ᒈ") or method_name == bstack1l1l_opy_ (u"ࠧࡤࡱࡱࡲࡪࡩࡴࠨᒉ") or method_name == bstack1l1l_opy_ (u"ࠨࡰࡨࡻࡤࡶࡡࡨࡧࠪᒊ"):
            return bstack1llll11ll11_opy_.bstack1lll1lll1ll_opy_
        if method_name == bstack1l1l_opy_ (u"ࠩࡧ࡭ࡸࡶࡡࡵࡥ࡫ࠫᒋ"):
            return bstack1llll11ll11_opy_.bstack1llll1l1l1l_opy_
        if method_name == bstack1l1l_opy_ (u"ࠪࡧࡱࡵࡳࡦࠩᒌ"):
            return bstack1llll11ll11_opy_.QUIT
        return bstack1llll11ll11_opy_.NONE
    @staticmethod
    def bstack1l111l11lll_opy_(bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_]):
        return bstack1l1l_opy_ (u"ࠦ࠿ࠨᒍ").join((bstack1llll11ll11_opy_(bstack1llll1llll1_opy_[0]).name, bstack1llll1ll111_opy_(bstack1llll1llll1_opy_[1]).name))
    @staticmethod
    def bstack1l1lllllll1_opy_(bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_], callback: Callable):
        bstack1l111l1l111_opy_ = bstack1ll1l1lllll_opy_.bstack1l111l11lll_opy_(bstack1llll1llll1_opy_)
        if not bstack1l111l1l111_opy_ in bstack1ll1l1lllll_opy_.bstack1l111l11l11_opy_:
            bstack1ll1l1lllll_opy_.bstack1l111l11l11_opy_[bstack1l111l1l111_opy_] = []
        bstack1ll1l1lllll_opy_.bstack1l111l11l11_opy_[bstack1l111l1l111_opy_].append(callback)
    @staticmethod
    def bstack1l1lll1l1l1_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1ll11l11111_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1ll111l1ll1_opy_(instance: bstack1lllll11l1l_opy_, default_value=None):
        return bstack1llll1ll1ll_opy_.bstack1llll1l11ll_opy_(instance, bstack1ll1l1lllll_opy_.bstack1l11llll1ll_opy_, default_value)
    @staticmethod
    def bstack1l1ll1l11l1_opy_(instance: bstack1lllll11l1l_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll111l1lll_opy_(instance: bstack1lllll11l1l_opy_, default_value=None):
        return bstack1llll1ll1ll_opy_.bstack1llll1l11ll_opy_(instance, bstack1ll1l1lllll_opy_.bstack1l11lll1111_opy_, default_value)
    @staticmethod
    def bstack1ll111ll111_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1llll1111_opy_(method_name: str, *args):
        if not bstack1ll1l1lllll_opy_.bstack1l1lll1l1l1_opy_(method_name):
            return False
        if not bstack1ll1l1lllll_opy_.bstack1l111l11ll1_opy_ in bstack1ll1l1lllll_opy_.bstack1l111llll1l_opy_(*args):
            return False
        bstack1l1lll11lll_opy_ = bstack1ll1l1lllll_opy_.bstack1l1ll1llll1_opy_(*args)
        return bstack1l1lll11lll_opy_ and bstack1l1l_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᒎ") in bstack1l1lll11lll_opy_ and bstack1l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᒏ") in bstack1l1lll11lll_opy_[bstack1l1l_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᒐ")]
    @staticmethod
    def bstack1ll111lll1l_opy_(method_name: str, *args):
        if not bstack1ll1l1lllll_opy_.bstack1l1lll1l1l1_opy_(method_name):
            return False
        if not bstack1ll1l1lllll_opy_.bstack1l111l11ll1_opy_ in bstack1ll1l1lllll_opy_.bstack1l111llll1l_opy_(*args):
            return False
        bstack1l1lll11lll_opy_ = bstack1ll1l1lllll_opy_.bstack1l1ll1llll1_opy_(*args)
        return (
            bstack1l1lll11lll_opy_
            and bstack1l1l_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᒑ") in bstack1l1lll11lll_opy_
            and bstack1l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡣࡳ࡫ࡳࡸࠧᒒ") in bstack1l1lll11lll_opy_[bstack1l1l_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᒓ")]
        )
    @staticmethod
    def bstack1l111llll1l_opy_(*args):
        return str(bstack1ll1l1lllll_opy_.bstack1ll111ll111_opy_(*args)).lower()