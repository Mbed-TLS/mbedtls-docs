#!/usr/bin/env python3
# Script to get the security advisories from the mbedtls website and
# convert them to markdown.
# Notes:
# - Uses Selenium for convenience.
# - Currently Unix-like-only due to '/' in paths.

from selenium import webdriver
import html2text
import os


def scrape_advisory(drvr, url):
    # Get the advisory page
    drvr.get(url)

    # Grab the part containing the useful content
    content = drvr.find_element_by_class_name("content")
    article = content.find_element_by_xpath("./article")

    # Get the raw HTML
    article_html = article.get_attribute("innerHTML")

    # Convert to markdown
    article_md = html2text.html2text(article_html)

    # Remove the 'Sharing' section
    article_md = article_md.split("**Sharing:**")[0]

    # Remove trailing whitespace from lines
    article_md = "\n".join([ln.rstrip() for ln in article_md.split("\n")])

    # Remove trailing blank lines
    article_md = article_md.rstrip("\n")

    return article_md


MAIN_URL = "https://tls.mbed.org/tech-updates/security-advisories"
SECADV_FILENAME = "security-advisories.md"
ADV_DIR = "./advisories"

driver = webdriver.Firefox()
# Get the main advisory list page
driver.get(MAIN_URL)

# Get the list of advisories
main_content = driver.find_element_by_class_name("main-content")
secadv_list = main_content.find_elements_by_xpath("./ul/li")

advisories = []

# Walk through the main page and gather a list of advisories
for secadv in secadv_list:
    # Grab the <a> and extract the name and link
    advisory_link = secadv.find_element_by_xpath("./a")
    advisory_url = advisory_link.get_attribute("href")
    advisory_name = advisory_link.text

    # Generate markdown filename from end of url
    md_filename = advisory_url.replace(MAIN_URL, "") + ".md"
    md_filename = md_filename.lstrip("/")

    # Add name and filename to list
    advisories.append((advisory_name, advisory_url, md_filename))

# Save current dir as 'root' dir
root_dir = os.getcwd()

# Create dir for advisories if needed and chdir to it
if not os.path.isdir(ADV_DIR):
    os.mkdir(ADV_DIR)
os.chdir(ADV_DIR)

# Go and scrape all the individual advisories
for (advisory_name, advisory_url, md_filename) in advisories:
    # Get the advisory text in markdown
    advisory_md = scrape_advisory(driver, advisory_url)

    # Write the advisory to the markdown file
    md_file = open(md_filename, "w")
    md_file.write(advisory_md)
    md_file.close()

# Jump back up into 'root' dir
os.chdir(root_dir)

# Now scrape the main advisory list into markdown
# Get the main page
driver.get(MAIN_URL)

# Grab the part containing the useful content
content = driver.find_element_by_class_name("content")

# Get the raw HTML
content_html = content.get_attribute("innerHTML")

# Tell html2text to ignore links
h2t = html2text.HTML2Text()
h2t.ignore_links = True

# Convert to markdown
content_md = h2t.handle(content_html)

# Remove trailing whitespace from lines
content_md = "\n".join([ln.rstrip() for ln in content_md.split("\n")])

# Create the links to advisories by crude find-replace
# (Note: this is something of a fiddly hack, but it does work)
for (name, url, md_filename) in advisories:
    content_md = content_md.replace(" "+name+"\n", " ["+name+"]("+ADV_DIR+"/"+md_filename+")\n", 1)

# Write to the markdown file
md_file = open(SECADV_FILENAME, "w")
md_file.write(content_md)
md_file.close()

