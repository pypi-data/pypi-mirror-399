"""
Client for POS Media Data Core API.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .credentials import Credentials
import uuid

class Client:
    def __init__(self, credentials: Credentials) -> None:
        """
        Initialize the POS Core Client.

        Args:
            credentials: An instance of the Credentials class to handle authentication.
        """
        self.credentials = credentials
        # Reuse the session from credentials if available, otherwise create a new one
        self.session = self.credentials.session

    def get_campaigns(
        self,
        size: int = 250,
        page: int = 0,
        orderby: str = "created desc",
        expand: bool = True,
        fetch_all: bool = True,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Retrieve a list of campaigns.

        Args:
            size: Number of records per page.
            page: Page number (0-based).
            orderby: Sorting criteria (e.g. "created desc").
            expand: Whether to expand related entities.
            fetch_all: Whether to fetch all pages or just the requested one.
            **kwargs: Additional query parameters.

        Returns:
            A list of campaigns (dictionaries).
        """
        endpoint = f"{self.credentials.base_url}/cm/campaigns"
        headers = self.credentials.authorization_header
        
        campaigns = []
        
        while True:
            params = {
                "size": size,
                "page": page,
                "orderby": orderby,
                "expand": str(expand).lower()
            }
            params.update(kwargs)

            response = self.session.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            page_count = None
            current_page = None
            data = None
            
            if isinstance(response_data, dict) and "data" in response_data:
                data = response_data["data"]
                page_count = response_data.get("pageCount")
                current_page = response_data.get("currentPage")

            if not data:
                break
                
            campaigns.extend(data)
            
            if not fetch_all:
                break
            
            if page_count is not None and current_page is not None:
                if current_page >= page_count - 1:
                    break
            elif len(data) < size:
                break
                
            page += 1
        
        return campaigns

    def get_campaign_installations(
        self,
        campaign_id: int,
        locations: Optional[List[int]] = None,
        cm_carriers: Optional[List[int]] = None,
        components: Optional[List[int]] = None,
        task_types: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch campaign installations progress summary.

        Args:
            campaign_id: The ID of the campaign.
            locations: List of locations to filter by.
            cm_carriers: List of CM carriers to filter by.
            components: List of components to filter by.
            task_types: List of task types to filter by.

        Returns:
            The installation progress summary.
        """
        endpoint = f"{self.credentials.base_url}/cm/campaigns/{campaign_id}/installationprogresssummary"
        headers = self.credentials.authorization_header
        
        payload = {
            "locations": locations or [],
            "cmCarriers": cm_carriers or [],
            "components": components or [],
            "taskTypes": task_types or []
        }

        response = self.session.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def fetch_document(
        self,
        document_id: uuid.UUID,
        thumbnail: bool = False
    ) -> bytes:
        """Fetch a document by its ID via endpoint: https://pos-core.pos-media.eu/gate/api/v1/cm/documents/dc85d712-dc49-4e07-bb6c-876a6aa97ec6/thumbnail

        Args:
            document_id: The UUID of the document to fetch.
            thumbnail: Whether to fetch the thumbnail version.
        Returns:
            The document content as bytes.
        """
        endpoint = f"{self.credentials.base_url}/cm/documents/{document_id}"
        headers = self.credentials.authorization_header

        if thumbnail is True:

            endpoint += "/thumbnail"
        
        params = {
            "skipValidation": True
        }

        response = self.session.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        content_disposition = response.headers.get("Content-Disposition","")
        
        filename = "unknown"
        
        if content_disposition:
            filename_part = content_disposition.split("filename=")
            if len(filename_part) > 1:
                filename = filename_part[1].strip('"')

            
        
        return {
            "content": response.content,
            "contentType": response.headers.get("Content-Type"),
            "fileName": filename
        }
