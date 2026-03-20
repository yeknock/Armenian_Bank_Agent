import asyncio
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


# Loans - credit
# Savings - deposit

async def main():
    # config for javascript based bank websites
    browser_config = BrowserConfig(headless=True, java_script_enabled=True)

    run_config = CrawlerRunConfig(
        wait_for="body",
        delay_before_return_html=2.5,
        stream=True
    )

    bank_url = "https://conversebank.am/hy/kutakayin/"

    output_path = "converse/deposits"


    # Here I used a simple scrapper to take the data and turn it into markdown format
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=bank_url,
            config=run_config
        )

        # if scrapping succeeded, writing it in its .md file
        if result.success:
            with open("converse/deposits/cumulative.md", "w", encoding="utf-8") as f:
                # Write the source URL at the top so the AI knows where it is
                f.write(f"SOURCE: {result.url}\n\n")
                f.write(result.markdown)
            print(f"Succeeded to scrap: {result.url}")
        else:
            print(f"Failed to scrap: {result.url}")



if __name__ == "__main__":
    asyncio.run(main())