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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
from bstack_utils.bstack1ll111ll11_opy_ import bstack1ll1l1ll111_opy_
bstack1ll111ll11_opy_ = bstack1ll1l1ll111_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l1l1l11_opy_: Optional[str] = None):
    bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡇࡩࡨࡵࡲࡢࡶࡲࡶࠥࡺ࡯ࠡ࡮ࡲ࡫ࠥࡺࡨࡦࠢࡶࡸࡦࡸࡴࠡࡶ࡬ࡱࡪࠦ࡯ࡧࠢࡤࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࡡ࡭ࡱࡱ࡫ࠥࡽࡩࡵࡪࠣࡩࡻ࡫࡮ࡵࠢࡱࡥࡲ࡫ࠠࡢࡰࡧࠤࡸࡺࡡࡨࡧ࠱ࠎࠥࠦࠠࠡࠤࠥࠦṣ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1ll11l111l1_opy_: str = bstack1ll111ll11_opy_.bstack11l1lllllll_opy_(label)
            start_mark: str = label + bstack1l1l_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥṤ")
            end_mark: str = label + bstack1l1l_opy_ (u"ࠦ࠿࡫࡮ࡥࠤṥ")
            result = None
            try:
                if stage.value == STAGE.bstack1l1ll1l1ll_opy_.value:
                    bstack1ll111ll11_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1ll111ll11_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l1l1l11_opy_)
                elif stage.value == STAGE.bstack11lll1l1_opy_.value:
                    start_mark: str = bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧṦ")
                    end_mark: str = bstack1ll11l111l1_opy_ + bstack1l1l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦṧ")
                    bstack1ll111ll11_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1ll111ll11_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l1l1l11_opy_)
            except Exception as e:
                bstack1ll111ll11_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l1l1l11_opy_)
            return result
        return wrapper
    return decorator