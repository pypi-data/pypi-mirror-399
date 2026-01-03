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
from uuid import uuid4
from bstack_utils.helper import bstack1111lllll_opy_, bstack111llllll11_opy_
from bstack_utils.bstack111111l11_opy_ import bstack1lllll111lll_opy_
class bstack1111ll1l11_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll1l1l111_opy_=None, bstack1llll11ll1l1_opy_=True, bstack11lllll11ll_opy_=None, bstack11111ll1_opy_=None, result=None, duration=None, bstack1111l1llll_opy_=None, meta={}):
        self.bstack1111l1llll_opy_ = bstack1111l1llll_opy_
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
        self.bstack1llll1l1l111_opy_ = bstack1llll1l1l111_opy_
        self.bstack11lllll11ll_opy_ = bstack11lllll11ll_opy_
        self.bstack11111ll1_opy_ = bstack11111ll1_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l111l1l_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111ll111ll_opy_(self, meta):
        self.meta = meta
    def bstack111ll11ll1_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll11lllll_opy_(self):
        bstack1llll1l11l11_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1l1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭⃌"): bstack1llll1l11l11_opy_,
            bstack1l1l_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࠭⃍"): bstack1llll1l11l11_opy_,
            bstack1l1l_opy_ (u"ࠬࡼࡣࡠࡨ࡬ࡰࡪࡶࡡࡵࡪࠪ⃎"): bstack1llll1l11l11_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1l1l_opy_ (u"ࠨࡕ࡯ࡧࡻࡴࡪࡩࡴࡦࡦࠣࡥࡷ࡭ࡵ࡮ࡧࡱࡸ࠿ࠦࠢ⃏") + key)
            setattr(self, key, val)
    def bstack1llll1l11lll_opy_(self):
        return {
            bstack1l1l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⃐"): self.name,
            bstack1l1l_opy_ (u"ࠨࡤࡲࡨࡾ࠭⃑"): {
                bstack1l1l_opy_ (u"ࠩ࡯ࡥࡳ࡭⃒ࠧ"): bstack1l1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ⃓ࠪ"),
                bstack1l1l_opy_ (u"ࠫࡨࡵࡤࡦࠩ⃔"): self.code
            },
            bstack1l1l_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬ⃕"): self.scope,
            bstack1l1l_opy_ (u"࠭ࡴࡢࡩࡶࠫ⃖"): self.tags,
            bstack1l1l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ⃗"): self.framework,
            bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸ⃘ࠬ"): self.started_at
        }
    def bstack1llll1l11l1l_opy_(self):
        return {
         bstack1l1l_opy_ (u"ࠩࡰࡩࡹࡧ⃙ࠧ"): self.meta
        }
    def bstack1llll11lll11_opy_(self):
        return {
            bstack1l1l_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡕࡩࡷࡻ࡮ࡑࡣࡵࡥࡲ⃚࠭"): {
                bstack1l1l_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࡢࡲࡦࡳࡥࠨ⃛"): self.bstack1llll1l1l111_opy_
            }
        }
    def bstack1llll11llll1_opy_(self, bstack1llll1l1111l_opy_, details):
        step = next(filter(lambda st: st[bstack1l1l_opy_ (u"ࠬ࡯ࡤࠨ⃜")] == bstack1llll1l1111l_opy_, self.meta[bstack1l1l_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⃝")]), None)
        step.update(details)
    def bstack1l11ll11l_opy_(self, bstack1llll1l1111l_opy_):
        step = next(filter(lambda st: st[bstack1l1l_opy_ (u"ࠧࡪࡦࠪ⃞")] == bstack1llll1l1111l_opy_, self.meta[bstack1l1l_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ⃟")]), None)
        step.update({
            bstack1l1l_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⃠"): bstack1111lllll_opy_()
        })
    def bstack111ll1111l_opy_(self, bstack1llll1l1111l_opy_, result, duration=None):
        bstack11lllll11ll_opy_ = bstack1111lllll_opy_()
        if bstack1llll1l1111l_opy_ is not None and self.meta.get(bstack1l1l_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ⃡")):
            step = next(filter(lambda st: st[bstack1l1l_opy_ (u"ࠫ࡮ࡪࠧ⃢")] == bstack1llll1l1111l_opy_, self.meta[bstack1l1l_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⃣")]), None)
            step.update({
                bstack1l1l_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⃤"): bstack11lllll11ll_opy_,
                bstack1l1l_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯⃥ࠩ"): duration if duration else bstack111llllll11_opy_(step[bstack1l1l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸ⃦ࠬ")], bstack11lllll11ll_opy_),
                bstack1l1l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⃧"): result.result,
                bstack1l1l_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨ⃨ࠫ"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll1l11ll1_opy_):
        if self.meta.get(bstack1l1l_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⃩")):
            self.meta[bstack1l1l_opy_ (u"ࠬࡹࡴࡦࡲࡶ⃪ࠫ")].append(bstack1llll1l11ll1_opy_)
        else:
            self.meta[bstack1l1l_opy_ (u"࠭ࡳࡵࡧࡳࡷ⃫ࠬ")] = [ bstack1llll1l11ll1_opy_ ]
    def bstack1llll11ll11l_opy_(self):
        return {
            bstack1l1l_opy_ (u"ࠧࡶࡷ࡬ࡨ⃬ࠬ"): self.bstack111l111l1l_opy_(),
            bstack1l1l_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⃭"): bstack1l1l_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩ⃮ࠪ"),
            **self.bstack1llll1l11lll_opy_(),
            **self.bstack1llll11lllll_opy_(),
            **self.bstack1llll1l11l1l_opy_()
        }
    def bstack1llll11ll1ll_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1l1l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⃯"): self.bstack11lllll11ll_opy_,
            bstack1l1l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬ⃰"): self.duration,
            bstack1l1l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⃱"): self.result.result
        }
        if data[bstack1l1l_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⃲")] == bstack1l1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ⃳"):
            data[bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࡡࡷࡽࡵ࡫ࠧ⃴")] = self.result.bstack1llllll111l_opy_()
            data[bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪ⃵")] = [{bstack1l1l_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭⃶"): self.result.bstack111l1l1llll_opy_()}]
        return data
    def bstack1llll11lll1l_opy_(self):
        return {
            bstack1l1l_opy_ (u"ࠫࡺࡻࡩࡥࠩ⃷"): self.bstack111l111l1l_opy_(),
            **self.bstack1llll1l11lll_opy_(),
            **self.bstack1llll11lllll_opy_(),
            **self.bstack1llll11ll1ll_opy_(),
            **self.bstack1llll1l11l1l_opy_()
        }
    def bstack1111ll1ll1_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1l1l_opy_ (u"࡙ࠬࡴࡢࡴࡷࡩࡩ࠭⃸") in event:
            return self.bstack1llll11ll11l_opy_()
        elif bstack1l1l_opy_ (u"࠭ࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⃹") in event:
            return self.bstack1llll11lll1l_opy_()
    def bstack1111l11lll_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack11lllll11ll_opy_ = time if time else bstack1111lllll_opy_()
        self.duration = duration if duration else bstack111llllll11_opy_(self.started_at, self.bstack11lllll11ll_opy_)
        if result:
            self.result = result
class bstack111l1ll1l1_opy_(bstack1111ll1l11_opy_):
    def __init__(self, hooks=[], bstack111ll1l1l1_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111ll1l1l1_opy_ = bstack111ll1l1l1_opy_
        super().__init__(*args, **kwargs, bstack11111ll1_opy_=bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࠬ⃺"))
    @classmethod
    def bstack1llll1l111ll_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1l1l_opy_ (u"ࠨ࡫ࡧࠫ⃻"): id(step),
                bstack1l1l_opy_ (u"ࠩࡷࡩࡽࡺࠧ⃼"): step.name,
                bstack1l1l_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫ⃽"): step.keyword,
            })
        return bstack111l1ll1l1_opy_(
            **kwargs,
            meta={
                bstack1l1l_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬ⃾"): {
                    bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⃿"): feature.name,
                    bstack1l1l_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ℀"): feature.filename,
                    bstack1l1l_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ℁"): feature.description
                },
                bstack1l1l_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪℂ"): {
                    bstack1l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ℃"): scenario.name
                },
                bstack1l1l_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ℄"): steps,
                bstack1l1l_opy_ (u"ࠫࡪࡾࡡ࡮ࡲ࡯ࡩࡸ࠭℅"): bstack1lllll111lll_opy_(test)
            }
        )
    def bstack1llll1l11111_opy_(self):
        return {
            bstack1l1l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ℆"): self.hooks
        }
    def bstack1llll11ll111_opy_(self):
        if self.bstack111ll1l1l1_opy_:
            return {
                bstack1l1l_opy_ (u"࠭ࡩ࡯ࡶࡨ࡫ࡷࡧࡴࡪࡱࡱࡷࠬℇ"): self.bstack111ll1l1l1_opy_
            }
        return {}
    def bstack1llll11lll1l_opy_(self):
        return {
            **super().bstack1llll11lll1l_opy_(),
            **self.bstack1llll1l11111_opy_()
        }
    def bstack1llll11ll11l_opy_(self):
        return {
            **super().bstack1llll11ll11l_opy_(),
            **self.bstack1llll11ll111_opy_()
        }
    def bstack1111l11lll_opy_(self):
        return bstack1l1l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩ℈")
class bstack111ll11lll_opy_(bstack1111ll1l11_opy_):
    def __init__(self, hook_type, *args,bstack111ll1l1l1_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1l1lll1ll11_opy_ = None
        self.bstack111ll1l1l1_opy_ = bstack111ll1l1l1_opy_
        super().__init__(*args, **kwargs, bstack11111ll1_opy_=bstack1l1l_opy_ (u"ࠨࡪࡲࡳࡰ࠭℉"))
    def bstack1111lll111_opy_(self):
        return self.hook_type
    def bstack1llll1l111l1_opy_(self):
        return {
            bstack1l1l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬℊ"): self.hook_type
        }
    def bstack1llll11lll1l_opy_(self):
        return {
            **super().bstack1llll11lll1l_opy_(),
            **self.bstack1llll1l111l1_opy_()
        }
    def bstack1llll11ll11l_opy_(self):
        return {
            **super().bstack1llll11ll11l_opy_(),
            bstack1l1l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡯ࡤࠨℋ"): self.bstack1l1lll1ll11_opy_,
            **self.bstack1llll1l111l1_opy_()
        }
    def bstack1111l11lll_opy_(self):
        return bstack1l1l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳ࠭ℌ")
    def bstack111ll1l111_opy_(self, bstack1l1lll1ll11_opy_):
        self.bstack1l1lll1ll11_opy_ = bstack1l1lll1ll11_opy_