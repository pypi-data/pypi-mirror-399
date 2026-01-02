from .sanitize_html import (
    default_cleaner,
    markdown_to_raw_html,
    clean_raw_html,
)
from bs4 import BeautifulSoup
import re

import logging

log = logging.getLogger(__name__)


def make_cleaner_from_shop(shop):
    """Given a Shop return a bleach Cleaner object."""
    cleaner = default_cleaner()
    cleaner.link_protection = True
    # Store shop reference for link color styling
    cleaner.shop = shop
    if shop.domain_name:
        apex_domain_name = shop.domain_name.split(".")[-2:]
        cleaner.whitelist_domains.append("makepostsell.com")
        cleaner.whitelist_domains.append("my.makepostsell.com")
        cleaner.whitelist_domains.append(shop.domain_name)
        cleaner.whitelist_domains.append(apex_domain_name)
        cleaner.absolute_domain = shop.domain_name
    return cleaner


def add_shop_theme_classes(html, shop):
    """Add shop-theme-link-color class to all links in HTML if shop has theme color."""
    if not shop or not shop.theme_link_color:
        return html

    # Validate that the color looks like a valid CSS color
    color_pattern = r"^(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\)|[a-zA-Z]+)$"
    if not re.match(color_pattern, shop.theme_link_color.strip()):
        return html

    soup = BeautifulSoup(html, "html.parser")

    for a_tag in soup.find_all("a"):
        # Add CSS class for shop-themed links
        existing_classes = a_tag.attrs.get("class", [])
        if isinstance(existing_classes, str):
            existing_classes = existing_classes.split()

        # Only add if not already present
        if "shop-theme-link-color" not in existing_classes:
            existing_classes.append("shop-theme-link-color")
            a_tag.attrs["class"] = existing_classes

    return str(soup)


def markdown_to_html(data, shop=None):
    raw_html = markdown_to_raw_html(data)
    if shop:
        cleaner = make_cleaner_from_shop(shop)
    else:
        cleaner = default_cleaner()

    cleaned_html = clean_raw_html(raw_html, cleaner)

    # Add shop theme classes after sanitization
    if shop:
        cleaned_html = add_shop_theme_classes(cleaned_html, shop)

    return cleaned_html
