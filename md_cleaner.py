from pathlib import Path

def cleaner(filepath):
    junky_lines = ["![", "SOURCE:", ".pdf", "* * *"]

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(filepath, "w", encoding="utf-8") as f:
        for line in lines:
            if not any(word in line for word in junky_lines):
                f.write(line)


dirs = [
    "acba/branches", "acba/credits", "acba/deposits",
    "ameria/branches", "ameria/credits", "ameria/deposits",
    "converse/branches", "converse/credits", "converse/deposits"
    ]

for dir in dirs:
    directory = Path("knowledge/" + dir)

    if not directory.exists():
        print(f"Directory not found: {directory}")
        continue

    for filepath in directory.glob('*.md'):
        cleaner(filepath)