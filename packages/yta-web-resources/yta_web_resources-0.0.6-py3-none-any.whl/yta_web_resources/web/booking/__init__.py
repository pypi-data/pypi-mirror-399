"""
The index.html file has been uploaded to 'danialcalayt' >
yta_resources > otros > web_resources > booking_review_image'
"""
from yta_web_resources import _WebResource
from yta_general_utils.url.dataclasses import UrlParameters, UrlParameter


class _BookingReviewImageWebResource(_WebResource):
    """
    *For internal use only*

    Web resource to create a Booking platform review and
    download it as an image.

    This is associated with the `web.booking.index.html`
    resource.
    """

    def get_booking_review(
        self,
        name: str = 'María',
        country: str = 'México',
        score: str = '9,5',
        score_label: str = 'Exceptional',
        text: str = 'Hotel excelente, muy cómodo y bien ubicado.',
        date: str = 'Estancia de febrero de 2025',
        output_filename: str = 'booking_review.png'
    ) -> str:
        """
        Navigate to the web resource and obtain a Booking Review
        with the parameters provided, that will be stored with
        the `output_filename` filename provided.
        """
        parameters = UrlParameters([
            UrlParameter('name', name),
            UrlParameter('country', country),
            UrlParameter('score', score),
            UrlParameter('scoreLabel', score_label),
            UrlParameter('text', text),
            UrlParameter('date', date)
        ])

        """
        Example of a valid request
        
        name = 'María'
        country = 'México'
        score = '9,6' # has to be with comma
        scoreLabel = 'Excepcional'
        text = 'Hotel%20excelente%2C%20muy%20cómodo%20y%20bien%20ubicado.'
        date = 'Estancia%20de%20febrero%202025'
        # TODO: Transform the parameters into the query
        parameters = '?name=María%20López&country=México&score=9,6&scoreLabel=Excepcional&text=Hotel%20excelente%2C%20muy%20cómodo%20y%20bien%20ubicado, y un desayuno espectacular.&date=Estancia%20de%20febrero%202025'
        """

        self._load(parameters)

        # The screenshot is taken respecting the alpha
        self.scraper.screenshot_element(
            element = self.scraper.find_element_by_id_waiting('review-card'),
            do_include_alpha = True,
            output_filename = output_filename
        )

        return output_filename
    
# Instances to export here below
BookingReviewImageWebResource = lambda do_use_local_url = True, do_use_gui = False: _BookingReviewImageWebResource(
    local_path = 'src/yta_web_resources/web/booking/index.html',
    # 17/12/2025 - yta_resources/otros/web_resources/booking_review_image
    google_drive_direct_download_url = 'https://drive.google.com/file/d/1TyAz89ZLIMB3a-fk1qaaKa2qDoVHJ8t3/view?usp=drive_link',
    do_use_local_url = do_use_local_url,
    do_use_gui = do_use_gui
    # do_use_local_url = True,
    # do_use_gui = False
)
"""
Booking review generator constructor. Call it like this:
```
BookingReviewImageWebResource(
    do_use_local_url = True,
    do_use_gui = False
)
```
"""