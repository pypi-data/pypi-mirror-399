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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l111lll_opy_, bstack11l1l1ll111_opy_, bstack11l1l1lll11_opy_
import tempfile
import json
bstack111l111l1l1_opy_ = os.getenv(bstack1l1l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡇࡠࡈࡌࡐࡊࠨḠ"), None) or os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡥࡣࡷࡪ࠲ࡱࡵࡧࠣḡ"))
bstack111l1111ll1_opy_ = os.path.join(bstack1l1l_opy_ (u"ࠢ࡭ࡱࡪࠦḢ"), bstack1l1l_opy_ (u"ࠨࡵࡧ࡯࠲ࡩ࡬ࡪ࠯ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠬḣ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1l1l_opy_ (u"ࠩࠨࠬࡦࡹࡣࡵ࡫ࡰࡩ࠮ࡹࠠ࡜ࠧࠫࡲࡦࡳࡥࠪࡵࡠ࡟ࠪ࠮࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠫࡶࡡࠥ࠳ࠠࠦࠪࡰࡩࡸࡹࡡࡨࡧࠬࡷࠬḤ"),
      datefmt=bstack1l1l_opy_ (u"ࠪࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙࡚ࠪࠨḥ"),
      stream=sys.stdout
    )
  return logger
def bstack1ll1ll1ll11_opy_():
  bstack111l11ll11l_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡈࡊࡈࡕࡈࠤḦ"), bstack1l1l_opy_ (u"ࠧ࡬ࡡ࡭ࡵࡨࠦḧ"))
  return logging.DEBUG if bstack111l11ll11l_opy_.lower() == bstack1l1l_opy_ (u"ࠨࡴࡳࡷࡨࠦḨ") else logging.INFO
def bstack1l1l1ll1l1l_opy_():
  global bstack111l111l1l1_opy_
  if os.path.exists(bstack111l111l1l1_opy_):
    os.remove(bstack111l111l1l1_opy_)
  if os.path.exists(bstack111l1111ll1_opy_):
    os.remove(bstack111l1111ll1_opy_)
def bstack1lllll11l1_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l11ll111_opy_ = log_level
  if bstack1l1l_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩḩ") in config and config[bstack1l1l_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪḪ")] in bstack11l1l1ll111_opy_:
    bstack111l11ll111_opy_ = bstack11l1l1ll111_opy_[config[bstack1l1l_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫḫ")]]
  if config.get(bstack1l1l_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬḬ"), False):
    logging.getLogger().setLevel(bstack111l11ll111_opy_)
    return bstack111l11ll111_opy_
  global bstack111l111l1l1_opy_
  bstack1lllll11l1_opy_()
  bstack111l11l1lll_opy_ = logging.Formatter(
    fmt=bstack1l1l_opy_ (u"ࠫࠪ࠮ࡡࡴࡥࡷ࡭ࡲ࡫ࠩࡴࠢ࡞ࠩ࠭ࡴࡡ࡮ࡧࠬࡷࡢࡡࠥࠩ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨ࠭ࡸࡣࠠ࠮ࠢࠨࠬࡲ࡫ࡳࡴࡣࡪࡩ࠮ࡹࠧḭ"),
    datefmt=bstack1l1l_opy_ (u"࡙ࠬࠫ࠮ࠧࡰ࠱ࠪࡪࡔࠦࡊ࠽ࠩࡒࡀࠥࡔ࡜ࠪḮ"),
  )
  bstack111l111ll1l_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l111l1l1_opy_)
  file_handler.setFormatter(bstack111l11l1lll_opy_)
  bstack111l111ll1l_opy_.setFormatter(bstack111l11l1lll_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l111ll1l_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1l1l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵ࠲ࡷ࡫࡭ࡰࡶࡨ࠲ࡷ࡫࡭ࡰࡶࡨࡣࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡵ࡮ࠨḯ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l111ll1l_opy_.setLevel(bstack111l11ll111_opy_)
  logging.getLogger().addHandler(bstack111l111ll1l_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l11ll111_opy_
def bstack111l111lll1_opy_(config):
  try:
    bstack111l11l1l1l_opy_ = set(bstack11l1l1lll11_opy_)
    bstack111l111llll_opy_ = bstack1l1l_opy_ (u"ࠧࠨḰ")
    with open(bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯ࠫḱ")) as bstack111l11l1ll1_opy_:
      bstack111l11ll1l1_opy_ = bstack111l11l1ll1_opy_.read()
      bstack111l111llll_opy_ = re.sub(bstack1l1l_opy_ (u"ࡴࠪࡢ࠭ࡢࡳࠬࠫࡂࠧ࠳࠰ࠤ࡝ࡰࠪḲ"), bstack1l1l_opy_ (u"ࠪࠫḳ"), bstack111l11ll1l1_opy_, flags=re.M)
      bstack111l111llll_opy_ = re.sub(
        bstack1l1l_opy_ (u"ࡶࠬࡤࠨ࡝ࡵ࠮࠭ࡄ࠮ࠧḴ") + bstack1l1l_opy_ (u"ࠬࢂࠧḵ").join(bstack111l11l1l1l_opy_) + bstack1l1l_opy_ (u"࠭ࠩ࠯ࠬࠧࠫḶ"),
        bstack1l1l_opy_ (u"ࡲࠨ࡞࠵࠾ࠥࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩḷ"),
        bstack111l111llll_opy_, flags=re.M | re.I
      )
    def bstack111l11l11l1_opy_(dic):
      bstack111l1111lll_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l11l1l1l_opy_:
          bstack111l1111lll_opy_[key] = bstack1l1l_opy_ (u"ࠨ࡝ࡕࡉࡉࡇࡃࡕࡇࡇࡡࠬḸ")
        else:
          if isinstance(value, dict):
            bstack111l1111lll_opy_[key] = bstack111l11l11l1_opy_(value)
          else:
            bstack111l1111lll_opy_[key] = value
      return bstack111l1111lll_opy_
    bstack111l1111lll_opy_ = bstack111l11l11l1_opy_(config)
    return {
      bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠬḹ"): bstack111l111llll_opy_,
      bstack1l1l_opy_ (u"ࠪࡪ࡮ࡴࡡ࡭ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭Ḻ"): json.dumps(bstack111l1111lll_opy_)
    }
  except Exception as e:
    return {}
def bstack111l11l111l_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1l1l_opy_ (u"ࠫࡱࡵࡧࠨḻ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l111l1ll_opy_ = os.path.join(log_dir, bstack1l1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠭Ḽ"))
  if not os.path.exists(bstack111l111l1ll_opy_):
    bstack111l11l11ll_opy_ = {
      bstack1l1l_opy_ (u"ࠨࡩ࡯࡫ࡳࡥࡹ࡮ࠢḽ"): str(inipath),
      bstack1l1l_opy_ (u"ࠢࡳࡱࡲࡸࡵࡧࡴࡩࠤḾ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧḿ")), bstack1l1l_opy_ (u"ࠩࡺࠫṀ")) as bstack111l1111l1l_opy_:
      bstack111l1111l1l_opy_.write(json.dumps(bstack111l11l11ll_opy_))
def bstack111l11l1l11_opy_():
  try:
    bstack111l111l1ll_opy_ = os.path.join(os.getcwd(), bstack1l1l_opy_ (u"ࠪࡰࡴ࡭ࠧṁ"), bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪṂ"))
    if os.path.exists(bstack111l111l1ll_opy_):
      with open(bstack111l111l1ll_opy_, bstack1l1l_opy_ (u"ࠬࡸࠧṃ")) as bstack111l1111l1l_opy_:
        bstack111l11ll1ll_opy_ = json.load(bstack111l1111l1l_opy_)
      return bstack111l11ll1ll_opy_.get(bstack1l1l_opy_ (u"࠭ࡩ࡯࡫ࡳࡥࡹ࡮ࠧṄ"), bstack1l1l_opy_ (u"ࠧࠨṅ")), bstack111l11ll1ll_opy_.get(bstack1l1l_opy_ (u"ࠨࡴࡲࡳࡹࡶࡡࡵࡪࠪṆ"), bstack1l1l_opy_ (u"ࠩࠪṇ"))
  except:
    pass
  return None, None
def bstack111l11l1111_opy_():
  try:
    bstack111l111l1ll_opy_ = os.path.join(os.getcwd(), bstack1l1l_opy_ (u"ࠪࡰࡴ࡭ࠧṈ"), bstack1l1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪṉ"))
    if os.path.exists(bstack111l111l1ll_opy_):
      os.remove(bstack111l111l1ll_opy_)
  except:
    pass
def bstack1llll11lll_opy_(config):
  try:
    from bstack_utils.helper import bstack1l1ll1l1_opy_, bstack1ll1lll111_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l111l1l1_opy_
    if config.get(bstack1l1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇࡵࡵࡱࡆࡥࡵࡺࡵࡳࡧࡏࡳ࡬ࡹࠧṊ"), False):
      return
    uuid = os.getenv(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫṋ")) if os.getenv(bstack1l1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬṌ")) else bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠣࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠥṍ"))
    if not uuid or uuid == bstack1l1l_opy_ (u"ࠩࡱࡹࡱࡲࠧṎ"):
      return
    bstack111l111l11l_opy_ = [bstack1l1l_opy_ (u"ࠪࡶࡪࡷࡵࡪࡴࡨࡱࡪࡴࡴࡴ࠰ࡷࡼࡹ࠭ṏ"), bstack1l1l_opy_ (u"ࠫࡕ࡯ࡰࡧ࡫࡯ࡩࠬṐ"), bstack1l1l_opy_ (u"ࠬࡶࡹࡱࡴࡲ࡮ࡪࡩࡴ࠯ࡶࡲࡱࡱ࠭ṑ"), bstack111l111l1l1_opy_, bstack111l1111ll1_opy_]
    bstack111l111l111_opy_, root_path = bstack111l11l1l11_opy_()
    if bstack111l111l111_opy_ != None:
      bstack111l111l11l_opy_.append(bstack111l111l111_opy_)
    if root_path != None:
      bstack111l111l11l_opy_.append(os.path.join(root_path, bstack1l1l_opy_ (u"࠭ࡣࡰࡰࡩࡸࡪࡹࡴ࠯ࡲࡼࠫṒ")))
    bstack1lllll11l1_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠭࡭ࡱࡪࡷ࠲࠭ṓ") + uuid + bstack1l1l_opy_ (u"ࠨ࠰ࡷࡥࡷ࠴ࡧࡻࠩṔ"))
    with tarfile.open(output_file, bstack1l1l_opy_ (u"ࠤࡺ࠾࡬ࢀࠢṕ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l111l11l_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l111lll1_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l11lll11_opy_ = data.encode()
        tarinfo.size = len(bstack111l11lll11_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l11lll11_opy_))
    bstack111ll111l_opy_ = MultipartEncoder(
      fields= {
        bstack1l1l_opy_ (u"ࠪࡨࡦࡺࡡࠨṖ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1l1l_opy_ (u"ࠫࡷࡨࠧṗ")), bstack1l1l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲ࡼ࠲࡭ࡺࡪࡲࠪṘ")),
        bstack1l1l_opy_ (u"࠭ࡣ࡭࡫ࡨࡲࡹࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨṙ"): uuid
      }
    )
    bstack111l111ll11_opy_ = bstack1ll1lll111_opy_(cli.config, [bstack1l1l_opy_ (u"ࠢࡢࡲ࡬ࡷࠧṚ"), bstack1l1l_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣṛ"), bstack1l1l_opy_ (u"ࠤࡸࡴࡱࡵࡡࡥࠤṜ")], bstack11l1l111lll_opy_)
    response = requests.post(
      bstack1l1l_opy_ (u"ࠥࡿࢂ࠵ࡣ࡭࡫ࡨࡲࡹ࠳࡬ࡰࡩࡶ࠳ࡺࡶ࡬ࡰࡣࡧࠦṝ").format(bstack111l111ll11_opy_),
      data=bstack111ll111l_opy_,
      headers={bstack1l1l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪṞ"): bstack111ll111l_opy_.content_type},
      auth=(config[bstack1l1l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧṟ")], config[bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩṠ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1l1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡵࡱ࡮ࡲࡥࡩࠦ࡬ࡰࡩࡶ࠾ࠥ࠭ṡ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1l1l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡱࡨ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࡀࠧṢ") + str(e))
  finally:
    try:
      bstack1l1l1ll1l1l_opy_()
      bstack111l11l1111_opy_()
    except:
      pass