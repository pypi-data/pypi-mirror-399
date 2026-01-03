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
from bstack_utils.bstack1lllllll1l_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1llll111_opy_(object):
  bstack1l11lll11l_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠨࢀࠪា")), bstack1l1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩិ"))
  bstack11l1lll1ll1_opy_ = os.path.join(bstack1l11lll11l_opy_, bstack1l1l_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡷ࠳ࡰࡳࡰࡰࠪី"))
  commands_to_wrap = None
  perform_scan = None
  bstack1l11l1ll1_opy_ = None
  bstack11llll1l1l_opy_ = None
  bstack11ll11l1l1l_opy_ = None
  bstack11l1lllll11_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack1l1l_opy_ (u"ࠫ࡮ࡴࡳࡵࡣࡱࡧࡪ࠭ឹ")):
      cls.instance = super(bstack11l1llll111_opy_, cls).__new__(cls)
      cls.instance.bstack11l1lll1l11_opy_()
    return cls.instance
  def bstack11l1lll1l11_opy_(self):
    try:
      with open(self.bstack11l1lll1ll1_opy_, bstack1l1l_opy_ (u"ࠬࡸࠧឺ")) as bstack11llll1111_opy_:
        bstack11l1lll1lll_opy_ = bstack11llll1111_opy_.read()
        data = json.loads(bstack11l1lll1lll_opy_)
        if bstack1l1l_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨុ") in data:
          self.bstack11ll11llll1_opy_(data[bstack1l1l_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࡴࠩូ")])
        if bstack1l1l_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩួ") in data:
          self.bstack11l1l1l11_opy_(data[bstack1l1l_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪើ")])
        if bstack1l1l_opy_ (u"ࠪࡲࡴࡴࡂࡔࡶࡤࡧࡰࡏ࡮ࡧࡴࡤࡅ࠶࠷ࡹࡄࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧឿ") in data:
          self.bstack11l1lll1l1l_opy_(data[bstack1l1l_opy_ (u"ࠫࡳࡵ࡮ࡃࡕࡷࡥࡨࡱࡉ࡯ࡨࡵࡥࡆ࠷࠱ࡺࡅ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨៀ")])
    except:
      pass
  def bstack11l1lll1l1l_opy_(self, bstack11l1lllll11_opy_):
    if bstack11l1lllll11_opy_ != None:
      self.bstack11l1lllll11_opy_ = bstack11l1lllll11_opy_
  def bstack11l1l1l11_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack1l1l_opy_ (u"ࠬࡹࡣࡢࡰࠪេ"),bstack1l1l_opy_ (u"࠭ࠧែ"))
      self.bstack1l11l1ll1_opy_ = scripts.get(bstack1l1l_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠫៃ"),bstack1l1l_opy_ (u"ࠨࠩោ"))
      self.bstack11llll1l1l_opy_ = scripts.get(bstack1l1l_opy_ (u"ࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾ࠭ៅ"),bstack1l1l_opy_ (u"ࠪࠫំ"))
      self.bstack11ll11l1l1l_opy_ = scripts.get(bstack1l1l_opy_ (u"ࠫࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠩះ"),bstack1l1l_opy_ (u"ࠬ࠭ៈ"))
  def bstack11ll11llll1_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1lll1ll1_opy_, bstack1l1l_opy_ (u"࠭ࡷࠨ៉")) as file:
        json.dump({
          bstack1l1l_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡴࠤ៊"): self.commands_to_wrap,
          bstack1l1l_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࡴࠤ់"): {
            bstack1l1l_opy_ (u"ࠤࡶࡧࡦࡴࠢ៌"): self.perform_scan,
            bstack1l1l_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠢ៍"): self.bstack1l11l1ll1_opy_,
            bstack1l1l_opy_ (u"ࠦ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠣ៎"): self.bstack11llll1l1l_opy_,
            bstack1l1l_opy_ (u"ࠧࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠥ៏"): self.bstack11ll11l1l1l_opy_
          },
          bstack1l1l_opy_ (u"ࠨ࡮ࡰࡰࡅࡗࡹࡧࡣ࡬ࡋࡱࡪࡷࡧࡁ࠲࠳ࡼࡇ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠥ័"): self.bstack11l1lllll11_opy_
        }, file)
    except Exception as e:
      logger.error(bstack1l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡹࡴࡰࡴ࡬ࡲ࡬ࠦࡣࡰ࡯ࡰࡥࡳࡪࡳ࠻ࠢࡾࢁࠧ៑").format(e))
      pass
  def bstack1ll1l1111_opy_(self, command_name):
    try:
      return any(command.get(bstack1l1l_opy_ (u"ࠨࡰࡤࡱࡪ្࠭")) == command_name for command in self.commands_to_wrap)
    except:
      return False
bstack111111lll_opy_ = bstack11l1llll111_opy_()