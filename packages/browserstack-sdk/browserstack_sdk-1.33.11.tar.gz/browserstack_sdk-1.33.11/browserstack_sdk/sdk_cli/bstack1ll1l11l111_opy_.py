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
from datetime import datetime
import os
import threading
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1llll1ll1ll_opy_,
    bstack1lllll11l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_, bstack1lll111l1ll_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllll11_opy_ import bstack1ll11lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111lll_opy_ import bstack1lll11l1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll11llll1l_opy_ import bstack1ll1l1lllll_opy_
from bstack_utils.helper import bstack1l1llll1ll1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
import grpc
import traceback
import json
class bstack1ll1l1l111l_opy_(bstack1lll11ll111_opy_):
    bstack1ll1111l1ll_opy_ = False
    bstack1ll11111ll1_opy_ = bstack1l1l_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵࠦᇓ")
    bstack1ll111111ll_opy_ = bstack1l1l_opy_ (u"ࠢࡳࡧࡰࡳࡹ࡫࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࠥᇔ")
    bstack1l1llll1l1l_opy_ = bstack1l1l_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠ࡫ࡱ࡭ࡹࠨᇕ")
    bstack1l1llll11ll_opy_ = bstack1l1l_opy_ (u"ࠤࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡ࡬ࡷࡤࡹࡣࡢࡰࡱ࡭ࡳ࡭ࠢᇖ")
    bstack1l1llll11l1_opy_ = bstack1l1l_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴࡢ࡬ࡦࡹ࡟ࡶࡴ࡯ࠦᇗ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self, bstack1lll11ll1ll_opy_, bstack1lll1l1111l_opy_):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        self.bstack1ll111llll1_opy_ = False
        self.bstack1ll111l11l1_opy_ = dict()
        self.bstack1ll11l11l11_opy_ = False
        self.bstack1ll1111l11l_opy_ = dict()
        if not self.is_enabled():
            return
        self.bstack1ll11l1lll1_opy_ = bstack1lll1l1111l_opy_
        bstack1lll11ll1ll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1ll11l11l1l_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.PRE), self.bstack1ll11111l11_opy_)
        TestFramework.bstack1l1lllllll1_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST), self.bstack1ll111l1111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll11111l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll111lll11_opy_(instance, args)
        test_framework = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l11lll_opy_)
        if self.bstack1ll111llll1_opy_:
            self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠦᇘ")] = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
        if bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠩᇙ") in instance.bstack1ll11l111ll_opy_:
            platform_index = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1llllll1l_opy_)
            self.accessibility = self.bstack1ll111l1l11_opy_(tags, self.config[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᇚ")][platform_index])
        else:
            capabilities = self.bstack1ll11l1lll1_opy_.bstack1l1llll1l11_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
            if not capabilities:
                self.logger.debug(bstack1l1l_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤ࡫ࡵࡵ࡯ࡦࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᇛ") + str(kwargs) + bstack1l1l_opy_ (u"ࠣࠤᇜ"))
                return
            self.accessibility = self.bstack1ll111l1l11_opy_(tags, capabilities)
        if self.bstack1ll11l1lll1_opy_.pages and self.bstack1ll11l1lll1_opy_.pages.values():
            bstack1l1lll1l11l_opy_ = list(self.bstack1ll11l1lll1_opy_.pages.values())
            if bstack1l1lll1l11l_opy_ and isinstance(bstack1l1lll1l11l_opy_[0], (list, tuple)) and bstack1l1lll1l11l_opy_[0]:
                bstack1ll11l1l1ll_opy_ = bstack1l1lll1l11l_opy_[0][0]
                if callable(bstack1ll11l1l1ll_opy_):
                    page = bstack1ll11l1l1ll_opy_()
                    def bstack1l11l1ll1_opy_():
                        self.get_accessibility_results(page, bstack1l1l_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨᇝ"))
                    def bstack1ll111l111l_opy_():
                        self.get_accessibility_results_summary(page, bstack1l1l_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᇞ"))
                    setattr(page, bstack1l1l_opy_ (u"ࠦ࡬࡫ࡴࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡒࡦࡵࡸࡰࡹࡹࠢᇟ"), bstack1l11l1ll1_opy_)
                    setattr(page, bstack1l1l_opy_ (u"ࠧ࡭ࡥࡵࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡓࡧࡶࡹࡱࡺࡓࡶ࡯ࡰࡥࡷࡿࠢᇠ"), bstack1ll111l111l_opy_)
        self.logger.debug(bstack1l1l_opy_ (u"ࠨࡳࡩࡱࡸࡰࡩࠦࡲࡶࡰࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡺࡦࡲࡵࡦ࠿ࠥᇡ") + str(self.accessibility) + bstack1l1l_opy_ (u"ࠢࠣᇢ"))
    def bstack1ll11l11l1l_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            bstack1ll111l1_opy_ = datetime.now()
            self.bstack1l1lll1lll1_opy_(f, exec, *args, **kwargs)
            instance, method_name = exec
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠣࡣ࠴࠵ࡾࡀࡩ࡯࡫ࡷࡣࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡨࡵ࡮ࡧ࡫ࡪࠦᇣ"), datetime.now() - bstack1ll111l1_opy_)
            if (
                not f.bstack1l1lll1l1l1_opy_(method_name)
                or f.bstack1l1llll1111_opy_(method_name, *args)
                or f.bstack1ll111lll1l_opy_(method_name, *args)
            ):
                return
            if not f.bstack1llll1l11ll_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll1l1l_opy_, False):
                if not bstack1ll1l1l111l_opy_.bstack1ll1111l1ll_opy_:
                    self.logger.warning(bstack1l1l_opy_ (u"ࠤ࡞ࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࠧᇤ") + str(f.platform_index) + bstack1l1l_opy_ (u"ࠥࡡࠥࡧ࠱࠲ࡻࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢ࡫ࡥࡻ࡫ࠠ࡯ࡱࡷࠤࡧ࡫ࡥ࡯ࠢࡶࡩࡹࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡵࡨࡷࡸ࡯࡯࡯ࠤᇥ"))
                    bstack1ll1l1l111l_opy_.bstack1ll1111l1ll_opy_ = True
                return
            bstack1ll1111ll11_opy_ = self.scripts.get(f.framework_name, {})
            if not bstack1ll1111ll11_opy_:
                platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_, 0)
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡳࡵࠠࡢ࠳࠴ࡽࠥࡹࡣࡳ࡫ࡳࡸࡸࠦࡦࡰࡴࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࢃࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࠤᇦ") + str(f.framework_name) + bstack1l1l_opy_ (u"ࠧࠨᇧ"))
                return
            command_name = f.bstack1ll111ll111_opy_(*args)
            if not command_name:
                self.logger.debug(bstack1l1l_opy_ (u"ࠨ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬࠮ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࡾࠢࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫࠽ࠣᇨ") + str(method_name) + bstack1l1l_opy_ (u"ࠢࠣᇩ"))
                return
            bstack1l1llll111l_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll11l1_opy_, False)
            if command_name == bstack1l1l_opy_ (u"ࠣࡩࡨࡸࠧᇪ") and not bstack1l1llll111l_opy_:
                f.bstack1llll1lll11_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll11l1_opy_, True)
                bstack1l1llll111l_opy_ = True
            if not bstack1l1llll111l_opy_ and not self.bstack1ll111llll1_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠤࡱࡳ࡛ࠥࡒࡍࠢ࡯ࡳࡦࡪࡥࡥࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᇫ") + str(command_name) + bstack1l1l_opy_ (u"ࠥࠦᇬ"))
                return
            scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(command_name, [])
            if not scripts_to_run:
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡳࡵࠠࡢ࠳࠴ࡽࠥࡹࡣࡳ࡫ࡳࡸࡸࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬࠮ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࡾࠢࡦࡳࡲࡳࡡ࡯ࡦࡢࡲࡦࡳࡥ࠾ࠤᇭ") + str(command_name) + bstack1l1l_opy_ (u"ࠧࠨᇮ"))
                return
            self.logger.info(bstack1l1l_opy_ (u"ࠨࡲࡶࡰࡱ࡭ࡳ࡭ࠠࡼ࡮ࡨࡲ࠭ࡹࡣࡳ࡫ࡳࡸࡸࡥࡴࡰࡡࡵࡹࡳ࠯ࡽࠡࡵࡦࡶ࡮ࡶࡴࡴࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᇯ") + str(command_name) + bstack1l1l_opy_ (u"ࠢࠣᇰ"))
            scripts = [(s, bstack1ll1111ll11_opy_[s]) for s in scripts_to_run if s in bstack1ll1111ll11_opy_]
            for script_name, bstack1ll111111l1_opy_ in scripts:
                try:
                    bstack1ll111l1_opy_ = datetime.now()
                    if script_name == bstack1l1l_opy_ (u"ࠣࡵࡦࡥࡳࠨᇱ"):
                        result = self.perform_scan(driver, method=command_name, framework_name=f.framework_name)
                    instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡤ࠵࠶ࡿ࠺ࠣᇲ") + script_name, datetime.now() - bstack1ll111l1_opy_)
                    if isinstance(result, dict) and not result.get(bstack1l1l_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦᇳ"), True):
                        self.logger.warning(bstack1l1l_opy_ (u"ࠦࡸࡱࡩࡱࠢࡨࡼࡪࡩࡵࡵ࡫ࡱ࡫ࠥࡸࡥ࡮ࡣ࡬ࡲ࡮ࡴࡧࠡࡵࡦࡶ࡮ࡶࡴࡴ࠼ࠣࠦᇴ") + str(result) + bstack1l1l_opy_ (u"ࠧࠨᇵ"))
                        break
                except Exception as e:
                    self.logger.error(bstack1l1l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡴࡧࠡࡵࡦࡶ࡮ࡶࡴ࠾ࡽࡶࡧࡷ࡯ࡰࡵࡡࡱࡥࡲ࡫ࡽࠡࡧࡵࡶࡴࡸ࠽ࠣᇶ") + str(e) + bstack1l1l_opy_ (u"ࠢࠣᇷ"))
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩࠥ࡫ࡲࡳࡱࡵࡁࠧᇸ") + str(e) + bstack1l1l_opy_ (u"ࠤࠥᇹ"))
    def bstack1ll111l1111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llll1llll1_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll111lll11_opy_(instance, args)
        capabilities = self.bstack1ll11l1lll1_opy_.bstack1l1llll1l11_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        self.accessibility = self.bstack1ll111l1l11_opy_(tags, capabilities)
        if not self.accessibility:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠢᇺ"))
            return
        driver = self.bstack1ll11l1lll1_opy_.bstack1ll11l1l11l_opy_(f, instance, bstack1llll1llll1_opy_, *args, **kwargs)
        test_name = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll111l1l1l_opy_)
        if not test_name:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡳࡧ࡭ࡦࠤᇻ"))
            return
        test_uuid = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l1ll1l_opy_)
        if not test_uuid:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡻࡵࡪࡦࠥᇼ"))
            return
        if isinstance(self.bstack1ll11l1lll1_opy_, bstack1lll11l1l1l_opy_):
            framework_name = bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᇽ")
        else:
            framework_name = bstack1l1l_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩᇾ")
        self.bstack11llll1ll_opy_(driver, test_name, framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1lll11l111_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡࡣ࠴࠵ࡾࠦ࡮ࡰࡶࠣࡩࡳࡧࡢ࡭ࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࠤᇿ"))
            return
        bstack1ll111l1_opy_ = datetime.now()
        bstack1ll111111l1_opy_ = self.scripts.get(framework_name, {}).get(bstack1l1l_opy_ (u"ࠤࡶࡧࡦࡴࠢሀ"), None)
        if not bstack1ll111111l1_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡴࡪࡸࡦࡰࡴࡰࡣࡸࡩࡡ࡯࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࠬࡹࡣࡢࡰࠪࠤࡸࡩࡲࡪࡲࡷࠤ࡫ࡵࡲࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࠥሁ") + str(framework_name) + bstack1l1l_opy_ (u"ࠦࠥࠨሂ"))
            return
        if self.bstack1ll111llll1_opy_:
            arg = dict()
            arg[bstack1l1l_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠧሃ")] = method if method else bstack1l1l_opy_ (u"ࠨࠢሄ")
            arg[bstack1l1l_opy_ (u"ࠢࡵࡪࡗࡩࡸࡺࡒࡶࡰࡘࡹ࡮ࡪࠢህ")] = self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠣሆ")]
            arg[bstack1l1l_opy_ (u"ࠤࡷ࡬ࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠢሇ")] = self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡧࡻࡩ࡭ࡦࡢࡹࡺ࡯ࡤࠣለ")]
            arg[bstack1l1l_opy_ (u"ࠦࡦࡻࡴࡩࡊࡨࡥࡩ࡫ࡲࠣሉ")] = self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠧࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽ࡙ࡵ࡫ࡦࡰࠥሊ")]
            arg[bstack1l1l_opy_ (u"ࠨࡴࡩࡌࡺࡸ࡙ࡵ࡫ࡦࡰࠥላ")] = self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠢࡵࡪࡢ࡮ࡼࡺ࡟ࡵࡱ࡮ࡩࡳࠨሌ")]
            arg[bstack1l1l_opy_ (u"ࠣࡵࡦࡥࡳ࡚ࡩ࡮ࡧࡶࡸࡦࡳࡰࠣል")] = str(int(datetime.now().timestamp() * 1000))
            bstack1l1llllll11_opy_ = self.bstack1ll1111l111_opy_(bstack1l1l_opy_ (u"ࠤࡶࡧࡦࡴࠢሎ"), self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥሏ")])
            if bstack1l1l_opy_ (u"ࠦࡨ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡖࡲ࡯ࡪࡴࠢሐ") in bstack1l1llllll11_opy_:
                bstack1l1llllll11_opy_ = bstack1l1llllll11_opy_.copy()
                bstack1l1llllll11_opy_[bstack1l1l_opy_ (u"ࠧࡩࡥ࡯ࡶࡵࡥࡱࡇࡵࡵࡪࡋࡩࡦࡪࡥࡳࠤሑ")] = bstack1l1llllll11_opy_.pop(bstack1l1l_opy_ (u"ࠨࡣࡦࡰࡷࡶࡦࡲࡁࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠤሒ"))
            arg = bstack1l1llll1ll1_opy_(arg, bstack1l1llllll11_opy_)
            bstack1ll11l1l111_opy_ = bstack1ll111111l1_opy_ % json.dumps(arg)
            driver.execute_script(bstack1ll11l1l111_opy_)
            return
        instance = bstack1llll1ll1ll_opy_.bstack1lll1llll11_opy_(driver)
        if instance:
            if not bstack1llll1ll1ll_opy_.bstack1llll1l11ll_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll11ll_opy_, False):
                bstack1llll1ll1ll_opy_.bstack1llll1lll11_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll11ll_opy_, True)
            else:
                self.logger.info(bstack1l1l_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࡀࠠࡢ࡮ࡵࡩࡦࡪࡹࠡ࡫ࡱࠤࡵࡸ࡯ࡨࡴࡨࡷࡸࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࡼࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࡱࡪࡺࡨࡰࡦࡀࠦሓ") + str(method) + bstack1l1l_opy_ (u"ࠣࠤሔ"))
                return
        self.logger.info(bstack1l1l_opy_ (u"ࠤࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮࠻ࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࢂࠦ࡭ࡦࡶ࡫ࡳࡩࡃࠢሕ") + str(method) + bstack1l1l_opy_ (u"ࠥࠦሖ"))
        if framework_name == bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨሗ"):
            result = self.bstack1ll11l1lll1_opy_.bstack1ll1111111l_opy_(driver, bstack1ll111111l1_opy_)
        else:
            result = driver.execute_async_script(bstack1ll111111l1_opy_, {bstack1l1l_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠧመ"): method if method else bstack1l1l_opy_ (u"ࠨࠢሙ")})
        bstack1ll1l1ll111_opy_.end(EVENTS.bstack1lll11l111_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢሚ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠣ࠼ࡨࡲࡩࠨማ"), True, None, command=method)
        if instance:
            bstack1llll1ll1ll_opy_.bstack1llll1lll11_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll11ll_opy_, False)
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡤ࠵࠶ࡿ࠺ࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࠨሜ"), datetime.now() - bstack1ll111l1_opy_)
        return result
        def bstack1ll11l1111l_opy_(self, driver: object, framework_name, result_type: str):
            self.bstack1ll11l1ll11_opy_()
            req = structs.AccessibilityResultRequest()
            req.bin_session_id = self.bin_session_id
            req.bstack1l1lll1ll11_opy_ = self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥም")]
            req.result_type = result_type
            req.session_id = self.bin_session_id
            try:
                r = self.bstack1ll1l11111l_opy_.AccessibilityResult(req)
                if not r.success:
                    self.logger.debug(bstack1l1l_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨሞ") + str(r) + bstack1l1l_opy_ (u"ࠧࠨሟ"))
                else:
                    bstack1l1lll1llll_opy_ = json.loads(r.bstack1ll111ll11l_opy_.decode(bstack1l1l_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬሠ")))
                    if result_type == bstack1l1l_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠫሡ"):
                        return bstack1l1lll1llll_opy_.get(bstack1l1l_opy_ (u"ࠣࡦࡤࡸࡦࠨሢ"), [])
                    else:
                        return bstack1l1lll1llll_opy_.get(bstack1l1l_opy_ (u"ࠤࡧࡥࡹࡧࠢሣ"), {})
            except grpc.RpcError as e:
                self.logger.error(bstack1l1l_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥ࡬ࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡨࡧࡷࡣࡦࡶࡰࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࠡࡨࡵࡳࡲࠦࡣ࡭࡫࠽ࠤࠧሤ") + str(e) + bstack1l1l_opy_ (u"ࠦࠧሥ"))
    @measure(event_name=EVENTS.bstack111l1ll1l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡵࡩࡸࡻ࡬ࡵࡵ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠢሦ"))
            return
        if self.bstack1ll111llll1_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡨࡲࡶࠥࡧࡰࡱࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩሧ"))
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll11l1111l_opy_(driver, framework_name, bstack1l1l_opy_ (u"ࠢࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠦረ"))
        bstack1ll111111l1_opy_ = self.scripts.get(framework_name, {}).get(bstack1l1l_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠧሩ"), None)
        if not bstack1ll111111l1_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣሪ") + str(framework_name) + bstack1l1l_opy_ (u"ࠥࠦራ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1ll111l1_opy_ = datetime.now()
        if framework_name == bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨሬ"):
            result = self.bstack1ll11l1lll1_opy_.bstack1ll1111111l_opy_(driver, bstack1ll111111l1_opy_)
        else:
            result = driver.execute_async_script(bstack1ll111111l1_opy_)
        instance = bstack1llll1ll1ll_opy_.bstack1lll1llll11_opy_(driver)
        if instance:
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠧࡧ࠱࠲ࡻ࠽࡫ࡪࡺ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡳࡧࡶࡹࡱࡺࡳࠣር"), datetime.now() - bstack1ll111l1_opy_)
        return result
    @measure(event_name=EVENTS.bstack1lllll11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack1l1l_opy_ (u"ࠨࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡶࡪࡹࡵ࡭ࡶࡶࡣࡸࡻ࡭࡮ࡣࡵࡽ࠿ࠦࡡ࠲࠳ࡼࠤࡳࡵࡴࠡࡧࡱࡥࡧࡲࡥࡥࠤሮ"))
            return
        if self.bstack1ll111llll1_opy_:
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll11l1111l_opy_(driver, framework_name, bstack1l1l_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠫሯ"))
        bstack1ll111111l1_opy_ = self.scripts.get(framework_name, {}).get(bstack1l1l_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࡘࡻ࡭࡮ࡣࡵࡽࠧሰ"), None)
        if not bstack1ll111111l1_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣሱ") + str(framework_name) + bstack1l1l_opy_ (u"ࠥࠦሲ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1ll111l1_opy_ = datetime.now()
        if framework_name == bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨሳ"):
            result = self.bstack1ll11l1lll1_opy_.bstack1ll1111111l_opy_(driver, bstack1ll111111l1_opy_)
        else:
            result = driver.execute_async_script(bstack1ll111111l1_opy_)
        instance = bstack1llll1ll1ll_opy_.bstack1lll1llll11_opy_(driver)
        if instance:
            instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠧࡧ࠱࠲ࡻ࠽࡫ࡪࡺ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡳࡧࡶࡹࡱࡺࡳࡠࡵࡸࡱࡲࡧࡲࡺࠤሴ"), datetime.now() - bstack1ll111l1_opy_)
        return result
    @measure(event_name=EVENTS.bstack1l1lllll1l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1ll1111l1l1_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1ll11l1ll11_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack1ll1l11111l_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣስ") + str(r) + bstack1l1l_opy_ (u"ࠢࠣሶ"))
            else:
                self.bstack1ll111lllll_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨሷ") + str(e) + bstack1l1l_opy_ (u"ࠤࠥሸ"))
            traceback.print_exc()
            raise e
    def bstack1ll111lllll_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡰࡴࡧࡤࡠࡥࡲࡲ࡫࡯ࡧ࠻ࠢࡤ࠵࠶ࡿࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦࠥሹ"))
            return False
        if result.accessibility.is_app_accessibility:
            self.bstack1ll111llll1_opy_ = result.accessibility.is_app_accessibility
        if result.testhub.build_hashed_id:
            self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠦࡹ࡫ࡳࡵࡪࡸࡦࡤࡨࡵࡪ࡮ࡧࡣࡺࡻࡩࡥࠤሺ")] = result.testhub.build_hashed_id
        if result.testhub.jwt:
            self.bstack1ll111l11l1_opy_[bstack1l1l_opy_ (u"ࠧࡺࡨࡠ࡬ࡺࡸࡤࡺ࡯࡬ࡧࡱࠦሻ")] = result.testhub.jwt
        if result.accessibility.options:
            options = result.accessibility.options
            if options.capabilities:
                for caps in options.capabilities:
                    self.bstack1ll111l11l1_opy_[caps.name] = caps.value
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1ll11111111_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1ll11111ll1_opy_ and command.module == self.bstack1ll111111ll_opy_:
                        if command.method and not command.method in bstack1ll11111111_opy_:
                            bstack1ll11111111_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1ll11111111_opy_[command.method]:
                            bstack1ll11111111_opy_[command.method][command.name] = list()
                        bstack1ll11111111_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1ll11111111_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1l1lll1lll1_opy_(
        self,
        f: bstack1ll1lll1lll_opy_,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if isinstance(self.bstack1ll11l1lll1_opy_, bstack1lll11l1l1l_opy_) and method_name != bstack1l1l_opy_ (u"࠭ࡣࡰࡰࡱࡩࡨࡺࠧሼ"):
            return
        if bstack1llll1ll1ll_opy_.bstack1llll1l1l11_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll1l1l_opy_):
            return
        if f.bstack1ll11l11111_opy_(method_name, *args):
            bstack1ll1111ll1l_opy_ = False
            desired_capabilities = f.bstack1ll111l1ll1_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1ll111l1lll_opy_(instance)
                platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1lll1lll_opy_.bstack1l1llllll1l_opy_, 0)
                bstack1ll11l1l1l1_opy_ = datetime.now()
                r = self.bstack1ll1111l1l1_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡩ࡯࡯ࡨ࡬࡫ࠧሽ"), datetime.now() - bstack1ll11l1l1l1_opy_)
                bstack1ll1111ll1l_opy_ = r.success
            else:
                self.logger.error(bstack1l1l_opy_ (u"ࠣ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡧࡩࡸ࡯ࡲࡦࡦࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠿ࠥሾ") + str(desired_capabilities) + bstack1l1l_opy_ (u"ࠤࠥሿ"))
            f.bstack1llll1lll11_opy_(instance, bstack1ll1l1l111l_opy_.bstack1l1llll1l1l_opy_, bstack1ll1111ll1l_opy_)
    def bstack1l111lll_opy_(self, test_tags):
        bstack1ll1111l1l1_opy_ = self.config.get(bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪቀ"))
        if not bstack1ll1111l1l1_opy_:
            return True
        try:
            include_tags = bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩቁ")] if bstack1l1l_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪቂ") in bstack1ll1111l1l1_opy_ and isinstance(bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫቃ")], list) else []
            exclude_tags = bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬቄ")] if bstack1l1l_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ቅ") in bstack1ll1111l1l1_opy_ and isinstance(bstack1ll1111l1l1_opy_[bstack1l1l_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧቆ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡸࡤࡰ࡮ࡪࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡨࡲࡶࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡨࡥࡧࡱࡵࡩࠥࡹࡣࡢࡰࡱ࡭ࡳ࡭࠮ࠡࡇࡵࡶࡴࡸࠠ࠻ࠢࠥቇ") + str(error))
        return False
    def bstack1111ll1l_opy_(self, caps):
        try:
            if self.bstack1ll111llll1_opy_:
                bstack1l1llllllll_opy_ = caps.get(bstack1l1l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥቈ"))
                if bstack1l1llllllll_opy_ is not None and str(bstack1l1llllllll_opy_).lower() == bstack1l1l_opy_ (u"ࠧࡧ࡮ࡥࡴࡲ࡭ࡩࠨ቉"):
                    bstack1ll111l11ll_opy_ = caps.get(bstack1l1l_opy_ (u"ࠨࡡࡱࡲ࡬ࡹࡲࡀࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣቊ")) or caps.get(bstack1l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤቋ"))
                    if bstack1ll111l11ll_opy_ is not None and int(bstack1ll111l11ll_opy_) < 11:
                        self.logger.warning(bstack1l1l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡃࡱࡨࡷࡵࡩࡥࠢ࠴࠵ࠥࡧ࡮ࡥࠢࡤࡦࡴࡼࡥ࠯ࠢࡆࡹࡷࡸࡥ࡯ࡶࠣࡴࡱࡧࡴࡧࡱࡵࡱࠥࡼࡥࡳࡵ࡬ࡳࡳࠦ࠽ࠣቌ") + str(bstack1ll111l11ll_opy_) + bstack1l1l_opy_ (u"ࠤࠥቍ"))
                        return False
                return True
            bstack1l1lll1ll1l_opy_ = caps.get(bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ቎"), {}).get(bstack1l1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨ቏"), caps.get(bstack1l1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬቐ"), bstack1l1l_opy_ (u"࠭ࠧቑ")))
            if bstack1l1lll1ll1l_opy_:
                self.logger.warning(bstack1l1l_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡅࡧࡶ࡯ࡹࡵࡰࠡࡤࡵࡳࡼࡹࡥࡳࡵ࠱ࠦቒ"))
                return False
            browser = caps.get(bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ቓ"), bstack1l1l_opy_ (u"ࠩࠪቔ")).lower()
            if browser != bstack1l1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪቕ"):
                self.logger.warning(bstack1l1l_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢቖ"))
                return False
            bstack1ll11111lll_opy_ = bstack1ll1111llll_opy_
            if not self.config.get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ቗")) or self.config.get(bstack1l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪቘ")):
                bstack1ll11111lll_opy_ = bstack1ll111ll1l1_opy_
            browser_version = caps.get(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ቙"))
            if not browser_version:
                browser_version = caps.get(bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩቚ"), {}).get(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪቛ"), bstack1l1l_opy_ (u"ࠪࠫቜ"))
            bstack1ll11l11ll1_opy_ = str(browser_version).lower() if browser_version is not None else bstack1l1l_opy_ (u"ࠫࠬቝ")
            if bstack1ll11l11ll1_opy_:
                if bstack1ll11l11ll1_opy_.startswith(bstack1l1l_opy_ (u"ࠬࡲࡡࡵࡧࡶࡸࠬ቞")):
                    if bstack1ll11l11ll1_opy_.startswith(bstack1l1l_opy_ (u"࠭࡬ࡢࡶࡨࡷࡹ࠳ࠧ቟")):
                        bstack1ll1111lll1_opy_ = bstack1ll11l11ll1_opy_[len(bstack1l1l_opy_ (u"ࠧ࡭ࡣࡷࡩࡸࡺ࠭ࠨበ")):]
                        if bstack1ll1111lll1_opy_ and not bstack1ll1111lll1_opy_.isdigit():
                            self.logger.warning(bstack1l1l_opy_ (u"ࠣࡋࡱࡺࡦࡲࡩࡥࠢࡥࡶࡴࡽࡳࡦࡴࠣࡺࡪࡸࡳࡪࡱࡱࠤ࡫ࡵࡲ࡮ࡣࡷࠤࠬࠨቡ") + str(browser_version) + bstack1l1l_opy_ (u"ࠤࠪ࠿ࠥ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࠨ࡮ࡤࡸࡪࡹࡴࠨࠢࡲࡶࠥ࠭࡬ࡢࡶࡨࡷࡹ࠳࠼࡯ࡷࡰࡦࡪࡸ࠾ࠨ࠰ࠥቢ"))
                            return False
                else:
                    try:
                        if int(bstack1ll11l11ll1_opy_.split(bstack1l1l_opy_ (u"ࠪ࠲ࠬባ"))[0]) <= bstack1ll11111lll_opy_:
                            self.logger.warning(bstack1l1l_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡧࡳࡧࡤࡸࡪࡸࠠࡵࡪࡤࡲࠥࠨቤ") + str(bstack1ll11111lll_opy_) + bstack1l1l_opy_ (u"ࠧ࠴ࠢብ"))
                            return False
                    except (ValueError, IndexError) as e:
                        self.logger.debug(bstack1l1l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡤࡵࡳࡼࡹࡥࡳࠢࡹࡩࡷࡹࡩࡰࡰࠣࠫࢀࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࡽࠨ࠼ࠣࠦቦ") + str(e) + bstack1l1l_opy_ (u"ࠢࠣቧ"))
            bstack1l1lllll111_opy_ = caps.get(bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩቨ"), {}).get(bstack1l1l_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩቩ"))
            if not bstack1l1lllll111_opy_:
                bstack1l1lllll111_opy_ = caps.get(bstack1l1l_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨቪ"), {})
            if bstack1l1lllll111_opy_ and bstack1l1l_opy_ (u"ࠫ࠲࠳ࡨࡦࡣࡧࡰࡪࡹࡳࠨቫ") in bstack1l1lllll111_opy_.get(bstack1l1l_opy_ (u"ࠬࡧࡲࡨࡵࠪቬ"), []):
                self.logger.warning(bstack1l1l_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡰࡲࡸࠥࡸࡵ࡯ࠢࡲࡲࠥࡲࡥࡨࡣࡦࡽࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠦࡓࡸ࡫ࡷࡧ࡭ࠦࡴࡰࠢࡱࡩࡼࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪࠦ࡯ࡳࠢࡤࡺࡴ࡯ࡤࠡࡷࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠣቭ"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡶࡢ࡮࡬ࡨࡦࡺࡥࠡࡣ࠴࠵ࡾࠦࡳࡶࡲࡳࡳࡷࡺࠠ࠻ࠤቮ") + str(error))
            return False
    def bstack1l1lllll11l_opy_(self, test_uuid: str, result: structs.FetchDriverExecuteParamsEventResponse):
        bstack1l1llll1lll_opy_ = {
            bstack1l1l_opy_ (u"ࠨࡶ࡫ࡘࡪࡹࡴࡓࡷࡱ࡙ࡺ࡯ࡤࠨቯ"): test_uuid,
        }
        bstack1l1lll1l1ll_opy_ = {}
        if result.success:
            bstack1l1lll1l1ll_opy_ = json.loads(result.accessibility_execute_params)
        return bstack1l1llll1ll1_opy_(bstack1l1llll1lll_opy_, bstack1l1lll1l1ll_opy_)
    def bstack1ll1111l111_opy_(self, script_name: str, test_uuid: str) -> dict:
        bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡆࡦࡶࡦ࡬ࠥࡩࡥ࡯ࡶࡵࡥࡱࠦࡡࡶࡶ࡫ࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡸࡩࡲࡪࡲࡷࠤࡳࡧ࡭ࡦ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷࠥࡩࡡࡤࡪࡨࡨࠥࡩ࡯࡯ࡨ࡬࡫ࠥ࡯ࡦࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡩࡩࡹࡩࡨࡦࡦ࠯ࠤࡴࡺࡨࡦࡴࡺ࡭ࡸ࡫ࠠ࡭ࡱࡤࡨࡸࠦࡡ࡯ࡦࠣࡧࡦࡩࡨࡦࡵࠣ࡭ࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡹࡣࡳ࡫ࡳࡸࡤࡴࡡ࡮ࡧ࠽ࠤࡓࡧ࡭ࡦࠢࡲࡪࠥࡺࡨࡦࠢࡶࡧࡷ࡯ࡰࡵࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡫ࡵࡲࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡴࡦࡵࡷࡣࡺࡻࡩࡥ࠼࡙࡚ࠣࡏࡄࠡࡱࡩࠤࡹ࡮ࡥࠡࡶࡨࡷࡹࠦࡲࡶࡰࠣࡪࡴࡸࠠࡸࡪ࡬ࡧ࡭ࠦࡴࡰࠢࡩࡩࡹࡩࡨࠡࡥࡲࡲ࡫࡯ࡧࠋࠢࠣࠤࠥࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡧ࡭ࡨࡺ࠺ࠡࡅࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽ࠱ࠦࡥ࡮ࡲࡷࡽࠥࡪࡩࡤࡶࠣ࡭࡫ࠦࡥࡳࡴࡲࡶࠥࡵࡣࡤࡷࡵࡷࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤተ")
        try:
            if self.bstack1ll11l11l11_opy_:
                return self.bstack1ll1111l11l_opy_
            self.bstack1ll11l1ll11_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack1l1l_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥቱ")
            req.script_name = script_name
            r = self.bstack1ll1l11111l_opy_.FetchDriverExecuteParamsEvent(req)
            if r.success:
                self.bstack1ll1111l11l_opy_ = self.bstack1l1lllll11l_opy_(test_uuid, r)
                self.bstack1ll11l11l11_opy_ = True
            else:
                self.logger.error(bstack1l1l_opy_ (u"ࠦ࡫࡫ࡴࡤࡪࡆࡩࡳࡺࡲࡢ࡮ࡄࡹࡹ࡮ࡁ࠲࠳ࡼࡇࡴࡴࡦࡪࡩ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡧࡧࡷࡧ࡭ࠦࡤࡳ࡫ࡹࡩࡷࠦࡥࡹࡧࡦࡹࡹ࡫ࠠࡱࡣࡵࡥࡲࡹࠠࡧࡱࡵࠤࢀࡹࡣࡳ࡫ࡳࡸࡤࡴࡡ࡮ࡧࢀ࠾ࠥࠨቲ") + str(r.error) + bstack1l1l_opy_ (u"ࠧࠨታ"))
                self.bstack1ll1111l11l_opy_ = dict()
            return self.bstack1ll1111l11l_opy_
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠨࡦࡦࡶࡦ࡬ࡈ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡃ࠴࠵ࡾࡉ࡯࡯ࡨ࡬࡫࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡩࡩࡹࡩࡨࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡧࡻࡩࡨࡻࡴࡦࠢࡳࡥࡷࡧ࡭ࡴࠢࡩࡳࡷࠦࡻࡴࡥࡵ࡭ࡵࡺ࡟࡯ࡣࡰࡩࢂࡀࠠࠣቴ") + str(traceback.format_exc()) + bstack1l1l_opy_ (u"ࠢࠣት"))
            return dict()
    def bstack11llll1ll_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1ll11l111l1_opy_ = None
        try:
            self.bstack1ll11l1ll11_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack1l1l_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣቶ")
            req.script_name = bstack1l1l_opy_ (u"ࠤࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠢቷ")
            r = self.bstack1ll1l11111l_opy_.FetchDriverExecuteParamsEvent(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥࡪࡲࡪࡸࡨࡶࠥ࡫ࡸࡦࡥࡸࡸࡪࠦࡰࡢࡴࡤࡱࡸࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨቸ") + str(r.error) + bstack1l1l_opy_ (u"ࠦࠧቹ"))
            else:
                bstack1l1llll1lll_opy_ = self.bstack1l1lllll11l_opy_(test_uuid, r)
                bstack1ll111111l1_opy_ = r.script
            self.logger.debug(bstack1l1l_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡣࡹ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠨቺ") + str(bstack1l1llll1lll_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            if not bstack1ll111111l1_opy_:
                self.logger.debug(bstack1l1l_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳ࡟ࡴࡥࡤࡲ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࠨࡵࡤࡺࡪࡘࡥࡴࡷ࡯ࡸࡸ࠭ࠠࡴࡥࡵ࡭ࡵࡺࠠࡧࡱࡵࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࠨቻ") + str(framework_name) + bstack1l1l_opy_ (u"ࠢࠡࠤቼ"))
                return
            bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack1ll11l1llll_opy_(EVENTS.bstack1ll11111l1l_opy_.value)
            self.bstack1ll111ll1ll_opy_(driver, bstack1ll111111l1_opy_, bstack1l1llll1lll_opy_, framework_name)
            self.logger.info(bstack1l1l_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡶࡨࡷࡹ࡯࡮ࡨࠢࡩࡳࡷࠦࡴࡩ࡫ࡶࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡩࡣࡶࠤࡪࡴࡤࡦࡦ࠱ࠦች"))
            bstack1ll1l1ll111_opy_.end(EVENTS.bstack1ll11111l1l_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤቾ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠥ࠾ࡪࡴࡤࠣቿ"), True, None, command=bstack1l1l_opy_ (u"ࠫࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠩኀ"),test_name=name)
        except Exception as bstack1l1lllll1ll_opy_:
            self.logger.error(bstack1l1l_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡨࡲࡶࠥࡺࡨࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩ࠿ࠦࠢኁ") + bstack1l1l_opy_ (u"ࠨࡳࡵࡴࠫࡴࡦࡺࡨࠪࠤኂ") + bstack1l1l_opy_ (u"ࠢࠡࡇࡵࡶࡴࡸࠠ࠻ࠤኃ") + str(bstack1l1lllll1ll_opy_))
            bstack1ll1l1ll111_opy_.end(EVENTS.bstack1ll11111l1l_opy_.value, bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣኄ"), bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠤ࠽ࡩࡳࡪࠢኅ"), False, bstack1l1lllll1ll_opy_, command=bstack1l1l_opy_ (u"ࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨኆ"),test_name=name)
    def bstack1ll111ll1ll_opy_(self, driver, bstack1ll111111l1_opy_, bstack1l1llll1lll_opy_, framework_name):
        if framework_name == bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨኇ"):
            self.bstack1ll11l1lll1_opy_.bstack1ll1111111l_opy_(driver, bstack1ll111111l1_opy_, bstack1l1llll1lll_opy_)
        else:
            self.logger.debug(driver.execute_async_script(bstack1ll111111l1_opy_, bstack1l1llll1lll_opy_))
    def _1ll111lll11_opy_(self, instance: bstack1lll111l1ll_opy_, args: Tuple) -> list:
        bstack1l1l_opy_ (u"ࠧࠨࠢࡆࡺࡷࡶࡦࡩࡴࠡࡶࡤ࡫ࡸࠦࡢࡢࡵࡨࡨࠥࡵ࡮ࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠴ࠢࠣࠤኈ")
        if bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠪ኉") in instance.bstack1ll11l111ll_opy_:
            return args[2].tags if hasattr(args[2], bstack1l1l_opy_ (u"ࠧࡵࡣࡪࡷࠬኊ")) else []
        if hasattr(args[0], bstack1l1l_opy_ (u"ࠨࡱࡺࡲࡤࡳࡡࡳ࡭ࡨࡶࡸ࠭ኋ")):
            return [marker.name for marker in args[0].own_markers]
        return []
    def bstack1ll111l1l11_opy_(self, tags, capabilities):
        return self.bstack1l111lll_opy_(tags) and self.bstack1111ll1l_opy_(capabilities)