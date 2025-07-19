Overview
This is a Python-based desktop application that automates the posting of cybersecurity news roundups to a blog on Site123. It fetches the latest news from top cybersecurity RSS feeds, generates a formatted blog post, and uses Selenium to simulate browser interactions for logging in, navigating the Site123 editor, and publishing the post. The app features a simple Tkinter GUI for user input.

Ideal for users who want to maintain an active blog without manual effort, focusing on curated cybersecurity content.

Features
News Aggregation: Collects recent stories from 10 prominent cybersecurity sources via RSS (e.g., The Hacker News, Krebs on Security).
Post Generation: Creates a blog post with a title like "Latest Cybersecurity News Roundup - [Date]", including summaries and links to original articles.
GUI Interface: Input fields for login URL, email, and password; one-click "Generate & Post" button.
Browser Automation: Handles Site123's lack of API by simulating user actions with Selenium (login, add post, publish).
Customization: Easily modifiable RSS list, post content, and Selenium selectors.
Debugging Aids: Console prints for step-by-step progress; increased timeouts for reliability.

Requirements
Python: 3.8 or higher (tested on 3.12).

Libraries:
tkinter (built-in for GUI).

feedparser (for parsing RSS feeds).

selenium (for browser automation).

webdriver-manager (for automatic ChromeDriver management).

Browser: Google Chrome installed and up to date.

Site123 Account: Must have a Site123 website with the blog feature enabled.

No Additional Installs: All dependencies can be installed via pip; no internet access required during runtime beyond RSS fetching and Site123 access.

Installation
Download or clone the script file: cyber_blog_site123_app_v2.py.
Install required packages:

pip install feedparser selenium webdriver-manager
Ensure Chrome is installed. The script will handle downloading the matching ChromeDriver.
Usage
Run the application:

python cyber_blog_site123_app_v2.py
In the popped-up window:
Login URL: Enter the Site123 login page (default pre-filled: https://app.site123.com/manager/login.php?l=en). Override if your site uses a custom domain or different endpoint.
Email: Your Site123 account email.
Password: Your account password (entered in plain text field; shown as asterisks).
Click Generate & Post.

The app will:
Fetch and sort the top 5 latest news items.
Generate HTML-formatted post.
Launch a Chrome session (visible by default).
Log in to Site123 manager.
Navigate to Pages > Blog > Add and publish the new post.
On success, a message box confirms the post is published. Check your blog for the new entry.
Headless Operation: For automated/scheduled runs without a visible window, uncomment the --headless option in the code under create_post() function.
Security Note: Passwords are handled in plain text in the GUI. For sensitive use, consider storing credentials in environment variables or using a more secure input method. Automation may be subject to Site123's terms—review their policy to avoid account issues.


Configuration and Customization
RSS Feeds: Edit the RSS_FEEDS array in the script to change sources or add more (e.g., add "https://example.com/rss").
Post Format: Modify generate_post_content() to adjust the post structure, e.g., images or more/less summaries.
Selenium Selectors: Critical for reliability. If Site123's UI changes:
Use Chrome DevTools (F12) to inspect elements on the login/editor pages.
Update By.ID, By.CSS_SELECTOR, etc. in create_post() (e.g., email field might be By.NAME="user_email").
Test step-by-step with console prints.
Timeouts: If pages load slowly, increase WebDriverWait(driver, 20) to a higher value (e.g., 30).
Scheduling: Automate daily runs using cron (Linux/Mac):

Copy
0 8 * * * /usr/bin/python /path/to/cyber_blog_site123_app_v2.py
Or Windows Task Scheduler. Note: GUI inputs would need to be hardcoded or passed as args for non-interactive runs.
Troubleshooting
TimeoutException or NoSuchElementException: Usually due to mismatched selectors or slow loading. Verify selectors with DevTools; increase wait times; ensure stable internet.
Login Failures: Double-check credentials by logging in manually. If two-factor auth or CAPTCHA triggers, automation may need manual setup (e.g., session cookies).
No News Items: RSS feeds might be down or URLs changed—test individually with feedparser.parse().
ChromeDriver Errors: If version mismatch, reinstall webdriver-manager or manually download matching driver.
General Errors: Run in a terminal to see console output (e.g., "Waiting for email field..."). Share stacktraces for help.
Platform Changes: If Site123 updates their interface, selectors may break—monitor and update accordingly.
For advanced fixes or features (e.g., email notifications, AI-summarized content), extend the code or consult Python/Selenium docs.

Limitations
UI Dependency: Relies on Site123's current HTML structure; prone to breaking on site updates.
Performance: Selenium is slower than API-based methods; not ideal for very frequent posts.
Legal/Ethical: Aggregating news summaries is for personal use—ensure compliance with source copyrights (links and attributions are included). Over-automation might violate Site123 TOS.
Alternatives: For easier automation, consider platforms like WordPress with REST API support.
Contributing
Feel free to fork and improve! Suggestions: Add support for other site builders, integrate AI for better summaries, or make it web-based.

License
This project is open-source under the MIT License. Use, modify, and distribute freely. No warranties provided.


COPYRIGHT@CYBERDUDEBIVASH  2025