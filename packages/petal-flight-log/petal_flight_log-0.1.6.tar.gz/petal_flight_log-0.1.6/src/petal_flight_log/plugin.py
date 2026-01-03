import uuid
import os
from pathlib import Path
import json
from datetime import datetime, date
import time
from typing import Dict, Any, List, Optional, Union, Callable
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Response
from pymavlink import mavutil, mavftp
from . import logger
import threading

from petal_app_manager.plugins.base import Petal
from petal_app_manager.plugins.decorators import http_action, websocket_action
from petal_app_manager.proxies import (
    S3BucketProxy,
    MavLinkExternalProxy,
    MavLinkFTPProxy,
    RedisProxy,
    LocalDBProxy,
    CloudDBProxy
)

from pydantic import BaseModel, Field, field_validator

# Global progress state and client set
download_progress_state = {}
active_downloads = {} # To track active downloads
last_progress_values = {} # To track previous progress values
last_progress_times = {} # To track when progress was last updated
websocket_clients = set()

class FileMetadata(BaseModel):
    """Base metadata for flight log files"""
    id: Optional[str] = Field(None, description="File ID (auto-generated if missing)")
    file_path: str = Field(..., description="Path to the file")
    storage_type: str = Field(..., description="Type of storage (e.g., local, pixhawk)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the file")
    file_type: Optional[str] = Field(None, description="Type of file")
    file_name: Optional[str] = Field(None, description="Name of the file")
    deleted: bool = Field(False, description="Whether the file is marked as deleted")

    @field_validator('id', mode='before')
    @classmethod
    def default_id(cls, v):
        return v or str(uuid.uuid4())
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                "file_path": "/home/khalil/ulog_records/log_44_2025-02-16-12-17-22.ulg",
                "file_name": "log_44_2025-02-16-12-17-22.ulg",
                "storage_type": "local",
                "file_type": "ulg",
                "deleted": False,
                "metadata": {
                    "date": "2025-02-16-12-17-22",
                    "timestamp": 1718593200,
                    "size_bytes": 1048576,
                    "size_kb": 1024,
                    "qgc_name": "log_44_2025-02-16-12-17-22.ulg"
                }
            }
        }
    }

class FlightRecordBase(BaseModel):
    """Base fields for flight records"""
    name: str = Field(..., description="Flight name")
    pilot_name: str = Field(..., description="Name of the pilot")
    takeoff_date: str = Field(..., description="Date of takeoff (YYYY-MM-DD)")
    takeoff_time: str = Field(..., description="Time of takeoff (HH:MM:SS)")
    time_zone: str = Field(..., description="Timezone of the flight")
    takeoff_utc_timestamp: int = Field(..., description="UTC timestamp of the flight start")
    flight_duration: float = Field(..., ge=0, description="Duration of flight in minutes")
    
    # Optional battery-related fields
    battery_before: Optional[float] = Field(None, ge=0, le=100, description="Battery percentage before flight")
    battery_after: Optional[float] = Field(None, ge=0, le=100, description="Battery percentage after flight")
    battery_before_secondary: Optional[float] = Field(None, ge=0, le=100, description="Secondary battery percentage before flight")
    battery_after_secondary: Optional[float] = Field(None, ge=0, le=100, description="Secondary battery percentage after flight")
    
    # Notes fields
    purpose: Optional[str] = Field(None, description="Purpose of the flight")
    post_landing_notes: Optional[str] = Field(None, description="Notes recorded after landing")
    
    # Validation methods
    @field_validator('takeoff_date')
    @classmethod
    def validate_date(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    @field_validator('takeoff_time')
    @classmethod
    def validate_time(cls, value):
        try:
            datetime.strptime(value, "%H:%M:%S")
            return value
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM:SS")

class FlightRecordInput(FlightRecordBase):
    """Flight record input model"""
    # File paths and IDs
    local_rosbag_path: Optional[str] = Field(None, description="Local path to ROS bag file (not stored)")
    local_ulog_path: Optional[str] = Field(None, description="Local path to ULog file (not stored)")

    # Metadata objects for file storage
    rosbag_metadata: Optional[FileMetadata] = Field(None, description="Metadata for ROS bag file")
    ulog_metadata: Optional[FileMetadata] = Field(None, description="Metadata for ULog file")
    
    # Other optional fields that might be set by client
    address: Optional[str] = Field(None, description="Address identifier (defaults to machine ID)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Test Flight 1",
                "pilot_name": "John Doe",
                "takeoff_date": "2025-06-16",
                "takeoff_time": "14:30:00",
                "time_zone": "UTC",
                "takeoff_utc_timestamp": 1718593200,
                "flight_duration": 15.5,
                "battery_before": 100,
                "battery_after": 60,
                "secondary_battery_before": 90,
                "secondary_battery_after": 50,
                "purpose": "Functional test",
                "post_landing_notes": "Smooth landing, no issues",
                "local_rosbag_path": "/home/khalil/rosbag_records/flight1.bag",
                "rosbag_metadata": {
                    "file_path": "/home/khalil/rosbag_records/flight1.bag",
                    "file_name": "flight1.bag",
                    "storage_type": "local",
                    "file_type": "bag",
                    "deleted": False,
                    "metadata": {
                        "date": "2025-06-16-14-30-00",
                        "timestamp": 1718593200,
                        "size_bytes": 1048576,
                    }
                },
                "local_ulog_path": "/home/khalil/ulog_records/log_44_2025-06-16-14-30-00.ulg",
                "ulog_metadata": {
                    "file_path": "/home/khalil/ulog_records/log_44_2025-06-16-14-30-00.ulg",
                    "file_name": "log_44_2025-06-16-14-30-00.ulg",
                    "storage_type": "local",
                    "file_type": "ulg",
                    "deleted": False,
                    "metadata": {
                        "date": "2025-06-16-14-30-00",
                        "timestamp": 1718593200,
                        "size_bytes": 2048576,
                        "qgc_name": "log_44_2025-06-16-14-30-00.ulg"
                    }
                }
            }
        }
    }

class FlightRecord(FlightRecordBase):
    """Complete flight record as stored in the database"""
    id: str = Field(..., description="Unique identifier for the flight record")
    organization_id: str = Field(..., description="Organization ID this record belongs to")
    robot_instance_id: Optional[str] = Field(None, description="Robot instance ID")
    robot_type_id: Optional[str] = Field(None, description="Robot type ID")
    address: Optional[str] = Field(None, description="Address identifier")
    deleted: bool = Field(False, description="Whether this record is deleted")
    
    # File reference IDs
    rosbag_id: Optional[str] = Field(None, description="ID of associated ROS bag file")
    ulog_id: Optional[str] = Field(None, description="ID of associated ULog file")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "organization_id": "org-123",
                "robot_instance_id": "robot-456",
                "robot_type_id": "type-789",
                "name": "Test Flight 1",
                "pilot_name": "John Doe",
                "takeoff_date": "2025-06-16",
                "takeoff_time": "14:30:00",
                "time_zone": "UTC",
                "flight_duration": 15.5,
                "battery_before": 100,
                "battery_after": 60,
                "purpose": "Functional test",
                "post_landing_notes": "Smooth landing, no issues",
                "rosbag_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                "deleted": False,
                "metadata": {
                    "timestamp": 1718593200,
                    "date": "2025-06-16-14-30-00"
                }
            }
        }
    }

class FlightRecordsResponse(BaseModel):
    """Response for retrieving multiple flight records"""
    flight_records: List[FlightRecord] = Field(..., description="List of flight records")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "flight_records": [
                    {
                        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                        "organization_id": "org-123",
                        "name": "Morning Test Flight",
                        "pilot_name": "John Doe",
                        "takeoff_date": "2025-06-16",
                        "takeoff_time": "14:30:00",
                        "takeoff_utc_timestamp": 1718593200,
                        "time_zone": "UTC",
                        "flight_duration": 15.5,
                        "battery_before": 100,
                        "battery_after": 60,
                        "purpose": "Functional test",
                        "post_landing_notes": "Smooth landing, no issues",
                        "rosbag_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                        "deleted": False,
                        "metadata": {
                            "timestamp": 1718593200,
                            "date": "2025-06-16-14-30-00"
                        }
                    },
                    {
                        "id": "a8b4c16d-39ef-47a0-bc12-345def678901",
                        "organization_id": "org-123",
                        "name": "Afternoon Test Flight",
                        "pilot_name": "Jane Smith",
                        "takeoff_date": "2025-06-16",
                        "takeoff_time": "18:30:00",
                        "takeoff_utc_timestamp": 1718607600,
                        "time_zone": "UTC",
                        "flight_duration": 22.3,
                        "battery_before": 95,
                        "battery_after": 50,
                        "purpose": "Performance test",
                        "post_landing_notes": "Minor issues with landing gear",
                        "ulog_id": "b2c3d4e5-f6a7-8901-abcd-2345678901ef",
                        "deleted": False,
                        "metadata": {
                            "timestamp": 1718607600,
                            "date": "2025-06-16-18-30-00"
                        }
                    }
                ]
            }
        }
    }

class FlightRecordResponse(BaseModel):
    """Response after saving a flight record"""
    success: bool = Field(..., description="Whether the operation was successful")
    record_id: str = Field(..., description="ID of the created flight record")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "record_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
            }
        }
    }

class FlightLogPetal(Petal):
    name = "flight-log-petal"
    version = "1.0.0"


    # helpers
    async def _upload_record_to_cloud(
        self, flight_record_id: str,
        local_db_proxy: LocalDBProxy,
        cloud_proxy: CloudDBProxy,
        bucket_proxy: S3BucketProxy
    ) -> None:
        # Get the flight record from local database
        local_result = await local_db_proxy.get_item(
            table_name="config-log-flight_record",
            partition_key="id",
            partition_value=flight_record_id
        )

        upload_results = {
            "uploaded_files": [],
            "errors": []
        }
        
        if "error" in local_result or not local_result.get("data"):
            logger.error(f"Flight record {flight_record_id} not found in local database")
            raise HTTPException(
                status_code=404,
                detail="Flight record not found in local database",
                headers={"source": "upload_flight_record"}
            )
        
        flight_record = local_result["data"]
        logger.info(f"Retrieved flight record {flight_record_id} from local database")
        
        # Upload the main flight record
        cloud_result = await cloud_proxy.set_item(
            table_name="config-log-flight_record",
            filter_key="id",
            filter_value=flight_record_id,
            data=flight_record
        )
        
        if "error" in cloud_result:
            logger.error(f"Failed to upload flight record to cloud: {cloud_result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload flight record to cloud: {cloud_result['error']}",
                headers={"source": "upload_flight_record"}
            )
        
        # Upload associated RosBag metadata if present
        uploaded_files = []
        if "rosbag_id" in flight_record:
            rosbag_result = await local_db_proxy.get_item(
                table_name="config-log-file_system",
                partition_key="id",
                partition_value=flight_record["rosbag_id"]
            )
            
            if rosbag_result.get("data"):
                # upload robag to S3 bucket
                file_path = Path(rosbag_result["data"].get("file_path"))
                rosbag_bucket_result = await bucket_proxy.upload_file(
                    file_path=file_path
                )

                if "error" in rosbag_bucket_result:
                    logger.warning(f"Failed to upload RosBag file to S3: {rosbag_bucket_result['error']}")
                    rosbag_result["data"]["s3_key"] = None
                    upload_results["errors"].append({
                        "flight_record_id": flight_record_id,
                        "error": f"Failed to upload RosBag file to S3: {rosbag_bucket_result['error']}"
                    })
                else:
                    rosbag_result["data"]["s3_key"] = rosbag_bucket_result.get("s3_key")

                rosbag_cloud_result = await cloud_proxy.set_item(
                    table_name="config-log-file_system",
                    filter_key="id",
                    filter_value=flight_record["rosbag_id"],
                    data=rosbag_result["data"]
                )
                
                if "error" not in rosbag_cloud_result:
                    uploaded_files.append("rosbag_metadata")
                    logger.info(f"Uploaded RosBag metadata {flight_record['rosbag_id']} to cloud")
                else:
                    logger.warning(f"Failed to upload RosBag metadata: {rosbag_cloud_result['error']}")
                    # rollback S3 upload if cloud upload fails
                    if rosbag_bucket_result.get("success"):
                        await bucket_proxy.delete_file(
                            s3_key=rosbag_bucket_result.get("s3_key")
                        )
                    upload_results["errors"].append({
                        "flight_record_id": flight_record_id,
                        "error": f"Failed to upload RosBag metadata: {rosbag_cloud_result['error']}"
                    })
                            
        # Upload associated ULog metadata if present
        if "ulog_id" in flight_record:
            ulog_result = await local_db_proxy.get_item(
                table_name="config-log-file_system",
                partition_key="id",
                partition_value=flight_record["ulog_id"]
            )
            
            if ulog_result.get("data"):
                
                # upload ulog to S3 bucket
                file_path = Path(ulog_result["data"].get("file_path"))
                ulog_bucket_result = await bucket_proxy.upload_file(
                    file_path=file_path
                )

                if "error" in ulog_bucket_result:
                    logger.warning(f"Failed to upload ULog file to S3: {ulog_bucket_result['error']}")
                    ulog_result["data"]["s3_key"] = None
                    upload_results["errors"].append({
                        "flight_record_id": flight_record_id,
                        "error": f"Failed to upload ULog file to S3: {ulog_bucket_result['error']}"
                    })
                else:
                    ulog_result["data"]["s3_key"] = ulog_bucket_result.get("s3_key")

                ulog_cloud_result = await cloud_proxy.set_item(
                    table_name="config-log-file_system",
                    filter_key="id",
                    filter_value=flight_record["ulog_id"],
                    data=ulog_result["data"]
                )
                
                if "error" not in ulog_cloud_result:
                    uploaded_files.append("ulog_metadata")
                    logger.info(f"Uploaded ULog metadata {flight_record['ulog_id']} to cloud")
                else:
                    logger.warning(f"Failed to upload ULog metadata: {ulog_cloud_result['error']}")
                    # rollback S3 upload if cloud upload fails
                    if ulog_bucket_result.get("success"):
                        await bucket_proxy.delete_file(
                            s3_key=ulog_bucket_result.get("s3_key")
                        )
                    upload_results["errors"].append({
                        "flight_record_id": flight_record_id,
                        "error": f"Failed to upload ULog metadata: {ulog_cloud_result['error']}"
                    })

        upload_results["uploaded_files"] = uploaded_files

        logger.info(f"Successfully uploaded flight record {flight_record_id} to cloud with {len(uploaded_files)} associated files")

        return upload_results

    async def _download_flight_record(
        self, flight_record_id: str,
        local_db_proxy: LocalDBProxy,
        cloud_proxy: CloudDBProxy,
    ) -> Dict[str, Any]:
        
        # Get the flight record from cloud database
        cloud_result = await cloud_proxy.get_item(
            table_name="config-log-flight_record",
            partition_key="id",
            partition_value=flight_record_id
        )
        
        if "error" in cloud_result or not cloud_result.get("data"):
            logger.error(f"Flight record {flight_record_id} not found in cloud database")
            raise HTTPException(
                status_code=404,
                detail="Flight record not found in cloud database",
                headers={"source": "download_flight_record"}
            )
        
        flight_record = cloud_result["data"]
        logger.info(f"Retrieved flight record {flight_record_id} from cloud database")
        
        # Download the main flight record to local
        local_result = await local_db_proxy.set_item(
            table_name="config-log-flight_record",
            filter_key="id",
            filter_value=flight_record_id,
            data=flight_record
        )
        
        if "error" in local_result:
            logger.error(f"Failed to save flight record to local database: {local_result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save flight record to local database: {local_result['error']}",
                headers={"source": "download_flight_record"}
            )
        
        # Download associated RosBag metadata if present
        downloaded_files = []
        if "rosbag_id" in flight_record:
            rosbag_cloud_result = await cloud_proxy.get_item(
                table_name="config-log-file_system",
                partition_key="id",
                partition_value=flight_record["rosbag_id"]
            )
            
            if rosbag_cloud_result.get("data"):
                rosbag_local_result = await local_db_proxy.set_item(
                    table_name="config-log-file_system",
                    filter_key="id",
                    filter_value=flight_record["rosbag_id"],
                    data=rosbag_cloud_result["data"]
                )
                
                if "error" not in rosbag_local_result:
                    downloaded_files.append("rosbag_metadata")
                    logger.info(f"Downloaded RosBag metadata {flight_record['rosbag_id']} from cloud")
                else:
                    logger.warning(f"Failed to save RosBag metadata: {rosbag_local_result['error']}")
        
        # Download associated ULog metadata if present
        if "ulog_id" in flight_record:
            ulog_cloud_result = await cloud_proxy.get_item(
                table_name="config-log-file_system",
                partition_key="id",
                partition_value=flight_record["ulog_id"]
            )
            
            if ulog_cloud_result.get("data"):
                ulog_local_result = await local_db_proxy.set_item(
                    table_name="config-log-file_system",
                    filter_key="id",
                    filter_value=flight_record["ulog_id"],
                    data=ulog_cloud_result["data"]
                )
                
                if "error" not in ulog_local_result:
                    downloaded_files.append("ulog_metadata")
                    logger.info(f"Downloaded ULog metadata {flight_record['ulog_id']} from cloud")
                else:
                    logger.warning(f"Failed to save ULog metadata: {ulog_local_result['error']}")
        
        logger.info(f"Successfully downloaded flight record {flight_record_id} from cloud with {len(downloaded_files)} associated files")
        
        return {
            "success": True,
            "message": "Flight record downloaded successfully",
            "flight_record_id": flight_record_id,
            "downloaded_files": downloaded_files
        }

    async def _delete_flight_record(
        self, flight_record_id: str,
        local_db_proxy: LocalDBProxy,
        cloud_proxy: CloudDBProxy,
        bucket_proxy: S3BucketProxy
    ) -> Dict[str, Any]:
        
        if not flight_record_id:
            logger.error("Flight record ID is required for deletion")
            raise HTTPException(
                status_code=400,
                detail="Flight record ID is required for deletion",
                headers={"source": "delete_flight_record"}
            )
        
        # Get the flight record from local database
        local_result = await local_db_proxy.get_item(
            table_name="config-log-flight_record",
            partition_key="id",
            partition_value=flight_record_id
        )

        # Delete the flight record from local database
        local_delete_result = await local_db_proxy.delete_item(
            table_name="config-log-flight_record",
            filter_key="id",
            filter_value=flight_record_id
        )
        if "error" in local_delete_result:
            logger.error(f"Failed to delete flight record from local database: {local_result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete flight record from local database: {local_result['error']}",
                headers={"source": "delete_flight_record"}
            )
        logger.info(f"Flight record {flight_record_id} deleted from local database")
        # Delete the flight record from cloud database
        cloud_delete_result = await cloud_proxy.delete_item(
            table_name="config-log-flight_record",
            filter_key="id",
            filter_value=flight_record_id
        )
        if "error" in cloud_delete_result:
            logger.error(f"Failed to delete flight record from cloud database: {cloud_delete_result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete flight record from cloud database: {cloud_delete_result['error']}",
                headers={"source": "delete_flight_record"}
            )
        logger.info(f"Flight record {flight_record_id} deleted from cloud database")
        # Delete associated RosBag metadata if present
        if "rosbag_id" in local_result.get("data", {}):
            rosbag_id = local_result["data"]["rosbag_id"]
            rosbag_result = await local_db_proxy.delete_item(
                table_name="config-log-file_system",
                filter_key="id",
                filter_value=rosbag_id
            )
            if "error" in rosbag_result:
                logger.error(f"Failed to delete RosBag metadata from local database: {rosbag_result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete RosBag metadata from local database: {rosbag_result['error']}",
                    headers={"source": "delete_flight_record"}
                )
            logger.info(f"RosBag metadata {rosbag_id} deleted from local database")
        # Delete associated ULog metadata if present
        if "ulog_id" in local_result.get("data", {}):
            ulog_id = local_result["data"]["ulog_id"]
            ulog_result = await local_db_proxy.delete_item(
                table_name="config-log-file_system",
                filter_key="id",
                filter_value=ulog_id
            )
            if "error" in ulog_result:
                logger.error(f"Failed to delete ULog metadata from local database: {ulog_result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete ULog metadata from local database: {ulog_result['error']}",
                    headers={"source": "delete_flight_record"}
                )
        logger.info(f"ULog metadata {ulog_id} deleted from local database")
        # Delete associated files from S3 bucket if present
        if "rosbag_id" in local_result.get("data", {}):
            rosbag_id = local_result["data"]["rosbag_id"]
            rosbag_result = await local_db_proxy.get_item(
                table_name="config-log-file_system",
                partition_key="id",
                partition_value=rosbag_id
            )
            if rosbag_result.get("data") and rosbag_result["data"].get("s3_key"):
                s3_key = rosbag_result["data"]["s3_key"]
                s3_delete_result = await bucket_proxy.delete_file(s3_key=s3_key)
                if "error" in s3_delete_result:
                    logger.error(f"Failed to delete RosBag file from S3: {s3_delete_result['error']}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to delete RosBag file from S3: {s3_delete_result['error']}",
                        headers={"source": "delete_flight_record"}
                    )
                logger.info(f"RosBag file {s3_key} deleted from S3 bucket")
        if "ulog_id" in local_result.get("data", {}):
            ulog_id = local_result["data"]["ulog_id"]
            ulog_result = await local_db_proxy.get_item(
                table_name="config-log-file_system",
                partition_key="id",
                partition_value=ulog_id
            )
            if ulog_result.get("data") and ulog_result["data"].get("s3_key"):
                s3_key = ulog_result["data"]["s3_key"]
                s3_delete_result = await bucket_proxy.delete_file(s3_key=s3_key)
                if "error" in s3_delete_result:
                    logger.error(f"Failed to delete ULog file from S3: {s3_delete_result['error']}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to delete ULog file from S3: {s3_delete_result['error']}",
                        headers={"source": "delete_flight_record"}
                    )
                logger.info(f"ULog file {s3_key} deleted from S3 bucket")
        
        return {
            "success": True,
            "message": f"Flight record {flight_record_id} deleted successfully"
        }

    # WebSocket endpoint for progress updates
    @websocket_action(
        path="/ws/download-progress",
        name="WebSocket for download progress updates",
    )
    async def ws_download_progress(self, websocket: WebSocket):
        await websocket.accept()
        websocket_clients.add(websocket)
        try:
            while True:
                await websocket.receive_text()  # Keep the connection alive
        except WebSocketDisconnect:
            websocket_clients.discard(websocket)

    async def get_message(
        self,
        *,
        msg_id: str,
        request_msg: mavutil.mavlink.MAVLink_message,
        timeout: float = 3.0,
    ) -> mavutil.mavlink.MAVLink_message:
        """
        Send *request_msg* and return the **first** packet whose ID equals *msg_id*.
        """
        mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]
        holder: Dict[str, mavutil.mavlink.MAVLink_message] = {}

        def _collector(pkt):
            holder["msg"] = pkt
            return True                     # one packet is enough

        await mavlink_proxy.send_and_wait(
            match_key=msg_id,
            request_msg=request_msg,
            collector=_collector,
            timeout=timeout,
        )
        return holder["msg"]

    # --------------------------------------------------------------------------- #

    @http_action(
        method="GET", 
        path="/flight-records",
        response_model=FlightRecordsResponse,
        summary="Get all flight records",
        description="Retrieves all flight records for the current organization.",
        status_code=200,
        responses={
            200: {
                "description": "Successfully retrieved flight records",
                "model": FlightRecordsResponse
            },
            404: {
                "description": "No flight records found",
                "content": {
                    "application/json": {
                        "example": {"flight_records": []}
                    }
                }
            },
            500: {
                "description": "Server error",
                "content": {
                    "application/json": {
                        "example": {"error": "Failed to retrieve flight records"}
                    }
                }
            }
        }
    )
    async def get_flight_records(self) -> FlightRecordsResponse:
        """Get all flight records from the database."""
        # Access the LocalDBProxy through self._proxies
        db_proxy:LocalDBProxy = self._proxies["db"]
        
        # Scan for flight records
        filters = [
            {"filter_key_name": "organization_id", "filter_key_value": db_proxy.organization_id}
        ]
        result = await db_proxy.scan_items("config-log-flight_record", filters)

        if "error" in result:
            logger.error(f"Failed to retrieve flight records: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve flight records",
                headers={"source": "get_flight_records"},
                extra={"error": result["error"]}
            )
        records = result.get("data", [])

        if not records or len(records) == 0:
            logger.info("No flight records found for organization %s", db_proxy.organization_id)
            # If no records found, return an empty response should raise a 404
            raise HTTPException(
                status_code=404,
                detail="No flight records found",
                headers={"source": "get_flight_records"}
            )
        
        # Sort records by timestamp if metadata and timestamp exist, newest to oldest
        def get_timestamp(record):
            try:
                return record.get("metadata", {}).get("timestamp", 0)
            except:
                return 0
                
        records.sort(key=get_timestamp, reverse=True)

        logger.info(f"Retrieved {len(records)} flight records for organization {db_proxy.organization_id}")
        
        # Process and return the records
        return {"flight_records": records}
    
    @http_action(
        method="GET", 
        path="/cloud-flight-records",
        response_model=FlightRecordsResponse,
        summary="Get all flight records from cloud",
        description="Retrieves all flight records for the current organization from the cloud database.",
        status_code=200,
        responses={
            200: {
                "description": "Successfully retrieved flight records from cloud",
                "model": FlightRecordsResponse
            },
            404: {
                "description": "No flight records found in cloud",
                "content": {
                    "application/json": {
                        "example": {"flight_records": []}
                    }
                }
            },
            500: {
                "description": "Server error or cloud authentication failed",
                "content": {
                    "application/json": {
                        "example": {"error": "Failed to retrieve flight records from cloud"}
                    }
                }
            }
        }
    )
    async def get_cloud_flight_records(self) -> FlightRecordsResponse:
        """Get all flight records from the cloud database."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]

        try:
            # Scan for flight records in the cloud
            filters = [
                {"filter_key_name": "organization_id", "filter_key_value": local_db_proxy.organization_id}
            ]
            result = await cloud_proxy.scan_items(
                table_name="config-log-flight_record", 
                filters=filters
            )

            if "error" in result:
                logger.error(f"Failed to retrieve flight records from cloud: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records from cloud",
                    headers={"source": "get_cloud_flight_records"},
                    extra={"error": result["error"]}
                )
            
            records = result.get("data", [])

            if not records or len(records) == 0:
                logger.info("No flight records found in cloud for organization %s", local_db_proxy.organization_id)
                raise HTTPException(
                    status_code=404,
                    detail="No flight records found in cloud",
                    headers={"source": "get_cloud_flight_records"}
                )
            
            # Sort records by timestamp if metadata and timestamp exist, newest to oldest
            def get_timestamp(record):
                try:
                    return record.get("metadata", {}).get("timestamp", 0)
                except:
                    return 0
                    
            records.sort(key=get_timestamp, reverse=True)

            logger.info(f"Retrieved {len(records)} flight records from cloud for organization {local_db_proxy.organization_id}")
            
            # Process and return the records
            return {"flight_records": records}
                
        except HTTPException as e:
            logger.error(f"HTTP error retrieving cloud flight records: {str(e)}")
            raise

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving cloud flight records: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error retrieving cloud flight records: {str(e)}",
                headers={"source": "get_cloud_flight_records"}
            )
    
    @http_action(
        method="GET", 
        path="/compare-flight-records",
        summary="Compare local and cloud flight records",
        description="Compare flight records between local and cloud databases to identify sync status.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Successfully compared flight records",
                "content": {
                    "application/json": {
                        "example": {
                            "local_count": 10,
                            "cloud_count": 8,
                            "local_only": ["uuid1", "uuid2"],
                            "cloud_only": ["uuid3"],
                            "synced": ["uuid4", "uuid5"],
                            "sync_percentage": 80.0
                        }
                    }
                }
            },
            500: {
                "description": "Server error during comparison",
                "content": {
                    "application/json": {
                        "example": {"error": "Failed to compare flight records"}
                    }
                }
            }
        }
    )
    async def compare_flight_records(self) -> Dict[str, Any]:
        """Compare flight records between local and cloud databases."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]

        try:
            # Get local flight records
            filters = [
                {"filter_key_name": "organization_id", "filter_key_value": local_db_proxy.organization_id}
            ]
            local_result = await local_db_proxy.scan_items("config-log-flight_record", filters)
            
            if "error" in local_result:
                logger.error(f"Failed to retrieve local flight records: {local_result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve local flight records",
                    headers={"source": "compare_flight_records"}
                )
            
            local_records = local_result.get("data", [])
            local_ids = {record.get("id") for record in local_records if record.get("id")}
            
            cloud_result = await cloud_proxy.scan_items(
                table_name="config-log-flight_record", 
                filters=filters
            )
            
            if "error" in cloud_result:
                logger.warning(f"Failed to retrieve cloud flight records: {cloud_result['error']}")
                cloud_records = []
            else:
                cloud_records = cloud_result.get("data", [])
            
            cloud_ids = {record.get("id") for record in cloud_records if record.get("id")}
            
            # Compare the sets
            local_only = list(local_ids - cloud_ids)
            cloud_only = list(cloud_ids - local_ids)
            synced = list(local_ids & cloud_ids)
            
            # Calculate sync percentage
            total_unique = len(local_ids | cloud_ids)
            sync_percentage = (len(synced) / total_unique * 100) if total_unique > 0 else 100.0
            
            logger.info(f"Flight record comparison: {len(local_records)} local, {len(cloud_records)} cloud, {len(synced)} synced")
            
            return {
                "local_count": len(local_records),
                "cloud_count": len(cloud_records),
                "local_only": local_only,
                "cloud_only": cloud_only,
                "synced": synced,
                "sync_percentage": round(sync_percentage, 2),
                "total_unique_records": total_unique,
                "needs_sync": len(local_only) > 0 or len(cloud_only) > 0
            }

                
        except HTTPException:
            logger.error(f"HTTP error comparing flight records: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error comparing flight records: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error comparing flight records: {str(e)}",
                headers={"source": "compare_flight_records"}
            )
    
    @http_action(
        method="POST", 
        path="/download-flight-record",
        summary="Download flight record from cloud to local",
        description="Download a flight record from cloud database to local database.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Flight record successfully downloaded from cloud",
                "content": {
                    "application/json": {
                        "example": {"success": True, "message": "Flight record downloaded successfully"}
                    }
                }
            },
            404: {
                "description": "Flight record not found in cloud",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Flight record not found in cloud"}
                    }
                }
            },
            500: {
                "description": "Server error during download",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to download flight record"}
                    }
                }
            }
        }
    )
    async def download_flight_record(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Download a flight record from cloud database to local database."""

        flight_record_id = data.get("flight_record_id")
        if not flight_record_id:
            logger.error("Flight record ID is required")
            raise HTTPException(
                status_code=400,
                detail="Flight record ID is required",
                headers={"source": "download_flight_record"}
            )
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        local_db_proxy: LocalDBProxy = self._proxies["db"]   

        try:
            result = await self._download_flight_record(
                flight_record_id=flight_record_id,
                local_db_proxy=local_db_proxy,
                cloud_proxy=cloud_proxy
            )
            
            return {
                "success": True,
                "message": "Flight record downloaded successfully",
                "flight_record_id": flight_record_id,
                "downloaded_files": result.get("downloaded_files", [])
            }
                
        except HTTPException:
            logger.error(f"HTTP error downloading flight record {flight_record_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading flight record {flight_record_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error downloading flight record: {str(e)}",
                headers={"source": "download_flight_record"}
            )
    
    @http_action(
        method="POST", 
        path="/save-record",
        summary="Save flight record",
        description="Save a new flight record to the database.",
        response_model=FlightRecordResponse,
        status_code=201,
        responses={
            201: {
                "description": "Flight record successfully created",
                "model": FlightRecordResponse
            },
            500: {
                "description": "Server error during record creation",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to save flight record"}
                    }
                }
            }
        }
    )
    async def save_flight_record(self, record_data: FlightRecordInput) -> FlightRecordResponse:
        """Save a new flight record to the database."""
        db_proxy: LocalDBProxy = self._proxies["db"]
        
        # Generate a unique ID for the record
        record_id = str(uuid.uuid4())

        # copy record_data to a dictionary
        if hasattr(record_data, 'model_dump'):
            record_data = record_data.model_dump(exclude_unset=True, by_alias=True)

        # Add required fields
        record_data["id"] = record_id

        # Check for organization_id, robot_instance_id, robot_type_id
        if "organization_id" not in record_data:
            record_data["organization_id"] = db_proxy.organization_id
        
        if "robot_instance_id" not in record_data:
            record_data["robot_instance_id"] = db_proxy.machine_id
            
        if "robot_type_id" not in record_data:
            record_data["robot_type_id"] = db_proxy.robot_type_id
            
        if "address" not in record_data:
            record_data["address"] = db_proxy.machine_id
            
        if "deleted" not in record_data:
            record_data["deleted"] = False
            
        # Add timestamp and date
        if "metadata" not in record_data:
            record_data["metadata"] = {}
            
        timestamp = int(datetime.now().timestamp())
        record_data["metadata"]["timestamp"] = timestamp
        record_data["metadata"]["date"] = datetime.fromtimestamp(timestamp).isoformat().replace(':', '-').replace('T', '-').split('.')[0]

        # Handle special fields - rosbag_metadata and ulog_metadata
        if "rosbag_metadata" in record_data:
            rosbag_data = record_data.pop("rosbag_metadata")
            rosbag_data["id"] = str(uuid.uuid4())
            result = await db_proxy.set_item(
                "config-log-file_system",
                "id",
                rosbag_data["id"],
                rosbag_data
            )
            body = json.loads(result.get("data", {}).get("body", "{}"))
            if "error" in body:
                logger.error(f"Failed to save ROS bag metadata: {body['error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save ROS bag metadata - {body['error']}",
                    headers={"source": "save_flight_record"},
                )

            record_data["rosbag_id"] = rosbag_data["id"]
        
        if "ulog_metadata" in record_data:
            ulog_data = record_data.pop("ulog_metadata")
            ulog_data["id"] = str(uuid.uuid4())
            result = await db_proxy.set_item(
                "config-log-file_system",
                "id",
                ulog_data["id"],
                ulog_data
            )
            body = json.loads(result.get("data", {}).get("body", "{}"))
            if "error" in body:
                logger.error(f"Failed to save ULog metadata: {body['error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save ULog metadata - {body['error']}",
                    headers={"source": "save_flight_record"},
                )

            record_data["ulog_id"] = ulog_data["id"]
            
        # Remove local paths if present
        record_data.pop("local_rosbag_path", None)
        record_data.pop("local_ulog_path", None)
        
        # Save the record
        result = await db_proxy.set_item(
            "config-log-flight_record",
            "id",
            record_id,
            record_data
        )
        body = json.loads(result.get("data", {}).get("body", "{}"))
        if "error" in body:
            logger.error(f"Failed to save flight record: {body['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save flight record - {body['error']}",
                headers={"source": "save_flight_record"},
            )
        
        logger.info(f"Flight record {record_id} saved successfully for organization {db_proxy.organization_id}")
        return {"success": True, "record_id": record_id}

    @http_action(
        method="POST", 
        path="/upload-flight-record",
        summary="Upload flight record to cloud",
        description="Upload a flight record from local database to cloud database.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Flight record successfully uploaded to cloud",
                "content": {
                    "application/json": {
                        "example": {"success": True, "message": "Flight record uploaded successfully"}
                    }
                }
            },
            404: {
                "description": "Flight record not found",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Flight record not found"}
                    }
                }
            },
            500: {
                "description": "Server error during upload",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to upload flight record"}
                    }
                }
            }
        }
    )
    async def upload_flight_record(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Upload a flight record from local database to cloud database."""
        
        flight_record_id = data.get("flight_record_id")
        if not flight_record_id:
            logger.error("Flight record ID is required")
            raise HTTPException(
                status_code=400,
                detail="Flight record ID is required",
                headers={"source": "upload_flight_record"}
            )
        
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        bucket_proxy: S3BucketProxy = self._proxies["bucket"]

        try:
            
            result = await self._upload_record_to_cloud(
                    flight_record_id=flight_record_id,
                    local_db_proxy=local_db_proxy,
                    cloud_proxy=cloud_proxy,
                    bucket_proxy=bucket_proxy
                )
            
            return {
                "success": True,
                "message": "Flight record uploaded successfully",
                "flight_record_id": flight_record_id,
                "uploaded_files": result["uploaded_files"],
            }
                
        except HTTPException:
            logger.error(f"HTTP error uploading flight record {flight_record_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading flight record {flight_record_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error uploading flight record: {str(e)}",
                headers={"source": "upload_flight_record"}
            )
    
    @http_action(
        method="POST", 
        path="/upload-all-flight-records",
        summary="Upload all flight records to cloud",
        description="Upload all flight records from local database to cloud database.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Flight records upload completed",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True, 
                            "uploaded_count": 5,
                            "failed_count": 1,
                            "results": []
                        }
                    }
                }
            },
            500: {
                "description": "Server error during upload",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to upload flight records"}
                    }
                }
            }
        }
    )
    async def upload_all_flight_records(self) -> Dict[str, Any]:
        """Upload all flight records from local database to cloud database."""
        
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        bucket_proxy: S3BucketProxy = self._proxies["bucket"]

        try:
            # Get all flight records from local database
            filters = [
                {"filter_key_name": "organization_id", "filter_key_value": local_db_proxy.organization_id}
            ]
            local_result = await local_db_proxy.scan_items("config-log-flight_record", filters)
            
            if "error" in local_result:
                logger.error(f"Failed to retrieve flight records from local database: {local_result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records from local database",
                    headers={"source": "upload_all_flight_records"}
                )
            
            flight_records = local_result.get("data", [])
            
            if not flight_records:
                logger.info("No flight records found to upload")
                return {
                    "success": True,
                    "message": "No flight records found to upload",
                    "uploaded_count": 0,
                    "failed_count": 0,
                    "results": []
                }
            
            logger.info(f"Found {len(flight_records)} flight records to upload")
            
            upload_results = []
            uploaded_count = 0
            failed_count = 0
            
            for flight_record in flight_records:
                flight_record_id = flight_record.get("id")
                if not flight_record_id:
                    failed_count += 1
                    upload_results.append({
                        "flight_record_id": None,
                        "success": False,
                        "error": "Flight record missing ID"
                    })
                    continue
                
                try:
                    
                    result = await self._upload_record_to_cloud(
                        flight_record_id=flight_record_id,
                        local_db_proxy=local_db_proxy,
                        cloud_proxy=cloud_proxy,
                        bucket_proxy=bucket_proxy
                    )

                    uploaded_count += 1
                    upload_results.append({
                        "flight_record_id": flight_record_id,
                        "success": True,
                        "uploaded_files": result["uploaded_files"]
                    })
                    
                    logger.info(f"Successfully uploaded flight record {flight_record_id}")
                    
                except Exception as e:
                    failed_count += 1
                    upload_results.append({
                        "flight_record_id": flight_record_id,
                        "success": False,
                        "error": f"Unexpected error: {str(e)}"
                    })
                    logger.error(f"Error uploading flight record {flight_record_id}: {str(e)}")
            
            logger.info(f"Upload completed: {uploaded_count} successful, {failed_count} failed")
            
            return {
                "success": True,
                "message": f"Upload completed: {uploaded_count} successful, {failed_count} failed",
                "uploaded_count": uploaded_count,
                "failed_count": failed_count,
                "results": upload_results
            }
                
        except HTTPException:
            logger.error("HTTPException occurred during upload_all_flight_records")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading all flight records: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error uploading flight records: {str(e)}",
                headers={"source": "upload_all_flight_records"}
            )

    @http_action(
        method="DELETE",
        path="/delete-flight-record",
        summary="Delete flight record",
        description="Delete a flight record from the database.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Flight record successfully deleted",
                "content": {
                    "application/json": {
                        "example": {"success": True, "message": "Flight record deleted successfully"}
                    }
                }
            },
            404: {
                "description": "Flight record not found",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Flight record not found"}
                    }
                }
            },
            500: {
                "description": "Server error during deletion",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to delete flight record"}
                    }
                }
            }
        }
    )
    async def delete_flight_record(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Delete a flight record from the database."""
        flight_record_id = data.get("flight_record_id")
        if not flight_record_id:
            logger.error("Flight record ID is required for deletion")
            raise HTTPException(
                status_code=400,
                detail="Flight record ID is required for deletion",
                headers={"source": "delete_flight_record"}
            )
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        bucket_proxy: S3BucketProxy = self._proxies["bucket"]
        try:
            
            # Delete the flight record from local database
            result = await self._delete_flight_record(
                flight_record_id=flight_record_id,
                local_db_proxy=local_db_proxy,
                cloud_proxy=cloud_proxy,
                bucket_proxy=bucket_proxy
            )

            return {
                "success": True,
                "message": f"Flight record {flight_record_id} deleted successfully",
                "flight_record_id": flight_record_id
            }

        except HTTPException as e:
            logger.error(f"HTTP error deleting flight record {flight_record_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting flight record {flight_record_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error deleting flight record: {str(e)}",
                headers={"source": "delete_flight_record"}
            )

    @http_action(
        method="DELETE",
        path="/delete-all-flight-records",
        summary="Delete all flight records",
        description="Delete all flight records from the database.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "All flight records successfully deleted",
                "content": {
                    "application/json": {
                        "example": {"success": True, "message": "All flight records deleted successfully"}
                    }
                }
            },
            500: {
                "description": "Server error during deletion",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to delete flight records"}
                    }
                }
            }
        }
    )
    async def delete_all_flight_records(self) -> Dict[str, Any]:
        """Delete all flight records from the database."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        bucket_proxy: S3BucketProxy = self._proxies["bucket"]

        try:
            # Get all flight records from local database
            filters = [
                {"filter_key_name": "organization_id", "filter_key_value": local_db_proxy.organization_id}
            ]
            local_result = await local_db_proxy.scan_items("config-log-flight_record", filters)
            if "error" in local_result:
                logger.error(f"Failed to retrieve flight records from local database: {local_result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records from local database",
                    headers={"source": "delete_all_flight_records"}
                )
            flight_records = local_result.get("data", [])
            if not flight_records:
                logger.info("No flight records found to delete")
                return {
                    "success": True,
                    "message": "No flight records found to delete",
                    "deleted_count": 0
                }
            logger.info(f"Found {len(flight_records)} flight records to delete")
            deleted_count = 0
            for flight_record in flight_records:
                flight_record_id = flight_record.get("id")
                if not flight_record_id:
                    logger.warning("Flight record missing ID, skipping deletion")
                    continue
                try:
                    result = await self._delete_flight_record(
                        flight_record_id=flight_record_id,
                        local_db_proxy=local_db_proxy,
                        cloud_proxy=cloud_proxy,
                        bucket_proxy=bucket_proxy
                    )
                    deleted_count += 1
                    logger.info(f"Successfully deleted flight record {flight_record_id}")
                except Exception as e:
                    logger.error(f"Error deleting flight record {flight_record_id}: {str(e)}")
                    continue
            logger.info(f"Deletion completed: {deleted_count} flight records deleted")
            return {
                "success": True,
                "message": f"Deletion completed: {deleted_count} flight records deleted",
                "deleted_count": deleted_count
            }
        except HTTPException as e:
            logger.error(f"HTTPException occurred during delete_all_flight_records: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting all flight records: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error deleting flight records: {str(e)}",
                headers={"source": "delete_all_flight_records"}
            )

    @http_action(method="POST", path="/available-px4-ulogs")
    async def get_available_px4_ulogs(self, data: Dict[str, str] = None):
        """List available PX4 ULog files."""
        db_proxy: LocalDBProxy = self._proxies["db"]
        mavlink_proxy: MavLinkFTPProxy = self._proxies["ftp_mavlink"]
        redis_proxy: RedisProxy = self._proxies["redis"]

        # Get organization_id and machine_id
        organization_id = db_proxy.organization_id
        machine_id = db_proxy.machine_id
        robot_type_id = db_proxy.robot_type_id

        if data is not None and "base" in data:
            base = data['base']
        else:
            base = None # defaults to default sd log path

        # Get ULog files from PX4 using MavLinkProxy
        ulog_files = await mavlink_proxy.list_ulogs(base=base)
        
        # Convert to the expected format
        log_records = []
        for file in ulog_files:
            # Convert UTC timestamp to formatted date
            timestamp = file.utc
            est_timestamp = timestamp - (5 * 3600)  # Subtract 5 hours in seconds
            dt = datetime.fromtimestamp(est_timestamp)
            date = dt.isoformat().replace('-', '-').replace(':', '-').replace('T', '-').split('.')[0]            
            index = file.index

            # Create record with metadata
            item = {
                "id": str(uuid.uuid4()),
                "robot_instance_id": db_proxy.machine_id,
                "robot_type_id": db_proxy.robot_type_id,
                "organization_id": db_proxy.organization_id,
                "address": db_proxy.machine_id,
                "file_name": os.path.basename(file.remote_path),
                "file_path": file.remote_path,
                "file_type": "ulg",
                "storage_type": "pixhawk",
                "deleted": False,
                "metadata": {
                    "index": file.index,
                    "date": date,
                    "size_bytes": file.size_bytes,
                    "size_kb": round(file.size_bytes / 1024, 2),
                    "timestamp": timestamp,
                    "qgc_name": f"log_{index}_{date}.ulg"  # QGroundControl compatible name
                }
            }
            log_records.append(item)
        
        # Sort records by timestamp (newest first)
        log_records.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)

        # store the records in the redis database
        redis_key = f"px4_ulogs:{machine_id}"
        await redis_proxy.set(redis_key, json.dumps(log_records))

        logger.info(f"Found {len(log_records)} PX4 ULog files for machine {machine_id} in organization {organization_id}")
            
        return {"px4_ulogs": log_records}
    
    @http_action(method="GET", path="/available-ulogs")
    async def get_available_local_ulogs(self):
        """List available local ULog files."""
        try:
            # Define the directory where ULog files are stored
            db_proxy: LocalDBProxy = self._proxies["db"]
            redis_proxy: RedisProxy = self._proxies["redis"]
            home_dir = os.path.expanduser("~")
            local_dir = os.path.join(home_dir, "ulog_records")
            
            # Get the PX4 ULog files data from Redis
            ulog_files = []
            px4_ulogs = await redis_proxy.get(f"px4_ulogs:{db_proxy.machine_id}")
            if px4_ulogs:
                px4_ulogs = json.loads(px4_ulogs)
            else:
                px4_ulogs = []

            # Make sure the directory exists
            if os.path.exists(local_dir):
                for filename in os.listdir(local_dir):
                    if filename.endswith(".ulg"):
                        file_path = os.path.join(local_dir, filename)
                        
                        # Try to find matching file in PX4 ULogs by QGC name
                        file_data = next((file for file in px4_ulogs 
                                        if file.get("metadata", {}).get("qgc_name") == filename), None)
                        
                        if not file_data:
                            logger.warning(f"File {filename} not found in the database")
                            continue
                        
                        # Copy and update the file data
                        file_data = file_data.copy()  # Create a copy to avoid modifying original
                        file_data["file_path"] = file_path
                        file_data["file_name"] = filename
                        file_data["storage_type"] = "local"
                        
                        ulog_files.append(file_data)
            
            logger.info(f"Stored {len(ulog_files)} ULog files in memory")
            
            # Sort records by timestamp (newest first)
            ulog_files.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)
            
            # Store the records in the redis database
            redis_key = f"local_ulogs:{db_proxy.machine_id}"
            await redis_proxy.set(redis_key, json.dumps(ulog_files))

            logger.info(f"Found {len(ulog_files)} local ULog files in {local_dir}")

            return {"local_ulogs": ulog_files}
            
        except Exception as error:
            logger.error(f"Error parsing ULog list output: {error}")
            raise HTTPException(
                status_code=500,
                detail="Error parsing ULog list output",
                headers={"source": "get_available_local_ulogs"}
            )
    
    @http_action(method="GET", path="/available-bags")
    async def get_available_rosbags(self):
        """List available local RosBag files."""
        # Define the directory where RosBag files are stored
        db_proxy: LocalDBProxy = self._proxies["db"]
        redis_proxy = self._proxies["redis"]
        home_dir = os.path.expanduser("~")
        local_dir = os.path.join(home_dir, "rosbag_records")
        
        # Get the list of RosBag files recursively
        rosbag_files = []
        
        def find_bag_files_recursively(directory):
            if not os.path.exists(directory):
                return
                
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    # If it's a directory, search inside it
                    find_bag_files_recursively(item_path)
                elif os.path.isfile(item_path) and item.endswith(".bag"):
                    # If it's a bag file, add it to our results
                    stats = os.stat(item_path)
                    
                    # Create record with metadata
                    item = {
                        "id": str(uuid.uuid4()),
                        "robot_instance_id": db_proxy.machine_id,
                        "robot_type_id": db_proxy.robot_type_id,
                        "organization_id": db_proxy.organization_id,
                        "address": db_proxy.machine_id,
                        "file_name": os.path.basename(item_path),
                        "file_path": item_path,
                        "file_type": "bag",
                        "storage_type": "local",
                        "deleted": False,
                        "metadata": {
                            "date": datetime.fromtimestamp(stats.st_mtime).isoformat().replace(':', '-').replace('T', '-').split('.')[0],
                            "size_bytes": stats.st_size,
                            "size_kb": round(stats.st_size / 1024, 2),
                            "timestamp": int(stats.st_mtime)
                        }
                    }
                    rosbag_files.append(item)
        
        # Start the recursive search
        find_bag_files_recursively(local_dir)
        
        # Store the records in the redis database
        redis_key = f"local_rosbags:{db_proxy.machine_id}"
        await redis_proxy.set(redis_key, json.dumps(rosbag_files))

        # Sort records by timestamp (newest first)
        rosbag_files.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)

        logger.info(f"Found {len(rosbag_files)} RosBag files in {local_dir}")
        
        return {"rosbag_files": rosbag_files}

    @http_action(method="GET", path="/download-ulog-pixhawk")
    async def download_ulog_pixhawk(self, file_id: str):
        """Download a ULog file from Pixhawk and broadcast progress."""
        mavlink_proxy: MavLinkFTPProxy = self._proxies["ftp_mavlink"]
        redis_proxy: RedisProxy = self._proxies["redis"]
        db_proxy: LocalDBProxy = self._proxies["db"]

        # Get the ULog file information from the database
        files = await redis_proxy.get(f"px4_ulogs:{db_proxy.machine_id}")
        if not files:
            logger.error(f"No ULog files found for Pixhawk with ID {db_proxy.machine_id}")
            raise HTTPException(
                status_code=404,
                detail="No ULog files found for this Pixhawk",
                headers={"source": "download_ulog_pixhawk"}
            )
        files = json.loads(files)
        # Find the file with the given ID
        result = next((f for f in files if f["id"] == file_id), None)
        if not result:
            logger.error(f"File with ID {file_id} not found in Pixhawk logs")
            raise HTTPException(
                status_code=404,
                detail="File not found in Pixhawk logs",
                headers={"source": "download_ulog_pixhawk"}
            )
        # Check if the file has a valid remote path
        if "file_path" not in result or not result["file_path"]:
            logger.error(f"File metadata not found in Pixhawk logs for file ID {file_id}")
            raise HTTPException(
                status_code=404,
                detail="File metadata not found in Pixhawk logs",
                headers={"source": "download_ulog_pixhawk"}
            )
        # If the file is not a ULog, raise an error
        if result["file_type"] != "ulg":
            logger.error(f"File with ID {file_id} is not a ULog file")
            raise HTTPException(
                status_code=400,
                detail="File is not a ULog",
                headers={"source": "download_ulog_pixhawk"}
            )
        
        remote_path = result.get("file_path")
        if remote_path is None:
            logger.error(f"Remote path for ULog file not found in metadata for file ID {file_id}")
            raise HTTPException(
                status_code=404,
                detail="Remote path for ULog file not found",
                headers={"source": "download_ulog_pixhawk"}
            )

        home_dir = os.path.expanduser("~")
        local_dir = os.path.join(home_dir, "ulog_records")
        os.makedirs(local_dir, exist_ok=True)

        metadata = result.get("metadata", {})
        if not metadata:
            logger.error(f"Metadata for ULog file is missing in file ID {file_id}")
            raise HTTPException(
                status_code=400,
                detail="Metadata for ULog file is missing",
                headers={"source": "download_ulog_pixhawk"}
            )
        remote_path = result.get("file_path")
        timestamp = metadata.get("timestamp")
        date = metadata.get("date")
        index = metadata.get("index")
        size_bytes = metadata.get("size_bytes")

        choice = index
        local_filename = f"log_{choice}_{date}.ulg"
        local_path = os.path.join(local_dir, local_filename)

        download_id = str(uuid.uuid4())
        # Create cancellation event
        cancel_event = threading.Event()
        active_downloads[download_id] = cancel_event
        
        progress_data = {
            "type": "progress",
            "path": remote_path,
            "download_id": download_id,
            "progress": 0,
            "completed": False,
            "rate KB/s": 0 if size_bytes is None else None
        }
        download_progress_state[download_id] = progress_data
        start_time = time.time()

        async def on_progress(progress: float):
            # Check if already cancelled
            if cancel_event.is_set():
                return
            
            current_time = time.time()
            elapsed_total = current_time - start_time
            
            # Calculate current transfer rate using recent interval
            if download_id in last_progress_values and download_id in last_progress_times:
                last_progress = last_progress_values[download_id]
                last_time = last_progress_times[download_id]
                
                # Calculate data transferred since last update
                progress_delta = progress - last_progress
                time_delta = current_time - last_time
                
                # Only update rate if meaningful time has passed (avoid division by very small numbers)
                if time_delta > 0.5:  # Only update rate calculation every half second
                    # Calculate instantaneous rate based on progress since last update
                    current_rate = (progress_delta * size_bytes) / 1024 / time_delta
                    # Use a weighted average to smooth the rate display
                    if "current_rate" in progress_data:
                        # Weighted average: 70% new rate, 30% previous rate
                        progress_data["rate KB/s"] = round(0.7 * current_rate + 0.3 * progress_data["rate KB/s"], 1)
                    else:
                        progress_data["rate KB/s"] = round(current_rate, 1)
                        
                    # Update tracking variables
                    last_progress_values[download_id] = progress
                    last_progress_times[download_id] = current_time
            else:
                # First progress update - initialize tracking
                last_progress_values[download_id] = progress
                last_progress_times[download_id] = current_time
                # Use average rate for first update
                progress_data["rate KB/s"] = round(size_bytes * progress / 1024 / elapsed_total, 1) if size_bytes else None
            
            # Update other progress data
            progress_data["type"] = "progress"
            progress_data["path"] = remote_path
            progress_data["progress"] = round(progress * 100, 1)
            progress_data["completed"] = progress >= 1.0
            
            # Broadcast to all connected WebSocket clients
            for ws in list(websocket_clients):
                try:
                    await ws.send_json(progress_data)
                except Exception:
                    logger.warning(f"Failed to send progress update to WebSocket client: {ws}")
                    websocket_clients.discard(ws)

        try:
            result = await mavlink_proxy.download_ulog(
                remote_path, 
                Path(local_path), 
                on_progress,
                cancel_event
            )
            
            # Only update progress if not cancelled
            if not cancel_event.is_set() and result:
                progress_data["completed"] = True
                progress_data["progress"] = 100
                # Final broadcast
                for ws in list(websocket_clients):
                    try:
                        await ws.send_json(progress_data)
                    except Exception:
                        logger.warning(f"Failed to send final progress update to WebSocket client: {ws}")
                        websocket_clients.discard(ws)
                        
                logger.info(f"Successfully downloaded ULog file {local_filename} from Pixhawk")
                return {
                    "success": True,
                    "file_path": local_path,
                    "file_name": local_filename,
                    "download_id": download_id
                }
            else:
                logger.info(f"Download cancelled for ULog file {local_filename}")
                return {
                    "success": False,
                    "message": "Download was cancelled",
                    "download_id": download_id
                }
                
        finally:
            # Clean up regardless of success or failure
            active_downloads.pop(download_id, None)
        
    @http_action(method="POST", path="/cancel-download")
    async def cancel_download(self, data: Dict[str, str]):
        """Cancel an in-progress download operation."""
        download_id = data.get("download_id")
        if not download_id:
            logger.error("Download ID parameter required for cancellation")
            raise HTTPException(
                status_code=400,
                detail="Download ID parameter required",
                headers={"source": "cancel_download"}
            )

        if download_id not in active_downloads:
            logger.warning(f"Download ID {download_id} not found or already completed")
            raise HTTPException(
                status_code=404,
                detail="Download not found or already completed",
                headers={"source": "cancel_download"}
            )
        
        # Set the cancellation event
        active_downloads[download_id].set()
        
        # Broadcast cancellation to WebSocket clients
        cancel_progress_data = {
            "type": "cancelled",
            "download_id": download_id,
            "message": "Download cancelled by user",
            "completed": True,
            "progress": 0
        }
        
        for ws in list(websocket_clients):
            try:
                await ws.send_json(cancel_progress_data)
            except Exception:
                logger.warning(f"Failed to send cancellation message to WebSocket client: {ws}")
                websocket_clients.discard(ws)
        
        logger.info(f"Download with ID {download_id} has been cancelled")
        return {
            "success": True,
            "message": "Download cancellation requested",
            "download_id": download_id
        }

    @http_action(method="GET", path="/download-ulog-local")
    async def download_ulog_local(self, file_id: str):
        """Download a ULog file from local storage."""
        try:
            # Parameter validation
            if not file_id:
                raise HTTPException(
                    status_code=400,
                    detail="UUID parameter required",
                    headers={"source": "download_ulog_local"}
                )
            
            # Get local ULog files from Redis
            db_proxy: LocalDBProxy = self._proxies["db"]
            redis_proxy: RedisProxy = self._proxies["redis"]
            
            # Get file data from Redis
            redis_key = f"local_ulogs:{db_proxy.machine_id}"
            local_ulogs = await redis_proxy.get(redis_key)
            
            if not local_ulogs:
                logger.error(f"No local ULog files found for machine {db_proxy.machine_id}")
                raise HTTPException(
                    status_code=404,
                    detail="No local ULog files found",
                    headers={"source": "download_ulog_local"}
                )
            
            # Parse the JSON data
            local_ulogs = json.loads(local_ulogs)
            
            # Find the file with the matching ID
            file_data = next((file for file in local_ulogs if file["id"] == file_id), None)
            if not file_data:
                logger.error(f"ULog file with ID {file_id} not found in local records")
                raise HTTPException(
                    status_code=404,
                    detail="ULog file not found",
                    headers={"source": "download_ulog_local"}
                )
            
            # Get the file path
            local_file_path = file_data.get("file_path")
            if not local_file_path:
                logger.error(f"File path not found in metadata for ULog file ID {file_id}")
                raise HTTPException(
                    status_code=400,
                    detail="File path parameter required",
                    headers={"source": "download_ulog_local"}
                )
            
            # Check if file exists
            if not os.path.exists(local_file_path):
                logger.error(f"File not found on disk for ULog file ID {file_id}")
                raise HTTPException(
                    status_code=404,
                    detail="File not found on disk",
                    headers={"source": "download_ulog_local"}
                )
            
            # Read the file
            try:
                with open(local_file_path, "rb") as f:
                    file_content = f.read()
            except Exception as e:
                logger.error(f"Error reading downloaded file for ULog ID {file_id}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error reading downloaded file: {str(e)}",
                    headers={"source": "download_ulog_local"}
                )
            
            # Set appropriate headers for file download
            filename = os.path.basename(local_file_path)
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(file_content)),
                "Access-Control-Expose-Headers": "Content-Disposition"
            }

            logger.info(f"Returning ULog file {filename} for download")
            
            # Return the file as a response
            return Response(
                content=file_content,
                headers=headers
            )
            
        except HTTPException:
            logger.error(f"HTTP error downloading ULog file: {file_id}")
            raise
        except Exception as e:
            logger.error(f"Error downloading ULog file {file_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading ULog file: {str(e)}",
                headers={"source": "download_ulog_local"}
            )

    @http_action(method="GET", path="/download-rosbag-local")
    async def download_rosbag_local(self, file_id: str):
        """Download a RosBag file from local storage."""
        try:
            # Parameter validation
            if not file_id:
                logger.error("UUID parameter required for RosBag download")
                raise HTTPException(
                    status_code=400,
                    detail="UUID parameter required",
                    headers={"source": "download_rosbag_local"}
                )
            
            # Get local RosBag files from Redis
            db_proxy: LocalDBProxy = self._proxies["db"]
            redis_proxy: RedisProxy = self._proxies["redis"]
            
            # Get file data from Redis
            redis_key = f"local_rosbags:{db_proxy.machine_id}"
            local_rosbags = await redis_proxy.get(redis_key)
            
            if not local_rosbags:
                logger.error(f"No local RosBag files found for machine {db_proxy.machine_id}")
                raise HTTPException(
                    status_code=404,
                    detail="No local RosBag files found",
                    headers={"source": "download_rosbag_local"}
                )
            
            # Parse the JSON data
            local_rosbags = json.loads(local_rosbags)
            
            # Find the file with the matching ID
            file_data = next((file for file in local_rosbags if file["id"] == file_id), None)
            if not file_data:
                logger.error(f"RosBag file with ID {file_id} not found in local records")
                raise HTTPException(
                    status_code=404,
                    detail="RosBag file not found",
                    headers={"source": "download_rosbag_local"}
                )
            
            # Get the file path
            local_file_path = file_data.get("file_path")
            if not local_file_path:
                logger.error(f"File path not found in metadata for RosBag file ID {file_id}")
                raise HTTPException(
                    status_code=400,
                    detail="File path parameter required",
                    headers={"source": "download_rosbag_local"}
                )
            
            # Check if file exists
            if not os.path.exists(local_file_path):
                raise HTTPException(
                    status_code=404,
                    detail="File not found on disk",
                    headers={"source": "download_rosbag_local"}
                )
            
            # Read the file
            try:
                with open(local_file_path, "rb") as f:
                    file_content = f.read()
            except Exception as e:
                logger.error(f"Error reading downloaded file for RosBag ID {file_id}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error reading downloaded file: {str(e)}",
                    headers={"source": "download_rosbag_local"}
                )
            
            # Set appropriate headers for file download
            filename = os.path.basename(local_file_path)
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(file_content)),
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
            
            logger.info(f"Returning RosBag file {filename} for download")
            # Return the file as a response
            return Response(
                content=file_content,
                headers=headers
            )
            
        except HTTPException:
            logger.error(f"HTTP error downloading RosBag file: {file_id}")
            raise
        except Exception as e:
            logger.error(f"Error downloading RosBag file {file_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading RosBag file: {str(e)}",
                headers={"source": "download_rosbag_local"}
            )

    @http_action(method="POST", path="/get-file-info-db")
    async def get_file_info_db(self, data: Dict[str, str]):
        """Get file information from the database."""
        try:
            # Parameter validation
            file_id = data.get("file_id")
            if not file_id:
                logger.error("UUID parameter required for file information retrieval")
                raise HTTPException(
                    status_code=400,
                    detail="UUID parameter required",
                    headers={"source": "get_file_info_db"}
                )

            # Get file information from the database
            db_proxy: LocalDBProxy = self._proxies["db"]
            result = await db_proxy.get_item(
                "config-log-file_system",
                "id",
                file_id
            )

            if "error" in result:
                logger.error(f"Error retrieving file metadata from database: {result['error']}")
                raise HTTPException(
                    status_code=404,
                    detail="File not found in database",
                    headers={"source": "get_file_info_db"}
                )

            # Extract file information from result

            if "data" not in result or "file_path" not in result["data"]:
                logger.error(f"File metadata not found in database for file ID {file_id}")
                raise HTTPException(
                    status_code=404,
                    detail="File metadata not found in database",
                    headers={"source": "get_file_info_db"}
                )
            
            file_info = result["data"]
            file_info["id"] = file_id  # Ensure ID is included in the response
            file_info["file_path"] = file_info.get("file_path", "")
            file_info["file_name"] = os.path.basename(file_info["file_path"]) if file_info["file_path"] else ""
            file_info["file_type"] = file_info.get("file_type", "unknown")
            file_info["storage_type"] = file_info.get("storage_type", "unknown")
            file_info["deleted"] = file_info.get("deleted", False)
            file_info["metadata"] = file_info.get("metadata", {})
            file_info["available_locally"] = os.path.exists(file_info["file_path"]) if file_info["file_path"] else False
            if "metadata" in file_info:
                file_info["metadata"]["size_kb"] = round(file_info["metadata"].get("size_bytes", 0) / 1024, 2)
            else:
                file_info["metadata"] = {"size_kb": 0}
            logger.info(f"Retrieved file information for file ID {file_id}")
            return file_info
        except HTTPException:
            logger.error(f"HTTP error retrieving file information from database: {file_id}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving file information {file_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving file information: {str(e)}",
                headers={"source": "get_file_info_db"}
            )

    @http_action(method="GET", path="/download-file-db")
    async def download_file_db(self, file_id: str):
        """Download a file from storage using database information."""
        try:
            # Parameter validation
            if not file_id:
                logger.error("UUID parameter required for file download")
                raise HTTPException(
                    status_code=400,
                    detail="UUID parameter required",
                    headers={"source": "download_file_db"}
                )
            
            # Get file information from the database
            db_proxy: LocalDBProxy = self._proxies["db"]
            
            result = await db_proxy.get_item(
                "config-log-file_system",
                "id",
                file_id
            )

            if "error" in result:
                logger.error(f"Error retrieving file metadata from database: {result['error']}")
                raise HTTPException(
                    status_code=404,
                    detail="File not found in database",
                    headers={"source": "download_file_db"}
                )
            
            # Extract file path from result
            if "file_path" not in result.get("data", {}):
                logger.error("File metadata not found in database for file ID {file_id}")
                raise HTTPException(
                    status_code=404,
                    detail="File metadata not found in database",
                    headers={"source": "download_file_db"}
                )
            
            local_file_path = result["data"]["file_path"]
            
            if not local_file_path:
                logger.error(f"File path not found in metadata for file ID {file_id}")
                raise HTTPException(
                    status_code=400,
                    detail="File path parameter required",
                    headers={"source": "download_file_db"}
                )
            
            # Check if file exists on disk
            if not os.path.exists(local_file_path):
                logger.error(f"File not found on disk for file ID {file_id}")
                raise HTTPException(
                    status_code=404,
                    detail="File not found on disk",
                    headers={"source": "download_file_db"}
                )
            
            # Read the file
            try:
                with open(local_file_path, "rb") as f:
                    file_content = f.read()
            except Exception as e:
                logger.error(f"Error reading downloaded file for file ID {file_id}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error reading downloaded file: {str(e)}",
                    headers={"source": "download_file_db"}
                )
            
            # Set appropriate headers for file download
            filename = os.path.basename(local_file_path)
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(file_content)),
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
            
            logger.info(f"Returning file {filename} for download from database")

            # Return the file as a response
            return Response(
                content=file_content,
                headers=headers
            )
            
        except HTTPException:
            logger.error(f"HTTP error downloading file from database: {file_id}")
            raise
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading file: {str(e)}",
                headers={"source": "download_file_db"}
            )

    @http_action(
        method="GET", 
        path="/get-px4-time",
        summary="Get PX4 time",
        description="Retrieve the PX4 autopilot time using MAVLink.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Successfully retrieved PX4 time",
                "content": {
                    "application/json": {
                        "example": {
                            "timestamp_s": 1718593200,
                            "utc_human": "2025-06-16 14:30:00",
                            "source_msg": "AUTOPILOT_VERSION"
                        }
                    }
                }
            },
            404: {
                "description": "PX4 time not found",
                "content": {
                    "application/json": {
                        "example": {"error": "No valid PX4 time information found"}
                    }
                }
            },
            500: {
                "description": "Server error",
                "content": {
                    "application/json": {
                        "example": {"error": "Failed to retrieve PX4 time"}
                    }
                }
            },
            504: {
                "description": "Timeout while waiting for PX4 time",
                "content": {
                    "application/json": {
                        "example": {"error": "Timeout while waiting for PX4 time"}
                    }
                }
            }
        }
    )
    async def get_px4_time(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Return PX4 time (best-effort) using the new proxy infrastructure.
        """
        mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]

        try:
            msg_id = str(mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION)
            msg = mavlink_proxy.build_req_msg_long(message_id=msg_id)
            msg = await self.get_message(msg_id=msg_id, request_msg=msg, timeout=timeout)

            # ---- identical timestamp extraction logic to your original function ----
            if hasattr(msg, "time_utc") and msg.time_utc:
                ts = int(msg.time_utc)
                logger.debug(f"PX4 time_utc: {ts}")
                return dict(
                    time_unix_usec=ts * 1_000_000,
                    time_boot_ms=None,
                    timestamp_s=ts,
                    utc_human=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)),
                    source_msg="AUTOPILOT_VERSION",
                )

            # fallbacks
            for fld in ("time_boot_ms", "time_usec", "_timestamp"):
                if hasattr(msg, fld):
                    raw = getattr(msg, fld)
                    ts = int(
                        raw
                        / (
                            1000
                            if fld == "time_boot_ms"
                            else 1_000_000
                            if fld == "time_usec"
                            else 1
                        )
                    )
                    logger.debug(f"PX4 {fld}: {ts}")
                    return dict(
                        time_unix_usec=raw,
                        time_boot_ms=raw if fld == "time_boot_ms" else None,
                        timestamp_s=ts,
                        utc_human=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)),
                        source_msg=f"AUTOPILOT_VERSION[{fld}]",
                    )
            logger.error("No valid PX4 time information found in AUTOPILOT_VERSION message")
            raise HTTPException(
                status_code=404, 
                detail="No valid PX4 time information found",
                headers={"source_msg": "AUTOPILOT_VERSION (no time fields available)"}
            )
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 time: {str(exc)}")
            raise HTTPException(
                status_code=504, 
                detail=str(exc),
                headers={"source": "get_px4_time"}
            )
        except Exception as exc:
            logger.error(f"Unexpected error while waiting for PX4 time: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=str(exc),
                headers={"source": "get_px4_time"}
            )

    @http_action(
        method="GET",
        path="/px4-log-entries",
        summary="Get flight-log directory",
        description="Return the list of available ULog files on the PX4 SD card.",
        response_model=Dict[int, Dict[str, int]],
        status_code=200,
    )
    async def px4_log_entries(self, timeout: float = 8.0):
        mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]
        try:
            msg_id = str(mavutil.mavlink.MAVLINK_MSG_ID_LOG_ENTRY)
            msg = mavlink_proxy.build_req_msg_log_request(message_id=msg_id)
            msg =  await mavlink_proxy.get_log_entries(msg_id=msg_id, request_msg=msg, timeout=timeout)
            if not msg:
                logger.error("No log entries found in PX4 logs")
                raise HTTPException(
                    status_code=404, 
                    detail="No log entries found",
                    headers={"source": "px4_log_entries"}
                )
            return msg
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 log entries: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))

    @http_action(
        method="GET", 
        path="/sync-flight-records",
        summary="Sync flight records between local and cloud",
        description="Synchronize all flight records between local and cloud databases. Uploads local-only records to cloud and downloads cloud-only records to local.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Successfully synchronized flight records",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "Flight records synchronized successfully",
                            "uploaded_count": 5,
                            "downloaded_count": 3,
                            "upload_errors": [],
                            "download_errors": [],
                            "total_synced": 8
                        }
                    }
                }
            },
            500: {
                "description": "Server error during synchronization",
                "content": {
                    "application/json": {
                        "example": {"success": False, "error": "Failed to sync flight records"}
                    }
                }
            }
        }
    )
    async def sync_flight_records(self) -> Dict[str, Any]:
        """Synchronize all flight records between local and cloud databases."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        bucket_proxy: S3BucketProxy = self._proxies["bucket"]

        try:
            logger.info("Starting flight records synchronization")
            
            # Get comparison data to identify what needs to be synced
            comparison_result = await self.compare_flight_records()
            
            local_only_ids = comparison_result.get("local_only", [])
            cloud_only_ids = comparison_result.get("cloud_only", [])
            
            upload_results = {
                "uploaded_count": 0,
                "upload_errors": []
            }
            
            download_results = {
                "downloaded_count": 0,
                "download_errors": []
            }
            
            # Upload local-only records to cloud
            logger.info(f"Uploading {len(local_only_ids)} records to cloud")
            for flight_record_id in local_only_ids:
                try:
                    await self._upload_record_to_cloud(
                        flight_record_id=flight_record_id,
                        local_db_proxy=local_db_proxy,
                        cloud_proxy=cloud_proxy,
                        bucket_proxy=bucket_proxy
                    )
                    upload_results["uploaded_count"] += 1
                    logger.info(f"Successfully uploaded flight record {flight_record_id} to cloud")
                    
                except Exception as e:
                    error_msg = f"Failed to upload flight record {flight_record_id}: {str(e)}"
                    logger.error(error_msg)
                    upload_results["upload_errors"].append({
                        "flight_record_id": flight_record_id,
                        "error": error_msg
                    })
            
            # Download cloud-only records to local
            logger.info(f"Downloading {len(cloud_only_ids)} records from cloud")
            for flight_record_id in cloud_only_ids:
                try:
                    await self._download_flight_record(
                        flight_record_id=flight_record_id,
                        local_db_proxy=local_db_proxy,
                        cloud_proxy=cloud_proxy
                    )
                    download_results["downloaded_count"] += 1
                    logger.info(f"Successfully downloaded flight record {flight_record_id} from cloud")
                    
                except Exception as e:
                    error_msg = f"Failed to download flight record {flight_record_id}: {str(e)}"
                    logger.error(error_msg)
                    download_results["download_errors"].append({
                        "flight_record_id": flight_record_id,
                        "error": error_msg
                    })
            
            total_synced = upload_results["uploaded_count"] + download_results["downloaded_count"]
            total_errors = len(upload_results["upload_errors"]) + len(download_results["download_errors"])
            
            success_message = f"Synchronized {total_synced} flight records"
            if total_errors > 0:
                success_message += f" with {total_errors} errors"
            
            logger.info(f"Flight records synchronization completed: {success_message}")
            
            return {
                "success": True,
                "message": success_message,
                "uploaded_count": upload_results["uploaded_count"],
                "downloaded_count": download_results["downloaded_count"],
                "upload_errors": upload_results["upload_errors"],
                "download_errors": download_results["download_errors"],
                "total_synced": total_synced,
                "total_errors": total_errors,
                "local_only_processed": len(local_only_ids),
                "cloud_only_processed": len(cloud_only_ids)
            }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during flight records synchronization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during synchronization: {str(e)}",
                headers={"source": "sync_flight_records"}
            )
