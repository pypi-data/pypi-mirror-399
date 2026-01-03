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
import multiprocessing
import os
from bstack_utils.config import Config
class bstack11l111111l_opy_():
  def __init__(self, args, logger, bstack11111111ll_opy_, bstack1lllllll1ll_opy_, bstack1llllll11ll_opy_):
    self.args = args
    self.logger = logger
    self.bstack11111111ll_opy_ = bstack11111111ll_opy_
    self.bstack1lllllll1ll_opy_ = bstack1lllllll1ll_opy_
    self.bstack1llllll11ll_opy_ = bstack1llllll11ll_opy_
  def bstack1lll11l11l_opy_(self, bstack11111ll111_opy_, bstack11lllll1l1_opy_, bstack1llllll1l11_opy_=False):
    bstack11ll11llll_opy_ = []
    manager = multiprocessing.Manager()
    bstack1lllllll111_opy_ = manager.list()
    bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
    if bstack1llllll1l11_opy_:
      for index, platform in enumerate(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ე")]):
        if index == 0:
          bstack11lllll1l1_opy_[bstack1l1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧვ")] = self.args
        bstack11ll11llll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack11111ll111_opy_,
                                                    args=(bstack11lllll1l1_opy_, bstack1lllllll111_opy_)))
    else:
      for index, platform in enumerate(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨზ")]):
        bstack11ll11llll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack11111ll111_opy_,
                                                    args=(bstack11lllll1l1_opy_, bstack1lllllll111_opy_)))
    i = 0
    for t in bstack11ll11llll_opy_:
      try:
        if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧთ")):
          os.environ[bstack1l1l_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨი")] = json.dumps(self.bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫკ")][i % self.bstack1llllll11ll_opy_])
      except Exception as e:
        self.logger.debug(bstack1l1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡶࡲࡶ࡮ࡴࡧࠡࡥࡸࡶࡷ࡫࡮ࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡩ࡫ࡴࡢ࡫࡯ࡷ࠿ࠦࡻࡾࠤლ").format(str(e)))
      i += 1
      t.start()
    for t in bstack11ll11llll_opy_:
      t.join()
    return list(bstack1lllllll111_opy_)