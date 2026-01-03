"""
Reward functions for JD (JingDong) e-commerce SPA tasks - V2 Architecture.

This version includes both frontend and backend validation with bundled reward functions.
Each task exports a bundle containing:
  - state_key: Dict defining backend queries (collection + filter)
  - validate_backend: Function (state_key, final_state) -> (float, str)
  - validate_frontend: Function (initial_state, final_state) -> (float, str)
"""

import logging
import re
from .backend import Backend
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict, Union

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

def _check_page(final_state: Dict[str, Any], expected_page: str) -> Tuple[bool, str]:
    """Check if the current page matches the expected page."""
    page = final_state.get("page")
    if page != expected_page:
        return False, f"page='{page}' expected '{expected_page}'"
    return True, ""


def _check_search_query_contains(final_state: Dict[str, Any], expected_text: str) -> Tuple[bool, str]:
    """Check if the search query contains the expected text."""
    search_query = final_state.get("searchQuery", "")
    if expected_text not in search_query:
        return False, f"searchQuery='{search_query}' expected to contain '{expected_text}'"
    return True, ""


def _check_search_query_contains_any(final_state: Dict[str, Any], expected_texts: List[str]) -> Tuple[bool, str]:
    """Check if the search query contains any of the expected texts."""
    search_query = final_state.get("searchQuery", "")
    if not any(text in search_query for text in expected_texts):
        return False, f"searchQuery='{search_query}' expected to contain one of {expected_texts}"
    return True, ""


def _check_selected_product_id(final_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    """Check if the selected product ID matches."""
    selected_id = final_state.get("selectedProductId")
    if selected_id != expected_id:
        return False, f"selectedProductId='{selected_id}' expected '{expected_id}'"
    return True, ""


def _check_home_feed_category(final_state: Dict[str, Any], expected_category: str) -> Tuple[bool, str]:
    """Check if the home feed category matches."""
    category = final_state.get("homeFeedCategory")
    if category != expected_category:
        return False, f"homeFeedCategory='{category}' expected '{expected_category}'"
    return True, ""


# =============================================================================
# NAVIGATION TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: go-to-the-cart-page-from-the-homepage
# -----------------------------------------------------------------------------

def _validate_backend_go_to_the_cart_page_from_the_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_the_cart_page_from_the_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart page from homepage"


_validate_go_to_the_cart_page_from_the_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_the_cart_page_from_the_homepage,
    "validate_frontend": _validate_frontend_go_to_the_cart_page_from_the_homepage,
}


# -----------------------------------------------------------------------------
# Task: go-to-a-product-page-from-home
# -----------------------------------------------------------------------------

def _validate_backend_go_to_a_product_page_from_home(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_a_product_page_from_home(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product page from home"


_validate_go_to_a_product_page_from_home: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_a_product_page_from_home,
    "validate_frontend": _validate_frontend_go_to_a_product_page_from_home,
}


# -----------------------------------------------------------------------------
# Task: go-to-homepage-from-product-page
# -----------------------------------------------------------------------------

def _validate_backend_go_to_homepage_from_product_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_homepage_from_product_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to homepage from product page"


_validate_go_to_homepage_from_product_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_homepage_from_product_page,
    "validate_frontend": _validate_frontend_go_to_homepage_from_product_page,
}


# -----------------------------------------------------------------------------
# Task: go-to-cart-page-from-product-detail-page
# -----------------------------------------------------------------------------

def _validate_backend_go_to_cart_page_from_product_detail_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_cart_page_from_product_detail_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart page from product detail"


_validate_go_to_cart_page_from_product_detail_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_cart_page_from_product_detail_page,
    "validate_frontend": _validate_frontend_go_to_cart_page_from_product_detail_page,
}


# -----------------------------------------------------------------------------
# Task: go-to-product-detail-from-search
# -----------------------------------------------------------------------------

def _validate_backend_go_to_product_detail_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_product_detail_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product detail from search"


_validate_go_to_product_detail_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_product_detail_from_search,
    "validate_frontend": _validate_frontend_go_to_product_detail_from_search,
}


# -----------------------------------------------------------------------------
# Task: navigate-from-cart-back-to-homepage
# -----------------------------------------------------------------------------

def _validate_backend_navigate_from_cart_back_to_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_from_cart_back_to_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated from cart back to homepage"


_validate_navigate_from_cart_back_to_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_from_cart_back_to_homepage,
    "validate_frontend": _validate_frontend_navigate_from_cart_back_to_homepage,
}


# -----------------------------------------------------------------------------
# Task: navigate-from-search-to-homepage
# -----------------------------------------------------------------------------

def _validate_backend_navigate_from_search_to_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_from_search_to_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated from search to homepage"


_validate_navigate_from_search_to_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_from_search_to_homepage,
    "validate_frontend": _validate_frontend_navigate_from_search_to_homepage,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-cart-from-product-page-via-header
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_cart_from_product_page_via_header(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_cart_from_product_page_via_header(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart from product page via header"


_validate_navigate_to_cart_from_product_page_via_header: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_cart_from_product_page_via_header,
    "validate_frontend": _validate_frontend_navigate_to_cart_from_product_page_via_header,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-cart-from-search-page
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_cart_from_search_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_cart_from_search_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart from search page"


_validate_navigate_to_cart_from_search_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_cart_from_search_page,
    "validate_frontend": _validate_frontend_navigate_to_cart_from_search_page,
}


# -----------------------------------------------------------------------------
# Task: navigate-from-product-to-another-product
# -----------------------------------------------------------------------------

def _validate_backend_navigate_from_product_to_another_product(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_from_product_to_another_product(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-y7z8a9")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "华丰京觅")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated from product to another product"


_validate_navigate_from_product_to_another_product: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_from_product_to_another_product,
    "validate_frontend": _validate_frontend_navigate_from_product_to_another_product,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-product-from-homepage-section
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_product_from_homepage_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_product_from_homepage_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-a1b2c3")
    if not ok:
        return 0.0, error
    ok, error = _check_home_feed_category(final_state, "电脑数码")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product from homepage section"


_validate_navigate_to_product_from_homepage_section: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_product_from_homepage_section,
    "validate_frontend": _validate_frontend_navigate_to_product_from_homepage_section,
}


# -----------------------------------------------------------------------------
# Task: navigate-via-category-sidebar-appliances
# -----------------------------------------------------------------------------

def _validate_backend_navigate_via_category_sidebar_appliances(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_via_category_sidebar_appliances(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "家用电器")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated via category sidebar to appliances"


_validate_navigate_via_category_sidebar_appliances: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_via_category_sidebar_appliances,
    "validate_frontend": _validate_frontend_navigate_via_category_sidebar_appliances,
}


# -----------------------------------------------------------------------------
# Task: navigate-via-category-sidebar-electronics
# -----------------------------------------------------------------------------

def _validate_backend_navigate_via_category_sidebar_electronics(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_via_category_sidebar_electronics(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-a1b2c3")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated via category sidebar to Apple iPhone product"


_validate_navigate_via_category_sidebar_electronics: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_via_category_sidebar_electronics,
    "validate_frontend": _validate_frontend_navigate_via_category_sidebar_electronics,
}


# -----------------------------------------------------------------------------
# Task: multi-step-navigation-home-to-product-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_multi_step_navigation_home_to_product_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_multi_step_navigation_home_to_product_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    ok, error = _check_home_feed_category(final_state, "服饰鞋包")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully completed multi-step navigation"


_validate_multistep_navigation_home_to_product_to_cart: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_multi_step_navigation_home_to_product_to_cart,
    "validate_frontend": _validate_frontend_multi_step_navigation_home_to_product_to_cart,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-store-page
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_store_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_store_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "store")
    if not ok:
        return 0.0, error
    selected_store_id = final_state.get("selectedStoreId")
    if not selected_store_id:
        return 0.0, "selectedStoreId is not set"
    return 1.0, "Successfully navigated to store page"


_validate_navigate_to_store_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_store_page,
    "validate_frontend": _validate_frontend_navigate_to_store_page,
}


# -----------------------------------------------------------------------------
# Task: filter-homepage-feed-by-category
# -----------------------------------------------------------------------------

def _validate_backend_filter_homepage_feed_by_category(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for feed filter"


def _validate_frontend_filter_homepage_feed_by_category(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    category = final_state.get("homeFeedCategory", "")
    valid_categories = ["服饰鞋包", "手机通讯", "电脑数码"]
    if category not in valid_categories:
        return 0.0, f"homeFeedCategory='{category}' expected one of {valid_categories}"
    return 1.0, f"Successfully filtered homepage feed by category '{category}'"


_validate_filter_homepage_feed_by_category: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_filter_homepage_feed_by_category,
    "validate_frontend": _validate_frontend_filter_homepage_feed_by_category,
}


# =============================================================================
# SEARCH TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: search-jeep-shirt
# -----------------------------------------------------------------------------

def _validate_backend_search_jeep_shirt(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_jeep_shirt(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_search_query_contains(final_state, "吉普衬衫")
    if not ok:
        return 0.0, error
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 吉普衬衫"


_validate_search_jeep_shirt: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_jeep_shirt,
    "validate_frontend": _validate_frontend_search_jeep_shirt,
}


# -----------------------------------------------------------------------------
# Task: find-a-product-using-search-from-homepage
# -----------------------------------------------------------------------------

def _validate_backend_find_a_product_using_search_from_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_find_a_product_using_search_from_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "吉普衬衫")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for product and navigated to detail page"


_validate_find_a_product_using_search_from_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_find_a_product_using_search_from_homepage,
    "validate_frontend": _validate_frontend_find_a_product_using_search_from_homepage,
}


# -----------------------------------------------------------------------------
# Task: search-a-product-from-another-product-page
# -----------------------------------------------------------------------------

def _validate_backend_search_a_product_from_another_product_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_a_product_from_another_product_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-y7z8a9")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for product and navigated to detail page"


_validate_search_a_product_from_another_product_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_a_product_from_another_product_page,
    "validate_frontend": _validate_frontend_search_a_product_from_another_product_page,
}


# -----------------------------------------------------------------------------
# Task: search-using-multi-term-query
# -----------------------------------------------------------------------------

def _validate_backend_search_using_multi_term_query(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_using_multi_term_query(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if "JEEP 衬衫 男" not in search_query and "JEEP" not in search_query:
        return 0.0, f"searchQuery='{search_query}' expected to contain 'JEEP 衬衫 男'"
    return 1.0, "Successfully searched with multi-term query"


_validate_search_using_multiterm_query: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_multi_term_query,
    "validate_frontend": _validate_frontend_search_using_multi_term_query,
}


# -----------------------------------------------------------------------------
# Task: search-from-search-history
# -----------------------------------------------------------------------------

def _validate_backend_search_from_search_history(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_from_search_history(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    history_items = ["漂亮的裙子", "历史记录", "京东品酒会"]
    if not any(item in search_query for item in history_items):
        return 0.0, f"searchQuery='{search_query}' expected from history {history_items}"
    return 1.0, "Successfully searched from search history"


_validate_search_from_search_history: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_from_search_history,
    "validate_frontend": _validate_frontend_search_from_search_history,
}


# -----------------------------------------------------------------------------
# Task: search-then-use-history-to-research
# -----------------------------------------------------------------------------

def _validate_backend_search_then_use_history_to_research(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    search_history_data = final_state.get("searchHistory")
    if not isinstance(search_history_data, list) or len(search_history_data) == 0:
        return 0.0, "searchHistory is missing or not a list in backend"
    
    # Check that "华为手机" is in the search history
    huawei_found = any(
        item.get("query") == "华为手机" for item in search_history_data
    )
    if not huawei_found:
        return 0.0, "searchHistory does not contain '华为手机'"
    
    return 1.0, "Backend: Successfully added '华为手机' to search history"


def _validate_frontend_search_then_use_history_to_research(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "华为手机")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched then re-searched using search history"


_validate_search_then_use_history_to_research: ValidateTask = {
    "state_key": {
        "searchHistory": {"collection": "searchHistory", "filter": {"query": "华为手机"}},
    },
    "validate_backend": _validate_backend_search_then_use_history_to_research,
    "validate_frontend": _validate_frontend_search_then_use_history_to_research,
}


# -----------------------------------------------------------------------------
# Task: search-using-suggestion-dropdown
# -----------------------------------------------------------------------------

def _validate_backend_search_using_suggestion_dropdown(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_using_suggestion_dropdown(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if "iPhone" not in search_query:
        return 0.0, f"searchQuery='{search_query}' expected to contain 'iPhone'"
    return 1.0, "Successfully searched using suggestion dropdown"


_validate_search_using_suggestion_dropdown: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_suggestion_dropdown,
    "validate_frontend": _validate_frontend_search_using_suggestion_dropdown,
}


# -----------------------------------------------------------------------------
# Task: search-for-apple-iphone
# -----------------------------------------------------------------------------

def _validate_backend_search_for_apple_iphone(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_apple_iphone(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["Apple", "iPhone"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for Apple iPhone"


_validate_search_for_apple_iphone: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_apple_iphone,
    "validate_frontend": _validate_frontend_search_for_apple_iphone,
}


# -----------------------------------------------------------------------------
# Task: search-for-huafeng-instant-noodles
# -----------------------------------------------------------------------------

def _validate_backend_search_for_huafeng_instant_noodles(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_huafeng_instant_noodles(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["华丰", "方便面"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 华丰方便面"


_validate_search_for_huafeng_instant_noodles: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_huafeng_instant_noodles,
    "validate_frontend": _validate_frontend_search_for_huafeng_instant_noodles,
}


# -----------------------------------------------------------------------------
# Task: search-for-aux-massage-chair
# -----------------------------------------------------------------------------

def _validate_backend_search_for_aux_massage_chair(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_aux_massage_chair(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["奥克斯", "按摩椅"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 奥克斯按摩椅"


_validate_search_for_aux_massage_chair: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_aux_massage_chair,
    "validate_frontend": _validate_frontend_search_for_aux_massage_chair,
}


# -----------------------------------------------------------------------------
# Task: search-for-asd-wok
# -----------------------------------------------------------------------------

def _validate_backend_search_for_asd_wok(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_asd_wok(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["爱仕达", "炒锅"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 爱仕达炒锅"


_validate_search_for_asd_wok: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_asd_wok,
    "validate_frontend": _validate_frontend_search_for_asd_wok,
}


# -----------------------------------------------------------------------------
# Task: search-for-huoli-28-laundry-detergent
# -----------------------------------------------------------------------------

def _validate_backend_search_for_huoli_28_laundry_detergent(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_huoli_28_laundry_detergent(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if "活力28" not in search_query and "洗衣液" not in search_query and "活力 28" not in search_query:
        return 0.0, f"searchQuery='{search_query}' expected to contain '活力28' or '洗衣液'"
    return 1.0, "Successfully searched for 活力28洗衣液"


_validate_search_for_huoli_28_laundry_detergent: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_huoli_28_laundry_detergent,
    "validate_frontend": _validate_frontend_search_for_huoli_28_laundry_detergent,
}


# -----------------------------------------------------------------------------
# Task: search-for-stores
# -----------------------------------------------------------------------------

def _validate_backend_search_for_stores(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for store search"


def _validate_frontend_search_for_stores(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_scope = final_state.get("searchScope", "")
    if search_scope != "店铺":
        return 0.0, f"searchScope='{search_scope}' expected '店铺'"
    ok, error = _check_search_query_contains_any(final_state, ["京东自营", "官方旗舰店"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for stores"


_validate_search_for_stores: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_stores,
    "validate_frontend": _validate_frontend_search_for_stores,
}


# -----------------------------------------------------------------------------
# Task: search-clear-history
# -----------------------------------------------------------------------------

def _validate_backend_search_clear_history(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    search_history_data = final_state.get("searchHistory")
    if search_history_data is None:
        return 1.0, "Search history cleared (no data)"
    if isinstance(search_history_data, list) and len(search_history_data) == 0:
        return 1.0, "Search history cleared successfully"
    return 0.0, f"Search history not cleared, found {len(search_history_data) if isinstance(search_history_data, list) else 'invalid'} items"


def _validate_frontend_search_clear_history(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation passed (backend validates history clearing)"


_validate_search_clear_history: ValidateTask = {
    "state_key": {
        "searchHistory": {"collection": "searchHistory", "filter": {}},
    },
    "validate_backend": _validate_backend_search_clear_history,
    "validate_frontend": _validate_frontend_search_clear_history,
}


# -----------------------------------------------------------------------------
# Task: search-using-placeholder
# -----------------------------------------------------------------------------

PLACEHOLDER_SUGGESTIONS = [
    "电脑 显卡",
    "iPhone 15 Pro Max",
    "按摩椅",
    "方便面",
    "洗衣液",
    "炒锅",
    "紫苏酱",
    "男士衬衫",
    "JEEP衬衫",
    "活力28洗衣液",
]


def _validate_backend_search_using_placeholder(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for placeholder search"


def _validate_frontend_search_using_placeholder(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if search_query not in PLACEHOLDER_SUGGESTIONS:
        return 0.0, f"searchQuery='{search_query}' expected one of placeholder suggestions"
    return 1.0, "Successfully searched using placeholder suggestion"


_validate_search_using_placeholder: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_placeholder,
    "validate_frontend": _validate_frontend_search_using_placeholder,
}


# -----------------------------------------------------------------------------
# Task: search-using-arrow-keys
# -----------------------------------------------------------------------------

def _validate_backend_search_using_arrow_keys(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for arrow key search"


def _validate_frontend_search_using_arrow_keys(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "iPhone")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched using arrow key navigation"


_validate_search_using_arrow_keys: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_arrow_keys,
    "validate_frontend": _validate_frontend_search_using_arrow_keys,
}


# -----------------------------------------------------------------------------
# Task: search-from-hot-search-link
# -----------------------------------------------------------------------------

HOT_SEARCH_LINKS = [
    "桌面加湿器办公小型",
    "银饰",
    "羽绒服",
    "发热鼠标垫",
    "保暖内衣",
    "手套",
    "暖手宝",
    "围巾",
    "电动车挡风被加厚",
]


def _validate_backend_search_from_hot_search_link(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for hot search link"


def _validate_frontend_search_from_hot_search_link(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if search_query not in HOT_SEARCH_LINKS:
        return 0.0, f"searchQuery='{search_query}' expected one of hot search links"
    return 1.0, "Successfully searched from hot search link"


_validate_search_from_hot_search_link: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_from_hot_search_link,
    "validate_frontend": _validate_frontend_search_from_hot_search_link,
}


# -----------------------------------------------------------------------------
# Task: search-refine-query
# -----------------------------------------------------------------------------

def _validate_backend_search_refine_query_from_results_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search refinement"


def _validate_frontend_search_refine_query_from_results_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "华为手机")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully refined search query"


_validate_search_refine_query_from_results_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_refine_query_from_results_page,
    "validate_frontend": _validate_frontend_search_refine_query_from_results_page,
}


# -----------------------------------------------------------------------------
# Task: search-and-navigate-to-product-detail
# -----------------------------------------------------------------------------

def _validate_backend_search_and_navigate_to_product_detail(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_and_navigate_to_product_detail(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    selected_id = final_state.get("selectedProductId", "")
    if selected_id not in ["prod-q7r8s9", "prod-y1z2a3b4"]:
        return 0.0, f"selectedProductId='{selected_id}' expected 'prod-q7r8s9' or 'prod-y1z2a3b4'"
    ok, error = _check_search_query_contains(final_state, "紫苏酱")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched and navigated to product detail"


_validate_search_and_navigate_to_product_detail: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_and_navigate_to_product_detail,
    "validate_frontend": _validate_frontend_search_and_navigate_to_product_detail,
}


# =============================================================================
# FILTER & SORT TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: apply-price-range-filter
# -----------------------------------------------------------------------------

def _validate_backend_apply_price_range_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_price_range_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    price_filter = final_state.get("searchPriceFilter")
    if price_filter is None:
        return 0.0, "searchPriceFilter is null, expected to be set"
    if "min" not in price_filter or "max" not in price_filter:
        return 0.0, f"searchPriceFilter={price_filter} missing 'min' or 'max'"
    
    # Validate the specific min and max values
    min_price = price_filter.get("min")
    max_price = price_filter.get("max")
    if min_price != 100:
        return 0.0, f"searchPriceFilter min={min_price}, expected 100"
    if max_price != 300:
        return 0.0, f"searchPriceFilter max={max_price}, expected 300"
    
    return 1.0, f"Successfully applied price range filter {price_filter}"


_validate_apply_price_range_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_price_range_filter,
    "validate_frontend": _validate_frontend_apply_price_range_filter,
}


# -----------------------------------------------------------------------------
# Task: apply-brand-filter-single-brand
# -----------------------------------------------------------------------------

def _validate_backend_apply_brand_filter_single_brand(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_brand_filter_single_brand(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    brand_filter = final_state.get("searchBrandFilter", [])
    if len(brand_filter) != 1:
        return 0.0, f"searchBrandFilter has {len(brand_filter)} brands, expected 1"
    if brand_filter[0] != "JEEP":
        return 0.0, f"searchBrandFilter={brand_filter} expected ['JEEP']"
    return 1.0, "Successfully applied single brand filter"


_validate_apply_brand_filter_single_brand: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_brand_filter_single_brand,
    "validate_frontend": _validate_frontend_apply_brand_filter_single_brand,
}


# -----------------------------------------------------------------------------
# Task: apply-brand-filter-multiple-brands
# -----------------------------------------------------------------------------

def _validate_backend_apply_brand_filter_multiple_brands(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_brand_filter_multiple_brands(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    brand_filter = final_state.get("searchBrandFilter", [])
    if len(brand_filter) < 2:
        return 0.0, f"searchBrandFilter has {len(brand_filter)} brands, expected at least 2"
    valid_combinations = [{"JEEP", "Apple"}, {"ASD", "AUX"}]
    brand_set = set(brand_filter)
    if not any(brand_set == combo for combo in valid_combinations):
        return 0.0, f"searchBrandFilter={brand_filter} expected ['JEEP', 'Apple'] or ['ASD', 'AUX']"
    return 1.0, f"Successfully applied multiple brand filter {brand_filter}"


_validate_apply_brand_filter_multiple_brands: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_brand_filter_multiple_brands,
    "validate_frontend": _validate_frontend_apply_brand_filter_multiple_brands,
}


# -----------------------------------------------------------------------------
# Task: apply-multiple-filters-price-and-brand
# -----------------------------------------------------------------------------

def _validate_backend_apply_multiple_filters_price_and_brand(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_multiple_filters_price_and_brand(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    price_filter = final_state.get("searchPriceFilter")
    brand_filter = final_state.get("searchBrandFilter", [])
    if price_filter is None:
        return 0.0, "searchPriceFilter is null, expected to be set"
    
    # Validate the specific min and max values
    min_price = price_filter.get("min")
    max_price = price_filter.get("max")
    if min_price != 100:
        return 0.0, f"searchPriceFilter min={min_price}, expected 100"
    if max_price != 300:
        return 0.0, f"searchPriceFilter max={max_price}, expected 300"
    
    if len(brand_filter) == 0:
        return 0.0, "searchBrandFilter is empty, expected at least one brand"
    return 1.0, f"Successfully applied multiple filters (price: {price_filter}, brands: {brand_filter})"


_validate_apply_multiple_filters_price_and_brand: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_multiple_filters_price_and_brand,
    "validate_frontend": _validate_frontend_apply_multiple_filters_price_and_brand,
}


# -----------------------------------------------------------------------------
# Task: clear-price-filter
# -----------------------------------------------------------------------------

def _validate_backend_clear_price_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_clear_price_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    price_filter = final_state.get("searchPriceFilter")
    if price_filter is not None:
        return 0.0, f"searchPriceFilter={price_filter} expected null"
    return 1.0, "Successfully cleared price filter"


_validate_clear_price_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_clear_price_filter,
    "validate_frontend": _validate_frontend_clear_price_filter,
}


# -----------------------------------------------------------------------------
# Task: clear-brand-filter
# -----------------------------------------------------------------------------

def _validate_backend_clear_brand_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_clear_brand_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    brand_filter = final_state.get("searchBrandFilter", [])
    if len(brand_filter) != 0:
        return 0.0, f"searchBrandFilter={brand_filter} expected empty []"
    return 1.0, "Successfully cleared brand filter"


_validate_clear_brand_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_clear_brand_filter,
    "validate_frontend": _validate_frontend_clear_brand_filter,
}


# -----------------------------------------------------------------------------
# Task: filter-and-navigate-to-product
# -----------------------------------------------------------------------------

def _validate_backend_filter_and_navigate_to_product(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_filter_and_navigate_to_product(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    
    # Check selectedProductId is exactly prod-m4n5o6
    selected_id = final_state.get("selectedProductId")
    if selected_id != "prod-m4n5o6":
        return 0.0, f"selectedProductId is '{selected_id}', expected 'prod-m4n5o6'"
    
    # Check price filter is set with min=100 and max=300
    price_filter = final_state.get("searchPriceFilter")
    if price_filter is None:
        return 0.0, "searchPriceFilter is null, expected to be set with min: 100, max: 300"
    min_price = price_filter.get("min")
    max_price = price_filter.get("max")
    if min_price != 100:
        return 0.0, f"searchPriceFilter min={min_price}, expected 100"
    if max_price != 300:
        return 0.0, f"searchPriceFilter max={max_price}, expected 300"
    
    # Check brand filter contains JEEP
    brand_filter = final_state.get("searchBrandFilter", [])
    if "JEEP" not in brand_filter:
        return 0.0, f"searchBrandFilter is {brand_filter}, expected to contain 'JEEP'"
    
    return 1.0, f"Successfully filtered and navigated to product '{selected_id}' with price filter {price_filter} and brand filter {brand_filter}"


_validate_filter_and_navigate_to_product: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_filter_and_navigate_to_product,
    "validate_frontend": _validate_frontend_filter_and_navigate_to_product,
}


# -----------------------------------------------------------------------------
# Task: sort-by-price-ascending
# -----------------------------------------------------------------------------

def _validate_backend_sort_by_price_ascending(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for sort"


def _validate_frontend_sort_by_price_ascending(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    sort_type = final_state.get("searchSortType")
    if sort_type != "price":
        return 0.0, f"searchSortType='{sort_type}' expected 'price'"
    sort_order = final_state.get("searchSortOrder")
    if sort_order != "asc":
        return 0.0, f"searchSortOrder='{sort_order}' expected 'asc'"
    return 1.0, "Successfully sorted by price ascending"


_validate_sort_by_price_ascending: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_sort_by_price_ascending,
    "validate_frontend": _validate_frontend_sort_by_price_ascending,
}


# -----------------------------------------------------------------------------
# Task: sort-by-price-descending
# -----------------------------------------------------------------------------

def _validate_backend_sort_by_price_descending(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for sort"


def _validate_frontend_sort_by_price_descending(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    sort_type = final_state.get("searchSortType")
    if sort_type != "price":
        return 0.0, f"searchSortType='{sort_type}' expected 'price'"
    sort_order = final_state.get("searchSortOrder")
    if sort_order != "desc":
        return 0.0, f"searchSortOrder='{sort_order}' expected 'desc'"
    return 1.0, "Successfully sorted by price descending"


_validate_sort_by_price_descending: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_sort_by_price_descending,
    "validate_frontend": _validate_frontend_sort_by_price_descending,
}


# -----------------------------------------------------------------------------
# Task: sort-by-sales
# -----------------------------------------------------------------------------

def _validate_backend_sort_by_sales(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for sort"


def _validate_frontend_sort_by_sales(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    sort_type = final_state.get("searchSortType")
    if sort_type != "sales":
        return 0.0, f"searchSortType='{sort_type}' expected 'sales'"
    return 1.0, "Successfully sorted by sales"


_validate_sort_by_sales: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_sort_by_sales,
    "validate_frontend": _validate_frontend_sort_by_sales,
}


# =============================================================================
# CART TASKS (Backend validation)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: add-a-product-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_add_a_product_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    return 1.0, "Backend: Successfully added product to cart"


def _validate_frontend_add_a_product_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation skipped (cart data not in UI state)"


_validate_add_a_product_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_a_product_to_cart,
    "validate_frontend": _validate_frontend_add_a_product_to_cart,
}


# -----------------------------------------------------------------------------
# Task: add-a-product-from-search-result-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_add_a_product_from_search_result_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    return 1.0, "Backend: Successfully added product from search to cart"


def _validate_frontend_add_a_product_from_search_result_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product detail page"


_validate_add_a_product_from_search_result_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_a_product_from_search_result_to_cart,
    "validate_frontend": _validate_frontend_add_a_product_from_search_result_to_cart,
}


# -----------------------------------------------------------------------------
# Task: add-an-item-from-the-homepage
# -----------------------------------------------------------------------------

def _validate_backend_add_an_item_from_the_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-q7r8s9' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    return 1.0, "Backend: Successfully added item from homepage to cart"


def _validate_frontend_add_an_item_from_the_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on homepage"


_validate_add_an_item_from_the_homepage: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-q7r8s9"}},
    },
    "validate_backend": _validate_backend_add_an_item_from_the_homepage,
    "validate_frontend": _validate_frontend_add_an_item_from_the_homepage,
}


# -----------------------------------------------------------------------------
# Task: add-an-item-with-3-quantity
# -----------------------------------------------------------------------------

def _validate_backend_add_an_item_with_3_quantity(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 3:
        return 0.0, f"Cart item qty={item.get('qty')} expected 3"
    return 1.0, "Backend: Successfully added item with qty 3"


def _validate_frontend_add_an_item_with_3_quantity(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on product page"


_validate_add_an_item_with_3_quantity: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_an_item_with_3_quantity,
    "validate_frontend": _validate_frontend_add_an_item_with_3_quantity,
}


# -----------------------------------------------------------------------------
# Task: add-product-with-specific-variant-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_add_product_with_specific_variant_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    variants = item.get("selectedVariants", {})
    if variants.get("颜色") != "深蓝" or variants.get("尺码") != "XL":
        return 0.0, f"selectedVariants={variants} expected {{'颜色': '深蓝', '尺码': 'XL'}}"
    return 1.0, "Backend: Successfully added product with specific variant"


def _validate_frontend_add_product_with_specific_variant_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on product page"


_validate_add_product_with_specific_variant_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_product_with_specific_variant_to_cart,
    "validate_frontend": _validate_frontend_add_product_with_specific_variant_to_cart,
}


# -----------------------------------------------------------------------------
# Task: select-variant-and-add-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_select_variant_and_add_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) < 2:
        return 0.0, f"Cart should have 2 entries, found {len(cart) if isinstance(cart, list) else 0}"
    
    matching_items = [item for item in cart if item.get("productId") == "prod-m4n5o6"]
    if len(matching_items) != 2:
        return 0.0, f"Expected 2 cart entries for prod-m4n5o6, found {len(matching_items)}"
    
    variant1_found = False
    variant2_found = False
    
    for item in matching_items:
        variants = item.get("selectedVariants", {})
        qty = item.get("qty")
        
        if variants.get("颜色") == "经典黑色" and variants.get("尺码") == "S" and qty == 1:
            variant1_found = True
        elif variants.get("颜色") == "卡其色" and variants.get("尺码") == "XL" and qty == 2:
            variant2_found = True
    
    if not variant1_found:
        return 0.0, "Missing cart entry: qty 1 with variants {颜色: 经典黑色, 尺码: S}"
    if not variant2_found:
        return 0.0, "Missing cart entry: qty 2 with variants {颜色: 卡其色, 尺码: XL}"
    
    return 1.0, "Backend: Successfully added multiple variants to cart"


def _validate_frontend_select_variant_and_add_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on product page"


_validate_select_variant_and_add_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_select_variant_and_add_to_cart,
    "validate_frontend": _validate_frontend_select_variant_and_add_to_cart,
}


# -----------------------------------------------------------------------------
# Task: remove-one-item-from-cart
# -----------------------------------------------------------------------------

def _validate_backend_remove_one_item_from_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    # Cart can be null or empty list when all items are removed
    if cart is None:
        return 1.0, "Backend: Successfully removed item from cart (cart is null)"
    if not isinstance(cart, list):
        return 0.0, "Cart is not a list or null"
    if len(cart) != 0:
        return 0.0, f"Cart has {len(cart)} items, expected 0"
    return 1.0, "Backend: Successfully removed item from cart"


def _validate_frontend_remove_one_item_from_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation skipped (cart data not in UI state)"


_validate_remove_one_item_from_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {}},
    },
    "validate_backend": _validate_backend_remove_one_item_from_cart,
    "validate_frontend": _validate_frontend_remove_one_item_from_cart,
}


# -----------------------------------------------------------------------------
# Task: remove-multiple-items-in-the-cart
# -----------------------------------------------------------------------------

def _validate_backend_remove_multiple_items_in_the_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    # Cart can be null or empty list when all items are removed
    if cart is None:
        return 1.0, "Backend: Successfully removed all items from cart (cart is null)"
    if not isinstance(cart, list):
        return 0.0, "Cart is not a list or null"
    if len(cart) != 0:
        return 0.0, f"Cart has {len(cart)} items, expected 0"
    return 1.0, "Backend: Successfully removed all items from cart"


def _validate_frontend_remove_multiple_items_in_the_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_remove_multiple_items_in_the_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {}},
    },
    "validate_backend": _validate_backend_remove_multiple_items_in_the_cart,
    "validate_frontend": _validate_frontend_remove_multiple_items_in_the_cart,
}


# -----------------------------------------------------------------------------
# Task: reduce-an-item-quantity-in-the-cart
# -----------------------------------------------------------------------------

def _validate_backend_reduce_an_item_quantity_in_the_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 2:
        return 0.0, f"Cart item qty={item.get('qty')} expected 2"
    return 1.0, "Backend: Successfully reduced item quantity to 2"


def _validate_frontend_reduce_an_item_quantity_in_the_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation skipped (cart data not in UI state)"


_validate_reduce_an_item_quantity_in_the_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_reduce_an_item_quantity_in_the_cart,
    "validate_frontend": _validate_frontend_reduce_an_item_quantity_in_the_cart,
}


# -----------------------------------------------------------------------------
# Task: increase-an-item-and-reduce-another-item
# -----------------------------------------------------------------------------

def _validate_backend_increase_an_item_and_reduce_another_item(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    
    item1 = next((i for i in cart if i.get("productId") == "prod-m4n5o6"), None)
    if not item1:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    if item1.get("qty") != 4:
        return 0.0, f"Cart item prod-m4n5o6 qty={item1.get('qty')} expected 4"
    
    item2 = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item2:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    if item2.get("qty") != 1:
        return 0.0, f"Cart item prod-y7z8a9 qty={item2.get('qty')} expected 1"
    
    return 1.0, "Backend: Successfully increased one item and reduced another"


def _validate_frontend_increase_an_item_and_reduce_another_item(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_increase_an_item_and_reduce_another_item: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-m4n5o6", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_increase_an_item_and_reduce_another_item,
    "validate_frontend": _validate_frontend_increase_an_item_and_reduce_another_item,
}


# -----------------------------------------------------------------------------
# Task: search-and-add-two-items-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_search_and_add_two_items_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    if len(cart) < 2:
        return 0.0, f"Cart has {len(cart)} items, expected at least 2"
    
    item1 = next((i for i in cart if i.get("productId") == "prod-m4n5o6"), None)
    if not item1:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    if item1.get("qty") != 3:
        return 0.0, f"Cart item prod-m4n5o6 qty={item1.get('qty')} expected 3"
    
    item2 = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item2:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    if item2.get("qty") != 3:
        return 0.0, f"Cart item prod-y7z8a9 qty={item2.get('qty')} expected 3"
    
    return 1.0, "Backend: Successfully added two items with qty 3 each"


def _validate_frontend_search_and_add_two_items_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_search_and_add_two_items_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-m4n5o6", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_search_and_add_two_items_to_cart,
    "validate_frontend": _validate_frontend_search_and_add_two_items_to_cart,
}


# -----------------------------------------------------------------------------
# Task: search-and-add-item-to-cart-and-back-to-home
# -----------------------------------------------------------------------------

def _validate_backend_search_and_add_item_to_cart_and_back_to_home(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-q7r8s9' not found in backend"
    return 1.0, "Backend: Successfully added item to cart"


def _validate_frontend_search_and_add_item_to_cart_and_back_to_home(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "紫苏酱新")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on homepage with search query"


_validate_search_and_add_item_to_cart_and_back_to_home: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-q7r8s9"}},
    },
    "validate_backend": _validate_backend_search_and_add_item_to_cart_and_back_to_home,
    "validate_frontend": _validate_frontend_search_and_add_item_to_cart_and_back_to_home,
}


# -----------------------------------------------------------------------------
# Task: remove-item-from-cart-then-search-and-add-item
# -----------------------------------------------------------------------------

def _validate_backend_remove_item_from_cart_then_search_and_add_item(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    if len(cart) != 1:
        return 0.0, f"Cart has {len(cart)} items, expected 1"
    
    item = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    
    # Verify the old item is not in cart
    old_item = next((i for i in cart if i.get("productId") == "prod-m4n5o6"), None)
    if old_item:
        return 0.0, "Cart still contains prod-m4n5o6, expected it to be removed"
    
    return 1.0, "Backend: Successfully removed old item and added new item"


def _validate_frontend_remove_item_from_cart_then_search_and_add_item(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_remove_item_from_cart_then_search_and_add_item: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-m4n5o6", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_remove_item_from_cart_then_search_and_add_item,
    "validate_frontend": _validate_frontend_remove_item_from_cart_then_search_and_add_item,
}


# -----------------------------------------------------------------------------
# Task: use-homepage-to-navigate-and-add-items
# -----------------------------------------------------------------------------

def _validate_backend_use_homepage_to_navigate_and_add_items(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    if len(cart) < 2:
        return 0.0, f"Cart has {len(cart)} items, expected at least 2"
    
    item1 = next((i for i in cart if i.get("productId") == "prod-k1l2m3"), None)
    if not item1:
        return 0.0, "Cart item with productId 'prod-k1l2m3' not found in backend"
    
    item2 = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item2:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    
    return 1.0, "Backend: Successfully added two items from homepage"


def _validate_frontend_use_homepage_to_navigate_and_add_items(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_use_homepage_to_navigate_and_add_items: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-k1l2m3", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_use_homepage_to_navigate_and_add_items,
    "validate_frontend": _validate_frontend_use_homepage_to_navigate_and_add_items,
}


# =============================================================================
# New Agent Testing Tasks (Multi-Step Workflows)
# =============================================================================
# These tasks validate complex user journeys that span multiple actions.
# Unlike atomic tasks, they use a combined validation function that queries
# backend collections directly via the Backend interface.
# =============================================================================

# Backend collections to hydrate for agent tasks
BACKEND_COLLECTIONS_AGENT: List[str] = ["cart", "products", "stores", "productMeta"]


# =============================================================================
# Generated Tasks from jd-generated-tasks.json
# =============================================================================
# Total: 50 tasks (G1-G50)
#
# Tasks with non-default initial state (7 tasks):
#   Product page with variant: G42, G43, G45, G46, G47
#   Cart page with items:      G48, G50
#
# All other tasks (43): page='home', cart=[], searchQuery=''
# =============================================================================


# =============================================================================
# Helper Functions for Generated Tasks
# =============================================================================

def _get_cart(backend: Backend) -> List[Dict[str, Any]]:
    """Query cart directly from backend."""
    result = backend.query({"collection": "cart", "filter": {}})
    return result if isinstance(result, list) else []


def _get_product(backend: Backend, product_id: str) -> Optional[Dict[str, Any]]:
    """Query single product by ID from backend."""
    if not product_id:
        return None
    result = backend.query({"collection": "products", "filter": {"_id": product_id}})
    if isinstance(result, list) and len(result) > 0:
        return result[0]
    return None


def _get_product_meta(backend: Backend, product_id: str) -> Optional[Dict[str, Any]]:
    """Query productMeta by productId from backend.
    
    ProductMeta contains:
    - specs: product specifications (e.g., 调光方式, 材质, 功率)
    - reviewTags: user review tags (e.g., 护眼效果好, 亮度调节方便)
    - productReviews, productQA: reviews and Q&A
    """
    if not product_id:
        return None
    result = backend.query({"collection": "productMeta", "filter": {"productId": product_id}})
    if isinstance(result, list) and len(result) > 0:
        return result[0]
    return None


def _find_cart_product(
    backend: Backend,
    cart: List[Dict[str, Any]],
    terms: List[str],
) -> Optional[Dict[str, Any]]:
    """Find first cart product matching search terms (queries backend directly).
    
    Returns product if ANY term matches (OR logic).
    """
    terms_lower = [t.lower() for t in terms]
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if product:
            combined = f"{product.get('title', '')} {product.get('category', '')}".lower()
            if any(term in combined for term in terms_lower):
                return product
    return None


def _find_cart_product_all_terms(
    backend: Backend,
    cart: List[Dict[str, Any]],
    terms: List[str],
) -> Optional[Dict[str, Any]]:
    """Find first cart product matching ALL search terms (AND logic).
    
    Use this for compound matching like "芝麻" + "油" to match "芝麻香油"
    but NOT "花椒香油" (missing 芝麻) or "芝麻糊" (missing 油).
    """
    terms_lower = [t.lower() for t in terms]
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if product:
            combined = f"{product.get('title', '')} {product.get('category', '')}".lower()
            if all(term in combined for term in terms_lower):
                return product
    return None


def _count_cart_products(
    backend: Backend,
    cart: List[Dict[str, Any]],
    terms: List[str],
) -> int:
    """Count cart products matching search terms (queries backend directly)."""
    terms_lower = [t.lower() for t in terms]
    count = 0
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if product:
            combined = f"{product.get('title', '')} {product.get('category', '')}".lower()
            if any(term in combined for term in terms_lower):
                count += 1
    return count


def _find_cart_product_with_category(
    backend: Backend,
    cart: List[Dict[str, Any]],
    terms: List[str],
    allowed_categories: Optional[List[str]] = None,
    excluded_categories: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Find cart product matching terms AND category filter.
    
    Use this to filter out false positives by category:
    - allowed_categories: product must be in one of these categories
    - excluded_categories: product must NOT be in any of these categories
    
    Example: Find power bank but exclude car jump starters:
        _find_cart_product_with_category(backend, cart, ["充电宝"], excluded_categories=["汽车服务"])
    """
    terms_lower = [t.lower() for t in terms]
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
        
        category = product.get("category", "")
        
        # Category filtering
        if allowed_categories and category not in allowed_categories:
            continue
        if excluded_categories and category in excluded_categories:
            continue
        
        # Term matching (OR logic - any term matches)
        title = product.get("title", "").lower()
        if any(term in title for term in terms_lower):
            return product
    return None


def _check_product_price_range(
    product: Dict[str, Any],
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> Tuple[bool, str]:
    """Validate product price is within range."""
    price = product.get("currentPrice", 0)
    if min_price is not None and price < min_price:
        return False, f"price {price} below minimum {min_price}"
    if max_price is not None and price > max_price:
        return False, f"price {price} above maximum {max_price}"
    return True, ""

# -----------------------------------------------------------------------------
# Task G1: Kitchen Faucet Under 300 Yuan
# -----------------------------------------------------------------------------
def _validate_agent_kitchen_faucet_under_300(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 kitchen faucet priced <=300 yuan
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    faucet_terms = ["水龙头", "龙头", "厨房龙头"]
    product = _find_cart_product(backend, cart, faucet_terms)
    
    if not product:
        # Provide context about what's in the cart
        cart_info = []
        for item in cart:
            p = _get_product(backend, item.get("productId"))
            if p:
                cart_info.append(p.get("title", "unknown")[:40])
            else:
                cart_info.append(f"<productId={item.get('productId')} not found>")
        return 0.0, f"cart has {len(cart)} item(s) but none match faucet terms; cart contains: {cart_info}"
    
    ok, msg = _check_product_price_range(product, max_price=300)
    if not ok:
        return 0.0, f"faucet {msg}"

    return 1.0, "Kitchen faucet under 300 yuan added to cart"


# -----------------------------------------------------------------------------
# Task G2: Phone Charger Search with Filter
# -----------------------------------------------------------------------------
def _validate_agent_phone_charger_search(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Search results show phone chargers with price filter applied
    """
    errors: List[str] = []

    page = final_state_frontend.get("page")
    if page != "search":
        errors.append(f"page should be 'search', got '{page}'")
    search_query = final_state_frontend.get("searchQuery", "")
    charger_terms = ["充电器", "充电"]
    if not any(term in search_query.lower() for term in charger_terms):
        errors.append(f"searchQuery should contain charger terms, got '{search_query}'")
    price_filter = final_state_frontend.get("searchPriceFilter")
    if not price_filter:
        errors.append("price filter should be applied")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Phone charger search with price filter displayed"


# -----------------------------------------------------------------------------
# Task G3: Bulk Laundry Detergent
# -----------------------------------------------------------------------------
def _validate_agent_bulk_laundry_detergent(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 laundry detergent in bulk/large size
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    detergent_terms = ["洗衣液", "洗衣粉", "洗涤"]
    product = _find_cart_product(backend, cart, detergent_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 laundry detergent"

    return 1.0, "Bulk laundry detergent added to cart"


# -----------------------------------------------------------------------------
# Task G4: Drill Bit Set
# -----------------------------------------------------------------------------
def _validate_agent_drill_bit_set(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 drill bit set with multiple pieces/sizes
    
    Valid products include:
    - Products with "套装" (set) in title and piece count (e.g., "20件", "50件套")
    - Products with variants like "钻头套装", "钻头附件包" with multiple pieces
    - Example variants: "多功能综合钻头螺批套装 (50件套)", "高速钢钻头套装 (20件)"
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    drill_terms = ["钻头", "钻头套装", "钻", "电钻", "工具套装"]
    
    # Pattern to match piece counts like "20件", "50件套", "(10件套)"
    piece_count_pattern = re.compile(r'\d+件')
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
            
        title = product.get("title", "").lower()
        
        # Check if product matches drill terms
        if not any(term.lower() in title for term in drill_terms):
            continue
        
        # Check for multiple pieces indicator in title
        if piece_count_pattern.search(title) or "套装" in title:
            return 1.0, "Drill bit set with multiple pieces added to cart"
        
        # Check selected variants for piece count indicators
        selected_variants = cart_item.get("selectedVariants", {})
        for variant_key, variant_value in selected_variants.items():
            variant_str = str(variant_value)
            if piece_count_pattern.search(variant_str) or "套装" in variant_str:
                return 1.0, "Drill bit set with multiple pieces added to cart"
    
    return 0.0, "cart should contain a drill/tool set with multiple pieces (look for 套装 with piece count like 20件, 50件套)"


# -----------------------------------------------------------------------------
# Task G5: Portable Speaker Search
# -----------------------------------------------------------------------------
def _validate_agent_portable_speaker_search(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Search results for portable speakers with price filter 200-400 yuan
    """
    errors: List[str] = []

    page = final_state_frontend.get("page")
    if page != "search":
        errors.append(f"page should be 'search', got '{page}'")
    search_query = final_state_frontend.get("searchQuery", "")
    speaker_terms = ["音箱", "音响", "蓝牙音箱"]
    if not any(term in search_query.lower() for term in speaker_terms):
        errors.append(f"searchQuery should contain speaker terms, got '{search_query}'")
    
    # Check price filter is applied and strictly within 200-400 yuan range
    price_filter = final_state_frontend.get("searchPriceFilter")
    if not price_filter:
        errors.append("price filter should be applied for 200-400 yuan range")
    else:
        min_p = price_filter.get("min", 0)
        max_p = price_filter.get("max", 9999)
        # Filter must be strictly within 200-400: min >= 200 AND max <= 400
        if min_p < 200 or max_p > 400:
            errors.append(f"price filter [{min_p}-{max_p}] should be strictly within 200-400 yuan range")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Portable speaker search with price filter displayed"


# -----------------------------------------------------------------------------
# Task G6: Cat Scratching Post
# -----------------------------------------------------------------------------
def _validate_agent_cat_scratching_post(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 cat scratching post
    
    Only accepts actual pet supplies (萌宠护理 category).
    Excludes "防猫抓" sofa covers from 日用品 category.
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    scratch_terms = ["猫抓板", "猫抓", "抓板", "猫爬架"]
    # Only allow pet supplies, not furniture covers
    product = _find_cart_product_with_category(
        backend, cart, scratch_terms,
        allowed_categories=["萌宠护理"]
    )
    
    if not product:
        return 0.0, "cart should contain at least 1 cat scratching post (from 萌宠护理 category)"

    return 1.0, "Cat scratching post added to cart"


# -----------------------------------------------------------------------------
# Task G7: Car Phone Mount
# -----------------------------------------------------------------------------
def _validate_agent_car_phone_mount(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 car phone mount/holder
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    mount_terms = ["手机支架", "车载支架", "手机座", "车载"]
    product = _find_cart_product(backend, cart, mount_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 car phone mount"

    return 1.0, "Car phone mount added to cart"


# -----------------------------------------------------------------------------
# Task G8: Rice Cooker for 4-6 People
# -----------------------------------------------------------------------------
def _validate_agent_rice_cooker(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 rice cooker suitable for 4-6 people
    
    Capacity validation:
    - Title patterns like "4-6人", "4-5人", "5-6人", "6-8人" = PASS
    - Selected variant patterns like "5L (4-6人)", "4L (3-5人)" = PASS
    - Capacity >= 4L is generally suitable for 4+ people
    - Title with "2-3人" or "1-2人" without larger variant selected = FAIL
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    cooker_terms = ["电饭煲", "电饭锅", "饭煲", "电压力锅"]
    
    for cart_item in cart:
        product_id = cart_item.get("productId")
        product = _get_product(backend, product_id)
        if not product:
            continue
        
        title = product.get("title", "")
        if not any(term in title for term in cooker_terms):
            continue
        
        # Check title for people capacity patterns (e.g., "4-6人", "家用4-5人")
        # Valid: 4-5人, 4-6人, 5-6人, 6-8人, etc. (min >= 4)
        title_people_match = re.search(r"(\d+)-(\d+)\s*人", title)
        if title_people_match:
            min_people = int(title_people_match.group(1))
            max_people = int(title_people_match.group(2))
            if min_people >= 4 or max_people >= 5:
                return 1.0, f"Rice cooker ({min_people}-{max_people}人) added to cart"
        
        # Check selected variant for capacity
        selected_variants = cart_item.get("selectedVariants", {})
        for variant_label, variant_value in selected_variants.items():
            variant_str = str(variant_value)
            
            # Check for people pattern in variant (e.g., "5L (4-6人)")
            variant_people_match = re.search(r"(\d+)-(\d+)\s*人", variant_str)
            if variant_people_match:
                min_people = int(variant_people_match.group(1))
                max_people = int(variant_people_match.group(2))
                if min_people >= 4 or max_people >= 5:
                    return 1.0, f"Rice cooker variant ({min_people}-{max_people}人) added to cart"
            
            # Check for capacity in liters (4L+ is generally good for 4+ people)
            capacity_match = re.search(r"(\d+(?:\.\d+)?)\s*[lL升]", variant_str)
            if capacity_match:
                capacity = float(capacity_match.group(1))
                if capacity >= 4.0:
                    return 1.0, f"Rice cooker ({capacity}L) added to cart - suitable for 4+ people"
        
        # Rice cooker found but doesn't meet capacity requirements
        return 0.0, "rice cooker capacity should be suitable for 4-6 people (need >= 4L or 4-6人 in title/variant)"
    
    return 0.0, "cart should contain at least 1 rice cooker"


# -----------------------------------------------------------------------------
# Task G9: Premium Cooking Oil
# -----------------------------------------------------------------------------
def _validate_agent_premium_cooking_oil(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 premium cooking oil (peanut or sesame)
    
    Based on JD catalog:
    - 花生油: 鲁花花生油, 刀唛花生油, 胡姬花花生油
    - 芝麻油: 金龙鱼纯芝麻香油 (compound: 芝麻 + 油)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Check for peanut oil first (direct match)
    peanut_oil = _find_cart_product(backend, cart, ["花生油"])
    if peanut_oil:
        return 1.0, "Premium peanut oil added to cart"
    
    # Check for sesame oil using compound matching (芝麻 + 油)
    sesame_oil = _find_cart_product_all_terms(backend, cart, ["芝麻", "油"])
    if sesame_oil:
        return 1.0, "Premium sesame oil added to cart"

    return 0.0, "cart should contain at least 1 cooking oil (花生油 or 芝麻香油)"


# -----------------------------------------------------------------------------
# Task G10: Dog Food Bowl
# -----------------------------------------------------------------------------
def _validate_agent_dog_food_bowl(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 pet food bowl or feeder
    
    Based on JD catalog:
    - 喂食器: 霍曼智能自动喂食器, 小佩AI智能自动喂食器
    - 猫碗: 西屋智能无线宠物喂食器猫碗
    - 不锈钢碗: included in feeder products
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Broad pet bowl/feeder terms based on actual catalog
    bowl_terms = ["喂食器", "猫碗", "狗碗", "宠物碗", "食盆", "不锈钢碗"]
    product = _find_cart_product(backend, cart, bowl_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 pet food bowl or feeder"

    return 1.0, "Pet food bowl/feeder added to cart"


# -----------------------------------------------------------------------------
# Task G11: Adjustable Desk Lamp
# -----------------------------------------------------------------------------
def _validate_agent_desk_lamp(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 desk lamp with adjustable/dimmable features
    
    Checks multiple sources for adjustability:
    - Product title/description
    - Selected variants and available variants
    - ProductMeta specs (e.g., 调光方式: 触摸式无级调光)
    - ProductMeta reviewTags (e.g., 亮度调节方便)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    lamp_terms = ["台灯", "护眼灯", "书桌灯", "阅读灯", "学习灯"]
    # Adjustability terms found in actual JD desk lamp products
    adjustable_terms = [
        "调光", "调节", "可调", "调色",  # dimming/adjustable
        "触控", "感应", "智能",           # touch/sensor/smart control
        "无极", "多档", "三档", "四档",   # brightness levels
        "护眼", "全光谱",                 # eye-protection (these are adjustable)
        "AAAA", "AAA", "AA级"             # rated lamps have adjustable features
    ]
    
    lamp_found = False
    for cart_item in cart:
        product_id = cart_item.get("productId")
        product = _get_product(backend, product_id)
        if not product:
            continue
        
        title = product.get("title", "")
        category = product.get("category", "")
        combined = f"{title} {category}".lower()
        
        # Check if it's a desk lamp
        if not any(term.lower() in combined for term in lamp_terms):
            continue
        
        lamp_found = True
        
        # 1. Check title/description
        description = product.get("description", "")
        product_info = f"{title} {description}"
        
        if any(term in product_info for term in adjustable_terms):
            return 1.0, "Adjustable desk lamp added to cart"
        
        # 2. Check selected variants
        selected_variants = cart_item.get("selectedVariants", {})
        for variant_label, variant_value in selected_variants.items():
            variant_str = f"{variant_label} {variant_value}"
            if any(term in variant_str for term in adjustable_terms):
                return 1.0, "Adjustable desk lamp added to cart"
        
        # 3. Check available variants in product
        variants = product.get("variants", {})
        for variant_key, variant_options in variants.items():
            if isinstance(variant_options, list):
                for option in variant_options:
                    if isinstance(option, dict):
                        option_str = str(option.get("value", "") or option.get("label", ""))
                    else:
                        option_str = str(option)
                    if any(term in option_str for term in adjustable_terms):
                        return 1.0, "Adjustable desk lamp added to cart"
        
        # 4. Check productMeta specs and reviewTags
        meta = _get_product_meta(backend, product_id)
        if meta:
            # Check specs (e.g., 调光方式: 触摸式无级调光)
            for spec in meta.get("specs", []):
                spec_str = f"{spec.get('label', '')} {spec.get('value', '')}"
                if any(term in spec_str for term in adjustable_terms):
                    return 1.0, "Adjustable desk lamp added to cart"
            
            # Check reviewTags (e.g., 亮度调节方便)
            for tag in meta.get("reviewTags", []):
                tag_label = tag.get("label", "")
                if any(term in tag_label for term in adjustable_terms):
                    return 1.0, "Adjustable desk lamp added to cart"
    
    if lamp_found:
        return 0.0, "desk lamp found but missing adjustable feature (look for 调光/触控/护眼/智能)"
    return 0.0, "cart should contain at least 1 desk lamp"


# -----------------------------------------------------------------------------
# Task G12: Snack Variety Pack
# -----------------------------------------------------------------------------
def _validate_agent_snack_variety(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains snack variety pack OR multiple different snack items
    
    STRICT: Must be EITHER:
    1. A variety pack (礼盒, 大礼包, 组合, 混合, 综合, 多口味, 什锦)
    2. OR multiple different snack products (>=2)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    snack_terms = ["零食", "坚果", "饼干", "薯片", "糖果", "巧克力", "果干", "蜜饯", "肉干"]
    variety_terms = ["组合", "混合", "礼盒", "大礼包", "综合", "多口味", "什锦"]
    
    snack_count = 0
    has_variety_pack = False
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
        
        title = product.get("title", "")
        
        # Check if it's a snack
        if any(term in title for term in snack_terms):
            snack_count += 1
            
            # Check if it's a variety pack
            if any(term in title for term in variety_terms):
                has_variety_pack = True
    
    # Pass if: variety pack OR multiple snacks
    if has_variety_pack:
        return 1.0, "Snack variety pack added to cart"
    
    if snack_count >= 2:
        return 1.0, f"Multiple snack items ({snack_count}) added to cart"
    
    if snack_count == 1:
        return 0.0, "need a variety pack (礼盒/组合/混合) OR multiple different snacks (>=2)"
    
    return 0.0, "cart should contain snack variety pack or multiple snack items"


# -----------------------------------------------------------------------------
# Task G13: MagSafe Wireless Charger Silver
# -----------------------------------------------------------------------------
def _validate_agent_magsafe_charger_silver(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains MUJI MagSafe wireless charger (prod-a1b2c3d) with silver color
    
    Product: 无印良品（MUJI）铝合金磁吸 桌面无线充电手机支架 角度可调节MagSafe磁吸无线充 适用于苹果
    Product ID: prod-a1b2c3d
    Required variant: 颜色 = 银色
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"
    
    target_product_id = "prod-a1b2c3d"
    
    # Find the target product in cart
    cart_item = None
    product = None
    for item in cart:
        if item.get("productId") == target_product_id:
            cart_item = item
            product = _get_product(backend, target_product_id)
            break
    
    if not cart_item or not product:
        # Also check by title keywords as fallback
        charger_terms = ["无线充电", "MagSafe", "磁吸充电"]
        for item in cart:
            prod = _get_product(backend, item.get("productId"))
            if prod:
                title = prod.get("title", "").lower()
                if any(term.lower() in title for term in charger_terms):
                    cart_item = item
                    product = prod
                    break
    
    if not cart_item or not product:
        return 0.0, "cart should contain MUJI MagSafe wireless charger (prod-a1b2c3d)"
    
    # Check for silver color variant
    selected_variants = cart_item.get("selectedVariants", {})
    color_variant = selected_variants.get("颜色", "")
    
    if "银" not in color_variant and "silver" not in color_variant.lower():
        if color_variant:
            return 0.0, f"charger should have silver (银色) color selected, got '{color_variant}'"
        return 0.0, "charger should have silver (银色) color variant selected"

    return 1.0, "MUJI MagSafe wireless charger with silver color added to cart"


# -----------------------------------------------------------------------------
# Task G14: Vitamins and Supplements
# -----------------------------------------------------------------------------
def _validate_agent_vitamins(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 multivitamin or vitamin D supplement
    
    Only accepts human vitamins (健康保养 category).
    Excludes pet vitamins (萌宠护理 category).
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    vitamin_terms = ["维生素", "多维", "钙片", "保健品", "营养素"]
    # Only allow human vitamins from health category
    product = _find_cart_product_with_category(
        backend, cart, vitamin_terms,
        allowed_categories=["健康保养"]
    )
    
    if not product:
        return 0.0, "cart should contain at least 1 human vitamin supplement (from 健康保养 category)"

    return 1.0, "Vitamin supplement added to cart"


# -----------------------------------------------------------------------------
# Task G15: Mouse Search
# -----------------------------------------------------------------------------
def _validate_agent_mouse_search(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', searchResultIds=[]
    Verification: Search results show wireless/ergonomic mice products
    
    Checks:
    1. Page is 'search'
    2. searchQuery contains mouse terms (鼠标, 无线鼠标, 蓝牙鼠标)
    3. searchResultIds contains mouse products
    """
    errors: List[str] = []

    # Check page is search
    page = final_state_frontend.get("page")
    if page != "search":
        errors.append(f"page should be 'search', got '{page}'")
    
    # Check search query contains mouse terms
    search_query = final_state_frontend.get("searchQuery", "")
    mouse_terms = ["鼠标", "无线鼠标", "蓝牙鼠标"]
    if not any(term in search_query.lower() for term in mouse_terms):
        errors.append(f"searchQuery should contain mouse terms, got '{search_query}'")
    
    # Check searchResultIds contains mouse products
    search_result_ids = final_state_frontend.get("searchResultIds", [])
    if not search_result_ids:
        errors.append("searchResultIds is empty - no search results displayed")
    else:
        # Find mouse products in search results
        mouse_products = []
        for product_id in search_result_ids:
            product = _get_product(backend, product_id)
            if product:
                title = product.get("title", "").lower()
                if any(term in title for term in mouse_terms):
                    mouse_products.append(product)
        
        if not mouse_products:
            errors.append(f"searchResultIds ({len(search_result_ids)} products) should contain mouse products")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, f"Mouse search results displayed ({len(search_result_ids)} products)"


# -----------------------------------------------------------------------------
# Task G16: Gardening Tools
# -----------------------------------------------------------------------------
def _validate_agent_gardening_tools(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains gardening tool set or multiple tools
    
    Must be actual TOOLS, not supplies like soil, pots, or seeds.
    Valid tools: 园艺工具套装, 铲子, 锄头, 耙子, 剪刀, 修枝剪, 喷壶, 浇水壶
    Invalid: 营养土, 花盆, 种菜盆, 种植箱, 种子
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Specific tool terms - must be actual tools, not supplies
    tool_terms = [
        "园艺工具",  # gardening tool set
        "铲子",      # shovel
        "锄头",      # hoe
        "耙子",      # rake
        "修枝剪",    # pruning shears
        "园艺剪",    # gardening scissors
        "果枝剪",    # fruit branch scissors
        "浇水壶",    # watering can
        "喷壶",      # spray bottle
    ]
    
    # Terms that indicate supplies, not tools (exclusions)
    supply_terms = ["营养土", "花土", "种菜土", "花盆", "种植箱", "种子", "肥"]
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
        
        title = product.get("title", "")
        
        # Must match a tool term
        if not any(term in title for term in tool_terms):
            continue
        
        # Must NOT be a supply
        if any(term in title for term in supply_terms):
            continue
        
        return 1.0, "Gardening tools added to cart"
    
    return 0.0, "cart should contain at least 1 gardening tool (not soil/pots/seeds)"


# -----------------------------------------------------------------------------
# Task G17: Electric Kettle
# -----------------------------------------------------------------------------
def _validate_agent_coffee_maker(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 electric kettle
    
    Note: Adapted from coffee maker since no coffee makers exist in catalog.
    Available products: 美的电热水壶 (prod-a7b8c9), 苏泊尔电水壶 (100118502877)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    kettle_terms = ["电水壶", "电热水壶", "烧水壶", "热水壶", "开水壶"]
    product = _find_cart_product(backend, cart, kettle_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 electric kettle"

    return 1.0, "Electric kettle added to cart"


# -----------------------------------------------------------------------------
# Task G18: Power Bank
# -----------------------------------------------------------------------------
def _validate_agent_power_bank(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 power bank with >=10000mAh capacity
    
    Checks multiple sources:
    - Product title
    - Selected variants
    - ProductMeta specs (e.g., 电池容量: 10000mAh)
    
    Excludes: Car jump starters (汽车服务 category)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    powerbank_terms = ["充电宝", "移动电源"]
    excluded_categories = ["汽车服务"]
    
    for cart_item in cart:
        product_id = cart_item.get("productId")
        product = _get_product(backend, product_id)
        if not product:
            continue
        
        title = product.get("title", "")
        category = product.get("category", "")
        
        # Skip car jump starters
        if category in excluded_categories:
            continue
        
        if not any(term in title for term in powerbank_terms):
            continue
        
        # 1. Check capacity in title
        title_match = re.search(r"(\d+)\s*mah", title, re.IGNORECASE)
        if title_match and int(title_match.group(1)) >= 10000:
            return 1.0, f"Power bank ({title_match.group(1)}mAh) added to cart"
        
        # 2. Check capacity in selected variants
        selected_variants = cart_item.get("selectedVariants", {})
        for variant_label, variant_value in selected_variants.items():
            variant_str = str(variant_value)
            variant_match = re.search(r"(\d+)\s*mah", variant_str, re.IGNORECASE)
            if variant_match and int(variant_match.group(1)) >= 10000:
                return 1.0, f"Power bank ({variant_match.group(1)}mAh) added to cart"
        
        # 3. Check capacity in productMeta specs
        meta = _get_product_meta(backend, product_id)
        if meta:
            for spec in meta.get("specs", []):
                spec_str = f"{spec.get('label', '')} {spec.get('value', '')}"
                spec_match = re.search(r"(\d+)\s*mah", spec_str, re.IGNORECASE)
                if spec_match and int(spec_match.group(1)) >= 10000:
                    return 1.0, f"Power bank ({spec_match.group(1)}mAh) added to cart"
        
        # Power bank found but capacity too low or not found
        return 0.0, "power bank capacity should be >= 10000mAh"
    
    return 0.0, "cart should contain at least 1 power bank"


# -----------------------------------------------------------------------------
# Task G19: Plumbing Tool Set
# -----------------------------------------------------------------------------
def _validate_agent_plumbing_tools(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 plumbing/repair tool set (must be a set, not individual tools)
    
    Checks multiple sources:
    - Product title/description
    - Selected variants
    - ProductMeta specs (e.g., 包装清单: 47件工具)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Terms that indicate a tool SET (not individual tools)
    toolset_terms = ["工具套装", "工具箱", "套装", "件套"]
    
    tool_found = False
    for cart_item in cart:
        product_id = cart_item.get("productId")
        product = _get_product(backend, product_id)
        if not product:
            continue
        
        title = product.get("title", "")
        description = product.get("description", "")
        product_info = f"{title} {description}"
        
        # 1. Check title/description
        if any(term in product_info for term in toolset_terms):
            return 1.0, "Plumbing tool set added to cart"
        
        # 2. Check selected variants for set indicators
        selected_variants = cart_item.get("selectedVariants", {})
        for variant_label, variant_value in selected_variants.items():
            variant_str = f"{variant_label} {variant_value}"
            if any(term in variant_str for term in toolset_terms):
                return 1.0, "Plumbing tool set added to cart"
        
        # 3. Check productMeta specs
        meta = _get_product_meta(backend, product_id)
        if meta:
            for spec in meta.get("specs", []):
                spec_str = f"{spec.get('label', '')} {spec.get('value', '')}"
                if any(term in spec_str for term in toolset_terms):
                    return 1.0, "Plumbing tool set added to cart"
        
        # Track if we found any tool-related product
        if any(term in title for term in ["工具", "扳手", "螺丝刀", "钳子", "维修"]):
            tool_found = True
    
    if tool_found:
        return 0.0, "found tool but should be a SET (套装/工具箱), not individual tools"
    return 0.0, "cart should contain at least 1 tool set (套装)"


# -----------------------------------------------------------------------------
# Task G20: Condiments
# -----------------------------------------------------------------------------
def _validate_agent_condiments(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=2 different condiments
    
    Based on JD catalog:
    - 酱油: 海天生抽酱油, 老抽王酱油, 千禾御藏本酿, 厨邦金品生抽
    - 芝麻油: 金龙鱼纯芝麻香油 (use compound: 芝麻 + 油)
    - 花生油: 鲁花花生油, 刀唛花生油
    - 醋: 恒顺醇酿香醋, 水塔老陈醋
    - 料酒: 厨邦葱姜汁料酒
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Check for different condiment categories
    soy_found = _find_cart_product(backend, cart, ["酱油", "生抽", "老抽"])
    # Use compound matching for sesame oil: must contain BOTH "芝麻" AND "油"
    # This matches "芝麻香油" but NOT "花椒香油" or "芝麻糊"
    sesame_oil_found = _find_cart_product_all_terms(backend, cart, ["芝麻", "油"])
    peanut_oil_found = _find_cart_product(backend, cart, ["花生油"])
    vinegar_found = _find_cart_product(backend, cart, ["醋"])
    sauce_found = _find_cart_product(backend, cart, ["辣酱", "辣椒酱", "料酒", "腌料"])

    # Count distinct types (sesame oil and peanut oil are different types)
    types_found = sum(1 for x in [soy_found, sesame_oil_found, peanut_oil_found, vinegar_found, sauce_found] if x)
    if types_found < 2:
        return 0.0, "cart should contain at least 2 different types of condiments"
    return 1.0, f"Added {types_found} different types of condiments to cart"


# -----------------------------------------------------------------------------
# Task G21: Instant Noodles
# -----------------------------------------------------------------------------
def _validate_agent_instant_noodles(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains instant noodle variety pack or multiple products
    
    Only accepts food products (食品饮料, 粮油调味 categories).
    Excludes cooking pots/utensils that mention "泡面" in their description.
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    noodle_terms = ["方便面", "泡面", "拉面", "面条"]
    # Only allow actual food products, not cooking utensils
    product = _find_cart_product_with_category(
        backend, cart, noodle_terms,
        allowed_categories=["食品饮料", "粮油调味"]
    )
    
    if not product:
        return 0.0, "cart should contain at least 1 instant noodle product (food category)"

    return 1.0, "Instant noodles added to cart"


# -----------------------------------------------------------------------------
# Task G22: Wireless Charger
# -----------------------------------------------------------------------------
def _validate_agent_wireless_charger(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 fast wireless charger
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    charger_terms = ["无线充电", "无线充"]
    product = _find_cart_product(backend, cart, charger_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 wireless charger"

    return 1.0, "Wireless charger added to cart"


# -----------------------------------------------------------------------------
# Task G23: Hand Cream
# -----------------------------------------------------------------------------
def _validate_agent_hand_cream(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 hand cream
    
    Based on JD catalog:
    - 凡士林护手霜, 美加净护手霜, 祖玛珑护手霜, 半亩花田护手霜
    - Note: "保湿" alone is too broad, matches face creams, body lotions
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Specific hand cream terms (not generic moisturizer terms)
    cream_terms = ["护手霜", "手霜"]
    product = _find_cart_product(backend, cart, cream_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 hand cream (护手霜)"

    return 1.0, "Hand cream added to cart"


# -----------------------------------------------------------------------------
# Task G24: Dog Leash
# -----------------------------------------------------------------------------
def _validate_agent_dog_leash(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 dog leash that is retractable or heavy-duty
    
    Checks multiple sources:
    - Product title/description
    - Selected variants
    - ProductMeta specs and reviewTags
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    leash_terms = ["狗绳", "牵引绳", "遛狗绳", "牵引带", "狗链"]
    
    # Quality indicators
    quality_terms = ["自动", "可伸缩", "伸缩", "加粗", "加厚", "重型", "耐用", "加固"]
    
    leash_found = False
    for cart_item in cart:
        product_id = cart_item.get("productId")
        product = _get_product(backend, product_id)
        if not product:
            continue
        
        title = product.get("title", "")
        if not any(term in title for term in leash_terms):
            continue
        
        leash_found = True
        
        # 1. Check title/description
        description = product.get("description", "")
        product_info = f"{title} {description}"
        
        if any(term in product_info for term in quality_terms):
            return 1.0, "Retractable/heavy-duty dog leash added to cart"
        
        # 2. Check selected variants
        selected_variants = cart_item.get("selectedVariants", {})
        for variant_label, variant_value in selected_variants.items():
            variant_str = f"{variant_label} {variant_value}"
            if any(term in variant_str for term in quality_terms):
                return 1.0, "Retractable/heavy-duty dog leash added to cart"
        
        # 3. Check productMeta specs and reviewTags
        meta = _get_product_meta(backend, product_id)
        if meta:
            for spec in meta.get("specs", []):
                spec_str = f"{spec.get('label', '')} {spec.get('value', '')}"
                if any(term in spec_str for term in quality_terms):
                    return 1.0, "Retractable/heavy-duty dog leash added to cart"
            
            for tag in meta.get("reviewTags", []):
                tag_label = tag.get("label", "")
                if any(term in tag_label for term in quality_terms):
                    return 1.0, "Retractable/heavy-duty dog leash added to cart"
    
    if leash_found:
        return 0.0, "dog leash found but should be retractable (自动/可伸缩) or heavy-duty (加粗/耐用)"
    return 0.0, "cart should contain at least 1 dog leash"


# -----------------------------------------------------------------------------
# Task G25: Kitchen Appliance Gift Under 300
# -----------------------------------------------------------------------------
def _validate_agent_kitchen_appliance_gift(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 kitchen appliance priced <=300 yuan
    
    STRICT: Must be actual kitchen appliance (cooking/food prep), not general 小家电
    like hair dryers, shavers, heaters, vacuums, etc.
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Kitchen appliance terms - cooking/food preparation only
    kitchen_terms = [
        # Cooking appliances
        "电饭煲", "电饭锅",           # rice cookers
        "空气炸锅", "电炸锅",         # air fryers
        "电压力锅",                   # pressure cookers
        "电火锅", "电煮锅",           # electric hot pots
        "电饼铛", "烙饼",             # electric pancake pans
        "烤肉锅", "电烤盘", "电烧烤",  # electric grills
        "微波炉", "烤箱",             # microwave/ovens
        # Water/beverage appliances
        "电水壶", "电热水壶", "烧水壶", "热水壶",  # electric kettles
        "养生壶", "煮茶壶", "煮茶器",  # health pots / tea makers
        "电热水瓶",                   # thermos pots
        "饮水机",                     # water dispensers
        "茶吧机",                     # tea bar machines
        # Food prep appliances
        "豆浆机", "破壁机",           # soy milk/blenders
        "榨汁机", "榨汁杯", "果汁机",  # juicers
        "料理机", "搅拌机",           # food processors
        "绞肉机", "碎肉机",           # meat grinders
        # Other kitchen
        "暖菜板",                     # food warmers
        "滤水壶", "净水壶",           # water filter pitchers
    ]
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
        
        title = product.get("title", "")
        
        # Must match kitchen appliance term in title
        if any(term in title for term in kitchen_terms):
            ok, _ = _check_product_price_range(product, max_price=300)
            if ok:
                return 1.0, "Kitchen appliance gift under 300 yuan added to cart"
    
    return 0.0, "cart should contain at least 1 kitchen appliance under 300 yuan"


# -----------------------------------------------------------------------------
# Task G26: Wireless Mouse
# -----------------------------------------------------------------------------
def _validate_agent_wireless_mouse(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 wireless mouse
    
    Must be an actual mouse, not a keyboard-mouse converter/adapter.
    Valid: 无线鼠标, 蓝牙鼠标, 游戏鼠标, 办公鼠标, MX Master
    Invalid: 键盘鼠标转换器, 键鼠套装 (converter accessories)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Specific mouse terms - actual mice products
    mouse_terms = ["无线鼠标", "蓝牙鼠标", "游戏鼠标", "办公鼠标", "静音鼠标", "MX Master"]
    
    # Terms that indicate converters/adapters, not actual mice
    excluded_terms = ["转换器", "转接器", "键鼠套装", "键盘鼠标转换"]
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
        
        title = product.get("title", "")
        
        # Must match a mouse term
        if not any(term in title for term in mouse_terms):
            continue
        
        # Must NOT be a converter/adapter
        if any(term in title for term in excluded_terms):
            continue
        
        return 1.0, "Wireless mouse added to cart"
    
    return 0.0, "cart should contain at least 1 wireless mouse (not converter/adapter)"


# -----------------------------------------------------------------------------
# Task G27: Wall Outlet
# -----------------------------------------------------------------------------
def _validate_agent_wall_outlet(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 wall outlet/switch panel
    
    Note: Original task was for power strips, but JD catalog only has
    wall-mounted outlets (86型墙壁插座). Task updated to wall outlet.
    Valid products: 公牛五孔插座, 施耐德电气插座, 正泰开关插座
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Wall sockets/outlets - products from 公牛, 施耐德, 正泰
    outlet_terms = ["五孔插座", "开关插座", "墙壁插座", "插座面板", "86型"]
    product = _find_cart_product(backend, cart, outlet_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 wall outlet/switch panel"

    return 1.0, "Wall outlet/switch panel added to cart"


# =============================================================================
# Category Browsing Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task G28: Kitchen Knife Set
# -----------------------------------------------------------------------------
def _validate_agent_kitchen_knife_set(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 kitchen knife set; browsed kitchen tools category
    
    Based on JD catalog:
    - 张小泉 刀具套装七件套, 菜刀, 切菜刀
    - Note: "刀具" alone matches screwdriver kits, need kitchen-specific terms
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Kitchen knife specific terms (避免匹配螺丝刀套装)
    knife_terms = ["菜刀", "切菜刀", "斩骨刀", "水果刀", "厨刀", "张小泉"]
    product = _find_cart_product(backend, cart, knife_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 kitchen knife"

    return 1.0, "Kitchen knife added to cart"


# -----------------------------------------------------------------------------
# Task G29: Small Kitchen Appliances Promo
# -----------------------------------------------------------------------------
def _validate_agent_small_appliances_promo(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', homeFeedCategory='为你推荐'
    Verification: User has browsed to small appliances section (selected 小家电 category)
    
    Valid homeFeedCategory: "小家电"
    """
    errors: List[str] = []

    promotional_page = final_state_frontend.get("promotionalPage")
    home_feed_category = final_state_frontend.get("homeFeedCategory", "")
    
    # User must have actively selected small appliances category or viewed promotions
    # Just being on home page or search page is NOT enough
    is_valid_view = (
        home_feed_category == "小家电" or
        promotional_page is not None
    )
    
    if not is_valid_view:
        errors.append(f"should have selected '小家电' category or viewed promotions, got homeFeedCategory='{home_feed_category}'")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Small appliances category selected and displayed"


# -----------------------------------------------------------------------------
# Task G30: Office Supplies
# -----------------------------------------------------------------------------
def _validate_agent_office_supplies(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=2 different office supply items
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    office_terms = ["笔", "本子", "文件夹", "办公", "文具"]
    count = _count_cart_products(backend, cart, office_terms)
    
    if count < 2:
        return 0.0, f"cart should contain at least 2 office supply items, got {count}"

    return 1.0, f"Added {count} office supply items to cart"


# -----------------------------------------------------------------------------
# Task G31: Skincare Set Browse
# -----------------------------------------------------------------------------
def _validate_agent_skincare_set_browse(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 skincare product with good reviews (>=1000), 200-500 yuan range
    
    Matching product: 欧莱雅紫熨斗精华液 (289 yuan, 100,000 reviews)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    skincare_terms = ["护肤", "精华", "面霜", "化妆品", "美妆", "个护"]
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if product:
            combined = f"{product.get('title', '')} {product.get('category', '')}".lower()
            if any(term.lower() in combined for term in skincare_terms):
                # Check price range: 200-500 yuan
                price_ok, price_msg = _check_product_price_range(product, min_price=200, max_price=500)
                if not price_ok:
                    continue
                # Check well-reviewed: reviews count >= 1000
                reviews = product.get("reviews", {})
                review_count = reviews.get("count", 0)
                if review_count < 1000:
                    continue
                return 1.0, "Well-reviewed skincare product (200-500 yuan) added to cart"
    
    return 0.0, "cart should contain at least 1 skincare product in 200-500 yuan range with good reviews"


# -----------------------------------------------------------------------------
# Task G32: Homepage Electronics Promo
# -----------------------------------------------------------------------------
def _validate_agent_electronics_promo(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', homeFeedCategory='为你推荐'
    Verification: User has browsed to electronics section (selected 电脑数码 category)
    
    Valid homeFeedCategory for electronics: "电脑数码"
    """
    errors: List[str] = []

    promotional_page = final_state_frontend.get("promotionalPage")
    home_feed_category = final_state_frontend.get("homeFeedCategory", "")
    
    # User must have actively selected electronics category or viewed promotions
    # Just being on home page is NOT enough (that's the initial state)
    is_valid_view = (
        home_feed_category == "电脑数码" or
        promotional_page is not None
    )
    
    if not is_valid_view:
        errors.append(f"should have selected '电脑数码' category or viewed promotions, got homeFeedCategory='{home_feed_category}'")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Electronics category selected and displayed"


# -----------------------------------------------------------------------------
# Task G33: Bathroom Materials Browse
# -----------------------------------------------------------------------------
def _validate_agent_bathroom_materials(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', homeFeedCategory='为你推荐'
    Verification: User has browsed to building materials/bathroom section
    
    Valid homeFeedCategory: "家具建材"
    Or search query contains bathroom-related terms
    """
    errors: List[str] = []

    page = final_state_frontend.get("page")
    search_query = final_state_frontend.get("searchQuery", "")
    home_feed_category = final_state_frontend.get("homeFeedCategory", "")
    
    bathroom_terms = ["卫浴", "浴室", "洗手间"]
    
    # User must have actively selected building materials category or searched for bathroom items
    is_valid_view = (
        home_feed_category == "家具建材" or
        (page == "search" and any(term in search_query.lower() for term in bathroom_terms))
    )
    
    if not is_valid_view:
        errors.append(f"should have selected '家具建材' category or searched for bathroom items, got homeFeedCategory='{home_feed_category}', searchQuery='{search_query}'")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Building materials/bathroom category displayed"


# -----------------------------------------------------------------------------
# Task G34: Casual Jacket Under 400
# -----------------------------------------------------------------------------
def _validate_agent_casual_jacket(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 casual jacket priced <=400 yuan
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    jacket_terms = ["夹克", "外套", "休闲外套", "上衣"]
    
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if product:
            combined = f"{product.get('title', '')} {product.get('category', '')}".lower()
            if any(term.lower() in combined for term in jacket_terms):
                ok, _ = _check_product_price_range(product, max_price=400)
                if ok:
                    return 1.0, "Casual jacket under 400 yuan added to cart"
    
    return 0.0, "cart should contain at least 1 jacket under 400 yuan"


# -----------------------------------------------------------------------------
# Task G35: Baby Supplies
# -----------------------------------------------------------------------------
def _validate_agent_baby_supplies(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=2 baby items from mother/baby category
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    baby_terms = ["婴儿", "宝宝", "奶瓶", "尿不湿", "母婴"]
    count = _count_cart_products(backend, cart, baby_terms)
    
    if count < 2:
        return 0.0, f"cart should contain at least 2 baby items, got {count}"

    return 1.0, f"Added {count} baby items to cart"


# -----------------------------------------------------------------------------
# Task G36: Educational Toy
# -----------------------------------------------------------------------------
def _validate_agent_educational_toy(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 educational toy suitable for children
    
    Based on JD catalog 教育文娱 category:
    - 儿童画板 (children's drawing board)
    - 粘土/彩泥 (clay)
    - 画画套装 (drawing sets)
    - 立体书/触摸书 (3D/touch books for kids)
    - 益智玩具 (educational toys)
    - 积木/拼图 (building blocks/puzzles)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Educational toy terms - expanded to cover JD catalog
    toy_terms = [
        "玩具",      # toy
        "益智",      # educational/puzzle
        "积木",      # building blocks
        "拼图",      # puzzle
        "画板",      # drawing board
        "彩泥",      # colored clay
        "粘土",      # clay/play-doh
        "画画套装",  # drawing set
        "立体书",    # 3D book
        "触摸书",    # touch book
        "绘本",      # picture book
        "早教",      # early education
    ]
    
    # Also accept products from 教育文娱 category with 儿童 keyword
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if not product:
            continue
        
        title = product.get("title", "")
        category = product.get("category", "")
        
        # Direct match on toy terms
        if any(term in title for term in toy_terms):
            return 1.0, "Educational toy added to cart"
        
        # Products in 教育文娱 category with 儿童 are educational toys
        if category == "教育文娱" and "儿童" in title:
            return 1.0, "Educational toy added to cart"
    
    return 0.0, "cart should contain at least 1 educational toy"


# -----------------------------------------------------------------------------
# Task G37: Site-wide Promotions
# -----------------------------------------------------------------------------
def _validate_agent_site_promotions(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', homeFeedCategory='为你推荐'
    Verification: User has browsed to promotions/flash sales section
    
    Valid homeFeedCategory: "摸鱼顺手秒"
    """
    errors: List[str] = []

    promotional_page = final_state_frontend.get("promotionalPage")
    home_feed_category = final_state_frontend.get("homeFeedCategory", "")
    
    # User must have actively navigated to promotions section
    is_valid_view = (
        home_feed_category == "摸鱼顺手秒" or
        promotional_page is not None
    )
    
    if not is_valid_view:
        errors.append(f"should have selected '摸鱼顺手秒' category or viewed promotions, got homeFeedCategory='{home_feed_category}'")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Site-wide promotions displayed"


# -----------------------------------------------------------------------------
# Task G38: Trending/Recommended Items
# -----------------------------------------------------------------------------
def _validate_agent_trending_items(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', homeFeedCategory='为你推荐'
    Verification: User is viewing the recommended/trending products section
    
    Note: Initial state starts with homeFeedCategory='为你推荐', so this verifies
    the user is on home page with recommendations visible (not navigated away)
    """
    errors: List[str] = []

    page = final_state_frontend.get("page")
    home_feed_category = final_state_frontend.get("homeFeedCategory", "")
    
    # User should be on home page with recommended section
    is_valid_view = (
        page == "home" and
        home_feed_category == "为你推荐"
    )
    
    if not is_valid_view:
        errors.append(f"should be on home page with '为你推荐' category, got page='{page}', homeFeedCategory='{home_feed_category}'")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Trending/recommended items displayed"


# -----------------------------------------------------------------------------
# Task G39: Sports Equipment
# -----------------------------------------------------------------------------
def _validate_agent_workout_clothes(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=2 sports/fitness items
    
    Note: Adapted from workout clothes since no sports shirts/shorts exist in catalog.
    Available products: 迪卡侬瑜伽垫 (prod-t4u5v6), Keep智能跳绳 (prod-w7x8y9)
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    # Check for sports/fitness items (yoga mat, jump rope, etc.)
    sports_terms = ["运动", "健身", "瑜伽", "跳绳"]
    sports_count = _count_cart_products(backend, cart, sports_terms)
    
    if sports_count < 2:
        return 0.0, "cart should contain at least 2 sports/fitness items"

    return 1.0, f"Sports equipment added to cart ({sports_count} items)"


# -----------------------------------------------------------------------------
# Task G40: Flash Sales Browse
# -----------------------------------------------------------------------------
def _validate_agent_flash_sales(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery='', homeFeedCategory='为你推荐'
    Verification: User has browsed to flash sales/limited-time deals section
    
    Valid homeFeedCategory: "摸鱼顺手秒"
    """
    errors: List[str] = []

    promotional_page = final_state_frontend.get("promotionalPage")
    home_feed_category = final_state_frontend.get("homeFeedCategory", "")
    
    # User must have actively selected flash sales category
    is_valid_view = (
        home_feed_category == "摸鱼顺手秒" or
        promotional_page is not None
    )
    
    if not is_valid_view:
        errors.append(f"should have selected '摸鱼顺手秒' category or viewed promotions, got homeFeedCategory='{home_feed_category}'")

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Flash sales section displayed"


# -----------------------------------------------------------------------------
# Task G41: Cleaning Supplies Browse
# -----------------------------------------------------------------------------
def _validate_agent_cleaning_supplies(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains >=1 all-purpose cleaner or cleaning supply
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    cleaning_terms = ["清洁剂", "洗洁精", "消毒液"]
    product = _find_cart_product(backend, cart, cleaning_terms)
    
    if not product:
        return 0.0, "cart should contain at least 1 cleaning supply"

    return 1.0, "Cleaning supplies added to cart"


# =============================================================================
# Product Evaluation Tasks (with Variants)
# =============================================================================

# -----------------------------------------------------------------------------
# Task G42: Change Headphones Color to Silver
# -----------------------------------------------------------------------------
def _validate_change_headphones_color_to_silver(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='product', selectedProductId='prod-g7h8i9', selectedVariants={'颜色': '黑色'}
    Verification: Cart contains Sony WH-1000XM5 headphones with silver (银色) color selected
    
    Product: 索尼 WH-1000XM5 (prod-g7h8i9)
    Available variants: 黑色 (available), 银色 (available), 白色 (NOT available)
    Task: Change from default black to silver, then add to cart
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    sony_headphone_terms = ["索尼", "sony", "wh-1000xm5", "降噪耳机"]
    product = _find_cart_product(backend, cart, sony_headphone_terms)
    
    if not product:
        return 0.0, "cart should contain Sony noise-canceling headphones"
    
    # Check if silver variant is selected
    for cart_item in cart:
        if cart_item.get("productId") == product.get("_id"):
            selected_variants = cart_item.get("selectedVariants", {})
            color_variant = selected_variants.get("颜色", "")
            if "银" not in color_variant and "silver" not in color_variant.lower():
                if color_variant:
                    return 0.0, f"headphones should have silver (银色) color selected, got '{color_variant}'"
                return 0.0, "headphones should have silver (银色) color selected"
            break

    return 1.0, "Sony headphones with silver variant added to cart"


# -----------------------------------------------------------------------------
# Task G43: Sports Shoes Under 500 Yuan
# -----------------------------------------------------------------------------
def _validate_agent_sports_shoes(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains sports/running shoes priced <= 500 yuan
    
    Matching product: 李宁运动鞋 (prod-p7q8r9) at 459 yuan
    Note: Cheapest sports shoe is 459 yuan, so 500 yuan limit allows it
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    shoe_terms = ["运动鞋", "跑步鞋", "跑鞋"]
    product = _find_cart_product(backend, cart, shoe_terms)
    
    if not product:
        return 0.0, "cart should contain sports/running shoes"
    
    ok, msg = _check_product_price_range(product, max_price=500)
    if not ok:
        return 0.0, f"shoes {msg}"

    return 1.0, "Sports shoes under 500 yuan added to cart"


# -----------------------------------------------------------------------------
# Task G44: Change Drying Rack Length
# -----------------------------------------------------------------------------
def _validate_change_drying_rack_length(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='product', selectedProductId='100222552661', selectedVariants={'晾杆长度': '1.5米'}
    Verification: Cart contains 好太太电动晾衣架 with 2.0米 length variant
    
    Product: 好太太电动晾衣架 Q32Pro (100222552661)
    Available 晾杆长度 variants: 1.5米, 1.8米, 2.0米, 2.4米 (2.2米 NOT available)
    Task: Change from 1.5米 to 2.0米, then add to cart
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    rack_terms = ["晾衣架", "晾衣", "好太太"]
    product = _find_cart_product(backend, cart, rack_terms)
    
    if not product:
        return 0.0, "cart should contain smart clothes drying rack"
    
    for cart_item in cart:
        if cart_item.get("productId") == product.get("_id"):
            selected_variants = cart_item.get("selectedVariants", {})
            length_variant = selected_variants.get("晾杆长度", "")
            if "2.0" not in length_variant and "2米" not in length_variant:
                if length_variant:
                    return 0.0, f"rack should have 2.0米 length selected, got '{length_variant}'"
                return 0.0, "rack should have 2.0米 length selected"
            break

    return 1.0, "Smart clothes rack with 2.0m variant added to cart"


# -----------------------------------------------------------------------------
# Task G45: Change Gift Card Amount
# -----------------------------------------------------------------------------
def _validate_change_gift_card_amount(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='product', selectedProductId='prod-g9h1i2j3', selectedVariants={'面值': '1000元'}
    Verification: Cart contains JD gift card with 500元 face value variant selected
    
    Product: 京东E卡 (prod-g9h1i2j3)
    Available 面值 variants: 5000元, 1000元, 500元
    Task: Change from 1000元 to 500元, then add to cart
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    gift_terms = ["礼品卡", "购物卡", "京东卡", "京东E卡", "E卡"]
    product = _find_cart_product(backend, cart, gift_terms)
    
    if not product:
        return 0.0, "cart should contain a JD gift card"
    
    for cart_item in cart:
        if cart_item.get("productId") == product.get("_id"):
            selected_variants = cart_item.get("selectedVariants", {})
            face_value = selected_variants.get("面值", "")
            if "500" not in face_value:
                if face_value:
                    return 0.0, f"gift card should have 500元 face value selected, got '{face_value}'"
                return 0.0, "gift card should have 500元 face value variant selected"
            break

    return 1.0, "JD gift card with 500 yuan face value added to cart"


# -----------------------------------------------------------------------------
# Task G46: Change Drill Power and Color
# -----------------------------------------------------------------------------
def _validate_change_drill_power_and_color(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='product', selectedProductId='100002159649', 
                   selectedVariants={'功率/型号': '600W 增强版', '颜色': '黑色'}
    Verification: Cart contains 德力西电钻 with 710W专业版 and 蓝色 selected
    
    Product: 德力西电气冲击钻 (100002159649)
    Available 功率/型号 variants: 600W 增强版, 710W 专业版 (500W标准版 NOT available)
    Available 颜色 variants: 蓝色, 黑色, 红色 (绿色, 灰色 NOT available)
    Task: Change from 600W增强版+黑色 to 710W专业版+蓝色, then add to cart
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty"

    drill_terms = ["电钻", "冲击钻", "德力西"]
    product = _find_cart_product(backend, cart, drill_terms)
    
    if not product:
        return 0.0, "cart should contain power drill"
    
    errors: List[str] = []
    for cart_item in cart:
        if cart_item.get("productId") == product.get("_id"):
            selected_variants = cart_item.get("selectedVariants", {})
            
            # Check power variant
            power_variant = selected_variants.get("功率/型号", "")
            if "710W" not in power_variant and "专业版" not in power_variant:
                if power_variant:
                    errors.append(f"drill should have 710W专业版 selected, got '{power_variant}'")
                else:
                    errors.append("drill should have 710W专业版 selected")
            
            # Check color variant
            color_variant = selected_variants.get("颜色", "")
            if "蓝" not in color_variant and "blue" not in color_variant.lower():
                if color_variant:
                    errors.append(f"drill should have 蓝色 (blue) selected, got '{color_variant}'")
                else:
                    errors.append("drill should have 蓝色 (blue) selected")
            break

    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, "Power drill with 710W Pro variant and blue color added to cart"


# =============================================================================
# Cart Management Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task G47: Clear Shopping Cart
# -----------------------------------------------------------------------------
def _validate_clear_shopping_cart(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='cart', cart=[3 items pre-populated], searchQuery=''
    Verification: Cart is empty (all items removed)
    
    Note: Since we can't compare to initial state, we verify cart is completely empty.
    Initial state must have items pre-populated for this task to be meaningful.
    """
    cart = _get_cart(backend)

    if len(cart) > 0:
        return 0.0, f"cart should be empty after cleanup, got {len(cart)} items remaining"

    return 1.0, "Cart cleared successfully"


# -----------------------------------------------------------------------------
# Task G48: Cart Total Check
# -----------------------------------------------------------------------------
def _validate_agent_cart_total_check(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[items], searchQuery=''
    Verification: Current screen is cart with total price visible
    
    Note: Cart total shown includes promotional discounts. The reward function
    calculates subtotal (before discounts) for informational purposes.
    """
    page = final_state_frontend.get("page")
    if page != "cart":
        return 0.0, f"page should be 'cart', got '{page}'"

    # Calculate cart subtotal (before promotions) for informational purposes
    # Frontend applies promotional discounts, so actual displayed total will be lower
    cart = _get_cart(backend)
    subtotal = 0.0
    for cart_item in cart:
        product = _get_product(backend, cart_item.get("productId"))
        if product:
            price = product.get("currentPrice", 0)
            qty = cart_item.get("qty", 1)  # Fixed: use "qty" not "quantity"
            subtotal += price * qty

    return 1.0, f"Cart displayed (subtotal before promotions: {subtotal:.2f} yuan)"


# -----------------------------------------------------------------------------
# Task G49: Remove Items Keeping Only One
# -----------------------------------------------------------------------------
def _validate_remove_items_keeping_only_one(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='cart', cart=[4 items pre-populated], searchQuery=''
    Verification: Cart has exactly 1 item remaining (kept the essential, removed the rest)
    
    Note: Since we can't compare to initial state, we verify cart has exactly 1 item.
    Initial state must have multiple items (4) pre-populated for this task to be meaningful.
    """
    cart = _get_cart(backend)

    if len(cart) != 1:
        return 0.0, f"cart should have exactly 1 essential item, got {len(cart)} items"

    return 1.0, "Cart cleaned up to 1 essential item"


# -----------------------------------------------------------------------------
# Task: find-usb-c-cable-under-100
# -----------------------------------------------------------------------------
def _validate_find_usb_c_cable_under_100(
    backend: Backend, final_state_frontend: Dict[str, Any]
) -> Tuple[float, str]:
    """
    Initial State: page='home', cart=[], searchQuery=''
    Verification: Cart contains USB-C cable (绿联Type-C数据线) under 100 yuan
    
    Product: 绿联Type-C数据线6A (6468018) at ¥20.9
    Task: Search for USB-C cable, find durable one under 100 yuan, add to cart
    """
    cart = _get_cart(backend)
    if not cart:
        return 0.0, "cart is empty, expected USB-C cable"
    
    # Check for the specific USB-C cable product (绿联Type-C数据线)
    usbc_terms = ["USB-C", "Type-C", "数据线", "充电线", "绿联"]
    product = _find_cart_product(backend, cart, usbc_terms)
    
    if not product:
        return 0.0, "cart should contain USB-C cable"
    
    # Verify price is under 100 yuan
    ok, msg = _check_product_price_range(product, max_price=100)
    if not ok:
        return 0.0, f"USB-C cable {msg}"
    
    # Verify search query contains USB-C/Type-C related terms
    search_query = final_state_frontend.get("searchQuery", "")
    if not any(term in search_query for term in usbc_terms):
        return 0.0, f"searchQuery='{search_query}' expected to contain USB-C/Type-C terms"
    
    return 1.0, "USB-C cable under 100 yuan added to cart"


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================

REWARD_FUNCTIONS_JD_V2: Dict[
    str, Union[ValidateTask, Callable[[Backend, Dict[str, Any]], Tuple[float, str]]]
] = {
    # Navigation Tasks
    "_validate_go_to_the_cart_page_from_the_homepage": _validate_go_to_the_cart_page_from_the_homepage,
    "_validate_go_to_a_product_page_from_home": _validate_go_to_a_product_page_from_home,
    "_validate_go_to_homepage_from_product_page": _validate_go_to_homepage_from_product_page,
    "_validate_go_to_cart_page_from_product_detail_page": _validate_go_to_cart_page_from_product_detail_page,
    "_validate_go_to_product_detail_from_search": _validate_go_to_product_detail_from_search,
    "_validate_navigate_from_cart_back_to_homepage": _validate_navigate_from_cart_back_to_homepage,
    "_validate_navigate_from_search_to_homepage": _validate_navigate_from_search_to_homepage,
    "_validate_navigate_to_cart_from_product_page_via_header": _validate_navigate_to_cart_from_product_page_via_header,
    "_validate_navigate_to_cart_from_search_page": _validate_navigate_to_cart_from_search_page,
    "_validate_navigate_from_product_to_another_product": _validate_navigate_from_product_to_another_product,
    "_validate_navigate_to_product_from_homepage_section": _validate_navigate_to_product_from_homepage_section,
    "_validate_navigate_via_category_sidebar_appliances": _validate_navigate_via_category_sidebar_appliances,
    "_validate_navigate_via_category_sidebar_electronics": _validate_navigate_via_category_sidebar_electronics,
    "_validate_multistep_navigation_home_to_product_to_cart": _validate_multistep_navigation_home_to_product_to_cart,
    "_validate_navigate_to_store_page": _validate_navigate_to_store_page,
    "_validate_filter_homepage_feed_by_category": _validate_filter_homepage_feed_by_category,
    # Search Tasks
    "_validate_search_jeep_shirt": _validate_search_jeep_shirt,
    "_validate_find_a_product_using_search_from_homepage": _validate_find_a_product_using_search_from_homepage,
    "_validate_search_a_product_from_another_product_page": _validate_search_a_product_from_another_product_page,
    "_validate_search_using_multiterm_query": _validate_search_using_multiterm_query,
    "_validate_search_from_search_history": _validate_search_from_search_history,
    "_validate_search_then_use_history_to_research": _validate_search_then_use_history_to_research,
    "_validate_search_using_suggestion_dropdown": _validate_search_using_suggestion_dropdown,
    "_validate_search_for_apple_iphone": _validate_search_for_apple_iphone,
    "_validate_search_for_huafeng_instant_noodles": _validate_search_for_huafeng_instant_noodles,
    "_validate_search_for_aux_massage_chair": _validate_search_for_aux_massage_chair,
    "_validate_search_for_asd_wok": _validate_search_for_asd_wok,
    "_validate_search_for_huoli_28_laundry_detergent": _validate_search_for_huoli_28_laundry_detergent,
    "_validate_search_for_stores": _validate_search_for_stores,
    "_validate_search_clear_history": _validate_search_clear_history,
    "_validate_search_using_placeholder": _validate_search_using_placeholder,
    "_validate_search_using_arrow_keys": _validate_search_using_arrow_keys,
    "_validate_search_from_hot_search_link": _validate_search_from_hot_search_link,
    "_validate_search_refine_query_from_results_page": _validate_search_refine_query_from_results_page,
    "_validate_search_and_navigate_to_product_detail": _validate_search_and_navigate_to_product_detail,
    # Filter & Sort Tasks
    "_validate_apply_price_range_filter": _validate_apply_price_range_filter,
    "_validate_apply_brand_filter_single_brand": _validate_apply_brand_filter_single_brand,
    "_validate_apply_brand_filter_multiple_brands": _validate_apply_brand_filter_multiple_brands,
    "_validate_apply_multiple_filters_price_and_brand": _validate_apply_multiple_filters_price_and_brand,
    "_validate_clear_price_filter": _validate_clear_price_filter,
    "_validate_clear_brand_filter": _validate_clear_brand_filter,
    "_validate_filter_and_navigate_to_product": _validate_filter_and_navigate_to_product,
    "_validate_sort_by_price_ascending": _validate_sort_by_price_ascending,
    "_validate_sort_by_price_descending": _validate_sort_by_price_descending,
    "_validate_sort_by_sales": _validate_sort_by_sales,
    # Cart Tasks
    "_validate_add_a_product_to_cart": _validate_add_a_product_to_cart,
    "_validate_add_a_product_from_search_result_to_cart": _validate_add_a_product_from_search_result_to_cart,
    "_validate_add_an_item_from_the_homepage": _validate_add_an_item_from_the_homepage,
    "_validate_add_an_item_with_3_quantity": _validate_add_an_item_with_3_quantity,
    "_validate_add_product_with_specific_variant_to_cart": _validate_add_product_with_specific_variant_to_cart,
    "_validate_select_variant_and_add_to_cart": _validate_select_variant_and_add_to_cart,
    "_validate_remove_one_item_from_cart": _validate_remove_one_item_from_cart,
    "_validate_remove_multiple_items_in_the_cart": _validate_remove_multiple_items_in_the_cart,
    "_validate_reduce_an_item_quantity_in_the_cart": _validate_reduce_an_item_quantity_in_the_cart,
    "_validate_increase_an_item_and_reduce_another_item": _validate_increase_an_item_and_reduce_another_item,
    "_validate_search_and_add_two_items_to_cart": _validate_search_and_add_two_items_to_cart,
    "_validate_search_and_add_item_to_cart_and_back_to_home": _validate_search_and_add_item_to_cart_and_back_to_home,
    "_validate_remove_item_from_cart_then_search_and_add_item": _validate_remove_item_from_cart_then_search_and_add_item,
    "_validate_use_homepage_to_navigate_and_add_items": _validate_use_homepage_to_navigate_and_add_items,
    # Generated Tasks - Search/Discovery
    "_validate_agent_kitchen_faucet_under_300": _validate_agent_kitchen_faucet_under_300,
    "_validate_agent_phone_charger_search": _validate_agent_phone_charger_search,
    "_validate_agent_bulk_laundry_detergent": _validate_agent_bulk_laundry_detergent,
    "_validate_agent_drill_bit_set": _validate_agent_drill_bit_set,
    "_validate_agent_portable_speaker_search": _validate_agent_portable_speaker_search,
    "_validate_agent_cat_scratching_post": _validate_agent_cat_scratching_post,
    "_validate_agent_car_phone_mount": _validate_agent_car_phone_mount,
    "_validate_agent_rice_cooker": _validate_agent_rice_cooker,
    "_validate_agent_premium_cooking_oil": _validate_agent_premium_cooking_oil,
    "_validate_agent_dog_food_bowl": _validate_agent_dog_food_bowl,
    "_validate_agent_desk_lamp": _validate_agent_desk_lamp,
    "_validate_agent_snack_variety": _validate_agent_snack_variety,
    "_validate_agent_magsafe_charger_silver": _validate_agent_magsafe_charger_silver,
    "_validate_agent_vitamins": _validate_agent_vitamins,
    "_validate_agent_mouse_search": _validate_agent_mouse_search,
    "_validate_agent_gardening_tools": _validate_agent_gardening_tools,
    "_validate_agent_coffee_maker": _validate_agent_coffee_maker,
    "_validate_agent_power_bank": _validate_agent_power_bank,
    "_validate_agent_plumbing_tools": _validate_agent_plumbing_tools,
    "_validate_agent_condiments": _validate_agent_condiments,
    "_validate_agent_instant_noodles": _validate_agent_instant_noodles,
    "_validate_agent_wireless_charger": _validate_agent_wireless_charger,
    "_validate_agent_hand_cream": _validate_agent_hand_cream,
    "_validate_agent_dog_leash": _validate_agent_dog_leash,
    "_validate_agent_kitchen_appliance_gift": _validate_agent_kitchen_appliance_gift,
    "_validate_agent_wireless_mouse": _validate_agent_wireless_mouse,
    "_validate_agent_wall_outlet": _validate_agent_wall_outlet,
    # Generated Tasks - Category Browsing
    "_validate_agent_kitchen_knife_set": _validate_agent_kitchen_knife_set,
    "_validate_agent_small_appliances_promo": _validate_agent_small_appliances_promo,
    "_validate_agent_office_supplies": _validate_agent_office_supplies,
    "_validate_agent_skincare_set_browse": _validate_agent_skincare_set_browse,
    "_validate_agent_electronics_promo": _validate_agent_electronics_promo,
    "_validate_agent_bathroom_materials": _validate_agent_bathroom_materials,
    "_validate_agent_casual_jacket": _validate_agent_casual_jacket,
    "_validate_agent_baby_supplies": _validate_agent_baby_supplies,
    "_validate_agent_educational_toy": _validate_agent_educational_toy,
    "_validate_agent_site_promotions": _validate_agent_site_promotions,
    "_validate_agent_trending_items": _validate_agent_trending_items,
    "_validate_agent_workout_clothes": _validate_agent_workout_clothes,
    "_validate_agent_flash_sales": _validate_agent_flash_sales,
    "_validate_agent_cleaning_supplies": _validate_agent_cleaning_supplies,
    # Generated Tasks - Product Evaluation
    "_validate_change_headphones_color_to_silver": _validate_change_headphones_color_to_silver,
    "_validate_agent_sports_shoes": _validate_agent_sports_shoes,
    "_validate_change_drying_rack_length": _validate_change_drying_rack_length,
    "_validate_change_gift_card_amount": _validate_change_gift_card_amount,
    "_validate_change_drill_power_and_color": _validate_change_drill_power_and_color,
    # Generated Tasks - Cart Management
    "_validate_clear_shopping_cart": _validate_clear_shopping_cart,
    "_validate_agent_cart_total_check": _validate_agent_cart_total_check,
    "_validate_remove_items_keeping_only_one": _validate_remove_items_keeping_only_one,
    "_validate_find_usb_c_cable_under_100": _validate_find_usb_c_cable_under_100,
}


__all__ = [
    "REWARD_FUNCTIONS_JD_V2",
    "ValidateTask",
    "StateKey",
    "StateKeyQuery",
]
