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
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11l1ll1ll1l_opy_ import bstack11l1ll1l1l1_opy_
from bstack_utils.constants import bstack11l11lll1l1_opy_, bstack1lllll111l_opy_
from bstack_utils.bstack1l11l1l1ll_opy_ import bstack111l1111l_opy_
from bstack_utils import bstack1lllllll1l_opy_
bstack11l11ll11l1_opy_ = 10
class bstack1l11l111_opy_:
    def __init__(self, bstack111lllllll_opy_, config, bstack11l11ll11ll_opy_=0):
        self.bstack11l11l1ll11_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l11l111ll_opy_ = bstack1l1l_opy_ (u"ࠦࢀࢃ࠯ࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳࡫ࡧࡩ࡭ࡧࡧ࠱ࡹ࡫ࡳࡵࡵࠥᭇ").format(bstack11l11lll1l1_opy_)
        self.bstack11l11l11lll_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠧࡧࡢࡰࡴࡷࡣࡧࡻࡩ࡭ࡦࡢࡿࢂࠨᭈ").format(os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᭉ"))))
        self.bstack11l11l111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࡥࡻࡾ࠰ࡷࡼࡹࠨᭊ").format(os.environ.get(bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᭋ"))))
        self.bstack11l11l11l1l_opy_ = 2
        self.bstack111lllllll_opy_ = bstack111lllllll_opy_
        self.config = config
        self.logger = bstack1lllllll1l_opy_.get_logger(__name__, bstack1lllll111l_opy_)
        self.bstack11l11ll11ll_opy_ = bstack11l11ll11ll_opy_
        self.bstack11l11l1l1ll_opy_ = False
        self.bstack11l11l1llll_opy_ = not (
                            os.environ.get(bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠣᭌ")) and
                            os.environ.get(bstack1l1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨ᭍")) and
                            os.environ.get(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡔ࡚ࡁࡍࡡࡑࡓࡉࡋ࡟ࡄࡑࡘࡒ࡙ࠨ᭎"))
                        )
        if bstack111l1111l_opy_.bstack11l11l1lll1_opy_(config):
            self.bstack11l11l11l1l_opy_ = bstack111l1111l_opy_.bstack11l11l11l11_opy_(config, self.bstack11l11ll11ll_opy_)
            self.bstack11l11ll111l_opy_()
    def bstack11l11ll1l11_opy_(self):
        return bstack1l1l_opy_ (u"ࠧࢁࡽࡠࡽࢀࠦ᭏").format(self.config.get(bstack1l1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ᭐")), os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭᭑")))
    def bstack11l11ll1111_opy_(self):
        try:
            if self.bstack11l11l1llll_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l11l111l1_opy_, bstack1l1l_opy_ (u"ࠣࡴࠥ᭒")) as f:
                        bstack11l11l1l111_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l11l1l111_opy_ = set()
                bstack11l11l1111l_opy_ = bstack11l11l1l111_opy_ - self.bstack11l11l1ll11_opy_
                if not bstack11l11l1111l_opy_:
                    return
                self.bstack11l11l1ll11_opy_.update(bstack11l11l1111l_opy_)
                data = {bstack1l1l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࡖࡨࡷࡹࡹࠢ᭓"): list(self.bstack11l11l1ll11_opy_), bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠨ᭔"): self.config.get(bstack1l1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ᭕")), bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡖࡺࡴࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥ᭖"): os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬ᭗")), bstack1l1l_opy_ (u"ࠢࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠧ᭘"): self.config.get(bstack1l1l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭᭙"))}
            response = bstack11l1ll1l1l1_opy_.bstack11l11l11ll1_opy_(self.bstack11l11l111ll_opy_, data)
            if response.get(bstack1l1l_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࠤ᭚")) == 200:
                self.logger.debug(bstack1l1l_opy_ (u"ࠥࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺࠢࡶࡩࡳࡺࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࡀࠠࡼࡿࠥ᭛").format(data))
            else:
                self.logger.debug(bstack1l1l_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡱࡨࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶ࠾ࠥࢁࡽࠣ᭜").format(response))
        except Exception as e:
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡦࡸࡶ࡮ࡴࡧࠡࡵࡨࡲࡩ࡯࡮ࡨࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧ᭝").format(e))
    def bstack11l11l1l1l1_opy_(self):
        if self.bstack11l11l1llll_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l11l111l1_opy_, bstack1l1l_opy_ (u"ࠨࡲࠣ᭞")) as f:
                        bstack11l11l1ll1l_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l11l1ll1l_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack1l1l_opy_ (u"ࠢࡑࡱ࡯ࡰࡪࡪࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࠦࡣࡰࡷࡱࡸࠥ࠮࡬ࡰࡥࡤࡰ࠮ࡀࠠࡼࡿࠥ᭟").format(failed_count))
                if failed_count >= self.bstack11l11l11l1l_opy_:
                    self.logger.info(bstack1l1l_opy_ (u"ࠣࡖ࡫ࡶࡪࡹࡨࡰ࡮ࡧࠤࡨࡸ࡯ࡴࡵࡨࡨࠥ࠮࡬ࡰࡥࡤࡰ࠮ࡀࠠࡼࡿࠣࡂࡂࠦࡻࡾࠤ᭠").format(failed_count, self.bstack11l11l11l1l_opy_))
                    self.bstack11l11l1l11l_opy_(failed_count)
                    self.bstack11l11l1l1ll_opy_ = True
            return
        try:
            response = bstack11l1ll1l1l1_opy_.bstack11l11l1l1l1_opy_(bstack1l1l_opy_ (u"ࠤࡾࢁࡄࡨࡵࡪ࡮ࡧࡒࡦࡳࡥ࠾ࡽࢀࠪࡧࡻࡩ࡭ࡦࡕࡹࡳࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ࠿ࡾࢁࠫࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࡀࡿࢂࠨ᭡").format(self.bstack11l11l111ll_opy_, self.config.get(bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭᭢")), os.environ.get(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪ᭣")), self.config.get(bstack1l1l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ᭤"))))
            if response.get(bstack1l1l_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨ᭥")) == 200:
                failed_count = response.get(bstack1l1l_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࡔࡦࡵࡷࡷࡈࡵࡵ࡯ࡶࠥ᭦"), 0)
                self.logger.debug(bstack1l1l_opy_ (u"ࠣࡒࡲࡰࡱ࡫ࡤࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡤࡱࡸࡲࡹࡀࠠࡼࡿࠥ᭧").format(failed_count))
                if failed_count >= self.bstack11l11l11l1l_opy_:
                    self.logger.info(bstack1l1l_opy_ (u"ࠤࡗ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࠥࡩࡲࡰࡵࡶࡩࡩࡀࠠࡼࡿࠣࡂࡂࠦࡻࡾࠤ᭨").format(failed_count, self.bstack11l11l11l1l_opy_))
                    self.bstack11l11l1l11l_opy_(failed_count)
                    self.bstack11l11l1l1ll_opy_ = True
            else:
                self.logger.error(bstack1l1l_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡰ࡮࡯ࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢ᭩").format(response))
        except Exception as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡥࡷࡵ࡭ࡳ࡭ࠠࡱࡱ࡯ࡰ࡮ࡴࡧ࠻ࠢࡾࢁࠧ᭪").format(e))
    def bstack11l11l1l11l_opy_(self, failed_count):
        with open(self.bstack11l11l11lll_opy_, bstack1l1l_opy_ (u"ࠧࡽࠢ᭫")) as f:
            f.write(bstack1l1l_opy_ (u"ࠨࡔࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡦࡶࡴࡹࡳࡦࡦࠣࡥࡹࠦࡻࡾ࡞ࡱ᭬ࠦ").format(datetime.now()))
            f.write(bstack1l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࠦࡣࡰࡷࡱࡸ࠿ࠦࡻࡾ࡞ࡱࠦ᭭").format(failed_count))
        self.logger.debug(bstack1l1l_opy_ (u"ࠣࡃࡥࡳࡷࡺࠠࡃࡷ࡬ࡰࡩࠦࡦࡪ࡮ࡨࠤࡨࡸࡥࡢࡶࡨࡨ࠿ࠦࡻࡾࠤ᭮").format(self.bstack11l11l11lll_opy_))
    def bstack11l11ll111l_opy_(self):
        def bstack11l11ll1l1l_opy_():
            while not self.bstack11l11l1l1ll_opy_:
                time.sleep(bstack11l11ll11l1_opy_)
                self.bstack11l11ll1111_opy_()
                self.bstack11l11l1l1l1_opy_()
        bstack11l11ll1ll1_opy_ = threading.Thread(target=bstack11l11ll1l1l_opy_, daemon=True)
        bstack11l11ll1ll1_opy_.start()