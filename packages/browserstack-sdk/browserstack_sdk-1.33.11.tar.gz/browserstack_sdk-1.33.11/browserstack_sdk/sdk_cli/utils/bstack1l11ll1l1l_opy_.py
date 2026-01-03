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
import shutil
import tempfile
import threading
import urllib.request
import uuid
from pathlib import Path
import logging
import re
from bstack_utils.helper import bstack1l1l11lll11_opy_
bstack11ll1l1l111_opy_ = 100 * 1024 * 1024 # 100 bstack11ll1l1l1ll_opy_
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bstack1l1l11l1l1l_opy_ = bstack1l1l11lll11_opy_()
bstack1l1l1l1l1l1_opy_ = bstack1l1l_opy_ (u"ࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣᙘ")
bstack11lll11ll11_opy_ = bstack1l1l_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᙙ")
bstack11lll11lll1_opy_ = bstack1l1l_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᙚ")
bstack11lll11ll1l_opy_ = bstack1l1l_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᙛ")
bstack11ll1l1lll1_opy_ = bstack1l1l_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᙜ")
_11ll1ll1l1l_opy_ = threading.local()
def bstack11lllll1111_opy_(test_framework_state, test_hook_state):
    bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡓࡦࡶࠣࡸ࡭࡫ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡶࡨࡷࡹࠦࡥࡷࡧࡱࡸࠥࡹࡴࡢࡶࡨࠤ࡮ࡴࠠࡵࡪࡵࡩࡦࡪ࠭࡭ࡱࡦࡥࡱࠦࡳࡵࡱࡵࡥ࡬࡫࠮ࠋࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࠥࡹࡨࡰࡷ࡯ࡨࠥࡨࡥࠡࡥࡤࡰࡱ࡫ࡤࠡࡤࡼࠤࡹ࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡩࡣࡱࡨࡱ࡫ࡲࠡࠪࡶࡹࡨ࡮ࠠࡢࡵࠣࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴࠪࠌࠣࠤࠥࠦࡢࡦࡨࡲࡶࡪࠦࡡ࡯ࡻࠣࡪ࡮ࡲࡥࠡࡷࡳࡰࡴࡧࡤࡴࠢࡲࡧࡨࡻࡲ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᙝ")
    _11ll1ll1l1l_opy_.test_framework_state = test_framework_state
    _11ll1ll1l1l_opy_.test_hook_state = test_hook_state
def bstack11ll1l1l11l_opy_():
    bstack1l1l_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡓࡧࡷࡶ࡮࡫ࡶࡦࠢࡷ࡬ࡪࠦࡣࡶࡴࡵࡩࡳࡺࠠࡵࡧࡶࡸࠥ࡫ࡶࡦࡰࡷࠤࡸࡺࡡࡵࡧࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡶࡪࡧࡤ࠮࡮ࡲࡧࡦࡲࠠࡴࡶࡲࡶࡦ࡭ࡥ࠯ࠌࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹࠠࡢࠢࡷࡹࡵࡲࡥࠡࠪࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠮ࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩ࠮ࠦ࡯ࡳࠢࠫࡒࡴࡴࡥ࠭ࠢࡑࡳࡳ࡫ࠩࠡ࡫ࡩࠤࡳࡵࡴࠡࡵࡨࡸ࠳ࠐࠠࠡࠢࠣࠦࠧࠨᙞ")
    return (
        getattr(_11ll1ll1l1l_opy_, bstack1l1l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࠨᙟ"), None),
        getattr(_11ll1ll1l1l_opy_, bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࠫᙠ"), None)
    )
class bstack1l1111llll_opy_:
    bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡊ࡮ࡲࡥࡖࡲ࡯ࡳࡦࡪࡥࡳࠢࡳࡶࡴࡼࡩࡥࡧࡶࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡧ࡬ࡪࡶࡼࠤࡹࡵࠠࡶࡲ࡯ࡳࡦࡪࠠࡢࡰࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠠࡣࡣࡶࡩࡩࠦ࡯࡯ࠢࡷ࡬ࡪࠦࡧࡪࡸࡨࡲࠥ࡬ࡩ࡭ࡧࠣࡴࡦࡺࡨ࠯ࠌࠣࠤࠥࠦࡉࡵࠢࡶࡹࡵࡶ࡯ࡳࡶࡶࠤࡧࡵࡴࡩࠢ࡯ࡳࡨࡧ࡬ࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࡷࠥࡧ࡮ࡥࠢࡋࡘ࡙ࡖ࠯ࡉࡖࡗࡔࡘࠦࡕࡓࡎࡶ࠰ࠥࡧ࡮ࡥࠢࡦࡳࡵ࡯ࡥࡴࠢࡷ࡬ࡪࠦࡦࡪ࡮ࡨࠤ࡮ࡴࡴࡰࠢࡤࠤࡩ࡫ࡳࡪࡩࡱࡥࡹ࡫ࡤࠋࠢࠣࠤࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡࡹ࡬ࡸ࡭࡯࡮ࠡࡶ࡫ࡩࠥࡻࡳࡦࡴࠪࡷࠥ࡮࡯࡮ࡧࠣࡪࡴࡲࡤࡦࡴࠣࡹࡳࡪࡥࡳࠢࢁ࠳࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠳࡚ࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠱ࠎࠥࠦࠠࠡࡋࡩࠤࡦࡴࠠࡰࡲࡷ࡭ࡴࡴࡡ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡰࡢࡴࡤࡱࡪࡺࡥࡳࠢࠫ࡭ࡳࠦࡊࡔࡑࡑࠤ࡫ࡵࡲ࡮ࡣࡷ࠭ࠥ࡯ࡳࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡥࡳࡪࠠࡤࡱࡱࡸࡦ࡯࡮ࡴࠢࡤࠤࡹࡸࡵࡵࡪࡼࠤࡻࡧ࡬ࡶࡧࠍࠤࠥࠦࠠࡧࡱࡵࠤࡹ࡮ࡥࠡ࡭ࡨࡽࠥࠨࡢࡶ࡫࡯ࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣ࠮ࠣࡸ࡭࡫ࠠࡧ࡫࡯ࡩࠥࡽࡩ࡭࡮ࠣࡦࡪࠦࡰ࡭ࡣࡦࡩࡩࠦࡩ࡯ࠢࡷ࡬ࡪࠦࠢࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠦࠥ࡬࡯࡭ࡦࡨࡶࡀࠦ࡯ࡵࡪࡨࡶࡼ࡯ࡳࡦ࠮ࠍࠤࠥࠦࠠࡪࡶࠣࡨࡪ࡬ࡡࡶ࡮ࡷࡷࠥࡺ࡯ࠡࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧ࠴ࠊࠡࠢࠣࠤ࡙࡮ࡩࡴࠢࡹࡩࡷࡹࡩࡰࡰࠣࡳ࡫ࠦࡡࡥࡦࡢࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠠࡪࡵࠣࡥࠥࡼ࡯ࡪࡦࠣࡱࡪࡺࡨࡰࡦ⠗࡭ࡹࠦࡨࡢࡰࡧࡰࡪࡹࠠࡢ࡮࡯ࠤࡪࡸࡲࡰࡴࡶࠤ࡬ࡸࡡࡤࡧࡩࡹࡱࡲࡹࠡࡤࡼࠤࡱࡵࡧࡨ࡫ࡱ࡫ࠏࠦࠠࠡࠢࡷ࡬ࡪࡳࠠࡢࡰࡧࠤࡸ࡯࡭ࡱ࡮ࡼࠤࡷ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡶ࡫ࡶࡴࡽࡩ࡯ࡩࠣࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࡹ࠮ࠋࠢࠣࠤࠥࠨࠢࠣᙡ")
    @staticmethod
    def upload_attachment(bstack11ll1ll111l_opy_: str, *bstack11ll1ll1111_opy_) -> None:
        if not bstack11ll1ll111l_opy_ or not bstack11ll1ll111l_opy_.strip():
            logger.error(bstack1l1l_opy_ (u"ࠦࡦࡪࡤࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥ࡬ࡡࡪ࡮ࡨࡨ࠿ࠦࡐࡳࡱࡹ࡭ࡩ࡫ࡤࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࠤ࡮ࡹࠠࡦ࡯ࡳࡸࡾࠦ࡯ࡳࠢࡑࡳࡳ࡫࠮ࠣᙢ"))
            return
        bstack11ll1l1ll1l_opy_ = bstack11ll1ll1111_opy_[0] if bstack11ll1ll1111_opy_ and len(bstack11ll1ll1111_opy_) > 0 else None
        bstack11ll1ll1l11_opy_ = None
        test_framework_state, test_hook_state = bstack11ll1l1l11l_opy_()
        try:
            if bstack11ll1ll111l_opy_.startswith(bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᙣ")) or bstack11ll1ll111l_opy_.startswith(bstack1l1l_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣᙤ")):
                logger.debug(bstack1l1l_opy_ (u"ࠢࡑࡣࡷ࡬ࠥ࡯ࡳࠡ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡨࠥࡧࡳࠡࡗࡕࡐࡀࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡹ࡮ࡥࠡࡨ࡬ࡰࡪ࠴ࠢᙥ"))
                url = bstack11ll1ll111l_opy_
                bstack11ll1l11ll1_opy_ = str(uuid.uuid4())
                bstack11ll1l1ll11_opy_ = os.path.basename(urllib.request.urlparse(url).path)
                if not bstack11ll1l1ll11_opy_ or not bstack11ll1l1ll11_opy_.strip():
                    bstack11ll1l1ll11_opy_ = bstack11ll1l11ll1_opy_
                temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=bstack1l1l_opy_ (u"ࠣࡷࡳࡰࡴࡧࡤࡠࠤᙦ") + bstack11ll1l11ll1_opy_ + bstack1l1l_opy_ (u"ࠤࡢࠦᙧ"),
                                                        suffix=bstack1l1l_opy_ (u"ࠥࡣࠧᙨ") + bstack11ll1l1ll11_opy_)
                with urllib.request.urlopen(url) as response, open(temp_file.name, bstack1l1l_opy_ (u"ࠫࡼࡨࠧᙩ")) as out_file:
                    shutil.copyfileobj(response, out_file)
                bstack11ll1ll1l11_opy_ = Path(temp_file.name)
                logger.debug(bstack1l1l_opy_ (u"ࠧࡊ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡩ࡭ࡱ࡫ࠠࡵࡱࠣࡸࡪࡳࡰࡰࡴࡤࡶࡾࠦ࡬ࡰࡥࡤࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧᙪ").format(bstack11ll1ll1l11_opy_))
            else:
                bstack11ll1ll1l11_opy_ = Path(bstack11ll1ll111l_opy_)
                logger.debug(bstack1l1l_opy_ (u"ࠨࡐࡢࡶ࡫ࠤ࡮ࡹࠠࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡧࠤࡦࡹࠠ࡭ࡱࡦࡥࡱࠦࡦࡪ࡮ࡨ࠾ࠥࢁࡽࠣᙫ").format(bstack11ll1ll1l11_opy_))
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡳࡧࡺࡡࡪࡰࠣࡪ࡮ࡲࡥࠡࡨࡵࡳࡲࠦࡰࡢࡶ࡫࠳࡚ࡘࡌ࠻ࠢࡾࢁࠧᙬ").format(e))
            return
        if bstack11ll1ll1l11_opy_ is None or not bstack11ll1ll1l11_opy_.exists():
            logger.error(bstack1l1l_opy_ (u"ࠣࡕࡲࡹࡷࡩࡥࠡࡨ࡬ࡰࡪࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡧࡻ࡭ࡸࡺ࠺ࠡࡽࢀࠦ᙭").format(bstack11ll1ll1l11_opy_))
            return
        if bstack11ll1ll1l11_opy_.stat().st_size > bstack11ll1l1l111_opy_:
            logger.error(bstack1l1l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࡴ࡫ࡽࡩࠥ࡫ࡸࡤࡧࡨࡨࡸࠦ࡭ࡢࡺ࡬ࡱࡺࡳࠠࡢ࡮࡯ࡳࡼ࡫ࡤࠡࡵ࡬ࡾࡪࠦ࡯ࡧࠢࡾࢁࠧ᙮").format(bstack11ll1l1l111_opy_))
            return
        bstack11ll1ll11ll_opy_ = bstack1l1l_opy_ (u"ࠥࡘࡪࡹࡴࡍࡧࡹࡩࡱࠨᙯ")
        if bstack11ll1l1ll1l_opy_:
            try:
                params = json.loads(bstack11ll1l1ll1l_opy_)
                if bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨᙰ") in params and params.get(bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࠢᙱ")) is True:
                    bstack11ll1ll11ll_opy_ = bstack1l1l_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥᙲ")
            except Exception as bstack11ll1l11lll_opy_:
                logger.error(bstack1l1l_opy_ (u"ࠢࡋࡕࡒࡒࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡥࡳࡴࡲࡶࠥ࡯࡮ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡕࡧࡲࡢ࡯ࡶ࠾ࠥࢁࡽࠣᙳ").format(bstack11ll1l11lll_opy_))
        bstack11ll1l11l11_opy_ = False
        from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1ll1ll11lll_opy_
        if test_framework_state in bstack1ll1ll11lll_opy_.bstack11llll11ll1_opy_:
            if bstack11ll1ll11ll_opy_ == bstack11lll11lll1_opy_:
                bstack11ll1l11l11_opy_ = True
            bstack11ll1ll11ll_opy_ = bstack11lll11ll1l_opy_
        try:
            platform_index = os.environ[bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᙴ")]
            target_dir = os.path.join(bstack1l1l11l1l1l_opy_, bstack1l1l1l1l1l1_opy_ + str(platform_index),
                                      bstack11ll1ll11ll_opy_)
            if bstack11ll1l11l11_opy_:
                target_dir = os.path.join(target_dir, bstack11ll1l1lll1_opy_)
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(bstack1l1l_opy_ (u"ࠤࡆࡶࡪࡧࡴࡦࡦ࠲ࡺࡪࡸࡩࡧ࡫ࡨࡨࠥࡺࡡࡳࡩࡨࡸࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠻ࠢࡾࢁࠧᙵ").format(target_dir))
            file_name = os.path.basename(bstack11ll1ll1l11_opy_)
            bstack11ll1l1llll_opy_ = os.path.join(target_dir, file_name)
            if os.path.exists(bstack11ll1l1llll_opy_):
                base_name, extension = os.path.splitext(file_name)
                bstack11ll1l1l1l1_opy_ = 1
                while os.path.exists(os.path.join(target_dir, base_name + str(bstack11ll1l1l1l1_opy_) + extension)):
                    bstack11ll1l1l1l1_opy_ += 1
                bstack11ll1l1llll_opy_ = os.path.join(target_dir, base_name + str(bstack11ll1l1l1l1_opy_) + extension)
            shutil.copy(bstack11ll1ll1l11_opy_, bstack11ll1l1llll_opy_)
            logger.info(bstack1l1l_opy_ (u"ࠥࡊ࡮ࡲࡥࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡤࡱࡳ࡭ࡪࡪࠠࡵࡱ࠽ࠤࢀࢃࠢᙶ").format(bstack11ll1l1llll_opy_))
        except Exception as e:
            logger.error(bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡱࡴࡼࡩ࡯ࡩࠣࡪ࡮ࡲࡥࠡࡶࡲࠤࡹࡧࡲࡨࡧࡷࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠺ࠡࡽࢀࠦᙷ").format(e))
            return
        finally:
            if bstack11ll1ll111l_opy_.startswith(bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᙸ")) or bstack11ll1ll111l_opy_.startswith(bstack1l1l_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣᙹ")):
                try:
                    if bstack11ll1ll1l11_opy_ is not None and bstack11ll1ll1l11_opy_.exists():
                        bstack11ll1ll1l11_opy_.unlink()
                        logger.debug(bstack1l1l_opy_ (u"ࠢࡕࡧࡰࡴࡴࡸࡡࡳࡻࠣࡪ࡮ࡲࡥࠡࡦࡨࡰࡪࡺࡥࡥ࠼ࠣࡿࢂࠨᙺ").format(bstack11ll1ll1l11_opy_))
                except Exception as ex:
                    logger.error(bstack1l1l_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡷࡩࡲࡶ࡯ࡳࡣࡵࡽࠥ࡬ࡩ࡭ࡧ࠽ࠤࢀࢃࠢᙻ").format(ex))
    @staticmethod
    def bstack1lll1ll11_opy_() -> None:
        bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡄࡦ࡮ࡨࡸࡪࡹࠠࡢ࡮࡯ࠤ࡫ࡵ࡬ࡥࡧࡵࡷࠥࡽࡨࡰࡵࡨࠤࡳࡧ࡭ࡦࡵࠣࡷࡹࡧࡲࡵࠢࡺ࡭ࡹ࡮ࠠࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣࠢࡩࡳࡱࡲ࡯ࡸࡧࡧࠤࡧࡿࠠࡢࠢࡱࡹࡲࡨࡥࡳࠢ࡬ࡲࠏࠦࠠࠡࠢࠣࠤࠥࠦࡴࡩࡧࠣࡹࡸ࡫ࡲࠨࡵࠣࢂ࠴࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᙼ")
        bstack11ll1ll11l1_opy_ = bstack1l1l11lll11_opy_()
        pattern = re.compile(bstack1l1l_opy_ (u"ࡵ࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࡠࡩ࠱ࠢᙽ"))
        if os.path.exists(bstack11ll1ll11l1_opy_):
            for item in os.listdir(bstack11ll1ll11l1_opy_):
                bstack11ll1l11l1l_opy_ = os.path.join(bstack11ll1ll11l1_opy_, item)
                if os.path.isdir(bstack11ll1l11l1l_opy_) and pattern.fullmatch(item):
                    try:
                        shutil.rmtree(bstack11ll1l11l1l_opy_)
                    except Exception as e:
                        logger.error(bstack1l1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠻ࠢࡾࢁࠧᙾ").format(e))
        else:
            logger.info(bstack1l1l_opy_ (u"࡚ࠧࡨࡦࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹࡀࠠࡼࡿࠥᙿ").format(bstack11ll1ll11l1_opy_))