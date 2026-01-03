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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
from unittest import result
import urllib
from urllib.parse import urlparse
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack11l111ll_opy_, bstack1l1ll1ll_opy_, bstack1llll11111_opy_,
                                    bstack11l1l1ll1l1_opy_, bstack11l1l1l1ll1_opy_, bstack11l1l1lll11_opy_, bstack11l1l1111l1_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1l1ll11l_opy_, bstack11l11111l_opy_
from bstack_utils.proxy import bstack1l11l1ll1l_opy_, bstack1l11ll1ll_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1lllllll1l_opy_
from bstack_utils.bstack111ll11l1_opy_ import bstack1l11llll1_opy_
from browserstack_sdk._version import __version__
bstack1l1ll1l1_opy_ = Config.bstack1l1ll1l111_opy_()
logger = bstack1lllllll1l_opy_.get_logger(__name__, bstack1lllllll1l_opy_.bstack1ll1ll1ll11_opy_())
def bstack11ll1l111l1_opy_(config):
    return config[bstack1l1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ᭻")]
def bstack11ll1l11111_opy_(config):
    return config[bstack1l1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ᭼")]
def bstack11llll11l1_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111lll1l11l_opy_(obj):
    values = []
    bstack111l1ll11ll_opy_ = re.compile(bstack1l1l_opy_ (u"ࡴࠥࡢࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࡞ࡧ࠯ࠩࠨ᭽"), re.I)
    for key in obj.keys():
        if bstack111l1ll11ll_opy_.match(key):
            values.append(obj[key])
    return values
def bstack11l111l11ll_opy_(config):
    tags = []
    tags.extend(bstack111lll1l11l_opy_(os.environ))
    tags.extend(bstack111lll1l11l_opy_(config))
    return tags
def bstack11l111l1l11_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111l1l1ll1l_opy_(bstack111lll1l111_opy_):
    if not bstack111lll1l111_opy_:
        return bstack1l1l_opy_ (u"ࠪࠫ᭾")
    return bstack1l1l_opy_ (u"ࠦࢀࢃࠠࠩࡽࢀ࠭ࠧ᭿").format(bstack111lll1l111_opy_.name, bstack111lll1l111_opy_.email)
def bstack11ll11lllll_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack11l111ll11l_opy_ = repo.common_dir
        info = {
            bstack1l1l_opy_ (u"ࠧࡹࡨࡢࠤᮀ"): repo.head.commit.hexsha,
            bstack1l1l_opy_ (u"ࠨࡳࡩࡱࡵࡸࡤࡹࡨࡢࠤᮁ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1l1l_opy_ (u"ࠢࡣࡴࡤࡲࡨ࡮ࠢᮂ"): repo.active_branch.name,
            bstack1l1l_opy_ (u"ࠣࡶࡤ࡫ࠧᮃ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1l1l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡶࡨࡶࠧᮄ"): bstack111l1l1ll1l_opy_(repo.head.commit.committer),
            bstack1l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡷࡩࡷࡥࡤࡢࡶࡨࠦᮅ"): repo.head.commit.committed_datetime.isoformat(),
            bstack1l1l_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࠦᮆ"): bstack111l1l1ll1l_opy_(repo.head.commit.author),
            bstack1l1l_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࡤࡪࡡࡵࡧࠥᮇ"): repo.head.commit.authored_datetime.isoformat(),
            bstack1l1l_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠢᮈ"): repo.head.commit.message,
            bstack1l1l_opy_ (u"ࠢࡳࡱࡲࡸࠧᮉ"): repo.git.rev_parse(bstack1l1l_opy_ (u"ࠣ࠯࠰ࡷ࡭ࡵࡷ࠮ࡶࡲࡴࡱ࡫ࡶࡦ࡮ࠥᮊ")),
            bstack1l1l_opy_ (u"ࠤࡦࡳࡲࡳ࡯࡯ࡡࡪ࡭ࡹࡥࡤࡪࡴࠥᮋ"): bstack11l111ll11l_opy_,
            bstack1l1l_opy_ (u"ࠥࡻࡴࡸ࡫ࡵࡴࡨࡩࡤ࡭ࡩࡵࡡࡧ࡭ࡷࠨᮌ"): subprocess.check_output([bstack1l1l_opy_ (u"ࠦ࡬࡯ࡴࠣᮍ"), bstack1l1l_opy_ (u"ࠧࡸࡥࡷ࠯ࡳࡥࡷࡹࡥࠣᮎ"), bstack1l1l_opy_ (u"ࠨ࠭࠮ࡩ࡬ࡸ࠲ࡩ࡯࡮࡯ࡲࡲ࠲ࡪࡩࡳࠤᮏ")]).strip().decode(
                bstack1l1l_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᮐ")),
            bstack1l1l_opy_ (u"ࠣ࡮ࡤࡷࡹࡥࡴࡢࡩࠥᮑ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1l1l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡵࡢࡷ࡮ࡴࡣࡦࡡ࡯ࡥࡸࡺ࡟ࡵࡣࡪࠦᮒ"): repo.git.rev_list(
                bstack1l1l_opy_ (u"ࠥࡿࢂ࠴࠮ࡼࡿࠥᮓ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111l1ll1l1l_opy_ = []
        for remote in remotes:
            bstack111lll1111l_opy_ = {
                bstack1l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᮔ"): remote.name,
                bstack1l1l_opy_ (u"ࠧࡻࡲ࡭ࠤᮕ"): remote.url,
            }
            bstack111l1ll1l1l_opy_.append(bstack111lll1111l_opy_)
        bstack111ll1l1l11_opy_ = {
            bstack1l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᮖ"): bstack1l1l_opy_ (u"ࠢࡨ࡫ࡷࠦᮗ"),
            **info,
            bstack1l1l_opy_ (u"ࠣࡴࡨࡱࡴࡺࡥࡴࠤᮘ"): bstack111l1ll1l1l_opy_
        }
        bstack111ll1l1l11_opy_ = bstack111ll111lll_opy_(bstack111ll1l1l11_opy_)
        return bstack111ll1l1l11_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack1l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡲࡴࡺࡲࡡࡵ࡫ࡱ࡫ࠥࡍࡩࡵࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠧᮙ").format(err))
        return {}
def bstack111ll1111ll_opy_(bstack11l111ll1l1_opy_=None):
    bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡋࡪࡺࠠࡨ࡫ࡷࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡳࡱࡧࡦ࡭࡫࡯ࡣࡢ࡮࡯ࡽࠥ࡬࡯ࡳ࡯ࡤࡸࡹ࡫ࡤࠡࡨࡲࡶࠥࡇࡉࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱࠤࡺࡹࡥࠡࡥࡤࡷࡪࡹࠠࡧࡱࡵࠤࡪࡧࡣࡩࠢࡩࡳࡱࡪࡥࡳࠢ࡬ࡲࠥࡺࡨࡦࠢ࡯࡭ࡸࡺ࠮ࠋࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥ࡬࡯࡭ࡦࡨࡶࡸࠦࠨ࡭࡫ࡶࡸ࠱ࠦ࡯ࡱࡶ࡬ࡳࡳࡧ࡬ࠪ࠼ࠣࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡓࡵ࡮ࡦ࠼ࠣࡑࡴࡴ࡯࠮ࡴࡨࡴࡴࠦࡡࡱࡲࡵࡳࡦࡩࡨ࠭ࠢࡸࡷࡪࡹࠠࡤࡷࡵࡶࡪࡴࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡠࡵࡳ࠯ࡩࡨࡸࡨࡽࡤࠩࠫࡠࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡊࡳࡰࡵࡻࠣࡰ࡮ࡹࡴࠡ࡝ࡠ࠾ࠥࡓࡵ࡭ࡶ࡬࠱ࡷ࡫ࡰࡰࠢࡤࡴࡵࡸ࡯ࡢࡥ࡫ࠤࡼ࡯ࡴࡩࠢࡱࡳࠥࡹ࡯ࡶࡴࡦࡩࡸࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡦࡦ࠯ࠤࡷ࡫ࡴࡶࡴࡱࡷࠥࡡ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡳࡥࡹ࡮ࡳ࠻ࠢࡐࡹࡱࡺࡩ࠮ࡴࡨࡴࡴࠦࡡࡱࡲࡵࡳࡦࡩࡨࠡࡹ࡬ࡸ࡭ࠦࡳࡱࡧࡦ࡭࡫࡯ࡣࠡࡨࡲࡰࡩ࡫ࡲࡴࠢࡷࡳࠥࡧ࡮ࡢ࡮ࡼࡾࡪࠐࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦ࡬ࡪࡵࡷ࠾ࠥࡒࡩࡴࡶࠣࡳ࡫ࠦࡤࡪࡥࡷࡷ࠱ࠦࡥࡢࡥ࡫ࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡩ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡧࡱࡵࠤࡦࠦࡦࡰ࡮ࡧࡩࡷ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᮚ")
    if bstack11l111ll1l1_opy_ is None:
        bstack11l111ll1l1_opy_ = [os.getcwd()]
    elif isinstance(bstack11l111ll1l1_opy_, list) and len(bstack11l111ll1l1_opy_) == 0:
        return []
    results = []
    for folder in bstack11l111ll1l1_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack1l1l_opy_ (u"ࠦࡋࡵ࡬ࡥࡧࡵࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠤᮛ").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack1l1l_opy_ (u"ࠧࡶࡲࡊࡦࠥᮜ"): bstack1l1l_opy_ (u"ࠨࠢᮝ"),
                bstack1l1l_opy_ (u"ࠢࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠨᮞ"): [],
                bstack1l1l_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࡴࠤᮟ"): [],
                bstack1l1l_opy_ (u"ࠤࡳࡶࡉࡧࡴࡦࠤᮠ"): bstack1l1l_opy_ (u"ࠥࠦᮡ"),
                bstack1l1l_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡑࡪࡹࡳࡢࡩࡨࡷࠧᮢ"): [],
                bstack1l1l_opy_ (u"ࠧࡶࡲࡕ࡫ࡷࡰࡪࠨᮣ"): bstack1l1l_opy_ (u"ࠨࠢᮤ"),
                bstack1l1l_opy_ (u"ࠢࡱࡴࡇࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠢᮥ"): bstack1l1l_opy_ (u"ࠣࠤᮦ"),
                bstack1l1l_opy_ (u"ࠤࡳࡶࡗࡧࡷࡅ࡫ࡩࡪࠧᮧ"): bstack1l1l_opy_ (u"ࠥࠦᮨ")
            }
            bstack111ll1ll11l_opy_ = repo.active_branch.name
            bstack11l111l1111_opy_ = repo.head.commit
            result[bstack1l1l_opy_ (u"ࠦࡵࡸࡉࡥࠤᮩ")] = bstack11l111l1111_opy_.hexsha
            bstack11l111lll1l_opy_ = _111l1llllll_opy_(repo)
            logger.debug(bstack1l1l_opy_ (u"ࠧࡈࡡࡴࡧࠣࡦࡷࡧ࡮ࡤࡪࠣࡪࡴࡸࠠࡤࡱࡰࡴࡦࡸࡩࡴࡱࡱ࠾ࠥࠨ᮪") + str(bstack11l111lll1l_opy_) + bstack1l1l_opy_ (u"ࠨ᮫ࠢ"))
            if bstack11l111lll1l_opy_:
                try:
                    bstack111lll1lll1_opy_ = repo.git.diff(bstack1l1l_opy_ (u"ࠢ࠮࠯ࡱࡥࡲ࡫࠭ࡰࡰ࡯ࡽࠧᮬ"), bstack1lll1l111ll_opy_ (u"ࠣࡽࡥࡥࡸ࡫࡟ࡣࡴࡤࡲࡨ࡮ࡽ࠯࠰࠱ࡿࡨࡻࡲࡳࡧࡱࡸࡤࡨࡲࡢࡰࡦ࡬ࢂࠨᮭ")).split(bstack1l1l_opy_ (u"ࠩ࡟ࡲࠬᮮ"))
                    logger.debug(bstack1l1l_opy_ (u"ࠥࡇ࡭ࡧ࡮ࡨࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡦࡪࡺࡷࡦࡧࡱࠤࢀࡨࡡࡴࡧࡢࡦࡷࡧ࡮ࡤࡪࢀࠤࡦࡴࡤࠡࡽࡦࡹࡷࡸࡥ࡯ࡶࡢࡦࡷࡧ࡮ࡤࡪࢀ࠾ࠥࠨᮯ") + str(bstack111lll1lll1_opy_) + bstack1l1l_opy_ (u"ࠦࠧ᮰"))
                    result[bstack1l1l_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠦ᮱")] = [f.strip() for f in bstack111lll1lll1_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack1lll1l111ll_opy_ (u"ࠨࡻࡣࡣࡶࡩࡤࡨࡲࡢࡰࡦ࡬ࢂ࠴࠮ࡼࡥࡸࡶࡷ࡫࡮ࡵࡡࡥࡶࡦࡴࡣࡩࡿࠥ᮲")))
                except Exception:
                    logger.debug(bstack1l1l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣ࡫ࡪࡺࠠࡤࡪࡤࡲ࡬࡫ࡤࠡࡨ࡬ࡰࡪࡹࠠࡧࡴࡲࡱࠥࡨࡲࡢࡰࡦ࡬ࠥࡩ࡯࡮ࡲࡤࡶ࡮ࡹ࡯࡯࠰ࠣࡊࡦࡲ࡬ࡪࡰࡪࠤࡧࡧࡣ࡬ࠢࡷࡳࠥࡸࡥࡤࡧࡱࡸࠥࡩ࡯࡮࡯࡬ࡸࡸ࠴ࠢ᮳"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack1l1l_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢ᮴")] = _11l11111l1l_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack1l1l_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣ᮵")] = _11l11111l1l_opy_(commits[:5])
            bstack111ll111ll1_opy_ = set()
            bstack11l1111l11l_opy_ = []
            for commit in commits:
                logger.debug(bstack1l1l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡤࡱࡰࡱ࡮ࡺ࠺ࠡࠤ᮶") + str(commit.message) + bstack1l1l_opy_ (u"ࠦࠧ᮷"))
                bstack11l111llll1_opy_ = commit.author.name if commit.author else bstack1l1l_opy_ (u"࡛ࠧ࡮࡬ࡰࡲࡻࡳࠨ᮸")
                bstack111ll111ll1_opy_.add(bstack11l111llll1_opy_)
                bstack11l1111l11l_opy_.append({
                    bstack1l1l_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢ᮹"): commit.message.strip(),
                    bstack1l1l_opy_ (u"ࠢࡶࡵࡨࡶࠧᮺ"): bstack11l111llll1_opy_
                })
            result[bstack1l1l_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࡴࠤᮻ")] = list(bstack111ll111ll1_opy_)
            result[bstack1l1l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡏࡨࡷࡸࡧࡧࡦࡵࠥᮼ")] = bstack11l1111l11l_opy_
            result[bstack1l1l_opy_ (u"ࠥࡴࡷࡊࡡࡵࡧࠥᮽ")] = bstack11l111l1111_opy_.committed_datetime.strftime(bstack1l1l_opy_ (u"ࠦࠪ࡟࠭ࠦ࡯࠰ࠩࡩࠨᮾ"))
            if (not result[bstack1l1l_opy_ (u"ࠧࡶࡲࡕ࡫ࡷࡰࡪࠨᮿ")] or result[bstack1l1l_opy_ (u"ࠨࡰࡳࡖ࡬ࡸࡱ࡫ࠢᯀ")].strip() == bstack1l1l_opy_ (u"ࠢࠣᯁ")) and bstack11l111l1111_opy_.message:
                bstack11l111111ll_opy_ = bstack11l111l1111_opy_.message.strip().splitlines()
                result[bstack1l1l_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤᯂ")] = bstack11l111111ll_opy_[0] if bstack11l111111ll_opy_ else bstack1l1l_opy_ (u"ࠤࠥᯃ")
                if len(bstack11l111111ll_opy_) > 2:
                    result[bstack1l1l_opy_ (u"ࠥࡴࡷࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠥᯄ")] = bstack1l1l_opy_ (u"ࠫࡡࡴࠧᯅ").join(bstack11l111111ll_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack1l1l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡵࡰࡶ࡮ࡤࡸ࡮ࡴࡧࠡࡉ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡧࡱࡵࠤࡆࡏࠠࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠣࠬ࡫ࡵ࡬ࡥࡧࡵ࠾ࠥࢁࡽࠪ࠼ࠣࡿࢂࠦ࠭ࠡࡽࢀࠦᯆ").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _11l111l11l1_opy_(result)
    ]
    return filtered_results
def _11l111l11l1_opy_(result):
    bstack1l1l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡈࡦ࡮ࡳࡩࡷࠦࡴࡰࠢࡦ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡦࠦࡧࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡸࡥࡴࡷ࡯ࡸࠥ࡯ࡳࠡࡸࡤࡰ࡮ࡪࠠࠩࡰࡲࡲ࠲࡫࡭ࡱࡶࡼࠤ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠣࡥࡳࡪࠠࡢࡷࡷ࡬ࡴࡸࡳࠪ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᯇ")
    return (
        isinstance(result.get(bstack1l1l_opy_ (u"ࠢࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠨᯈ"), None), list)
        and len(result[bstack1l1l_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᯉ")]) > 0
        and isinstance(result.get(bstack1l1l_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࡵࠥᯊ"), None), list)
        and len(result[bstack1l1l_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡶࠦᯋ")]) > 0
    )
def _111l1llllll_opy_(repo):
    bstack1l1l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤ࡙ࡸࡹࠡࡶࡲࠤࡩ࡫ࡴࡦࡴࡰ࡭ࡳ࡫ࠠࡵࡪࡨࠤࡧࡧࡳࡦࠢࡥࡶࡦࡴࡣࡩࠢࡩࡳࡷࠦࡴࡩࡧࠣ࡫࡮ࡼࡥ࡯ࠢࡵࡩࡵࡵࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡪࡤࡶࡩࡩ࡯ࡥࡧࡧࠤࡳࡧ࡭ࡦࡵࠣࡥࡳࡪࠠࡸࡱࡵ࡯ࠥࡽࡩࡵࡪࠣࡥࡱࡲࠠࡗࡅࡖࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡷࡹ࠮ࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࠦࡴࡩࡧࠣࡨࡪ࡬ࡡࡶ࡮ࡷࠤࡧࡸࡡ࡯ࡥ࡫ࠤ࡮࡬ࠠࡱࡱࡶࡷ࡮ࡨ࡬ࡦ࠮ࠣࡩࡱࡹࡥࠡࡐࡲࡲࡪ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᯌ")
    try:
        try:
            origin = repo.remotes.origin
            bstack111llll1111_opy_ = origin.refs[bstack1l1l_opy_ (u"ࠬࡎࡅࡂࡆࠪᯍ")]
            target = bstack111llll1111_opy_.reference.name
            if target.startswith(bstack1l1l_opy_ (u"࠭࡯ࡳ࡫ࡪ࡭ࡳ࠵ࠧᯎ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack1l1l_opy_ (u"ࠧࡰࡴ࡬࡫࡮ࡴ࠯ࠨᯏ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _11l11111l1l_opy_(commits):
    bstack1l1l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡉࡨࡸࠥࡲࡩࡴࡶࠣࡳ࡫ࠦࡣࡩࡣࡱ࡫ࡪࡪࠠࡧ࡫࡯ࡩࡸࠦࡦࡳࡱࡰࠤࡦࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡤࡱࡰࡱ࡮ࡺࡳ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᯐ")
    bstack111lll1lll1_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack111llll111l_opy_ in diff:
                        if bstack111llll111l_opy_.a_path:
                            bstack111lll1lll1_opy_.add(bstack111llll111l_opy_.a_path)
                        if bstack111llll111l_opy_.b_path:
                            bstack111lll1lll1_opy_.add(bstack111llll111l_opy_.b_path)
    except Exception:
        pass
    return list(bstack111lll1lll1_opy_)
def bstack111ll111lll_opy_(bstack111ll1l1l11_opy_):
    bstack111llll1l11_opy_ = bstack111llll1l1l_opy_(bstack111ll1l1l11_opy_)
    if bstack111llll1l11_opy_ and bstack111llll1l11_opy_ > bstack11l1l1ll1l1_opy_:
        bstack111ll1l11l1_opy_ = bstack111llll1l11_opy_ - bstack11l1l1ll1l1_opy_
        bstack111l1l1lll1_opy_ = bstack111l1ll1111_opy_(bstack111ll1l1l11_opy_[bstack1l1l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡡࡰࡩࡸࡹࡡࡨࡧࠥᯑ")], bstack111ll1l11l1_opy_)
        bstack111ll1l1l11_opy_[bstack1l1l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡢࡱࡪࡹࡳࡢࡩࡨࠦᯒ")] = bstack111l1l1lll1_opy_
        logger.info(bstack1l1l_opy_ (u"࡙ࠦ࡮ࡥࠡࡥࡲࡱࡲ࡯ࡴࠡࡪࡤࡷࠥࡨࡥࡦࡰࠣࡸࡷࡻ࡮ࡤࡣࡷࡩࡩ࠴ࠠࡔ࡫ࡽࡩࠥࡵࡦࠡࡥࡲࡱࡲ࡯ࡴࠡࡣࡩࡸࡪࡸࠠࡵࡴࡸࡲࡨࡧࡴࡪࡱࡱࠤ࡮ࡹࠠࡼࡿࠣࡏࡇࠨᯓ")
                    .format(bstack111llll1l1l_opy_(bstack111ll1l1l11_opy_) / 1024))
    return bstack111ll1l1l11_opy_
def bstack111llll1l1l_opy_(bstack1l111lll11_opy_):
    try:
        if bstack1l111lll11_opy_:
            bstack111ll11ll1l_opy_ = json.dumps(bstack1l111lll11_opy_)
            bstack111ll11l1l1_opy_ = sys.getsizeof(bstack111ll11ll1l_opy_)
            return bstack111ll11l1l1_opy_
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"࡙ࠧ࡯࡮ࡧࡷ࡬࡮ࡴࡧࠡࡹࡨࡲࡹࠦࡷࡳࡱࡱ࡫ࠥࡽࡨࡪ࡮ࡨࠤࡨࡧ࡬ࡤࡷ࡯ࡥࡹ࡯࡮ࡨࠢࡶ࡭ࡿ࡫ࠠࡰࡨࠣࡎࡘࡕࡎࠡࡱࡥ࡮ࡪࡩࡴ࠻ࠢࡾࢁࠧᯔ").format(e))
    return -1
def bstack111l1ll1111_opy_(field, bstack11l11111ll1_opy_):
    try:
        bstack111ll1l1ll1_opy_ = len(bytes(bstack11l1l1l1ll1_opy_, bstack1l1l_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᯕ")))
        bstack111ll11l11l_opy_ = bytes(field, bstack1l1l_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᯖ"))
        bstack11l111l111l_opy_ = len(bstack111ll11l11l_opy_)
        bstack111ll1l1lll_opy_ = ceil(bstack11l111l111l_opy_ - bstack11l11111ll1_opy_ - bstack111ll1l1ll1_opy_)
        if bstack111ll1l1lll_opy_ > 0:
            bstack111l1lll11l_opy_ = bstack111ll11l11l_opy_[:bstack111ll1l1lll_opy_].decode(bstack1l1l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᯗ"), errors=bstack1l1l_opy_ (u"ࠩ࡬࡫ࡳࡵࡲࡦࠩᯘ")) + bstack11l1l1l1ll1_opy_
            return bstack111l1lll11l_opy_
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡶࡵࡹࡳࡩࡡࡵ࡫ࡱ࡫ࠥ࡬ࡩࡦ࡮ࡧ࠰ࠥࡴ࡯ࡵࡪ࡬ࡲ࡬ࠦࡷࡢࡵࠣࡸࡷࡻ࡮ࡤࡣࡷࡩࡩࠦࡨࡦࡴࡨ࠾ࠥࢁࡽࠣᯙ").format(e))
    return field
def bstack1l1lll1l_opy_():
    env = os.environ
    if (bstack1l1l_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍࠤᯚ") in env and len(env[bstack1l1l_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡕࡓࡎࠥᯛ")]) > 0) or (
            bstack1l1l_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠧᯜ") in env and len(env[bstack1l1l_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡊࡒࡑࡊࠨᯝ")]) > 0):
        return {
            bstack1l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨᯞ"): bstack1l1l_opy_ (u"ࠤࡍࡩࡳࡱࡩ࡯ࡵࠥᯟ"),
            bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᯠ"): env.get(bstack1l1l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢᯡ")),
            bstack1l1l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᯢ"): env.get(bstack1l1l_opy_ (u"ࠨࡊࡐࡄࡢࡒࡆࡓࡅࠣᯣ")),
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᯤ"): env.get(bstack1l1l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᯥ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠤࡆࡍ᯦ࠧ")) == bstack1l1l_opy_ (u"ࠥࡸࡷࡻࡥࠣᯧ") and bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡇࡎࠨᯨ"))):
        return {
            bstack1l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯩ"): bstack1l1l_opy_ (u"ࠨࡃࡪࡴࡦࡰࡪࡉࡉࠣᯪ"),
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯫ"): env.get(bstack1l1l_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᯬ")),
            bstack1l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᯭ"): env.get(bstack1l1l_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡢࡎࡔࡈࠢᯮ")),
            bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᯯ"): env.get(bstack1l1l_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࠣᯰ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠨࡃࡊࠤᯱ")) == bstack1l1l_opy_ (u"ࠢࡵࡴࡸࡩ᯲ࠧ") and bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓ᯳ࠣ"))):
        return {
            bstack1l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᯴"): bstack1l1l_opy_ (u"ࠥࡘࡷࡧࡶࡪࡵࠣࡇࡎࠨ᯵"),
            bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᯶"): env.get(bstack1l1l_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࡤࡈࡕࡊࡎࡇࡣ࡜ࡋࡂࡠࡗࡕࡐࠧ᯷")),
            bstack1l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᯸"): env.get(bstack1l1l_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤ᯹")),
            bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᯺"): env.get(bstack1l1l_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᯻"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠥࡇࡎࠨ᯼")) == bstack1l1l_opy_ (u"ࠦࡹࡸࡵࡦࠤ᯽") and env.get(bstack1l1l_opy_ (u"ࠧࡉࡉࡠࡐࡄࡑࡊࠨ᯾")) == bstack1l1l_opy_ (u"ࠨࡣࡰࡦࡨࡷ࡭࡯ࡰࠣ᯿"):
        return {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰀ"): bstack1l1l_opy_ (u"ࠣࡅࡲࡨࡪࡹࡨࡪࡲࠥᰁ"),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰂ"): None,
            bstack1l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰃ"): None,
            bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᰄ"): None
        }
    if env.get(bstack1l1l_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡄࡕࡅࡓࡉࡈࠣᰅ")) and env.get(bstack1l1l_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡆࡓࡒࡓࡉࡕࠤᰆ")):
        return {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰇ"): bstack1l1l_opy_ (u"ࠣࡄ࡬ࡸࡧࡻࡣ࡬ࡧࡷࠦᰈ"),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰉ"): env.get(bstack1l1l_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡇࡊࡖࡢࡌ࡙࡚ࡐࡠࡑࡕࡍࡌࡏࡎࠣᰊ")),
            bstack1l1l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰋ"): None,
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰌ"): env.get(bstack1l1l_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣᰍ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠢࡄࡋࠥᰎ")) == bstack1l1l_opy_ (u"ࠣࡶࡵࡹࡪࠨᰏ") and bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠤࡇࡖࡔࡔࡅࠣᰐ"))):
        return {
            bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᰑ"): bstack1l1l_opy_ (u"ࠦࡉࡸ࡯࡯ࡧࠥᰒ"),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰓ"): env.get(bstack1l1l_opy_ (u"ࠨࡄࡓࡑࡑࡉࡤࡈࡕࡊࡎࡇࡣࡑࡏࡎࡌࠤᰔ")),
            bstack1l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰕ"): None,
            bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᰖ"): env.get(bstack1l1l_opy_ (u"ࠤࡇࡖࡔࡔࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᰗ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠥࡇࡎࠨᰘ")) == bstack1l1l_opy_ (u"ࠦࡹࡸࡵࡦࠤᰙ") and bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࠣᰚ"))):
        return {
            bstack1l1l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰛ"): bstack1l1l_opy_ (u"ࠢࡔࡧࡰࡥࡵ࡮࡯ࡳࡧࠥᰜ"),
            bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰝ"): env.get(bstack1l1l_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࡤࡕࡒࡈࡃࡑࡍ࡟ࡇࡔࡊࡑࡑࡣ࡚ࡘࡌࠣᰞ")),
            bstack1l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰟ"): env.get(bstack1l1l_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤᰠ")),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰡ"): env.get(bstack1l1l_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡉࡅࠤᰢ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠢࡄࡋࠥᰣ")) == bstack1l1l_opy_ (u"ࠣࡶࡵࡹࡪࠨᰤ") and bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠤࡊࡍ࡙ࡒࡁࡃࡡࡆࡍࠧᰥ"))):
        return {
            bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᰦ"): bstack1l1l_opy_ (u"ࠦࡌ࡯ࡴࡍࡣࡥࠦᰧ"),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰨ"): env.get(bstack1l1l_opy_ (u"ࠨࡃࡊࡡࡍࡓࡇࡥࡕࡓࡎࠥᰩ")),
            bstack1l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰪ"): env.get(bstack1l1l_opy_ (u"ࠣࡅࡌࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᰫ")),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰬ"): env.get(bstack1l1l_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢࡍࡉࠨᰭ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠦࡈࡏࠢᰮ")) == bstack1l1l_opy_ (u"ࠧࡺࡲࡶࡧࠥᰯ") and bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࠤᰰ"))):
        return {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰱ"): bstack1l1l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪ࡫ࡪࡶࡨࠦᰲ"),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰳ"): env.get(bstack1l1l_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᰴ")),
            bstack1l1l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰵ"): env.get(bstack1l1l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡎࡄࡆࡊࡒࠢᰶ")) or env.get(bstack1l1l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡓࡇࡍࡆࠤ᰷")),
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᰸"): env.get(bstack1l1l_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥ᰹"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠤࡗࡊࡤࡈࡕࡊࡎࡇࠦ᰺"))):
        return {
            bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣ᰻"): bstack1l1l_opy_ (u"࡛ࠦ࡯ࡳࡶࡣ࡯ࠤࡘࡺࡵࡥ࡫ࡲࠤ࡙࡫ࡡ࡮ࠢࡖࡩࡷࡼࡩࡤࡧࡶࠦ᰼"),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᰽"): bstack1l1l_opy_ (u"ࠨࡻࡾࡽࢀࠦ᰾").format(env.get(bstack1l1l_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡋࡕࡕࡏࡆࡄࡘࡎࡕࡎࡔࡇࡕ࡚ࡊࡘࡕࡓࡋࠪ᰿")), env.get(bstack1l1l_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡖࡒࡐࡌࡈࡇ࡙ࡏࡄࠨ᱀"))),
            bstack1l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᱁"): env.get(bstack1l1l_opy_ (u"ࠥࡗ࡞࡙ࡔࡆࡏࡢࡈࡊࡌࡉࡏࡋࡗࡍࡔࡔࡉࡅࠤ᱂")),
            bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᱃"): env.get(bstack1l1l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠧ᱄"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠨࡁࡑࡒ࡙ࡉ࡞ࡕࡒࠣ᱅"))):
        return {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᱆"): bstack1l1l_opy_ (u"ࠣࡃࡳࡴࡻ࡫ࡹࡰࡴࠥ᱇"),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᱈"): bstack1l1l_opy_ (u"ࠥࡿࢂ࠵ࡰࡳࡱ࡭ࡩࡨࡺ࠯ࡼࡿ࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠤ᱉").format(env.get(bstack1l1l_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡕࡓࡎࠪ᱊")), env.get(bstack1l1l_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡂࡅࡆࡓ࡚ࡔࡔࡠࡐࡄࡑࡊ࠭᱋")), env.get(bstack1l1l_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡒࡕࡓࡏࡋࡃࡕࡡࡖࡐ࡚ࡍࠧ᱌")), env.get(bstack1l1l_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫᱍ"))),
            bstack1l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᱎ"): env.get(bstack1l1l_opy_ (u"ࠤࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᱏ")),
            bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᱐"): env.get(bstack1l1l_opy_ (u"ࠦࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧ᱑"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠧࡇ࡚ࡖࡔࡈࡣࡍ࡚ࡔࡑࡡࡘࡗࡊࡘ࡟ࡂࡉࡈࡒ࡙ࠨ᱒")) and env.get(bstack1l1l_opy_ (u"ࠨࡔࡇࡡࡅ࡙ࡎࡒࡄࠣ᱓")):
        return {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᱔"): bstack1l1l_opy_ (u"ࠣࡃࡽࡹࡷ࡫ࠠࡄࡋࠥ᱕"),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᱖"): bstack1l1l_opy_ (u"ࠥࡿࢂࢁࡽ࠰ࡡࡥࡹ࡮ࡲࡤ࠰ࡴࡨࡷࡺࡲࡴࡴࡁࡥࡹ࡮ࡲࡤࡊࡦࡀࡿࢂࠨ᱗").format(env.get(bstack1l1l_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡈࡒ࡙ࡓࡊࡁࡕࡋࡒࡒࡘࡋࡒࡗࡇࡕ࡙ࡗࡏࠧ᱘")), env.get(bstack1l1l_opy_ (u"࡙࡙ࠬࡔࡖࡈࡑࡤ࡚ࡅࡂࡏࡓࡖࡔࡐࡅࡄࡖࠪ᱙")), env.get(bstack1l1l_opy_ (u"࠭ࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡍࡉ࠭ᱚ"))),
            bstack1l1l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᱛ"): env.get(bstack1l1l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠣᱜ")),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᱝ"): env.get(bstack1l1l_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠥᱞ"))
        }
    if any([env.get(bstack1l1l_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᱟ")), env.get(bstack1l1l_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡔࡈࡗࡔࡒࡖࡆࡆࡢࡗࡔ࡛ࡒࡄࡇࡢ࡚ࡊࡘࡓࡊࡑࡑࠦᱠ")), env.get(bstack1l1l_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡖࡓ࡚ࡘࡃࡆࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᱡ"))]):
        return {
            bstack1l1l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᱢ"): bstack1l1l_opy_ (u"ࠣࡃ࡚ࡗࠥࡉ࡯ࡥࡧࡅࡹ࡮ࡲࡤࠣᱣ"),
            bstack1l1l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᱤ"): env.get(bstack1l1l_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡐࡖࡄࡏࡍࡈࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᱥ")),
            bstack1l1l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᱦ"): env.get(bstack1l1l_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᱧ")),
            bstack1l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᱨ"): env.get(bstack1l1l_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧᱩ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡎࡶ࡯ࡥࡩࡷࠨᱪ")):
        return {
            bstack1l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᱫ"): bstack1l1l_opy_ (u"ࠥࡆࡦࡳࡢࡰࡱࠥᱬ"),
            bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᱭ"): env.get(bstack1l1l_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡨࡵࡪ࡮ࡧࡖࡪࡹࡵ࡭ࡶࡶ࡙ࡷࡲࠢᱮ")),
            bstack1l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᱯ"): env.get(bstack1l1l_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡴࡪࡲࡶࡹࡐ࡯ࡣࡐࡤࡱࡪࠨᱰ")),
            bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᱱ"): env.get(bstack1l1l_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡥࡹ࡮ࡲࡤࡏࡷࡰࡦࡪࡸࠢᱲ"))
        }
    if env.get(bstack1l1l_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࠦᱳ")) or env.get(bstack1l1l_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡓࡁࡊࡐࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤ࡙ࡔࡂࡔࡗࡉࡉࠨᱴ")):
        return {
            bstack1l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᱵ"): bstack1l1l_opy_ (u"ࠨࡗࡦࡴࡦ࡯ࡪࡸࠢᱶ"),
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᱷ"): env.get(bstack1l1l_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᱸ")),
            bstack1l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱹ"): bstack1l1l_opy_ (u"ࠥࡑࡦ࡯࡮ࠡࡒ࡬ࡴࡪࡲࡩ࡯ࡧࠥᱺ") if env.get(bstack1l1l_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡓࡁࡊࡐࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤ࡙ࡔࡂࡔࡗࡉࡉࠨᱻ")) else None,
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᱼ"): env.get(bstack1l1l_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡈࡋࡗࡣࡈࡕࡍࡎࡋࡗࠦᱽ"))
        }
    if any([env.get(bstack1l1l_opy_ (u"ࠢࡈࡅࡓࡣࡕࡘࡏࡋࡇࡆࡘࠧ᱾")), env.get(bstack1l1l_opy_ (u"ࠣࡉࡆࡐࡔ࡛ࡄࡠࡒࡕࡓࡏࡋࡃࡕࠤ᱿")), env.get(bstack1l1l_opy_ (u"ࠤࡊࡓࡔࡍࡌࡆࡡࡆࡐࡔ࡛ࡄࡠࡒࡕࡓࡏࡋࡃࡕࠤᲀ"))]):
        return {
            bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᲁ"): bstack1l1l_opy_ (u"ࠦࡌࡵ࡯ࡨ࡮ࡨࠤࡈࡲ࡯ࡶࡦࠥᲂ"),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᲃ"): None,
            bstack1l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᲄ"): env.get(bstack1l1l_opy_ (u"ࠢࡑࡔࡒࡎࡊࡉࡔࡠࡋࡇࠦᲅ")),
            bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᲆ"): env.get(bstack1l1l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᲇ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࠨᲈ")):
        return {
            bstack1l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲉ"): bstack1l1l_opy_ (u"࡙ࠧࡨࡪࡲࡳࡥࡧࡲࡥࠣᲊ"),
            bstack1l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᲋"): env.get(bstack1l1l_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨ᲌")),
            bstack1l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ᲍"): bstack1l1l_opy_ (u"ࠤࡍࡳࡧࠦࠣࡼࡿࠥ᲎").format(env.get(bstack1l1l_opy_ (u"ࠪࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡊࡐࡄࡢࡍࡉ࠭᲏"))) if env.get(bstack1l1l_opy_ (u"ࠦࡘࡎࡉࡑࡒࡄࡆࡑࡋ࡟ࡋࡑࡅࡣࡎࡊࠢᲐ")) else None,
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᲑ"): env.get(bstack1l1l_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣᲒ"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠢࡏࡇࡗࡐࡎࡌ࡙ࠣᲓ"))):
        return {
            bstack1l1l_opy_ (u"ࠣࡰࡤࡱࡪࠨᲔ"): bstack1l1l_opy_ (u"ࠤࡑࡩࡹࡲࡩࡧࡻࠥᲕ"),
            bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲖ"): env.get(bstack1l1l_opy_ (u"ࠦࡉࡋࡐࡍࡑ࡜ࡣ࡚ࡘࡌࠣᲗ")),
            bstack1l1l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᲘ"): env.get(bstack1l1l_opy_ (u"ࠨࡓࡊࡖࡈࡣࡓࡇࡍࡆࠤᲙ")),
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲚ"): env.get(bstack1l1l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᲛ"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1l1l_opy_ (u"ࠤࡊࡍ࡙ࡎࡕࡃࡡࡄࡇ࡙ࡏࡏࡏࡕࠥᲜ"))):
        return {
            bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣᲝ"): bstack1l1l_opy_ (u"ࠦࡌ࡯ࡴࡉࡷࡥࠤࡆࡩࡴࡪࡱࡱࡷࠧᲞ"),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᲟ"): bstack1l1l_opy_ (u"ࠨࡻࡾ࠱ࡾࢁ࠴ࡧࡣࡵ࡫ࡲࡲࡸ࠵ࡲࡶࡰࡶ࠳ࢀࢃࠢᲠ").format(env.get(bstack1l1l_opy_ (u"ࠧࡈࡋࡗࡌ࡚ࡈ࡟ࡔࡇࡕ࡚ࡊࡘ࡟ࡖࡔࡏࠫᲡ")), env.get(bstack1l1l_opy_ (u"ࠨࡉࡌࡘࡍ࡛ࡂࡠࡔࡈࡔࡔ࡙ࡉࡕࡑࡕ࡝ࠬᲢ")), env.get(bstack1l1l_opy_ (u"ࠩࡊࡍ࡙ࡎࡕࡃࡡࡕ࡙ࡓࡥࡉࡅࠩᲣ"))),
            bstack1l1l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᲤ"): env.get(bstack1l1l_opy_ (u"ࠦࡌࡏࡔࡉࡗࡅࡣ࡜ࡕࡒࡌࡈࡏࡓ࡜ࠨᲥ")),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᲦ"): env.get(bstack1l1l_opy_ (u"ࠨࡇࡊࡖࡋ࡙ࡇࡥࡒࡖࡐࡢࡍࡉࠨᲧ"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠢࡄࡋࠥᲨ")) == bstack1l1l_opy_ (u"ࠣࡶࡵࡹࡪࠨᲩ") and env.get(bstack1l1l_opy_ (u"ࠤ࡙ࡉࡗࡉࡅࡍࠤᲪ")) == bstack1l1l_opy_ (u"ࠥ࠵ࠧᲫ"):
        return {
            bstack1l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲬ"): bstack1l1l_opy_ (u"ࠧ࡜ࡥࡳࡥࡨࡰࠧᲭ"),
            bstack1l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᲮ"): bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࡼࡿࠥᲯ").format(env.get(bstack1l1l_opy_ (u"ࠨࡘࡈࡖࡈࡋࡌࡠࡗࡕࡐࠬᲰ"))),
            bstack1l1l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᲱ"): None,
            bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲲ"): None,
        }
    if env.get(bstack1l1l_opy_ (u"࡙ࠦࡋࡁࡎࡅࡌࡘ࡞ࡥࡖࡆࡔࡖࡍࡔࡔࠢᲳ")):
        return {
            bstack1l1l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᲴ"): bstack1l1l_opy_ (u"ࠨࡔࡦࡣࡰࡧ࡮ࡺࡹࠣᲵ"),
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᲶ"): None,
            bstack1l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲷ"): env.get(bstack1l1l_opy_ (u"ࠤࡗࡉࡆࡓࡃࡊࡖ࡜ࡣࡕࡘࡏࡋࡇࡆࡘࡤࡔࡁࡎࡇࠥᲸ")),
            bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲹ"): env.get(bstack1l1l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᲺ"))
        }
    if any([env.get(bstack1l1l_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࠣ᲻")), env.get(bstack1l1l_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࡡࡘࡖࡑࠨ᲼")), env.get(bstack1l1l_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠧᲽ")), env.get(bstack1l1l_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࡣ࡙ࡋࡁࡎࠤᲾ"))]):
        return {
            bstack1l1l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᲿ"): bstack1l1l_opy_ (u"ࠥࡇࡴࡴࡣࡰࡷࡵࡷࡪࠨ᳀"),
            bstack1l1l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᳁"): None,
            bstack1l1l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᳂"): env.get(bstack1l1l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢ᳃")) or None,
            bstack1l1l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᳄"): env.get(bstack1l1l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥ᳅"), 0)
        }
    if env.get(bstack1l1l_opy_ (u"ࠤࡊࡓࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢ᳆")):
        return {
            bstack1l1l_opy_ (u"ࠥࡲࡦࡳࡥࠣ᳇"): bstack1l1l_opy_ (u"ࠦࡌࡵࡃࡅࠤ᳈"),
            bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᳉"): None,
            bstack1l1l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᳊"): env.get(bstack1l1l_opy_ (u"ࠢࡈࡑࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧ᳋")),
            bstack1l1l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᳌"): env.get(bstack1l1l_opy_ (u"ࠤࡊࡓࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡄࡑࡘࡒ࡙ࡋࡒࠣ᳍"))
        }
    if env.get(bstack1l1l_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣ᳎")):
        return {
            bstack1l1l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᳏"): bstack1l1l_opy_ (u"ࠧࡉ࡯ࡥࡧࡉࡶࡪࡹࡨࠣ᳐"),
            bstack1l1l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᳑"): env.get(bstack1l1l_opy_ (u"ࠢࡄࡈࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨ᳒")),
            bstack1l1l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ᳓"): env.get(bstack1l1l_opy_ (u"ࠤࡆࡊࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡏࡃࡐࡉ᳔ࠧ")),
            bstack1l1l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᳕"): env.get(bstack1l1l_opy_ (u"ࠦࡈࡌ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤ᳖"))
        }
    return {bstack1l1l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵ᳗ࠦ"): None}
def get_host_info():
    return {
        bstack1l1l_opy_ (u"ࠨࡨࡰࡵࡷࡲࡦࡳࡥ᳘ࠣ"): platform.node(),
        bstack1l1l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠤ᳙"): platform.system(),
        bstack1l1l_opy_ (u"ࠣࡶࡼࡴࡪࠨ᳚"): platform.machine(),
        bstack1l1l_opy_ (u"ࠤࡹࡩࡷࡹࡩࡰࡰࠥ᳛"): platform.version(),
        bstack1l1l_opy_ (u"ࠥࡥࡷࡩࡨ᳜ࠣ"): platform.architecture()[0]
    }
def bstack111ll1111_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111l1ll1ll1_opy_():
    if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲ᳝ࠬ")):
        return bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮᳞ࠫ")
    return bstack1l1l_opy_ (u"࠭ࡵ࡯࡭ࡱࡳࡼࡴ࡟ࡨࡴ࡬ࡨ᳟ࠬ")
def bstack111ll1lllll_opy_(driver):
    info = {
        bstack1l1l_opy_ (u"ࠧࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭᳠"): driver.capabilities,
        bstack1l1l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠬ᳡"): driver.session_id,
        bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ᳢ࠪ"): driver.capabilities.get(bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨ᳣"), None),
        bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ᳤࠭"): driver.capabilities.get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ᳥࠭"), None),
        bstack1l1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᳦"): driver.capabilities.get(bstack1l1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ᳧࠭"), None),
        bstack1l1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢࡺࡪࡸࡳࡪࡱࡱ᳨ࠫ"):driver.capabilities.get(bstack1l1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫᳩ"), None),
    }
    if bstack111l1ll1ll1_opy_() == bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩᳪ"):
        if bstack11ll11ll1_opy_():
            info[bstack1l1l_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬᳫ")] = bstack1l1l_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨࠫᳬ")
        elif driver.capabilities.get(bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹ᳭ࠧ"), {}).get(bstack1l1l_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫᳮ"), False):
            info[bstack1l1l_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩᳯ")] = bstack1l1l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭ᳰ")
        else:
            info[bstack1l1l_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫᳱ")] = bstack1l1l_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᳲ")
    return info
def bstack11ll11ll1_opy_():
    if bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠬࡧࡰࡱࡡࡤࡹࡹࡵ࡭ࡢࡶࡨࠫᳳ")):
        return True
    if bstack1l1l1111l1_opy_(os.environ.get(bstack1l1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧ᳴"), None)):
        return True
    return False
def bstack11l11llll_opy_(bstack11l111l1lll_opy_, url, data, config):
    headers = config.get(bstack1l1l_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨᳵ"), None)
    proxies = bstack1l11l1ll1l_opy_(config, url)
    auth = config.get(bstack1l1l_opy_ (u"ࠨࡣࡸࡸ࡭࠭ᳶ"), None)
    response = requests.request(
            bstack11l111l1lll_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1111l111_opy_(bstack1l1ll111_opy_, size):
    bstack111lll1l1_opy_ = []
    while len(bstack1l1ll111_opy_) > size:
        bstack11l1ll111l_opy_ = bstack1l1ll111_opy_[:size]
        bstack111lll1l1_opy_.append(bstack11l1ll111l_opy_)
        bstack1l1ll111_opy_ = bstack1l1ll111_opy_[size:]
    bstack111lll1l1_opy_.append(bstack1l1ll111_opy_)
    return bstack111lll1l1_opy_
def bstack11l111l1ll1_opy_(message, bstack11l1111l1ll_opy_=False):
    os.write(1, bytes(message, bstack1l1l_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨ᳷")))
    os.write(1, bytes(bstack1l1l_opy_ (u"ࠪࡠࡳ࠭᳸"), bstack1l1l_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪ᳹")))
    if bstack11l1111l1ll_opy_:
        with open(bstack1l1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠲ࡵ࠱࠲ࡻ࠰ࠫᳺ") + os.environ[bstack1l1l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡋࡅࡘࡎࡅࡅࡡࡌࡈࠬ᳻")] + bstack1l1l_opy_ (u"ࠧ࠯࡮ࡲ࡫ࠬ᳼"), bstack1l1l_opy_ (u"ࠨࡣࠪ᳽")) as f:
            f.write(message + bstack1l1l_opy_ (u"ࠩ࡟ࡲࠬ᳾"))
def bstack1l1l111l1l1_opy_():
    return os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭᳿")].lower() == bstack1l1l_opy_ (u"ࠫࡹࡸࡵࡦࠩᴀ")
def bstack1111lllll_opy_():
    return bstack1111llll11_opy_().replace(tzinfo=None).isoformat() + bstack1l1l_opy_ (u"ࠬࡠࠧᴁ")
def bstack111llllll11_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack1l1l_opy_ (u"࡚࠭ࠨᴂ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack1l1l_opy_ (u"࡛ࠧࠩᴃ")))).total_seconds() * 1000
def bstack111lll11lll_opy_(timestamp):
    return bstack11l11l11111_opy_(timestamp).isoformat() + bstack1l1l_opy_ (u"ࠨ࡜ࠪᴄ")
def bstack11l1111111l_opy_(bstack11l111111l1_opy_):
    date_format = bstack1l1l_opy_ (u"ࠩࠨ࡝ࠪࡳࠥࡥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࠲ࠪ࡬ࠧᴅ")
    bstack111ll11lll1_opy_ = datetime.datetime.strptime(bstack11l111111l1_opy_, date_format)
    return bstack111ll11lll1_opy_.isoformat() + bstack1l1l_opy_ (u"ࠪ࡞ࠬᴆ")
def bstack111ll11llll_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1l1l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᴇ")
    else:
        return bstack1l1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᴈ")
def bstack1l1l1111l1_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack1l1l_opy_ (u"࠭ࡴࡳࡷࡨࠫᴉ")
def bstack111l1ll1l11_opy_(val):
    return val.__str__().lower() == bstack1l1l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ᴊ")
def error_handler(bstack111llll1lll_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack111llll1lll_opy_ as e:
                print(bstack1l1l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡾࢁࠥ࠳࠾ࠡࡽࢀ࠾ࠥࢁࡽࠣᴋ").format(func.__name__, bstack111llll1lll_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack111l1lllll1_opy_(bstack111l1llll1l_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack111l1llll1l_opy_(cls, *args, **kwargs)
            except bstack111llll1lll_opy_ as e:
                print(bstack1l1l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡿࢂࠦ࠭࠿ࠢࡾࢁ࠿ࠦࡻࡾࠤᴌ").format(bstack111l1llll1l_opy_.__name__, bstack111llll1lll_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack111l1lllll1_opy_
    else:
        return decorator
def bstack1l11ll1l11_opy_(bstack11111111ll_opy_):
    if os.getenv(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ᴍ")) is not None:
        return bstack1l1l1111l1_opy_(os.getenv(bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᴎ")))
    if bstack1l1l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᴏ") in bstack11111111ll_opy_ and bstack111l1ll1l11_opy_(bstack11111111ll_opy_[bstack1l1l_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᴐ")]):
        return False
    if bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᴑ") in bstack11111111ll_opy_ and bstack111l1ll1l11_opy_(bstack11111111ll_opy_[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᴒ")]):
        return False
    return True
def bstack11ll111l11_opy_():
    try:
        from pytest_bdd import reporting
        bstack111ll111111_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠤᴓ"), None)
        return bstack111ll111111_opy_ is None or bstack111ll111111_opy_ == bstack1l1l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢᴔ")
    except Exception as e:
        return False
def bstack111lll11ll_opy_(hub_url, CONFIG):
    if bstack1llllll1l1_opy_() <= version.parse(bstack1l1l_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫᴕ")):
        if hub_url:
            return bstack1l1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᴖ") + hub_url + bstack1l1l_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥᴗ")
        return bstack1l1ll1ll_opy_
    if hub_url:
        return bstack1l1l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤᴘ") + hub_url + bstack1l1l_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤᴙ")
    return bstack1llll11111_opy_
def bstack111ll1lll11_opy_():
    return isinstance(os.getenv(bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒ࡜ࡘࡊ࡙ࡔࡠࡒࡏ࡙ࡌࡏࡎࠨᴚ")), str)
def bstack1l1l1111l_opy_(url):
    return urlparse(url).hostname
def bstack11111ll11_opy_(hostname):
    for bstack1l111l11l1_opy_ in bstack11l111ll_opy_:
        regex = re.compile(bstack1l111l11l1_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11l1111llll_opy_(bstack111l1ll1lll_opy_, file_name, logger):
    bstack1l11lll11l_opy_ = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠪࢂࠬᴛ")), bstack111l1ll1lll_opy_)
    try:
        if not os.path.exists(bstack1l11lll11l_opy_):
            os.makedirs(bstack1l11lll11l_opy_)
        file_path = os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠫࢃ࠭ᴜ")), bstack111l1ll1lll_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack1l1l_opy_ (u"ࠬࡽࠧᴝ")):
                pass
            with open(file_path, bstack1l1l_opy_ (u"ࠨࡷࠬࠤᴞ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1l1ll11l_opy_.format(str(e)))
def bstack111l1lll111_opy_(file_name, key, value, logger):
    file_path = bstack11l1111llll_opy_(bstack1l1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᴟ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack11ll1l1111_opy_ = json.load(open(file_path, bstack1l1l_opy_ (u"ࠨࡴࡥࠫᴠ")))
        else:
            bstack11ll1l1111_opy_ = {}
        bstack11ll1l1111_opy_[key] = value
        with open(file_path, bstack1l1l_opy_ (u"ࠤࡺ࠯ࠧᴡ")) as outfile:
            json.dump(bstack11ll1l1111_opy_, outfile)
def bstack1ll11llll_opy_(file_name, logger):
    file_path = bstack11l1111llll_opy_(bstack1l1l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᴢ"), file_name, logger)
    bstack11ll1l1111_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack1l1l_opy_ (u"ࠫࡷ࠭ᴣ")) as bstack11llll1111_opy_:
            bstack11ll1l1111_opy_ = json.load(bstack11llll1111_opy_)
    return bstack11ll1l1111_opy_
def bstack1ll111111l_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡩ࡭ࡱ࡫࠺ࠡࠩᴤ") + file_path + bstack1l1l_opy_ (u"࠭ࠠࠨᴥ") + str(e))
def bstack1llllll1l1_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack1l1l_opy_ (u"ࠢ࠽ࡐࡒࡘࡘࡋࡔ࠿ࠤᴦ")
def bstack1llll11l1_opy_(config):
    if bstack1l1l_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᴧ") in config:
        del (config[bstack1l1l_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᴨ")])
        return False
    if bstack1llllll1l1_opy_() < version.parse(bstack1l1l_opy_ (u"ࠪ࠷࠳࠺࠮࠱ࠩᴩ")):
        return False
    if bstack1llllll1l1_opy_() >= version.parse(bstack1l1l_opy_ (u"ࠫ࠹࠴࠱࠯࠷ࠪᴪ")):
        return True
    if bstack1l1l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬᴫ") in config and config[bstack1l1l_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ᴬ")] is False:
        return False
    else:
        return True
def bstack1l11111l11_opy_(args_list, bstack111ll1llll1_opy_):
    index = -1
    for value in bstack111ll1llll1_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1111l1l_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1111l1l_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111l1l1lll_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111l1l1lll_opy_ = bstack111l1l1lll_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack1l1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧᴭ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack1l1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᴮ"), exception=exception)
    def bstack1llllll111l_opy_(self):
        if self.result != bstack1l1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᴯ"):
            return None
        if isinstance(self.exception_type, str) and bstack1l1l_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨᴰ") in self.exception_type:
            return bstack1l1l_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᴱ")
        return bstack1l1l_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᴲ")
    def bstack111l1l1llll_opy_(self):
        if self.result != bstack1l1l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᴳ"):
            return None
        if self.bstack111l1l1lll_opy_:
            return self.bstack111l1l1lll_opy_
        return bstack11l1111ll1l_opy_(self.exception)
def bstack11l1111ll1l_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11l111l1l1l_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack11llll11ll_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack11ll1ll1l_opy_(config, logger):
    try:
        import playwright
        bstack111lllll1l1_opy_ = playwright.__file__
        bstack111ll1l1l1l_opy_ = os.path.split(bstack111lllll1l1_opy_)
        bstack11l1111lll1_opy_ = bstack111ll1l1l1l_opy_[0] + bstack1l1l_opy_ (u"ࠧ࠰ࡦࡵ࡭ࡻ࡫ࡲ࠰ࡲࡤࡧࡰࡧࡧࡦ࠱࡯࡭ࡧ࠵ࡣ࡭࡫࠲ࡧࡱ࡯࠮࡫ࡵࠪᴴ")
        os.environ[bstack1l1l_opy_ (u"ࠨࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜ࠫᴵ")] = bstack1l11ll1ll_opy_(config)
        with open(bstack11l1111lll1_opy_, bstack1l1l_opy_ (u"ࠩࡵࠫᴶ")) as f:
            bstack11l1l1ll1l_opy_ = f.read()
            bstack111ll1ll1ll_opy_ = bstack1l1l_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠩᴷ")
            bstack111ll11l111_opy_ = bstack11l1l1ll1l_opy_.find(bstack111ll1ll1ll_opy_)
            if bstack111ll11l111_opy_ == -1:
              process = subprocess.Popen(bstack1l1l_opy_ (u"ࠦࡳࡶ࡭ࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡪࡰࡴࡨࡡ࡭࠯ࡤ࡫ࡪࡴࡴࠣᴸ"), shell=True, cwd=bstack111ll1l1l1l_opy_[0])
              process.wait()
              bstack111llllll1l_opy_ = bstack1l1l_opy_ (u"ࠬࠨࡵࡴࡧࠣࡷࡹࡸࡩࡤࡶࠥ࠿ࠬᴹ")
              bstack111lllll11l_opy_ = bstack1l1l_opy_ (u"ࠨࠢࠣࠢ࡟ࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴ࡝ࠤ࠾ࠤࡨࡵ࡮ࡴࡶࠣࡿࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠡࡿࠣࡁࠥࡸࡥࡲࡷ࡬ࡶࡪ࠮ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭ࠩ࠼ࠢ࡬ࡪࠥ࠮ࡰࡳࡱࡦࡩࡸࡹ࠮ࡦࡰࡹ࠲ࡌࡒࡏࡃࡃࡏࡣࡆࡍࡅࡏࡖࡢࡌ࡙࡚ࡐࡠࡒࡕࡓ࡝࡟ࠩࠡࡤࡲࡳࡹࡹࡴࡳࡣࡳࠬ࠮ࡁࠠࠣࠤࠥᴺ")
              bstack111ll111l11_opy_ = bstack11l1l1ll1l_opy_.replace(bstack111llllll1l_opy_, bstack111lllll11l_opy_)
              with open(bstack11l1111lll1_opy_, bstack1l1l_opy_ (u"ࠧࡸࠩᴻ")) as f:
                f.write(bstack111ll111l11_opy_)
    except Exception as e:
        logger.error(bstack11l11111l_opy_.format(str(e)))
def bstack11ll11ll11_opy_():
  try:
    bstack111lll1l1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠨࡱࡳࡸ࡮ࡳࡡ࡭ࡡ࡫ࡹࡧࡥࡵࡳ࡮࠱࡮ࡸࡵ࡮ࠨᴼ"))
    bstack111ll1lll1l_opy_ = []
    if os.path.exists(bstack111lll1l1l1_opy_):
      with open(bstack111lll1l1l1_opy_) as f:
        bstack111ll1lll1l_opy_ = json.load(f)
      os.remove(bstack111lll1l1l1_opy_)
    return bstack111ll1lll1l_opy_
  except:
    pass
  return []
def bstack1ll1ll111_opy_(bstack11llllll1l_opy_):
  try:
    bstack111ll1lll1l_opy_ = []
    bstack111lll1l1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠩࡲࡴࡹ࡯࡭ࡢ࡮ࡢ࡬ࡺࡨ࡟ࡶࡴ࡯࠲࡯ࡹ࡯࡯ࠩᴽ"))
    if os.path.exists(bstack111lll1l1l1_opy_):
      with open(bstack111lll1l1l1_opy_) as f:
        bstack111ll1lll1l_opy_ = json.load(f)
    bstack111ll1lll1l_opy_.append(bstack11llllll1l_opy_)
    with open(bstack111lll1l1l1_opy_, bstack1l1l_opy_ (u"ࠪࡻࠬᴾ")) as f:
        json.dump(bstack111ll1lll1l_opy_, f)
  except:
    pass
def bstack11ll11lll_opy_(logger, bstack111ll1ll111_opy_ = False):
  try:
    test_name = os.environ.get(bstack1l1l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧᴿ"), bstack1l1l_opy_ (u"ࠬ࠭ᵀ"))
    if test_name == bstack1l1l_opy_ (u"࠭ࠧᵁ"):
        test_name = threading.current_thread().__dict__.get(bstack1l1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࡂࡥࡦࡢࡸࡪࡹࡴࡠࡰࡤࡱࡪ࠭ᵂ"), bstack1l1l_opy_ (u"ࠨࠩᵃ"))
    bstack11l11111l11_opy_ = bstack1l1l_opy_ (u"ࠩ࠯ࠤࠬᵄ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111ll1ll111_opy_:
        bstack1111lll1l_opy_ = os.environ.get(bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᵅ"), bstack1l1l_opy_ (u"ࠫ࠵࠭ᵆ"))
        bstack1llll1111l_opy_ = {bstack1l1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᵇ"): test_name, bstack1l1l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᵈ"): bstack11l11111l11_opy_, bstack1l1l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᵉ"): bstack1111lll1l_opy_}
        bstack11l111lllll_opy_ = []
        bstack111l1lll1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡲࡳࡴࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧᵊ"))
        if os.path.exists(bstack111l1lll1ll_opy_):
            with open(bstack111l1lll1ll_opy_) as f:
                bstack11l111lllll_opy_ = json.load(f)
        bstack11l111lllll_opy_.append(bstack1llll1111l_opy_)
        with open(bstack111l1lll1ll_opy_, bstack1l1l_opy_ (u"ࠩࡺࠫᵋ")) as f:
            json.dump(bstack11l111lllll_opy_, f)
    else:
        bstack1llll1111l_opy_ = {bstack1l1l_opy_ (u"ࠪࡲࡦࡳࡥࠨᵌ"): test_name, bstack1l1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᵍ"): bstack11l11111l11_opy_, bstack1l1l_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᵎ"): str(multiprocessing.current_process().name)}
        if bstack1l1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪᵏ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1llll1111l_opy_)
  except Exception as e:
      logger.warn(bstack1l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡳࡽࡹ࡫ࡳࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧ࠺ࠡࡽࢀࠦᵐ").format(e))
def bstack1lllll1l1l_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1l1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡲ࡯ࡤ࡭ࠣࡲࡴࡺࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧ࠯ࠤࡺࡹࡩ࡯ࡩࠣࡦࡦࡹࡩࡤࠢࡩ࡭ࡱ࡫ࠠࡰࡲࡨࡶࡦࡺࡩࡰࡰࡶࠫᵑ"))
    try:
      bstack11l111lll11_opy_ = []
      bstack1llll1111l_opy_ = {bstack1l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᵒ"): test_name, bstack1l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᵓ"): error_message, bstack1l1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᵔ"): index}
      bstack111lll11l11_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ᵕ"))
      if os.path.exists(bstack111lll11l11_opy_):
          with open(bstack111lll11l11_opy_) as f:
              bstack11l111lll11_opy_ = json.load(f)
      bstack11l111lll11_opy_.append(bstack1llll1111l_opy_)
      with open(bstack111lll11l11_opy_, bstack1l1l_opy_ (u"࠭ࡷࠨᵖ")) as f:
          json.dump(bstack11l111lll11_opy_, f)
    except Exception as e:
      logger.warn(bstack1l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡵࡳࡧࡵࡴࠡࡨࡸࡲࡳ࡫࡬ࠡࡦࡤࡸࡦࡀࠠࡼࡿࠥᵗ").format(e))
    return
  bstack11l111lll11_opy_ = []
  bstack1llll1111l_opy_ = {bstack1l1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᵘ"): test_name, bstack1l1l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᵙ"): error_message, bstack1l1l_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᵚ"): index}
  bstack111lll11l11_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l_opy_ (u"ࠫࡷࡵࡢࡰࡶࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᵛ"))
  lock_file = bstack111lll11l11_opy_ + bstack1l1l_opy_ (u"ࠬ࠴࡬ࡰࡥ࡮ࠫᵜ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111lll11l11_opy_):
          with open(bstack111lll11l11_opy_, bstack1l1l_opy_ (u"࠭ࡲࠨᵝ")) as f:
              content = f.read().strip()
              if content:
                  bstack11l111lll11_opy_ = json.load(open(bstack111lll11l11_opy_))
      bstack11l111lll11_opy_.append(bstack1llll1111l_opy_)
      with open(bstack111lll11l11_opy_, bstack1l1l_opy_ (u"ࠧࡸࠩᵞ")) as f:
          json.dump(bstack11l111lll11_opy_, f)
  except Exception as e:
    logger.warn(bstack1l1l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡶࡴࡨ࡯ࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧࠠࡸ࡫ࡷ࡬ࠥ࡬ࡩ࡭ࡧࠣࡰࡴࡩ࡫ࡪࡰࡪ࠾ࠥࢁࡽࠣᵟ").format(e))
def bstack111llll1_opy_(bstack11llllllll_opy_, name, logger):
  try:
    bstack1llll1111l_opy_ = {bstack1l1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᵠ"): name, bstack1l1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᵡ"): bstack11llllllll_opy_, bstack1l1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᵢ"): str(threading.current_thread()._name)}
    return bstack1llll1111l_opy_
  except Exception as e:
    logger.warn(bstack1l1l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡣࡧ࡫ࡥࡻ࡫ࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᵣ").format(e))
  return
def bstack111llllllll_opy_():
    return platform.system() == bstack1l1l_opy_ (u"࠭ࡗࡪࡰࡧࡳࡼࡹࠧᵤ")
def bstack1ll1ll11_opy_(bstack11l111ll1ll_opy_, config, logger):
    bstack111ll1l111l_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack11l111ll1ll_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡲࡴࡦࡴࠣࡧࡴࡴࡦࡪࡩࠣ࡯ࡪࡿࡳࠡࡤࡼࠤࡷ࡫ࡧࡦࡺࠣࡱࡦࡺࡣࡩ࠼ࠣࡿࢂࠨᵥ").format(e))
    return bstack111ll1l111l_opy_
def bstack111l1ll11l1_opy_(bstack111ll1ll1l1_opy_, bstack111llll11l1_opy_):
    bstack111lll111ll_opy_ = version.parse(bstack111ll1ll1l1_opy_)
    bstack111l1ll111l_opy_ = version.parse(bstack111llll11l1_opy_)
    if bstack111lll111ll_opy_ > bstack111l1ll111l_opy_:
        return 1
    elif bstack111lll111ll_opy_ < bstack111l1ll111l_opy_:
        return -1
    else:
        return 0
def bstack1111llll11_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack11l11l11111_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll1l1111_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1ll11111_opy_(options, framework, config, bstack1l1ll11l1l_opy_={}):
    if options is None:
        return
    if getattr(options, bstack1l1l_opy_ (u"ࠨࡩࡨࡸࠬᵦ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack11l111ll11_opy_ = caps.get(bstack1l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᵧ"))
    bstack111llll1ll1_opy_ = True
    bstack1l11111l_opy_ = os.environ[bstack1l1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᵨ")]
    bstack1ll111l1l11_opy_ = config.get(bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᵩ"), False)
    if bstack1ll111l1l11_opy_:
        bstack1ll1lll1l11_opy_ = config.get(bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᵪ"), {})
        bstack1ll1lll1l11_opy_[bstack1l1l_opy_ (u"࠭ࡡࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠩᵫ")] = os.getenv(bstack1l1l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᵬ"))
        bstack11ll11ll11l_opy_ = json.loads(os.getenv(bstack1l1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᵭ"), bstack1l1l_opy_ (u"ࠩࡾࢁࠬᵮ"))).get(bstack1l1l_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᵯ"))
    if bstack111l1ll1l11_opy_(caps.get(bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡗ࠴ࡅࠪᵰ"))) or bstack111l1ll1l11_opy_(caps.get(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡠࡹ࠶ࡧࠬᵱ"))):
        bstack111llll1ll1_opy_ = False
    if bstack1llll11l1_opy_({bstack1l1l_opy_ (u"ࠨࡵࡴࡧ࡚࠷ࡈࠨᵲ"): bstack111llll1ll1_opy_}):
        bstack11l111ll11_opy_ = bstack11l111ll11_opy_ or {}
        bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᵳ")] = bstack111ll1l1111_opy_(framework)
        bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵴ")] = bstack1l1l111l1l1_opy_()
        bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᵵ")] = bstack1l11111l_opy_
        bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᵶ")] = bstack1l1ll11l1l_opy_
        if bstack1ll111l1l11_opy_:
            bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᵷ")] = bstack1ll111l1l11_opy_
            bstack11l111ll11_opy_[bstack1l1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᵸ")] = bstack1ll1lll1l11_opy_
            bstack11l111ll11_opy_[bstack1l1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᵹ")][bstack1l1l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᵺ")] = bstack11ll11ll11l_opy_
        if getattr(options, bstack1l1l_opy_ (u"ࠨࡵࡨࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡺࠩᵻ"), None):
            options.set_capability(bstack1l1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᵼ"), bstack11l111ll11_opy_)
        else:
            options[bstack1l1l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᵽ")] = bstack11l111ll11_opy_
    else:
        if getattr(options, bstack1l1l_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬᵾ"), None):
            options.set_capability(bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᵿ"), bstack111ll1l1111_opy_(framework))
            options.set_capability(bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᶀ"), bstack1l1l111l1l1_opy_())
            options.set_capability(bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᶁ"), bstack1l11111l_opy_)
            options.set_capability(bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᶂ"), bstack1l1ll11l1l_opy_)
            if bstack1ll111l1l11_opy_:
                options.set_capability(bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᶃ"), bstack1ll111l1l11_opy_)
                options.set_capability(bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᶄ"), bstack1ll1lll1l11_opy_)
                options.set_capability(bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵ࠱ࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᶅ"), bstack11ll11ll11l_opy_)
        else:
            options[bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᶆ")] = bstack111ll1l1111_opy_(framework)
            options[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᶇ")] = bstack1l1l111l1l1_opy_()
            options[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᶈ")] = bstack1l11111l_opy_
            options[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᶉ")] = bstack1l1ll11l1l_opy_
            if bstack1ll111l1l11_opy_:
                options[bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᶊ")] = bstack1ll111l1l11_opy_
                options[bstack1l1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᶋ")] = bstack1ll1lll1l11_opy_
                options[bstack1l1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᶌ")][bstack1l1l_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᶍ")] = bstack11ll11ll11l_opy_
    return options
def bstack111ll11ll11_opy_(bstack11l11111111_opy_, framework):
    bstack1l1ll11l1l_opy_ = bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠨࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡔࡗࡕࡄࡖࡅࡗࡣࡒࡇࡐࠣᶎ"))
    if bstack11l11111111_opy_ and len(bstack11l11111111_opy_.split(bstack1l1l_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᶏ"))) > 1:
        ws_url = bstack11l11111111_opy_.split(bstack1l1l_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᶐ"))[0]
        if bstack1l1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬᶑ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111lll1l1ll_opy_ = json.loads(urllib.parse.unquote(bstack11l11111111_opy_.split(bstack1l1l_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᶒ"))[1]))
            bstack111lll1l1ll_opy_ = bstack111lll1l1ll_opy_ or {}
            bstack1l11111l_opy_ = os.environ[bstack1l1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᶓ")]
            bstack111lll1l1ll_opy_[bstack1l1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᶔ")] = str(framework) + str(__version__)
            bstack111lll1l1ll_opy_[bstack1l1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᶕ")] = bstack1l1l111l1l1_opy_()
            bstack111lll1l1ll_opy_[bstack1l1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᶖ")] = bstack1l11111l_opy_
            bstack111lll1l1ll_opy_[bstack1l1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᶗ")] = bstack1l1ll11l1l_opy_
            bstack11l11111111_opy_ = bstack11l11111111_opy_.split(bstack1l1l_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᶘ"))[0] + bstack1l1l_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᶙ") + urllib.parse.quote(json.dumps(bstack111lll1l1ll_opy_))
    return bstack11l11111111_opy_
def bstack11111l1ll_opy_():
    global bstack1111l1l1_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1111l1l1_opy_ = BrowserType.connect
    return bstack1111l1l1_opy_
def bstack1l1ll1lll_opy_(framework_name):
    global bstack1lll1l11l1_opy_
    bstack1lll1l11l1_opy_ = framework_name
    return framework_name
def bstack111l11l11_opy_(self, *args, **kwargs):
    global bstack1111l1l1_opy_
    try:
        global bstack1lll1l11l1_opy_
        if bstack1l1l_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᶚ") in kwargs:
            kwargs[bstack1l1l_opy_ (u"ࠬࡽࡳࡆࡰࡧࡴࡴ࡯࡮ࡵࠩᶛ")] = bstack111ll11ll11_opy_(
                kwargs.get(bstack1l1l_opy_ (u"࠭ࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶࠪᶜ"), None),
                bstack1lll1l11l1_opy_
            )
    except Exception as e:
        logger.error(bstack1l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡕࡇࡏࠥࡩࡡࡱࡵ࠽ࠤࢀࢃࠢᶝ").format(str(e)))
    return bstack1111l1l1_opy_(self, *args, **kwargs)
def bstack111lllll111_opy_(bstack111lll11l1l_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1l11l1ll1l_opy_(bstack111lll11l1l_opy_, bstack1l1l_opy_ (u"ࠣࠤᶞ"))
        if proxies and proxies.get(bstack1l1l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳࠣᶟ")):
            parsed_url = urlparse(proxies.get(bstack1l1l_opy_ (u"ࠥ࡬ࡹࡺࡰࡴࠤᶠ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack1l1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡋࡳࡸࡺࠧᶡ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack1l1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨᶢ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack1l1l_opy_ (u"࠭ࡰࡳࡱࡻࡽ࡚ࡹࡥࡳࠩᶣ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack1l1l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖࡡࡴࡵࠪᶤ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11ll1l1l1_opy_(bstack111lll11l1l_opy_):
    bstack111ll1111l1_opy_ = {
        bstack11l1l1111l1_opy_[bstack111ll1l11ll_opy_]: bstack111lll11l1l_opy_[bstack111ll1l11ll_opy_]
        for bstack111ll1l11ll_opy_ in bstack111lll11l1l_opy_
        if bstack111ll1l11ll_opy_ in bstack11l1l1111l1_opy_
    }
    bstack111ll1111l1_opy_[bstack1l1l_opy_ (u"ࠣࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠣᶥ")] = bstack111lllll111_opy_(bstack111lll11l1l_opy_, bstack1l1ll1l1_opy_.get_property(bstack1l1l_opy_ (u"ࠤࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠤᶦ")))
    bstack11l111ll111_opy_ = [element.lower() for element in bstack11l1l1lll11_opy_]
    bstack111llll11ll_opy_(bstack111ll1111l1_opy_, bstack11l111ll111_opy_)
    return bstack111ll1111l1_opy_
def bstack111llll11ll_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack1l1l_opy_ (u"ࠥ࠮࠯࠰ࠪࠣᶧ")
    for value in d.values():
        if isinstance(value, dict):
            bstack111llll11ll_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack111llll11ll_opy_(item, keys)
def bstack1l1l11lll11_opy_():
    bstack111lll111l1_opy_ = [os.environ.get(bstack1l1l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡎࡒࡅࡔࡡࡇࡍࡗࠨᶨ")), os.path.join(os.path.expanduser(bstack1l1l_opy_ (u"ࠧࢄࠢᶩ")), bstack1l1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᶪ")), os.path.join(bstack1l1l_opy_ (u"ࠧ࠰ࡶࡰࡴࠬᶫ"), bstack1l1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᶬ"))]
    for path in bstack111lll111l1_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack1l1l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࠨࠤᶭ") + str(path) + bstack1l1l_opy_ (u"ࠥࠫࠥ࡫ࡸࡪࡵࡷࡷ࠳ࠨᶮ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack1l1l_opy_ (u"ࠦࡌ࡯ࡶࡪࡰࡪࠤࡵ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮ࡴࠢࡩࡳࡷࠦࠧࠣᶯ") + str(path) + bstack1l1l_opy_ (u"ࠧ࠭ࠢᶰ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack1l1l_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࠬࠨᶱ") + str(path) + bstack1l1l_opy_ (u"ࠢࠨࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡬ࡦࡹࠠࡵࡪࡨࠤࡷ࡫ࡱࡶ࡫ࡵࡩࡩࠦࡰࡦࡴࡰ࡭ࡸࡹࡩࡰࡰࡶ࠲ࠧᶲ"))
            else:
                logger.debug(bstack1l1l_opy_ (u"ࠣࡅࡵࡩࡦࡺࡩ࡯ࡩࠣࡪ࡮ࡲࡥࠡࠩࠥᶳ") + str(path) + bstack1l1l_opy_ (u"ࠤࠪࠤࡼ࡯ࡴࡩࠢࡺࡶ࡮ࡺࡥࠡࡲࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲ࠳ࠨᶴ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack1l1l_opy_ (u"ࠥࡓࡵ࡫ࡲࡢࡶ࡬ࡳࡳࠦࡳࡶࡥࡦࡩࡪࡪࡥࡥࠢࡩࡳࡷࠦࠧࠣᶵ") + str(path) + bstack1l1l_opy_ (u"ࠦࠬ࠴ࠢᶶ"))
            return path
        except Exception as e:
            logger.debug(bstack1l1l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡻࡰࠡࡨ࡬ࡰࡪࠦࠧࡼࡲࡤࡸ࡭ࢃࠧ࠻ࠢࠥᶷ") + str(e) + bstack1l1l_opy_ (u"ࠨࠢᶸ"))
    logger.debug(bstack1l1l_opy_ (u"ࠢࡂ࡮࡯ࠤࡵࡧࡴࡩࡵࠣࡪࡦ࡯࡬ࡦࡦ࠱ࠦᶹ"))
    return None
@measure(event_name=EVENTS.bstack11l1l111l1l_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack1ll1l111ll1_opy_(binary_path, bstack1ll1ll1111l_opy_, bs_config):
    logger.debug(bstack1l1l_opy_ (u"ࠣࡅࡸࡶࡷ࡫࡮ࡵࠢࡆࡐࡎࠦࡐࡢࡶ࡫ࠤ࡫ࡵࡵ࡯ࡦ࠽ࠤࢀࢃࠢᶺ").format(binary_path))
    bstack111lllllll1_opy_ = bstack1l1l_opy_ (u"ࠩࠪᶻ")
    bstack111l1llll11_opy_ = {
        bstack1l1l_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᶼ"): __version__,
        bstack1l1l_opy_ (u"ࠦࡴࡹࠢᶽ"): platform.system(),
        bstack1l1l_opy_ (u"ࠧࡵࡳࡠࡣࡵࡧ࡭ࠨᶾ"): platform.machine(),
        bstack1l1l_opy_ (u"ࠨࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠦᶿ"): bstack1l1l_opy_ (u"ࠧ࠱ࠩ᷀"),
        bstack1l1l_opy_ (u"ࠣࡵࡧ࡯ࡤࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠢ᷁"): bstack1l1l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯᷂ࠩ")
    }
    bstack111l1lll1l1_opy_(bstack111l1llll11_opy_)
    try:
        if binary_path:
            if bstack111llllllll_opy_():
                bstack111l1llll11_opy_[bstack1l1l_opy_ (u"ࠪࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᷃")] = subprocess.check_output([binary_path, bstack1l1l_opy_ (u"ࠦࡻ࡫ࡲࡴ࡫ࡲࡲࠧ᷄")]).strip().decode(bstack1l1l_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫ᷅"))
            else:
                bstack111l1llll11_opy_[bstack1l1l_opy_ (u"࠭ࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠫ᷆")] = subprocess.check_output([binary_path, bstack1l1l_opy_ (u"ࠢࡷࡧࡵࡷ࡮ࡵ࡮ࠣ᷇")], stderr=subprocess.DEVNULL).strip().decode(bstack1l1l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧ᷈"))
        response = requests.request(
            bstack1l1l_opy_ (u"ࠩࡊࡉ࡙࠭᷉"),
            url=bstack1l11llll1_opy_(bstack11l11llllll_opy_),
            headers=None,
            auth=(bs_config[bstack1l1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩ᷊ࠬ")], bs_config[bstack1l1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ᷋")]),
            json=None,
            params=bstack111l1llll11_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack1l1l_opy_ (u"ࠬࡻࡲ࡭ࠩ᷌") in data.keys() and bstack1l1l_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡪ࡟ࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ᷍") in data.keys():
            logger.debug(bstack1l1l_opy_ (u"ࠢࡏࡧࡨࡨࠥࡺ࡯ࠡࡷࡳࡨࡦࡺࡥࠡࡤ࡬ࡲࡦࡸࡹ࠭ࠢࡦࡹࡷࡸࡥ࡯ࡶࠣࡦ࡮ࡴࡡࡳࡻࠣࡺࡪࡸࡳࡪࡱࡱ࠾ࠥࢁࡽ᷎ࠣ").format(bstack111l1llll11_opy_[bstack1l1l_opy_ (u"ࠨࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ᷏࠭")]))
            if bstack1l1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡗࡕࡐ᷐ࠬ") in os.environ:
                logger.debug(bstack1l1l_opy_ (u"ࠥࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡨࡩ࡯ࡣࡵࡽࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡢࡵࠣࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡘࡖࡑࠦࡩࡴࠢࡶࡩࡹࠨ᷑"))
                data[bstack1l1l_opy_ (u"ࠫࡺࡸ࡬ࠨ᷒")] = os.environ[bstack1l1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇࡏࡎࡂࡔ࡜ࡣ࡚ࡘࡌࠨᷓ")]
            bstack111lll11111_opy_ = bstack111lll1ll1l_opy_(data[bstack1l1l_opy_ (u"࠭ࡵࡳ࡮ࠪᷔ")], bstack1ll1ll1111l_opy_)
            bstack111lllllll1_opy_ = os.path.join(bstack1ll1ll1111l_opy_, bstack111lll11111_opy_)
            os.chmod(bstack111lllllll1_opy_, 0o777) # bstack111lll11ll1_opy_ permission
            return bstack111lllllll1_opy_
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡲࡪࡽࠠࡔࡆࡎࠤࢀࢃࠢᷕ").format(e))
    return binary_path
def bstack111l1lll1l1_opy_(bstack111l1llll11_opy_):
    try:
        if bstack1l1l_opy_ (u"ࠨ࡮࡬ࡲࡺࡾࠧᷖ") not in bstack111l1llll11_opy_[bstack1l1l_opy_ (u"ࠩࡲࡷࠬᷗ")].lower():
            return
        if os.path.exists(bstack1l1l_opy_ (u"ࠥ࠳ࡪࡺࡣ࠰ࡱࡶ࠱ࡷ࡫࡬ࡦࡣࡶࡩࠧᷘ")):
            with open(bstack1l1l_opy_ (u"ࠦ࠴࡫ࡴࡤ࠱ࡲࡷ࠲ࡸࡥ࡭ࡧࡤࡷࡪࠨᷙ"), bstack1l1l_opy_ (u"ࠧࡸࠢᷚ")) as f:
                bstack111lllll1ll_opy_ = {}
                for line in f:
                    if bstack1l1l_opy_ (u"ࠨ࠽ࠣᷛ") in line:
                        key, value = line.rstrip().split(bstack1l1l_opy_ (u"ࠢ࠾ࠤᷜ"), 1)
                        bstack111lllll1ll_opy_[key] = value.strip(bstack1l1l_opy_ (u"ࠨࠤ࡟ࠫࠬᷝ"))
                bstack111l1llll11_opy_[bstack1l1l_opy_ (u"ࠩࡧ࡭ࡸࡺࡲࡰࠩᷞ")] = bstack111lllll1ll_opy_.get(bstack1l1l_opy_ (u"ࠥࡍࡉࠨᷟ"), bstack1l1l_opy_ (u"ࠦࠧᷠ"))
        elif os.path.exists(bstack1l1l_opy_ (u"ࠧ࠵ࡥࡵࡥ࠲ࡥࡱࡶࡩ࡯ࡧ࠰ࡶࡪࡲࡥࡢࡵࡨࠦᷡ")):
            bstack111l1llll11_opy_[bstack1l1l_opy_ (u"࠭ࡤࡪࡵࡷࡶࡴ࠭ᷢ")] = bstack1l1l_opy_ (u"ࠧࡢ࡮ࡳ࡭ࡳ࡫ࠧᷣ")
    except Exception as e:
        logger.debug(bstack1l1l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡬࡫ࡴࠡࡦ࡬ࡷࡹࡸ࡯ࠡࡱࡩࠤࡱ࡯࡮ࡶࡺࠥᷤ") + e)
@measure(event_name=EVENTS.bstack11l1l11111l_opy_, stage=STAGE.bstack11lll1l1_opy_)
def bstack111lll1ll1l_opy_(bstack111ll11111l_opy_, bstack11l1111l111_opy_):
    logger.debug(bstack1l1l_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡸ࡯࡮࠼ࠣࠦᷥ") + str(bstack111ll11111l_opy_) + bstack1l1l_opy_ (u"ࠥࠦᷦ"))
    zip_path = os.path.join(bstack11l1111l111_opy_, bstack1l1l_opy_ (u"ࠦࡩࡵࡷ࡯࡮ࡲࡥࡩ࡫ࡤࡠࡨ࡬ࡰࡪ࠴ࡺࡪࡲࠥᷧ"))
    bstack111lll11111_opy_ = bstack1l1l_opy_ (u"ࠬ࠭ᷨ")
    with requests.get(bstack111ll11111l_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack1l1l_opy_ (u"ࠨࡷࡣࠤᷩ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack1l1l_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹ࠯ࠤᷪ"))
    with zipfile.ZipFile(zip_path, bstack1l1l_opy_ (u"ࠨࡴࠪᷫ")) as zip_ref:
        bstack111lll1llll_opy_ = zip_ref.namelist()
        if len(bstack111lll1llll_opy_) > 0:
            bstack111lll11111_opy_ = bstack111lll1llll_opy_[0] # bstack11l11111lll_opy_ bstack11l1l1l1l11_opy_ will be bstack11l1111ll11_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11l1111l111_opy_)
        logger.debug(bstack1l1l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࡳࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡦࡺࡷࡶࡦࡩࡴࡦࡦࠣࡸࡴࠦࠧࠣᷬ") + str(bstack11l1111l111_opy_) + bstack1l1l_opy_ (u"ࠥࠫࠧᷭ"))
    os.remove(zip_path)
    return bstack111lll11111_opy_
def get_cli_dir():
    bstack111lll1ll11_opy_ = bstack1l1l11lll11_opy_()
    if bstack111lll1ll11_opy_:
        bstack1ll1ll1111l_opy_ = os.path.join(bstack111lll1ll11_opy_, bstack1l1l_opy_ (u"ࠦࡨࡲࡩࠣᷮ"))
        if not os.path.exists(bstack1ll1ll1111l_opy_):
            os.makedirs(bstack1ll1ll1111l_opy_, mode=0o777, exist_ok=True)
        return bstack1ll1ll1111l_opy_
    else:
        raise FileNotFoundError(bstack1l1l_opy_ (u"ࠧࡔ࡯ࠡࡹࡵ࡭ࡹࡧࡢ࡭ࡧࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡩࡳࡷࠦࡴࡩࡧࠣࡗࡉࡑࠠࡣ࡫ࡱࡥࡷࡿ࠮ࠣᷯ"))
def bstack1lll1ll111l_opy_(bstack1ll1ll1111l_opy_):
    bstack1l1l_opy_ (u"ࠨࠢࠣࡉࡨࡸࠥࡺࡨࡦࠢࡳࡥࡹ࡮ࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼࠤ࡮ࡴࠠࡢࠢࡺࡶ࡮ࡺࡡࡣ࡮ࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠮ࠣࠤࠥᷰ")
    bstack11l1111l1l1_opy_ = [
        os.path.join(bstack1ll1ll1111l_opy_, f)
        for f in os.listdir(bstack1ll1ll1111l_opy_)
        if os.path.isfile(os.path.join(bstack1ll1ll1111l_opy_, f)) and f.startswith(bstack1l1l_opy_ (u"ࠢࡣ࡫ࡱࡥࡷࡿ࠭ࠣᷱ"))
    ]
    if len(bstack11l1111l1l1_opy_) > 0:
        return max(bstack11l1111l1l1_opy_, key=os.path.getmtime) # get bstack111ll11l1ll_opy_ binary
    return bstack1l1l_opy_ (u"ࠣࠤᷲ")
def bstack11ll11l11l1_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1l1llll1ll1_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1l1llll1ll1_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1ll1lll111_opy_(data, keys, default=None):
    bstack1l1l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡖࡥ࡫࡫࡬ࡺࠢࡪࡩࡹࠦࡡࠡࡰࡨࡷࡹ࡫ࡤࠡࡸࡤࡰࡺ࡫ࠠࡧࡴࡲࡱࠥࡧࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡴࡸࠠ࡭࡫ࡶࡸ࠳ࠐࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡨࡦࡺࡡ࠻ࠢࡗ࡬ࡪࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳࡻࠣࡳࡷࠦ࡬ࡪࡵࡷࠤࡹࡵࠠࡵࡴࡤࡺࡪࡸࡳࡦ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠ࡬ࡧࡼࡷ࠿ࠦࡁࠡ࡮࡬ࡷࡹࠦ࡯ࡧࠢ࡮ࡩࡾࡹ࠯ࡪࡰࡧ࡭ࡨ࡫ࡳࠡࡴࡨࡴࡷ࡫ࡳࡦࡰࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡵࡧࡴࡩ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠࡥࡧࡩࡥࡺࡲࡴ࠻࡙ࠢࡥࡱࡻࡥࠡࡶࡲࠤࡷ࡫ࡴࡶࡴࡱࠤ࡮࡬ࠠࡵࡪࡨࠤࡵࡧࡴࡩࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠱ࠎࠥࠦࠠࠡ࠼ࡵࡩࡹࡻࡲ࡯࠼ࠣࡘ࡭࡫ࠠࡷࡣ࡯ࡹࡪࠦࡡࡵࠢࡷ࡬ࡪࠦ࡮ࡦࡵࡷࡩࡩࠦࡰࡢࡶ࡫࠰ࠥࡵࡲࠡࡦࡨࡪࡦࡻ࡬ࡵࠢ࡬ࡪࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᷳ")
    if not data:
        return default
    current = data
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default
def bstack11llll1ll1_opy_(bstack111ll111l1l_opy_, key, value):
    bstack1l1l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡗࡹࡵࡲࡦࠢࡆࡐࡎࠦࡥ࡯ࡸ࡬ࡶࡴࡴ࡭ࡦࡰࡷࠤࡻࡧࡲࡪࡣࡥࡰࡪࡹࠠ࡮ࡣࡳࡴ࡮ࡴࡧࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿ࠮ࠋࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡩ࡬ࡪࡡࡨࡲࡻࡥࡶࡢࡴࡶࡣࡲࡧࡰ࠻ࠢࡇ࡭ࡨࡺࡩࡰࡰࡤࡶࡾࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࡰ࡫ࡹ࠻ࠢࡎࡩࡾࠦࡦࡳࡱࡰࠤࡈࡒࡉࡠࡅࡄࡔࡘࡥࡔࡐࡡࡆࡓࡓࡌࡉࡈࠌࠣࠤࠥࠦࠠࠡࠢࠣࡺࡦࡲࡵࡦ࠼࡚ࠣࡦࡲࡵࡦࠢࡩࡶࡴࡳࠠࡤࡱࡰࡱࡦࡴࡤࠡ࡮࡬ࡲࡪࠦࡡࡳࡩࡸࡱࡪࡴࡴࡴࠌࠣࠤࠥࠦࠢࠣࠤᷴ")
    if key in bstack11lll1111l_opy_:
        bstack1l11l11ll1_opy_ = bstack11lll1111l_opy_[key]
        if isinstance(bstack1l11l11ll1_opy_, list):
            for env_name in bstack1l11l11ll1_opy_:
                bstack111ll111l1l_opy_[env_name] = value
        else:
            bstack111ll111l1l_opy_[bstack1l11l11ll1_opy_] = value