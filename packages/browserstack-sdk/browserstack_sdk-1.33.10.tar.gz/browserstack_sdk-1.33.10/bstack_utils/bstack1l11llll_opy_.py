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
import json
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l111l11ll_opy_, bstack1111l1lll_opy_, bstack11l1l111l_opy_, bstack1l1l1l1111_opy_, \
    bstack11l1111l11l_opy_
from bstack_utils.measure import measure
def bstack1lllll1lll_opy_(bstack1llll1l1l1ll_opy_):
    for driver in bstack1llll1l1l1ll_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l1111111l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
def bstack1l1111l1l1_opy_(driver, status, reason=bstack11111l_opy_ (u"ࠧࠨₑ")):
    bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
    if bstack11l11l1lll_opy_.bstack111111l111_opy_():
        return
    bstack1lllll1ll_opy_ = bstack1l1111ll11_opy_(bstack11111l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫₒ"), bstack11111l_opy_ (u"ࠩࠪₓ"), status, reason, bstack11111l_opy_ (u"ࠪࠫₔ"), bstack11111l_opy_ (u"ࠫࠬₕ"))
    driver.execute_script(bstack1lllll1ll_opy_)
@measure(event_name=EVENTS.bstack1l1111111l_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
def bstack11l11111l_opy_(page, status, reason=bstack11111l_opy_ (u"ࠬ࠭ₖ")):
    try:
        if page is None:
            return
        bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
        if bstack11l11l1lll_opy_.bstack111111l111_opy_():
            return
        bstack1lllll1ll_opy_ = bstack1l1111ll11_opy_(bstack11111l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩₗ"), bstack11111l_opy_ (u"ࠧࠨₘ"), status, reason, bstack11111l_opy_ (u"ࠨࠩₙ"), bstack11111l_opy_ (u"ࠩࠪₚ"))
        page.evaluate(bstack11111l_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦₛ"), bstack1lllll1ll_opy_)
    except Exception as e:
        print(bstack11111l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡻࡾࠤₜ"), e)
def bstack1l1111ll11_opy_(type, name, status, reason, bstack111llllll1_opy_, bstack11ll1111l_opy_):
    bstack1ll1111ll1_opy_ = {
        bstack11111l_opy_ (u"ࠬࡧࡣࡵ࡫ࡲࡲࠬ₝"): type,
        bstack11111l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ₞"): {}
    }
    if type == bstack11111l_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ₟"):
        bstack1ll1111ll1_opy_[bstack11111l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ₠")][bstack11111l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ₡")] = bstack111llllll1_opy_
        bstack1ll1111ll1_opy_[bstack11111l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭₢")][bstack11111l_opy_ (u"ࠫࡩࡧࡴࡢࠩ₣")] = json.dumps(str(bstack11ll1111l_opy_))
    if type == bstack11111l_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭₤"):
        bstack1ll1111ll1_opy_[bstack11111l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ₥")][bstack11111l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ₦")] = name
    if type == bstack11111l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫ₧"):
        bstack1ll1111ll1_opy_[bstack11111l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ₨")][bstack11111l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ₩")] = status
        if status == bstack11111l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ₪") and str(reason) != bstack11111l_opy_ (u"ࠧࠨ₫"):
            bstack1ll1111ll1_opy_[bstack11111l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ€")][bstack11111l_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ₭")] = json.dumps(str(reason))
    bstack1111l1111_opy_ = bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭₮").format(json.dumps(bstack1ll1111ll1_opy_))
    return bstack1111l1111_opy_
def bstack1ll11ll11_opy_(url, config, logger, bstack111l111l_opy_=False):
    hostname = bstack1111l1lll_opy_(url)
    is_private = bstack1l1l1l1111_opy_(hostname)
    try:
        if is_private or bstack111l111l_opy_:
            file_path = bstack11l111l11ll_opy_(bstack11111l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ₯"), bstack11111l_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ₰"), logger)
            if os.environ.get(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡑࡓ࡙ࡥࡓࡆࡖࡢࡉࡗࡘࡏࡓࠩ₱")) and eval(
                    os.environ.get(bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪ₲"))):
                return
            if (bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ₳") in config and not config[bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ₴")]):
                os.environ[bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭₵")] = str(True)
                bstack1llll1l1lll1_opy_ = {bstack11111l_opy_ (u"ࠩ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨࠫ₶"): hostname}
                bstack11l1111l11l_opy_(bstack11111l_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ₷"), bstack11111l_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩ₸"), bstack1llll1l1lll1_opy_, logger)
    except Exception as e:
        pass
def bstack1l11ll1ll1_opy_(caps, bstack1llll1l1ll11_opy_):
    if bstack11111l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭₹") in caps:
        caps[bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ₺")][bstack11111l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭₻")] = True
        if bstack1llll1l1ll11_opy_:
            caps[bstack11111l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ₼")][bstack11111l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ₽")] = bstack1llll1l1ll11_opy_
    else:
        caps[bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࠨ₾")] = True
        if bstack1llll1l1ll11_opy_:
            caps[bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ₿")] = bstack1llll1l1ll11_opy_
def bstack1lllll1l11ll_opy_(bstack1111l1ll1l_opy_):
    bstack1llll1l1ll1l_opy_ = bstack11l1l111l_opy_(threading.current_thread(), bstack11111l_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩ⃀"), bstack11111l_opy_ (u"࠭ࠧ⃁"))
    if bstack1llll1l1ll1l_opy_ == bstack11111l_opy_ (u"ࠧࠨ⃂") or bstack1llll1l1ll1l_opy_ == bstack11111l_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ⃃"):
        threading.current_thread().testStatus = bstack1111l1ll1l_opy_
    else:
        if bstack1111l1ll1l_opy_ == bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⃄"):
            threading.current_thread().testStatus = bstack1111l1ll1l_opy_