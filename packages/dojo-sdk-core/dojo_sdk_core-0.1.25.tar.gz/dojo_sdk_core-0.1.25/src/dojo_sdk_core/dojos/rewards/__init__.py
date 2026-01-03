"""
Modular reward functions organized by game/application.

This package contains reward validation functions for different dojos,
organized into separate modules for maintainability.
"""

from dojo_sdk_core.dojos.rewards.backend import Backend
from dojo_sdk_core.dojos.rewards.jd_v2 import REWARD_FUNCTIONS_JD_V2
from dojo_sdk_core.dojos.rewards.weibo_v2 import REWARD_FUNCTIONS_WEIBO_V2
from dojo_sdk_core.dojos.rewards.xiaohongshu_v2 import REWARD_FUNCTIONS_XIAOHONGSHU_V2

# Unified registry of all reward functions
REWARD_FUNCTIONS = {
    **REWARD_FUNCTIONS_JD_V2,
    **REWARD_FUNCTIONS_WEIBO_V2,
    **REWARD_FUNCTIONS_XIAOHONGSHU_V2,
}

def get_reward_function(name: str):
    """Get a reward function by name from the unified registry."""
    return REWARD_FUNCTIONS.get(name)


__all__ = ["REWARD_FUNCTIONS", "get_reward_function", "Backend"]