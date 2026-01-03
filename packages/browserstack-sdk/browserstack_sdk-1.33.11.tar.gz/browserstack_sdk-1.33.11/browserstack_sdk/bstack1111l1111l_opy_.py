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
bstack1l1l_opy_ (u"ࠧࠨࠢࠋࡒࡼࡸࡪࡹࡴࠡࡶࡨࡷࡹࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣ࡬ࡪࡲࡰࡦࡴࠣࡹࡸ࡯࡮ࡨࠢࡧ࡭ࡷ࡫ࡣࡵࠢࡳࡽࡹ࡫ࡳࡵࠢ࡫ࡳࡴࡱࡳ࠯ࠌࠥࠦࠧၟ")
import pytest
import io
import os
from contextlib import redirect_stdout, redirect_stderr
import subprocess
import sys
def bstack11111lll1l_opy_(bstack1111l11l11_opy_=None, bstack11111lllll_opy_=None):
    bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡃࡰ࡮࡯ࡩࡨࡺࠠࡱࡻࡷࡩࡸࡺࠠࡵࡧࡶࡸࡸࠦࡵࡴ࡫ࡱ࡫ࠥࡶࡹࡵࡧࡶࡸࠬࡹࠠࡪࡰࡷࡩࡷࡴࡡ࡭ࠢࡄࡔࡎࡹ࠮ࠋࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡺࡥࡴࡶࡢࡥࡷ࡭ࡳࠡࠪ࡯࡭ࡸࡺࠬࠡࡱࡳࡸ࡮ࡵ࡮ࡢ࡮ࠬ࠾ࠥࡉ࡯࡮ࡲ࡯ࡩࡹ࡫ࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡲࡼࡸࡪࡹࡴࠡࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠤ࡮ࡴࡣ࡭ࡷࡧ࡭ࡳ࡭ࠠࡱࡣࡷ࡬ࡸࠦࡡ࡯ࡦࠣࡪࡱࡧࡧࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡘࡦࡱࡥࡴࠢࡳࡶࡪࡩࡥࡥࡧࡱࡧࡪࠦ࡯ࡷࡧࡵࠤࡹ࡫ࡳࡵࡡࡳࡥࡹ࡮ࡳࠡ࡫ࡩࠤࡧࡵࡴࡩࠢࡤࡶࡪࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡸࡪࡹࡴࡠࡲࡤࡸ࡭ࡹࠠࠩ࡮࡬ࡷࡹࠦ࡯ࡳࠢࡶࡸࡷ࠲ࠠࡰࡲࡷ࡭ࡴࡴࡡ࡭ࠫ࠽ࠤ࡙࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࠨࡴࠫ࠲ࡨ࡮ࡸࡥࡤࡶࡲࡶࡾ࠮ࡩࡦࡵࠬࠤࡹࡵࠠࡤࡱ࡯ࡰࡪࡩࡴࠡࡨࡵࡳࡲ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡅࡤࡲࠥࡨࡥࠡࡣࠣࡷ࡮ࡴࡧ࡭ࡧࠣࡴࡦࡺࡨࠡࡵࡷࡶ࡮ࡴࡧࠡࡱࡵࠤࡱ࡯ࡳࡵࠢࡲࡪࠥࡶࡡࡵࡪࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡉࡨࡰࡲࡶࡪࡪࠠࡪࡨࠣࡸࡪࡹࡴࡠࡣࡵ࡫ࡸࠦࡩࡴࠢࡳࡶࡴࡼࡩࡥࡧࡧ࠲ࠏࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡪࡩࡤࡶ࠽ࠤࡈࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡴࡨࡷࡺࡲࡴࡴࠢࡺ࡭ࡹ࡮ࠠ࡬ࡧࡼࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡳࡶࡥࡦࡩࡸࡹࠠࠩࡤࡲࡳࡱ࠯ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡤࡱࡸࡲࡹࠦࠨࡪࡰࡷ࠭ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡴ࡯ࡥࡧ࡬ࡨࡸࠦࠨ࡭࡫ࡶࡸ࠮ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡴࡦࡵࡷࡣ࡫࡯࡬ࡦࡵࠣࠬࡱ࡯ࡳࡵࠫࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡩࡷࡸ࡯ࡳࠢࠫࡷࡹࡸࠩࠋࠢࠣࠤࠥࠨࠢࠣၠ")
    try:
        bstack11111lll11_opy_ = os.getenv(bstack1l1l_opy_ (u"ࠢࡑ࡛ࡗࡉࡘ࡚࡟ࡄࡗࡕࡖࡊࡔࡔࡠࡖࡈࡗ࡙ࠨၡ")) is not None
        if bstack1111l11l11_opy_ is not None:
            args = list(bstack1111l11l11_opy_)
        elif bstack11111lllll_opy_ is not None:
            if isinstance(bstack11111lllll_opy_, str):
                args = [bstack11111lllll_opy_]
            elif isinstance(bstack11111lllll_opy_, list):
                args = list(bstack11111lllll_opy_)
            else:
                args = [bstack1l1l_opy_ (u"ࠣ࠰ࠥၢ")]
        else:
            args = [bstack1l1l_opy_ (u"ࠤ࠱ࠦၣ")]
        if bstack11111lll11_opy_:
            return _11111ll1l1_opy_(args)
        bstack1111l111l1_opy_ = args + [
            bstack1l1l_opy_ (u"ࠥ࠱࠲ࡩ࡯࡭࡮ࡨࡧࡹ࠳࡯࡯࡮ࡼࠦၤ"),
            bstack1l1l_opy_ (u"ࠦ࠲࠳ࡱࡶ࡫ࡨࡸࠧၥ")
        ]
        class bstack11111ll11l_opy_:
            bstack1l1l_opy_ (u"ࠧࠨࠢࡑࡻࡷࡩࡸࡺࠠࡱ࡮ࡸ࡫࡮ࡴࠠࡵࡪࡤࡸࠥࡩࡡࡱࡶࡸࡶࡪࡹࠠࡤࡱ࡯ࡰࡪࡩࡴࡦࡦࠣࡸࡪࡹࡴࠡ࡫ࡷࡩࡲࡹ࠮ࠣࠤࠥၦ")
            def __init__(self):
                self.bstack11111llll1_opy_ = []
                self.test_files = set()
                self.bstack1111l11111_opy_ = None
            def pytest_collection_finish(self, session):
                bstack1l1l_opy_ (u"ࠨࠢࠣࡊࡲࡳࡰࠦࡣࡢ࡮࡯ࡩࡩࠦࡡࡧࡶࡨࡶࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯ࠢ࡬ࡷࠥ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࠮ࠣࠤࠥၧ")
                try:
                    for item in session.items:
                        nodeid = item.nodeid
                        self.bstack11111llll1_opy_.append(nodeid)
                        if bstack1l1l_opy_ (u"ࠢ࠻࠼ࠥၨ") in nodeid:
                            file_path = nodeid.split(bstack1l1l_opy_ (u"ࠣ࠼࠽ࠦၩ"), 1)[0]
                            if file_path.endswith(bstack1l1l_opy_ (u"ࠩ࠱ࡴࡾ࠭ၪ")):
                                self.test_files.add(file_path)
                except Exception as e:
                    self.bstack1111l11111_opy_ = str(e)
        collector = bstack11111ll11l_opy_()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            exit_code = pytest.main(bstack1111l111l1_opy_, plugins=[collector])
        if collector.bstack1111l11111_opy_:
            return {bstack1l1l_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦၫ"): False, bstack1l1l_opy_ (u"ࠦࡨࡵࡵ࡯ࡶࠥၬ"): 0, bstack1l1l_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࡸࠨၭ"): [], bstack1l1l_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯࡬ࡦࡵࠥၮ"): [], bstack1l1l_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨၯ"): bstack1l1l_opy_ (u"ࠣࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣၰ").format(collector.bstack1111l11111_opy_)}
        return {
            bstack1l1l_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵࠥၱ"): True,
            bstack1l1l_opy_ (u"ࠥࡧࡴࡻ࡮ࡵࠤၲ"): len(collector.bstack11111llll1_opy_),
            bstack1l1l_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࡷࠧၳ"): collector.bstack11111llll1_opy_,
            bstack1l1l_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴࠤၴ"): sorted(collector.test_files),
            bstack1l1l_opy_ (u"ࠨࡥࡹ࡫ࡷࡣࡨࡵࡤࡦࠤၵ"): exit_code
        }
    except Exception as e:
        return {bstack1l1l_opy_ (u"ࠢࡴࡷࡦࡧࡪࡹࡳࠣၶ"): False, bstack1l1l_opy_ (u"ࠣࡥࡲࡹࡳࡺࠢၷ"): 0, bstack1l1l_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࡵࠥၸ"): [], bstack1l1l_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡹࠢၹ"): [], bstack1l1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥၺ"): bstack1l1l_opy_ (u"࡛ࠧ࡮ࡦࡺࡳࡩࡨࡺࡥࡥࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤࡹ࡫ࡳࡵࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࡀࠠࡼࡿࠥၻ").format(e)}
def _11111ll1l1_opy_(args):
    bstack1l1l_opy_ (u"ࠨࠢࠣࡋࡶࡳࡱࡧࡴࡦࡦࠣࡧࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠠࡦࡺࡨࡧࡺࡺࡥࡥࠢ࡬ࡲࠥࡧࠠࡴࡧࡳࡥࡷࡧࡴࡦࠢࡓࡽࡹ࡮࡯࡯ࠢࡳࡶࡴࡩࡥࡴࡵࠣࡸࡴࠦࡡࡷࡱ࡬ࡨࠥࡴࡥࡴࡶࡨࡨࠥࡶࡹࡵࡧࡶࡸࠥ࡯ࡳࡴࡷࡨࡷ࠳ࠨࠢࠣၼ")
    bstack1111l111ll_opy_ = [sys.executable, bstack1l1l_opy_ (u"ࠢ࠮࡯ࠥၽ"), bstack1l1l_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࠣၾ"), bstack1l1l_opy_ (u"ࠤ࠰࠱ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡵ࡮࡭ࡻࠥၿ"), bstack1l1l_opy_ (u"ࠥ࠱࠲ࡷࡵࡪࡧࡷࠦႀ")]
    bstack11111ll1ll_opy_ = [a for a in args if a not in (bstack1l1l_opy_ (u"ࠦ࠲࠳ࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡰࡰ࡯ࡽࠧႁ"), bstack1l1l_opy_ (u"ࠧ࠳࠭ࡲࡷ࡬ࡩࡹࠨႂ"), bstack1l1l_opy_ (u"ࠨ࠭ࡲࠤႃ"))]
    cmd = bstack1111l111ll_opy_ + bstack11111ll1ll_opy_
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        stdout = proc.stdout.splitlines()
        bstack11111llll1_opy_ = []
        test_files = set()
        for line in stdout:
            line = line.strip()
            if not line or bstack1l1l_opy_ (u"ࠢࠡࡥࡲࡰࡱ࡫ࡣࡵࡧࡧࠦႄ") in line.lower():
                continue
            if bstack1l1l_opy_ (u"ࠣ࠼࠽ࠦႅ") in line:
                bstack11111llll1_opy_.append(line)
                file_path = line.split(bstack1l1l_opy_ (u"ࠤ࠽࠾ࠧႆ"), 1)[0]
                if file_path.endswith(bstack1l1l_opy_ (u"ࠪ࠲ࡵࡿࠧႇ")):
                    test_files.add(file_path)
        success = proc.returncode in (0, 5)
        return {
            bstack1l1l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷࠧႈ"): success,
            bstack1l1l_opy_ (u"ࠧࡩ࡯ࡶࡰࡷࠦႉ"): len(bstack11111llll1_opy_),
            bstack1l1l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࡹࠢႊ"): bstack11111llll1_opy_,
            bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࠦႋ"): sorted(test_files),
            bstack1l1l_opy_ (u"ࠣࡧࡻ࡭ࡹࡥࡣࡰࡦࡨࠦႌ"): proc.returncode,
            bstack1l1l_opy_ (u"ࠤࡨࡶࡷࡵࡲႍࠣ"): None if success else bstack1l1l_opy_ (u"ࠥࡗࡺࡨࡰࡳࡱࡦࡩࡸࡹࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧࠤ࠭࡫ࡸࡪࡶࠣࡿࢂ࠯ࠢႎ").format(proc.returncode)
        }
    except Exception as e:
        return {bstack1l1l_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷࠧႏ"): False, bstack1l1l_opy_ (u"ࠧࡩ࡯ࡶࡰࡷࠦ႐"): 0, bstack1l1l_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࡹࠢ႑"): [], bstack1l1l_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࠦ႒"): [], bstack1l1l_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢ႓"): bstack1l1l_opy_ (u"ࠤࡖࡹࡧࡶࡲࡰࡥࡨࡷࡸࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨ႔").format(e)}