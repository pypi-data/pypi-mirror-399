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
import logging
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1lllll1l11l_opy_ import bstack1lllll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1lll1ll_opy_ import bstack1llll1l11ll_opy_, bstack1lllll1l111_opy_
class bstack1lll1ll1111_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack11111l_opy_ (u"ࠥࡘࡪࡹࡴࡉࡱࡲ࡯ࡘࡺࡡࡵࡧ࠱ࡿࢂࠨᘔ").format(self.name)
class bstack1ll1l11ll1l_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack11111l_opy_ (u"࡙ࠦ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡗࡹࡧࡴࡦ࠰ࡾࢁࠧᘕ").format(self.name)
class bstack1lll1ll1ll1_opy_(bstack1llll1l11ll_opy_):
    bstack1l1llll11ll_opy_: List[str]
    bstack11lllll11ll_opy_: Dict[str, str]
    state: bstack1ll1l11ll1l_opy_
    bstack1lll1llll11_opy_: datetime
    bstack1lll1lll1l1_opy_: datetime
    def __init__(
        self,
        context: bstack1lllll1l111_opy_,
        bstack1l1llll11ll_opy_: List[str],
        bstack11lllll11ll_opy_: Dict[str, str],
        state=bstack1ll1l11ll1l_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1l1llll11ll_opy_ = bstack1l1llll11ll_opy_
        self.bstack11lllll11ll_opy_ = bstack11lllll11ll_opy_
        self.state = state
        self.bstack1lll1llll11_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1lll1lll1l1_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llll1l1lll_opy_(self, bstack1llll11ll1l_opy_: bstack1ll1l11ll1l_opy_):
        bstack1llll111111_opy_ = bstack1ll1l11ll1l_opy_(bstack1llll11ll1l_opy_).name
        if not bstack1llll111111_opy_:
            return False
        if bstack1llll11ll1l_opy_ == self.state:
            return False
        self.state = bstack1llll11ll1l_opy_
        self.bstack1lll1lll1l1_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack1l1111ll1l1_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1ll1lllll11_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1l1ll1111ll_opy_: int = None
    bstack1l1l1l1l111_opy_: str = None
    bstack1l1ll11_opy_: str = None
    bstack111llll1_opy_: str = None
    bstack1l1l1ll1ll1_opy_: str = None
    bstack11lllll1111_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll11111l11_opy_ = bstack11111l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠣᘖ")
    bstack11llll1llll_opy_ = bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡮ࡪࠢᘗ")
    bstack1ll111111l1_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡴࡡ࡮ࡧࠥᘘ")
    bstack11llll1l11l_opy_ = bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡣࡵࡧࡴࡩࠤᘙ")
    bstack11llll111l1_opy_ = bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡵࡣࡪࡷࠧᘚ")
    bstack1l11l1ll1l1_opy_ = bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡨࡷࡺࡲࡴࠣᘛ")
    bstack1l1l1l11l1l_opy_ = bstack11111l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡩࡸࡻ࡬ࡵࡡࡤࡸࠧᘜ")
    bstack1l1l1l111ll_opy_ = bstack11111l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠢᘝ")
    bstack1l1l11lll1l_opy_ = bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡣࡪࡴࡤࡦࡦࡢࡥࡹࠨᘞ")
    bstack11llll11lll_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠢᘟ")
    bstack1l1lllllll1_opy_ = bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࠢᘠ")
    bstack1l1l111llll_opy_ = bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠦᘡ")
    bstack11lllll11l1_opy_ = bstack11111l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡥࡲࡨࡪࠨᘢ")
    bstack1l1l1111l11_opy_ = bstack11111l_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡩࡷࡻ࡮ࡠࡰࡤࡱࡪࠨᘣ")
    bstack1ll111ll111_opy_ = bstack11111l_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࠨᘤ")
    bstack1l11ll11lll_opy_ = bstack11111l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫ࡧࡩ࡭ࡷࡵࡩࠧᘥ")
    bstack1l111111ll1_opy_ = bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠦᘦ")
    bstack11llll1l1ll_opy_ = bstack11111l_opy_ (u"ࠣࡶࡨࡷࡹࡥ࡬ࡰࡩࡶࠦᘧ")
    bstack1l111l111l1_opy_ = bstack11111l_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡮ࡧࡷࡥࠧᘨ")
    bstack11lll1l111l_opy_ = bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡵࡦࡳࡵ࡫ࡳࠨᘩ")
    bstack1l111lll11l_opy_ = bstack11111l_opy_ (u"ࠦࡦࡻࡴࡰ࡯ࡤࡸࡪࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟࡯ࡣࡰࡩࠧᘪ")
    bstack1l111l1111l_opy_ = bstack11111l_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣᘫ")
    bstack11llll1l1l1_opy_ = bstack11111l_opy_ (u"ࠨࡥࡷࡧࡱࡸࡤ࡫࡮ࡥࡧࡧࡣࡦࡺࠢᘬ")
    bstack1l1111l111l_opy_ = bstack11111l_opy_ (u"ࠢࡩࡱࡲ࡯ࡤ࡯ࡤࠣᘭ")
    bstack1l1111l11ll_opy_ = bstack11111l_opy_ (u"ࠣࡪࡲࡳࡰࡥࡲࡦࡵࡸࡰࡹࠨᘮ")
    bstack11lll1ll1ll_opy_ = bstack11111l_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟࡭ࡱࡪࡷࠧᘯ")
    bstack1l11111l11l_opy_ = bstack11111l_opy_ (u"ࠥ࡬ࡴࡵ࡫ࡠࡰࡤࡱࡪࠨᘰ")
    bstack1l1111l1lll_opy_ = bstack11111l_opy_ (u"ࠦࡱࡵࡧࡴࠤᘱ")
    bstack1l11111ll1l_opy_ = bstack11111l_opy_ (u"ࠧࡩࡵࡴࡶࡲࡱࡤࡳࡥࡵࡣࡧࡥࡹࡧࠢᘲ")
    bstack1l111111111_opy_ = bstack11111l_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢᘳ")
    bstack1l11111l1ll_opy_ = bstack11111l_opy_ (u"ࠢࡱࡧࡱࡨ࡮ࡴࡧࠣᘴ")
    bstack1l1l1ll11ll_opy_ = bstack11111l_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࠥᘵ")
    bstack1l1l111lll1_opy_ = bstack11111l_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡍࡑࡊࠦᘶ")
    bstack1l1ll11l11l_opy_ = bstack11111l_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᘷ")
    bstack1lll1llllll_opy_: Dict[str, bstack1lll1ll1ll1_opy_] = dict()
    bstack11lll11ll1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1l1llll11ll_opy_: List[str]
    bstack11lllll11ll_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1l1llll11ll_opy_: List[str],
        bstack11lllll11ll_opy_: Dict[str, str],
        bstack1lllll1l11l_opy_: bstack1lllll1l1l1_opy_
    ):
        self.bstack1l1llll11ll_opy_ = bstack1l1llll11ll_opy_
        self.bstack11lllll11ll_opy_ = bstack11lllll11ll_opy_
        self.bstack1lllll1l11l_opy_ = bstack1lllll1l11l_opy_
    def track_event(
        self,
        context: bstack1l1111ll1l1_opy_,
        test_framework_state: bstack1ll1l11ll1l_opy_,
        test_hook_state: bstack1lll1ll1111_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack11111l_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠦࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥ࠾ࡽࢀࠤࡦࡸࡧࡴ࠿ࡾࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁࡽࠣᘸ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack11lll1l1l11_opy_(
        self,
        instance: bstack1lll1ll1ll1_opy_,
        bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_],
        *args,
        **kwargs,
    ):
        bstack1l111l1l1l1_opy_ = TestFramework.bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_)
        if not bstack1l111l1l1l1_opy_ in TestFramework.bstack11lll11ll1l_opy_:
            return
        self.logger.debug(bstack11111l_opy_ (u"ࠧ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࡼࡿࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࡸࠨᘹ").format(len(TestFramework.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_])))
        for callback in TestFramework.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_]:
            try:
                callback(self, instance, bstack1llll1lll1l_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack11111l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠥ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬࠼ࠣࡿࢂࠨᘺ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1l11l11l1_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1l111ll1l_opy_(self, instance, bstack1llll1lll1l_opy_):
        return
    @abc.abstractmethod
    def bstack1l1l1llllll_opy_(self, instance, bstack1llll1lll1l_opy_):
        return
    @staticmethod
    def bstack1lllll11l1l_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1llll1l11ll_opy_.create_context(target)
        instance = TestFramework.bstack1lll1llllll_opy_.get(ctx.id, None)
        if instance and instance.bstack1lll1llll1l_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1ll1111l1_opy_(reverse=True) -> List[bstack1lll1ll1ll1_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1lll1llll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll11111l_opy_(ctx: bstack1lllll1l111_opy_, reverse=True) -> List[bstack1lll1ll1ll1_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1lll1llll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lllll111l1_opy_(instance: bstack1lll1ll1ll1_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llll111ll1_opy_(instance: bstack1lll1ll1ll1_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llll1l1lll_opy_(instance: bstack1lll1ll1ll1_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11111l_opy_ (u"ࠢࡴࡧࡷࡣࡸࡺࡡࡵࡧ࠽ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡾࠢ࡮ࡩࡾࡃࡻࡾࠢࡹࡥࡱࡻࡥ࠾ࡽࢀࠦᘻ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l1111lll11_opy_(instance: bstack1lll1ll1ll1_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack11111l_opy_ (u"ࠣࡵࡨࡸࡤࡹࡴࡢࡶࡨࡣࡪࡴࡴࡳ࡫ࡨࡷ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽࢀࠤࡪࡴࡴࡳ࡫ࡨࡷࡂࢁࡽࠣᘼ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11lll1111ll_opy_(instance: bstack1ll1l11ll1l_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack11111l_opy_ (u"ࠤࡸࡴࡩࡧࡴࡦࡡࡶࡸࡦࡺࡥ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀࢃࠠ࡬ࡧࡼࡁࢀࢃࠠࡷࡣ࡯ࡹࡪࡃࡻࡾࠤᘽ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1lllll11l1l_opy_(target, strict)
        return TestFramework.bstack1llll111ll1_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1lllll11l1l_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack11lll1ll1l1_opy_(instance: bstack1lll1ll1ll1_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l1111ll111_opy_(instance: bstack1lll1ll1ll1_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_]):
        return bstack11111l_opy_ (u"ࠥ࠾ࠧᘾ").join((bstack1ll1l11ll1l_opy_(bstack1llll1lll1l_opy_[0]).name, bstack1lll1ll1111_opy_(bstack1llll1lll1l_opy_[1]).name))
    @staticmethod
    def bstack1l1llllll1l_opy_(bstack1llll1lll1l_opy_: Tuple[bstack1ll1l11ll1l_opy_, bstack1lll1ll1111_opy_], callback: Callable):
        bstack1l111l1l1l1_opy_ = TestFramework.bstack1l111l1l1ll_opy_(bstack1llll1lll1l_opy_)
        TestFramework.logger.debug(bstack11111l_opy_ (u"ࠦࡸ࡫ࡴࡠࡪࡲࡳࡰࡥࡣࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢ࡫ࡳࡴࡱ࡟ࡳࡧࡪ࡭ࡸࡺࡲࡺࡡ࡮ࡩࡾࡃࡻࡾࠤᘿ").format(bstack1l111l1l1l1_opy_))
        if not bstack1l111l1l1l1_opy_ in TestFramework.bstack11lll11ll1l_opy_:
            TestFramework.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_] = []
        TestFramework.bstack11lll11ll1l_opy_[bstack1l111l1l1l1_opy_].append(callback)
    @staticmethod
    def bstack1l1l1l1lll1_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡷ࡭ࡳࡹࠢᙀ"):
            return klass.__qualname__
        return module + bstack11111l_opy_ (u"ࠨ࠮ࠣᙁ") + klass.__qualname__
    @staticmethod
    def bstack1l1l111ll11_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}