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
from bstack_utils.constants import (bstack1l1ll111ll_opy_, bstack1l1l1lll_opy_, bstack11ll11l1_opy_,
                                    bstack11l1l111l11_opy_, bstack11l11lll1ll_opy_, bstack11l1l1l111l_opy_, bstack11l1l11l111_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1l11ll1ll_opy_, bstack1ll11ll111_opy_
from bstack_utils.proxy import bstack1llllll1ll_opy_, bstack1l111l1l_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1l1llll1_opy_
from bstack_utils.bstack111l111l1_opy_ import bstack11l111l11_opy_
from browserstack_sdk._version import __version__
bstack11l11l1lll_opy_ = Config.bstack1llll1lll_opy_()
logger = bstack1l1llll1_opy_.get_logger(__name__, bstack1l1llll1_opy_.bstack1ll1llll1l1_opy_())
def bstack11ll111l1ll_opy_(config):
    return config[bstack11111l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ᭴")]
def bstack11l1llll1ll_opy_(config):
    return config[bstack11111l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ᭵")]
def bstack1l11l1ll_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111lll111ll_opy_(obj):
    values = []
    bstack11l1111lll1_opy_ = re.compile(bstack11111l_opy_ (u"ࡴࠥࡢࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࡞ࡧ࠯ࠩࠨ᭶"), re.I)
    for key in obj.keys():
        if bstack11l1111lll1_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111ll1111l1_opy_(config):
    tags = []
    tags.extend(bstack111lll111ll_opy_(os.environ))
    tags.extend(bstack111lll111ll_opy_(config))
    return tags
def bstack11l1111llll_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111l1ll1lll_opy_(bstack11l111111l1_opy_):
    if not bstack11l111111l1_opy_:
        return bstack11111l_opy_ (u"ࠪࠫ᭷")
    return bstack11111l_opy_ (u"ࠦࢀࢃࠠࠩࡽࢀ࠭ࠧ᭸").format(bstack11l111111l1_opy_.name, bstack11l111111l1_opy_.email)
def bstack11ll111l11l_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111l1ll1ll1_opy_ = repo.common_dir
        info = {
            bstack11111l_opy_ (u"ࠧࡹࡨࡢࠤ᭹"): repo.head.commit.hexsha,
            bstack11111l_opy_ (u"ࠨࡳࡩࡱࡵࡸࡤࡹࡨࡢࠤ᭺"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack11111l_opy_ (u"ࠢࡣࡴࡤࡲࡨ࡮ࠢ᭻"): repo.active_branch.name,
            bstack11111l_opy_ (u"ࠣࡶࡤ࡫ࠧ᭼"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡶࡨࡶࠧ᭽"): bstack111l1ll1lll_opy_(repo.head.commit.committer),
            bstack11111l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡷࡩࡷࡥࡤࡢࡶࡨࠦ᭾"): repo.head.commit.committed_datetime.isoformat(),
            bstack11111l_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࠦ᭿"): bstack111l1ll1lll_opy_(repo.head.commit.author),
            bstack11111l_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࡤࡪࡡࡵࡧࠥᮀ"): repo.head.commit.authored_datetime.isoformat(),
            bstack11111l_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠢᮁ"): repo.head.commit.message,
            bstack11111l_opy_ (u"ࠢࡳࡱࡲࡸࠧᮂ"): repo.git.rev_parse(bstack11111l_opy_ (u"ࠣ࠯࠰ࡷ࡭ࡵࡷ࠮ࡶࡲࡴࡱ࡫ࡶࡦ࡮ࠥᮃ")),
            bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳ࡯࡯ࡡࡪ࡭ࡹࡥࡤࡪࡴࠥᮄ"): bstack111l1ll1ll1_opy_,
            bstack11111l_opy_ (u"ࠥࡻࡴࡸ࡫ࡵࡴࡨࡩࡤ࡭ࡩࡵࡡࡧ࡭ࡷࠨᮅ"): subprocess.check_output([bstack11111l_opy_ (u"ࠦ࡬࡯ࡴࠣᮆ"), bstack11111l_opy_ (u"ࠧࡸࡥࡷ࠯ࡳࡥࡷࡹࡥࠣᮇ"), bstack11111l_opy_ (u"ࠨ࠭࠮ࡩ࡬ࡸ࠲ࡩ࡯࡮࡯ࡲࡲ࠲ࡪࡩࡳࠤᮈ")]).strip().decode(
                bstack11111l_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᮉ")),
            bstack11111l_opy_ (u"ࠣ࡮ࡤࡷࡹࡥࡴࡢࡩࠥᮊ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡵࡢࡷ࡮ࡴࡣࡦࡡ࡯ࡥࡸࡺ࡟ࡵࡣࡪࠦᮋ"): repo.git.rev_list(
                bstack11111l_opy_ (u"ࠥࡿࢂ࠴࠮ࡼࡿࠥᮌ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111llllllll_opy_ = []
        for remote in remotes:
            bstack11l111l1l1l_opy_ = {
                bstack11111l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᮍ"): remote.name,
                bstack11111l_opy_ (u"ࠧࡻࡲ࡭ࠤᮎ"): remote.url,
            }
            bstack111llllllll_opy_.append(bstack11l111l1l1l_opy_)
        bstack11l111ll11l_opy_ = {
            bstack11111l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᮏ"): bstack11111l_opy_ (u"ࠢࡨ࡫ࡷࠦᮐ"),
            **info,
            bstack11111l_opy_ (u"ࠣࡴࡨࡱࡴࡺࡥࡴࠤᮑ"): bstack111llllllll_opy_
        }
        bstack11l111ll11l_opy_ = bstack11l11111ll1_opy_(bstack11l111ll11l_opy_)
        return bstack11l111ll11l_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack11111l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡲࡴࡺࡲࡡࡵ࡫ࡱ࡫ࠥࡍࡩࡵࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠧᮒ").format(err))
        return {}
def bstack111lllllll1_opy_(bstack111ll11l1ll_opy_=None):
    bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡋࡪࡺࠠࡨ࡫ࡷࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡳࡱࡧࡦ࡭࡫࡯ࡣࡢ࡮࡯ࡽࠥ࡬࡯ࡳ࡯ࡤࡸࡹ࡫ࡤࠡࡨࡲࡶࠥࡇࡉࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱࠤࡺࡹࡥࠡࡥࡤࡷࡪࡹࠠࡧࡱࡵࠤࡪࡧࡣࡩࠢࡩࡳࡱࡪࡥࡳࠢ࡬ࡲࠥࡺࡨࡦࠢ࡯࡭ࡸࡺ࠮ࠋࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥ࡬࡯࡭ࡦࡨࡶࡸࠦࠨ࡭࡫ࡶࡸ࠱ࠦ࡯ࡱࡶ࡬ࡳࡳࡧ࡬ࠪ࠼ࠣࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡓࡵ࡮ࡦ࠼ࠣࡑࡴࡴ࡯࠮ࡴࡨࡴࡴࠦࡡࡱࡲࡵࡳࡦࡩࡨ࠭ࠢࡸࡷࡪࡹࠠࡤࡷࡵࡶࡪࡴࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡠࡵࡳ࠯ࡩࡨࡸࡨࡽࡤࠩࠫࡠࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡊࡳࡰࡵࡻࠣࡰ࡮ࡹࡴࠡ࡝ࡠ࠾ࠥࡓࡵ࡭ࡶ࡬࠱ࡷ࡫ࡰࡰࠢࡤࡴࡵࡸ࡯ࡢࡥ࡫ࠤࡼ࡯ࡴࡩࠢࡱࡳࠥࡹ࡯ࡶࡴࡦࡩࡸࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡦࡦ࠯ࠤࡷ࡫ࡴࡶࡴࡱࡷࠥࡡ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡳࡥࡹ࡮ࡳ࠻ࠢࡐࡹࡱࡺࡩ࠮ࡴࡨࡴࡴࠦࡡࡱࡲࡵࡳࡦࡩࡨࠡࡹ࡬ࡸ࡭ࠦࡳࡱࡧࡦ࡭࡫࡯ࡣࠡࡨࡲࡰࡩ࡫ࡲࡴࠢࡷࡳࠥࡧ࡮ࡢ࡮ࡼࡾࡪࠐࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦ࡬ࡪࡵࡷ࠾ࠥࡒࡩࡴࡶࠣࡳ࡫ࠦࡤࡪࡥࡷࡷ࠱ࠦࡥࡢࡥ࡫ࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡩ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡧࡱࡵࠤࡦࠦࡦࡰ࡮ࡧࡩࡷ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᮓ")
    if bstack111ll11l1ll_opy_ is None:
        bstack111ll11l1ll_opy_ = [os.getcwd()]
    elif isinstance(bstack111ll11l1ll_opy_, list) and len(bstack111ll11l1ll_opy_) == 0:
        return []
    results = []
    for folder in bstack111ll11l1ll_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack11111l_opy_ (u"ࠦࡋࡵ࡬ࡥࡧࡵࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠤᮔ").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack11111l_opy_ (u"ࠧࡶࡲࡊࡦࠥᮕ"): bstack11111l_opy_ (u"ࠨࠢᮖ"),
                bstack11111l_opy_ (u"ࠢࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠨᮗ"): [],
                bstack11111l_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࡴࠤᮘ"): [],
                bstack11111l_opy_ (u"ࠤࡳࡶࡉࡧࡴࡦࠤᮙ"): bstack11111l_opy_ (u"ࠥࠦᮚ"),
                bstack11111l_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡑࡪࡹࡳࡢࡩࡨࡷࠧᮛ"): [],
                bstack11111l_opy_ (u"ࠧࡶࡲࡕ࡫ࡷࡰࡪࠨᮜ"): bstack11111l_opy_ (u"ࠨࠢᮝ"),
                bstack11111l_opy_ (u"ࠢࡱࡴࡇࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠢᮞ"): bstack11111l_opy_ (u"ࠣࠤᮟ"),
                bstack11111l_opy_ (u"ࠤࡳࡶࡗࡧࡷࡅ࡫ࡩࡪࠧᮠ"): bstack11111l_opy_ (u"ࠥࠦᮡ")
            }
            bstack111l1l1llll_opy_ = repo.active_branch.name
            bstack111llll11l1_opy_ = repo.head.commit
            result[bstack11111l_opy_ (u"ࠦࡵࡸࡉࡥࠤᮢ")] = bstack111llll11l1_opy_.hexsha
            bstack111ll1l11l1_opy_ = _11l11l111l1_opy_(repo)
            logger.debug(bstack11111l_opy_ (u"ࠧࡈࡡࡴࡧࠣࡦࡷࡧ࡮ࡤࡪࠣࡪࡴࡸࠠࡤࡱࡰࡴࡦࡸࡩࡴࡱࡱ࠾ࠥࠨᮣ") + str(bstack111ll1l11l1_opy_) + bstack11111l_opy_ (u"ࠨࠢᮤ"))
            if bstack111ll1l11l1_opy_:
                try:
                    bstack111ll111lll_opy_ = repo.git.diff(bstack11111l_opy_ (u"ࠢ࠮࠯ࡱࡥࡲ࡫࠭ࡰࡰ࡯ࡽࠧᮥ"), bstack1ll1lll1l1l_opy_ (u"ࠣࡽࡥࡥࡸ࡫࡟ࡣࡴࡤࡲࡨ࡮ࡽ࠯࠰࠱ࡿࡨࡻࡲࡳࡧࡱࡸࡤࡨࡲࡢࡰࡦ࡬ࢂࠨᮦ")).split(bstack11111l_opy_ (u"ࠩ࡟ࡲࠬᮧ"))
                    logger.debug(bstack11111l_opy_ (u"ࠥࡇ࡭ࡧ࡮ࡨࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡦࡪࡺࡷࡦࡧࡱࠤࢀࡨࡡࡴࡧࡢࡦࡷࡧ࡮ࡤࡪࢀࠤࡦࡴࡤࠡࡽࡦࡹࡷࡸࡥ࡯ࡶࡢࡦࡷࡧ࡮ࡤࡪࢀ࠾ࠥࠨᮨ") + str(bstack111ll111lll_opy_) + bstack11111l_opy_ (u"ࠦࠧᮩ"))
                    result[bstack11111l_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧ᮪ࠦ")] = [f.strip() for f in bstack111ll111lll_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack1ll1lll1l1l_opy_ (u"ࠨࡻࡣࡣࡶࡩࡤࡨࡲࡢࡰࡦ࡬ࢂ࠴࠮ࡼࡥࡸࡶࡷ࡫࡮ࡵࡡࡥࡶࡦࡴࡣࡩࡿ᮫ࠥ")))
                except Exception:
                    logger.debug(bstack11111l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣ࡫ࡪࡺࠠࡤࡪࡤࡲ࡬࡫ࡤࠡࡨ࡬ࡰࡪࡹࠠࡧࡴࡲࡱࠥࡨࡲࡢࡰࡦ࡬ࠥࡩ࡯࡮ࡲࡤࡶ࡮ࡹ࡯࡯࠰ࠣࡊࡦࡲ࡬ࡪࡰࡪࠤࡧࡧࡣ࡬ࠢࡷࡳࠥࡸࡥࡤࡧࡱࡸࠥࡩ࡯࡮࡯࡬ࡸࡸ࠴ࠢᮬ"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack11111l_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᮭ")] = _111ll1l1l1l_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack11111l_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣᮮ")] = _111ll1l1l1l_opy_(commits[:5])
            bstack111ll1l1l11_opy_ = set()
            bstack111llll1l11_opy_ = []
            for commit in commits:
                logger.debug(bstack11111l_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡤࡱࡰࡱ࡮ࡺ࠺ࠡࠤᮯ") + str(commit.message) + bstack11111l_opy_ (u"ࠦࠧ᮰"))
                bstack11l11l11111_opy_ = commit.author.name if commit.author else bstack11111l_opy_ (u"࡛ࠧ࡮࡬ࡰࡲࡻࡳࠨ᮱")
                bstack111ll1l1l11_opy_.add(bstack11l11l11111_opy_)
                bstack111llll1l11_opy_.append({
                    bstack11111l_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢ᮲"): commit.message.strip(),
                    bstack11111l_opy_ (u"ࠢࡶࡵࡨࡶࠧ᮳"): bstack11l11l11111_opy_
                })
            result[bstack11111l_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࡴࠤ᮴")] = list(bstack111ll1l1l11_opy_)
            result[bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡏࡨࡷࡸࡧࡧࡦࡵࠥ᮵")] = bstack111llll1l11_opy_
            result[bstack11111l_opy_ (u"ࠥࡴࡷࡊࡡࡵࡧࠥ᮶")] = bstack111llll11l1_opy_.committed_datetime.strftime(bstack11111l_opy_ (u"ࠦࠪ࡟࠭ࠦ࡯࠰ࠩࡩࠨ᮷"))
            if (not result[bstack11111l_opy_ (u"ࠧࡶࡲࡕ࡫ࡷࡰࡪࠨ᮸")] or result[bstack11111l_opy_ (u"ࠨࡰࡳࡖ࡬ࡸࡱ࡫ࠢ᮹")].strip() == bstack11111l_opy_ (u"ࠢࠣᮺ")) and bstack111llll11l1_opy_.message:
                bstack111ll1l11ll_opy_ = bstack111llll11l1_opy_.message.strip().splitlines()
                result[bstack11111l_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤᮻ")] = bstack111ll1l11ll_opy_[0] if bstack111ll1l11ll_opy_ else bstack11111l_opy_ (u"ࠤࠥᮼ")
                if len(bstack111ll1l11ll_opy_) > 2:
                    result[bstack11111l_opy_ (u"ࠥࡴࡷࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠥᮽ")] = bstack11111l_opy_ (u"ࠫࡡࡴࠧᮾ").join(bstack111ll1l11ll_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack11111l_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡵࡰࡶ࡮ࡤࡸ࡮ࡴࡧࠡࡉ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡧࡱࡵࠤࡆࡏࠠࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠣࠬ࡫ࡵ࡬ࡥࡧࡵ࠾ࠥࢁࡽࠪ࠼ࠣࡿࢂࠦ࠭ࠡࡽࢀࠦᮿ").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _11l11111l1l_opy_(result)
    ]
    return filtered_results
def _11l11111l1l_opy_(result):
    bstack11111l_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡈࡦ࡮ࡳࡩࡷࠦࡴࡰࠢࡦ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡦࠦࡧࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡸࡥࡴࡷ࡯ࡸࠥ࡯ࡳࠡࡸࡤࡰ࡮ࡪࠠࠩࡰࡲࡲ࠲࡫࡭ࡱࡶࡼࠤ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠣࡥࡳࡪࠠࡢࡷࡷ࡬ࡴࡸࡳࠪ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᯀ")
    return (
        isinstance(result.get(bstack11111l_opy_ (u"ࠢࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠨᯁ"), None), list)
        and len(result[bstack11111l_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᯂ")]) > 0
        and isinstance(result.get(bstack11111l_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࡵࠥᯃ"), None), list)
        and len(result[bstack11111l_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡶࠦᯄ")]) > 0
    )
def _11l11l111l1_opy_(repo):
    bstack11111l_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤ࡙ࡸࡹࠡࡶࡲࠤࡩ࡫ࡴࡦࡴࡰ࡭ࡳ࡫ࠠࡵࡪࡨࠤࡧࡧࡳࡦࠢࡥࡶࡦࡴࡣࡩࠢࡩࡳࡷࠦࡴࡩࡧࠣ࡫࡮ࡼࡥ࡯ࠢࡵࡩࡵࡵࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡪࡤࡶࡩࡩ࡯ࡥࡧࡧࠤࡳࡧ࡭ࡦࡵࠣࡥࡳࡪࠠࡸࡱࡵ࡯ࠥࡽࡩࡵࡪࠣࡥࡱࡲࠠࡗࡅࡖࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡷࡹ࠮ࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࠦࡴࡩࡧࠣࡨࡪ࡬ࡡࡶ࡮ࡷࠤࡧࡸࡡ࡯ࡥ࡫ࠤ࡮࡬ࠠࡱࡱࡶࡷ࡮ࡨ࡬ࡦ࠮ࠣࡩࡱࡹࡥࠡࡐࡲࡲࡪ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᯅ")
    try:
        try:
            origin = repo.remotes.origin
            bstack111ll11l1l1_opy_ = origin.refs[bstack11111l_opy_ (u"ࠬࡎࡅࡂࡆࠪᯆ")]
            target = bstack111ll11l1l1_opy_.reference.name
            if target.startswith(bstack11111l_opy_ (u"࠭࡯ࡳ࡫ࡪ࡭ࡳ࠵ࠧᯇ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack11111l_opy_ (u"ࠧࡰࡴ࡬࡫࡮ࡴ࠯ࠨᯈ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _111ll1l1l1l_opy_(commits):
    bstack11111l_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡉࡨࡸࠥࡲࡩࡴࡶࠣࡳ࡫ࠦࡣࡩࡣࡱ࡫ࡪࡪࠠࡧ࡫࡯ࡩࡸࠦࡦࡳࡱࡰࠤࡦࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡤࡱࡰࡱ࡮ࡺࡳ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᯉ")
    bstack111ll111lll_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack11l111llll1_opy_ in diff:
                        if bstack11l111llll1_opy_.a_path:
                            bstack111ll111lll_opy_.add(bstack11l111llll1_opy_.a_path)
                        if bstack11l111llll1_opy_.b_path:
                            bstack111ll111lll_opy_.add(bstack11l111llll1_opy_.b_path)
    except Exception:
        pass
    return list(bstack111ll111lll_opy_)
def bstack11l11111ll1_opy_(bstack11l111ll11l_opy_):
    bstack11l111l1ll1_opy_ = bstack111lllll11l_opy_(bstack11l111ll11l_opy_)
    if bstack11l111l1ll1_opy_ and bstack11l111l1ll1_opy_ > bstack11l1l111l11_opy_:
        bstack111l1ll1l11_opy_ = bstack11l111l1ll1_opy_ - bstack11l1l111l11_opy_
        bstack111lllll1l1_opy_ = bstack11l11111l11_opy_(bstack11l111ll11l_opy_[bstack11111l_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡡࡰࡩࡸࡹࡡࡨࡧࠥᯊ")], bstack111l1ll1l11_opy_)
        bstack11l111ll11l_opy_[bstack11111l_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡢࡱࡪࡹࡳࡢࡩࡨࠦᯋ")] = bstack111lllll1l1_opy_
        logger.info(bstack11111l_opy_ (u"࡙ࠦ࡮ࡥࠡࡥࡲࡱࡲ࡯ࡴࠡࡪࡤࡷࠥࡨࡥࡦࡰࠣࡸࡷࡻ࡮ࡤࡣࡷࡩࡩ࠴ࠠࡔ࡫ࡽࡩࠥࡵࡦࠡࡥࡲࡱࡲ࡯ࡴࠡࡣࡩࡸࡪࡸࠠࡵࡴࡸࡲࡨࡧࡴࡪࡱࡱࠤ࡮ࡹࠠࡼࡿࠣࡏࡇࠨᯌ")
                    .format(bstack111lllll11l_opy_(bstack11l111ll11l_opy_) / 1024))
    return bstack11l111ll11l_opy_
def bstack111lllll11l_opy_(bstack1l11l11l1_opy_):
    try:
        if bstack1l11l11l1_opy_:
            bstack111ll11111l_opy_ = json.dumps(bstack1l11l11l1_opy_)
            bstack111lll11lll_opy_ = sys.getsizeof(bstack111ll11111l_opy_)
            return bstack111lll11lll_opy_
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"࡙ࠧ࡯࡮ࡧࡷ࡬࡮ࡴࡧࠡࡹࡨࡲࡹࠦࡷࡳࡱࡱ࡫ࠥࡽࡨࡪ࡮ࡨࠤࡨࡧ࡬ࡤࡷ࡯ࡥࡹ࡯࡮ࡨࠢࡶ࡭ࡿ࡫ࠠࡰࡨࠣࡎࡘࡕࡎࠡࡱࡥ࡮ࡪࡩࡴ࠻ࠢࡾࢁࠧᯍ").format(e))
    return -1
def bstack11l11111l11_opy_(field, bstack111l1lll1ll_opy_):
    try:
        bstack111lll1l1ll_opy_ = len(bytes(bstack11l11lll1ll_opy_, bstack11111l_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᯎ")))
        bstack111ll1llll1_opy_ = bytes(field, bstack11111l_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᯏ"))
        bstack111ll111ll1_opy_ = len(bstack111ll1llll1_opy_)
        bstack11l111lll1l_opy_ = ceil(bstack111ll111ll1_opy_ - bstack111l1lll1ll_opy_ - bstack111lll1l1ll_opy_)
        if bstack11l111lll1l_opy_ > 0:
            bstack11l111l111l_opy_ = bstack111ll1llll1_opy_[:bstack11l111lll1l_opy_].decode(bstack11111l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᯐ"), errors=bstack11111l_opy_ (u"ࠩ࡬࡫ࡳࡵࡲࡦࠩᯑ")) + bstack11l11lll1ll_opy_
            return bstack11l111l111l_opy_
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡶࡵࡹࡳࡩࡡࡵ࡫ࡱ࡫ࠥ࡬ࡩࡦ࡮ࡧ࠰ࠥࡴ࡯ࡵࡪ࡬ࡲ࡬ࠦࡷࡢࡵࠣࡸࡷࡻ࡮ࡤࡣࡷࡩࡩࠦࡨࡦࡴࡨ࠾ࠥࢁࡽࠣᯒ").format(e))
    return field
def bstack1lllll11l1_opy_():
    env = os.environ
    if (bstack11111l_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍࠤᯓ") in env and len(env[bstack11111l_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡕࡓࡎࠥᯔ")]) > 0) or (
            bstack11111l_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠧᯕ") in env and len(env[bstack11111l_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡊࡒࡑࡊࠨᯖ")]) > 0):
        return {
            bstack11111l_opy_ (u"ࠣࡰࡤࡱࡪࠨᯗ"): bstack11111l_opy_ (u"ࠤࡍࡩࡳࡱࡩ࡯ࡵࠥᯘ"),
            bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᯙ"): env.get(bstack11111l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢᯚ")),
            bstack11111l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᯛ"): env.get(bstack11111l_opy_ (u"ࠨࡊࡐࡄࡢࡒࡆࡓࡅࠣᯜ")),
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᯝ"): env.get(bstack11111l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᯞ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠤࡆࡍࠧᯟ")) == bstack11111l_opy_ (u"ࠥࡸࡷࡻࡥࠣᯠ") and bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡇࡎࠨᯡ"))):
        return {
            bstack11111l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯢ"): bstack11111l_opy_ (u"ࠨࡃࡪࡴࡦࡰࡪࡉࡉࠣᯣ"),
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯤ"): env.get(bstack11111l_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᯥ")),
            bstack11111l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨ᯦ࠦ"): env.get(bstack11111l_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡢࡎࡔࡈࠢᯧ")),
            bstack11111l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᯨ"): env.get(bstack11111l_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࠣᯩ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠨࡃࡊࠤᯪ")) == bstack11111l_opy_ (u"ࠢࡵࡴࡸࡩࠧᯫ") and bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࠣᯬ"))):
        return {
            bstack11111l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᯭ"): bstack11111l_opy_ (u"ࠥࡘࡷࡧࡶࡪࡵࠣࡇࡎࠨᯮ"),
            bstack11111l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᯯ"): env.get(bstack11111l_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࡤࡈࡕࡊࡎࡇࡣ࡜ࡋࡂࡠࡗࡕࡐࠧᯰ")),
            bstack11111l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᯱ"): env.get(bstack11111l_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤ᯲")),
            bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸ᯳ࠢ"): env.get(bstack11111l_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᯴"))
        }
    if env.get(bstack11111l_opy_ (u"ࠥࡇࡎࠨ᯵")) == bstack11111l_opy_ (u"ࠦࡹࡸࡵࡦࠤ᯶") and env.get(bstack11111l_opy_ (u"ࠧࡉࡉࡠࡐࡄࡑࡊࠨ᯷")) == bstack11111l_opy_ (u"ࠨࡣࡰࡦࡨࡷ࡭࡯ࡰࠣ᯸"):
        return {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᯹"): bstack11111l_opy_ (u"ࠣࡅࡲࡨࡪࡹࡨࡪࡲࠥ᯺"),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᯻"): None,
            bstack11111l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᯼"): None,
            bstack11111l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᯽"): None
        }
    if env.get(bstack11111l_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡄࡕࡅࡓࡉࡈࠣ᯾")) and env.get(bstack11111l_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡆࡓࡒࡓࡉࡕࠤ᯿")):
        return {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰀ"): bstack11111l_opy_ (u"ࠣࡄ࡬ࡸࡧࡻࡣ࡬ࡧࡷࠦᰁ"),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰂ"): env.get(bstack11111l_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡇࡊࡖࡢࡌ࡙࡚ࡐࡠࡑࡕࡍࡌࡏࡎࠣᰃ")),
            bstack11111l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰄ"): None,
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰅ"): env.get(bstack11111l_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣᰆ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠢࡄࡋࠥᰇ")) == bstack11111l_opy_ (u"ࠣࡶࡵࡹࡪࠨᰈ") and bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠤࡇࡖࡔࡔࡅࠣᰉ"))):
        return {
            bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣᰊ"): bstack11111l_opy_ (u"ࠦࡉࡸ࡯࡯ࡧࠥᰋ"),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰌ"): env.get(bstack11111l_opy_ (u"ࠨࡄࡓࡑࡑࡉࡤࡈࡕࡊࡎࡇࡣࡑࡏࡎࡌࠤᰍ")),
            bstack11111l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰎ"): None,
            bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᰏ"): env.get(bstack11111l_opy_ (u"ࠤࡇࡖࡔࡔࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᰐ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠥࡇࡎࠨᰑ")) == bstack11111l_opy_ (u"ࠦࡹࡸࡵࡦࠤᰒ") and bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࠣᰓ"))):
        return {
            bstack11111l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰔ"): bstack11111l_opy_ (u"ࠢࡔࡧࡰࡥࡵ࡮࡯ࡳࡧࠥᰕ"),
            bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰖ"): env.get(bstack11111l_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࡤࡕࡒࡈࡃࡑࡍ࡟ࡇࡔࡊࡑࡑࡣ࡚ࡘࡌࠣᰗ")),
            bstack11111l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰘ"): env.get(bstack11111l_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤᰙ")),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰚ"): env.get(bstack11111l_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡉࡅࠤᰛ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠢࡄࡋࠥᰜ")) == bstack11111l_opy_ (u"ࠣࡶࡵࡹࡪࠨᰝ") and bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠤࡊࡍ࡙ࡒࡁࡃࡡࡆࡍࠧᰞ"))):
        return {
            bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣᰟ"): bstack11111l_opy_ (u"ࠦࡌ࡯ࡴࡍࡣࡥࠦᰠ"),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰡ"): env.get(bstack11111l_opy_ (u"ࠨࡃࡊࡡࡍࡓࡇࡥࡕࡓࡎࠥᰢ")),
            bstack11111l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰣ"): env.get(bstack11111l_opy_ (u"ࠣࡅࡌࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᰤ")),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰥ"): env.get(bstack11111l_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢࡍࡉࠨᰦ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠦࡈࡏࠢᰧ")) == bstack11111l_opy_ (u"ࠧࡺࡲࡶࡧࠥᰨ") and bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࠤᰩ"))):
        return {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰪ"): bstack11111l_opy_ (u"ࠣࡄࡸ࡭ࡱࡪ࡫ࡪࡶࡨࠦᰫ"),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰬ"): env.get(bstack11111l_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᰭ")),
            bstack11111l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰮ"): env.get(bstack11111l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡎࡄࡆࡊࡒࠢᰯ")) or env.get(bstack11111l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡓࡇࡍࡆࠤᰰ")),
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᰱ"): env.get(bstack11111l_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᰲ"))
        }
    if bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠤࡗࡊࡤࡈࡕࡊࡎࡇࠦᰳ"))):
        return {
            bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣᰴ"): bstack11111l_opy_ (u"࡛ࠦ࡯ࡳࡶࡣ࡯ࠤࡘࡺࡵࡥ࡫ࡲࠤ࡙࡫ࡡ࡮ࠢࡖࡩࡷࡼࡩࡤࡧࡶࠦᰵ"),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰶ"): bstack11111l_opy_ (u"ࠨࡻࡾࡽࢀ᰷ࠦ").format(env.get(bstack11111l_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡋࡕࡕࡏࡆࡄࡘࡎࡕࡎࡔࡇࡕ࡚ࡊࡘࡕࡓࡋࠪ᰸")), env.get(bstack11111l_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡖࡒࡐࡌࡈࡇ࡙ࡏࡄࠨ᰹"))),
            bstack11111l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᰺"): env.get(bstack11111l_opy_ (u"ࠥࡗ࡞࡙ࡔࡆࡏࡢࡈࡊࡌࡉࡏࡋࡗࡍࡔࡔࡉࡅࠤ᰻")),
            bstack11111l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᰼"): env.get(bstack11111l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠧ᰽"))
        }
    if bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠨࡁࡑࡒ࡙ࡉ࡞ࡕࡒࠣ᰾"))):
        return {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᰿"): bstack11111l_opy_ (u"ࠣࡃࡳࡴࡻ࡫ࡹࡰࡴࠥ᱀"),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᱁"): bstack11111l_opy_ (u"ࠥࡿࢂ࠵ࡰࡳࡱ࡭ࡩࡨࡺ࠯ࡼࡿ࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠤ᱂").format(env.get(bstack11111l_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡕࡓࡎࠪ᱃")), env.get(bstack11111l_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡂࡅࡆࡓ࡚ࡔࡔࡠࡐࡄࡑࡊ࠭᱄")), env.get(bstack11111l_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡒࡕࡓࡏࡋࡃࡕࡡࡖࡐ࡚ࡍࠧ᱅")), env.get(bstack11111l_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫ᱆"))),
            bstack11111l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ᱇"): env.get(bstack11111l_opy_ (u"ࠤࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨ᱈")),
            bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᱉"): env.get(bstack11111l_opy_ (u"ࠦࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧ᱊"))
        }
    if env.get(bstack11111l_opy_ (u"ࠧࡇ࡚ࡖࡔࡈࡣࡍ࡚ࡔࡑࡡࡘࡗࡊࡘ࡟ࡂࡉࡈࡒ࡙ࠨ᱋")) and env.get(bstack11111l_opy_ (u"ࠨࡔࡇࡡࡅ࡙ࡎࡒࡄࠣ᱌")):
        return {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᱍ"): bstack11111l_opy_ (u"ࠣࡃࡽࡹࡷ࡫ࠠࡄࡋࠥᱎ"),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᱏ"): bstack11111l_opy_ (u"ࠥࡿࢂࢁࡽ࠰ࡡࡥࡹ࡮ࡲࡤ࠰ࡴࡨࡷࡺࡲࡴࡴࡁࡥࡹ࡮ࡲࡤࡊࡦࡀࡿࢂࠨ᱐").format(env.get(bstack11111l_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡈࡒ࡙ࡓࡊࡁࡕࡋࡒࡒࡘࡋࡒࡗࡇࡕ࡙ࡗࡏࠧ᱑")), env.get(bstack11111l_opy_ (u"࡙࡙ࠬࡔࡖࡈࡑࡤ࡚ࡅࡂࡏࡓࡖࡔࡐࡅࡄࡖࠪ᱒")), env.get(bstack11111l_opy_ (u"࠭ࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡍࡉ࠭᱓"))),
            bstack11111l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᱔"): env.get(bstack11111l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠣ᱕")),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ᱖"): env.get(bstack11111l_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠥ᱗"))
        }
    if any([env.get(bstack11111l_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤ᱘")), env.get(bstack11111l_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡔࡈࡗࡔࡒࡖࡆࡆࡢࡗࡔ࡛ࡒࡄࡇࡢ࡚ࡊࡘࡓࡊࡑࡑࠦ᱙")), env.get(bstack11111l_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡖࡓ࡚ࡘࡃࡆࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᱚ"))]):
        return {
            bstack11111l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᱛ"): bstack11111l_opy_ (u"ࠣࡃ࡚ࡗࠥࡉ࡯ࡥࡧࡅࡹ࡮ࡲࡤࠣᱜ"),
            bstack11111l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᱝ"): env.get(bstack11111l_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡐࡖࡄࡏࡍࡈࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᱞ")),
            bstack11111l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᱟ"): env.get(bstack11111l_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᱠ")),
            bstack11111l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᱡ"): env.get(bstack11111l_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧᱢ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡎࡶ࡯ࡥࡩࡷࠨᱣ")):
        return {
            bstack11111l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᱤ"): bstack11111l_opy_ (u"ࠥࡆࡦࡳࡢࡰࡱࠥᱥ"),
            bstack11111l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᱦ"): env.get(bstack11111l_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡨࡵࡪ࡮ࡧࡖࡪࡹࡵ࡭ࡶࡶ࡙ࡷࡲࠢᱧ")),
            bstack11111l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᱨ"): env.get(bstack11111l_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡴࡪࡲࡶࡹࡐ࡯ࡣࡐࡤࡱࡪࠨᱩ")),
            bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᱪ"): env.get(bstack11111l_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡥࡹ࡮ࡲࡤࡏࡷࡰࡦࡪࡸࠢᱫ"))
        }
    if env.get(bstack11111l_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࠦᱬ")) or env.get(bstack11111l_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡓࡁࡊࡐࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤ࡙ࡔࡂࡔࡗࡉࡉࠨᱭ")):
        return {
            bstack11111l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᱮ"): bstack11111l_opy_ (u"ࠨࡗࡦࡴࡦ࡯ࡪࡸࠢᱯ"),
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᱰ"): env.get(bstack11111l_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᱱ")),
            bstack11111l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱲ"): bstack11111l_opy_ (u"ࠥࡑࡦ࡯࡮ࠡࡒ࡬ࡴࡪࡲࡩ࡯ࡧࠥᱳ") if env.get(bstack11111l_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡓࡁࡊࡐࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤ࡙ࡔࡂࡔࡗࡉࡉࠨᱴ")) else None,
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᱵ"): env.get(bstack11111l_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡈࡋࡗࡣࡈࡕࡍࡎࡋࡗࠦᱶ"))
        }
    if any([env.get(bstack11111l_opy_ (u"ࠢࡈࡅࡓࡣࡕࡘࡏࡋࡇࡆࡘࠧᱷ")), env.get(bstack11111l_opy_ (u"ࠣࡉࡆࡐࡔ࡛ࡄࡠࡒࡕࡓࡏࡋࡃࡕࠤᱸ")), env.get(bstack11111l_opy_ (u"ࠤࡊࡓࡔࡍࡌࡆࡡࡆࡐࡔ࡛ࡄࡠࡒࡕࡓࡏࡋࡃࡕࠤᱹ"))]):
        return {
            bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣᱺ"): bstack11111l_opy_ (u"ࠦࡌࡵ࡯ࡨ࡮ࡨࠤࡈࡲ࡯ࡶࡦࠥᱻ"),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᱼ"): None,
            bstack11111l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᱽ"): env.get(bstack11111l_opy_ (u"ࠢࡑࡔࡒࡎࡊࡉࡔࡠࡋࡇࠦ᱾")),
            bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᱿"): env.get(bstack11111l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᲀ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࠨᲁ")):
        return {
            bstack11111l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲂ"): bstack11111l_opy_ (u"࡙ࠧࡨࡪࡲࡳࡥࡧࡲࡥࠣᲃ"),
            bstack11111l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᲄ"): env.get(bstack11111l_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᲅ")),
            bstack11111l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲆ"): bstack11111l_opy_ (u"ࠤࡍࡳࡧࠦࠣࡼࡿࠥᲇ").format(env.get(bstack11111l_opy_ (u"ࠪࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡊࡐࡄࡢࡍࡉ࠭ᲈ"))) if env.get(bstack11111l_opy_ (u"ࠦࡘࡎࡉࡑࡒࡄࡆࡑࡋ࡟ࡋࡑࡅࡣࡎࡊࠢᲉ")) else None,
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᲊ"): env.get(bstack11111l_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᲋"))
        }
    if bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠢࡏࡇࡗࡐࡎࡌ࡙ࠣ᲌"))):
        return {
            bstack11111l_opy_ (u"ࠣࡰࡤࡱࡪࠨ᲍"): bstack11111l_opy_ (u"ࠤࡑࡩࡹࡲࡩࡧࡻࠥ᲎"),
            bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᲏"): env.get(bstack11111l_opy_ (u"ࠦࡉࡋࡐࡍࡑ࡜ࡣ࡚ࡘࡌࠣᲐ")),
            bstack11111l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᲑ"): env.get(bstack11111l_opy_ (u"ࠨࡓࡊࡖࡈࡣࡓࡇࡍࡆࠤᲒ")),
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲓ"): env.get(bstack11111l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᲔ"))
        }
    if bstack1lll11ll11_opy_(env.get(bstack11111l_opy_ (u"ࠤࡊࡍ࡙ࡎࡕࡃࡡࡄࡇ࡙ࡏࡏࡏࡕࠥᲕ"))):
        return {
            bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣᲖ"): bstack11111l_opy_ (u"ࠦࡌ࡯ࡴࡉࡷࡥࠤࡆࡩࡴࡪࡱࡱࡷࠧᲗ"),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᲘ"): bstack11111l_opy_ (u"ࠨࡻࡾ࠱ࡾࢁ࠴ࡧࡣࡵ࡫ࡲࡲࡸ࠵ࡲࡶࡰࡶ࠳ࢀࢃࠢᲙ").format(env.get(bstack11111l_opy_ (u"ࠧࡈࡋࡗࡌ࡚ࡈ࡟ࡔࡇࡕ࡚ࡊࡘ࡟ࡖࡔࡏࠫᲚ")), env.get(bstack11111l_opy_ (u"ࠨࡉࡌࡘࡍ࡛ࡂࡠࡔࡈࡔࡔ࡙ࡉࡕࡑࡕ࡝ࠬᲛ")), env.get(bstack11111l_opy_ (u"ࠩࡊࡍ࡙ࡎࡕࡃࡡࡕ࡙ࡓࡥࡉࡅࠩᲜ"))),
            bstack11111l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᲝ"): env.get(bstack11111l_opy_ (u"ࠦࡌࡏࡔࡉࡗࡅࡣ࡜ࡕࡒࡌࡈࡏࡓ࡜ࠨᲞ")),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᲟ"): env.get(bstack11111l_opy_ (u"ࠨࡇࡊࡖࡋ࡙ࡇࡥࡒࡖࡐࡢࡍࡉࠨᲠ"))
        }
    if env.get(bstack11111l_opy_ (u"ࠢࡄࡋࠥᲡ")) == bstack11111l_opy_ (u"ࠣࡶࡵࡹࡪࠨᲢ") and env.get(bstack11111l_opy_ (u"ࠤ࡙ࡉࡗࡉࡅࡍࠤᲣ")) == bstack11111l_opy_ (u"ࠥ࠵ࠧᲤ"):
        return {
            bstack11111l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲥ"): bstack11111l_opy_ (u"ࠧ࡜ࡥࡳࡥࡨࡰࠧᲦ"),
            bstack11111l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᲧ"): bstack11111l_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࡼࡿࠥᲨ").format(env.get(bstack11111l_opy_ (u"ࠨࡘࡈࡖࡈࡋࡌࡠࡗࡕࡐࠬᲩ"))),
            bstack11111l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᲪ"): None,
            bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲫ"): None,
        }
    if env.get(bstack11111l_opy_ (u"࡙ࠦࡋࡁࡎࡅࡌࡘ࡞ࡥࡖࡆࡔࡖࡍࡔࡔࠢᲬ")):
        return {
            bstack11111l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᲭ"): bstack11111l_opy_ (u"ࠨࡔࡦࡣࡰࡧ࡮ࡺࡹࠣᲮ"),
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᲯ"): None,
            bstack11111l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲰ"): env.get(bstack11111l_opy_ (u"ࠤࡗࡉࡆࡓࡃࡊࡖ࡜ࡣࡕࡘࡏࡋࡇࡆࡘࡤࡔࡁࡎࡇࠥᲱ")),
            bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲲ"): env.get(bstack11111l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᲳ"))
        }
    if any([env.get(bstack11111l_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࠣᲴ")), env.get(bstack11111l_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࡡࡘࡖࡑࠨᲵ")), env.get(bstack11111l_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠧᲶ")), env.get(bstack11111l_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࡣ࡙ࡋࡁࡎࠤᲷ"))]):
        return {
            bstack11111l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᲸ"): bstack11111l_opy_ (u"ࠥࡇࡴࡴࡣࡰࡷࡵࡷࡪࠨᲹ"),
            bstack11111l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᲺ"): None,
            bstack11111l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᲻"): env.get(bstack11111l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢ᲼")) or None,
            bstack11111l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲽ"): env.get(bstack11111l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᲾ"), 0)
        }
    if env.get(bstack11111l_opy_ (u"ࠤࡊࡓࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢᲿ")):
        return {
            bstack11111l_opy_ (u"ࠥࡲࡦࡳࡥࠣ᳀"): bstack11111l_opy_ (u"ࠦࡌࡵࡃࡅࠤ᳁"),
            bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᳂"): None,
            bstack11111l_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᳃"): env.get(bstack11111l_opy_ (u"ࠢࡈࡑࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧ᳄")),
            bstack11111l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᳅"): env.get(bstack11111l_opy_ (u"ࠤࡊࡓࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡄࡑࡘࡒ࡙ࡋࡒࠣ᳆"))
        }
    if env.get(bstack11111l_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣ᳇")):
        return {
            bstack11111l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᳈"): bstack11111l_opy_ (u"ࠧࡉ࡯ࡥࡧࡉࡶࡪࡹࡨࠣ᳉"),
            bstack11111l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᳊"): env.get(bstack11111l_opy_ (u"ࠢࡄࡈࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨ᳋")),
            bstack11111l_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ᳌"): env.get(bstack11111l_opy_ (u"ࠤࡆࡊࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡏࡃࡐࡉࠧ᳍")),
            bstack11111l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᳎"): env.get(bstack11111l_opy_ (u"ࠦࡈࡌ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤ᳏"))
        }
    return {bstack11111l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᳐"): None}
def get_host_info():
    return {
        bstack11111l_opy_ (u"ࠨࡨࡰࡵࡷࡲࡦࡳࡥࠣ᳑"): platform.node(),
        bstack11111l_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠤ᳒"): platform.system(),
        bstack11111l_opy_ (u"ࠣࡶࡼࡴࡪࠨ᳓"): platform.machine(),
        bstack11111l_opy_ (u"ࠤࡹࡩࡷࡹࡩࡰࡰ᳔ࠥ"): platform.version(),
        bstack11111l_opy_ (u"ࠥࡥࡷࡩࡨ᳕ࠣ"): platform.architecture()[0]
    }
def bstack1ll11l1111_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111lll11l1l_opy_():
    if bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲ᳖ࠬ")):
        return bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮᳗ࠫ")
    return bstack11111l_opy_ (u"࠭ࡵ࡯࡭ࡱࡳࡼࡴ࡟ࡨࡴ࡬ࡨ᳘ࠬ")
def bstack11l11111lll_opy_(driver):
    info = {
        bstack11111l_opy_ (u"ࠧࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ᳙࠭"): driver.capabilities,
        bstack11111l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠬ᳚"): driver.session_id,
        bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪ᳛"): driver.capabilities.get(bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨ᳜"), None),
        bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ᳝࠭"): driver.capabilities.get(bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ᳞࠭"), None),
        bstack11111l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᳟"): driver.capabilities.get(bstack11111l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭᳠"), None),
        bstack11111l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫ᳡"):driver.capabilities.get(bstack11111l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱ᳢ࠫ"), None),
    }
    if bstack111lll11l1l_opy_() == bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬᳣ࠩ"):
        if bstack11lllll1l_opy_():
            info[bstack11111l_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸ᳤ࠬ")] = bstack11111l_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨ᳥ࠫ")
        elif driver.capabilities.get(bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹ᳦ࠧ"), {}).get(bstack11111l_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨ᳧ࠫ"), False):
            info[bstack11111l_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵ᳨ࠩ")] = bstack11111l_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭ᳩ")
        else:
            info[bstack11111l_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫᳪ")] = bstack11111l_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᳫ")
    return info
def bstack11lllll1l_opy_():
    if bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠬࡧࡰࡱࡡࡤࡹࡹࡵ࡭ࡢࡶࡨࠫᳬ")):
        return True
    if bstack1lll11ll11_opy_(os.environ.get(bstack11111l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋ᳭ࠧ"), None)):
        return True
    return False
def bstack111ll1lll_opy_(bstack111ll1lll1l_opy_, url, data, config):
    headers = config.get(bstack11111l_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨᳮ"), None)
    proxies = bstack1llllll1ll_opy_(config, url)
    auth = config.get(bstack11111l_opy_ (u"ࠨࡣࡸࡸ࡭࠭ᳯ"), None)
    response = requests.request(
            bstack111ll1lll1l_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1lll111lll_opy_(bstack1ll11lll1l_opy_, size):
    bstack1l111111ll_opy_ = []
    while len(bstack1ll11lll1l_opy_) > size:
        bstack111l1l1l_opy_ = bstack1ll11lll1l_opy_[:size]
        bstack1l111111ll_opy_.append(bstack111l1l1l_opy_)
        bstack1ll11lll1l_opy_ = bstack1ll11lll1l_opy_[size:]
    bstack1l111111ll_opy_.append(bstack1ll11lll1l_opy_)
    return bstack1l111111ll_opy_
def bstack111l1ll1111_opy_(message, bstack111ll1l1ll1_opy_=False):
    os.write(1, bytes(message, bstack11111l_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᳰ")))
    os.write(1, bytes(bstack11111l_opy_ (u"ࠪࡠࡳ࠭ᳱ"), bstack11111l_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᳲ")))
    if bstack111ll1l1ll1_opy_:
        with open(bstack11111l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠲ࡵ࠱࠲ࡻ࠰ࠫᳳ") + os.environ[bstack11111l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡋࡅࡘࡎࡅࡅࡡࡌࡈࠬ᳴")] + bstack11111l_opy_ (u"ࠧ࠯࡮ࡲ࡫ࠬᳵ"), bstack11111l_opy_ (u"ࠨࡣࠪᳶ")) as f:
            f.write(message + bstack11111l_opy_ (u"ࠩ࡟ࡲࠬ᳷"))
def bstack1l1ll11lll1_opy_():
    return os.environ[bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭᳸")].lower() == bstack11111l_opy_ (u"ࠫࡹࡸࡵࡦࠩ᳹")
def bstack111l1l11_opy_():
    return bstack1111ll1ll1_opy_().replace(tzinfo=None).isoformat() + bstack11111l_opy_ (u"ࠬࡠࠧᳺ")
def bstack111llll1ll1_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack11111l_opy_ (u"࡚࠭ࠨ᳻"))) - datetime.datetime.fromisoformat(start.rstrip(bstack11111l_opy_ (u"࡛ࠧࠩ᳼")))).total_seconds() * 1000
def bstack111l1lllll1_opy_(timestamp):
    return bstack111lll11ll1_opy_(timestamp).isoformat() + bstack11111l_opy_ (u"ࠨ࡜ࠪ᳽")
def bstack111lll1111l_opy_(bstack111ll1l1lll_opy_):
    date_format = bstack11111l_opy_ (u"ࠩࠨ࡝ࠪࡳࠥࡥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࠲ࠪ࡬ࠧ᳾")
    bstack11l11l1111l_opy_ = datetime.datetime.strptime(bstack111ll1l1lll_opy_, date_format)
    return bstack11l11l1111l_opy_.isoformat() + bstack11111l_opy_ (u"ࠪ࡞ࠬ᳿")
def bstack111ll1ll11l_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack11111l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᴀ")
    else:
        return bstack11111l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᴁ")
def bstack1lll11ll11_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack11111l_opy_ (u"࠭ࡴࡳࡷࡨࠫᴂ")
def bstack11l111ll1l1_opy_(val):
    return val.__str__().lower() == bstack11111l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ᴃ")
def error_handler(bstack111lll11111_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack111lll11111_opy_ as e:
                print(bstack11111l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡾࢁࠥ࠳࠾ࠡࡽࢀ࠾ࠥࢁࡽࠣᴄ").format(func.__name__, bstack111lll11111_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack11l111l1111_opy_(bstack111llll1lll_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack111llll1lll_opy_(cls, *args, **kwargs)
            except bstack111lll11111_opy_ as e:
                print(bstack11111l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡿࢂࠦ࠭࠿ࠢࡾࢁ࠿ࠦࡻࡾࠤᴅ").format(bstack111llll1lll_opy_.__name__, bstack111lll11111_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack11l111l1111_opy_
    else:
        return decorator
def bstack1l1ll11l1l_opy_(bstack1lllllll1ll_opy_):
    if os.getenv(bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ᴆ")) is not None:
        return bstack1lll11ll11_opy_(os.getenv(bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᴇ")))
    if bstack11111l_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᴈ") in bstack1lllllll1ll_opy_ and bstack11l111ll1l1_opy_(bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᴉ")]):
        return False
    if bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᴊ") in bstack1lllllll1ll_opy_ and bstack11l111ll1l1_opy_(bstack1lllllll1ll_opy_[bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᴋ")]):
        return False
    return True
def bstack1l1ll1111l_opy_():
    try:
        from pytest_bdd import reporting
        bstack111lll1l11l_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠤᴌ"), None)
        return bstack111lll1l11l_opy_ is None or bstack111lll1l11l_opy_ == bstack11111l_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢᴍ")
    except Exception as e:
        return False
def bstack1ll1111lll_opy_(hub_url, CONFIG):
    if bstack11lll1l1ll_opy_() <= version.parse(bstack11111l_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫᴎ")):
        if hub_url:
            return bstack11111l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᴏ") + hub_url + bstack11111l_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥᴐ")
        return bstack1l1l1lll_opy_
    if hub_url:
        return bstack11111l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤᴑ") + hub_url + bstack11111l_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤᴒ")
    return bstack11ll11l1_opy_
def bstack111l1llll1l_opy_():
    return isinstance(os.getenv(bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒ࡜ࡘࡊ࡙ࡔࡠࡒࡏ࡙ࡌࡏࡎࠨᴓ")), str)
def bstack1111l1lll_opy_(url):
    return urlparse(url).hostname
def bstack1l1l1l1111_opy_(hostname):
    for bstack111l1llll_opy_ in bstack1l1ll111ll_opy_:
        regex = re.compile(bstack111l1llll_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11l111l11ll_opy_(bstack111l1lll1l1_opy_, file_name, logger):
    bstack11l1ll1l_opy_ = os.path.join(os.path.expanduser(bstack11111l_opy_ (u"ࠪࢂࠬᴔ")), bstack111l1lll1l1_opy_)
    try:
        if not os.path.exists(bstack11l1ll1l_opy_):
            os.makedirs(bstack11l1ll1l_opy_)
        file_path = os.path.join(os.path.expanduser(bstack11111l_opy_ (u"ࠫࢃ࠭ᴕ")), bstack111l1lll1l1_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack11111l_opy_ (u"ࠬࡽࠧᴖ")):
                pass
            with open(file_path, bstack11111l_opy_ (u"ࠨࡷࠬࠤᴗ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1l11ll1ll_opy_.format(str(e)))
def bstack11l1111l11l_opy_(file_name, key, value, logger):
    file_path = bstack11l111l11ll_opy_(bstack11111l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᴘ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1ll11l1ll1_opy_ = json.load(open(file_path, bstack11111l_opy_ (u"ࠨࡴࡥࠫᴙ")))
        else:
            bstack1ll11l1ll1_opy_ = {}
        bstack1ll11l1ll1_opy_[key] = value
        with open(file_path, bstack11111l_opy_ (u"ࠤࡺ࠯ࠧᴚ")) as outfile:
            json.dump(bstack1ll11l1ll1_opy_, outfile)
def bstack1l1l11l11l_opy_(file_name, logger):
    file_path = bstack11l111l11ll_opy_(bstack11111l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᴛ"), file_name, logger)
    bstack1ll11l1ll1_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack11111l_opy_ (u"ࠫࡷ࠭ᴜ")) as bstack11llll1ll_opy_:
            bstack1ll11l1ll1_opy_ = json.load(bstack11llll1ll_opy_)
    return bstack1ll11l1ll1_opy_
def bstack1lll111ll_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡩ࡭ࡱ࡫࠺ࠡࠩᴝ") + file_path + bstack11111l_opy_ (u"࠭ࠠࠨᴞ") + str(e))
def bstack11lll1l1ll_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack11111l_opy_ (u"ࠢ࠽ࡐࡒࡘࡘࡋࡔ࠿ࠤᴟ")
def bstack11111ll1_opy_(config):
    if bstack11111l_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᴠ") in config:
        del (config[bstack11111l_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᴡ")])
        return False
    if bstack11lll1l1ll_opy_() < version.parse(bstack11111l_opy_ (u"ࠪ࠷࠳࠺࠮࠱ࠩᴢ")):
        return False
    if bstack11lll1l1ll_opy_() >= version.parse(bstack11111l_opy_ (u"ࠫ࠹࠴࠱࠯࠷ࠪᴣ")):
        return True
    if bstack11111l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬᴤ") in config and config[bstack11111l_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ᴥ")] is False:
        return False
    else:
        return True
def bstack11llll1l1_opy_(args_list, bstack11l1111l111_opy_):
    index = -1
    for value in bstack11l1111l111_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1l11l11_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1l11l11_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111ll1l1l1_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111ll1l1l1_opy_ = bstack111ll1l1l1_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack11111l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧᴦ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack11111l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᴧ"), exception=exception)
    def bstack1llllll1111_opy_(self):
        if self.result != bstack11111l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᴨ"):
            return None
        if isinstance(self.exception_type, str) and bstack11111l_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨᴩ") in self.exception_type:
            return bstack11111l_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᴪ")
        return bstack11111l_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᴫ")
    def bstack11l111l11l1_opy_(self):
        if self.result != bstack11111l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᴬ"):
            return None
        if self.bstack111ll1l1l1_opy_:
            return self.bstack111ll1l1l1_opy_
        return bstack11l111111ll_opy_(self.exception)
def bstack11l111111ll_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack111lll1lll1_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack11l1l111l_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1lllllll1l_opy_(config, logger):
    try:
        import playwright
        bstack11l111l1l11_opy_ = playwright.__file__
        bstack11l1111ll11_opy_ = os.path.split(bstack11l111l1l11_opy_)
        bstack11l111l1lll_opy_ = bstack11l1111ll11_opy_[0] + bstack11111l_opy_ (u"ࠧ࠰ࡦࡵ࡭ࡻ࡫ࡲ࠰ࡲࡤࡧࡰࡧࡧࡦ࠱࡯࡭ࡧ࠵ࡣ࡭࡫࠲ࡧࡱ࡯࠮࡫ࡵࠪᴭ")
        os.environ[bstack11111l_opy_ (u"ࠨࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜ࠫᴮ")] = bstack1l111l1l_opy_(config)
        with open(bstack11l111l1lll_opy_, bstack11111l_opy_ (u"ࠩࡵࠫᴯ")) as f:
            bstack1ll1111l_opy_ = f.read()
            bstack11l11111111_opy_ = bstack11111l_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠩᴰ")
            bstack111ll1lll11_opy_ = bstack1ll1111l_opy_.find(bstack11l11111111_opy_)
            if bstack111ll1lll11_opy_ == -1:
              process = subprocess.Popen(bstack11111l_opy_ (u"ࠦࡳࡶ࡭ࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡪࡰࡴࡨࡡ࡭࠯ࡤ࡫ࡪࡴࡴࠣᴱ"), shell=True, cwd=bstack11l1111ll11_opy_[0])
              process.wait()
              bstack11l1111ll1l_opy_ = bstack11111l_opy_ (u"ࠬࠨࡵࡴࡧࠣࡷࡹࡸࡩࡤࡶࠥ࠿ࠬᴲ")
              bstack111ll11lll1_opy_ = bstack11111l_opy_ (u"ࠨࠢࠣࠢ࡟ࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴ࡝ࠤ࠾ࠤࡨࡵ࡮ࡴࡶࠣࡿࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠡࡿࠣࡁࠥࡸࡥࡲࡷ࡬ࡶࡪ࠮ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭ࠩ࠼ࠢ࡬ࡪࠥ࠮ࡰࡳࡱࡦࡩࡸࡹ࠮ࡦࡰࡹ࠲ࡌࡒࡏࡃࡃࡏࡣࡆࡍࡅࡏࡖࡢࡌ࡙࡚ࡐࡠࡒࡕࡓ࡝࡟ࠩࠡࡤࡲࡳࡹࡹࡴࡳࡣࡳࠬ࠮ࡁࠠࠣࠤࠥᴳ")
              bstack111ll1l111l_opy_ = bstack1ll1111l_opy_.replace(bstack11l1111ll1l_opy_, bstack111ll11lll1_opy_)
              with open(bstack11l111l1lll_opy_, bstack11111l_opy_ (u"ࠧࡸࠩᴴ")) as f:
                f.write(bstack111ll1l111l_opy_)
    except Exception as e:
        logger.error(bstack1ll11ll111_opy_.format(str(e)))
def bstack1ll1lll11l_opy_():
  try:
    bstack111ll111111_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠨࡱࡳࡸ࡮ࡳࡡ࡭ࡡ࡫ࡹࡧࡥࡵࡳ࡮࠱࡮ࡸࡵ࡮ࠨᴵ"))
    bstack111l1ll11l1_opy_ = []
    if os.path.exists(bstack111ll111111_opy_):
      with open(bstack111ll111111_opy_) as f:
        bstack111l1ll11l1_opy_ = json.load(f)
      os.remove(bstack111ll111111_opy_)
    return bstack111l1ll11l1_opy_
  except:
    pass
  return []
def bstack1lll1l11l1_opy_(bstack1l1l1l111_opy_):
  try:
    bstack111l1ll11l1_opy_ = []
    bstack111ll111111_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠩࡲࡴࡹ࡯࡭ࡢ࡮ࡢ࡬ࡺࡨ࡟ࡶࡴ࡯࠲࡯ࡹ࡯࡯ࠩᴶ"))
    if os.path.exists(bstack111ll111111_opy_):
      with open(bstack111ll111111_opy_) as f:
        bstack111l1ll11l1_opy_ = json.load(f)
    bstack111l1ll11l1_opy_.append(bstack1l1l1l111_opy_)
    with open(bstack111ll111111_opy_, bstack11111l_opy_ (u"ࠪࡻࠬᴷ")) as f:
        json.dump(bstack111l1ll11l1_opy_, f)
  except:
    pass
def bstack1ll111l1_opy_(logger, bstack111ll1lllll_opy_ = False):
  try:
    test_name = os.environ.get(bstack11111l_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧᴸ"), bstack11111l_opy_ (u"ࠬ࠭ᴹ"))
    if test_name == bstack11111l_opy_ (u"࠭ࠧᴺ"):
        test_name = threading.current_thread().__dict__.get(bstack11111l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࡂࡥࡦࡢࡸࡪࡹࡴࡠࡰࡤࡱࡪ࠭ᴻ"), bstack11111l_opy_ (u"ࠨࠩᴼ"))
    bstack11l1111111l_opy_ = bstack11111l_opy_ (u"ࠩ࠯ࠤࠬᴽ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111ll1lllll_opy_:
        bstack1l11l111ll_opy_ = os.environ.get(bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᴾ"), bstack11111l_opy_ (u"ࠫ࠵࠭ᴿ"))
        bstack1l11ll111_opy_ = {bstack11111l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᵀ"): test_name, bstack11111l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᵁ"): bstack11l1111111l_opy_, bstack11111l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᵂ"): bstack1l11l111ll_opy_}
        bstack111lllll1ll_opy_ = []
        bstack11l111ll1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡲࡳࡴࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧᵃ"))
        if os.path.exists(bstack11l111ll1ll_opy_):
            with open(bstack11l111ll1ll_opy_) as f:
                bstack111lllll1ll_opy_ = json.load(f)
        bstack111lllll1ll_opy_.append(bstack1l11ll111_opy_)
        with open(bstack11l111ll1ll_opy_, bstack11111l_opy_ (u"ࠩࡺࠫᵄ")) as f:
            json.dump(bstack111lllll1ll_opy_, f)
    else:
        bstack1l11ll111_opy_ = {bstack11111l_opy_ (u"ࠪࡲࡦࡳࡥࠨᵅ"): test_name, bstack11111l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᵆ"): bstack11l1111111l_opy_, bstack11111l_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᵇ"): str(multiprocessing.current_process().name)}
        if bstack11111l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪᵈ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l11ll111_opy_)
  except Exception as e:
      logger.warn(bstack11111l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡳࡽࡹ࡫ࡳࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧ࠺ࠡࡽࢀࠦᵉ").format(e))
def bstack11l111ll11_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11111l_opy_ (u"ࠨࡨ࡬ࡰࡪࡲ࡯ࡤ࡭ࠣࡲࡴࡺࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧ࠯ࠤࡺࡹࡩ࡯ࡩࠣࡦࡦࡹࡩࡤࠢࡩ࡭ࡱ࡫ࠠࡰࡲࡨࡶࡦࡺࡩࡰࡰࡶࠫᵊ"))
    try:
      bstack111llll11ll_opy_ = []
      bstack1l11ll111_opy_ = {bstack11111l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᵋ"): test_name, bstack11111l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᵌ"): error_message, bstack11111l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᵍ"): index}
      bstack111llll1l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ᵎ"))
      if os.path.exists(bstack111llll1l1l_opy_):
          with open(bstack111llll1l1l_opy_) as f:
              bstack111llll11ll_opy_ = json.load(f)
      bstack111llll11ll_opy_.append(bstack1l11ll111_opy_)
      with open(bstack111llll1l1l_opy_, bstack11111l_opy_ (u"࠭ࡷࠨᵏ")) as f:
          json.dump(bstack111llll11ll_opy_, f)
    except Exception as e:
      logger.warn(bstack11111l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡵࡳࡧࡵࡴࠡࡨࡸࡲࡳ࡫࡬ࠡࡦࡤࡸࡦࡀࠠࡼࡿࠥᵐ").format(e))
    return
  bstack111llll11ll_opy_ = []
  bstack1l11ll111_opy_ = {bstack11111l_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᵑ"): test_name, bstack11111l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᵒ"): error_message, bstack11111l_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᵓ"): index}
  bstack111llll1l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack11111l_opy_ (u"ࠫࡷࡵࡢࡰࡶࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᵔ"))
  lock_file = bstack111llll1l1l_opy_ + bstack11111l_opy_ (u"ࠬ࠴࡬ࡰࡥ࡮ࠫᵕ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111llll1l1l_opy_):
          with open(bstack111llll1l1l_opy_, bstack11111l_opy_ (u"࠭ࡲࠨᵖ")) as f:
              content = f.read().strip()
              if content:
                  bstack111llll11ll_opy_ = json.load(open(bstack111llll1l1l_opy_))
      bstack111llll11ll_opy_.append(bstack1l11ll111_opy_)
      with open(bstack111llll1l1l_opy_, bstack11111l_opy_ (u"ࠧࡸࠩᵗ")) as f:
          json.dump(bstack111llll11ll_opy_, f)
  except Exception as e:
    logger.warn(bstack11111l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡶࡴࡨ࡯ࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧࠠࡸ࡫ࡷ࡬ࠥ࡬ࡩ࡭ࡧࠣࡰࡴࡩ࡫ࡪࡰࡪ࠾ࠥࢁࡽࠣᵘ").format(e))
def bstack1ll111llll_opy_(bstack1llll111_opy_, name, logger):
  try:
    bstack1l11ll111_opy_ = {bstack11111l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᵙ"): name, bstack11111l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᵚ"): bstack1llll111_opy_, bstack11111l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᵛ"): str(threading.current_thread()._name)}
    return bstack1l11ll111_opy_
  except Exception as e:
    logger.warn(bstack11111l_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡣࡧ࡫ࡥࡻ࡫ࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᵜ").format(e))
  return
def bstack111ll1ll1l1_opy_():
    return platform.system() == bstack11111l_opy_ (u"࠭ࡗࡪࡰࡧࡳࡼࡹࠧᵝ")
def bstack1l1l1ll1ll_opy_(bstack111llllll11_opy_, config, logger):
    bstack111llllll1l_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack111llllll11_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪ࡮ࡲࡴࡦࡴࠣࡧࡴࡴࡦࡪࡩࠣ࡯ࡪࡿࡳࠡࡤࡼࠤࡷ࡫ࡧࡦࡺࠣࡱࡦࡺࡣࡩ࠼ࠣࡿࢂࠨᵞ").format(e))
    return bstack111llllll1l_opy_
def bstack111ll111l1l_opy_(bstack11l111lllll_opy_, bstack111lll1llll_opy_):
    bstack111lll1l1l1_opy_ = version.parse(bstack11l111lllll_opy_)
    bstack111lll111l1_opy_ = version.parse(bstack111lll1llll_opy_)
    if bstack111lll1l1l1_opy_ > bstack111lll111l1_opy_:
        return 1
    elif bstack111lll1l1l1_opy_ < bstack111lll111l1_opy_:
        return -1
    else:
        return 0
def bstack1111ll1ll1_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack111lll11ll1_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll11l11l_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack11lllll11_opy_(options, framework, config, bstack1ll11ll11l_opy_={}):
    if options is None:
        return
    if getattr(options, bstack11111l_opy_ (u"ࠨࡩࡨࡸࠬᵟ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1l1ll111l_opy_ = caps.get(bstack11111l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᵠ"))
    bstack111ll1ll1ll_opy_ = True
    bstack1111l11ll_opy_ = os.environ[bstack11111l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᵡ")]
    bstack1ll111l111l_opy_ = config.get(bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᵢ"), False)
    if bstack1ll111l111l_opy_:
        bstack1ll1l111l1l_opy_ = config.get(bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᵣ"), {})
        bstack1ll1l111l1l_opy_[bstack11111l_opy_ (u"࠭ࡡࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠩᵤ")] = os.getenv(bstack11111l_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᵥ"))
        bstack11ll11111ll_opy_ = json.loads(os.getenv(bstack11111l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᵦ"), bstack11111l_opy_ (u"ࠩࡾࢁࠬᵧ"))).get(bstack11111l_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᵨ"))
    if bstack11l111ll1l1_opy_(caps.get(bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡗ࠴ࡅࠪᵩ"))) or bstack11l111ll1l1_opy_(caps.get(bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡠࡹ࠶ࡧࠬᵪ"))):
        bstack111ll1ll1ll_opy_ = False
    if bstack11111ll1_opy_({bstack11111l_opy_ (u"ࠨࡵࡴࡧ࡚࠷ࡈࠨᵫ"): bstack111ll1ll1ll_opy_}):
        bstack1l1ll111l_opy_ = bstack1l1ll111l_opy_ or {}
        bstack1l1ll111l_opy_[bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᵬ")] = bstack111ll11l11l_opy_(framework)
        bstack1l1ll111l_opy_[bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵭ")] = bstack1l1ll11lll1_opy_()
        bstack1l1ll111l_opy_[bstack11111l_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᵮ")] = bstack1111l11ll_opy_
        bstack1l1ll111l_opy_[bstack11111l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᵯ")] = bstack1ll11ll11l_opy_
        if bstack1ll111l111l_opy_:
            bstack1l1ll111l_opy_[bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᵰ")] = bstack1ll111l111l_opy_
            bstack1l1ll111l_opy_[bstack11111l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᵱ")] = bstack1ll1l111l1l_opy_
            bstack1l1ll111l_opy_[bstack11111l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᵲ")][bstack11111l_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᵳ")] = bstack11ll11111ll_opy_
        if getattr(options, bstack11111l_opy_ (u"ࠨࡵࡨࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡺࠩᵴ"), None):
            options.set_capability(bstack11111l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᵵ"), bstack1l1ll111l_opy_)
        else:
            options[bstack11111l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᵶ")] = bstack1l1ll111l_opy_
    else:
        if getattr(options, bstack11111l_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬᵷ"), None):
            options.set_capability(bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᵸ"), bstack111ll11l11l_opy_(framework))
            options.set_capability(bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᵹ"), bstack1l1ll11lll1_opy_())
            options.set_capability(bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᵺ"), bstack1111l11ll_opy_)
            options.set_capability(bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᵻ"), bstack1ll11ll11l_opy_)
            if bstack1ll111l111l_opy_:
                options.set_capability(bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᵼ"), bstack1ll111l111l_opy_)
                options.set_capability(bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᵽ"), bstack1ll1l111l1l_opy_)
                options.set_capability(bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵ࠱ࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᵾ"), bstack11ll11111ll_opy_)
        else:
            options[bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᵿ")] = bstack111ll11l11l_opy_(framework)
            options[bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᶀ")] = bstack1l1ll11lll1_opy_()
            options[bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᶁ")] = bstack1111l11ll_opy_
            options[bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᶂ")] = bstack1ll11ll11l_opy_
            if bstack1ll111l111l_opy_:
                options[bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᶃ")] = bstack1ll111l111l_opy_
                options[bstack11111l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᶄ")] = bstack1ll1l111l1l_opy_
                options[bstack11111l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᶅ")][bstack11111l_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᶆ")] = bstack11ll11111ll_opy_
    return options
def bstack111lll1ll11_opy_(bstack111lllll111_opy_, framework):
    bstack1ll11ll11l_opy_ = bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠨࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡔࡗࡕࡄࡖࡅࡗࡣࡒࡇࡐࠣᶇ"))
    if bstack111lllll111_opy_ and len(bstack111lllll111_opy_.split(bstack11111l_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᶈ"))) > 1:
        ws_url = bstack111lllll111_opy_.split(bstack11111l_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᶉ"))[0]
        if bstack11111l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬᶊ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111l1ll111l_opy_ = json.loads(urllib.parse.unquote(bstack111lllll111_opy_.split(bstack11111l_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᶋ"))[1]))
            bstack111l1ll111l_opy_ = bstack111l1ll111l_opy_ or {}
            bstack1111l11ll_opy_ = os.environ[bstack11111l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᶌ")]
            bstack111l1ll111l_opy_[bstack11111l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᶍ")] = str(framework) + str(__version__)
            bstack111l1ll111l_opy_[bstack11111l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᶎ")] = bstack1l1ll11lll1_opy_()
            bstack111l1ll111l_opy_[bstack11111l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᶏ")] = bstack1111l11ll_opy_
            bstack111l1ll111l_opy_[bstack11111l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᶐ")] = bstack1ll11ll11l_opy_
            bstack111lllll111_opy_ = bstack111lllll111_opy_.split(bstack11111l_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᶑ"))[0] + bstack11111l_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᶒ") + urllib.parse.quote(json.dumps(bstack111l1ll111l_opy_))
    return bstack111lllll111_opy_
def bstack1lll11ll_opy_():
    global bstack11111l11_opy_
    from playwright._impl._browser_type import BrowserType
    bstack11111l11_opy_ = BrowserType.connect
    return bstack11111l11_opy_
def bstack1l1lll1l11_opy_(framework_name):
    global bstack1llll11l1l_opy_
    bstack1llll11l1l_opy_ = framework_name
    return framework_name
def bstack111llll1l1_opy_(self, *args, **kwargs):
    global bstack11111l11_opy_
    try:
        global bstack1llll11l1l_opy_
        if bstack11111l_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᶓ") in kwargs:
            kwargs[bstack11111l_opy_ (u"ࠬࡽࡳࡆࡰࡧࡴࡴ࡯࡮ࡵࠩᶔ")] = bstack111lll1ll11_opy_(
                kwargs.get(bstack11111l_opy_ (u"࠭ࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶࠪᶕ"), None),
                bstack1llll11l1l_opy_
            )
    except Exception as e:
        logger.error(bstack11111l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡕࡇࡏࠥࡩࡡࡱࡵ࠽ࠤࢀࢃࠢᶖ").format(str(e)))
    return bstack11111l11_opy_(self, *args, **kwargs)
def bstack111lll1l111_opy_(bstack111ll1ll111_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1llllll1ll_opy_(bstack111ll1ll111_opy_, bstack11111l_opy_ (u"ࠣࠤᶗ"))
        if proxies and proxies.get(bstack11111l_opy_ (u"ࠤ࡫ࡸࡹࡶࡳࠣᶘ")):
            parsed_url = urlparse(proxies.get(bstack11111l_opy_ (u"ࠥ࡬ࡹࡺࡰࡴࠤᶙ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack11111l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡋࡳࡸࡺࠧᶚ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack11111l_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨᶛ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack11111l_opy_ (u"࠭ࡰࡳࡱࡻࡽ࡚ࡹࡥࡳࠩᶜ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack11111l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖࡡࡴࡵࠪᶝ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack1ll1l11l_opy_(bstack111ll1ll111_opy_):
    bstack111llll1111_opy_ = {
        bstack11l1l11l111_opy_[bstack11l1111l1ll_opy_]: bstack111ll1ll111_opy_[bstack11l1111l1ll_opy_]
        for bstack11l1111l1ll_opy_ in bstack111ll1ll111_opy_
        if bstack11l1111l1ll_opy_ in bstack11l1l11l111_opy_
    }
    bstack111llll1111_opy_[bstack11111l_opy_ (u"ࠣࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠣᶞ")] = bstack111lll1l111_opy_(bstack111ll1ll111_opy_, bstack11l11l1lll_opy_.get_property(bstack11111l_opy_ (u"ࠤࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠤᶟ")))
    bstack111ll11l111_opy_ = [element.lower() for element in bstack11l1l1l111l_opy_]
    bstack111ll111l11_opy_(bstack111llll1111_opy_, bstack111ll11l111_opy_)
    return bstack111llll1111_opy_
def bstack111ll111l11_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack11111l_opy_ (u"ࠥ࠮࠯࠰ࠪࠣᶠ")
    for value in d.values():
        if isinstance(value, dict):
            bstack111ll111l11_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack111ll111l11_opy_(item, keys)
def bstack1l1l1ll1lll_opy_():
    bstack111l1lll111_opy_ = [os.environ.get(bstack11111l_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡎࡒࡅࡔࡡࡇࡍࡗࠨᶡ")), os.path.join(os.path.expanduser(bstack11111l_opy_ (u"ࠧࢄࠢᶢ")), bstack11111l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᶣ")), os.path.join(bstack11111l_opy_ (u"ࠧ࠰ࡶࡰࡴࠬᶤ"), bstack11111l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᶥ"))]
    for path in bstack111l1lll111_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack11111l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࠨࠤᶦ") + str(path) + bstack11111l_opy_ (u"ࠥࠫࠥ࡫ࡸࡪࡵࡷࡷ࠳ࠨᶧ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack11111l_opy_ (u"ࠦࡌ࡯ࡶࡪࡰࡪࠤࡵ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮ࡴࠢࡩࡳࡷࠦࠧࠣᶨ") + str(path) + bstack11111l_opy_ (u"ࠧ࠭ࠢᶩ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack11111l_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࠬࠨᶪ") + str(path) + bstack11111l_opy_ (u"ࠢࠨࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡬ࡦࡹࠠࡵࡪࡨࠤࡷ࡫ࡱࡶ࡫ࡵࡩࡩࠦࡰࡦࡴࡰ࡭ࡸࡹࡩࡰࡰࡶ࠲ࠧᶫ"))
            else:
                logger.debug(bstack11111l_opy_ (u"ࠣࡅࡵࡩࡦࡺࡩ࡯ࡩࠣࡪ࡮ࡲࡥࠡࠩࠥᶬ") + str(path) + bstack11111l_opy_ (u"ࠤࠪࠤࡼ࡯ࡴࡩࠢࡺࡶ࡮ࡺࡥࠡࡲࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲ࠳ࠨᶭ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack11111l_opy_ (u"ࠥࡓࡵ࡫ࡲࡢࡶ࡬ࡳࡳࠦࡳࡶࡥࡦࡩࡪࡪࡥࡥࠢࡩࡳࡷࠦࠧࠣᶮ") + str(path) + bstack11111l_opy_ (u"ࠦࠬ࠴ࠢᶯ"))
            return path
        except Exception as e:
            logger.debug(bstack11111l_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡻࡰࠡࡨ࡬ࡰࡪࠦࠧࡼࡲࡤࡸ࡭ࢃࠧ࠻ࠢࠥᶰ") + str(e) + bstack11111l_opy_ (u"ࠨࠢᶱ"))
    logger.debug(bstack11111l_opy_ (u"ࠢࡂ࡮࡯ࠤࡵࡧࡴࡩࡵࠣࡪࡦ࡯࡬ࡦࡦ࠱ࠦᶲ"))
    return None
@measure(event_name=EVENTS.bstack11l1l1l11l1_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
def bstack1lll11l1lll_opy_(binary_path, bstack1ll1lll1lll_opy_, bs_config):
    logger.debug(bstack11111l_opy_ (u"ࠣࡅࡸࡶࡷ࡫࡮ࡵࠢࡆࡐࡎࠦࡐࡢࡶ࡫ࠤ࡫ࡵࡵ࡯ࡦ࠽ࠤࢀࢃࠢᶳ").format(binary_path))
    bstack111ll11llll_opy_ = bstack11111l_opy_ (u"ࠩࠪᶴ")
    bstack111lll11l11_opy_ = {
        bstack11111l_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᶵ"): __version__,
        bstack11111l_opy_ (u"ࠦࡴࡹࠢᶶ"): platform.system(),
        bstack11111l_opy_ (u"ࠧࡵࡳࡠࡣࡵࡧ࡭ࠨᶷ"): platform.machine(),
        bstack11111l_opy_ (u"ࠨࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠦᶸ"): bstack11111l_opy_ (u"ࠧ࠱ࠩᶹ"),
        bstack11111l_opy_ (u"ࠣࡵࡧ࡯ࡤࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠢᶺ"): bstack11111l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩᶻ")
    }
    bstack11l1111l1l1_opy_(bstack111lll11l11_opy_)
    try:
        if binary_path:
            if bstack111ll1ll1l1_opy_():
                bstack111lll11l11_opy_[bstack11111l_opy_ (u"ࠪࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᶼ")] = subprocess.check_output([binary_path, bstack11111l_opy_ (u"ࠦࡻ࡫ࡲࡴ࡫ࡲࡲࠧᶽ")]).strip().decode(bstack11111l_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᶾ"))
            else:
                bstack111lll11l11_opy_[bstack11111l_opy_ (u"࠭ࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠫᶿ")] = subprocess.check_output([binary_path, bstack11111l_opy_ (u"ࠢࡷࡧࡵࡷ࡮ࡵ࡮ࠣ᷀")], stderr=subprocess.DEVNULL).strip().decode(bstack11111l_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧ᷁"))
        response = requests.request(
            bstack11111l_opy_ (u"ࠩࡊࡉ࡙᷂࠭"),
            url=bstack11l111l11_opy_(bstack11l1l1llll1_opy_),
            headers=None,
            auth=(bs_config[bstack11111l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ᷃")], bs_config[bstack11111l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ᷄")]),
            json=None,
            params=bstack111lll11l11_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack11111l_opy_ (u"ࠬࡻࡲ࡭ࠩ᷅") in data.keys() and bstack11111l_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡪ࡟ࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ᷆") in data.keys():
            logger.debug(bstack11111l_opy_ (u"ࠢࡏࡧࡨࡨࠥࡺ࡯ࠡࡷࡳࡨࡦࡺࡥࠡࡤ࡬ࡲࡦࡸࡹ࠭ࠢࡦࡹࡷࡸࡥ࡯ࡶࠣࡦ࡮ࡴࡡࡳࡻࠣࡺࡪࡸࡳࡪࡱࡱ࠾ࠥࢁࡽࠣ᷇").format(bstack111lll11l11_opy_[bstack11111l_opy_ (u"ࠨࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭᷈")]))
            if bstack11111l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡗࡕࡐࠬ᷉") in os.environ:
                logger.debug(bstack11111l_opy_ (u"ࠥࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡨࡩ࡯ࡣࡵࡽࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡢࡵࠣࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡘࡖࡑࠦࡩࡴࠢࡶࡩࡹࠨ᷊"))
                data[bstack11111l_opy_ (u"ࠫࡺࡸ࡬ࠨ᷋")] = os.environ[bstack11111l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇࡏࡎࡂࡔ࡜ࡣ࡚ࡘࡌࠨ᷌")]
            bstack111l1llllll_opy_ = bstack111ll1111ll_opy_(data[bstack11111l_opy_ (u"࠭ࡵࡳ࡮ࠪ᷍")], bstack1ll1lll1lll_opy_)
            bstack111ll11llll_opy_ = os.path.join(bstack1ll1lll1lll_opy_, bstack111l1llllll_opy_)
            os.chmod(bstack111ll11llll_opy_, 0o777) # bstack111l1llll11_opy_ permission
            return bstack111ll11llll_opy_
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡲࡪࡽࠠࡔࡆࡎࠤࢀࢃ᷎ࠢ").format(e))
    return binary_path
def bstack11l1111l1l1_opy_(bstack111lll11l11_opy_):
    try:
        if bstack11111l_opy_ (u"ࠨ࡮࡬ࡲࡺࡾ᷏ࠧ") not in bstack111lll11l11_opy_[bstack11111l_opy_ (u"ࠩࡲࡷ᷐ࠬ")].lower():
            return
        if os.path.exists(bstack11111l_opy_ (u"ࠥ࠳ࡪࡺࡣ࠰ࡱࡶ࠱ࡷ࡫࡬ࡦࡣࡶࡩࠧ᷑")):
            with open(bstack11111l_opy_ (u"ࠦ࠴࡫ࡴࡤ࠱ࡲࡷ࠲ࡸࡥ࡭ࡧࡤࡷࡪࠨ᷒"), bstack11111l_opy_ (u"ࠧࡸࠢᷓ")) as f:
                bstack111llll111l_opy_ = {}
                for line in f:
                    if bstack11111l_opy_ (u"ࠨ࠽ࠣᷔ") in line:
                        key, value = line.rstrip().split(bstack11111l_opy_ (u"ࠢ࠾ࠤᷕ"), 1)
                        bstack111llll111l_opy_[key] = value.strip(bstack11111l_opy_ (u"ࠨࠤ࡟ࠫࠬᷖ"))
                bstack111lll11l11_opy_[bstack11111l_opy_ (u"ࠩࡧ࡭ࡸࡺࡲࡰࠩᷗ")] = bstack111llll111l_opy_.get(bstack11111l_opy_ (u"ࠥࡍࡉࠨᷘ"), bstack11111l_opy_ (u"ࠦࠧᷙ"))
        elif os.path.exists(bstack11111l_opy_ (u"ࠧ࠵ࡥࡵࡥ࠲ࡥࡱࡶࡩ࡯ࡧ࠰ࡶࡪࡲࡥࡢࡵࡨࠦᷚ")):
            bstack111lll11l11_opy_[bstack11111l_opy_ (u"࠭ࡤࡪࡵࡷࡶࡴ࠭ᷛ")] = bstack11111l_opy_ (u"ࠧࡢ࡮ࡳ࡭ࡳ࡫ࠧᷜ")
    except Exception as e:
        logger.debug(bstack11111l_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡬࡫ࡴࠡࡦ࡬ࡷࡹࡸ࡯ࠡࡱࡩࠤࡱ࡯࡮ࡶࡺࠥᷝ") + e)
@measure(event_name=EVENTS.bstack11l1l1ll111_opy_, stage=STAGE.bstack1ll1l1ll1_opy_)
def bstack111ll1111ll_opy_(bstack111l1lll11l_opy_, bstack111ll11ll1l_opy_):
    logger.debug(bstack11111l_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡸ࡯࡮࠼ࠣࠦᷞ") + str(bstack111l1lll11l_opy_) + bstack11111l_opy_ (u"ࠥࠦᷟ"))
    zip_path = os.path.join(bstack111ll11ll1l_opy_, bstack11111l_opy_ (u"ࠦࡩࡵࡷ࡯࡮ࡲࡥࡩ࡫ࡤࡠࡨ࡬ࡰࡪ࠴ࡺࡪࡲࠥᷠ"))
    bstack111l1llllll_opy_ = bstack11111l_opy_ (u"ࠬ࠭ᷡ")
    with requests.get(bstack111l1lll11l_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack11111l_opy_ (u"ࠨࡷࡣࠤᷢ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack11111l_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹ࠯ࠤᷣ"))
    with zipfile.ZipFile(zip_path, bstack11111l_opy_ (u"ࠨࡴࠪᷤ")) as zip_ref:
        bstack111ll1l1111_opy_ = zip_ref.namelist()
        if len(bstack111ll1l1111_opy_) > 0:
            bstack111l1llllll_opy_ = bstack111ll1l1111_opy_[0] # bstack11l111ll111_opy_ bstack11l1l1l1l1l_opy_ will be bstack111ll11ll11_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack111ll11ll1l_opy_)
        logger.debug(bstack11111l_opy_ (u"ࠤࡉ࡭ࡱ࡫ࡳࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡦࡺࡷࡶࡦࡩࡴࡦࡦࠣࡸࡴࠦࠧࠣᷥ") + str(bstack111ll11ll1l_opy_) + bstack11111l_opy_ (u"ࠥࠫࠧᷦ"))
    os.remove(zip_path)
    return bstack111l1llllll_opy_
def get_cli_dir():
    bstack11l111lll11_opy_ = bstack1l1l1ll1lll_opy_()
    if bstack11l111lll11_opy_:
        bstack1ll1lll1lll_opy_ = os.path.join(bstack11l111lll11_opy_, bstack11111l_opy_ (u"ࠦࡨࡲࡩࠣᷧ"))
        if not os.path.exists(bstack1ll1lll1lll_opy_):
            os.makedirs(bstack1ll1lll1lll_opy_, mode=0o777, exist_ok=True)
        return bstack1ll1lll1lll_opy_
    else:
        raise FileNotFoundError(bstack11111l_opy_ (u"ࠧࡔ࡯ࠡࡹࡵ࡭ࡹࡧࡢ࡭ࡧࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡩࡳࡷࠦࡴࡩࡧࠣࡗࡉࡑࠠࡣ࡫ࡱࡥࡷࡿ࠮ࠣᷨ"))
def bstack1lll1l1l11l_opy_(bstack1ll1lll1lll_opy_):
    bstack11111l_opy_ (u"ࠨࠢࠣࡉࡨࡸࠥࡺࡨࡦࠢࡳࡥࡹ࡮ࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼࠤ࡮ࡴࠠࡢࠢࡺࡶ࡮ࡺࡡࡣ࡮ࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠮ࠣࠤࠥᷩ")
    bstack111l1ll11ll_opy_ = [
        os.path.join(bstack1ll1lll1lll_opy_, f)
        for f in os.listdir(bstack1ll1lll1lll_opy_)
        if os.path.isfile(os.path.join(bstack1ll1lll1lll_opy_, f)) and f.startswith(bstack11111l_opy_ (u"ࠢࡣ࡫ࡱࡥࡷࡿ࠭ࠣᷪ"))
    ]
    if len(bstack111l1ll11ll_opy_) > 0:
        return max(bstack111l1ll11ll_opy_, key=os.path.getmtime) # get bstack111l1ll1l1l_opy_ binary
    return bstack11111l_opy_ (u"ࠣࠤᷫ")
def bstack11ll1111l11_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll111l11l1_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1ll111l11l1_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1111l1ll_opy_(data, keys, default=None):
    bstack11111l_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡖࡥ࡫࡫࡬ࡺࠢࡪࡩࡹࠦࡡࠡࡰࡨࡷࡹ࡫ࡤࠡࡸࡤࡰࡺ࡫ࠠࡧࡴࡲࡱࠥࡧࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡴࡸࠠ࡭࡫ࡶࡸ࠳ࠐࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡨࡦࡺࡡ࠻ࠢࡗ࡬ࡪࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳࡻࠣࡳࡷࠦ࡬ࡪࡵࡷࠤࡹࡵࠠࡵࡴࡤࡺࡪࡸࡳࡦ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠ࡬ࡧࡼࡷ࠿ࠦࡁࠡ࡮࡬ࡷࡹࠦ࡯ࡧࠢ࡮ࡩࡾࡹ࠯ࡪࡰࡧ࡭ࡨ࡫ࡳࠡࡴࡨࡴࡷ࡫ࡳࡦࡰࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡵࡧࡴࡩ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠࡥࡧࡩࡥࡺࡲࡴ࠻࡙ࠢࡥࡱࡻࡥࠡࡶࡲࠤࡷ࡫ࡴࡶࡴࡱࠤ࡮࡬ࠠࡵࡪࡨࠤࡵࡧࡴࡩࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠱ࠎࠥࠦࠠࠡ࠼ࡵࡩࡹࡻࡲ࡯࠼ࠣࡘ࡭࡫ࠠࡷࡣ࡯ࡹࡪࠦࡡࡵࠢࡷ࡬ࡪࠦ࡮ࡦࡵࡷࡩࡩࠦࡰࡢࡶ࡫࠰ࠥࡵࡲࠡࡦࡨࡪࡦࡻ࡬ࡵࠢ࡬ࡪࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᷬ")
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
def bstack1ll1llll11_opy_(bstack111lll1ll1l_opy_, key, value):
    bstack11111l_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡗࡹࡵࡲࡦࠢࡆࡐࡎࠦࡥ࡯ࡸ࡬ࡶࡴࡴ࡭ࡦࡰࡷࠤࡻࡧࡲࡪࡣࡥࡰࡪࡹࠠ࡮ࡣࡳࡴ࡮ࡴࡧࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿ࠮ࠋࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡩ࡬ࡪࡡࡨࡲࡻࡥࡶࡢࡴࡶࡣࡲࡧࡰ࠻ࠢࡇ࡭ࡨࡺࡩࡰࡰࡤࡶࡾࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࡰ࡫ࡹ࠻ࠢࡎࡩࡾࠦࡦࡳࡱࡰࠤࡈࡒࡉࡠࡅࡄࡔࡘࡥࡔࡐࡡࡆࡓࡓࡌࡉࡈࠌࠣࠤࠥࠦࠠࠡࠢࠣࡺࡦࡲࡵࡦ࠼࡚ࠣࡦࡲࡵࡦࠢࡩࡶࡴࡳࠠࡤࡱࡰࡱࡦࡴࡤࠡ࡮࡬ࡲࡪࠦࡡࡳࡩࡸࡱࡪࡴࡴࡴࠌࠣࠤࠥࠦࠢࠣࠤᷭ")
    if key in bstack11llll1l_opy_:
        bstack1ll11llll_opy_ = bstack11llll1l_opy_[key]
        if isinstance(bstack1ll11llll_opy_, list):
            for env_name in bstack1ll11llll_opy_:
                bstack111lll1ll1l_opy_[env_name] = value
        else:
            bstack111lll1ll1l_opy_[bstack1ll11llll_opy_] = value