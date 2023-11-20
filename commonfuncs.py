# commonfuncs.py

import re
import os
import datetime
from ruamel.yaml import YAML, comments
from io import StringIO

root = os.path.dirname(__file__)
timeOffset = 5.5

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


def quoteNcomma(a):
    # turn array into sql IN query string: 'a','b','c'
    holder = []
    for n in a:
        holder.append("'{}'".format(n))
    return ','.join(holder)


# YAML conversion funcions

def cleanup(d):
    # 2023-11-20 : cleanup function needed to resolve issue where yaml loader interprets lines having only "{{img:img1}}"
    # as {ordereddict([('img:img2', None)]): None}
    for key in d.keys():
        if isinstance(d[key], comments.CommentedMap):
            print("replacing",d[key])
            d[key] = str(d[key]).replace("{ordereddict([('",'{{').replace("', None)]): None}","}}")
        if isinstance(d[key], list):
            collector = []
            for l in d[key]:
                if isinstance(l, comments.CommentedMap):
                    print("replacing",l)
                    collector.append(str(l).replace("{ordereddict([('",'{{').replace("', None)]): None}","}}"))
                else:
                    collector.append(l)
            d[key] = collector
    return d

def yaml2dict(y):
    d = YAML().load(y)
    return cleanup(d)

def dict2yaml(d):
    output_stream = StringIO()
    YAML().dump(d, output_stream)
    return output_stream.getvalue()


def split_string_with_placeholders(input_string):
    # from chatgpt
    img_placeholders = re.findall(r'{{img:(.*?)}}', input_string)
    non_placeholder_parts = re.split(r'{{img:.*?}}', input_string)
    return img_placeholders, non_placeholder_parts

def embeds2dict(eArr):
    embeds = {}
    for d in eArr:
        embeds.update(d)
    return embeds


def remove_sql_comments(sql):
    # from chatgpt
    lines = sql.split('\n')
    cleaned_lines = []

    for line in lines:
        cleaned_line = line.split('--')[0].strip()
        cleaned_lines.append(cleaned_line)

    cleaned_sql = '\n'.join(cleaned_lines)
    return cleaned_sql


def int_to_letter(N):
    if 0 <= N < 26:
        return chr(ord('a') + N )
    else:
        return None


def html_formatting(x, embeds={}):
    if "\n" in x:
        x = x.replace('\n','<br>')
    if r"{{img:" in x:
        # print(f"Got image placeholder in {key}: {x}")
        for placeholder in embeds.keys():
            if f"{{{{img:{placeholder}}}}}" in x:
                x = x.replace(
                    f"{{{{img:{placeholder}}}}}", 
                    f"""<img class="qbpreview" src="IMAGEPATH/{embeds[placeholder]}"> """
                )
    return x


def render_html(content_yaml):
    content = yaml2dict(content_yaml)
    embeds = embeds2dict(content.get('embeds',[]))

    for key in content.keys():
        if not isinstance(content[key],str):
            continue

        content[key] = html_formatting(content[key], embeds=embeds)

    
    html_content = f"""<p>{content.get('question')}</p>
    """
    if content['answer_type'] == "TrueFalse":
        html_content += "<ol>"
        for N, statement in enumerate(content['statements']):
            html_content += f"<li>{html_formatting(statement, embeds=embeds)} - ______</li>"
        html_content += "</ol>"
        
    elif content['answer_type'] == "MCQ_single":
        html_content += """<ol class="mcq">"""
        for N, choice in enumerate(content['choices']):
            html_content += f"<li>{html_formatting(choice, embeds=embeds)}</li>"
        html_content += "</ol>"

    elif content['answer_type'] == "MTF":
        html_content += """<div class="row table_mtf">
        <div class="col-md-6">
        """
        for N, statement in enumerate(content['left_side']):
            html_content += f"""<p>{int_to_letter(N)}. {statement}</p>"""
        
        html_content += """</div> <div class="col-md-6">"""
        for N, statement in enumerate(content['right_side']):
            html_content += f"""<p>{N+1}. {statement}</p>"""

        html_content += "</div></div>"
    
    return html_content

def logmessage( *content ):
    global timeOffset
    timestamp = '{:%Y-%m-%d %H:%M:%S} :'.format(datetime.datetime.utcnow() + datetime.timedelta(hours=timeOffset)) # from https://stackoverflow.com/a/26455617/4355695
    line = ' '.join(str(x) for x in list(content)) # from https://stackoverflow.com/a/3590168/4355695
    print(line) # print to screen also
    with open(os.path.join(root,'log.txt'), 'a') as f:
        print(timestamp, line, file=f) # file=f argument at end writes to file. from https://stackoverflow.com/a/2918367/4355695


def is_valid_email(email):
    # Regular expression for a valid email address
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Use re.match to check if the email matches the pattern
    match = re.match(email_pattern, email)
    return bool(match)
