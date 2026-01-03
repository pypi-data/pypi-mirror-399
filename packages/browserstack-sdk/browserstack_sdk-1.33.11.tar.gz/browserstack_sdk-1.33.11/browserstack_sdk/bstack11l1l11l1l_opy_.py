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
import json
import logging
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack1lll111l11_opy_ = {}
        bstack111ll1ll1l_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠫࡈ࡛ࡒࡓࡇࡑࡘࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡅࡃࡗࡅࠬ༜"), bstack1l1l_opy_ (u"ࠬ࠭༝"))
        if not bstack111ll1ll1l_opy_:
            return bstack1lll111l11_opy_
        try:
            bstack111ll1lll1_opy_ = json.loads(bstack111ll1ll1l_opy_)
            if bstack1l1l_opy_ (u"ࠨ࡯ࡴࠤ༞") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠢࡰࡵࠥ༟")] = bstack111ll1lll1_opy_[bstack1l1l_opy_ (u"ࠣࡱࡶࠦ༠")]
            if bstack1l1l_opy_ (u"ࠤࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ༡") in bstack111ll1lll1_opy_ or bstack1l1l_opy_ (u"ࠥࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༢") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠦࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠢ༣")] = bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠧࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ༤"), bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠨ࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠤ༥")))
            if bstack1l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࠣ༦") in bstack111ll1lll1_opy_ or bstack1l1l_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪࠨ༧") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠢ༨")] = bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࠦ༩"), bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤ༪")))
            if bstack1l1l_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠢ༫") in bstack111ll1lll1_opy_ or bstack1l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠢ༬") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠣ༭")] = bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠥ༮"), bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥ༯")))
            if bstack1l1l_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࠥ༰") in bstack111ll1lll1_opy_ or bstack1l1l_opy_ (u"ࠦࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠣ༱") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠧࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠤ༲")] = bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠨࡤࡦࡸ࡬ࡧࡪࠨ༳"), bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠦ༴")))
            if bstack1l1l_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯༵ࠥ") in bstack111ll1lll1_opy_ or bstack1l1l_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣ༶") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ༷")] = bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨ༸"), bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨ༹ࠦ")))
            if bstack1l1l_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ༺") in bstack111ll1lll1_opy_ or bstack1l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤ༻") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥ༼")] = bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ༽"), bstack111ll1lll1_opy_.get(bstack1l1l_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༾")))
            if bstack1l1l_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰ࡚ࡦࡸࡩࡢࡤ࡯ࡩࡸࠨ༿") in bstack111ll1lll1_opy_:
                bstack1lll111l11_opy_[bstack1l1l_opy_ (u"ࠧࡩࡵࡴࡶࡲࡱ࡛ࡧࡲࡪࡣࡥࡰࡪࡹࠢཀ")] = bstack111ll1lll1_opy_[bstack1l1l_opy_ (u"ࠨࡣࡶࡵࡷࡳࡲ࡜ࡡࡳ࡫ࡤࡦࡱ࡫ࡳࠣཁ")]
        except Exception as error:
            logger.error(bstack1l1l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡧࡺࡸࡲࡦࡰࡷࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡤࡢࡶࡤ࠾ࠥࠨག") +  str(error))
        return bstack1lll111l11_opy_