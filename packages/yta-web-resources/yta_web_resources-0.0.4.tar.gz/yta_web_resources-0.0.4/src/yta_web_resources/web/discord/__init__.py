"""
The index.html file has been uploaded to 'danialcalayt' >
yta_resources > otros > web_resources > discord_message_image'
"""
from yta_web_resources import _WebResource
from yta_general_utils.url.dataclasses import UrlParameters, UrlParameter


class _DiscordMessageImageWebResource(_WebResource):
    """
    *For internal use only*

    Web resource to create a Discord message and download
    it as an image.

    This is associated with the `web.discord.index.html`
    resource.
    """

    def get_discord_message(
        self,
        username: str = 'Usuario',
        message: str = 'Texto de mensaje de prueba',
        output_filename: str = 'discord_message.png'
    ) -> str:
        """
        Navigate to the web resource and obtain a Discord Review
        with the parameters provided, that will be stored with
        the `output_filename` filename provided.
        """
        parameters = UrlParameters([
            UrlParameter('username', username),
            UrlParameter('message', message),
        ])

        self._load(parameters)

        # The screenshot is taken respecting the alpha
        self.scraper.screenshot_element(
            element = self.scraper.find_element_by_id_waiting('discord-message'),
            do_include_alpha = True,
            output_filename = output_filename
        )

        return output_filename

# Instances to export here below
DiscordMessageImageWebResource = lambda do_use_local_url = True, do_use_gui = False: _DiscordMessageImageWebResource(
    local_path = 'src/yta_web_resources/web/discord/index.html',
    google_drive_direct_download_url = 'https://drive.google.com/file/d/1JG3O5I6lTYpd5iebqdnd6fLpIB1WcFCQ/view?usp=sharing',
    do_use_local_url = do_use_local_url,
    do_use_gui = do_use_gui
)