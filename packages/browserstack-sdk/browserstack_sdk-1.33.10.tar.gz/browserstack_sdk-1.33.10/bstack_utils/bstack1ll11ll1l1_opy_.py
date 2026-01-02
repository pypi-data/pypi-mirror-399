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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack1l1llll1_opy_ import get_logger
logger = get_logger(__name__)
bstack1llllll111l1_opy_: Dict[str, float] = {}
bstack1llllll1111l_opy_: List = []
bstack1llllll11l11_opy_ = 5
bstack1l1l11l1l1_opy_ = os.path.join(os.getcwd(), bstack11111l_opy_ (u"ࠬࡲ࡯ࡨࠩΉ"), bstack11111l_opy_ (u"࠭࡫ࡦࡻ࠰ࡱࡪࡺࡲࡪࡥࡶ࠲࡯ࡹ࡯࡯ࠩῌ"))
logging.getLogger(bstack11111l_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠩ῍")).setLevel(logging.WARNING)
lock = FileLock(bstack1l1l11l1l1_opy_+bstack11111l_opy_ (u"ࠣ࠰࡯ࡳࡨࡱࠢ῎"))
class bstack1lllll1lll1l_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack1llllll111ll_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1llllll111ll_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack11111l_opy_ (u"ࠤࡰࡩࡦࡹࡵࡳࡧࠥ῏")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1ll1l111ll1_opy_:
    global bstack1llllll111l1_opy_
    @staticmethod
    def bstack1ll1111111l_opy_(key: str):
        bstack1l1lll1ll1l_opy_ = bstack1ll1l111ll1_opy_.bstack11ll1111lll_opy_(key)
        bstack1ll1l111ll1_opy_.mark(bstack1l1lll1ll1l_opy_+bstack11111l_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥῐ"))
        return bstack1l1lll1ll1l_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1llllll111l1_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠦࡊࡸࡲࡰࡴ࠽ࠤࢀࢃࠢῑ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1ll1l111ll1_opy_.mark(end)
            bstack1ll1l111ll1_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷ࠿ࠦࡻࡾࠤῒ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1llllll111l1_opy_ or end not in bstack1llllll111l1_opy_:
                logger.debug(bstack11111l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡷࡥࡷࡺࠠ࡬ࡧࡼࠤࡼ࡯ࡴࡩࠢࡹࡥࡱࡻࡥࠡࡽࢀࠤࡴࡸࠠࡦࡰࡧࠤࡰ࡫ࡹࠡࡹ࡬ࡸ࡭ࠦࡶࡢ࡮ࡸࡩࠥࢁࡽࠣΐ").format(start,end))
                return
            duration: float = bstack1llllll111l1_opy_[end] - bstack1llllll111l1_opy_[start]
            bstack1llllll11111_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡉࡔࡡࡕ࡙ࡓࡔࡉࡏࡉࠥ῔"), bstack11111l_opy_ (u"ࠣࡨࡤࡰࡸ࡫ࠢ῕")).lower() == bstack11111l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢῖ")
            bstack1llllll11ll1_opy_: bstack1lllll1lll1l_opy_ = bstack1lllll1lll1l_opy_(duration, label, bstack1llllll111l1_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack11111l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠥῗ"), 0), command, test_name, hook_type, bstack1llllll11111_opy_)
            del bstack1llllll111l1_opy_[start]
            del bstack1llllll111l1_opy_[end]
            bstack1ll1l111ll1_opy_.bstack1lllll1lllll_opy_(bstack1llllll11ll1_opy_)
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡰࡩࡦࡹࡵࡳ࡫ࡱ࡫ࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵ࠽ࠤࢀࢃࠢῘ").format(e))
    @staticmethod
    def bstack1lllll1lllll_opy_(bstack1llllll11ll1_opy_):
        os.makedirs(os.path.dirname(bstack1l1l11l1l1_opy_)) if not os.path.exists(os.path.dirname(bstack1l1l11l1l1_opy_)) else None
        bstack1ll1l111ll1_opy_.bstack1lllll1llll1_opy_()
        try:
            with lock:
                with open(bstack1l1l11l1l1_opy_, bstack11111l_opy_ (u"ࠧࡸࠫࠣῙ"), encoding=bstack11111l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧῚ")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1llllll11ll1_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack1llllll11l1l_opy_:
            logger.debug(bstack11111l_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤࠡࡽࢀࠦΊ").format(bstack1llllll11l1l_opy_))
            with lock:
                with open(bstack1l1l11l1l1_opy_, bstack11111l_opy_ (u"ࠣࡹࠥ῜"), encoding=bstack11111l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣ῝")) as file:
                    data = [bstack1llllll11ll1_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵࠣࡥࡵࡶࡥ࡯ࡦࠣࡿࢂࠨ῞").format(str(e)))
        finally:
            if os.path.exists(bstack1l1l11l1l1_opy_+bstack11111l_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ῟")):
                os.remove(bstack1l1l11l1l1_opy_+bstack11111l_opy_ (u"ࠧ࠴࡬ࡰࡥ࡮ࠦῠ"))
    @staticmethod
    def bstack1lllll1llll1_opy_():
        attempt = 0
        while (attempt < bstack1llllll11l11_opy_):
            attempt += 1
            if os.path.exists(bstack1l1l11l1l1_opy_+bstack11111l_opy_ (u"ࠨ࠮࡭ࡱࡦ࡯ࠧῡ")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll1111lll_opy_(label: str) -> str:
        try:
            return bstack11111l_opy_ (u"ࠢࡼࡿ࠽ࡿࢂࠨῢ").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠣࡇࡵࡶࡴࡸ࠺ࠡࡽࢀࠦΰ").format(e))