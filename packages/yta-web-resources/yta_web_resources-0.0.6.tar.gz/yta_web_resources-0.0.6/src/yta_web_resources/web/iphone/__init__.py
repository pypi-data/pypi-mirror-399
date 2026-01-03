"""
The index.html file has been uploaded to 'danialcalayt' >
yta_resources > otros > web_resources > iphone_notification_image'
"""
from yta_web_resources import _WebResource
from yta_general_utils.url.dataclasses import UrlParameters, UrlParameter
from typing import Union


class _IphoneNotificationImageWebResource(_WebResource):
    """
    *For internal use only*

    Web resource to create an Iphone notification and
    download it as an image.

    This is associated with the `web.iphone.index.html`
    resource.
    """

    def get_iphone_notification(
        self,
        app_name: str = 'Booking',
        app_icon_url: str = 'https://play-lh.googleusercontent.com/eJuvWSnbPwEWAQCYwl8i9nPJXRzTv94JSYGGrKIu0qeuG_5wgYtb982-2F_jOGtIytY=w240-h480-rw',
        title: Union[str, None] = None,
        message: str = 'Texto de mensaje de prueba',
        output_filename: str = 'discord_message.png'
    ) -> str:
        """
        Navigate to the web resource and obtain an Iphone
        Notification with the parameters provided, that will
        be stored with the `output_filename` filename provided.
        """
        parameters = UrlParameters([
            UrlParameter('app_name', app_name),
            UrlParameter('app_icon_url', app_icon_url),
            UrlParameter('title', title),
            UrlParameter('message', message)
        ])

        self._load(parameters)

        # The screenshot is taken respecting the alpha
        self.scraper.screenshot_element(
            element = self.scraper.find_element_by_id_waiting('ios-notification'),
            do_include_alpha = True,
            output_filename = output_filename
        )

        return output_filename

# Instances to export here below
IphoneNotificationImageWebResource = lambda do_use_local_url = True, do_use_gui = False: _IphoneNotificationImageWebResource(
    local_path = 'src/yta_web_resources/web/iphone/index.html',
    google_drive_direct_download_url = 'https://drive.google.com/file/d/1M64-t2qB6Aimc0wjknSAGyJwiCK9xVW4/view?usp=sharing',
    do_use_local_url = do_use_local_url,
    do_use_gui = do_use_gui
)