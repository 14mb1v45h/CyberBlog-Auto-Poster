import tkinter as tk
from tkinter import messagebox
import feedparser
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.exceptions import ServerConnectionError, InvalidCredentialsError
from datetime import datetime
import time  # For sorting timestamps

# List of top 10 cybersecurity RSS feeds (sourced from Feedspot rankings, July 2025)
RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",  # The Hacker News
    "https://grahamcluley.com/feed/",  # Graham Cluley
    "https://www.schneier.com/feed/atom/",  # Schneier on Security
    "https://krebsonsecurity.com/feed/",  # Krebs on Security
    "https://www.csoonline.com/feed/",  # CSO Online
    "https://www.darkreading.com/rss.xml",  # Dark Reading
    "https://www.troyhunt.com/rss/",  # Troy Hunt
    "https://feeds.feedburner.com/eset/blog",  # We Live Security
    "https://news.sophos.com/en-us/feed/",  # Sophos
    "https://www.infosecurity-magazine.com/rss/news/"  # Infosecurity Magazine
]

def fetch_latest_news():
    all_entries = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:  # Get top 3 per feed to avoid overload
                published_time = entry.get('published_parsed') or time.localtime()
                all_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', 'No summary available.'),
                    'published': published_time
                })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    
    # Sort by publish date descending and take top 5
    all_entries.sort(key=lambda x: time.mktime(x['published']), reverse=True)
    return all_entries[:5]

def generate_post_content(news_entries):
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"<h2>Latest Cybersecurity News Roundup - {today}</h2>\n<p>Here's a quick roundup of the top recent stories from leading cybersecurity sources. All links lead to original articles for full details.</p>\n<ul>\n"
    for entry in news_entries:
        content += f"<li><strong><a href='{entry['link']}'>{entry['title']}</a></strong><br>{entry['summary'][:200]}... (Read more at source)</li>\n"
    content += "</ul>\n<p>Stay safe out there! This post is auto-generated for informational purposes.</p>"
    return content

def create_post(url, username, password):
    news_entries = fetch_latest_news()
    if not news_entries:
        raise ValueError("No news fetched. Check RSS feeds.")
    
    today = datetime.now().strftime("%Y-%m-%d")
    post_title = f"Latest Cybersecurity News Roundup - {today}"
    post_content = generate_post_content(news_entries)
    
    try:
        client = Client(f"{url}/xmlrpc.php", username, password)
        post = WordPressPost()
        post.title = post_title
        post.content = post_content
        post.post_status = 'publish'  # Or 'draft' for testing
        post.terms_names = {'post_tag': ['cybersecurity', 'news'], 'category': ['News']}  # Optional: Add tags/categories
        
        post_id = client.call(NewPost(post))
        return post_id
    except InvalidCredentialsError:
        raise ValueError("Invalid username or password.")
    except ServerConnectionError:
        raise ValueError("Could not connect to the site. Ensure XML-RPC is enabled.")
    except Exception as e:
        raise ValueError(f"Error posting: {str(e)}")

# GUI Setup
def on_generate():
    url = url_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    
    if not url or not username or not password:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return
    
    try:
        post_id = create_post(url, username, password)
        messagebox.showinfo("Success", f"Post created! ID: {post_id}")
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Unexpected Error", str(e))

root = tk.Tk()
root.title("Cyber Blog Auto-Poster")
root.geometry("400x250")

tk.Label(root, text="WordPress URL (e.g., https://yourblog.com)").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Label(root, text="Username").pack(pady=5)
username_entry = tk.Entry(root, width=50)
username_entry.pack()

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, width=50, show="*")
password_entry.pack()

generate_button = tk.Button(root, text="Generate & Post", command=on_generate)
generate_button.pack(pady=20)

root.mainloop()