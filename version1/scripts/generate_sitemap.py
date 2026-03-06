#!/usr/bin/env python3
"""
Generate sitemap.xml for the website
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings


def generate_sitemap():
    """Generate sitemap.xml file"""

    # Create root element
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Static pages
    pages = [
        {"loc": "", "priority": "1.0", "changefreq": "daily"},
        {"loc": "courses", "priority": "0.9", "changefreq": "daily"},
        {"loc": "about", "priority": "0.7", "changefreq": "monthly"},
        {"loc": "contact", "priority": "0.7", "changefreq": "monthly"},
    ]

    for page in pages:
        url = ET.SubElement(urlset, "url")

        loc = ET.SubElement(url, "loc")
        loc.text = f"{settings.BASE_URL}/{page['loc']}"

        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = datetime.now().strftime("%Y-%m-%d")

        changefreq = ET.SubElement(url, "changefreq")
        changefreq.text = page["changefreq"]

        priority = ET.SubElement(url, "priority")
        priority.text = page["priority"]

    # Write to file
    tree = ET.ElementTree(urlset)

    # Ensure static directory exists
    os.makedirs("app/static", exist_ok=True)

    tree.write("app/static/sitemap.xml", encoding="utf-8", xml_declaration=True)
    print("Sitemap generated successfully at app/static/sitemap.xml")


def generate_robots():
    """Generate robots.txt file"""
    robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {settings.BASE_URL}/sitemap.xml
"""
    with open("app/static/robots.txt", "w") as f:
        f.write(robots_content)
    print("robots.txt generated successfully")


if __name__ == "__main__":
    generate_sitemap()
    generate_robots()