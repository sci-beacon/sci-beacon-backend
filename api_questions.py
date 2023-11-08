# api_questions.py
import os
import re
import json

# import yaml

from fastapi import HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Any

import dbconnect
from questionbank_launch import app
import commonfuncs as cf
from api_users import authenticate


ANSWER_TYPES = ("MCQ_single", "InQuestion", "TrueFalse", "MTF")
root = os.path.dirname(__file__)
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "data/uploads")
uploadFolder = os.path.join(root, UPLOAD_FOLDER)

TEMPLATE_FOLDER = os.path.join(root, "templates")


@app.get("/api/questions/list", tags=["questions"])
def questionsList(
    category: str = None,
    value: str = None,
):
    cf.logmessage("questionsList GET api call")
    if category in ("subject_id", "topic_id", "subtopic_id"):
        pattern = "^[a-z0-9-]+$"
        if not re.match(pattern, value):
            raise HTTPException(status_code=400, detail="Invalid value")
        whereClause = f"where t2.{category} = '{value}'"

    else:
        whereClause = ""

    s1 = f"""select t1.id, t1.subtopic_id, t1.title, t1.content, 
    t2.subject_name, t2.topic_name, t2.subtopic_name,
    t2.topic_id, t2.subject_id
    from questionbank as t1
    left join topics as  t2
    on t1.subtopic_id = t2.subtopic_id
    {whereClause}
    
    """

    df1 = dbconnect.makeQuery(s1, output="df")
    if not len(df1):
        return {"message": "no questions found for this selection", "data": []}

    df1["preview"] = df1['content'].apply(cf.render_html)
    # del df1['content']

    returnD = {"data": df1.to_dict(orient="records")}
    return returnD


class add_question_payload(BaseModel):
    subtopic_id: str
    content: str
    embeds: List[Dict[str, Any]] = []


@app.post("/api/questions/add", tags=["questions"])
def add_question(r: add_question_payload, x_access_token: str = Header(...)):
    cf.logmessage("add_question POST api call")

    user_id, email = authenticate(x_access_token)

    global uploadFolder, ANSWER_TYPES
    s1 = f"select id from topics where subtopic_id = '{r.subtopic_id}'"
    checkTopic = dbconnect.makeQuery(s1, output="oneValue")

    if not checkTopic:
        raise HTTPException(status_code=400, detail="Invalid subtopic_id")

    contentD = cf.yaml2dict(r.content)

    title = contentD.get("title", None)
    embedsList = r.embeds
    # what r.embeds should look like: [{"img1": "gt4d.webp"}, {"img2": "ghjuy654edfghy.webp"}]

    # validation of content fields
    # if (not title) or (not question) or (not answer_type):
    #      raise HTTPException(status_code=400, detail="Invalid question")
    for embed in embedsList:
        assert isinstance(embed, dict), "bad embeds"
        assert len(embed.keys()) == 1, f"too many keys in embed: {embed}"
        for key in embed.keys():
            if f"{{img:{key}}}" not in r.content:
                raise HTTPException(
                    status_code=401, detail=f"Didn't find {key} in the content"
                )
            if not os.path.isfile(os.path.join(uploadFolder, embed[key])):
                raise HTTPException(
                    status_code=401, detail=f"File not found: {key}: {embed[key]}"
                )

    # check if title is repeating within this sub-topic
    s2 = f"select count(*) from questionbank where subtopic_id = '{r.subtopic_id}' and title = '{title}'"
    repeatTitle = dbconnect.makeQuery(s2, output="oneValue")
    if repeatTitle:
        raise HTTPException(
            status_code=409, detail="Title already taken, please choose another"
        )

    # return "ok"

    # update embeds and other fixed fields in content
    if len(embedsList):
        contentD["embeds"] = embedsList

    content = cf.dict2yaml(contentD)

    escaped_text = content.replace("'", "''")
    # begin insert
    i1 = f"""insert into questionbank (subtopic_id, title, content, embeds) values
    ('{r.subtopic_id}', '{title}', '{escaped_text}', '{json.dumps(embedsList)}')
    """
    i1Count = dbconnect.execSQL(i1)
    if not i1Count:
        raise HTTPException(
            status_code=500, detail="Unable to add question to DB"
        )
        return

    returnD = {"message": "Question added successfully", "count": i1Count}
    return returnD



@app.get("/api/questions/templates", tags=["questions"])
def question_templates():
    cf.logmessage("question_templates GET api call")
    # ANSWER_TYPES = ("MCQ_single", "InQuestion", "TrueFalse", "MTF")
    data = []

    with open(os.path.join(TEMPLATE_FOLDER,"mcq.yaml"),"r") as f:
        data.append({
            "title": "Multiple Choice Question",
            "template": f.read(),
            "answer_type": "MCQ_single",
        })
        # data['Multiple Choice Question'] = f.read()
    
    with open(os.path.join(TEMPLATE_FOLDER,"inquestion.yaml"),"r") as f:
        data.append({
            "title": "Only Question",
            "template": f.read(),
            "answer_type": "InQuestion",
        })

    with open(os.path.join(TEMPLATE_FOLDER,"mtf.yaml"),"r") as f:
        data.append({
            "title": "Match the Following",
            "template": f.read(),
            "answer_type": "MTF",
        })
        # data['Match the Following'] = f.read()

    
    with open(os.path.join(TEMPLATE_FOLDER,"truefalse.yaml"),"r") as f:
        data.append({
            "title": "True or False",
            "template": f.read(),
            "answer_type": "TrueFalse",
        })
    returnD = {"data": data}
    return returnD




@app.delete("/api/questions/delete")
def delete_question(qid: int, x_access_token: str = Header(...)):
    cf.logmessage("delete_question DELETE api call")

    user_id, email = authenticate(x_access_token)

    d1 = f"delete from questionbank where id={qid}"

    d1Count = dbconnect.execSQL(d1)

    returnD = {"deleted": True, "count": d1Count}
    return returnD
