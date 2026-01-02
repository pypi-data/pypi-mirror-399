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
    bstack1llll111l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l1111_opy_ import bstack1lll1l11111_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1lll11111l1_opy_(bstack1ll1l11lll1_opy_):
    bstack1ll11111l1l_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1lll1l11111_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l1lll1l11l_opy_)
    def is_enabled(self) -> bool:
        return True
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
        hub_url = f.hub_url(driver)
        if f.bstack1l1lll111l1_opy_(hub_url):
            if not bstack1lll11111l1_opy_.bstack1ll11111l1l_opy_:
                self.logger.warning(bstack11111l_opy_ (u"ࠤ࡯ࡳࡨࡧ࡬ࠡࡵࡨࡰ࡫࠳ࡨࡦࡣ࡯ࠤ࡫ࡲ࡯ࡸࠢࡧ࡭ࡸࡧࡢ࡭ࡧࡧࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡪࡰࡩࡶࡦࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡪࡸࡦࡤࡻࡲ࡭࠿ࠥኅ") + str(hub_url) + bstack11111l_opy_ (u"ࠥࠦኆ"))
                bstack1lll11111l1_opy_.bstack1ll11111l1l_opy_ = True
            return
        command_name = f.bstack1ll11l11l11_opy_(*args)
        bstack1l1lll11111_opy_ = f.bstack1l1lll1l1l1_opy_(*args)
        if command_name and command_name.lower() == bstack11111l_opy_ (u"ࠦ࡫࡯࡮ࡥࡧ࡯ࡩࡲ࡫࡮ࡵࠤኇ") and bstack1l1lll11111_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1l1lll11111_opy_.get(bstack11111l_opy_ (u"ࠧࡻࡳࡪࡰࡪࠦኈ"), None), bstack1l1lll11111_opy_.get(bstack11111l_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧ኉"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack11111l_opy_ (u"ࠢࡼࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫ࡽ࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠣࡳࡷࠦࡡࡳࡩࡶ࠲ࡺࡹࡩ࡯ࡩࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡴࡸࠠࡢࡴࡪࡷ࠳ࡼࡡ࡭ࡷࡨࡁࠧኊ") + str(locator_value) + bstack11111l_opy_ (u"ࠣࠤኋ"))
                return
            def bstack1lllll11l11_opy_(driver, bstack1l1lll1111l_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1l1lll1111l_opy_(driver, *args, **kwargs)
                    response = self.bstack1l1lll111ll_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack11111l_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵ࠰ࡷࡨࡸࡩࡱࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࠧኌ") + str(locator_value) + bstack11111l_opy_ (u"ࠥࠦኍ"))
                    else:
                        self.logger.warning(bstack11111l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷ࠲ࡴ࡯࠮ࡵࡦࡶ࡮ࡶࡴ࠻ࠢ࡯ࡳࡨࡧࡴࡰࡴࡢࡸࡾࡶࡥ࠾ࡽ࡯ࡳࡨࡧࡴࡰࡴࡢࡸࡾࡶࡥࡾࠢ࡯ࡳࡨࡧࡴࡰࡴࡢࡺࡦࡲࡵࡦ࠿ࡾࡰࡴࡩࡡࡵࡱࡵࡣࡻࡧ࡬ࡶࡧࢀࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡃࠢ኎") + str(response) + bstack11111l_opy_ (u"ࠧࠨ኏"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1l1lll1l111_opy_(
                        driver, bstack1l1lll1111l_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1lllll11l11_opy_.__name__ = command_name
            return bstack1lllll11l11_opy_
    def __1l1lll1l111_opy_(
        self,
        driver,
        bstack1l1lll1111l_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l1lll111ll_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack11111l_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭ࡩࡧࡤࡰ࡮ࡴࡧ࠮ࡶࡵ࡭࡬࡭ࡥࡳࡧࡧ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࠨነ") + str(locator_value) + bstack11111l_opy_ (u"ࠢࠣኑ"))
                bstack1l1lll11l1l_opy_ = self.bstack1l1lll11ll1_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack11111l_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡶࡪࡹࡵ࡭ࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࢂࠦࡨࡦࡣ࡯࡭ࡳ࡭࡟ࡳࡧࡶࡹࡱࡺ࠽ࠣኒ") + str(bstack1l1lll11l1l_opy_) + bstack11111l_opy_ (u"ࠤࠥና"))
                if bstack1l1lll11l1l_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack11111l_opy_ (u"ࠥࡹࡸ࡯࡮ࡨࠤኔ"): bstack1l1lll11l1l_opy_.locator_type,
                            bstack11111l_opy_ (u"ࠦࡻࡧ࡬ࡶࡧࠥን"): bstack1l1lll11l1l_opy_.locator_value,
                        }
                    )
                    return bstack1l1lll1111l_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack11111l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡏ࡟ࡅࡇࡅ࡙ࡌࠨኖ"), False):
                    self.logger.info(bstack1ll1lll1l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭ࡩࡧࡤࡰ࡮ࡴࡧ࠮ࡴࡨࡷࡺࡲࡴ࠮࡯࡬ࡷࡸ࡯࡮ࡨ࠼ࠣࡷࡱ࡫ࡥࡱࠪ࠶࠴࠮ࠦ࡬ࡦࡶࡷ࡭ࡳ࡭ࠠࡺࡱࡸࠤ࡮ࡴࡳࡱࡧࡦࡸࠥࡺࡨࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࠦ࡬ࡰࡩࡶࠦኗ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack11111l_opy_ (u"ࠢࡧࡣ࡬ࡰࡺࡸࡥ࠮ࡰࡲ࠱ࡸࡩࡲࡪࡲࡷ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࢃࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠿ࠥኘ") + str(response) + bstack11111l_opy_ (u"ࠣࠤኙ"))
        except Exception as err:
            self.logger.warning(bstack11111l_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡷ࡫ࡳࡶ࡮ࡷ࠾ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࠨኚ") + str(err) + bstack11111l_opy_ (u"ࠥࠦኛ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l1lll11l11_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l1lll111ll_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack11111l_opy_ (u"ࠦ࠵ࠨኜ"),
    ):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack11111l_opy_ (u"ࠧࠨኝ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1lll1l1l1l1_opy_.AISelfHealStep(req)
            self.logger.info(bstack11111l_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣኞ") + str(r) + bstack11111l_opy_ (u"ࠢࠣኟ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨአ") + str(e) + bstack11111l_opy_ (u"ࠤࠥኡ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1lll11lll_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
    def bstack1l1lll11ll1_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack11111l_opy_ (u"ࠥ࠴ࠧኢ")):
        self.bstack1l1lll1l1ll_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1lll1l1l1l1_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack11111l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨኣ") + str(r) + bstack11111l_opy_ (u"ࠧࠨኤ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦእ") + str(e) + bstack11111l_opy_ (u"ࠢࠣኦ"))
            traceback.print_exc()
            raise e