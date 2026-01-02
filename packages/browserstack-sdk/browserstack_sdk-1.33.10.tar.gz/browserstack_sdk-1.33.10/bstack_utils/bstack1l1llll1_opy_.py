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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l1ll1l1_opy_, bstack11l1l11llll_opy_, bstack11l1l1l111l_opy_
import tempfile
import json
bstack111l111l1ll_opy_ = os.getenv(bstack11111l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡇࡠࡈࡌࡐࡊࠨḙ"), None) or os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡥࡣࡷࡪ࠲ࡱࡵࡧࠣḚ"))
bstack111l11l1111_opy_ = os.path.join(bstack11111l_opy_ (u"ࠢ࡭ࡱࡪࠦḛ"), bstack11111l_opy_ (u"ࠨࡵࡧ࡯࠲ࡩ࡬ࡪ࠯ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠬḜ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack11111l_opy_ (u"ࠩࠨࠬࡦࡹࡣࡵ࡫ࡰࡩ࠮ࡹࠠ࡜ࠧࠫࡲࡦࡳࡥࠪࡵࡠ࡟ࠪ࠮࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠫࡶࡡࠥ࠳ࠠࠦࠪࡰࡩࡸࡹࡡࡨࡧࠬࡷࠬḝ"),
      datefmt=bstack11111l_opy_ (u"ࠪࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙࡚ࠪࠨḞ"),
      stream=sys.stdout
    )
  return logger
def bstack1ll1llll1l1_opy_():
  bstack111l11l11ll_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡈࡊࡈࡕࡈࠤḟ"), bstack11111l_opy_ (u"ࠧ࡬ࡡ࡭ࡵࡨࠦḠ"))
  return logging.DEBUG if bstack111l11l11ll_opy_.lower() == bstack11111l_opy_ (u"ࠨࡴࡳࡷࡨࠦḡ") else logging.INFO
def bstack1l1l1llllll_opy_():
  global bstack111l111l1ll_opy_
  if os.path.exists(bstack111l111l1ll_opy_):
    os.remove(bstack111l111l1ll_opy_)
  if os.path.exists(bstack111l11l1111_opy_):
    os.remove(bstack111l11l1111_opy_)
def bstack11l111llll_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l111l11l_opy_ = log_level
  if bstack11111l_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩḢ") in config and config[bstack11111l_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪḣ")] in bstack11l1l11llll_opy_:
    bstack111l111l11l_opy_ = bstack11l1l11llll_opy_[config[bstack11111l_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫḤ")]]
  if config.get(bstack11111l_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬḥ"), False):
    logging.getLogger().setLevel(bstack111l111l11l_opy_)
    return bstack111l111l11l_opy_
  global bstack111l111l1ll_opy_
  bstack11l111llll_opy_()
  bstack111l11ll1l1_opy_ = logging.Formatter(
    fmt=bstack11111l_opy_ (u"ࠫࠪ࠮ࡡࡴࡥࡷ࡭ࡲ࡫ࠩࡴࠢ࡞ࠩ࠭ࡴࡡ࡮ࡧࠬࡷࡢࡡࠥࠩ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨ࠭ࡸࡣࠠ࠮ࠢࠨࠬࡲ࡫ࡳࡴࡣࡪࡩ࠮ࡹࠧḦ"),
    datefmt=bstack11111l_opy_ (u"࡙ࠬࠫ࠮ࠧࡰ࠱ࠪࡪࡔࠦࡊ࠽ࠩࡒࡀࠥࡔ࡜ࠪḧ"),
  )
  bstack111l111l1l1_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l111l1ll_opy_)
  file_handler.setFormatter(bstack111l11ll1l1_opy_)
  bstack111l111l1l1_opy_.setFormatter(bstack111l11ll1l1_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l111l1l1_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack11111l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵ࠲ࡷ࡫࡭ࡰࡶࡨ࠲ࡷ࡫࡭ࡰࡶࡨࡣࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡵ࡮ࠨḨ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l111l1l1_opy_.setLevel(bstack111l111l11l_opy_)
  logging.getLogger().addHandler(bstack111l111l1l1_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l111l11l_opy_
def bstack111l11l111l_opy_(config):
  try:
    bstack111l11ll11l_opy_ = set(bstack11l1l1l111l_opy_)
    bstack111l11l1l1l_opy_ = bstack11111l_opy_ (u"ࠧࠨḩ")
    with open(bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯ࠫḪ")) as bstack111l11lll11_opy_:
      bstack111l111lll1_opy_ = bstack111l11lll11_opy_.read()
      bstack111l11l1l1l_opy_ = re.sub(bstack11111l_opy_ (u"ࡴࠪࡢ࠭ࡢࡳࠬࠫࡂࠧ࠳࠰ࠤ࡝ࡰࠪḫ"), bstack11111l_opy_ (u"ࠪࠫḬ"), bstack111l111lll1_opy_, flags=re.M)
      bstack111l11l1l1l_opy_ = re.sub(
        bstack11111l_opy_ (u"ࡶࠬࡤࠨ࡝ࡵ࠮࠭ࡄ࠮ࠧḭ") + bstack11111l_opy_ (u"ࠬࢂࠧḮ").join(bstack111l11ll11l_opy_) + bstack11111l_opy_ (u"࠭ࠩ࠯ࠬࠧࠫḯ"),
        bstack11111l_opy_ (u"ࡲࠨ࡞࠵࠾ࠥࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩḰ"),
        bstack111l11l1l1l_opy_, flags=re.M | re.I
      )
    def bstack111l11l11l1_opy_(dic):
      bstack111l11l1ll1_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l11ll11l_opy_:
          bstack111l11l1ll1_opy_[key] = bstack11111l_opy_ (u"ࠨ࡝ࡕࡉࡉࡇࡃࡕࡇࡇࡡࠬḱ")
        else:
          if isinstance(value, dict):
            bstack111l11l1ll1_opy_[key] = bstack111l11l11l1_opy_(value)
          else:
            bstack111l11l1ll1_opy_[key] = value
      return bstack111l11l1ll1_opy_
    bstack111l11l1ll1_opy_ = bstack111l11l11l1_opy_(config)
    return {
      bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠬḲ"): bstack111l11l1l1l_opy_,
      bstack11111l_opy_ (u"ࠪࡪ࡮ࡴࡡ࡭ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭ḳ"): json.dumps(bstack111l11l1ll1_opy_)
    }
  except Exception as e:
    return {}
def bstack111l11llll1_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack11111l_opy_ (u"ࠫࡱࡵࡧࠨḴ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l111l111_opy_ = os.path.join(log_dir, bstack11111l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠭ḵ"))
  if not os.path.exists(bstack111l111l111_opy_):
    bstack111l11l1l11_opy_ = {
      bstack11111l_opy_ (u"ࠨࡩ࡯࡫ࡳࡥࡹ࡮ࠢḶ"): str(inipath),
      bstack11111l_opy_ (u"ࠢࡳࡱࡲࡸࡵࡧࡴࡩࠤḷ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack11111l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧḸ")), bstack11111l_opy_ (u"ࠩࡺࠫḹ")) as bstack111l111ll1l_opy_:
      bstack111l111ll1l_opy_.write(json.dumps(bstack111l11l1l11_opy_))
def bstack111l111ll11_opy_():
  try:
    bstack111l111l111_opy_ = os.path.join(os.getcwd(), bstack11111l_opy_ (u"ࠪࡰࡴ࡭ࠧḺ"), bstack11111l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪḻ"))
    if os.path.exists(bstack111l111l111_opy_):
      with open(bstack111l111l111_opy_, bstack11111l_opy_ (u"ࠬࡸࠧḼ")) as bstack111l111ll1l_opy_:
        bstack111l11ll111_opy_ = json.load(bstack111l111ll1l_opy_)
      return bstack111l11ll111_opy_.get(bstack11111l_opy_ (u"࠭ࡩ࡯࡫ࡳࡥࡹ࡮ࠧḽ"), bstack11111l_opy_ (u"ࠧࠨḾ")), bstack111l11ll111_opy_.get(bstack11111l_opy_ (u"ࠨࡴࡲࡳࡹࡶࡡࡵࡪࠪḿ"), bstack11111l_opy_ (u"ࠩࠪṀ"))
  except:
    pass
  return None, None
def bstack111l11l1lll_opy_():
  try:
    bstack111l111l111_opy_ = os.path.join(os.getcwd(), bstack11111l_opy_ (u"ࠪࡰࡴ࡭ࠧṁ"), bstack11111l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪṂ"))
    if os.path.exists(bstack111l111l111_opy_):
      os.remove(bstack111l111l111_opy_)
  except:
    pass
def bstack1l111111l_opy_(config):
  try:
    from bstack_utils.helper import bstack11l11l1lll_opy_, bstack1111l1ll_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l111l1ll_opy_
    if config.get(bstack11111l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇࡵࡵࡱࡆࡥࡵࡺࡵࡳࡧࡏࡳ࡬ࡹࠧṃ"), False):
      return
    uuid = os.getenv(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫṄ")) if os.getenv(bstack11111l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬṅ")) else bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠣࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠥṆ"))
    if not uuid or uuid == bstack11111l_opy_ (u"ࠩࡱࡹࡱࡲࠧṇ"):
      return
    bstack111l11ll1ll_opy_ = [bstack11111l_opy_ (u"ࠪࡶࡪࡷࡵࡪࡴࡨࡱࡪࡴࡴࡴ࠰ࡷࡼࡹ࠭Ṉ"), bstack11111l_opy_ (u"ࠫࡕ࡯ࡰࡧ࡫࡯ࡩࠬṉ"), bstack11111l_opy_ (u"ࠬࡶࡹࡱࡴࡲ࡮ࡪࡩࡴ࠯ࡶࡲࡱࡱ࠭Ṋ"), bstack111l111l1ll_opy_, bstack111l11l1111_opy_]
    bstack111l11lll1l_opy_, root_path = bstack111l111ll11_opy_()
    if bstack111l11lll1l_opy_ != None:
      bstack111l11ll1ll_opy_.append(bstack111l11lll1l_opy_)
    if root_path != None:
      bstack111l11ll1ll_opy_.append(os.path.join(root_path, bstack11111l_opy_ (u"࠭ࡣࡰࡰࡩࡸࡪࡹࡴ࠯ࡲࡼࠫṋ")))
    bstack11l111llll_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠭࡭ࡱࡪࡷ࠲࠭Ṍ") + uuid + bstack11111l_opy_ (u"ࠨ࠰ࡷࡥࡷ࠴ࡧࡻࠩṍ"))
    with tarfile.open(output_file, bstack11111l_opy_ (u"ࠤࡺ࠾࡬ࢀࠢṎ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l11ll1ll_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l11l111l_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l111llll_opy_ = data.encode()
        tarinfo.size = len(bstack111l111llll_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l111llll_opy_))
    bstack11lll11ll1_opy_ = MultipartEncoder(
      fields= {
        bstack11111l_opy_ (u"ࠪࡨࡦࡺࡡࠨṏ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack11111l_opy_ (u"ࠫࡷࡨࠧṐ")), bstack11111l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲ࡼ࠲࡭ࡺࡪࡲࠪṑ")),
        bstack11111l_opy_ (u"࠭ࡣ࡭࡫ࡨࡲࡹࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨṒ"): uuid
      }
    )
    bstack111l1111lll_opy_ = bstack1111l1ll_opy_(cli.config, [bstack11111l_opy_ (u"ࠢࡢࡲ࡬ࡷࠧṓ"), bstack11111l_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣṔ"), bstack11111l_opy_ (u"ࠤࡸࡴࡱࡵࡡࡥࠤṕ")], bstack11l1l1ll1l1_opy_)
    response = requests.post(
      bstack11111l_opy_ (u"ࠥࡿࢂ࠵ࡣ࡭࡫ࡨࡲࡹ࠳࡬ࡰࡩࡶ࠳ࡺࡶ࡬ࡰࡣࡧࠦṖ").format(bstack111l1111lll_opy_),
      data=bstack11lll11ll1_opy_,
      headers={bstack11111l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪṗ"): bstack11lll11ll1_opy_.content_type},
      auth=(config[bstack11111l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧṘ")], config[bstack11111l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩṙ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack11111l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡵࡱ࡮ࡲࡥࡩࠦ࡬ࡰࡩࡶ࠾ࠥ࠭Ṛ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack11111l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡱࡨ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࡀࠧṛ") + str(e))
  finally:
    try:
      bstack1l1l1llllll_opy_()
      bstack111l11l1lll_opy_()
    except:
      pass