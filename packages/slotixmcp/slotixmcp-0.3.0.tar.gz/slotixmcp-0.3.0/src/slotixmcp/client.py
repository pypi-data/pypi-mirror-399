"""
HTTP client for Slotix API.
"""
import os
from typing import Any, Optional
import httpx


class SlotixClient:
    """HTTP client for communicating with Slotix API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("SLOTIX_API_KEY")
        self.api_url = (api_url or os.environ.get("SLOTIX_API_URL", "https://app.slotix.ai/api")).rstrip("/")

        if not self.api_key:
            raise ValueError(
                "API key is required. Set SLOTIX_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self._client = httpx.AsyncClient(
            base_url=f"{self.api_url}/v1/mcp",
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None
    ) -> dict[str, Any]:
        """Make an HTTP request to the Slotix API."""
        response = await self._client.request(
            method=method,
            url=path,
            params=params,
            json=json
        )

        if response.status_code == 401:
            raise ValueError("Invalid API key. Please check your SLOTIX_API_KEY.")

        if response.status_code == 403:
            raise ValueError("Access forbidden. Your account may be inactive.")

        if response.status_code == 404:
            raise ValueError(f"Resource not found: {path}")

        if response.status_code >= 400:
            try:
                error = response.json()
                detail = error.get("detail", str(error))
            except Exception:
                detail = response.text
            raise ValueError(f"API error ({response.status_code}): {detail}")

        if response.status_code == 204:
            return {"success": True}

        return response.json()

    # Profile
    async def get_profile(self) -> dict:
        """Get professional profile."""
        return await self._request("GET", "/profile")

    # Appointments
    async def get_appointments(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict:
        """Get appointments."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if status:
            params["status"] = status
        return await self._request("GET", "/appointments", params=params)

    async def get_today_appointments(self) -> dict:
        """Get today's appointments."""
        return await self._request("GET", "/appointments/today")

    async def get_week_appointments(self) -> dict:
        """Get this week's appointments."""
        return await self._request("GET", "/appointments/week")

    async def get_appointment(self, appointment_id: int) -> dict:
        """Get a specific appointment."""
        return await self._request("GET", f"/appointments/{appointment_id}")

    async def create_appointment(
        self,
        start_datetime: str,
        duration_minutes: int = 30,
        client_name: Optional[str] = None,
        client_contact: Optional[str] = None,
        client_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> dict:
        """Create a new appointment.

        Either client_name or client_id must be provided.
        If client_id is provided, client info is resolved from the database.
        """
        data: dict[str, Any] = {
            "start_datetime": start_datetime,
            "duration_minutes": duration_minutes,
        }
        if client_name:
            data["client_name"] = client_name
        if client_contact:
            data["client_contact"] = client_contact
        if client_id:
            data["client_id"] = client_id
        if notes:
            data["notes"] = notes
        return await self._request("POST", "/appointments", json=data)

    async def update_appointment(
        self,
        appointment_id: int,
        start_datetime: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        amount_paid: Optional[float] = None,
        payment_method: Optional[str] = None,
        payment_notes: Optional[str] = None,
        payment_complete: Optional[bool] = None
    ) -> dict:
        """Update an appointment."""
        data = {}
        if start_datetime:
            data["start_datetime"] = start_datetime
        if duration_minutes:
            data["duration_minutes"] = duration_minutes
        if status:
            data["status"] = status
        if notes is not None:
            data["notes"] = notes
        if amount_paid is not None:
            data["amount_paid"] = amount_paid
        if payment_method is not None:
            data["payment_method"] = payment_method
        if payment_notes is not None:
            data["payment_notes"] = payment_notes
        if payment_complete is not None:
            data["payment_complete"] = payment_complete
        return await self._request("PUT", f"/appointments/{appointment_id}", json=data)

    async def cancel_appointment(self, appointment_id: int) -> dict:
        """Cancel an appointment."""
        return await self._request("DELETE", f"/appointments/{appointment_id}")

    # Clients
    async def get_clients(
        self,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Get clients."""
        params = {"limit": limit, "offset": offset}
        if search:
            params["search"] = search
        return await self._request("GET", "/clients", params=params)

    async def get_client(self, client_id: int) -> dict:
        """Get a specific client."""
        return await self._request("GET", f"/clients/{client_id}")

    # Availability
    async def get_availability(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list:
        """Get available slots."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._request("GET", "/availability", params=params)

    # Stats
    async def get_stats(self, period: str = "month") -> dict:
        """Get business statistics."""
        return await self._request("GET", "/stats", params={"period": period})

    # Notifications
    async def send_notification(
        self,
        message: str,
        client_id: Optional[int] = None,
        client_ids: Optional[list[int]] = None,
        channel: str = "auto"
    ) -> dict:
        """Send a notification to one or more clients.

        Either client_id (single) or client_ids (multiple) must be provided.
        """
        data: dict[str, Any] = {
            "message": message,
            "channel": channel
        }
        if client_ids:
            data["client_ids"] = client_ids
        elif client_id:
            data["client_id"] = client_id
        return await self._request("POST", "/notifications/send", json=data)

    # Coupons
    async def create_coupon(
        self,
        client_id: Optional[int] = None,
        client_ids: Optional[list[int]] = None,
        discount_type: Optional[str] = None,
        discount_value: Optional[float] = None,
        validity_days: Optional[int] = None
    ) -> dict:
        """Create and send a coupon to one or more clients.

        Either client_id (single) or client_ids (multiple) must be provided.
        """
        data: dict[str, Any] = {}
        if client_ids:
            data["client_ids"] = client_ids
        elif client_id:
            data["client_id"] = client_id
        if discount_type:
            data["discount_type"] = discount_type
        if discount_value is not None:
            data["discount_value"] = discount_value
        if validity_days is not None:
            data["validity_days"] = validity_days
        return await self._request("POST", "/coupons/send", json=data)

    # Catalog (Services/Products)
    async def get_catalog_items(
        self,
        is_active: Optional[bool] = None,
        is_product: Optional[bool] = None,
        category: Optional[str] = None
    ) -> dict:
        """Get catalog items (services/products)."""
        params = {}
        if is_active is not None:
            params["is_active"] = is_active
        if is_product is not None:
            params["is_product"] = is_product
        if category:
            params["category"] = category
        return await self._request("GET", "/catalog", params=params)

    async def create_catalog_item(
        self,
        name: str,
        price: float,
        description: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        is_active: bool = True,
        is_product: bool = False,
        category: Optional[str] = None
    ) -> dict:
        """Create a new catalog item (service or product)."""
        data: dict[str, Any] = {
            "name": name,
            "price": price,
            "is_active": is_active,
            "is_product": is_product,
        }
        if description:
            data["description"] = description
        if duration_minutes is not None:
            data["duration_minutes"] = duration_minutes
        if category:
            data["category"] = category
        return await self._request("POST", "/catalog", json=data)

    async def update_catalog_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        description: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_product: Optional[bool] = None,
        category: Optional[str] = None
    ) -> dict:
        """Update a catalog item."""
        data = {}
        if name is not None:
            data["name"] = name
        if price is not None:
            data["price"] = price
        if description is not None:
            data["description"] = description
        if duration_minutes is not None:
            data["duration_minutes"] = duration_minutes
        if is_active is not None:
            data["is_active"] = is_active
        if is_product is not None:
            data["is_product"] = is_product
        if category is not None:
            data["category"] = category
        return await self._request("PUT", f"/catalog/{item_id}", json=data)

    async def delete_catalog_item(self, item_id: int) -> dict:
        """Delete a catalog item."""
        return await self._request("DELETE", f"/catalog/{item_id}")

    # Appointment Services
    async def get_appointment_services(self, appointment_id: int) -> list:
        """Get services attached to an appointment."""
        return await self._request("GET", f"/appointments/{appointment_id}/services")

    async def add_service_to_appointment(
        self,
        appointment_id: int,
        catalog_item_id: int
    ) -> dict:
        """Add a service to an appointment."""
        return await self._request(
            "POST",
            f"/appointments/{appointment_id}/services",
            json={"catalog_item_id": catalog_item_id}
        )

    async def remove_service_from_appointment(
        self,
        appointment_id: int,
        service_id: int
    ) -> dict:
        """Remove a service from an appointment."""
        return await self._request(
            "DELETE",
            f"/appointments/{appointment_id}/services/{service_id}"
        )

    # Schedule / Availability Management
    async def get_weekly_schedule(self) -> dict:
        """Get the complete weekly availability schedule."""
        return await self._request("GET", "/schedule/weekly")

    async def set_availability(
        self,
        day_of_week: int,
        start_time: str,
        end_time: str,
        slot_duration: Optional[int] = None,
        is_active: bool = True
    ) -> dict:
        """Set or update availability for a specific day of the week.

        Args:
            day_of_week: 0=Monday through 6=Sunday
            start_time: Opening time in HH:MM format
            end_time: Closing time in HH:MM format
            slot_duration: Optional slot duration in minutes
            is_active: Whether this availability is active
        """
        data: dict[str, Any] = {
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time,
            "is_active": is_active
        }
        if slot_duration is not None:
            data["slot_duration"] = slot_duration
        return await self._request("POST", "/schedule/availability", json=data)

    async def delete_availability(self, availability_id: int) -> dict:
        """Delete an availability slot."""
        return await self._request("DELETE", f"/schedule/availability/{availability_id}")

    async def get_schedule_exceptions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        exception_type: Optional[str] = None
    ) -> dict:
        """Get availability exceptions (blocked time, extra availability).

        Args:
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)
            exception_type: Filter by 'block' or 'available'
        """
        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if exception_type:
            params["exception_type"] = exception_type
        return await self._request("GET", "/schedule/exceptions", params=params if params else None)

    async def create_schedule_exception(
        self,
        exception_type: str,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        reason: Optional[str] = None
    ) -> list:
        """Create an availability exception to block time or add extra availability.

        Args:
            exception_type: 'block' for vacation/break, 'available' for extra hours
            date: Single date (YYYY-MM-DD)
            start_date: Start of date range (YYYY-MM-DD)
            end_date: End of date range (YYYY-MM-DD)
            start_time: Start time (HH:MM) - leave empty for all day
            end_time: End time (HH:MM) - leave empty for all day
            reason: Optional reason (e.g., 'Vacation', 'Lunch break')
        """
        data: dict[str, Any] = {"exception_type": exception_type}
        if date:
            data["date"] = date
        if start_date:
            data["start_date"] = start_date
        if end_date:
            data["end_date"] = end_date
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time
        if reason:
            data["reason"] = reason
        return await self._request("POST", "/schedule/exceptions", json=data)

    async def delete_schedule_exception(self, exception_id: int) -> dict:
        """Delete an availability exception."""
        return await self._request("DELETE", f"/schedule/exceptions/{exception_id}")
