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

