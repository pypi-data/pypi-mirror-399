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
import threading
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111l1ll1l1_opy_ import bstack111ll11l11_opy_, bstack111ll1l11l_opy_
from bstack_utils.bstack111l1ll111_opy_ import bstack11l11ll11l_opy_
from bstack_utils.helper import bstack11l1l111l_opy_, bstack111l1l11_opy_, Result
from bstack_utils.bstack111l1l1l11_opy_ import bstack11l1ll1l1l_opy_
from bstack_utils.capture import bstack111l1l1lll_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack111lllll1_opy_:
    def __init__(self):
        self.bstack111l1lllll_opy_ = bstack111l1l1lll_opy_(self.bstack111l1ll1ll_opy_)
        self.tests = {}
    @staticmethod
    def bstack111l1ll1ll_opy_(log):
        if not (log[bstack11111l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩགྷ")] and log[bstack11111l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪང")].strip()):
            return
        active = bstack11l11ll11l_opy_.bstack111ll1l1ll_opy_()
        log = {
            bstack11111l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩཅ"): log[bstack11111l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪཆ")],
            bstack11111l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨཇ"): bstack111l1l11_opy_(),
            bstack11111l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ཈"): log[bstack11111l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨཉ")],
        }
        if active:
            if active[bstack11111l_opy_ (u"ࠨࡶࡼࡴࡪ࠭ཊ")] == bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱࠧཋ"):
                log[bstack11111l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪཌ")] = active[bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫཌྷ")]
            elif active[bstack11111l_opy_ (u"ࠬࡺࡹࡱࡧࠪཎ")] == bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࠫཏ"):
                log[bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧཐ")] = active[bstack11111l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨད")]
        bstack11l1ll1l1l_opy_.bstack1l111111l_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111l1lllll_opy_.start()
        driver = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨདྷ"), None)
        bstack111l1ll1l1_opy_ = bstack111ll1l11l_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack111l1l11_opy_(),
            file_path=attrs.feature.filename,
            result=bstack11111l_opy_ (u"ࠥࡴࡪࡴࡤࡪࡰࡪࠦན"),
            framework=bstack11111l_opy_ (u"ࠫࡇ࡫ࡨࡢࡸࡨࠫཔ"),
            scope=[attrs.feature.name],
            bstack111l1lll1l_opy_=bstack11l1ll1l1l_opy_.bstack111l1l1l1l_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨཕ")] = bstack111l1ll1l1_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack11l1ll1l1l_opy_.bstack111l1ll11l_opy_(bstack11111l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧབ"), bstack111l1ll1l1_opy_)
    def end_test(self, attrs):
        bstack111ll1ll11_opy_ = {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧབྷ"): attrs.feature.name,
            bstack11111l_opy_ (u"ࠣࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳࠨམ"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111l1ll1l1_opy_ = self.tests[current_test_uuid][bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬཙ")]
        meta = {
            bstack11111l_opy_ (u"ࠥࡪࡪࡧࡴࡶࡴࡨࠦཚ"): bstack111ll1ll11_opy_,
            bstack11111l_opy_ (u"ࠦࡸࡺࡥࡱࡵࠥཛ"): bstack111l1ll1l1_opy_.meta.get(bstack11111l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫཛྷ"), []),
            bstack11111l_opy_ (u"ࠨࡳࡤࡧࡱࡥࡷ࡯࡯ࠣཝ"): {
                bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧཞ"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111l1ll1l1_opy_.bstack111ll11ll1_opy_(meta)
        bstack111l1ll1l1_opy_.bstack111ll1l111_opy_(bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸ࠭ཟ"), []))
        bstack111ll11l1l_opy_, exception = self._111ll111ll_opy_(attrs)
        bstack111l1llll1_opy_ = Result(result=attrs.status.name, exception=exception, bstack111ll1l1l1_opy_=[bstack111ll11l1l_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬའ")].stop(time=bstack111l1l11_opy_(), duration=int(attrs.duration)*1000, result=bstack111l1llll1_opy_)
        bstack11l1ll1l1l_opy_.bstack111l1ll11l_opy_(bstack11111l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬཡ"), self.tests[threading.current_thread().current_test_uuid][bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧར")])
    def bstack1llll1l111_opy_(self, attrs):
        bstack111l1lll11_opy_ = {
            bstack11111l_opy_ (u"ࠬ࡯ࡤࠨལ"): uuid4().__str__(),
            bstack11111l_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧཤ"): attrs.keyword,
            bstack11111l_opy_ (u"ࠧࡴࡶࡨࡴࡤࡧࡲࡨࡷࡰࡩࡳࡺࠧཥ"): [],
            bstack11111l_opy_ (u"ࠨࡶࡨࡼࡹ࠭ས"): attrs.name,
            bstack11111l_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ཧ"): bstack111l1l11_opy_(),
            bstack11111l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪཨ"): bstack11111l_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬཀྵ"),
            bstack11111l_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪཪ"): bstack11111l_opy_ (u"࠭ࠧཫ")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪཬ")].add_step(bstack111l1lll11_opy_)
        threading.current_thread().current_step_uuid = bstack111l1lll11_opy_[bstack11111l_opy_ (u"ࠨ࡫ࡧࠫ཭")]
    def bstack11ll111ll_opy_(self, attrs):
        current_test_id = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭཮"), None)
        current_step_uuid = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡸࡺࡥࡱࡡࡸࡹ࡮ࡪࠧ཯"), None)
        bstack111ll11l1l_opy_, exception = self._111ll111ll_opy_(attrs)
        bstack111l1llll1_opy_ = Result(result=attrs.status.name, exception=exception, bstack111ll1l1l1_opy_=[bstack111ll11l1l_opy_])
        self.tests[current_test_id][bstack11111l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ཰")].bstack111ll11111_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack111l1llll1_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack1lll1111l1_opy_(self, name, attrs):
        try:
            bstack111l1l1ll1_opy_ = uuid4().__str__()
            self.tests[bstack111l1l1ll1_opy_] = {}
            self.bstack111l1lllll_opy_.start()
            scopes = []
            driver = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵཱࠫ"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack11111l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶིࠫ")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111l1l1ll1_opy_)
            if name in [bstack11111l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ཱིࠦ"), bstack11111l_opy_ (u"ࠣࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ུࠦ")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack11111l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧཱུࠥ"), bstack11111l_opy_ (u"ࠥࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠥྲྀ")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack11111l_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬཷ")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack111ll11l11_opy_(
                name=name,
                uuid=bstack111l1l1ll1_opy_,
                started_at=bstack111l1l11_opy_(),
                file_path=file_path,
                framework=bstack11111l_opy_ (u"ࠧࡈࡥࡩࡣࡹࡩࠧླྀ"),
                bstack111l1lll1l_opy_=bstack11l1ll1l1l_opy_.bstack111l1l1l1l_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack11111l_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢཹ"),
                hook_type=name
            )
            self.tests[bstack111l1l1ll1_opy_][bstack11111l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡪࡡࡵࡣེࠥ")] = hook_data
            current_test_id = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠣࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨཻࠧ"), None)
            if current_test_id:
                hook_data.bstack111ll1111l_opy_(current_test_id)
            if name == bstack11111l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨོ"):
                threading.current_thread().before_all_hook_uuid = bstack111l1l1ll1_opy_
            threading.current_thread().current_hook_uuid = bstack111l1l1ll1_opy_
            bstack11l1ll1l1l_opy_.bstack111l1ll11l_opy_(bstack11111l_opy_ (u"ࠥࡌࡴࡵ࡫ࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧཽࠦ"), hook_data)
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡳࡨࡩࡵࡳࡴࡨࡨࠥ࡯࡮ࠡࡵࡷࡥࡷࡺࠠࡩࡱࡲ࡯ࠥ࡫ࡶࡦࡰࡷࡷ࠱ࠦࡨࡰࡱ࡮ࠤࡳࡧ࡭ࡦ࠼ࠣࠩࡸ࠲ࠠࡦࡴࡵࡳࡷࡀࠠࠦࡵࠥཾ"), name, e)
    def bstack11ll1111l1_opy_(self, attrs):
        bstack111ll111l1_opy_ = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩཿ"), None)
        hook_data = self.tests[bstack111ll111l1_opy_][bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢྀࠩ")]
        status = bstack11111l_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪཱྀࠢ")
        exception = None
        bstack111ll11l1l_opy_ = None
        if hook_data.name == bstack11111l_opy_ (u"ࠣࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ࠦྂ"):
            self.bstack111l1lllll_opy_.reset()
            bstack111ll11lll_opy_ = self.tests[bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩྃ"), None)][bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ྄࠭")].result.result
            if bstack111ll11lll_opy_ == bstack11111l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ྅"):
                if attrs.hook_failures == 1:
                    status = bstack11111l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ྆")
                elif attrs.hook_failures == 2:
                    status = bstack11111l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ྇")
            elif attrs.aborted:
                status = bstack11111l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢྈ")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack11111l_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠬྉ") and attrs.hook_failures == 1:
                status = bstack11111l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤྊ")
            elif hasattr(attrs, bstack11111l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡡࡰࡩࡸࡹࡡࡨࡧࠪྋ")) and attrs.error_message:
                status = bstack11111l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦྌ")
            bstack111ll11l1l_opy_, exception = self._111ll111ll_opy_(attrs)
        bstack111l1llll1_opy_ = Result(result=status, exception=exception, bstack111ll1l1l1_opy_=[bstack111ll11l1l_opy_])
        hook_data.stop(time=bstack111l1l11_opy_(), duration=0, result=bstack111l1llll1_opy_)
        bstack11l1ll1l1l_opy_.bstack111l1ll11l_opy_(bstack11111l_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧྍ"), self.tests[bstack111ll111l1_opy_][bstack11111l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩྎ")])
        threading.current_thread().current_hook_uuid = None
    def _111ll111ll_opy_(self, attrs):
        try:
            import traceback
            bstack1llllll11l_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111ll11l1l_opy_ = bstack1llllll11l_opy_[-1] if bstack1llllll11l_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack11111l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦ࡯ࡤࡥࡸࡶࡷ࡫ࡤࠡࡹ࡫࡭ࡱ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡥࡸࡷࡹࡵ࡭ࠡࡶࡵࡥࡨ࡫ࡢࡢࡥ࡮ࠦྏ"))
            bstack111ll11l1l_opy_ = None
            exception = None
        return bstack111ll11l1l_opy_, exception