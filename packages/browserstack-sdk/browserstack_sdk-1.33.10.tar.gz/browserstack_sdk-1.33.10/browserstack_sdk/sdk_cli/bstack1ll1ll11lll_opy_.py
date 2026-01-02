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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
    bstack1llll111l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1l1l1111l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
class bstack1ll1l111l11_opy_(bstack1ll1l11lll1_opy_):
    bstack1l11l111ll1_opy_ = bstack11111l_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡩ࡯࡫ࡷࠦᏉ")
    bstack1l11l11l11l_opy_ = bstack11111l_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᏊ")
    bstack1l111llllll_opy_ = bstack11111l_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᏋ")
    def __init__(self, bstack1ll1ll11111_opy_):
        super().__init__()
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1llll111lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l111lllll1_opy_)
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l1lll1l11l_opy_)
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.POST), self.bstack1l111llll1l_opy_)
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.POST), self.bstack1l11l111111_opy_)
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.QUIT, bstack1llll1l1l1l_opy_.POST), self.bstack1l11l11l111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l111lllll1_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠢࡠࡡ࡬ࡲ࡮ࡺ࡟ࡠࠤᏌ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack11111l_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᏍ")), str):
                    url = kwargs.get(bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᏎ"))
                elif hasattr(kwargs.get(bstack11111l_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᏏ")), bstack11111l_opy_ (u"ࠫࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠬᏐ")):
                    url = kwargs.get(bstack11111l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᏑ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack11111l_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᏒ"))._url
            except Exception as e:
                url = bstack11111l_opy_ (u"ࠧࠨᏓ")
                self.logger.error(bstack11111l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡴ࡯ࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࢂࠨᏔ").format(e))
            self.logger.info(bstack11111l_opy_ (u"ࠤࡕࡩࡲࡵࡴࡦࠢࡖࡩࡷࡼࡥࡳࠢࡄࡨࡩࡸࡥࡴࡵࠣࡦࡪ࡯࡮ࡨࠢࡳࡥࡸࡹࡥࡥࠢࡤࡷࠥࡀࠠࡼࡿࠥᏕ").format(str(url)))
            self.bstack1l11l11ll1l_opy_(instance, url, f, kwargs)
            self.logger.info(bstack11111l_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࢃ࠺ࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᏖ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
    def bstack1l1lll1l11l_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if f.bstack1llll111ll1_opy_(instance, bstack1ll1l111l11_opy_.bstack1l11l111ll1_opy_, False):
            return
        if not f.bstack1lllll111l1_opy_(instance, bstack1lll1l11111_opy_.bstack1ll111ll111_opy_):
            return
        platform_index = f.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1ll111ll111_opy_)
        if f.bstack1ll11l111ll_opy_(method_name, *args) and len(args) > 1:
            bstack1l1lll1ll_opy_ = datetime.now()
            hub_url = bstack1lll1l11111_opy_.hub_url(driver)
            self.logger.warning(bstack11111l_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࡂࠨᏗ") + str(hub_url) + bstack11111l_opy_ (u"ࠧࠨᏘ"))
            bstack1l11l11l1ll_opy_ = args[1][bstack11111l_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᏙ")] if isinstance(args[1], dict) and bstack11111l_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᏚ") in args[1] else None
            bstack1l11l1111ll_opy_ = bstack11111l_opy_ (u"ࠣࡣ࡯ࡻࡦࡿࡳࡎࡣࡷࡧ࡭ࠨᏛ")
            if isinstance(bstack1l11l11l1ll_opy_, dict):
                bstack1l1lll1ll_opy_ = datetime.now()
                r = self.bstack1l11l111l1l_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡳࡧࡪ࡭ࡸࡺࡥࡳࡡ࡬ࡲ࡮ࡺࠢᏜ"), datetime.now() - bstack1l1lll1ll_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack11111l_opy_ (u"ࠥࡷࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩ࠽ࠤࠧᏝ") + str(r) + bstack11111l_opy_ (u"ࠦࠧᏞ"))
                        return
                    if r.hub_url:
                        f.bstack1l11l1ll111_opy_(instance, driver, r.hub_url)
                        f.bstack1llll1l1lll_opy_(instance, bstack1ll1l111l11_opy_.bstack1l11l111ll1_opy_, True)
                except Exception as e:
                    self.logger.error(bstack11111l_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦᏟ"), e)
    def bstack1l111llll1l_opy_(
        self,
        f: bstack1lll1l11111_opy_,
        driver: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1lll1l11111_opy_.session_id(driver)
            if session_id:
                bstack1l11l1l1111_opy_ = bstack11111l_opy_ (u"ࠨࡻࡾ࠼ࡶࡸࡦࡸࡴࠣᏠ").format(session_id)
                bstack1ll1l111ll1_opy_.mark(bstack1l11l1l1111_opy_)
    def bstack1l11l111111_opy_(
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
        if f.bstack1llll111ll1_opy_(instance, bstack1ll1l111l11_opy_.bstack1l11l11l11l_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1lll1l11111_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack11111l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢ࡫ࡹࡧࡥࡵࡳ࡮ࡀࠦᏡ") + str(hub_url) + bstack11111l_opy_ (u"ࠣࠤᏢ"))
            return
        framework_session_id = bstack1lll1l11111_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack11111l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧᏣ") + str(framework_session_id) + bstack11111l_opy_ (u"ࠥࠦᏤ"))
            return
        if bstack1lll1l11111_opy_.bstack1l11l1l111l_opy_(*args) == bstack1lll1l11111_opy_.bstack1l11l1l1lll_opy_:
            bstack1l11l11ll11_opy_ = bstack11111l_opy_ (u"ࠦࢀࢃ࠺ࡦࡰࡧࠦᏥ").format(framework_session_id)
            bstack1l11l1l1111_opy_ = bstack11111l_opy_ (u"ࠧࢁࡽ࠻ࡵࡷࡥࡷࡺࠢᏦ").format(framework_session_id)
            bstack1ll1l111ll1_opy_.end(
                label=bstack11111l_opy_ (u"ࠨࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽ࡴࡴࡹࡴ࠮࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠤᏧ"),
                start=bstack1l11l1l1111_opy_,
                end=bstack1l11l11ll11_opy_,
                status=True,
                failure=None
            )
            bstack1l1lll1ll_opy_ = datetime.now()
            r = self.bstack1l11l11l1l1_opy_(
                ref,
                f.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1ll111ll111_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᏨ"), datetime.now() - bstack1l1lll1ll_opy_)
            f.bstack1llll1l1lll_opy_(instance, bstack1ll1l111l11_opy_.bstack1l11l11l11l_opy_, r.success)
    def bstack1l11l11l111_opy_(
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
        if f.bstack1llll111ll1_opy_(instance, bstack1ll1l111l11_opy_.bstack1l111llllll_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1lll1l11111_opy_.session_id(driver)
        hub_url = bstack1lll1l11111_opy_.hub_url(driver)
        bstack1l1lll1ll_opy_ = datetime.now()
        r = self.bstack1l11l1l1ll1_opy_(
            ref,
            f.bstack1llll111ll1_opy_(instance, bstack1lll1l11111_opy_.bstack1ll111ll111_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1ll1l1l11l_opy_(bstack11111l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᏩ"), datetime.now() - bstack1l1lll1ll_opy_)
        f.bstack1llll1l1lll_opy_(instance, bstack1ll1l111l11_opy_.bstack1l111llllll_opy_, r.success)
    @measure(event_name=EVENTS.bstack1l1ll1l11l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l11lll111l_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack11111l_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࠿ࠦࠢᏪ") + str(req) + bstack11111l_opy_ (u"ࠥࠦᏫ"))
        try:
            r = self.bstack1lll1l1l1l1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11111l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࡹࡵࡤࡥࡨࡷࡸࡃࠢᏬ") + str(r.success) + bstack11111l_opy_ (u"ࠧࠨᏭ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᏮ") + str(e) + bstack11111l_opy_ (u"ࠢࠣᏯ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l11lll1_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l11l111l1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack11111l_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢ࡭ࡳ࡯ࡴ࠻ࠢࠥᏰ") + str(req) + bstack11111l_opy_ (u"ࠤࠥᏱ"))
        try:
            r = self.bstack1lll1l1l1l1_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack11111l_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࡸࡻࡣࡤࡧࡶࡷࡂࠨᏲ") + str(r.success) + bstack11111l_opy_ (u"ࠦࠧᏳ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᏴ") + str(e) + bstack11111l_opy_ (u"ࠨࠢᏵ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l11llll_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l11l11l1l1_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11111l_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴ࠻ࠢࠥ᏶") + str(req) + bstack11111l_opy_ (u"ࠣࠤ᏷"))
        try:
            r = self.bstack1lll1l1l1l1_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack11111l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦᏸ") + str(r) + bstack11111l_opy_ (u"ࠥࠦᏹ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᏺ") + str(e) + bstack11111l_opy_ (u"ࠧࠨᏻ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1111l1_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l11l1l1ll1_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack11111l_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࡀࠠࠣᏼ") + str(req) + bstack11111l_opy_ (u"ࠢࠣᏽ"))
        try:
            r = self.bstack1lll1l1l1l1_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack11111l_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥ᏾") + str(r) + bstack11111l_opy_ (u"ࠤࠥ᏿"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣ᐀") + str(e) + bstack11111l_opy_ (u"ࠦࠧᐁ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1llll11l11_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l11l11ll1l_opy_(self, instance: bstack1llll111l1l_opy_, url: str, f: bstack1lll1l11111_opy_, kwargs):
        bstack1l11l1l11l1_opy_ = version.parse(f.framework_version)
        bstack1l11l111lll_opy_ = kwargs.get(bstack11111l_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᐂ"))
        bstack1l11l1l1l1l_opy_ = kwargs.get(bstack11111l_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᐃ"))
        bstack1l11lll1l1l_opy_ = {}
        bstack1l11l1l1l11_opy_ = {}
        bstack1l11l11111l_opy_ = None
        bstack1l11l1l11ll_opy_ = {}
        if bstack1l11l1l1l1l_opy_ is not None or bstack1l11l111lll_opy_ is not None: # check top level caps
            if bstack1l11l1l1l1l_opy_ is not None:
                bstack1l11l1l11ll_opy_[bstack11111l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᐄ")] = bstack1l11l1l1l1l_opy_
            if bstack1l11l111lll_opy_ is not None and callable(getattr(bstack1l11l111lll_opy_, bstack11111l_opy_ (u"ࠣࡶࡲࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐅ"))):
                bstack1l11l1l11ll_opy_[bstack11111l_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࡢࡥࡸࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᐆ")] = bstack1l11l111lll_opy_.to_capabilities()
        response = self.bstack1l11lll111l_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l11l1l11ll_opy_).encode(bstack11111l_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤᐇ")))
        if response is not None and response.capabilities:
            bstack1l11lll1l1l_opy_ = json.loads(response.capabilities.decode(bstack11111l_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᐈ")))
            if not bstack1l11lll1l1l_opy_: # empty caps bstack1l11lll1lll_opy_ bstack1l11lll1111_opy_ bstack1l11lllll1l_opy_ bstack1ll1ll1111l_opy_ or error in processing
                return
            bstack1l11l11111l_opy_ = f.bstack1lll11ll111_opy_[bstack11111l_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡤࡵࡰࡵ࡫ࡲࡲࡸࡥࡦࡳࡱࡰࡣࡨࡧࡰࡴࠤᐉ")](bstack1l11lll1l1l_opy_)
        if bstack1l11l111lll_opy_ is not None and bstack1l11l1l11l1_opy_ >= version.parse(bstack11111l_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬᐊ")):
            bstack1l11l1l1l11_opy_ = None
        if (
                not bstack1l11l111lll_opy_ and not bstack1l11l1l1l1l_opy_
        ) or (
                bstack1l11l1l11l1_opy_ < version.parse(bstack11111l_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ᐋ"))
        ):
            bstack1l11l1l1l11_opy_ = {}
            bstack1l11l1l1l11_opy_.update(bstack1l11lll1l1l_opy_)
        self.logger.info(bstack1l1l1111l1_opy_)
        if os.environ.get(bstack11111l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠦᐌ")).lower().__eq__(bstack11111l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᐍ")):
            kwargs.update(
                {
                    bstack11111l_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᐎ"): f.bstack1l11l111l11_opy_,
                }
            )
        if bstack1l11l1l11l1_opy_ >= version.parse(bstack11111l_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫᐏ")):
            if bstack1l11l1l1l1l_opy_ is not None:
                del kwargs[bstack11111l_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᐐ")]
            kwargs.update(
                {
                    bstack11111l_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢᐑ"): bstack1l11l11111l_opy_,
                    bstack11111l_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦᐒ"): True,
                    bstack11111l_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣᐓ"): None,
                }
            )
        elif bstack1l11l1l11l1_opy_ >= version.parse(bstack11111l_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᐔ")):
            kwargs.update(
                {
                    bstack11111l_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐕ"): bstack1l11l1l1l11_opy_,
                    bstack11111l_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᐖ"): bstack1l11l11111l_opy_,
                    bstack11111l_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᐗ"): True,
                    bstack11111l_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᐘ"): None,
                }
            )
        elif bstack1l11l1l11l1_opy_ >= version.parse(bstack11111l_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧᐙ")):
            kwargs.update(
                {
                    bstack11111l_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᐚ"): bstack1l11l1l1l11_opy_,
                    bstack11111l_opy_ (u"ࠤ࡮ࡩࡪࡶ࡟ࡢ࡮࡬ࡺࡪࠨᐛ"): True,
                    bstack11111l_opy_ (u"ࠥࡪ࡮ࡲࡥࡠࡦࡨࡸࡪࡩࡴࡰࡴࠥᐜ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack11111l_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᐝ"): bstack1l11l1l1l11_opy_,
                    bstack11111l_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᐞ"): True,
                    bstack11111l_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᐟ"): None,
                }
            )