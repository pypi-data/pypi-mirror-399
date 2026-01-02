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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack111ll1lll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack111l111l1_opy_ import bstack11l111l11_opy_
class bstack11l111l1ll_opy_:
  working_dir = os.getcwd()
  bstack11lllll1l_opy_ = False
  config = {}
  bstack111l1llllll_opy_ = bstack11111l_opy_ (u"࠭ࠧ὇")
  binary_path = bstack11111l_opy_ (u"ࠧࠨὈ")
  bstack111111l11l1_opy_ = bstack11111l_opy_ (u"ࠨࠩὉ")
  bstack1l11lll11_opy_ = False
  bstack111111ll111_opy_ = None
  bstack1llllllll11l_opy_ = {}
  bstack1111111111l_opy_ = 300
  bstack11111l11l1l_opy_ = False
  logger = None
  bstack111111111l1_opy_ = False
  bstack1l1111llll_opy_ = False
  percy_build_id = None
  bstack111111l1111_opy_ = bstack11111l_opy_ (u"ࠩࠪὊ")
  bstack1llllllll1l1_opy_ = {
    bstack11111l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪὋ") : 1,
    bstack11111l_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬὌ") : 2,
    bstack11111l_opy_ (u"ࠬ࡫ࡤࡨࡧࠪὍ") : 3,
    bstack11111l_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮࠭὎") : 4
  }
  def __init__(self) -> None: pass
  def bstack111111llll1_opy_(self):
    bstack1111111l1l1_opy_ = bstack11111l_opy_ (u"ࠧࠨ὏")
    bstack111111l1lll_opy_ = sys.platform
    bstack11111l111l1_opy_ = bstack11111l_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧὐ")
    if re.match(bstack11111l_opy_ (u"ࠤࡧࡥࡷࡽࡩ࡯ࡾࡰࡥࡨࠦ࡯ࡴࠤὑ"), bstack111111l1lll_opy_) != None:
      bstack1111111l1l1_opy_ = bstack11l11lll11l_opy_ + bstack11111l_opy_ (u"ࠥ࠳ࡵ࡫ࡲࡤࡻ࠰ࡳࡸࡾ࠮ࡻ࡫ࡳࠦὒ")
      self.bstack111111l1111_opy_ = bstack11111l_opy_ (u"ࠫࡲࡧࡣࠨὓ")
    elif re.match(bstack11111l_opy_ (u"ࠧࡳࡳࡸ࡫ࡱࢀࡲࡹࡹࡴࡾࡰ࡭ࡳ࡭ࡷࡽࡥࡼ࡫ࡼ࡯࡮ࡽࡤࡦࡧࡼ࡯࡮ࡽࡹ࡬ࡲࡨ࡫ࡼࡦ࡯ࡦࢀࡼ࡯࡮࠴࠴ࠥὔ"), bstack111111l1lll_opy_) != None:
      bstack1111111l1l1_opy_ = bstack11l11lll11l_opy_ + bstack11111l_opy_ (u"ࠨ࠯ࡱࡧࡵࡧࡾ࠳ࡷࡪࡰ࠱ࡾ࡮ࡶࠢὕ")
      bstack11111l111l1_opy_ = bstack11111l_opy_ (u"ࠢࡱࡧࡵࡧࡾ࠴ࡥࡹࡧࠥὖ")
      self.bstack111111l1111_opy_ = bstack11111l_opy_ (u"ࠨࡹ࡬ࡲࠬὗ")
    else:
      bstack1111111l1l1_opy_ = bstack11l11lll11l_opy_ + bstack11111l_opy_ (u"ࠤ࠲ࡴࡪࡸࡣࡺ࠯࡯࡭ࡳࡻࡸ࠯ࡼ࡬ࡴࠧ὘")
      self.bstack111111l1111_opy_ = bstack11111l_opy_ (u"ࠪࡰ࡮ࡴࡵࡹࠩὙ")
    return bstack1111111l1l1_opy_, bstack11111l111l1_opy_
  def bstack11111l1ll1l_opy_(self):
    try:
      bstack11111111l1l_opy_ = [os.path.join(expanduser(bstack11111l_opy_ (u"ࠦࢃࠨ὚")), bstack11111l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬὛ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack11111111l1l_opy_:
        if(self.bstack11111ll11l1_opy_(path)):
          return path
      raise bstack11111l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠥ὜")
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨࠤࡵࡧࡴࡩࠢࡩࡳࡷࠦࡰࡦࡴࡦࡽࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࠲ࠦࡻࡾࠤὝ").format(e))
  def bstack11111ll11l1_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack11111ll111l_opy_(self, bstack11111l1ll11_opy_):
    return os.path.join(bstack11111l1ll11_opy_, self.bstack111l1llllll_opy_ + bstack11111l_opy_ (u"ࠣ࠰ࡨࡸࡦ࡭ࠢ὞"))
  def bstack1llllllll111_opy_(self, bstack11111l1ll11_opy_, bstack11111l11111_opy_):
    if not bstack11111l11111_opy_: return
    try:
      bstack1111111l11l_opy_ = self.bstack11111ll111l_opy_(bstack11111l1ll11_opy_)
      with open(bstack1111111l11l_opy_, bstack11111l_opy_ (u"ࠤࡺࠦὟ")) as f:
        f.write(bstack11111l11111_opy_)
        self.logger.debug(bstack11111l_opy_ (u"ࠥࡗࡦࡼࡥࡥࠢࡱࡩࡼࠦࡅࡕࡣࡪࠤ࡫ࡵࡲࠡࡲࡨࡶࡨࡿࠢὠ"))
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡣࡹࡩࠥࡺࡨࡦࠢࡨࡸࡦ࡭ࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠦὡ").format(e))
  def bstack1lllllllll1l_opy_(self, bstack11111l1ll11_opy_):
    try:
      bstack1111111l11l_opy_ = self.bstack11111ll111l_opy_(bstack11111l1ll11_opy_)
      if os.path.exists(bstack1111111l11l_opy_):
        with open(bstack1111111l11l_opy_, bstack11111l_opy_ (u"ࠧࡸࠢὢ")) as f:
          bstack11111l11111_opy_ = f.read().strip()
          return bstack11111l11111_opy_ if bstack11111l11111_opy_ else None
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡆࡖࡤ࡫࠱ࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤὣ").format(e))
  def bstack1lllllll1l1l_opy_(self, bstack11111l1ll11_opy_, bstack1111111l1l1_opy_):
    bstack1111111l111_opy_ = self.bstack1lllllllll1l_opy_(bstack11111l1ll11_opy_)
    if bstack1111111l111_opy_:
      try:
        bstack1111111llll_opy_ = self.bstack111111lllll_opy_(bstack1111111l111_opy_, bstack1111111l1l1_opy_)
        if not bstack1111111llll_opy_:
          self.logger.debug(bstack11111l_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡩࡴࠢࡸࡴࠥࡺ࡯ࠡࡦࡤࡸࡪࠦࠨࡆࡖࡤ࡫ࠥࡻ࡮ࡤࡪࡤࡲ࡬࡫ࡤࠪࠤὤ"))
          return True
        self.logger.debug(bstack11111l_opy_ (u"ࠣࡐࡨࡻࠥࡖࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡶࡲࡧࡥࡹ࡫ࠢὥ"))
        return False
      except Exception as e:
        self.logger.warn(bstack11111l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡩࡨࡦࡥ࡮ࠤ࡫ࡵࡲࠡࡤ࡬ࡲࡦࡸࡹࠡࡷࡳࡨࡦࡺࡥࡴ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡧ࡯࡮ࡢࡴࡼ࠾ࠥࢁࡽࠣὦ").format(e))
    return False
  def bstack111111lllll_opy_(self, bstack1111111l111_opy_, bstack1111111l1l1_opy_):
    try:
      headers = {
        bstack11111l_opy_ (u"ࠥࡍ࡫࠳ࡎࡰࡰࡨ࠱ࡒࡧࡴࡤࡪࠥὧ"): bstack1111111l111_opy_
      }
      response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"ࠫࡌࡋࡔࠨὨ"), bstack1111111l1l1_opy_, {}, {bstack11111l_opy_ (u"ࠧ࡮ࡥࡢࡦࡨࡶࡸࠨὩ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack11111l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡩࡨࡦࡥ࡮࡭ࡳ࡭ࠠࡧࡱࡵࠤࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡹࡵࡪࡡࡵࡧࡶ࠾ࠥࢁࡽࠣὪ").format(e))
  @measure(event_name=EVENTS.bstack11l1l11lll1_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
  def bstack111111lll1l_opy_(self, bstack1111111l1l1_opy_, bstack11111l111l1_opy_):
    try:
      bstack111111l11ll_opy_ = self.bstack11111l1ll1l_opy_()
      bstack11111l1l1l1_opy_ = os.path.join(bstack111111l11ll_opy_, bstack11111l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠴ࡺࡪࡲࠪὫ"))
      bstack11111l11lll_opy_ = os.path.join(bstack111111l11ll_opy_, bstack11111l111l1_opy_)
      if self.bstack1lllllll1l1l_opy_(bstack111111l11ll_opy_, bstack1111111l1l1_opy_): # if bstack1lllllll1l11_opy_, bstack1l11lll1lll_opy_ bstack11111l11111_opy_ is bstack11111111ll1_opy_ to bstack111l1ll1l1l_opy_ version available (response 304)
        if os.path.exists(bstack11111l11lll_opy_):
          self.logger.info(bstack11111l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡱࡸࡲࡩࠦࡩ࡯ࠢࡾࢁ࠱ࠦࡳ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠥὬ").format(bstack11111l11lll_opy_))
          return bstack11111l11lll_opy_
        if os.path.exists(bstack11111l1l1l1_opy_):
          self.logger.info(bstack11111l_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡼ࡬ࡴࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡼࡿ࠯ࠤࡺࡴࡺࡪࡲࡳ࡭ࡳ࡭ࠢὭ").format(bstack11111l1l1l1_opy_))
          return self.bstack111111l1ll1_opy_(bstack11111l1l1l1_opy_, bstack11111l111l1_opy_)
      self.logger.info(bstack11111l_opy_ (u"ࠥࡈࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡴࡲࡱࠥࢁࡽࠣὮ").format(bstack1111111l1l1_opy_))
      response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"ࠫࡌࡋࡔࠨὯ"), bstack1111111l1l1_opy_, {}, {})
      if response.status_code == 200:
        bstack11111l1lll1_opy_ = response.headers.get(bstack11111l_opy_ (u"ࠧࡋࡔࡢࡩࠥὰ"), bstack11111l_opy_ (u"ࠨࠢά"))
        if bstack11111l1lll1_opy_:
          self.bstack1llllllll111_opy_(bstack111111l11ll_opy_, bstack11111l1lll1_opy_)
        with open(bstack11111l1l1l1_opy_, bstack11111l_opy_ (u"ࠧࡸࡤࠪὲ")) as file:
          file.write(response.content)
        self.logger.info(bstack11111l_opy_ (u"ࠣࡆࡲࡻࡳࡲ࡯ࡢࡦࡨࡨࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡦࡴࡤࠡࡵࡤࡺࡪࡪࠠࡢࡶࠣࡿࢂࠨέ").format(bstack11111l1l1l1_opy_))
        return self.bstack111111l1ll1_opy_(bstack11111l1l1l1_opy_, bstack11111l111l1_opy_)
      else:
        raise(bstack11111l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡵࡪࡨࠤ࡫࡯࡬ࡦ࠰ࠣࡗࡹࡧࡴࡶࡵࠣࡧࡴࡪࡥ࠻ࠢࡾࢁࠧὴ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿ࠺ࠡࡽࢀࠦή").format(e))
  def bstack11111l1llll_opy_(self, bstack1111111l1l1_opy_, bstack11111l111l1_opy_):
    try:
      retry = 2
      bstack11111l11lll_opy_ = None
      bstack11111l11ll1_opy_ = False
      while retry > 0:
        bstack11111l11lll_opy_ = self.bstack111111lll1l_opy_(bstack1111111l1l1_opy_, bstack11111l111l1_opy_)
        bstack11111l11ll1_opy_ = self.bstack111111l1l1l_opy_(bstack1111111l1l1_opy_, bstack11111l111l1_opy_, bstack11111l11lll_opy_)
        if bstack11111l11ll1_opy_:
          break
        retry -= 1
      return bstack11111l11lll_opy_, bstack11111l11ll1_opy_
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡷࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡴࡦࡺࡨࠣὶ").format(e))
    return bstack11111l11lll_opy_, False
  def bstack111111l1l1l_opy_(self, bstack1111111l1l1_opy_, bstack11111l111l1_opy_, bstack11111l11lll_opy_, bstack1lllllll1lll_opy_ = 0):
    if bstack1lllllll1lll_opy_ > 1:
      return False
    if bstack11111l11lll_opy_ == None or os.path.exists(bstack11111l11lll_opy_) == False:
      self.logger.warn(bstack11111l_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡵࡧࡴࡩࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨ࠱ࠦࡲࡦࡶࡵࡽ࡮ࡴࡧࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠥί"))
      return False
    bstack111111lll11_opy_ = bstack11111l_opy_ (u"ࡸࠢ࡟࠰࠭ࡄࡵ࡫ࡲࡤࡻ࠲ࡧࡱ࡯ࠠ࡝ࡦ࠮ࡠ࠳ࡢࡤࠬ࡞࠱ࡠࡩ࠱ࠢὸ")
    command = bstack11111l_opy_ (u"ࠧࡼࡿࠣ࠱࠲ࡼࡥࡳࡵ࡬ࡳࡳ࠭ό").format(bstack11111l11lll_opy_)
    bstack1111111lll1_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack111111lll11_opy_, bstack1111111lll1_opy_) != None:
      return True
    else:
      self.logger.error(bstack11111l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡥ࡫ࡩࡨࡱࠠࡧࡣ࡬ࡰࡪࡪࠢὺ"))
      return False
  def bstack111111l1ll1_opy_(self, bstack11111l1l1l1_opy_, bstack11111l111l1_opy_):
    try:
      working_dir = os.path.dirname(bstack11111l1l1l1_opy_)
      shutil.unpack_archive(bstack11111l1l1l1_opy_, working_dir)
      bstack11111l11lll_opy_ = os.path.join(working_dir, bstack11111l111l1_opy_)
      os.chmod(bstack11111l11lll_opy_, 0o755)
      return bstack11111l11lll_opy_
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡻ࡮ࡻ࡫ࡳࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠥύ"))
  def bstack1lllllll1ll1_opy_(self):
    try:
      bstack11111l111ll_opy_ = self.config.get(bstack11111l_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩὼ"))
      bstack1lllllll1ll1_opy_ = bstack11111l111ll_opy_ or (bstack11111l111ll_opy_ is None and self.bstack11lllll1l_opy_)
      if not bstack1lllllll1ll1_opy_ or self.config.get(bstack11111l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧώ"), None) not in bstack11l11llllll_opy_:
        return False
      self.bstack1l11lll11_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡩࡴࠡࡲࡨࡶࡨࡿࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢ὾").format(e))
  def bstack11111ll11ll_opy_(self):
    try:
      bstack11111ll11ll_opy_ = self.percy_capture_mode
      return bstack11111ll11ll_opy_
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡩࡹ࡫ࡣࡵࠢࡳࡩࡷࡩࡹࠡࡥࡤࡴࡹࡻࡲࡦࠢࡰࡳࡩ࡫ࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢ὿").format(e))
  def init(self, bstack11lllll1l_opy_, config, logger):
    self.bstack11lllll1l_opy_ = bstack11lllll1l_opy_
    self.config = config
    self.logger = logger
    if not self.bstack1lllllll1ll1_opy_():
      return
    self.bstack1llllllll11l_opy_ = config.get(bstack11111l_opy_ (u"ࠧࡱࡧࡵࡧࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᾀ"), {})
    self.percy_capture_mode = config.get(bstack11111l_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫᾁ"))
    try:
      bstack1111111l1l1_opy_, bstack11111l111l1_opy_ = self.bstack111111llll1_opy_()
      self.bstack111l1llllll_opy_ = bstack11111l111l1_opy_
      bstack11111l11lll_opy_, bstack11111l11ll1_opy_ = self.bstack11111l1llll_opy_(bstack1111111l1l1_opy_, bstack11111l111l1_opy_)
      if bstack11111l11ll1_opy_:
        self.binary_path = bstack11111l11lll_opy_
        thread = Thread(target=self.bstack1llllllllll1_opy_)
        thread.start()
      else:
        self.bstack111111111l1_opy_ = True
        self.logger.error(bstack11111l_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡴࡪࡸࡣࡺࠢࡳࡥࡹ࡮ࠠࡧࡱࡸࡲࡩࠦ࠭ࠡࡽࢀ࠰࡛ࠥ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡑࡧࡵࡧࡾࠨᾂ").format(bstack11111l11lll_opy_))
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦᾃ").format(e))
  def bstack11111l11l11_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack11111l_opy_ (u"ࠫࡱࡵࡧࠨᾄ"), bstack11111l_opy_ (u"ࠬࡶࡥࡳࡥࡼ࠲ࡱࡵࡧࠨᾅ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack11111l_opy_ (u"ࠨࡐࡶࡵ࡫࡭ࡳ࡭ࠠࡱࡧࡵࡧࡾࠦ࡬ࡰࡩࡶࠤࡦࡺࠠࡼࡿࠥᾆ").format(logfile))
      self.bstack111111l11l1_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡪࡺࠠࡱࡧࡵࡧࡾࠦ࡬ࡰࡩࠣࡴࡦࡺࡨ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᾇ").format(e))
  @measure(event_name=EVENTS.bstack11l1l11ll11_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
  def bstack1llllllllll1_opy_(self):
    bstack111111ll11l_opy_ = self.bstack111111l1l11_opy_()
    if bstack111111ll11l_opy_ == None:
      self.bstack111111111l1_opy_ = True
      self.logger.error(bstack11111l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡵࡱ࡮ࡩࡳࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠮ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼࠦᾈ"))
      return False
    bstack11111l1l111_opy_ = [bstack11111l_opy_ (u"ࠤࡤࡴࡵࡀࡥࡹࡧࡦ࠾ࡸࡺࡡࡳࡶࠥᾉ") if self.bstack11lllll1l_opy_ else bstack11111l_opy_ (u"ࠪࡩࡽ࡫ࡣ࠻ࡵࡷࡥࡷࡺࠧᾊ")]
    bstack111l111l111_opy_ = self.bstack11111ll1111_opy_()
    if bstack111l111l111_opy_ != None:
      bstack11111l1l111_opy_.append(bstack11111l_opy_ (u"ࠦ࠲ࡩࠠࡼࡿࠥᾋ").format(bstack111l111l111_opy_))
    env = os.environ.copy()
    env[bstack11111l_opy_ (u"ࠧࡖࡅࡓࡅ࡜ࡣ࡙ࡕࡋࡆࡐࠥᾌ")] = bstack111111ll11l_opy_
    env[bstack11111l_opy_ (u"ࠨࡔࡉࡡࡅ࡙ࡎࡒࡄࡠࡗࡘࡍࡉࠨᾍ")] = os.environ.get(bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᾎ"), bstack11111l_opy_ (u"ࠨࠩᾏ"))
    bstack1lllllllllll_opy_ = [self.binary_path]
    self.bstack11111l11l11_opy_()
    self.bstack111111ll111_opy_ = self.bstack11111l1111l_opy_(bstack1lllllllllll_opy_ + bstack11111l1l111_opy_, env)
    self.logger.debug(bstack11111l_opy_ (u"ࠤࡖࡸࡦࡸࡴࡪࡰࡪࠤࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠥᾐ"))
    bstack1lllllll1lll_opy_ = 0
    while self.bstack111111ll111_opy_.poll() == None:
      bstack111111111ll_opy_ = self.bstack1111111ll11_opy_()
      if bstack111111111ll_opy_:
        self.logger.debug(bstack11111l_opy_ (u"ࠥࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࠨᾑ"))
        self.bstack11111l11l1l_opy_ = True
        return True
      bstack1lllllll1lll_opy_ += 1
      self.logger.debug(bstack11111l_opy_ (u"ࠦࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠣࡖࡪࡺࡲࡺࠢ࠰ࠤࢀࢃࠢᾒ").format(bstack1lllllll1lll_opy_))
      time.sleep(2)
    self.logger.error(bstack11111l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡱࡧࡵࡧࡾ࠲ࠠࡉࡧࡤࡰࡹ࡮ࠠࡄࡪࡨࡧࡰࠦࡆࡢ࡫࡯ࡩࡩࠦࡡࡧࡶࡨࡶࠥࢁࡽࠡࡣࡷࡸࡪࡳࡰࡵࡵࠥᾓ").format(bstack1lllllll1lll_opy_))
    self.bstack111111111l1_opy_ = True
    return False
  def bstack1111111ll11_opy_(self, bstack1lllllll1lll_opy_ = 0):
    if bstack1lllllll1lll_opy_ > 10:
      return False
    try:
      bstack1llllllll1ll_opy_ = os.environ.get(bstack11111l_opy_ (u"࠭ࡐࡆࡔࡆ࡝ࡤ࡙ࡅࡓࡘࡈࡖࡤࡇࡄࡅࡔࡈࡗࡘ࠭ᾔ"), bstack11111l_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶ࠽࠹࠸࠹࠸ࠨᾕ"))
      bstack11111l1l1ll_opy_ = bstack1llllllll1ll_opy_ + bstack11l1l111lll_opy_
      response = requests.get(bstack11111l1l1ll_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack11111l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧᾖ"), {}).get(bstack11111l_opy_ (u"ࠩ࡬ࡨࠬᾗ"), None)
      return True
    except:
      self.logger.debug(bstack11111l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡲࡧࡨࡻࡲࡳࡧࡧࠤࡼ࡮ࡩ࡭ࡧࠣࡴࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡰࡹ࡮ࠠࡤࡪࡨࡧࡰࠦࡲࡦࡵࡳࡳࡳࡹࡥࠣᾘ"))
      return False
  def bstack111111l1l11_opy_(self):
    bstack111111ll1ll_opy_ = bstack11111l_opy_ (u"ࠫࡦࡶࡰࠨᾙ") if self.bstack11lllll1l_opy_ else bstack11111l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᾚ")
    bstack1111111l1ll_opy_ = bstack11111l_opy_ (u"ࠨࡵ࡯ࡦࡨࡪ࡮ࡴࡥࡥࠤᾛ") if self.config.get(bstack11111l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭ᾜ")) is None else True
    bstack11l1lll1l1l_opy_ = bstack11111l_opy_ (u"ࠣࡣࡳ࡭࠴ࡧࡰࡱࡡࡳࡩࡷࡩࡹ࠰ࡩࡨࡸࡤࡶࡲࡰ࡬ࡨࡧࡹࡥࡴࡰ࡭ࡨࡲࡄࡴࡡ࡮ࡧࡀࡿࢂࠬࡴࡺࡲࡨࡁࢀࢃࠦࡱࡧࡵࡧࡾࡃࡻࡾࠤᾝ").format(self.config[bstack11111l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᾞ")], bstack111111ll1ll_opy_, bstack1111111l1ll_opy_)
    if self.percy_capture_mode:
      bstack11l1lll1l1l_opy_ += bstack11111l_opy_ (u"ࠥࠪࡵ࡫ࡲࡤࡻࡢࡧࡦࡶࡴࡶࡴࡨࡣࡲࡵࡤࡦ࠿ࡾࢁࠧᾟ").format(self.percy_capture_mode)
    uri = bstack11l111l11_opy_(bstack11l1lll1l1l_opy_)
    try:
      response = bstack111ll1lll_opy_(bstack11111l_opy_ (u"ࠫࡌࡋࡔࠨᾠ"), uri, {}, {bstack11111l_opy_ (u"ࠬࡧࡵࡵࡪࠪᾡ"): (self.config[bstack11111l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨᾢ")], self.config[bstack11111l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᾣ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack1l11lll11_opy_ = data.get(bstack11111l_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᾤ"))
        self.percy_capture_mode = data.get(bstack11111l_opy_ (u"ࠩࡳࡩࡷࡩࡹࡠࡥࡤࡴࡹࡻࡲࡦࡡࡰࡳࡩ࡫ࠧᾥ"))
        os.environ[bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࠨᾦ")] = str(self.bstack1l11lll11_opy_)
        os.environ[bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࡡࡆࡅࡕ࡚ࡕࡓࡇࡢࡑࡔࡊࡅࠨᾧ")] = str(self.percy_capture_mode)
        if bstack1111111l1ll_opy_ == bstack11111l_opy_ (u"ࠧࡻ࡮ࡥࡧࡩ࡭ࡳ࡫ࡤࠣᾨ") and str(self.bstack1l11lll11_opy_).lower() == bstack11111l_opy_ (u"ࠨࡴࡳࡷࡨࠦᾩ"):
          self.bstack1l1111llll_opy_ = True
        if bstack11111l_opy_ (u"ࠢࡵࡱ࡮ࡩࡳࠨᾪ") in data:
          return data[bstack11111l_opy_ (u"ࠣࡶࡲ࡯ࡪࡴࠢᾫ")]
        else:
          raise bstack11111l_opy_ (u"ࠩࡗࡳࡰ࡫࡮ࠡࡐࡲࡸࠥࡌ࡯ࡶࡰࡧࠤ࠲ࠦࡻࡾࠩᾬ").format(data)
      else:
        raise bstack11111l_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡶࡥࡳࡥࡼࠤࡹࡵ࡫ࡦࡰ࠯ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡳࡵࡣࡷࡹࡸࠦ࠭ࠡࡽࢀ࠰ࠥࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡃࡱࡧࡽࠥ࠳ࠠࡼࡿࠥᾭ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡵࡸ࡯࡫ࡧࡦࡸࠧᾮ").format(e))
  def bstack11111ll1111_opy_(self):
    bstack1111111ll1l_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠧࡶࡥࡳࡥࡼࡇࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠣᾯ"))
    try:
      if bstack11111l_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧᾰ") not in self.bstack1llllllll11l_opy_:
        self.bstack1llllllll11l_opy_[bstack11111l_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨᾱ")] = 2
      with open(bstack1111111ll1l_opy_, bstack11111l_opy_ (u"ࠨࡹࠪᾲ")) as fp:
        json.dump(self.bstack1llllllll11l_opy_, fp)
      return bstack1111111ll1l_opy_
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡩࡲࡦࡣࡷࡩࠥࡶࡥࡳࡥࡼࠤࡨࡵ࡮ࡧ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᾳ").format(e))
  def bstack11111l1111l_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack111111l1111_opy_ == bstack11111l_opy_ (u"ࠪࡻ࡮ࡴࠧᾴ"):
        bstack1lllllllll11_opy_ = [bstack11111l_opy_ (u"ࠫࡨࡳࡤ࠯ࡧࡻࡩࠬ᾵"), bstack11111l_opy_ (u"ࠬ࠵ࡣࠨᾶ")]
        cmd = bstack1lllllllll11_opy_ + cmd
      cmd = bstack11111l_opy_ (u"࠭ࠠࠨᾷ").join(cmd)
      self.logger.debug(bstack11111l_opy_ (u"ࠢࡓࡷࡱࡲ࡮ࡴࡧࠡࡽࢀࠦᾸ").format(cmd))
      with open(self.bstack111111l11l1_opy_, bstack11111l_opy_ (u"ࠣࡣࠥᾹ")) as bstack11111ll1ll1_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack11111ll1ll1_opy_, text=True, stderr=bstack11111ll1ll1_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack111111111l1_opy_ = True
      self.logger.error(bstack11111l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻࠣࡻ࡮ࡺࡨࠡࡥࡰࡨࠥ࠳ࠠࡼࡿ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦᾺ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack11111l11l1l_opy_:
        self.logger.info(bstack11111l_opy_ (u"ࠥࡗࡹࡵࡰࡱ࡫ࡱ࡫ࠥࡖࡥࡳࡥࡼࠦΆ"))
        cmd = [self.binary_path, bstack11111l_opy_ (u"ࠦࡪࡾࡥࡤ࠼ࡶࡸࡴࡶࠢᾼ")]
        self.bstack11111l1111l_opy_(cmd)
        self.bstack11111l11l1l_opy_ = False
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡳࡵࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡸ࡫ࡷ࡬ࠥࡩ࡯࡮࡯ࡤࡲࡩࠦ࠭ࠡࡽࢀ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧ᾽").format(cmd, e))
  def bstack1ll1l1ll_opy_(self):
    if not self.bstack1l11lll11_opy_:
      return
    try:
      bstack11111111l11_opy_ = 0
      while not self.bstack11111l11l1l_opy_ and bstack11111111l11_opy_ < self.bstack1111111111l_opy_:
        if self.bstack111111111l1_opy_:
          self.logger.info(bstack11111l_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡹࡥࡵࡷࡳࠤ࡫ࡧࡩ࡭ࡧࡧࠦι"))
          return
        time.sleep(1)
        bstack11111111l11_opy_ += 1
      os.environ[bstack11111l_opy_ (u"ࠧࡑࡇࡕࡇ࡞ࡥࡂࡆࡕࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒ࠭᾿")] = str(self.bstack11111111lll_opy_())
      self.logger.info(bstack11111l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡴࡧࡷࡹࡵࠦࡣࡰ࡯ࡳࡰࡪࡺࡥࡥࠤ῀"))
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡥࡵࡷࡳࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥ῁").format(e))
  def bstack11111111lll_opy_(self):
    if self.bstack11lllll1l_opy_:
      return
    try:
      bstack11111ll1l11_opy_ = [platform[bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨῂ")].lower() for platform in self.config.get(bstack11111l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧῃ"), [])]
      bstack11111111111_opy_ = sys.maxsize
      bstack111111ll1l1_opy_ = bstack11111l_opy_ (u"ࠬ࠭ῄ")
      for browser in bstack11111ll1l11_opy_:
        if browser in self.bstack1llllllll1l1_opy_:
          bstack11111l1l11l_opy_ = self.bstack1llllllll1l1_opy_[browser]
        if bstack11111l1l11l_opy_ < bstack11111111111_opy_:
          bstack11111111111_opy_ = bstack11111l1l11l_opy_
          bstack111111ll1l1_opy_ = browser
      return bstack111111ll1l1_opy_
    except Exception as e:
      self.logger.error(bstack11111l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡣࡧࡶࡸࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢ῅").format(e))
  @classmethod
  def bstack11l11l1111_opy_(self):
    return os.getenv(bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࠬῆ"), bstack11111l_opy_ (u"ࠨࡈࡤࡰࡸ࡫ࠧῇ")).lower()
  @classmethod
  def bstack1l1ll11l_opy_(self):
    return os.getenv(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭Ὲ"), bstack11111l_opy_ (u"ࠪࠫΈ"))
  @classmethod
  def bstack1l1l11111ll_opy_(cls, value):
    cls.bstack1l1111llll_opy_ = value
  @classmethod
  def bstack11111ll1l1l_opy_(cls):
    return cls.bstack1l1111llll_opy_
  @classmethod
  def bstack1l1l11111l1_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack111111l111l_opy_(cls):
    return cls.percy_build_id