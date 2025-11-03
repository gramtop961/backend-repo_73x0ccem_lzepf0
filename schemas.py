"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user"
- Product -> "product"
- Blog -> "blog"
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

class Blog(BaseModel):
    """Blogs collection schema (collection name: "blog")"""
    title: str = Field(..., min_length=3, max_length=160)
    summary: str = Field(..., min_length=10, max_length=500)
    content: Optional[str] = Field(None, description="Full blog content in markdown or HTML")
    tag: Optional[str] = Field(None, description="Category tag like Training, Nutrition, Gear")
    image: Optional[HttpUrl] = Field(None, description="Cover image URL")
    affiliate_label: Optional[str] = Field(None, description="CTA button label")
    affiliate_url: Optional[HttpUrl] = Field(None, description="Affiliate link URL")
    featured: bool = Field(False, description="Whether to feature in Top Picks or hero modules")

class BlogUpdate(BaseModel):
    """Partial update model for blogs"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None
    image: Optional[HttpUrl] = None
    affiliate_label: Optional[str] = None
    affiliate_url: Optional[HttpUrl] = None
    featured: Optional[bool] = None
