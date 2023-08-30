# api_questions.py
import os
import re
import json

# import yaml

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

import dbconnect
from questionbank_launch import app
import commonfuncs as cf

ANSWER_TYPES = ("MCQ_single", "InQuestion", "TrueFalse", "MTF")
root = os.path.dirname(__file__)
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "data/uploads")
uploadFolder = os.path.join(root, UPLOAD_FOLDER)


@app.get("/api/questions/list", tags=["questions"])
def questionsList(
    category: str,
    value: str,
):
    if category not in ("subject_id", "topic_id", "subtopic_id"):
        raise HTTPException(status_code=400, detail="Invalid category")

    pattern = "^[a-z0-9-]+$"
    if not re.match(pattern, value):
        raise HTTPException(status_code=400, detail="Invalid value")

    s1 = f"""select t1.id, t1.subtopic_id, t1.title, t1.content, t1.embeds, 
    t2.subject_name, t2.topic_name, t2.subtopic_name
    from questionbank as t1
    left join topics as  t2
    on t1.subtopic_id = t2.subtopic_id
    where t2.{category} = '{value}'
    """

    df1 = dbconnect.makeQuery(s1, output="df")
    if not len(df1):
        return {"message": "no questions found for this selection", "data": []}

    df1["embeds"] = df1["embeds"].apply(json.loads)

    returnD = {"data": df1.to_dict(orient="records")}
    return returnD


class add_question_payload(BaseModel):
    subtopic_id: str
    content: str
    embeds: List[Dict[str, Any]] = []


@app.post("/api/questions/add", tags=["questions"])
def add_question(r: add_question_payload):
    global uploadFolder, ANSWER_TYPES
    s1 = f"select id from topics where subtopic_id = '{r.subtopic_id}'"
    checkTopic = dbconnect.makeQuery(s1, output="oneValue")

    if not checkTopic:
        raise HTTPException(status_code=400, detail="Invalid subtopic_id")

    contentD = cf.yaml2dict(r.content)

    title = contentD.get("title", None)
    embedsList = r.embeds

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

    returnD = {"message": "Question added successfully"}
    return returnD
