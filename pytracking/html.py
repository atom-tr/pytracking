from lxml import html

from pytracking.tracking import (
    get_configuration, get_open_tracking_url, get_click_tracking_url)

from typing import Dict, Optional
from pytracking.tracking import Configuration


DEFAULT_ATTRIBUTES = {
    "border": "0",
    "width": "0",
    "height": "0",
    "alt": ""
}

DOCTYPE = "<!DOCTYPE html>"


def adapt_html(html_text: str, extra_metadata: dict, click_tracking: bool = True, open_tracking: bool = True, configuration: Configuration = None, **kwargs) -> str:
    """
    Modify HTML by adding tracking links and a tracking pixel.

    Args:
        html_text (str): The HTML content to modify.
        extra_metadata (dict): Additional data to include in tracking links.
        click_tracking (bool): If True, replace links with tracking links.
        open_tracking (bool): If True, add a tracking pixel.
        configuration (Configuration): Custom configuration settings.
        **kwargs: Additional configuration parameters.

    Returns:
        str: Modified HTML content with tracking elements.

    This function processes the input HTML to add tracking capabilities:
    
    * Replaces regular links with click-tracking links if click_tracking is True.
    * Adds a 1x1 transparent pixel for open tracking if open_tracking is True.
    * Uses the provided configuration or creates a new one from kwargs.
    """
    configuration = get_configuration(configuration, kwargs)
    tree = html.fromstring(html_text)
    
    if click_tracking:
        _replace_links(tree, extra_metadata, configuration)
    
    if open_tracking:
        _add_tracking_pixel(tree, extra_metadata, configuration)
    
    return html.tostring(tree, include_meta_content_type=True, doctype=DOCTYPE).decode("utf-8")


def _replace_links(tree: html.Element, extra_metadata: Dict, configuration: Configuration):
    """
    Replace all links in the HTML tree with tracking links.

    :param tree: The HTML tree to modify
    :param extra_metadata: Additional metadata for the tracking URL
    :param configuration: Configuration object containing settings
    """
    for (element, attribute, link, pos) in tree.iterlinks():
        if element.tag == "a" and attribute == "href" and _valid_link(link, configuration):
            new_link = get_click_tracking_url(
                link, extra_metadata, configuration)
            element.attrib["href"] = new_link


def _add_tracking_pixel(tree: html.Element, extra_metadata: Dict, configuration: Configuration):
    """
    Add a tracking pixel to the HTML tree.

    :param tree: The HTML tree to modify
    :param extra_metadata: Additional metadata for the tracking URL
    :param configuration: Configuration object containing settings
    """
    url = get_open_tracking_url(extra_metadata, configuration)
    pixel = html.Element("img", {"src": url})
    
    if hasattr(tree, 'body'):
        if configuration.pixel_position == 'top':
            tree.body.insert(0, pixel)
        else:
            tree.body.append(pixel)
    else:
        tree.insert(0, pixel)

_valid_scheme = ["http://", "https://", "//"]

def _valid_link(link: str, configuration: Configuration = None) -> bool:
    """
    Check if a link is valid for click tracking.
    """
    is_valid = any(link.startswith(scheme) for scheme in _valid_scheme)
    if configuration and configuration.base_click_tracking_url:
        is_valid = is_valid and not link.startswith(configuration.base_click_tracking_url)
    return is_valid
