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
from browserstack_sdk.bstack1lll1ll1l1_opy_ import bstack1lllll1l1_opy_
from browserstack_sdk.bstack1111ll1111_opy_ import RobotHandler
def bstack11llll111l_opy_(framework):
    if framework.lower() == bstack11111l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ᭨"):
        return bstack1lllll1l1_opy_.version()
    elif framework.lower() == bstack11111l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ᭩"):
        return RobotHandler.version()
    elif framework.lower() == bstack11111l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ᭪"):
        import behave
        return behave.__version__
    else:
        return bstack11111l_opy_ (u"ࠬࡻ࡮࡬ࡰࡲࡻࡳ࠭᭫")
def bstack11ll1llll_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack11111l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨ᭬"))
        framework_version.append(importlib.metadata.version(bstack11111l_opy_ (u"ࠢࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠤ᭭")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬ᭮"))
        framework_version.append(importlib.metadata.version(bstack11111l_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨ᭯")))
    except:
        pass
    return {
        bstack11111l_opy_ (u"ࠪࡲࡦࡳࡥࠨ᭰"): bstack11111l_opy_ (u"ࠫࡤ࠭᭱").join(framework_name),
        bstack11111l_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭᭲"): bstack11111l_opy_ (u"࠭࡟ࠨ᭳").join(framework_version)
    }