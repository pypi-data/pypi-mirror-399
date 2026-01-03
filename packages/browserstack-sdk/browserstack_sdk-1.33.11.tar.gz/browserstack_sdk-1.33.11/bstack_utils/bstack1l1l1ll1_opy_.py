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
import json
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l1111llll_opy_, bstack1l1l1111l_opy_, bstack11llll11ll_opy_, bstack11111ll11_opy_, \
    bstack111l1lll111_opy_
from bstack_utils.measure import measure
def bstack111ll11ll_opy_(bstack1llll1l1l11l_opy_):
    for driver in bstack1llll1l1l11l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l11l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack11ll11111_opy_(driver, status, reason=bstack1l1l_opy_ (u"ࠧࠨₘ")):
    bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
    if bstack1l1ll1l1_opy_.bstack1llllll1l1l_opy_():
        return
    bstack11ll1llll_opy_ = bstack11l11lll1l_opy_(bstack1l1l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫₙ"), bstack1l1l_opy_ (u"ࠩࠪₚ"), status, reason, bstack1l1l_opy_ (u"ࠪࠫₛ"), bstack1l1l_opy_ (u"ࠫࠬₜ"))
    driver.execute_script(bstack11ll1llll_opy_)
@measure(event_name=EVENTS.bstack1l11l1l11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack1l11l111l1_opy_(page, status, reason=bstack1l1l_opy_ (u"ࠬ࠭₝")):
    try:
        if page is None:
            return
        bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
        if bstack1l1ll1l1_opy_.bstack1llllll1l1l_opy_():
            return
        bstack11ll1llll_opy_ = bstack11l11lll1l_opy_(bstack1l1l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ₞"), bstack1l1l_opy_ (u"ࠧࠨ₟"), status, reason, bstack1l1l_opy_ (u"ࠨࠩ₠"), bstack1l1l_opy_ (u"ࠩࠪ₡"))
        page.evaluate(bstack1l1l_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ₢"), bstack11ll1llll_opy_)
    except Exception as e:
        print(bstack1l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡻࡾࠤ₣"), e)
def bstack11l11lll1l_opy_(type, name, status, reason, bstack1l111111l1_opy_, bstack11l11lll_opy_):
    bstack1l1111l11l_opy_ = {
        bstack1l1l_opy_ (u"ࠬࡧࡣࡵ࡫ࡲࡲࠬ₤"): type,
        bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ₥"): {}
    }
    if type == bstack1l1l_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ₦"):
        bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ₧")][bstack1l1l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ₨")] = bstack1l111111l1_opy_
        bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭₩")][bstack1l1l_opy_ (u"ࠫࡩࡧࡴࡢࠩ₪")] = json.dumps(str(bstack11l11lll_opy_))
    if type == bstack1l1l_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭₫"):
        bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ€")][bstack1l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ₭")] = name
    if type == bstack1l1l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫ₮"):
        bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ₯")][bstack1l1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ₰")] = status
        if status == bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ₱") and str(reason) != bstack1l1l_opy_ (u"ࠧࠨ₲"):
            bstack1l1111l11l_opy_[bstack1l1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ₳")][bstack1l1l_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ₴")] = json.dumps(str(reason))
    bstack1ll1llll1_opy_ = bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭₵").format(json.dumps(bstack1l1111l11l_opy_))
    return bstack1ll1llll1_opy_
def bstack11l11111_opy_(url, config, logger, bstack111lll1l1l_opy_=False):
    hostname = bstack1l1l1111l_opy_(url)
    is_private = bstack11111ll11_opy_(hostname)
    try:
        if is_private or bstack111lll1l1l_opy_:
            file_path = bstack11l1111llll_opy_(bstack1l1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ₶"), bstack1l1l_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ₷"), logger)
            if os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡑࡓ࡙ࡥࡓࡆࡖࡢࡉࡗࡘࡏࡓࠩ₸")) and eval(
                    os.environ.get(bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪ₹"))):
                return
            if (bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ₺") in config and not config[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ₻")]):
                os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭₼")] = str(True)
                bstack1llll1l1l1ll_opy_ = {bstack1l1l_opy_ (u"ࠩ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨࠫ₽"): hostname}
                bstack111l1lll111_opy_(bstack1l1l_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ₾"), bstack1l1l_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩ₿"), bstack1llll1l1l1ll_opy_, logger)
    except Exception as e:
        pass
def bstack1llll111ll_opy_(caps, bstack1llll1l1l1l1_opy_):
    if bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭⃀") in caps:
        caps[bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ⃁")][bstack1l1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭⃂")] = True
        if bstack1llll1l1l1l1_opy_:
            caps[bstack1l1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ⃃")][bstack1l1l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ⃄")] = bstack1llll1l1l1l1_opy_
    else:
        caps[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࠨ⃅")] = True
        if bstack1llll1l1l1l1_opy_:
            caps[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⃆")] = bstack1llll1l1l1l1_opy_
def bstack1lllll11llll_opy_(bstack1111ll1l1l_opy_):
    bstack1llll1l1ll11_opy_ = bstack11llll11ll_opy_(threading.current_thread(), bstack1l1l_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩ⃇"), bstack1l1l_opy_ (u"࠭ࠧ⃈"))
    if bstack1llll1l1ll11_opy_ == bstack1l1l_opy_ (u"ࠧࠨ⃉") or bstack1llll1l1ll11_opy_ == bstack1l1l_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ⃊"):
        threading.current_thread().testStatus = bstack1111ll1l1l_opy_
    else:
        if bstack1111ll1l1l_opy_ == bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⃋"):
            threading.current_thread().testStatus = bstack1111ll1l1l_opy_