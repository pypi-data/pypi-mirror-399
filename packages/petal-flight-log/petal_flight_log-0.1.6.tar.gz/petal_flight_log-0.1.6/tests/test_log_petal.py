from __future__ import annotations
import asyncio, sys, time, uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, AsyncMock
from petal_flight_log.plugin import FlightLogPetal
from petal_app_manager.proxies.localdb import LocalDBProxy

from fastapi import HTTPException

import pytest

@pytest.fixture
def mock_db_proxy():
    """Create a mock database proxy for testing."""
    mock_proxy = AsyncMock()
    
    # Setup default attributes
    mock_proxy.organization_id = "test-org-id"
    mock_proxy.machine_id = "test-machine-id"
    mock_proxy.robot_type_id = "test-robot-type-id"
    
    # Setup default return values for the DB methods
    mock_proxy.scan_items.return_value = {"data": []}
    mock_proxy.set_item.return_value = {"data": {"body": "{}"}}
    mock_proxy.update_item.return_value = {"success": True}
    
    return mock_proxy


@pytest.fixture
def flight_petal(mock_db_proxy: LocalDBProxy):
    """Create a petal instance with mocked proxies."""
    petal = FlightLogPetal()
    # Inject the mock proxy
    petal._proxies = {"db": mock_db_proxy}
    return petal


class TestFlightRecordPetal:
    
    @pytest.mark.asyncio
    async def test_get_flight_records(self, flight_petal: FlightLogPetal, mock_db_proxy: LocalDBProxy):
        """Test retrieving flight records."""
        # Setup mock return data
        mock_records = [
            {"id": "record1", "organization_id": "test-org-id", "flight_data": "data1"},
            {"id": "record2", "organization_id": "test-org-id", "flight_data": "data2"}
        ]
        mock_db_proxy.scan_items.return_value = {"data": mock_records}
        
        # Call the action
        result = await flight_petal.get_flight_records()
        
        # Verify the DB was queried correctly
        mock_db_proxy.scan_items.assert_called_once_with(
            "config-log-flight_record", 
            [{"filter_key_name": "organization_id", "filter_key_value": "test-org-id"}]
        )
        
        # Verify the result
        assert result == {"flight_records": mock_records}
    
    @pytest.mark.asyncio
    @patch("petal_flight_log.plugin.uuid.uuid4")
    async def test_save_flight_record(self, mock_uuid, flight_petal: FlightLogPetal, mock_db_proxy: LocalDBProxy):
        """Test saving a new flight record."""
        # Setup mock UUID
        mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
        expected_id = "12345678-1234-5678-1234-567812345678"
        
        # Setup mock to return successful save
        mock_db_proxy.set_item.return_value = {"data": {"body": "{}"}}
        
        # Test data - using the actual FlightRecordInput model
        from petal_flight_log.plugin import FlightRecordInput
        record_data = FlightRecordInput(
            name="Test Flight",
            pilot_name="Test Pilot",
            takeoff_date="2025-12-31",
            takeoff_time="12:00:00",
            time_zone="UTC",
            takeoff_utc_timestamp=1735646400,
            flight_duration=15.5,
            organization_id="test-org-id"
        )
        
        # Call the action
        result = await flight_petal.save_flight_record(record_data=record_data)
        
        # Verify the record was saved
        assert mock_db_proxy.set_item.called
        assert mock_db_proxy.set_item.call_count == 1
        
        # Verify the result
        assert result == {"success": True, "record_id": expected_id}
    
    @pytest.mark.asyncio
    async def test_get_flight_records_empty(self, flight_petal: FlightLogPetal, mock_db_proxy: LocalDBProxy):
        """Test retrieving flight records when none exist."""
        # Setup mock to return empty list
        mock_db_proxy.scan_items.return_value = {"data": []}
        
        # Expect the HTTPException to be raised
        with pytest.raises(HTTPException) as excinfo:
            await flight_petal.get_flight_records()
        
        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "No flight records found"
        assert excinfo.value.headers == {"source": "get_flight_records"}

    @pytest.mark.asyncio
    async def test_save_flight_record_db_error(self, flight_petal: FlightLogPetal, mock_db_proxy: LocalDBProxy):
        """Test error handling when saving a flight record fails."""
        # Setup mock to simulate DB error in the response
        mock_db_proxy.set_item.return_value = {
            "data": {"body": '{"error": "Database error"}'}
        }
        
        # Test data - using the actual FlightRecordInput model
        from petal_flight_log.plugin import FlightRecordInput
        record_data = FlightRecordInput(
            name="Test Flight",
            pilot_name="Test Pilot",
            takeoff_date="2025-12-31",
            takeoff_time="12:00:00",
            time_zone="UTC",
            takeoff_utc_timestamp=1735646400,
            flight_duration=15.5,
            organization_id="test-org-id"
        )
        
        # Verify HTTPException is raised with the error
        with pytest.raises(HTTPException) as exc_info:
            await flight_petal.save_flight_record(record_data=record_data)
        
        # Verify the exception details
        assert exc_info.value.status_code == 500
        assert "Failed to save flight record" in exc_info.value.detail