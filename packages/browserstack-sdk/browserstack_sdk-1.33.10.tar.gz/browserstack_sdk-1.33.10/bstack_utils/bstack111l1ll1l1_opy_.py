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
from uuid import uuid4
from bstack_utils.helper import bstack111l1l11_opy_, bstack111llll1ll1_opy_
from bstack_utils.bstack1l11l1lll_opy_ import bstack1lllll11l1l1_opy_
class bstack1111ll1l1l_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll11lll11_opy_=None, bstack1llll11ll1l1_opy_=True, bstack11lllll1l11_opy_=None, bstack1l111l1lll_opy_=None, result=None, duration=None, bstack111l1l111l_opy_=None, meta={}):
        self.bstack111l1l111l_opy_ = bstack111l1l111l_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1llll11ll1l1_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llll11lll11_opy_ = bstack1llll11lll11_opy_
        self.bstack11lllll1l11_opy_ = bstack11lllll1l11_opy_
        self.bstack1l111l1lll_opy_ = bstack1l111l1lll_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l11l111_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111ll11ll1_opy_(self, meta):
        self.meta = meta
    def bstack111ll1l111_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll1l1111l_opy_(self):
        bstack1llll1l1l111_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack11111l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭⃅"): bstack1llll1l1l111_opy_,
            bstack11111l_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࠭⃆"): bstack1llll1l1l111_opy_,
            bstack11111l_opy_ (u"ࠬࡼࡣࡠࡨ࡬ࡰࡪࡶࡡࡵࡪࠪ⃇"): bstack1llll1l1l111_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack11111l_opy_ (u"ࠨࡕ࡯ࡧࡻࡴࡪࡩࡴࡦࡦࠣࡥࡷ࡭ࡵ࡮ࡧࡱࡸ࠿ࠦࠢ⃈") + key)
            setattr(self, key, val)
    def bstack1llll11ll1ll_opy_(self):
        return {
            bstack11111l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⃉"): self.name,
            bstack11111l_opy_ (u"ࠨࡤࡲࡨࡾ࠭⃊"): {
                bstack11111l_opy_ (u"ࠩ࡯ࡥࡳ࡭ࠧ⃋"): bstack11111l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ⃌"),
                bstack11111l_opy_ (u"ࠫࡨࡵࡤࡦࠩ⃍"): self.code
            },
            bstack11111l_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬ⃎"): self.scope,
            bstack11111l_opy_ (u"࠭ࡴࡢࡩࡶࠫ⃏"): self.tags,
            bstack11111l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ⃐"): self.framework,
            bstack11111l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⃑"): self.started_at
        }
    def bstack1llll1l11ll1_opy_(self):
        return {
         bstack11111l_opy_ (u"ࠩࡰࡩࡹࡧ⃒ࠧ"): self.meta
        }
    def bstack1llll11lllll_opy_(self):
        return {
            bstack11111l_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡕࡩࡷࡻ࡮ࡑࡣࡵࡥࡲ⃓࠭"): {
                bstack11111l_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࡢࡲࡦࡳࡥࠨ⃔"): self.bstack1llll11lll11_opy_
            }
        }
    def bstack1llll1l111ll_opy_(self, bstack1llll11llll1_opy_, details):
        step = next(filter(lambda st: st[bstack11111l_opy_ (u"ࠬ࡯ࡤࠨ⃕")] == bstack1llll11llll1_opy_, self.meta[bstack11111l_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⃖")]), None)
        step.update(details)
    def bstack1llll1l111_opy_(self, bstack1llll11llll1_opy_):
        step = next(filter(lambda st: st[bstack11111l_opy_ (u"ࠧࡪࡦࠪ⃗")] == bstack1llll11llll1_opy_, self.meta[bstack11111l_opy_ (u"ࠨࡵࡷࡩࡵࡹ⃘ࠧ")]), None)
        step.update({
            bstack11111l_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ⃙࠭"): bstack111l1l11_opy_()
        })
    def bstack111ll11111_opy_(self, bstack1llll11llll1_opy_, result, duration=None):
        bstack11lllll1l11_opy_ = bstack111l1l11_opy_()
        if bstack1llll11llll1_opy_ is not None and self.meta.get(bstack11111l_opy_ (u"ࠪࡷࡹ࡫ࡰࡴ⃚ࠩ")):
            step = next(filter(lambda st: st[bstack11111l_opy_ (u"ࠫ࡮ࡪࠧ⃛")] == bstack1llll11llll1_opy_, self.meta[bstack11111l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⃜")]), None)
            step.update({
                bstack11111l_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⃝"): bstack11lllll1l11_opy_,
                bstack11111l_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ⃞"): duration if duration else bstack111llll1ll1_opy_(step[bstack11111l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⃟")], bstack11lllll1l11_opy_),
                bstack11111l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⃠"): result.result,
                bstack11111l_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫ⃡"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll1l11l1l_opy_):
        if self.meta.get(bstack11111l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⃢")):
            self.meta[bstack11111l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⃣")].append(bstack1llll1l11l1l_opy_)
        else:
            self.meta[bstack11111l_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⃤")] = [ bstack1llll1l11l1l_opy_ ]
    def bstack1llll1l11lll_opy_(self):
        return {
            bstack11111l_opy_ (u"ࠧࡶࡷ࡬ࡨ⃥ࠬ"): self.bstack111l11l111_opy_(),
            bstack11111l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⃦"): bstack11111l_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ⃧"),
            **self.bstack1llll11ll1ll_opy_(),
            **self.bstack1llll1l1111l_opy_(),
            **self.bstack1llll1l11ll1_opy_()
        }
    def bstack1llll1l1l11l_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack11111l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⃨"): self.bstack11lllll1l11_opy_,
            bstack11111l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬ⃩"): self.duration,
            bstack11111l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸ⃪ࠬ"): self.result.result
        }
        if data[bstack11111l_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ⃫࠭")] == bstack11111l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪ⃬ࠧ"):
            data[bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࡡࡷࡽࡵ࡫⃭ࠧ")] = self.result.bstack1llllll1111_opy_()
            data[bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧ⃮ࠪ")] = [{bstack11111l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ⃯࠭"): self.result.bstack11l111l11l1_opy_()}]
        return data
    def bstack1llll1l11l11_opy_(self):
        return {
            bstack11111l_opy_ (u"ࠫࡺࡻࡩࡥࠩ⃰"): self.bstack111l11l111_opy_(),
            **self.bstack1llll11ll1ll_opy_(),
            **self.bstack1llll1l1111l_opy_(),
            **self.bstack1llll1l1l11l_opy_(),
            **self.bstack1llll1l11ll1_opy_()
        }
    def bstack111l11l1ll_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack11111l_opy_ (u"࡙ࠬࡴࡢࡴࡷࡩࡩ࠭⃱") in event:
            return self.bstack1llll1l11lll_opy_()
        elif bstack11111l_opy_ (u"࠭ࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⃲") in event:
            return self.bstack1llll1l11l11_opy_()
    def bstack1111ll11l1_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack11lllll1l11_opy_ = time if time else bstack111l1l11_opy_()
        self.duration = duration if duration else bstack111llll1ll1_opy_(self.started_at, self.bstack11lllll1l11_opy_)
        if result:
            self.result = result
class bstack111ll1l11l_opy_(bstack1111ll1l1l_opy_):
    def __init__(self, hooks=[], bstack111l1lll1l_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111l1lll1l_opy_ = bstack111l1lll1l_opy_
        super().__init__(*args, **kwargs, bstack1l111l1lll_opy_=bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࠬ⃳"))
    @classmethod
    def bstack1llll11lll1l_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11111l_opy_ (u"ࠨ࡫ࡧࠫ⃴"): id(step),
                bstack11111l_opy_ (u"ࠩࡷࡩࡽࡺࠧ⃵"): step.name,
                bstack11111l_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫ⃶"): step.keyword,
            })
        return bstack111ll1l11l_opy_(
            **kwargs,
            meta={
                bstack11111l_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬ⃷"): {
                    bstack11111l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⃸"): feature.name,
                    bstack11111l_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ⃹"): feature.filename,
                    bstack11111l_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ⃺"): feature.description
                },
                bstack11111l_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪ⃻"): {
                    bstack11111l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ⃼"): scenario.name
                },
                bstack11111l_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ⃽"): steps,
                bstack11111l_opy_ (u"ࠫࡪࡾࡡ࡮ࡲ࡯ࡩࡸ࠭⃾"): bstack1lllll11l1l1_opy_(test)
            }
        )
    def bstack1llll1l111l1_opy_(self):
        return {
            bstack11111l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⃿"): self.hooks
        }
    def bstack1llll1l11111_opy_(self):
        if self.bstack111l1lll1l_opy_:
            return {
                bstack11111l_opy_ (u"࠭ࡩ࡯ࡶࡨ࡫ࡷࡧࡴࡪࡱࡱࡷࠬ℀"): self.bstack111l1lll1l_opy_
            }
        return {}
    def bstack1llll1l11l11_opy_(self):
        return {
            **super().bstack1llll1l11l11_opy_(),
            **self.bstack1llll1l111l1_opy_()
        }
    def bstack1llll1l11lll_opy_(self):
        return {
            **super().bstack1llll1l11lll_opy_(),
            **self.bstack1llll1l11111_opy_()
        }
    def bstack1111ll11l1_opy_(self):
        return bstack11111l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩ℁")
class bstack111ll11l11_opy_(bstack1111ll1l1l_opy_):
    def __init__(self, hook_type, *args,bstack111l1lll1l_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1l1llll1ll1_opy_ = None
        self.bstack111l1lll1l_opy_ = bstack111l1lll1l_opy_
        super().__init__(*args, **kwargs, bstack1l111l1lll_opy_=bstack11111l_opy_ (u"ࠨࡪࡲࡳࡰ࠭ℂ"))
    def bstack1111ll111l_opy_(self):
        return self.hook_type
    def bstack1llll1l1l1l1_opy_(self):
        return {
            bstack11111l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ℃"): self.hook_type
        }
    def bstack1llll1l11l11_opy_(self):
        return {
            **super().bstack1llll1l11l11_opy_(),
            **self.bstack1llll1l1l1l1_opy_()
        }
    def bstack1llll1l11lll_opy_(self):
        return {
            **super().bstack1llll1l11lll_opy_(),
            bstack11111l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡯ࡤࠨ℄"): self.bstack1l1llll1ll1_opy_,
            **self.bstack1llll1l1l1l1_opy_()
        }
    def bstack1111ll11l1_opy_(self):
        return bstack11111l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳ࠭℅")
    def bstack111ll1111l_opy_(self, bstack1l1llll1ll1_opy_):
        self.bstack1l1llll1ll1_opy_ = bstack1l1llll1ll1_opy_