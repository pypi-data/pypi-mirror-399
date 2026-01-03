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
import os
import threading
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack111l11ll1l_opy_ import RobotHandler
from bstack_utils.capture import bstack111ll11111_opy_
from bstack_utils.bstack111l1lll1l_opy_ import bstack1111ll1l11_opy_, bstack111ll11lll_opy_, bstack111l1ll1l1_opy_
from bstack_utils.bstack111ll11l11_opy_ import bstack1l1ll11111_opy_
from bstack_utils.bstack111ll11l1l_opy_ import bstack11l1llllll_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack11llll11ll_opy_, bstack1111lllll_opy_, Result, \
    error_handler, bstack1111llll11_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    _lock = threading.Lock()
    store = {
        bstack1l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬྐ"): [],
        bstack1l1l_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡡ࡫ࡳࡴࡱࡳࠨྑ"): [],
        bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹࠧྒ"): []
    }
    bstack1111ll11ll_opy_ = []
    bstack1111ll11l1_opy_ = []
    @staticmethod
    def bstack111l1llll1_opy_(log):
        if not ((isinstance(log[bstack1l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྒྷ")], list) or (isinstance(log[bstack1l1l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ྔ")], dict)) and len(log[bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧྕ")])>0) or (isinstance(log[bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨྖ")], str) and log[bstack1l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩྗ")].strip())):
            return
        active = bstack1l1ll11111_opy_.bstack111ll111l1_opy_()
        log = {
            bstack1l1l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ྘"): log[bstack1l1l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩྙ")],
            bstack1l1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧྚ"): bstack1111llll11_opy_().isoformat() + bstack1l1l_opy_ (u"ࠬࡠࠧྛ"),
            bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧྜ"): log[bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨྜྷ")],
        }
        if active:
            if active[bstack1l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭ྞ")] == bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱࠧྟ"):
                log[bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪྠ")] = active[bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫྡ")]
            elif active[bstack1l1l_opy_ (u"ࠬࡺࡹࡱࡧࠪྡྷ")] == bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࠫྣ"):
                log[bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧྤ")] = active[bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨྥ")]
        bstack11l1llllll_opy_.bstack1llll11lll_opy_([log])
    def __init__(self):
        self.messages = bstack1111l1l1l1_opy_()
        self._1111ll111l_opy_ = None
        self._1111l1ll11_opy_ = None
        self._111l1111ll_opy_ = OrderedDict()
        self.bstack111ll1ll11_opy_ = bstack111ll11111_opy_(self.bstack111l1llll1_opy_)
    @error_handler(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack1111l11ll1_opy_()
        if not self._111l1111ll_opy_.get(attrs.get(bstack1l1l_opy_ (u"ࠩ࡬ࡨࠬྦ")), None):
            self._111l1111ll_opy_[attrs.get(bstack1l1l_opy_ (u"ࠪ࡭ࡩ࠭ྦྷ"))] = {}
        bstack111l11111l_opy_ = bstack111l1ll1l1_opy_(
                bstack1111l1llll_opy_=attrs.get(bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧྨ")),
                name=name,
                started_at=bstack1111lllll_opy_(),
                file_path=os.path.relpath(attrs[bstack1l1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬྩ")], start=os.getcwd()) if attrs.get(bstack1l1l_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ྪ")) != bstack1l1l_opy_ (u"ࠧࠨྫ") else bstack1l1l_opy_ (u"ࠨࠩྫྷ"),
                framework=bstack1l1l_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨྭ")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack1l1l_opy_ (u"ࠪ࡭ࡩ࠭ྮ"), None)
        self._111l1111ll_opy_[attrs.get(bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧྯ"))][bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨྰ")] = bstack111l11111l_opy_
    @error_handler(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack1111llllll_opy_()
        self._111l1l111l_opy_(messages)
        with self._lock:
            for bstack1111lll11l_opy_ in self.bstack1111ll11ll_opy_:
                bstack1111lll11l_opy_[bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨྱ")][bstack1l1l_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭ྲ")].extend(self.store[bstack1l1l_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬ࡠࡪࡲࡳࡰࡹࠧླ")])
                bstack11l1llllll_opy_.bstack1lll1111_opy_(bstack1111lll11l_opy_)
            self.bstack1111ll11ll_opy_ = []
            self.store[bstack1l1l_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡡ࡫ࡳࡴࡱࡳࠨྴ")] = []
    @error_handler(class_method=True)
    def start_test(self, name, attrs):
        self.bstack111ll1ll11_opy_.start()
        if not self._111l1111ll_opy_.get(attrs.get(bstack1l1l_opy_ (u"ࠪ࡭ࡩ࠭ྵ")), None):
            self._111l1111ll_opy_[attrs.get(bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧྶ"))] = {}
        driver = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫྷ"), None)
        bstack111l1lll1l_opy_ = bstack111l1ll1l1_opy_(
            bstack1111l1llll_opy_=attrs.get(bstack1l1l_opy_ (u"࠭ࡩࡥࠩྸ")),
            name=name,
            started_at=bstack1111lllll_opy_(),
            file_path=os.path.relpath(attrs[bstack1l1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧྐྵ")], start=os.getcwd()),
            scope=RobotHandler.bstack1111llll1l_opy_(attrs.get(bstack1l1l_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨྺ"), None)),
            framework=bstack1l1l_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨྻ"),
            tags=attrs[bstack1l1l_opy_ (u"ࠪࡸࡦ࡭ࡳࠨྼ")],
            hooks=self.store[bstack1l1l_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪ྽")],
            bstack111ll1l1l1_opy_=bstack11l1llllll_opy_.bstack111l1l1l11_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack1l1l_opy_ (u"ࠧࢁࡽࠡ࡞ࡱࠤࢀࢃࠢ྾").format(bstack1l1l_opy_ (u"ࠨࠠࠣ྿").join(attrs[bstack1l1l_opy_ (u"ࠧࡵࡣࡪࡷࠬ࿀")]), name) if attrs[bstack1l1l_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭࿁")] else name
        )
        self._111l1111ll_opy_[attrs.get(bstack1l1l_opy_ (u"ࠩ࡬ࡨࠬ࿂"))][bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭࿃")] = bstack111l1lll1l_opy_
        threading.current_thread().current_test_uuid = bstack111l1lll1l_opy_.bstack111l111l1l_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧ࿄"), None)
        self.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭࿅"), bstack111l1lll1l_opy_)
    @error_handler(class_method=True)
    def end_test(self, name, attrs):
        self.bstack111ll1ll11_opy_.reset()
        bstack1111ll1l1l_opy_ = bstack1111l1l11l_opy_.get(attrs.get(bstack1l1l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࿆࠭")), bstack1l1l_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨ࿇"))
        self._111l1111ll_opy_[attrs.get(bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫ࿈"))][bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ࿉")].stop(time=bstack1111lllll_opy_(), duration=int(attrs.get(bstack1l1l_opy_ (u"ࠪࡩࡱࡧࡰࡴࡧࡧࡸ࡮ࡳࡥࠨ࿊"), bstack1l1l_opy_ (u"ࠫ࠵࠭࿋"))), result=Result(result=bstack1111ll1l1l_opy_, exception=attrs.get(bstack1l1l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭࿌")), bstack111l1l1lll_opy_=[attrs.get(bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ࿍"))]))
        self.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ࿎"), self._111l1111ll_opy_[attrs.get(bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫ࿏"))][bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ࿐")], True)
        with self._lock:
            self.store[bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹࠧ࿑")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @error_handler(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack1111l11ll1_opy_()
        current_test_id = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡩ࠭࿒"), None)
        bstack1111lllll1_opy_ = current_test_id if bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡪࠧ࿓"), None) else bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡴࡷ࡬ࡸࡪࡥࡩࡥࠩ࿔"), None)
        if attrs.get(bstack1l1l_opy_ (u"ࠧࡵࡻࡳࡩࠬ࿕"), bstack1l1l_opy_ (u"ࠨࠩ࿖")).lower() in [bstack1l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ࿗"), bstack1l1l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ࿘")]:
            hook_type = bstack111l11l11l_opy_(attrs.get(bstack1l1l_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿙")), bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ࿚"), None))
            hook_name = bstack1l1l_opy_ (u"࠭ࡻࡾࠩ࿛").format(attrs.get(bstack1l1l_opy_ (u"ࠧ࡬ࡹࡱࡥࡲ࡫ࠧ࿜"), bstack1l1l_opy_ (u"ࠨࠩ࿝")))
            if hook_type in [bstack1l1l_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡄࡐࡑ࠭࿞"), bstack1l1l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭࿟")]:
                hook_name = bstack1l1l_opy_ (u"ࠫࡠࢁࡽ࡞ࠢࡾࢁࠬ࿠").format(bstack111l11l111_opy_.get(hook_type), attrs.get(bstack1l1l_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬ࿡"), bstack1l1l_opy_ (u"࠭ࠧ࿢")))
            bstack1111l1lll1_opy_ = bstack111ll11lll_opy_(
                bstack1111l1llll_opy_=bstack1111lllll1_opy_ + bstack1l1l_opy_ (u"ࠧ࠮ࠩ࿣") + attrs.get(bstack1l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭࿤"), bstack1l1l_opy_ (u"ࠩࠪ࿥")).lower(),
                name=hook_name,
                started_at=bstack1111lllll_opy_(),
                file_path=os.path.relpath(attrs.get(bstack1l1l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ࿦")), start=os.getcwd()),
                framework=bstack1l1l_opy_ (u"ࠫࡗࡵࡢࡰࡶࠪ࿧"),
                tags=attrs[bstack1l1l_opy_ (u"ࠬࡺࡡࡨࡵࠪ࿨")],
                scope=RobotHandler.bstack1111llll1l_opy_(attrs.get(bstack1l1l_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭࿩"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack1111l1lll1_opy_.bstack111l111l1l_opy_()
            threading.current_thread().current_hook_id = bstack1111lllll1_opy_ + bstack1l1l_opy_ (u"ࠧ࠮ࠩ࿪") + attrs.get(bstack1l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭࿫"), bstack1l1l_opy_ (u"ࠩࠪ࿬")).lower()
            with self._lock:
                self.store[bstack1l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ࿭")] = [bstack1111l1lll1_opy_.bstack111l111l1l_opy_()]
                if bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ࿮"), None):
                    self.store[bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࠩ࿯")].append(bstack1111l1lll1_opy_.bstack111l111l1l_opy_())
                else:
                    self.store[bstack1l1l_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱࡥࡨࡰࡱ࡮ࡷࠬ࿰")].append(bstack1111l1lll1_opy_.bstack111l111l1l_opy_())
            if bstack1111lllll1_opy_:
                self._111l1111ll_opy_[bstack1111lllll1_opy_ + bstack1l1l_opy_ (u"ࠧ࠮ࠩ࿱") + attrs.get(bstack1l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭࿲"), bstack1l1l_opy_ (u"ࠩࠪ࿳")).lower()] = { bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭࿴"): bstack1111l1lll1_opy_ }
            bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ࿵"), bstack1111l1lll1_opy_)
        else:
            bstack111l1l1ll1_opy_ = {
                bstack1l1l_opy_ (u"ࠬ࡯ࡤࠨ࿶"): uuid4().__str__(),
                bstack1l1l_opy_ (u"࠭ࡴࡦࡺࡷࠫ࿷"): bstack1l1l_opy_ (u"ࠧࡼࡿࠣࡿࢂ࠭࿸").format(attrs.get(bstack1l1l_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨ࿹")), attrs.get(bstack1l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ࿺"), bstack1l1l_opy_ (u"ࠪࠫ࿻"))) if attrs.get(bstack1l1l_opy_ (u"ࠫࡦࡸࡧࡴࠩ࿼"), []) else attrs.get(bstack1l1l_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬ࿽")),
                bstack1l1l_opy_ (u"࠭ࡳࡵࡧࡳࡣࡦࡸࡧࡶ࡯ࡨࡲࡹ࠭࿾"): attrs.get(bstack1l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬ࿿"), []),
                bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬက"): bstack1111lllll_opy_(),
                bstack1l1l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩခ"): bstack1l1l_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫဂ"),
                bstack1l1l_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩဃ"): attrs.get(bstack1l1l_opy_ (u"ࠬࡪ࡯ࡤࠩင"), bstack1l1l_opy_ (u"࠭ࠧစ"))
            }
            if attrs.get(bstack1l1l_opy_ (u"ࠧ࡭࡫ࡥࡲࡦࡳࡥࠨဆ"), bstack1l1l_opy_ (u"ࠨࠩဇ")) != bstack1l1l_opy_ (u"ࠩࠪဈ"):
                bstack111l1l1ll1_opy_[bstack1l1l_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫဉ")] = attrs.get(bstack1l1l_opy_ (u"ࠫࡱ࡯ࡢ࡯ࡣࡰࡩࠬည"))
            if not self.bstack1111ll11l1_opy_:
                self._111l1111ll_opy_[self._1111lll1l1_opy_()][bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨဋ")].add_step(bstack111l1l1ll1_opy_)
                threading.current_thread().current_step_uuid = bstack111l1l1ll1_opy_[bstack1l1l_opy_ (u"࠭ࡩࡥࠩဌ")]
            self.bstack1111ll11l1_opy_.append(bstack111l1l1ll1_opy_)
    @error_handler(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack1111llllll_opy_()
        self._111l1l111l_opy_(messages)
        current_test_id = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡥࠩဍ"), None)
        bstack1111lllll1_opy_ = current_test_id if current_test_id else bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡶࡹ࡮ࡺࡥࡠ࡫ࡧࠫဎ"), None)
        bstack111l1l11l1_opy_ = bstack1111l1l11l_opy_.get(attrs.get(bstack1l1l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩဏ")), bstack1l1l_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫတ"))
        bstack111l11ll11_opy_ = attrs.get(bstack1l1l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬထ"))
        if bstack111l1l11l1_opy_ != bstack1l1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭ဒ") and not attrs.get(bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧဓ")) and self._1111ll111l_opy_:
            bstack111l11ll11_opy_ = self._1111ll111l_opy_
        bstack111l1lll11_opy_ = Result(result=bstack111l1l11l1_opy_, exception=bstack111l11ll11_opy_, bstack111l1l1lll_opy_=[bstack111l11ll11_opy_])
        if attrs.get(bstack1l1l_opy_ (u"ࠧࡵࡻࡳࡩࠬန"), bstack1l1l_opy_ (u"ࠨࠩပ")).lower() in [bstack1l1l_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨဖ"), bstack1l1l_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬဗ")]:
            bstack1111lllll1_opy_ = current_test_id if current_test_id else bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡹࡵࡪࡶࡨࡣ࡮ࡪࠧဘ"), None)
            if bstack1111lllll1_opy_:
                bstack111l1ll1ll_opy_ = bstack1111lllll1_opy_ + bstack1l1l_opy_ (u"ࠧ࠳ࠢမ") + attrs.get(bstack1l1l_opy_ (u"࠭ࡴࡺࡲࡨࠫယ"), bstack1l1l_opy_ (u"ࠧࠨရ")).lower()
                self._111l1111ll_opy_[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫလ")].stop(time=bstack1111lllll_opy_(), duration=int(attrs.get(bstack1l1l_opy_ (u"ࠩࡨࡰࡦࡶࡳࡦࡦࡷ࡭ࡲ࡫ࠧဝ"), bstack1l1l_opy_ (u"ࠪ࠴ࠬသ"))), result=bstack111l1lll11_opy_)
                bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭ဟ"), self._111l1111ll_opy_[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨဠ")])
        else:
            bstack1111lllll1_opy_ = current_test_id if current_test_id else bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤ࡯ࡤࠨအ"), None)
            if bstack1111lllll1_opy_ and len(self.bstack1111ll11l1_opy_) == 1:
                current_step_uuid = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡵࡷࡩࡵࡥࡵࡶ࡫ࡧࠫဢ"), None)
                self._111l1111ll_opy_[bstack1111lllll1_opy_][bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫဣ")].bstack111ll1111l_opy_(current_step_uuid, duration=int(attrs.get(bstack1l1l_opy_ (u"ࠩࡨࡰࡦࡶࡳࡦࡦࡷ࡭ࡲ࡫ࠧဤ"), bstack1l1l_opy_ (u"ࠪ࠴ࠬဥ"))), result=bstack111l1lll11_opy_)
            else:
                self.bstack1111ll1111_opy_(attrs)
            self.bstack1111ll11l1_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack1l1l_opy_ (u"ࠫ࡭ࡺ࡭࡭ࠩဦ"), bstack1l1l_opy_ (u"ࠬࡴ࡯ࠨဧ")) == bstack1l1l_opy_ (u"࠭ࡹࡦࡵࠪဨ"):
                return
            self.messages.push(message)
            logs = []
            if bstack1l1ll11111_opy_.bstack111ll111l1_opy_():
                logs.append({
                    bstack1l1l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪဩ"): bstack1111lllll_opy_(),
                    bstack1l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩဪ"): message.get(bstack1l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪါ")),
                    bstack1l1l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩာ"): message.get(bstack1l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪိ")),
                    **bstack1l1ll11111_opy_.bstack111ll111l1_opy_()
                })
                if len(logs) > 0:
                    bstack11l1llllll_opy_.bstack1llll11lll_opy_(logs)
        except Exception as err:
            pass
    def close(self):
        bstack11l1llllll_opy_.bstack111l111lll_opy_()
    def bstack1111ll1111_opy_(self, bstack111l1l1111_opy_):
        if not bstack1l1ll11111_opy_.bstack111ll111l1_opy_():
            return
        kwname = bstack1l1l_opy_ (u"ࠬࢁࡽࠡࡽࢀࠫီ").format(bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"࠭࡫ࡸࡰࡤࡱࡪ࠭ု")), bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠧࡢࡴࡪࡷࠬူ"), bstack1l1l_opy_ (u"ࠨࠩေ"))) if bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧဲ"), []) else bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪဳ"))
        error_message = bstack1l1l_opy_ (u"ࠦࡰࡽ࡮ࡢ࡯ࡨ࠾ࠥࡢࠢࡼ࠲ࢀࡠࠧࠦࡼࠡࡵࡷࡥࡹࡻࡳ࠻ࠢ࡟ࠦࢀ࠷ࡽ࡝ࠤࠣࢀࠥ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢ࡟ࠦࢀ࠸ࡽ࡝ࠤࠥဴ").format(kwname, bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬဵ")), str(bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧံ"))))
        bstack111l1111l1_opy_ = bstack1l1l_opy_ (u"ࠢ࡬ࡹࡱࡥࡲ࡫࠺ࠡ࡞ࠥࡿ࠵ࢃ࡜ࠣࠢࡿࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࡢࠢࡼ࠳ࢀࡠࠧࠨ့").format(kwname, bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨး")))
        bstack111l11llll_opy_ = error_message if bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧ္ࠪ")) else bstack111l1111l1_opy_
        bstack111l11l1l1_opy_ = {
            bstack1l1l_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ်࠭"): self.bstack1111ll11l1_opy_[-1].get(bstack1l1l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨျ"), bstack1111lllll_opy_()),
            bstack1l1l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ြ"): bstack111l11llll_opy_,
            bstack1l1l_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬွ"): bstack1l1l_opy_ (u"ࠧࡆࡔࡕࡓࡗ࠭ှ") if bstack111l1l1111_opy_.get(bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨဿ")) == bstack1l1l_opy_ (u"ࠩࡉࡅࡎࡒࠧ၀") else bstack1l1l_opy_ (u"ࠪࡍࡓࡌࡏࠨ၁"),
            **bstack1l1ll11111_opy_.bstack111ll111l1_opy_()
        }
        bstack11l1llllll_opy_.bstack1llll11lll_opy_([bstack111l11l1l1_opy_])
    def _1111lll1l1_opy_(self):
        for bstack1111l1llll_opy_ in reversed(self._111l1111ll_opy_):
            bstack1111l11l1l_opy_ = bstack1111l1llll_opy_
            data = self._111l1111ll_opy_[bstack1111l1llll_opy_][bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ၂")]
            if isinstance(data, bstack111ll11lll_opy_):
                if not bstack1l1l_opy_ (u"ࠬࡋࡁࡄࡊࠪ၃") in data.bstack1111lll111_opy_():
                    return bstack1111l11l1l_opy_
            else:
                return bstack1111l11l1l_opy_
    def _111l1l111l_opy_(self, messages):
        try:
            bstack111l111111_opy_ = BuiltIn().get_variable_value(bstack1l1l_opy_ (u"ࠨࠤࡼࡎࡒࡋࠥࡒࡅࡗࡇࡏࢁࠧ၄")) in (bstack1111l1l1ll_opy_.DEBUG, bstack1111l1l1ll_opy_.TRACE)
            for message, bstack1111lll1ll_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ၅"))
                level = message.get(bstack1l1l_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ၆"))
                if level == bstack1111l1l1ll_opy_.FAIL:
                    self._1111ll111l_opy_ = name or self._1111ll111l_opy_
                    self._1111l1ll11_opy_ = bstack1111lll1ll_opy_.get(bstack1l1l_opy_ (u"ࠤࡰࡩࡸࡹࡡࡨࡧࠥ၇")) if bstack111l111111_opy_ and bstack1111lll1ll_opy_ else self._1111l1ll11_opy_
        except:
            pass
    @classmethod
    def bstack111ll1l1ll_opy_(self, event: str, bstack111l111l11_opy_: bstack1111ll1l11_opy_, bstack1111ll1lll_opy_=False):
        if event == bstack1l1l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ၈"):
            bstack111l111l11_opy_.set(hooks=self.store[bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࠨ၉")])
        if event == bstack1l1l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙࡫ࡪࡲࡳࡩࡩ࠭၊"):
            event = bstack1l1l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ။")
        if bstack1111ll1lll_opy_:
            bstack111l11lll1_opy_ = {
                bstack1l1l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ၌"): event,
                bstack111l111l11_opy_.bstack1111l11lll_opy_(): bstack111l111l11_opy_.bstack1111ll1ll1_opy_(event)
            }
            with self._lock:
                self.bstack1111ll11ll_opy_.append(bstack111l11lll1_opy_)
        else:
            bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(event, bstack111l111l11_opy_)
class bstack1111l1l1l1_opy_:
    def __init__(self):
        self._1111l1ll1l_opy_ = []
    def bstack1111l11ll1_opy_(self):
        self._1111l1ll1l_opy_.append([])
    def bstack1111llllll_opy_(self):
        return self._1111l1ll1l_opy_.pop() if self._1111l1ll1l_opy_ else list()
    def push(self, message):
        self._1111l1ll1l_opy_[-1].append(message) if self._1111l1ll1l_opy_ else self._1111l1ll1l_opy_.append([message])
class bstack1111l1l1ll_opy_:
    FAIL = bstack1l1l_opy_ (u"ࠨࡈࡄࡍࡑ࠭၍")
    ERROR = bstack1l1l_opy_ (u"ࠩࡈࡖࡗࡕࡒࠨ၎")
    WARNING = bstack1l1l_opy_ (u"࡛ࠪࡆࡘࡎࠨ၏")
    bstack111l111ll1_opy_ = bstack1l1l_opy_ (u"ࠫࡎࡔࡆࡐࠩၐ")
    DEBUG = bstack1l1l_opy_ (u"ࠬࡊࡅࡃࡗࡊࠫၑ")
    TRACE = bstack1l1l_opy_ (u"࠭ࡔࡓࡃࡆࡉࠬၒ")
    bstack1111l1l111_opy_ = [FAIL, ERROR]
def bstack111l11l1ll_opy_(bstack111l1l11ll_opy_):
    if not bstack111l1l11ll_opy_:
        return None
    if bstack111l1l11ll_opy_.get(bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪၓ"), None):
        return getattr(bstack111l1l11ll_opy_[bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫၔ")], bstack1l1l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧၕ"), None)
    return bstack111l1l11ll_opy_.get(bstack1l1l_opy_ (u"ࠪࡹࡺ࡯ࡤࠨၖ"), None)
def bstack111l11l11l_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack1l1l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪၗ"), bstack1l1l_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧၘ")]:
        return
    if hook_type.lower() == bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬၙ"):
        if current_test_uuid is None:
            return bstack1l1l_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏࠫၚ")
        else:
            return bstack1l1l_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍ࠭ၛ")
    elif hook_type.lower() == bstack1l1l_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫၜ"):
        if current_test_uuid is None:
            return bstack1l1l_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭ၝ")
        else:
            return bstack1l1l_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨၞ")