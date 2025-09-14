from datetime import datetime, time, timedelta
from typing import Annotated, Literal
from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str = Field(example="Foo")
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300,
        examples=["A very nice item"],
    )
    price: float = Field(
        gt=0, description="The price must be greater than zero", examples=[35.4]
    )
    tax: float | None = Field(examples=[3.2])
    tags: set[str] = set()
    images: list[Image] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class User(BaseModel):
    username: str
    full_name: str | None = None


class FilterParams(BaseModel):
    limit: int = Field(10, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        total_price = item.price + item.tax
        item_dict.update({"price_with_tax": total_price})
    return item_dict


@app.get("/items/")
async def read_items(
    filter_query: Annotated[FilterParams, Query()],
):
    return filter_query


@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[
        int, Path(title="The ID of the item to retrieve", ge=1, le=1000)
    ],
    q: Annotated[str | None, Query(alias="item-query")],
    size: Annotated[float | None, Query(gt=0, lt=10.5)],
    short: bool = False,
):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if size:
        item.update({"size": size})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.put("/items/{item_id}")
async def update_item(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


@app.post("/images/multiple/")
async def create_images(images: list[Image]):
    return images


@app.post("/weights")
async def create_index_weights(weights: dict[int, float]):
    return weights
