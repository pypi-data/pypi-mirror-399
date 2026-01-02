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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111l11111ll_opy_
bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
def bstack1lllll1ll1l1_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1lllll1ll11l_opy_(bstack1lllll1ll111_opy_, bstack1lllll1lll11_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1lllll1ll111_opy_):
        with open(bstack1lllll1ll111_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1lllll1ll1l1_opy_(bstack1lllll1ll111_opy_):
        pac = get_pac(url=bstack1lllll1ll111_opy_)
    else:
        raise Exception(bstack11111l_opy_ (u"ࠩࡓࡥࡨࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠩῤ").format(bstack1lllll1ll111_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack11111l_opy_ (u"ࠥ࠼࠳࠾࠮࠹࠰࠻ࠦῥ"), 80))
        bstack1lllll1ll1ll_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1lllll1ll1ll_opy_ = bstack11111l_opy_ (u"ࠫ࠵࠴࠰࠯࠲࠱࠴ࠬῦ")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1lllll1lll11_opy_, bstack1lllll1ll1ll_opy_)
    return proxy_url
def bstack11lll11l1_opy_(config):
    return bstack11111l_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨῧ") in config or bstack11111l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪῨ") in config
def bstack1l111l1l_opy_(config):
    if not bstack11lll11l1_opy_(config):
        return
    if config.get(bstack11111l_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪῩ")):
        return config.get(bstack11111l_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫῪ"))
    if config.get(bstack11111l_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭Ύ")):
        return config.get(bstack11111l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧῬ"))
def bstack1llllll1ll_opy_(config, bstack1lllll1lll11_opy_):
    proxy = bstack1l111l1l_opy_(config)
    proxies = {}
    if config.get(bstack11111l_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧ῭")) or config.get(bstack11111l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩ΅")):
        if proxy.endswith(bstack11111l_opy_ (u"࠭࠮ࡱࡣࡦࠫ`")):
            proxies = bstack1l11l11l11_opy_(proxy, bstack1lllll1lll11_opy_)
        else:
            proxies = {
                bstack11111l_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭῰"): proxy
            }
    bstack11l11l1lll_opy_.bstack1ll1lll11_opy_(bstack11111l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨ῱"), proxies)
    return proxies
def bstack1l11l11l11_opy_(bstack1lllll1ll111_opy_, bstack1lllll1lll11_opy_):
    proxies = {}
    global bstack1lllll1l1lll_opy_
    if bstack11111l_opy_ (u"ࠩࡓࡅࡈࡥࡐࡓࡑ࡛࡝ࠬῲ") in globals():
        return bstack1lllll1l1lll_opy_
    try:
        proxy = bstack1lllll1ll11l_opy_(bstack1lllll1ll111_opy_, bstack1lllll1lll11_opy_)
        if bstack11111l_opy_ (u"ࠥࡈࡎࡘࡅࡄࡖࠥῳ") in proxy:
            proxies = {}
        elif bstack11111l_opy_ (u"ࠦࡍ࡚ࡔࡑࠤῴ") in proxy or bstack11111l_opy_ (u"ࠧࡎࡔࡕࡒࡖࠦ῵") in proxy or bstack11111l_opy_ (u"ࠨࡓࡐࡅࡎࡗࠧῶ") in proxy:
            bstack1lllll1l1ll1_opy_ = proxy.split(bstack11111l_opy_ (u"ࠢࠡࠤῷ"))
            if bstack11111l_opy_ (u"ࠣ࠼࠲࠳ࠧῸ") in bstack11111l_opy_ (u"ࠤࠥΌ").join(bstack1lllll1l1ll1_opy_[1:]):
                proxies = {
                    bstack11111l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩῺ"): bstack11111l_opy_ (u"ࠦࠧΏ").join(bstack1lllll1l1ll1_opy_[1:])
                }
            else:
                proxies = {
                    bstack11111l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫῼ"): str(bstack1lllll1l1ll1_opy_[0]).lower() + bstack11111l_opy_ (u"ࠨ࠺࠰࠱ࠥ´") + bstack11111l_opy_ (u"ࠢࠣ῾").join(bstack1lllll1l1ll1_opy_[1:])
                }
        elif bstack11111l_opy_ (u"ࠣࡒࡕࡓ࡝࡟ࠢ῿") in proxy:
            bstack1lllll1l1ll1_opy_ = proxy.split(bstack11111l_opy_ (u"ࠤࠣࠦ "))
            if bstack11111l_opy_ (u"ࠥ࠾࠴࠵ࠢ ") in bstack11111l_opy_ (u"ࠦࠧ ").join(bstack1lllll1l1ll1_opy_[1:]):
                proxies = {
                    bstack11111l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫ "): bstack11111l_opy_ (u"ࠨࠢ ").join(bstack1lllll1l1ll1_opy_[1:])
                }
            else:
                proxies = {
                    bstack11111l_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭ "): bstack11111l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ ") + bstack11111l_opy_ (u"ࠤࠥ ").join(bstack1lllll1l1ll1_opy_[1:])
                }
        else:
            proxies = {
                bstack11111l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩ "): proxy
            }
    except Exception as e:
        print(bstack11111l_opy_ (u"ࠦࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠣ "), bstack111l11111ll_opy_.format(bstack1lllll1ll111_opy_, str(e)))
    bstack1lllll1l1lll_opy_ = proxies
    return proxies