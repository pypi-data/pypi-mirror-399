"""Flo Python SDK - Datasets, integrations, and workflow utilities for Flo workflows."""

from flo.quickbooks import QuickBooksClient
from flo.jobber import JobberClient
from flo.plaid import PlaidClient
from flo.buildium import BuildiumClient
from flo.rent_manager import RentManagerClient
from flo.hostaway import HostawayClient
from flo.review import (
    FloReviewClient,
    request_human_review,
    get_review_client,
    ReviewField,
    ReviewFieldOption,
    ReviewResponse,
    HumanReviewPending,
)
from flo.exceptions import (
    FloIntegrationError,
    AuthenticationError,
    APIError,
    QuickBooksError,
    JobberError,
    PlaidError,
    BuildiumError,
    RentManagerError,
    HostawayError,
    DataSourceNotFoundError,
)
from flo.datasets import (
    FloDatasetClient,
    DatasetClient,
    DatasetRow,
    DatasetNotFoundError,
    DatasetError,
)

__all__ = [
    "QuickBooksClient",
    "JobberClient",
    "PlaidClient",
    "BuildiumClient",
    "RentManagerClient",
    "HostawayClient",
    # Human Review
    "FloReviewClient",
    "request_human_review",
    "get_review_client",
    "ReviewField",
    "ReviewFieldOption",
    "ReviewResponse",
    "HumanReviewPending",
    # Datasets
    "FloDatasetClient",
    "DatasetClient",
    "DatasetRow",
    "DatasetNotFoundError",
    "DatasetError",
    # Exceptions
    "FloIntegrationError",
    "AuthenticationError",
    "APIError",
    "QuickBooksError",
    "JobberError",
    "PlaidError",
    "BuildiumError",
    "RentManagerError",
    "HostawayError",
    "DataSourceNotFoundError",
]

__version__ = "0.9.0"

