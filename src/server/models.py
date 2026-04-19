"""Pydantic data models for product search."""

from pydantic import BaseModel, Field


class Product(BaseModel):
    """A single product returned from a search tool."""

    name: str = Field(..., description="Product title")
    price: float = Field(..., ge=0, description="Price in INR")
    rating: float = Field(..., ge=0, le=5, description="Average star rating (0-5)")
    buyers: int = Field(..., ge=0, description="Number of buyers / reviews")
    source: str = Field(..., description="E-commerce platform (amazon.in, flipkart.com, myntra.com)")
    url: str = Field(..., description="Direct product URL")
    image_url: str | None = Field(None, description="Product image URL")
    category: str | None = Field(None, description="Product category")


class SearchRequest(BaseModel):
    """Input parameters for a product search tool."""

    query: str = Field(..., min_length=1, max_length=200, description="Search term")
    max_price: float | None = Field(None, ge=0, description="Maximum price in INR")
    limit: int = Field(10, ge=1, le=50, description="Max number of results")


class SearchResponse(BaseModel):
    """Structured response from a product search tool."""

    products: list[Product]
    source: str
    query: str
    total_found: int
