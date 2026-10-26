#!/usr/bin/env python3
"""Add og:image + twitter:image site-wide to Layer8 pages lacking them."""
import re, glob, os

IMG = "https://layer8techgroup.com/assets/images/og-image.jpg"
OG_IMAGE_BLOCK = (
    '  <meta property="og:image" content="' + IMG + '">\n'
    '  <meta property="og:image:width" content="1200">\n'
    '  <meta property="og:image:height" content="630">\n'
    '  <meta name="twitter:image" content="' + IMG + '">\n'
)

# Full OG block for pages with no OG tags at all (ai-services/*, 404.html)
FULL_OG = (
    '  <meta property="og:type" content="website">\n'
    '  <meta property="og:site_name" content="Layer8 Tech Group">\n'
    '  <meta property="og:title" content="{title}">\n'
    '  <meta property="og:description" content="{desc}">\n'
    '  <meta property="og:url" content="{url}">\n'
    '  <meta property="og:image" content="' + IMG + '">\n'
    '  <meta property="og:image:width" content="1200">\n'
    '  <meta property="og:image:height" content="630">\n'
    '  <meta name="twitter:card" content="summary_large_image">\n'
    '  <meta name="twitter:image" content="' + IMG + '">\n'
)

pages = sorted(glob.glob("**/index.html", recursive=True)) + ["404.html"]
changed = []
for p in pages:
    s = open(p).read()
    if "og:image" in s:
        continue  # already has it
    if "twitter:card" in s:
        # has card but no image -> insert image block after twitter:card line
        if "twitter:image" in s:
            continue
        s = s.replace(
            '  <meta name="twitter:card" content="summary_large_image">\n',
            '  <meta name="twitter:card" content="summary_large_image">\n' + OG_IMAGE_BLOCK,
            1,
        )
    else:
        # no OG at all -> build full block from title/desc/canonical
        title = re.search(r"<title>(.*?)</title>", s, re.S)
        title = title.group(1).strip() if title else "Layer8 Tech Group"
        desc = re.search(r'<meta name="description" content="(.*?)">', s)
        desc = desc.group(1) if desc else ""
        canon = re.search(r'<link rel="canonical" href="(.*?)">', s)
        url = canon.group(1) if canon else "https://layer8techgroup.com/"
        block = FULL_OG.format(title=title, desc=desc, url=url)
        # insert after the canonical link if present, else after <head>
        if canon:
            s = s.replace(canon.group(0) + "\n", canon.group(0) + "\n" + block, 1)
        else:
            s = s.replace("<head>\n", "<head>\n" + block, 1)
    open(p, "w").write(s)
    changed.append(p)

print("Changed %d pages:" % len(changed))
for c in changed:
    print("  ", c)
