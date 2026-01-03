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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
logger = get_logger(__name__)
bstack1lllll1ll1ll_opy_: Dict[str, float] = {}
bstack1lllll1llll1_opy_: List = []
bstack1lllll1lll11_opy_ = 5
bstack111lllll11_opy_ = os.path.join(os.getcwd(), bstack1l1l_opy_ (u"ࠬࡲ࡯ࡨࠩῒ"), bstack1l1l_opy_ (u"࠭࡫ࡦࡻ࠰ࡱࡪࡺࡲࡪࡥࡶ࠲࡯ࡹ࡯࡯ࠩΐ"))
logging.getLogger(bstack1l1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠩ῔")).setLevel(logging.WARNING)
lock = FileLock(bstack111lllll11_opy_+bstack1l1l_opy_ (u"ࠣ࠰࡯ࡳࡨࡱࠢ῕"))
class bstack1llllll1111l_opy_:
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
    def __init__(self, duration: float, name: str, start_time: float, bstack1lllll1lll1l_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1lllll1lll1l_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack1l1l_opy_ (u"ࠤࡰࡩࡦࡹࡵࡳࡧࠥῖ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1ll1l1ll111_opy_:
    global bstack1lllll1ll1ll_opy_
    @staticmethod
    def bstack1ll11l1llll_opy_(key: str):
        bstack1ll11l111l1_opy_ = bstack1ll1l1ll111_opy_.bstack11l1lllllll_opy_(key)
        bstack1ll1l1ll111_opy_.mark(bstack1ll11l111l1_opy_+bstack1l1l_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥῗ"))
        return bstack1ll11l111l1_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1lllll1ll1ll_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴ࠽ࠤࢀࢃࠢῘ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1ll1l1ll111_opy_.mark(end)
            bstack1ll1l1ll111_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷ࠿ࠦࡻࡾࠤῙ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1lllll1ll1ll_opy_ or end not in bstack1lllll1ll1ll_opy_:
                logger.debug(bstack1l1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡷࡥࡷࡺࠠ࡬ࡧࡼࠤࡼ࡯ࡴࡩࠢࡹࡥࡱࡻࡥࠡࡽࢀࠤࡴࡸࠠࡦࡰࡧࠤࡰ࡫ࡹࠡࡹ࡬ࡸ࡭ࠦࡶࡢ࡮ࡸࡩࠥࢁࡽࠣῚ").format(start,end))
                return
            duration: float = bstack1lllll1ll1ll_opy_[end] - bstack1lllll1ll1ll_opy_[start]
            bstack1llllll111ll_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡉࡔࡡࡕ࡙ࡓࡔࡉࡏࡉࠥΊ"), bstack1l1l_opy_ (u"ࠣࡨࡤࡰࡸ࡫ࠢ῜")).lower() == bstack1l1l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ῝")
            bstack1llllll11111_opy_: bstack1llllll1111l_opy_ = bstack1llllll1111l_opy_(duration, label, bstack1lllll1ll1ll_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠥ῞"), 0), command, test_name, hook_type, bstack1llllll111ll_opy_)
            del bstack1lllll1ll1ll_opy_[start]
            del bstack1lllll1ll1ll_opy_[end]
            bstack1ll1l1ll111_opy_.bstack1lllll1lllll_opy_(bstack1llllll11111_opy_)
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡰࡩࡦࡹࡵࡳ࡫ࡱ࡫ࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵ࠽ࠤࢀࢃࠢ῟").format(e))
    @staticmethod
    def bstack1lllll1lllll_opy_(bstack1llllll11111_opy_):
        os.makedirs(os.path.dirname(bstack111lllll11_opy_)) if not os.path.exists(os.path.dirname(bstack111lllll11_opy_)) else None
        bstack1ll1l1ll111_opy_.bstack1llllll11l11_opy_()
        try:
            with lock:
                with open(bstack111lllll11_opy_, bstack1l1l_opy_ (u"ࠧࡸࠫࠣῠ"), encoding=bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧῡ")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1llllll11111_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack1llllll111l1_opy_:
            logger.debug(bstack1l1l_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤࠡࡽࢀࠦῢ").format(bstack1llllll111l1_opy_))
            with lock:
                with open(bstack111lllll11_opy_, bstack1l1l_opy_ (u"ࠣࡹࠥΰ"), encoding=bstack1l1l_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣῤ")) as file:
                    data = [bstack1llllll11111_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵࠣࡥࡵࡶࡥ࡯ࡦࠣࡿࢂࠨῥ").format(str(e)))
        finally:
            if os.path.exists(bstack111lllll11_opy_+bstack1l1l_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥῦ")):
                os.remove(bstack111lllll11_opy_+bstack1l1l_opy_ (u"ࠧ࠴࡬ࡰࡥ࡮ࠦῧ"))
    @staticmethod
    def bstack1llllll11l11_opy_():
        attempt = 0
        while (attempt < bstack1lllll1lll11_opy_):
            attempt += 1
            if os.path.exists(bstack111lllll11_opy_+bstack1l1l_opy_ (u"ࠨ࠮࡭ࡱࡦ࡯ࠧῨ")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11l1lllllll_opy_(label: str) -> str:
        try:
            return bstack1l1l_opy_ (u"ࠢࡼࡿ࠽ࡿࢂࠨῩ").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸ࠺ࠡࡽࢀࠦῪ").format(e))