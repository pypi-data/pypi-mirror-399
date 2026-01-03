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
import json
import os
import grpc
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import (
    bstack1llll11ll11_opy_,
    bstack1llll1ll111_opy_,
    bstack1lllll11l1l_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll11llll1l_opy_ import bstack1ll1l1lllll_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11l1111ll1_opy_
from bstack_utils.helper import bstack1l1l111l1l1_opy_
import threading
import os
import urllib.parse
class bstack1lll111llll_opy_(bstack1lll11ll111_opy_):
    def __init__(self, bstack1lll1l1111l_opy_):
        super().__init__()
        bstack1ll1l1lllll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1lll1lll1ll_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11lll111l_opy_)
        bstack1ll1l1lllll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1lll1lll1ll_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11lll11l1_opy_)
        bstack1ll1l1lllll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1l1l_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11ll1lll1_opy_)
        bstack1ll1l1lllll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1llll1l1ll1_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11ll1ll11_opy_)
        bstack1ll1l1lllll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.bstack1lll1lll1ll_opy_, bstack1llll1ll111_opy_.PRE), self.bstack1l11llll11l_opy_)
        bstack1ll1l1lllll_opy_.bstack1l1lllllll1_opy_((bstack1llll11ll11_opy_.QUIT, bstack1llll1ll111_opy_.PRE), self.on_close)
        self.bstack1lll1l1111l_opy_ = bstack1lll1l1111l_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l11lll111l_opy_(
        self,
        f: bstack1ll1l1lllll_opy_,
        bstack1l11ll1l1l1_opy_: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠥࡰࡦࡻ࡮ࡤࡪࠥፘ"):
            return
        if not bstack1l1l111l1l1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡰࡦࡻ࡮ࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣፙ"))
            return
        def wrapped(bstack1l11ll1l1l1_opy_, launch, *args, **kwargs):
            response = self.bstack1l11ll1ll1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack1l1l_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫፚ"): True}).encode(bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧ፛")))
            if response is not None and response.capabilities:
                if not bstack1l1l111l1l1_opy_():
                    browser = launch(bstack1l11ll1l1l1_opy_)
                    return browser
                bstack1l11llll111_opy_ = json.loads(response.capabilities.decode(bstack1l1l_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨ፜")))
                if not bstack1l11llll111_opy_: # empty caps bstack1l11ll1l11l_opy_ bstack1l11lll1ll1_opy_ bstack1l11ll1llll_opy_ bstack1lll111ll11_opy_ or error in processing
                    return
                bstack1l11llll1l1_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l11llll111_opy_))
                f.bstack1llll1lll11_opy_(instance, bstack1ll1l1lllll_opy_.bstack1l11lll1111_opy_, bstack1l11llll1l1_opy_)
                f.bstack1llll1lll11_opy_(instance, bstack1ll1l1lllll_opy_.bstack1l11llll1ll_opy_, bstack1l11llll111_opy_)
                browser = bstack1l11ll1l1l1_opy_.connect(bstack1l11llll1l1_opy_)
                return browser
        return wrapped
    def bstack1l11ll1lll1_opy_(
        self,
        f: bstack1ll1l1lllll_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠣࡦ࡬ࡷࡵࡧࡴࡤࡪࠥ፝"):
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡦ࡬ࡷࡵࡧࡴࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፞"))
            return
        if not bstack1l1l111l1l1_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack1l1l_opy_ (u"ࠪࡴࡦࡸࡡ࡮ࡵࠪ፟"), {}).get(bstack1l1l_opy_ (u"ࠫࡧࡹࡐࡢࡴࡤࡱࡸ࠭፠")):
                    bstack1l11lll1l1l_opy_ = args[0][bstack1l1l_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧ፡")][bstack1l1l_opy_ (u"ࠨࡢࡴࡒࡤࡶࡦࡳࡳࠣ።")]
                    session_id = bstack1l11lll1l1l_opy_.get(bstack1l1l_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡊࡦࠥ፣"))
                    f.bstack1llll1lll11_opy_(instance, bstack1ll1l1lllll_opy_.bstack1l11lll1l11_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡥ࡫ࡶࡴࡦࡺࡣࡩࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠣࠦ፤"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l11llll11l_opy_(
        self,
        f: bstack1ll1l1lllll_opy_,
        bstack1l11ll1l1l1_opy_: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠤࡦࡳࡳࡴࡥࡤࡶࠥ፥"):
            return
        if not bstack1l1l111l1l1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠥࡖࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡩ࡯ࠢࡦࡳࡳࡴࡥࡤࡶࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፦"))
            return
        def wrapped(bstack1l11ll1l1l1_opy_, connect, *args, **kwargs):
            response = self.bstack1l11ll1ll1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack1l1l_opy_ (u"ࠫ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪ፧"): True}).encode(bstack1l1l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ፨")))
            if response is not None and response.capabilities:
                bstack1l11llll111_opy_ = json.loads(response.capabilities.decode(bstack1l1l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧ፩")))
                if not bstack1l11llll111_opy_:
                    return
                bstack1l11llll1l1_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l11llll111_opy_))
                if bstack1l11llll111_opy_.get(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭፪")):
                    browser = bstack1l11ll1l1l1_opy_.bstack1l11lll1lll_opy_(bstack1l11llll1l1_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l11llll1l1_opy_
                    return connect(bstack1l11ll1l1l1_opy_, *args, **kwargs)
        return wrapped
    def bstack1l11lll11l1_opy_(
        self,
        f: bstack1ll1l1lllll_opy_,
        bstack1l1ll1l1lll_opy_: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥ፫"):
            return
        if not bstack1l1l111l1l1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡰࡨࡻࡤࡶࡡࡨࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፬"))
            return
        def wrapped(bstack1l1ll1l1lll_opy_, bstack1l11lll11ll_opy_, *args, **kwargs):
            contexts = bstack1l1ll1l1lll_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack1l1l_opy_ (u"ࠥࡥࡧࡵࡵࡵ࠼ࡥࡰࡦࡴ࡫ࠣ፭") in page.url:
                                return page
                            else:
                                return bstack1l11lll11ll_opy_(bstack1l1ll1l1lll_opy_)
                    else:
                        return bstack1l11lll11ll_opy_(bstack1l1ll1l1lll_opy_)
        return wrapped
    def bstack1l11ll1ll1l_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack1l1l_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲ࡮ࡺ࠺ࠡࠤ፮") + str(req) + bstack1l1l_opy_ (u"ࠧࠨ፯"))
        try:
            r = self.bstack1ll1l11111l_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1l1l_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࡴࡷࡦࡧࡪࡹࡳ࠾ࠤ፰") + str(r.success) + bstack1l1l_opy_ (u"ࠢࠣ፱"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨ፲") + str(e) + bstack1l1l_opy_ (u"ࠤࠥ፳"))
            traceback.print_exc()
            raise e
    def bstack1l11ll1ll11_opy_(
        self,
        f: bstack1ll1l1lllll_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠥࡣࡸ࡫࡮ࡥࡡࡰࡩࡸࡹࡡࡨࡧࡢࡸࡴࡥࡳࡦࡴࡹࡩࡷࠨ፴"):
            return
        if not bstack1l1l111l1l1_opy_():
            return
        def wrapped(Connection, bstack1l11ll1l1ll_opy_, *args, **kwargs):
            return bstack1l11ll1l1ll_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1l1lllll_opy_,
        bstack1l11ll1l1l1_opy_: object,
        exec: Tuple[bstack1lllll11l1l_opy_, str],
        bstack1llll1llll1_opy_: Tuple[bstack1llll11ll11_opy_, bstack1llll1ll111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1l_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥ፵"):
            return
        if not bstack1l1l111l1l1_opy_():
            self.logger.debug(bstack1l1l_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡨࡲ࡯ࡴࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፶"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped