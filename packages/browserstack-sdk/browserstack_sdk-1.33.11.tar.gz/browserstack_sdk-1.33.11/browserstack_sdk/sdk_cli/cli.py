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
import subprocess
import threading
import time
import sys
import grpc
import os
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lllll1ll1l_opy_ import bstack1lllll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l11l111_opy_ import bstack1ll1l1l111l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll11ll_opy_ import bstack1ll11llllll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1l1l1_opy_ import bstack1lll1lll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll11lll11l_opy_ import bstack1ll1ll111ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllll11_opy_ import bstack1ll11lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllll1l_opy_ import bstack1lll111llll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111lll_opy_ import bstack1lll11l1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1ll1l111l1l_opy_
from browserstack_sdk.sdk_cli.bstack111l111l_opy_ import bstack111l111l_opy_, bstack11l111111_opy_, bstack11lll1l1l1_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1ll1ll11lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll111l1l1_opy_ import bstack1ll1lll1lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1llll1ll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11llll1l_opy_ import bstack1ll1l1lllll_opy_
from bstack_utils.helper import Notset, bstack1ll1l111ll1_opy_, get_cli_dir, bstack1lll1ll111l_opy_, bstack11ll111l11_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from browserstack_sdk.sdk_cli.utils.bstack1lll1l11lll_opy_ import bstack1ll1l1ll1ll_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11ll1l1l_opy_ import bstack1l1111llll_opy_
from bstack_utils.helper import Notset, bstack1ll1l111ll1_opy_, get_cli_dir, bstack1lll1ll111l_opy_, bstack11ll111l11_opy_, bstack11l11llll_opy_, bstack11llll11l1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1lll111l1ll_opy_, bstack1ll1ll111l1_opy_, bstack1lll1l11l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1lllll11l1l_opy_, bstack1llll11ll11_opy_, bstack1llll1ll111_opy_
from bstack_utils.constants import *
from bstack_utils.bstack111ll11l1_opy_ import bstack1l11llll1_opy_
from bstack_utils import bstack1lllllll1l_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11lllll1l_opy_, bstack11lll1l11l_opy_
logger = bstack1lllllll1l_opy_.get_logger(__name__, bstack1lllllll1l_opy_.bstack1ll1ll1ll11_opy_())
def bstack1ll1l1l11l1_opy_(bs_config):
    bstack1lll11lll1l_opy_ = None
    bstack1ll1ll1111l_opy_ = None
    try:
        bstack1ll1ll1111l_opy_ = get_cli_dir()
        bstack1lll11lll1l_opy_ = bstack1lll1ll111l_opy_(bstack1ll1ll1111l_opy_)
        bstack1lll11l1111_opy_ = bstack1ll1l111ll1_opy_(bstack1lll11lll1l_opy_, bstack1ll1ll1111l_opy_, bs_config)
        bstack1lll11lll1l_opy_ = bstack1lll11l1111_opy_ if bstack1lll11l1111_opy_ else bstack1lll11lll1l_opy_
        if not bstack1lll11lll1l_opy_:
            raise ValueError(bstack1l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡕࡇࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡐࡂࡖࡋࠦჴ"))
    except Exception as ex:
        logger.debug(bstack1l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡹ࡮ࡥࠡ࡮ࡤࡸࡪࡹࡴࠡࡤ࡬ࡲࡦࡸࡹࠡࡽࢀࠦჵ").format(ex))
        bstack1lll11lll1l_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡑࡃࡗࡌࠧჶ"))
        if bstack1lll11lll1l_opy_:
            logger.debug(bstack1l1l_opy_ (u"ࠥࡊࡦࡲ࡬ࡪࡰࡪࠤࡧࡧࡣ࡬ࠢࡷࡳ࡙ࠥࡄࡌࡡࡆࡐࡎࡥࡂࡊࡐࡢࡔࡆ࡚ࡈࠡࡨࡵࡳࡲࠦࡥ࡯ࡸ࡬ࡶࡴࡴ࡭ࡦࡰࡷ࠾ࠥࠨჷ") + str(bstack1lll11lll1l_opy_) + bstack1l1l_opy_ (u"ࠦࠧჸ"))
        else:
            logger.debug(bstack1l1l_opy_ (u"ࠧࡔ࡯ࠡࡸࡤࡰ࡮ࡪࠠࡔࡆࡎࡣࡈࡒࡉࡠࡄࡌࡒࡤࡖࡁࡕࡊࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶ࠾ࠤࡸ࡫ࡴࡶࡲࠣࡱࡦࡿࠠࡣࡧࠣ࡭ࡳࡩ࡯࡮ࡲ࡯ࡩࡹ࡫࠮ࠣჹ"))
    return bstack1lll11lll1l_opy_, bstack1ll1ll1111l_opy_
bstack1ll1l11l1ll_opy_ = bstack1l1l_opy_ (u"ࠨ࠹࠺࠻࠼ࠦჺ")
bstack1ll1l11l11l_opy_ = bstack1l1l_opy_ (u"ࠢࡳࡧࡤࡨࡾࠨ჻")
bstack1ll1lllllll_opy_ = bstack1l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡕࡈࡗࡘࡏࡏࡏࡡࡌࡈࠧჼ")
bstack1lll11l11l1_opy_ = bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡏࡍࡘ࡚ࡅࡏࡡࡄࡈࡉࡘࠢჽ")
bstack1l1lll11l1_opy_ = bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓࠨჾ")
bstack1ll1lll11ll_opy_ = re.compile(bstack1l1l_opy_ (u"ࡶࠧ࠮࠿ࡪࠫ࠱࠮࠭ࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࢀࡇ࡙ࠩ࠯ࠬࠥჿ"))
bstack1lll11l1l11_opy_ = bstack1l1l_opy_ (u"ࠧࡪࡥࡷࡧ࡯ࡳࡵࡳࡥ࡯ࡶࠥᄀ")
bstack1ll1l1l1111_opy_ = bstack1l1l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡏࡓࡅࡈࡣࡋࡇࡌࡍࡄࡄࡇࡐࠨᄁ")
bstack1lll111ll1l_opy_ = [
    bstack11l111111_opy_.bstack1llll1ll1l_opy_,
    bstack11l111111_opy_.CONNECT,
    bstack11l111111_opy_.bstack1llll11l1l_opy_,
]
class SDKCLI:
    _1ll1ll1l1ll_opy_ = None
    process: Union[None, Any]
    bstack1lll1l1l111_opy_: bool
    bstack1ll1ll1llll_opy_: bool
    bstack1ll1l1llll1_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack1ll1l111l11_opy_: Union[None, grpc.Channel]
    bstack1ll1l1111ll_opy_: str
    test_framework: TestFramework
    bstack1lll1llllll_opy_: bstack1llll1ll1ll_opy_
    session_framework: str
    config: Union[None, Dict[str, Any]]
    bstack1ll1l11lll1_opy_: bstack1ll1l111l1l_opy_
    accessibility: bstack1ll1l1l111l_opy_
    bstack1l11ll1l1l_opy_: bstack1l1111llll_opy_
    ai: bstack1ll11llllll_opy_
    bstack1ll1ll1l111_opy_: bstack1lll1lll111_opy_
    bstack1ll1l11llll_opy_: List[bstack1lll11ll111_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack1lll111111l_opy_: Any
    bstack1ll1lll1111_opy_: Dict[str, timedelta]
    bstack1lll111l111_opy_: str
    bstack1lllll1ll1l_opy_: bstack1lllll1lll1_opy_
    def __new__(cls):
        if not cls._1ll1ll1l1ll_opy_:
            cls._1ll1ll1l1ll_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._1ll1ll1l1ll_opy_
    def __init__(self):
        self.process = None
        self.bstack1lll1l1l111_opy_ = False
        self.bstack1ll1l111l11_opy_ = None
        self.bstack1ll1l11111l_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack1lll11l11l1_opy_, None)
        self.bstack1lll1ll1111_opy_ = os.environ.get(bstack1ll1lllllll_opy_, bstack1l1l_opy_ (u"ࠢࠣᄂ")) == bstack1l1l_opy_ (u"ࠣࠤᄃ")
        self.bstack1ll1ll1llll_opy_ = False
        self.bstack1ll1l1llll1_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack1lll111111l_opy_ = None
        self.test_framework = None
        self.bstack1lll1llllll_opy_ = None
        self.bstack1ll1l1111ll_opy_=bstack1l1l_opy_ (u"ࠤࠥᄄ")
        self.session_framework = None
        self.logger = bstack1lllllll1l_opy_.get_logger(self.__class__.__name__, bstack1lllllll1l_opy_.bstack1ll1ll1ll11_opy_())
        self.bstack1ll1lll1111_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack1lllll1ll1l_opy_ = bstack1lllll1lll1_opy_()
        self.bstack1lll11ll1ll_opy_ = None
        self.bstack1lll1l1111l_opy_ = None
        self.bstack1ll1l11lll1_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1ll1l11llll_opy_ = []
    def bstack1l11ll1l11_opy_(self):
        return os.environ.get(bstack1l1lll11l1_opy_).lower().__eq__(bstack1l1l_opy_ (u"ࠥࡸࡷࡻࡥࠣᄅ"))
    def is_enabled(self, config):
        if os.environ.get(bstack1ll1l1l1111_opy_, bstack1l1l_opy_ (u"ࠫࠬᄆ")).lower() in [bstack1l1l_opy_ (u"ࠬࡺࡲࡶࡧࠪᄇ"), bstack1l1l_opy_ (u"࠭࠱ࠨᄈ"), bstack1l1l_opy_ (u"ࠧࡺࡧࡶࠫᄉ")]:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡈࡲࡶࡨ࡯࡮ࡨࠢࡩࡥࡱࡲࡢࡢࡥ࡮ࠤࡲࡵࡤࡦࠢࡧࡹࡪࠦࡴࡰࠢࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡒࡖࡈࡋ࡟ࡇࡃࡏࡐࡇࡇࡃࡌࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺࠠࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠤᄊ"))
            os.environ[bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡋࡖࡣࡗ࡛ࡎࡏࡋࡑࡋࠧᄋ")] = bstack1l1l_opy_ (u"ࠥࡊࡦࡲࡳࡦࠤᄌ")
            return False
        if bstack1l1l_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨᄍ") in config and str(config[bstack1l1l_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩᄎ")]).lower() != bstack1l1l_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬᄏ"):
            return False
        bstack1lll1111lll_opy_ = [bstack1l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢᄐ"), bstack1l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧᄑ")]
        bstack1ll1ll1ll1l_opy_ = config.get(bstack1l1l_opy_ (u"ࠤࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠧᄒ")) in bstack1lll1111lll_opy_ or os.environ.get(bstack1l1l_opy_ (u"ࠪࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࡥࡕࡔࡇࡇࠫᄓ")) in bstack1lll1111lll_opy_
        os.environ[bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡍࡘࡥࡒࡖࡐࡑࡍࡓࡍࠢᄔ")] = str(bstack1ll1ll1ll1l_opy_) # bstack1lll11l1ll1_opy_ bstack1ll1l11ll11_opy_ VAR to bstack1ll1lll111l_opy_ is binary running
        return bstack1ll1ll1ll1l_opy_
    def bstack1l1l11ll11_opy_(self):
        for event in bstack1lll111ll1l_opy_:
            bstack111l111l_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack111l111l_opy_.logger.debug(bstack1l1l_opy_ (u"ࠧࢁࡥࡷࡧࡱࡸࡤࡴࡡ࡮ࡧࢀࠤࡂࡄࠠࡼࡣࡵ࡫ࡸࢃࠠࠣᄕ") + str(kwargs) + bstack1l1l_opy_ (u"ࠨࠢᄖ"))
            )
        bstack111l111l_opy_.register(bstack11l111111_opy_.bstack1llll1ll1l_opy_, self.__1lll1l111l1_opy_)
        bstack111l111l_opy_.register(bstack11l111111_opy_.CONNECT, self.__1lll1l11l11_opy_)
        bstack111l111l_opy_.register(bstack11l111111_opy_.bstack1llll11l1l_opy_, self.__1ll1ll11ll1_opy_)
        bstack111l111l_opy_.register(bstack11l111111_opy_.bstack111ll1ll1_opy_, self.__1ll1l11l1l1_opy_)
    def bstack1llll1lll1_opy_(self):
        return not self.bstack1lll1ll1111_opy_ and os.environ.get(bstack1ll1lllllll_opy_, bstack1l1l_opy_ (u"ࠢࠣᄗ")) != bstack1l1l_opy_ (u"ࠣࠤᄘ")
    def is_running(self):
        if self.bstack1lll1ll1111_opy_:
            return self.bstack1lll1l1l111_opy_
        else:
            return bool(self.bstack1ll1l111l11_opy_)
    def bstack1lll1l1ll11_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1ll1l11llll_opy_) and cli.is_running()
    def __1ll1ll1l1l1_opy_(self, bstack1ll1llll1ll_opy_=10):
        if self.bstack1ll1l11111l_opy_:
            return
        bstack1ll111l1_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack1lll11l11l1_opy_, self.cli_listen_addr)
        self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡞ࠦᄙ") + str(id(self)) + bstack1l1l_opy_ (u"ࠥࡡࠥࡩ࡯࡯ࡰࡨࡧࡹ࡯࡮ࡨࠤᄚ"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack1l1l_opy_ (u"ࠦ࡬ࡸࡰࡤ࠰ࡨࡲࡦࡨ࡬ࡦࡡ࡫ࡸࡹࡶ࡟ࡱࡴࡲࡼࡾࠨᄛ"), 0), (bstack1l1l_opy_ (u"ࠧ࡭ࡲࡱࡥ࠱ࡩࡳࡧࡢ࡭ࡧࡢ࡬ࡹࡺࡰࡴࡡࡳࡶࡴࡾࡹࠣᄜ"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1ll1llll1ll_opy_)
        self.bstack1ll1l111l11_opy_ = channel
        self.bstack1ll1l11111l_opy_ = sdk_pb2_grpc.SDKStub(self.bstack1ll1l111l11_opy_)
        self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡨࡵ࡮࡯ࡧࡦࡸࠧᄝ"), datetime.now() - bstack1ll111l1_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack1lll11l11l1_opy_] = self.cli_listen_addr
        self.logger.debug(bstack1l1l_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡣࡰࡰࡱࡩࡨࡺࡥࡥ࠼ࠣ࡭ࡸࡥࡣࡩ࡫࡯ࡨࡤࡶࡲࡰࡥࡨࡷࡸࡃࠢᄞ") + str(self.bstack1llll1lll1_opy_()) + bstack1l1l_opy_ (u"ࠣࠤᄟ"))
    def __1ll1ll11ll1_opy_(self, event_name):
        if self.bstack1llll1lll1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡷࡹࡵࡰࡱ࡫ࡱ࡫ࠥࡉࡌࡊࠤᄠ"))
        self.__1ll1ll1lll1_opy_()
    def __1ll1l11l1l1_opy_(self, event_name, bstack1lll1ll11l1_opy_ = None, exit_code=1):
        if exit_code == 1:
            self.logger.error(bstack1l1l_opy_ (u"ࠥࡗࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩࠥᄡ"))
        bstack1ll11lll111_opy_ = Path(bstack1lll1l111ll_opy_ (u"ࠦࢀࡹࡥ࡭ࡨ࠱ࡧࡱ࡯࡟ࡥ࡫ࡵࢁ࠴ࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࡹ࠮࡫ࡵࡲࡲࠧᄢ"))
        if self.bstack1ll1ll1111l_opy_ and bstack1ll11lll111_opy_.exists():
            with open(bstack1ll11lll111_opy_, bstack1l1l_opy_ (u"ࠬࡸࠧᄣ"), encoding=bstack1l1l_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᄤ")) as fp:
                data = json.load(fp)
                try:
                    bstack11l11llll_opy_(bstack1l1l_opy_ (u"ࠧࡑࡑࡖࡘࠬᄥ"), bstack1l11llll1_opy_(bstack1l1l1l1l_opy_), data, {
                        bstack1l1l_opy_ (u"ࠨࡣࡸࡸ࡭࠭ᄦ"): (self.config[bstack1l1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫᄧ")], self.config[bstack1l1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ᄨ")])
                    })
                except Exception as e:
                    logger.debug(bstack11lll1l11l_opy_.format(str(e)))
            bstack1ll11lll111_opy_.unlink()
        sys.exit(exit_code)
    @measure(event_name=EVENTS.bstack1lll11ll11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1lll1l111l1_opy_(self, event_name: str, data):
        from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
        self.bstack1ll1l1111ll_opy_, self.bstack1ll1ll1111l_opy_ = bstack1ll1l1l11l1_opy_(data.bs_config)
        os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡛ࡗࡏࡔࡂࡄࡏࡉࡤࡊࡉࡓࠩᄩ")] = self.bstack1ll1ll1111l_opy_
        if not self.bstack1ll1l1111ll_opy_ or not self.bstack1ll1ll1111l_opy_:
            raise ValueError(bstack1l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡴࡩࡧࠣࡗࡉࡑࠠࡄࡎࡌࠤࡧ࡯࡮ࡢࡴࡼࠦᄪ"))
        if self.bstack1llll1lll1_opy_():
            self.__1lll1l11l11_opy_(event_name, bstack11lll1l1l1_opy_())
            return
        try:
            bstack1ll1l1ll111_opy_.end(EVENTS.bstack1l1l1l111_opy_.value, EVENTS.bstack1l1l1l111_opy_.value + bstack1l1l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᄫ"), EVENTS.bstack1l1l1l111_opy_.value + bstack1l1l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧᄬ"), status=True, failure=None, test_name=None)
            logger.debug(bstack1l1l_opy_ (u"ࠣࡅࡲࡱࡵࡲࡥࡵࡧࠣࡗࡉࡑࠠࡔࡧࡷࡹࡵ࠴ࠢᄭ"))
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵࠣࡿࢂࠨᄮ").format(e))
        start = datetime.now()
        is_started = self.__1ll1l1l11ll_opy_()
        self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠥࡷࡵࡧࡷ࡯ࡡࡷ࡭ࡲ࡫ࠢᄯ"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1ll1ll1l1l1_opy_()
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠦࡨࡵ࡮࡯ࡧࡦࡸࡤࡺࡩ࡮ࡧࠥᄰ"), datetime.now() - start)
            start = datetime.now()
            self.__1ll1l1l1l1l_opy_(data)
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠧࡹࡴࡢࡴࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡺࡩ࡮ࡧࠥᄱ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1lll1ll1l11_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1lll1l11l11_opy_(self, event_name: str, data: bstack11lll1l1l1_opy_):
        if not self.bstack1llll1lll1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡳࡴࡥࡤࡶ࠽ࠤࡳࡵࡴࠡࡣࠣࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵࠥᄲ"))
            return
        bin_session_id = os.environ.get(bstack1ll1lllllll_opy_)
        start = datetime.now()
        self.__1ll1ll1l1l1_opy_()
        self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࡠࡶ࡬ࡱࡪࠨᄳ"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack1l1l_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡤࡪ࡬ࡰࡩ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧࠤࡹࡵࠠࡦࡺ࡬ࡷࡹ࡯࡮ࡨࠢࡆࡐࡎࠦࠢᄴ") + str(bin_session_id) + bstack1l1l_opy_ (u"ࠤࠥᄵ"))
        start = datetime.now()
        self.__1ll1l1ll11l_opy_()
        self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠥࡷࡹࡧࡲࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡸ࡮ࡳࡥࠣᄶ"), datetime.now() - start)
    def __1lll1111111_opy_(self):
        if not self.bstack1ll1l11111l_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡨࡧ࡮࡯ࡱࡷࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷ࡫ࠠ࡮ࡱࡧࡹࡱ࡫ࡳࠣᄷ"))
            return
        bstack1lll11lll11_opy_ = {
            bstack1l1l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᄸ"): (bstack1lll111llll_opy_, bstack1lll11l1l1l_opy_, bstack1ll1l1lllll_opy_),
            bstack1l1l_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣᄹ"): (bstack1ll1ll111ll_opy_, bstack1ll11lll1ll_opy_, bstack1ll1lll1lll_opy_),
        }
        if not self.bstack1lll11ll1ll_opy_ and self.session_framework in bstack1lll11lll11_opy_:
            bstack1ll1l1l1l11_opy_, bstack1ll1ll11111_opy_, bstack1ll1ll11l11_opy_ = bstack1lll11lll11_opy_[self.session_framework]
            bstack1lll11lllll_opy_ = bstack1ll1ll11111_opy_()
            self.bstack1lll1l1111l_opy_ = bstack1lll11lllll_opy_
            self.bstack1lll11ll1ll_opy_ = bstack1ll1ll11l11_opy_
            self.bstack1ll1l11llll_opy_.append(bstack1lll11lllll_opy_)
            self.bstack1ll1l11llll_opy_.append(bstack1ll1l1l1l11_opy_(self.bstack1lll1l1111l_opy_))
        if not self.bstack1ll1l11lll1_opy_ and self.config_observability and self.config_observability.success: # bstack1lll111ll11_opy_
            self.bstack1ll1l11lll1_opy_ = bstack1ll1l111l1l_opy_(self.bstack1lll11ll1ll_opy_, self.bstack1lll1l1111l_opy_) # bstack1lll11l1lll_opy_
            self.bstack1ll1l11llll_opy_.append(self.bstack1ll1l11lll1_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack1ll1l1l111l_opy_(self.bstack1lll11ll1ll_opy_, self.bstack1lll1l1111l_opy_)
            self.bstack1ll1l11llll_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack1l1l_opy_ (u"ࠢࡴࡧ࡯ࡪࡍ࡫ࡡ࡭ࠤᄺ"), False) == True:
            self.ai = bstack1ll11llllll_opy_()
            self.bstack1ll1l11llll_opy_.append(self.ai)
        if not self.percy and self.bstack1lll111111l_opy_ and self.bstack1lll111111l_opy_.success:
            self.percy = bstack1lll1lll111_opy_(self.bstack1lll111111l_opy_)
            self.bstack1ll1l11llll_opy_.append(self.percy)
        for mod in self.bstack1ll1l11llll_opy_:
            if not mod.bstack1ll1lll11l1_opy_():
                mod.configure(self.bstack1ll1l11111l_opy_, self.config, self.cli_bin_session_id, self.bstack1lllll1ll1l_opy_)
    def __1ll1lll1ll1_opy_(self):
        for mod in self.bstack1ll1l11llll_opy_:
            if mod.bstack1ll1lll11l1_opy_():
                mod.configure(self.bstack1ll1l11111l_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1lll1l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1l1l1l1l_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1ll1ll1llll_opy_:
            return
        self.__1lll1111l11_opy_(data)
        bstack1ll111l1_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack1l1l_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࠣᄻ")
        req.sdk_language = bstack1l1l_opy_ (u"ࠤࡳࡽࡹ࡮࡯࡯ࠤᄼ")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1ll1lll11ll_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥ࡟ࠧᄽ") + str(id(self)) + bstack1l1l_opy_ (u"ࠦࡢࠦ࡭ࡢ࡫ࡱ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡳࡵࡣࡵࡸࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠥᄾ"))
            r = self.bstack1ll1l11111l_opy_.StartBinSession(req)
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡷࡹࡧࡲࡵࡡࡥ࡭ࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࠢᄿ"), datetime.now() - bstack1ll111l1_opy_)
            os.environ[bstack1ll1lllllll_opy_] = r.bin_session_id
            self.__1ll1l1111l1_opy_(r)
            self.__1lll1111111_opy_()
            self.bstack1lllll1ll1l_opy_.start()
            self.bstack1ll1ll1llll_opy_ = True
            self.logger.debug(bstack1l1l_opy_ (u"ࠨ࡛ࠣᅀ") + str(id(self)) + bstack1l1l_opy_ (u"ࠢ࡞ࠢࡰࡥ࡮ࡴ࠭ࡱࡴࡲࡧࡪࡹࡳ࠻ࠢࡦࡳࡳࡴࡥࡤࡶࡨࡨࠧᅁ"))
        except grpc.bstack1lll1111l1l_opy_ as bstack1lll1111ll1_opy_:
            self.logger.error(bstack1l1l_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡵ࡫ࡰࡩࡴ࡫ࡵࡵ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᅂ") + str(bstack1lll1111ll1_opy_) + bstack1l1l_opy_ (u"ࠤࠥᅃ"))
            traceback.print_exc()
            raise bstack1lll1111ll1_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢᅄ") + str(e) + bstack1l1l_opy_ (u"ࠦࠧᅅ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1lll111lll1_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1l1ll11l_opy_(self):
        if not self.bstack1llll1lll1_opy_() or not self.cli_bin_session_id or self.bstack1ll1l1llll1_opy_:
            return
        bstack1ll111l1_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᅆ"), bstack1l1l_opy_ (u"࠭࠰ࠨᅇ")))
        try:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢ࡜ࠤᅈ") + str(id(self)) + bstack1l1l_opy_ (u"ࠣ࡟ࠣࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵ࠽ࠤࡨࡵ࡮࡯ࡧࡦࡸࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠥᅉ"))
            r = self.bstack1ll1l11111l_opy_.ConnectBinSession(req)
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡤࡱࡱࡲࡪࡩࡴࡠࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࠨᅊ"), datetime.now() - bstack1ll111l1_opy_)
            self.__1ll1l1111l1_opy_(r)
            self.__1lll1111111_opy_()
            self.bstack1lllll1ll1l_opy_.start()
            self.bstack1ll1l1llll1_opy_ = True
            self.logger.debug(bstack1l1l_opy_ (u"ࠥ࡟ࠧᅋ") + str(id(self)) + bstack1l1l_opy_ (u"ࠦࡢࠦࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡀࠠࡤࡱࡱࡲࡪࡩࡴࡦࡦࠥᅌ"))
        except grpc.bstack1lll1111l1l_opy_ as bstack1lll1111ll1_opy_:
            self.logger.error(bstack1l1l_opy_ (u"ࠧࡡࡻࡪࡦࠫࡷࡪࡲࡦࠪࡿࡠࠤࡹ࡯࡭ࡦࡱࡨࡹࡹ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢᅍ") + str(bstack1lll1111ll1_opy_) + bstack1l1l_opy_ (u"ࠨࠢᅎ"))
            traceback.print_exc()
            raise bstack1lll1111ll1_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᅏ") + str(e) + bstack1l1l_opy_ (u"ࠣࠤᅐ"))
            traceback.print_exc()
            raise e
    def __1ll1l1111l1_opy_(self, r):
        self.bstack1lll1lll11l_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack1l1l_opy_ (u"ࠤࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡳࡦࡴࡹࡩࡷࠦࡲࡦࡵࡳࡳࡳࡹࡥࠣᅑ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack1l1l_opy_ (u"ࠥࡩࡲࡶࡴࡺࠢࡦࡳࡳ࡬ࡩࡨࠢࡩࡳࡺࡴࡤࠣᅒ"))
        self.session_framework = r.session_framework
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack1l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡨࡶࡨࡿࠠࡪࡵࠣࡷࡪࡴࡴࠡࡱࡱࡰࡾࠦࡡࡴࠢࡳࡥࡷࡺࠠࡰࡨࠣࡸ࡭࡫ࠠࠣࡅࡲࡲࡳ࡫ࡣࡵࡄ࡬ࡲࡘ࡫ࡳࡴ࡫ࡲࡲ࠱ࠨࠠࡢࡰࡧࠤࡹ࡮ࡩࡴࠢࡩࡹࡳࡩࡴࡪࡱࡱࠤ࡮ࡹࠠࡢ࡮ࡶࡳࠥࡻࡳࡦࡦࠣࡦࡾࠦࡓࡵࡣࡵࡸࡇ࡯࡮ࡔࡧࡶࡷ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡘ࡭࡫ࡲࡦࡨࡲࡶࡪ࠲ࠠࡏࡱࡱࡩࠥ࡮ࡡ࡯ࡦ࡯࡭ࡳ࡭ࠠࡪࡵࠣ࡭ࡲࡶ࡬ࡦ࡯ࡨࡲࡹ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᅓ")
        self.bstack1lll111111l_opy_ = getattr(r, bstack1l1l_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫᅔ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᅕ")] = self.config_testhub.jwt
        os.environ[bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᅖ")] = self.config_testhub.build_hashed_id
    def bstack1lll11l11ll_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1lll1l1l111_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1lll1ll1lll_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1lll1ll1lll_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1lll11l11ll_opy_(event_name=EVENTS.bstack1lll111l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1l1l11ll_opy_(self, bstack1ll1llll1ll_opy_=10):
        if self.bstack1lll1l1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠣࡵࡷࡥࡷࡺ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡵࡹࡳࡴࡩ࡯ࡩࠥᅗ"))
            return True
        self.logger.debug(bstack1l1l_opy_ (u"ࠤࡶࡸࡦࡸࡴࠣᅘ"))
        if os.getenv(bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡐࡎࡥࡅࡏࡘࠥᅙ")) == bstack1lll11l1l11_opy_:
            self.cli_bin_session_id = bstack1lll11l1l11_opy_
            self.cli_listen_addr = bstack1l1l_opy_ (u"ࠦࡺࡴࡩࡹ࠼࠲ࡸࡲࡶ࠯ࡴࡦ࡮࠱ࡵࡲࡡࡵࡨࡲࡶࡲ࠳ࠥࡴ࠰ࡶࡳࡨࡱࠢᅚ") % (self.cli_bin_session_id)
            self.bstack1lll1l1l111_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack1ll1l1111ll_opy_, bstack1l1l_opy_ (u"ࠧࡹࡤ࡬ࠤᅛ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack1lll11ll1l1_opy_ compat for text=True in bstack1ll11llll11_opy_ python
            encoding=bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᅜ"),
            bufsize=1,
            close_fds=True,
        )
        bstack1ll1l11ll1l_opy_ = threading.Thread(target=self.__1ll1l111111_opy_, args=(bstack1ll1llll1ll_opy_,))
        bstack1ll1l11ll1l_opy_.start()
        bstack1ll1l11ll1l_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack1l1l_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡳࡱࡣࡺࡲ࠿ࠦࡲࡦࡶࡸࡶࡳࡩ࡯ࡥࡧࡀࡿࡸ࡫࡬ࡧ࠰ࡳࡶࡴࡩࡥࡴࡵ࠱ࡶࡪࡺࡵࡳࡰࡦࡳࡩ࡫ࡽࠡࡱࡸࡸࡂࢁࡳࡦ࡮ࡩ࠲ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡹࡴࡥࡱࡸࡸ࠳ࡸࡥࡢࡦࠫ࠭ࢂࠦࡥࡳࡴࡀࠦᅝ") + str(self.process.stderr.read()) + bstack1l1l_opy_ (u"ࠣࠤᅞ"))
        if not self.bstack1lll1l1l111_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠤ࡞ࠦᅟ") + str(id(self)) + bstack1l1l_opy_ (u"ࠥࡡࠥࡩ࡬ࡦࡣࡱࡹࡵࠨᅠ"))
            self.__1ll1ll1lll1_opy_()
        self.logger.debug(bstack1l1l_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡴࡷࡵࡣࡦࡵࡶࡣࡷ࡫ࡡࡥࡻ࠽ࠤࠧᅡ") + str(self.bstack1lll1l1l111_opy_) + bstack1l1l_opy_ (u"ࠧࠨᅢ"))
        return self.bstack1lll1l1l111_opy_
    def __1ll1l111111_opy_(self, bstack1ll1llllll1_opy_=10):
        bstack1ll1l1lll11_opy_ = time.time()
        while self.process and time.time() - bstack1ll1l1lll11_opy_ < bstack1ll1llllll1_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack1l1l_opy_ (u"ࠨࡩࡥ࠿ࠥᅣ") in line:
                    self.cli_bin_session_id = line.split(bstack1l1l_opy_ (u"ࠢࡪࡦࡀࠦᅤ"))[-1:][0].strip()
                    self.logger.debug(bstack1l1l_opy_ (u"ࠣࡥ࡯࡭ࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࡀࠢᅥ") + str(self.cli_bin_session_id) + bstack1l1l_opy_ (u"ࠤࠥᅦ"))
                    continue
                if bstack1l1l_opy_ (u"ࠥࡰ࡮ࡹࡴࡦࡰࡀࠦᅧ") in line:
                    self.cli_listen_addr = line.split(bstack1l1l_opy_ (u"ࠦࡱ࡯ࡳࡵࡧࡱࡁࠧᅨ"))[-1:][0].strip()
                    self.logger.debug(bstack1l1l_opy_ (u"ࠧࡩ࡬ࡪࡡ࡯࡭ࡸࡺࡥ࡯ࡡࡤࡨࡩࡸ࠺ࠣᅩ") + str(self.cli_listen_addr) + bstack1l1l_opy_ (u"ࠨࠢᅪ"))
                    continue
                if bstack1l1l_opy_ (u"ࠢࡱࡱࡵࡸࡂࠨᅫ") in line:
                    port = line.split(bstack1l1l_opy_ (u"ࠣࡲࡲࡶࡹࡃࠢᅬ"))[-1:][0].strip()
                    self.logger.debug(bstack1l1l_opy_ (u"ࠤࡳࡳࡷࡺ࠺ࠣᅭ") + str(port) + bstack1l1l_opy_ (u"ࠥࠦᅮ"))
                    continue
                if line.strip() == bstack1ll1l11l11l_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack1l1l_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡍࡔࡥࡓࡕࡔࡈࡅࡒࠨᅯ"), bstack1l1l_opy_ (u"ࠧ࠷ࠢᅰ")) == bstack1l1l_opy_ (u"ࠨ࠱ࠣᅱ"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1lll1l1l111_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack1l1l_opy_ (u"ࠢࡦࡴࡵࡳࡷࡀࠠࠣᅲ") + str(e) + bstack1l1l_opy_ (u"ࠣࠤᅳ"))
        return False
    @measure(event_name=EVENTS.bstack1ll1llll11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1ll1lll1_opy_(self):
        if self.bstack1ll1l111l11_opy_:
            self.bstack1lllll1ll1l_opy_.stop()
            start = datetime.now()
            if self.bstack1lll11llll1_opy_():
                self.cli_bin_session_id = None
                if self.bstack1ll1l1llll1_opy_:
                    self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡶࡸࡴࡶ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡶ࡬ࡱࡪࠨᅴ"), datetime.now() - start)
                else:
                    self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠥࡷࡹࡵࡰࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡷ࡭ࡲ࡫ࠢᅵ"), datetime.now() - start)
            self.__1ll1lll1ll1_opy_()
            start = datetime.now()
            self.bstack1ll1l111l11_opy_.close()
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠦࡩ࡯ࡳࡤࡱࡱࡲࡪࡩࡴࡠࡶ࡬ࡱࡪࠨᅶ"), datetime.now() - start)
            self.bstack1ll1l111l11_opy_ = None
        if self.process:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡹࡴࡰࡲࠥᅷ"))
            start = datetime.now()
            self.process.terminate()
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠨ࡫ࡪ࡮࡯ࡣࡹ࡯࡭ࡦࠤᅸ"), datetime.now() - start)
            self.process = None
            if self.bstack1lll1ll1111_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack111ll1lll_opy_()
                self.logger.info(
                    bstack1l1l_opy_ (u"ࠢࡗ࡫ࡶ࡭ࡹࠦࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿࠣࡸࡴࠦࡶࡪࡧࡺࠤࡧࡻࡩ࡭ࡦࠣࡶࡪࡶ࡯ࡳࡶ࠯ࠤ࡮ࡴࡳࡪࡩ࡫ࡸࡸ࠲ࠠࡢࡰࡧࠤࡲࡧ࡮ࡺࠢࡰࡳࡷ࡫ࠠࡥࡧࡥࡹ࡬࡭ࡩ࡯ࡩࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮ࠡࡣ࡯ࡰࠥࡧࡴࠡࡱࡱࡩࠥࡶ࡬ࡢࡥࡨࠥࡡࡴࠢᅹ").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack1l1l_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧᅺ")] = self.config_testhub.build_hashed_id
        self.bstack1lll1l1l111_opy_ = False
    def __1lll1111l11_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack1l1l_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᅻ")] = selenium.__version__
            data.frameworks.append(bstack1l1l_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧᅼ"))
        except:
            pass
        try:
            from playwright._repo_version import __version__
            data.framework_versions[bstack1l1l_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᅽ")] = __version__
            data.frameworks.append(bstack1l1l_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᅾ"))
        except:
            pass
    def bstack1lll11111l1_opy_(self, hub_url: str, platform_index: int, bstack1l11l11l11_opy_: Any):
        if self.bstack1lll1llllll_opy_:
            self.logger.debug(bstack1l1l_opy_ (u"ࠨࡳ࡬࡫ࡳࡴࡪࡪࠠࡴࡧࡷࡹࡵࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠻ࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡷࡪࡺࠠࡶࡲࠥᅿ"))
            return
        try:
            bstack1ll111l1_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack1l1l_opy_ (u"ࠢࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠤᆀ")
            self.bstack1lll1llllll_opy_ = bstack1ll1lll1lll_opy_(
                cli.config.get(bstack1l1l_opy_ (u"ࠣࡪࡸࡦ࡚ࡸ࡬ࠣᆁ"), hub_url),
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1lll1ll1l1l_opy_={bstack1l1l_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡡࡲࡴࡹ࡯࡯࡯ࡵࡢࡪࡷࡵ࡭ࡠࡥࡤࡴࡸࠨᆂ"): bstack1l11l11l11_opy_}
            )
            def bstack1ll1l1l1lll_opy_(self):
                return
            if self.config.get(bstack1l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠧᆃ"), True):
                Service.start = bstack1ll1l1l1lll_opy_
                Service.stop = bstack1ll1l1l1lll_opy_
            def get_accessibility_results(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results(driver, framework_name=framework)
            def get_accessibility_results_summary(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results_summary(driver, framework_name=framework)
            def perform_scan(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.perform_scan(driver, method=None, framework_name=framework)
            WebDriver.getAccessibilityResults = get_accessibility_results
            WebDriver.get_accessibility_results = get_accessibility_results
            WebDriver.getAccessibilityResultsSummary = get_accessibility_results_summary
            WebDriver.get_accessibility_results_summary = get_accessibility_results_summary
            WebDriver.upload_attachment = staticmethod(bstack1l1111llll_opy_.upload_attachment)
            WebDriver.set_custom_tag = staticmethod(bstack1ll1l1ll1ll_opy_.set_custom_tag)
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡷࡪࡲࡥ࡯࡫ࡸࡱࠧᆄ"), datetime.now() - bstack1ll111l1_opy_)
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࡺࡶࠠࡴࡧ࡯ࡩࡳ࡯ࡵ࡮࠼ࠣࠦᆅ") + str(e) + bstack1l1l_opy_ (u"ࠨࠢᆆ"))
    def bstack1ll1l1ll1l1_opy_(self, platform_index: int):
        try:
            from playwright.sync_api import BrowserType
            from playwright.sync_api import BrowserContext
            from playwright._impl._connection import Connection
            from playwright._repo_version import __version__
            from bstack_utils.helper import bstack111l11l11_opy_
            self.bstack1lll1llllll_opy_ = bstack1ll1l1lllll_opy_(
                platform_index,
                framework_name=bstack1l1l_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᆇ"),
                framework_version=__version__,
                classes=[BrowserType, BrowserContext, Connection],
            )
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࡶࡲࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠺ࠡࠤᆈ") + str(e) + bstack1l1l_opy_ (u"ࠤࠥᆉ"))
            pass
    def bstack1lll1l1l1ll_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡷࡰ࡯ࡰࡱࡧࡧࠤࡸ࡫ࡴࡶࡲࠣࡴࡾࡺࡥࡴࡶ࠽ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡹࡥࡵࠢࡸࡴࠧᆊ"))
            return
        if bstack11ll111l11_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack1l1l_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᆋ"): pytest.__version__ }, [bstack1l1l_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤᆌ")], self.bstack1lllll1ll1l_opy_, self.bstack1ll1l11111l_opy_)
            return
        try:
            import pytest
            self.test_framework = bstack1ll1ll11lll_opy_({ bstack1l1l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᆍ"): pytest.__version__ }, [bstack1l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢᆎ")], self.bstack1lllll1ll1l_opy_, self.bstack1ll1l11111l_opy_)
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࡶࡲࠣࡴࡾࡺࡥࡴࡶ࠽ࠤࠧᆏ") + str(e) + bstack1l1l_opy_ (u"ࠤࠥᆐ"))
        self.bstack1ll11lllll1_opy_()
    def bstack1ll11lllll1_opy_(self):
        if not self.bstack1l11ll1l11_opy_():
            return
        bstack1l111l111_opy_ = None
        def bstack1llll1lll_opy_(config, startdir):
            return bstack1l1l_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀ࠶ࡽࠣᆑ").format(bstack1l1l_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥᆒ"))
        def bstack1lll1l11_opy_():
            return
        def bstack1l1ll1111l_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack1l1l_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࠬᆓ"):
                return bstack1l1l_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧᆔ")
            else:
                return bstack1l111l111_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack1l111l111_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack1llll1lll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1lll1l11_opy_
            Config.getoption = bstack1l1ll1111l_opy_
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡺࡣࡩࠢࡳࡽࡹ࡫ࡳࡵࠢࡶࡩࡱ࡫࡮ࡪࡷࡰࠤ࡫ࡵࡲࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠺ࠡࠤᆕ") + str(e) + bstack1l1l_opy_ (u"ࠣࠤᆖ"))
    def bstack1lll1l1ll1l_opy_(self):
        bstack1llll111l1_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack1llll111l1_opy_, dict):
            if cli.config_observability:
                bstack1llll111l1_opy_.update(
                    {bstack1l1l_opy_ (u"ࠤࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠤᆗ"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack1l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡷࡤࡺ࡯ࡠࡹࡵࡥࡵࠨᆘ") in accessibility.get(bstack1l1l_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᆙ"), {}):
                    bstack1ll1lll1l11_opy_ = accessibility.get(bstack1l1l_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᆚ"))
                    bstack1ll1lll1l11_opy_.update({ bstack1l1l_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࡳࡕࡱ࡚ࡶࡦࡶࠢᆛ"): bstack1ll1lll1l11_opy_.pop(bstack1l1l_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡴࡡࡷࡳࡤࡽࡲࡢࡲࠥᆜ")) })
                bstack1llll111l1_opy_.update({bstack1l1l_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣᆝ"): accessibility })
        return bstack1llll111l1_opy_
    @measure(event_name=EVENTS.bstack1ll1lll1l1l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1lll11llll1_opy_(self, bstack1ll1l1l1ll1_opy_: str = None, bstack1ll1l1lll1l_opy_: str = None, exit_code: int = None):
        if not self.cli_bin_session_id or not self.bstack1ll1l11111l_opy_:
            return
        bstack1ll111l1_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if exit_code:
            req.exit_code = exit_code
        if bstack1ll1l1l1ll1_opy_:
            req.bstack1ll1l1l1ll1_opy_ = bstack1ll1l1l1ll1_opy_
        if bstack1ll1l1lll1l_opy_:
            req.bstack1ll1l1lll1l_opy_ = bstack1ll1l1lll1l_opy_
        try:
            r = self.bstack1ll1l11111l_opy_.StopBinSession(req)
            SDKCLI.automate_buildlink = r.automate_buildlink
            SDKCLI.hashed_id = r.hashed_id
            self.bstack1lll1l1l_opy_(bstack1l1l_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡶࡲࡴࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠥᆞ"), datetime.now() - bstack1ll111l1_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack1lll1l1l_opy_(self, key: str, value: timedelta):
        tag = bstack1l1l_opy_ (u"ࠥࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵࠥᆟ") if self.bstack1llll1lll1_opy_() else bstack1l1l_opy_ (u"ࠦࡲࡧࡩ࡯࠯ࡳࡶࡴࡩࡥࡴࡵࠥᆠ")
        self.bstack1ll1lll1111_opy_[bstack1l1l_opy_ (u"ࠧࡀࠢᆡ").join([tag + bstack1l1l_opy_ (u"ࠨ࠭ࠣᆢ") + str(id(self)), key])] += value
    def bstack111ll1lll_opy_(self):
        if not os.getenv(bstack1l1l_opy_ (u"ࠢࡅࡇࡅ࡙ࡌࡥࡐࡆࡔࡉࠦᆣ"), bstack1l1l_opy_ (u"ࠣ࠲ࠥᆤ")) == bstack1l1l_opy_ (u"ࠤ࠴ࠦᆥ"):
            return
        bstack1ll1ll1l11l_opy_ = dict()
        bstack1llll111l11_opy_ = []
        if self.test_framework:
            bstack1llll111l11_opy_.extend(list(self.test_framework.bstack1llll111l11_opy_.values()))
        if self.bstack1lll1llllll_opy_:
            bstack1llll111l11_opy_.extend(list(self.bstack1lll1llllll_opy_.bstack1llll111l11_opy_.values()))
        for instance in bstack1llll111l11_opy_:
            if not instance.platform_index in bstack1ll1ll1l11l_opy_:
                bstack1ll1ll1l11l_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1ll1ll1l11l_opy_[instance.platform_index]
            for k, v in instance.bstack1ll1ll11l1l_opy_().items():
                report[k] += v
                report[k.split(bstack1l1l_opy_ (u"ࠥ࠾ࠧᆦ"))[0]] += v
        bstack1lll11111ll_opy_ = sorted([(k, v) for k, v in self.bstack1ll1lll1111_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack1lll1l11111_opy_ = 0
        for r in bstack1lll11111ll_opy_:
            bstack1lll11l111l_opy_ = r[1].total_seconds()
            bstack1lll1l11111_opy_ += bstack1lll11l111l_opy_
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡠࡶࡥࡳࡨࡠࠤࡨࡲࡩ࠻ࡽࡵ࡟࠵ࡣࡽ࠾ࠤᆧ") + str(bstack1lll11l111l_opy_) + bstack1l1l_opy_ (u"ࠧࠨᆨ"))
        self.logger.debug(bstack1l1l_opy_ (u"ࠨ࠭࠮ࠤᆩ"))
        bstack1ll1llll1l1_opy_ = []
        for platform_index, report in bstack1ll1ll1l11l_opy_.items():
            bstack1ll1llll1l1_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1ll1llll1l1_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack1lll111l11_opy_ = set()
        bstack1ll11lll1l1_opy_ = 0
        for r in bstack1ll1llll1l1_opy_:
            bstack1lll11l111l_opy_ = r[2].total_seconds()
            bstack1ll11lll1l1_opy_ += bstack1lll11l111l_opy_
            bstack1lll111l11_opy_.add(r[0])
            self.logger.debug(bstack1l1l_opy_ (u"ࠢ࡜ࡲࡨࡶ࡫ࡣࠠࡵࡧࡶࡸ࠿ࡶ࡬ࡢࡶࡩࡳࡷࡳ࠭ࡼࡴ࡞࠴ࡢࢃ࠺ࡼࡴ࡞࠵ࡢࢃ࠽ࠣᆪ") + str(bstack1lll11l111l_opy_) + bstack1l1l_opy_ (u"ࠣࠤᆫ"))
        if self.bstack1llll1lll1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠤ࠰࠱ࠧᆬ"))
            self.logger.debug(bstack1l1l_opy_ (u"ࠥ࡟ࡵ࡫ࡲࡧ࡟ࠣࡧࡱ࡯࠺ࡤࡪ࡬ࡰࡩ࠳ࡰࡳࡱࡦࡩࡸࡹ࠽ࡼࡶࡲࡸࡦࡲ࡟ࡤ࡮࡬ࢁࠥࡺࡥࡴࡶ࠽ࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠳ࡻࡴࡶࡵࠬࡵࡲࡡࡵࡨࡲࡶࡲࡹࠩࡾ࠿ࠥᆭ") + str(bstack1ll11lll1l1_opy_) + bstack1l1l_opy_ (u"ࠦࠧᆮ"))
        else:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡡࡰࡦࡴࡩࡡࠥࡩ࡬ࡪ࠼ࡰࡥ࡮ࡴ࠭ࡱࡴࡲࡧࡪࡹࡳ࠾ࠤᆯ") + str(bstack1lll1l11111_opy_) + bstack1l1l_opy_ (u"ࠨࠢᆰ"))
        self.logger.debug(bstack1l1l_opy_ (u"ࠢ࠮࠯ࠥᆱ"))
    def test_orchestration_session(self, test_files: list, orchestration_strategy: str, orchestration_metadata: str):
        request = structs.TestOrchestrationRequest(
            bin_session_id=self.cli_bin_session_id,
            orchestration_strategy=orchestration_strategy,
            test_files=test_files,
            orchestration_metadata=orchestration_metadata
        )
        if not self.bstack1ll1l11111l_opy_:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡥ࡯࡭ࡤࡹࡥࡳࡸ࡬ࡧࡪࠦࡩࡴࠢࡱࡳࡹࠦࡩ࡯࡫ࡷ࡭ࡦࡲࡩࡻࡧࡧ࠲ࠥࡉࡡ࡯ࡰࡲࡸࠥࡶࡥࡳࡨࡲࡶࡲࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧᆲ"))
            return None
        response = self.bstack1ll1l11111l_opy_.TestOrchestration(request)
        self.logger.debug(bstack1l1l_opy_ (u"ࠤࡷࡩࡸࡺ࠭ࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴ࠭ࡴࡧࡶࡷ࡮ࡵ࡮࠾ࡽࢀࠦᆳ").format(response))
        if response.success:
            return list(response.ordered_test_files)
        return None
    def bstack1lll1lll11l_opy_(self, r):
        if r is not None and getattr(r, bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࠫᆴ"), None) and getattr(r.testhub, bstack1l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫᆵ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack1l1l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᆶ")))
            for bstack1lll1l11ll1_opy_, err in errors.items():
                if err[bstack1l1l_opy_ (u"࠭ࡴࡺࡲࡨࠫᆷ")] == bstack1l1l_opy_ (u"ࠧࡪࡰࡩࡳࠬᆸ"):
                    self.logger.info(err[bstack1l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᆹ")])
                else:
                    self.logger.error(err[bstack1l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᆺ")])
    def bstack111l11l1l_opy_(self):
        return SDKCLI.automate_buildlink, SDKCLI.hashed_id
cli = SDKCLI()