"""
Reward functions for Xiaohongshu (Little Red Book) app tasks - V2 Architecture.

This version includes both frontend and backend validation with bundled reward functions.
Each task exports a bundle containing:
  - state_key: Dict defining backend queries (collection + filter)
  - validate_backend: Function (state_key, final_state) -> (float, str)
  - validate_frontend: Function (initial_state, final_state) -> (float, str)
"""

import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict, Union

logger = logging.getLogger(__name__)

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


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
# BATCH 1: Navigation & UI State Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: access-creative-center-page-v2
# -----------------------------------------------------------------------------


def _validate_backend_access_creative_center_page(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # No backend state changes for this navigation task
    return 1.0, "No backend validation required for creative center navigation"


def _validate_frontend_access_creative_center_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    return 1.0, "Creative center opened via publish entry point"


_validate_access_creative_center_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_access_creative_center_page,
    "validate_frontend": _validate_frontend_access_creative_center_page,
}


# -----------------------------------------------------------------------------
# Task: album-view-v2
# -----------------------------------------------------------------------------


def _validate_backend_album_view(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # No backend state changes for this navigation task
    return 1.0, "No backend validation required for album view navigation"


def _validate_frontend_album_view(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    for field, expected in (("page", "profile"), ("previousPage", "explore"), ("profileView", "bookmarks")):
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Profile bookmarks view is visible from album grid"


_validate_album_view: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_album_view,
    "validate_frontend": _validate_frontend_album_view,
}


# -----------------------------------------------------------------------------
# Task: back-page-v2
# -----------------------------------------------------------------------------


def _validate_backend_back_page(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for back page navigation"


def _validate_frontend_back_page(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "album":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'album'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Returned to profile from album view using back navigation"


_validate_back_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_back_page,
    "validate_frontend": _validate_frontend_back_page,
}


# -----------------------------------------------------------------------------
# Task: bookmarks-view-v2
# -----------------------------------------------------------------------------


def _validate_backend_bookmarks_view(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for bookmarks view navigation"


def _validate_frontend_bookmarks_view(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("profileView") != "bookmarks":
        return 0.0, f"profileView={final_state.get('profileView')} expected 'bookmarks'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Viewing current user's bookmarks"


_validate_bookmarks_view: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_bookmarks_view,
    "validate_frontend": _validate_frontend_bookmarks_view,
}


# -----------------------------------------------------------------------------
# Task: business-hover-v2
# -----------------------------------------------------------------------------


def _validate_backend_business_hover(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for hover state"


def _validate_frontend_business_hover(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    hover_state = final_state.get("navbarHoverState")
    if not isinstance(hover_state, dict):
        return 0.0, "navbarHoverState missing or not an object"
    if hover_state.get("business") is not True:
        return 0.0, "navbarHoverState.business is not true"
    return 1.0, "Business dropdown is open via hover"


_validate_business_hover: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_business_hover,
    "validate_frontend": _validate_frontend_business_hover,
}


# -----------------------------------------------------------------------------
# Task: creative-center-hover-v2
# -----------------------------------------------------------------------------


def _validate_backend_creative_center_hover(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for hover state"


def _validate_frontend_creative_center_hover(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    hover_state = final_state.get("navbarHoverState")
    if not isinstance(hover_state, dict):
        return 0.0, "navbarHoverState missing or not an object"
    if hover_state.get("creative") is not True:
        return 0.0, "navbarHoverState.creative is not true"
    return 1.0, "Creative center hover modal is visible"


_validate_creative_center_hover: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_creative_center_hover,
    "validate_frontend": _validate_frontend_creative_center_hover,
}


# -----------------------------------------------------------------------------
# Task: creative-dashboard-v2
# -----------------------------------------------------------------------------


def _validate_backend_creative_dashboard(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for creative dashboard navigation"


def _validate_frontend_creative_dashboard(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("creativeSidebarNav") != "home":
        return 0.0, f"creativeSidebarNav={final_state.get('creativeSidebarNav')} expected 'home'"
    if final_state.get("creativeView") != "home":
        return 0.0, f"creativeView={final_state.get('creativeView')} expected 'home'"
    return 1.0, "Creative dashboard is visible with the Home tab selected"


_validate_creative_dashboard: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_creative_dashboard,
    "validate_frontend": _validate_frontend_creative_dashboard,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-v2
# -----------------------------------------------------------------------------


def _validate_backend_dark_mode(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_dark_mode(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"
    return 1.0, "Theme set to dark mode"


_validate_dark_mode: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_dark_mode,
    "validate_frontend": _validate_frontend_dark_mode,
}


# -----------------------------------------------------------------------------
# Task: light-mode-v2
# -----------------------------------------------------------------------------


def _validate_backend_light_mode(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_light_mode(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("themeMode") != "light":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'light'"
    return 1.0, "Theme set to light mode"


_validate_light_mode: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_light_mode,
    "validate_frontend": _validate_frontend_light_mode,
}


# -----------------------------------------------------------------------------
# Task: system-theme-v2
# -----------------------------------------------------------------------------


def _validate_backend_system_theme(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_system_theme(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("themeMode") != "system":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'system'"
    return 1.0, "Theme set to follow system setting"


_validate_system_theme: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_system_theme,
    "validate_frontend": _validate_frontend_system_theme,
}


# -----------------------------------------------------------------------------
# Task: likes-view-v2
# -----------------------------------------------------------------------------


def _validate_backend_likes_view(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for likes view navigation"


def _validate_frontend_likes_view(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("profileView") != "likes":
        return 0.0, f"profileView={final_state.get('profileView')} expected 'likes'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Viewing current user's liked posts"


_validate_likes_view: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_likes_view,
    "validate_frontend": _validate_frontend_likes_view,
}


# -----------------------------------------------------------------------------
# Task: navigate-own-profile-v2
# -----------------------------------------------------------------------------


def _validate_backend_navigate_own_profile(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for profile navigation"


def _validate_frontend_navigate_own_profile(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page is {final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Navigated to current user's profile"


_validate_navigate_own_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_own_profile,
    "validate_frontend": _validate_frontend_navigate_own_profile,
}


# -----------------------------------------------------------------------------
# Task: open-an-album-v2
# -----------------------------------------------------------------------------


def _validate_backend_open_an_album(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for album navigation"


def _validate_frontend_open_an_album(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "album":
        return 0.0, f"page={final_state.get('page')} expected 'album'"
    if final_state.get("previousPage") != "profile":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'profile'"
    if final_state.get("activeAlbumId") != "1764819999139-kaqa0ell41o":
        return 0.0, f"activeAlbumId={final_state.get('activeAlbumId')} expected '1764819999139-kaqa0ell41o'"
    return 1.0, "Opened an album from the profile grid"


_validate_open_an_album: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_an_album,
    "validate_frontend": _validate_frontend_open_an_album,
}


# -----------------------------------------------------------------------------
# Task: open-post-modal-v2
# -----------------------------------------------------------------------------


def _validate_backend_open_post_modal(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for modal opening"


def _validate_frontend_open_post_modal(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if not final_state.get("activePostId"):
        return 0.0, "activePostId is missing or null"
    if final_state.get("isVideoPaused") is True:
        return 0.0, "isVideoPaused is True; expected False while modal open"
    return 1.0, "Opened a post modal with video playing"


_validate_open_post_modal: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_post_modal,
    "validate_frontend": _validate_frontend_open_post_modal,
}


# -----------------------------------------------------------------------------
# Task: open-video-pause-v2
# -----------------------------------------------------------------------------


def _validate_backend_open_video_pause(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for video pause"


def _validate_frontend_open_video_pause(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "2":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '2'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused after opening post 2"
    return 1.0, "Opened post 2 video and paused it"


_validate_open_video_pause: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_video_pause,
    "validate_frontend": _validate_frontend_open_video_pause,
}


# -----------------------------------------------------------------------------
# Task: search-input-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_input(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search input"


def _validate_frontend_search_input(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("searchQuery") != "hello":
        return 0.0, f"searchQuery={final_state.get('searchQuery')} expected 'hello'"
    return 1.0, "Updated search input to 'hello'"


_validate_search_input: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_input,
    "validate_frontend": _validate_frontend_search_input,
}


# -----------------------------------------------------------------------------
# Task: search-filter-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_filter(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search filter"


def _validate_frontend_search_filter(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("searchQuery") != "oo":
        return 0.0, f"searchQuery={final_state.get('searchQuery')} expected 'oo'"
    filters = final_state.get("searchAdvancedFilters")
    if not isinstance(filters, dict):
        return 0.0, "searchAdvancedFilters missing or not an object"
    expected = {
        "sortBy": "latest",
        "noteType": "image",
        "publishTime": "year",
        "searchScope": "unseen",
        "location": "any",
    }
    for key, value in expected.items():
        if filters.get(key) != value:
            return 0.0, f"searchAdvancedFilters.{key}={filters.get(key)} expected '{value}'"
    return 1.0, "Search query and filters updated to requested values"


_validate_search_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_filter,
    "validate_frontend": _validate_frontend_search_filter,
}


# -----------------------------------------------------------------------------
# Task: set-filter-v2
# -----------------------------------------------------------------------------


def _validate_backend_set_filter(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for feed filter"


def _validate_frontend_set_filter(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("feedFilter") != "OOTD":
        return 0.0, f"feedFilter={final_state.get('feedFilter')} expected 'OOTD'"
    return 1.0, "Feed filter set to OOTD"


_validate_set_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_set_filter,
    "validate_frontend": _validate_frontend_set_filter,
}


# -----------------------------------------------------------------------------
# Task: share-v2
# -----------------------------------------------------------------------------


def _validate_backend_share(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for share popover"


def _validate_frontend_share(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("sharePopoverPostId") != "1":
        return 0.0, f"sharePopoverPostId={final_state.get('sharePopoverPostId')} expected '1'"
    return 1.0, "Share popover open for post 1"


_validate_share: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_share,
    "validate_frontend": _validate_frontend_share,
}


# -----------------------------------------------------------------------------
# Task: watch-full-video-v2
# -----------------------------------------------------------------------------


def _validate_backend_watch_full_video(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for video watching"


def _validate_frontend_watch_full_video(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "2":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '2'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused at completion"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching video"
    return 1.0, "Watched post 2 video through completion"


_validate_watch_full_video: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_watch_full_video,
    "validate_frontend": _validate_frontend_watch_full_video,
}


# -----------------------------------------------------------------------------
# Task: find-mention-v2
# -----------------------------------------------------------------------------


def _validate_backend_find_mention(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for finding mention"


def _validate_frontend_find_mention(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "notifications" or final_state.get("previousPage") != "explore":
        return 0.0, (
            f"page={final_state.get('page')} previousPage={final_state.get('previousPage')} expected notifications/explore"
        )
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("highlightCommentId") != "c1":
        return 0.0, f"highlightCommentId={final_state.get('highlightCommentId')} expected 'c1'"
    return 1.0, "Navigated to notifications and opened the mention thread"


_validate_find_mention: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_find_mention,
    "validate_frontend": _validate_frontend_find_mention,
}


# =============================================================================
# BATCH 2: Like/Bookmark/Interaction Tasks (with backend validation)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: like-post-v2
# -----------------------------------------------------------------------------


def _validate_backend_like_post(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user = user_1[0]
    if user.get("likeCount") != 1:
        return 0.0, f"Backend: User 1 likeCount={user.get('likeCount')} expected 1"

    return 1.0, "Backend: Post 1 liked successfully"


def _validate_frontend_like_post(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    return 1.0, "Post 1 modal was opened"


_validate_like_post: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_like_post,
    "validate_frontend": _validate_frontend_like_post,
}


# -----------------------------------------------------------------------------
# Task: unlike-post-v2
# -----------------------------------------------------------------------------


def _validate_backend_unlike_post(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_10 = final_state.get("post_10")
    if not isinstance(post_10, list) or len(post_10) == 0:
        return 0.0, "Post 10 not found in backend"
    post = post_10[0]
    if post.get("likes") != 0:
        return 0.0, f"Backend: Post 10 likes={post.get('likes')} expected 0"

    return 1.0, "Backend: Post 10 unliked successfully"


def _validate_frontend_unlike_post(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "3":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '3'"
    return 1.0, "Post 3 modal was opened for unliking"


_validate_unlike_post: ValidateTask = {
    "state_key": {
        "post_10": {"collection": "posts", "filter": {"_id": "10"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_unlike_post,
    "validate_frontend": _validate_frontend_unlike_post,
}


# -----------------------------------------------------------------------------
# Task: bookmark-post-v2
# -----------------------------------------------------------------------------


def _validate_backend_bookmark_post(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("bookmarks") != 1:
        return 0.0, f"Backend: Post 1 bookmarks={post.get('bookmarks')} expected 1"

    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user = user_1[0]
    if user.get("bookmarkedCount") != 1:
        return 0.0, f"Backend: User 1 bookmarkedCount={user.get('bookmarkedCount')} expected 1"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    bookmarks = current_user[0].get("bookmarks")
    if not isinstance(bookmarks, list) or "1" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks={bookmarks} expected to include '1'"

    return 1.0, "Backend: Post 1 bookmarked successfully"


def _validate_frontend_bookmark_post(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Bookmarked post 1 while remaining on explore feed"


_validate_bookmark_post: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_post,
    "validate_frontend": _validate_frontend_bookmark_post,
}


# -----------------------------------------------------------------------------
# Task: like-and-bookmark-v2
# -----------------------------------------------------------------------------


def _validate_backend_like_and_bookmark(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post = post_2[0]
    if post.get("likes") != 1 or post.get("bookmarks") != 1:
        return 0.0, f"Backend: Post 2 likes={post.get('likes')} bookmarks={post.get('bookmarks')} expected 1/1"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    if "2" not in current_user[0].get("liked", []):
        return 0.0, "Backend: currentUser.liked should contain '2'"
    if "2" not in current_user[0].get("bookmarks", []):
        return 0.0, "Backend: currentUser.bookmarks should contain '2'"

    return 1.0, "Backend: Liked and bookmarked post 2 successfully"


def _validate_frontend_like_and_bookmark(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    # Frontend validation skipped - data not in UI state
    return 1.0, "Frontend validation skipped (data not in UI state)"


_validate_like_and_bookmark: ValidateTask = {
    "state_key": {
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
        "user_2": {"collection": "users", "filter": {"_id": "2"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_like_and_bookmark,
    "validate_frontend": _validate_frontend_like_and_bookmark,
}


# -----------------------------------------------------------------------------
# Task: like-3-sequential-v2
# -----------------------------------------------------------------------------


def _validate_backend_like_3_sequential(final_state: Dict[str, Any]) -> Tuple[float, str]:
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"

    # Check that we have all 3 posts
    if len(posts) < 3:
        return 0.0, f"Expected 3 posts, got {len(posts)}"

    for post in posts:
        pid = post.get("_id")
        if post.get("likes") != 1:
            return 0.0, f"Backend: Post {pid} likes={post.get('likes')} expected 1"

    users = final_state.get("users")
    if not isinstance(users, list):
        return 0.0, "Users array missing in backend"

    # Check users 1 and 3 (user 2 is the author of post 2, doesn't need validation per original logic)
    for user in users:
        uid = user.get("_id")
        if uid in ("1", "3"):
            if user.get("likeCount") != 1:
                return 0.0, f"Backend: User {uid} likeCount={user.get('likeCount')} expected 1"

    return 1.0, "Backend: Sequentially liked posts 1, 2, and 3"


def _validate_frontend_like_3_sequential(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Sequential likes performed from explore feed"


_validate_like_3_sequential: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["1", "2", "3"]}}},
        "users": {"collection": "users", "filter": {"_id": {"$in": ["1", "2", "3"]}}},
    },
    "validate_backend": _validate_backend_like_3_sequential,
    "validate_frontend": _validate_frontend_like_3_sequential,
}


# -----------------------------------------------------------------------------
# Task: bookmark-and-like-v2
# -----------------------------------------------------------------------------


def _validate_backend_bookmark_and_like(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1 or post.get("bookmarks") != 1:
        return 0.0, (
            f"Backend: Post 1 likes/bookmarks mismatch. likes={post.get('likes')} bookmarks={post.get('bookmarks')} expected 1/1"
        )

    return 1.0, "Backend: Bookmarked and liked post 1"


def _validate_frontend_bookmark_and_like(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    requirements = (
        ("page", "profile"),
        ("previousPage", "explore"),
        ("profileView", "bookmarks"),
        ("profileUserId", "0"),
    )
    for field, expected in requirements:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    return 1.0, "Viewing own bookmark tab while interacting with post 1"


_validate_bookmark_and_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_and_like,
    "validate_frontend": _validate_frontend_bookmark_and_like,
}


# -----------------------------------------------------------------------------
# Task: bookmark-album-v2
# -----------------------------------------------------------------------------


def _validate_backend_bookmark_album(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # Check posts 8 and 9 have bookmarks
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"

    if len(posts) < 2:
        return 0.0, f"Expected 2 posts (8 and 9), got {len(posts)}"

    for post in posts:
        pid = post.get("_id")
        if post.get("bookmarks") != 1:
            return 0.0, f"Backend: Post {pid} bookmarks={post.get('bookmarks')} expected 1"

    # Check current user has both posts in bookmarks and album "yoo" with post 9
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    user = current_user[0]

    bookmarks = user.get("bookmarks", [])
    if "8" not in bookmarks:
        return 0.0, "Backend: currentUser.bookmarks should contain '8'"
    if "9" not in bookmarks:
        return 0.0, "Backend: currentUser.bookmarks should contain '9'"

    # Check for album named "yoo" with post 9 in it
    albums = user.get("albums", [])
    yoo_album = next((a for a in albums if a.get("name") == "yoo"), None)
    if not yoo_album:
        return 0.0, "Backend: currentUser should have an album named 'yoo'"
    if "9" not in yoo_album.get("postIds", []):
        return 0.0, "Backend: Album 'yoo' should contain post '9'"

    return 1.0, "Backend: Bookmarked posts 8 and 9, album 'yoo' created with post 9"


def _validate_frontend_bookmark_album(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Bookmarked posts from explore feed"


_validate_bookmark_album: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["8", "9"]}}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_album,
    "validate_frontend": _validate_frontend_bookmark_album,
}


# =============================================================================
# BATCH 3: Follow/Unfollow Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: follow-user-v2
# -----------------------------------------------------------------------------


def _validate_backend_follow_user(final_state: Dict[str, Any]) -> Tuple[float, str]:
    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user1 = user_1[0]
    followers = user1.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 1 followers={followers} expected to include '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list) or "1" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '1'"

    return 1.0, "Backend: Successfully followed user 1"


def _validate_frontend_follow_user(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("profileUserId") != "1":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '1'"
    return 1.0, "Viewing user 1 profile before following"


_validate_follow_user: ValidateTask = {
    "state_key": {
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_follow_user,
    "validate_frontend": _validate_frontend_follow_user,
}


# -----------------------------------------------------------------------------
# Task: unfollow-user-v2
# -----------------------------------------------------------------------------


def _validate_backend_unfollow_user(final_state: Dict[str, Any]) -> Tuple[float, str]:
    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user1 = user_1[0]
    followers = user1.get("followers", [])
    if "0" in followers:
        return 0.0, f"Backend: User 1 followers={followers} should not contain '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following", [])
    if "1" in following:
        return 0.0, f"Backend: currentUser.following={following} should not contain '1'"

    return 1.0, "Backend: Successfully unfollowed user 1"


def _validate_frontend_unfollow_user(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("profileUserId", "1"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "On user 1's profile page after unfollowing"


_validate_unfollow_user: ValidateTask = {
    "state_key": {
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_unfollow_user,
    "validate_frontend": _validate_frontend_unfollow_user,
}


# -----------------------------------------------------------------------------
# Task: follow-new-follower-v2
# -----------------------------------------------------------------------------


def _validate_backend_follow_new_follower(final_state: Dict[str, Any]) -> Tuple[float, str]:
    user_15 = final_state.get("user_15")
    if not isinstance(user_15, list) or len(user_15) == 0:
        return 0.0, "User 15 not found in backend"
    new_user = user_15[0]
    followers = new_user.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 15 followers={followers} expected to include '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list) or "15" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '15'"

    return 1.0, "Backend: Followed the new follower"


def _validate_frontend_follow_new_follower(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "notifications" or final_state.get("previousPage") != "explore":
        return 0.0, (
            f"page={final_state.get('page')} previousPage={final_state.get('previousPage')} expected notifications/explore"
        )
    return 1.0, "Following action performed from notifications view"


_validate_follow_new_follower: ValidateTask = {
    "state_key": {
        "user_15": {"collection": "users", "filter": {"_id": "15"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_follow_new_follower,
    "validate_frontend": _validate_frontend_follow_new_follower,
}


# -----------------------------------------------------------------------------
# Task: search-and-follow-all-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_and_follow_all(final_state: Dict[str, Any]) -> Tuple[float, str]:
    users = final_state.get("users")
    if not isinstance(users, list):
        return 0.0, "Users array missing in backend"

    if len(users) < 5:
        return 0.0, f"Expected 5 users, got {len(users)}"

    for user in users:
        uid = user.get("_id")
        followers = user.get("followers")
        if not isinstance(followers, list) or "0" not in followers:
            return 0.0, f"Backend: User {uid} followers={followers} expected to include '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list):
        return 0.0, "Backend: currentUser.following is not a list"
    for uid in ("1", "2", "3", "4", "5"):
        if uid not in following:
            return 0.0, f"Backend: currentUser.following={following} expected to include '{uid}'"

    return 1.0, "Backend: Followed all users 1-5"


def _validate_frontend_search_and_follow_all(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Returned to explore page after following all users"


_validate_search_and_follow_all: ValidateTask = {
    "state_key": {
        "users": {"collection": "users", "filter": {"_id": {"$in": ["1", "2", "3", "4", "5"]}}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_and_follow_all,
    "validate_frontend": _validate_frontend_search_and_follow_all,
}


# =============================================================================
# BATCH 4: Comment Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: comment-on-video-v2
# -----------------------------------------------------------------------------


def _validate_backend_comment_on_video(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_4 = final_state.get("post_4")
    if not isinstance(post_4, list) or len(post_4) == 0:
        return 0.0, "Post 4 not found in backend"
    post = post_4[0]
    comments = post.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Backend: Post 4 comments array missing"

    # Look for comment with content containing "this cat so cute!"
    found = False
    for comment in comments:
        content = comment.get("content", "")
        if "this cat so cute!" in content.lower():
            found = True
            break
    if not found:
        return 0.0, "Backend: Comment 'this cat so cute!' not found on post 4"

    return 1.0, "Backend: Comment added to post 4"


def _validate_frontend_comment_on_video(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Commented on post 4 from explore feed"


_validate_comment_on_video: ValidateTask = {
    "state_key": {
        "post_4": {"collection": "posts", "filter": {"_id": "4"}},
    },
    "validate_backend": _validate_backend_comment_on_video,
    "validate_frontend": _validate_frontend_comment_on_video,
}


# -----------------------------------------------------------------------------
# Task: comment-on-two-separate-posts-v2
# -----------------------------------------------------------------------------


def _validate_backend_comment_on_two_separate_posts(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post1 = post_1[0]
    comments1 = post1.get("comments", [])
    found1 = any("nice song!" in c.get("content", "").lower() for c in comments1)
    if not found1:
        return 0.0, "Backend: Comment 'nice song!' not found on post 1"

    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post2 = post_2[0]
    comments2 = post2.get("comments", [])
    found2 = any("what the dog doing?" in c.get("content", "").lower() for c in comments2)
    if not found2:
        return 0.0, "Backend: Comment 'what the dog doing?' not found on post 2"

    return 1.0, "Backend: Comments added to posts 1 and 2"


def _validate_frontend_comment_on_two_separate_posts(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Comments added while staying on explore feed"


_validate_comment_on_two_separate_posts: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
    },
    "validate_backend": _validate_backend_comment_on_two_separate_posts,
    "validate_frontend": _validate_frontend_comment_on_two_separate_posts,
}


# -----------------------------------------------------------------------------
# Task: reply-chain-v2
# -----------------------------------------------------------------------------


def _validate_backend_reply_chain(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    comments = post.get("comments", [])

    # Should have at least 3 comments including the new reply
    has_nested_reply = any(
        isinstance(c.get("content"), str) and c["content"].strip().lower() == "nice" and c.get("parentId") == "c1-1"
        for c in comments
    )
    if not has_nested_reply:
        return 0.0, "Backend: Reply with content 'nice' to comment c1-1 not found"

    return 1.0, "Backend: Nested reply added to comment chain"


def _validate_frontend_reply_chain(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    return 1.0, "Reply chain interaction completed on post 1"


_validate_reply_chain: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_reply_chain,
    "validate_frontend": _validate_frontend_reply_chain,
}


# -----------------------------------------------------------------------------
# Task: comment-interaction-series-v2
# -----------------------------------------------------------------------------


def _validate_backend_comment_interaction_series(final_state: Dict[str, Any]) -> Tuple[float, str]:
    def _get_post(key: str) -> Tuple[Optional[Dict[str, Any]], str]:
        data = final_state.get(key)
        if not isinstance(data, list) or not data:
            return None, f"{key} not found in backend"
        return data[0], ""

    # Get current user's liked items
    current_user_data = final_state.get("current_user")
    if not isinstance(current_user_data, list) or len(current_user_data) == 0:
        return 0.0, "Current user not found in backend"
    current_user_liked = current_user_data[0].get("liked", [])
    if not isinstance(current_user_liked, list):
        current_user_liked = []

    def _require_comment_liked(post: Dict[str, Any], comment_id: str, label: str) -> Tuple[bool, str]:
        comment = next((c for c in post.get("comments", []) if c.get("_id") == comment_id), None)
        if not comment:
            return False, f"{label}: comment {comment_id} not found"
        if comment_id not in current_user_liked:
            return False, f"{label}: comment {comment_id} should be in currentUser.liked, got {current_user_liked}"
        return True, ""

    def _require_reply(post: Dict[str, Any], *, expected_parent: str, expected_content: str) -> Tuple[bool, str]:
        replies = [
            c
            for c in post.get("comments", [])
            if isinstance(c.get("content"), str)
            and c["content"].strip().lower() == expected_content
            and c.get("parentId") == expected_parent
            and c.get("authorId") == "0"
        ]
        if not replies:
            return False, (f"Reply '{expected_content}' to {expected_parent} not found on post {post.get('_id')}")
        return True, ""

    post1, error = _get_post("post_1")
    if not post1:
        return 0.0, error
    ok, error = _require_comment_liked(post1, "c1", "Post 1")
    if not ok:
        return 0.0, error
    ok, error = _require_comment_liked(post1, "seed-1", "Post 1")
    if not ok:
        return 0.0, error
    ok, error = _require_reply(post1, expected_parent="seed-1", expected_content="nice")
    if not ok:
        return 0.0, error

    post2, error = _get_post("post_2")
    if not post2:
        return 0.0, error
    ok, error = _require_comment_liked(post2, "c2", "Post 2")
    if not ok:
        return 0.0, error
    ok, error = _require_reply(post2, expected_parent="c2", expected_content="nice2")
    if not ok:
        return 0.0, error

    post3, error = _get_post("post_3")
    if not post3:
        return 0.0, error
    ok, error = _require_comment_liked(post3, "c3", "Post 3")
    if not ok:
        return 0.0, error
    ok, error = _require_reply(post3, expected_parent="c3", expected_content="nice3")
    if not ok:
        return 0.0, error

    return 1.0, "Backend: Comment interaction series completed"


def _validate_backend_comment_interaction_series_unused(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # Get current user's liked items
    current_user_data = final_state.get("current_user")
    if not isinstance(current_user_data, list) or len(current_user_data) == 0:
        return 0.0, "Current user not found in backend"
    current_user_liked = current_user_data[0].get("liked", [])
    if not isinstance(current_user_liked, list):
        current_user_liked = []

    # Check post 1: comments c1, c1-1 liked and reply to c1-1
    post1 = final_state.get("post_1")
    if not post1:
        return 0.0, "post_1 not found in final_state"
    comments1 = post1.get("comments", [])
    for cid in ("c1", "c1-1"):
        comment = next((c for c in comments1 if c.get("_id") == cid), None)
        if not comment:
            return 0.0, f"Comment {cid} not found on post 1"
        if cid not in current_user_liked:
            return 0.0, f"Backend: Comment {cid} should be in currentUser.liked, got {current_user_liked}"

    # Check post 2: comment c2 liked and reply
    post2 = final_state.get("post_2")
    if not post2:
        return 0.0, "post_2 not found in final_state"
    comments2 = post2.get("comments", [])
    comment = next((c for c in comments2 if c.get("_id") == "c2"), None)
    if not comment:
        return 0.0, "Comment c2 not found on post 2"
    if "c2" not in current_user_liked:
        return 0.0, f"Backend: Comment c2 should be in currentUser.liked, got {current_user_liked}"

    # Check post 3: comment c3 liked and reply
    post3 = final_state.get("post_3")
    if not post3:
        return 0.0, "post_3 not found in final_state"
    comments3 = post3.get("comments", [])
    comment = next((c for c in comments3 if c.get("_id") == "c3"), None)
    if not comment:
        return 0.0, "Comment c3 not found on post 3"
    if "c3" not in current_user_liked:
        return 0.0, f"Backend: Comment c3 should be in currentUser.liked, got {current_user_liked}"

    return 1.0, "Backend: Comment interaction series completed"


def _validate_frontend_comment_interaction_series(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null"
    return 1.0, "Completed comment interactions while returning to explore feed"


_validate_comment_interaction_series: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
        "post_3": {"collection": "posts", "filter": {"_id": "3"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_comment_interaction_series,
    "validate_frontend": _validate_frontend_comment_interaction_series,
}


# -----------------------------------------------------------------------------
# Task: bookmark-album-comment-reply-v2
# -----------------------------------------------------------------------------


def _validate_backend_bookmark_album_comment_reply(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # Check current user has bookmark
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    if "8" not in current_user[0].get("bookmarks", []):
        return 0.0, "Backend: currentUser.bookmarks should contain '8'"

    # Check post 8 has the comments with reply chain
    post_8 = final_state.get("post_8")
    if not isinstance(post_8, list) or len(post_8) == 0:
        return 0.0, "Post 8 not found in backend"
    post = post_8[0]

    comments = post.get("comments", [])
    nice_comments = [c for c in comments if isinstance(c.get("content"), str) and c["content"].strip().lower() == "nice"]
    if len(nice_comments) < 2:
        return 0.0, f"Backend: Post 8 has {len(nice_comments)} 'nice' comments, expected 2"

    # Check that one comment has parentId pointing to another (reply chain)
    nice_comment_ids = {c.get("_id") for c in nice_comments}
    has_reply = any(c.get("parentId") and c.get("parentId") in nice_comment_ids for c in nice_comments)
    if not has_reply:
        return 0.0, "Backend: No reply found - one 'nice' comment should have parentId pointing to the other"

    return 1.0, "Backend: Post 8 bookmarked with comment reply chain"


def _validate_frontend_bookmark_album_comment_reply(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    page_requirements = (
        ("page", "album"),
        ("previousPage", "profile"),
        ("profileView", "bookmarks"),
        ("albumOwnerId", "0"),
    )
    for field, expected in page_requirements:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if not final_state.get("activeAlbumId"):
        return 0.0, "activeAlbumId missing while viewing bookmarks"
    if final_state.get("activePostId") != "8":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '8'"

    return 1.0, "Album bookmarks UI state validated for post 8"


_validate_bookmark_album_comment_reply: ValidateTask = {
    "state_key": {
        "post_8": {"collection": "posts", "filter": {"_id": "8"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_album_comment_reply,
    "validate_frontend": _validate_frontend_bookmark_album_comment_reply,
}


# =============================================================================
# BATCH 5: Album & Complex Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: create-album-add-v2
# -----------------------------------------------------------------------------


def _validate_backend_create_album_add(final_state: Dict[str, Any]) -> Tuple[float, str]:
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"

    if len(posts) < 2:
        return 0.0, f"Expected 2 posts, got {len(posts)}"

    for post in posts:
        pid = post.get("_id")
        if post.get("bookmarks") != 1:
            return 0.0, f"Backend: Post {pid} bookmarks={post.get('bookmarks')} expected 1"

    return 1.0, "Backend: Posts 1 and 2 bookmarked"


def _validate_frontend_create_album_add(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Created album while browsing explore feed"


_validate_create_album_add: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["1", "2"]}}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_create_album_add,
    "validate_frontend": _validate_frontend_create_album_add,
}


# -----------------------------------------------------------------------------
# Task: open-album-watch-video-v2
# -----------------------------------------------------------------------------


def _validate_backend_open_album_watch_video(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for video watching"


def _validate_frontend_open_album_watch_video(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "album":
        return 0.0, f"page={final_state.get('page')} expected 'album'"
    if final_state.get("previousPage") != "profile":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'profile'"
    if final_state.get("activeAlbumId") != "1764819999139-kaqa0ell41o":
        return 0.0, f"activeAlbumId={final_state.get('activeAlbumId')} expected '1764819999139-kaqa0ell41o'"
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused after watching album video"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching album video"
    return 1.0, "Opened an album, played post 1, and watched it to completion"


_validate_open_album_watch_video: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_album_watch_video,
    "validate_frontend": _validate_frontend_open_album_watch_video,
}


# -----------------------------------------------------------------------------
# Task: remove-bookmarks-in-album-v2
# -----------------------------------------------------------------------------


def _validate_backend_remove_bookmarks_in_album(final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"

    bookmarks = current_user[0].get("bookmarks", [])
    for bid in ["4", "7", "8", "9", "12"]:
        if bid in bookmarks:
            return 0.0, f"Backend: Bookmark {bid} should have been removed"
    return 1.0, "Backend: Bookmarks removed"


def _validate_frontend_remove_bookmarks_in_album(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "album":
        return 0.0, f"page={final_state.get('page')} expected 'album'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null (modal closed)"
    return 1.0, "Album page with modal closed after unbookmarking"


_validate_remove_bookmarks_in_album: ValidateTask = {
    "state_key": {
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_remove_bookmarks_in_album,
    "validate_frontend": _validate_frontend_remove_bookmarks_in_album,
}


# -----------------------------------------------------------------------------
# Task: edit-album-collection-v2
# -----------------------------------------------------------------------------

ALBUM_EDIT_TARGET_ID = "album-0"
ALBUM_EDIT_TARGET_NAME = "私密收藏"
ALBUM_EDIT_TARGET_DESCRIPTION = "这是我的私密专辑"


def _validate_backend_edit_album_collection(final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    albums = current_user[0].get("albums", [])
    album = next((a for a in albums or [] if a.get("_id") == ALBUM_EDIT_TARGET_ID), None)
    if not album:
        return 0.0, f"Backend: Album '{ALBUM_EDIT_TARGET_ID}' not found for current user"
    if album.get("name") != ALBUM_EDIT_TARGET_NAME:
        return 0.0, f"Backend: Album name='{album.get('name')}' expected '{ALBUM_EDIT_TARGET_NAME}'"
    if album.get("description") != ALBUM_EDIT_TARGET_DESCRIPTION:
        return 0.0, (f"Backend: Album description='{album.get('description')}' expected '{ALBUM_EDIT_TARGET_DESCRIPTION}'")
    if album.get("isPublic") is not False:
        return 0.0, f"Backend: Album isPublic={album.get('isPublic')} expected False"
    return 1.0, "Backend: Album renamed, updated description, and set to private"


def _validate_frontend_edit_album_collection(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    requirements = (
        ("page", "album"),
        ("previousPage", "profile"),
        ("profileView", "bookmarks"),
        ("profileUserId", "0"),
        ("albumOwnerId", "0"),
    )
    for field, expected in requirements:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if final_state.get("activeAlbumId") not in (ALBUM_EDIT_TARGET_ID, "album-0"):
        return 0.0, f"activeAlbumId={final_state.get('activeAlbumId')} expected '{ALBUM_EDIT_TARGET_ID}'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null"
    return 1.0, "Album editor open for the current user's bookmarks collection"


_validate_edit_album_collection: ValidateTask = {
    "state_key": {
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_edit_album_collection,
    "validate_frontend": _validate_frontend_edit_album_collection,
}


# -----------------------------------------------------------------------------
# Task: draft-article-v2
# -----------------------------------------------------------------------------


def _validate_backend_draft_article(final_state: Dict[str, Any]) -> Tuple[float, str]:
    drafts = final_state.get("drafts")
    if not isinstance(drafts, list):
        return 0.0, "Backend: drafts array missing"

    for draft in drafts:
        if draft.get("title") == "Hi" and draft.get("content") == "wow" and draft.get("type") == "article":
            return 1.0, "Backend: Article draft 'Hi' with content 'wow' saved"

    return 0.0, "Backend: No article draft with title 'Hi' and content 'wow' found"


def _validate_frontend_draft_article(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("creativePublishTab") != "article":
        return 0.0, f"creativePublishTab={final_state.get('creativePublishTab')} expected 'article'"
    if final_state.get("creativeView") not in ("text-editor", "dashboard"):
        return 0.0, f"creativeView={final_state.get('creativeView')} expected 'text-editor' or 'dashboard'"

    return 1.0, "Article editor UI state validated"


_validate_draft_article: ValidateTask = {
    "state_key": {
        "drafts": {"collection": "drafts", "filter": {"userId": "0"}},
    },
    "validate_backend": _validate_backend_draft_article,
    "validate_frontend": _validate_frontend_draft_article,
}


# -----------------------------------------------------------------------------
# Task: edit-draft-v2
# -----------------------------------------------------------------------------


def _validate_backend_edit_draft(final_state: Dict[str, Any]) -> Tuple[float, str]:
    drafts = final_state.get("drafts")
    if not isinstance(drafts, list):
        return 0.0, "Backend: drafts array missing"

    for draft in drafts:
        if not isinstance(draft, dict):
            continue
        title = (draft.get("title") or "").strip()
        content = (draft.get("content") or "").strip()
        if (
            draft.get("type") == "article"
            and draft.get("userId") == "0"
            and title.lower() == "new draft"
            and content.lower() == "new body"
        ):
            return 1.0, "Backend: Article draft updated to 'new draft'"

    return 0.0, "Backend: Edited article draft with title 'new draft' not found"


def _validate_frontend_edit_draft(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("creativePublishTab") != "article":
        return 0.0, f"creativePublishTab={final_state.get('creativePublishTab')} expected 'article'"
    if final_state.get("creativeView") != "dashboard":
        return 0.0, f"creativeView={final_state.get('creativeView')} expected 'dashboard'"
    return 1.0, "Edited draft saved while viewing the creative dashboard"


_validate_edit_draft: ValidateTask = {
    "state_key": {
        "drafts": {"collection": "drafts", "filter": {"userId": "0"}},
    },
    "validate_backend": _validate_backend_edit_draft,
    "validate_frontend": _validate_frontend_edit_draft,
}


# =============================================================================
# BATCH 6: Search & Multi-Action Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: clear-search-history-v2
# -----------------------------------------------------------------------------


def _validate_backend_clear_search_history(final_state: Dict[str, Any]) -> Tuple[float, str]:
    history = final_state.get("searchHistory")
    if history is None:
        return 1.0, "Backend: Search history cleared"
    if not isinstance(history, list):
        return 0.0, "Backend: searchHistory is not a list"
    if history:
        return 0.0, f"Backend: searchHistory still has {len(history)} entries"
    return 1.0, "Backend: Search history cleared"


def _validate_frontend_clear_search_history(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    if final_state.get("previousPage") != "search":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'search'"
    if final_state.get("searchQuery"):
        return 0.0, f"searchQuery='{final_state.get('searchQuery')}' expected empty string"
    return 1.0, "Cleared search history while remaining on explore feed"


_validate_clear_search_history: ValidateTask = {
    "state_key": {
        "searchHistory": {"collection": "searchHistory", "filter": {"userId": "0"}},
    },
    "validate_backend": _validate_backend_clear_search_history,
    "validate_frontend": _validate_frontend_clear_search_history,
}


# -----------------------------------------------------------------------------
# Task: search-and-like-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_and_like(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user1 = user_1[0]
    if user1.get("likeCount") != 1:
        return 0.0, f"Backend: User 1 likeCount={user1.get('likeCount')} expected 1"

    return 1.0, "Backend: Searched and liked post 1"


def _validate_frontend_search_and_like(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    search_query = final_state.get("searchQuery")
    active_post = final_state.get("activePostId")
    if search_query != "手势舞一枚" and active_post != "1":
        return 0.0, f"searchQuery={search_query} or activePostId={active_post} expected search '手势舞一枚' or post '1' opened"
    return 1.0, "Searched and liked post 1"


_validate_search_and_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_search_and_like,
    "validate_frontend": _validate_frontend_search_and_like,
}


# -----------------------------------------------------------------------------
# Task: search-user-and-like-all-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_user_and_like_all(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # Check user 2 (妹妹宝) has likeCount == 3
    user_2 = final_state.get("user_2")
    if not isinstance(user_2, list) or len(user_2) == 0:
        return 0.0, "User 2 not found in backend"
    user = user_2[0]
    if user.get("likeCount") != 3:
        return 0.0, f"Backend: User 2 likeCount={user.get('likeCount')} expected 3"

    # Check current user has liked posts 12, 23, 24
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    liked = current_user[0].get("liked", [])
    expected_likes = {"12", "23", "24"}
    if not expected_likes.issubset(set(liked)):
        return 0.0, f"Backend: currentUser.liked={liked} should contain ['12', '23', '24']"

    # Check that posts 12, 23, 24 each have 1 like
    posts_to_check = [("post_12", "12"), ("post_23", "23"), ("post_24", "24")]
    for post_key, post_id in posts_to_check:
        post_data = final_state.get(post_key)
        if isinstance(post_data, list) and len(post_data) > 0:
            if post_data[0].get("likes") != 1:
                return 0.0, f"Backend: Post {post_id} likes={post_data[0].get('likes')} expected 1"

    return 1.0, "Backend: Searched user 2 and liked all their posts"


def _validate_frontend_search_user_and_like_all(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user navigated to user 2's (妹妹宝) profile page
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "2":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '2' (妹妹宝's profile)"
    # After closing all modals, activePostId should be null
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null (all modals closed)"
    return 1.0, "On user 2's profile page with all modals closed after liking posts"


_validate_search_user_and_like_all: ValidateTask = {
    "state_key": {
        "post_12": {"collection": "posts", "filter": {"_id": "12"}},
        "post_23": {"collection": "posts", "filter": {"_id": "23"}},
        "post_24": {"collection": "posts", "filter": {"_id": "24"}},
        "user_2": {"collection": "users", "filter": {"_id": "2"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_user_and_like_all,
    "validate_frontend": _validate_frontend_search_user_and_like_all,
}


# -----------------------------------------------------------------------------
# Task: search-like-unbookmark-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_like_unbookmark(final_state: Dict[str, Any]) -> Tuple[float, str]:
    # Check that post 1 has 1 like
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    if post_1[0].get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post_1[0].get('likes')} expected 1"

    # Check that current user has unbookmarked the post (not in bookmarks)
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    bookmarks = current_user[0].get("bookmarks", [])
    if "1" in bookmarks:
        return 0.0, f"Backend: Post 1 still in currentUser.bookmarks={bookmarks}, should be removed"

    return 1.0, "Backend: Post 1 has 1 like and is unbookmarked"


def _validate_frontend_search_like_unbookmark(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("previousPage", "search"),
        ("profileView", "bookmarks"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null (modal closed)"
    return 1.0, "Profile bookmarks view with modal closed after unbookmarking"


_validate_search_like_unbookmark: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_like_unbookmark,
    "validate_frontend": _validate_frontend_search_like_unbookmark,
}


# -----------------------------------------------------------------------------
# Task: search-history-like-v2
# -----------------------------------------------------------------------------

SEARCH_HISTORY_QUERY = "🍂秋天落叶拍照姿势"


def _validate_backend_search_history_like(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_data = final_state.get("post_3")
    if not isinstance(post_data, list) or len(post_data) == 0:
        return 0.0, "Post 3 not found in backend"
    post = post_data[0]
    if post.get("likes", 0) < 1:
        return 0.0, f"Backend: Post 3 likes={post.get('likes')} expected at least 1"
    if post.get("bookmarks", 0) < 1:
        return 0.0, f"Backend: Post 3 bookmarks={post.get('bookmarks')} expected at least 1"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    user = current_user[0]
    liked = user.get("liked", [])
    if "3" not in liked:
        return 0.0, f"Backend: currentUser.liked={liked} expected to include '3'"
    bookmarks = user.get("bookmarks", [])
    if "3" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks={bookmarks} expected to include '3'"

    return 1.0, "Backend: Liked post 3 from search history"


def _validate_frontend_search_history_like(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "search":
        return 0.0, f"page={final_state.get('page')} expected 'search'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("searchQuery") != SEARCH_HISTORY_QUERY:
        return 0.0, f"searchQuery='{final_state.get('searchQuery')}' expected '{SEARCH_HISTORY_QUERY}'"
    if final_state.get("activePostId") != "3":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '3'"
    return 1.0, "Liked bookmarked post 3 while searching via history entry"


_validate_search_history_like: ValidateTask = {
    "state_key": {
        "post_3": {"collection": "posts", "filter": {"_id": "3"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_history_like,
    "validate_frontend": _validate_frontend_search_history_like,
}


# -----------------------------------------------------------------------------
# Task: advanced-filter-search-follow-v2
# -----------------------------------------------------------------------------

ADVANCED_SEARCH_QUERY = "咖啡"
ADVANCED_FILTERS_EXPECTED = {
    "sortBy": "mostLikes",
    "noteType": "image",
    "publishTime": "week",
    "searchScope": "following",
    "location": "any",
}
ADVANCED_TARGET_USER_ID = "18"


def _validate_backend_advanced_filter_search_follow(final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following", [])
    if not isinstance(following, list) or ADVANCED_TARGET_USER_ID not in following:
        return 0.0, (f"Backend: currentUser.following={following} expected to include '{ADVANCED_TARGET_USER_ID}'")

    user_18 = final_state.get("user_18")
    if not isinstance(user_18, list) or len(user_18) == 0:
        return 0.0, "User 18 not found in backend"
    followers = user_18[0].get("followers", [])
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 18 followers={followers} expected to include '0'"

    return 1.0, "Backend: Followed user 18 after applying advanced filters"


def _validate_frontend_advanced_filter_search_follow(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    filters = final_state.get("searchAdvancedFilters")
    if not isinstance(filters, dict):
        return 0.0, "searchAdvancedFilters missing from UI state"
    for key, expected in ADVANCED_FILTERS_EXPECTED.items():
        value = filters.get(key)
        if value != expected:
            return 0.0, f"searchAdvancedFilters.{key}={value} expected '{expected}'"

    page = final_state.get("page")
    if page == "search":
        expectations = (
            ("previousPage", "explore"),
            ("searchQuery", ADVANCED_SEARCH_QUERY),
            ("searchType", "user"),
        )
        for field, expected in expectations:
            value = final_state.get(field)
            if value != expected:
                return 0.0, f"{field}={value} expected '{expected}'"
        return 1.0, "Remained on search page with filters applied while following the user"

    if page == "profile":
        if final_state.get("profileUserId") != ADVANCED_TARGET_USER_ID:
            return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '{ADVANCED_TARGET_USER_ID}'"
        if final_state.get("previousPage") != "search":
            return 0.0, f"previousPage={final_state.get('previousPage')} expected 'search'"
        return 1.0, "Viewing followed user's profile after advanced search follow"

    return 0.0, f"page={page} expected 'search' or 'profile' after advanced search follow"


_validate_advanced_filter_search_follow: ValidateTask = {
    "state_key": {
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
        "user_18": {"collection": "users", "filter": {"_id": ADVANCED_TARGET_USER_ID}},
    },
    "validate_backend": _validate_backend_advanced_filter_search_follow,
    "validate_frontend": _validate_frontend_advanced_filter_search_follow,
}


# -----------------------------------------------------------------------------
# Task: search-own-profile-reply-v2
# -----------------------------------------------------------------------------


def _validate_backend_search_own_profile_reply(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post = post_2[0]
    comments = post.get("comments", [])
    has_reply = any(
        isinstance(c.get("content"), str) and c["content"].strip().lower() == "nice" and c.get("parentId") == "c2"
        for c in comments
    )
    if not has_reply:
        return 0.0, "Backend: Post 2 is missing reply 'nice' to comment c2"

    return 1.0, "Backend: Reply added to post 2"


def _validate_frontend_search_own_profile_reply(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("previousPage", "search"),
        ("activePostId", "2"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Own profile page with post 2 modal opened for reply"


_validate_search_own_profile_reply: ValidateTask = {
    "state_key": {
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
    },
    "validate_backend": _validate_backend_search_own_profile_reply,
    "validate_frontend": _validate_frontend_search_own_profile_reply,
}


# =============================================================================
# BATCH 7: Dark Mode Combination Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: dark-mode-filter-v2
# -----------------------------------------------------------------------------


def _validate_backend_dark_mode_filter(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for dark mode filter"


def _validate_frontend_dark_mode_filter(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"
    if final_state.get("feedFilter") != "校园日常":
        return 0.0, f"feedFilter={final_state.get('feedFilter')} expected '校园日常'"
    return 1.0, "Dark mode enabled and feed filter set to 校园日常"


_validate_dark_mode_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_dark_mode_filter,
    "validate_frontend": _validate_frontend_dark_mode_filter,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-like-v2
# -----------------------------------------------------------------------------


def _validate_backend_dark_mode_like(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    return 1.0, "Backend: Post 1 liked"


def _validate_frontend_dark_mode_like(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    expectations = (
        ("page", "explore"),
        ("previousPage", "explore"),
        ("themeMode", "dark"),
    )
    for field, expected in expectations:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Dark mode stays enabled while liking post 1 on explore"


_validate_dark_mode_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_dark_mode_like,
    "validate_frontend": _validate_frontend_dark_mode_like,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-notif-like-v2
# -----------------------------------------------------------------------------


def _validate_backend_dark_mode_notif_like(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    comments = post.get("comments", [])
    comment = next((c for c in comments if c.get("_id") == "c1"), None)
    if not comment:
        return 0.0, "Comment c1 not found on post 1"

    # Get current user's liked items
    current_user_data = final_state.get("current_user")
    if not isinstance(current_user_data, list) or len(current_user_data) == 0:
        return 0.0, "Current user not found in backend"
    current_user_liked = current_user_data[0].get("liked", [])
    if not isinstance(current_user_liked, list):
        current_user_liked = []

    if "c1" not in current_user_liked:
        return 0.0, f"Backend: Comment c1 should be in currentUser.liked, got {current_user_liked}"

    return 1.0, "Backend: Comment c1 liked"


def _validate_frontend_dark_mode_notif_like(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"
    if final_state.get("page") != "explore" or final_state.get("previousPage") != "notifications":
        return 0.0, (
            f"page={final_state.get('page')} previousPage={final_state.get('previousPage')} expected explore/notifications"
        )
    return 1.0, "Handled notification and returned to explore with dark mode on"


_validate_dark_mode_notif_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_dark_mode_notif_like,
    "validate_frontend": _validate_frontend_dark_mode_notif_like,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-search-watch-v2
# -----------------------------------------------------------------------------


def _validate_backend_dark_mode_search_watch(final_state: Dict[str, Any]) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search and watch"


def _validate_frontend_dark_mode_search_watch(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"

    expected = (("page", "search"), ("previousPage", "explore"), ("searchQuery", "oo"))
    for field, value in expected:
        current = final_state.get(field)
        if current != value:
            return 0.0, f"{field}={current} expected '{value}'"
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching search result video"
    return 1.0, "Searched for 'oo', switched to dark mode, and watched post 1"


_validate_dark_mode_search_watch: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_dark_mode_search_watch,
    "validate_frontend": _validate_frontend_dark_mode_search_watch,
}


# -----------------------------------------------------------------------------
# Task: filter-comment-profile-dark-v2
# -----------------------------------------------------------------------------


def _validate_backend_filter_comment_profile_dark(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post = post_2[0]
    comments = post.get("comments", [])
    found = any("nice" in c.get("content", "").lower() for c in comments)
    if not found:
        return 0.0, "Backend: Comment 'nice' not found on post 2"

    return 1.0, "Backend: Comment added to post 2"


def _validate_frontend_filter_comment_profile_dark(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    expectations = (
        ("page", "profile"),
        ("previousPage", "explore"),
        ("feedFilter", "萌宠日常"),
        ("profileUserId", "0"),
        ("themeMode", "dark"),
    )
    for field, expected in expectations:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Profile view reflects 萌宠日常 filter in dark mode"


_validate_filter_comment_profile_dark: ValidateTask = {
    "state_key": {
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
    },
    "validate_backend": _validate_backend_filter_comment_profile_dark,
    "validate_frontend": _validate_frontend_filter_comment_profile_dark,
}


# -----------------------------------------------------------------------------
# Task: like-search-follow-dark-v2
# -----------------------------------------------------------------------------


def _validate_backend_like_search_follow_dark(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    user_2 = final_state.get("user_2")
    if not isinstance(user_2, list) or len(user_2) == 0:
        return 0.0, "User 2 not found in backend"
    user2 = user_2[0]
    followers = user2.get("followers")
    if not isinstance(followers, list) or followers != ["0"]:
        return 0.0, f"Backend: User 2 followers={followers} expected ['0']"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list) or "2" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '2'"

    return 1.0, "Backend: Liked post 1 and followed user 2"


def _validate_frontend_like_search_follow_dark(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    checks = [
        ("page", "search"),
        ("previousPage", "explore"),
        ("searchQuery", "妹妹宝"),
        ("searchType", "user"),
        ("themeMode", "dark"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Liked, searched, followed user, and set dark theme"


_validate_like_search_follow_dark: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_2": {"collection": "users", "filter": {"_id": "2"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_like_search_follow_dark,
    "validate_frontend": _validate_frontend_like_search_follow_dark,
}


# =============================================================================
# BATCH 8: Complex Multi-Action Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: comprehensive-user-interaction-v2
# -----------------------------------------------------------------------------


def _validate_backend_comprehensive_user_interaction(final_state: Dict[str, Any]) -> Tuple[float, str]:
    def _get_entry(key: str, label: str) -> Tuple[Optional[Dict[str, Any]], str]:
        data = final_state.get(key)
        if not isinstance(data, list) or len(data) == 0:
            return None, f"{label} not found in backend"
        return data[0], ""

    post1, error = _get_entry("post_1", "Post 1")
    if not post1:
        return 0.0, error
    if post1.get("likes", 0) < 1:
        return 0.0, f"Backend: Post 1 likes={post1.get('likes')} expected at least 1"
    comments = post1.get("comments", [])
    new_comment = next(
        (
            c
            for c in comments
            if isinstance(c.get("content"), str) and c["content"].strip().lower() == "nice" and c.get("authorId") == "0"
        ),
        None,
    )
    if not new_comment:
        return 0.0, "Backend: Comment 'nice' from current user not found on post 1"

    post3, error = _get_entry("post_3", "Post 3")
    if not post3:
        return 0.0, error
    if post3.get("likes", 0) < 1:
        return 0.0, f"Backend: Post 3 likes={post3.get('likes')} expected at least 1"
    if post3.get("bookmarks", 0) < 1:
        return 0.0, f"Backend: Post 3 bookmarks={post3.get('bookmarks')} expected at least 1"

    current_user, error = _get_entry("current_user", "Current user")
    if not current_user:
        return 0.0, error
    liked = current_user.get("liked", [])
    if not isinstance(liked, list) or not all(pid in liked for pid in ("1", "3")):
        return 0.0, f"Backend: currentUser.liked={liked} expected to include '1' and '3'"
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list) or "3" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks={bookmarks} expected to include '3'"
    following = current_user.get("following", [])
    if not isinstance(following, list) or "1" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '1'"

    user1, error = _get_entry("user_1", "User 1")
    if not user1:
        return 0.0, error
    followers = user1.get("followers", [])
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 1 followers={followers} expected to include '0'"

    return 1.0, "Backend: Comprehensive user interaction completed"


def _validate_frontend_comprehensive_user_interaction(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    if final_state.get("previousPage") != "profile":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'profile'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null"
    return 1.0, "Returned to explore after completing comprehensive interactions"


_validate_comprehensive_user_interaction: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "post_3": {"collection": "posts", "filter": {"_id": "3"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_comprehensive_user_interaction,
    "validate_frontend": _validate_frontend_comprehensive_user_interaction,
}


# -----------------------------------------------------------------------------
# Task: cross-user-engagement-v2
# -----------------------------------------------------------------------------


def _validate_backend_cross_user_engagement(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_expectations = {
        "1": {"likes": 1},
        "2": {"likes": 1, "bookmarks": 1},
        "3": {"likes": 1},
        "4": {"likes": 1, "bookmarks": 1},
        "5": {"likes": 1},
    }

    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"

    if len(posts) < 5:
        return 0.0, f"Expected 5 posts, got {len(posts)}"

    for post in posts:
        pid = post.get("_id")
        if pid in post_expectations:
            expectations = post_expectations[pid]
            for field, expected_value in expectations.items():
                if post.get(field) != expected_value:
                    return 0.0, f"Backend: Post {pid} {field}={post.get(field)} expected {expected_value}"

    user_5 = final_state.get("user_5")
    if not isinstance(user_5, list) or len(user_5) == 0:
        return 0.0, "User 5 not found in backend"
    user5 = user_5[0]
    followers = user5.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 5 followers={followers} expected to include '0'"

    return 1.0, "Backend: Cross-user engagement completed"


def _validate_frontend_cross_user_engagement(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "5":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '5'"
    return 1.0, "Viewing user 5 profile after cross-user engagement"


_validate_cross_user_engagement: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["1", "2", "3", "4", "5"]}}},
        "user_5": {"collection": "users", "filter": {"_id": "5"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_cross_user_engagement,
    "validate_frontend": _validate_frontend_cross_user_engagement,
}


# -----------------------------------------------------------------------------
# Task: unlike-currentuser-likes-v2
# -----------------------------------------------------------------------------


def _validate_backend_unlike_currentuser_likes(final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") not in (0, None):
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 0"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    liked = current_user[0].get("liked", [])
    if not isinstance(liked, list) or liked:
        return 0.0, f"Backend: currentUser.liked={liked} expected empty list"

    return 1.0, "Backend: Unliked post 1"


def _validate_frontend_unlike_currentuser_likes(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("profileView", "likes"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "On profile likes view after unliking post"


_validate_unlike_currentuser_likes: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_unlike_currentuser_likes,
    "validate_frontend": _validate_frontend_unlike_currentuser_likes,
}


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================
#
# Task Mapping Structure:
# - Tasks 1-20 (current): Use _validate_generated_task_X_... functions
#   These are defined as aliases at the bottom of the file (lines ~7515-7534)
#   and use Backend ABC validation (different signature than ValidateTask)
# - Tasks 21-60: Use _validate_generated_task_X_... functions in this dict
# - Legacy tasks (renamed files): Use _validate_<name> functions (lines 2755-2768)
#   These are the old tasks that had their task- prefix removed
#
# File naming convention:
# - task-1 through task-20: Current tasks matching xhs-generated-tasks.json
# - Files without task- prefix: Legacy tasks (old numbering system)
#
# REWARD_FUNCTIONS_XIAOHONGSHU_V2 dictionary moved to end of file (after all function definitions)
# to avoid NameError when functions are referenced before they are defined

# =============================================================================
# BATCH: Agent Testing Tasks (Tasks 1-20)
# =============================================================================
# These tasks use a combined validation approach with a Backend ABC.
# We create adapters to bridge them with the existing ValidateTask structure.

from .backend import Backend


def _get_current_user(backend: Backend) -> Dict[str, Any]:
    """Get current user from backend."""
    current_user_id = backend.query({"collection": "currentUser", "filter": {}})[0].get("currentUserId")
    result = backend.query({"collection": "users", "filter": {"_id": current_user_id}})
    if isinstance(result, list) and len(result) > 0:
        return result[0]
    if isinstance(result, dict):
        return result
    raise ValueError(f"Current user {current_user_id} not found in backend")


def _get_post(backend: Backend, post_id: str) -> Dict[str, Any]:
    """Get post from backend."""
    result = backend.query({"collection": "posts", "filter": {"_id": post_id}})
    if isinstance(result, list) and len(result) > 0:
        return result[0]
    if isinstance(result, dict):
        return result
    raise ValueError(f"Post {post_id} not found in backend")


def _get_comments_for_post(backend: Backend, post_id: str) -> list[Dict[str, Any]]:
    """Get all comments for a post."""
    result = backend.query({"collection": "comments", "filter": {"postId": post_id}})
    if isinstance(result, list):
        return result
    return []


def _get_user(backend: Backend, user_id: str) -> Dict[str, Any]:
    """Get user from backend."""
    result = backend.query({"collection": "users", "filter": {"_id": user_id}})
    if isinstance(result, list) and len(result) > 0:
        return result[0]
    if isinstance(result, dict):
        return result
    raise ValueError(f"User {user_id} not found in backend")


def _check_topic_relevance(post: Dict[str, Any], topic_area: str, keywords: Optional[List[str]] = None) -> bool:
    """Check if a post is relevant to a topic area."""
    if keywords is None:
        keywords = TOPIC_KEYWORDS.get(topic_area.lower(), [topic_area.lower()])

    title = (post.get("title", "") or "").lower()
    caption = (post.get("caption", "") or "").lower()
    tags = [tag.lower() for tag in post.get("tags", [])]
    location = (post.get("location", "") or "").lower()

    content = f"{title} {caption} {location} {' '.join(tags)}"
    return any(keyword.lower() in content for keyword in keywords)


def _check_user_category_relevance(user: Dict[str, Any], topic_area: str) -> bool:
    """Check if a user's category is relevant to a topic area."""
    category = (user.get("category", "") or "").lower()
    bio = (user.get("bio", "") or "").lower()
    keywords = TOPIC_KEYWORDS.get(topic_area.lower(), [topic_area.lower()])

    return any(keyword in category or keyword in bio for keyword in keywords)


# =============================================================================
# Topic Keywords - Centralized Keyword Dictionary
# =============================================================================

# Comprehensive keyword lists for topic relevance checking
# Used by both post content and user category/bio checking
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "fitness": [
        "fitness",
        "workout",
        "exercise",
        "gym",
        "training",
        "motivation",
        "transformation",
        "beginner",
        "yoga",
        "instructor",
        "运动",
        "健身",
        "锻炼",
        "运动健身",
        "健身运动",
        "减脂",
        "增肌",
        "瑜伽",
        "跑步",
        "健身教练",
        "健身动机",
        "健身转型",
        "新手健身",
        "瑜伽入门",
        "瑜伽教练",
    ],
    "beauty": [
        "beauty",
        "makeup",
        "skincare",
        "cosmetic",
        "nail",
        "hair",
        "tutorial",
        "reviewer",
        "美容",
        "化妆",
        "护肤",
        "美妆",
        "彩妆",
        "美甲",
        "发型",
        "美容护肤",
        "化妆品",
        "护肤品",
        "美发",
        "化妆教程",
        "护肤教程",
        "美甲教程",
        "美妆博主",
        "护肤博主",
    ],
    "food": [
        "food",
        "recipe",
        "cooking",
        "meal",
        "dining",
        "chef",
        "healthy",
        "meal prep",
        "dessert",
        "baking",
        "quick",
        "easy",
        "美食",
        "食谱",
        "烹饪",
        "料理",
        "菜谱",
        "做饭",
        "下厨",
        "餐厅",
        "小吃",
        "甜品",
        "烘焙",
        "家常菜",
        "健康美食",
        "健康食谱",
        "减脂餐",
        "快手菜",
        "简单料理",
        "美食博主",
    ],
    "travel": [
        "travel",
        "trip",
        "vacation",
        "destination",
        "location",
        "旅游",
        "旅行",
        "景点",
        "出游",
        "度假",
        "攻略",
        "游记",
        "自由行",
        "旅行攻略",
        "旅游攻略",
        "打卡",
        "旅行地",
        "旅游地",
        "景点推荐",
    ],
    "home": [
        "home",
        "interior",
        "decor",
        "furniture",
        "workspace",
        "office",
        "desk",
        "organization",
        "garden",
        "gardening",
        "plant",
        "balcony",
        "kitchen",
        "storage",
        "家居",
        "装修",
        "装饰",
        "家装",
        "室内",
        "家具",
        "收纳",
        "整理",
        "布置",
        "软装",
        "硬装",
        "工作区",
        "办公区",
        "办公桌",
        "书桌",
        "书房",
        "工作空间",
        "种植",
        "植物",
        "园艺",
        "阳台",
        "厨房",
        "储物",
        "组织",
        "整理师",
    ],
    "fashion": [
        "fashion",
        "outfit",
        "style",
        "clothing",
        "casual",
        "street style",
        "capsule wardrobe",
        "versatile",
        "winter",
        "coat",
        "时尚",
        "穿搭",
        "服装",
        "搭配",
        "穿衣",
        "潮流",
        "时装",
        "服饰",
        "穿搭分享",
        "ootd",
        "日常穿搭",
        "街头风",
        "胶囊衣橱",
        "百搭",
        "冬季穿搭",
        "外套",
    ],
    "art": [
        "art",
        "drawing",
        "painting",
        "illustration",
        "photography",
        "photo",
        "DIY",
        "craft",
        "creative",
        "technique",
        "艺术",
        "绘画",
        "插画",
        "画画",
        "手绘",
        "水彩",
        "油画",
        "素描",
        "创作",
        "设计",
        "艺术家",
        "摄影",
        "拍照",
        "手工",
        "创意",
        "艺术技巧",
        "摄影技巧",
        "拍照技巧",
        "摄影师",
    ],
    "pets": [
        "pet",
        "dog",
        "cat",
        "animal",
        "宠物",
        "狗",
        "猫",
        "养宠",
        "萌宠",
        "宠物日常",
        "宠物用品",
        "宠物护理",
        "宠物训练",
        "宠物建议",
        "宠物知识",
        "宠物博主",
    ],
    "wellness": [
        "wellness",
        "meditation",
        "mindfulness",
        "wellbeing",
        "健康",
        "冥想",
        "养生",
        "保健",
        "身心健康",
        "心理健康",
        "放松",
        "减压",
        "瑜伽",
        "正念",
        "自我关怀",
        "健康生活",
        "健康博主",
    ],
    "lifestyle": [
        "lifestyle",
        "routine",
        "daily",
        "life",
        "eco",
        "sustainable",
        "productivity",
        "organization",
        "morning",
        "work-life",
        "career",
        "balance",
        "生活方式",
        "日常",
        "生活",
        "日常分享",
        "生活记录",
        "生活vlog",
        "生活碎片",
        "环保",
        "可持续",
        "可持续发展",
        "绿色生活",
        "效率",
        "整理",
        "组织",
        "早晨",
        "清晨",
        "晨间",
        "工作生活",
        "职业",
        "平衡",
    ],
    "education": [
        "education",
        "study",
        "learning",
        "tutorial",
        "productivity",
        "technique",
        "tip",
        "教育",
        "学习",
        "教程",
        "知识",
        "学习分享",
        "学习方法",
        "学习笔记",
        "读书",
        "阅读",
        "课程",
        "效率",
        "学习技巧",
        "学习建议",
        "学习tips",
    ],
    "settings": [],
    "general": [],
    "culture": [
        "book",
        "reading",
        "literature",
        "书籍",
        "阅读",
        "文学",
        "读书",
        "书单",
        "读后感",
        "文学作品",
        "小说",
        "阅读分享",
        "好书推荐",
        "文学推荐",
        "读书博主",
    ],
}

# Task-specific keyword lists for specialized validation
TASK_SPECIFIC_KEYWORDS: Dict[str, List[str]] = {
    "skincare": ["skincare", "护肤", "美容", "routine"],
    "fashion": ["时尚", "穿搭", "搭配", "服装", "服饰", "穿衣", "ootd"],
    "hair_beauty": ["发型", "美发", "教程", "头发", "编发", "造型", "美容", "化妆", "美妆", "护肤"],
    "healthy_food": ["健康", "食谱", "健康食谱", "减脂餐", "低卡", "营养", "轻食", "健康饮食", "健康美食", "健康料理"],
    "dessert": ["dessert", "cooking", "recipe", "甜品", "烘焙", "制作"],
    "productivity": ["productivity", "organization", "organize", "效率", "整理", "组织"],
    "shanghai": ["上海", "shanghai"],
    "eco": ["eco", "sustainable", "sustainability", "green", "环保", "可持续", "可持续发展", "绿色", "低碳", "生态"],
    "gardening": ["gardening", "plant", "garden", "种植", "植物", "园艺"],
    "literature": [
        "book",
        "reading",
        "literature",
        "书籍",
        "阅读",
        "文学",
        "读书",
        "书单",
        "读后感",
        "文学作品",
        "小说",
        "阅读分享",
    ],
    "makeup": ["makeup", "tutorial", "化妆", "教程", "美妆", "彩妆"],
    "morning": ["morning", "routine", "早晨", "清晨", "晨间", "早起", "晨练", "晨间routine"],
    "workspace": [
        "desk setup",
        "desk",
        "home office",
        "workspace",
        "office",
        "办公桌",
        "书桌",
        "工作区",
        "办公区",
        "书房",
        "工作空间",
    ],
    "quick_recipe": ["quick", "easy", "recipe", "fast", "简单", "快速", "食谱", "快手"],
    "beginner_yoga": [
        "beginner",
        "yoga",
        "beginner yoga",
        "新手",
        "瑜伽",
        "初学者",
        "入门",
        "基础瑜伽",
        "新手瑜伽",
        "瑜伽入门",
    ],
    "photography_technique": [
        "photography",
        "photo",
        "technique",
        "camera",
        "lens",
        "shutter",
        "aperture",
        "iso",
        "composition",
        "lighting",
        "摄影",
        "拍照",
        "摄影技巧",
        "摄影技术",
        "拍照技巧",
        "相机",
        "镜头",
        "构图",
        "光线",
    ],
}


def _get_current_user_safe(backend: Backend) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Safely get current user, returning (user, error_message) tuple."""
    try:
        return _get_current_user(backend), None
    except ValueError as e:
        return None, str(e)


def _check_post_contains_keywords(post: Dict[str, Any], keywords: List[str]) -> bool:
    """Check if a post's title, caption, or tags contain any of the given keywords."""
    title = (post.get("title", "") or "").lower()
    caption = (post.get("caption", "") or "").lower()
    tags = [tag.lower() for tag in post.get("tags", [])]

    content = f"{title} {caption} {' '.join(tags)}"
    return any(keyword.lower() in content for keyword in keywords)


def _count_topic_relevant_users(backend: Backend, user_ids: List[str], topic_area: str) -> int:
    """Count users that are relevant to a topic area."""
    count = 0
    for user_id in user_ids:
        try:
            user = _get_user(backend, user_id)
            if _check_user_category_relevance(user, topic_area):
                count += 1
        except ValueError:
            continue
    return count


def _count_topic_relevant_posts(
    backend: Backend, post_ids: List[str], topic_area: str, additional_keywords: Optional[List[str]] = None
) -> int:
    """Count posts that are relevant to a topic area, optionally with additional keywords."""
    count = 0
    for post_id in post_ids:
        try:
            post = _get_post(backend, post_id)
            if not _check_topic_relevance(post, topic_area):
                continue
            if additional_keywords and not _check_post_contains_keywords(post, additional_keywords):
                continue
            count += 1
        except ValueError:
            continue
    return count


def _count_posts_in_bookmarks_and_albums(
    backend: Backend, current_user: Dict[str, Any], topic_area: str, additional_keywords: Optional[List[str]] = None
) -> int:
    """Count topic-relevant posts in bookmarks and albums combined."""
    count = 0

    # Check bookmarks
    bookmarks = current_user.get("bookmarks", [])
    if isinstance(bookmarks, list):
        count += _count_topic_relevant_posts(backend, bookmarks, topic_area, additional_keywords)

    # Check albums/collections
    albums = current_user.get("albums", [])
    if isinstance(albums, list):
        for album in albums:
            post_ids = album.get("postIds", [])
            if isinstance(post_ids, list):
                count += _count_topic_relevant_posts(backend, post_ids, topic_area, additional_keywords)

    return count


def _check_search_history(backend: Backend, current_user_id: str, keywords: List[str]) -> Tuple[bool, List[str]]:
    """Check if search history contains any of the given keywords. Returns (found, queries)."""
    search_history = backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "") for entry in search_history if isinstance(entry, dict)]
    has_search = any(any(keyword.lower() in query.lower() for keyword in keywords) for query in search_queries)
    return has_search, search_queries


def _has_comment_on_topic(backend: Backend, current_user_id: str, topic_area: str, min_count: int = 1) -> Tuple[bool, int]:
    """Check if user has commented on topic-relevant posts. Returns (has_comment, count)."""
    user_comments = backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    if not isinstance(user_comments, list):
        return False, 0

    count = 0
    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(backend, post_id)
            if _check_topic_relevance(post, topic_area):
                count += 1
        except ValueError:
            continue

    return count >= min_count, count


def _find_album_with_topic_posts(
    backend: Backend,
    albums: List[Dict[str, Any]],
    topic_area: str,
    min_posts: int,
    additional_keywords: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Find an album with at least min_posts topic-relevant posts."""
    for album in albums:
        post_ids = album.get("postIds", [])
        if not isinstance(post_ids, list) or len(post_ids) < min_posts:
            continue

        count = _count_topic_relevant_posts(backend, post_ids, topic_area, additional_keywords)
        if count >= min_posts:
            return album

    return None


# =============================================================================
# Generated Tasks 1-20: From xhs-reward-functions.py the old prompts
# =============================================================================


def _validate_starting_new_fitness_routine(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I'm starting a new fitness routine and need motivation. Find...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following)}"

    # Check if followed users are fitness-related
    fitness_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "fitness"):
                fitness_following_count += 1
        except ValueError:
            continue

    if fitness_following_count < 2:
        return 0.0, f"Expected at least 2 fitness-related followed user(s), got {fitness_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are fitness-related
    fitness_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "fitness"):
                fitness_bookmarks_count += 1
        except ValueError:
            continue

    if fitness_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 fitness-related bookmarked posts, got {fitness_bookmarks_count}"

    # Check for album with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = None
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list) and len(post_ids) >= 3:
            album_found = album
            break

    if not album_found:
        return 0.0, "No album found with at least 3 posts"

    return 1.0, "Task completed successfully"


def _validate_friend_recommended_some_beauty(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My friend recommended some beauty blogger but I can't rememb...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are beauty-related
    beauty_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "beauty"):
                beauty_following_count += 1
        except ValueError:
            continue

    if beauty_following_count < 1:
        return 0.0, f"Expected at least 1 beauty-related followed user(s), got {beauty_following_count}"

    # Check liked posts count
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    if len(liked) < 2:
        return 0.0, f"Expected at least 2 liked post(s), got {len(liked)}"

    # Check if liked posts are beauty-related
    beauty_liked_count = 0
    for post_id in liked:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "beauty"):
                beauty_liked_count += 1
        except ValueError:
            continue

    if beauty_liked_count < 2:
        return 0.0, f"Expected at least 2 beauty-related liked posts, got {beauty_liked_count}"

    return 1.0, "Task completed successfully"


def _validate_this_eye_strain_getting(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate This eye strain is getting ridiculous working late nights. S..."""
    theme_mode = final_state_frontend.get("themeMode")
    if theme_mode != "dark":
        return 0.0, f"Expected themeMode='dark', got '{theme_mode}'"
    page = final_state_frontend.get("page")
    if page != "notifications":
        return 0.0, f"Expected page='notifications', got '{page}'"

    return 1.0, "Task completed successfully"


def _validate_want_learn_some_simple(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate I want to learn some simple recipes for meal prep—nothing to...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are food-related
    food_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "food"):
                food_following_count += 1
        except ValueError:
            continue

    if food_following_count < 1:
        return 0.0, f"Expected at least 1 food-related followed user(s), got {food_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are food-related
    food_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "food"):
                food_bookmarks_count += 1
        except ValueError:
            continue

    if food_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 food-related bookmarked posts, got {food_bookmarks_count}"

    # Check for album with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = None
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list) and len(post_ids) >= 3:
            album_found = album
            break

    if not album_found:
        return 0.0, "No album found with at least 3 posts"

    return 1.0, "Task completed successfully"


def _validate_redecorating_small_bedroom_and(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I'm redecorating my small bedroom and looking for space-savi...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following)}"

    # Check if followed users are home-related
    home_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "home"):
                home_following_count += 1
        except ValueError:
            continue

    if home_following_count < 2:
        return 0.0, f"Expected at least 2 home-related followed user(s), got {home_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are home-related
    home_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "home"):
                home_bookmarks_count += 1
        except ValueError:
            continue

    if home_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 home-related bookmarked posts, got {home_bookmarks_count}"

    # Check for album with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = None
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list) and len(post_ids) >= 3:
            album_found = album
            break

    if not album_found:
        return 0.0, "No album found with at least 3 posts"

    return 1.0, "Task completed successfully"


def _validate_saw_amazing_travel_photo(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Saw an amazing travel photo earlier and want to leave a nice...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on travel-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    travel_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "travel"):
                travel_comment_found = True
                break
        except ValueError:
            continue

    if not travel_comment_found:
        return 0.0, "No comment found on travel-related post"

    return 1.0, "Task completed successfully"


def _validate_need_find_some_quick(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Need to find some quick skincare routine ideas for someone w...

    Initial State Assumptions:
    - currentUser.searchHistory is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for skincare-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    skincare_keywords = ["skincare", "护肤", "美容", "routine"]
    has_skincare_search = any(any(keyword in query for keyword in skincare_keywords) for query in search_queries)
    if not has_skincare_search:
        return 0.0, f"searchHistory should contain skincare-related search terms, got: {search_queries}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 1:
        return 0.0, f"Expected at least 1 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are beauty-related
    beauty_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "beauty"):
                beauty_bookmarks_count += 1
        except ValueError:
            continue

    if beauty_bookmarks_count < 1:
        return 0.0, f"Expected at least 1 beauty-related bookmarked post(s), got {beauty_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_cat_has_been_acting(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate My cat has been acting weird lately and I want to see if oth...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are pets-related
    pets_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "pets"):
                pets_following_count += 1
        except ValueError:
            continue

    if pets_following_count < 1:
        return 0.0, f"Expected at least 1 pets-related followed user(s), got {pets_following_count}"

    # Check bookmarks or liked posts (at least 2)
    bookmarks = current_user.get("bookmarks", [])
    liked = current_user.get("liked", [])

    pets_content_count = 0
    for post_id in list(bookmarks) + list(liked):
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "pets"):
                pets_content_count += 1
        except ValueError:
            continue

    if pets_content_count < 2:
        return 0.0, f"Expected at least 2 pets-related bookmarked or liked posts, got {pets_content_count}"

    return 1.0, "Task completed successfully"


def _validate_planning_weekend_trip_and(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Planning a weekend trip to 杭州 and want authentic local food ...

    Initial State Assumptions:
    - currentUser.searchHistory is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for 杭州-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "") for entry in search_history if isinstance(entry, dict)]
    has_hangzhou_search = any("杭州" in query for query in search_queries)
    if not has_hangzhou_search:
        return 0.0, f"searchHistory should contain '杭州' in search query, got: {search_queries}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are travel-related
    travel_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "travel"):
                travel_bookmarks_count += 1
        except ValueError:
            continue

    if travel_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 travel-related bookmarked posts, got {travel_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_someone_posted_amazing_nail(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Someone posted amazing nail art that I want to try myself. F...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on beauty-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    beauty_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "beauty"):
                beauty_comment_found = True
                break
        except ValueError:
            continue

    if not beauty_comment_found:
        return 0.0, "No comment found on beauty-related post"

    return 1.0, "Task completed successfully"


def _validate_been_getting_back_into(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate I've been getting back into drawing and need some inspiratio...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following)}"

    # Check if followed users are art-related
    art_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "art"):
                art_following_count += 1
        except ValueError:
            continue

    if art_following_count < 2:
        return 0.0, f"Expected at least 2 art-related followed user(s), got {art_following_count}"

    # Check bookmarks or liked posts (at least 2)
    bookmarks = current_user.get("bookmarks", [])
    liked = current_user.get("liked", [])

    art_content_count = 0
    for post_id in list(bookmarks) + list(liked):
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "art"):
                art_content_count += 1
        except ValueError:
            continue

    if art_content_count < 2:
        return 0.0, f"Expected at least 2 art-related bookmarked or liked posts, got {art_content_count}"

    return 1.0, "Task completed successfully"


def _validate_looking_for_budget_friendly(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Looking for budget-friendly fashion inspiration since I'm tr...

    Initial State Assumptions:
    - currentUser.searchHistory is empty [] before task starts
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for fashion-related search (Chinese terms)
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "") for entry in search_history if isinstance(entry, dict)]
    fashion_keywords = ["时尚", "穿搭", "搭配", "服装", "服饰", "穿衣", "ootd"]
    has_fashion_search = any(any(keyword in query for keyword in fashion_keywords) for query in search_queries)
    if not has_fashion_search:
        return 0.0, f"searchHistory should contain fashion-related search terms (时尚, 穿搭, etc.), got: {search_queries}"

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are fashion-related
    fashion_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "fashion"):
                fashion_following_count += 1
        except ValueError:
            continue

    if fashion_following_count < 1:
        return 0.0, f"Expected at least 1 fashion-related followed user(s), got {fashion_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 2:
        return 0.0, f"Expected at least 2 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are fashion-related
    fashion_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "fashion"):
                fashion_bookmarks_count += 1
        except ValueError:
            continue

    if fashion_bookmarks_count < 2:
        return 0.0, f"Expected at least 2 fashion-related bookmarked posts, got {fashion_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_this_bright_screen_hurting(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate This bright screen is hurting my eyes during my late-night s..."""
    theme_mode = final_state_frontend.get("themeMode")
    if theme_mode != "dark":
        return 0.0, f"Expected themeMode='dark', got '{theme_mode}'"

    return 1.0, "Task completed successfully"


def _validate_workout_motivation_has_been(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My workout motivation has been lacking lately. Find some ins...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for 2 comments on fitness-related posts
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    comment_count = 0

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "fitness"):
                comment_count += 1
        except ValueError:
            continue

    if comment_count < 2:
        return 0.0, f"Expected at least 2 comments on fitness-related posts, got {comment_count}"

    return 1.0, "Task completed successfully"


def _validate_need_organize_tiny_kitchen(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Need to organize my tiny kitchen better and looking for clev...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are home-related
    home_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "home"):
                home_following_count += 1
        except ValueError:
            continue

    if home_following_count < 1:
        return 0.0, f"Expected at least 1 home-related followed user(s), got {home_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are home-related
    home_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "home"):
                home_bookmarks_count += 1
        except ValueError:
            continue

    if home_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 home-related bookmarked posts, got {home_bookmarks_count}"

    # Check for album with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = None
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list) and len(post_ids) >= 3:
            album_found = album
            break

    if not album_found:
        return 0.0, "No album found with at least 3 posts"

    return 1.0, "Task completed successfully"


def _validate_want_try_some_new(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate I want to try some new hairstyles but my hair is pretty basi...

    Initial State Assumptions:
    - currentUser.searchHistory is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for hair/beauty-related search (Chinese terms)
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "") for entry in search_history if isinstance(entry, dict)]
    hair_beauty_keywords = ["发型", "美发", "教程", "头发", "编发", "造型", "美容", "化妆", "美妆", "护肤"]
    has_hair_beauty_search = any(any(keyword in query for keyword in hair_beauty_keywords) for query in search_queries)
    if not has_hair_beauty_search:
        return (
            0.0,
            f"searchHistory should contain hair/beauty tutorial-related search terms (发型, 教程, etc.), got: {search_queries}",
        )

    # Check bookmarks OR album with beauty-related posts (at least 3)
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"

    # Check if bookmarked posts are beauty-related
    beauty_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "beauty"):
                beauty_bookmarks_count += 1
        except ValueError:
            continue

    # Check for album with at least 3 beauty-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        albums = []

    beauty_album_posts_count = 0
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list):
            for post_id in post_ids:
                try:
                    post = _get_post(final_state_backend, post_id)
                    if _check_topic_relevance(post, "beauty"):
                        beauty_album_posts_count += 1
                except ValueError:
                    continue

    # Pass if either condition is met: bookmarked posts OR album posts
    if beauty_bookmarks_count < 3 and beauty_album_posts_count < 3:
        return (
            0.0,
            f"Expected at least 3 beauty-related posts either bookmarked (got {beauty_bookmarks_count}) or in a collection (got {beauty_album_posts_count})",
        )

    return 1.0, "Task completed successfully"


def _validate_thinking_about_getting_dog(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Thinking about getting a dog and want to see what daily life...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following)}"

    # Check if followed users are pets-related
    pets_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "pets"):
                pets_following_count += 1
        except ValueError:
            continue

    if pets_following_count < 2:
        return 0.0, f"Expected at least 2 pets-related followed user(s), got {pets_following_count}"

    return 1.0, "Task completed successfully"


def _validate_someone_shared_really_creative(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Someone shared a really creative DIY project that caught my ...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on art-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    art_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "art"):
                art_comment_found = True
                break
        except ValueError:
            continue

    if not art_comment_found:
        return 0.0, "No comment found on art-related post"

    return 1.0, "Task completed successfully"


def _validate_trying_eat_healthier_but(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate I'm trying to eat healthier but don't want to give up flavor...

    Initial State Assumptions:
    - currentUser.searchHistory is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for healthy/recipe-related search (Chinese terms)
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "") for entry in search_history if isinstance(entry, dict)]
    healthy_food_keywords = ["健康", "食谱", "健康食谱", "减脂餐", "低卡", "营养", "轻食", "健康饮食", "健康美食", "健康料理"]
    has_healthy_food_search = any(any(keyword in query for keyword in healthy_food_keywords) for query in search_queries)
    if not has_healthy_food_search:
        return (
            0.0,
            f"searchHistory should contain healthy/recipe-related search terms (健康, 食谱, etc.), got: {search_queries}",
        )

    # Check bookmarks OR album with food-related posts (at least 3)
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"

    # Check if bookmarked posts are food-related
    food_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "food"):
                food_bookmarks_count += 1
        except ValueError:
            continue

    # Check for album with at least 3 food-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        albums = []

    food_album_posts_count = 0
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list):
            for post_id in post_ids:
                try:
                    post = _get_post(final_state_backend, post_id)
                    if _check_topic_relevance(post, "food"):
                        food_album_posts_count += 1
                except ValueError:
                    continue

    # Pass if either condition is met: bookmarked posts OR album posts
    if food_bookmarks_count < 3 and food_album_posts_count < 3:
        return (
            0.0,
            f"Expected at least 3 food-related posts either bookmarked (got {food_bookmarks_count}) or in a collection (got {food_album_posts_count})",
        )

    return 1.0, "Task completed successfully"


def _validate_want_support_some_smaller(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Want to support some smaller creators by engaging with their...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for 3 comments on posts with less than 1000 likes
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    comment_count = 0

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            # Check that post has less than 1000 likes
            post_likes = post.get("likes", 0)
            if not isinstance(post_likes, (int, float)):
                continue
            if post_likes >= 1000:
                continue
            # Post has less than 1000 likes, count this comment
            comment_count += 1
        except ValueError:
            continue

    if comment_count < 3:
        return 0.0, f"Expected at least 3 comments on posts with less than 1000 likes, got {comment_count}"

    return 1.0, "Task completed successfully"


def _validate_travel_planning(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 1: Search for '成都旅游', find at least 3 different creators,
    follow at least 2 of them, collect at least 5 posts, save to '成都行程' collection.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album called '成都行程' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains Chengdu travel-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    chengdu_keywords = ["成都", "chengdu", "旅游", "travel"]
    has_chengdu_search = any(any(keyword in query for keyword in chengdu_keywords) for query in search_queries)
    if not has_chengdu_search:
        return 0.0, f"searchHistory should contain Chengdu travel-related search terms, got: {search_queries}"

    # Verify at least 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed users, got {len(following)}"

    # Verify at least 5 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 5:
        return 0.0, f"Expected at least 5 bookmarked posts, got {len(bookmarks)}"

    # Verify "成都行程" album exists with at least 5 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    chengdu_itinerary = None
    for album in albums:
        if album.get("name") == "成都行程":
            chengdu_itinerary = album
            break

    if not chengdu_itinerary:
        return 0.0, "Album '成都行程' not found"

    album_post_ids = chengdu_itinerary.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 5:
        return (
            0.0,
            f"成都行程 album should have at least 5 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least 2 followed users match creators of bookmarked posts
    bookmarked_post_user_ids = set()
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            post_user_id = post.get("userId")
            if post_user_id:
                bookmarked_post_user_ids.add(post_user_id)
        except ValueError:
            continue

    following_set = set(following)
    matched_creators = bookmarked_post_user_ids.intersection(following_set)
    if len(matched_creators) < 2:
        return 0.0, f"Expected at least 2 followed users to be creators of bookmarked posts, got {len(matched_creators)}"

    # Verify bookmarked posts have Chengdu-related content
    chengdu_content_keywords = ["成都", "chengdu", "restaurant", "cafe", "scenic", "景点", "餐厅", "咖啡"]
    chengdu_related_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]
            location = post.get("location", "").lower()

            has_chengdu_content = any(
                keyword in title or keyword in caption or keyword in location or any(keyword in tag for tag in tags)
                for keyword in chengdu_content_keywords
            )
            if has_chengdu_content:
                chengdu_related_count += 1
        except ValueError:
            continue

    if chengdu_related_count < 3:
        return 0.0, f"Expected at least 3 bookmarked posts with Chengdu-related content, got {chengdu_related_count}"

    # Verify all followed users exist
    for user_id in following:
        try:
            _get_user(final_state_backend, user_id)
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 1 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, saved to '成都行程' collection",
    )


# =============================================================================
# Task 2: Beauty Product Research & Community Engagement
# =============================================================================


def _validate_beauty_product_research(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 2: Search for '干皮护肤', find at least 3 posts, like them,
    leave a comment asking a follow-up question, follow the creator with most detailed routine.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - No existing comments from currentUser in the comments collection before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Verify comment draft is empty (cleared after posting)
    comment_draft = final_state_frontend.get("commentDraft", "")
    if comment_draft:
        return 0.0, f"commentDraft should be empty after posting, got '{comment_draft}'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains dry skin care-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    skincare_keywords = ["干皮", "护肤", "skincare", "dry skin"]
    has_skincare_search = any(any(keyword in query for keyword in skincare_keywords) for query in search_queries)
    if not has_skincare_search:
        return 0.0, f"searchHistory should contain dry skin care-related search terms, got: {search_queries}"

    # Verify at least 3 liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) < 3:
        return 0.0, f"Expected at least 3 liked posts, got {len(liked_posts)}"

    # Verify at least one comment with question about product usage
    all_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    if not isinstance(all_comments, list):
        all_comments = []

    question_keywords = ["?", "？", "how", "怎么", "如何", "usage", "use", "用法"]
    question_comments = [
        c for c in all_comments if any(keyword in c.get("content", "").lower() for keyword in question_keywords)
    ]

    if len(question_comments) == 0:
        return 0.0, "Expected at least one comment asking a follow-up question about product usage"

    # Verify comment is on one of the liked posts
    question_comment_post_ids = {c.get("postId") for c in question_comments}
    liked_posts_set = set(liked_posts)
    if not question_comment_post_ids.intersection(liked_posts_set):
        return 0.0, "Question comment should be on one of the liked posts"

    # Verify at least 1 followed user
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user, got {len(following)}"

    # Cross-reference checks
    # Verify followed user is creator of at least one liked post
    liked_post_creators = set()
    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                liked_post_creators.add(creator_id)
        except ValueError:
            continue

    following_set = set(following)
    if not following_set.intersection(liked_post_creators):
        return 0.0, "Followed user should be creator of at least one liked post"

    # Verify liked posts have skincare/dry skin-related content
    skincare_content_keywords = ["干皮", "护肤", "skincare", "product", "routine", "产品", "routine"]
    skincare_related_count = 0
    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_skincare_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in skincare_content_keywords
            )
            if has_skincare_content:
                skincare_related_count += 1
        except ValueError:
            continue

    if skincare_related_count < 2:
        return 0.0, f"Expected at least 2 liked posts with skincare-related content, got {skincare_related_count}"

    # Verify each liked post has likes count incremented
    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            likes_count = post.get("likes", 0)
            if likes_count < 1:
                return 0.0, f"Post {post_id} should have likes count >= 1, got {likes_count}"
        except ValueError:
            continue

    return (
        1.0,
        f"Task 2 completed: {len(liked_posts)} posts liked, {len(question_comments)} question comments, {len(following)} creator followed",
    )


# =============================================================================
# Task 3: Fashion Inspiration & Style Discovery
# =============================================================================


def _validate_fashion_inspiration(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 3: Search for '面试穿搭' or '通勤穿搭', browse at least 10 posts,
    collect at least 4 outfit posts, follow at least 2 fashion creators, check their profiles.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # searchAdvancedFilters may show applied filters (optional check)
    search_advanced_filters = final_state_frontend.get("searchAdvancedFilters", {})

    # profileUserId should show the last profile visited
    profile_user_id = final_state_frontend.get("profileUserId")
    if not profile_user_id:
        return 0.0, "profileUserId should be set (indicating at least one profile was visited)"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains fashion-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    fashion_keywords = ["面试穿搭", "通勤穿搭", "outfit", "fashion", "穿搭"]
    has_fashion_search = any(any(keyword in query for keyword in fashion_keywords) for query in search_queries)
    if not has_fashion_search:
        return 0.0, f"searchHistory should contain fashion-related search terms, got: {search_queries}"

    # Verify at least 4 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 4:
        return 0.0, f"Expected at least 4 bookmarked posts, got {len(bookmarks)}"

    # Verify at least 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed users, got {len(following)}"

    # Cross-reference checks
    # Verify bookmarked posts have fashion-related content
    fashion_content_keywords = ["穿搭", "outfit", "fashion", "面试", "通勤", "style", "clothing"]
    fashion_related_count = 0
    bookmarked_post_creators = {}

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_fashion_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in fashion_content_keywords
            )
            if has_fashion_content:
                fashion_related_count += 1

            # Track creators
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    if fashion_related_count < 3:
        return 0.0, f"Expected at least 3 bookmarked posts with fashion-related content, got {fashion_related_count}"

    # Verify followed users exist and have content
    following_set = set(following)
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            user_posts = user.get("posts", [])
            if not isinstance(user_posts, list) or len(user_posts) == 0:
                return 0.0, f"Followed user {user_id} should have at least one post"
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    # Verify at least one bookmarked post's creator is followed
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least one bookmarked post's creator should be followed"

    # Verify followed users have fashion-related content (check category or bio)
    fashion_user_keywords = ["fashion", "style", "outfit", "穿搭", "时尚", "服装"]
    fashion_related_users = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_fashion_content = any(keyword in category or keyword in bio for keyword in fashion_user_keywords)
            if has_fashion_content:
                fashion_related_users += 1
        except ValueError:
            continue

    if fashion_related_users < 1:
        logger.warning("Expected at least one followed user to have fashion-related category/bio")

    return 1.0, f"Task 3 completed: {len(following)} fashion creators followed, {len(bookmarks)} outfit posts bookmarked"


# =============================================================================
# Task 4: Recipe Discovery & Meal Planning
# =============================================================================


def _validate_recipe_discovery(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 4: Search for '简单食谱' or '周末美食', find at least 3 recipes,
    check creator profiles, save to '待做美食' collection, like posts, verify detailed instructions in comments.

    Initial State Assumptions:
    - currentUser.liked is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album called '待做美食' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains recipe-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    recipe_keywords = ["简单食谱", "周末美食", "recipe", "食谱", "美食", "cooking"]
    has_recipe_search = any(any(keyword in query for keyword in recipe_keywords) for query in search_queries)
    if not has_recipe_search:
        return 0.0, f"searchHistory should contain recipe-related search terms, got: {search_queries}"

    # Verify at least 3 liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) < 3:
        return 0.0, f"Expected at least 3 liked posts, got {len(liked_posts)}"

    # Verify at least 3 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked posts, got {len(bookmarks)}"

    # Verify "待做美食" album exists with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    foods_to_make = None
    for album in albums:
        if album.get("name") == "待做美食":
            foods_to_make = album
            break

    if not foods_to_make:
        return 0.0, "Album '待做美食' not found"

    album_post_ids = foods_to_make.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 3:
        return (
            0.0,
            f"待做美食 album should have at least 3 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify bookmarked posts are subset of liked posts (recipes that were both liked and bookmarked)
    liked_set = set(liked_posts)
    if not bookmarked_set.issubset(liked_set):
        missing = bookmarked_set - liked_set
        return 0.0, f"Bookmarked posts {missing} should be subset of liked posts"

    # Verify posts have recipe-related content and are video/image type
    recipe_content_keywords = ["食谱", "recipe", "美食", "cooking", "food", "dish", "meal"]
    recipe_related_count = 0
    video_image_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)

            # Check type
            post_type = post.get("type")
            if post_type in ["video", "image"]:
                video_image_count += 1

            # Check content
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_recipe_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in recipe_content_keywords
            )
            if has_recipe_content:
                recipe_related_count += 1
        except ValueError:
            continue

    if recipe_related_count < 2:
        return 0.0, f"Expected at least 2 bookmarked posts with recipe-related content, got {recipe_related_count}"

    if video_image_count < 2:
        return 0.0, f"Expected at least 2 posts to be video or image type, got {video_image_count}"

    # Verify at least one post has detailed instructions in comments
    instruction_keywords = ["ingredient", "step", "步骤", "材料", "ingredients", "instructions", "做法"]
    has_detailed_instructions = False

    for post_id in album_post_ids:
        post_comments = _get_comments_for_post(final_state_backend, post_id)
        for comment in post_comments:
            content = comment.get("content", "").lower()
            if any(keyword in content for keyword in instruction_keywords):
                # Check if it's substantial (more than just a mention)
                if len(content) > 20:  # Basic check for detailed content
                    has_detailed_instructions = True
                    break
        if has_detailed_instructions:
            break

    if not has_detailed_instructions:
        return 0.0, "Expected at least one post to have detailed ingredient list or step-by-step instructions in comments"

    # Verify creators were checked (each bookmarked post's userId exists)
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                _get_user(final_state_backend, creator_id)  # Verify creator exists
        except ValueError:
            return 0.0, f"Creator of bookmarked post {post_id} does not exist"

    return 1.0, f"Task 4 completed: {len(liked_posts)} recipes liked, {len(bookmarks)} saved to '待做美食' collection"


# =============================================================================
# Task 5: Interior Design Ideas & Home Organization
# =============================================================================


def _validate_interior_design_discovery(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Validate Task 5: Search for '小户型卧室' or '收纳技巧', explore at least 15 posts,
    follow at least 3 creators, collect at least 6 posts, check notifications.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Verify page ends at notifications
    page = final_state_frontend.get("page")
    if page != "notifications":
        return 0.0, f"page={page} expected 'notifications' (user should check notifications at the end)"

    # Verify notificationView is set
    notification_view = final_state_frontend.get("notificationView")
    if notification_view is None:
        return 0.0, "notificationView should be set (indicating notifications page was accessed)"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains interior design/storage-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    design_keywords = ["小户型卧室", "收纳技巧", "interior", "organization", "storage", "bedroom", "收纳", "小户型"]
    has_design_search = any(any(keyword in query for keyword in design_keywords) for query in search_queries)
    if not has_design_search:
        return 0.0, f"searchHistory should contain interior design/storage-related search terms, got: {search_queries}"

    # Verify at least 3 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 3:
        return 0.0, f"Expected at least 3 followed users, got {len(following)}"

    # Verify at least 6 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 6:
        return 0.0, f"Expected at least 6 bookmarked posts, got {len(bookmarks)}"

    # Cross-reference checks
    # Verify bookmarked posts have interior design/storage-related content
    design_content_keywords = [
        "小户型",
        "卧室",
        "收纳",
        "interior",
        "organization",
        "storage",
        "furniture",
        "bedroom",
        "layout",
    ]
    design_related_count = 0
    bookmarked_post_creators = {}

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_design_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in design_content_keywords
            )
            if has_design_content:
                design_related_count += 1

            # Track creators
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    if design_related_count < 4:
        return (
            0.0,
            f"Expected at least 4 bookmarked posts with interior design/storage-related content, got {design_related_count}",
        )

    # Verify followed users exist and have interior design/home organization-related content
    following_set = set(following)
    design_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            design_user_keywords = ["interior", "design", "organization", "home", "收纳", "家居", "室内"]
            has_design_content = any(keyword in category or keyword in bio for keyword in design_user_keywords)
            if has_design_content:
                design_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if design_related_users < 2:
        logger.warning(
            f"Expected at least 2 followed users with interior design/home organization-related content, got {design_related_users}"
        )

    # Verify at least one bookmarked post's creator is followed
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least one bookmarked post's creator should be followed"

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 5 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, notifications checked",
    )


# =============================================================================
# Task 6: Fitness Journey Documentation Discovery
# =============================================================================


def _validate_fitness_journey(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 6: Search for '居家健身', follow at least 4 creators, save at least 7 posts
    to '健身计划' collection, like posts with detailed explanations.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    - No album called '健身计划' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains home fitness-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    fitness_keywords = ["居家健身", "home fitness", "fitness", "workout", "健身"]
    has_fitness_search = any(any(keyword in query for keyword in fitness_keywords) for query in search_queries)
    if not has_fitness_search:
        return 0.0, f"searchHistory should contain home fitness-related search terms, got: {search_queries}"

    # Verify at least 4 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 4:
        return 0.0, f"Expected at least 4 followed users, got {len(following)}"

    # Verify at least 7 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 7:
        return 0.0, f"Expected at least 7 bookmarked posts, got {len(bookmarks)}"

    # Verify at least some liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) == 0:
        return 0.0, "Expected at least some liked posts (posts with detailed explanations)"

    # Verify "健身计划" album exists with at least 7 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    fitness_plan = None
    for album in albums:
        if album.get("name") == "健身计划":
            fitness_plan = album
            break

    if not fitness_plan:
        return 0.0, "Album '健身计划' not found"

    album_post_ids = fitness_plan.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 7:
        return (
            0.0,
            f"健身计划 album should have at least 7 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have fitness-related content
    fitness_content_keywords = ["健身", "fitness", "workout", "exercise", "transformation", "routine", "运动", "训练"]
    fitness_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_fitness_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in fitness_content_keywords
            )
            if has_fitness_content:
                fitness_related_count += 1
        except ValueError:
            continue

    if fitness_related_count < 5:
        return 0.0, f"Expected at least 5 bookmarked posts with fitness-related content, got {fitness_related_count}"

    # Verify followed creators have fitness-related content
    fitness_user_keywords = ["fitness", "workout", "exercise", "健身", "运动", "训练"]
    fitness_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_fitness_content = any(keyword in category or keyword in bio for keyword in fitness_user_keywords)
            if has_fitness_content:
                fitness_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if fitness_related_users < 2:
        logger.warning(f"Expected at least 2 followed users with fitness-related content, got {fitness_related_users}")

    # Verify liked posts include detailed explanations
    explanation_keywords = ["form", "technique", "beginner", "modification", "步骤", "方法", "详细", "explanation"]
    explanation_count = 0

    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()

            has_explanation = any(keyword in title or keyword in caption for keyword in explanation_keywords)

            # Also check comments for explanations
            if not has_explanation:
                post_comments = _get_comments_for_post(final_state_backend, post_id)
                for comment in post_comments:
                    content = comment.get("content", "").lower()
                    if any(keyword in content for keyword in explanation_keywords):
                        has_explanation = True
                        break

            if has_explanation:
                explanation_count += 1
        except ValueError:
            continue

    if explanation_count == 0:
        return 0.0, "Expected at least some liked posts to include detailed explanations"

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 6 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, {len(liked_posts)} posts liked",
    )


# =============================================================================
# Task 7: Pet Care & Training Advice
# =============================================================================


def _validate_pet_care_training(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 7: Search for '狗狗训练' or '养狗日常', find at least 5 creators,
    follow 2 creators, collect at least 4 posts, leave a comment asking about a challenge.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No existing comments from currentUser in the comments collection before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    comment_draft = final_state_frontend.get("commentDraft", "")
    if comment_draft:
        return 0.0, f"commentDraft should be empty after posting, got '{comment_draft}'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains pet care-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    pet_keywords = ["狗狗训练", "养狗日常", "dog training", "pet care", "puppy", "训练", "养狗"]
    has_pet_search = any(any(keyword in query for keyword in pet_keywords) for query in search_queries)
    if not has_pet_search:
        return 0.0, f"searchHistory should contain pet care-related search terms, got: {search_queries}"

    # Verify exactly 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) != 2:
        return 0.0, f"Expected exactly 2 followed users, got {len(following)}"

    # Verify at least 4 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 4:
        return 0.0, f"Expected at least 4 bookmarked posts, got {len(bookmarks)}"

    # Verify at least one comment asking about a challenge
    all_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    if not isinstance(all_comments, list):
        all_comments = []

    challenge_keywords = ["challenge", "problem", "issue", "困难", "问题", "挑战", "help", "如何", "怎么"]
    challenge_comments = [
        c for c in all_comments if any(keyword in c.get("content", "").lower() for keyword in challenge_keywords)
    ]

    if len(challenge_comments) == 0:
        return 0.0, "Expected at least one comment asking about a challenge related to pet training"

    # Verify bookmarked posts have bookmarks count incremented
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            bookmarks_count = post.get("bookmarks", 0)
            if bookmarks_count < 1:
                return 0.0, f"Post {post_id} should have bookmarks count >= 1, got {bookmarks_count}"
        except ValueError:
            continue

    # Cross-reference checks
    # Verify comment postId exists
    for comment in challenge_comments:
        post_id = comment.get("postId")
        if post_id:
            try:
                _get_post(final_state_backend, post_id)
            except ValueError:
                return 0.0, f"Comment's postId {post_id} does not exist in posts collection"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have pet training/care-related content
    pet_content_keywords = ["狗狗", "训练", "dog", "training", "puppy", "pet", "养狗", "care", "routine"]
    pet_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_pet_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in pet_content_keywords
            )
            if has_pet_content:
                pet_related_count += 1
        except ValueError:
            continue

    if pet_related_count < 3:
        return 0.0, f"Expected at least 3 bookmarked posts with pet training/care-related content, got {pet_related_count}"

    # Verify followed creators have pet-related content
    pet_user_keywords = ["pet", "dog", "puppy", "training", "宠物", "狗狗", "养狗"]
    pet_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_pet_content = any(keyword in category or keyword in bio for keyword in pet_user_keywords)
            if has_pet_content:
                pet_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if pet_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with pet-related content, got {pet_related_users}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 7 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, {len(challenge_comments)} challenge comments",
    )


# =============================================================================
# Task 8: Photography Skills & Equipment Research
# =============================================================================


def _validate_photography_research(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 8: Search for '摄影教程' or '手机摄影', follow at least 3 photographers,
    save at least 5 posts to '摄影学习' collection, check profiles.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album called '摄影学习' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    profile_user_id = final_state_frontend.get("profileUserId")
    if not profile_user_id:
        return 0.0, "profileUserId should be set (indicating at least one profile was visited)"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains photography-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    photo_keywords = ["摄影教程", "手机摄影", "photography", "tutorial", "教程", "camera", "photo"]
    has_photo_search = any(any(keyword in query for keyword in photo_keywords) for query in search_queries)
    if not has_photo_search:
        return 0.0, f"searchHistory should contain photography-related search terms, got: {search_queries}"

    # Verify at least 3 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 3:
        return 0.0, f"Expected at least 3 followed users, got {len(following)}"

    # Verify at least 5 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 5:
        return 0.0, f"Expected at least 5 bookmarked posts, got {len(bookmarks)}"

    # Verify "摄影学习" album exists with at least 5 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    photography_learning = None
    for album in albums:
        if album.get("name") == "摄影学习":
            photography_learning = album
            break

    if not photography_learning:
        return 0.0, "Album '摄影学习' not found"

    album_post_ids = photography_learning.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 5:
        return (
            0.0,
            f"摄影学习 album should have at least 5 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have photography-related content
    photo_content_keywords = [
        "摄影",
        "photography",
        "tutorial",
        "教程",
        "portrait",
        "street",
        "technique",
        "equipment",
        "camera",
        "photo",
    ]
    photo_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_photo_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in photo_content_keywords
            )
            if has_photo_content:
                photo_related_count += 1
        except ValueError:
            continue

    if photo_related_count < 4:
        return 0.0, f"Expected at least 4 bookmarked posts with photography-related content, got {photo_related_count}"

    # Verify followed creators have photography-related content
    photo_user_keywords = ["photography", "photographer", "camera", "photo", "摄影", "摄影师"]
    photo_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_photo_content = any(keyword in category or keyword in bio for keyword in photo_user_keywords)
            if has_photo_content:
                photo_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if photo_related_users < 2:
        logger.warning(f"Expected at least 2 followed users with photography-related content, got {photo_related_users}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 8 completed: {len(following)} photographers followed, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 9: Study Techniques & Productivity Systems
# =============================================================================


def _validate_study_techniques(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 9: Search for '学习方法' or '时间管理', collect at least 6 posts to
    '学习技巧' collection, follow at least 3 users, like posts with templates/detailed breakdowns.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    - No album called '学习技巧' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains study/productivity-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    study_keywords = ["学习方法", "时间管理", "study", "productivity", "学习", "方法", "管理"]
    has_study_search = any(any(keyword in query for keyword in study_keywords) for query in search_queries)
    if not has_study_search:
        return 0.0, f"searchHistory should contain study/productivity-related search terms, got: {search_queries}"

    # Verify at least 3 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 3:
        return 0.0, f"Expected at least 3 followed users, got {len(following)}"

    # Verify at least 6 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 6:
        return 0.0, f"Expected at least 6 bookmarked posts, got {len(bookmarks)}"

    # Verify at least some liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) == 0:
        return 0.0, "Expected at least some liked posts (posts with templates/detailed breakdowns)"

    # Verify "学习技巧" album exists with at least 6 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    study_techniques = None
    for album in albums:
        if album.get("name") == "学习技巧":
            study_techniques = album
            break

    if not study_techniques:
        return 0.0, "Album '学习技巧' not found"

    album_post_ids = study_techniques.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 6:
        return (
            0.0,
            f"学习技巧 album should have at least 6 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have study/productivity-related content
    study_content_keywords = [
        "学习",
        "study",
        "productivity",
        "时间管理",
        "planner",
        "note-taking",
        "system",
        "method",
        "方法",
        "技巧",
    ]
    study_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_study_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in study_content_keywords
            )
            if has_study_content:
                study_related_count += 1
        except ValueError:
            continue

    if study_related_count < 4:
        return 0.0, f"Expected at least 4 bookmarked posts with study/productivity-related content, got {study_related_count}"

    # Verify followed creators have educational content
    education_user_keywords = ["education", "study", "learning", "教育", "学习", "知识"]
    education_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_education_content = any(keyword in category or keyword in bio for keyword in education_user_keywords)
            if has_education_content:
                education_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if education_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with educational content, got {education_related_users}")

    # Verify liked posts include templates or detailed breakdowns
    template_keywords = ["template", "download", "breakdown", "详细", "模板", "下载", "步骤", "system"]
    template_count = 0

    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()

            has_template = any(keyword in title or keyword in caption for keyword in template_keywords)

            # Also check comments for templates/breakdowns
            if not has_template:
                post_comments = _get_comments_for_post(final_state_backend, post_id)
                for comment in post_comments:
                    content = comment.get("content", "").lower()
                    if any(keyword in content for keyword in template_keywords):
                        has_template = True
                        break

            if has_template:
                template_count += 1
        except ValueError:
            continue

    if template_count == 0:
        return 0.0, "Expected at least some liked posts to include templates or detailed breakdowns"

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 9 completed: {len(following)} users followed, {len(bookmarks)} posts bookmarked, {len(liked_posts)} posts liked",
    )


# =============================================================================
# Task 10: Plant Care & Urban Gardening
# =============================================================================


def _validate_plant_care_gardening(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 10: Search for '阳台种植' or '室内植物', follow at least 2 creators,
    collect at least 5 posts, leave a comment asking about watering schedules.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No existing comments from currentUser in the comments collection before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    comment_draft = final_state_frontend.get("commentDraft", "")
    if comment_draft:
        return 0.0, f"commentDraft should be empty after posting, got '{comment_draft}'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains plant care-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    plant_keywords = ["阳台种植", "室内植物", "balcony", "indoor", "plant", "gardening", "种植", "植物"]
    has_plant_search = any(any(keyword in query for keyword in plant_keywords) for query in search_queries)
    if not has_plant_search:
        return 0.0, f"searchHistory should contain plant care-related search terms, got: {search_queries}"

    # Verify at least 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed users, got {len(following)}"

    # Verify at least 5 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 5:
        return 0.0, f"Expected at least 5 bookmarked posts, got {len(bookmarks)}"

    # Verify at least one comment asking about watering schedules
    all_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    if not isinstance(all_comments, list):
        all_comments = []

    watering_keywords = ["watering", "water", "schedule", "浇水", "时间", "频率"]
    watering_comments = [
        c for c in all_comments if any(keyword in c.get("content", "").lower() for keyword in watering_keywords)
    ]

    if len(watering_comments) == 0:
        return 0.0, "Expected at least one comment asking about watering schedules or plant care"

    # Verify bookmarked posts have bookmarks count incremented
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            bookmarks_count = post.get("bookmarks", 0)
            if bookmarks_count < 1:
                return 0.0, f"Post {post_id} should have bookmarks count >= 1, got {bookmarks_count}"
        except ValueError:
            continue

    # Cross-reference checks
    # Verify comment postId exists
    for comment in watering_comments:
        post_id = comment.get("postId")
        if post_id:
            try:
                _get_post(final_state_backend, post_id)
            except ValueError:
                return 0.0, f"Comment's postId {post_id} does not exist in posts collection"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have plant care/gardening-related content
    plant_content_keywords = [
        "植物",
        "plant",
        "阳台",
        "balcony",
        "indoor",
        "室内",
        "gardening",
        "种植",
        "low-light",
        "beginner",
    ]
    plant_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_plant_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in plant_content_keywords
            )
            if has_plant_content:
                plant_related_count += 1
        except ValueError:
            continue

    if plant_related_count < 4:
        return 0.0, f"Expected at least 4 bookmarked posts with plant care/gardening-related content, got {plant_related_count}"

    # Verify followed creators have plant/gardening-related content
    plant_user_keywords = ["plant", "gardening", "garden", "植物", "种植", "园艺"]
    plant_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_plant_content = any(keyword in category or keyword in bio for keyword in plant_user_keywords)
            if has_plant_content:
                plant_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if plant_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with plant/gardening-related content, got {plant_related_users}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 10 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, {len(watering_comments)} watering comments",
    )


# =============================================================================
# Task 11: Wedding Planning & Inspiration Board
# =============================================================================


def _validate_wedding_planning(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 11: Search for '户外婚礼' or '简约婚礼', follow at least 4 creators,
    save at least 8 posts to '婚礼灵感' collection, visit profiles.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album called '婚礼灵感' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    profile_user_id = final_state_frontend.get("profileUserId")
    if not profile_user_id:
        return 0.0, "profileUserId should be set (indicating at least one profile was visited)"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains wedding-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    wedding_keywords = ["户外婚礼", "简约婚礼", "wedding", "outdoor", "minimalist", "婚礼", "户外", "简约"]
    has_wedding_search = any(any(keyword in query for keyword in wedding_keywords) for query in search_queries)
    if not has_wedding_search:
        return 0.0, f"searchHistory should contain wedding-related search terms, got: {search_queries}"

    # Verify at least 4 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 4:
        return 0.0, f"Expected at least 4 followed users, got {len(following)}"

    # Verify at least 8 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 8:
        return 0.0, f"Expected at least 8 bookmarked posts, got {len(bookmarks)}"

    # Verify "婚礼灵感" album exists with at least 8 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    wedding_inspiration = None
    for album in albums:
        if album.get("name") == "婚礼灵感":
            wedding_inspiration = album
            break

    if not wedding_inspiration:
        return 0.0, "Album '婚礼灵感' not found"

    album_post_ids = wedding_inspiration.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 8:
        return (
            0.0,
            f"婚礼灵感 album should have at least 8 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have wedding-related content
    wedding_content_keywords = [
        "婚礼",
        "wedding",
        "outdoor",
        "户外",
        "minimalist",
        "简约",
        "venue",
        "decoration",
        "ceremony",
        "装饰",
    ]
    wedding_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_wedding_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in wedding_content_keywords
            )
            if has_wedding_content:
                wedding_related_count += 1
        except ValueError:
            continue

    if wedding_related_count < 6:
        return 0.0, f"Expected at least 6 bookmarked posts with wedding-related content, got {wedding_related_count}"

    # Verify followed creators are wedding planners or photographers
    wedding_user_keywords = ["wedding", "planner", "photographer", "event", "婚礼", "策划", "摄影师", "摄影"]
    wedding_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_wedding_content = any(keyword in category or keyword in bio for keyword in wedding_user_keywords)
            if has_wedding_content:
                wedding_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if wedding_related_users < 2:
        logger.warning(
            f"Expected at least 2 followed users with wedding/event/photography-related content, got {wedding_related_users}"
        )

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 11 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 12: Career Development & Interview Preparation
# =============================================================================


def _validate_career_development(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 12: Search for '市场营销' or '求职经验', follow at least 3 users,
    collect at least 5 posts, read comments on at least 2 posts.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains career/interview-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    career_keywords = ["市场营销", "求职经验", "marketing", "career", "interview", "job", "求职", "面试"]
    has_career_search = any(any(keyword in query for keyword in career_keywords) for query in search_queries)
    if not has_career_search:
        return 0.0, f"searchHistory should contain career/interview-related search terms, got: {search_queries}"

    # Verify at least 3 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 3:
        return 0.0, f"Expected at least 3 followed users, got {len(following)}"

    # Verify at least 5 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 5:
        return 0.0, f"Expected at least 5 bookmarked posts, got {len(bookmarks)}"

    # Verify bookmarked posts have bookmarks count incremented
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            bookmarks_count = post.get("bookmarks", 0)
            if bookmarks_count < 1:
                return 0.0, f"Post {post_id} should have bookmarks count >= 1, got {bookmarks_count}"
        except ValueError:
            continue

    # Cross-reference checks
    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have career/interview-related content
    career_content_keywords = [
        "市场营销",
        "marketing",
        "求职",
        "interview",
        "career",
        "job",
        "portfolio",
        "industry",
        "trends",
        "经验",
    ]
    career_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_career_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in career_content_keywords
            )
            if has_career_content:
                career_related_count += 1
        except ValueError:
            continue

    if career_related_count < 4:
        return 0.0, f"Expected at least 4 bookmarked posts with career/interview-related content, got {career_related_count}"

    # Verify followed creators work in marketing or HR
    career_user_keywords = ["marketing", "hr", "human resources", "career", "recruiter", "市场营销", "人力资源", "hr"]
    career_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_career_content = any(keyword in category or keyword in bio for keyword in career_user_keywords)
            if has_career_content:
                career_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if career_related_users < 1:
        logger.warning(
            f"Expected at least 1 followed user with marketing/HR/career-related content, got {career_related_users}"
        )

    # Verify at least 2 posts have comments (indicating comments were read)
    posts_with_comments = 0
    for post_id in bookmarks[:5]:  # Check first 5 bookmarked posts
        try:
            post_comments = _get_comments_for_post(final_state_backend, post_id)
            if len(post_comments) > 0:
                posts_with_comments += 1
        except ValueError:
            continue

    if posts_with_comments < 2:
        logger.warning(f"Expected at least 2 posts with comments (indicating comments were read), got {posts_with_comments}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 12 completed: {len(following)} users followed, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 13: Language Learning Resources & Practice
# =============================================================================


def _validate_language_learning(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 13: Search for '英语学习', follow at least 3 creators, save at least 6 posts
    to '英语资料' collection, like posts with audio/video, check profile.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    - No album called '英语资料' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    profile_user_id = final_state_frontend.get("profileUserId")
    if not profile_user_id:
        return 0.0, "profileUserId should be set (indicating at least one profile was visited)"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains language learning-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    language_keywords = ["英语学习", "english learning", "language", "学习", "英语"]
    has_language_search = any(any(keyword in query for keyword in language_keywords) for query in search_queries)
    if not has_language_search:
        return 0.0, f"searchHistory should contain language learning-related search terms, got: {search_queries}"

    # Verify at least 3 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 3:
        return 0.0, f"Expected at least 3 followed users, got {len(following)}"

    # Verify at least 6 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 6:
        return 0.0, f"Expected at least 6 bookmarked posts, got {len(bookmarks)}"

    # Verify at least some liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) == 0:
        return 0.0, "Expected at least some liked posts (posts with audio/video demonstrations)"

    # Verify "英语资料" album exists with at least 6 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    english_materials = None
    for album in albums:
        if album.get("name") == "英语资料":
            english_materials = album
            break

    if not english_materials:
        return 0.0, "Album '英语资料' not found"

    album_post_ids = english_materials.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 6:
        return (
            0.0,
            f"英语资料 album should have at least 6 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have language learning-related content
    language_content_keywords = [
        "英语",
        "english",
        "learning",
        "vocabulary",
        "pronunciation",
        "study",
        "practice",
        "exercise",
        "学习",
        "词汇",
    ]
    language_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_language_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in language_content_keywords
            )
            if has_language_content:
                language_related_count += 1
        except ValueError:
            continue

    if language_related_count < 4:
        return 0.0, f"Expected at least 4 bookmarked posts with language learning-related content, got {language_related_count}"

    # Verify followed creators have language learning content
    language_user_keywords = ["language", "learning", "education", "english", "语言", "学习", "教育", "英语"]
    language_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_language_content = any(keyword in category or keyword in bio for keyword in language_user_keywords)
            if has_language_content:
                language_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if language_related_users < 1:
        logger.warning(
            f"Expected at least 1 followed user with language/education-related content, got {language_related_users}"
        )

    # Verify liked posts include audio or video demonstrations
    audio_video_count = 0
    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            post_type = post.get("type", "").lower()

            # Check if post is video or audio type
            if post_type in ["video", "audio"]:
                audio_video_count += 1
            else:
                # Check title/caption for audio/video keywords
                title = post.get("title", "").lower()
                caption = post.get("caption", "").lower()
                audio_video_keywords = ["audio", "video", "pronunciation", "发音", "视频", "音频"]
                if any(keyword in title or keyword in caption for keyword in audio_video_keywords):
                    audio_video_count += 1
        except ValueError:
            continue

    if audio_video_count == 0:
        return 0.0, "Expected at least some liked posts to include audio or video demonstrations"

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 13 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, {len(liked_posts)} posts liked",
    )


# =============================================================================
# Task 14: Coffee Culture & Brewing Techniques
# =============================================================================


def _validate_coffee_culture(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 14: Search for '咖啡制作' or '拉花技巧', follow at least 3 creators,
    save at least 5 posts to '咖啡笔记' collection, like posts with step-by-step processes.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    - No album called '咖啡笔记' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains coffee-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    coffee_keywords = ["咖啡制作", "拉花技巧", "coffee", "espresso", "latte", "brewing", "咖啡", "拉花"]
    has_coffee_search = any(any(keyword in query for keyword in coffee_keywords) for query in search_queries)
    if not has_coffee_search:
        return 0.0, f"searchHistory should contain coffee-related search terms, got: {search_queries}"

    # Verify at least 3 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 3:
        return 0.0, f"Expected at least 3 followed users, got {len(following)}"

    # Verify at least 5 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 5:
        return 0.0, f"Expected at least 5 bookmarked posts, got {len(bookmarks)}"

    # Verify at least some liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) == 0:
        return 0.0, "Expected at least some liked posts (posts with step-by-step processes)"

    # Verify "咖啡笔记" album exists with at least 5 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    coffee_notes = None
    for album in albums:
        if album.get("name") == "咖啡笔记":
            coffee_notes = album
            break

    if not coffee_notes:
        return 0.0, "Album '咖啡笔记' not found"

    album_post_ids = coffee_notes.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 5:
        return (
            0.0,
            f"咖啡笔记 album should have at least 5 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have coffee-related content
    coffee_content_keywords = [
        "咖啡",
        "coffee",
        "espresso",
        "latte",
        "拉花",
        "brewing",
        "technique",
        "tutorial",
        "equipment",
        "制作",
    ]
    coffee_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_coffee_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in coffee_content_keywords
            )
            if has_coffee_content:
                coffee_related_count += 1
        except ValueError:
            continue

    if coffee_related_count < 4:
        return 0.0, f"Expected at least 4 bookmarked posts with coffee-related content, got {coffee_related_count}"

    # Verify followed creators are coffee enthusiasts or baristas
    coffee_user_keywords = ["coffee", "barista", "espresso", "latte", "咖啡", "拉花", "barista"]
    coffee_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_coffee_content = any(keyword in category or keyword in bio for keyword in coffee_user_keywords)
            if has_coffee_content:
                coffee_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if coffee_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with coffee/barista-related content, got {coffee_related_users}")

    # Verify liked posts show step-by-step processes or common mistakes
    step_by_step_keywords = ["step-by-step", "步骤", "mistake", "错误", "common", "process", "详细", "方法"]
    step_by_step_count = 0

    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()

            has_step_by_step = any(keyword in title or keyword in caption for keyword in step_by_step_keywords)

            # Also check comments for step-by-step content
            if not has_step_by_step:
                post_comments = _get_comments_for_post(final_state_backend, post_id)
                for comment in post_comments:
                    content = comment.get("content", "").lower()
                    if any(keyword in content for keyword in step_by_step_keywords):
                        has_step_by_step = True
                        break

            if has_step_by_step:
                step_by_step_count += 1
        except ValueError:
            continue

    if step_by_step_count == 0:
        return 0.0, "Expected at least some liked posts to show step-by-step processes or common mistakes"

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return (
        1.0,
        f"Task 14 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked, {len(liked_posts)} posts liked",
    )


# =============================================================================
# Task 15: Sustainable Living & Zero Waste Tips
# =============================================================================


def _validate_sustainable_living(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 15: Search for '环保生活' or '零浪费', follow at least 4 creators,
    save at least 7 posts to '可持续生活' collection, read comments on at least 2 posts.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album called '可持续生活' exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains sustainability-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    sustainability_keywords = ["环保生活", "零浪费", "eco-friendly", "sustainable", "zero waste", "环保", "可持续"]
    has_sustainability_search = any(any(keyword in query for keyword in sustainability_keywords) for query in search_queries)
    if not has_sustainability_search:
        return 0.0, f"searchHistory should contain sustainability-related search terms, got: {search_queries}"

    # Verify at least 4 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 4:
        return 0.0, f"Expected at least 4 followed users, got {len(following)}"

    # Verify at least 7 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 7:
        return 0.0, f"Expected at least 7 bookmarked posts, got {len(bookmarks)}"

    # Verify "可持续生活" album exists with at least 7 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    sustainable_living = None
    for album in albums:
        if album.get("name") == "可持续生活":
            sustainable_living = album
            break

    if not sustainable_living:
        return 0.0, "Album '可持续生活' not found"

    album_post_ids = sustainable_living.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 7:
        return (
            0.0,
            f"可持续生活 album should have at least 7 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have sustainability-related content
    sustainability_content_keywords = [
        "环保",
        "eco-friendly",
        "sustainable",
        "零浪费",
        "zero waste",
        "diy",
        "swap",
        "waste reduction",
        "product",
        "可持续",
    ]
    sustainability_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_sustainability_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in sustainability_content_keywords
            )
            if has_sustainability_content:
                sustainability_related_count += 1
        except ValueError:
            continue

    if sustainability_related_count < 5:
        return (
            0.0,
            f"Expected at least 5 bookmarked posts with sustainability-related content, got {sustainability_related_count}",
        )

    # Verify followed creators are dedicated to environmental content
    environmental_user_keywords = ["environmental", "sustainable", "eco", "green", "环保", "可持续", "环境"]
    environmental_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_environmental_content = any(keyword in category or keyword in bio for keyword in environmental_user_keywords)
            if has_environmental_content:
                environmental_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if environmental_related_users < 2:
        logger.warning(
            f"Expected at least 2 followed users with environmental/sustainability-related content, got {environmental_related_users}"
        )

    # Verify at least 2 posts have comments (indicating comments were read)
    posts_with_comments = 0
    for post_id in bookmarks[:7]:  # Check first 7 bookmarked posts
        try:
            post_comments = _get_comments_for_post(final_state_backend, post_id)
            if len(post_comments) > 0:
                posts_with_comments += 1
        except ValueError:
            continue

    if posts_with_comments < 2:
        logger.warning(f"Expected at least 2 posts with comments (indicating comments were read), got {posts_with_comments}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 15 completed: {len(following)} creators followed, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 16: Cat Care Basics Discovery
# =============================================================================


def _validate_cat_care_basics(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 16: Search for cat care basics, follow at least 2 pet bloggers,
    save at least 3 posts to a cat/pet-related collection.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album with cat/pet-related name exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains cat/pet care-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    cat_keywords = ["cat care", "猫咪", "pet care", "feeding", "litter", "cat", "pet", "宠物"]
    has_cat_search = any(any(keyword in query for keyword in cat_keywords) for query in search_queries)
    if not has_cat_search:
        return 0.0, f"searchHistory should contain cat/pet care-related search terms, got: {search_queries}"

    # Verify at least 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed users, got {len(following)}"

    # Verify at least 3 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked posts, got {len(bookmarks)}"

    # Verify album with cat/pet-related name exists with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    cat_album_keywords = ["cat", "猫咪", "pet", "宠物", "care"]
    cat_album = None
    for album in albums:
        album_name = album.get("name", "").lower()
        if any(keyword in album_name for keyword in cat_album_keywords):
            cat_album = album
            break

    if not cat_album:
        return 0.0, "Album with cat/pet-related name not found"

    album_post_ids = cat_album.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 3:
        return (
            0.0,
            f"Cat/pet album should have at least 3 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify bookmarked posts have cat/pet care-related content
    cat_content_keywords = ["cat", "猫咪", "pet", "feeding", "litter", "care", "training", "宠物"]
    cat_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_cat_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in cat_content_keywords
            )
            if has_cat_content:
                cat_related_count += 1
        except ValueError:
            continue

    if cat_related_count < 2:
        return 0.0, f"Expected at least 2 bookmarked posts with cat/pet care-related content, got {cat_related_count}"

    # Verify followed creators have pet/cat-related content
    pet_user_keywords = ["pet", "cat", "animal", "宠物", "猫咪", "animal"]
    pet_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_pet_content = any(keyword in category or keyword in bio for keyword in pet_user_keywords)
            if has_pet_content:
                pet_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if pet_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with pet/cat-related content, got {pet_related_users}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 16 completed: {len(following)} pet bloggers followed, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 17: Bullet Journal Inspiration Discovery
# =============================================================================


def _validate_bullet_journal_inspiration(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Validate Task 17: Search for bullet journal content, leave a positive comment,
    save at least 3 posts to a journal-related collection.

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    - No existing comments from currentUser in the comments collection before task starts
    - No album with journal-related name exists before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    comment_draft = final_state_frontend.get("commentDraft", "")
    if comment_draft:
        return 0.0, f"commentDraft should be empty after posting, got '{comment_draft}'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains journaling/bullet journal-related search
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    journal_keywords = ["bullet journal", "journaling", "planning", "手账", "日记", "journal"]
    has_journal_search = any(any(keyword in query for keyword in journal_keywords) for query in search_queries)
    if not has_journal_search:
        return 0.0, f"searchHistory should contain journaling/bullet journal-related search terms, got: {search_queries}"

    # Verify at least 3 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked posts, got {len(bookmarks)}"

    # Verify album with journal-related name exists with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    journal_album_keywords = ["journal", "手账", "planning", "bullet", "日记"]
    journal_album = None
    for album in albums:
        album_name = album.get("name", "").lower()
        if any(keyword in album_name for keyword in journal_album_keywords):
            journal_album = album
            break

    if not journal_album:
        return 0.0, "Album with journal-related name not found"

    album_post_ids = journal_album.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 3:
        return (
            0.0,
            f"Journal album should have at least 3 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Verify at least one comment with positive sentiment
    all_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    if not isinstance(all_comments, list):
        all_comments = []

    positive_keywords = ["nice", "beautiful", "inspiring", "love", "喜欢", "好看", "漂亮", "great", "amazing", "wonderful"]
    positive_comments = [
        c for c in all_comments if any(keyword in c.get("content", "").lower() for keyword in positive_keywords)
    ]

    if len(positive_comments) == 0:
        return 0.0, "Expected at least one comment with positive sentiment"

    # Verify comment is on one of the bookmarked posts
    comment_post_ids = {c.get("postId") for c in positive_comments}
    bookmarked_set = set(bookmarks)
    if not comment_post_ids.intersection(bookmarked_set):
        return 0.0, "Comment should be on one of the bookmarked posts"

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify comment postId exists
    for comment in positive_comments:
        post_id = comment.get("postId")
        if post_id:
            try:
                _get_post(final_state_backend, post_id)
            except ValueError:
                return 0.0, f"Comment's postId {post_id} does not exist in posts collection"

    # Verify bookmarked posts have journaling/bullet journal-related content
    journal_content_keywords = ["journal", "bullet journal", "planning", "spread", "layout", "手账", "日记", "aesthetic"]
    journal_related_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()
            tags = [tag.lower() for tag in post.get("tags", [])]

            has_journal_content = any(
                keyword in title or keyword in caption or any(keyword in tag for tag in tags)
                for keyword in journal_content_keywords
            )
            if has_journal_content:
                journal_related_count += 1
        except ValueError:
            continue

    if journal_related_count < 2:
        return (
            0.0,
            f"Expected at least 2 bookmarked posts with journaling/bullet journal-related content, got {journal_related_count}",
        )

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 17 completed: {len(positive_comments)} positive comments, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 18: Dark Mode & Notifications Check
# =============================================================================


def _validate_dark_mode_notifications(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 18: Switch to dark mode and check notifications page.

    Initial State Assumptions:
    - None required (this is a UI state change task)
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    theme_mode = final_state_frontend.get("themeMode")
    if theme_mode != "dark":
        return 0.0, f"themeMode={theme_mode} expected 'dark'"

    page = final_state_frontend.get("page")
    if page != "notifications":
        return 0.0, f"page={page} expected 'notifications'"

    notification_view = final_state_frontend.get("notificationView")
    if notification_view is None:
        return 0.0, "notificationView should be set (indicating notifications page was accessed)"

    # Backend checks - none required for this task

    return 1.0, "Task 18 completed: Dark mode enabled, notifications page accessed"


# =============================================================================
# Task 19: Shanghai Coffee Cafe Discovery
# =============================================================================


def _validate_shanghai_coffee_discovery(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Validate Task 19: Search for Shanghai coffee cafes, follow at least 2 coffee enthusiasts,
    save at least 3 posts to a Shanghai/coffee-related collection.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - No album with Shanghai/coffee-related name exists before task starts
    - Empty searchHistory before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains a new entry (Shanghai and coffee-related)
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    if len(search_history) == 0:
        return 0.0, "Expected at least one searchHistory entry"

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    shanghai_coffee_keywords = ["shanghai", "上海", "coffee", "咖啡", "cafe", "咖啡店"]
    has_shanghai_coffee_search = any(any(keyword in query for keyword in shanghai_coffee_keywords) for query in search_queries)
    if not has_shanghai_coffee_search:
        return 0.0, f"searchHistory should contain Shanghai and coffee-related search terms, got: {search_queries}"

    # Verify at least 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed users, got {len(following)}"

    # Verify at least 3 bookmarked posts
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked posts, got {len(bookmarks)}"

    # Verify album with Shanghai/coffee-related name exists with at least 3 posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    shanghai_coffee_album_keywords = ["shanghai", "上海", "coffee", "咖啡", "cafe"]
    shanghai_coffee_album = None
    for album in albums:
        album_name = album.get("name", "").lower()
        if any(keyword in album_name for keyword in shanghai_coffee_album_keywords):
            shanghai_coffee_album = album
            break

    if not shanghai_coffee_album:
        return 0.0, "Album with Shanghai/coffee-related name not found"

    album_post_ids = shanghai_coffee_album.get("postIds", [])
    if not isinstance(album_post_ids, list) or len(album_post_ids) < 3:
        return (
            0.0,
            f"Shanghai/coffee album should have at least 3 posts, got {len(album_post_ids) if isinstance(album_post_ids, list) else 'not a list'}",
        )

    # Cross-reference checks
    # Verify album post IDs match bookmarked posts
    album_post_set = set(album_post_ids)
    bookmarked_set = set(bookmarks)
    if not album_post_set.issubset(bookmarked_set):
        missing = album_post_set - bookmarked_set
        return 0.0, f"Album postIds {missing} should be subset of bookmarked posts"

    # Verify at least some followed users match creators of bookmarked posts
    bookmarked_post_creators = {}
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in bookmarked_post_creators:
                    bookmarked_post_creators[creator_id] = []
                bookmarked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    bookmarked_creators_set = set(bookmarked_post_creators.keys())
    if not following_set.intersection(bookmarked_creators_set):
        return 0.0, "At least some followed users should be creators of bookmarked posts"

    # Verify posts mention Shanghai location
    shanghai_location_keywords = ["shanghai", "上海"]
    shanghai_location_count = 0

    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            location = post.get("location", "").lower()
            title = post.get("title", "").lower()
            caption = post.get("caption", "").lower()

            has_shanghai_location = any(
                keyword in location or keyword in title or keyword in caption for keyword in shanghai_location_keywords
            )
            if has_shanghai_location:
                shanghai_location_count += 1
        except ValueError:
            continue

    if shanghai_location_count < 2:
        return 0.0, f"Expected at least 2 posts mentioning Shanghai location, got {shanghai_location_count}"

    # Verify followed creators have coffee/cafe-related content
    coffee_user_keywords = ["coffee", "cafe", "barista", "espresso", "咖啡", "咖啡店"]
    coffee_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_coffee_content = any(keyword in category or keyword in bio for keyword in coffee_user_keywords)
            if has_coffee_content:
                coffee_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if coffee_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with coffee/cafe-related content, got {coffee_related_users}")

    # Verify all bookmarked posts exist
    for post_id in bookmarks:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Bookmarked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 19 completed: {len(following)} coffee enthusiasts followed, {len(bookmarks)} posts bookmarked"


# =============================================================================
# Task 20: Beginner Yoga Content Discovery
# =============================================================================


def _validate_beginner_yoga_discovery(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """
    Validate Task 20: Search for beginner yoga content, like at least 3 posts,
    follow at least 2 yoga creators.

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    - Empty searchHistory before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    # Frontend checks
    search_type = final_state_frontend.get("searchType")
    if search_type not in ["posts", "all"]:
        return 0.0, f"searchType={search_type} expected 'posts' or 'all'"

    # Backend checks
    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Verify searchHistory contains a new entry (beginner yoga-related)
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    if len(search_history) == 0:
        return 0.0, "Expected at least one searchHistory entry"

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    yoga_keywords = ["beginner yoga", "yoga for beginners", "瑜伽", "初学者", "yoga"]
    has_yoga_search = any(any(keyword in query for keyword in yoga_keywords) for query in search_queries)
    if not has_yoga_search:
        return 0.0, f"searchHistory should contain beginner yoga-related search terms, got: {search_queries}"

    # Verify at least 3 liked posts
    liked = current_user.get("liked", [])
    if not isinstance(liked, list):
        return 0.0, "liked is not a list"
    # Filter to get only post IDs (exclude comment IDs) by checking if ID exists in posts collection
    liked_posts = []
    for item in liked:
        if not isinstance(item, str):
            continue
        try:
            _get_post(final_state_backend, item)
            liked_posts.append(item)
        except ValueError:
            # Not a post ID, skip (likely a comment ID)
            continue
    if len(liked_posts) < 3:
        return 0.0, f"Expected at least 3 liked posts, got {len(liked_posts)}"

    # Verify at least 2 followed users
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed users, got {len(following)}"

    # Verify each liked post has likes count incremented
    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            likes_count = post.get("likes", 0)
            if likes_count < 1:
                return 0.0, f"Post {post_id} should have likes count >= 1, got {likes_count}"
        except ValueError:
            continue

    # Cross-reference checks
    # Verify at least some followed users match creators of liked posts
    liked_post_creators = {}
    for post_id in liked_posts:
        try:
            post = _get_post(final_state_backend, post_id)
            creator_id = post.get("userId")
            if creator_id:
                if creator_id not in liked_post_creators:
                    liked_post_creators[creator_id] = []
                liked_post_creators[creator_id].append(post_id)
        except ValueError:
            continue

    following_set = set(following)
    liked_creators_set = set(liked_post_creators.keys())
    if not following_set.intersection(liked_creators_set):
        return 0.0, "At least some followed users should be creators of liked posts"

    # Verify followed creators have yoga/fitness-related content
    yoga_user_keywords = ["yoga", "fitness", "exercise", "workout", "瑜伽", "健身", "运动"]
    yoga_related_users = 0

    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = user.get("category", "").lower()
            bio = user.get("bio", "").lower()

            has_yoga_content = any(keyword in category or keyword in bio for keyword in yoga_user_keywords)
            if has_yoga_content:
                yoga_related_users += 1
        except ValueError:
            return 0.0, f"Followed user {user_id} does not exist in users collection"

    if yoga_related_users < 1:
        logger.warning(f"Expected at least 1 followed user with yoga/fitness-related content, got {yoga_related_users}")

    # Verify all liked posts exist
    for post_id in liked_posts:
        try:
            _get_post(final_state_backend, post_id)
        except ValueError:
            return 0.0, f"Liked post {post_id} does not exist in posts collection"

    return 1.0, f"Task 20 completed: {len(following)} yoga creators followed, {len(liked_posts)} posts liked"


# =============================================================================
# Generated Tasks 21-50: From xhs-reward-functions.py
# =============================================================================


def _validate_planning_redecorate_living_room(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Planning to redecorate my living room with a cozy, minimalis...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    home_following_count = _count_topic_relevant_users(final_state_backend, following, "home")
    if home_following_count < 2:
        return 0.0, f"Expected at least 2 home-related followed user(s), got {home_following_count}"

    # Check for album (collection) with at least 3 home-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = _find_album_with_topic_posts(final_state_backend, albums, "home", 3)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 home-related posts"

    return 1.0, "Task completed successfully"


def _validate_keep_seeing_these_amazing_street_style(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I keep seeing these amazing street style photos and want to ...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check bookmarks OR collection
    # Verification: "≥4 casual fashion/street style posts bookmarked or in fashion-related collection"
    fashion_count = 0

    # Check bookmarks
    bookmarks = current_user.get("bookmarks", [])
    if isinstance(bookmarks, list):
        for post_id in bookmarks:
            try:
                post = _get_post(final_state_backend, post_id)
                if _check_topic_relevance(post, "fashion"):
                    fashion_count += 1
            except ValueError:
                continue

    if fashion_count < 4:
        return 0.0, f"Expected at least 4 fashion-related posts bookmarked or in collection, got {fashion_count}"

    return 1.0, "Task completed successfully"


def _validate_notifications_are_probably_piling(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My notifications are probably piling up and I should check w...

    Verification: "User on notifications page; notifications viewed or marked as read"
    """
    page = final_state_frontend.get("page")
    if page != "notifications":
        return 0.0, f"Expected page='notifications', got '{page}'"

    # Check that all notifications are marked as read (seen: true) in backend
    notifications = final_state_backend.query({"collection": "notifications", "filter": {}})
    if not isinstance(notifications, list):
        return 0.0, "notifications is not a list"

    if len(notifications) == 0:
        return 1.0, "No notifications to check"

    # Check if all notifications are marked as seen/read
    unread_notifications = []
    for notification in notifications:
        if isinstance(notification, dict):
            seen = notification.get("seen", False)
            if not seen:
                unread_notifications.append(notification.get("_id", "unknown"))

    if len(unread_notifications) > 0:
        return (
            0.0,
            f"Expected all notifications to be marked as read, but {len(unread_notifications)} notification(s) are still unread: {unread_notifications[:5]}",
        )

    return 1.0, "Task completed successfully - all notifications marked as read"


def _validate_looking_for_some_meditation(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Looking for some meditation and wellness content to help wit...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are wellness-related
    wellness_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "wellness"):
                wellness_following_count += 1
        except ValueError:
            continue

    if wellness_following_count < 1:
        return 0.0, f"Expected at least 1 wellness-related followed user(s), got {wellness_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are wellness-related
    wellness_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "wellness"):
                wellness_bookmarks_count += 1
        except ValueError:
            continue

    if wellness_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 wellness-related bookmarked posts, got {wellness_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_want_try_making_some(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Want to try making some traditional Chinese desserts but nee...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for dessert/cooking-related search
    # Verification: "Search performed for dessert/cooking terms"
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    dessert_keywords = TASK_SPECIFIC_KEYWORDS["dessert"]
    has_dessert_search = any(any(keyword in query for keyword in dessert_keywords) for query in search_queries)
    if not has_dessert_search:
        return 0.0, f"searchHistory should contain dessert/cooking-related search terms, got: {search_queries}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are food-related
    food_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "food"):
                food_bookmarks_count += 1
        except ValueError:
            continue

    if food_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 food-related bookmarked posts, got {food_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_saw_someone_post_about(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Saw someone post about their morning routine and it looked s...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on lifestyle-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    lifestyle_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "lifestyle"):
                lifestyle_comment_found = True
                break
        except ValueError:
            continue

    if not lifestyle_comment_found:
        return 0.0, "No comment found on lifestyle-related post"

    return 1.0, "Task completed successfully"


def _validate_trying_learn_watercolor_painting(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I'm trying to learn watercolor painting and need some beginn...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following)}"

    # Check if followed users are art-related
    art_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "art"):
                art_following_count += 1
        except ValueError:
            continue

    if art_following_count < 2:
        return 0.0, f"Expected at least 2 art-related followed user(s), got {art_following_count}"

    # Check bookmarks or liked posts (at least 3)
    bookmarks = current_user.get("bookmarks", [])
    liked = current_user.get("liked", [])

    art_content_count = 0
    for post_id in list(bookmarks) + list(liked):
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "art"):
                art_content_count += 1
        except ValueError:
            continue

    if art_content_count < 3:
        return 0.0, f"Expected at least 3 art-related bookmarked or liked posts, got {art_content_count}"

    return 1.0, "Task completed successfully"


def _validate_need_some_winter_fashion(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Need some winter fashion inspiration that works for cold wea...

    Initial State Assumptions:
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for album (collection) with at least 4 posts
    # Verification: "Collection with winter/fashion-related name containing ≥4 winter outfit posts"
    # Note: We check for album existence with ≥4 posts, not the name
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = None
    for album in albums:
        post_ids = album.get("postIds", [])
        if isinstance(post_ids, list) and len(post_ids) >= 4:
            # Check if album contains fashion-related posts
            fashion_posts_in_album = 0
            for post_id in post_ids:
                try:
                    post = _get_post(final_state_backend, post_id)
                    if _check_topic_relevance(post, "fashion"):
                        fashion_posts_in_album += 1
                except ValueError:
                    continue
            if fashion_posts_in_album >= 4:
                album_found = album
                break

    if not album_found:
        return 0.0, "No album (collection) found with at least 4 fashion-related posts"

    return 1.0, "Task completed successfully"


def _validate_friend_keeps_talking_about(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My friend keeps talking about this productivity system she s...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for productivity/organization-related search
    # Verification: "Search performed for productivity/organization terms"
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    productivity_keywords = TASK_SPECIFIC_KEYWORDS["productivity"]
    has_productivity_search = any(any(keyword in query for keyword in productivity_keywords) for query in search_queries)
    if not has_productivity_search:
        return 0.0, f"searchHistory should contain productivity/organization-related search terms, got: {search_queries}"

    # Check bookmarks OR saved (collection)
    # Verification: "≥3 productivity posts bookmarked or saved"
    productivity_count = 0

    # Check bookmarks
    bookmarks = current_user.get("bookmarks", [])
    if isinstance(bookmarks, list):
        for post_id in bookmarks:
            try:
                post = _get_post(final_state_backend, post_id)
                if _check_topic_relevance(post, "lifestyle"):
                    productivity_count += 1
            except ValueError:
                continue

    # Check albums/collections (saved)
    albums = current_user.get("albums", [])
    if isinstance(albums, list):
        for album in albums:
            post_ids = album.get("postIds", [])
            if isinstance(post_ids, list):
                for post_id in post_ids:
                    try:
                        post = _get_post(final_state_backend, post_id)
                        if _check_topic_relevance(post, "lifestyle"):
                            productivity_count += 1
                    except ValueError:
                        continue

    if productivity_count < 3:
        return 0.0, f"Expected at least 3 productivity posts bookmarked or saved, got {productivity_count}"

    return 1.0, "Task completed successfully"


def _validate_want_more_encouraging_content(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I want to be more encouraging to content creators I follow. ...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    if not isinstance(user_comments, list):
        return 0.0, "comments is not a list"

    comment_count = len(user_comments)
    if comment_count < 4:
        return 0.0, f"Expected at least 4 comments, got {comment_count}"

    return 1.0, "Task completed successfully"


def _validate_looking_upgrade_skincare_routine(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Looking to upgrade my skincare routine without breaking the ...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are beauty-related
    beauty_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "beauty"):
                beauty_following_count += 1
        except ValueError:
            continue

    if beauty_following_count < 1:
        return 0.0, f"Expected at least 1 beauty-related followed user(s), got {beauty_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are beauty-related
    beauty_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "beauty"):
                beauty_bookmarks_count += 1
        except ValueError:
            continue

    if beauty_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 beauty-related bookmarked posts, got {beauty_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_planning_staycation_and_want(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Planning a staycation in 上海 and want to discover hidden gems...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check searchHistory for 上海-related search
    has_search, queries = _check_search_history(final_state_backend, current_user_id, ["上海"])
    if not has_search:
        return 0.0, f"searchHistory should contain '上海' in search query, got: {queries}"

    # Check bookmarks OR saved (collection) - posts must mention 上海
    shanghai_keywords = TASK_SPECIFIC_KEYWORDS["shanghai"]
    shanghai_travel_count = _count_posts_in_bookmarks_and_albums(final_state_backend, current_user, "travel", shanghai_keywords)

    if shanghai_travel_count < 3:
        return (
            0.0,
            f"Expected at least 3 上海 location posts (mentioning 上海 and travel related) bookmarked or saved, got {shanghai_travel_count}",
        )

    return 1.0, "Task completed successfully"


def _validate_been_struggling_with_work(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I've been struggling with work-life balance and need some pe...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on lifestyle-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    lifestyle_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "lifestyle"):
                lifestyle_comment_found = True
                break
        except ValueError:
            continue

    if not lifestyle_comment_found:
        return 0.0, "No comment found on lifestyle-related post"

    return 1.0, "Task completed successfully"


def _validate_want_learn_more_about(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Want to learn more about sustainable living without being pr...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    lifestyle_following_count = _count_topic_relevant_users(final_state_backend, following, "lifestyle")
    if lifestyle_following_count < 1:
        return 0.0, f"Expected at least 1 lifestyle-related followed user(s), got {lifestyle_following_count}"

    # Check bookmarks - must mention eco/sustainable keywords
    eco_keywords = TASK_SPECIFIC_KEYWORDS["eco"]
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"

    eco_bookmarks_count = _count_topic_relevant_posts(final_state_backend, bookmarks, "lifestyle", eco_keywords)
    if eco_bookmarks_count < 3:
        return (
            0.0,
            f"Expected at least 3 sustainable/eco-related bookmarked posts (mentioning eco keywords), got {eco_bookmarks_count}",
        )

    return 1.0, "Task completed successfully"


def _validate_apartment_balcony_tiny_but(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My apartment balcony is tiny but I want to try growing some ...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for gardening/plant-related search
    # Verification: "Search performed for gardening/plant terms"
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    gardening_keywords = TASK_SPECIFIC_KEYWORDS["gardening"]
    has_gardening_search = any(any(keyword in query for keyword in gardening_keywords) for query in search_queries)
    if not has_gardening_search:
        return 0.0, f"searchHistory should contain gardening/plant-related search terms, got: {search_queries}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are home-related
    home_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "home"):
                home_bookmarks_count += 1
        except ValueError:
            continue

    if home_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 home-related bookmarked posts, got {home_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_keep_seeing_these_amazing_baking(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I keep seeing these amazing baking posts and want to try mak...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on food-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    food_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "food"):
                food_comment_found = True
                break
        except ValueError:
            continue

    if not food_comment_found:
        return 0.0, "No comment found on food-related post"

    return 1.0, "Task completed successfully"


def _validate_need_some_motivation_for(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Need some motivation for my fitness goals and want to follow...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following)}"

    # Check if followed users are fitness-related
    fitness_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "fitness"):
                fitness_following_count += 1
        except ValueError:
            continue

    if fitness_following_count < 2:
        return 0.0, f"Expected at least 2 fitness-related followed user(s), got {fitness_following_count}"

    # Check bookmarks OR liked posts
    # Verification: "≥3 fitness motivation posts liked or saved"
    fitness_content_count = 0

    # Check bookmarks
    bookmarks = current_user.get("bookmarks", [])
    if isinstance(bookmarks, list):
        for post_id in bookmarks:
            try:
                post = _get_post(final_state_backend, post_id)
                if _check_topic_relevance(post, "fitness"):
                    fitness_content_count += 1
            except ValueError:
                continue

    # Check liked posts
    liked = current_user.get("liked", [])
    if isinstance(liked, list):
        for post_id in liked:
            try:
                post = _get_post(final_state_backend, post_id)
                if _check_topic_relevance(post, "fitness"):
                    fitness_content_count += 1
            except ValueError:
                continue

    if fitness_content_count < 3:
        return 0.0, f"Expected at least 3 fitness-related posts bookmarked or liked, got {fitness_content_count}"

    return 1.0, "Task completed successfully"


def _validate_curious_about_that_creative(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I'm curious about that Creative Center feature I keep seeing..."""
    page_display_state = final_state_frontend.get("pageDisplayState")
    if page_display_state != "creative":
        return 0.0, f"Expected pageDisplayState='creative', got '{page_display_state}'"

    return 1.0, "Task completed successfully"


def _validate_looking_for_some_book(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Looking for some book recommendations from people who have s...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are culture/literature-related
    # Verification: "user following ≥1 book-focused account"
    literature_keywords = TASK_SPECIFIC_KEYWORDS["literature"]
    literature_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            category = (user.get("category", "") or "").lower()
            bio = (user.get("bio", "") or "").lower()
            if any(keyword in category or keyword in bio for keyword in literature_keywords):
                literature_following_count += 1
        except ValueError:
            continue

    if literature_following_count < 1:
        return 0.0, f"Expected at least 1 literature/book-focused followed user(s), got {literature_following_count}"

    return 1.0, "Task completed successfully"


def _validate_want_try_some_new_makeup(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Want to try some new makeup techniques but I'm pretty basic ...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for makeup tutorial-related search
    # Verification: "Search performed for makeup tutorial terms"
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    makeup_keywords = TASK_SPECIFIC_KEYWORDS["makeup"]
    has_makeup_search = any(any(keyword in query for keyword in makeup_keywords) for query in search_queries)
    if not has_makeup_search:
        return 0.0, f"searchHistory should contain makeup tutorial-related search terms, got: {search_queries}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are beauty-related
    beauty_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "beauty"):
                beauty_bookmarks_count += 1
        except ValueError:
            continue

    if beauty_bookmarks_count < 3:
        return 0.0, f"Expected at least 3 beauty-related bookmarked posts, got {beauty_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_someone_posted_gorgeous_photos(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Someone posted gorgeous photos from their recent trip and I ...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on travel-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    travel_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "travel"):
                travel_comment_found = True
                break
        except ValueError:
            continue

    if not travel_comment_found:
        return 0.0, "No comment found on travel-related post"

    return 1.0, "Task completed successfully"


def _validate_trying_develop_better_morning(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I'm trying to develop better morning habits and need some re...

    Initial State Assumptions:
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check for album (collection) with at least 3 lifestyle posts mentioning morning
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    morning_keywords = TASK_SPECIFIC_KEYWORDS["morning"]
    album_found = _find_album_with_topic_posts(final_state_backend, albums, "lifestyle", 3, morning_keywords)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 lifestyle-related posts mentioning morning"

    return 1.0, "Task completed successfully"


def _validate_workspace_home_pretty_chaotic(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My workspace at home is pretty chaotic and I need better org...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    home_following_count = _count_topic_relevant_users(final_state_backend, following, "home")
    if home_following_count < 1:
        return 0.0, f"Expected at least 1 home-related followed user(s), got {home_following_count}"

    # Check bookmarks - must mention desk setup or home office
    workspace_keywords = TASK_SPECIFIC_KEYWORDS["workspace"]
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"

    workspace_bookmarks_count = _count_topic_relevant_posts(final_state_backend, bookmarks, "home", workspace_keywords)
    if workspace_bookmarks_count < 3:
        return (
            0.0,
            f"Expected at least 3 workspace/office-related bookmarked posts (mentioning desk setup or home office), got {workspace_bookmarks_count}",
        )

    return 1.0, "Task completed successfully"


def _validate_want_more_active_supporting(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I want to be more active in supporting artists and creators ...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check for comment on art-related post
    # Query comments collection for comments by current user
    user_comments = final_state_backend.query({"collection": "comments", "filter": {"authorId": current_user_id}})
    art_comment_found = False

    for comment in user_comments:
        post_id = comment.get("postId")
        if not post_id:
            continue

        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "art"):
                art_comment_found = True
                break
        except ValueError:
            continue

    if not art_comment_found:
        return 0.0, "No comment found on art-related post"

    return 1.0, "Task completed successfully"


def _validate_looking_for_some_easy(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate Looking for some easy weeknight dinner ideas that don't requ...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check searchHistory for quick/easy recipe-related search
    # Verification: "Search performed for quick/easy recipe terms"
    search_history = final_state_backend.query({"collection": "searchHistory", "filter": {"userId": current_user_id}})
    if not isinstance(search_history, list):
        search_history = []

    search_queries = [entry.get("query", "").lower() for entry in search_history if isinstance(entry, dict)]
    quick_recipe_keywords = TASK_SPECIFIC_KEYWORDS["quick_recipe"]
    has_quick_recipe_search = any(any(keyword in query for keyword in quick_recipe_keywords) for query in search_queries)
    if not has_quick_recipe_search:
        return 0.0, f"searchHistory should contain quick/easy recipe-related search terms, got: {search_queries}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 4:
        return 0.0, f"Expected at least 4 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are food-related
    food_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "food"):
                food_bookmarks_count += 1
        except ValueError:
            continue

    if food_bookmarks_count < 4:
        return 0.0, f"Expected at least 4 food-related bookmarked posts, got {food_bookmarks_count}"

    return 1.0, "Task completed successfully"


def _validate_been_thinking_about_trying(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I've been thinking about trying yoga but feel intimidated by...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are fitness-related
    fitness_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "fitness"):
                fitness_following_count += 1
        except ValueError:
            continue

    if fitness_following_count < 1:
        return 0.0, f"Expected at least 1 fitness-related followed user(s), got {fitness_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are fitness-related and mention beginner yoga
    # Verification: "≥3 beginner yoga posts saved"
    beginner_yoga_keywords = TASK_SPECIFIC_KEYWORDS["beginner_yoga"]
    fitness_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "fitness") and _check_post_contains_keywords(post, beginner_yoga_keywords):
                fitness_bookmarks_count += 1
        except ValueError:
            continue

    if fitness_bookmarks_count < 3:
        return (
            0.0,
            f"Expected at least 3 beginner yoga-related bookmarked posts (mentioning beginner yoga), got {fitness_bookmarks_count}",
        )

    return 1.0, "Task completed successfully"


def _validate_want_update_wardrobe_with(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Want to update my wardrobe with some versatile pieces that w...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check bookmarks OR collection
    # Verification: "≥4 versatile fashion/capsule wardrobe posts bookmarked or in fashion collection"
    fashion_count = 0

    # Check bookmarks
    bookmarks = current_user.get("bookmarks", [])
    if isinstance(bookmarks, list):
        for post_id in bookmarks:
            try:
                post = _get_post(final_state_backend, post_id)
                if _check_topic_relevance(post, "fashion"):
                    fashion_count += 1
            except ValueError:
                continue

    # Check albums/collections
    albums = current_user.get("albums", [])
    if isinstance(albums, list):
        for album in albums:
            post_ids = album.get("postIds", [])
            if isinstance(post_ids, list):
                for post_id in post_ids:
                    try:
                        post = _get_post(final_state_backend, post_id)
                        if _check_topic_relevance(post, "fashion"):
                            fashion_count += 1
                    except ValueError:
                        continue

    if fashion_count < 4:
        return 0.0, f"Expected at least 4 fashion-related posts bookmarked or in collection, got {fashion_count}"

    return 1.0, "Task completed successfully"


def _validate_keep_forgetting_check_liked(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I keep forgetting to check my liked posts section to revisit...

    Verification: "User on profile page viewing liked posts or collections section"
    """
    page = final_state_frontend.get("page")
    if page != "profile":
        return 0.0, f"Expected page='profile', got '{page}'"
    profile_view = final_state_frontend.get("profileView")
    # Check for likes section (not bookmarks)
    if profile_view != "likes":
        return 0.0, f"Expected profileView='likes', got '{profile_view}'"

    return 1.0, "Task completed successfully"


def _validate_looking_for_some_photography(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Looking for some photography inspiration and tips to improve...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list):
        return 0.0, "following is not a list"
    if len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following)}"

    # Check if followed users are art-related
    art_following_count = 0
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "art"):
                art_following_count += 1
        except ValueError:
            continue

    if art_following_count < 1:
        return 0.0, f"Expected at least 1 art-related followed user(s), got {art_following_count}"

    # Check bookmarks count
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list):
        return 0.0, "bookmarks is not a list"
    if len(bookmarks) < 3:
        return 0.0, f"Expected at least 3 bookmarked post(s), got {len(bookmarks)}"

    # Check if bookmarked posts are art-related and mention photography techniques
    # Verification: "≥3 photography posts saved"
    photography_technique_keywords = TASK_SPECIFIC_KEYWORDS["photography_technique"]
    art_bookmarks_count = 0
    for post_id in bookmarks:
        try:
            post = _get_post(final_state_backend, post_id)
            if _check_topic_relevance(post, "art") and _check_post_contains_keywords(post, photography_technique_keywords):
                art_bookmarks_count += 1
        except ValueError:
            continue

    if art_bookmarks_count < 3:
        return (
            0.0,
            f"Expected at least 3 photography-related bookmarked posts (mentioning photography techniques), got {art_bookmarks_count}",
        )

    return 1.0, "Task completed successfully"


def _validate_someone_shared_really_helpful(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Someone shared a really helpful study technique that I want ...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check bookmarks OR collection
    # Verification: "≥3 educational/study posts bookmarked or in productivity-related collection"
    education_count = 0

    # Check bookmarks
    bookmarks = current_user.get("bookmarks", [])
    if isinstance(bookmarks, list):
        for post_id in bookmarks:
            try:
                post = _get_post(final_state_backend, post_id)
                if _check_topic_relevance(post, "education"):
                    education_count += 1
            except ValueError:
                continue

    # Check albums/collections
    albums = current_user.get("albums", [])
    if isinstance(albums, list):
        for album in albums:
            post_ids = album.get("postIds", [])
            if isinstance(post_ids, list):
                for post_id in post_ids:
                    try:
                        post = _get_post(final_state_backend, post_id)
                        if _check_topic_relevance(post, "education"):
                            education_count += 1
                    except ValueError:
                        continue

    if education_count < 3:
        return 0.0, f"Expected at least 3 education-related posts bookmarked or in collection, got {education_count}"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 51: I'm trying to get back into a fitness routine after being lazy all winter...
# =============================================================================


def _validate_trying_get_back_into_fitness(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I'm trying to get back into a fitness routine after being lazy all winter...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    fitness_following_count = _count_topic_relevant_users(final_state_backend, following, "fitness")
    if fitness_following_count < 2:
        return 0.0, f"Expected at least 2 fitness-related followed user(s), got {fitness_following_count}"

    # Check for album (collection) with at least 3 fitness-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = _find_album_with_topic_posts(final_state_backend, albums, "fitness", 3)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 fitness-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 52: Been seeing amazing makeup looks on my feed lately...
# =============================================================================


def _validate_been_seeing_amazing_makeup(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Been seeing amazing makeup looks on my feed lately...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    beauty_following_count = _count_topic_relevant_users(final_state_backend, following, "beauty")
    if beauty_following_count < 2:
        return 0.0, f"Expected at least 2 beauty-related followed user(s), got {beauty_following_count}"

    # Check for album (collection) with at least 3 eye makeup-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    # Use eye makeup keywords to ensure posts are specifically about eye makeup
    eye_makeup_keywords = [
        "eye makeup",
        "eyeshadow",
        "eyeliner",
        "mascara",
        "eye look",
        "eye tutorial",
        "眼妆",
        "眼影",
        "眼线",
        "睫毛",
        "眼部妆容",
        "眼妆教程",
    ]
    album_found = _find_album_with_topic_posts(final_state_backend, albums, "beauty", 3, eye_makeup_keywords)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 eye makeup-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 53: My friend just got a puppy and I want to send her some helpful content...
# =============================================================================


def _validate_friend_just_got_puppy(final_state_backend: Backend, final_state_frontend: Dict[str, Any]) -> Tuple[float, str]:
    """Validate My friend just got a puppy and I want to send her some helpful content...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    pets_following_count = _count_topic_relevant_users(final_state_backend, following, "pets")
    if pets_following_count < 2:
        return 0.0, f"Expected at least 2 pet-related followed user(s), got {pets_following_count}"

    # Check for album (collection) with at least 3 pet-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = _find_album_with_topic_posts(final_state_backend, albums, "pets", 3)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 pet-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 54: Planning to redecorate my small bedroom and need ideas...
# =============================================================================


def _validate_planning_redecorate_small_bedroom(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Planning to redecorate my small bedroom and need ideas...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    home_following_count = _count_topic_relevant_users(final_state_backend, following, "home")
    if home_following_count < 2:
        return 0.0, f"Expected at least 2 home decor-related followed user(s), got {home_following_count}"

    # Check for album (collection) with at least 3 home-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = _find_album_with_topic_posts(final_state_backend, albums, "home", 3)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 home-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 55: I keep seeing this one creator posting amazing travel vlogs...
# =============================================================================


def _validate_keep_seeing_creator_posting_travel(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate I keep seeing this one creator posting amazing travel vlogs...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.liked is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    try:
        current_user = _get_current_user(final_state_backend)
    except ValueError as e:
        return 0.0, str(e)

    # Check following count - at least 1 travel-related account
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 1:
        return 0.0, f"Expected at least 1 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    travel_following_count = _count_topic_relevant_users(final_state_backend, following, "travel")
    if travel_following_count < 1:
        return 0.0, f"Expected at least 1 travel-related followed user(s), got {travel_following_count}"

    # Find a travel-related account that the user is following
    travel_account_id = None
    for user_id in following:
        try:
            user = _get_user(final_state_backend, user_id)
            if _check_user_category_relevance(user, "travel"):
                travel_account_id = user_id
                break
        except ValueError:
            continue

    if not travel_account_id:
        return 0.0, "No travel-related account found in following list"

    # Check if user has liked at least 2 posts from that account's profile
    has_enough_likes, like_count = _count_liked_posts_on_account_profile(
        final_state_backend, current_user_id, travel_account_id, "travel", 2
    )
    if not has_enough_likes:
        return 0.0, f"Expected at least 2 posts liked on travel account's profile, got {like_count}"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 56: Trying to eat healthier but all the diet content online is so extreme...
# =============================================================================


def _validate_trying_eat_healthier_extreme(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Trying to eat healthier but all the diet content online is so extreme...

    Initial State Assumptions:
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check for album (collection) with at least 3 food-related posts (healthy eating/meal prep)
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    # Use healthy_food keywords to ensure posts are about healthy eating/meal prep
    healthy_food_keywords = TASK_SPECIFIC_KEYWORDS.get("healthy_food", [])
    album_found = _find_album_with_topic_posts(final_state_backend, albums, "food", 3, healthy_food_keywords)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 healthy eating/meal prep-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 57: Saw someone post a gorgeous outfit earlier today...
# =============================================================================


def _validate_saw_someone_post_gorgeous_outfit(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Saw someone post a gorgeous outfit earlier today...

    Initial State Assumptions:
    - No comments from currentUser exist before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    has_comment, _ = _has_comment_on_topic(final_state_backend, current_user_id, "fashion", 1)
    if not has_comment:
        return 0.0, "No comment found on fashion-related post"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 58: My eyes are getting tired from this bright screen...
# =============================================================================


def _validate_eyes_getting_tired_bright_screen(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate My eyes are getting tired from this bright screen...

    Initial State Assumptions:
    - themeMode is 'light' before task starts
    """
    theme_mode = final_state_frontend.get("themeMode")
    if theme_mode != "dark":
        return 0.0, f"Expected themeMode='dark', got '{theme_mode}'"

    # Check if user is on notifications page OR notifications have been viewed
    page = final_state_frontend.get("page")
    if page == "notifications":
        return 1.0, "Task completed successfully - user on notifications page"

    # Check if notifications have been viewed (all marked as seen)
    notifications = final_state_backend.query({"collection": "notifications", "filter": {}})
    if isinstance(notifications, list) and len(notifications) > 0:
        unread_notifications = [
            n.get("_id", "unknown") for n in notifications if isinstance(n, dict) and not n.get("seen", False)
        ]
        if len(unread_notifications) == 0:
            return 1.0, "Task completed successfully - all notifications viewed"
        else:
            return (
                0.0,
                f"Expected user to be on notifications page or all notifications viewed, but {len(unread_notifications)} notification(s) are still unread",
            )

    return 0.0, "Expected user to be on notifications page or notifications to have been viewed"


# =============================================================================
# Task 59: Getting into skincare lately and want to learn proper routines...
# =============================================================================


def _validate_getting_into_skincare_lately(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Getting into skincare lately and want to learn proper routines...

    Initial State Assumptions:
    - currentUser.searchHistory is empty [] before task starts
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user_id = final_state_frontend.get("currentUserId", "0")
    if not current_user_id:
        return 0.0, "currentUserId missing in frontend state"

    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check searchHistory for skincare-related search
    skincare_keywords = TASK_SPECIFIC_KEYWORDS.get("skincare", ["skincare", "护肤", "美容", "routine"])
    has_search, queries = _check_search_history(final_state_backend, current_user_id, skincare_keywords)
    if not has_search:
        return 0.0, f"searchHistory should contain skincare-related search terms, got: {queries}"

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    beauty_following_count = _count_topic_relevant_users(final_state_backend, following, "beauty")
    if beauty_following_count < 2:
        return 0.0, f"Expected at least 2 beauty/skincare-related followed user(s), got {beauty_following_count}"

    # Check for album (collection) with at least 3 beauty/skincare-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    album_found = _find_album_with_topic_posts(final_state_backend, albums, "beauty", 3)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 skincare-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Task 60: Need some motivation for my weight loss journey...
# =============================================================================


def _validate_need_motivation_weight_loss(
    final_state_backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """Validate Need some motivation for my weight loss journey...

    Initial State Assumptions:
    - currentUser.following is empty [] before task starts
    - currentUser.bookmarks is empty [] before task starts
    - currentUser.albums is empty [] before task starts
    """
    current_user, error = _get_current_user_safe(final_state_backend)
    if error:
        return 0.0, error

    # Check following count
    following = current_user.get("following", [])
    if not isinstance(following, list) or len(following) < 2:
        return 0.0, f"Expected at least 2 followed user(s), got {len(following) if isinstance(following, list) else 0}"

    fitness_following_count = _count_topic_relevant_users(final_state_backend, following, "fitness")
    if fitness_following_count < 2:
        return 0.0, f"Expected at least 2 fitness/health-related followed user(s), got {fitness_following_count}"

    # Check for album (collection) with at least 3 fitness/weight loss-related posts
    albums = current_user.get("albums", [])
    if not isinstance(albums, list):
        return 0.0, "albums is not a list"

    # Use weight loss keywords to ensure posts are about weight loss/fitness transformation
    weight_loss_keywords = ["weight loss", "weightloss", "transformation", "减脂", "减肥", "瘦身", "减重"]
    album_found = _find_album_with_topic_posts(final_state_backend, albums, "fitness", 3, weight_loss_keywords)
    if not album_found:
        return 0.0, "No album (collection) found with at least 3 weight loss/fitness-related posts"

    return 1.0, "Task completed successfully"


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================
# This dictionary is defined at the end of the file to ensure all functions
# are defined before being referenced, avoiding NameError exceptions.
#
# Task Mapping Structure:
# - Tasks 1-20 (current): Use _validate_generated_task_X_... functions
#   These are defined as aliases at the bottom of the file (lines ~7515-7534)
#   and use Backend ABC validation (different signature than ValidateTask)
# - Tasks 21-60: Use _validate_generated_task_X_... functions in this dict
# - Legacy tasks (renamed files): Use _validate_<name> functions
#
# File naming convention:
# - task-1 through task-20: Current tasks matching xhs-generated-tasks.json
# - Files without task- prefix: Legacy tasks (old numbering system)

REWARD_FUNCTIONS_XIAOHONGSHU_V2: Dict[str, Union[ValidateTask, Callable[[Backend, Dict[str, Any]], Tuple[float, str]]]] = {
    # Navigation & UI State Tasks
    "_validate_access_creative_center_page": _validate_access_creative_center_page,
    "_validate_album_view": _validate_album_view,
    "_validate_back_page": _validate_back_page,
    "_validate_bookmarks_view": _validate_bookmarks_view,
    "_validate_business_hover": _validate_business_hover,
    "_validate_creative_center_hover": _validate_creative_center_hover,
    "_validate_creative_dashboard": _validate_creative_dashboard,
    "_validate_dark_mode": _validate_dark_mode,
    "_validate_light_mode": _validate_light_mode,
    "_validate_system_theme": _validate_system_theme,
    "_validate_likes_view": _validate_likes_view,
    "_validate_navigate_own_profile": _validate_navigate_own_profile,
    "_validate_open_an_album": _validate_open_an_album,
    "_validate_open_post_modal": _validate_open_post_modal,
    "_validate_open_video_pause": _validate_open_video_pause,
    "_validate_search_input": _validate_search_input,
    "_validate_search_filter": _validate_search_filter,
    "_validate_set_filter": _validate_set_filter,
    "_validate_share": _validate_share,
    "_validate_watch_full_video": _validate_watch_full_video,
    "_validate_find_mention": _validate_find_mention,
    # Like/Bookmark Tasks
    "_validate_like_post": _validate_like_post,
    "_validate_unlike_post": _validate_unlike_post,
    "_validate_bookmark_post": _validate_bookmark_post,
    "_validate_like_and_bookmark": _validate_like_and_bookmark,
    "_validate_like_3_sequential": _validate_like_3_sequential,
    "_validate_bookmark_and_like": _validate_bookmark_and_like,
    "_validate_bookmark_album": _validate_bookmark_album,
    # Follow/Unfollow Tasks
    "_validate_follow_user": _validate_follow_user,
    "_validate_unfollow_user": _validate_unfollow_user,
    "_validate_follow_new_follower": _validate_follow_new_follower,
    "_validate_search_and_follow_all": _validate_search_and_follow_all,
    # Comment Tasks
    "_validate_comment_on_video": _validate_comment_on_video,
    "_validate_comment_on_two_separate_posts": _validate_comment_on_two_separate_posts,
    "_validate_reply_chain": _validate_reply_chain,
    "_validate_comment_interaction_series": _validate_comment_interaction_series,
    "_validate_bookmark_album_comment_reply": _validate_bookmark_album_comment_reply,
    # Album & Complex Tasks
    "_validate_create_album_add": _validate_create_album_add,
    "_validate_open_album_watch_video": _validate_open_album_watch_video,
    "_validate_remove_bookmarks_in_album": _validate_remove_bookmarks_in_album,
    "_validate_edit_album_collection": _validate_edit_album_collection,
    "_validate_draft_article": _validate_draft_article,
    "_validate_edit_draft": _validate_edit_draft,
    # Search & Multi-Action Tasks
    "_validate_clear_search_history": _validate_clear_search_history,
    "_validate_search_and_like": _validate_search_and_like,
    "_validate_search_user_and_like_all": _validate_search_user_and_like_all,
    "_validate_search_like_unbookmark": _validate_search_like_unbookmark,
    "_validate_search_own_profile_reply": _validate_search_own_profile_reply,
    "_validate_search_history_like": _validate_search_history_like,
    "_validate_advanced_filter_search_follow": _validate_advanced_filter_search_follow,
    # Dark Mode Combination Tasks
    "_validate_dark_mode_filter": _validate_dark_mode_filter,
    "_validate_dark_mode_like": _validate_dark_mode_like,
    "_validate_dark_mode_notif_like": _validate_dark_mode_notif_like,
    "_validate_dark_mode_search_watch": _validate_dark_mode_search_watch,
    "_validate_filter_comment_profile_dark": _validate_filter_comment_profile_dark,
    "_validate_like_search_follow_dark": _validate_like_search_follow_dark,
    # Complex Multi-Action Tasks
    "_validate_comprehensive_user_interaction": _validate_comprehensive_user_interaction,
    "_validate_cross_user_engagement": _validate_cross_user_engagement,
    "_validate_unlike_currentuser_likes": _validate_unlike_currentuser_likes,
    # Aliases for task files that use names without underscores
    "_validate_creativ_edashboard": _validate_creative_dashboard,
    "_validate_clear_search_history": _validate_clear_search_history,
    "_validate_search_history_like": _validate_search_history_like,
    "_validate_edit_draft": _validate_edit_draft,
    # Generated Tasks 1-20 (Backend ABC validation with different signature)
    "_validate_starting_new_fitness_routine": _validate_starting_new_fitness_routine,
    "_validate_friend_recommended_some_beauty": _validate_friend_recommended_some_beauty,
    "_validate_this_eye_strain_getting": _validate_this_eye_strain_getting,
    "_validate_want_learn_some_simple": _validate_want_learn_some_simple,
    "_validate_saw_amazing_travel_photo": _validate_saw_amazing_travel_photo,
    "_validate_redecorating_small_bedroom_and": _validate_redecorating_small_bedroom_and,
    "_validate_need_find_some_quick": _validate_need_find_some_quick,
    "_validate_cat_has_been_acting": _validate_cat_has_been_acting,
    "_validate_planning_weekend_trip_and": _validate_planning_weekend_trip_and,
    "_validate_someone_posted_amazing_nail": _validate_someone_posted_amazing_nail,
    "_validate_been_getting_back_into": _validate_been_getting_back_into,
    "_validate_looking_for_budget_friendly": _validate_looking_for_budget_friendly,
    "_validate_this_bright_screen_hurting": _validate_this_bright_screen_hurting,
    "_validate_workout_motivation_has_been": _validate_workout_motivation_has_been,
    "_validate_need_organize_tiny_kitchen": _validate_need_organize_tiny_kitchen,
    "_validate_want_try_some_new": _validate_want_try_some_new,
    "_validate_thinking_about_getting_dog": _validate_thinking_about_getting_dog,
    "_validate_someone_shared_really_creative": _validate_someone_shared_really_creative,
    "_validate_trying_eat_healthier_but": _validate_trying_eat_healthier_but,
    "_validate_want_support_some_smaller": _validate_want_support_some_smaller,
    # Generated Tasks 21-60
    "_validate_planning_redecorate_living_room": _validate_planning_redecorate_living_room,
    "_validate_keep_seeing_these_amazing_street_style": _validate_keep_seeing_these_amazing_street_style,
    "_validate_notifications_are_probably_piling": _validate_notifications_are_probably_piling,
    "_validate_looking_for_some_meditation": _validate_looking_for_some_meditation,
    "_validate_want_try_making_some": _validate_want_try_making_some,
    "_validate_saw_someone_post_about": _validate_saw_someone_post_about,
    "_validate_trying_learn_watercolor_painting": _validate_trying_learn_watercolor_painting,
    "_validate_need_some_winter_fashion": _validate_need_some_winter_fashion,
    "_validate_friend_keeps_talking_about": _validate_friend_keeps_talking_about,
    "_validate_want_more_encouraging_content": _validate_want_more_encouraging_content,
    "_validate_looking_upgrade_skincare_routine": _validate_looking_upgrade_skincare_routine,
    "_validate_planning_staycation_and_want": _validate_planning_staycation_and_want,
    "_validate_been_struggling_with_work": _validate_been_struggling_with_work,
    "_validate_want_learn_more_about": _validate_want_learn_more_about,
    "_validate_apartment_balcony_tiny_but": _validate_apartment_balcony_tiny_but,
    "_validate_keep_seeing_these_amazing_baking": _validate_keep_seeing_these_amazing_baking,
    "_validate_need_some_motivation_for": _validate_need_some_motivation_for,
    "_validate_curious_about_that_creative": _validate_curious_about_that_creative,
    "_validate_looking_for_some_book": _validate_looking_for_some_book,
    "_validate_want_try_some_new_makeup": _validate_want_try_some_new_makeup,
    "_validate_someone_posted_gorgeous_photos": _validate_someone_posted_gorgeous_photos,
    "_validate_trying_develop_better_morning": _validate_trying_develop_better_morning,
    "_validate_workspace_home_pretty_chaotic": _validate_workspace_home_pretty_chaotic,
    "_validate_want_more_active_supporting": _validate_want_more_active_supporting,
    "_validate_looking_for_some_easy": _validate_looking_for_some_easy,
    "_validate_been_thinking_about_trying": _validate_been_thinking_about_trying,
    "_validate_want_update_wardrobe_with": _validate_want_update_wardrobe_with,
    "_validate_keep_forgetting_check_liked": _validate_keep_forgetting_check_liked,
    "_validate_looking_for_some_photography": _validate_looking_for_some_photography,
    "_validate_someone_shared_really_helpful": _validate_someone_shared_really_helpful,
    "_validate_trying_get_back_into_fitness": _validate_trying_get_back_into_fitness,
    "_validate_been_seeing_amazing_makeup": _validate_been_seeing_amazing_makeup,
    "_validate_friend_just_got_puppy": _validate_friend_just_got_puppy,
    "_validate_planning_redecorate_small_bedroom": _validate_planning_redecorate_small_bedroom,
    "_validate_keep_seeing_creator_posting_travel": _validate_keep_seeing_creator_posting_travel,
    "_validate_trying_eat_healthier_extreme": _validate_trying_eat_healthier_extreme,
    "_validate_saw_someone_post_gorgeous_outfit": _validate_saw_someone_post_gorgeous_outfit,
    "_validate_eyes_getting_tired_bright_screen": _validate_eyes_getting_tired_bright_screen,
    "_validate_getting_into_skincare_lately": _validate_getting_into_skincare_lately,
    "_validate_need_motivation_weight_loss": _validate_need_motivation_weight_loss,
    # Legacy task mappings (without task- prefix in filename)
    "_validate_travel_planning": _validate_travel_planning,
    "_validate_beauty_product_research": _validate_beauty_product_research,
    "_validate_fashion_inspiration": _validate_fashion_inspiration,
    "_validate_recipe_discovery": _validate_recipe_discovery,
    "_validate_interior_design_discovery": _validate_interior_design_discovery,
    "_validate_fitness_journey": _validate_fitness_journey,
    "_validate_pet_care_training": _validate_pet_care_training,
    "_validate_photography_research": _validate_photography_research,
    "_validate_study_techniques": _validate_study_techniques,
    "_validate_plant_care_gardening": _validate_plant_care_gardening,
    "_validate_wedding_planning": _validate_wedding_planning,
    "_validate_career_development": _validate_career_development,
    "_validate_language_learning": _validate_language_learning,
    "_validate_coffee_culture": _validate_coffee_culture,
    "_validate_sustainable_living": _validate_sustainable_living,
    "_validate_cat_care_basics": _validate_cat_care_basics,
    "_validate_bullet_journal_inspiration": _validate_bullet_journal_inspiration,
    "_validate_dark_mode_notifications": _validate_dark_mode_notifications,
    "_validate_shanghai_coffee_discovery": _validate_shanghai_coffee_discovery,
    "_validate_beginner_yoga_discovery": _validate_beginner_yoga_discovery,
}
