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
class RobotHandler():
    def __init__(self, args, logger, bstack1lllllll1ll_opy_, bstack11111l11l1_opy_):
        self.args = args
        self.logger = logger
        self.bstack1lllllll1ll_opy_ = bstack1lllllll1ll_opy_
        self.bstack11111l11l1_opy_ = bstack11111l11l1_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack1111lll1ll_opy_(bstack1llllll111l_opy_):
        bstack1lllll1llll_opy_ = []
        if bstack1llllll111l_opy_:
            tokens = str(os.path.basename(bstack1llllll111l_opy_)).split(bstack11111l_opy_ (u"ࠥࡣࠧმ"))
            camelcase_name = bstack11111l_opy_ (u"ࠦࠥࠨნ").join(t.title() for t in tokens)
            suite_name, bstack1llllll11l1_opy_ = os.path.splitext(camelcase_name)
            bstack1lllll1llll_opy_.append(suite_name)
        return bstack1lllll1llll_opy_
    @staticmethod
    def bstack1llllll1111_opy_(typename):
        if bstack11111l_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣო") in typename:
            return bstack11111l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢპ")
        return bstack11111l_opy_ (u"ࠢࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠣჟ")