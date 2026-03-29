"""API resource modules organized by Marketo object type."""

from marketo_api.resources.leads import LeadsResource
from marketo_api.resources.activities import ActivitiesResource
from marketo_api.resources.campaigns import CampaignsResource
from marketo_api.resources.programs import ProgramsResource
from marketo_api.resources.lists import ListsResource
from marketo_api.resources.folders import FoldersResource
from marketo_api.resources.tokens import TokensResource
from marketo_api.resources.custom_objects import CustomObjectsResource
from marketo_api.resources.bulk_import import BulkImportResource
from marketo_api.resources.bulk_extract import BulkExtractResource

__all__ = [
    "LeadsResource",
    "ActivitiesResource",
    "CampaignsResource",
    "ProgramsResource",
    "ListsResource",
    "FoldersResource",
    "TokensResource",
    "CustomObjectsResource",
    "BulkImportResource",
    "BulkExtractResource",
]
