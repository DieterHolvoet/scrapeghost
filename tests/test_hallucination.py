import pytest
import lxml.html
from scrapeghost.responses import ScrapeResponse
from scrapeghost.postprocessors import HallucinationChecker, PostprocessingError


def test_hallucination_checker():
    response = ScrapeResponse(
        parsed_html=lxml.html.fromstring(
            """<a href="https://example.com">Moltar</a><p>Director</p>"""
        ),
        data={"name": "Moltar", "role": "Director", "url": "https://example.com"},
    )

    # no hallucination
    hpp = HallucinationChecker()
    hpp(response, None)

    response.data["last_name"] = "Moltanski"
    with pytest.raises(PostprocessingError):
        hpp(response, None)
