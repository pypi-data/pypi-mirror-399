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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111ll111l1l_opy_
from browserstack_sdk.bstack1lll1ll1l1_opy_ import bstack1lllll1l1_opy_
def _111l11lllll_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111l1l1ll11_opy_:
    def __init__(self, handler):
        self._111l1l1l1ll_opy_ = {}
        self._111l1l11lll_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1lllll1l1_opy_.version()
        if bstack111ll111l1l_opy_(pytest_version, bstack11111l_opy_ (u"ࠦ࠽࠴࠱࠯࠳ࠥᷮ")) >= 0:
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"ࠬ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᷯ")] = Module._register_setup_function_fixture
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"࠭࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᷰ")] = Module._register_setup_module_fixture
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"ࠧࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᷱ")] = Class._register_setup_class_fixture
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᷲ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᷳ"))
            Module._register_setup_module_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᷴ"))
            Class._register_setup_class_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᷵"))
            Class._register_setup_method_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭᷶"))
        else:
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦ᷷ࠩ")] = Module._inject_setup_function_fixture
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᷸")] = Module._inject_setup_module_fixture
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᷹")] = Class._inject_setup_class_fixture
            self._111l1l1l1ll_opy_[bstack11111l_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧ᷺ࠪ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭᷻"))
            Module._inject_setup_module_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ᷼"))
            Class._inject_setup_class_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩ᷽ࠬ"))
            Class._inject_setup_method_fixture = self.bstack111l1l11l11_opy_(bstack11111l_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ᷾"))
    def bstack111l1l11111_opy_(self, bstack111l1l111ll_opy_, hook_type):
        bstack111l1l1lll1_opy_ = id(bstack111l1l111ll_opy_.__class__)
        if (bstack111l1l1lll1_opy_, hook_type) in self._111l1l11lll_opy_:
            return
        meth = getattr(bstack111l1l111ll_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111l1l11lll_opy_[(bstack111l1l1lll1_opy_, hook_type)] = meth
            setattr(bstack111l1l111ll_opy_, hook_type, self.bstack111l1l111l1_opy_(hook_type, bstack111l1l1lll1_opy_))
    def bstack111l1l11l1l_opy_(self, instance, bstack111l1l1l111_opy_):
        if bstack111l1l1l111_opy_ == bstack11111l_opy_ (u"ࠢࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧ᷿ࠥ"):
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠤḀ"))
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨḁ"))
        if bstack111l1l1l111_opy_ == bstack11111l_opy_ (u"ࠥࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠦḂ"):
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࠥḃ"))
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡱࡧࡹࡱ࡫ࠢḄ"))
        if bstack111l1l1l111_opy_ == bstack11111l_opy_ (u"ࠨࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪࠨḅ"):
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠧḆ"))
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠤḇ"))
        if bstack111l1l1l111_opy_ == bstack11111l_opy_ (u"ࠤࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠥḈ"):
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠤḉ"))
            self.bstack111l1l11111_opy_(instance.obj, bstack11111l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩࠨḊ"))
    @staticmethod
    def bstack111l1l1l11l_opy_(hook_type, func, args):
        if hook_type in [bstack11111l_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲ࡫ࡴࡩࡱࡧࠫḋ"), bstack11111l_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠨḌ")]:
            _111l11lllll_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l1l111l1_opy_(self, hook_type, bstack111l1l1lll1_opy_):
        def bstack111l1l11ll1_opy_(arg=None):
            self.handler(hook_type, bstack11111l_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫ࠧḍ"))
            result = None
            try:
                bstack1llll1lll11_opy_ = self._111l1l11lll_opy_[(bstack111l1l1lll1_opy_, hook_type)]
                self.bstack111l1l1l11l_opy_(hook_type, bstack1llll1lll11_opy_, (arg,))
                result = Result(result=bstack11111l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨḎ"))
            except Exception as e:
                result = Result(result=bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩḏ"), exception=e)
                self.handler(hook_type, bstack11111l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࠩḐ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11111l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪḑ"), result)
        def bstack111l1l1l1l1_opy_(this, arg=None):
            self.handler(hook_type, bstack11111l_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬḒ"))
            result = None
            exception = None
            try:
                self.bstack111l1l1l11l_opy_(hook_type, self._111l1l11lll_opy_[hook_type], (this, arg))
                result = Result(result=bstack11111l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ḓ"))
            except Exception as e:
                result = Result(result=bstack11111l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧḔ"), exception=e)
                self.handler(hook_type, bstack11111l_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧḕ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11111l_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨḖ"), result)
        if hook_type in [bstack11111l_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩḗ"), bstack11111l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭Ḙ")]:
            return bstack111l1l1l1l1_opy_
        return bstack111l1l11ll1_opy_
    def bstack111l1l11l11_opy_(self, bstack111l1l1l111_opy_):
        def bstack111l1l1111l_opy_(this, *args, **kwargs):
            self.bstack111l1l11l1l_opy_(this, bstack111l1l1l111_opy_)
            self._111l1l1l1ll_opy_[bstack111l1l1l111_opy_](this, *args, **kwargs)
        return bstack111l1l1111l_opy_