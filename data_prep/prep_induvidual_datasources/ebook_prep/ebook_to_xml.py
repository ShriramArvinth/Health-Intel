import re

file_path = './knowledge.txt'
with open(file_path, 'r') as file:
    content = file.read()

# Replace < and > with textual versions to avoid XML issues
content = re.sub(r"<", "less than", content)
content = re.sub(r">", "greater than", content)
# Replace curly apostrophes with straight ones
content = re.sub(r"’", "'", content)

# Split content into sections as before
sections = [m.group() for m in re.finditer(r'((?:^Section \d+.*?(?=^Section \d+|\Z))|(?:^.+?(?=^Section \d+|\Z)))', content, re.MULTILINE | re.DOTALL)]

# Build XML string
xml_lines = ["<all_chapters>"]
for section in sections:
    xml_lines.append("  <chapter>")
    xml_lines.append("    <content>")
    xml_lines.append(section.strip())
    xml_lines.append("    </content>")
    xml_lines.append("  </chapter>")
xml_lines.append("</all_chapters>")

xml_string = "\n".join(xml_lines)

with open("./ebook1.xml", "w", encoding="utf-8") as f:
    f.write(xml_string)