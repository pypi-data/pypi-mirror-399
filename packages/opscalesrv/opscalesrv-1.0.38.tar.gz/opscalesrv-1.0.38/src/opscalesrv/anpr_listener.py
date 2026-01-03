
import http.server
import socketserver
import threading
import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Global storage for the latest captured plate
# Structure: {'plate': '...', 'timestamp': datetime_obj, 'source': 'listener', 'xml_content': '...'}
LATEST_LISTENER_PLATE = {
    'plate': None,
    'timestamp': None,
    'captured_at': None,
    'captured_at': None,
    'xml_content': None
}

PLATE_CALLBACK = None

def register_callback(func):
    global PLATE_CALLBACK
    PLATE_CALLBACK = func



def process_anpr_xml(xml_data, config):
    """
    Process ANPR XML data and update global state
    """
    global LATEST_LISTENER_PLATE
    
    # Always update raw content for debugging/test view
    LATEST_LISTENER_PLATE['last_received_xml'] = xml_data
    LATEST_LISTENER_PLATE['last_received_at'] = datetime.now()

    try:
        # Parse XML
        root = ET.fromstring(xml_data)
        
        plate_tag = config.get('plate_tag', 'licensePlate')
        tolerance_min = config.get('tolerance_minutes', 5)
        
        # Extract Plate
        plate = "NO_PLATE"
        # Namespace insensitive search
        for elem in root.iter():
            if plate_tag in elem.tag and elem.text:
                plate = elem.text.strip()
                break
        
        if plate == "NO_PLATE":
            logger.debug("No plate found in incoming XML")
            return

        # Extract Timestamp
        # Cameras often use 'dateTime' or 'absTime'
        # We will search for common time tags
        xml_time = None
        time_str = ""
        for tag in ['dateTime', 'absTime', 'captureTime', 'Timestamp']:
            found = False
            for elem in root.iter():
                if tag in elem.tag and elem.text:
                    time_str = elem.text.strip()
                    found = True
                    break
            if found:
                break
        
        if not time_str:
            logger.warning("No timestamp found in ANPR XML")
            return

        # Parse timestamp (Try common formats)
        try:
            # Remove fractional seconds for simpler parsing if needed, or handle them
            # Removing Z for now to handle simple naive comparison (assuming local time or UTC consistency)
            clean_time_str = time_str.split('.')[0].replace('Z', '')
            xml_time = datetime.strptime(clean_time_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            logger.error(f"Could not parse timestamp: {time_str}")
            return

        # Validate Time
        now = datetime.now()
        # If xml_time is naive, assume it's system local time (or camera is synced)
        # Calculate difference
        diff = abs((now - xml_time).total_seconds()) / 60.0
        
        if diff <= tolerance_min:
            logger.info(f"ANPR Listener: Accepted plate {plate} (Time diff: {diff:.2f} min)")
            LATEST_LISTENER_PLATE['plate'] = plate
            LATEST_LISTENER_PLATE['timestamp'] = xml_time
            LATEST_LISTENER_PLATE['captured_at'] = now
            LATEST_LISTENER_PLATE['timestamp'] = xml_time
            LATEST_LISTENER_PLATE['captured_at'] = now
            LATEST_LISTENER_PLATE['xml_content'] = xml_data
            
            if PLATE_CALLBACK:
                try:
                    PLATE_CALLBACK(plate)
                except Exception as e:
                    logger.error(f"Error in ANPR callback: {e}")
        else:
            logger.warning(f"ANPR Listener: Ignored plate {plate} - Time out of tolerance ({diff:.2f} > {tolerance_min} min)")

    except Exception as e:
        logger.error(f"Error parsing ANPR XML body: {e}")


def get_latest_plate():
    return LATEST_LISTENER_PLATE

