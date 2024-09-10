=============
Configuration
=============

Using pytracking with Django
----------------------------

pytracking comes with View classes that you can extend and that handle open and
click tracking link request.

For example, the ``pytracking.django.OpenTrackingView`` will return a 1x1
transparent PNG pixel for GET requests. The
``pytracking.django.ClickTrackingView`` will return a 302 redirect response to
the tracked URL.

Both views will return a 404 response if the tracking URL is invalid. Both
views will capture the user agent and the user ip of the request. This
information will be available in TrackingResult.request_data.

You can extend both views to determine what to do with the tracking result
(e.g., call a webhook or submit a task to a celery queue). Finally, you can
encode your configuration parameters in your Django settings or you can compute
them in your view.

To use the django feature, you must install pytracking with
``pytracking[django]``.

Configuration parameters in Django settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can provide default configuration parameters in your Django settings by
adding this key in your settings file:

::

    PYTRACKING_CONFIGURATION = {
        "webhook_url": "http://requestb.in/123",
        "base_open_tracking_url": "http://tracking.domain.com/open/",
        "base_click_tracking_url": "http://tracking.domain.com/click/",
        "default_metadata": {"analytics_key": "123456"},
        "append_slash": True
    }


Extending default views
~~~~~~~~~~~~~~~~~~~~~~~

::

    from pytracking import Configuration
    from pytracking.django import OpenTrackingView, ClickTrackingView

    class MyOpenTrackingView(OpenTrackingView):

        def notify_tracking_event(self, tracking_result):
            # Override this method to do something with the tracking result.
            # tracking_result.request_data["user_agent"] and
            # tracking_result.request_data["user_ip"] contains the user agent
            # and ip of the client.
            send_tracking_result_to_queue(tracking_result)

        def notify_decoding_error(self, exception, request):
            # Called when the tracking link cannot be decoded
            # Override this to, for example, log the exception
            logger.log(exception)

        def get_configuration(self):
            # By defaut, fetchs the configuration parameters from the Django
            # settings. You can return your own Configuration object here if
            # you do not want to use Django settings.
            return Configuration()


    class MyClickTrackingView(ClickTrackingView):

        def notify_tracking_event(self, tracking_result):
            # Override this method to do something with the tracking result.
            # tracking_result.request_data["user_agent"] and
            # tracking_result.request_data["user_ip"] contains the user agent
            # and ip of the client.
            send_tracking_result_to_queue(tracking_result)

        def notify_decoding_error(self, exception, request):
            # Called when the tracking link cannot be decoded
            # Override this to, for example, log the exception
            logger.log(exception)

        def get_configuration(self):
            # By defaut, fetchs the configuration parameters from the Django
            # settings. You can return your own Configuration object here if
            # you do not want to use Django settings.
            return Configuration()

URLs configuration
~~~~~~~~~~~~~~~~~~

Add this to your urls.py file:

::

    urlpatterns = [
        url(
            "^open/(?P<path>[\w=-]+)/$", MyOpenTrackingView.as_view(),
            name="open_tracking"),
        url(
            "^click/(?P<path>[\w=-]+)/$", MyClickTrackingView.as_view(),
            name="click_tracking"),
    ]

.. ## Flask

.. ## FastAPI