import os

dirs = [
    "acba/branches", "acba/credits", "acba/deposits",
    "ameria/branches", "ameria/credits", "ameria/deposits",
    "converse/branches", "converse/credits", "converse/deposits"
    ]

for dir in dirs:
    directory = os.fsencode("knowledge/" + dir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".md"):
            print(f"{directory}/{os.path.basename(filename)}")
            continue
        else:
            continue