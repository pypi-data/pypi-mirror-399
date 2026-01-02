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
from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
from bstack_utils.constants import EVENTS
class bstack1lll1l11111_opy_(bstack1llll1ll1l1_opy_):
    bstack1l111l1llll_opy_ = bstack11111l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠤᗛ")
    NAME = bstack11111l_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧᗜ")
    bstack1l11llll111_opy_ = bstack11111l_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࠧᗝ")
    bstack1l11lllll11_opy_ = bstack11111l_opy_ (u"ࠧ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠧᗞ")
    bstack11lll111lll_opy_ = bstack11111l_opy_ (u"ࠨࡩ࡯ࡲࡸࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᗟ")
    bstack1l11llll11l_opy_ = bstack11111l_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᗠ")
    bstack1l111lll1ll_opy_ = bstack11111l_opy_ (u"ࠣ࡫ࡶࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢ࡬ࡺࡨࠢᗡ")
    bstack11lll111ll1_opy_ = bstack11111l_opy_ (u"ࠤࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨᗢ")
    bstack11lll11l111_opy_ = bstack11111l_opy_ (u"ࠥࡩࡳࡪࡥࡥࡡࡤࡸࠧᗣ")
    bstack1ll111ll111_opy_ = bstack11111l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠧᗤ")
    bstack1l11l1l1lll_opy_ = bstack11111l_opy_ (u"ࠧࡴࡥࡸࡵࡨࡷࡸ࡯࡯࡯ࠤᗥ")
    bstack11lll111l1l_opy_ = bstack11111l_opy_ (u"ࠨࡧࡦࡶࠥᗦ")
    bstack1l1ll111lll_opy_ = bstack11111l_opy_ (u"ࠢࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠦᗧ")
    bstack1l111l1ll1l_opy_ = bstack11111l_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࠦᗨ")
    bstack1l111l11lll_opy_ = bstack11111l_opy_ (u"ࠤࡺ࠷ࡨ࡫ࡸࡦࡥࡸࡸࡪࡹࡣࡳ࡫ࡳࡸࡦࡹࡹ࡯ࡥࠥᗩ")
    bstack11lll11l1l1_opy_ = bstack11111l_opy_ (u"ࠥࡵࡺ࡯ࡴࠣᗪ")
    bstack11lll11ll1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1l11l111l11_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll11ll111_opy_: Any
    bstack1l111l1l11l_opy_: Dict
    def __init__(
        self,
        bstack1l11l111l11_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1lll11ll111_opy_: Dict[str, Any],
        methods=[bstack11111l_opy_ (u"ࠦࡤࡥࡩ࡯࡫ࡷࡣࡤࠨᗫ"), bstack11111l_opy_ (u"ࠧࡹࡴࡢࡴࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᗬ"), bstack11111l_opy_ (u"ࠨࡥࡹࡧࡦࡹࡹ࡫ࠢᗭ"), bstack11111l_opy_ (u"ࠢࡲࡷ࡬ࡸࠧᗮ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1l11l111l11_opy_ = bstack1l11l111l11_opy_
        self.platform_index = platform_index
        self.bstack1llll11llll_opy_(methods)
        self.bstack1lll11ll111_opy_ = bstack1lll11ll111_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1llll1ll1l1_opy_.get_data(bstack1lll1l11111_opy_.bstack1l11lllll11_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1llll1ll1l1_opy_.get_data(bstack1lll1l11111_opy_.bstack1l11llll111_opy_, target, strict)
    @staticmethod
    def bstack11lll111l11_opy_(target: object, strict=True):
        return bstack1llll1ll1l1_opy_.get_data(bstack1lll1l11111_opy_.bstack11lll111lll_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1llll1ll1l1_opy_.get_data(bstack1lll1l11111_opy_.bstack1l11llll11l_opy_, target, strict)
    @staticmethod
    def bstack1l1ll1l1l1l_opy_(instance: bstack1llll111l1l_opy_) -> bool:
        return bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1l111lll1ll_opy_, False)
    @staticmethod
    def bstack1ll1111ll11_opy_(instance: bstack1llll111l1l_opy_, default_value=None):
        return bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1l11llll111_opy_, default_value)
    @staticmethod
    def bstack1l1llll111l_opy_(instance: bstack1llll111l1l_opy_, default_value=None):
        return bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1l11llll11l_opy_, default_value)
    @staticmethod
    def bstack1l1lll111l1_opy_(hub_url: str, bstack11lll11l1ll_opy_=bstack11111l_opy_ (u"ࠣ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠧᗯ")):
        try:
            bstack11lll11l11l_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack11lll11l11l_opy_.endswith(bstack11lll11l1ll_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll111ll11l_opy_(method_name: str):
        return method_name == bstack11111l_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥᗰ")
    @staticmethod
    def bstack1ll11l111ll_opy_(method_name: str, *args):
        return (
            bstack1lll1l11111_opy_.bstack1ll111ll11l_opy_(method_name)
            and bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args) == bstack1lll1l11111_opy_.bstack1l11l1l1lll_opy_
        )
    @staticmethod
    def bstack1l1llll1l11_opy_(method_name: str, *args):
        if not bstack1lll1l11111_opy_.bstack1ll111ll11l_opy_(method_name):
            return False
        if not bstack1lll1l11111_opy_.bstack1l111l1ll1l_opy_ in bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args):
            return False
        bstack1l1lll11111_opy_ = bstack1lll1l11111_opy_.bstack1l1lll1l1l1_opy_(*args)
        return bstack1l1lll11111_opy_ and bstack11111l_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᗱ") in bstack1l1lll11111_opy_ and bstack11111l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᗲ") in bstack1l1lll11111_opy_[bstack11111l_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᗳ")]
    @staticmethod
    def bstack1l1lll1lll1_opy_(method_name: str, *args):
        if not bstack1lll1l11111_opy_.bstack1ll111ll11l_opy_(method_name):
            return False
        if not bstack1lll1l11111_opy_.bstack1l111l1ll1l_opy_ in bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args):
            return False
        bstack1l1lll11111_opy_ = bstack1lll1l11111_opy_.bstack1l1lll1l1l1_opy_(*args)
        return (
            bstack1l1lll11111_opy_
            and bstack11111l_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࠨᗴ") in bstack1l1lll11111_opy_
            and bstack11111l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡨࡸࡩࡱࡶࠥᗵ") in bstack1l1lll11111_opy_[bstack11111l_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᗶ")]
        )
    @staticmethod
    def bstack1l11l1l111l_opy_(*args):
        return str(bstack1lll1l11111_opy_.bstack1ll11l11l11_opy_(*args)).lower()
    @staticmethod
    def bstack1ll11l11l11_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1lll1l1l1_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack1ll1111lll_opy_(driver):
        command_executor = getattr(driver, bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᗷ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack11111l_opy_ (u"ࠥࡣࡺࡸ࡬ࠣᗸ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack11111l_opy_ (u"ࠦࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠧᗹ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack11111l_opy_ (u"ࠧࡸࡥ࡮ࡱࡷࡩࡤࡹࡥࡳࡸࡨࡶࡤࡧࡤࡥࡴࠥᗺ"), None)
        return hub_url
    def bstack1l11l1ll111_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack11111l_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᗻ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack11111l_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡠࡧࡻࡩࡨࡻࡴࡰࡴࠥᗼ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack11111l_opy_ (u"ࠣࡡࡸࡶࡱࠨᗽ")):
                setattr(command_executor, bstack11111l_opy_ (u"ࠤࡢࡹࡷࡲࠢᗾ"), hub_url)
                result = True
        if result:
            self.bstack1l11l111l11_opy_ = hub_url
            bstack1lll1l11111_opy_.bstack1llll1l1lll_opy_(instance, bstack1lll1l11111_opy_.bstack1l11llll111_opy_, hub_url)
            bstack1lll1l11111_opy_.bstack1llll1l1lll_opy_(
                instance, bstack1lll1l11111_opy_.bstack1l111lll1ll_opy_, bstack1lll1l11111_opy_.bstack1l1lll111l1_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_]):
        return bstack11111l_opy_ (u"ࠥ࠾ࠧᗿ").join((bstack1lllll11111_opy_(bstack1llll1lll1l_opy_[0]).name, bstack1llll1l1l1l_opy_(bstack1llll1lll1l_opy_[1]).name))
    @staticmethod
    def bstack1l1llllll1l_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_], callback: Callable):
        bstack1l111l1l1l1_opy_ = bstack1lll1l11111_opy_.bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_)
        if not bstack1l111l1l1l1_opy_ in bstack1lll1l11111_opy_.bstack11lll11ll1l_opy_:
            bstack1lll1l11111_opy_.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_] = []
        bstack1lll1l11111_opy_.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_].append(callback)
    def bstack1llll11lll1_opy_(self, instance: bstack1llll111l1l_opy_, method_name: str, bstack1llll1llll1_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack11111l_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࠦᘀ")):
            return
        cmd = args[0] if method_name == bstack11111l_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨᘁ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack11lll11ll11_opy_ = bstack11111l_opy_ (u"ࠨ࠺ࠣᘂ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠢࡥࡴ࡬ࡺࡪࡸ࠺ࠣᘃ") + bstack11lll11ll11_opy_, bstack1llll1llll1_opy_)
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
        bstack1l111l1l1l1_opy_ = bstack1lll1l11111_opy_.bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_)
        self.logger.debug(bstack11111l_opy_ (u"ࠣࡱࡱࡣ࡭ࡵ࡯࡬࠼ࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᘄ") + str(kwargs) + bstack11111l_opy_ (u"ࠤࠥᘅ"))
        if bstack1llll11l11l_opy_ == bstack1lllll11111_opy_.QUIT:
            if bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.PRE:
                bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack1ll1111111l_opy_(EVENTS.bstack1lll1111ll_opy_.value)
                bstack1llll1ll1l1_opy_.bstack1llll1l1lll_opy_(instance, EVENTS.bstack1lll1111ll_opy_.value, bstack1l1lll1ll1l_opy_)
                self.logger.debug(bstack11111l_opy_ (u"ࠥ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࡻࡾࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠠࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠢᘆ").format(instance, method_name, bstack1llll11l11l_opy_, bstack1l111l1ll11_opy_))
        if bstack1llll11l11l_opy_ == bstack1lllll11111_opy_.bstack1llll111lll_opy_:
            if bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.POST and not bstack1lll1l11111_opy_.bstack1l11lllll11_opy_ in instance.data:
                session_id = getattr(target, bstack11111l_opy_ (u"ࠦࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠣᘇ"), None)
                if session_id:
                    instance.data[bstack1lll1l11111_opy_.bstack1l11lllll11_opy_] = session_id
        elif (
            bstack1llll11l11l_opy_ == bstack1lllll11111_opy_.bstack1lllll11lll_opy_
            and bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args) == bstack1lll1l11111_opy_.bstack1l11l1l1lll_opy_
        ):
            if bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.PRE:
                hub_url = bstack1lll1l11111_opy_.bstack1ll1111lll_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1lll1l11111_opy_.bstack1l11llll111_opy_: hub_url,
                            bstack1lll1l11111_opy_.bstack1l111lll1ll_opy_: bstack1lll1l11111_opy_.bstack1l1lll111l1_opy_(hub_url),
                            bstack1lll1l11111_opy_.bstack1ll111ll111_opy_: int(
                                os.environ.get(bstack11111l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠧᘈ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1l1lll11111_opy_ = bstack1lll1l11111_opy_.bstack1l1lll1l1l1_opy_(*args)
                bstack11lll111l11_opy_ = bstack1l1lll11111_opy_.get(bstack11111l_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᘉ"), None) if bstack1l1lll11111_opy_ else None
                if isinstance(bstack11lll111l11_opy_, dict):
                    instance.data[bstack1lll1l11111_opy_.bstack11lll111lll_opy_] = copy.deepcopy(bstack11lll111l11_opy_)
                    instance.data[bstack1lll1l11111_opy_.bstack1l11llll11l_opy_] = bstack11lll111l11_opy_
            elif bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack11111l_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࠨᘊ"), dict()).get(bstack11111l_opy_ (u"ࠣࡵࡨࡷࡸ࡯࡯࡯ࡋࡧࠦᘋ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1lll1l11111_opy_.bstack1l11lllll11_opy_: framework_session_id,
                                bstack1lll1l11111_opy_.bstack11lll111ll1_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1llll11l11l_opy_ == bstack1lllll11111_opy_.bstack1lllll11lll_opy_
            and bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args) == bstack1lll1l11111_opy_.bstack11lll11l1l1_opy_
            and bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.POST
        ):
            instance.data[bstack1lll1l11111_opy_.bstack11lll11l111_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l111l1l1l1_opy_ in bstack1lll1l11111_opy_.bstack11lll11ll1l_opy_:
            bstack1l111l11ll1_opy_ = None
            for callback in bstack1lll1l11111_opy_.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_]:
                try:
                    bstack1l111l1l111_opy_ = callback(self, target, exec, bstack1llll1lll1l_opy_, result, *args, **kwargs)
                    if bstack1l111l11ll1_opy_ == None:
                        bstack1l111l11ll1_opy_ = bstack1l111l1l111_opy_
                except Exception as e:
                    self.logger.error(bstack11111l_opy_ (u"ࠤࡨࡶࡷࡵࡲࠡ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࠢᘌ") + str(e) + bstack11111l_opy_ (u"ࠥࠦᘍ"))
                    traceback.print_exc()
            if bstack1llll11l11l_opy_ == bstack1lllll11111_opy_.QUIT:
                if bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.POST:
                    bstack1l1lll1ll1l_opy_ = bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, EVENTS.bstack1lll1111ll_opy_.value)
                    if bstack1l1lll1ll1l_opy_!=None:
                        bstack1ll1l111ll1_opy_.end(EVENTS.bstack1lll1111ll_opy_.value, bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᘎ"), bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᘏ"), True, None)
            if bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.PRE and callable(bstack1l111l11ll1_opy_):
                return bstack1l111l11ll1_opy_
            elif bstack1l111l1ll11_opy_ == bstack1llll1l1l1l_opy_.POST and bstack1l111l11ll1_opy_:
                return bstack1l111l11ll1_opy_
    def bstack1llll1111ll_opy_(
        self, method_name, previous_state: bstack1lllll11111_opy_, *args, **kwargs
    ) -> bstack1lllll11111_opy_:
        if method_name == bstack11111l_opy_ (u"ࠨ࡟ࡠ࡫ࡱ࡭ࡹࡥ࡟ࠣᘐ") or method_name == bstack11111l_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࠢᘑ"):
            return bstack1lllll11111_opy_.bstack1llll111lll_opy_
        if method_name == bstack11111l_opy_ (u"ࠣࡳࡸ࡭ࡹࠨᘒ"):
            return bstack1lllll11111_opy_.QUIT
        if method_name == bstack11111l_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥᘓ"):
            if previous_state != bstack1lllll11111_opy_.NONE:
                command_name = bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args)
                if command_name == bstack1lll1l11111_opy_.bstack1l11l1l1lll_opy_:
                    return bstack1lllll11111_opy_.bstack1llll111lll_opy_
            return bstack1lllll11111_opy_.bstack1lllll11lll_opy_
        return bstack1lllll11111_opy_.NONE