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
from bstack_utils.helper import bstack11l11llll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack111ll11l1_opy_ import bstack1l11llll1_opy_
class bstack111111l1_opy_:
  working_dir = os.getcwd()
  bstack11ll11ll1_opy_ = False
  config = {}
  bstack111lll11111_opy_ = bstack1l1l_opy_ (u"࠭ࠧ὎")
  binary_path = bstack1l1l_opy_ (u"ࠧࠨ὏")
  bstack11111l1ll11_opy_ = bstack1l1l_opy_ (u"ࠨࠩὐ")
  bstack11l1lllll_opy_ = False
  bstack111111l11ll_opy_ = None
  bstack111111lll1l_opy_ = {}
  bstack11111l111ll_opy_ = 300
  bstack111111l111l_opy_ = False
  logger = None
  bstack1111111l11l_opy_ = False
  bstack11l111l11l_opy_ = False
  percy_build_id = None
  bstack11111111lll_opy_ = bstack1l1l_opy_ (u"ࠩࠪὑ")
  bstack11111111111_opy_ = {
    bstack1l1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪὒ") : 1,
    bstack1l1l_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬὓ") : 2,
    bstack1l1l_opy_ (u"ࠬ࡫ࡤࡨࡧࠪὔ") : 3,
    bstack1l1l_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮࠭ὕ") : 4
  }
  def __init__(self) -> None: pass
  def bstack11111l1ll1l_opy_(self):
    bstack11111ll1l11_opy_ = bstack1l1l_opy_ (u"ࠧࠨὖ")
    bstack1llllllll1l1_opy_ = sys.platform
    bstack111111111l1_opy_ = bstack1l1l_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧὗ")
    if re.match(bstack1l1l_opy_ (u"ࠤࡧࡥࡷࡽࡩ࡯ࡾࡰࡥࡨࠦ࡯ࡴࠤ὘"), bstack1llllllll1l1_opy_) != None:
      bstack11111ll1l11_opy_ = bstack11l1l1lll1l_opy_ + bstack1l1l_opy_ (u"ࠥ࠳ࡵ࡫ࡲࡤࡻ࠰ࡳࡸࡾ࠮ࡻ࡫ࡳࠦὙ")
      self.bstack11111111lll_opy_ = bstack1l1l_opy_ (u"ࠫࡲࡧࡣࠨ὚")
    elif re.match(bstack1l1l_opy_ (u"ࠧࡳࡳࡸ࡫ࡱࢀࡲࡹࡹࡴࡾࡰ࡭ࡳ࡭ࡷࡽࡥࡼ࡫ࡼ࡯࡮ࡽࡤࡦࡧࡼ࡯࡮ࡽࡹ࡬ࡲࡨ࡫ࡼࡦ࡯ࡦࢀࡼ࡯࡮࠴࠴ࠥὛ"), bstack1llllllll1l1_opy_) != None:
      bstack11111ll1l11_opy_ = bstack11l1l1lll1l_opy_ + bstack1l1l_opy_ (u"ࠨ࠯ࡱࡧࡵࡧࡾ࠳ࡷࡪࡰ࠱ࡾ࡮ࡶࠢ὜")
      bstack111111111l1_opy_ = bstack1l1l_opy_ (u"ࠢࡱࡧࡵࡧࡾ࠴ࡥࡹࡧࠥὝ")
      self.bstack11111111lll_opy_ = bstack1l1l_opy_ (u"ࠨࡹ࡬ࡲࠬ὞")
    else:
      bstack11111ll1l11_opy_ = bstack11l1l1lll1l_opy_ + bstack1l1l_opy_ (u"ࠤ࠲ࡴࡪࡸࡣࡺ࠯࡯࡭ࡳࡻࡸ࠯ࡼ࡬ࡴࠧὟ")
      self.bstack11111111lll_opy_ = bstack1l1l_opy_ (u"ࠪࡰ࡮ࡴࡵࡹࠩὠ")
    return bstack11111ll1l11_opy_, bstack111111111l1_opy_
  def bstack11111ll11ll_opy_(self):
    try:
      bstack1llllllll111_opy_ = [os.path.join(expanduser(bstack1l1l_opy_ (u"ࠦࢃࠨὡ")), bstack1l1l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬὢ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack1llllllll111_opy_:
        if(self.bstack111111ll1l1_opy_(path)):
          return path
      raise bstack1l1l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠥὣ")
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨࠤࡵࡧࡴࡩࠢࡩࡳࡷࠦࡰࡦࡴࡦࡽࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࠲ࠦࡻࡾࠤὤ").format(e))
  def bstack111111ll1l1_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack111111llll1_opy_(self, bstack111111ll11l_opy_):
    return os.path.join(bstack111111ll11l_opy_, self.bstack111lll11111_opy_ + bstack1l1l_opy_ (u"ࠣ࠰ࡨࡸࡦ࡭ࠢὥ"))
  def bstack1llllllll11l_opy_(self, bstack111111ll11l_opy_, bstack11111l11l1l_opy_):
    if not bstack11111l11l1l_opy_: return
    try:
      bstack11111ll11l1_opy_ = self.bstack111111llll1_opy_(bstack111111ll11l_opy_)
      with open(bstack11111ll11l1_opy_, bstack1l1l_opy_ (u"ࠤࡺࠦὦ")) as f:
        f.write(bstack11111l11l1l_opy_)
        self.logger.debug(bstack1l1l_opy_ (u"ࠥࡗࡦࡼࡥࡥࠢࡱࡩࡼࠦࡅࡕࡣࡪࠤ࡫ࡵࡲࠡࡲࡨࡶࡨࡿࠢὧ"))
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡣࡹࡩࠥࡺࡨࡦࠢࡨࡸࡦ࡭ࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠦὨ").format(e))
  def bstack11111111l11_opy_(self, bstack111111ll11l_opy_):
    try:
      bstack11111ll11l1_opy_ = self.bstack111111llll1_opy_(bstack111111ll11l_opy_)
      if os.path.exists(bstack11111ll11l1_opy_):
        with open(bstack11111ll11l1_opy_, bstack1l1l_opy_ (u"ࠧࡸࠢὩ")) as f:
          bstack11111l11l1l_opy_ = f.read().strip()
          return bstack11111l11l1l_opy_ if bstack11111l11l1l_opy_ else None
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡆࡖࡤ࡫࠱ࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤὪ").format(e))
  def bstack1lllllllll11_opy_(self, bstack111111ll11l_opy_, bstack11111ll1l11_opy_):
    bstack1111111l111_opy_ = self.bstack11111111l11_opy_(bstack111111ll11l_opy_)
    if bstack1111111l111_opy_:
      try:
        bstack11111l11111_opy_ = self.bstack111111l1l11_opy_(bstack1111111l111_opy_, bstack11111ll1l11_opy_)
        if not bstack11111l11111_opy_:
          self.logger.debug(bstack1l1l_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡩࡴࠢࡸࡴࠥࡺ࡯ࠡࡦࡤࡸࡪࠦࠨࡆࡖࡤ࡫ࠥࡻ࡮ࡤࡪࡤࡲ࡬࡫ࡤࠪࠤὫ"))
          return True
        self.logger.debug(bstack1l1l_opy_ (u"ࠣࡐࡨࡻࠥࡖࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡶࡲࡧࡥࡹ࡫ࠢὬ"))
        return False
      except Exception as e:
        self.logger.warn(bstack1l1l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡩࡨࡦࡥ࡮ࠤ࡫ࡵࡲࠡࡤ࡬ࡲࡦࡸࡹࠡࡷࡳࡨࡦࡺࡥࡴ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡧ࡯࡮ࡢࡴࡼ࠾ࠥࢁࡽࠣὭ").format(e))
    return False
  def bstack111111l1l11_opy_(self, bstack1111111l111_opy_, bstack11111ll1l11_opy_):
    try:
      headers = {
        bstack1l1l_opy_ (u"ࠥࡍ࡫࠳ࡎࡰࡰࡨ࠱ࡒࡧࡴࡤࡪࠥὮ"): bstack1111111l111_opy_
      }
      response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"ࠫࡌࡋࡔࠨὯ"), bstack11111ll1l11_opy_, {}, {bstack1l1l_opy_ (u"ࠧ࡮ࡥࡢࡦࡨࡶࡸࠨὰ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack1l1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡩࡨࡦࡥ࡮࡭ࡳ࡭ࠠࡧࡱࡵࠤࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡹࡵࡪࡡࡵࡧࡶ࠾ࠥࢁࡽࠣά").format(e))
  @measure(event_name=EVENTS.bstack11l1l1llll1_opy_, stage=STAGE.bstack11lll1l1_opy_)
  def bstack11111l1l11l_opy_(self, bstack11111ll1l11_opy_, bstack111111111l1_opy_):
    try:
      bstack1llllllllll1_opy_ = self.bstack11111ll11ll_opy_()
      bstack1lllllll1l1l_opy_ = os.path.join(bstack1llllllllll1_opy_, bstack1l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠴ࡺࡪࡲࠪὲ"))
      bstack1lllllll1l11_opy_ = os.path.join(bstack1llllllllll1_opy_, bstack111111111l1_opy_)
      if self.bstack1lllllllll11_opy_(bstack1llllllllll1_opy_, bstack11111ll1l11_opy_): # if bstack11111l1l1ll_opy_, bstack1l11ll1l11l_opy_ bstack11111l11l1l_opy_ is bstack1111111111l_opy_ to bstack111ll11l1ll_opy_ version available (response 304)
        if os.path.exists(bstack1lllllll1l11_opy_):
          self.logger.info(bstack1l1l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡱࡸࡲࡩࠦࡩ࡯ࠢࡾࢁ࠱ࠦࡳ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠥέ").format(bstack1lllllll1l11_opy_))
          return bstack1lllllll1l11_opy_
        if os.path.exists(bstack1lllllll1l1l_opy_):
          self.logger.info(bstack1l1l_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡼ࡬ࡴࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡼࡿ࠯ࠤࡺࡴࡺࡪࡲࡳ࡭ࡳ࡭ࠢὴ").format(bstack1lllllll1l1l_opy_))
          return self.bstack111111l1l1l_opy_(bstack1lllllll1l1l_opy_, bstack111111111l1_opy_)
      self.logger.info(bstack1l1l_opy_ (u"ࠥࡈࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡴࡲࡱࠥࢁࡽࠣή").format(bstack11111ll1l11_opy_))
      response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"ࠫࡌࡋࡔࠨὶ"), bstack11111ll1l11_opy_, {}, {})
      if response.status_code == 200:
        bstack11111ll1111_opy_ = response.headers.get(bstack1l1l_opy_ (u"ࠧࡋࡔࡢࡩࠥί"), bstack1l1l_opy_ (u"ࠨࠢὸ"))
        if bstack11111ll1111_opy_:
          self.bstack1llllllll11l_opy_(bstack1llllllllll1_opy_, bstack11111ll1111_opy_)
        with open(bstack1lllllll1l1l_opy_, bstack1l1l_opy_ (u"ࠧࡸࡤࠪό")) as file:
          file.write(response.content)
        self.logger.info(bstack1l1l_opy_ (u"ࠣࡆࡲࡻࡳࡲ࡯ࡢࡦࡨࡨࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡦࡴࡤࠡࡵࡤࡺࡪࡪࠠࡢࡶࠣࡿࢂࠨὺ").format(bstack1lllllll1l1l_opy_))
        return self.bstack111111l1l1l_opy_(bstack1lllllll1l1l_opy_, bstack111111111l1_opy_)
      else:
        raise(bstack1l1l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡵࡪࡨࠤ࡫࡯࡬ࡦ࠰ࠣࡗࡹࡧࡴࡶࡵࠣࡧࡴࡪࡥ࠻ࠢࡾࢁࠧύ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿ࠺ࠡࡽࢀࠦὼ").format(e))
  def bstack11111111l1l_opy_(self, bstack11111ll1l11_opy_, bstack111111111l1_opy_):
    try:
      retry = 2
      bstack1lllllll1l11_opy_ = None
      bstack111111l1lll_opy_ = False
      while retry > 0:
        bstack1lllllll1l11_opy_ = self.bstack11111l1l11l_opy_(bstack11111ll1l11_opy_, bstack111111111l1_opy_)
        bstack111111l1lll_opy_ = self.bstack1llllllll1ll_opy_(bstack11111ll1l11_opy_, bstack111111111l1_opy_, bstack1lllllll1l11_opy_)
        if bstack111111l1lll_opy_:
          break
        retry -= 1
      return bstack1lllllll1l11_opy_, bstack111111l1lll_opy_
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡷࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡴࡦࡺࡨࠣώ").format(e))
    return bstack1lllllll1l11_opy_, False
  def bstack1llllllll1ll_opy_(self, bstack11111ll1l11_opy_, bstack111111111l1_opy_, bstack1lllllll1l11_opy_, bstack11111ll111l_opy_ = 0):
    if bstack11111ll111l_opy_ > 1:
      return False
    if bstack1lllllll1l11_opy_ == None or os.path.exists(bstack1lllllll1l11_opy_) == False:
      self.logger.warn(bstack1l1l_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡵࡧࡴࡩࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨ࠱ࠦࡲࡦࡶࡵࡽ࡮ࡴࡧࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠥ὾"))
      return False
    bstack1lllllllllll_opy_ = bstack1l1l_opy_ (u"ࡸࠢ࡟࠰࠭ࡄࡵ࡫ࡲࡤࡻ࠲ࡧࡱ࡯ࠠ࡝ࡦ࠮ࡠ࠳ࡢࡤࠬ࡞࠱ࡠࡩ࠱ࠢ὿")
    command = bstack1l1l_opy_ (u"ࠧࡼࡿࠣ࠱࠲ࡼࡥࡳࡵ࡬ࡳࡳ࠭ᾀ").format(bstack1lllllll1l11_opy_)
    bstack11111l11lll_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack1lllllllllll_opy_, bstack11111l11lll_opy_) != None:
      return True
    else:
      self.logger.error(bstack1l1l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡥ࡫ࡩࡨࡱࠠࡧࡣ࡬ࡰࡪࡪࠢᾁ"))
      return False
  def bstack111111l1l1l_opy_(self, bstack1lllllll1l1l_opy_, bstack111111111l1_opy_):
    try:
      working_dir = os.path.dirname(bstack1lllllll1l1l_opy_)
      shutil.unpack_archive(bstack1lllllll1l1l_opy_, working_dir)
      bstack1lllllll1l11_opy_ = os.path.join(working_dir, bstack111111111l1_opy_)
      os.chmod(bstack1lllllll1l11_opy_, 0o755)
      return bstack1lllllll1l11_opy_
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡻ࡮ࡻ࡫ࡳࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠥᾂ"))
  def bstack111111lllll_opy_(self):
    try:
      bstack1111111llll_opy_ = self.config.get(bstack1l1l_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩᾃ"))
      bstack111111lllll_opy_ = bstack1111111llll_opy_ or (bstack1111111llll_opy_ is None and self.bstack11ll11ll1_opy_)
      if not bstack111111lllll_opy_ or self.config.get(bstack1l1l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧᾄ"), None) not in bstack11l1l1ll1ll_opy_:
        return False
      self.bstack11l1lllll_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡩࡴࠡࡲࡨࡶࡨࡿࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢᾅ").format(e))
  def bstack1lllllll11ll_opy_(self):
    try:
      bstack1lllllll11ll_opy_ = self.percy_capture_mode
      return bstack1lllllll11ll_opy_
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡩࡹ࡫ࡣࡵࠢࡳࡩࡷࡩࡹࠡࡥࡤࡴࡹࡻࡲࡦࠢࡰࡳࡩ࡫ࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢᾆ").format(e))
  def init(self, bstack11ll11ll1_opy_, config, logger):
    self.bstack11ll11ll1_opy_ = bstack11ll11ll1_opy_
    self.config = config
    self.logger = logger
    if not self.bstack111111lllll_opy_():
      return
    self.bstack111111lll1l_opy_ = config.get(bstack1l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᾇ"), {})
    self.percy_capture_mode = config.get(bstack1l1l_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫᾈ"))
    try:
      bstack11111ll1l11_opy_, bstack111111111l1_opy_ = self.bstack11111l1ll1l_opy_()
      self.bstack111lll11111_opy_ = bstack111111111l1_opy_
      bstack1lllllll1l11_opy_, bstack111111l1lll_opy_ = self.bstack11111111l1l_opy_(bstack11111ll1l11_opy_, bstack111111111l1_opy_)
      if bstack111111l1lll_opy_:
        self.binary_path = bstack1lllllll1l11_opy_
        thread = Thread(target=self.bstack11111l11l11_opy_)
        thread.start()
      else:
        self.bstack1111111l11l_opy_ = True
        self.logger.error(bstack1l1l_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡴࡪࡸࡣࡺࠢࡳࡥࡹ࡮ࠠࡧࡱࡸࡲࡩࠦ࠭ࠡࡽࢀ࠰࡛ࠥ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡑࡧࡵࡧࡾࠨᾉ").format(bstack1lllllll1l11_opy_))
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦᾊ").format(e))
  def bstack111111lll11_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack1l1l_opy_ (u"ࠫࡱࡵࡧࠨᾋ"), bstack1l1l_opy_ (u"ࠬࡶࡥࡳࡥࡼ࠲ࡱࡵࡧࠨᾌ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack1l1l_opy_ (u"ࠨࡐࡶࡵ࡫࡭ࡳ࡭ࠠࡱࡧࡵࡧࡾࠦ࡬ࡰࡩࡶࠤࡦࡺࠠࡼࡿࠥᾍ").format(logfile))
      self.bstack11111l1ll11_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡪࡺࠠࡱࡧࡵࡧࡾࠦ࡬ࡰࡩࠣࡴࡦࡺࡨ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᾎ").format(e))
  @measure(event_name=EVENTS.bstack11l1l1l1111_opy_, stage=STAGE.bstack11lll1l1_opy_)
  def bstack11111l11l11_opy_(self):
    bstack111111ll111_opy_ = self.bstack11111l11ll1_opy_()
    if bstack111111ll111_opy_ == None:
      self.bstack1111111l11l_opy_ = True
      self.logger.error(bstack1l1l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡵࡱ࡮ࡩࡳࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠮ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼࠦᾏ"))
      return False
    bstack1111111lll1_opy_ = [bstack1l1l_opy_ (u"ࠤࡤࡴࡵࡀࡥࡹࡧࡦ࠾ࡸࡺࡡࡳࡶࠥᾐ") if self.bstack11ll11ll1_opy_ else bstack1l1l_opy_ (u"ࠪࡩࡽ࡫ࡣ࠻ࡵࡷࡥࡷࡺࠧᾑ")]
    bstack111l111l1ll_opy_ = self.bstack111111l1111_opy_()
    if bstack111l111l1ll_opy_ != None:
      bstack1111111lll1_opy_.append(bstack1l1l_opy_ (u"ࠦ࠲ࡩࠠࡼࡿࠥᾒ").format(bstack111l111l1ll_opy_))
    env = os.environ.copy()
    env[bstack1l1l_opy_ (u"ࠧࡖࡅࡓࡅ࡜ࡣ࡙ࡕࡋࡆࡐࠥᾓ")] = bstack111111ll111_opy_
    env[bstack1l1l_opy_ (u"ࠨࡔࡉࡡࡅ࡙ࡎࡒࡄࡠࡗࡘࡍࡉࠨᾔ")] = os.environ.get(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᾕ"), bstack1l1l_opy_ (u"ࠨࠩᾖ"))
    bstack1111111ll11_opy_ = [self.binary_path]
    self.bstack111111lll11_opy_()
    self.bstack111111l11ll_opy_ = self.bstack11111l1l111_opy_(bstack1111111ll11_opy_ + bstack1111111lll1_opy_, env)
    self.logger.debug(bstack1l1l_opy_ (u"ࠤࡖࡸࡦࡸࡴࡪࡰࡪࠤࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠥᾗ"))
    bstack11111ll111l_opy_ = 0
    while self.bstack111111l11ll_opy_.poll() == None:
      bstack11111l1lll1_opy_ = self.bstack111111l11l1_opy_()
      if bstack11111l1lll1_opy_:
        self.logger.debug(bstack1l1l_opy_ (u"ࠥࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࠨᾘ"))
        self.bstack111111l111l_opy_ = True
        return True
      bstack11111ll111l_opy_ += 1
      self.logger.debug(bstack1l1l_opy_ (u"ࠦࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠣࡖࡪࡺࡲࡺࠢ࠰ࠤࢀࢃࠢᾙ").format(bstack11111ll111l_opy_))
      time.sleep(2)
    self.logger.error(bstack1l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡱࡧࡵࡧࡾ࠲ࠠࡉࡧࡤࡰࡹ࡮ࠠࡄࡪࡨࡧࡰࠦࡆࡢ࡫࡯ࡩࡩࠦࡡࡧࡶࡨࡶࠥࢁࡽࠡࡣࡷࡸࡪࡳࡰࡵࡵࠥᾚ").format(bstack11111ll111l_opy_))
    self.bstack1111111l11l_opy_ = True
    return False
  def bstack111111l11l1_opy_(self, bstack11111ll111l_opy_ = 0):
    if bstack11111ll111l_opy_ > 10:
      return False
    try:
      bstack11111l1111l_opy_ = os.environ.get(bstack1l1l_opy_ (u"࠭ࡐࡆࡔࡆ࡝ࡤ࡙ࡅࡓࡘࡈࡖࡤࡇࡄࡅࡔࡈࡗࡘ࠭ᾛ"), bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶ࠽࠹࠸࠹࠸ࠨᾜ"))
      bstack11111l1llll_opy_ = bstack11111l1111l_opy_ + bstack11l1l11ll11_opy_
      response = requests.get(bstack11111l1llll_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack1l1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧᾝ"), {}).get(bstack1l1l_opy_ (u"ࠩ࡬ࡨࠬᾞ"), None)
      return True
    except:
      self.logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡲࡧࡨࡻࡲࡳࡧࡧࠤࡼ࡮ࡩ࡭ࡧࠣࡴࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡰࡹ࡮ࠠࡤࡪࡨࡧࡰࠦࡲࡦࡵࡳࡳࡳࡹࡥࠣᾟ"))
      return False
  def bstack11111l11ll1_opy_(self):
    bstack11111l111l1_opy_ = bstack1l1l_opy_ (u"ࠫࡦࡶࡰࠨᾠ") if self.bstack11ll11ll1_opy_ else bstack1l1l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᾡ")
    bstack1lllllllll1l_opy_ = bstack1l1l_opy_ (u"ࠨࡵ࡯ࡦࡨࡪ࡮ࡴࡥࡥࠤᾢ") if self.config.get(bstack1l1l_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭ᾣ")) is None else True
    bstack11l1lll11ll_opy_ = bstack1l1l_opy_ (u"ࠣࡣࡳ࡭࠴ࡧࡰࡱࡡࡳࡩࡷࡩࡹ࠰ࡩࡨࡸࡤࡶࡲࡰ࡬ࡨࡧࡹࡥࡴࡰ࡭ࡨࡲࡄࡴࡡ࡮ࡧࡀࡿࢂࠬࡴࡺࡲࡨࡁࢀࢃࠦࡱࡧࡵࡧࡾࡃࡻࡾࠤᾤ").format(self.config[bstack1l1l_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᾥ")], bstack11111l111l1_opy_, bstack1lllllllll1l_opy_)
    if self.percy_capture_mode:
      bstack11l1lll11ll_opy_ += bstack1l1l_opy_ (u"ࠥࠪࡵ࡫ࡲࡤࡻࡢࡧࡦࡶࡴࡶࡴࡨࡣࡲࡵࡤࡦ࠿ࡾࢁࠧᾦ").format(self.percy_capture_mode)
    uri = bstack1l11llll1_opy_(bstack11l1lll11ll_opy_)
    try:
      response = bstack11l11llll_opy_(bstack1l1l_opy_ (u"ࠫࡌࡋࡔࠨᾧ"), uri, {}, {bstack1l1l_opy_ (u"ࠬࡧࡵࡵࡪࠪᾨ"): (self.config[bstack1l1l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨᾩ")], self.config[bstack1l1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᾪ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack11l1lllll_opy_ = data.get(bstack1l1l_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᾫ"))
        self.percy_capture_mode = data.get(bstack1l1l_opy_ (u"ࠩࡳࡩࡷࡩࡹࡠࡥࡤࡴࡹࡻࡲࡦࡡࡰࡳࡩ࡫ࠧᾬ"))
        os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࠨᾭ")] = str(self.bstack11l1lllll_opy_)
        os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࡡࡆࡅࡕ࡚ࡕࡓࡇࡢࡑࡔࡊࡅࠨᾮ")] = str(self.percy_capture_mode)
        if bstack1lllllllll1l_opy_ == bstack1l1l_opy_ (u"ࠧࡻ࡮ࡥࡧࡩ࡭ࡳ࡫ࡤࠣᾯ") and str(self.bstack11l1lllll_opy_).lower() == bstack1l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦᾰ"):
          self.bstack11l111l11l_opy_ = True
        if bstack1l1l_opy_ (u"ࠢࡵࡱ࡮ࡩࡳࠨᾱ") in data:
          return data[bstack1l1l_opy_ (u"ࠣࡶࡲ࡯ࡪࡴࠢᾲ")]
        else:
          raise bstack1l1l_opy_ (u"ࠩࡗࡳࡰ࡫࡮ࠡࡐࡲࡸࠥࡌ࡯ࡶࡰࡧࠤ࠲ࠦࡻࡾࠩᾳ").format(data)
      else:
        raise bstack1l1l_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡶࡥࡳࡥࡼࠤࡹࡵ࡫ࡦࡰ࠯ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡳࡵࡣࡷࡹࡸࠦ࠭ࠡࡽࢀ࠰ࠥࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡃࡱࡧࡽࠥ࠳ࠠࡼࡿࠥᾴ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡵࡸ࡯࡫ࡧࡦࡸࠧ᾵").format(e))
  def bstack111111l1111_opy_(self):
    bstack1lllllll1lll_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠧࡶࡥࡳࡥࡼࡇࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠣᾶ"))
    try:
      if bstack1l1l_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧᾷ") not in self.bstack111111lll1l_opy_:
        self.bstack111111lll1l_opy_[bstack1l1l_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨᾸ")] = 2
      with open(bstack1lllllll1lll_opy_, bstack1l1l_opy_ (u"ࠨࡹࠪᾹ")) as fp:
        json.dump(self.bstack111111lll1l_opy_, fp)
      return bstack1lllllll1lll_opy_
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡩࡲࡦࡣࡷࡩࠥࡶࡥࡳࡥࡼࠤࡨࡵ࡮ࡧ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᾺ").format(e))
  def bstack11111l1l111_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack11111111lll_opy_ == bstack1l1l_opy_ (u"ࠪࡻ࡮ࡴࠧΆ"):
        bstack111111111ll_opy_ = [bstack1l1l_opy_ (u"ࠫࡨࡳࡤ࠯ࡧࡻࡩࠬᾼ"), bstack1l1l_opy_ (u"ࠬ࠵ࡣࠨ᾽")]
        cmd = bstack111111111ll_opy_ + cmd
      cmd = bstack1l1l_opy_ (u"࠭ࠠࠨι").join(cmd)
      self.logger.debug(bstack1l1l_opy_ (u"ࠢࡓࡷࡱࡲ࡮ࡴࡧࠡࡽࢀࠦ᾿").format(cmd))
      with open(self.bstack11111l1ll11_opy_, bstack1l1l_opy_ (u"ࠣࡣࠥ῀")) as bstack111111l1ll1_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack111111l1ll1_opy_, text=True, stderr=bstack111111l1ll1_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack1111111l11l_opy_ = True
      self.logger.error(bstack1l1l_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻࠣࡻ࡮ࡺࡨࠡࡥࡰࡨࠥ࠳ࠠࡼࡿ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦ῁").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack111111l111l_opy_:
        self.logger.info(bstack1l1l_opy_ (u"ࠥࡗࡹࡵࡰࡱ࡫ࡱ࡫ࠥࡖࡥࡳࡥࡼࠦῂ"))
        cmd = [self.binary_path, bstack1l1l_opy_ (u"ࠦࡪࡾࡥࡤ࠼ࡶࡸࡴࡶࠢῃ")]
        self.bstack11111l1l111_opy_(cmd)
        self.bstack111111l111l_opy_ = False
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡳࡵࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡸ࡫ࡷ࡬ࠥࡩ࡯࡮࡯ࡤࡲࡩࠦ࠭ࠡࡽࢀ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧῄ").format(cmd, e))
  def bstack1ll11111l1_opy_(self):
    if not self.bstack11l1lllll_opy_:
      return
    try:
      bstack1lllllll11l1_opy_ = 0
      while not self.bstack111111l111l_opy_ and bstack1lllllll11l1_opy_ < self.bstack11111l111ll_opy_:
        if self.bstack1111111l11l_opy_:
          self.logger.info(bstack1l1l_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡹࡥࡵࡷࡳࠤ࡫ࡧࡩ࡭ࡧࡧࠦ῅"))
          return
        time.sleep(1)
        bstack1lllllll11l1_opy_ += 1
      os.environ[bstack1l1l_opy_ (u"ࠧࡑࡇࡕࡇ࡞ࡥࡂࡆࡕࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒ࠭ῆ")] = str(self.bstack1111111l1l1_opy_())
      self.logger.info(bstack1l1l_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡴࡧࡷࡹࡵࠦࡣࡰ࡯ࡳࡰࡪࡺࡥࡥࠤῇ"))
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡥࡵࡷࡳࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥῈ").format(e))
  def bstack1111111l1l1_opy_(self):
    if self.bstack11ll11ll1_opy_:
      return
    try:
      bstack1lllllll1ll1_opy_ = [platform[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨΈ")].lower() for platform in self.config.get(bstack1l1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧῊ"), [])]
      bstack111111ll1ll_opy_ = sys.maxsize
      bstack11111l1l1l1_opy_ = bstack1l1l_opy_ (u"ࠬ࠭Ή")
      for browser in bstack1lllllll1ll1_opy_:
        if browser in self.bstack11111111111_opy_:
          bstack11111111ll1_opy_ = self.bstack11111111111_opy_[browser]
        if bstack11111111ll1_opy_ < bstack111111ll1ll_opy_:
          bstack111111ll1ll_opy_ = bstack11111111ll1_opy_
          bstack11111l1l1l1_opy_ = browser
      return bstack11111l1l1l1_opy_
    except Exception as e:
      self.logger.error(bstack1l1l_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡣࡧࡶࡸࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢῌ").format(e))
  @classmethod
  def bstack1l1l11111l_opy_(self):
    return os.getenv(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࠬ῍"), bstack1l1l_opy_ (u"ࠨࡈࡤࡰࡸ࡫ࠧ῎")).lower()
  @classmethod
  def bstack1lll11lll1_opy_(self):
    return os.getenv(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭῏"), bstack1l1l_opy_ (u"ࠪࠫῐ"))
  @classmethod
  def bstack1l1l1111lll_opy_(cls, value):
    cls.bstack11l111l11l_opy_ = value
  @classmethod
  def bstack1111111ll1l_opy_(cls):
    return cls.bstack11l111l11l_opy_
  @classmethod
  def bstack1l11llllll1_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack1111111l1ll_opy_(cls):
    return cls.percy_build_id