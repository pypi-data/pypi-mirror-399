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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111l1111111_opy_
bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
def bstack1lllll1l1lll_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1lllll1l1l11_opy_(bstack1lllll1l1l1l_opy_, bstack1lllll1ll111_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1lllll1l1l1l_opy_):
        with open(bstack1lllll1l1l1l_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1lllll1l1lll_opy_(bstack1lllll1l1l1l_opy_):
        pac = get_pac(url=bstack1lllll1l1l1l_opy_)
    else:
        raise Exception(bstack1l1l_opy_ (u"ࠩࡓࡥࡨࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠩΎ").format(bstack1lllll1l1l1l_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack1l1l_opy_ (u"ࠥ࠼࠳࠾࠮࠹࠰࠻ࠦῬ"), 80))
        bstack1lllll1ll1l1_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1lllll1ll1l1_opy_ = bstack1l1l_opy_ (u"ࠫ࠵࠴࠰࠯࠲࠱࠴ࠬ῭")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1lllll1ll111_opy_, bstack1lllll1ll1l1_opy_)
    return proxy_url
def bstack1l1l1l1l1_opy_(config):
    return bstack1l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ΅") in config or bstack1l1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ`") in config
def bstack1l11ll1ll_opy_(config):
    if not bstack1l1l1l1l1_opy_(config):
        return
    if config.get(bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ῰")):
        return config.get(bstack1l1l_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫ῱"))
    if config.get(bstack1l1l_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ῲ")):
        return config.get(bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧῳ"))
def bstack1l11l1ll1l_opy_(config, bstack1lllll1ll111_opy_):
    proxy = bstack1l11ll1ll_opy_(config)
    proxies = {}
    if config.get(bstack1l1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧῴ")) or config.get(bstack1l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩ῵")):
        if proxy.endswith(bstack1l1l_opy_ (u"࠭࠮ࡱࡣࡦࠫῶ")):
            proxies = bstack11l1111ll_opy_(proxy, bstack1lllll1ll111_opy_)
        else:
            proxies = {
                bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭ῷ"): proxy
            }
    bstack1l1ll1l1_opy_.bstack1lll1111l_opy_(bstack1l1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨῸ"), proxies)
    return proxies
def bstack11l1111ll_opy_(bstack1lllll1l1l1l_opy_, bstack1lllll1ll111_opy_):
    proxies = {}
    global bstack1lllll1l1ll1_opy_
    if bstack1l1l_opy_ (u"ࠩࡓࡅࡈࡥࡐࡓࡑ࡛࡝ࠬΌ") in globals():
        return bstack1lllll1l1ll1_opy_
    try:
        proxy = bstack1lllll1l1l11_opy_(bstack1lllll1l1l1l_opy_, bstack1lllll1ll111_opy_)
        if bstack1l1l_opy_ (u"ࠥࡈࡎࡘࡅࡄࡖࠥῺ") in proxy:
            proxies = {}
        elif bstack1l1l_opy_ (u"ࠦࡍ࡚ࡔࡑࠤΏ") in proxy or bstack1l1l_opy_ (u"ࠧࡎࡔࡕࡒࡖࠦῼ") in proxy or bstack1l1l_opy_ (u"ࠨࡓࡐࡅࡎࡗࠧ´") in proxy:
            bstack1lllll1ll11l_opy_ = proxy.split(bstack1l1l_opy_ (u"ࠢࠡࠤ῾"))
            if bstack1l1l_opy_ (u"ࠣ࠼࠲࠳ࠧ῿") in bstack1l1l_opy_ (u"ࠤࠥ ").join(bstack1lllll1ll11l_opy_[1:]):
                proxies = {
                    bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩ "): bstack1l1l_opy_ (u"ࠦࠧ ").join(bstack1lllll1ll11l_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫ "): str(bstack1lllll1ll11l_opy_[0]).lower() + bstack1l1l_opy_ (u"ࠨ࠺࠰࠱ࠥ ") + bstack1l1l_opy_ (u"ࠢࠣ ").join(bstack1lllll1ll11l_opy_[1:])
                }
        elif bstack1l1l_opy_ (u"ࠣࡒࡕࡓ࡝࡟ࠢ ") in proxy:
            bstack1lllll1ll11l_opy_ = proxy.split(bstack1l1l_opy_ (u"ࠤࠣࠦ "))
            if bstack1l1l_opy_ (u"ࠥ࠾࠴࠵ࠢ ") in bstack1l1l_opy_ (u"ࠦࠧ ").join(bstack1lllll1ll11l_opy_[1:]):
                proxies = {
                    bstack1l1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫ "): bstack1l1l_opy_ (u"ࠨࠢ​").join(bstack1lllll1ll11l_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1l_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭‌"): bstack1l1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ‍") + bstack1l1l_opy_ (u"ࠤࠥ‎").join(bstack1lllll1ll11l_opy_[1:])
                }
        else:
            proxies = {
                bstack1l1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩ‏"): proxy
            }
    except Exception as e:
        print(bstack1l1l_opy_ (u"ࠦࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠣ‐"), bstack111l1111111_opy_.format(bstack1lllll1l1l1l_opy_, str(e)))
    bstack1lllll1l1ll1_opy_ = proxies
    return proxies