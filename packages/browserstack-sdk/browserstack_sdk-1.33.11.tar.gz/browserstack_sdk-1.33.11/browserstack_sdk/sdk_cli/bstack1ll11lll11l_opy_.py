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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1lllll11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11l1111ll1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
class bstack1ll1ll111ll_opy_(bstack1lll11ll111_opy_):
    bstack1l11l1111ll_opy_ = bstack1l1l_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡩ࡯࡫ࡷࠦᏐ")
    bstack1l111lll1ll_opy_ = bstack1l1l_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᏑ")
    bstack1l111llll11_opy_ = bstack1l1l_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᏒ")
    def __init__(self, bstack1ll1l11l111_opy_):
        super().__init__()
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1lll1lll1ll_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11l11ll11_opy_)
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l1lll111l1_opy_)
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.POST), self.bstack1l11l1111l1_opy_)
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.POST), self.bstack1l11l11l11l_opy_)
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.QUIT, bstack1llll1ll111_opy_.POST), self.bstack1l11l1l1111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l11ll11_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠢࡠࡡ࡬ࡲ࡮ࡺ࡟ࡠࠤᏓ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack1l1l_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᏔ")), str):
                    url = kwargs.get(bstack1l1l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᏕ"))
                elif hasattr(kwargs.get(bstack1l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᏖ")), bstack1l1l_opy_ (u"ࠫࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠬᏗ")):
                    url = kwargs.get(bstack1l1l_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᏘ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack1l1l_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᏙ"))._url
            except Exception as e:
                url = bstack1l1l_opy_ (u"ࠧࠨᏚ")
                self.logger.error(bstack1l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡴ࡯ࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࢂࠨᏛ").format(e))
            self.logger.info(bstack1l1l_opy_ (u"ࠤࡕࡩࡲࡵࡴࡦࠢࡖࡩࡷࡼࡥࡳࠢࡄࡨࡩࡸࡥࡴࡵࠣࡦࡪ࡯࡮ࡨࠢࡳࡥࡸࡹࡥࡥࠢࡤࡷࠥࡀࠠࡼࡿࠥᏜ").format(str(url)))
            self.bstack1l11l11l1ll_opy_(instance, url, f, kwargs)
            self.logger.info(bstack1l1l_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࢃ࠺ࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣᏝ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
    def bstack1l1lll111l1_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll111ll_opy_.bstack1l11l1111ll_opy_, False):
            return
        if not f.bstack1llll1l1l11_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_):
            return
        platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_)
        if f.bstack1ll11l11111_opy_(method_name, *args) and len(args) > 1:
            bstack1ll111l1_opy_ = datetime.now()
            hub_url = bstack1ll1lll1lll_opy_.hub_url(driver)
            self.logger.warning(bstack1l1l_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࡂࠨᏞ") + str(hub_url) + bstack1l1l_opy_ (u"ࠧࠨᏟ"))
            bstack1l111lllll1_opy_ = args[1][bstack1l1l_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᏠ")] if isinstance(args[1], dict) and bstack1l1l_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᏡ") in args[1] else None
            bstack1l11l1l11l1_opy_ = bstack1l1l_opy_ (u"ࠣࡣ࡯ࡻࡦࡿࡳࡎࡣࡷࡧ࡭ࠨᏢ")
            if isinstance(bstack1l111lllll1_opy_, dict):
                bstack1ll111l1_opy_ = datetime.now()
                r = self.bstack1l11l111l1l_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡳࡧࡪ࡭ࡸࡺࡥࡳࡡ࡬ࡲ࡮ࡺࠢᏣ"), datetime.now() - bstack1ll111l1_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack1l1l_opy_ (u"ࠥࡷࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩ࠽ࠤࠧᏤ") + str(r) + bstack1l1l_opy_ (u"ࠦࠧᏥ"))
                        return
                    if r.hub_url:
                        f.bstack1l11l111lll_opy_(instance, driver, r.hub_url)
                        f.bstack1llll1lll11_opy_(instance, bstack1ll1ll111ll_opy_.bstack1l11l1111ll_opy_, True)
                except Exception as e:
                    self.logger.error(bstack1l1l_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦᏦ"), e)
    def bstack1l11l1111l1_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1ll1lll1lll_opy_.session_id(driver)
            if session_id:
                bstack1l11l11lll1_opy_ = bstack1l1l_opy_ (u"ࠨࡻࡾ࠼ࡶࡸࡦࡸࡴࠣᏧ").format(session_id)
                bstack1ll1l1ll111_opy_.mark(bstack1l11l11lll1_opy_)
    def bstack1l11l11l11l_opy_(
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
        if f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll111ll_opy_.bstack1l111lll1ll_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1ll1lll1lll_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢ࡫ࡹࡧࡥࡵࡳ࡮ࡀࠦᏨ") + str(hub_url) + bstack1l1l_opy_ (u"ࠣࠤᏩ"))
            return
        framework_session_id = bstack1ll1lll1lll_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack1l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧᏪ") + str(framework_session_id) + bstack1l1l_opy_ (u"ࠥࠦᏫ"))
            return
        if bstack1ll1lll1lll_opy_.bstack1l111llll1l_opy_(*args) == bstack1ll1lll1lll_opy_.bstack1l11l11llll_opy_:
            bstack1l11l111ll1_opy_ = bstack1l1l_opy_ (u"ࠦࢀࢃ࠺ࡦࡰࡧࠦᏬ").format(framework_session_id)
            bstack1l11l11lll1_opy_ = bstack1l1l_opy_ (u"ࠧࢁࡽ࠻ࡵࡷࡥࡷࡺࠢᏭ").format(framework_session_id)
            bstack1ll1l1ll111_opy_.end(
                label=bstack1l1l_opy_ (u"ࠨࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽ࡴࡴࡹࡴ࠮࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠤᏮ"),
                start=bstack1l11l11lll1_opy_,
                end=bstack1l11l111ll1_opy_,
                status=True,
                failure=None
            )
            bstack1ll111l1_opy_ = datetime.now()
            r = self.bstack1l11l111111_opy_(
                ref,
                f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᏯ"), datetime.now() - bstack1ll111l1_opy_)
            f.bstack1llll1lll11_opy_(instance, bstack1ll1ll111ll_opy_.bstack1l111lll1ll_opy_, r.success)
    def bstack1l11l1l1111_opy_(
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
        if f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll111ll_opy_.bstack1l111llll11_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1ll1lll1lll_opy_.session_id(driver)
        hub_url = bstack1ll1lll1lll_opy_.hub_url(driver)
        bstack1ll111l1_opy_ = datetime.now()
        r = self.bstack1l11l111l11_opy_(
            ref,
            f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠣࡩࡵࡴࡨࡀࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᏰ"), datetime.now() - bstack1ll111l1_opy_)
        f.bstack1llll1lll11_opy_(instance, bstack1ll1ll111ll_opy_.bstack1l111llll11_opy_, r.success)
    @measure(event_name=EVENTS.bstack1l11l11lll_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l11ll1ll1l_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack1l1l_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࠿ࠦࠢᏱ") + str(req) + bstack1l1l_opy_ (u"ࠥࠦᏲ"))
        try:
            r = self.bstack1ll1l11111l_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࡹࡵࡤࡥࡨࡷࡸࡃࠢᏳ") + str(r.success) + bstack1l1l_opy_ (u"ࠧࠨᏴ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᏵ") + str(e) + bstack1l1l_opy_ (u"ࠢࠣ᏶"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l11l1l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l11l111l1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack1l1l_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢ࡭ࡳ࡯ࡴ࠻ࠢࠥ᏷") + str(req) + bstack1l1l_opy_ (u"ࠤࠥᏸ"))
        try:
            r = self.bstack1ll1l11111l_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࡸࡻࡣࡤࡧࡶࡷࡂࠨᏹ") + str(r.success) + bstack1l1l_opy_ (u"ࠦࠧᏺ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᏻ") + str(e) + bstack1l1l_opy_ (u"ࠨࠢᏼ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l11ll1l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l11l111111_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1l1l_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴ࠻ࠢࠥᏽ") + str(req) + bstack1l1l_opy_ (u"ࠣࠤ᏾"))
        try:
            r = self.bstack1ll1l11111l_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦ᏿") + str(r) + bstack1l1l_opy_ (u"ࠥࠦ᐀"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᐁ") + str(e) + bstack1l1l_opy_ (u"ࠧࠨᐂ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l111llllll_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l11l111l11_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1l1l_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࡀࠠࠣᐃ") + str(req) + bstack1l1l_opy_ (u"ࠢࠣᐄ"))
        try:
            r = self.bstack1ll1l11111l_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥᐅ") + str(r) + bstack1l1l_opy_ (u"ࠤࠥᐆ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣᐇ") + str(e) + bstack1l1l_opy_ (u"ࠦࠧᐈ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack111l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l11l11l1ll_opy_(self, instance: bstack1lllll11l1l_opy_, url: str, f: bstack1ll1lll1lll_opy_, kwargs):
        bstack1l11l11111l_opy_ = version.parse(f.framework_version)
        bstack1l11l1l1ll1_opy_ = kwargs.get(bstack1l1l_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᐉ"))
        bstack1l11l11l111_opy_ = kwargs.get(bstack1l1l_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᐊ"))
        bstack1l11llll111_opy_ = {}
        bstack1l11l1l11ll_opy_ = {}
        bstack1l11l1l1l1l_opy_ = None
        bstack1l11l1l1l11_opy_ = {}
        if bstack1l11l11l111_opy_ is not None or bstack1l11l1l1ll1_opy_ is not None: # check top level caps
            if bstack1l11l11l111_opy_ is not None:
                bstack1l11l1l1l11_opy_[bstack1l1l_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᐋ")] = bstack1l11l11l111_opy_
            if bstack1l11l1l1ll1_opy_ is not None and callable(getattr(bstack1l11l1l1ll1_opy_, bstack1l1l_opy_ (u"ࠣࡶࡲࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐌ"))):
                bstack1l11l1l1l11_opy_[bstack1l1l_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࡢࡥࡸࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᐍ")] = bstack1l11l1l1ll1_opy_.to_capabilities()
        response = self.bstack1l11ll1ll1l_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l11l1l1l11_opy_).encode(bstack1l1l_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤᐎ")))
        if response is not None and response.capabilities:
            bstack1l11llll111_opy_ = json.loads(response.capabilities.decode(bstack1l1l_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᐏ")))
            if not bstack1l11llll111_opy_: # empty caps bstack1l11ll1l11l_opy_ bstack1l11lll1ll1_opy_ bstack1l11ll1llll_opy_ bstack1lll111ll11_opy_ or error in processing
                return
            bstack1l11l1l1l1l_opy_ = f.bstack1lll1ll1l1l_opy_[bstack1l1l_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡤࡵࡰࡵ࡫ࡲࡲࡸࡥࡦࡳࡱࡰࡣࡨࡧࡰࡴࠤᐐ")](bstack1l11llll111_opy_)
        if bstack1l11l1l1ll1_opy_ is not None and bstack1l11l11111l_opy_ >= version.parse(bstack1l1l_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬᐑ")):
            bstack1l11l1l11ll_opy_ = None
        if (
                not bstack1l11l1l1ll1_opy_ and not bstack1l11l11l111_opy_
        ) or (
                bstack1l11l11111l_opy_ < version.parse(bstack1l1l_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ᐒ"))
        ):
            bstack1l11l1l11ll_opy_ = {}
            bstack1l11l1l11ll_opy_.update(bstack1l11llll111_opy_)
        self.logger.info(bstack11l1111ll1_opy_)
        if os.environ.get(bstack1l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠦᐓ")).lower().__eq__(bstack1l1l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᐔ")):
            kwargs.update(
                {
                    bstack1l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᐕ"): f.bstack1l11l1l111l_opy_,
                }
            )
        if bstack1l11l11111l_opy_ >= version.parse(bstack1l1l_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫᐖ")):
            if bstack1l11l11l111_opy_ is not None:
                del kwargs[bstack1l1l_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᐗ")]
            kwargs.update(
                {
                    bstack1l1l_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢᐘ"): bstack1l11l1l1l1l_opy_,
                    bstack1l1l_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦᐙ"): True,
                    bstack1l1l_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣᐚ"): None,
                }
            )
        elif bstack1l11l11111l_opy_ >= version.parse(bstack1l1l_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᐛ")):
            kwargs.update(
                {
                    bstack1l1l_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐜ"): bstack1l11l1l11ll_opy_,
                    bstack1l1l_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᐝ"): bstack1l11l1l1l1l_opy_,
                    bstack1l1l_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᐞ"): True,
                    bstack1l1l_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᐟ"): None,
                }
            )
        elif bstack1l11l11111l_opy_ >= version.parse(bstack1l1l_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧᐠ")):
            kwargs.update(
                {
                    bstack1l1l_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᐡ"): bstack1l11l1l11ll_opy_,
                    bstack1l1l_opy_ (u"ࠤ࡮ࡩࡪࡶ࡟ࡢ࡮࡬ࡺࡪࠨᐢ"): True,
                    bstack1l1l_opy_ (u"ࠥࡪ࡮ࡲࡥࡠࡦࡨࡸࡪࡩࡴࡰࡴࠥᐣ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack1l1l_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᐤ"): bstack1l11l1l11ll_opy_,
                    bstack1l1l_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᐥ"): True,
                    bstack1l1l_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᐦ"): None,
                }
            )