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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack1ll111ll11_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack1l111lll1_opy_, bstack1l1llll11l_opy_, update, bstack1l11l11l11_opy_,
                                       bstack1llll1lll_opy_, bstack1lll1l11_opy_, bstack1l11111ll1_opy_, bstack1l1l11l1_opy_,
                                       bstack11l1l1ll_opy_, bstack1l1111ll_opy_, bstack111lll11l_opy_,
                                       bstack111llll1l1_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack11ll1l11l1_opy_)
from browserstack_sdk.bstack111l11ll1_opy_ import bstack1l11111l1_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack1lllllll1l_opy_
from bstack_utils.capture import bstack111ll11111_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack1lllll111l_opy_, bstack1llll11l_opy_, bstack1l1ll1lll1_opy_, \
    bstack1l11l1ll_opy_
from bstack_utils.helper import bstack11llll11ll_opy_, bstack11l11l11111_opy_, bstack1111llll11_opy_, bstack111ll1111_opy_, bstack1l1l111l1l1_opy_, bstack1111lllll_opy_, \
    bstack111ll11llll_opy_, \
    bstack11l111l1l11_opy_, bstack1llllll1l1_opy_, bstack111lll11ll_opy_, bstack111ll1lll11_opy_, bstack11ll111l11_opy_, Notset, \
    bstack1llll11l1_opy_, bstack111llllll11_opy_, bstack11l1111ll1l_opy_, Result, bstack111lll11lll_opy_, bstack11l111l1l1l_opy_, error_handler, \
    bstack1ll1ll111_opy_, bstack11ll11lll_opy_, bstack1l1l1111l1_opy_, bstack111llllllll_opy_
from bstack_utils.bstack111l1l111l1_opy_ import bstack111l1l1l1l1_opy_
from bstack_utils.messages import bstack1l1l1ll1l_opy_, bstack11l1ll1lll_opy_, bstack11l1111ll1_opy_, bstack1ll1lll11l_opy_, bstack1l1lll1ll_opy_, \
    bstack11l11111l_opy_, bstack11lll1lll_opy_, bstack1l11ll1ll1_opy_, bstack1l111lllll_opy_, bstack1lll1l111_opy_, \
    bstack11l1111l_opy_, bstack11111111l_opy_, bstack1l11l11ll_opy_
from bstack_utils.proxy import bstack1l11ll1ll_opy_, bstack11l1111ll_opy_
from bstack_utils.bstack111111l11_opy_ import bstack1lllll1l11ll_opy_, bstack1lllll11l1ll_opy_, bstack1lllll11l111_opy_, bstack1lllll11l1l1_opy_, \
    bstack1lllll11l11l_opy_, bstack1lllll1l11l1_opy_, bstack1lllll111ll1_opy_, bstack1l1l111l1_opy_, bstack1lllll1l111l_opy_
from bstack_utils.bstack11ll1lll1_opy_ import bstack1lllll11_opy_
from bstack_utils.bstack1l1l1ll1_opy_ import bstack11l11lll1l_opy_, bstack11l11111_opy_, bstack1llll111ll_opy_, \
    bstack11ll11111_opy_, bstack1l11l111l1_opy_
from bstack_utils.bstack111l1lll1l_opy_ import bstack111l1ll1l1_opy_
from bstack_utils.bstack111ll11l11_opy_ import bstack1l1ll11111_opy_
import bstack_utils.accessibility as bstack1lllllll11_opy_
from bstack_utils.bstack111ll11l1l_opy_ import bstack11l1llllll_opy_
from bstack_utils.bstack111111lll_opy_ import bstack111111lll_opy_
from bstack_utils.bstack1l11l1l1ll_opy_ import bstack111l1111l_opy_
from browserstack_sdk.__init__ import bstack11l1lll11l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1ll1l111l1l_opy_
from browserstack_sdk.sdk_cli.bstack111l111l_opy_ import bstack111l111l_opy_, bstack11l111111_opy_, bstack11lll1l1l1_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack11lll1l1l1l_opy_, bstack1ll1llll111_opy_, bstack1ll1ll111l1_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack111l111l_opy_ import bstack111l111l_opy_, bstack11l111111_opy_, bstack11lll1l1l1_opy_
bstack111ll1l1l_opy_ = None
bstack11l1lll111_opy_ = None
bstack1l1llll11_opy_ = None
bstack1l1l1l1l11_opy_ = None
bstack11lll11l1l_opy_ = None
bstack1l11lll1ll_opy_ = None
bstack1ll1l1ll1l_opy_ = None
bstack111llll111_opy_ = None
bstack11l1lllll1_opy_ = None
bstack1l1ll11ll1_opy_ = None
bstack1l111l111_opy_ = None
bstack1ll11l11l1_opy_ = None
bstack111lll1ll_opy_ = None
bstack1lll1l11l1_opy_ = bstack1l1l_opy_ (u"ࠩࠪ⊼")
CONFIG = {}
bstack11l11l11l1_opy_ = False
bstack11ll1lll1l_opy_ = bstack1l1l_opy_ (u"ࠪࠫ⊽")
bstack1lllll1ll1_opy_ = bstack1l1l_opy_ (u"ࠫࠬ⊾")
bstack1l1ll11lll_opy_ = False
bstack1l11l11l_opy_ = []
bstack1ll1l11l1l_opy_ = bstack1lllll111l_opy_
bstack1lll1l11l111_opy_ = bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ⊿")
bstack11l11l1ll_opy_ = {}
bstack11ll11ll_opy_ = None
bstack1l1l1ll111_opy_ = False
logger = bstack1lllllll1l_opy_.get_logger(__name__, bstack1ll1l11l1l_opy_)
store = {
    bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⋀"): []
}
bstack1lll1l11llll_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_111l1111ll_opy_ = {}
current_test_uuid = None
cli_context = bstack11lll1l1l1l_opy_(
    test_framework_name=bstack11ll111l_opy_[bstack1l1l_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࠭ࡃࡆࡇࠫ⋁")] if bstack11ll111l11_opy_() else bstack11ll111l_opy_[bstack1l1l_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࠨ⋂")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack11l11l1ll1_opy_(page, bstack1l11l1llll_opy_):
    try:
        page.evaluate(bstack1l1l_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ⋃"),
                      bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠧ⋄") + json.dumps(
                          bstack1l11l1llll_opy_) + bstack1l1l_opy_ (u"ࠦࢂࢃࠢ⋅"))
    except Exception as e:
        print(bstack1l1l_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠠࡼࡿࠥ⋆"), e)
def bstack1ll11111ll_opy_(page, message, level):
    try:
        page.evaluate(bstack1l1l_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢ⋇"), bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬ⋈") + json.dumps(
            message) + bstack1l1l_opy_ (u"ࠨ࠮ࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠫ⋉") + json.dumps(level) + bstack1l1l_opy_ (u"ࠩࢀࢁࠬ⋊"))
    except Exception as e:
        print(bstack1l1l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡡ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠣࡿࢂࠨ⋋"), e)
def pytest_configure(config):
    global bstack11ll1lll1l_opy_
    global CONFIG
    bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
    config.args = bstack1l1ll11111_opy_.bstack1lll1l1ll1ll_opy_(config.args)
    bstack1l1ll1l1_opy_.bstack1ll11ll11l_opy_(bstack1l1l1111l1_opy_(config.getoption(bstack1l1l_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ⋌"))))
    try:
        bstack1lllllll1l_opy_.bstack111l11l111l_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack111l111l_opy_.invoke(bstack11l111111_opy_.CONNECT, bstack11lll1l1l1_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬ⋍"), bstack1l1l_opy_ (u"࠭࠰ࠨ⋎")))
        config = json.loads(os.environ.get(bstack1l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࠨ⋏"), bstack1l1l_opy_ (u"ࠣࡽࢀࠦ⋐")))
        cli.bstack1lll11111l1_opy_(bstack111lll11ll_opy_(bstack11ll1lll1l_opy_, CONFIG), cli_context.platform_index, bstack1l11l11l11_opy_)
    if cli.bstack1lll1l1ll11_opy_(bstack1ll1l111l1l_opy_):
        cli.bstack1lll1l1l1ll_opy_()
        logger.debug(bstack1l1l_opy_ (u"ࠤࡆࡐࡎࠦࡩࡴࠢࡤࡧࡹ࡯ࡶࡦࠢࡩࡳࡷࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾ࠽ࠣ⋑") + str(cli_context.platform_index) + bstack1l1l_opy_ (u"ࠥࠦ⋒"))
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.BEFORE_ALL, bstack1ll1ll111l1_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack1l1l_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤ⋓"), None)
    if cli.is_running() and when == bstack1l1l_opy_ (u"ࠧࡩࡡ࡭࡮ࠥ⋔"):
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.LOG_REPORT, bstack1ll1ll111l1_opy_.PRE, item, call)
    outcome = yield
    if when == bstack1l1l_opy_ (u"ࠨࡣࡢ࡮࡯ࠦ⋕"):
        report = outcome.get_result()
        passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1l_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤ⋖")))
        if not passed:
            config = json.loads(os.environ.get(bstack1l1l_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠢ⋗"), bstack1l1l_opy_ (u"ࠤࡾࢁࠧ⋘")))
            if bstack111l1111l_opy_.bstack111l11l1_opy_(config):
                bstack11111ll111l_opy_ = bstack111l1111l_opy_.bstack1ll111l1l1_opy_(config)
                if item.execution_count > bstack11111ll111l_opy_:
                    print(bstack1l1l_opy_ (u"ࠪࡘࡪࡹࡴࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡣࡩࡸࡪࡸࠠࡳࡧࡷࡶ࡮࡫ࡳ࠻ࠢࠪ⋙"), report.nodeid, os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ⋚")))
                    bstack111l1111l_opy_.bstack1111l11lll1_opy_(report.nodeid)
            else:
                print(bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࠬ⋛"), report.nodeid, os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ⋜")))
                bstack111l1111l_opy_.bstack1111l11lll1_opy_(report.nodeid)
        else:
            print(bstack1l1l_opy_ (u"ࠧࡕࡧࡶࡸࠥࡶࡡࡴࡵࡨࡨ࠿ࠦࠧ⋝"), report.nodeid, os.environ.get(bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭⋞")))
    if cli.is_running():
        if when == bstack1l1l_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣ⋟"):
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.BEFORE_EACH, bstack1ll1ll111l1_opy_.POST, item, call, outcome)
        elif when == bstack1l1l_opy_ (u"ࠥࡧࡦࡲ࡬ࠣ⋠"):
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.LOG_REPORT, bstack1ll1ll111l1_opy_.POST, item, call, outcome)
        elif when == bstack1l1l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨ⋡"):
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.AFTER_EACH, bstack1ll1ll111l1_opy_.POST, item, call, outcome)
        return # skip all existing operations
    skipSessionName = item.config.getoption(bstack1l1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ⋢"))
    plugins = item.config.getoption(bstack1l1l_opy_ (u"ࠨࡰ࡭ࡷࡪ࡭ࡳࡹࠢ⋣"))
    report = outcome.get_result()
    os.environ[bstack1l1l_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪ⋤")] = report.nodeid
    bstack1lll1l11l11l_opy_(item, call, report)
    if bstack1l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡰ࡭ࡷࡪ࡭ࡳࠨ⋥") not in plugins or bstack11ll111l11_opy_():
        return
    summary = []
    driver = getattr(item, bstack1l1l_opy_ (u"ࠤࡢࡨࡷ࡯ࡶࡦࡴࠥ⋦"), None)
    page = getattr(item, bstack1l1l_opy_ (u"ࠥࡣࡵࡧࡧࡦࠤ⋧"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack1lll11lllll1_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack1lll1l1l1111_opy_(item, report, summary, skipSessionName)
def bstack1lll11lllll1_opy_(item, report, summary, skipSessionName):
    if report.when == bstack1l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ⋨") and report.skipped:
        bstack1lllll1l111l_opy_(report)
    if report.when in [bstack1l1l_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦ⋩"), bstack1l1l_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࠣ⋪")]:
        return
    if not bstack1l1l111l1l1_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack1l1l_opy_ (u"ࠧࡵࡴࡸࡩࠬ⋫")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭⋬") + json.dumps(
                    report.nodeid) + bstack1l1l_opy_ (u"ࠩࢀࢁࠬ⋭"))
        os.environ[bstack1l1l_opy_ (u"ࠪࡔ࡞࡚ࡅࡔࡖࡢࡘࡊ࡙ࡔࡠࡐࡄࡑࡊ࠭⋮")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack1l1l_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࡀࠠࡼ࠲ࢀࠦ⋯").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1l_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ⋰")))
    bstack11l11l1l11_opy_ = bstack1l1l_opy_ (u"ࠨࠢ⋱")
    bstack1lllll1l111l_opy_(report)
    if not passed:
        try:
            bstack11l11l1l11_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1l_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡵࡩࡦࡹ࡯࡯࠼ࠣࡿ࠵ࢃࠢ⋲").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack11l11l1l11_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack1l1l_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ⋳")))
        bstack11l11l1l11_opy_ = bstack1l1l_opy_ (u"ࠤࠥ⋴")
        if not passed:
            try:
                bstack11l11l1l11_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1l1l_opy_ (u"࡛ࠥࡆࡘࡎࡊࡐࡊ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤ࡫ࡧࡩ࡭ࡷࡵࡩࠥࡸࡥࡢࡵࡲࡲ࠿ࠦࡻ࠱ࡿࠥ⋵").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack11l11l1l11_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡥࡣࡷࡥࠧࡀࠠࠨ⋶")
                    + json.dumps(bstack1l1l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠦࠨ⋷"))
                    + bstack1l1l_opy_ (u"ࠨ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࠤ⋸")
                )
            else:
                item._driver.execute_script(
                    bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡩࡧࡴࡢࠤ࠽ࠤࠬ⋹")
                    + json.dumps(str(bstack11l11l1l11_opy_))
                    + bstack1l1l_opy_ (u"ࠣ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࠦ⋺")
                )
        except Exception as e:
            summary.append(bstack1l1l_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡢࡰࡱࡳࡹࡧࡴࡦ࠼ࠣࡿ࠵ࢃࠢ⋻").format(e))
def bstack1lll1l1l11l1_opy_(test_name, error_message):
    try:
        bstack1lll1l1l111l_opy_ = []
        bstack1111lll1l_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ⋼"), bstack1l1l_opy_ (u"ࠫ࠵࠭⋽"))
        bstack1llll1111l_opy_ = {bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⋾"): test_name, bstack1l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ⋿"): error_message, bstack1l1l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭⌀"): bstack1111lll1l_opy_}
        bstack1lll1l11ll1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠨࡲࡺࡣࡵࡿࡴࡦࡵࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭⌁"))
        if os.path.exists(bstack1lll1l11ll1l_opy_):
            with open(bstack1lll1l11ll1l_opy_) as f:
                bstack1lll1l1l111l_opy_ = json.load(f)
        bstack1lll1l1l111l_opy_.append(bstack1llll1111l_opy_)
        with open(bstack1lll1l11ll1l_opy_, bstack1l1l_opy_ (u"ࠩࡺࠫ⌂")) as f:
            json.dump(bstack1lll1l1l111l_opy_, f)
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡥࡳࡵ࡬ࡷࡹ࡯࡮ࡨࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡰࡺࡶࡨࡷࡹࠦࡥࡳࡴࡲࡶࡸࡀࠠࠨ⌃") + str(e))
def bstack1lll1l1l1111_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack1l1l_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࠥ⌄"), bstack1l1l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢ⌅")]:
        return
    if (str(skipSessionName).lower() != bstack1l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫ⌆")):
        bstack11l11l1ll1_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1l_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤ⌇")))
    bstack11l11l1l11_opy_ = bstack1l1l_opy_ (u"ࠣࠤ⌈")
    bstack1lllll1l111l_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack11l11l1l11_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1l1l_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡷ࡫ࡡࡴࡱࡱ࠾ࠥࢁ࠰ࡾࠤ⌉").format(e)
                )
        try:
            if passed:
                bstack1l11l111l1_opy_(getattr(item, bstack1l1l_opy_ (u"ࠪࡣࡵࡧࡧࡦࠩ⌊"), None), bstack1l1l_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ⌋"))
            else:
                error_message = bstack1l1l_opy_ (u"ࠬ࠭⌌")
                if bstack11l11l1l11_opy_:
                    bstack1ll11111ll_opy_(item._page, str(bstack11l11l1l11_opy_), bstack1l1l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ⌍"))
                    bstack1l11l111l1_opy_(getattr(item, bstack1l1l_opy_ (u"ࠧࡠࡲࡤ࡫ࡪ࠭⌎"), None), bstack1l1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ⌏"), str(bstack11l11l1l11_opy_))
                    error_message = str(bstack11l11l1l11_opy_)
                else:
                    bstack1l11l111l1_opy_(getattr(item, bstack1l1l_opy_ (u"ࠩࡢࡴࡦ࡭ࡥࠨ⌐"), None), bstack1l1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ⌑"))
                bstack1lll1l1l11l1_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack1l1l_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡸࡴࡩࡧࡴࡦࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀ࠶ࡽࠣ⌒").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack1l1l_opy_ (u"ࠧ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ⌓"), default=bstack1l1l_opy_ (u"ࠨࡆࡢ࡮ࡶࡩࠧ⌔"), help=bstack1l1l_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡪࡥࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠨ⌕"))
    parser.addoption(bstack1l1l_opy_ (u"ࠣ࠯࠰ࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ⌖"), default=bstack1l1l_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣ⌗"), help=bstack1l1l_opy_ (u"ࠥࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡨࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠤ⌘"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1l1l_opy_ (u"ࠦ࠲࠳ࡤࡳ࡫ࡹࡩࡷࠨ⌙"), action=bstack1l1l_opy_ (u"ࠧࡹࡴࡰࡴࡨࠦ⌚"), default=bstack1l1l_opy_ (u"ࠨࡣࡩࡴࡲࡱࡪࠨ⌛"),
                         help=bstack1l1l_opy_ (u"ࠢࡅࡴ࡬ࡺࡪࡸࠠࡵࡱࠣࡶࡺࡴࠠࡵࡧࡶࡸࡸࠨ⌜"))
def bstack111l1llll1_opy_(log):
    if not (log[bstack1l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⌝")] and log[bstack1l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ⌞")].strip()):
        return
    active = bstack111ll111l1_opy_()
    log = {
        bstack1l1l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ⌟"): log[bstack1l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ⌠")],
        bstack1l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ⌡"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"࡚࠭ࠨ⌢"),
        bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⌣"): log[bstack1l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⌤")],
    }
    if active:
        if active[bstack1l1l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⌥")] == bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⌦"):
            log[bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⌧")] = active[bstack1l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⌨")]
        elif active[bstack1l1l_opy_ (u"࠭ࡴࡺࡲࡨࠫ〈")] == bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࠬ〉"):
            log[bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⌫")] = active[bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⌬")]
    bstack11l1llllll_opy_.bstack1llll11lll_opy_([log])
def bstack111ll111l1_opy_():
    if len(store[bstack1l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⌭")]) > 0 and store[bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⌮")][-1]:
        return {
            bstack1l1l_opy_ (u"ࠬࡺࡹࡱࡧࠪ⌯"): bstack1l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ⌰"),
            bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⌱"): store[bstack1l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⌲")][-1]
        }
    if store.get(bstack1l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭⌳"), None):
        return {
            bstack1l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨ⌴"): bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⌵"),
            bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⌶"): store[bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ⌷")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.INIT_TEST, bstack1ll1ll111l1_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.INIT_TEST, bstack1ll1ll111l1_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._1lll1l111lll_opy_ = True
        bstack1l1llll111_opy_ = bstack1lllllll11_opy_.bstack1l111lll_opy_(bstack11l111l1l11_opy_(item.own_markers))
        if not cli.bstack1lll1l1ll11_opy_(bstack1ll1l111l1l_opy_):
            item._a11y_test_case = bstack1l1llll111_opy_
            if bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭⌸"), None):
                driver = getattr(item, bstack1l1l_opy_ (u"ࠨࡡࡧࡶ࡮ࡼࡥࡳࠩ⌹"), None)
                item._a11y_started = bstack1lllllll11_opy_.bstack1l1111111l_opy_(driver, bstack1l1llll111_opy_)
        if not bstack11l1llllll_opy_.on() or bstack1lll1l11l111_opy_ != bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ⌺"):
            return
        global current_test_uuid #, bstack111ll1ll11_opy_
        bstack111l1l11ll_opy_ = {
            bstack1l1l_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⌻"): uuid4().__str__(),
            bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⌼"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠬࡠࠧ⌽")
        }
        current_test_uuid = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⌾")]
        store[bstack1l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⌿")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⍀")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _111l1111ll_opy_[item.nodeid] = {**_111l1111ll_opy_[item.nodeid], **bstack111l1l11ll_opy_}
        bstack1lll1l1111l1_opy_(item, _111l1111ll_opy_[item.nodeid], bstack1l1l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ⍁"))
    except Exception as err:
        print(bstack1l1l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡵࡹࡳࡺࡥࡴࡶࡢࡧࡦࡲ࡬࠻ࠢࡾࢁࠬ⍂"), str(err))
def pytest_runtest_setup(item):
    store[bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡹ࡫࡭ࠨ⍃")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.BEFORE_EACH, bstack1ll1ll111l1_opy_.PRE, item, bstack1l1l_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⍄"))
    if bstack111l1111l_opy_.bstack11111llll11_opy_():
            bstack1lll1l11111l_opy_ = bstack1l1l_opy_ (u"ࠨࡓ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡡࡴࠢࡷ࡬ࡪࠦࡡࡣࡱࡵࡸࠥࡨࡵࡪ࡮ࡧࠤ࡫࡯࡬ࡦࠢࡨࡼ࡮ࡹࡴࡴ࠰ࠥ⍅")
            logger.error(bstack1lll1l11111l_opy_)
            bstack111l1l11ll_opy_ = {
                bstack1l1l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⍆"): uuid4().__str__(),
                bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⍇"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠩ࡝ࠫ⍈"),
                bstack1l1l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⍉"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠫ࡟࠭⍊"),
                bstack1l1l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⍋"): bstack1l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ⍌"),
                bstack1l1l_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ⍍"): bstack1lll1l11111l_opy_,
                bstack1l1l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⍎"): [],
                bstack1l1l_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⍏"): []
            }
            bstack1lll1l1111l1_opy_(item, bstack111l1l11ll_opy_, bstack1l1l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ⍐"))
            pytest.skip(bstack1lll1l11111l_opy_)
            return # skip all existing operations
    global bstack1lll1l11llll_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack111ll1lll11_opy_():
        atexit.register(bstack111ll11ll_opy_)
        if not bstack1lll1l11llll_opy_:
            try:
                bstack1lll1l111l11_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack111llllllll_opy_():
                    bstack1lll1l111l11_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1lll1l111l11_opy_:
                    signal.signal(s, bstack1lll1l11lll1_opy_)
                bstack1lll1l11llll_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡲࡦࡩ࡬ࡷࡹ࡫ࡲࠡࡵ࡬࡫ࡳࡧ࡬ࠡࡪࡤࡲࡩࡲࡥࡳࡵ࠽ࠤࠧ⍑") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1lllll1l11ll_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack1l1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ⍒")
    try:
        if not bstack11l1llllll_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack111l1l11ll_opy_ = {
            bstack1l1l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍓"): uuid,
            bstack1l1l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⍔"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠨ࡜ࠪ⍕"),
            bstack1l1l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⍖"): bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⍗"),
            bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ⍘"): bstack1l1l_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠪ⍙"),
            bstack1l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡳࡧ࡭ࡦࠩ⍚"): bstack1l1l_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭⍛")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack1l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⍜")] = item
        store[bstack1l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⍝")] = [uuid]
        if not _111l1111ll_opy_.get(item.nodeid, None):
            _111l1111ll_opy_[item.nodeid] = {bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⍞"): [], bstack1l1l_opy_ (u"ࠫ࡫࡯ࡸࡵࡷࡵࡩࡸ࠭⍟"): []}
        _111l1111ll_opy_[item.nodeid][bstack1l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⍠")].append(bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍡")])
        _111l1111ll_opy_[item.nodeid + bstack1l1l_opy_ (u"ࠧ࠮ࡵࡨࡸࡺࡶࠧ⍢")] = bstack111l1l11ll_opy_
        bstack1lll1l111ll1_opy_(item, bstack111l1l11ll_opy_, bstack1l1l_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⍣"))
    except Exception as err:
        print(bstack1l1l_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡶࡩࡹࡻࡰ࠻ࠢࡾࢁࠬ⍤"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.AFTER_EACH, bstack1ll1ll111l1_opy_.PRE, item, bstack1l1l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ⍥"))
        return # skip all existing operations
    try:
        global bstack11l11l1ll_opy_
        bstack1111lll1l_opy_ = 0
        if bstack1l1ll11lll_opy_ is True:
            bstack1111lll1l_opy_ = int(os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ⍦")))
        if bstack111111l1_opy_.bstack1l1l11111l_opy_() == bstack1l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥ⍧"):
            if bstack111111l1_opy_.bstack1lll11lll1_opy_() == bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ⍨"):
                bstack1lll11llllll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⍩"), None)
                bstack1ll1l1l11l_opy_ = bstack1lll11llllll_opy_ + bstack1l1l_opy_ (u"ࠣ࠯ࡷࡩࡸࡺࡣࡢࡵࡨࠦ⍪")
                driver = getattr(item, bstack1l1l_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ⍫"), None)
                bstack1l1l11l111_opy_ = getattr(item, bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ⍬"), None)
                bstack11l1111lll_opy_ = getattr(item, bstack1l1l_opy_ (u"ࠫࡺࡻࡩࡥࠩ⍭"), None)
                PercySDK.screenshot(driver, bstack1ll1l1l11l_opy_, bstack1l1l11l111_opy_=bstack1l1l11l111_opy_, bstack11l1111lll_opy_=bstack11l1111lll_opy_, bstack1ll11l1111_opy_=bstack1111lll1l_opy_)
        if not cli.bstack1lll1l1ll11_opy_(bstack1ll1l111l1l_opy_):
            if getattr(item, bstack1l1l_opy_ (u"ࠬࡥࡡ࠲࠳ࡼࡣࡸࡺࡡࡳࡶࡨࡨࠬ⍮"), False):
                bstack1l11111l1_opy_.bstack1ll1lllll1_opy_(getattr(item, bstack1l1l_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⍯"), None), bstack11l11l1ll_opy_, logger, item)
        if not bstack11l1llllll_opy_.on():
            return
        bstack111l1l11ll_opy_ = {
            bstack1l1l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⍰"): uuid4().__str__(),
            bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⍱"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠩ࡝ࠫ⍲"),
            bstack1l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨ⍳"): bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⍴"),
            bstack1l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡸࡾࡶࡥࠨ⍵"): bstack1l1l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠪ⍶"),
            bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠪ⍷"): bstack1l1l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⍸")
        }
        _111l1111ll_opy_[item.nodeid + bstack1l1l_opy_ (u"ࠩ࠰ࡸࡪࡧࡲࡥࡱࡺࡲࠬ⍹")] = bstack111l1l11ll_opy_
        bstack1lll1l111ll1_opy_(item, bstack111l1l11ll_opy_, bstack1l1l_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⍺"))
    except Exception as err:
        print(bstack1l1l_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡶࡺࡴࡴࡦࡵࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡀࠠࡼࡿࠪ⍻"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack1lllll11l1l1_opy_(fixturedef.argname):
        store[bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥ࡭ࡰࡦࡸࡰࡪࡥࡩࡵࡧࡰࠫ⍼")] = request.node
    elif bstack1lllll11l11l_opy_(fixturedef.argname):
        store[bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡤ࡮ࡤࡷࡸࡥࡩࡵࡧࡰࠫ⍽")] = request.node
    if not bstack11l1llllll_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.SETUP_FIXTURE, bstack1ll1ll111l1_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.SETUP_FIXTURE, bstack1ll1ll111l1_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.SETUP_FIXTURE, bstack1ll1ll111l1_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.SETUP_FIXTURE, bstack1ll1ll111l1_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    try:
        fixture = {
            bstack1l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⍾"): fixturedef.argname,
            bstack1l1l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⍿"): bstack111ll11llll_opy_(outcome),
            bstack1l1l_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫ⎀"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack1l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧ⎁")]
        if not _111l1111ll_opy_.get(current_test_item.nodeid, None):
            _111l1111ll_opy_[current_test_item.nodeid] = {bstack1l1l_opy_ (u"ࠫ࡫࡯ࡸࡵࡷࡵࡩࡸ࠭⎂"): []}
        _111l1111ll_opy_[current_test_item.nodeid][bstack1l1l_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ⎃")].append(fixture)
    except Exception as err:
        logger.debug(bstack1l1l_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡳࡦࡶࡸࡴ࠿ࠦࡻࡾࠩ⎄"), str(err))
if bstack11ll111l11_opy_() and bstack11l1llllll_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.STEP, bstack1ll1ll111l1_opy_.PRE, request, step)
            return
        try:
            _111l1111ll_opy_[request.node.nodeid][bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⎅")].bstack1l11ll11l_opy_(id(step))
        except Exception as err:
            print(bstack1l1l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱ࠼ࠣࡿࢂ࠭⎆"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.STEP, bstack1ll1ll111l1_opy_.POST, request, step, exception)
            return
        try:
            _111l1111ll_opy_[request.node.nodeid][bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⎇")].bstack111ll1111l_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack1l1l_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡳࡵࡧࡳࡣࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠧ⎈"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.STEP, bstack1ll1ll111l1_opy_.POST, request, step)
            return
        try:
            bstack111l1lll1l_opy_: bstack111l1ll1l1_opy_ = _111l1111ll_opy_[request.node.nodeid][bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ⎉")]
            bstack111l1lll1l_opy_.bstack111ll1111l_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack1l1l_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡵࡷࡩࡵࡥࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠩ⎊"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1lll1l11l111_opy_
        try:
            if not bstack11l1llllll_opy_.on() or bstack1lll1l11l111_opy_ != bstack1l1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠪ⎋"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.TEST, bstack1ll1ll111l1_opy_.PRE, request, feature, scenario)
                return
            driver = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭⎌"), None)
            if not _111l1111ll_opy_.get(request.node.nodeid, None):
                _111l1111ll_opy_[request.node.nodeid] = {}
            bstack111l1lll1l_opy_ = bstack111l1ll1l1_opy_.bstack1llll1l111ll_opy_(
                scenario, feature, request.node,
                name=bstack1lllll1l11l1_opy_(request.node, scenario),
                started_at=bstack1111lllll_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack1l1l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪ⎍"),
                tags=bstack1lllll111ll1_opy_(feature, scenario),
                bstack111ll1l1l1_opy_=bstack11l1llllll_opy_.bstack111l1l1l11_opy_(driver) if driver and driver.session_id else {}
            )
            _111l1111ll_opy_[request.node.nodeid][bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⎎")] = bstack111l1lll1l_opy_
            bstack1lll1l1l1l1l_opy_(bstack111l1lll1l_opy_.uuid)
            bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⎏"), bstack111l1lll1l_opy_)
        except Exception as err:
            print(bstack1l1l_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰ࠼ࠣࡿࢂ࠭⎐"), str(err))
def bstack1lll1l1ll11l_opy_(bstack111l1l1l1l_opy_):
    if bstack111l1l1l1l_opy_ in store[bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ⎑")]:
        store[bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⎒")].remove(bstack111l1l1l1l_opy_)
def bstack1lll1l1l1l1l_opy_(test_uuid):
    store[bstack1l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⎓")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack11l1llllll_opy_.bstack1lll1lll11l1_opy_
def bstack1lll1l11l11l_opy_(item, call, report):
    logger.debug(bstack1l1l_opy_ (u"ࠨࡪࡤࡲࡩࡲࡥࡠࡱ࠴࠵ࡾࡥࡴࡦࡵࡷࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡸࡺࡡࡳࡶࠪ⎔"))
    global bstack1lll1l11l111_opy_
    bstack11lllllll1_opy_ = bstack1111lllll_opy_()
    if hasattr(report, bstack1l1l_opy_ (u"ࠩࡶࡸࡴࡶࠧ⎕")):
        bstack11lllllll1_opy_ = bstack111lll11lll_opy_(report.stop)
    elif hasattr(report, bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡲࡵࠩ⎖")):
        bstack11lllllll1_opy_ = bstack111lll11lll_opy_(report.start)
    try:
        if getattr(report, bstack1l1l_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩ⎗"), bstack1l1l_opy_ (u"ࠬ࠭⎘")) == bstack1l1l_opy_ (u"࠭ࡣࡢ࡮࡯ࠫ⎙"):
            logger.debug(bstack1l1l_opy_ (u"ࠧࡩࡣࡱࡨࡱ࡫࡟ࡰ࠳࠴ࡽࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡷࡹࡧࡴࡦࠢ࠰ࠤࢀࢃࠬࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤ࠲ࠦࡻࡾࠩ⎚").format(getattr(report, bstack1l1l_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⎛"), bstack1l1l_opy_ (u"ࠩࠪ⎜")).__str__(), bstack1lll1l11l111_opy_))
            if bstack1lll1l11l111_opy_ == bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⎝"):
                _111l1111ll_opy_[item.nodeid][bstack1l1l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⎞")] = bstack11lllllll1_opy_
                bstack1lll1l1111l1_opy_(item, _111l1111ll_opy_[item.nodeid], bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⎟"), report, call)
                store[bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ⎠")] = None
            elif bstack1lll1l11l111_opy_ == bstack1l1l_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦ⎡"):
                bstack111l1lll1l_opy_ = _111l1111ll_opy_[item.nodeid][bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ⎢")]
                bstack111l1lll1l_opy_.set(hooks=_111l1111ll_opy_[item.nodeid].get(bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⎣"), []))
                exception, bstack111l1l1lll_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack111l1l1lll_opy_ = [call.excinfo.exconly(), getattr(report, bstack1l1l_opy_ (u"ࠪࡰࡴࡴࡧࡳࡧࡳࡶࡹ࡫ࡸࡵࠩ⎤"), bstack1l1l_opy_ (u"ࠫࠬ⎥"))]
                bstack111l1lll1l_opy_.stop(time=bstack11lllllll1_opy_, result=Result(result=getattr(report, bstack1l1l_opy_ (u"ࠬࡵࡵࡵࡥࡲࡱࡪ࠭⎦"), bstack1l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭⎧")), exception=exception, bstack111l1l1lll_opy_=bstack111l1l1lll_opy_))
                bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ⎨"), _111l1111ll_opy_[item.nodeid][bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ⎩")])
        elif getattr(report, bstack1l1l_opy_ (u"ࠩࡺ࡬ࡪࡴࠧ⎪"), bstack1l1l_opy_ (u"ࠪࠫ⎫")) in [bstack1l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ⎬"), bstack1l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧ⎭")]:
            logger.debug(bstack1l1l_opy_ (u"࠭ࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡶࡸࡦࡺࡥࠡ࠯ࠣࡿࢂ࠲ࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠣ࠱ࠥࢁࡽࠨ⎮").format(getattr(report, bstack1l1l_opy_ (u"ࠧࡸࡪࡨࡲࠬ⎯"), bstack1l1l_opy_ (u"ࠨࠩ⎰")).__str__(), bstack1lll1l11l111_opy_))
            bstack111l1ll1ll_opy_ = item.nodeid + bstack1l1l_opy_ (u"ࠩ࠰ࠫ⎱") + getattr(report, bstack1l1l_opy_ (u"ࠪࡻ࡭࡫࡮ࠨ⎲"), bstack1l1l_opy_ (u"ࠫࠬ⎳"))
            if getattr(report, bstack1l1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭⎴"), False):
                hook_type = bstack1l1l_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫ⎵") if getattr(report, bstack1l1l_opy_ (u"ࠧࡸࡪࡨࡲࠬ⎶"), bstack1l1l_opy_ (u"ࠨࠩ⎷")) == bstack1l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⎸") else bstack1l1l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ⎹")
                _111l1111ll_opy_[bstack111l1ll1ll_opy_] = {
                    bstack1l1l_opy_ (u"ࠫࡺࡻࡩࡥࠩ⎺"): uuid4().__str__(),
                    bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⎻"): bstack11lllllll1_opy_,
                    bstack1l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ⎼"): hook_type
                }
            _111l1111ll_opy_[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⎽")] = bstack11lllllll1_opy_
            bstack1lll1l1ll11l_opy_(_111l1111ll_opy_[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⎾")])
            bstack1lll1l111ll1_opy_(item, _111l1111ll_opy_[bstack111l1ll1ll_opy_], bstack1l1l_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⎿"), report, call)
            if getattr(report, bstack1l1l_opy_ (u"ࠪࡻ࡭࡫࡮ࠨ⏀"), bstack1l1l_opy_ (u"ࠫࠬ⏁")) == bstack1l1l_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⏂"):
                if getattr(report, bstack1l1l_opy_ (u"࠭࡯ࡶࡶࡦࡳࡲ࡫ࠧ⏃"), bstack1l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⏄")) == bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⏅"):
                    bstack111l1l11ll_opy_ = {
                        bstack1l1l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⏆"): uuid4().__str__(),
                        bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⏇"): bstack1111lllll_opy_(),
                        bstack1l1l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⏈"): bstack1111lllll_opy_()
                    }
                    _111l1111ll_opy_[item.nodeid] = {**_111l1111ll_opy_[item.nodeid], **bstack111l1l11ll_opy_}
                    bstack1lll1l1111l1_opy_(item, _111l1111ll_opy_[item.nodeid], bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭⏉"))
                    bstack1lll1l1111l1_opy_(item, _111l1111ll_opy_[item.nodeid], bstack1l1l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⏊"), report, call)
    except Exception as err:
        print(bstack1l1l_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡾࢁࠬ⏋"), str(err))
def bstack1lll11llll11_opy_(test, bstack111l1l11ll_opy_, result=None, call=None, bstack11111ll1_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111l1lll1l_opy_ = {
        bstack1l1l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⏌"): bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⏍")],
        bstack1l1l_opy_ (u"ࠪࡸࡾࡶࡥࠨ⏎"): bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ⏏"),
        bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⏐"): test.name,
        bstack1l1l_opy_ (u"࠭ࡢࡰࡦࡼࠫ⏑"): {
            bstack1l1l_opy_ (u"ࠧ࡭ࡣࡱ࡫ࠬ⏒"): bstack1l1l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ⏓"),
            bstack1l1l_opy_ (u"ࠩࡦࡳࡩ࡫ࠧ⏔"): inspect.getsource(test.obj)
        },
        bstack1l1l_opy_ (u"ࠪ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ⏕"): test.name,
        bstack1l1l_opy_ (u"ࠫࡸࡩ࡯ࡱࡧࠪ⏖"): test.name,
        bstack1l1l_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬ⏗"): bstack1l1ll11111_opy_.bstack1111llll1l_opy_(test),
        bstack1l1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ⏘"): file_path,
        bstack1l1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠩ⏙"): file_path,
        bstack1l1l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⏚"): bstack1l1l_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ⏛"),
        bstack1l1l_opy_ (u"ࠪࡺࡨࡥࡦࡪ࡮ࡨࡴࡦࡺࡨࠨ⏜"): file_path,
        bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⏝"): bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⏞")],
        bstack1l1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ⏟"): bstack1l1l_opy_ (u"ࠧࡑࡻࡷࡩࡸࡺࠧ⏠"),
        bstack1l1l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡓࡧࡵࡹࡳࡖࡡࡳࡣࡰࠫ⏡"): {
            bstack1l1l_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡰࡤࡱࡪ࠭⏢"): test.nodeid
        },
        bstack1l1l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ⏣"): bstack11l111l1l11_opy_(test.own_markers)
    }
    if bstack11111ll1_opy_ in [bstack1l1l_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡱࡩࡱࡲࡨࡨࠬ⏤"), bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⏥")]:
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"࠭࡭ࡦࡶࡤࠫ⏦")] = {
            bstack1l1l_opy_ (u"ࠧࡧ࡫ࡻࡸࡺࡸࡥࡴࠩ⏧"): bstack111l1l11ll_opy_.get(bstack1l1l_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪ⏨"), [])
        }
    if bstack11111ll1_opy_ == bstack1l1l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ⏩"):
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⏪")] = bstack1l1l_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⏫")
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⏬")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⏭")]
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⏮")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⏯")]
    if result:
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⏰")] = result.outcome
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫ⏱")] = result.duration * 1000
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⏲")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⏳")]
        if result.failed:
            bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ⏴")] = bstack11l1llllll_opy_.bstack1llllll111l_opy_(call.excinfo.typename)
            bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ⏵")] = bstack11l1llllll_opy_.bstack1llll11111ll_opy_(call.excinfo, result)
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⏶")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⏷")]
    if outcome:
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⏸")] = bstack111ll11llll_opy_(outcome)
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬ⏹")] = 0
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⏺")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⏻")]
        if bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⏼")] == bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⏽"):
            bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨ⏾")] = bstack1l1l_opy_ (u"࡙ࠪࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠫ⏿")  # bstack1lll1l11ll11_opy_
            bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ␀")] = [{bstack1l1l_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ␁"): [bstack1l1l_opy_ (u"࠭ࡳࡰ࡯ࡨࠤࡪࡸࡲࡰࡴࠪ␂")]}]
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭␃")] = bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ␄")]
    return bstack111l1lll1l_opy_
def bstack1lll1l11l1ll_opy_(test, bstack1111l1lll1_opy_, bstack11111ll1_opy_, result, call, outcome, bstack1lll1l1l11ll_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ␅")]
    hook_name = bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡰࡤࡱࡪ࠭␆")]
    hook_data = {
        bstack1l1l_opy_ (u"ࠫࡺࡻࡩࡥࠩ␇"): bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠬࡻࡵࡪࡦࠪ␈")],
        bstack1l1l_opy_ (u"࠭ࡴࡺࡲࡨࠫ␉"): bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࠬ␊"),
        bstack1l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭␋"): bstack1l1l_opy_ (u"ࠩࡾࢁࠬ␌").format(bstack1lllll11l1ll_opy_(hook_name)),
        bstack1l1l_opy_ (u"ࠪࡦࡴࡪࡹࠨ␍"): {
            bstack1l1l_opy_ (u"ࠫࡱࡧ࡮ࡨࠩ␎"): bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ␏"),
            bstack1l1l_opy_ (u"࠭ࡣࡰࡦࡨࠫ␐"): None
        },
        bstack1l1l_opy_ (u"ࠧࡴࡥࡲࡴࡪ࠭␑"): test.name,
        bstack1l1l_opy_ (u"ࠨࡵࡦࡳࡵ࡫ࡳࠨ␒"): bstack1l1ll11111_opy_.bstack1111llll1l_opy_(test, hook_name),
        bstack1l1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ␓"): file_path,
        bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡࡵ࡫ࡲࡲࠬ␔"): file_path,
        bstack1l1l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ␕"): bstack1l1l_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭␖"),
        bstack1l1l_opy_ (u"࠭ࡶࡤࡡࡩ࡭ࡱ࡫ࡰࡢࡶ࡫ࠫ␗"): file_path,
        bstack1l1l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ␘"): bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ␙")],
        bstack1l1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ␚"): bstack1l1l_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶ࠰ࡧࡺࡩࡵ࡮ࡤࡨࡶࠬ␛") if bstack1lll1l11l111_opy_ == bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨ␜") else bstack1l1l_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ␝"),
        bstack1l1l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ␞"): hook_type
    }
    bstack1l1lll1ll11_opy_ = bstack111l11l1ll_opy_(_111l1111ll_opy_.get(test.nodeid, None))
    if bstack1l1lll1ll11_opy_:
        hook_data[bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡ࡬ࡨࠬ␟")] = bstack1l1lll1ll11_opy_
    if result:
        hook_data[bstack1l1l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ␠")] = result.outcome
        hook_data[bstack1l1l_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ␡")] = result.duration * 1000
        hook_data[bstack1l1l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ␢")] = bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ␣")]
        if result.failed:
            hook_data[bstack1l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠫ␤")] = bstack11l1llllll_opy_.bstack1llllll111l_opy_(call.excinfo.typename)
            hook_data[bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ␥")] = bstack11l1llllll_opy_.bstack1llll11111ll_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack1l1l_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ␦")] = bstack111ll11llll_opy_(outcome)
        hook_data[bstack1l1l_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ␧")] = 100
        hook_data[bstack1l1l_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ␨")] = bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ␩")]
        if hook_data[bstack1l1l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ␪")] == bstack1l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ␫"):
            hook_data[bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ␬")] = bstack1l1l_opy_ (u"ࠧࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠨ␭")  # bstack1lll1l11ll11_opy_
            hook_data[bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩ␮")] = [{bstack1l1l_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬ␯"): [bstack1l1l_opy_ (u"ࠪࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠧ␰")]}]
    if bstack1lll1l1l11ll_opy_:
        hook_data[bstack1l1l_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ␱")] = bstack1lll1l1l11ll_opy_.result
        hook_data[bstack1l1l_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡢࡱࡸ࠭␲")] = bstack111llllll11_opy_(bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ␳")], bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ␴")])
        hook_data[bstack1l1l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭␵")] = bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ␶")]
        if hook_data[bstack1l1l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ␷")] == bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ␸"):
            hook_data[bstack1l1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠫ␹")] = bstack11l1llllll_opy_.bstack1llllll111l_opy_(bstack1lll1l1l11ll_opy_.exception_type)
            hook_data[bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ␺")] = [{bstack1l1l_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪ␻"): bstack11l1111ll1l_opy_(bstack1lll1l1l11ll_opy_.exception)}]
    return hook_data
def bstack1lll1l1111l1_opy_(test, bstack111l1l11ll_opy_, bstack11111ll1_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack1l1l_opy_ (u"ࠨࡵࡨࡲࡩࡥࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡧࡹࡩࡳࡺ࠺ࠡࡃࡷࡸࡪࡳࡰࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡩࡨࡲࡪࡸࡡࡵࡧࠣࡸࡪࡹࡴࠡࡦࡤࡸࡦࠦࡦࡰࡴࠣࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠠ࠮ࠢࡾࢁࠬ␼").format(bstack11111ll1_opy_))
    bstack111l1lll1l_opy_ = bstack1lll11llll11_opy_(test, bstack111l1l11ll_opy_, result, call, bstack11111ll1_opy_, outcome)
    driver = getattr(test, bstack1l1l_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ␽"), None)
    if bstack11111ll1_opy_ == bstack1l1l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ␾") and driver:
        bstack111l1lll1l_opy_[bstack1l1l_opy_ (u"ࠫ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠪ␿")] = bstack11l1llllll_opy_.bstack111l1l1l11_opy_(driver)
    if bstack11111ll1_opy_ == bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙࡫ࡪࡲࡳࡩࡩ࠭⑀"):
        bstack11111ll1_opy_ = bstack1l1l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⑁")
    bstack111l11lll1_opy_ = {
        bstack1l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⑂"): bstack11111ll1_opy_,
        bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ⑃"): bstack111l1lll1l_opy_
    }
    bstack11l1llllll_opy_.bstack1lll1111_opy_(bstack111l11lll1_opy_)
    if bstack11111ll1_opy_ == bstack1l1l_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ⑄"):
        threading.current_thread().bstackTestMeta = {bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⑅"): bstack1l1l_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ⑆")}
    elif bstack11111ll1_opy_ == bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⑇"):
        threading.current_thread().bstackTestMeta = {bstack1l1l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⑈"): getattr(result, bstack1l1l_opy_ (u"ࠧࡰࡷࡷࡧࡴࡳࡥࠨ⑉"), bstack1l1l_opy_ (u"ࠨࠩ⑊"))}
def bstack1lll1l111ll1_opy_(test, bstack111l1l11ll_opy_, bstack11111ll1_opy_, result=None, call=None, outcome=None, bstack1lll1l1l11ll_opy_=None):
    logger.debug(bstack1l1l_opy_ (u"ࠩࡶࡩࡳࡪ࡟ࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡨࡺࡪࡴࡴ࠻ࠢࡄࡸࡹ࡫࡭ࡱࡶ࡬ࡲ࡬ࠦࡴࡰࠢࡪࡩࡳ࡫ࡲࡢࡶࡨࠤ࡭ࡵ࡯࡬ࠢࡧࡥࡹࡧࠬࠡࡧࡹࡩࡳࡺࡔࡺࡲࡨࠤ࠲ࠦࡻࡾࠩ⑋").format(bstack11111ll1_opy_))
    hook_data = bstack1lll1l11l1ll_opy_(test, bstack111l1l11ll_opy_, bstack11111ll1_opy_, result, call, outcome, bstack1lll1l1l11ll_opy_)
    bstack111l11lll1_opy_ = {
        bstack1l1l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⑌"): bstack11111ll1_opy_,
        bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳ࠭⑍"): hook_data
    }
    bstack11l1llllll_opy_.bstack1lll1111_opy_(bstack111l11lll1_opy_)
def bstack111l11l1ll_opy_(bstack111l1l11ll_opy_):
    if not bstack111l1l11ll_opy_:
        return None
    if bstack111l1l11ll_opy_.get(bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⑎"), None):
        return getattr(bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⑏")], bstack1l1l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⑐"), None)
    return bstack111l1l11ll_opy_.get(bstack1l1l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⑑"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.LOG, bstack1ll1ll111l1_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_.LOG, bstack1ll1ll111l1_opy_.POST, request, caplog)
        return # skip all existing operations
    try:
        if not bstack11l1llllll_opy_.on():
            return
        places = [bstack1l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⑒"), bstack1l1l_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⑓"), bstack1l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠭⑔")]
        logs = []
        for bstack1lll11llll1l_opy_ in places:
            records = caplog.get_records(bstack1lll11llll1l_opy_)
            bstack1lll1l111l1l_opy_ = bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⑕") if bstack1lll11llll1l_opy_ == bstack1l1l_opy_ (u"࠭ࡣࡢ࡮࡯ࠫ⑖") else bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⑗")
            bstack1lll1l1111ll_opy_ = request.node.nodeid + (bstack1l1l_opy_ (u"ࠨࠩ⑘") if bstack1lll11llll1l_opy_ == bstack1l1l_opy_ (u"ࠩࡦࡥࡱࡲࠧ⑙") else bstack1l1l_opy_ (u"ࠪ࠱ࠬ⑚") + bstack1lll11llll1l_opy_)
            test_uuid = bstack111l11l1ll_opy_(_111l1111ll_opy_.get(bstack1lll1l1111ll_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack11l111l1l1l_opy_(record.message):
                    continue
                logs.append({
                    bstack1l1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ⑛"): bstack11l11l11111_opy_(record.created).isoformat() + bstack1l1l_opy_ (u"ࠬࡠࠧ⑜"),
                    bstack1l1l_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⑝"): record.levelname,
                    bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⑞"): record.message,
                    bstack1lll1l111l1l_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack11l1llllll_opy_.bstack1llll11lll_opy_(logs)
    except Exception as err:
        print(bstack1l1l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡦࡳࡳࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥ࠻ࠢࡾࢁࠬ⑟"), str(err))
def bstack1ll1ll1111_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack1l1l1ll111_opy_
    bstack11l11ll1_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩ࡬ࡷࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭①"), None) and bstack11llll11ll_opy_(
            threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ②"), None)
    bstack1ll11l1l1_opy_ = getattr(driver, bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫ③"), None) != None and getattr(driver, bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡆ࠷࠱ࡺࡕ࡫ࡳࡺࡲࡤࡔࡥࡤࡲࠬ④"), None) == True
    if sequence == bstack1l1l_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭⑤") and driver != None:
      if not bstack1l1l1ll111_opy_ and bstack1l1l111l1l1_opy_() and bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ⑥") in CONFIG and CONFIG[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⑦")] == True and bstack111111lll_opy_.bstack1ll1l1111_opy_(driver_command) and (bstack1ll11l1l1_opy_ or bstack11l11ll1_opy_) and not bstack11ll1l11l1_opy_(args):
        try:
          bstack1l1l1ll111_opy_ = True
          logger.debug(bstack1l1l_opy_ (u"ࠩࡓࡩࡷ࡬࡯ࡳ࡯࡬ࡲ࡬ࠦࡳࡤࡣࡱࠤ࡫ࡵࡲࠡࡽࢀࠫ⑧").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack1l1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡦࡴࡩࡳࡷࡳࠠࡴࡥࡤࡲࠥࢁࡽࠨ⑨").format(str(err)))
        bstack1l1l1ll111_opy_ = False
    if sequence == bstack1l1l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪ⑩"):
        if driver_command == bstack1l1l_opy_ (u"ࠬࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࠩ⑪"):
            bstack11l1llllll_opy_.bstack1ll11l111l_opy_({
                bstack1l1l_opy_ (u"࠭ࡩ࡮ࡣࡪࡩࠬ⑫"): response[bstack1l1l_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭⑬")],
                bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⑭"): store[bstack1l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭⑮")]
            })
def bstack111ll11ll_opy_():
    global bstack1l11l11l_opy_
    bstack1lllllll1l_opy_.bstack1lllll11l1_opy_()
    logging.shutdown()
    bstack11l1llllll_opy_.bstack111l111lll_opy_()
    for driver in bstack1l11l11l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1lll1l11lll1_opy_(*args):
    global bstack1l11l11l_opy_
    bstack11l1llllll_opy_.bstack111l111lll_opy_()
    for driver in bstack1l11l11l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1ll1l1l1l1_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1lllll11ll_opy_(self, *args, **kwargs):
    bstack1llll11ll1_opy_ = bstack111ll1l1l_opy_(self, *args, **kwargs)
    bstack111lll111l_opy_ = getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ⑯"), None)
    if bstack111lll111l_opy_ and bstack111lll111l_opy_.get(bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⑰"), bstack1l1l_opy_ (u"ࠬ࠭⑱")) == bstack1l1l_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧ⑲"):
        bstack11l1llllll_opy_.bstack111ll1llll_opy_(self)
    return bstack1llll11ll1_opy_
@measure(event_name=EVENTS.bstack1l1l1l111_opy_, stage=STAGE.bstack1l1ll1l1ll_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1ll11111l_opy_(framework_name):
    from bstack_utils.config import Config
    bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
    if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ⑳")):
        return
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠ࡯ࡲࡨࡤࡩࡡ࡭࡮ࡨࡨࠬ⑴"), True)
    global bstack1lll1l11l1_opy_
    global bstack11ll1l11ll_opy_
    bstack1lll1l11l1_opy_ = framework_name
    logger.info(bstack11111111l_opy_.format(bstack1lll1l11l1_opy_.split(bstack1l1l_opy_ (u"ࠩ࠰ࠫ⑵"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1l1l111l1l1_opy_():
            Service.start = bstack1l11111ll1_opy_
            Service.stop = bstack1l1l11l1_opy_
            webdriver.Remote.get = bstack1l1111111_opy_
            webdriver.Remote.__init__ = bstack111lll1ll1_opy_
            if not isinstance(os.getenv(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡅࡗࡇࡌࡍࡇࡏࠫ⑶")), str):
                return
            WebDriver.quit = bstack11l1111l1l_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack11l1llllll_opy_.on():
            webdriver.Remote.__init__ = bstack1lllll11ll_opy_
        bstack11ll1l11ll_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack1l1l_opy_ (u"ࠫࡘࡋࡌࡆࡐࡌ࡙ࡒࡥࡏࡓࡡࡓࡐࡆ࡟ࡗࡓࡋࡊࡌ࡙ࡥࡉࡏࡕࡗࡅࡑࡒࡅࡅࠩ⑷")):
        bstack11ll1l11ll_opy_ = eval(os.environ.get(bstack1l1l_opy_ (u"࡙ࠬࡅࡍࡇࡑࡍ࡚ࡓ࡟ࡐࡔࡢࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡊࡐࡖࡘࡆࡒࡌࡆࡆࠪ⑸")))
    if not bstack11ll1l11ll_opy_:
        bstack1l1111ll_opy_(bstack1l1l_opy_ (u"ࠨࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠡࡰࡲࡸࠥ࡯࡮ࡴࡶࡤࡰࡱ࡫ࡤࠣ⑹"), bstack11l1111l_opy_)
    if bstack11l1111l1_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack1l1l_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨ⑺")) and callable(getattr(RemoteConnection, bstack1l1l_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩ⑻"))):
                RemoteConnection._get_proxy_url = bstack1l1l111l1l_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack1l1l111l1l_opy_
        except Exception as e:
            logger.error(bstack11l11111l_opy_.format(str(e)))
    if bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ⑼") in str(framework_name).lower():
        if not bstack1l1l111l1l1_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack1llll1lll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1lll1l11_opy_
            Config.getoption = bstack1l1ll1111l_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack1l1llllll1_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack11l1l111ll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack11l1111l1l_opy_(self):
    global bstack1lll1l11l1_opy_
    global bstack1lll1lll1_opy_
    global bstack11l1lll111_opy_
    try:
        if bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⑽") in bstack1lll1l11l1_opy_ and self.session_id != None and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡕࡷࡥࡹࡻࡳࠨ⑾"), bstack1l1l_opy_ (u"ࠬ࠭⑿")) != bstack1l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ⒀"):
            bstack11l11l1111_opy_ = bstack1l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⒁") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⒂")
            bstack11ll11lll_opy_(logger, True)
            if os.environ.get(bstack1l1l_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ⒃"), None):
                self.execute_script(
                    bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨ⒄") + json.dumps(
                        os.environ.get(bstack1l1l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧ⒅"))) + bstack1l1l_opy_ (u"ࠬࢃࡽࠨ⒆"))
            if self != None:
                bstack11ll11111_opy_(self, bstack11l11l1111_opy_, bstack1l1l_opy_ (u"࠭ࠬࠡࠩ⒇").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1lll1l1ll11_opy_(bstack1ll1l111l1l_opy_):
            item = store.get(bstack1l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫ⒈"), None)
            if item is not None and bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ⒉"), None):
                bstack1l11111l1_opy_.bstack1ll1lllll1_opy_(self, bstack11l11l1ll_opy_, logger, item)
        threading.current_thread().testStatus = bstack1l1l_opy_ (u"ࠩࠪ⒊")
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦ⒋") + str(e))
    bstack11l1lll111_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack111l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack111lll1ll1_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1lll1lll1_opy_
    global bstack11ll11ll_opy_
    global bstack1l1ll11lll_opy_
    global bstack1lll1l11l1_opy_
    global bstack111ll1l1l_opy_
    global bstack1l11l11l_opy_
    global bstack11ll1lll1l_opy_
    global bstack1lllll1ll1_opy_
    global bstack11l11l1ll_opy_
    CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭⒌")] = str(bstack1lll1l11l1_opy_) + str(__version__)
    command_executor = bstack111lll11ll_opy_(bstack11ll1lll1l_opy_, CONFIG)
    logger.debug(bstack1ll1lll11l_opy_.format(command_executor))
    proxy = bstack111llll1l1_opy_(CONFIG, proxy)
    bstack1111lll1l_opy_ = 0
    try:
        if bstack1l1ll11lll_opy_ is True:
            bstack1111lll1l_opy_ = int(os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬ⒍")))
    except:
        bstack1111lll1l_opy_ = 0
    bstack11lll1ll11_opy_ = bstack1l111lll1_opy_(CONFIG, bstack1111lll1l_opy_)
    logger.debug(bstack1l11ll1ll1_opy_.format(str(bstack11lll1ll11_opy_)))
    bstack11l11l1ll_opy_ = CONFIG.get(bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ⒎"))[bstack1111lll1l_opy_]
    if bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ⒏") in CONFIG and CONFIG[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ⒐")]:
        bstack1llll111ll_opy_(bstack11lll1ll11_opy_, bstack1lllll1ll1_opy_)
    if bstack1lllllll11_opy_.bstack1l1l11l1ll_opy_(CONFIG, bstack1111lll1l_opy_) and bstack1lllllll11_opy_.bstack1111ll1l_opy_(bstack11lll1ll11_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1lll1l1ll11_opy_(bstack1ll1l111l1l_opy_):
            bstack1lllllll11_opy_.set_capabilities(bstack11lll1ll11_opy_, CONFIG)
    if desired_capabilities:
        bstack1lll1l1ll1_opy_ = bstack1l1llll11l_opy_(desired_capabilities)
        bstack1lll1l1ll1_opy_[bstack1l1l_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩ⒑")] = bstack1llll11l1_opy_(CONFIG)
        bstack1lll1111l1_opy_ = bstack1l111lll1_opy_(bstack1lll1l1ll1_opy_)
        if bstack1lll1111l1_opy_:
            bstack11lll1ll11_opy_ = update(bstack1lll1111l1_opy_, bstack11lll1ll11_opy_)
        desired_capabilities = None
    if options:
        bstack11l1l1ll_opy_(options, bstack11lll1ll11_opy_)
    if not options:
        options = bstack1l11l11l11_opy_(bstack11lll1ll11_opy_)
    if proxy and bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠪ࠸࠳࠷࠰࠯࠲ࠪ⒒")):
        options.proxy(proxy)
    if options and bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪ⒓")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack1llllll1l1_opy_() < version.parse(bstack1l1l_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫ⒔")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack11lll1ll11_opy_)
    logger.info(bstack11l1111ll1_opy_)
    bstack1ll111ll11_opy_.end(EVENTS.bstack1l1l1l111_opy_.value, EVENTS.bstack1l1l1l111_opy_.value + bstack1l1l_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨ⒕"),
                               EVENTS.bstack1l1l1l111_opy_.value + bstack1l1l_opy_ (u"ࠢ࠻ࡧࡱࡨࠧ⒖"), True, None)
    try:
        if bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨ⒗")):
            bstack111ll1l1l_opy_(self, command_executor=command_executor,
                      options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
        elif bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨ⒘")):
            bstack111ll1l1l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities, options=options,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        elif bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠪ࠶࠳࠻࠳࠯࠲ࠪ⒙")):
            bstack111ll1l1l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        else:
            bstack111ll1l1l_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive)
    except Exception as bstack1llll1l11l_opy_:
        logger.error(bstack1l11l11ll_opy_.format(bstack1l1l_opy_ (u"ࠫࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠪ⒚"), str(bstack1llll1l11l_opy_)))
        raise bstack1llll1l11l_opy_
    try:
        bstack11llllll1l_opy_ = bstack1l1l_opy_ (u"ࠬ࠭⒛")
        if bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"࠭࠴࠯࠲࠱࠴ࡧ࠷ࠧ⒜")):
            bstack11llllll1l_opy_ = self.caps.get(bstack1l1l_opy_ (u"ࠢࡰࡲࡷ࡭ࡲࡧ࡬ࡉࡷࡥ࡙ࡷࡲࠢ⒝"))
        else:
            bstack11llllll1l_opy_ = self.capabilities.get(bstack1l1l_opy_ (u"ࠣࡱࡳࡸ࡮ࡳࡡ࡭ࡊࡸࡦ࡚ࡸ࡬ࠣ⒞"))
        if bstack11llllll1l_opy_:
            bstack1ll1ll111_opy_(bstack11llllll1l_opy_)
            if bstack1llllll1l1_opy_() <= version.parse(bstack1l1l_opy_ (u"ࠩ࠶࠲࠶࠹࠮࠱ࠩ⒟")):
                self.command_executor._url = bstack1l1l_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࠦ⒠") + bstack11ll1lll1l_opy_ + bstack1l1l_opy_ (u"ࠦ࠿࠾࠰࠰ࡹࡧ࠳࡭ࡻࡢࠣ⒡")
            else:
                self.command_executor._url = bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢ⒢") + bstack11llllll1l_opy_ + bstack1l1l_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢ⒣")
            logger.debug(bstack11l1ll1lll_opy_.format(bstack11llllll1l_opy_))
        else:
            logger.debug(bstack1l1l1ll1l_opy_.format(bstack1l1l_opy_ (u"ࠢࡐࡲࡷ࡭ࡲࡧ࡬ࠡࡊࡸࡦࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤࠣ⒤")))
    except Exception as e:
        logger.debug(bstack1l1l1ll1l_opy_.format(e))
    bstack1lll1lll1_opy_ = self.session_id
    if bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⒥") in bstack1lll1l11l1_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack1l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⒦"), None)
        if item:
            bstack1lll1l111111_opy_ = getattr(item, bstack1l1l_opy_ (u"ࠪࡣࡹ࡫ࡳࡵࡡࡦࡥࡸ࡫࡟ࡴࡶࡤࡶࡹ࡫ࡤࠨ⒧"), False)
            if not getattr(item, bstack1l1l_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ⒨"), None) and bstack1lll1l111111_opy_:
                setattr(store[bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⒩")], bstack1l1l_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⒪"), self)
        bstack111lll111l_opy_ = getattr(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡔࡦࡵࡷࡑࡪࡺࡡࠨ⒫"), None)
        if bstack111lll111l_opy_ and bstack111lll111l_opy_.get(bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ⒬"), bstack1l1l_opy_ (u"ࠩࠪ⒭")) == bstack1l1l_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ⒮"):
            bstack11l1llllll_opy_.bstack111ll1llll_opy_(self)
    bstack1l11l11l_opy_.append(self)
    if bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ⒯") in CONFIG and bstack1l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⒰") in CONFIG[bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ⒱")][bstack1111lll1l_opy_]:
        bstack11ll11ll_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ⒲")][bstack1111lll1l_opy_][bstack1l1l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭⒳")]
    logger.debug(bstack1lll1l111_opy_.format(bstack1lll1lll1_opy_))
@measure(event_name=EVENTS.bstack1l11l11lll_opy_, stage=STAGE.bstack11lll1l1_opy_, bstack1l1l1l11_opy_=bstack11ll11ll_opy_)
def bstack1l1111111_opy_(self, url):
    global bstack11l1lllll1_opy_
    global CONFIG
    try:
        bstack11l11111_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack1l111lllll_opy_.format(str(err)))
    try:
        bstack11l1lllll1_opy_(self, url)
    except Exception as e:
        try:
            bstack11lll11l_opy_ = str(e)
            if any(err_msg in bstack11lll11l_opy_ for err_msg in bstack1l1ll1lll1_opy_):
                bstack11l11111_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack1l111lllll_opy_.format(str(err)))
        raise e
def bstack11111l1l1_opy_(item, when):
    global bstack1ll11l11l1_opy_
    try:
        bstack1ll11l11l1_opy_(item, when)
    except Exception as e:
        pass
def bstack1l1llllll1_opy_(item, call, rep):
    global bstack111lll1ll_opy_
    global bstack1l11l11l_opy_
    name = bstack1l1l_opy_ (u"ࠩࠪ⒴")
    try:
        if rep.when == bstack1l1l_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⒵"):
            bstack1lll1lll1_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack1l1l_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭Ⓐ"))
            try:
                if (str(skipSessionName).lower() != bstack1l1l_opy_ (u"ࠬࡺࡲࡶࡧࠪⒷ")):
                    name = str(rep.nodeid)
                    bstack11ll1llll_opy_ = bstack11l11lll1l_opy_(bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧⒸ"), name, bstack1l1l_opy_ (u"ࠧࠨⒹ"), bstack1l1l_opy_ (u"ࠨࠩⒺ"), bstack1l1l_opy_ (u"ࠩࠪⒻ"), bstack1l1l_opy_ (u"ࠪࠫⒼ"))
                    os.environ[bstack1l1l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧⒽ")] = name
                    for driver in bstack1l11l11l_opy_:
                        if bstack1lll1lll1_opy_ == driver.session_id:
                            driver.execute_script(bstack11ll1llll_opy_)
            except Exception as e:
                logger.debug(bstack1l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠦࡦࡰࡴࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡴࡧࡶࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠬⒾ").format(str(e)))
            try:
                bstack1l1l111l1_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack1l1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧⒿ"):
                    status = bstack1l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧⓀ") if rep.outcome.lower() == bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨⓁ") else bstack1l1l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩⓂ")
                    reason = bstack1l1l_opy_ (u"ࠪࠫⓃ")
                    if status == bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫⓄ"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack1l1l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪⓅ") if status == bstack1l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭Ⓠ") else bstack1l1l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭Ⓡ")
                    data = name + bstack1l1l_opy_ (u"ࠨࠢࡳࡥࡸࡹࡥࡥࠣࠪⓈ") if status == bstack1l1l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩⓉ") else name + bstack1l1l_opy_ (u"ࠪࠤ࡫ࡧࡩ࡭ࡧࡧࠥࠥ࠭Ⓤ") + reason
                    bstack1ll111l1l_opy_ = bstack11l11lll1l_opy_(bstack1l1l_opy_ (u"ࠫࡦࡴ࡮ࡰࡶࡤࡸࡪ࠭Ⓥ"), bstack1l1l_opy_ (u"ࠬ࠭Ⓦ"), bstack1l1l_opy_ (u"࠭ࠧⓍ"), bstack1l1l_opy_ (u"ࠧࠨⓎ"), level, data)
                    for driver in bstack1l11l11l_opy_:
                        if bstack1lll1lll1_opy_ == driver.session_id:
                            driver.execute_script(bstack1ll111l1l_opy_)
            except Exception as e:
                logger.debug(bstack1l1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡩ࡯࡯ࡶࡨࡼࡹࠦࡦࡰࡴࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡴࡧࡶࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠬⓏ").format(str(e)))
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡴࡢࡶࡨࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹ࡫ࡳࡵࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࡿࢂ࠭ⓐ").format(str(e)))
    bstack111lll1ll_opy_(item, call, rep)
notset = Notset()
def bstack1l1ll1111l_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack1l111l111_opy_
    if str(name).lower() == bstack1l1l_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࠪⓑ"):
        return bstack1l1l_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥⓒ")
    else:
        return bstack1l111l111_opy_(self, name, default, skip)
def bstack1l1l111l1l_opy_(self):
    global CONFIG
    global bstack1ll1l1ll1l_opy_
    try:
        proxy = bstack1l11ll1ll_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack1l1l_opy_ (u"ࠬ࠴ࡰࡢࡥࠪⓓ")):
                proxies = bstack11l1111ll_opy_(proxy, bstack111lll11ll_opy_())
                if len(proxies) > 0:
                    protocol, bstack11l11l111l_opy_ = proxies.popitem()
                    if bstack1l1l_opy_ (u"ࠨ࠺࠰࠱ࠥⓔ") in bstack11l11l111l_opy_:
                        return bstack11l11l111l_opy_
                    else:
                        return bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣⓕ") + bstack11l11l111l_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack1l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡵࡸ࡯ࡹࡻࠣࡹࡷࡲࠠ࠻ࠢࡾࢁࠧⓖ").format(str(e)))
    return bstack1ll1l1ll1l_opy_(self)
def bstack11l1111l1_opy_():
    return (bstack1l1l_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬⓗ") in CONFIG or bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧⓘ") in CONFIG) and bstack111ll1111_opy_() and bstack1llllll1l1_opy_() >= version.parse(
        bstack1llll11l_opy_)
def bstack11lll111_opy_(self,
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
    global bstack11ll11ll_opy_
    global bstack1l1ll11lll_opy_
    global bstack1lll1l11l1_opy_
    CONFIG[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ⓙ")] = str(bstack1lll1l11l1_opy_) + str(__version__)
    bstack1111lll1l_opy_ = 0
    try:
        if bstack1l1ll11lll_opy_ is True:
            bstack1111lll1l_opy_ = int(os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬⓚ")))
    except:
        bstack1111lll1l_opy_ = 0
    CONFIG[bstack1l1l_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧⓛ")] = True
    bstack11lll1ll11_opy_ = bstack1l111lll1_opy_(CONFIG, bstack1111lll1l_opy_)
    logger.debug(bstack1l11ll1ll1_opy_.format(str(bstack11lll1ll11_opy_)))
    if CONFIG.get(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫⓜ")):
        bstack1llll111ll_opy_(bstack11lll1ll11_opy_, bstack1lllll1ll1_opy_)
    if bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫⓝ") in CONFIG and bstack1l1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧⓞ") in CONFIG[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ⓟ")][bstack1111lll1l_opy_]:
        bstack11ll11ll_opy_ = CONFIG[bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧⓠ")][bstack1111lll1l_opy_][bstack1l1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪⓡ")]
    import urllib
    import json
    if bstack1l1l_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪⓢ") in CONFIG and str(CONFIG[bstack1l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫⓣ")]).lower() != bstack1l1l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧⓤ"):
        bstack1l1111ll11_opy_ = bstack11l1lll11l_opy_()
        bstack11l11ll111_opy_ = bstack1l1111ll11_opy_ + urllib.parse.quote(json.dumps(bstack11lll1ll11_opy_))
    else:
        bstack11l11ll111_opy_ = bstack1l1l_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫⓥ") + urllib.parse.quote(json.dumps(bstack11lll1ll11_opy_))
    browser = self.connect(bstack11l11ll111_opy_)
    return browser
def bstack11l1ll11l1_opy_():
    global bstack11ll1l11ll_opy_
    global bstack1lll1l11l1_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack111l11l11_opy_
        if not bstack1l1l111l1l1_opy_():
            global bstack1111l1l1_opy_
            if not bstack1111l1l1_opy_:
                from bstack_utils.helper import bstack11111l1ll_opy_, bstack1l1ll1lll_opy_
                bstack1111l1l1_opy_ = bstack11111l1ll_opy_()
                bstack1l1ll1lll_opy_(bstack1lll1l11l1_opy_)
            BrowserType.connect = bstack111l11l11_opy_
            return
        BrowserType.launch = bstack11lll111_opy_
        bstack11ll1l11ll_opy_ = True
    except Exception as e:
        pass
def bstack1lll1l11l1l1_opy_():
    global CONFIG
    global bstack11l11l11l1_opy_
    global bstack11ll1lll1l_opy_
    global bstack1lllll1ll1_opy_
    global bstack1l1ll11lll_opy_
    global bstack1ll1l11l1l_opy_
    CONFIG = json.loads(os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࠩⓦ")))
    bstack11l11l11l1_opy_ = eval(os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬⓧ")))
    bstack11ll1lll1l_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡍ࡛ࡂࡠࡗࡕࡐࠬⓨ"))
    bstack111lll11l_opy_(CONFIG, bstack11l11l11l1_opy_)
    bstack1ll1l11l1l_opy_ = bstack1lllllll1l_opy_.configure_logger(CONFIG, bstack1ll1l11l1l_opy_)
    if cli.bstack1llll1lll1_opy_():
        bstack111l111l_opy_.invoke(bstack11l111111_opy_.CONNECT, bstack11lll1l1l1_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ⓩ"), bstack1l1l_opy_ (u"ࠧ࠱ࠩ⓪")))
        cli.bstack1ll1l1ll1l1_opy_(cli_context.platform_index)
        cli.bstack1lll11111l1_opy_(bstack111lll11ll_opy_(bstack11ll1lll1l_opy_, CONFIG), cli_context.platform_index, bstack1l11l11l11_opy_)
        cli.bstack1lll1l1l1ll_opy_()
        logger.debug(bstack1l1l_opy_ (u"ࠣࡅࡏࡍࠥ࡯ࡳࠡࡣࡦࡸ࡮ࡼࡥࠡࡨࡲࡶࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࠢ⓫") + str(cli_context.platform_index) + bstack1l1l_opy_ (u"ࠤࠥ⓬"))
        return # skip all existing operations
    global bstack111ll1l1l_opy_
    global bstack11l1lll111_opy_
    global bstack1l1llll11_opy_
    global bstack1l1l1l1l11_opy_
    global bstack11lll11l1l_opy_
    global bstack1l11lll1ll_opy_
    global bstack111llll111_opy_
    global bstack11l1lllll1_opy_
    global bstack1ll1l1ll1l_opy_
    global bstack1l111l111_opy_
    global bstack1ll11l11l1_opy_
    global bstack111lll1ll_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack111ll1l1l_opy_ = webdriver.Remote.__init__
        bstack11l1lll111_opy_ = WebDriver.quit
        bstack111llll111_opy_ = WebDriver.close
        bstack11l1lllll1_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭⓭") in CONFIG or bstack1l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨ⓮") in CONFIG) and bstack111ll1111_opy_():
        if bstack1llllll1l1_opy_() < version.parse(bstack1llll11l_opy_):
            logger.error(bstack11lll1lll_opy_.format(bstack1llllll1l1_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack1l1l_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭⓯")) and callable(getattr(RemoteConnection, bstack1l1l_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ⓰"))):
                    bstack1ll1l1ll1l_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack1ll1l1ll1l_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack11l11111l_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack1l111l111_opy_ = Config.getoption
        from _pytest import runner
        bstack1ll11l11l1_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warning(bstack1l1l_opy_ (u"ࠢࠦࡵ࠽ࠤࠪࡹࠢ⓱"), bstack1l1lll1ll_opy_, str(e))
    try:
        from pytest_bdd import reporting
        bstack111lll1ll_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩ⓲"))
    bstack1lllll1ll1_opy_ = CONFIG.get(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭⓳"), {}).get(bstack1l1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⓴"))
    bstack1l1ll11lll_opy_ = True
    bstack1ll11111l_opy_(bstack1l11l1ll_opy_)
if (bstack111ll1lll11_opy_()):
    bstack1lll1l11l1l1_opy_()
@error_handler(class_method=False)
def bstack1lll1l1l1l11_opy_(hook_name, event, bstack11lll1lll11_opy_=None):
    if hook_name not in [bstack1l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬ⓵"), bstack1l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ⓶"), bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⓷"), bstack1l1l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⓸"), bstack1l1l_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸ࠭⓹"), bstack1l1l_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪ⓺"), bstack1l1l_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩ⓻"), bstack1l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭⓼")]:
        return
    node = store[bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⓽")]
    if hook_name in [bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⓾"), bstack1l1l_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⓿")]:
        node = store[bstack1l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡰࡳࡩࡻ࡬ࡦࡡ࡬ࡸࡪࡳࠧ─")]
    elif hook_name in [bstack1l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠧ━"), bstack1l1l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡩ࡬ࡢࡵࡶࠫ│")]:
        node = store[bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡩ࡬ࡢࡵࡶࡣ࡮ࡺࡥ࡮ࠩ┃")]
    hook_type = bstack1lllll11l111_opy_(hook_name)
    if event == bstack1l1l_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬ┄"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_[hook_type], bstack1ll1ll111l1_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack1111l1lll1_opy_ = {
            bstack1l1l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ┅"): uuid,
            bstack1l1l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ┆"): bstack1111lllll_opy_(),
            bstack1l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭┇"): bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ┈"),
            bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭┉"): hook_type,
            bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ┊"): hook_name
        }
        store[bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ┋")].append(uuid)
        bstack1lll1l1l1lll_opy_ = node.nodeid
        if hook_type == bstack1l1l_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫ┌"):
            if not _111l1111ll_opy_.get(bstack1lll1l1l1lll_opy_, None):
                _111l1111ll_opy_[bstack1lll1l1l1lll_opy_] = {bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭┍"): []}
            _111l1111ll_opy_[bstack1lll1l1l1lll_opy_][bstack1l1l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ┎")].append(bstack1111l1lll1_opy_[bstack1l1l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ┏")])
        _111l1111ll_opy_[bstack1lll1l1l1lll_opy_ + bstack1l1l_opy_ (u"ࠪ࠱ࠬ┐") + hook_name] = bstack1111l1lll1_opy_
        bstack1lll1l111ll1_opy_(node, bstack1111l1lll1_opy_, bstack1l1l_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ┑"))
    elif event == bstack1l1l_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫ┒"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1ll1llll111_opy_[hook_type], bstack1ll1ll111l1_opy_.POST, node, None, bstack11lll1lll11_opy_)
            return
        bstack111l1ll1ll_opy_ = node.nodeid + bstack1l1l_opy_ (u"࠭࠭ࠨ┓") + hook_name
        _111l1111ll_opy_[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ└")] = bstack1111lllll_opy_()
        bstack1lll1l1ll11l_opy_(_111l1111ll_opy_[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭┕")])
        bstack1lll1l111ll1_opy_(node, _111l1111ll_opy_[bstack111l1ll1ll_opy_], bstack1l1l_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ┖"), bstack1lll1l1l11ll_opy_=bstack11lll1lll11_opy_)
def bstack1lll1l1ll111_opy_():
    global bstack1lll1l11l111_opy_
    if bstack11ll111l11_opy_():
        bstack1lll1l11l111_opy_ = bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠧ┗")
    else:
        bstack1lll1l11l111_opy_ = bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ┘")
@bstack11l1llllll_opy_.bstack1lll1lll11l1_opy_
def bstack1lll1l1l1ll1_opy_():
    bstack1lll1l1ll111_opy_()
    if cli.is_running():
        try:
            bstack111l1l1l1l1_opy_(bstack1lll1l1l1l11_opy_)
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࡵࠣࡴࡦࡺࡣࡩ࠼ࠣࡿࢂࠨ┙").format(e))
        return
    if bstack111ll1111_opy_():
        bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
        bstack1l1l_opy_ (u"࠭ࠧࠨࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡇࡱࡵࠤࡵࡶࡰࠡ࠿ࠣ࠵࠱ࠦ࡭ࡰࡦࡢࡩࡽ࡫ࡣࡶࡶࡨࠤ࡬࡫ࡴࡴࠢࡸࡷࡪࡪࠠࡧࡱࡵࠤࡦ࠷࠱ࡺࠢࡦࡳࡲࡳࡡ࡯ࡦࡶ࠱ࡼࡸࡡࡱࡲ࡬ࡲ࡬ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡋࡵࡲࠡࡲࡳࡴࠥࡄࠠ࠲࠮ࠣࡱࡴࡪ࡟ࡦࡺࡨࡧࡺࡺࡥࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡶࡺࡴࠠࡣࡧࡦࡥࡺࡹࡥࠡ࡫ࡷࠤ࡮ࡹࠠࡱࡣࡷࡧ࡭࡫ࡤࠡ࡫ࡱࠤࡦࠦࡤࡪࡨࡩࡩࡷ࡫࡮ࡵࠢࡳࡶࡴࡩࡥࡴࡵࠣ࡭ࡩࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡙࡮ࡵࡴࠢࡺࡩࠥࡴࡥࡦࡦࠣࡸࡴࠦࡵࡴࡧࠣࡗࡪࡲࡥ࡯࡫ࡸࡱࡕࡧࡴࡤࡪࠫࡷࡪࡲࡥ࡯࡫ࡸࡱࡤ࡮ࡡ࡯ࡦ࡯ࡩࡷ࠯ࠠࡧࡱࡵࠤࡵࡶࡰࠡࡀࠣ࠵ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠧࠨࠩ┚")
        if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ┛")):
            if CONFIG.get(bstack1l1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ├")) is not None and int(CONFIG[bstack1l1l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ┝")]) > 1:
                bstack1lllll11_opy_(bstack1ll1ll1111_opy_)
            return
        bstack1lllll11_opy_(bstack1ll1ll1111_opy_)
    try:
        bstack111l1l1l1l1_opy_(bstack1lll1l1l1l11_opy_)
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢ࡫ࡳࡴࡱࡳࠡࡲࡤࡸࡨ࡮࠺ࠡࡽࢀࠦ┞").format(e))
bstack1lll1l1l1ll1_opy_()