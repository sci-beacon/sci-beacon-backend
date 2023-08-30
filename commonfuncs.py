# commonfuncs.py

import re
from ruamel.yaml import YAML
from io import StringIO

def create_unique_slug(text, existing_slugs):
    # Remove non-alphanumeric characters and convert to lowercase
    slug = re.sub(r'\W+', '', text.lower())
    
    # Limit the slug to 10 characters
    slug = slug[:16]
    
    # If the slug is not unique, append a unique 2-digit number
    if slug in existing_slugs:
        for i in range(1, 100):
            unique_slug = f"{slug}-{i:03d}"
            if unique_slug not in existing_slugs:
                return unique_slug
    else:
        return slug



if __name__ == "__main__":
    # Test create_unique_slug
    title = "Cell organelles"
    # List of existing slugs (for testing purposes)
    existing_slugs = ["example", "unique01", "slug02", "thisisates", "thisisatesttitle","thisisatesttitle-001"]
    slug = create_unique_slug(title, existing_slugs)
    print(slug)  # Output will be "thisisatest"


def quoteNcomma(a):
    # turn array into sql IN query string: 'a','b','c'
    holder = []
    for n in a:
        holder.append("'{}'".format(n))
    return ','.join(holder)


# YAML conversion funcions
def yaml2dict(y):
    return YAML().load(y)

def dict2yaml(d):
    output_stream = StringIO()
    YAML().dump(d, output_stream)
    return output_stream.getvalue()
