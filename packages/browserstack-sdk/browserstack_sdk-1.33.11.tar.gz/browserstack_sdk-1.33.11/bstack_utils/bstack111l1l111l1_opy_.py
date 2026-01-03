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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111l1ll11l1_opy_
from browserstack_sdk.bstack111l11ll1_opy_ import bstack1l11111l1_opy_
def _111l11lllll_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111l1l1l1l1_opy_:
    def __init__(self, handler):
        self._111l1l1ll11_opy_ = {}
        self._111l1l1l1ll_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1l11111l1_opy_.version()
        if bstack111l1ll11l1_opy_(pytest_version, bstack1l1l_opy_ (u"ࠦ࠽࠴࠱࠯࠳ࠥ᷵")) >= 0:
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"ࠬ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᷶")] = Module._register_setup_function_fixture
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"࠭࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫᷷ࠧ")] = Module._register_setup_module_fixture
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"ࠧࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫᷸ࠧ")] = Class._register_setup_class_fixture
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦ᷹ࠩ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩ᷺ࠬ"))
            Module._register_setup_module_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᷻"))
            Class._register_setup_class_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᷼"))
            Class._register_setup_method_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ᷽࠭"))
        else:
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ᷾")] = Module._inject_setup_function_fixture
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᷿")] = Module._inject_setup_module_fixture
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨḀ")] = Class._inject_setup_class_fixture
            self._111l1l1ll11_opy_[bstack1l1l_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪḁ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭Ḃ"))
            Module._inject_setup_module_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬḃ"))
            Class._inject_setup_class_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬḄ"))
            Class._inject_setup_method_fixture = self.bstack111l1l11l11_opy_(bstack1l1l_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧḅ"))
    def bstack111l1l1l111_opy_(self, bstack111l1l11l1l_opy_, hook_type):
        bstack111l1l11ll1_opy_ = id(bstack111l1l11l1l_opy_.__class__)
        if (bstack111l1l11ll1_opy_, hook_type) in self._111l1l1l1ll_opy_:
            return
        meth = getattr(bstack111l1l11l1l_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111l1l1l1ll_opy_[(bstack111l1l11ll1_opy_, hook_type)] = meth
            setattr(bstack111l1l11l1l_opy_, hook_type, self.bstack111l11llll1_opy_(hook_type, bstack111l1l11ll1_opy_))
    def bstack111l1l1l11l_opy_(self, instance, bstack111l1l11111_opy_):
        if bstack111l1l11111_opy_ == bstack1l1l_opy_ (u"ࠢࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠥḆ"):
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠤḇ"))
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨḈ"))
        if bstack111l1l11111_opy_ == bstack1l1l_opy_ (u"ࠥࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠦḉ"):
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࠥḊ"))
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡱࡧࡹࡱ࡫ࠢḋ"))
        if bstack111l1l11111_opy_ == bstack1l1l_opy_ (u"ࠨࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪࠨḌ"):
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠧḍ"))
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠤḎ"))
        if bstack111l1l11111_opy_ == bstack1l1l_opy_ (u"ࠤࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠥḏ"):
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠤḐ"))
            self.bstack111l1l1l111_opy_(instance.obj, bstack1l1l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩࠨḑ"))
    @staticmethod
    def bstack111l11lll1l_opy_(hook_type, func, args):
        if hook_type in [bstack1l1l_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲ࡫ࡴࡩࡱࡧࠫḒ"), bstack1l1l_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠨḓ")]:
            _111l11lllll_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l11llll1_opy_(self, hook_type, bstack111l1l11ll1_opy_):
        def bstack111l1l11lll_opy_(arg=None):
            self.handler(hook_type, bstack1l1l_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫ࠧḔ"))
            result = None
            try:
                bstack1lll1lll1l1_opy_ = self._111l1l1l1ll_opy_[(bstack111l1l11ll1_opy_, hook_type)]
                self.bstack111l11lll1l_opy_(hook_type, bstack1lll1lll1l1_opy_, (arg,))
                result = Result(result=bstack1l1l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨḕ"))
            except Exception as e:
                result = Result(result=bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩḖ"), exception=e)
                self.handler(hook_type, bstack1l1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࠩḗ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1l1l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪḘ"), result)
        def bstack111l1l111ll_opy_(this, arg=None):
            self.handler(hook_type, bstack1l1l_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬḙ"))
            result = None
            exception = None
            try:
                self.bstack111l11lll1l_opy_(hook_type, self._111l1l1l1ll_opy_[hook_type], (this, arg))
                result = Result(result=bstack1l1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭Ḛ"))
            except Exception as e:
                result = Result(result=bstack1l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧḛ"), exception=e)
                self.handler(hook_type, bstack1l1l_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧḜ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1l1l_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨḝ"), result)
        if hook_type in [bstack1l1l_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩḞ"), bstack1l1l_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ḟ")]:
            return bstack111l1l111ll_opy_
        return bstack111l1l11lll_opy_
    def bstack111l1l11l11_opy_(self, bstack111l1l11111_opy_):
        def bstack111l1l1111l_opy_(this, *args, **kwargs):
            self.bstack111l1l1l11l_opy_(this, bstack111l1l11111_opy_)
            self._111l1l1ll11_opy_[bstack111l1l11111_opy_](this, *args, **kwargs)
        return bstack111l1l1111l_opy_