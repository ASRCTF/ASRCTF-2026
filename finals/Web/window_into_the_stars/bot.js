const puppeteer = require('puppeteer');
const url = process.argv[2];
const adminUser = process.argv[3];
const adminPass = process.argv[4];
(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-popup-blocking',
                '--disable-gpu',
                '--disable-dev-shm-usage'
            ],
            headless: 'new'
        });
        const page = await browser.newPage();
        await page.goto('http:
        await page.type('input[name="username"]', adminUser);
        await page.type('input[name="password"]', adminPass);
        await Promise.all([
            page.waitForNavigation(),
            page.click('button[type="submit"]')
        ]);
        console.log(`[Bot] Logged in successfully. Visiting ${url}`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await new Promise(resolve => setTimeout(resolve, 300000));
    } catch (err) {
        console.error(`[Bot] Error: ${err}`);
    } finally {
        if (browser) await browser.close();
        process.exit(0);
    }
})();
