import logging
import re
import unicodedata

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.agent import Answer, ask

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI()

MAX_QUESTION_LENGTH = 500
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)

    @field_validator("question", mode="before")
    @classmethod
    def sanitize(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = unicodedata.normalize("NFKC", value)
        value = CONTROL_CHARS.sub("", value)
        return " ".join(value.split())


@app.post("/question")
async def question(body: Question) -> Answer:
    return await ask(body.question)
