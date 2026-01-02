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
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1l1llll1_opy_ import get_logger
from bstack_utils.bstack1ll11ll1l1_opy_ import bstack1ll1l111ll1_opy_
bstack1ll11ll1l1_opy_ = bstack1ll1l111ll1_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l1l1ll11l_opy_: Optional[str] = None):
    bstack11111l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡇࡩࡨࡵࡲࡢࡶࡲࡶࠥࡺ࡯ࠡ࡮ࡲ࡫ࠥࡺࡨࡦࠢࡶࡸࡦࡸࡴࠡࡶ࡬ࡱࡪࠦ࡯ࡧࠢࡤࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࡡ࡭ࡱࡱ࡫ࠥࡽࡩࡵࡪࠣࡩࡻ࡫࡮ࡵࠢࡱࡥࡲ࡫ࠠࡢࡰࡧࠤࡸࡺࡡࡨࡧ࠱ࠎࠥࠦࠠࠡࠤࠥࠦṜ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1l1lll1ll1l_opy_: str = bstack1ll11ll1l1_opy_.bstack11ll1111lll_opy_(label)
            start_mark: str = label + bstack11111l_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥṝ")
            end_mark: str = label + bstack11111l_opy_ (u"ࠦ࠿࡫࡮ࡥࠤṞ")
            result = None
            try:
                if stage.value == STAGE.bstack1ll1l1l1ll_opy_.value:
                    bstack1ll11ll1l1_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1ll11ll1l1_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l1l1ll11l_opy_)
                elif stage.value == STAGE.bstack1ll1l1ll1_opy_.value:
                    start_mark: str = bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧṟ")
                    end_mark: str = bstack1l1lll1ll1l_opy_ + bstack11111l_opy_ (u"ࠨ࠺ࡦࡰࡧࠦṠ")
                    bstack1ll11ll1l1_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1ll11ll1l1_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l1l1ll11l_opy_)
            except Exception as e:
                bstack1ll11ll1l1_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l1l1ll11l_opy_)
            return result
        return wrapper
    return decorator