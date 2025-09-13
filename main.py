from typing import Annotated, Literal
from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


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
    *,
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results
