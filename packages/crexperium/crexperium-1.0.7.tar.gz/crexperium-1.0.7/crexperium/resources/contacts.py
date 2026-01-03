"""Contacts resource."""
from typing import Any, Dict, List, Optional

from .base import BaseResource
from ..models import Contact


class ContactsResource(BaseResource):
    """
    Resource for managing contacts.
    """

    def identify(
        self,
        external_id: Optional[str] = None,
        email: Optional[str] = None,
        first_name: str = "",
        last_name: str = "",
        **kwargs,
    ) -> tuple[Contact, bool]:
        """
        Identify or create a contact by external_id or email.

        This is the primary method for SDK user identification. It tries to find
        a contact by external_id first, falls back to email, and creates a new
        contact if neither is found.

        Args:
            external_id: External identifier from your system
            email: Email address
            first_name: First name (used when creating new contact)
            last_name: Last name (used when creating new contact)
            **kwargs: Additional contact fields (phone, title, department, etc.)

        Returns:
            Tuple of (Contact, created) where created is True if contact was created

        Raises:
            ValidationError: If neither external_id nor email is provided
            ValidationError: If email is required but not provided when creating

        Example:
            >>> contact, created = client.contacts.identify(
            ...     external_id="user_123",
            ...     email="user@example.com",
            ...     first_name="John",
            ...     last_name="Doe"
            ... )
        """
        data = {
            "external_id": external_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            **kwargs,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = self.http.post("/api/v1/contacts/identify/", data=data)

        contact = Contact.from_dict(response["contact"])
        created = response.get("created", False)

        return contact, created

    def lookup(
        self, external_id: Optional[str] = None, email: Optional[str] = None
    ) -> Optional[Contact]:
        """
        Lookup a contact by external_id or email without creating.

        Args:
            external_id: External identifier
            email: Email address

        Returns:
            Contact if found, None otherwise

        Example:
            >>> contact = client.contacts.lookup(external_id="user_123")
        """
        params = {}
        if external_id:
            params["external_id"] = external_id
        if email:
            params["email"] = email

        try:
            response = self.http.get("/api/v1/contacts/lookup/", params=params)
            return Contact.from_dict(response)
        except Exception:
            # ResourceNotFoundError or other errors
            return None

    def create(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        **kwargs,
    ) -> Contact:
        """
        Create a new contact.

        Args:
            email: Email address (required)
            first_name: First name
            last_name: Last name
            **kwargs: Additional contact fields

        Returns:
            Created contact

        Example:
            >>> contact = client.contacts.create(
            ...     email="user@example.com",
            ...     first_name="John",
            ...     last_name="Doe",
            ...     phone="+1234567890"
            ... )
        """
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            **kwargs,
        }
        response = self.http.post("/api/v1/contacts/", data=data)
        return Contact.from_dict(response)

    def get(self, contact_id: str) -> Contact:
        """
        Get a contact by ID.

        Args:
            contact_id: Contact UUID

        Returns:
            Contact

        Example:
            >>> contact = client.contacts.get("contact-uuid")
        """
        response = self.http.get(f"/api/v1/contacts/{contact_id}/")
        return Contact.from_dict(response)

    def update(
        self,
        contact_id: Optional[str] = None,
        external_id: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs
    ) -> Contact:
        """
        Update a contact by ID or identifier.

        You can update a contact using either:
        1. contact_id (internal UUID)
        2. external_id, email, or phone (any identifier)

        Args:
            contact_id: Contact UUID (optional if using identifiers)
            external_id: External identifier (optional if using contact_id)
            email: Email address (optional if using contact_id)
            phone: Phone number (optional if using contact_id)
            **kwargs: Fields to update (first_name, last_name, title, etc.)

        Returns:
            Updated contact

        Raises:
            ValueError: If neither contact_id nor any identifier is provided

        Examples:
            # Update by contact_id (legacy method)
            >>> contact = client.contacts.update(
            ...     contact_id="contact-uuid",
            ...     first_name="Jane",
            ...     title="Senior Engineer"
            ... )

            # Update by external_id
            >>> contact = client.contacts.update(
            ...     external_id="user_123",
            ...     first_name="Jane",
            ...     last_name="Doe"
            ... )

            # Update by email
            >>> contact = client.contacts.update(
            ...     email="user@example.com",
            ...     first_name="Jane",
            ...     title="Senior Engineer"
            ... )

            # Update by phone
            >>> contact = client.contacts.update(
            ...     phone="+1234567890",
            ...     first_name="Jane"
            ... )
        """
        # Check if using contact_id (legacy method)
        if contact_id:
            response = self.http.patch(f"/api/v1/contacts/{contact_id}/", data=kwargs)
            return Contact.from_dict(response)

        # Using identifier method
        if not any([external_id, email, phone]):
            raise ValueError(
                "Must provide either contact_id or at least one identifier "
                "(external_id, email, or phone)"
            )

        # Build data with identifiers and update fields
        data = {**kwargs}
        if external_id:
            data["external_id"] = external_id
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone

        response = self.http.patch("/api/v1/contacts/update-by-identifier/", data=data)
        return Contact.from_dict(response)

    def delete(self, contact_id: str) -> None:
        """
        Delete a contact.

        Args:
            contact_id: Contact UUID

        Example:
            >>> client.contacts.delete("contact-uuid")
        """
        self.http.delete(f"/api/v1/contacts/{contact_id}/")

    def list(self, **filters) -> List[Contact]:
        """
        List contacts with optional filters.

        Args:
            **filters: Filter parameters (status, company, etc.)

        Returns:
            List of contacts

        Example:
            >>> contacts = client.contacts.list(status="CUSTOMER")
        """
        response = self.http.get("/api/v1/contacts/", params=filters)
        results = response.get("results", [])
        return [Contact.from_dict(item) for item in results]

    def mark_contacted(self, contact_id: str) -> Contact:
        """
        Mark contact as contacted (updates last_contacted timestamp).

        Args:
            contact_id: Contact UUID

        Returns:
            Updated contact

        Example:
            >>> contact = client.contacts.mark_contacted("contact-uuid")
        """
        response = self.http.patch(f"/api/v1/contacts/{contact_id}/mark_contacted/")
        return Contact.from_dict(response)

    def update_status(self, contact_id: str, status: str) -> Contact:
        """
        Update contact status.

        Args:
            contact_id: Contact UUID
            status: New status (LEAD, PROSPECT, CUSTOMER, etc.)

        Returns:
            Updated contact

        Example:
            >>> contact = client.contacts.update_status("contact-uuid", "CUSTOMER")
        """
        response = self.http.patch(
            f"/api/v1/contacts/{contact_id}/update_status/", data={"status": status}
        )
        return Contact.from_dict(response)
