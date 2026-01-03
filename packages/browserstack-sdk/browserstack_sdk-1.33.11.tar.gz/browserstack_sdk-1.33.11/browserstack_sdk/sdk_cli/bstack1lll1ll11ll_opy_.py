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
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1lllll11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1ll11llllll_opy_(bstack1lll11ll111_opy_):
    bstack1ll1111l1ll_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1ll1lll1lll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l1lll111l1_opy_)
    def is_enabled(self) -> bool:
        return True
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
        hub_url = f.hub_url(driver)
        if f.bstack1l1lll11111_opy_(hub_url):
            if not bstack1ll11llllll_opy_.bstack1ll1111l1ll_opy_:
                self.logger.warning(bstack1l1l_opy_ (u"ࠤ࡯ࡳࡨࡧ࡬ࠡࡵࡨࡰ࡫࠳ࡨࡦࡣ࡯ࠤ࡫ࡲ࡯ࡸࠢࡧ࡭ࡸࡧࡢ࡭ࡧࡧࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡪࡰࡩࡶࡦࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡪࡸࡦࡤࡻࡲ࡭࠿ࠥኌ") + str(hub_url) + bstack1l1l_opy_ (u"ࠥࠦኍ"))
                bstack1ll11llllll_opy_.bstack1ll1111l1ll_opy_ = True
            return
        command_name = f.bstack1ll111ll111_opy_(*args)
        bstack1l1lll11lll_opy_ = f.bstack1l1ll1llll1_opy_(*args)
        if command_name and command_name.lower() == bstack1l1l_opy_ (u"ࠦ࡫࡯࡮ࡥࡧ࡯ࡩࡲ࡫࡮ࡵࠤ኎") and bstack1l1lll11lll_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1l1lll11lll_opy_.get(bstack1l1l_opy_ (u"ࠧࡻࡳࡪࡰࡪࠦ኏"), None), bstack1l1lll11lll_opy_.get(bstack1l1l_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧነ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack1l1l_opy_ (u"ࠢࡼࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫ࡽ࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠣࡳࡷࠦࡡࡳࡩࡶ࠲ࡺࡹࡩ࡯ࡩࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡴࡸࠠࡢࡴࡪࡷ࠳ࡼࡡ࡭ࡷࡨࡁࠧኑ") + str(locator_value) + bstack1l1l_opy_ (u"ࠣࠤኒ"))
                return
            def bstack1lllll11111_opy_(driver, bstack1l1lll111ll_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1l1lll111ll_opy_(driver, *args, **kwargs)
                    response = self.bstack1l1lll11l11_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack1l1l_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵ࠰ࡷࡨࡸࡩࡱࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࠧና") + str(locator_value) + bstack1l1l_opy_ (u"ࠥࠦኔ"))
                    else:
                        self.logger.warning(bstack1l1l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷ࠲ࡴ࡯࠮ࡵࡦࡶ࡮ࡶࡴ࠻ࠢ࡯ࡳࡨࡧࡴࡰࡴࡢࡸࡾࡶࡥ࠾ࡽ࡯ࡳࡨࡧࡴࡰࡴࡢࡸࡾࡶࡥࡾࠢ࡯ࡳࡨࡧࡴࡰࡴࡢࡺࡦࡲࡵࡦ࠿ࡾࡰࡴࡩࡡࡵࡱࡵࡣࡻࡧ࡬ࡶࡧࢀࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡃࠢን") + str(response) + bstack1l1l_opy_ (u"ࠧࠨኖ"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1l1lll1111l_opy_(
                        driver, bstack1l1lll111ll_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1lllll11111_opy_.__name__ = command_name
            return bstack1lllll11111_opy_
    def __1l1lll1111l_opy_(
        self,
        driver,
        bstack1l1lll111ll_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l1lll11l11_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack1l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭ࡩࡧࡤࡰ࡮ࡴࡧ࠮ࡶࡵ࡭࡬࡭ࡥࡳࡧࡧ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࠨኗ") + str(locator_value) + bstack1l1l_opy_ (u"ࠢࠣኘ"))
                bstack1l1lll1l111_opy_ = self.bstack1l1lll11ll1_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack1l1l_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡶࡪࡹࡵ࡭ࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࢂࠦࡨࡦࡣ࡯࡭ࡳ࡭࡟ࡳࡧࡶࡹࡱࡺ࠽ࠣኙ") + str(bstack1l1lll1l111_opy_) + bstack1l1l_opy_ (u"ࠤࠥኚ"))
                if bstack1l1lll1l111_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack1l1l_opy_ (u"ࠥࡹࡸ࡯࡮ࡨࠤኛ"): bstack1l1lll1l111_opy_.locator_type,
                            bstack1l1l_opy_ (u"ࠦࡻࡧ࡬ࡶࡧࠥኜ"): bstack1l1lll1l111_opy_.locator_value,
                        }
                    )
                    return bstack1l1lll111ll_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack1l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡏ࡟ࡅࡇࡅ࡙ࡌࠨኝ"), False):
                    self.logger.info(bstack1lll1l111ll_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭ࡩࡧࡤࡰ࡮ࡴࡧ࠮ࡴࡨࡷࡺࡲࡴ࠮࡯࡬ࡷࡸ࡯࡮ࡨ࠼ࠣࡷࡱ࡫ࡥࡱࠪ࠶࠴࠮ࠦ࡬ࡦࡶࡷ࡭ࡳ࡭ࠠࡺࡱࡸࠤ࡮ࡴࡳࡱࡧࡦࡸࠥࡺࡨࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࠦ࡬ࡰࡩࡶࠦኞ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡺࡸࡥ࠮ࡰࡲ࠱ࡸࡩࡲࡪࡲࡷ࠾ࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡴࡺࡲࡨࢁࠥࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࢃࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠿ࠥኟ") + str(response) + bstack1l1l_opy_ (u"ࠣࠤአ"))
        except Exception as err:
            self.logger.warning(bstack1l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰࡬ࡪࡧ࡬ࡪࡰࡪ࠱ࡷ࡫ࡳࡶ࡮ࡷ࠾ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࠨኡ") + str(err) + bstack1l1l_opy_ (u"ࠥࠦኢ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l1lll11l1l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l1lll11l11_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack1l1l_opy_ (u"ࠦ࠵ࠨኣ"),
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack1l1l_opy_ (u"ࠧࠨኤ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1ll1l11111l_opy_.AISelfHealStep(req)
            self.logger.info(bstack1l1l_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣእ") + str(r) + bstack1l1l_opy_ (u"ࠢࠣኦ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨኧ") + str(e) + bstack1l1l_opy_ (u"ࠤࠥከ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1ll1lllll_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1l1lll11ll1_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack1l1l_opy_ (u"ࠥ࠴ࠧኩ")):
        self.bstack1ll11l1ll11_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1ll1l11111l_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack1l1l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨኪ") + str(r) + bstack1l1l_opy_ (u"ࠧࠨካ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦኬ") + str(e) + bstack1l1l_opy_ (u"ࠢࠣክ"))
            traceback.print_exc()
            raise e