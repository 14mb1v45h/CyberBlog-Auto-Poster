import tkinter as tk
from tkinter import messagebox
import feedparser
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# RSS feeds (same as before)
RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://grahamcluley.com/feed/",
    "https://www.schneier.com/feed/atom/",
    "https://krebsonsecurity.com/feed/",
    "https://www.csoonline.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.troyhunt.com/rss/",
    "https://feeds.feedburner.com/eset/blog",
    "https://news.sophos.com/en-us/feed/",
    "https://www.infosecurity-magazine.com/rss/news/"
]

def fetch_latest_news():
    all_entries = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                published_time = entry.get('published_parsed') or time.localtime()
                all_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', 'No summary available.'),
                    'published': published_time
                })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    all_entries.sort(key=lambda x: time.mktime(x['published']), reverse=True)
    return all_entries[:5]

def generate_post_content(news_entries):
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"<h2>Latest Cybersecurity News Roundup - {today}</h2>\n<p>Here's a quick roundup of the top recent stories from leading cybersecurity sources. All links lead to original articles for full details.</p>\n<ul>\n"
    for entry in news_entries:
        content += f"<li><strong><a href='{entry['link']}'>{entry['title']}</a></strong><br>{entry['summary'][:200]}... (Read more at source)</li>\n"
    content += "</ul>\n<p>Stay safe out there! This post is auto-generated for informational purposes.</p>"
    return content

def create_post(login_url, email, password):
    news_entries = fetch_latest_news()
    if not news_entries:
        raise ValueError("No news fetched. Check RSS feeds.")
    
    today = datetime.now().strftime("%Y-%m-%d")
    post_title = f"Latest Cybersecurity News Roundup - {today}"
    post_content = generate_post_content(news_entries)
    
    try:
        # Setup Selenium
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Uncomment for background run (no visible browser)
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)  # Increased timeout to 20s
        
        print("Navigating to login URL...")
        driver.get(login_url)  # Use login URL, e.g., https://app.site123.com/manager/login/login.php?l=en
        
        # Step 1: Fill login form - UPDATE SELECTORS HERE
        print("Waiting for email field...")
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))  # Or By.NAME="email", By.CSS_SELECTOR="input[type='email']"
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "password")  # Or By.NAME="password", By.CSS_SELECTOR="input[type='password']"
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.ID, "login-button")  # Or By.CSS_SELECTOR="button[type='submit']", By.CLASS_NAME="btn-login"
        login_button.click()
        
        print("Logged in, waiting for dashboard...")
        wait.until(EC.url_contains("manager/wizard"))  # Assumes redirect to wizard.php or dashboard
        
        # Step 2: Navigate to Blog - UPDATE SELECTORS BASED ON INSPECTION
        print("Navigating to Pages/Blog...")
        pages_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Pages")))  # Or By.CSS_SELECTOR="a[href*='pages']"
        pages_link.click()
        
        blog_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Blog")))  # Or By.CSS_SELECTOR=".blog-page-link"
        blog_link.click()
        
        edit_blog_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.edit")))  # From docs: Edit button
        edit_blog_button.click()
        
        # Step 3: Add New Post
        print("Adding new post...")
        add_post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-new-post")))  # Or By.ID="add-new-post"
        add_post_button.click()
        
        # Step 4: Fill post form
        title_field = wait.until(EC.presence_of_element_located((By.ID, "post-title")))  # Update
        title_field.send_keys(post_title)
        
        # Content editor (likely iframe)
        content_iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))  # If multiple, specify By.CSS_SELECTOR="iframe.editor"
        driver.switch_to.frame(content_iframe)
        content_body = driver.find_element(By.TAG_NAME, "body")  # Or By.ID="tinymce" for TinyMCE
        content_body.clear()
        content_body.send_keys(post_content)  # Send HTML directly; if not working, use execute_script
        driver.switch_to.default_content()
        
        # Optional: Tags
        # tags_field = driver.find_element(By.ID, "tags")
        # tags_field.send_keys("cybersecurity, news")
        
        # Step 5: Publish
        print("Publishing post...")
        publish_button = driver.find_element(By.ID, "publish")  # Or By.CLASS_NAME="btn-publish"
        publish_button.click()
        
        # Wait for confirmation
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))  # Update if needed
        
        driver.quit()
        return "Post published successfully!"
    
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise ValueError(f"Automation error: {str(e)}")

# GUI Setup
def on_generate():
    login_url = url_entry.get().strip() or "https://app.site123.com/manager/login/login.php?l=en"  # Default to login URL
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    
    if not email or not password:
        messagebox.showerror("Input Error", "Please fill in email and password.")
        return
    
    try:
        result = create_post(login_url, email, password)
        messagebox.showinfo("Success", result)
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Unexpected Error", str(e))

root = tk.Tk()
root.title("Cyber Blog Auto-Poster for Site123")
root.geometry("400x300")

tk.Label(root, text="Login URL (default: https://app.site123.com/manager/login/login.php?l=en)").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Label(root, text="Email").pack(pady=5)
email_entry = tk.Entry(root, width=50)
email_entry.pack()

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, width=50, show="*")
password_entry.pack()

generate_button = tk.Button(root, text="Generate & Post", command=on_generate)
generate_button.pack(pady=20)

root.mainloop()