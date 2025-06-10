from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import create_model, BaseModel, Field
from typing import Any, Dict, Type, List, Literal
from datetime import date

app = FastAPI()

# In a real ERP, this comes from your database (e.g., a ProductCategory table)
CATEGORY_DEFINITIONS = {
    1: {"name": "Laptop",
        "fields": {"cpu_type": (str, ...), "ram_gb": (int, ...)}},
    2: {"name": "T-Shirt",
        "fields": {"color": (str, ...), "size": (Literal['S','M','L','XL'], ...)}},
    3: {"name": "Equipment",
        "fields": {"voltage": (int, 220), "warranty_expires_on": (date, ...)}}
}

# create method which can generate dynamic model
def get_product_model_for_category(category_id: int) -> Type[BaseModel]:
    """Dependency: Creates a dynamic Pydantic model based on the category."""
    category = CATEGORY_DEFINITIONS.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Product category {category_id} not found.")

    # Base fields common to ALL products
    base_fields = {
        'sku': (str, ...),
        'price': (float, Field(..., gt=0))
    }
    # Add category-specific fields
    all_fields = {**base_fields, **category["fields"]}

    # Use create_model to build the class
    ProductModel = create_model(
        f'Dynamic{category["name"]}Model',
        **all_fields
    )
    return ProductModel

# post request
@app.post("/products/{category_id}")
async def create_dynamic_product(
        category_id: int,
        request_body: Dict[str, Any]
):
    Model = get_product_model_for_category(category_id)
    try:
        validate_product = Model(**request_body)
    except Exception as error:
        raise HTTPException(status_code=422, detail=error)
    return {
        "message" : "Product created successfully",
        "product": validate_product.model_dump()
        }

PRODUCT_DATABASE = {
    101: {"category_id": 1, "sku": "DELL-XPS-15", "price": 1899.99, "attributes": {"cpu_type": "Intel i9", "ram_gb": 32}},
    202: {"category_id": 2, "sku": "PLAIN-WHITE-T", "price": 15.50, "attributes": {"color": "White", "size": "L"}},
    303: {"category_id": 3, "sku": "CNC-MILL-01", "price": 75000.00, "attributes": {"voltage": 220, "warranty_expires_on": "2027-12-31"}}
}

@app.get("/products/{product_id}")
async def get_product(product_id):
    product_data = PRODUCT_DATABASE[int(product_id)]
    if not product_data:
        raise HTTPException(status_code=404, detail="Product does not exist")
    category_id = product_data["category_id"]
    ResponseModel = get_product_model_for_category(category_id)
    response_data = {
        "sku": product_data["sku"],
        "price": product_data["price"],
        **product_data["attributes"]
    }
    try:
        return ResponseModel(**response_data)
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"{error}")

@app.get("/products", response_model=List[Dict[str, Any]])
async def get_all_products():
    """
    Retrieves all products from the database.
    Note: This endpoint returns the raw database entries without dynamic validation.
    """
    return list(PRODUCT_DATABASE.values())

















