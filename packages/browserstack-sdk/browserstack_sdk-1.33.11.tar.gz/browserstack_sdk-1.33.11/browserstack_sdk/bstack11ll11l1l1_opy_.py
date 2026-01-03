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
import threading
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111l1lll1l_opy_ import bstack111ll11lll_opy_, bstack111l1ll1l1_opy_
from bstack_utils.bstack111ll11l11_opy_ import bstack1l1ll11111_opy_
from bstack_utils.helper import bstack11llll11ll_opy_, bstack1111lllll_opy_, Result
from bstack_utils.bstack111ll11l1l_opy_ import bstack11l1llllll_opy_
from bstack_utils.capture import bstack111ll11111_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack11ll11l1l1_opy_:
    def __init__(self):
        self.bstack111ll1ll11_opy_ = bstack111ll11111_opy_(self.bstack111l1llll1_opy_)
        self.tests = {}
    @staticmethod
    def bstack111l1llll1_opy_(log):
        if not (log[bstack1l1l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩགྷ")] and log[bstack1l1l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪང")].strip()):
            return
        active = bstack1l1ll11111_opy_.bstack111ll111l1_opy_()
        log = {
            bstack1l1l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩཅ"): log[bstack1l1l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪཆ")],
            bstack1l1l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨཇ"): bstack1111lllll_opy_(),
            bstack1l1l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ཈"): log[bstack1l1l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨཉ")],
        }
        if active:
            if active[bstack1l1l_opy_ (u"ࠨࡶࡼࡴࡪ࠭ཊ")] == bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱࠧཋ"):
                log[bstack1l1l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪཌ")] = active[bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫཌྷ")]
            elif active[bstack1l1l_opy_ (u"ࠬࡺࡹࡱࡧࠪཎ")] == bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࠫཏ"):
                log[bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧཐ")] = active[bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨད")]
        bstack11l1llllll_opy_.bstack1llll11lll_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111ll1ll11_opy_.start()
        driver = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨདྷ"), None)
        bstack111l1lll1l_opy_ = bstack111l1ll1l1_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack1111lllll_opy_(),
            file_path=attrs.feature.filename,
            result=bstack1l1l_opy_ (u"ࠥࡴࡪࡴࡤࡪࡰࡪࠦན"),
            framework=bstack1l1l_opy_ (u"ࠫࡇ࡫ࡨࡢࡸࡨࠫཔ"),
            scope=[attrs.feature.name],
            bstack111ll1l1l1_opy_=bstack11l1llllll_opy_.bstack111l1l1l11_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨཕ")] = bstack111l1lll1l_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧབ"), bstack111l1lll1l_opy_)
    def end_test(self, attrs):
        bstack111ll1l11l_opy_ = {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧབྷ"): attrs.feature.name,
            bstack1l1l_opy_ (u"ࠣࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳࠨམ"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111l1lll1l_opy_ = self.tests[current_test_uuid][bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬཙ")]
        meta = {
            bstack1l1l_opy_ (u"ࠥࡪࡪࡧࡴࡶࡴࡨࠦཚ"): bstack111ll1l11l_opy_,
            bstack1l1l_opy_ (u"ࠦࡸࡺࡥࡱࡵࠥཛ"): bstack111l1lll1l_opy_.meta.get(bstack1l1l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫཛྷ"), []),
            bstack1l1l_opy_ (u"ࠨࡳࡤࡧࡱࡥࡷ࡯࡯ࠣཝ"): {
                bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧཞ"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111l1lll1l_opy_.bstack111ll111ll_opy_(meta)
        bstack111l1lll1l_opy_.bstack111ll11ll1_opy_(bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸ࠭ཟ"), []))
        bstack111l1lllll_opy_, exception = self._111l1ll111_opy_(attrs)
        bstack111l1lll11_opy_ = Result(result=attrs.status.name, exception=exception, bstack111l1l1lll_opy_=[bstack111l1lllll_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬའ")].stop(time=bstack1111lllll_opy_(), duration=int(attrs.duration)*1000, result=bstack111l1lll11_opy_)
        bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬཡ"), self.tests[threading.current_thread().current_test_uuid][bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧར")])
    def bstack1l11ll11l_opy_(self, attrs):
        bstack111l1l1ll1_opy_ = {
            bstack1l1l_opy_ (u"ࠬ࡯ࡤࠨལ"): uuid4().__str__(),
            bstack1l1l_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧཤ"): attrs.keyword,
            bstack1l1l_opy_ (u"ࠧࡴࡶࡨࡴࡤࡧࡲࡨࡷࡰࡩࡳࡺࠧཥ"): [],
            bstack1l1l_opy_ (u"ࠨࡶࡨࡼࡹ࠭ས"): attrs.name,
            bstack1l1l_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ཧ"): bstack1111lllll_opy_(),
            bstack1l1l_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪཨ"): bstack1l1l_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬཀྵ"),
            bstack1l1l_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪཪ"): bstack1l1l_opy_ (u"࠭ࠧཫ")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪཬ")].add_step(bstack111l1l1ll1_opy_)
        threading.current_thread().current_step_uuid = bstack111l1l1ll1_opy_[bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫ཭")]
    def bstack1llll1ll_opy_(self, attrs):
        current_test_id = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭཮"), None)
        current_step_uuid = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡸࡺࡥࡱࡡࡸࡹ࡮ࡪࠧ཯"), None)
        bstack111l1lllll_opy_, exception = self._111l1ll111_opy_(attrs)
        bstack111l1lll11_opy_ = Result(result=attrs.status.name, exception=exception, bstack111l1l1lll_opy_=[bstack111l1lllll_opy_])
        self.tests[current_test_id][bstack1l1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ཰")].bstack111ll1111l_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack111l1lll11_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack11l1ll1l1l_opy_(self, name, attrs):
        try:
            bstack111l1l1l1l_opy_ = uuid4().__str__()
            self.tests[bstack111l1l1l1l_opy_] = {}
            self.bstack111ll1ll11_opy_.start()
            scopes = []
            driver = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵཱࠫ"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack1l1l_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶིࠫ")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111l1l1l1l_opy_)
            if name in [bstack1l1l_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ཱིࠦ"), bstack1l1l_opy_ (u"ࠣࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ུࠦ")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack1l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧཱུࠥ"), bstack1l1l_opy_ (u"ࠥࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠥྲྀ")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack1l1l_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬཷ")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack111ll11lll_opy_(
                name=name,
                uuid=bstack111l1l1l1l_opy_,
                started_at=bstack1111lllll_opy_(),
                file_path=file_path,
                framework=bstack1l1l_opy_ (u"ࠧࡈࡥࡩࡣࡹࡩࠧླྀ"),
                bstack111ll1l1l1_opy_=bstack11l1llllll_opy_.bstack111l1l1l11_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack1l1l_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢཹ"),
                hook_type=name
            )
            self.tests[bstack111l1l1l1l_opy_][bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤࡪࡡࡵࡣེࠥ")] = hook_data
            current_test_id = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠣࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨཻࠧ"), None)
            if current_test_id:
                hook_data.bstack111ll1l111_opy_(current_test_id)
            if name == bstack1l1l_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨོ"):
                threading.current_thread().before_all_hook_uuid = bstack111l1l1l1l_opy_
            threading.current_thread().current_hook_uuid = bstack111l1l1l1l_opy_
            bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠥࡌࡴࡵ࡫ࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧཽࠦ"), hook_data)
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡳࡨࡩࡵࡳࡴࡨࡨࠥ࡯࡮ࠡࡵࡷࡥࡷࡺࠠࡩࡱࡲ࡯ࠥ࡫ࡶࡦࡰࡷࡷ࠱ࠦࡨࡰࡱ࡮ࠤࡳࡧ࡭ࡦ࠼ࠣࠩࡸ࠲ࠠࡦࡴࡵࡳࡷࡀࠠࠦࡵࠥཾ"), name, e)
    def bstack11l111l1_opy_(self, attrs):
        bstack111l1ll1ll_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩཿ"), None)
        hook_data = self.tests[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢྀࠩ")]
        status = bstack1l1l_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪཱྀࠢ")
        exception = None
        bstack111l1lllll_opy_ = None
        if hook_data.name == bstack1l1l_opy_ (u"ࠣࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ࠦྂ"):
            self.bstack111ll1ll11_opy_.reset()
            bstack111l1ll11l_opy_ = self.tests[bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩྃ"), None)][bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ྄࠭")].result.result
            if bstack111l1ll11l_opy_ == bstack1l1l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ྅"):
                if attrs.hook_failures == 1:
                    status = bstack1l1l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ྆")
                elif attrs.hook_failures == 2:
                    status = bstack1l1l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ྇")
            elif attrs.aborted:
                status = bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢྈ")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack1l1l_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠬྉ") and attrs.hook_failures == 1:
                status = bstack1l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤྊ")
            elif hasattr(attrs, bstack1l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡡࡰࡩࡸࡹࡡࡨࡧࠪྋ")) and attrs.error_message:
                status = bstack1l1l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦྌ")
            bstack111l1lllll_opy_, exception = self._111l1ll111_opy_(attrs)
        bstack111l1lll11_opy_ = Result(result=status, exception=exception, bstack111l1l1lll_opy_=[bstack111l1lllll_opy_])
        hook_data.stop(time=bstack1111lllll_opy_(), duration=0, result=bstack111l1lll11_opy_)
        bstack11l1llllll_opy_.bstack111ll1l1ll_opy_(bstack1l1l_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧྍ"), self.tests[bstack111l1ll1ll_opy_][bstack1l1l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩྎ")])
        threading.current_thread().current_hook_uuid = None
    def _111l1ll111_opy_(self, attrs):
        try:
            import traceback
            bstack1l1ll1ll1l_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111l1lllll_opy_ = bstack1l1ll1ll1l_opy_[-1] if bstack1l1ll1ll1l_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack1l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦ࡯ࡤࡥࡸࡶࡷ࡫ࡤࠡࡹ࡫࡭ࡱ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡥࡸࡷࡹࡵ࡭ࠡࡶࡵࡥࡨ࡫ࡢࡢࡥ࡮ࠦྏ"))
            bstack111l1lllll_opy_ = None
            exception = None
        return bstack111l1lllll_opy_, exception