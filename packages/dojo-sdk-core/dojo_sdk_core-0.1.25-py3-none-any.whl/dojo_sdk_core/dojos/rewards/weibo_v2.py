"""
Reward functions for Weibo SPA tasks - V2 Architecture.

This version includes both frontend and backend validation with bundled reward functions.
Each task exports a bundle containing:
  - state_key: Dict defining backend queries (collection + filter)
  - validate_backend: Function (state_key, final_state) -> (float, str)
  - validate_frontend: Function (initial_state, final_state) -> (float, str)
"""

import logging
import re
from typing import Any, Callable, Dict, Tuple, TypedDict, Union
from .backend import Backend

logger = logging.getLogger(__name__)

# =============================================================================
# Type Definitions
# =============================================================================

class StateKeyQuery(TypedDict):
    collection: str
    filter: Dict[str, Any]


StateKey = Dict[str, StateKeyQuery]
ValidatorFunc = Callable[[Dict[str, Any]], Tuple[float, str]]


class ValidateTask(TypedDict):
    state_key: StateKey
    validate_backend: ValidatorFunc
    validate_frontend: ValidatorFunc


# =============================================================================
# Helper Functions - Frontend State
# =============================================================================

def _check_current_view(final_state: Dict[str, Any], expected_view: str) -> Tuple[bool, str]:
    """Check if the current view matches the expected view."""
    view = final_state.get("currentView")
    if view != expected_view:
        return False, f"currentView='{view}' expected '{expected_view}'"
    return True, ""


def _check_theme(final_state: Dict[str, Any], expected_theme: str) -> Tuple[bool, str]:
    """Check if the theme matches the expected theme."""
    theme = final_state.get("theme")
    if theme != expected_theme:
        return False, f"theme='{theme}' expected '{expected_theme}'"
    return True, ""


def _check_viewed_user_id(final_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    """Check if the viewed user ID matches."""
    viewed_id = final_state.get("viewedUserId")
    if viewed_id != expected_id:
        return False, f"viewedUserId='{viewed_id}' expected '{expected_id}'"
    return True, ""


def _check_viewed_post_id(final_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    """Check if the viewed post ID matches."""
    viewed_id = final_state.get("viewedPostId")
    if viewed_id != expected_id:
        return False, f"viewedPostId='{viewed_id}' expected '{expected_id}'"
    return True, ""


def _check_search_category(final_state: Dict[str, Any], expected_category: str) -> Tuple[bool, str]:
    """Check if the search category matches."""
    category = final_state.get("searchCategory")
    if category != expected_category:
        return False, f"searchCategory='{category}' expected '{expected_category}'"
    return True, ""

def _check_search_query_equals(final_state: Dict[str, Any], expected_query: str) -> Tuple[bool, str]:
    """Check if the search query equals the expected value."""
    search_query = final_state.get("searchQuery", "")
    if search_query != expected_query:
        return False, f"searchQuery='{search_query}' expected '{expected_query}'"
    return True, ""


def _check_search_dropdown_open(final_state: Dict[str, Any], expected_open: bool) -> Tuple[bool, str]:
    """Check if the search dropdown is open."""
    dropdown_open = final_state.get("searchDropdownOpen", False)
    if dropdown_open != expected_open:
        return False, f"searchDropdownOpen={dropdown_open} expected {expected_open}"
    return True, ""


def _check_search_dropdown_results_empty(final_state: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if the search dropdown results are empty."""
    results = final_state.get("searchDropdownResults", {})
    suggestions = results.get("suggestions", [])
    users = results.get("users", [])
    if suggestions or users:
        return False, f"searchDropdownResults should be empty. suggestions={len(suggestions)}, users={len(users)}"
    return True, ""


def _check_search_dropdown_has_suggestions(final_state: Dict[str, Any], min_count: int = 1) -> Tuple[bool, str]:
    """Check if the search dropdown has suggestions."""
    results = final_state.get("searchDropdownResults", {})
    suggestions = results.get("suggestions", [])
    if len(suggestions) < min_count:
        return False, f"Expected at least {min_count} suggestion(s), got {len(suggestions)}"
    return True, ""


def _check_more_options_dropdown_open(final_state: Dict[str, Any], expected_open: bool) -> Tuple[bool, str]:
    """Check if the more options dropdown is open."""
    dropdown_open = final_state.get("moreOptionsDropdownOpen", False)
    if dropdown_open != expected_open:
        return False, f"moreOptionsDropdownOpen={dropdown_open} expected {expected_open}"
    return True, ""


def _check_feed_post_comments_open(final_state: Dict[str, Any], post_id: str) -> Tuple[bool, str]:
    """Check if a post's inline comments section is open in the feed."""
    displayed_posts = final_state.get("feedDisplayedPosts", [])
    for post in displayed_posts:
        if post.get("_id") == post_id:
            if post.get("isCommentsOpen") is True:
                return True, ""
            return False, f"Post '{post_id}' has isCommentsOpen={post.get('isCommentsOpen')}"
    return False, f"Post '{post_id}' not found in feedDisplayedPosts"


def _check_local_comment_like_override(
    final_state: Dict[str, Any], 
    comment_id: str, 
    expected_liked: bool
) -> Tuple[bool, str]:
    """Check if the comment like override matches the expected state."""
    overrides = final_state.get("localCommentLikeOverrides", {})
    comment_override = overrides.get(comment_id)
    if comment_override is None:
        return False, f"Comment '{comment_id}' not in localCommentLikeOverrides"
    is_liked = comment_override.get("isLiked")
    if is_liked != expected_liked:
        return False, f"Comment '{comment_id}' isLiked={is_liked} expected {expected_liked}"
    return True, ""


def _check_feed_comments_liked(
    final_state: Dict[str, Any], post_id: str, expected_comment_ids: list[str]
) -> Tuple[bool, str]:
    """Ensure specific comments on a feed post are liked (isLiked true).
    
    Checks localCommentLikeOverrides in dojo state (source of truth).
    """
    for comment_id in expected_comment_ids:
        ok, error = _check_local_comment_like_override(final_state, comment_id, True)
        if not ok:
            return False, error
    return True, ""


def _check_viewed_post_comments_liked(
    final_state: Dict[str, Any], expected_comment_ids: list[str]
) -> Tuple[bool, str]:
    """Ensure specific comments on the viewedPost are liked (isLiked true).
    
    Checks localCommentLikeOverrides in dojo state (source of truth).
    """
    for comment_id in expected_comment_ids:
        ok, error = _check_local_comment_like_override(final_state, comment_id, True)
        if not ok:
            return False, error
    return True, ""


def _check_local_post_like_override(
    final_state: Dict[str, Any], 
    post_id: str, 
    expected_liked: bool
) -> Tuple[bool, str]:
    """Check if the post like override matches the expected state."""
    overrides = final_state.get("localPostLikeOverrides", {})
    post_override = overrides.get(post_id)
    if post_override is None:
        return False, f"Post '{post_id}' not in localPostLikeOverrides"
    is_liked = post_override.get("isLiked")
    if is_liked != expected_liked:
        return False, f"Post '{post_id}' isLiked={is_liked} expected {expected_liked}"
    return True, ""

# =============================================================================
# NAVIGATION & SEARCH TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: profile-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    # Check that we're viewing a user's profile
    viewed_user_id = final_state.get("viewedUserId")
    if not viewed_user_id:
        return 0.0, "viewedUserId is missing or null"
    
    return 1.0, f"Successfully navigated to profile from search (user: {viewed_user_id})"


_validate_profile_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_search,
    "validate_frontend": _validate_frontend_profile_from_search,
}


# -----------------------------------------------------------------------------
# Task: search-users-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_users(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_users(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to search users page"


_validate_search_users: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_users,
    "validate_frontend": _validate_frontend_search_users,
}


# -----------------------------------------------------------------------------
# Task: switch-theme-v2
# -----------------------------------------------------------------------------

def _validate_backend_switch_theme(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_switch_theme(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_theme(final_state, "dark")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully switched to dark theme"


_validate_switch_theme: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_switch_theme,
    "validate_frontend": _validate_frontend_switch_theme,
}


# -----------------------------------------------------------------------------
# Task: search-dropdown-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_dropdown_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_search_dropdown_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user13")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to user profile via search dropdown"


_validate_search_dropdown_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_dropdown_profile,
    "validate_frontend": _validate_frontend_search_dropdown_profile,
}


# -----------------------------------------------------------------------------
# Task: profile-from-sorted-comments-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_sorted_comments(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_sorted_comments(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user13")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from sorted comments"


_validate_profile_from_sorted_comments: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_sorted_comments,
    "validate_frontend": _validate_frontend_profile_from_sorted_comments,
}


# -----------------------------------------------------------------------------
# Task: view-full-comment-thread-v2
# -----------------------------------------------------------------------------

def _validate_backend_view_full_comment_thread(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for viewing comments"


def _validate_frontend_view_full_comment_thread(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:

    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "5")
    if not ok:
        return 0.0, error
    
    # Check that ViewAllRepliesModal is open (viewAllRepliesModalCommentId is not null)
    view_all_replies_modal_comment_id = final_state.get("viewAllRepliesModalCommentId")
    if view_all_replies_modal_comment_id is None:
        return 0.0, "ViewAllRepliesModal is not open (viewAllRepliesModalCommentId is null)"
    
    return 1.0, f"Successfully viewing full comment thread on post 5 (comment {view_all_replies_modal_comment_id})"


_validate_view_full_comment_thread: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_view_full_comment_thread,
    "validate_frontend": _validate_frontend_view_full_comment_thread,
}


# -----------------------------------------------------------------------------
# Task: video-post-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_video_post_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for viewing post"


def _validate_frontend_video_post_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "23")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to video post from profile"


_validate_video_post_from_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_video_post_from_profile,
    "validate_frontend": _validate_frontend_video_post_from_profile,
}


# -----------------------------------------------------------------------------
# Task: refresh-list-of-trending-topics-v2
# -----------------------------------------------------------------------------

def _validate_backend_refresh_list_of_trending_topics(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # hotSearch is frontend-only state
    return 1.0, "No backend validation required for trending topics refresh"


def _validate_frontend_refresh_list_of_trending_topics(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    init_topics = initial_state.get("mineTrendingTopics") or []
    final_topics = final_state.get("mineTrendingTopics") or []

    if not isinstance(init_topics, list) or not isinstance(final_topics, list):
        return 0.0, "mineTrendingTopics is not a list"

    def topic_ids(topics):
        ids = []
        for t in topics:
            if isinstance(t, dict):
                ids.append(t.get("_id") or t.get("text"))
        return ids

    init_ids = topic_ids(init_topics)
    final_ids = topic_ids(final_topics)

    if not final_ids:
        return 0.0, "mineTrendingTopics is empty after refresh"

    if init_ids and set(init_ids) == set(final_ids):
        return 0.0, "mineTrendingTopics did not change after refresh"

    return 1.0, "Successfully refreshed trending topics"

    

_validate_refresh_list_of_trending_topics: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_refresh_list_of_trending_topics,
    "validate_frontend": _validate_frontend_refresh_list_of_trending_topics,
}


# -----------------------------------------------------------------------------
# Task: refresh-list-of-suggested-users-v2
# -----------------------------------------------------------------------------

def _validate_backend_refresh_list_of_suggested_users(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Backend state doesn't change for suggested users refresh
    # The refresh is a frontend re-query of the same backend data
    suggested = final_state.get("suggestedUsers")
    if not isinstance(suggested, list):
        return 0.0, "suggestedUsers array missing in backend final state"
    
    if len(suggested) == 0:
        return 0.0, "suggestedUsers array is empty"
    
    return 1.0, "Backend: Suggested users data exists"


def _validate_frontend_refresh_list_of_suggested_users(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    init_users = initial_state.get("suggestedUsers") or []
    final_users = final_state.get("suggestedUsers") or []

    if not isinstance(init_users, list) or not isinstance(final_users, list):
        return 0.0, "suggestedUsers is not a list"

    def topic_ids(topics):
        ids = []
        for t in topics:
            if isinstance(t, dict):
                ids.append(t.get("_id") or t.get("name"))
        return ids

    init_ids = topic_ids(init_users)
    final_ids = topic_ids(final_users)

    if not final_ids:
        return 0.0, "suggestedUsers is empty after refresh"

    if init_ids and set(init_ids) == set(final_ids):
        return 0.0, "suggestedUsers did not change after refresh"

    return 1.0, "Successfully refreshed suggested users"


_validate_refresh_list_of_suggested_users: ValidateTask = {
    "state_key": {
        "suggestedUsers": {"collection": "suggestedUsers", "filter": {}},
    },
    "validate_backend": _validate_backend_refresh_list_of_suggested_users,
    "validate_frontend": _validate_frontend_refresh_list_of_suggested_users,
}


# =============================================================================
# LIKE/UNLIKE TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: unlike-single-post-from-feed-v2
# -----------------------------------------------------------------------------

def _validate_backend_unlike_single_post_from_feed(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 1 has isLiked=false
    posts = final_state.get("posts")
    if not isinstance(posts, list) or len(posts) == 0:
        return 0.0, "Post 1 not found in backend"
    
    post = posts[0]

    initialNumberOfLikes = 128

    if post.get("likeCount") == initialNumberOfLikes - 1:
        return 1.0, "Backend: Post unliked successfully"

    return 0.0, "Backend: Post like count did not decrease after unlike"

def _validate_frontend_unlike_single_post_from_feed(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_local_post_like_override(final_state, "1", False)
    if not ok:
        return 0.0, error
    return 1.0, "Successfully unliked post from feed"


_validate_unlike_single_post_from_feed: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_unlike_single_post_from_feed,
    "validate_frontend": _validate_frontend_unlike_single_post_from_feed,
}


# -----------------------------------------------------------------------------
# Task: unlike-all-posts-on-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_unlike_all_posts_on_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that all posts by user1 are not liked
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    # Iterate through all posts and check none have isLiked=True
    liked_posts = []
    for post in posts:
        if post.get("isLiked") is True:
            liked_posts.append(post.get("_id", "unknown"))
    
    if len(liked_posts) > 0:
        return 0.0, f"Backend: Found {len(liked_posts)} liked post(s) by user1: {liked_posts}"
    
    return 1.0, f"Backend: All {len(posts)} posts by user1 are unliked successfully"


def _validate_frontend_unlike_all_posts_on_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check localPostLikeOverrides - all posts should be unliked
    overrides = final_state.get("localPostLikeOverrides", {})
    
    # All overrides should have isLiked=False
    for post_id, override in overrides.items():
        if override.get("isLiked") is True:
            return 0.0, f"Post '{post_id}' should be unliked"
    
    return 1.0, "Successfully unliked all posts on profile"


_validate_unlike_all_posts_on_profile: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "user1"}},
    },
    "validate_backend": _validate_backend_unlike_all_posts_on_profile,
    "validate_frontend": _validate_frontend_unlike_all_posts_on_profile,
}


# =============================================================================
# FOLLOW/UNFOLLOW TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: unfollow-user-from-profile-page-v2
# -----------------------------------------------------------------------------

def _validate_backend_unfollow_user_from_profile_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user5 is not followed (expect empty array)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) > 0:
        return 0.0, f"Backend: User 'user5' is still followed"
    
    return 1.0, "Backend: User unfollowed successfully"


def _validate_frontend_unfollow_user_from_profile_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user5")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully unfollowed user from profile page"


_validate_unfollow_user_from_profile_page: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user5"}},
    },
    "validate_backend": _validate_backend_unfollow_user_from_profile_page,
    "validate_frontend": _validate_frontend_unfollow_user_from_profile_page,
}


# -----------------------------------------------------------------------------
# Task: search-follow-last-user-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_follow_user(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user "8200663693" (当前用户) is followed in userFollows
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "User 8200663693 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId
    follow = user_follows[0]
    target_user_id = "8200663693"
    if follow.get("followedUserId") == target_user_id:
        return 1.0, f"Backend: User {target_user_id} successfully followed"
    
    return 0.0, f"Unexpected followedUserId: {follow.get('followedUserId')}"


def _validate_frontend_search_follow_user(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully searched and followed last user"


_validate_search_follow_user: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "8200663693"}},
    },
    "validate_backend": _validate_backend_search_follow_user,
    "validate_frontend": _validate_frontend_search_follow_user,
}


# =============================================================================
# GROUP MANAGEMENT TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: remove-user-from-single-group-v2
# -----------------------------------------------------------------------------

def _validate_backend_remove_user_from_single_group(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Get user1's follow entry (already filtered by followedUserId)
    user_follows_user1 = final_state.get("userFollows_user1")
    if not isinstance(user_follows_user1, list) or len(user_follows_user1) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows_user1[0]
    groups = follow.get("groups", [])
    
    # Check that user1 is NOT in "classmates" group
    if "classmates" in groups:
        return 0.0, "Backend: user1 is still in 'classmates' group"
    
    # Check that user1 is NOT in "colleagues" group
    # Just an extra award check to make sure the AI doesn't make multiple groups 
    if "colleagues" in groups:
        return 0.0, "Backend: user1 is still in 'colleagues' group"
    
    # Check that user1 is still in "celebrities" group
    if "celebrities" not in groups:
        return 0.0, "Backend: user1 is not in 'celebrities' group"
    
    return 1.0, "Backend: User removed from classmates group successfully"

def _validate_frontend_remove_user_from_single_group(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_viewed_user_id(final_state, "user1")
    
    if not ok:
        return 0.0, error

    return 1.0, "Successfully removed user from single group"


_validate_remove_user_from_single_group: ValidateTask = {
    "state_key": {
        "userFollows_user1": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_remove_user_from_single_group,
    "validate_frontend": _validate_frontend_remove_user_from_single_group,
}


# -----------------------------------------------------------------------------
# Task: reassign-user-to-different-group-v2
# -----------------------------------------------------------------------------

def _validate_backend_reassign_user_to_different_group(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Get user1's follow entry (already filtered by followedUserId)
    user_follows_user1 = final_state.get("userFollows_user1")
    if not isinstance(user_follows_user1, list) or len(user_follows_user1) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows_user1[0]
    groups = follow.get("groups", [])
    
    # Check that user1 is NOT in "classmates" group anymore
    if "classmates" in groups:
        return 0.0, "Backend: user1 is still in 'classmates' group"
    
    # Check that user1 is now in "colleagues" group
    if "colleagues" not in groups:
        return 0.0, "Backend: user1 is not in 'colleagues' group"
    
    return 1.0, "Backend: User reassigned from classmates to colleagues successfully"


def _validate_frontend_reassign_user_to_different_group(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully reassigned user to different group"


_validate_reassign_user_to_different_group: ValidateTask = {
    "state_key": {
        "userFollows_user1": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_reassign_user_to_different_group,
    "validate_frontend": _validate_frontend_reassign_user_to_different_group,
}


# -----------------------------------------------------------------------------
# Task: unassign-special-attention-and-groups-v2
# -----------------------------------------------------------------------------

def _validate_backend_unassign_special_attention_and_groups(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Get user1's follow entry (already filtered by followedUserId)
    user_follows_user1 = final_state.get("userFollows_user1")
    if not isinstance(user_follows_user1, list) or len(user_follows_user1) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows_user1[0]
    
    # Check that user1 has no groups assigned
    groups = follow.get("groups", [])
    if groups and len(groups) > 0:
        return 0.0, f"Backend: user1 still has groups assigned: {groups}"
    
    # Check that user1 has no special attention
    is_special = follow.get("isSpecialAttention", False)
    if is_special is True:
        return 0.0, "Backend: user1 still has special attention"
    
    return 1.0, "Backend: All groups and special attention removed successfully"


def _validate_frontend_unassign_special_attention_and_groups(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully unassigned special attention and groups"


_validate_unassign_special_attention_and_groups: ValidateTask = {
    "state_key": {
        "userFollows_user1": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_unassign_special_attention_and_groups,
    "validate_frontend": _validate_frontend_unassign_special_attention_and_groups,
}


# =============================================================================
# COMMENT TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: reply-to-comment-v2
# -----------------------------------------------------------------------------

def _validate_backend_reply_to_comment(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new reply was created on post 1 (already filtered by postId and user._id)
    replies = final_state.get("replies")
    if not isinstance(replies, list):
        return 0.0, "Replies array missing in backend final state"
    
    if len(replies) > 0:
        return 1.0, "Backend: Reply created successfully"
    
    return 0.0, "No new reply from current user found on post 1"


def _validate_frontend_reply_to_comment(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that comment section is open
    displayed_posts = final_state.get("feedDisplayedPosts", [])
    for post in displayed_posts:
        if post.get("_id") == "1":
            if post.get("isCommentsOpen") is True:
                return 1.0, "Successfully opened comments and replied"
    
    return 1.0, "Reply submitted (UI state may not track replies)"


_validate_reply_to_comment: ValidateTask = {
    "state_key": {
        "replies": {"collection": "replies", "filter": {"postId": "1", "user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_reply_to_comment,
    "validate_frontend": _validate_frontend_reply_to_comment,
}


# =============================================================================
# ADDITIONAL NAVIGATION TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: navigate-to-latest-feed-section-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_latest_feed_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_latest_feed_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "latest")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to latest feed section"


_validate_navigate_to_latest_feed_section: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_latest_feed_section,
    "validate_frontend": _validate_frontend_navigate_to_latest_feed_section,
}


# -----------------------------------------------------------------------------
# Task: navigate-via-trending-topic-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_via_trending_topic(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_via_trending_topic(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "comprehensive")
    if not ok:
        return 0.0, error
    
    # Search query should be set to the trending topic
    search_query = final_state.get("searchQuery", "")
    if not search_query:
        return 0.0, "searchQuery is empty"
    
    return 1.0, f"Successfully navigated via trending topic: {search_query}"


_validate_navigate_via_trending_topic: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_via_trending_topic,
    "validate_frontend": _validate_frontend_navigate_via_trending_topic,
}


# -----------------------------------------------------------------------------
# Task: no-search-suggestions-v2
# -----------------------------------------------------------------------------

def _validate_backend_no_search_suggestions(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_no_search_suggestions(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_search_query_equals(final_state, "asdf")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_open(final_state, True)
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_results_empty(final_state)
    if not ok:
        return 0.0, error
    
    return 1.0, "Search dropdown shows no suggestions for obscure query"


_validate_no_search_suggestions: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_no_search_suggestions,
    "validate_frontend": _validate_frontend_no_search_suggestions,
}


# -----------------------------------------------------------------------------
# Task: open-inline-comments-section-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_inline_comments_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for opening comments"


def _validate_frontend_open_inline_comments_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_feed_post_comments_open(final_state, "1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully opened inline comments section"


_validate_open_inline_comments_section: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_inline_comments_section,
    "validate_frontend": _validate_frontend_open_inline_comments_section,
}


# -----------------------------------------------------------------------------
# Task: open-post-composer-more-dropdown-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_post_composer_more_dropdown(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for opening dropdown"


def _validate_frontend_open_post_composer_more_dropdown(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_more_options_dropdown_open(final_state, True)
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully opened post composer more dropdown"


_validate_open_post_composer_more_dropdown: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_post_composer_more_dropdown,
    "validate_frontend": _validate_frontend_open_post_composer_more_dropdown,
}


# -----------------------------------------------------------------------------
# Task: partial-search-query-v2
# -----------------------------------------------------------------------------

def _validate_backend_partial_search_query(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_partial_search_query(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_search_query_equals(final_state, "电影")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_open(final_state, True)
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_has_suggestions(final_state, 1)
    if not ok:
        return 0.0, error
    
    return 1.0, "Search dropdown shows suggestions for partial query"


_validate_partial_search_query: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_partial_search_query,
    "validate_frontend": _validate_frontend_partial_search_query,
}


# -----------------------------------------------------------------------------
# Task: post-and-view-hashtag-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_and_view_hashtag(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with #weibo# hashtag was created (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        if "#weibo#" in content:
            return 1.0, "Backend: Post with #weibo# hashtag created"
    
    return 0.0, "No post with #weibo# hashtag found"


def _validate_frontend_post_and_view_hashtag(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_query_equals(final_state, "#weibo#")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "comprehensive")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully posted and navigated to hashtag view"


_validate_post_and_view_hashtag: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_post_and_view_hashtag,
    "validate_frontend": _validate_frontend_post_and_view_hashtag,
}


# -----------------------------------------------------------------------------
# Task: post-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_post_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "dot-1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post from profile"


_validate_post_from_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_post_from_profile,
    "validate_frontend": _validate_frontend_post_from_profile,
}


# -----------------------------------------------------------------------------
# Task: post-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_post_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "35")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post from search"


_validate_post_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_post_from_search,
    "validate_frontend": _validate_frontend_post_from_search,
}


# -----------------------------------------------------------------------------
# Task: post-image-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_image(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with image media was created (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        media = post.get("media", [])
        for m in media:
            if m.get("type") == "image":
                return 1.0, "Backend: Post with image created"
    
    return 0.0, "No post with image media found"


def _validate_frontend_post_image(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully posted image"


_validate_post_image: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_post_image,
    "validate_frontend": _validate_frontend_post_image,
}


# -----------------------------------------------------------------------------
# Task: post-video-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_video(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with video media was created (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        media = post.get("media", [])
        for m in media:
            if m.get("type") == "video":
                return 1.0, "Backend: Post with video created"
    
    return 0.0, "No post with video media found"


def _validate_frontend_post_video(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully posted video"


_validate_post_video: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_post_video,
    "validate_frontend": _validate_frontend_post_video,
}


# -----------------------------------------------------------------------------
# Task: profile-from-comments-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_comments(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_comments(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user9")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from comments"


_validate_profile_from_comments: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_comments,
    "validate_frontend": _validate_frontend_profile_from_comments,
}


# -----------------------------------------------------------------------------
# Task: profile-from-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user5")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from post"


_validate_profile_from_post: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_post,
    "validate_frontend": _validate_frontend_profile_from_post,
}


# -----------------------------------------------------------------------------
# Task: profile-from-reply-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_reply(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_reply(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user4")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from reply"


_validate_profile_from_reply: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_reply,
    "validate_frontend": _validate_frontend_profile_from_reply,
}


# =============================================================================
# CUSTOM GROUP MANAGEMENT TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: delete-custom-group-v2
# -----------------------------------------------------------------------------

def _validate_backend_delete_custom_group(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that the custom group 'celebrities' is deleted (expect empty array)
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list):
        return 0.0, "customGroups array missing in backend final state"
    
    if len(custom_groups) > 0:
        return 0.0, "Backend: Custom group 'celebrities' still exists"
    
    return 1.0, "Backend: Custom group deleted successfully"


def _validate_frontend_delete_custom_group(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Frontend validation intentionally skipped; rely solely on backend/state_key
    return 1.0, "No frontend validation required"


_validate_delete_custom_group: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"_id": "celebrities"}},
    },
    "validate_backend": _validate_backend_delete_custom_group,
    "validate_frontend": _validate_frontend_delete_custom_group,
}


# -----------------------------------------------------------------------------
# Task: edit-custom-group-name-v2
# -----------------------------------------------------------------------------

def _validate_backend_edit_custom_group_name(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that the custom group was renamed
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group with new name '新分组名' not found"
    
    # Get the first (and only) item since we filtered by label
    group = custom_groups[0]
    if group.get("label") == "新分组名":
        return 1.0, "Backend: Custom group renamed successfully"
    
    return 0.0, f"Unexpected group label: {group.get('label')}"


def _validate_frontend_edit_custom_group_name(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Frontend validation intentionally skipped; rely solely on backend/state_key
    return 1.0, "No frontend validation required"


_validate_edit_custom_group_name: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "新分组名"}},
    },
    "validate_backend": _validate_backend_edit_custom_group_name,
    "validate_frontend": _validate_frontend_edit_custom_group_name,
}


# =============================================================================
# FOLLOW FLOW TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: follow-and-set-special-attention-flow-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_and_set_special_attention_flow(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that both user1 and user2 are followed (filtered by followedUserId $in)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) < 2:
        return 0.0, f"Expected 2 followed users (user1 and user2), got {len(user_follows)}"
    
    # Find user1 and user2 entries
    user1_found = False
    user2_found = False
    user2_has_special = False
    
    for entry in user_follows:
        followed_id = entry.get("followedUserId")
        if followed_id == "user1":
            user1_found = True
        elif followed_id == "user2":
            user2_found = True
            user2_has_special = entry.get("isSpecialAttention", False) is True
    
    if not user1_found:
        return 0.0, "user1 not followed"
    if not user2_found:
        return 0.0, "user2 not followed"
    if not user2_has_special:
        return 0.0, "user2 is followed but does not have special attention"
    
    return 1.0, "Backend: Both users followed, user2 has special attention"


def _validate_frontend_follow_and_set_special_attention_flow(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "special-follow")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to special follow feed"


_validate_follow_and_set_special_attention_flow: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": {"$in": ["user1", "user2"]}}},
    },
    "validate_backend": _validate_backend_follow_and_set_special_attention_flow,
    "validate_frontend": _validate_frontend_follow_and_set_special_attention_flow,
}


# -----------------------------------------------------------------------------
# Task: follow-and-unfollow-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_and_unfollow_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user2 (科技资讯) is NOT followed (was followed then unfollowed)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) > 0:
        return 0.0, f"Backend: User 'user2' is still followed"
    
    return 1.0, "Backend: User followed and then unfollowed successfully"


def _validate_frontend_follow_and_unfollow_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully on profile page after follow/unfollow"


_validate_follow_and_unfollow_from_profile: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user2"}},
    },
    "validate_backend": _validate_backend_follow_and_unfollow_from_profile,
    "validate_frontend": _validate_frontend_follow_and_unfollow_from_profile,
}


# -----------------------------------------------------------------------------
# Task: follow-assign-to-group-and-navigate-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_assign_to_group_and_navigate(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user1 is followed (already filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not followed"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows[0]
    groups = follow.get("groups", [])
    if "celebrities" in groups:
        return 1.0, "Backend: User followed and assigned to celebrities group successfully"
    
    return 0.0, f"user1 not in 'celebrities' group. Groups: {groups}"


def _validate_frontend_follow_assign_to_group_and_navigate(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that current view is custom-group-celebrities
    view = final_state.get("currentView")
    if view != "custom-group-celebrities":
        return 0.0, f"currentView='{view}' expected 'custom-group-celebrities'"
    
    return 1.0, "Successfully navigated to custom group feed"


_validate_follow_assign_to_group_and_navigate: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_follow_assign_to_group_and_navigate,
    "validate_frontend": _validate_frontend_follow_assign_to_group_and_navigate,
}


# -----------------------------------------------------------------------------
# Task: follow-create-group-and-assign-flow-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_create_group_and_assign_flow(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new custom group "test" was created (filtered by label)
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group 'test' not found"
    
    # Get the first (and only) item since we filtered by label "test"
    group = custom_groups[0]
    group_id = group.get("_id")
    if not group_id:
        return 0.0, "Custom group 'test' has no _id"
    
    # Check that user1 follows exist (filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not followed"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows[0]
    groups = follow.get("groups", [])
    if group_id in groups:
        return 1.0, "Backend: User followed, group created, and user assigned successfully"
    
    return 0.0, f"user1 not in group '{group_id}'. Groups: {groups}"


def _validate_frontend_follow_create_group_and_assign_flow(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    # Check that manage groups modal is closed
    if final_state.get("manageGroupsModalOpen", False):
        return 0.0, "manageGroupsModalOpen should be false"
    
    return 1.0, "Successfully created group and assigned user"


_validate_follow_create_group_and_assign_flow: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "test"}},
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_follow_create_group_and_assign_flow,
    "validate_frontend": _validate_frontend_follow_create_group_and_assign_flow,
}


# -----------------------------------------------------------------------------
# Task: follow-multiple-users-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_multiple_users_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that at least 2 users are followed (already filtered by userId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) >= 2:
        return 1.0, f"Backend: {len(user_follows)} users followed successfully"
    else:
        return 0.0, f"Expected at least 2 users followed, found {len(user_follows)}"


def _validate_frontend_follow_multiple_users_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully followed multiple users from search"


_validate_follow_multiple_users_from_search: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"userId": "8200663693"}},
    },
    "validate_backend": _validate_backend_follow_multiple_users_from_search,
    "validate_frontend": _validate_frontend_follow_multiple_users_from_search,
}


# -----------------------------------------------------------------------------
# Task: follow-user-and-check-latest-feed-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_user_and_check_latest_feed(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user1 (用户小王) is followed (already filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not followed"
    
    # Verify the first (and only) item is user1
    follow = user_follows[0]
    if follow.get("followedUserId") == "user1":
        return 1.0, "Backend: user1 followed successfully"
    
    return 0.0, f"Unexpected followedUserId: {follow.get('followedUserId')}"


def _validate_frontend_follow_user_and_check_latest_feed(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "latest")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to latest feed after following user"


_validate_follow_user_and_check_latest_feed: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_follow_user_and_check_latest_feed,
    "validate_frontend": _validate_frontend_follow_user_and_check_latest_feed,
}


# =============================================================================
# NAVIGATION TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: home-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_home_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_home_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated home from search"


_validate_home_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_home_from_search,
    "validate_frontend": _validate_frontend_home_from_search,
}


# -----------------------------------------------------------------------------
# Task: navigate-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "4")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post detail page"


_validate_navigate_post: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_post,
    "validate_frontend": _validate_frontend_navigate_post,
}


# -----------------------------------------------------------------------------
# Task: navigate-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to user profile"


_validate_navigate_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_profile,
    "validate_frontend": _validate_frontend_navigate_profile,
}


# -----------------------------------------------------------------------------
# Task: load-more-posts-v2
# -----------------------------------------------------------------------------

def _validate_backend_load_more_posts(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for loading posts"


def _validate_frontend_load_more_posts(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    # Check that scrollPosition has increased (more posts loaded)
    initial_scroll = initial_state.get("feedScrollPosition", 0)
    final_scroll = final_state.get("feedScrollPosition", 0)
    
    if final_scroll <= initial_scroll:
        return 0.0, f"feedScrollPosition did not increase: {initial_scroll} -> {final_scroll}"
    
    return 1.0, f"Successfully loaded more posts (scrolled from {initial_scroll} to {final_scroll})"


_validate_load_more_posts: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_load_more_posts,
    "validate_frontend": _validate_frontend_load_more_posts,
}


# -----------------------------------------------------------------------------
# Task: load-many-posts-v2
# -----------------------------------------------------------------------------

def _validate_backend_load_many_posts(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for loading posts"


def _validate_frontend_load_many_posts(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "11")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post from far down in feed"


_validate_load_many_posts: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_load_many_posts,
    "validate_frontend": _validate_frontend_load_many_posts,
}


# =============================================================================
# LIKE TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: like-post-from-main-feed-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_post_from_main_feed(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 1 has isLiked=true
    posts = final_state.get("posts")
    if not isinstance(posts, list) or len(posts) == 0:
        return 0.0, "Post 1 not found in backend"
    
    post = posts[0]
    # if post.get("isLiked") is True:
    #     return 1.0, "Backend: Post liked successfully"
    
    initialNumberOfLikes = 127 
    if post.get("likeCount") == initialNumberOfLikes + 1:
        return 1.0, "Backend: Post liked successfully"

    return 0.0, "Backend: Post like count did not increase after like"


def _validate_frontend_like_post_from_main_feed(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_local_post_like_override(final_state, "1", True)
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully liked post from main feed"


_validate_like_post_from_main_feed: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_like_post_from_main_feed,
    "validate_frontend": _validate_frontend_like_post_from_main_feed,
}


# -----------------------------------------------------------------------------
# Task: like-comment-on-post-detail-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_comment_on_post_detail(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that comment p1-c1 has isLiked=true (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    for comment in comments:
        if comment.get("_id") == "p1-c1":
            if comment.get("isLiked") is True:
                return 1.0, "Backend: Comment liked successfully"
            else:
                return 0.0, "Comment p1-c1 is not liked in backend"
    
    return 0.0, "Comment p1-c1 not found in backend"


def _validate_frontend_like_comment_on_post_detail(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "1")
    if not ok:
        return 0.0, error

    ok, error = _check_viewed_post_comments_liked(final_state, ["p1-c1"])
    if not ok:
        return 0.0, error

    return 1.0, "Successfully liked comment on post detail page"


_validate_like_comment_on_post_detail: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "1"}},
    },
    "validate_backend": _validate_backend_like_comment_on_post_detail,
    "validate_frontend": _validate_frontend_like_comment_on_post_detail,
}


# -----------------------------------------------------------------------------
# Task: like-2-comments-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_2_comments(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that comments p1-c1 and p1-c2 have isLiked=true (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    liked_count = 0
    for comment in comments:
        if comment.get("_id") in ["p1-c1", "p1-c2"]:
            if comment.get("isLiked") is True:
                liked_count += 1
    
    if liked_count >= 2:
        return 1.0, "Backend: Both comments liked successfully"
    elif liked_count == 1:
        return 0.0, "Only 1 comment liked, expected 2"
    else:
        return 0.0, "Neither comment is liked in backend"


def _validate_frontend_like_2_comments(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    # Check that the post's comments section is open
    ok, error = _check_feed_post_comments_open(final_state, "1")
    if not ok:
        return 0.0, error

    ok, error = _check_feed_comments_liked(final_state, "1", ["p1-c1", "p1-c2"])
    if not ok:
        return 0.0, error

    return 1.0, "Successfully liked 2 comments"


_validate_like_2_comments: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "1"}},
    },
    "validate_backend": _validate_backend_like_2_comments,
    "validate_frontend": _validate_frontend_like_2_comments,
}


# =============================================================================
# SEARCH & NAVIGATION TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: accept-search-suggestion-v2
# -----------------------------------------------------------------------------

def _validate_backend_accept_search_suggestion(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_accept_search_suggestion(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_query_equals(final_state, "用户小王")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully accepted search suggestion"


_validate_accept_search_suggestion: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_accept_search_suggestion,
    "validate_frontend": _validate_frontend_accept_search_suggestion,
}


# -----------------------------------------------------------------------------
# Task: change-search-categories-v2
# -----------------------------------------------------------------------------

def _validate_backend_change_search_categories(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search category change"


def _validate_frontend_change_search_categories(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_query_equals(final_state, "用户小王")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully changed search category to users"


_validate_change_search_categories: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_change_search_categories,
    "validate_frontend": _validate_frontend_change_search_categories,
}


# -----------------------------------------------------------------------------
# Task: change-trending-tab-and-navigate-v2
# -----------------------------------------------------------------------------

def _validate_backend_change_trending_tab_and_navigate(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for trending tab navigation"


def _validate_frontend_change_trending_tab_and_navigate(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    # Check that hotSearchTab is "trending"
    hot_search_tab = final_state.get("hotSearchTab")
    if hot_search_tab != "trending":
        return 0.0, f"hotSearchTab='{hot_search_tab}' expected 'trending'"
    
    # Check that searchQuery is not empty (it should be the trending topic)
    search_query = final_state.get("searchQuery", "")
    if not search_query:
        return 0.0, "searchQuery is empty"
    
    return 1.0, f"Successfully changed trending tab and navigated to topic: {search_query}"


_validate_change_trending_tab_and_navigate: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_change_trending_tab_and_navigate,
    "validate_frontend": _validate_frontend_change_trending_tab_and_navigate,
}


# =============================================================================
# GROUP & USER MANAGEMENT TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: add-user-to-new-custom-group-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_add_user_to_new_custom_group_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new custom group "兴趣爱好" exists (filtered by label)
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group '兴趣爱好' not found"
    
    # Get the first (and only) item since we filtered by label
    group = custom_groups[0]
    group_id = group.get("_id")
    if not group_id:
        return 0.0, "Custom group '兴趣爱好' has no _id"
    
    # Check that user1 follows exist (filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows[0]
    groups = follow.get("groups", [])
    if group_id in groups:
        return 1.0, "Backend: New group created and user assigned"
    
    return 0.0, f"user1 not in group '{group_id}'. Groups: {groups}"


def _validate_frontend_add_user_to_new_custom_group_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully on profile page after adding user to new group"


_validate_add_user_to_new_custom_group_from_profile: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "兴趣爱好"}},
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_add_user_to_new_custom_group_from_profile,
    "validate_frontend": _validate_frontend_add_user_to_new_custom_group_from_profile,
}


# -----------------------------------------------------------------------------
# Task: create-custom-group-and-navigate-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_custom_group_and_navigate(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a custom group "test" exists
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group 'test' not found"
    
    # Get the first (and only) item since we filtered by label
    group = custom_groups[0]
    if group.get("label") == "test":
        return 1.0, "Backend: Custom group 'test' created"
    
    return 0.0, f"Unexpected group label: {group.get('label')}"


def _validate_frontend_create_custom_group_and_navigate(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that current view starts with "custom-group-"
    view = final_state.get("currentView", "")
    if not view.startswith("custom-group-"):
        return 0.0, f"currentView='{view}' expected to start with 'custom-group-'"
    
    return 1.0, f"Successfully navigated to custom group feed: {view}"


_validate_create_custom_group_and_navigate: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "test"}},
    },
    "validate_backend": _validate_backend_create_custom_group_and_navigate,
    "validate_frontend": _validate_frontend_create_custom_group_and_navigate,
}


# =============================================================================
# COMMENT TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: create-comment-with-expressions-on-detail-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_comment_with_expressions_on_detail(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 2 has a new comment with expression (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    # Look for a new comment from current user with expression content
    for comment in comments:
        if comment.get("user", {}).get("_id") == "8200663693":
            content = comment.get("content", "")
            # Check if it contains expression codes like [xxx]
            if "[" in content and "]" in content:
                return 1.0, "Backend: Comment with expression created successfully"
    
    return 0.0, "No new comment with expression found on post 2"


def _validate_frontend_create_comment_with_expressions_on_detail(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created comment with expressions on post detail"


_validate_create_comment_with_expressions_on_detail: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "2"}},
    },
    "validate_backend": _validate_backend_create_comment_with_expressions_on_detail,
    "validate_frontend": _validate_frontend_create_comment_with_expressions_on_detail,
}


# -----------------------------------------------------------------------------
# Task: create-comment-with-inline-section-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_comment_with_inline_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 2 has a new comment from current user (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    for comment in comments:
        if comment.get("user", {}).get("_id") == "8200663693":
            return 1.0, "Backend: New comment created on post 2"
    
    return 0.0, "No new comment from current user found on post 2"


def _validate_frontend_create_comment_with_inline_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_feed_post_comments_open(final_state, "2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created comment using inline section"


_validate_create_comment_with_inline_section: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "2"}},
    },
    "validate_backend": _validate_backend_create_comment_with_inline_section,
    "validate_frontend": _validate_frontend_create_comment_with_inline_section,
}


# =============================================================================
# POST CREATION TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: create-post-and-verify-in-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_and_verify_in_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post by current user exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        if "这是我的新微博" in content and "#日常生活#" in content:
            return 1.0, "Backend: New post created successfully"
    
    return 0.0, "No new post with expected content found"


def _validate_frontend_create_post_and_verify_in_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "8200663693")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post and verified in profile"


_validate_create_post_and_verify_in_profile: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_and_verify_in_profile,
    "validate_frontend": _validate_frontend_create_post_and_verify_in_profile,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-emoji-expression-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_emoji_expression(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with [doge] exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "[doge]" in content and is_original is True:
            return 1.0, "Backend: Post with [doge] expression created"
    
    return 0.0, "No post with [doge] expression found"


def _validate_frontend_create_post_with_emoji_expression(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with emoji expression"


_validate_create_post_with_emoji_expression: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_emoji_expression,
    "validate_frontend": _validate_frontend_create_post_with_emoji_expression,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-hashtags-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_hashtags(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with hashtags exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "#生活分享#" in content and "#每日心情#" in content and is_original is True:
            return 1.0, "Backend: Post with hashtags created with isOriginal=true"
    
    return 0.0, "No post with both hashtags #生活分享# and #每日心情# found with isOriginal=true"


def _validate_frontend_create_post_with_hashtags(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with hashtags"


_validate_create_post_with_hashtags: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_hashtags,
    "validate_frontend": _validate_frontend_create_post_with_hashtags,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-three-expressions-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_three_expressions(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with 3 expressions exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        # Count expression codes [xxx]
        expressions = re.findall(r'\[[^\]]+\]', content)
        if len(expressions) >= 3:
            return 1.0, f"Backend: Post with {len(expressions)} expressions created"
    
    return 0.0, "No post with at least 3 expressions found"


def _validate_frontend_create_post_with_three_expressions(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with three expressions"


_validate_create_post_with_three_expressions: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_three_expressions,
    "validate_frontend": _validate_frontend_create_post_with_three_expressions,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-two-or-more-emojis-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_two_or_more_emojis(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with 2+ different emojis exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        # Count unique expression codes [xxx]
        expressions = set(re.findall(r'\[[^\]]+\]', content))
        is_original = post.get("isOriginal", False)
        if len(expressions) >= 2 and is_original is True:
            return 1.0, f"Backend: Post with {len(expressions)} different emojis created"
    
    return 0.0, "No post with at least 2 different emojis found"


def _validate_frontend_create_post_with_two_or_more_emojis(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with two or more emojis"


_validate_create_post_with_two_or_more_emojis: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_two_or_more_emojis,
    "validate_frontend": _validate_frontend_create_post_with_two_or_more_emojis,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-user-mention-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_user_mention(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with @mention exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "@科技资讯" in content and is_original is True:
            return 1.0, "Backend: Post with @mention created"
    
    return 0.0, "No post with @科技资讯 mention found with isOriginal=true"


def _validate_frontend_create_post_with_user_mention(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with user mention"


_validate_create_post_with_user_mention: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_user_mention,
    "validate_frontend": _validate_frontend_create_post_with_user_mention,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-mention-and-hashtag-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_mention_and_hashtag(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with both @mention and hashtag exists (filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "@用户小王" in content and "#weibo#" in content and is_original is True:
            return 1.0, "Backend: Post with mention and hashtag created"
    
    return 0.0, "No post with @用户小王 and #weibo# found with isOriginal=true"


def _validate_frontend_create_post_with_mention_and_hashtag(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with mention and hashtag"


_validate_create_post_with_mention_and_hashtag: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_mention_and_hashtag,
    "validate_frontend": _validate_frontend_create_post_with_mention_and_hashtag,
}


# -----------------------------------------------------------------------------
# Task: Entertainment Special Attention Setup
# -----------------------------------------------------------------------------

def _validate_entertainment_special_attention_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for entertainment special attention setup task.
    
    Checks:
    - Backend: ≥2 verified entertainment-related accounts are in Special Attention category
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Entertainment keywords (Chinese and English)
    entertainment_keywords = [
        "娱乐", "明星", "艺人", "演员", "歌手", "偶像", "综艺", "影视", 
        "电影", "电视剧", "音乐", "演唱会", "粉丝", "追星", "娱乐圈", 
        "影视圈", "影视剧", "综艺节目", "娱乐新闻", "娱乐资讯",
        "entertainment", "celebrity", "actor", "singer", "idol", "fan"
    ]

    # Query userFollows for Special Attention accounts
    user_follows_result = backend.query({"collection": "userFollows", "filter": {"isSpecialAttention": True}})
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []

    # Extract account IDs
    special_attention_account_ids: list[str] = []
    if isinstance(user_follows, list):
        for f in user_follows:
            if isinstance(f, dict):
                followed_uid = f.get("followedUserId")
                if followed_uid:
                    special_attention_account_ids.append(followed_uid)

    # Verify ≥2 accounts exist in Special Attention
    if len(special_attention_account_ids) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 accounts in Special Attention, found {len(special_attention_account_ids)}"
        )

    # Query posts for each Special Attention account and verify entertainment content
    entertainment_accounts = []
    for account_id in special_attention_account_ids:
        posts_result = backend.query({"collection": "posts", "filter": {"user._id": account_id}})
        posts = posts_result if isinstance(posts_result, list) else []
        
        # Check recent posts for entertainment content
        has_entertainment_content = False
        if isinstance(posts, list):
            for post in posts[:10]:  # Check last 10 posts
                if not isinstance(post, dict):
                    continue
                content = post.get("content", "") or ""
                if any(keyword in content for keyword in entertainment_keywords):
                    has_entertainment_content = True
                    break
        
        if has_entertainment_content:
            entertainment_accounts.append(account_id)

    # Verify ≥2 accounts have entertainment-related posts
    if len(entertainment_accounts) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 entertainment-related accounts in Special Attention, found {len(entertainment_accounts)}"
        )

    # Check verified status (optional)
    if len(special_attention_account_ids) > 0:
        users_result = backend.query({
            "collection": "users",
            "filter": {"_id": {"$in": special_attention_account_ids}}
        })
        users = users_result if isinstance(users_result, list) else []
        
        verified_count = 0
        if isinstance(users, list):
            for user in users:
                if not isinstance(user, dict):
                    continue
                # Check for verified status (handle different possible field names)
                is_verified = (
                    user.get("verified") is True or
                    user.get("isVerified") is True or
                    user.get("verifiedStatus") == "verified" or
                    user.get("verificationStatus") == "verified"
                )
                if is_verified:
                    verified_count += 1
        
        # Only award points if verified status field exists and accounts are verified
        if verified_count >= 2:
            checks_passed.append(True)
        elif len(users) > 0:
            # If users were found but none are verified, don't penalize (field might not exist)
            # Only add message if we found users but they're not verified
            if verified_count == 0 and any(
                "verified" in str(user).lower() or "verification" in str(user).lower()
                for user in users if isinstance(user, dict)
            ):
                checks_passed.append(False)
                messages.append(
                    f"Expected ≥2 verified accounts in Special Attention, found {verified_count}"
                )
            else:
                # Field might not exist, so don't fail this check
                checks_passed.append(True)

    if all(checks_passed):
        return 1.0, "All entertainment special attention setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some entertainment special attention setup checks failed"


# -----------------------------------------------------------------------------
# Task: Political Trending Topic Comment
# -----------------------------------------------------------------------------

def _validate_political_trending_topic_comment(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for political trending topic comment task.
    
    Checks:
    - Frontend: Current screen shows political/government trending topic
    - Backend: Comment exists on a post within that topic
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Political keywords (Chinese and English)
    political_keywords = [
        "政治", "政府", "政策", "政治新闻", "政府政策", "政治话题", "政府公告", 
        "政策解读", "政治动态", "政府回应", "政策调整",
        "government", "policy", "politics", "political"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    if current_view in ["trending", "search"]:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Frontend checks: Verify trending topic contains political/government keywords
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_political_topic = False
    political_topic_text = ""
    
    # Check trendingTopics array
    if isinstance(trending_topics, list):
        for topic in trending_topics:
            if isinstance(topic, dict):
                topic_text = topic.get("text", "") or topic.get("_id", "") or ""
            elif isinstance(topic, str):
                topic_text = topic
            else:
                continue
            
            if any(keyword in topic_text for keyword in political_keywords):
                has_political_topic = True
                political_topic_text = topic_text
                break
    
    # Check searchQuery if trending topics array doesn't have political content
    if not has_political_topic and search_query:
        if any(keyword in search_query for keyword in political_keywords):
            has_political_topic = True
            political_topic_text = search_query
    
    if has_political_topic:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected trending topic or search query to contain political/government keywords"
        )

    # Backend checks: Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: list[str] = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.append(post_id)

    # Backend checks: Verify comment exists on a post within political trending topic
    comment_on_political_post = False
    if len(commented_post_ids) > 0:
        for post_id in commented_post_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"_id": post_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            if isinstance(posts, list) and len(posts) > 0:
                post = posts[0]
                if isinstance(post, dict):
                    # Check post content for political keywords
                    content = post.get("content", "") or ""
                    
                    # Check hashtags for political keywords
                    hashtags = post.get("hashtags") or []
                    hashtag_texts = []
                    if isinstance(hashtags, list):
                        for tag in hashtags:
                            if isinstance(tag, dict):
                                tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                            elif isinstance(tag, str):
                                tag_text = tag
                            else:
                                continue
                            hashtag_texts.append(tag_text)
                    
                    # Check if post content or hashtags contain political keywords
                    post_has_political_content = (
                        any(keyword in content for keyword in political_keywords) or
                        any(keyword in tag_text for tag_text in hashtag_texts for keyword in political_keywords)
                    )
                    
                    if post_has_political_content:
                        comment_on_political_post = True
                        break
    
    if comment_on_political_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected comment to exist on a post with political/government content within the trending topic"
        )

    if all(checks_passed):
        return 1.0, "All political trending topic comment checks passed"
    return 0.0, "; ".join(messages) if messages else "Some political trending topic comment checks failed"


# -----------------------------------------------------------------------------
# Task: Movie Review Post
# -----------------------------------------------------------------------------

def _validate_movie_review_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for movie review post task.
    
    Checks:
    - Backend: New post exists containing movie review content and ≥1 movie-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Movie keywords
    movie_keywords = [
        "电影", "影片", "movie", "film", "cinema", "影院", "影评", "电影推荐", 
        "观影", "电影观后感", "电影评价", "电影分享", "电影评论"
    ]
    
    # Review keywords
    review_keywords = [
        "推荐", "好看", "值得看", "必看", "建议", "值得", "不错", "推荐看", 
        "观后感", "评价", "分享", "评论"
    ]
    
    # Movie hashtag keywords
    movie_hashtag_keywords = [
        "电影", "影片", "movie", "film", "cinema", "影院", "影评", "电影推荐", 
        "观影", "电影观后感"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with movie review content
    movie_review_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains both movie keywords AND review keywords
            has_movie_keyword = any(keyword in content for keyword in movie_keywords)
            has_review_keyword = any(keyword in content for keyword in review_keywords)
            
            if has_movie_keyword and has_review_keyword:
                movie_review_post = post
                break

    if movie_review_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected post containing movie review content (both movie keywords and review keywords)"
        )

    # Verify post has ≥1 movie-related hashtag
    has_movie_hashtag = False
    if movie_review_post:
        hashtags = movie_review_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in movie_hashtag_keywords):
                    has_movie_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_movie_hashtag:
            content = movie_review_post.get("content", "") or ""
            if "#" in content:
                for keyword in movie_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_movie_hashtag = True
                        break
        
        if has_movie_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 movie-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: movie review post not found")

    if all(checks_passed):
        return 1.0, "All movie review post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some movie review post checks failed"


# -----------------------------------------------------------------------------
# Task: Food Recipe Post Likes
# -----------------------------------------------------------------------------

def _validate_food_recipe_post_likes(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for food recipe post likes task.
    
    Checks:
    - Backend: ≥3 food/recipe posts show as liked by user
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Food keywords
    food_keywords = [
        "美食", "食物", "food", "recipe", "食谱", "烹饪", "cooking", "做菜", 
        "料理", "菜谱", "美食分享", "美食推荐", "烹饪技巧", "做菜方法", 
        "料理教程", "食谱分享"
    ]
    
    # Recipe/cooking tip keywords (to distinguish from just food photos)
    recipe_keywords = [
        "食谱", "recipe", "烹饪", "cooking", "做法", "步骤", "教程", "方法", 
        "技巧", "分享"
    ]

    # Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: list[str] = []
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.append(post_id)

    # Query posts collection and verify food/recipe content
    food_recipe_posts = []
    for post_id in liked_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains both food keywords AND recipe/cooking tip keywords
                has_food_keyword = any(keyword in content for keyword in food_keywords)
                has_recipe_keyword = any(keyword in content for keyword in recipe_keywords)
                
                if has_food_keyword and has_recipe_keyword:
                    food_recipe_posts.append(post_id)

    # Verify ≥3 food/recipe posts are liked
    if len(food_recipe_posts) >= 3:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥3 food/recipe posts liked (posts with both food and recipe keywords), found {len(food_recipe_posts)}"
        )

    if all(checks_passed):
        return 1.0, "All food recipe post likes checks passed"
    return 0.0, "; ".join(messages) if messages else "Some food recipe post likes checks failed"


# -----------------------------------------------------------------------------
# Task: Work Group Organization
# -----------------------------------------------------------------------------

def _validate_work_group_organization(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for work group organization task.
    
    Checks:
    - Backend: Custom group named '工作' exists
    - Backend: ≥2 business/career accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Business/career keywords
    business_keywords = [
        "工作", "business", "career", "职业", "商业", "工作相关", "职场", 
        "职业发展", "商业资讯", "工作分享", "职场经验", "职业规划", 
        "商业分析", "工作技巧", "职场技能"
    ]

    # Query customGroups collection for '工作' group
    custom_groups_result = backend.query({
        "collection": "customGroups",
        "filter": {"label": "工作"}
    })
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Verify custom group named '工作' exists
    work_group_id: str | None = None
    if isinstance(custom_groups, list) and len(custom_groups) > 0:
        work_group = custom_groups[0]
        if isinstance(work_group, dict):
            work_group_id = work_group.get("_id")
    
    if work_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group named '工作' not found")

    # Query userFollows collection for accounts assigned to group
    business_accounts = []
    if work_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": work_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify business/career content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for business/career content
            has_business_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in business_keywords):
                        has_business_content = True
                        break
            
            if has_business_content:
                business_accounts.append(account_id)
        
        # Verify ≥2 accounts have business/career content
        if len(business_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 business/career accounts assigned to '工作' group, found {len(business_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify business accounts: '工作' group not found")

    if all(checks_passed):
        return 1.0, "All work group organization checks passed"
    return 0.0, "; ".join(messages) if messages else "Some work group organization checks failed"


# -----------------------------------------------------------------------------
# Task: Tech Trending Topic Engagement
# -----------------------------------------------------------------------------

def _validate_tech_trending_topic_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for tech trending topic engagement task.
    
    Checks:
    - Frontend: Current screen shows trending topic
    - Backend: ≥2 tech posts within trending topic show as liked and commented by user
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Tech keywords
    tech_keywords = [
        "科技", "技术", "tech", "technology", "手机", "smartphone", "智能手机", 
        "科技新闻", "技术创新", "科技资讯", "科技产品", "科技趋势"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_tech_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in tech_keywords):
                    has_tech_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have tech content
        if not has_tech_topic and search_query:
            if any(keyword in search_query for keyword in tech_keywords):
                has_tech_topic = True
        
        if has_tech_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain tech keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Backend checks: Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are both liked AND commented
    liked_and_commented_post_ids = liked_post_ids & commented_post_ids

    # Query posts collection and verify tech content
    tech_posts_liked_and_commented = []
    for post_id in liked_and_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains tech keywords
                if any(keyword in content for keyword in tech_keywords):
                    tech_posts_liked_and_commented.append(post_id)

    # Verify ≥2 tech posts are both liked and commented
    if len(tech_posts_liked_and_commented) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 tech posts that are both liked and commented, found {len(tech_posts_liked_and_commented)}"
        )

    if all(checks_passed):
        return 1.0, "All tech trending topic engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some tech trending topic engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Fitness Workout Post
# -----------------------------------------------------------------------------

def _validate_fitness_workout_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for fitness workout post task.
    
    Checks:
    - Backend: New post exists containing fitness/workout content, ≥1 fitness hashtag, and ≥1 emoji
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Fitness keywords
    fitness_keywords = [
        "健身", "运动", "fitness", "workout", "锻炼", "exercise", "运动健身", 
        "健身计划", "运动习惯", "健身分享", "运动日常"
    ]
    
    # Fitness hashtag keywords
    fitness_hashtag_keywords = [
        "健身", "运动", "fitness", "workout", "锻炼", "exercise", "健身打卡", "运动健身"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with fitness/workout content
    fitness_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains fitness keywords
            if any(keyword in content for keyword in fitness_keywords):
                fitness_post = post
                break

    if fitness_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing fitness/workout content")

    # Verify post has ≥1 fitness hashtag
    has_fitness_hashtag = False
    if fitness_post:
        hashtags = fitness_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in fitness_hashtag_keywords):
                    has_fitness_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_fitness_hashtag:
            content = fitness_post.get("content", "") or ""
            if "#" in content:
                for keyword in fitness_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_fitness_hashtag = True
                        break
        
        if has_fitness_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 fitness-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: fitness post not found")

    # Verify post contains ≥1 emoji
    has_emoji = False
    if fitness_post:
        content = fitness_post.get("content", "") or ""
        # Use regex to detect emoji
        emoji_pattern = re.compile(
            r'[\U0001F300-\U0001F9FF]|[\U0001F600-\U0001F64F]|[\U0001F680-\U0001F6FF]|[\u2600-\u26FF]|[\u2700-\u27BF]'
        )
        has_emoji = bool(emoji_pattern.search(content))
        
        if has_emoji:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 emoji")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify emoji: fitness post not found")

    if all(checks_passed):
        return 1.0, "All fitness workout post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some fitness workout post checks failed"


# -----------------------------------------------------------------------------
# Task: Travel Group Setup
# -----------------------------------------------------------------------------

def _validate_travel_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for travel group setup task.
    
    Checks:
    - Backend: Custom group with travel-related name exists
    - Backend: ≥2 travel accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Travel group name keywords
    travel_group_keywords = [
        "旅行", "旅游", "travel", "旅行分享", "旅游攻略", "旅行日记", "旅游资讯"
    ]
    
    # Travel content keywords
    travel_keywords = [
        "旅行", "旅游", "travel", "旅行分享", "旅游攻略", "旅行日记", "旅游资讯", 
        "旅行vlog", "旅游推荐", "旅行体验", "旅游景点"
    ]

    # Query customGroups collection for travel-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find travel-related group
    travel_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in travel_group_keywords):
                    travel_group_id = g.get("_id")
                    break
    
    if travel_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with travel-related name not found")

    # Query userFollows collection for accounts assigned to group
    travel_accounts = []
    if travel_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": travel_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify travel content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for travel content
            has_travel_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in travel_keywords):
                        has_travel_content = True
                        break
            
            if has_travel_content:
                travel_accounts.append(account_id)
        
        # Verify ≥2 accounts have travel content
        if len(travel_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 travel accounts assigned to group, found {len(travel_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify travel accounts: travel group not found")

    if all(checks_passed):
        return 1.0, "All travel group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some travel group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Latest Weibo Feed Comment
# -----------------------------------------------------------------------------

def _validate_latest_weibo_feed_comment(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for Latest Weibo feed comment task.
    
    Checks:
    - Frontend: Currently viewing Latest Weibo feed
    - Backend: Comment exists on a post with ≥3 existing comments
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"

    # Frontend checks: Verify currently viewing Latest Weibo feed
    current_view = final_state_frontend.get("currentView", "")
    if current_view == "latest":
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'latest', got '{current_view}'"
        )

    # Backend checks: Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: list[str] = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.append(post_id)

    # Query posts collection and verify ≥3 comments exist
    comment_on_post_with_3_comments = False
    for post_id in commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                # Count total comments on the post (including current user's comment)
                # Query comments collection for all comments on this post
                post_comments_result = backend.query({
                    "collection": "comments",
                    "filter": {"postId": post_id}
                })
                post_comments = post_comments_result if isinstance(post_comments_result, list) else []
                
                total_comment_count = len(post_comments) if isinstance(post_comments, list) else 0
                
                if total_comment_count >= 3:
                    comment_on_post_with_3_comments = True
                    break

    if comment_on_post_with_3_comments:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected comment to exist on a post with ≥3 existing comments"
        )

    if all(checks_passed):
        return 1.0, "All Latest Weibo feed comment checks passed"
    return 0.0, "; ".join(messages) if messages else "Some Latest Weibo feed comment checks failed"


# -----------------------------------------------------------------------------
# Task: Book Accounts Follow from Search
# -----------------------------------------------------------------------------

def _validate_book_accounts_follow_from_search(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for book accounts follow from search task.
    
    Checks:
    - Frontend: Search was performed
    - Backend: ≥2 book/reading accounts followed from search results
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Book search keywords
    book_search_keywords = [
        "读书", "阅读", "book", "reading", "书籍", "读书分享", "阅读推荐"
    ]
    
    # Book/reading keywords
    book_keywords = [
        "读书", "阅读", "book", "reading", "书籍", "读书分享", "阅读推荐", 
        "书评", "读书笔记", "阅读心得", "书籍推荐", "读书感悟"
    ]

    # Frontend checks: Verify search was performed
    search_query = final_state_frontend.get("searchQuery", "") or ""
    current_view = final_state_frontend.get("currentView", "")
    
    search_performed = False
    if current_view == "search":
        search_performed = True
    elif search_query:
        if any(keyword in search_query for keyword in book_search_keywords):
            search_performed = True
    
    if search_performed:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected search to be performed (currentView='search' or searchQuery contains book keywords)"
        )
        return 0.0, "; ".join(messages)

    # Backend checks: Query userFollows collection for followed accounts
    user_follows_result = backend.query({"collection": "userFollows", "filter": {}})
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []
    
    # Extract account IDs
    followed_account_ids: list[str] = []
    if isinstance(user_follows, list):
        for f in user_follows:
            if isinstance(f, dict):
                followed_uid = f.get("followedUserId")
                if followed_uid:
                    followed_account_ids.append(followed_uid)

    # Query posts collection for followed accounts and verify book/reading content
    book_accounts = []
    for account_id in followed_account_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"user._id": account_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        # Check recent posts for book/reading content
        has_book_content = False
        if isinstance(posts, list):
            for post in posts[:10]:  # Check last 10 posts
                if not isinstance(post, dict):
                    continue
                content = post.get("content", "") or ""
                
                if any(keyword in content for keyword in book_keywords):
                    has_book_content = True
                    break
        
        if has_book_content:
            book_accounts.append(account_id)

    # Verify ≥2 accounts have book/reading content with reviews
    if len(book_accounts) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 book/reading accounts followed, found {len(book_accounts)}"
        )
        return 0.0, "; ".join(messages)

    if all(checks_passed):
        return 1.0, "All book accounts follow from search checks passed"
    return 0.0, "; ".join(messages) if messages else "Some book accounts follow from search checks failed"


# -----------------------------------------------------------------------------
# Task: Trending News Topic Post
# -----------------------------------------------------------------------------

def _validate_trending_news_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for trending news topic post task.
    
    Checks:
    - Backend: New post exists referencing trending news topic with appropriate hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # News keywords
    news_keywords = [
        "新闻", "news", "时事", "热点", "事件", "报道", "新闻资讯", "时事新闻", 
        "热点新闻", "新闻事件", "新闻报道"
    ]
    
    # News hashtag keywords
    news_hashtag_keywords = [
        "新闻", "news", "时事", "热点", "事件", "报道", "新闻资讯", "时事新闻", "热点新闻"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with news content
    news_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains news keywords
            if any(keyword in content for keyword in news_keywords):
                news_post = post
                break

    if news_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing news content")

    # Verify post references trending topic
    has_trending_reference = False
    if news_post:
        content = news_post.get("content", "") or ""
        hashtags = news_post.get("hashtags") or []
        
        # Check if post content or hashtags contain trending news-related keywords
        # Check content for trending/news keywords
        if any(keyword in content for keyword in news_keywords):
            has_trending_reference = True
        
        # Check hashtags for trending/news keywords
        if not has_trending_reference and isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in news_keywords):
                    has_trending_reference = True
                    break
        
        if has_trending_reference:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to reference trending news topic")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify trending topic reference: news post not found")

    # Verify post has appropriate hashtag
    has_news_hashtag = False
    if news_post:
        hashtags = news_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in news_hashtag_keywords):
                    has_news_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_news_hashtag:
            content = news_post.get("content", "") or ""
            if "#" in content:
                for keyword in news_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_news_hashtag = True
                        break
        
        if has_news_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain appropriate news-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: news post not found")

    if all(checks_passed):
        return 1.0, "All trending news topic post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some trending news topic post checks failed"


# -----------------------------------------------------------------------------
# Task: Music Posts Likes and Follow
# -----------------------------------------------------------------------------

def _validate_music_posts_likes_and_follow(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for music posts likes and follow task.
    
    Checks:
    - Backend: ≥2 music posts liked
    - Backend: ≥1 music-related account followed
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Music keywords
    music_keywords = [
        "音乐", "music", "歌曲", "song", "歌手", "singer", "专辑", "album", 
        "演唱会", "concert", "音乐推荐", "音乐分享", "音乐人", "音乐作品", "音乐风格"
    ]

    # Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: list[str] = []
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.append(post_id)

    # Query posts collection for liked posts and verify music content
    music_posts_liked = []
    for post_id in liked_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains music keywords
                if any(keyword in content for keyword in music_keywords):
                    music_posts_liked.append(post_id)

    # Verify ≥2 music posts are liked
    if len(music_posts_liked) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 music posts to be liked, found {len(music_posts_liked)}"
        )

    # Query userFollows collection for followed accounts
    user_follows_result = backend.query({"collection": "userFollows", "filter": {}})
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []
    
    # Extract account IDs
    followed_account_ids: list[str] = []
    if isinstance(user_follows, list):
        for f in user_follows:
            if isinstance(f, dict):
                followed_uid = f.get("followedUserId")
                if followed_uid:
                    followed_account_ids.append(followed_uid)

    # Query posts collection for followed accounts and verify music content
    music_accounts = []
    for account_id in followed_account_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"user._id": account_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        # Check recent posts for music content
        has_music_content = False
        if isinstance(posts, list):
            for post in posts[:10]:  # Check last 10 posts
                if not isinstance(post, dict):
                    continue
                content = post.get("content", "") or ""
                if any(keyword in content for keyword in music_keywords):
                    has_music_content = True
                    break
        
        if has_music_content:
            music_accounts.append(account_id)

    # Verify ≥1 music-related account is followed
    if len(music_accounts) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 music-related account to be followed, found {len(music_accounts)}"
        )

    score = max(0.0, min(1.0, score_accum / total_weight)) if total_weight > 0 else 0.0
    if score == 1.0:
        return score, "All music posts likes and follow checks passed"
    return score, "; ".join(messages) if messages else "Some music posts likes and follow checks failed"
    

# -----------------------------------------------------------------------------
# Task: Special Attention Removal
# -----------------------------------------------------------------------------

def _validate_special_attention_removal(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for Special Attention removal task.
    
    Checks:
    - Backend: ≥1 account removed from Special Attention category
    
    Initial state: exactly 5 users followed, exactly 1 user in special attention
    Final state should have: 0 users in special attention
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"

    # Query userFollows collection for Special Attention accounts
    user_follows_result = backend.query({
        "collection": "userFollows",
        "filter": {"isSpecialAttention": True}
    })
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []

    # Count accounts in Special Attention
    special_attention_count = len(user_follows) if isinstance(user_follows, list) else 0

    # Verify removal occurred: should be 0 users in Special Attention
    # (initial state had exactly 1, so removal means final state should have 0)
    if special_attention_count == 0:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected 0 users in Special Attention (1 was removed), found {special_attention_count}"
        )

    if all(checks_passed):
        return 1.0, "All Special Attention removal checks passed"
    return 0.0, "; ".join(messages) if messages else "Some Special Attention removal checks failed"


# -----------------------------------------------------------------------------
# Task: Photography/Art Comments
# -----------------------------------------------------------------------------

def _validate_photography_art_comments(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for photography/art comments task.
    
    Checks:
    - Backend: ≥2 photography/art posts have comments from user
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Photography/art keywords
    photography_art_keywords = [
        "摄影", "photography", "照片", "photo", "艺术", "art", "艺术创作", "摄影作品", 
        "摄影技巧", "艺术分享", "摄影艺术", "艺术作品", "艺术欣赏", "摄影展", "艺术展"
    ]

    # Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: list[str] = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.append(post_id)

    # Query posts collection for commented posts and verify photography/art content
    photography_art_posts_commented = []
    for post_id in commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains photography/art keywords
                if any(keyword in content for keyword in photography_art_keywords):
                    photography_art_posts_commented.append(post_id)

    # Verify ≥2 photography/art posts have comments
    if len(photography_art_posts_commented) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 photography/art posts to have comments, found {len(photography_art_posts_commented)}"
        )

    if all(checks_passed):
        return 1.0, "All photography/art comments checks passed"
    return 0.0, "; ".join(messages) if messages else "Some photography/art comments checks failed"


# -----------------------------------------------------------------------------
# Task: Seasons/Nature Post
# -----------------------------------------------------------------------------

def _validate_seasons_nature_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for seasons/nature post task.
    
    Checks:
    - Backend: New post exists about seasons/nature with ≥1 nature-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Seasons keywords
    seasons_keywords = [
        "秋天", "autumn", "冬季", "winter", "季节", "season", "秋", "冬", 
        "季节变化", "季节更替"
    ]
    
    # Nature keywords
    nature_keywords = [
        "自然", "nature", "大自然", "自然风光", "自然美景", "自然景观", 
        "自然风景", "自然生态", "自然观察"
    ]
    
    # Nature hashtag keywords (includes seasons)
    nature_hashtag_keywords = [
        "自然", "nature", "大自然", "自然风光", "自然美景", "自然景观", 
        "自然风景", "自然生态", "自然观察", "季节", "season", "秋天", "autumn", 
        "冬季", "winter"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with seasons/nature content
    seasons_nature_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains either seasons keywords OR nature keywords (or both)
            has_seasons_keyword = any(keyword in content for keyword in seasons_keywords)
            has_nature_keyword = any(keyword in content for keyword in nature_keywords)
            
            if has_seasons_keyword or has_nature_keyword:
                seasons_nature_post = post
                break

    if seasons_nature_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing seasons/nature content")

    # Verify post has ≥1 nature-related hashtag
    has_nature_hashtag = False
    if seasons_nature_post:
        hashtags = seasons_nature_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in nature_hashtag_keywords):
                    has_nature_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_nature_hashtag:
            content = seasons_nature_post.get("content", "") or ""
            if "#" in content:
                for keyword in nature_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_nature_hashtag = True
                        break
        
        if has_nature_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 nature-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: seasons/nature post not found")

    if all(checks_passed):
        return 1.0, "All seasons/nature post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some seasons/nature post checks failed"


# -----------------------------------------------------------------------------
# Task: Gaming Group Setup
# -----------------------------------------------------------------------------

def _validate_gaming_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for gaming group setup task.
    
    Checks:
    - Backend: Custom group with gaming-related name exists
    - Backend: ≥2 gaming/esports accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Gaming group name keywords
    gaming_group_keywords = [
        "游戏", "gaming", "电竞", "esports", "游戏资讯", "游戏分享", "电竞资讯", "游戏社区"
    ]
    
    # Gaming/esports content keywords
    gaming_keywords = [
        "游戏", "gaming", "电竞", "esports", "游戏资讯", "游戏分享", "电竞资讯", "游戏社区", 
        "游戏攻略", "游戏推荐", "电竞比赛", "游戏直播", "游戏评测"
    ]

    # Query customGroups collection for gaming-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find gaming-related group
    gaming_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in gaming_group_keywords):
                    gaming_group_id = g.get("_id")
                    break
    
    if gaming_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with gaming-related name not found")

    # Query userFollows collection for accounts assigned to group
    gaming_accounts = []
    if gaming_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": gaming_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify gaming content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for gaming content
            has_gaming_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in gaming_keywords):
                        has_gaming_content = True
                        break
            
            if has_gaming_content:
                gaming_accounts.append(account_id)
        
        # Verify ≥2 accounts have gaming/esports content
        if len(gaming_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 gaming/esports accounts assigned to group, found {len(gaming_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify gaming accounts: gaming group not found")

    if all(checks_passed):
        return 1.0, "All gaming group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some gaming group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Trending Topic with High Engagement
# -----------------------------------------------------------------------------

def _validate_trending_topic_high_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for trending topic with high engagement task.
    
    Checks:
    - Frontend: Current screen shows trending topic
    - Frontend: Trending topic has high engagement count (>100k)
    """
    messages: list[str] = []
    checks_passed = []

    # Controversy keywords
    controversy_keywords = [
        "争议", "controversy", "讨论", "discussion", "热议", "热点", "热门", 
        "讨论度", "争议话题", "热门话题"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    if current_view in ["trending", "search"]:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )
        return 0.0, "; ".join(messages)

    # Verify trending topic has high engagement count (>100k)
    trending_topics = final_state_frontend.get("trendingTopics") or []
    has_high_engagement = False
    
    if isinstance(trending_topics, list):
        for topic in trending_topics:
            if isinstance(topic, dict):
                # Check the 'count' field (stored as string in frontend)
                count_str = topic.get("count", "")
                if count_str:
                    try:
                        count = int(count_str)
                        if count > 100000:
                            has_high_engagement = True
                            break
                    except (ValueError, TypeError):
                        pass
    
    if has_high_engagement:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected trending topic to have high engagement count (>100k)"
        )
        return 0.0, "; ".join(messages)

    if all(checks_passed):
        return 1.0, "All trending topic high engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some trending topic high engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Environment/Sustainability Post
# -----------------------------------------------------------------------------

def _validate_environment_sustainability_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for environment/sustainability post task.
    
    Checks:
    - Backend: New post exists about environment/sustainability with ≥1 environmental hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Environment keywords
    environment_keywords = [
        "环境", "environment", "环保", "环保意识", "可持续发展", "sustainability", 
        "绿色生活", "green living", "环保生活", "生态", "ecology", "环保建议", 
        "环保贴士", "绿色环保"
    ]
    
    # Environmental hashtag keywords
    environmental_hashtag_keywords = [
        "环境", "environment", "环保", "环保意识", "可持续发展", "sustainability", 
        "绿色生活", "green living", "环保生活", "生态", "ecology"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with environment/sustainability content
    environment_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains environment keywords
            if any(keyword in content for keyword in environment_keywords):
                environment_post = post
                break

    if environment_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing environment/sustainability content")

    # Verify post has ≥1 environmental hashtag
    has_environmental_hashtag = False
    if environment_post:
        hashtags = environment_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in environmental_hashtag_keywords):
                    has_environmental_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_environmental_hashtag:
            content = environment_post.get("content", "") or ""
            if "#" in content:
                for keyword in environmental_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_environmental_hashtag = True
                        break
        
        if has_environmental_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 environmental hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: environment post not found")

    if all(checks_passed):
        return 1.0, "All environment/sustainability post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some environment/sustainability post checks failed"


# -----------------------------------------------------------------------------
# Task: Unfollow Accounts
# -----------------------------------------------------------------------------

def _validate_unfollow_accounts(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for unfollow accounts task.
    
    Checks:
    - Backend: ≥2 accounts unfollowed from following list
    
    Initial state: exactly 5 users followed
    Final state should have: ≤3 users followed
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"

    # Query userFollows collection for all followed accounts
    user_follows_result = backend.query({"collection": "userFollows", "filter": {}})
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []

    # Count total followed accounts in final state
    final_count = len(user_follows) if isinstance(user_follows, list) else 0

    # Verify ≥2 accounts were unfollowed
    # Initial state: exactly 5 users followed
    # Final state: should have ≤3 users followed (since 5 - 2 = 3)
    if final_count <= 3:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≤3 users followed (≥2 unfollowed from initial 5), found {final_count}"
        )

    if all(checks_passed):
        return 1.0, "All unfollow accounts checks passed"
    return 0.0, "; ".join(messages) if messages else "Some unfollow accounts checks failed"


# -----------------------------------------------------------------------------
# Task: Sports Trending Engagement
# -----------------------------------------------------------------------------

def _validate_sports_trending_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for sports trending engagement task.
    
    Checks:
    - Frontend: Current screen shows trending topic with sports content
    - Backend: ≥1 sports post liked or commented within trending sports content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Sports keywords
    sports_keywords = [
        "体育", "sports", "运动", "比赛", "game", "球员", "player", "球队", "team", 
        "体育新闻", "体育资讯", "体育比赛", "体育赛事", "体育报道"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_sports_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in sports_keywords):
                    has_sports_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have sports content
        if not has_sports_topic and search_query:
            if any(keyword in search_query for keyword in sports_keywords):
                has_sports_topic = True
        
        if has_sports_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain sports keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Backend checks: Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are liked OR commented
    liked_or_commented_post_ids = liked_post_ids | commented_post_ids

    # Query posts collection and verify sports content
    sports_posts_engaged = []
    for post_id in liked_or_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains sports keywords
                if any(keyword in content for keyword in sports_keywords):
                    sports_posts_engaged.append(post_id)

    # Verify ≥1 sports post is liked or commented
    if len(sports_posts_engaged) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 sports post to be liked or commented, found {len(sports_posts_engaged)}"
        )

    if all(checks_passed):
        return 1.0, "All sports trending engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some sports trending engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Work-Life Balance Post
# -----------------------------------------------------------------------------

def _validate_work_life_balance_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for work-life balance post task.
    
    Checks:
    - Backend: New post exists about work/career topics with ≥1 business-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Work/career keywords
    work_career_keywords = [
        "工作", "work", "职业", "career", "职场", "职场生活", "工作生活", "职业发展", 
        "工作平衡", "工作心得", "职场心得", "职业规划", "工作分享", "职场分享"
    ]
    
    # Business hashtag keywords
    business_hashtag_keywords = [
        "工作", "work", "职业", "career", "职场", "职场生活", "工作生活", "职业发展", 
        "工作平衡", "商业", "business", "职场心得", "职业规划"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with work/career content
    work_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains work/career keywords
            if any(keyword in content for keyword in work_career_keywords):
                work_post = post
                break

    if work_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing work/career content")

    # Verify post has ≥1 business-related hashtag
    has_business_hashtag = False
    if work_post:
        hashtags = work_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in business_hashtag_keywords):
                    has_business_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_business_hashtag:
            content = work_post.get("content", "") or ""
            if "#" in content:
                for keyword in business_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_business_hashtag = True
                        break
        
        if has_business_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 business-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: work/career post not found")

    if all(checks_passed):
        return 1.0, "All work-life balance post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some work-life balance post checks failed"


# -----------------------------------------------------------------------------
# Task: Art/Design Group Setup
# -----------------------------------------------------------------------------

def _validate_art_design_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for art/design group setup task.
    
    Checks:
    - Backend: Custom group with art/design-related name exists
    - Backend: ≥2 art/design accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Art/design group name keywords
    art_design_group_keywords = [
        "艺术", "art", "设计", "design", "艺术创作", "设计作品", "艺术分享", "设计分享", 
        "艺术社区", "设计社区"
    ]
    
    # Art/design content keywords
    art_design_keywords = [
        "艺术", "art", "设计", "design", "艺术创作", "设计作品", "艺术分享", "设计分享", 
        "艺术社区", "设计社区", "艺术作品", "设计灵感", "艺术欣赏", "设计理念", "艺术风格", 
        "设计风格"
    ]

    # Query customGroups collection for art/design-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find art/design-related group
    art_design_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in art_design_group_keywords):
                    art_design_group_id = g.get("_id")
                    break
    
    if art_design_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with art/design-related name not found")

    # Query userFollows collection for accounts assigned to group
    art_design_accounts = []
    if art_design_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": art_design_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify art/design content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for art/design content
            has_art_design_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in art_design_keywords):
                        has_art_design_content = True
                        break
            
            if has_art_design_content:
                art_design_accounts.append(account_id)
        
        # Verify ≥2 accounts have art/design content
        if len(art_design_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 art/design accounts assigned to group, found {len(art_design_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify art/design accounts: art/design group not found")

    if all(checks_passed):
        return 1.0, "All art/design group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some art/design group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Fashion Trending Likes
# -----------------------------------------------------------------------------

def _validate_fashion_trending_likes(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for fashion trending likes task.
    
    Checks:
    - Frontend: Current screen shows trending topic with fashion content
    - Backend: ≥2 fashion/style posts liked within trending fashion content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Fashion/style keywords
    fashion_keywords = [
        "时尚", "fashion", "风格", "style", "穿搭", "outfit", "服装", "clothing", 
        "时尚搭配", "时尚风格", "时尚潮流", "时尚分享", "穿搭分享", "时尚资讯", "时尚趋势"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_fashion_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in fashion_keywords):
                    has_fashion_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have fashion content
        if not has_fashion_topic and search_query:
            if any(keyword in search_query for keyword in fashion_keywords):
                has_fashion_topic = True
        
        if has_fashion_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain fashion keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: list[str] = []
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.append(post_id)

    # Query posts collection for liked posts and verify fashion content
    fashion_posts_liked = []
    for post_id in liked_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains fashion keywords
                if any(keyword in content for keyword in fashion_keywords):
                    fashion_posts_liked.append(post_id)

    # Verify ≥2 fashion/style posts are liked
    if len(fashion_posts_liked) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 fashion/style posts to be liked, found {len(fashion_posts_liked)}"
        )

    if all(checks_passed):
        return 1.0, "All fashion trending likes checks passed"
    return 0.0, "; ".join(messages) if messages else "Some fashion trending likes checks failed"


# -----------------------------------------------------------------------------
# Task: Philosophical/Life Reflection Post
# -----------------------------------------------------------------------------

def _validate_philosophical_reflection_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for philosophical/life reflection post task.
    
    Checks:
    - Backend: New post exists with philosophical/life reflection content and ≥1 relevant hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Philosophical/life reflection keywords
    philosophical_keywords = [
        "哲学", "philosophy", "思考", "reflection", "人生", "life", "生活感悟", "人生感悟", 
        "人生思考", "生活思考", "人生哲学", "生活哲学", "成长", "growth", "个人成长", 
        "自我成长"
    ]
    
    # Relevant hashtag keywords
    relevant_hashtag_keywords = [
        "哲学", "philosophy", "思考", "reflection", "人生", "life", "生活感悟", "人生感悟", 
        "人生思考", "生活思考", "人生哲学", "生活哲学", "成长", "growth", "个人成长", 
        "自我成长"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with philosophical/life reflection content
    philosophical_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains philosophical/life reflection keywords
            if any(keyword in content for keyword in philosophical_keywords):
                philosophical_post = post
                break

    if philosophical_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing philosophical/life reflection content")

    # Verify post has ≥1 relevant hashtag
    has_relevant_hashtag = False
    if philosophical_post:
        hashtags = philosophical_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in relevant_hashtag_keywords):
                    has_relevant_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_relevant_hashtag:
            content = philosophical_post.get("content", "") or ""
            if "#" in content:
                for keyword in relevant_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_relevant_hashtag = True
                        break
        
        if has_relevant_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 relevant hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: philosophical post not found")

    if all(checks_passed):
        return 1.0, "All philosophical/life reflection post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some philosophical/life reflection post checks failed"


# -----------------------------------------------------------------------------
# Task: Health/Wellness Accounts Follow from Search
# -----------------------------------------------------------------------------

def _validate_health_wellness_accounts_follow(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for health/wellness accounts follow from search task.
    
    Checks:
    - Frontend: Search was performed
    - Backend: ≥2 health/wellness accounts followed from search results (with practical tips)
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Health/wellness search keywords
    health_search_keywords = [
        "健康", "health", "wellness", "健康生活", "健康分享", "健康建议", "健康贴士", "健康资讯"
    ]
    
    # Health/wellness keywords
    health_keywords = [
        "健康", "health", "wellness", "健康生活", "健康分享", "健康建议", "健康贴士", 
        "健康资讯", "健康饮食", "健康运动", "健康习惯", "健康管理", "健康知识", "健康养生"
    ]
    
    # Health tips keywords (to distinguish from gym selfies or product promotion)
    health_tips_keywords = [
        "健康建议", "健康贴士", "健康知识", "健康养生", "健康管理", "健康习惯", 
        "实用", "practical", "实用建议", "实用贴士"
    ]

    # Frontend checks: Verify search was performed
    search_query = final_state_frontend.get("searchQuery", "") or ""
    current_view = final_state_frontend.get("currentView", "")
    
    search_performed = False
    if current_view == "search":
        search_performed = True
    elif search_query:
        if any(keyword in search_query for keyword in health_search_keywords):
            search_performed = True
    
    if search_performed:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            "Expected search to be performed (currentView='search' or searchQuery contains health/wellness keywords)"
        )

    # Backend checks: Query userFollows collection for followed accounts
    user_follows_result = backend.query({"collection": "userFollows", "filter": {}})
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []
    
    # Extract account IDs
    followed_account_ids: list[str] = []
    if isinstance(user_follows, list):
        for f in user_follows:
            if isinstance(f, dict):
                followed_uid = f.get("followedUserId")
                if followed_uid:
                    followed_account_ids.append(followed_uid)

    # Query posts collection for followed accounts and verify health/wellness content with practical tips
    health_wellness_accounts = []
    for account_id in followed_account_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"user._id": account_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        # Check recent posts for health/wellness content with practical tips
        has_health_content = False
        has_health_tips = False
        if isinstance(posts, list):
            for post in posts[:10]:  # Check last 10 posts
                if not isinstance(post, dict):
                    continue
                content = post.get("content", "") or ""
                
                if any(keyword in content for keyword in health_keywords):
                    has_health_content = True
                    # Check for health tips keywords (to distinguish from gym selfies or product promotion)
                    if any(keyword in content for keyword in health_tips_keywords):
                        has_health_tips = True
                        break
        
        if has_health_content and has_health_tips:
            health_wellness_accounts.append(account_id)

    # Verify ≥2 accounts have health/wellness content with practical tips
    if len(health_wellness_accounts) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 health/wellness accounts followed (with practical tips), found {len(health_wellness_accounts)}"
        )

    if all(checks_passed):
        return 1.0, "All health/wellness accounts follow from search checks passed"
    return 0.0, "; ".join(messages) if messages else "Some health/wellness accounts follow from search checks failed"


# -----------------------------------------------------------------------------
# Task: Tech Trending Comment
# -----------------------------------------------------------------------------

def _validate_tech_trending_comment(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for tech trending comment task.
    
    Checks:
    - Frontend: Current screen shows trending topic with tech content
    - Backend: ≥1 comment exists on tech-related posts within trending technology content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Tech keywords
    tech_keywords = [
        "科技", "技术", "tech", "technology", "创新", "innovation", "科技新闻", "技术创新", 
        "科技资讯", "科技产品", "科技趋势", "科技发展", "科技创新"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_tech_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in tech_keywords):
                    has_tech_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have tech content
        if not has_tech_topic and search_query:
            if any(keyword in search_query for keyword in tech_keywords):
                has_tech_topic = True
        
        if has_tech_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain tech keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: list[str] = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.append(post_id)

    # Query posts collection for commented posts and verify tech content
    tech_posts_commented = []
    for post_id in commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains tech keywords
                if any(keyword in content for keyword in tech_keywords):
                    tech_posts_commented.append(post_id)

    # Verify ≥1 comment exists on tech-related posts
    if len(tech_posts_commented) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 comment on tech-related posts, found {len(tech_posts_commented)}"
        )

    if all(checks_passed):
        return 1.0, "All tech trending comment checks passed"
    return 0.0, "; ".join(messages) if messages else "Some tech trending comment checks failed"


# -----------------------------------------------------------------------------
# Task: Childhood Nostalgia Post
# -----------------------------------------------------------------------------

def _validate_childhood_nostalgia_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for childhood nostalgia post task.
    
    Checks:
    - Backend: New post exists about childhood/nostalgia with ≥1 memory-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Childhood/nostalgia keywords
    childhood_nostalgia_keywords = [
        "童年", "childhood", "回忆", "memory", "怀旧", "nostalgia", "童年回忆", "童年记忆", 
        "童年时光", "童年往事", "童年趣事", "童年故事"
    ]
    
    # Memory-related hashtag keywords
    memory_hashtag_keywords = [
        "童年", "childhood", "回忆", "memory", "怀旧", "nostalgia", "童年回忆", "童年记忆", 
        "童年时光", "童年往事", "童年趣事", "童年故事", "回忆录", "记忆"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with childhood/nostalgia content
    childhood_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains childhood/nostalgia keywords
            if any(keyword in content for keyword in childhood_nostalgia_keywords):
                childhood_post = post
                break

    if childhood_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing childhood/nostalgia content")

    # Verify post has ≥1 memory-related hashtag
    has_memory_hashtag = False
    if childhood_post:
        hashtags = childhood_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in memory_hashtag_keywords):
                    has_memory_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_memory_hashtag:
            content = childhood_post.get("content", "") or ""
            if "#" in content:
                for keyword in memory_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_memory_hashtag = True
                        break
        
        if has_memory_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 memory-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: childhood/nostalgia post not found")

    if all(checks_passed):
        return 1.0, "All childhood nostalgia post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some childhood nostalgia post checks failed"


# -----------------------------------------------------------------------------
# Task: Comedy/Humor Group Setup
# -----------------------------------------------------------------------------

def _validate_comedy_humor_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for comedy/humor group setup task.
    
    Checks:
    - Backend: Custom group with humor-related name exists
    - Backend: ≥2 comedy/humor accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Humor group name keywords
    humor_group_keywords = [
        "幽默", "humor", "喜剧", "comedy", "搞笑", "funny", "幽默分享", "喜剧分享", 
        "搞笑内容", "幽默内容"
    ]
    
    # Comedy/humor content keywords
    comedy_humor_keywords = [
        "幽默", "humor", "喜剧", "comedy", "搞笑", "funny", "幽默分享", "喜剧分享", 
        "搞笑内容", "幽默内容", "笑话", "joke", "段子", "搞笑段子", "幽默段子", "喜剧段子"
    ]

    # Query customGroups collection for humor-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find humor-related group
    humor_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in humor_group_keywords):
                    humor_group_id = g.get("_id")
                    break
    
    if humor_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with humor-related name not found")

    # Query userFollows collection for accounts assigned to group
    comedy_humor_accounts = []
    if humor_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": humor_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify comedy/humor content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for comedy/humor content
            has_comedy_humor_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in comedy_humor_keywords):
                        has_comedy_humor_content = True
                        break
            
            if has_comedy_humor_content:
                comedy_humor_accounts.append(account_id)
        
        # Verify ≥2 accounts have comedy/humor content
        if len(comedy_humor_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 comedy/humor accounts assigned to group, found {len(comedy_humor_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify comedy/humor accounts: humor group not found")

    if all(checks_passed):
        return 1.0, "All comedy/humor group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some comedy/humor group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Local/Regional Engagement
# -----------------------------------------------------------------------------

def _validate_local_regional_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for local/regional engagement task.
    
    Checks:
    - Backend: ≥1 local/regional post liked or commented
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Local/regional keywords
    local_regional_keywords = [
        "本地", "local", "地区", "region", "城市", "city", "社区", "community", 
        "本地新闻", "本地资讯", "本地活动", "本地事件", "地区新闻", "地区资讯", 
        "城市新闻", "城市资讯", "社区活动", "社区新闻"
    ]

    # Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are liked OR commented
    liked_or_commented_post_ids = liked_post_ids | commented_post_ids

    # Query posts collection and verify local/regional content
    local_regional_posts_engaged = []
    for post_id in liked_or_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains local/regional keywords
                if any(keyword in content for keyword in local_regional_keywords):
                    local_regional_posts_engaged.append(post_id)

    # Verify ≥1 local/regional post is liked or commented
    if len(local_regional_posts_engaged) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 local/regional post to be liked or commented, found {len(local_regional_posts_engaged)}"
        )

    if all(checks_passed):
        return 1.0, "All local/regional engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some local/regional engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Cooking/Recipe Post
# -----------------------------------------------------------------------------

def _validate_cooking_recipe_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for cooking/recipe post task.
    
    Checks:
    - Backend: New post exists about cooking/recipe with ≥1 food-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Cooking/recipe keywords
    cooking_recipe_keywords = [
        "烹饪", "cooking", "食谱", "recipe", "做菜", "料理", "美食", "food", 
        "烹饪分享", "食谱分享", "做菜分享", "料理分享", "美食制作", "美食烹饪", 
        "烹饪技巧", "做菜技巧", "料理技巧"
    ]
    
    # Food-related hashtag keywords
    food_hashtag_keywords = [
        "烹饪", "cooking", "食谱", "recipe", "做菜", "料理", "美食", "food", 
        "烹饪分享", "食谱分享", "做菜分享", "料理分享", "美食制作", "美食烹饪", 
        "美食", "食物", "food"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with cooking/recipe content
    cooking_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains cooking/recipe keywords
            if any(keyword in content for keyword in cooking_recipe_keywords):
                cooking_post = post
                break

    if cooking_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing cooking/recipe content")

    # Verify post has ≥1 food-related hashtag
    has_food_hashtag = False
    if cooking_post:
        hashtags = cooking_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in food_hashtag_keywords):
                    has_food_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_food_hashtag:
            content = cooking_post.get("content", "") or ""
            if "#" in content:
                for keyword in food_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_food_hashtag = True
                        break
        
        if has_food_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 food-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: cooking/recipe post not found")

    if all(checks_passed):
        return 1.0, "All cooking/recipe post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some cooking/recipe post checks failed"


# -----------------------------------------------------------------------------
# Task: Professional Account Follow and Special Attention
# -----------------------------------------------------------------------------

def _validate_professional_account_special_attention(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for professional account follow and Special Attention task.
    
    Checks:
    - Backend: ≥1 professional/industry account followed and added to Special Attention
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Professional/industry keywords
    professional_keywords = [
        "行业", "industry", "专业", "professional", "职业", "career", "行业新闻", 
        "行业资讯", "行业动态", "专业资讯", "专业分享", "行业分析", "行业趋势", 
        "行业报告", "专业观点", "行业观点"
    ]

    # Query userFollows collection for Special Attention accounts
    user_follows_result = backend.query({
        "collection": "userFollows",
        "filter": {"isSpecialAttention": True}
    })
    user_follows = user_follows_result if isinstance(user_follows_result, list) else []
    
    # Extract account IDs
    special_attention_account_ids: list[str] = []
    if isinstance(user_follows, list):
        for f in user_follows:
            if isinstance(f, dict):
                followed_uid = f.get("followedUserId")
                if followed_uid:
                    special_attention_account_ids.append(followed_uid)

    # Query posts collection for Special Attention accounts and verify professional/industry content
    professional_accounts = []
    for account_id in special_attention_account_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"user._id": account_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        # Check recent posts for professional/industry content
        has_professional_content = False
        if isinstance(posts, list):
            for post in posts[:10]:  # Check last 10 posts
                if not isinstance(post, dict):
                    continue
                content = post.get("content", "") or ""
                if any(keyword in content for keyword in professional_keywords):
                    has_professional_content = True
                    break
        
        if has_professional_content:
            professional_accounts.append(account_id)

    # Verify ≥1 professional/industry account is in Special Attention
    if len(professional_accounts) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 professional/industry account in Special Attention, found {len(professional_accounts)}"
        )

    if all(checks_passed):
        return 1.0, "All professional account special attention checks passed"
    return 0.0, "; ".join(messages) if messages else "Some professional account special attention checks failed"


# -----------------------------------------------------------------------------
# Task: Pet Posts Liked and Commented
# -----------------------------------------------------------------------------

def _validate_pet_posts_liked_and_commented(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for pet posts liked and commented task.
    
    Checks:
    - Backend: ≥2 pet-related posts liked and commented
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Pet-related keywords
    pet_keywords = [
        "宠物", "pet", "猫", "cat", "狗", "dog", "宠物分享", "宠物日常", "宠物生活", 
        "宠物照片", "宠物视频", "宠物故事", "宠物趣事", "萌宠", "可爱宠物"
    ]

    # Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are both liked AND commented
    liked_and_commented_post_ids = liked_post_ids & commented_post_ids

    # Query posts collection and verify pet content
    pet_posts_liked_and_commented = []
    for post_id in liked_and_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains pet keywords
                if any(keyword in content for keyword in pet_keywords):
                    pet_posts_liked_and_commented.append(post_id)

    # Verify ≥2 pet-related posts are both liked and commented
    if len(pet_posts_liked_and_commented) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 pet-related posts to be liked and commented, found {len(pet_posts_liked_and_commented)}"
        )

    if all(checks_passed):
        return 1.0, "All pet posts liked and commented checks passed"
    return 0.0, "; ".join(messages) if messages else "Some pet posts liked and commented checks failed"


# -----------------------------------------------------------------------------
# Task: Learning/Education Post
# -----------------------------------------------------------------------------

def _validate_learning_education_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for learning/education post task.
    
    Checks:
    - Backend: New post exists about learning/education with ≥1 learning-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Learning/education keywords
    learning_keywords = [
        "学习", "learning", "教育", "education", "知识", "knowledge", "学习分享", 
        "教育分享", "学习心得", "学习经验", "学习感悟", "学习收获", "知识分享", 
        "教育资讯", "学习资讯"
    ]
    
    # Learning-related hashtag keywords
    learning_hashtag_keywords = [
        "学习", "learning", "教育", "education", "知识", "knowledge", "学习分享", 
        "教育分享", "学习心得", "学习经验", "学习感悟", "学习收获", "知识分享", "教育"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with learning/education content
    learning_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains learning/education keywords
            if any(keyword in content for keyword in learning_keywords):
                learning_post = post
                break

    if learning_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing learning/education content")

    # Verify post has ≥1 learning-related hashtag
    has_learning_hashtag = False
    if learning_post:
        hashtags = learning_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in learning_hashtag_keywords):
                    has_learning_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_learning_hashtag:
            content = learning_post.get("content", "") or ""
            if "#" in content:
                for keyword in learning_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_learning_hashtag = True
                        break
        
        if has_learning_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 learning-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: learning/education post not found")

    if all(checks_passed):
        return 1.0, "All learning/education post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some learning/education post checks failed"


# -----------------------------------------------------------------------------
# Task: Science Group Setup
# -----------------------------------------------------------------------------

def _validate_science_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for science group setup task.
    
    Checks:
    - Backend: Custom group with science-related name exists
    - Backend: ≥2 science accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Science group name keywords
    science_group_keywords = [
        "科学", "science", "科普", "科学传播", "科学资讯", "科学分享", "科普分享", "科学社区"
    ]
    
    # Science content keywords
    science_keywords = [
        "科学", "science", "科普", "科学传播", "科学资讯", "科学分享", "科普分享", "科学社区", 
        "科学研究", "科学发现", "科学知识", "科普知识", "科学教育", "科普教育", "科学新闻", 
        "科普新闻"
    ]

    # Query customGroups collection for science-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find science-related group
    science_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in science_group_keywords):
                    science_group_id = g.get("_id")
                    break
    
    if science_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with science-related name not found")

    # Query userFollows collection for accounts assigned to group
    science_accounts = []
    if science_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": science_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify science content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for science content
            has_science_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in science_keywords):
                        has_science_content = True
                        break
            
            if has_science_content:
                science_accounts.append(account_id)
        
        # Verify ≥2 accounts have science content
        if len(science_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 science accounts assigned to group, found {len(science_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify science accounts: science group not found")

    if all(checks_passed):
        return 1.0, "All science group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some science group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Cultural/Event Engagement
# -----------------------------------------------------------------------------

def _validate_cultural_event_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for cultural/event engagement task.
    
    Checks:
    - Frontend: Current screen shows trending topic with cultural content
    - Backend: ≥1 cultural/event post liked or commented within trending cultural content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Cultural/event keywords
    cultural_keywords = [
        "文化", "culture", "活动", "event", "节日", "festival", "展览", "exhibition", 
        "文化活动", "文化事件", "文化节", "文化展", "文化节庆", "文化庆典", "文化展览"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_cultural_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in cultural_keywords):
                    has_cultural_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have cultural content
        if not has_cultural_topic and search_query:
            if any(keyword in search_query for keyword in cultural_keywords):
                has_cultural_topic = True
        
        if has_cultural_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain cultural keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are liked OR commented
    liked_or_commented_post_ids = liked_post_ids | commented_post_ids

    # Query posts collection and verify cultural/event content
    cultural_posts_engaged = []
    for post_id in liked_or_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains cultural/event keywords
                if any(keyword in content for keyword in cultural_keywords):
                    cultural_posts_engaged.append(post_id)

    # Verify ≥1 cultural/event post is liked or commented
    if len(cultural_posts_engaged) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 cultural/event post to be liked or commented, found {len(cultural_posts_engaged)}"
        )

    if all(checks_passed):
        return 1.0, "All cultural/event engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some cultural/event engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Positive/Motivational Post
# -----------------------------------------------------------------------------

def _validate_positive_motivational_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for positive/motivational post task.
    
    Checks:
    - Backend: New post exists with positive/motivational content and ≥1 inspirational hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Positive/motivational keywords
    positive_motivational_keywords = [
        "感恩", "gratitude", "激励", "motivation", "正能量", "positive", "积极", "inspiration", 
        "励志", "鼓励", "加油", "努力", "坚持", "梦想", "希望", "积极向上", "励志分享", 
        "正能量分享", "激励分享"
    ]
    
    # Inspirational hashtag keywords
    inspirational_hashtag_keywords = [
        "感恩", "gratitude", "激励", "motivation", "正能量", "positive", "积极", "inspiration", 
        "励志", "鼓励", "加油", "努力", "坚持", "梦想", "希望", "积极向上", "励志"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with positive/motivational content
    positive_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains positive/motivational keywords
            if any(keyword in content for keyword in positive_motivational_keywords):
                positive_post = post
                break

    if positive_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing positive/motivational content")

    # Verify post has ≥1 inspirational hashtag
    has_inspirational_hashtag = False
    if positive_post:
        hashtags = positive_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in inspirational_hashtag_keywords):
                    has_inspirational_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_inspirational_hashtag:
            content = positive_post.get("content", "") or ""
            if "#" in content:
                for keyword in inspirational_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_inspirational_hashtag = True
                        break
        
        if has_inspirational_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 inspirational hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: positive/motivational post not found")

    if all(checks_passed):
        return 1.0, "All positive/motivational post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some positive/motivational post checks failed"


# -----------------------------------------------------------------------------
# Task: History/Documentary Group Setup
# -----------------------------------------------------------------------------

def _validate_history_documentary_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for history/documentary group setup task.
    
    Checks:
    - Backend: Custom group with educational/history-related name exists
    - Backend: ≥2 history/documentary accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Educational/history group name keywords
    educational_history_group_keywords = [
        "历史", "history", "教育", "education", "纪录片", "documentary", "历史教育", 
        "历史分享", "纪录片分享", "历史资讯", "教育内容", "历史内容"
    ]
    
    # History/documentary content keywords
    history_documentary_keywords = [
        "历史", "history", "教育", "education", "纪录片", "documentary", "历史教育", 
        "历史分享", "纪录片分享", "历史资讯", "教育内容", "历史内容", "历史故事", 
        "历史事件", "历史人物", "历史知识", "纪录片推荐", "历史纪录片"
    ]

    # Query customGroups collection for educational/history-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find educational/history-related group
    history_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in educational_history_group_keywords):
                    history_group_id = g.get("_id")
                    break
    
    if history_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with educational/history-related name not found")

    # Query userFollows collection for accounts assigned to group
    history_documentary_accounts = []
    if history_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": history_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify history/documentary content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for history/documentary content
            has_history_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in history_documentary_keywords):
                        has_history_content = True
                        break
            
            if has_history_content:
                history_documentary_accounts.append(account_id)
        
        # Verify ≥2 accounts have history/documentary content
        if len(history_documentary_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 history/documentary accounts assigned to group, found {len(history_documentary_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify history/documentary accounts: educational/history group not found")

    if all(checks_passed):
        return 1.0, "All history/documentary group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some history/documentary group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Entertainment Trending Likes
# -----------------------------------------------------------------------------

def _validate_entertainment_trending_likes(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for entertainment trending likes task.
    
    Checks:
    - Frontend: Current screen shows trending topic with entertainment content
    - Backend: ≥2 entertainment posts liked within trending entertainment content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Entertainment keywords
    entertainment_keywords = [
        "娱乐", "entertainment", "明星", "celebrity", "电影", "movie", "影视", "影视剧", 
        "娱乐新闻", "娱乐资讯", "明星动态", "电影资讯", "影视资讯", "娱乐八卦", "明星八卦", 
        "电影推荐", "影视推荐"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_entertainment_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in entertainment_keywords):
                    has_entertainment_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have entertainment content
        if not has_entertainment_topic and search_query:
            if any(keyword in search_query for keyword in entertainment_keywords):
                has_entertainment_topic = True
        
        if has_entertainment_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain entertainment keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: list[str] = []
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.append(post_id)

    # Query posts collection for liked posts and verify entertainment content
    entertainment_posts_liked = []
    for post_id in liked_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains entertainment keywords
                if any(keyword in content for keyword in entertainment_keywords):
                    entertainment_posts_liked.append(post_id)

    # Verify ≥2 entertainment posts are liked
    if len(entertainment_posts_liked) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 entertainment posts to be liked, found {len(entertainment_posts_liked)}"
        )

    if all(checks_passed):
        return 1.0, "All entertainment trending likes checks passed"
    return 0.0, "; ".join(messages) if messages else "Some entertainment trending likes checks failed"


# -----------------------------------------------------------------------------
# Task: Minimalism/Simple Living Post
# -----------------------------------------------------------------------------

def _validate_minimalism_simple_living_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for minimalism/simple living post task.
    
    Checks:
    - Backend: New post exists about minimalism/simple living with ≥1 lifestyle hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Minimalism/simple living keywords
    minimalism_keywords = [
        "极简", "minimalism", "简约", "simple living", "断舍离", "整理", "清理", 
        "极简生活", "简约生活", "简单生活", "极简主义", "简约主义", "整理收纳", 
        "清理物品", "极简分享", "简约分享", "简单生活分享"
    ]
    
    # Lifestyle hashtag keywords
    lifestyle_hashtag_keywords = [
        "极简", "minimalism", "简约", "simple living", "断舍离", "整理", "清理", 
        "极简生活", "简约生活", "简单生活", "极简主义", "简约主义", "生活方式", 
        "lifestyle", "生活", "life"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with minimalism/simple living content
    minimalism_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains minimalism/simple living keywords
            if any(keyword in content for keyword in minimalism_keywords):
                minimalism_post = post
                break

    if minimalism_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing minimalism/simple living content")

    # Verify post has ≥1 lifestyle hashtag
    has_lifestyle_hashtag = False
    if minimalism_post:
        hashtags = minimalism_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in lifestyle_hashtag_keywords):
                    has_lifestyle_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_lifestyle_hashtag:
            content = minimalism_post.get("content", "") or ""
            if "#" in content:
                for keyword in lifestyle_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_lifestyle_hashtag = True
                        break
        
        if has_lifestyle_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 lifestyle hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: minimalism/simple living post not found")

    if all(checks_passed):
        return 1.0, "All minimalism/simple living post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some minimalism/simple living post checks failed"


# -----------------------------------------------------------------------------
# Task: Automotive Group Setup
# -----------------------------------------------------------------------------

def _validate_automotive_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for automotive group setup task.
    
    Checks:
    - Backend: Custom group with automotive-related name exists
    - Backend: ≥1 automotive account followed and assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Automotive group name keywords
    automotive_group_keywords = [
        "汽车", "automotive", "车", "car", "汽车资讯", "汽车分享", "汽车社区", "车友", 
        "汽车爱好者"
    ]
    
    # Automotive content keywords
    automotive_keywords = [
        "汽车", "automotive", "车", "car", "汽车资讯", "汽车分享", "汽车社区", "车友", 
        "汽车爱好者", "汽车评测", "汽车推荐", "汽车新闻", "汽车知识", "汽车保养", 
        "汽车维修", "汽车改装"
    ]

    # Query customGroups collection for automotive-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find automotive-related group
    automotive_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in automotive_group_keywords):
                    automotive_group_id = g.get("_id")
                    break
    
    if automotive_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with automotive-related name not found")

    # Query userFollows collection for accounts assigned to group
    automotive_accounts = []
    if automotive_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": automotive_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify automotive content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for automotive content
            has_automotive_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in automotive_keywords):
                        has_automotive_content = True
                        break
            
            if has_automotive_content:
                automotive_accounts.append(account_id)
        
        # Verify ≥1 account has automotive content
        if len(automotive_accounts) >= 1:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥1 automotive account assigned to group, found {len(automotive_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify automotive accounts: automotive group not found")

    if all(checks_passed):
        return 1.0, "All automotive group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some automotive group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Language Learning Posts Engagement
# -----------------------------------------------------------------------------

def _validate_language_learning_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for language learning posts engagement task.
    
    Checks:
    - Backend: ≥2 language learning posts liked or commented
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Language learning keywords
    language_learning_keywords = [
        "语言", "language", "学习", "learning", "外语", "foreign language", "语言学习", 
        "语言交流", "文化 exchange", "文化交换", "语言教育", "语言培训", "语言课程", 
        "语言学习分享", "语言学习经验", "语言学习技巧", "语言学习心得"
    ]

    # Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are liked OR commented
    liked_or_commented_post_ids = liked_post_ids | commented_post_ids

    # Query posts collection and verify language learning content
    language_learning_posts_engaged = []
    for post_id in liked_or_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains language learning keywords
                if any(keyword in content for keyword in language_learning_keywords):
                    language_learning_posts_engaged.append(post_id)

    # Verify ≥2 language learning posts are liked or commented
    if len(language_learning_posts_engaged) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 language learning posts to be liked or commented, found {len(language_learning_posts_engaged)}"
        )

    if all(checks_passed):
        return 1.0, "All language learning engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some language learning engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Movie/Cinema Post Creation
# -----------------------------------------------------------------------------

def _validate_movie_cinema_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for movie/cinema post task.
    
    Checks:
    - Backend: New post exists about movies/cinema with ≥1 film-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Movie/cinema keywords (limited to 10-20 as requested)
    movie_cinema_keywords = [
        "电影", "movie", "影片", "film", "cinema", "影院", "影评", "电影推荐", 
        "电影评论", "电影分析", "电影观后感", "电影分享", "电影资讯", "电影话题", "电影讨论"
    ]
    
    # Film-related hashtag keywords (same list, limited to 10-20)
    film_hashtag_keywords = [
        "电影", "movie", "影片", "film", "cinema", "影院", "影评", "电影推荐", 
        "电影评论", "电影分析", "电影观后感", "电影分享", "电影资讯", "电影话题", "电影讨论"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with movie/cinema content
    movie_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains movie/cinema keywords
            if any(keyword in content for keyword in movie_cinema_keywords):
                movie_post = post
                break

    if movie_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing movie/cinema content")

    # Verify post has ≥1 film-related hashtag
    has_film_hashtag = False
    if movie_post:
        hashtags = movie_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in film_hashtag_keywords):
                    has_film_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_film_hashtag:
            content = movie_post.get("content", "") or ""
            if "#" in content:
                for keyword in film_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_film_hashtag = True
                        break
        
        if has_film_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 film-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: movie/cinema post not found")

    if all(checks_passed):
        return 1.0, "All movie/cinema post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some movie/cinema post checks failed"


# -----------------------------------------------------------------------------
# Task: Finance Group Setup
# -----------------------------------------------------------------------------

def _validate_finance_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for finance group setup task.
    
    Checks:
    - Backend: Custom group with finance-related name exists
    - Backend: ≥2 finance/investment accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Finance group name keywords
    finance_group_keywords = [
        "金融", "finance", "投资", "investment", "理财", "financial", "金融资讯", 
        "投资分享", "理财分享", "金融教育", "投资教育", "理财教育", "金融分析", "投资分析"
    ]
    
    # Finance/investment content keywords
    finance_investment_keywords = [
        "金融", "finance", "投资", "investment", "理财", "financial", "金融资讯", 
        "投资分享", "理财分享", "金融教育", "投资教育", "理财教育", "金融分析", 
        "投资分析", "股票", "stock", "基金", "fund", "市场", "market", "经济", 
        "economy", "财经", "financial news", "投资建议", "理财建议", "金融知识", 
        "投资知识", "理财知识"
    ]

    # Query customGroups collection for finance-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find finance-related group
    finance_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in finance_group_keywords):
                    finance_group_id = g.get("_id")
                    break
    
    if finance_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with finance-related name not found")

    # Query userFollows collection for accounts assigned to group
    finance_investment_accounts = []
    if finance_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": finance_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify finance/investment content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for finance/investment content
            has_finance_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in finance_investment_keywords):
                        has_finance_content = True
                        break
            
            if has_finance_content:
                finance_investment_accounts.append(account_id)
        
        # Verify ≥2 accounts have finance/investment content
        if len(finance_investment_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 finance/investment accounts assigned to group, found {len(finance_investment_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify finance/investment accounts: finance group not found")

    if all(checks_passed):
        return 1.0, "All finance group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some finance group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Beauty/Skincare Trending Engagement
# -----------------------------------------------------------------------------

def _validate_beauty_skincare_trending_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for beauty/skincare trending engagement task.
    
    Checks:
    - Frontend: Current screen shows trending topic with beauty content
    - Backend: ≥1 beauty/skincare post liked or commented within trending beauty content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Beauty/skincare keywords
    beauty_skincare_keywords = [
        "美容", "beauty", "护肤", "skincare", "美妆", "makeup", "化妆品", "cosmetics", 
        "美容资讯", "护肤分享", "美妆分享", "美容心得", "护肤心得", "美妆心得", 
        "美容推荐", "护肤推荐", "美妆推荐", "产品评价", "product review", "使用心得", 
        "使用体验"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_beauty_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in beauty_skincare_keywords):
                    has_beauty_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have beauty content
        if not has_beauty_topic and search_query:
            if any(keyword in search_query for keyword in beauty_skincare_keywords):
                has_beauty_topic = True
        
        if has_beauty_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain beauty/skincare keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: set[str] = set()
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.add(post_id)

    # Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: set[str] = set()
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.add(post_id)

    # Find posts that are liked OR commented
    liked_or_commented_post_ids = liked_post_ids | commented_post_ids

    # Query posts collection and verify beauty/skincare content
    beauty_skincare_posts_engaged = []
    for post_id in liked_or_commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains beauty/skincare keywords
                if any(keyword in content for keyword in beauty_skincare_keywords):
                    beauty_skincare_posts_engaged.append(post_id)

    # Verify ≥1 beauty/skincare post is liked or commented
    if len(beauty_skincare_posts_engaged) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 beauty/skincare post to be liked or commented, found {len(beauty_skincare_posts_engaged)}"
        )

    if all(checks_passed):
        return 1.0, "All beauty/skincare trending engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some beauty/skincare trending engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Productivity Post Creation
# -----------------------------------------------------------------------------

def _validate_productivity_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for productivity post task.
    
    Checks:
    - Backend: New post exists about productivity/efficiency with ≥1 productivity hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Productivity/efficiency keywords
    productivity_keywords = [
        "效率", "efficiency", "生产力", "productivity", "时间管理", "time management", 
        "工作效率", "work efficiency", "效率提升", "效率方法", "效率技巧", "效率工具", 
        "效率分享", "效率心得", "效率建议", "时间管理技巧", "时间管理方法", "工作效率提升"
    ]
    
    # Productivity hashtag keywords
    productivity_hashtag_keywords = [
        "效率", "efficiency", "生产力", "productivity", "时间管理", "time management", 
        "工作效率", "work efficiency", "效率提升", "效率方法", "效率技巧", "效率工具", 
        "效率分享", "效率心得", "效率建议", "时间管理技巧", "时间管理方法", "工作效率提升"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with productivity/efficiency content
    productivity_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains productivity/efficiency keywords
            if any(keyword in content for keyword in productivity_keywords):
                productivity_post = post
                break

    if productivity_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing productivity/efficiency content")

    # Verify post has ≥1 productivity hashtag
    has_productivity_hashtag = False
    if productivity_post:
        hashtags = productivity_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in productivity_hashtag_keywords):
                    has_productivity_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_productivity_hashtag:
            content = productivity_post.get("content", "") or ""
            if "#" in content:
                for keyword in productivity_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_productivity_hashtag = True
                        break
        
        if has_productivity_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 productivity hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: productivity/efficiency post not found")

    if all(checks_passed):
        return 1.0, "All productivity post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some productivity post checks failed"


# -----------------------------------------------------------------------------
# Task: News Analysis Trending Likes
# -----------------------------------------------------------------------------

def _validate_news_analysis_trending_likes(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for news analysis trending likes task.
    
    Checks:
    - Frontend: Current screen shows trending topic with news content
    - Backend: ≥2 news analysis posts liked within trending news content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # News keywords for trending topic
    news_keywords = [
        "新闻", "news", "时事", "current events", "新闻分析", "新闻评论", "新闻资讯", 
        "时事分析", "时事评论", "新闻观点", "新闻解读", "新闻讨论"
    ]
    
    # News analysis keywords for post content
    news_analysis_keywords = [
        "新闻", "news", "时事", "current events", "新闻分析", "新闻评论", "新闻资讯", 
        "时事分析", "时事评论", "新闻观点", "新闻解读", "新闻讨论", "深度分析", 
        "深度评论", "分析", "评论", "观点", "解读", "讨论", "balanced analysis", 
        "thoughtful commentary"
    ]

    # Frontend checks: Verify current screen shows trending topic
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    
    has_news_topic = False
    if current_view in ["trending", "search"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in news_keywords):
                    has_news_topic = True
                    break
        
        # Check searchQuery if trending topics array doesn't have news content
        if not has_news_topic and search_query:
            if any(keyword in search_query for keyword in news_keywords):
                has_news_topic = True
        
        if has_news_topic:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic or search query to contain news keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending' or 'search', got '{current_view}'"
        )

    # Backend checks: Query userLikes collection for current user's likes
    user_likes_result = backend.query({
        "collection": "userLikes",
        "filter": {"userId": current_user_id}
    })
    user_likes = user_likes_result if isinstance(user_likes_result, list) else []
    
    # Extract post IDs from likes
    liked_post_ids: list[str] = []
    if isinstance(user_likes, list):
        for like in user_likes:
            if isinstance(like, dict):
                post_id = like.get("postId")
                if post_id:
                    liked_post_ids.append(post_id)

    # Query posts collection for liked posts and verify news analysis content
    news_analysis_posts_liked = []
    for post_id in liked_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains news analysis keywords
                if any(keyword in content for keyword in news_analysis_keywords):
                    news_analysis_posts_liked.append(post_id)

    # Verify ≥2 news analysis posts are liked
    if len(news_analysis_posts_liked) >= 2:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥2 news analysis posts to be liked, found {len(news_analysis_posts_liked)}"
        )

    if all(checks_passed):
        return 1.0, "All news analysis trending likes checks passed"
    return 0.0, "; ".join(messages) if messages else "Some news analysis trending likes checks failed"


# -----------------------------------------------------------------------------
# Task: Mental Wellness/Mindfulness Post
# -----------------------------------------------------------------------------

def _validate_mental_wellness_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for mental wellness/mindfulness post task.
    
    Checks:
    - Backend: New post exists about mental wellness/mindfulness with ≥1 wellness hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Mental wellness/mindfulness keywords
    mental_wellness_keywords = [
        "心理健康", "mental wellness", "正念", "mindfulness", "冥想", "meditation", 
        "心理疗愈", "正念练习", "冥想练习", "心理健康分享", "正念分享", "冥想分享", 
        "心理健康心得", "正念心得", "冥想心得", "心理健康建议", "正念建议", "冥想建议", 
        "wellness", "mindfulness techniques"
    ]
    
    # Wellness hashtag keywords
    wellness_hashtag_keywords = [
        "心理健康", "mental wellness", "正念", "mindfulness", "冥想", "meditation", 
        "心理疗愈", "正念练习", "冥想练习", "wellness", "健康", "health"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with mental wellness/mindfulness content
    wellness_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains mental wellness/mindfulness keywords
            if any(keyword in content for keyword in mental_wellness_keywords):
                wellness_post = post
                break

    if wellness_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing mental wellness/mindfulness content")

    # Verify post has ≥1 wellness hashtag
    has_wellness_hashtag = False
    if wellness_post:
        hashtags = wellness_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in wellness_hashtag_keywords):
                    has_wellness_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_wellness_hashtag:
            content = wellness_post.get("content", "") or ""
            if "#" in content:
                for keyword in wellness_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_wellness_hashtag = True
                        break
        
        if has_wellness_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 wellness hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: mental wellness/mindfulness post not found")

    if all(checks_passed):
        return 1.0, "All mental wellness post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some mental wellness post checks failed"


# -----------------------------------------------------------------------------
# Task: Outdoor/Adventure Group Setup
# -----------------------------------------------------------------------------

def _validate_outdoor_adventure_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for outdoor/adventure group setup task.
    
    Checks:
    - Backend: Custom group with outdoor/adventure-related name exists
    - Backend: ≥2 outdoor/adventure accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Outdoor/adventure group name keywords
    outdoor_adventure_group_keywords = [
        "户外", "outdoor", "探险", "adventure", "徒步", "hiking", "露营", "camping", 
        "户外运动", "户外活动", "户外分享", "探险分享", "户外爱好者", "户外社区"
    ]
    
    # Outdoor/adventure content keywords
    outdoor_adventure_keywords = [
        "户外", "outdoor", "探险", "adventure", "徒步", "hiking", "露营", "camping", 
        "户外运动", "户外活动", "户外分享", "探险分享", "户外爱好者", "户外社区", 
        "登山", "mountain climbing", "攀岩", "rock climbing", "自然", "nature", 
        "大自然", "户外装备", "户外技巧", "户外经验"
    ]

    # Query customGroups collection for outdoor/adventure-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find outdoor/adventure-related group
    outdoor_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in outdoor_adventure_group_keywords):
                    outdoor_group_id = g.get("_id")
                    break
    
    if outdoor_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with outdoor/adventure-related name not found")

    # Query userFollows collection for accounts assigned to group
    outdoor_adventure_accounts = []
    if outdoor_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": outdoor_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify outdoor/adventure content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for outdoor/adventure content
            has_outdoor_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in outdoor_adventure_keywords):
                        has_outdoor_content = True
                        break
            
            if has_outdoor_content:
                outdoor_adventure_accounts.append(account_id)
        
        # Verify ≥2 accounts have outdoor/adventure content
        if len(outdoor_adventure_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 outdoor/adventure accounts assigned to group, found {len(outdoor_adventure_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify outdoor/adventure accounts: outdoor/adventure group not found")

    if all(checks_passed):
        return 1.0, "All outdoor/adventure group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some outdoor/adventure group setup checks failed"


# -----------------------------------------------------------------------------
# Task: Startup/Entrepreneur Comment Engagement
# -----------------------------------------------------------------------------

def _validate_startup_entrepreneur_comment_engagement(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for startup/entrepreneur comment engagement task.
    
    Checks:
    - Frontend: Current screen shows business content
    - Backend: ≥1 startup/entrepreneur post commented within business content
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Business keywords for frontend check
    business_keywords = [
        "创业", "startup", "企业家", "entrepreneur", "商业", "business", "创业故事", 
        "创业经验", "商业创新", "商业资讯", "创业分享", "商业分享"
    ]
    
    # Startup/entrepreneur keywords for post content
    startup_entrepreneur_keywords = [
        "创业", "startup", "企业家", "entrepreneur", "商业", "business", "创业故事", 
        "创业经验", "商业创新", "商业资讯", "创业分享", "商业分享", "创业公司", 
        "startup stories", "business innovation", "创业建议", "商业建议", "创业心得", 
        "商业心得"
    ]

    # Frontend checks: Verify current screen shows business content
    current_view = final_state_frontend.get("currentView", "")
    trending_topics = final_state_frontend.get("trendingTopics") or []
    search_query = final_state_frontend.get("searchQuery", "") or ""
    feed_displayed_posts = final_state_frontend.get("feedDisplayedPosts") or []
    
    has_business_content = False
    if current_view in ["trending", "search", "feed"]:
        # Check trendingTopics array
        if isinstance(trending_topics, list):
            for topic in trending_topics:
                if isinstance(topic, dict):
                    topic_text = topic.get("text", "") or topic.get("_id", "") or ""
                elif isinstance(topic, str):
                    topic_text = topic
                else:
                    continue
                
                if any(keyword in topic_text for keyword in business_keywords):
                    has_business_content = True
                    break
        
        # Check searchQuery if trending topics array doesn't have business content
        if not has_business_content and search_query:
            if any(keyword in search_query for keyword in business_keywords):
                has_business_content = True
        
        # Check feedDisplayedPosts if still no business content found
        if not has_business_content and isinstance(feed_displayed_posts, list):
            for post in feed_displayed_posts:
                if isinstance(post, dict):
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in business_keywords):
                        has_business_content = True
                        break
        
        if has_business_content:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                "Expected trending topic, search query, or feed to contain business keywords"
            )
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected currentView to be 'trending', 'search', or 'feed', got '{current_view}'"
        )

    # Backend checks: Query comments collection for current user's comments
    comments_result = backend.query({
        "collection": "comments",
        "filter": {"user._id": current_user_id}
    })
    comments = comments_result if isinstance(comments_result, list) else []
    
    # Extract post IDs from comments
    commented_post_ids: list[str] = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                post_id = comment.get("postId")
                if post_id:
                    commented_post_ids.append(post_id)

    # Query posts collection for commented posts and verify startup/entrepreneur content
    startup_entrepreneur_posts_commented = []
    for post_id in commented_post_ids:
        posts_result = backend.query({
            "collection": "posts",
            "filter": {"_id": post_id}
        })
        posts = posts_result if isinstance(posts_result, list) else []
        
        if isinstance(posts, list) and len(posts) > 0:
            post = posts[0]
            if isinstance(post, dict):
                content = post.get("content", "") or ""
                
                # Check if post contains startup/entrepreneur keywords
                if any(keyword in content for keyword in startup_entrepreneur_keywords):
                    startup_entrepreneur_posts_commented.append(post_id)

    # Verify ≥1 startup/entrepreneur post is commented
    if len(startup_entrepreneur_posts_commented) >= 1:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append(
            f"Expected ≥1 startup/entrepreneur post to be commented, found {len(startup_entrepreneur_posts_commented)}"
        )

    if all(checks_passed):
        return 1.0, "All startup/entrepreneur comment engagement checks passed"
    return 0.0, "; ".join(messages) if messages else "Some startup/entrepreneur comment engagement checks failed"


# -----------------------------------------------------------------------------
# Task: Creativity/Art Post
# -----------------------------------------------------------------------------

def _validate_creativity_art_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for creativity/art post task.
    
    Checks:
    - Backend: New post exists about creativity/art with ≥1 art-related hashtag
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Creativity/art keywords
    creativity_art_keywords = [
        "创意", "creativity", "艺术", "art", "设计", "design", "创作", "creation", 
        "艺术创作", "创意设计", "艺术设计", "创意分享", "艺术分享", "设计分享", 
        "创作分享", "创意灵感", "艺术灵感", "设计灵感", "artistic processes", 
        "design thinking", "artistic inspiration"
    ]
    
    # Art-related hashtag keywords
    art_hashtag_keywords = [
        "创意", "creativity", "艺术", "art", "设计", "design", "创作", "creation", 
        "艺术创作", "创意设计", "艺术设计", "艺术", "art"
    ]

    # Query posts collection for current user's posts
    posts_result = backend.query({
        "collection": "posts",
        "filter": {"user._id": current_user_id}
    })
    posts = posts_result if isinstance(posts_result, list) else []

    # Find post with creativity/art content
    art_post = None
    if isinstance(posts, list):
        for post in posts:
            if not isinstance(post, dict):
                continue
            content = post.get("content", "") or ""
            
            # Check if post contains creativity/art keywords
            if any(keyword in content for keyword in creativity_art_keywords):
                art_post = post
                break

    if art_post:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Expected post containing creativity/art content")

    # Verify post has ≥1 art-related hashtag
    has_art_hashtag = False
    if art_post:
        hashtags = art_post.get("hashtags") or []
        
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, dict):
                    tag_text = tag.get("text", "") or tag.get("_id", "") or ""
                elif isinstance(tag, str):
                    tag_text = tag
                else:
                    continue
                
                if any(keyword in tag_text for keyword in art_hashtag_keywords):
                    has_art_hashtag = True
                    break
        
        # Also check if hashtag appears in content text
        if not has_art_hashtag:
            content = art_post.get("content", "") or ""
            if "#" in content:
                for keyword in art_hashtag_keywords:
                    if f"#{keyword}" in content or keyword in content:
                        has_art_hashtag = True
                        break
        
        if has_art_hashtag:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append("Expected post to contain ≥1 art-related hashtag")
    else:
        checks_passed.append(False)
        messages.append("Cannot verify hashtag: creativity/art post not found")

    if all(checks_passed):
        return 1.0, "All creativity/art post checks passed"
    return 0.0, "; ".join(messages) if messages else "Some creativity/art post checks failed"


# -----------------------------------------------------------------------------
# Task: Family/Parenting Group Setup
# -----------------------------------------------------------------------------

def _validate_family_parenting_group_setup(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Combined validation for family/parenting group setup task.
    
    Checks:
    - Backend: Custom group with family/parenting-related name exists
    - Backend: ≥2 family/parenting accounts assigned to group
    """
    messages: list[str] = []
    checks_passed = []

    current_user_id = "8200663693"
    
    # Family/parenting group name keywords
    family_parenting_group_keywords = [
        "家庭", "family", "育儿", "parenting", "亲子", "parent-child", "家庭生活", 
        "育儿分享", "亲子分享", "家庭分享", "育儿心得", "亲子活动", "家庭活动"
    ]
    
    # Family/parenting content keywords
    family_parenting_keywords = [
        "家庭", "family", "育儿", "parenting", "亲子", "parent-child", "家庭生活", 
        "育儿分享", "亲子分享", "家庭分享", "育儿心得", "亲子活动", "家庭活动", 
        "育儿技巧", "parenting tips", "家庭活动", "family activities", "育儿建议", 
        "parenting advice", "育儿经验", "parenting experience"
    ]

    # Query customGroups collection for family/parenting-related group
    custom_groups_result = backend.query({"collection": "customGroups", "filter": {}})
    custom_groups = custom_groups_result if isinstance(custom_groups_result, list) else []

    # Find family/parenting-related group
    family_group_id: str | None = None
    if isinstance(custom_groups, list):
        for g in custom_groups:
            if isinstance(g, dict):
                group_label = g.get("label", "")
                if any(keyword in group_label for keyword in family_parenting_group_keywords):
                    family_group_id = g.get("_id")
                    break
    
    if family_group_id:
        checks_passed.append(True)
    else:
        checks_passed.append(False)
        messages.append("Custom group with family/parenting-related name not found")

    # Query userFollows collection for accounts assigned to group
    family_parenting_accounts = []
    if family_group_id:
        user_follows_result = backend.query({
            "collection": "userFollows",
            "filter": {"groups": family_group_id}
        })
        user_follows = user_follows_result if isinstance(user_follows_result, list) else []
        
        # Extract account IDs assigned to group
        assigned_account_ids: list[str] = []
        if isinstance(user_follows, list):
            for f in user_follows:
                if isinstance(f, dict):
                    followed_uid = f.get("followedUserId")
                    if followed_uid:
                        assigned_account_ids.append(followed_uid)
        
        # Query posts collection for assigned accounts and verify family/parenting content
        for account_id in assigned_account_ids:
            posts_result = backend.query({
                "collection": "posts",
                "filter": {"user._id": account_id}
            })
            posts = posts_result if isinstance(posts_result, list) else []
            
            # Check recent posts for family/parenting content
            has_family_content = False
            if isinstance(posts, list):
                for post in posts[:10]:  # Check last 10 posts
                    if not isinstance(post, dict):
                        continue
                    content = post.get("content", "") or ""
                    if any(keyword in content for keyword in family_parenting_keywords):
                        has_family_content = True
                        break
            
            if has_family_content:
                family_parenting_accounts.append(account_id)
        
        # Verify ≥2 accounts have family/parenting content
        if len(family_parenting_accounts) >= 2:
            checks_passed.append(True)
        else:
            checks_passed.append(False)
            messages.append(
                f"Expected ≥2 family/parenting accounts assigned to group, found {len(family_parenting_accounts)}"
            )
    else:
        checks_passed.append(False)
        messages.append("Cannot verify family/parenting accounts: family/parenting group not found")

    if all(checks_passed):
        return 1.0, "All family/parenting group setup checks passed"
    return 0.0, "; ".join(messages) if messages else "Some family/parenting group setup checks failed"


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================

REWARD_FUNCTIONS_WEIBO_V2: Dict[
    str, Union[ValidateTask, Callable[[Backend, Dict[str, Any]], Tuple[float, str]]]
] = {
    # Navigation & Search Tasks
    "_validate_profile_from_search": _validate_profile_from_search,
    "_validate_search_users": _validate_search_users,
    "_validate_switch_theme": _validate_switch_theme,
    "_validate_search_dropdown_profile": _validate_search_dropdown_profile,
    "_validate_profile_from_sorted_comments": _validate_profile_from_sorted_comments,
    "_validate_view_full_comment_thread": _validate_view_full_comment_thread,
    "_validate_video_post_from_profile": _validate_video_post_from_profile,
    "_validate_refresh_list_of_trending_topics": _validate_refresh_list_of_trending_topics,
    "_validate_refresh_list_of_suggested_users": _validate_refresh_list_of_suggested_users,
    "_validate_navigate_to_latest_feed_section": _validate_navigate_to_latest_feed_section,
    "_validate_navigate_via_trending_topic": _validate_navigate_via_trending_topic,
    "_validate_no_search_suggestions": _validate_no_search_suggestions,
    "_validate_open_inline_comments_section": _validate_open_inline_comments_section,
    "_validate_open_post_composer_more_dropdown": _validate_open_post_composer_more_dropdown,
    "_validate_partial_search_query": _validate_partial_search_query,
    "_validate_post_from_profile": _validate_post_from_profile,
    "_validate_post_from_search": _validate_post_from_search,
    "_validate_profile_from_comments": _validate_profile_from_comments,
    "_validate_profile_from_post": _validate_profile_from_post,
    "_validate_profile_from_reply": _validate_profile_from_reply,
    "_validate_home_from_search": _validate_home_from_search,
    "_validate_navigate_post": _validate_navigate_post,
    "_validate_navigate_profile": _validate_navigate_profile,
    "_validate_load_more_posts": _validate_load_more_posts,
    "_validate_load_many_posts": _validate_load_many_posts,
    "_validate_accept_search_suggestion": _validate_accept_search_suggestion,
    "_validate_change_search_categories": _validate_change_search_categories,
    "_validate_change_trending_tab_and_navigate": _validate_change_trending_tab_and_navigate,
    # Like/Unlike Tasks
    "_validate_unlike_single_post_from_feed": _validate_unlike_single_post_from_feed,
    "_validate_unlike_all_posts_on_profile": _validate_unlike_all_posts_on_profile,
    "_validate_like_post_from_main_feed": _validate_like_post_from_main_feed,
    "_validate_like_comment_on_post_detail": _validate_like_comment_on_post_detail,
    "_validate_like_2_comments": _validate_like_2_comments,
    # Follow/Unfollow Tasks
    "_validate_unfollow_user_from_profile_page": _validate_unfollow_user_from_profile_page,
    "_validate_search_follow_user": _validate_search_follow_user,
    "_validate_follow_and_set_special_attention_flow": _validate_follow_and_set_special_attention_flow,
    "_validate_follow_and_unfollow_from_profile": _validate_follow_and_unfollow_from_profile,
    "_validate_follow_assign_to_group_and_navigate": _validate_follow_assign_to_group_and_navigate,
    "_validate_follow_create_group_and_assign_flow": _validate_follow_create_group_and_assign_flow,
    "_validate_follow_multiple_users_from_search": _validate_follow_multiple_users_from_search,
    "_validate_follow_user_and_check_latest_feed": _validate_follow_user_and_check_latest_feed,
    # Group Management Tasks
    "_validate_remove_user_from_single_group": _validate_remove_user_from_single_group,
    "_validate_reassign_user_to_different_group": _validate_reassign_user_to_different_group,
    "_validate_unassign_special_attention_and_groups": _validate_unassign_special_attention_and_groups,
    "_validate_delete_custom_group": _validate_delete_custom_group,
    "_validate_edit_custom_group_name": _validate_edit_custom_group_name,
    "_validate_add_user_to_new_custom_group_from_profile": _validate_add_user_to_new_custom_group_from_profile,
    "_validate_create_custom_group_and_navigate": _validate_create_custom_group_and_navigate,
    # Comment Tasks
    "_validate_reply_to_comment": _validate_reply_to_comment,
    "_validate_create_comment_with_expressions_on_detail": _validate_create_comment_with_expressions_on_detail,
    "_validate_create_comment_with_inline_section": _validate_create_comment_with_inline_section,
    # Post Creation Tasks
    "_validate_post_and_view_hashtag": _validate_post_and_view_hashtag,
    "_validate_post_image": _validate_post_image,
    "_validate_post_video": _validate_post_video,
    "_validate_create_post_and_verify_in_profile": _validate_create_post_and_verify_in_profile,
    "_validate_create_post_with_emoji_expression": _validate_create_post_with_emoji_expression,
    "_validate_create_post_with_hashtags": _validate_create_post_with_hashtags,
    "_validate_create_post_with_three_expressions": _validate_create_post_with_three_expressions,
    "_validate_create_post_with_two_or_more_emojis": _validate_create_post_with_two_or_more_emojis,
    "_validate_create_post_with_user_mention": _validate_create_post_with_user_mention,
    "_validate_create_post_with_mention_and_hashtag": _validate_create_post_with_mention_and_hashtag,
    # High-level Combined Validation Tasks (Backend pattern)
    # Post Creation Tasks
    "_validate_movie_review_post": _validate_movie_review_post,
    "_validate_fitness_workout_post": _validate_fitness_workout_post,
    "_validate_trending_news_post": _validate_trending_news_post,
    "_validate_seasons_nature_post": _validate_seasons_nature_post,
    "_validate_environment_sustainability_post": _validate_environment_sustainability_post,
    "_validate_work_life_balance_post": _validate_work_life_balance_post,
    "_validate_philosophical_reflection_post": _validate_philosophical_reflection_post,
    "_validate_childhood_nostalgia_post": _validate_childhood_nostalgia_post,
    "_validate_cooking_recipe_post": _validate_cooking_recipe_post,
    "_validate_learning_education_post": _validate_learning_education_post,
    "_validate_positive_motivational_post": _validate_positive_motivational_post,
    "_validate_minimalism_simple_living_post": _validate_minimalism_simple_living_post,
    "_validate_movie_cinema_post": _validate_movie_cinema_post,
    "_validate_mental_wellness_post": _validate_mental_wellness_post,
    "_validate_creativity_art_post": _validate_creativity_art_post,
    "_validate_productivity_post": _validate_productivity_post,
    # Group Setup Tasks
    "_validate_travel_group_setup": _validate_travel_group_setup,
    "_validate_gaming_group_setup": _validate_gaming_group_setup,
    "_validate_art_design_group_setup": _validate_art_design_group_setup,
    "_validate_comedy_humor_group_setup": _validate_comedy_humor_group_setup,
    "_validate_science_group_setup": _validate_science_group_setup,
    "_validate_history_documentary_group_setup": _validate_history_documentary_group_setup,
    "_validate_automotive_group_setup": _validate_automotive_group_setup,
    "_validate_finance_group_setup": _validate_finance_group_setup,
    "_validate_outdoor_adventure_group_setup": _validate_outdoor_adventure_group_setup,
    "_validate_family_parenting_group_setup": _validate_family_parenting_group_setup,
    "_validate_work_group_organization": _validate_work_group_organization,
    # Engagement Tasks - Likes/Comments
    "_validate_food_recipe_post_likes": _validate_food_recipe_post_likes,
    "_validate_music_posts_likes_and_follow": _validate_music_posts_likes_and_follow,
    "_validate_photography_art_comments": _validate_photography_art_comments,
    "_validate_sports_trending_engagement": _validate_sports_trending_engagement,
    "_validate_fashion_trending_likes": _validate_fashion_trending_likes,
    "_validate_local_regional_engagement": _validate_local_regional_engagement,
    "_validate_pet_posts_liked_and_commented": _validate_pet_posts_liked_and_commented,
    "_validate_cultural_event_engagement": _validate_cultural_event_engagement,
    "_validate_entertainment_trending_likes": _validate_entertainment_trending_likes,
    "_validate_beauty_skincare_trending_engagement": _validate_beauty_skincare_trending_engagement,
    "_validate_news_analysis_trending_likes": _validate_news_analysis_trending_likes,
    "_validate_language_learning_engagement": _validate_language_learning_engagement,
    "_validate_startup_entrepreneur_comment_engagement": _validate_startup_entrepreneur_comment_engagement,
    # Trending Topic Engagement Tasks
    "_validate_tech_trending_topic_engagement": _validate_tech_trending_topic_engagement,
    "_validate_trending_topic_high_engagement": _validate_trending_topic_high_engagement,
    "_validate_tech_trending_comment": _validate_tech_trending_comment,
    "_validate_political_trending_topic_comment": _validate_political_trending_topic_comment,
    "_validate_latest_weibo_feed_comment": _validate_latest_weibo_feed_comment,
    # Follow/Search Tasks
    "_validate_book_accounts_follow_from_search": _validate_book_accounts_follow_from_search,
    "_validate_health_wellness_accounts_follow": _validate_health_wellness_accounts_follow,
    "_validate_unfollow_accounts": _validate_unfollow_accounts, #special initial state
    # Special Attention Tasks
    "_validate_entertainment_special_attention_setup": _validate_entertainment_special_attention_setup,
    "_validate_professional_account_special_attention": _validate_professional_account_special_attention,
}


__all__ = [
    "REWARD_FUNCTIONS_WEIBO_V2",
    "ValidateTask",
    "StateKey",
    "StateKeyQuery",
]
