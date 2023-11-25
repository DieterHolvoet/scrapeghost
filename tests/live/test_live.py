"""
These tests require hitting the live API.

This means they require an API key, and cost money to run.
"""
import pytest
import os
from scrapeghost import SchemaScraper, CSS

api_key_is_set = os.getenv("OPENAI_API_KEY", "")


simple_page = """
<html><body>
<header>
<img src="site-logo.png" />
<ul>
<li><a href="/">Home</a></li>
<li><a href="/about">About</a></li>
<li><a href="/contact">Contact</a></li>
</ul>
</header>
{content}
</body></html>
"""

dave = """
<div class="person">
<h1>Dave Bautista</h1>
<img src="https://example.com/dave.jpg" />
<ul>
<li><span class="movie">Guardians of the Galaxy</span> - Drax</li>
<li><span class="movie">Spectre</span> - Mr. Hinx </li>
<li><span class="movie">Blade Runner 2049</span> - Sapper Morton</li>
<li><span class="movie">Glass Onion</span> - Duke Cody</li>
</ul>
<p>Dave also played Glossu Rabban Harkonnen in Dune.</p>
</div>
"""

sam = """
<div class="person">
<h1>Sam Richardson</h1>
<img src="https://example.com/sam.jpg" />
<ul>
<li><span class="tv">The Afterparty</span> - Aniq</li>
<li><span class="tv">Veep</span> - Richard Splett</li>
<li><span class="tv">Detroiters</span> - Sam Duvet</li>
<p>
Sam also played the Baby of the Year Host in long-time collaborator
 Tim Robinson's ITYSL.
</p>
</div>
"""

actor_schema = {
    "actor": "string",
    "image": "url",
    "roles": {"name": "string", "character": "string"},
}


@pytest.mark.skipif(not api_key_is_set, reason="requires API key")
def test_simple_html():
    scraper = SchemaScraper(actor_schema)
    html = simple_page.format(content=dave)
    result = scraper.scrape(html)
    assert 0.0001 < result.total_cost < 0.001
    assert 200 < result.total_prompt_tokens < 300
    assert 100 < result.total_completion_tokens < 200
    assert result.api_time > 0
    assert result.data == {
        "actor": "Dave Bautista",
        "image": "https://example.com/dave.jpg",
        "roles": [
            {"name": "Guardians of the Galaxy", "character": "Drax"},
            {"name": "Spectre", "character": "Mr. Hinx"},
            {"name": "Blade Runner 2049", "character": "Sapper Morton"},
            {"name": "Glass Onion", "character": "Duke Cody"},
            {"name": "Dune", "character": "Glossu Rabban Harkonnen"},
        ],
    }
    assert 0.0001 < scraper.total_cost < 0.001


@pytest.mark.skipif(not api_key_is_set, reason="requires API key")
def test_simple_html_different_content():
    scraper = SchemaScraper(actor_schema, models=["gpt-4"])
    html = simple_page.format(content=sam)
    result = scraper.scrape(html)
    assert result.data == {
        "actor": "Sam Richardson",
        "image": "https://example.com/sam.jpg",
        "roles": [
            {"name": "The Afterparty", "character": "Aniq"},
            {"name": "Veep", "character": "Richard Splett"},
            {"name": "Detroiters", "character": "Sam Duvet"},
            #{"name": "ITYSL", "character": "Baby of the Year Host"},
        ],
    }


@pytest.mark.skipif(not api_key_is_set, reason="requires API key")
def test_simple_html_split_length():
    # use the shortest split length possible to ensure each piece gets own split
    scraper = SchemaScraper(
        actor_schema, auto_split_length=1, extra_preprocessors=[CSS(".person")]
    )
    html = simple_page.format(content=sam + dave)
    result = scraper.scrape(html)
    # Interestingly, the non-structured data is excluded from
    # the list mode result.
    assert result.data == [
        {
            "actor": "Sam Richardson",
            "image": "https://example.com/sam.jpg",
            "roles": [
                {"name": "The Afterparty", "character": "Aniq"},
                {"name": "Veep", "character": "Richard Splett"},
                {"name": "Detroiters", "character": "Sam Duvet"},
                # Issue w/ deterministic outcome on this last piece?
                # {"name": "ITYSL", "character": "Baby of the Year Host"},
            ],
        },
        {
            "actor": "Dave Bautista",
            "image": "https://example.com/dave.jpg",
            "roles": [
                {"name": "Guardians of the Galaxy", "character": "Drax"},
                {"name": "Spectre", "character": "Mr. Hinx"},
                {"name": "Blade Runner 2049", "character": "Sapper Morton"},
                {"name": "Glass Onion", "character": "Duke Cody"},
                {"name": "Dune", "character": "Glossu Rabban Harkonnen"},
            ],
        },
    ]
