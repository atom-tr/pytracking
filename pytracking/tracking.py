import base64
from collections import namedtuple
from copy import deepcopy
from typing import Dict
import json
import time
from urllib.parse import urljoin

try:
    # Optional Import
    from cryptography.fernet import Fernet
except ImportError:
    pass


TRACKING_PIXEL = base64.b64decode(
    b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')  # noqa

PNG_MIME_TYPE = "image/png"

DEFAULT_TIMEOUT_SECONDS = 5


class Configuration(object):

    def __init__(
            self, webhook_url: str = None,
            webhook_timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
            include_webhook_url: bool = False, base_open_tracking_url: str = None,
            base_click_tracking_url: str = None, default_metadata: Dict = None,
            include_default_metadata: bool = False, encryption_bytestring_key: str = None,
            encoding: str = "utf-8", append_slash: bool = False, pixel_position: str = 'top', **kwargs):
        """

        :param webhook_url: The webhook to notify when a click or open is
            registered.
        :param webhook_timeout_seconds: Raises a timeout if the webhook does
            not response before the value. Default to None
        :param include_webhook_url: If True, the webhook URL is included in the
            encoded link. Default to False.
        :param base_open_tracking_url: The base URL to prepend to the encoded
            open tracking link.
        :param base_click_tracking_url: The base URL to prepend to the encoded
            click tracking link.
        :param default_metadata: Default metadata to associated with all
            tracking events.
        :param include_default_metadata: If True, the default metadata is
            included in the encoded link. Default to False.
        :param encryption_bytestring_key: The encryption key given by Fernet.
        :param encoding: The encoding to use to encode and decode the tracking
            link. Default to utf-8.
        :param pixel_position: The position of the tracking pixel in the HTML.
            Can be 'top' or 'bottom'. Default is 'top'.
        :param kwargs: Other args
        """
        self.webhook_url = webhook_url
        self.webhook_timeout_seconds = webhook_timeout_seconds
        self.include_webhook_url = include_webhook_url
        self.base_open_tracking_url = base_open_tracking_url
        self.base_click_tracking_url = base_click_tracking_url
        self.default_metadata = default_metadata
        self.include_default_metadata = include_default_metadata
        self.encryption_bytestring_key = encryption_bytestring_key
        self.encoding = encoding
        self.kwargs = kwargs
        self.encryption_key = None
        self.append_slash = append_slash
        self.pixel_position = pixel_position

        self.cache_encryption_key()

    def __str__(self):
        return "<pytracking.Configuration> "\
            "Open Tracking URL: {0} "\
            "Click Tracking URL: {1} "\
            "Webhook URL: {2}".format(
                self.base_open_tracking_url, self.base_click_tracking_url,
                self.webhook_url)

    def __deepcopy__(self, memo):
        new_config = Configuration()
        for key, value in self.__dict__.items():
            if key != "encryption_key":
                new_config.__dict__[key] = deepcopy(value)

        return new_config

    def merge_with_kwargs(self, kwargs):
        """
        Merge the current configuration with provided parameters.

        This method creates a copy of the current configuration and updates it with values
        from kwargs for existing attributes. It then updates the encryption key if necessary.

        :param kwargs: A dictionary containing configuration parameters to update.
        :return: A new Configuration object with the updated values.
        """
        new_configuration = deepcopy(self)
        for key, value in kwargs.items():
            if hasattr(new_configuration, key):
                setattr(new_configuration, key, value)

        # In case a new encryption key was provided
        new_configuration.cache_encryption_key()

        return new_configuration

    def cache_encryption_key(self):
        """
        Cache the encryption key.

        This method creates a Fernet object from the encryption bytestring key if provided.
        Otherwise, it sets the encryption key to None.

        The encryption key is used to encrypt and decrypt data in tracking URLs.
        """
        if self.encryption_bytestring_key:
            self.encryption_key = Fernet(self.encryption_bytestring_key)
        else:
            self.encryption_key = None

    def get_data_to_embed(self, url_to_track, extra_metadata):
        """
        Prepare data to be embedded in the tracking URL.

        This method constructs a dictionary containing the URL to track (if provided),
        metadata (including default and extra metadata), and webhook URL (if configured).

        :param url_to_track: The URL to be tracked (optional).
        :type url_to_track: str or None
        :param extra_metadata: Additional metadata to be included.
        :type extra_metadata: dict or None
        :return: A dictionary containing the data to be embedded in the tracking URL.
        :rtype: dict
        """
        data = {}
        if url_to_track:
            data["url"] = url_to_track
        metadata = {}

        if self.include_default_metadata and self.default_metadata:
            metadata.update(self.default_metadata)
        if extra_metadata:
            metadata.update(extra_metadata)

        if metadata:
            data["metadata"] = metadata

        if self.include_webhook_url and self.webhook_url:
            data["webhook"] = self.webhook_url

        return data

    def get_url_encoded_data_str(self, data_to_embed: Dict):
        """
        Encode and optionally encrypt the data to be embedded in the tracking URL.

        This method takes the data to be embedded, converts it to a JSON string,
        and then either encrypts it (if an encryption key is available) or
        encodes it using URL-safe Base64 encoding.

        :param data_to_embed: The data to be encoded and embedded in the URL.
        :type data_to_embed: dict
        :return: The encoded (and possibly encrypted) data string.
        :rtype: str
        """
        json_byte_str = json.dumps(data_to_embed).encode(self.encoding)

        if self.encryption_key:
            data_str = self.encryption_key.encrypt(
                json_byte_str).decode(self.encoding)
        else:
            data_str = base64.urlsafe_b64encode(
                json_byte_str).decode(self.encoding)

        return data_str

    def get_open_tracking_url_from_data_str(self, data_str: str):
        """
        Construct the full open tracking URL from the encoded data string.

        This method constructs the full URL for open tracking by appending the encoded data string
        to the base open tracking URL. It also appends a slash if configured.

        :param data_str: The encoded data string to be appended to the base URL.
        :type data_str: str
        """
        temp_url = urljoin(self.base_open_tracking_url, data_str)
        if self.append_slash:
            temp_url += "/"
        return temp_url

    def get_click_tracking_url_from_data_str(self, data_str: str):
        """
        Construct the full click tracking URL from the encoded data string.

        This method constructs the full URL for click tracking by appending the encoded data string
        to the base click tracking URL. It also appends a slash if configured.

        :param data_str: The encoded data string to be appended to the base URL.
        :type data_str: str
        """
        temp_url = urljoin(self.base_click_tracking_url, data_str)
        if self.append_slash:
            temp_url += "/"
        return temp_url

    def get_open_tracking_url(self, extra_metadata: Dict):
        """
        Generate the full open tracking URL.

        This method constructs the full URL for open tracking by embedding the provided metadata
        and other configuration settings into the URL.

        :param extra_metadata: Additional metadata to be included in the URL.
        :type extra_metadata: dict or None
        :return: The full open tracking URL.
        :rtype: str
        """
        data_to_embed = self.get_data_to_embed(None, extra_metadata)
        data_str = self.get_url_encoded_data_str(data_to_embed)
        return self.get_open_tracking_url_from_data_str(data_str)

    def get_click_tracking_url(self, url_to_track: str, extra_metadata: Dict):
        """
        Generate the full click tracking URL.

        This method constructs the full URL for click tracking by embedding the provided URL to track,
        metadata, and other configuration settings into the URL.

        :param url_to_track: The URL to be tracked.
        :type url_to_track: str
        :param extra_metadata: Additional metadata to be included in the URL.
        :type extra_metadata: dict or None
        :return: The full click tracking URL.
        :rtype: str
        """
        data_to_embed = self.get_data_to_embed(url_to_track, extra_metadata)
        data_str = self.get_url_encoded_data_str(data_to_embed)
        return self.get_click_tracking_url_from_data_str(data_str)

    def get_tracking_result(
            self, encoded_url_path: str, request_data: Dict, is_open: bool):
        """
        Parse the encoded tracking URL and return the tracking result.

        This method decodes the provided encoded URL path, decrypts it if an encryption key is available,
        and then extracts the relevant tracking information such as metadata, webhook URL, and tracked URL.

        :param encoded_url_path: The encoded URL path containing tracking information.
        :type encoded_url_path: str
        :param request_data: The request data (dict) associated with the client that made the request to the tracking link.
        :type request_data: dict or None
        :param is_open: Indicates if the URL is for open tracking.
        :type is_open: bool
        :return: The tracking result containing the parsed information.
        :rtype: TrackingResult
        """
        timestamp = int(time.time())
        if encoded_url_path.startswith("/"):
            encoded_url_path = encoded_url_path[1:]

        if self.encryption_key:
            payload = self.encryption_key.decrypt(
                encoded_url_path.encode(self.encoding)).decode(
                    self.encoding)
        else:
            payload = base64.urlsafe_b64decode(
                encoded_url_path.encode(self.encoding)).decode(
                    self.encoding)
        data = json.loads(payload)

        metadata = {}
        if not self.include_default_metadata and self.default_metadata:
            metadata.update(self.default_metadata)
        metadata.update(data.get("metadata", {}))

        if self.include_webhook_url:
            webhook_url = data.get("webhook")
        else:
            webhook_url = self.webhook_url

        return TrackingResult(
            is_open_tracking=is_open,
            is_click_tracking=not is_open,
            tracked_url=data.get("url"),
            webhook_url=webhook_url,
            metadata=metadata,
            request_data=request_data,
            timestamp=timestamp,
        )

    def get_click_tracking_url_path(self, url: str):
        """
        Extract the encoded click tracking URL path from the full URL.

        This method extracts the portion of the URL that contains the encoded click tracking information
        by removing the base click tracking URL from the full URL.

        :param url: The full URL containing the encoded click tracking information.
        :type url: str
        :return: The encoded click tracking URL path.
        """
        return url[len(self.base_click_tracking_url):]

    def get_open_tracking_url_path(self, url: str):
        """
        Extract the encoded open tracking URL path from the full URL.

        This method extracts the portion of the URL that contains the encoded open tracking information
        by removing the base open tracking URL from the full URL.

        :param url: The full URL containing the encoded open tracking information.
        :type url: str
        :return: The encoded open tracking URL path.
        """
        return url[len(self.base_open_tracking_url):]


TrackingResultJSON = namedtuple(
    "TrackingResultJSON", [
        "is_open_tracking", "is_click_tracking", "tracked_url", "webhook_url",
        "metadata", "request_data", "timestamp"])


class TrackingResult(object):

    def __init__(self, is_open_tracking=False, is_click_tracking=False,
                 tracked_url=None, webhook_url=None,
                 metadata=None, request_data=None, timestamp=None):
        """
        :param is_open_tracking: If the result is about open tracking.
        :param is_click_tracking: If the result is about click tracking.
        :param tracked_url: The URL to redirect to. Provided only if
            is_click_tracking is True
        :param webhook_url: The webhook URL to send the tracking notification.
        :param metadata: The metadata (dict) associated with a tracking link.
        :param request_data: The request data (dict) associated with the client
            that made the request to the tracking link.
        :param timestamp: Number of seconds since epoch in UTC
        """
        self.is_open_tracking = is_open_tracking
        self.is_click_tracking = is_click_tracking
        self.tracked_url = tracked_url
        self.webhook_url = webhook_url
        self.metadata = metadata
        self.request_data = request_data
        self.timestamp = timestamp

    def to_json_dict(self):
        """Returns a version of the tracking result that can be safely encoded
        and decoded in JSON

        :rtype: TrackingResultJSON
        """
        return TrackingResultJSON(
            self.is_open_tracking, self.is_click_tracking, self.tracked_url,
            self.webhook_url, self.metadata, self.request_data, self.timestamp)

    def __str__(self):
        return "<pytracking.TrackingResult> is_open_tracking: {0} "\
            "is_click_tracking: {1} tracked_url: {2}".format(
                self.is_open_tracking, self.is_click_tracking,
                self.tracked_url)


def get_configuration(configuration, kwargs):
    """Returns a Configuration instance that merges a configuration instance
    and individual parameters given in a dictionary (usually, the **kwargs of
    an API function).

    The kwargs parameters take precendence over the Configuration instance.
    """
    if configuration:
        configuration = configuration.merge_with_kwargs(kwargs)
    else:
        configuration = Configuration().merge_with_kwargs(kwargs)
    return configuration


def get_open_tracking_url(metadata: Dict = None, configuration: Configuration = None, **kwargs) -> str:
    """Returns a tracking URL encoding the metadata and other information
    specified in the configuration or kwargs.

    :param metadata: A dict that can be json-encoded and that will be encoded
        in the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)

    return configuration.get_open_tracking_url(metadata)


def get_open_tracking_pixel():
    """Returns a tuple consisting of a binary string (the transparent PNG
    pixel) and the MIME type.
    """
    return (TRACKING_PIXEL, PNG_MIME_TYPE)


def get_click_tracking_url(
        url_to_track: str, metadata: Dict = None, configuration: Configuration = None, **kwargs) -> str:
    """Returns a tracking URL encoding the link to track, the provided
    metadata, and other information specified in the configuration or kwargs.

    :param url_to_track: The URL to track.
    :param metadata: A dict that can be json-encoded and that will be encoded
        in the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)

    return configuration.get_click_tracking_url(url_to_track, metadata)


def get_click_tracking_result(
        encoded_url_path: str, request_data: Dict = None, configuration: Configuration = None, **kwargs) -> TrackingResult:
    """Get a TrackingResult instance from an encoded click tracking link.

    :param encoded_url_path: The part of the URL that is encoded and contains
        the tracking information or the full URL (base_click_tracking_url must
        be provided)
    :param request_data: The dictionary to attach to the TrackingResult
        representing the information (e.g., user agent) of the client that
        requested the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    if configuration.base_click_tracking_url and\
            encoded_url_path.startswith(
                configuration.base_click_tracking_url):
        encoded_url_path = get_click_tracking_url_path(
            encoded_url_path, configuration)
    return configuration.get_tracking_result(
        encoded_url_path, request_data, is_open=False)


def get_click_tracking_url_path(
        url: str, configuration: Configuration = None, **kwargs) -> str:
    """Get a part of a URL that contains the encoded click tracking
    information. This is the part that needs to be supplied to
    get_click_tracking_result.

    :param url: The full tracking URL
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    return configuration.get_click_tracking_url_path(url)


def get_open_tracking_result(
        encoded_url_path: str, request_data: Dict = None, configuration: Configuration = None, **kwargs) -> TrackingResult:
    """Get a TrackingResult instance from an encoded open tracking link.

    :param encoded_url_path: The part of the URL that is encoded and contains
        the tracking information or the full URL (base_open_tracking_url must
        be provided)
    :param request_data: The dictionary to attach to the TrackingResult
        representing the information (e.g., user agent) of the client that
        requested the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    if configuration.base_open_tracking_url and\
            encoded_url_path.startswith(
                configuration.base_open_tracking_url):
        encoded_url_path = get_open_tracking_url_path(
            encoded_url_path, configuration)
    return configuration.get_tracking_result(
        encoded_url_path, request_data, is_open=True)


def get_open_tracking_url_path(
        url: str, configuration: Configuration = None, **kwargs) -> str:
    """Get a part of a URL that contains the encoded open tracking
    information. This is the part that needs to be supplied to
    get_open_tracking_result.

    :param url: The full tracking URL
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    return configuration.get_open_tracking_url_path(url)
