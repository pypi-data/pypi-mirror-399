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
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
    bstack1llll1ll1l1_opy_,
    bstack1llll111l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from browserstack_sdk.sdk_cli.bstack1ll1llll11l_opy_ import bstack1ll1ll11ll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1lll1ll_opy_ import bstack1lllll1l111_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
import weakref
class bstack1l1ll1l1ll1_opy_(bstack1ll1l11lll1_opy_):
    bstack1l1ll1l11ll_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack1llll111l1l_opy_]]
    pages: Dict[str, Tuple[Callable, bstack1llll111l1l_opy_]]
    def __init__(self, bstack1l1ll1l11ll_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.pages = dict()
        self.bstack1l1ll1lll11_opy_ = dict()
        self.bstack1l1ll1l11ll_opy_ = bstack1l1ll1l11ll_opy_
        self.frameworks = frameworks
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1llll111lll_opy_, bstack1llll1l1l1l_opy_.POST), self.__1l1ll1l1lll_opy_)
        if any(bstack1lll1l11111_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_(
                (bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.__1l1ll1l11l1_opy_
            )
            bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_(
                (bstack1lllll11111_opy_.QUIT, bstack1llll1l1l1l_opy_.POST), self.__1l1ll1l1l11_opy_
            )
    def __1l1ll1l1lll_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        bstack1l1ll1llll1_opy_: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if method_name != bstack11111l_opy_ (u"ࠦࡳ࡫ࡷࡠࡲࡤ࡫ࡪࠨኪ"):
                return
            contexts = bstack1l1ll1llll1_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11111l_opy_ (u"ࠧࡧࡢࡰࡷࡷ࠾ࡧࡲࡡ࡯࡭ࠥካ") in page.url:
                                self.logger.debug(bstack11111l_opy_ (u"ࠨࡓࡵࡱࡵ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡳ࡫ࡷࠡࡲࡤ࡫ࡪࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠣኬ"))
                                self.pages[instance.ref()] = weakref.ref(page), instance
                                bstack1llll1ll1l1_opy_.bstack1llll1l1lll_opy_(instance, self.bstack1l1ll1l11ll_opy_, True)
                                self.logger.debug(bstack11111l_opy_ (u"ࠢࡠࡡࡲࡲࡤࡶࡡࡨࡧࡢ࡭ࡳ࡯ࡴ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧክ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠣࠤኮ"))
        except Exception as e:
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡷࡳࡷ࡯࡮ࡨࠢࡱࡩࡼࠦࡰࡢࡩࡨࠤ࠿ࠨኯ"),e)
    def __1l1ll1l11l1_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack1llll1ll1l1_opy_.bstack1llll111ll1_opy_(instance, self.bstack1l1ll1l11ll_opy_, False):
            return
        if not f.bstack1l1lll111l1_opy_(f.hub_url(driver)):
            self.bstack1l1ll1lll11_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack1llll1ll1l1_opy_.bstack1llll1l1lll_opy_(instance, self.bstack1l1ll1l11ll_opy_, True)
            self.logger.debug(bstack11111l_opy_ (u"ࠥࡣࡤࡵ࡮ࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࡢ࡭ࡳ࡯ࡴ࠻ࠢࡱࡳࡳࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡪࡲࡪࡸࡨࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣኰ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠦࠧ኱"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack1llll1ll1l1_opy_.bstack1llll1l1lll_opy_(instance, self.bstack1l1ll1l11ll_opy_, True)
        self.logger.debug(bstack11111l_opy_ (u"ࠧࡥ࡟ࡰࡰࡢࡷࡪࡲࡥ࡯࡫ࡸࡱࡤ࡯࡮ࡪࡶ࠽ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࠢኲ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠨࠢኳ"))
    def __1l1ll1l1l11_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1l1ll1ll1l1_opy_(instance)
        self.logger.debug(bstack11111l_opy_ (u"ࠢࡠࡡࡲࡲࡤࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࡟ࡲࡷ࡬ࡸ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤኴ") + str(instance.ref()) + bstack11111l_opy_ (u"ࠣࠤኵ"))
    def bstack1l1ll1ll1ll_opy_(self, context: bstack1lllll1l111_opy_, reverse=True) -> List[Tuple[Callable, bstack1llll111l1l_opy_]]:
        matches = []
        if self.pages:
            for data in self.pages.values():
                if data[1].bstack1l1ll1lll1l_opy_(context):
                    matches.append(data)
        if self.drivers:
            for data in self.drivers.values():
                if (
                    bstack1lll1l11111_opy_.bstack1l1ll1l1l1l_opy_(data[1])
                    and data[1].bstack1l1ll1lll1l_opy_(context)
                    and getattr(data[0](), bstack11111l_opy_ (u"ࠤࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠨ኶"), False)
                ):
                    matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1lll1llll11_opy_, reverse=reverse)
    def bstack1l1ll1ll111_opy_(self, context: bstack1lllll1l111_opy_, reverse=True) -> List[Tuple[Callable, bstack1llll111l1l_opy_]]:
        matches = []
        for data in self.bstack1l1ll1lll11_opy_.values():
            if (
                data[1].bstack1l1ll1lll1l_opy_(context)
                and getattr(data[0](), bstack11111l_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢ኷"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1lll1llll11_opy_, reverse=reverse)
    def bstack1l1ll1lllll_opy_(self, instance: bstack1llll111l1l_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1l1ll1ll1l1_opy_(self, instance: bstack1llll111l1l_opy_) -> bool:
        if self.bstack1l1ll1lllll_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack1llll1ll1l1_opy_.bstack1llll1l1lll_opy_(instance, self.bstack1l1ll1l11ll_opy_, False)
            return True
        return False