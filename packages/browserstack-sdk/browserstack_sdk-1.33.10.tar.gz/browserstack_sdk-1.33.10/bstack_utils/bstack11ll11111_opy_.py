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
import os
import json
from bstack_utils.bstack1l1llll1_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1llll11l_opy_(object):
  bstack11l1ll1l_opy_ = os.path.join(os.path.expanduser(bstack11111l_opy_ (u"ࠨࢀࠪឯ")), bstack11111l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩឰ"))
  bstack11l1llll1l1_opy_ = os.path.join(bstack11l1ll1l_opy_, bstack11111l_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡷ࠳ࡰࡳࡰࡰࠪឱ"))
  commands_to_wrap = None
  perform_scan = None
  bstack1ll111l111_opy_ = None
  bstack1ll11ll1_opy_ = None
  bstack11ll1l111l1_opy_ = None
  bstack11ll111l111_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack11111l_opy_ (u"ࠫ࡮ࡴࡳࡵࡣࡱࡧࡪ࠭ឲ")):
      cls.instance = super(bstack11l1llll11l_opy_, cls).__new__(cls)
      cls.instance.bstack11l1lll1lll_opy_()
    return cls.instance
  def bstack11l1lll1lll_opy_(self):
    try:
      with open(self.bstack11l1llll1l1_opy_, bstack11111l_opy_ (u"ࠬࡸࠧឳ")) as bstack11llll1ll_opy_:
        bstack11l1lll1ll1_opy_ = bstack11llll1ll_opy_.read()
        data = json.loads(bstack11l1lll1ll1_opy_)
        if bstack11111l_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨ឴") in data:
          self.bstack11ll1l111ll_opy_(data[bstack11111l_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࡴࠩ឵")])
        if bstack11111l_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩា") in data:
          self.bstack1lllll1ll1_opy_(data[bstack11111l_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪិ")])
        if bstack11111l_opy_ (u"ࠪࡲࡴࡴࡂࡔࡶࡤࡧࡰࡏ࡮ࡧࡴࡤࡅ࠶࠷ࡹࡄࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧី") in data:
          self.bstack11l1llll111_opy_(data[bstack11111l_opy_ (u"ࠫࡳࡵ࡮ࡃࡕࡷࡥࡨࡱࡉ࡯ࡨࡵࡥࡆ࠷࠱ࡺࡅ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨឹ")])
    except:
      pass
  def bstack11l1llll111_opy_(self, bstack11ll111l111_opy_):
    if bstack11ll111l111_opy_ != None:
      self.bstack11ll111l111_opy_ = bstack11ll111l111_opy_
  def bstack1lllll1ll1_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack11111l_opy_ (u"ࠬࡹࡣࡢࡰࠪឺ"),bstack11111l_opy_ (u"࠭ࠧុ"))
      self.bstack1ll111l111_opy_ = scripts.get(bstack11111l_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠫូ"),bstack11111l_opy_ (u"ࠨࠩួ"))
      self.bstack1ll11ll1_opy_ = scripts.get(bstack11111l_opy_ (u"ࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾ࠭ើ"),bstack11111l_opy_ (u"ࠪࠫឿ"))
      self.bstack11ll1l111l1_opy_ = scripts.get(bstack11111l_opy_ (u"ࠫࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠩៀ"),bstack11111l_opy_ (u"ࠬ࠭េ"))
  def bstack11ll1l111ll_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1llll1l1_opy_, bstack11111l_opy_ (u"࠭ࡷࠨែ")) as file:
        json.dump({
          bstack11111l_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡴࠤៃ"): self.commands_to_wrap,
          bstack11111l_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࡴࠤោ"): {
            bstack11111l_opy_ (u"ࠤࡶࡧࡦࡴࠢៅ"): self.perform_scan,
            bstack11111l_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠢំ"): self.bstack1ll111l111_opy_,
            bstack11111l_opy_ (u"ࠦ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠣះ"): self.bstack1ll11ll1_opy_,
            bstack11111l_opy_ (u"ࠧࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠥៈ"): self.bstack11ll1l111l1_opy_
          },
          bstack11111l_opy_ (u"ࠨ࡮ࡰࡰࡅࡗࡹࡧࡣ࡬ࡋࡱࡪࡷࡧࡁ࠲࠳ࡼࡇ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠥ៉"): self.bstack11ll111l111_opy_
        }, file)
    except Exception as e:
      logger.error(bstack11111l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡹࡴࡰࡴ࡬ࡲ࡬ࠦࡣࡰ࡯ࡰࡥࡳࡪࡳ࠻ࠢࡾࢁࠧ៊").format(e))
      pass
  def bstack1l111lll1_opy_(self, command_name):
    try:
      return any(command.get(bstack11111l_opy_ (u"ࠨࡰࡤࡱࡪ࠭់")) == command_name for command in self.commands_to_wrap)
    except:
      return False
bstack11ll11111_opy_ = bstack11l1llll11l_opy_()