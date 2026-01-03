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
class RobotHandler():
    def __init__(self, args, logger, bstack11111111ll_opy_, bstack1lllllll1ll_opy_):
        self.args = args
        self.logger = logger
        self.bstack11111111ll_opy_ = bstack11111111ll_opy_
        self.bstack1lllllll1ll_opy_ = bstack1lllllll1ll_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack1111llll1l_opy_(bstack1llllll11l1_opy_):
        bstack1llllll1111_opy_ = []
        if bstack1llllll11l1_opy_:
            tokens = str(os.path.basename(bstack1llllll11l1_opy_)).split(bstack1l1l_opy_ (u"ࠥࡣࠧმ"))
            camelcase_name = bstack1l1l_opy_ (u"ࠦࠥࠨნ").join(t.title() for t in tokens)
            suite_name, bstack1lllll1llll_opy_ = os.path.splitext(camelcase_name)
            bstack1llllll1111_opy_.append(suite_name)
        return bstack1llllll1111_opy_
    @staticmethod
    def bstack1llllll111l_opy_(typename):
        if bstack1l1l_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣო") in typename:
            return bstack1l1l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢპ")
        return bstack1l1l_opy_ (u"ࠢࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠣჟ")