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
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1l11l1l1ll_opy_():
  def __init__(self, args, logger, bstack1lllllll1ll_opy_, bstack11111l11l1_opy_, bstack1llllll11ll_opy_):
    self.args = args
    self.logger = logger
    self.bstack1lllllll1ll_opy_ = bstack1lllllll1ll_opy_
    self.bstack11111l11l1_opy_ = bstack11111l11l1_opy_
    self.bstack1llllll11ll_opy_ = bstack1llllll11ll_opy_
  def bstack111111l11_opy_(self, bstack1lllllll11l_opy_, bstack1ll11l1lll_opy_, bstack1llllll1l11_opy_=False):
    bstack1l11llll1_opy_ = []
    manager = multiprocessing.Manager()
    bstack11111l1l11_opy_ = manager.list()
    bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
    if bstack1llllll1l11_opy_:
      for index, platform in enumerate(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ე")]):
        if index == 0:
          bstack1ll11l1lll_opy_[bstack11111l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧვ")] = self.args
        bstack1l11llll1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1lllllll11l_opy_,
                                                    args=(bstack1ll11l1lll_opy_, bstack11111l1l11_opy_)))
    else:
      for index, platform in enumerate(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨზ")]):
        bstack1l11llll1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1lllllll11l_opy_,
                                                    args=(bstack1ll11l1lll_opy_, bstack11111l1l11_opy_)))
    i = 0
    for t in bstack1l11llll1_opy_:
      try:
        if bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧთ")):
          os.environ[bstack11111l_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨი")] = json.dumps(self.bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫკ")][i % self.bstack1llllll11ll_opy_])
      except Exception as e:
        self.logger.debug(bstack11111l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡶࡲࡶ࡮ࡴࡧࠡࡥࡸࡶࡷ࡫࡮ࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡩ࡫ࡴࡢ࡫࡯ࡷ࠿ࠦࡻࡾࠤლ").format(str(e)))
      i += 1
      t.start()
    for t in bstack1l11llll1_opy_:
      t.join()
    return list(bstack11111l1l11_opy_)