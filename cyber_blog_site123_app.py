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

# Same RSS feeds as before
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

def create_post(dashboard_url, email, password):
    news_entries = fetch_latest_news()
    if not news_entries:
        raise ValueError("No news fetched. Check RSS feeds.")
    
    today = datetime.now().strftime("%Y-%m-%d")
    post_title = f"Latest Cybersecurity News Roundup - {today}"
    post_content = generate_post_content(news_entries)
    
    try:
        # Set up Selenium with Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        wait = WebDriverWait(driver, 10)
        
        # Step 1: Navigate to login/dashboard (adjust if your login URL differs)
        driver.get(dashboard_url)  # e.g., https://app.site123.com/manager/wizard.php
        
        # Step 2: Log in (inspect elements for exact selectors)
        # Assuming standard login form; replace with actual IDs/classes
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))  # Or By.NAME = "email", By.CSS_SELECTOR = "input[type='email']"
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "password")  # Adjust similarly
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.ID, "login-button")  # Or By.CSS_SELECTOR = "button[type='submit']"
        login_button.click()
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("dashboard"))  # Adjust based on post-login URL
        
        # Step 3: Navigate to Blog section (e.g., click 'Blog' or 'Pages > Blog')
        blog_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Blog")))  # Or By.CSS_SELECTOR = "a[href*='blog']"
        blog_link.click()
        
        # Step 4: Click 'Add New Post' button
        add_post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-post")))  # Inspect for exact class/ID, e.g., ".btn-add-post"
        add_post_button.click()
        
        # Step 5: Fill in the post form (title, content editor)
        title_field = wait.until(EC.presence_of_element_located((By.ID, "post-title")))  # Adjust
        title_field.send_keys(post_title)
        
        # Content editor - assuming it's a WYSIWYG like CKEditor or similar; may need to switch to iframe
        content_iframe = driver.find_element(By.TAG_NAME, "iframe")  # If in iframe
        driver.switch_to.frame(content_iframe)
        content_body = driver.find_element(By.TAG_NAME, "body")  # Or By.ID = "editor"
        content_body.send_keys(post_content)  # Or use execute_script if needed
        driver.switch_to.default_content()
        
        # Optional: Add tags/categories if available
        # tags_field = driver.find_element(By.ID, "tags")
        # tags_field.send_keys("cybersecurity, news")
        
        # Step 6: Publish the post
        publish_button = driver.find_element(By.ID, "publish-button")  # Adjust
        publish_button.click()
        
        # Confirm success (e.g., wait for success message)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        
        driver.quit()
        return "Post published successfully!"
    
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise ValueError(f"Automation error: {str(e)}")

# GUI Setup
def on_generate():
    dashboard_url = url_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    
    if not dashboard_url or not email or not password:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return
    
    try:
        result = create_post(dashboard_url, email, password)
        messagebox.showinfo("Success", result)
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Unexpected Error", str(e))

root = tk.Tk()
root.title("Cyber Blog Auto-Poster for Site123")
root.geometry("400x300")

tk.Label(root, text="Dashboard URL (e.g., https://app.site123.com/manager/wizard.php)").pack(pady=5)
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