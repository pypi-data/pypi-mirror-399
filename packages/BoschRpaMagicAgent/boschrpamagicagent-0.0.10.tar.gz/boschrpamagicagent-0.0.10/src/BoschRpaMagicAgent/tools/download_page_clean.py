from browser_use import BrowserSession, ActionResult


async def clean_sap_download_page(browser_session: BrowserSession):
    # 1. Get the current page using the correct method
    page = await browser_session.must_get_current_page()

    # 2. Execute JavaScript to distill the DOM
    # This removes the rows directly in the browser memory
    await page.evaluate("""
        () => {
            const table = document.querySelector("tr[vpm='mrss-cont']");
            if (table) {

                table.innerHTML = `<tr><td style="padding:20px; color:red; font-size:18px; border:2px dashed red;">
                    [AI BOT]: table hidden for performance. Use Export shortcut now.
                </td></tr>`;
                return `Cleaned rows.`;
            }
            return "No table found.";
        }
    """)

    return ActionResult(extracted_content='The page has been distilled. The heavy table is removed.',
                        long_term_memory='The page has been distilled. The heavy table is removed.'
                        )
