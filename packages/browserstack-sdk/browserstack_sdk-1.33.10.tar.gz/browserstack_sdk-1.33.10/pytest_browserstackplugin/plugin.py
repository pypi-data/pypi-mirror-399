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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack1ll11ll1l1_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack1ll111l1l1_opy_, bstack1ll1ll1lll_opy_, update, bstack11l111111_opy_,
                                       bstack11l11l11ll_opy_, bstack1l1l1l1ll1_opy_, bstack1l11lll111_opy_, bstack1111llll_opy_,
                                       bstack1llll1ll1_opy_, bstack1l1lll1111_opy_, bstack1lll11l11_opy_,
                                       bstack11ll11ll1_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack11l11l111l_opy_)
from browserstack_sdk.bstack1lll1ll1l1_opy_ import bstack1lllll1l1_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack1l1llll1_opy_
from bstack_utils.capture import bstack111l1l1lll_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack111111111_opy_, bstack1ll111111_opy_, bstack1l1l11l111_opy_, \
    bstack1l1l11l1ll_opy_
from bstack_utils.helper import bstack11l1l111l_opy_, bstack111lll11ll1_opy_, bstack1111ll1ll1_opy_, bstack1ll11l1111_opy_, bstack1l1ll11lll1_opy_, bstack111l1l11_opy_, \
    bstack111ll1ll11l_opy_, \
    bstack11l1111llll_opy_, bstack11lll1l1ll_opy_, bstack1ll1111lll_opy_, bstack111l1llll1l_opy_, bstack1l1ll1111l_opy_, Notset, \
    bstack11111ll1_opy_, bstack111llll1ll1_opy_, bstack11l111111ll_opy_, Result, bstack111l1lllll1_opy_, bstack111lll1lll1_opy_, error_handler, \
    bstack1lll1l11l1_opy_, bstack1ll111l1_opy_, bstack1lll11ll11_opy_, bstack111ll1ll1l1_opy_
from bstack_utils.bstack111l1l1ll1l_opy_ import bstack111l1l1ll11_opy_
from bstack_utils.messages import bstack1l11lll1l_opy_, bstack1l1l1l1l_opy_, bstack1l1l1111l1_opy_, bstack11ll1111ll_opy_, bstack11llllll1l_opy_, \
    bstack1ll11ll111_opy_, bstack1l111l1l11_opy_, bstack1l11lll11l_opy_, bstack1l1l11111_opy_, bstack1ll11l1l_opy_, \
    bstack1l11llll11_opy_, bstack111111lll_opy_, bstack11ll1l1l1l_opy_
from bstack_utils.proxy import bstack1l111l1l_opy_, bstack1l11l11l11_opy_
from bstack_utils.bstack1l11l1lll_opy_ import bstack1lllll1l1l1l_opy_, bstack1lllll11ll1l_opy_, bstack1lllll11llll_opy_, bstack1lllll1l11l1_opy_, \
    bstack1lllll11l1ll_opy_, bstack1lllll11l111_opy_, bstack1lllll1l111l_opy_, bstack1lll1l111_opy_, bstack1lllll1l1l11_opy_
from bstack_utils.bstack11lllllll1_opy_ import bstack11l1l11l11_opy_
from bstack_utils.bstack1l11llll_opy_ import bstack1l1111ll11_opy_, bstack1ll11ll11_opy_, bstack1l11ll1ll1_opy_, \
    bstack1l1111l1l1_opy_, bstack11l11111l_opy_
from bstack_utils.bstack111l1ll1l1_opy_ import bstack111ll1l11l_opy_
from bstack_utils.bstack111l1ll111_opy_ import bstack11l11ll11l_opy_
import bstack_utils.accessibility as bstack1l1l11ll11_opy_
from bstack_utils.bstack111l1l1l11_opy_ import bstack11l1ll1l1l_opy_
from bstack_utils.bstack11ll11111_opy_ import bstack11ll11111_opy_
from bstack_utils.bstack1ll1ll1111_opy_ import bstack1l11ll1111_opy_
from browserstack_sdk.__init__ import bstack11ll1lll11_opy_
from browserstack_sdk.sdk_cli.bstack1lll11lll11_opy_ import bstack1ll1l1111ll_opy_
from browserstack_sdk.sdk_cli.bstack11lllll1ll_opy_ import bstack11lllll1ll_opy_, bstack11lll1l1l_opy_, bstack11l1111l11_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack1l1111ll1l1_opy_, bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack11lllll1ll_opy_ import bstack11lllll1ll_opy_, bstack11lll1l1l_opy_, bstack11l1111l11_opy_
bstack1111ll11l_opy_ = None
bstack11ll1l11_opy_ = None
bstack1l11lll1_opy_ = None
bstack1ll1lll1ll_opy_ = None
bstack1l11ll111l_opy_ = None
bstack1l1l1ll11_opy_ = None
bstack1ll1ll11ll_opy_ = None
bstack1l1lll11l_opy_ = None
bstack1llll11l_opy_ = None
bstack1lllllll11_opy_ = None
bstack11l1llll1l_opy_ = None
bstack1111l1ll1_opy_ = None
bstack1ll1111111_opy_ = None
bstack1llll11l1l_opy_ = bstack11111l_opy_ (u"ࠩࠪ⊵")
CONFIG = {}
bstack11l1l1l1ll_opy_ = False
bstack11l11l1l1l_opy_ = bstack11111l_opy_ (u"ࠪࠫ⊶")
bstack1lll1l11_opy_ = bstack11111l_opy_ (u"ࠫࠬ⊷")
bstack1ll11111l1_opy_ = False
bstack1l1lllll_opy_ = []
bstack1111llll1_opy_ = bstack111111111_opy_
bstack1lll1l1ll111_opy_ = bstack11111l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ⊸")
bstack1l1111l1_opy_ = {}
bstack11ll1ll1l1_opy_ = None
bstack1ll11ll1l_opy_ = False
logger = bstack1l1llll1_opy_.get_logger(__name__, bstack1111llll1_opy_)
store = {
    bstack11111l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⊹"): []
}
bstack1lll1l1l1l1l_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_111l11ll1l_opy_ = {}
current_test_uuid = None
cli_context = bstack1l1111ll1l1_opy_(
    test_framework_name=bstack1l11l111l_opy_[bstack11111l_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࠭ࡃࡆࡇࠫ⊺")] if bstack1l1ll1111l_opy_() else bstack1l11l111l_opy_[bstack11111l_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࠨ⊻")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack11ll1ll1_opy_(page, bstack11l111111l_opy_):
    try:
        page.evaluate(bstack11111l_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ⊼"),
                      bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠧ⊽") + json.dumps(
                          bstack11l111111l_opy_) + bstack11111l_opy_ (u"ࠦࢂࢃࠢ⊾"))
    except Exception as e:
        print(bstack11111l_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠠࡼࡿࠥ⊿"), e)
def bstack1l11ll11l_opy_(page, message, level):
    try:
        page.evaluate(bstack11111l_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢ⋀"), bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬ⋁") + json.dumps(
            message) + bstack11111l_opy_ (u"ࠨ࠮ࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠫ⋂") + json.dumps(level) + bstack11111l_opy_ (u"ࠩࢀࢁࠬ⋃"))
    except Exception as e:
        print(bstack11111l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡡ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠣࡿࢂࠨ⋄"), e)
def pytest_configure(config):
    global bstack11l11l1l1l_opy_
    global CONFIG
    bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
    config.args = bstack11l11ll11l_opy_.bstack1lll1ll11111_opy_(config.args)
    bstack11l11l1lll_opy_.bstack1l11111111_opy_(bstack1lll11ll11_opy_(config.getoption(bstack11111l_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ⋅"))))
    try:
        bstack1l1llll1_opy_.bstack111l11llll1_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack11lllll1ll_opy_.invoke(bstack11lll1l1l_opy_.CONNECT, bstack11l1111l11_opy_())
        cli_context.platform_index = int(os.environ.get(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬ⋆"), bstack11111l_opy_ (u"࠭࠰ࠨ⋇")))
        config = json.loads(os.environ.get(bstack11111l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࠨ⋈"), bstack11111l_opy_ (u"ࠣࡽࢀࠦ⋉")))
        cli.bstack1lll1l1ll1l_opy_(bstack1ll1111lll_opy_(bstack11l11l1l1l_opy_, CONFIG), cli_context.platform_index, bstack11l111111_opy_)
    if cli.bstack1lll1ll111l_opy_(bstack1ll1l1111ll_opy_):
        cli.bstack1ll1l1l11ll_opy_()
        logger.debug(bstack11111l_opy_ (u"ࠤࡆࡐࡎࠦࡩࡴࠢࡤࡧࡹ࡯ࡶࡦࠢࡩࡳࡷࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾ࠽ࠣ⋊") + str(cli_context.platform_index) + bstack11111l_opy_ (u"ࠥࠦ⋋"))
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.BEFORE_ALL, bstack1lll1ll1111_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack11111l_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤ⋌"), None)
    if cli.is_running() and when == bstack11111l_opy_ (u"ࠧࡩࡡ࡭࡮ࠥ⋍"):
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.LOG_REPORT, bstack1lll1ll1111_opy_.PRE, item, call)
    outcome = yield
    if when == bstack11111l_opy_ (u"ࠨࡣࡢ࡮࡯ࠦ⋎"):
        report = outcome.get_result()
        passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11111l_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤ⋏")))
        if not passed:
            config = json.loads(os.environ.get(bstack11111l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠢ⋐"), bstack11111l_opy_ (u"ࠤࡾࢁࠧ⋑")))
            if bstack1l11ll1111_opy_.bstack1l1l1l1l11_opy_(config):
                bstack1lllllll1lll_opy_ = bstack1l11ll1111_opy_.bstack111lll111_opy_(config)
                if item.execution_count > bstack1lllllll1lll_opy_:
                    print(bstack11111l_opy_ (u"ࠪࡘࡪࡹࡴࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡣࡩࡸࡪࡸࠠࡳࡧࡷࡶ࡮࡫ࡳ࠻ࠢࠪ⋒"), report.nodeid, os.environ.get(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ⋓")))
                    bstack1l11ll1111_opy_.bstack1111ll1l1l1_opy_(report.nodeid)
            else:
                print(bstack11111l_opy_ (u"࡚ࠬࡥࡴࡶࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࠬ⋔"), report.nodeid, os.environ.get(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ⋕")))
                bstack1l11ll1111_opy_.bstack1111ll1l1l1_opy_(report.nodeid)
        else:
            print(bstack11111l_opy_ (u"ࠧࡕࡧࡶࡸࠥࡶࡡࡴࡵࡨࡨ࠿ࠦࠧ⋖"), report.nodeid, os.environ.get(bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭⋗")))
    if cli.is_running():
        if when == bstack11111l_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣ⋘"):
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.BEFORE_EACH, bstack1lll1ll1111_opy_.POST, item, call, outcome)
        elif when == bstack11111l_opy_ (u"ࠥࡧࡦࡲ࡬ࠣ⋙"):
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.LOG_REPORT, bstack1lll1ll1111_opy_.POST, item, call, outcome)
        elif when == bstack11111l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨ⋚"):
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.AFTER_EACH, bstack1lll1ll1111_opy_.POST, item, call, outcome)
        return # skip all existing operations
    skipSessionName = item.config.getoption(bstack11111l_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ⋛"))
    plugins = item.config.getoption(bstack11111l_opy_ (u"ࠨࡰ࡭ࡷࡪ࡭ࡳࡹࠢ⋜"))
    report = outcome.get_result()
    os.environ[bstack11111l_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪ⋝")] = report.nodeid
    bstack1lll11lllll1_opy_(item, call, report)
    if bstack11111l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡰ࡭ࡷࡪ࡭ࡳࠨ⋞") not in plugins or bstack1l1ll1111l_opy_():
        return
    summary = []
    driver = getattr(item, bstack11111l_opy_ (u"ࠤࡢࡨࡷ࡯ࡶࡦࡴࠥ⋟"), None)
    page = getattr(item, bstack11111l_opy_ (u"ࠥࡣࡵࡧࡧࡦࠤ⋠"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack1lll1l1111ll_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack1lll1l1l1ll1_opy_(item, report, summary, skipSessionName)
def bstack1lll1l1111ll_opy_(item, report, summary, skipSessionName):
    if report.when == bstack11111l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ⋡") and report.skipped:
        bstack1lllll1l1l11_opy_(report)
    if report.when in [bstack11111l_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦ⋢"), bstack11111l_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࠣ⋣")]:
        return
    if not bstack1l1ll11lll1_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack11111l_opy_ (u"ࠧࡵࡴࡸࡩࠬ⋤")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭⋥") + json.dumps(
                    report.nodeid) + bstack11111l_opy_ (u"ࠩࢀࢁࠬ⋦"))
        os.environ[bstack11111l_opy_ (u"ࠪࡔ࡞࡚ࡅࡔࡖࡢࡘࡊ࡙ࡔࡠࡐࡄࡑࡊ࠭⋧")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack11111l_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࡀࠠࡼ࠲ࢀࠦ⋨").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11111l_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ⋩")))
    bstack1lll1ll11l_opy_ = bstack11111l_opy_ (u"ࠨࠢ⋪")
    bstack1lllll1l1l11_opy_(report)
    if not passed:
        try:
            bstack1lll1ll11l_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack11111l_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡵࡩࡦࡹ࡯࡯࠼ࠣࡿ࠵ࢃࠢ⋫").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1lll1ll11l_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack11111l_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ⋬")))
        bstack1lll1ll11l_opy_ = bstack11111l_opy_ (u"ࠤࠥ⋭")
        if not passed:
            try:
                bstack1lll1ll11l_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack11111l_opy_ (u"࡛ࠥࡆࡘࡎࡊࡐࡊ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤ࡫ࡧࡩ࡭ࡷࡵࡩࠥࡸࡥࡢࡵࡲࡲ࠿ࠦࡻ࠱ࡿࠥ⋮").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1lll1ll11l_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡥࡣࡷࡥࠧࡀࠠࠨ⋯")
                    + json.dumps(bstack11111l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠦࠨ⋰"))
                    + bstack11111l_opy_ (u"ࠨ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࠤ⋱")
                )
            else:
                item._driver.execute_script(
                    bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡩࡧࡴࡢࠤ࠽ࠤࠬ⋲")
                    + json.dumps(str(bstack1lll1ll11l_opy_))
                    + bstack11111l_opy_ (u"ࠣ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࠦ⋳")
                )
        except Exception as e:
            summary.append(bstack11111l_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡢࡰࡱࡳࡹࡧࡴࡦ࠼ࠣࡿ࠵ࢃࠢ⋴").format(e))
def bstack1lll1l11l1l1_opy_(test_name, error_message):
    try:
        bstack1lll1l111111_opy_ = []
        bstack1l11l111ll_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ⋵"), bstack11111l_opy_ (u"ࠫ࠵࠭⋶"))
        bstack1l11ll111_opy_ = {bstack11111l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⋷"): test_name, bstack11111l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ⋸"): error_message, bstack11111l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭⋹"): bstack1l11l111ll_opy_}
        bstack1lll1l1l1l11_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠨࡲࡺࡣࡵࡿࡴࡦࡵࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭⋺"))
        if os.path.exists(bstack1lll1l1l1l11_opy_):
            with open(bstack1lll1l1l1l11_opy_) as f:
                bstack1lll1l111111_opy_ = json.load(f)
        bstack1lll1l111111_opy_.append(bstack1l11ll111_opy_)
        with open(bstack1lll1l1l1l11_opy_, bstack11111l_opy_ (u"ࠩࡺࠫ⋻")) as f:
            json.dump(bstack1lll1l111111_opy_, f)
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡥࡳࡵ࡬ࡷࡹ࡯࡮ࡨࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡰࡺࡶࡨࡷࡹࠦࡥࡳࡴࡲࡶࡸࡀࠠࠨ⋼") + str(e))
def bstack1lll1l1l1ll1_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack11111l_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࠥ⋽"), bstack11111l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢ⋾")]:
        return
    if (str(skipSessionName).lower() != bstack11111l_opy_ (u"࠭ࡴࡳࡷࡨࠫ⋿")):
        bstack11ll1ll1_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack11111l_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤ⌀")))
    bstack1lll1ll11l_opy_ = bstack11111l_opy_ (u"ࠣࠤ⌁")
    bstack1lllll1l1l11_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1lll1ll11l_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack11111l_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡷ࡫ࡡࡴࡱࡱ࠾ࠥࢁ࠰ࡾࠤ⌂").format(e)
                )
        try:
            if passed:
                bstack11l11111l_opy_(getattr(item, bstack11111l_opy_ (u"ࠪࡣࡵࡧࡧࡦࠩ⌃"), None), bstack11111l_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ⌄"))
            else:
                error_message = bstack11111l_opy_ (u"ࠬ࠭⌅")
                if bstack1lll1ll11l_opy_:
                    bstack1l11ll11l_opy_(item._page, str(bstack1lll1ll11l_opy_), bstack11111l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ⌆"))
                    bstack11l11111l_opy_(getattr(item, bstack11111l_opy_ (u"ࠧࡠࡲࡤ࡫ࡪ࠭⌇"), None), bstack11111l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ⌈"), str(bstack1lll1ll11l_opy_))
                    error_message = str(bstack1lll1ll11l_opy_)
                else:
                    bstack11l11111l_opy_(getattr(item, bstack11111l_opy_ (u"ࠩࡢࡴࡦ࡭ࡥࠨ⌉"), None), bstack11111l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ⌊"))
                bstack1lll1l11l1l1_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack11111l_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡸࡴࡩࡧࡴࡦࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀ࠶ࡽࠣ⌋").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack11111l_opy_ (u"ࠧ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ⌌"), default=bstack11111l_opy_ (u"ࠨࡆࡢ࡮ࡶࡩࠧ⌍"), help=bstack11111l_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡪࡥࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠨ⌎"))
    parser.addoption(bstack11111l_opy_ (u"ࠣ࠯࠰ࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ⌏"), default=bstack11111l_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣ⌐"), help=bstack11111l_opy_ (u"ࠥࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡨࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠤ⌑"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack11111l_opy_ (u"ࠦ࠲࠳ࡤࡳ࡫ࡹࡩࡷࠨ⌒"), action=bstack11111l_opy_ (u"ࠧࡹࡴࡰࡴࡨࠦ⌓"), default=bstack11111l_opy_ (u"ࠨࡣࡩࡴࡲࡱࡪࠨ⌔"),
                         help=bstack11111l_opy_ (u"ࠢࡅࡴ࡬ࡺࡪࡸࠠࡵࡱࠣࡶࡺࡴࠠࡵࡧࡶࡸࡸࠨ⌕"))
def bstack111l1ll1ll_opy_(log):
    if not (log[bstack11111l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⌖")] and log[bstack11111l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ⌗")].strip()):
        return
    active = bstack111ll1l1ll_opy_()
    log = {
        bstack11111l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ⌘"): log[bstack11111l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ⌙")],
        bstack11111l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ⌚"): bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"࡚࠭ࠨ⌛"),
        bstack11111l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⌜"): log[bstack11111l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⌝")],
    }
    if active:
        if active[bstack11111l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⌞")] == bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⌟"):
            log[bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⌠")] = active[bstack11111l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⌡")]
        elif active[bstack11111l_opy_ (u"࠭ࡴࡺࡲࡨࠫ⌢")] == bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࠬ⌣"):
            log[bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⌤")] = active[bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⌥")]
    bstack11l1ll1l1l_opy_.bstack1l111111l_opy_([log])
def bstack111ll1l1ll_opy_():
    if len(store[bstack11111l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⌦")]) > 0 and store[bstack11111l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⌧")][-1]:
        return {
            bstack11111l_opy_ (u"ࠬࡺࡹࡱࡧࠪ⌨"): bstack11111l_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ〈"),
            bstack11111l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ〉"): store[bstack11111l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⌫")][-1]
        }
    if store.get(bstack11111l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭⌬"), None):
        return {
            bstack11111l_opy_ (u"ࠪࡸࡾࡶࡥࠨ⌭"): bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⌮"),
            bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⌯"): store[bstack11111l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ⌰")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.INIT_TEST, bstack1lll1ll1111_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.INIT_TEST, bstack1lll1ll1111_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._1lll1l111l11_opy_ = True
        bstack1llll1ll1l_opy_ = bstack1l1l11ll11_opy_.bstack11llllllll_opy_(bstack11l1111llll_opy_(item.own_markers))
        if not cli.bstack1lll1ll111l_opy_(bstack1ll1l1111ll_opy_):
            item._a11y_test_case = bstack1llll1ll1l_opy_
            if bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭⌱"), None):
                driver = getattr(item, bstack11111l_opy_ (u"ࠨࡡࡧࡶ࡮ࡼࡥࡳࠩ⌲"), None)
                item._a11y_started = bstack1l1l11ll11_opy_.bstack11l111l111_opy_(driver, bstack1llll1ll1l_opy_)
        if not bstack11l1ll1l1l_opy_.on() or bstack1lll1l1ll111_opy_ != bstack11111l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ⌳"):
            return
        global current_test_uuid #, bstack111l1lllll_opy_
        bstack1111ll1l11_opy_ = {
            bstack11111l_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⌴"): uuid4().__str__(),
            bstack11111l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⌵"): bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"ࠬࡠࠧ⌶")
        }
        current_test_uuid = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⌷")]
        store[bstack11111l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⌸")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⌹")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _111l11ll1l_opy_[item.nodeid] = {**_111l11ll1l_opy_[item.nodeid], **bstack1111ll1l11_opy_}
        bstack1lll1l11l11l_opy_(item, _111l11ll1l_opy_[item.nodeid], bstack11111l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ⌺"))
    except Exception as err:
        print(bstack11111l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡵࡹࡳࡺࡥࡴࡶࡢࡧࡦࡲ࡬࠻ࠢࡾࢁࠬ⌻"), str(err))
def pytest_runtest_setup(item):
    store[bstack11111l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡹ࡫࡭ࠨ⌼")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.BEFORE_EACH, bstack1lll1ll1111_opy_.PRE, item, bstack11111l_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⌽"))
    if bstack1l11ll1111_opy_.bstack1111l11lll1_opy_():
            bstack1lll1l11ll11_opy_ = bstack11111l_opy_ (u"ࠨࡓ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡡࡴࠢࡷ࡬ࡪࠦࡡࡣࡱࡵࡸࠥࡨࡵࡪ࡮ࡧࠤ࡫࡯࡬ࡦࠢࡨࡼ࡮ࡹࡴࡴ࠰ࠥ⌾")
            logger.error(bstack1lll1l11ll11_opy_)
            bstack1111ll1l11_opy_ = {
                bstack11111l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⌿"): uuid4().__str__(),
                bstack11111l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⍀"): bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"ࠩ࡝ࠫ⍁"),
                bstack11111l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⍂"): bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"ࠫ࡟࠭⍃"),
                bstack11111l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⍄"): bstack11111l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ⍅"),
                bstack11111l_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ⍆"): bstack1lll1l11ll11_opy_,
                bstack11111l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⍇"): [],
                bstack11111l_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⍈"): []
            }
            bstack1lll1l11l11l_opy_(item, bstack1111ll1l11_opy_, bstack11111l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ⍉"))
            pytest.skip(bstack1lll1l11ll11_opy_)
            return # skip all existing operations
    global bstack1lll1l1l1l1l_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack111l1llll1l_opy_():
        atexit.register(bstack1lllll1lll_opy_)
        if not bstack1lll1l1l1l1l_opy_:
            try:
                bstack1lll1l11ll1l_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack111ll1ll1l1_opy_():
                    bstack1lll1l11ll1l_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1lll1l11ll1l_opy_:
                    signal.signal(s, bstack1lll1l1l11l1_opy_)
                bstack1lll1l1l1l1l_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack11111l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡲࡦࡩ࡬ࡷࡹ࡫ࡲࠡࡵ࡬࡫ࡳࡧ࡬ࠡࡪࡤࡲࡩࡲࡥࡳࡵ࠽ࠤࠧ⍊") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1lllll1l1l1l_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack11111l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ⍋")
    try:
        if not bstack11l1ll1l1l_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack1111ll1l11_opy_ = {
            bstack11111l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍌"): uuid,
            bstack11111l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⍍"): bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"ࠨ࡜ࠪ⍎"),
            bstack11111l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⍏"): bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⍐"),
            bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ⍑"): bstack11111l_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠪ⍒"),
            bstack11111l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡳࡧ࡭ࡦࠩ⍓"): bstack11111l_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭⍔")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack11111l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⍕")] = item
        store[bstack11111l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⍖")] = [uuid]
        if not _111l11ll1l_opy_.get(item.nodeid, None):
            _111l11ll1l_opy_[item.nodeid] = {bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⍗"): [], bstack11111l_opy_ (u"ࠫ࡫࡯ࡸࡵࡷࡵࡩࡸ࠭⍘"): []}
        _111l11ll1l_opy_[item.nodeid][bstack11111l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⍙")].append(bstack1111ll1l11_opy_[bstack11111l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍚")])
        _111l11ll1l_opy_[item.nodeid + bstack11111l_opy_ (u"ࠧ࠮ࡵࡨࡸࡺࡶࠧ⍛")] = bstack1111ll1l11_opy_
        bstack1lll1l111ll1_opy_(item, bstack1111ll1l11_opy_, bstack11111l_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⍜"))
    except Exception as err:
        print(bstack11111l_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡶࡩࡹࡻࡰ࠻ࠢࡾࢁࠬ⍝"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.AFTER_EACH, bstack1lll1ll1111_opy_.PRE, item, bstack11111l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ⍞"))
        return # skip all existing operations
    try:
        global bstack1l1111l1_opy_
        bstack1l11l111ll_opy_ = 0
        if bstack1ll11111l1_opy_ is True:
            bstack1l11l111ll_opy_ = int(os.environ.get(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ⍟")))
        if bstack11l111l1ll_opy_.bstack11l11l1111_opy_() == bstack11111l_opy_ (u"ࠧࡺࡲࡶࡧࠥ⍠"):
            if bstack11l111l1ll_opy_.bstack1l1ll11l_opy_() == bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ⍡"):
                bstack1lll1l1l1111_opy_ = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⍢"), None)
                bstack11l1l1l111_opy_ = bstack1lll1l1l1111_opy_ + bstack11111l_opy_ (u"ࠣ࠯ࡷࡩࡸࡺࡣࡢࡵࡨࠦ⍣")
                driver = getattr(item, bstack11111l_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ⍤"), None)
                bstack1l111lll11_opy_ = getattr(item, bstack11111l_opy_ (u"ࠪࡲࡦࡳࡥࠨ⍥"), None)
                bstack1l11l1llll_opy_ = getattr(item, bstack11111l_opy_ (u"ࠫࡺࡻࡩࡥࠩ⍦"), None)
                PercySDK.screenshot(driver, bstack11l1l1l111_opy_, bstack1l111lll11_opy_=bstack1l111lll11_opy_, bstack1l11l1llll_opy_=bstack1l11l1llll_opy_, bstack11llll11ll_opy_=bstack1l11l111ll_opy_)
        if not cli.bstack1lll1ll111l_opy_(bstack1ll1l1111ll_opy_):
            if getattr(item, bstack11111l_opy_ (u"ࠬࡥࡡ࠲࠳ࡼࡣࡸࡺࡡࡳࡶࡨࡨࠬ⍧"), False):
                bstack1lllll1l1_opy_.bstack1ll1ll1l_opy_(getattr(item, bstack11111l_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⍨"), None), bstack1l1111l1_opy_, logger, item)
        if not bstack11l1ll1l1l_opy_.on():
            return
        bstack1111ll1l11_opy_ = {
            bstack11111l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⍩"): uuid4().__str__(),
            bstack11111l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⍪"): bstack1111ll1ll1_opy_().isoformat() + bstack11111l_opy_ (u"ࠩ࡝ࠫ⍫"),
            bstack11111l_opy_ (u"ࠪࡸࡾࡶࡥࠨ⍬"): bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⍭"),
            bstack11111l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡸࡾࡶࡥࠨ⍮"): bstack11111l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠪ⍯"),
            bstack11111l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠪ⍰"): bstack11111l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⍱")
        }
        _111l11ll1l_opy_[item.nodeid + bstack11111l_opy_ (u"ࠩ࠰ࡸࡪࡧࡲࡥࡱࡺࡲࠬ⍲")] = bstack1111ll1l11_opy_
        bstack1lll1l111ll1_opy_(item, bstack1111ll1l11_opy_, bstack11111l_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⍳"))
    except Exception as err:
        print(bstack11111l_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡶࡺࡴࡴࡦࡵࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡀࠠࡼࡿࠪ⍴"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack1lllll1l11l1_opy_(fixturedef.argname):
        store[bstack11111l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥ࡭ࡰࡦࡸࡰࡪࡥࡩࡵࡧࡰࠫ⍵")] = request.node
    elif bstack1lllll11l1ll_opy_(fixturedef.argname):
        store[bstack11111l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡤ࡮ࡤࡷࡸࡥࡩࡵࡧࡰࠫ⍶")] = request.node
    if not bstack11l1ll1l1l_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.SETUP_FIXTURE, bstack1lll1ll1111_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.SETUP_FIXTURE, bstack1lll1ll1111_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.SETUP_FIXTURE, bstack1lll1ll1111_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.SETUP_FIXTURE, bstack1lll1ll1111_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    try:
        fixture = {
            bstack11111l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⍷"): fixturedef.argname,
            bstack11111l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⍸"): bstack111ll1ll11l_opy_(outcome),
            bstack11111l_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫ⍹"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack11111l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧ⍺")]
        if not _111l11ll1l_opy_.get(current_test_item.nodeid, None):
            _111l11ll1l_opy_[current_test_item.nodeid] = {bstack11111l_opy_ (u"ࠫ࡫࡯ࡸࡵࡷࡵࡩࡸ࠭⍻"): []}
        _111l11ll1l_opy_[current_test_item.nodeid][bstack11111l_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ⍼")].append(fixture)
    except Exception as err:
        logger.debug(bstack11111l_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡳࡦࡶࡸࡴ࠿ࠦࡻࡾࠩ⍽"), str(err))
if bstack1l1ll1111l_opy_() and bstack11l1ll1l1l_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.STEP, bstack1lll1ll1111_opy_.PRE, request, step)
            return
        try:
            _111l11ll1l_opy_[request.node.nodeid][bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⍾")].bstack1llll1l111_opy_(id(step))
        except Exception as err:
            print(bstack11111l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱ࠼ࠣࡿࢂ࠭⍿"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.STEP, bstack1lll1ll1111_opy_.POST, request, step, exception)
            return
        try:
            _111l11ll1l_opy_[request.node.nodeid][bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⎀")].bstack111ll11111_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack11111l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡳࡵࡧࡳࡣࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠧ⎁"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.STEP, bstack1lll1ll1111_opy_.POST, request, step)
            return
        try:
            bstack111l1ll1l1_opy_: bstack111ll1l11l_opy_ = _111l11ll1l_opy_[request.node.nodeid][bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ⎂")]
            bstack111l1ll1l1_opy_.bstack111ll11111_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack11111l_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡵࡷࡩࡵࡥࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠩ⎃"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1lll1l1ll111_opy_
        try:
            if not bstack11l1ll1l1l_opy_.on() or bstack1lll1l1ll111_opy_ != bstack11111l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠪ⎄"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.TEST, bstack1lll1ll1111_opy_.PRE, request, feature, scenario)
                return
            driver = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭⎅"), None)
            if not _111l11ll1l_opy_.get(request.node.nodeid, None):
                _111l11ll1l_opy_[request.node.nodeid] = {}
            bstack111l1ll1l1_opy_ = bstack111ll1l11l_opy_.bstack1llll11lll1l_opy_(
                scenario, feature, request.node,
                name=bstack1lllll11l111_opy_(request.node, scenario),
                started_at=bstack111l1l11_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack11111l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪ⎆"),
                tags=bstack1lllll1l111l_opy_(feature, scenario),
                bstack111l1lll1l_opy_=bstack11l1ll1l1l_opy_.bstack111l1l1l1l_opy_(driver) if driver and driver.session_id else {}
            )
            _111l11ll1l_opy_[request.node.nodeid][bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⎇")] = bstack111l1ll1l1_opy_
            bstack1lll1l1ll1ll_opy_(bstack111l1ll1l1_opy_.uuid)
            bstack11l1ll1l1l_opy_.bstack111l1ll11l_opy_(bstack11111l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⎈"), bstack111l1ll1l1_opy_)
        except Exception as err:
            print(bstack11111l_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰ࠼ࠣࡿࢂ࠭⎉"), str(err))
def bstack1lll1l11l111_opy_(bstack111l1l1ll1_opy_):
    if bstack111l1l1ll1_opy_ in store[bstack11111l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ⎊")]:
        store[bstack11111l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⎋")].remove(bstack111l1l1ll1_opy_)
def bstack1lll1l1ll1ll_opy_(test_uuid):
    store[bstack11111l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⎌")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack11l1ll1l1l_opy_.bstack1lll1llll11l_opy_
def bstack1lll11lllll1_opy_(item, call, report):
    logger.debug(bstack11111l_opy_ (u"ࠨࡪࡤࡲࡩࡲࡥࡠࡱ࠴࠵ࡾࡥࡴࡦࡵࡷࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡸࡺࡡࡳࡶࠪ⎍"))
    global bstack1lll1l1ll111_opy_
    bstack111llll1l_opy_ = bstack111l1l11_opy_()
    if hasattr(report, bstack11111l_opy_ (u"ࠩࡶࡸࡴࡶࠧ⎎")):
        bstack111llll1l_opy_ = bstack111l1lllll1_opy_(report.stop)
    elif hasattr(report, bstack11111l_opy_ (u"ࠪࡷࡹࡧࡲࡵࠩ⎏")):
        bstack111llll1l_opy_ = bstack111l1lllll1_opy_(report.start)
    try:
        if getattr(report, bstack11111l_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩ⎐"), bstack11111l_opy_ (u"ࠬ࠭⎑")) == bstack11111l_opy_ (u"࠭ࡣࡢ࡮࡯ࠫ⎒"):
            logger.debug(bstack11111l_opy_ (u"ࠧࡩࡣࡱࡨࡱ࡫࡟ࡰ࠳࠴ࡽࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡷࡹࡧࡴࡦࠢ࠰ࠤࢀࢃࠬࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤ࠲ࠦࡻࡾࠩ⎓").format(getattr(report, bstack11111l_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⎔"), bstack11111l_opy_ (u"ࠩࠪ⎕")).__str__(), bstack1lll1l1ll111_opy_))
            if bstack1lll1l1ll111_opy_ == bstack11111l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⎖"):
                _111l11ll1l_opy_[item.nodeid][bstack11111l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⎗")] = bstack111llll1l_opy_
                bstack1lll1l11l11l_opy_(item, _111l11ll1l_opy_[item.nodeid], bstack11111l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⎘"), report, call)
                store[bstack11111l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ⎙")] = None
            elif bstack1lll1l1ll111_opy_ == bstack11111l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦ⎚"):
                bstack111l1ll1l1_opy_ = _111l11ll1l_opy_[item.nodeid][bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ⎛")]
                bstack111l1ll1l1_opy_.set(hooks=_111l11ll1l_opy_[item.nodeid].get(bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⎜"), []))
                exception, bstack111ll1l1l1_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack111ll1l1l1_opy_ = [call.excinfo.exconly(), getattr(report, bstack11111l_opy_ (u"ࠪࡰࡴࡴࡧࡳࡧࡳࡶࡹ࡫ࡸࡵࠩ⎝"), bstack11111l_opy_ (u"ࠫࠬ⎞"))]
                bstack111l1ll1l1_opy_.stop(time=bstack111llll1l_opy_, result=Result(result=getattr(report, bstack11111l_opy_ (u"ࠬࡵࡵࡵࡥࡲࡱࡪ࠭⎟"), bstack11111l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭⎠")), exception=exception, bstack111ll1l1l1_opy_=bstack111ll1l1l1_opy_))
                bstack11l1ll1l1l_opy_.bstack111l1ll11l_opy_(bstack11111l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ⎡"), _111l11ll1l_opy_[item.nodeid][bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ⎢")])
        elif getattr(report, bstack11111l_opy_ (u"ࠩࡺ࡬ࡪࡴࠧ⎣"), bstack11111l_opy_ (u"ࠪࠫ⎤")) in [bstack11111l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ⎥"), bstack11111l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧ⎦")]:
            logger.debug(bstack11111l_opy_ (u"࠭ࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡶࡸࡦࡺࡥࠡ࠯ࠣࡿࢂ࠲ࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠣ࠱ࠥࢁࡽࠨ⎧").format(getattr(report, bstack11111l_opy_ (u"ࠧࡸࡪࡨࡲࠬ⎨"), bstack11111l_opy_ (u"ࠨࠩ⎩")).__str__(), bstack1lll1l1ll111_opy_))
            bstack111ll111l1_opy_ = item.nodeid + bstack11111l_opy_ (u"ࠩ࠰ࠫ⎪") + getattr(report, bstack11111l_opy_ (u"ࠪࡻ࡭࡫࡮ࠨ⎫"), bstack11111l_opy_ (u"ࠫࠬ⎬"))
            if getattr(report, bstack11111l_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭⎭"), False):
                hook_type = bstack11111l_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫ⎮") if getattr(report, bstack11111l_opy_ (u"ࠧࡸࡪࡨࡲࠬ⎯"), bstack11111l_opy_ (u"ࠨࠩ⎰")) == bstack11111l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⎱") else bstack11111l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ⎲")
                _111l11ll1l_opy_[bstack111ll111l1_opy_] = {
                    bstack11111l_opy_ (u"ࠫࡺࡻࡩࡥࠩ⎳"): uuid4().__str__(),
                    bstack11111l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⎴"): bstack111llll1l_opy_,
                    bstack11111l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ⎵"): hook_type
                }
            _111l11ll1l_opy_[bstack111ll111l1_opy_][bstack11111l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⎶")] = bstack111llll1l_opy_
            bstack1lll1l11l111_opy_(_111l11ll1l_opy_[bstack111ll111l1_opy_][bstack11111l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⎷")])
            bstack1lll1l111ll1_opy_(item, _111l11ll1l_opy_[bstack111ll111l1_opy_], bstack11111l_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⎸"), report, call)
            if getattr(report, bstack11111l_opy_ (u"ࠪࡻ࡭࡫࡮ࠨ⎹"), bstack11111l_opy_ (u"ࠫࠬ⎺")) == bstack11111l_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⎻"):
                if getattr(report, bstack11111l_opy_ (u"࠭࡯ࡶࡶࡦࡳࡲ࡫ࠧ⎼"), bstack11111l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⎽")) == bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⎾"):
                    bstack1111ll1l11_opy_ = {
                        bstack11111l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⎿"): uuid4().__str__(),
                        bstack11111l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⏀"): bstack111l1l11_opy_(),
                        bstack11111l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⏁"): bstack111l1l11_opy_()
                    }
                    _111l11ll1l_opy_[item.nodeid] = {**_111l11ll1l_opy_[item.nodeid], **bstack1111ll1l11_opy_}
                    bstack1lll1l11l11l_opy_(item, _111l11ll1l_opy_[item.nodeid], bstack11111l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭⏂"))
                    bstack1lll1l11l11l_opy_(item, _111l11ll1l_opy_[item.nodeid], bstack11111l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⏃"), report, call)
    except Exception as err:
        print(bstack11111l_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡾࢁࠬ⏄"), str(err))
def bstack1lll11llllll_opy_(test, bstack1111ll1l11_opy_, result=None, call=None, bstack1l111l1lll_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111l1ll1l1_opy_ = {
        bstack11111l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⏅"): bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⏆")],
        bstack11111l_opy_ (u"ࠪࡸࡾࡶࡥࠨ⏇"): bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⏈"),
        bstack11111l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⏉"): test.name,
        bstack11111l_opy_ (u"࠭ࡢࡰࡦࡼࠫ⏊"): {
            bstack11111l_opy_ (u"ࠧ࡭ࡣࡱ࡫ࠬ⏋"): bstack11111l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ⏌"),
            bstack11111l_opy_ (u"ࠩࡦࡳࡩ࡫ࠧ⏍"): inspect.getsource(test.obj)
        },
        bstack11111l_opy_ (u"ࠪ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ⏎"): test.name,
        bstack11111l_opy_ (u"ࠫࡸࡩ࡯ࡱࡧࠪ⏏"): test.name,
        bstack11111l_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬ⏐"): bstack11l11ll11l_opy_.bstack1111lll1ll_opy_(test),
        bstack11111l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ⏑"): file_path,
        bstack11111l_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠩ⏒"): file_path,
        bstack11111l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⏓"): bstack11111l_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ⏔"),
        bstack11111l_opy_ (u"ࠪࡺࡨࡥࡦࡪ࡮ࡨࡴࡦࡺࡨࠨ⏕"): file_path,
        bstack11111l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⏖"): bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⏗")],
        bstack11111l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ⏘"): bstack11111l_opy_ (u"ࠧࡑࡻࡷࡩࡸࡺࠧ⏙"),
        bstack11111l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡓࡧࡵࡹࡳࡖࡡࡳࡣࡰࠫ⏚"): {
            bstack11111l_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡰࡤࡱࡪ࠭⏛"): test.nodeid
        },
        bstack11111l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ⏜"): bstack11l1111llll_opy_(test.own_markers)
    }
    if bstack1l111l1lll_opy_ in [bstack11111l_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡱࡩࡱࡲࡨࡨࠬ⏝"), bstack11111l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⏞")]:
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"࠭࡭ࡦࡶࡤࠫ⏟")] = {
            bstack11111l_opy_ (u"ࠧࡧ࡫ࡻࡸࡺࡸࡥࡴࠩ⏠"): bstack1111ll1l11_opy_.get(bstack11111l_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪ⏡"), [])
        }
    if bstack1l111l1lll_opy_ == bstack11111l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ⏢"):
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⏣")] = bstack11111l_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⏤")
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⏥")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⏦")]
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⏧")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⏨")]
    if result:
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⏩")] = result.outcome
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫ⏪")] = result.duration * 1000
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⏫")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⏬")]
        if result.failed:
            bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ⏭")] = bstack11l1ll1l1l_opy_.bstack1llllll1111_opy_(call.excinfo.typename)
            bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ⏮")] = bstack11l1ll1l1l_opy_.bstack1lll1lllll1l_opy_(call.excinfo, result)
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⏯")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⏰")]
    if outcome:
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⏱")] = bstack111ll1ll11l_opy_(outcome)
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬ⏲")] = 0
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⏳")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⏴")]
        if bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⏵")] == bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⏶"):
            bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨ⏷")] = bstack11111l_opy_ (u"࡙ࠪࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠫ⏸")  # bstack1lll1l1l11ll_opy_
            bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ⏹")] = [{bstack11111l_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ⏺"): [bstack11111l_opy_ (u"࠭ࡳࡰ࡯ࡨࠤࡪࡸࡲࡰࡴࠪ⏻")]}]
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⏼")] = bstack1111ll1l11_opy_[bstack11111l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⏽")]
    return bstack111l1ll1l1_opy_
def bstack1lll1l1l1lll_opy_(test, bstack111l11l11l_opy_, bstack1l111l1lll_opy_, result, call, outcome, bstack1lll1l1ll11l_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ⏾")]
    hook_name = bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡰࡤࡱࡪ࠭⏿")]
    hook_data = {
        bstack11111l_opy_ (u"ࠫࡺࡻࡩࡥࠩ␀"): bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠬࡻࡵࡪࡦࠪ␁")],
        bstack11111l_opy_ (u"࠭ࡴࡺࡲࡨࠫ␂"): bstack11111l_opy_ (u"ࠧࡩࡱࡲ࡯ࠬ␃"),
        bstack11111l_opy_ (u"ࠨࡰࡤࡱࡪ࠭␄"): bstack11111l_opy_ (u"ࠩࡾࢁࠬ␅").format(bstack1lllll11ll1l_opy_(hook_name)),
        bstack11111l_opy_ (u"ࠪࡦࡴࡪࡹࠨ␆"): {
            bstack11111l_opy_ (u"ࠫࡱࡧ࡮ࡨࠩ␇"): bstack11111l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ␈"),
            bstack11111l_opy_ (u"࠭ࡣࡰࡦࡨࠫ␉"): None
        },
        bstack11111l_opy_ (u"ࠧࡴࡥࡲࡴࡪ࠭␊"): test.name,
        bstack11111l_opy_ (u"ࠨࡵࡦࡳࡵ࡫ࡳࠨ␋"): bstack11l11ll11l_opy_.bstack1111lll1ll_opy_(test, hook_name),
        bstack11111l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ␌"): file_path,
        bstack11111l_opy_ (u"ࠪࡰࡴࡩࡡࡵ࡫ࡲࡲࠬ␍"): file_path,
        bstack11111l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ␎"): bstack11111l_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭␏"),
        bstack11111l_opy_ (u"࠭ࡶࡤࡡࡩ࡭ࡱ࡫ࡰࡢࡶ࡫ࠫ␐"): file_path,
        bstack11111l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ␑"): bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ␒")],
        bstack11111l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ␓"): bstack11111l_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶ࠰ࡧࡺࡩࡵ࡮ࡤࡨࡶࠬ␔") if bstack1lll1l1ll111_opy_ == bstack11111l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨ␕") else bstack11111l_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ␖"),
        bstack11111l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ␗"): hook_type
    }
    bstack1l1llll1ll1_opy_ = bstack111l111l1l_opy_(_111l11ll1l_opy_.get(test.nodeid, None))
    if bstack1l1llll1ll1_opy_:
        hook_data[bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡ࡬ࡨࠬ␘")] = bstack1l1llll1ll1_opy_
    if result:
        hook_data[bstack11111l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ␙")] = result.outcome
        hook_data[bstack11111l_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ␚")] = result.duration * 1000
        hook_data[bstack11111l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ␛")] = bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ␜")]
        if result.failed:
            hook_data[bstack11111l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠫ␝")] = bstack11l1ll1l1l_opy_.bstack1llllll1111_opy_(call.excinfo.typename)
            hook_data[bstack11111l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ␞")] = bstack11l1ll1l1l_opy_.bstack1lll1lllll1l_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack11111l_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ␟")] = bstack111ll1ll11l_opy_(outcome)
        hook_data[bstack11111l_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ␠")] = 100
        hook_data[bstack11111l_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ␡")] = bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ␢")]
        if hook_data[bstack11111l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ␣")] == bstack11111l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ␤"):
            hook_data[bstack11111l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ␥")] = bstack11111l_opy_ (u"ࠧࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠨ␦")  # bstack1lll1l1l11ll_opy_
            hook_data[bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩ␧")] = [{bstack11111l_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬ␨"): [bstack11111l_opy_ (u"ࠪࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠧ␩")]}]
    if bstack1lll1l1ll11l_opy_:
        hook_data[bstack11111l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ␪")] = bstack1lll1l1ll11l_opy_.result
        hook_data[bstack11111l_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡢࡱࡸ࠭␫")] = bstack111llll1ll1_opy_(bstack111l11l11l_opy_[bstack11111l_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ␬")], bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ␭")])
        hook_data[bstack11111l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭␮")] = bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ␯")]
        if hook_data[bstack11111l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ␰")] == bstack11111l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ␱"):
            hook_data[bstack11111l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠫ␲")] = bstack11l1ll1l1l_opy_.bstack1llllll1111_opy_(bstack1lll1l1ll11l_opy_.exception_type)
            hook_data[bstack11111l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ␳")] = [{bstack11111l_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪ␴"): bstack11l111111ll_opy_(bstack1lll1l1ll11l_opy_.exception)}]
    return hook_data
def bstack1lll1l11l11l_opy_(test, bstack1111ll1l11_opy_, bstack1l111l1lll_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack11111l_opy_ (u"ࠨࡵࡨࡲࡩࡥࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡧࡹࡩࡳࡺ࠺ࠡࡃࡷࡸࡪࡳࡰࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡩࡨࡲࡪࡸࡡࡵࡧࠣࡸࡪࡹࡴࠡࡦࡤࡸࡦࠦࡦࡰࡴࠣࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠠ࠮ࠢࡾࢁࠬ␵").format(bstack1l111l1lll_opy_))
    bstack111l1ll1l1_opy_ = bstack1lll11llllll_opy_(test, bstack1111ll1l11_opy_, result, call, bstack1l111l1lll_opy_, outcome)
    driver = getattr(test, bstack11111l_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ␶"), None)
    if bstack1l111l1lll_opy_ == bstack11111l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ␷") and driver:
        bstack111l1ll1l1_opy_[bstack11111l_opy_ (u"ࠫ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠪ␸")] = bstack11l1ll1l1l_opy_.bstack111l1l1l1l_opy_(driver)
    if bstack1l111l1lll_opy_ == bstack11111l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙࡫ࡪࡲࡳࡩࡩ࠭␹"):
        bstack1l111l1lll_opy_ = bstack11111l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ␺")
    bstack1111ll1lll_opy_ = {
        bstack11111l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ␻"): bstack1l111l1lll_opy_,
        bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ␼"): bstack111l1ll1l1_opy_
    }
    bstack11l1ll1l1l_opy_.bstack1ll1l1llll_opy_(bstack1111ll1lll_opy_)
    if bstack1l111l1lll_opy_ == bstack11111l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ␽"):
        threading.current_thread().bstackTestMeta = {bstack11111l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ␾"): bstack11111l_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ␿")}
    elif bstack1l111l1lll_opy_ == bstack11111l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⑀"):
        threading.current_thread().bstackTestMeta = {bstack11111l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⑁"): getattr(result, bstack11111l_opy_ (u"ࠧࡰࡷࡷࡧࡴࡳࡥࠨ⑂"), bstack11111l_opy_ (u"ࠨࠩ⑃"))}
def bstack1lll1l111ll1_opy_(test, bstack1111ll1l11_opy_, bstack1l111l1lll_opy_, result=None, call=None, outcome=None, bstack1lll1l1ll11l_opy_=None):
    logger.debug(bstack11111l_opy_ (u"ࠩࡶࡩࡳࡪ࡟ࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡨࡺࡪࡴࡴ࠻ࠢࡄࡸࡹ࡫࡭ࡱࡶ࡬ࡲ࡬ࠦࡴࡰࠢࡪࡩࡳ࡫ࡲࡢࡶࡨࠤ࡭ࡵ࡯࡬ࠢࡧࡥࡹࡧࠬࠡࡧࡹࡩࡳࡺࡔࡺࡲࡨࠤ࠲ࠦࡻࡾࠩ⑄").format(bstack1l111l1lll_opy_))
    hook_data = bstack1lll1l1l1lll_opy_(test, bstack1111ll1l11_opy_, bstack1l111l1lll_opy_, result, call, outcome, bstack1lll1l1ll11l_opy_)
    bstack1111ll1lll_opy_ = {
        bstack11111l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⑅"): bstack1l111l1lll_opy_,
        bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳ࠭⑆"): hook_data
    }
    bstack11l1ll1l1l_opy_.bstack1ll1l1llll_opy_(bstack1111ll1lll_opy_)
def bstack111l111l1l_opy_(bstack1111ll1l11_opy_):
    if not bstack1111ll1l11_opy_:
        return None
    if bstack1111ll1l11_opy_.get(bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⑇"), None):
        return getattr(bstack1111ll1l11_opy_[bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⑈")], bstack11111l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⑉"), None)
    return bstack1111ll1l11_opy_.get(bstack11111l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⑊"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.LOG, bstack1lll1ll1111_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_.LOG, bstack1lll1ll1111_opy_.POST, request, caplog)
        return # skip all existing operations
    try:
        if not bstack11l1ll1l1l_opy_.on():
            return
        places = [bstack11111l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⑋"), bstack11111l_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⑌"), bstack11111l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠭⑍")]
        logs = []
        for bstack1lll1l1111l1_opy_ in places:
            records = caplog.get_records(bstack1lll1l1111l1_opy_)
            bstack1lll1l1ll1l1_opy_ = bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⑎") if bstack1lll1l1111l1_opy_ == bstack11111l_opy_ (u"࠭ࡣࡢ࡮࡯ࠫ⑏") else bstack11111l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⑐")
            bstack1lll1l11llll_opy_ = request.node.nodeid + (bstack11111l_opy_ (u"ࠨࠩ⑑") if bstack1lll1l1111l1_opy_ == bstack11111l_opy_ (u"ࠩࡦࡥࡱࡲࠧ⑒") else bstack11111l_opy_ (u"ࠪ࠱ࠬ⑓") + bstack1lll1l1111l1_opy_)
            test_uuid = bstack111l111l1l_opy_(_111l11ll1l_opy_.get(bstack1lll1l11llll_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack111lll1lll1_opy_(record.message):
                    continue
                logs.append({
                    bstack11111l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ⑔"): bstack111lll11ll1_opy_(record.created).isoformat() + bstack11111l_opy_ (u"ࠬࡠࠧ⑕"),
                    bstack11111l_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⑖"): record.levelname,
                    bstack11111l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⑗"): record.message,
                    bstack1lll1l1ll1l1_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack11l1ll1l1l_opy_.bstack1l111111l_opy_(logs)
    except Exception as err:
        print(bstack11111l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡦࡳࡳࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥ࠻ࠢࡾࢁࠬ⑘"), str(err))
def bstack1lll1l1ll1_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack1ll11ll1l_opy_
    bstack11ll1llll1_opy_ = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠩ࡬ࡷࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭⑙"), None) and bstack11l1l111l_opy_(
            threading.current_thread(), bstack11111l_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ⑚"), None)
    bstack1ll11lll1_opy_ = getattr(driver, bstack11111l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫ⑛"), None) != None and getattr(driver, bstack11111l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡆ࠷࠱ࡺࡕ࡫ࡳࡺࡲࡤࡔࡥࡤࡲࠬ⑜"), None) == True
    if sequence == bstack11111l_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭⑝") and driver != None:
      if not bstack1ll11ll1l_opy_ and bstack1l1ll11lll1_opy_() and bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ⑞") in CONFIG and CONFIG[bstack11111l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⑟")] == True and bstack11ll11111_opy_.bstack1l111lll1_opy_(driver_command) and (bstack1ll11lll1_opy_ or bstack11ll1llll1_opy_) and not bstack11l11l111l_opy_(args):
        try:
          bstack1ll11ll1l_opy_ = True
          logger.debug(bstack11111l_opy_ (u"ࠩࡓࡩࡷ࡬࡯ࡳ࡯࡬ࡲ࡬ࠦࡳࡤࡣࡱࠤ࡫ࡵࡲࠡࡽࢀࠫ①").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack11111l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡦࡴࡩࡳࡷࡳࠠࡴࡥࡤࡲࠥࢁࡽࠨ②").format(str(err)))
        bstack1ll11ll1l_opy_ = False
    if sequence == bstack11111l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪ③"):
        if driver_command == bstack11111l_opy_ (u"ࠬࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࠩ④"):
            bstack11l1ll1l1l_opy_.bstack1l11l11l1l_opy_({
                bstack11111l_opy_ (u"࠭ࡩ࡮ࡣࡪࡩࠬ⑤"): response[bstack11111l_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭⑥")],
                bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⑦"): store[bstack11111l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭⑧")]
            })
def bstack1lllll1lll_opy_():
    global bstack1l1lllll_opy_
    bstack1l1llll1_opy_.bstack11l111llll_opy_()
    logging.shutdown()
    bstack11l1ll1l1l_opy_.bstack1111lllll1_opy_()
    for driver in bstack1l1lllll_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1lll1l1l11l1_opy_(*args):
    global bstack1l1lllll_opy_
    bstack11l1ll1l1l_opy_.bstack1111lllll1_opy_()
    for driver in bstack1l1lllll_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack11l1111111_opy_, stage=STAGE.bstack1ll1l1ll1_opy_, bstack1l1l1ll11l_opy_=bstack11ll1ll1l1_opy_)
def bstack1ll11l111l_opy_(self, *args, **kwargs):
    bstack11l1l1l11_opy_ = bstack1111ll11l_opy_(self, *args, **kwargs)
    bstack11l1llll_opy_ = getattr(threading.current_thread(), bstack11111l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ⑨"), None)
    if bstack11l1llll_opy_ and bstack11l1llll_opy_.get(bstack11111l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⑩"), bstack11111l_opy_ (u"ࠬ࠭⑪")) == bstack11111l_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧ⑫"):
        bstack11l1ll1l1l_opy_.bstack1l111l1ll_opy_(self)
    return bstack11l1l1l11_opy_
@measure(event_name=EVENTS.bstack1ll1ll11l_opy_, stage=STAGE.bstack1ll1l1l1ll_opy_, bstack1l1l1ll11l_opy_=bstack11ll1ll1l1_opy_)
def bstack1l111lll_opy_(framework_name):
    from bstack_utils.config import Config
    bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
    if bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ⑬")):
        return
    bstack11l11l1lll_opy_.bstack1ll1lll11_opy_(bstack11111l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠ࡯ࡲࡨࡤࡩࡡ࡭࡮ࡨࡨࠬ⑭"), True)
    global bstack1llll11l1l_opy_
    global bstack1llll1111_opy_
    bstack1llll11l1l_opy_ = framework_name
    logger.info(bstack111111lll_opy_.format(bstack1llll11l1l_opy_.split(bstack11111l_opy_ (u"ࠩ࠰ࠫ⑮"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1l1ll11lll1_opy_():
            Service.start = bstack1l11lll111_opy_
            Service.stop = bstack1111llll_opy_
            webdriver.Remote.get = bstack1l11111l11_opy_
            webdriver.Remote.__init__ = bstack11lll1ll_opy_
            if not isinstance(os.getenv(bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡅࡗࡇࡌࡍࡇࡏࠫ⑯")), str):
                return
            WebDriver.quit = bstack111lllllll_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack11l1ll1l1l_opy_.on():
            webdriver.Remote.__init__ = bstack1ll11l111l_opy_
        bstack1llll1111_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack11111l_opy_ (u"ࠫࡘࡋࡌࡆࡐࡌ࡙ࡒࡥࡏࡓࡡࡓࡐࡆ࡟ࡗࡓࡋࡊࡌ࡙ࡥࡉࡏࡕࡗࡅࡑࡒࡅࡅࠩ⑰")):
        bstack1llll1111_opy_ = eval(os.environ.get(bstack11111l_opy_ (u"࡙ࠬࡅࡍࡇࡑࡍ࡚ࡓ࡟ࡐࡔࡢࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡊࡐࡖࡘࡆࡒࡌࡆࡆࠪ⑱")))
    if not bstack1llll1111_opy_:
        bstack1l1lll1111_opy_(bstack11111l_opy_ (u"ࠨࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠡࡰࡲࡸࠥ࡯࡮ࡴࡶࡤࡰࡱ࡫ࡤࠣ⑲"), bstack1l11llll11_opy_)
    if bstack1l1l1l1lll_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack11111l_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨ⑳")) and callable(getattr(RemoteConnection, bstack11111l_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩ⑴"))):
                RemoteConnection._get_proxy_url = bstack11lll1l11_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack11lll1l11_opy_
        except Exception as e:
            logger.error(bstack1ll11ll111_opy_.format(str(e)))
    if bstack11111l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ⑵") in str(framework_name).lower():
        if not bstack1l1ll11lll1_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack11l11l11ll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l1l1l1ll1_opy_
            Config.getoption = bstack1l11l1l1l_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack1l11l11ll1_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1lll1111ll_opy_, stage=STAGE.bstack1ll1l1ll1_opy_, bstack1l1l1ll11l_opy_=bstack11ll1ll1l1_opy_)
def bstack111lllllll_opy_(self):
    global bstack1llll11l1l_opy_
    global bstack11ll111l11_opy_
    global bstack11ll1l11_opy_
    try:
        if bstack11111l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⑶") in bstack1llll11l1l_opy_ and self.session_id != None and bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡕࡷࡥࡹࡻࡳࠨ⑷"), bstack11111l_opy_ (u"ࠬ࠭⑸")) != bstack11111l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ⑹"):
            bstack1lll1ll1ll_opy_ = bstack11111l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⑺") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⑻")
            bstack1ll111l1_opy_(logger, True)
            if os.environ.get(bstack11111l_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ⑼"), None):
                self.execute_script(
                    bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨ⑽") + json.dumps(
                        os.environ.get(bstack11111l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧ⑾"))) + bstack11111l_opy_ (u"ࠬࢃࡽࠨ⑿"))
            if self != None:
                bstack1l1111l1l1_opy_(self, bstack1lll1ll1ll_opy_, bstack11111l_opy_ (u"࠭ࠬࠡࠩ⒀").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1lll1ll111l_opy_(bstack1ll1l1111ll_opy_):
            item = store.get(bstack11111l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫ⒁"), None)
            if item is not None and bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ⒂"), None):
                bstack1lllll1l1_opy_.bstack1ll1ll1l_opy_(self, bstack1l1111l1_opy_, logger, item)
        threading.current_thread().testStatus = bstack11111l_opy_ (u"ࠩࠪ⒃")
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦ⒄") + str(e))
    bstack11ll1l11_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack1llll11l11_opy_, stage=STAGE.bstack1ll1l1ll1_opy_, bstack1l1l1ll11l_opy_=bstack11ll1ll1l1_opy_)
def bstack11lll1ll_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack11ll111l11_opy_
    global bstack11ll1ll1l1_opy_
    global bstack1ll11111l1_opy_
    global bstack1llll11l1l_opy_
    global bstack1111ll11l_opy_
    global bstack1l1lllll_opy_
    global bstack11l11l1l1l_opy_
    global bstack1lll1l11_opy_
    global bstack1l1111l1_opy_
    CONFIG[bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭⒅")] = str(bstack1llll11l1l_opy_) + str(__version__)
    command_executor = bstack1ll1111lll_opy_(bstack11l11l1l1l_opy_, CONFIG)
    logger.debug(bstack11ll1111ll_opy_.format(command_executor))
    proxy = bstack11ll11ll1_opy_(CONFIG, proxy)
    bstack1l11l111ll_opy_ = 0
    try:
        if bstack1ll11111l1_opy_ is True:
            bstack1l11l111ll_opy_ = int(os.environ.get(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬ⒆")))
    except:
        bstack1l11l111ll_opy_ = 0
    bstack11ll1l111l_opy_ = bstack1ll111l1l1_opy_(CONFIG, bstack1l11l111ll_opy_)
    logger.debug(bstack1l11lll11l_opy_.format(str(bstack11ll1l111l_opy_)))
    bstack1l1111l1_opy_ = CONFIG.get(bstack11111l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ⒇"))[bstack1l11l111ll_opy_]
    if bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ⒈") in CONFIG and CONFIG[bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ⒉")]:
        bstack1l11ll1ll1_opy_(bstack11ll1l111l_opy_, bstack1lll1l11_opy_)
    if bstack1l1l11ll11_opy_.bstack11l1ll1lll_opy_(CONFIG, bstack1l11l111ll_opy_) and bstack1l1l11ll11_opy_.bstack1111lllll_opy_(bstack11ll1l111l_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1lll1ll111l_opy_(bstack1ll1l1111ll_opy_):
            bstack1l1l11ll11_opy_.set_capabilities(bstack11ll1l111l_opy_, CONFIG)
    if desired_capabilities:
        bstack11l11llll_opy_ = bstack1ll1ll1lll_opy_(desired_capabilities)
        bstack11l11llll_opy_[bstack11111l_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩ⒊")] = bstack11111ll1_opy_(CONFIG)
        bstack1ll111l11l_opy_ = bstack1ll111l1l1_opy_(bstack11l11llll_opy_)
        if bstack1ll111l11l_opy_:
            bstack11ll1l111l_opy_ = update(bstack1ll111l11l_opy_, bstack11ll1l111l_opy_)
        desired_capabilities = None
    if options:
        bstack1llll1ll1_opy_(options, bstack11ll1l111l_opy_)
    if not options:
        options = bstack11l111111_opy_(bstack11ll1l111l_opy_)
    if proxy and bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"ࠪ࠸࠳࠷࠰࠯࠲ࠪ⒋")):
        options.proxy(proxy)
    if options and bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪ⒌")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack11lll1l1ll_opy_() < version.parse(bstack11111l_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫ⒍")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack11ll1l111l_opy_)
    logger.info(bstack1l1l1111l1_opy_)
    bstack1ll11ll1l1_opy_.end(EVENTS.bstack1ll1ll11l_opy_.value, EVENTS.bstack1ll1ll11l_opy_.value + bstack11111l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨ⒎"),
                               EVENTS.bstack1ll1ll11l_opy_.value + bstack11111l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧ⒏"), True, None)
    try:
        if bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨ⒐")):
            bstack1111ll11l_opy_(self, command_executor=command_executor,
                      options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
        elif bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨ⒑")):
            bstack1111ll11l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities, options=options,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        elif bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"ࠪ࠶࠳࠻࠳࠯࠲ࠪ⒒")):
            bstack1111ll11l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        else:
            bstack1111ll11l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive)
    except Exception as bstack1l1lll1l_opy_:
        logger.error(bstack11ll1l1l1l_opy_.format(bstack11111l_opy_ (u"ࠫࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠪ⒓"), str(bstack1l1lll1l_opy_)))
        raise bstack1l1lll1l_opy_
    try:
        bstack1l1l1l111_opy_ = bstack11111l_opy_ (u"ࠬ࠭⒔")
        if bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"࠭࠴࠯࠲࠱࠴ࡧ࠷ࠧ⒕")):
            bstack1l1l1l111_opy_ = self.caps.get(bstack11111l_opy_ (u"ࠢࡰࡲࡷ࡭ࡲࡧ࡬ࡉࡷࡥ࡙ࡷࡲࠢ⒖"))
        else:
            bstack1l1l1l111_opy_ = self.capabilities.get(bstack11111l_opy_ (u"ࠣࡱࡳࡸ࡮ࡳࡡ࡭ࡊࡸࡦ࡚ࡸ࡬ࠣ⒗"))
        if bstack1l1l1l111_opy_:
            bstack1lll1l11l1_opy_(bstack1l1l1l111_opy_)
            if bstack11lll1l1ll_opy_() <= version.parse(bstack11111l_opy_ (u"ࠩ࠶࠲࠶࠹࠮࠱ࠩ⒘")):
                self.command_executor._url = bstack11111l_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࠦ⒙") + bstack11l11l1l1l_opy_ + bstack11111l_opy_ (u"ࠦ࠿࠾࠰࠰ࡹࡧ࠳࡭ࡻࡢࠣ⒚")
            else:
                self.command_executor._url = bstack11111l_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢ⒛") + bstack1l1l1l111_opy_ + bstack11111l_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢ⒜")
            logger.debug(bstack1l1l1l1l_opy_.format(bstack1l1l1l111_opy_))
        else:
            logger.debug(bstack1l11lll1l_opy_.format(bstack11111l_opy_ (u"ࠢࡐࡲࡷ࡭ࡲࡧ࡬ࠡࡊࡸࡦࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤࠣ⒝")))
    except Exception as e:
        logger.debug(bstack1l11lll1l_opy_.format(e))
    bstack11ll111l11_opy_ = self.session_id
    if bstack11111l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⒞") in bstack1llll11l1l_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack11111l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⒟"), None)
        if item:
            bstack1lll1l11l1ll_opy_ = getattr(item, bstack11111l_opy_ (u"ࠪࡣࡹ࡫ࡳࡵࡡࡦࡥࡸ࡫࡟ࡴࡶࡤࡶࡹ࡫ࡤࠨ⒠"), False)
            if not getattr(item, bstack11111l_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ⒡"), None) and bstack1lll1l11l1ll_opy_:
                setattr(store[bstack11111l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⒢")], bstack11111l_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⒣"), self)
        bstack11l1llll_opy_ = getattr(threading.current_thread(), bstack11111l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡔࡦࡵࡷࡑࡪࡺࡡࠨ⒤"), None)
        if bstack11l1llll_opy_ and bstack11l1llll_opy_.get(bstack11111l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ⒥"), bstack11111l_opy_ (u"ࠩࠪ⒦")) == bstack11111l_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ⒧"):
            bstack11l1ll1l1l_opy_.bstack1l111l1ll_opy_(self)
    bstack1l1lllll_opy_.append(self)
    if bstack11111l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ⒨") in CONFIG and bstack11111l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⒩") in CONFIG[bstack11111l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ⒪")][bstack1l11l111ll_opy_]:
        bstack11ll1ll1l1_opy_ = CONFIG[bstack11111l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ⒫")][bstack1l11l111ll_opy_][bstack11111l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭⒬")]
    logger.debug(bstack1ll11l1l_opy_.format(bstack11ll111l11_opy_))
@measure(event_name=EVENTS.bstack1l1ll1l11l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_, bstack1l1l1ll11l_opy_=bstack11ll1ll1l1_opy_)
def bstack1l11111l11_opy_(self, url):
    global bstack1llll11l_opy_
    global CONFIG
    try:
        bstack1ll11ll11_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack1l1l11111_opy_.format(str(err)))
    try:
        bstack1llll11l_opy_(self, url)
    except Exception as e:
        try:
            bstack11llll1111_opy_ = str(e)
            if any(err_msg in bstack11llll1111_opy_ for err_msg in bstack1l1l11l111_opy_):
                bstack1ll11ll11_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack1l1l11111_opy_.format(str(err)))
        raise e
def bstack11l1l1llll_opy_(item, when):
    global bstack1111l1ll1_opy_
    try:
        bstack1111l1ll1_opy_(item, when)
    except Exception as e:
        pass
def bstack1l11l11ll1_opy_(item, call, rep):
    global bstack1ll1111111_opy_
    global bstack1l1lllll_opy_
    name = bstack11111l_opy_ (u"ࠩࠪ⒭")
    try:
        if rep.when == bstack11111l_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⒮"):
            bstack11ll111l11_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack11111l_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭⒯"))
            try:
                if (str(skipSessionName).lower() != bstack11111l_opy_ (u"ࠬࡺࡲࡶࡧࠪ⒰")):
                    name = str(rep.nodeid)
                    bstack1lllll1ll_opy_ = bstack1l1111ll11_opy_(bstack11111l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ⒱"), name, bstack11111l_opy_ (u"ࠧࠨ⒲"), bstack11111l_opy_ (u"ࠨࠩ⒳"), bstack11111l_opy_ (u"ࠩࠪ⒴"), bstack11111l_opy_ (u"ࠪࠫ⒵"))
                    os.environ[bstack11111l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧⒶ")] = name
                    for driver in bstack1l1lllll_opy_:
                        if bstack11ll111l11_opy_ == driver.session_id:
                            driver.execute_script(bstack1lllll1ll_opy_)
            except Exception as e:
                logger.debug(bstack11111l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠦࡦࡰࡴࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡴࡧࡶࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠬⒷ").format(str(e)))
            try:
                bstack1lll1l111_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack11111l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧⒸ"):
                    status = bstack11111l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧⒹ") if rep.outcome.lower() == bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨⒺ") else bstack11111l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩⒻ")
                    reason = bstack11111l_opy_ (u"ࠪࠫⒼ")
                    if status == bstack11111l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫⒽ"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack11111l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪⒾ") if status == bstack11111l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭Ⓙ") else bstack11111l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭Ⓚ")
                    data = name + bstack11111l_opy_ (u"ࠨࠢࡳࡥࡸࡹࡥࡥࠣࠪⓁ") if status == bstack11111l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩⓂ") else name + bstack11111l_opy_ (u"ࠪࠤ࡫ࡧࡩ࡭ࡧࡧࠥࠥ࠭Ⓝ") + reason
                    bstack111lll1111_opy_ = bstack1l1111ll11_opy_(bstack11111l_opy_ (u"ࠫࡦࡴ࡮ࡰࡶࡤࡸࡪ࠭Ⓞ"), bstack11111l_opy_ (u"ࠬ࠭Ⓟ"), bstack11111l_opy_ (u"࠭ࠧⓆ"), bstack11111l_opy_ (u"ࠧࠨⓇ"), level, data)
                    for driver in bstack1l1lllll_opy_:
                        if bstack11ll111l11_opy_ == driver.session_id:
                            driver.execute_script(bstack111lll1111_opy_)
            except Exception as e:
                logger.debug(bstack11111l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡩ࡯࡯ࡶࡨࡼࡹࠦࡦࡰࡴࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡴࡧࡶࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠬⓈ").format(str(e)))
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡴࡢࡶࡨࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹ࡫ࡳࡵࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࡿࢂ࠭Ⓣ").format(str(e)))
    bstack1ll1111111_opy_(item, call, rep)
notset = Notset()
def bstack1l11l1l1l_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack11l1llll1l_opy_
    if str(name).lower() == bstack11111l_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࠪⓊ"):
        return bstack11111l_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥⓋ")
    else:
        return bstack11l1llll1l_opy_(self, name, default, skip)
def bstack11lll1l11_opy_(self):
    global CONFIG
    global bstack1ll1ll11ll_opy_
    try:
        proxy = bstack1l111l1l_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack11111l_opy_ (u"ࠬ࠴ࡰࡢࡥࠪⓌ")):
                proxies = bstack1l11l11l11_opy_(proxy, bstack1ll1111lll_opy_())
                if len(proxies) > 0:
                    protocol, bstack1111lll1l_opy_ = proxies.popitem()
                    if bstack11111l_opy_ (u"ࠨ࠺࠰࠱ࠥⓍ") in bstack1111lll1l_opy_:
                        return bstack1111lll1l_opy_
                    else:
                        return bstack11111l_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣⓎ") + bstack1111lll1l_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack11111l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡵࡸ࡯ࡹࡻࠣࡹࡷࡲࠠ࠻ࠢࡾࢁࠧⓏ").format(str(e)))
    return bstack1ll1ll11ll_opy_(self)
def bstack1l1l1l1lll_opy_():
    return (bstack11111l_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬⓐ") in CONFIG or bstack11111l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧⓑ") in CONFIG) and bstack1ll11l1111_opy_() and bstack11lll1l1ll_opy_() >= version.parse(
        bstack1ll111111_opy_)
def bstack1l1ll1ll11_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack11ll1ll1l1_opy_
    global bstack1ll11111l1_opy_
    global bstack1llll11l1l_opy_
    CONFIG[bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ⓒ")] = str(bstack1llll11l1l_opy_) + str(__version__)
    bstack1l11l111ll_opy_ = 0
    try:
        if bstack1ll11111l1_opy_ is True:
            bstack1l11l111ll_opy_ = int(os.environ.get(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬⓓ")))
    except:
        bstack1l11l111ll_opy_ = 0
    CONFIG[bstack11111l_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧⓔ")] = True
    bstack11ll1l111l_opy_ = bstack1ll111l1l1_opy_(CONFIG, bstack1l11l111ll_opy_)
    logger.debug(bstack1l11lll11l_opy_.format(str(bstack11ll1l111l_opy_)))
    if CONFIG.get(bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫⓕ")):
        bstack1l11ll1ll1_opy_(bstack11ll1l111l_opy_, bstack1lll1l11_opy_)
    if bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫⓖ") in CONFIG and bstack11111l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧⓗ") in CONFIG[bstack11111l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ⓘ")][bstack1l11l111ll_opy_]:
        bstack11ll1ll1l1_opy_ = CONFIG[bstack11111l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧⓙ")][bstack1l11l111ll_opy_][bstack11111l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪⓚ")]
    import urllib
    import json
    if bstack11111l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪⓛ") in CONFIG and str(CONFIG[bstack11111l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫⓜ")]).lower() != bstack11111l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧⓝ"):
        bstack1l11l1l11l_opy_ = bstack11ll1lll11_opy_()
        bstack111111l1_opy_ = bstack1l11l1l11l_opy_ + urllib.parse.quote(json.dumps(bstack11ll1l111l_opy_))
    else:
        bstack111111l1_opy_ = bstack11111l_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫⓞ") + urllib.parse.quote(json.dumps(bstack11ll1l111l_opy_))
    browser = self.connect(bstack111111l1_opy_)
    return browser
def bstack1l11ll11l1_opy_():
    global bstack1llll1111_opy_
    global bstack1llll11l1l_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack111llll1l1_opy_
        if not bstack1l1ll11lll1_opy_():
            global bstack11111l11_opy_
            if not bstack11111l11_opy_:
                from bstack_utils.helper import bstack1lll11ll_opy_, bstack1l1lll1l11_opy_
                bstack11111l11_opy_ = bstack1lll11ll_opy_()
                bstack1l1lll1l11_opy_(bstack1llll11l1l_opy_)
            BrowserType.connect = bstack111llll1l1_opy_
            return
        BrowserType.launch = bstack1l1ll1ll11_opy_
        bstack1llll1111_opy_ = True
    except Exception as e:
        pass
def bstack1lll1l111l1l_opy_():
    global CONFIG
    global bstack11l1l1l1ll_opy_
    global bstack11l11l1l1l_opy_
    global bstack1lll1l11_opy_
    global bstack1ll11111l1_opy_
    global bstack1111llll1_opy_
    CONFIG = json.loads(os.environ.get(bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࠩⓟ")))
    bstack11l1l1l1ll_opy_ = eval(os.environ.get(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬⓠ")))
    bstack11l11l1l1l_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡍ࡛ࡂࡠࡗࡕࡐࠬⓡ"))
    bstack1lll11l11_opy_(CONFIG, bstack11l1l1l1ll_opy_)
    bstack1111llll1_opy_ = bstack1l1llll1_opy_.configure_logger(CONFIG, bstack1111llll1_opy_)
    if cli.bstack1lll1l1111_opy_():
        bstack11lllll1ll_opy_.invoke(bstack11lll1l1l_opy_.CONNECT, bstack11l1111l11_opy_())
        cli_context.platform_index = int(os.environ.get(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ⓢ"), bstack11111l_opy_ (u"ࠧ࠱ࠩⓣ")))
        cli.bstack1ll11lll11l_opy_(cli_context.platform_index)
        cli.bstack1lll1l1ll1l_opy_(bstack1ll1111lll_opy_(bstack11l11l1l1l_opy_, CONFIG), cli_context.platform_index, bstack11l111111_opy_)
        cli.bstack1ll1l1l11ll_opy_()
        logger.debug(bstack11111l_opy_ (u"ࠣࡅࡏࡍࠥ࡯ࡳࠡࡣࡦࡸ࡮ࡼࡥࠡࡨࡲࡶࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࠢⓤ") + str(cli_context.platform_index) + bstack11111l_opy_ (u"ࠤࠥⓥ"))
        return # skip all existing operations
    global bstack1111ll11l_opy_
    global bstack11ll1l11_opy_
    global bstack1l11lll1_opy_
    global bstack1ll1lll1ll_opy_
    global bstack1l11ll111l_opy_
    global bstack1l1l1ll11_opy_
    global bstack1l1lll11l_opy_
    global bstack1llll11l_opy_
    global bstack1ll1ll11ll_opy_
    global bstack11l1llll1l_opy_
    global bstack1111l1ll1_opy_
    global bstack1ll1111111_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack1111ll11l_opy_ = webdriver.Remote.__init__
        bstack11ll1l11_opy_ = WebDriver.quit
        bstack1l1lll11l_opy_ = WebDriver.close
        bstack1llll11l_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack11111l_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭ⓦ") in CONFIG or bstack11111l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨⓧ") in CONFIG) and bstack1ll11l1111_opy_():
        if bstack11lll1l1ll_opy_() < version.parse(bstack1ll111111_opy_):
            logger.error(bstack1l111l1l11_opy_.format(bstack11lll1l1ll_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack11111l_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭ⓨ")) and callable(getattr(RemoteConnection, bstack11111l_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧⓩ"))):
                    bstack1ll1ll11ll_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack1ll1ll11ll_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack1ll11ll111_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack11l1llll1l_opy_ = Config.getoption
        from _pytest import runner
        bstack1111l1ll1_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warning(bstack11111l_opy_ (u"ࠢࠦࡵ࠽ࠤࠪࡹࠢ⓪"), bstack11llllll1l_opy_, str(e))
    try:
        from pytest_bdd import reporting
        bstack1ll1111111_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩ⓫"))
    bstack1lll1l11_opy_ = CONFIG.get(bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭⓬"), {}).get(bstack11111l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⓭"))
    bstack1ll11111l1_opy_ = True
    bstack1l111lll_opy_(bstack1l1l11l1ll_opy_)
if (bstack111l1llll1l_opy_()):
    bstack1lll1l111l1l_opy_()
@error_handler(class_method=False)
def bstack1lll1l11111l_opy_(hook_name, event, bstack1l111l11111_opy_=None):
    if hook_name not in [bstack11111l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬ⓮"), bstack11111l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ⓯"), bstack11111l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⓰"), bstack11111l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⓱"), bstack11111l_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸ࠭⓲"), bstack11111l_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪ⓳"), bstack11111l_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩ⓴"), bstack11111l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭⓵")]:
        return
    node = store[bstack11111l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⓶")]
    if hook_name in [bstack11111l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⓷"), bstack11111l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⓸")]:
        node = store[bstack11111l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡰࡳࡩࡻ࡬ࡦࡡ࡬ࡸࡪࡳࠧ⓹")]
    elif hook_name in [bstack11111l_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠧ⓺"), bstack11111l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡩ࡬ࡢࡵࡶࠫ⓻")]:
        node = store[bstack11111l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡩ࡬ࡢࡵࡶࡣ࡮ࡺࡥ࡮ࠩ⓼")]
    hook_type = bstack1lllll11llll_opy_(hook_name)
    if event == bstack11111l_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬ⓽"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_[hook_type], bstack1lll1ll1111_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack111l11l11l_opy_ = {
            bstack11111l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⓾"): uuid,
            bstack11111l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⓿"): bstack111l1l11_opy_(),
            bstack11111l_opy_ (u"ࠨࡶࡼࡴࡪ࠭─"): bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ━"),
            bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭│"): hook_type,
            bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ┃"): hook_name
        }
        store[bstack11111l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ┄")].append(uuid)
        bstack1lll1l1l111l_opy_ = node.nodeid
        if hook_type == bstack11111l_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫ┅"):
            if not _111l11ll1l_opy_.get(bstack1lll1l1l111l_opy_, None):
                _111l11ll1l_opy_[bstack1lll1l1l111l_opy_] = {bstack11111l_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭┆"): []}
            _111l11ll1l_opy_[bstack1lll1l1l111l_opy_][bstack11111l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ┇")].append(bstack111l11l11l_opy_[bstack11111l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ┈")])
        _111l11ll1l_opy_[bstack1lll1l1l111l_opy_ + bstack11111l_opy_ (u"ࠪ࠱ࠬ┉") + hook_name] = bstack111l11l11l_opy_
        bstack1lll1l111ll1_opy_(node, bstack111l11l11l_opy_, bstack11111l_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ┊"))
    elif event == bstack11111l_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫ┋"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1l11ll1l_opy_[hook_type], bstack1lll1ll1111_opy_.POST, node, None, bstack1l111l11111_opy_)
            return
        bstack111ll111l1_opy_ = node.nodeid + bstack11111l_opy_ (u"࠭࠭ࠨ┌") + hook_name
        _111l11ll1l_opy_[bstack111ll111l1_opy_][bstack11111l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ┍")] = bstack111l1l11_opy_()
        bstack1lll1l11l111_opy_(_111l11ll1l_opy_[bstack111ll111l1_opy_][bstack11111l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭┎")])
        bstack1lll1l111ll1_opy_(node, _111l11ll1l_opy_[bstack111ll111l1_opy_], bstack11111l_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ┏"), bstack1lll1l1ll11l_opy_=bstack1l111l11111_opy_)
def bstack1lll1l11lll1_opy_():
    global bstack1lll1l1ll111_opy_
    if bstack1l1ll1111l_opy_():
        bstack1lll1l1ll111_opy_ = bstack11111l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠧ┐")
    else:
        bstack1lll1l1ll111_opy_ = bstack11111l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ┑")
@bstack11l1ll1l1l_opy_.bstack1lll1llll11l_opy_
def bstack1lll1l111lll_opy_():
    bstack1lll1l11lll1_opy_()
    if cli.is_running():
        try:
            bstack111l1l1ll11_opy_(bstack1lll1l11111l_opy_)
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࡵࠣࡴࡦࡺࡣࡩ࠼ࠣࡿࢂࠨ┒").format(e))
        return
    if bstack1ll11l1111_opy_():
        bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
        bstack11111l_opy_ (u"࠭ࠧࠨࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡇࡱࡵࠤࡵࡶࡰࠡ࠿ࠣ࠵࠱ࠦ࡭ࡰࡦࡢࡩࡽ࡫ࡣࡶࡶࡨࠤ࡬࡫ࡴࡴࠢࡸࡷࡪࡪࠠࡧࡱࡵࠤࡦ࠷࠱ࡺࠢࡦࡳࡲࡳࡡ࡯ࡦࡶ࠱ࡼࡸࡡࡱࡲ࡬ࡲ࡬ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡋࡵࡲࠡࡲࡳࡴࠥࡄࠠ࠲࠮ࠣࡱࡴࡪ࡟ࡦࡺࡨࡧࡺࡺࡥࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡶࡺࡴࠠࡣࡧࡦࡥࡺࡹࡥࠡ࡫ࡷࠤ࡮ࡹࠠࡱࡣࡷࡧ࡭࡫ࡤࠡ࡫ࡱࠤࡦࠦࡤࡪࡨࡩࡩࡷ࡫࡮ࡵࠢࡳࡶࡴࡩࡥࡴࡵࠣ࡭ࡩࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡙࡮ࡵࡴࠢࡺࡩࠥࡴࡥࡦࡦࠣࡸࡴࠦࡵࡴࡧࠣࡗࡪࡲࡥ࡯࡫ࡸࡱࡕࡧࡴࡤࡪࠫࡷࡪࡲࡥ࡯࡫ࡸࡱࡤ࡮ࡡ࡯ࡦ࡯ࡩࡷ࠯ࠠࡧࡱࡵࠤࡵࡶࡰࠡࡀࠣ࠵ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠧࠨࠩ┓")
        if bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ└")):
            if CONFIG.get(bstack11111l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ┕")) is not None and int(CONFIG[bstack11111l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ┖")]) > 1:
                bstack11l1l11l11_opy_(bstack1lll1l1ll1_opy_)
            return
        bstack11l1l11l11_opy_(bstack1lll1l1ll1_opy_)
    try:
        bstack111l1l1ll11_opy_(bstack1lll1l11111l_opy_)
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢ࡫ࡳࡴࡱࡳࠡࡲࡤࡸࡨ࡮࠺ࠡࡽࢀࠦ┗").format(e))
bstack1lll1l111lll_opy_()