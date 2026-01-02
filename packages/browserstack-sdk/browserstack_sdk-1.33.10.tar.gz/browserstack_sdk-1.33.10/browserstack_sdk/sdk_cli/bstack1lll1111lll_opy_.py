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
import json
import os
import grpc
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll111l111_opy_ import bstack1ll1l11lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1111l_opy_ import (
    bstack1lllll11111_opy_,
    bstack1llll1l1l1l_opy_,
    bstack1llll111l1l_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll1llll11l_opy_ import bstack1ll1ll11ll1_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1l1l1111l1_opy_
from bstack_utils.helper import bstack1l1ll11lll1_opy_
import threading
import os
import urllib.parse
class bstack1ll1l1l1lll_opy_(bstack1ll1l11lll1_opy_):
    def __init__(self, bstack1ll1l1l1l1l_opy_):
        super().__init__()
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1llll111lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l11lll1ll1_opy_)
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1llll111lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l11llll1ll_opy_)
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1llll1l111l_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l11llll1l1_opy_)
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1lllll11lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l11ll1lll1_opy_)
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.bstack1llll111lll_opy_, bstack1llll1l1l1l_opy_.PRE), self.bstack1l11ll1ll11_opy_)
        bstack1ll1ll11ll1_opy_.bstack1l1llllll1l_opy_((bstack1lllll11111_opy_.QUIT, bstack1llll1l1l1l_opy_.PRE), self.on_close)
        self.bstack1ll1l1l1l1l_opy_ = bstack1ll1l1l1l1l_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l11lll1ll1_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        bstack1l11lll11ll_opy_: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠥࡰࡦࡻ࡮ࡤࡪࠥፑ"):
            return
        if not bstack1l1ll11lll1_opy_():
            self.logger.debug(bstack11111l_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡰࡦࡻ࡮ࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣፒ"))
            return
        def wrapped(bstack1l11lll11ll_opy_, launch, *args, **kwargs):
            response = self.bstack1l11lll111l_opy_(f.platform_index, instance.ref(), json.dumps({bstack11111l_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫፓ"): True}).encode(bstack11111l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧፔ")))
            if response is not None and response.capabilities:
                if not bstack1l1ll11lll1_opy_():
                    browser = launch(bstack1l11lll11ll_opy_)
                    return browser
                bstack1l11lll1l1l_opy_ = json.loads(response.capabilities.decode(bstack11111l_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨፕ")))
                if not bstack1l11lll1l1l_opy_: # empty caps bstack1l11lll1lll_opy_ bstack1l11lll1111_opy_ bstack1l11lllll1l_opy_ bstack1ll1ll1111l_opy_ or error in processing
                    return
                bstack1l11ll1ll1l_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l11lll1l1l_opy_))
                f.bstack1llll1l1lll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l11llll111_opy_, bstack1l11ll1ll1l_opy_)
                f.bstack1llll1l1lll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l11llll11l_opy_, bstack1l11lll1l1l_opy_)
                browser = bstack1l11lll11ll_opy_.connect(bstack1l11ll1ll1l_opy_)
                return browser
        return wrapped
    def bstack1l11llll1l1_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        Connection: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠣࡦ࡬ࡷࡵࡧࡴࡤࡪࠥፖ"):
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡦ࡬ࡷࡵࡧࡴࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣፗ"))
            return
        if not bstack1l1ll11lll1_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack11111l_opy_ (u"ࠪࡴࡦࡸࡡ࡮ࡵࠪፘ"), {}).get(bstack11111l_opy_ (u"ࠫࡧࡹࡐࡢࡴࡤࡱࡸ࠭ፙ")):
                    bstack1l11ll1llll_opy_ = args[0][bstack11111l_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧፚ")][bstack11111l_opy_ (u"ࠨࡢࡴࡒࡤࡶࡦࡳࡳࠣ፛")]
                    session_id = bstack1l11ll1llll_opy_.get(bstack11111l_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡊࡦࠥ፜"))
                    f.bstack1llll1l1lll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l11lllll11_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡥ࡫ࡶࡴࡦࡺࡣࡩࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠣࠦ፝"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l11ll1ll11_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        bstack1l11lll11ll_opy_: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠤࡦࡳࡳࡴࡥࡤࡶࠥ፞"):
            return
        if not bstack1l1ll11lll1_opy_():
            self.logger.debug(bstack11111l_opy_ (u"ࠥࡖࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡩ࡯ࠢࡦࡳࡳࡴࡥࡤࡶࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፟"))
            return
        def wrapped(bstack1l11lll11ll_opy_, connect, *args, **kwargs):
            response = self.bstack1l11lll111l_opy_(f.platform_index, instance.ref(), json.dumps({bstack11111l_opy_ (u"ࠫ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪ፠"): True}).encode(bstack11111l_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ፡")))
            if response is not None and response.capabilities:
                bstack1l11lll1l1l_opy_ = json.loads(response.capabilities.decode(bstack11111l_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧ።")))
                if not bstack1l11lll1l1l_opy_:
                    return
                bstack1l11ll1ll1l_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l11lll1l1l_opy_))
                if bstack1l11lll1l1l_opy_.get(bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭፣")):
                    browser = bstack1l11lll11ll_opy_.bstack1l11ll1l1ll_opy_(bstack1l11ll1ll1l_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l11ll1ll1l_opy_
                    return connect(bstack1l11lll11ll_opy_, *args, **kwargs)
        return wrapped
    def bstack1l11llll1ll_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        bstack1l1ll1llll1_opy_: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥ፤"):
            return
        if not bstack1l1ll11lll1_opy_():
            self.logger.debug(bstack11111l_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡰࡨࡻࡤࡶࡡࡨࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፥"))
            return
        def wrapped(bstack1l1ll1llll1_opy_, bstack1l11lll11l1_opy_, *args, **kwargs):
            contexts = bstack1l1ll1llll1_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11111l_opy_ (u"ࠥࡥࡧࡵࡵࡵ࠼ࡥࡰࡦࡴ࡫ࠣ፦") in page.url:
                                return page
                            else:
                                return bstack1l11lll11l1_opy_(bstack1l1ll1llll1_opy_)
                    else:
                        return bstack1l11lll11l1_opy_(bstack1l1ll1llll1_opy_)
        return wrapped
    def bstack1l11lll111l_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack11111l_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲ࡮ࡺ࠺ࠡࠤ፧") + str(req) + bstack11111l_opy_ (u"ࠧࠨ፨"))
        try:
            r = self.bstack1lll1l1l1l1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11111l_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࡴࡷࡦࡧࡪࡹࡳ࠾ࠤ፩") + str(r.success) + bstack11111l_opy_ (u"ࠢࠣ፪"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11111l_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨ፫") + str(e) + bstack11111l_opy_ (u"ࠤࠥ፬"))
            traceback.print_exc()
            raise e
    def bstack1l11ll1lll1_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        Connection: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠥࡣࡸ࡫࡮ࡥࡡࡰࡩࡸࡹࡡࡨࡧࡢࡸࡴࡥࡳࡦࡴࡹࡩࡷࠨ፭"):
            return
        if not bstack1l1ll11lll1_opy_():
            return
        def wrapped(Connection, bstack1l11lll1l11_opy_, *args, **kwargs):
            return bstack1l11lll1l11_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1ll11ll1_opy_,
        bstack1l11lll11ll_opy_: object,
        exec: Tuple[bstack1llll111l1l_opy_, str],
        bstack1llll1lll1l_opy_: Tuple[bstack1lllll11111_opy_, bstack1llll1l1l1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11111l_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥ፮"):
            return
        if not bstack1l1ll11lll1_opy_():
            self.logger.debug(bstack11111l_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡨࡲ࡯ࡴࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ፯"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped