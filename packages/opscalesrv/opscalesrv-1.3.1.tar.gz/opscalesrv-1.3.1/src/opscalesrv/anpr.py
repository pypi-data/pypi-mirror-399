#!/usr/bin/env python3
import requests
from requests.auth import HTTPDigestAuth
import logging
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Cache structure: { 'entrance': { 'plate': '...', 'timestamp': ..., 'status': ... }, 'exit': ... }
_PLATE_CACHE = {}


def fetch_and_log_xml(path, config):
    """
    Gelen path'e göre ilgili kameradan XML verisini çeker, loglar ve plakayı parse eder.
    """
    anpr_config = config.get('query', {})  # Changed from 'anpr' to 'query'
    # No enabled check - query config exists means it's enabled



    # Path kontrolü
    target_key = None
    path_lower = path.lower().split('?')[0]
    
    if path_lower == '/' or 'entrance' in path_lower:
        target_key = 'entrance'
    elif 'exit' in path_lower:
        target_key = 'exit'
    
    if not target_key or target_key not in anpr_config:
        return "NO_DIRECTIONS", 0, "licensePlate"


    cam_settings = anpr_config[target_key]
    
    # No enabled check - camera exists in config means it's enabled


    server = cam_settings.get('server')
    port = cam_settings.get('port', 80)
    url_path = cam_settings.get('URL', '/ISAPI/Event/notification/alertStream')
    username = cam_settings.get('username')
    password = cam_settings.get('password')
    plate_tag = cam_settings.get('plate', 'licensePlate') # Örn: "licensePlate"
    timeout = anpr_config.get('timeout', 10)
    cache_duration = anpr_config.get('cache_duration', 3.0)
    retry_count = anpr_config.get('retry_count', 0)

    # 1. Check Cache
    now = datetime.now()
    if target_key in _PLATE_CACHE:
        cached = _PLATE_CACHE[target_key]
        delta = (now - cached['timestamp']).total_seconds()
        if delta < cache_duration:
            logger.info(f"Returning cached plate for {target_key}: {cached['plate']} (age: {delta:.1f}s)")
            return cached['plate'], cached['status'], plate_tag

    url = f"http://{server}:{port}{url_path}"
    
    # 2. Fetch with Retries
    attempts = 0
    max_attempts = retry_count + 1
    
    while attempts < max_attempts:
        attempts += 1
        try:
            auth = HTTPDigestAuth(username, password)
            # Konfigüre edilen timeout kullanılıyor
            response = requests.get(url, auth=auth, stream=True, timeout=timeout)
            http_status = response.status_code
            
            xml_content = ""
            # Sadece 200 OK ise içeriği oku
            if http_status == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8', errors='ignore')
                        xml_content += decoded_line + "\n"
                        if "</EventNotificationAlert>" in decoded_line or "</ResponseStatus>" in decoded_line:
                            break
                    if len(xml_content) > 30000: 
                        break
            else:
                xml_content = response.text
            
            if xml_content:
                log_anpr_xml(target_key, xml_content, http_status)
                if http_status != 200:
                    # If it's a transient error, retry
                    if attempts < max_attempts: continue
                    return "ANPR_ERROR", http_status, plate_tag
                
                if "<ResponseStatus" in xml_content:
                    if attempts < max_attempts: continue
                    return "ANPR_ERROR", http_status, plate_tag

                
                plate = parse_plate_from_xml(xml_content, plate_tag)
                
                # If NO_PLATE, maybe retry?
                if plate == "NO_PLATE" and attempts < max_attempts:
                    logger.info(f"Attempt {attempts}: No plate found, retrying...")
                    continue

                # Update Cache
                _PLATE_CACHE[target_key] = {
                    'plate': plate,
                    'status': http_status,
                    'timestamp': now
                }
                return plate, http_status, plate_tag
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout connecting to camera {target_key} (Attempt {attempts}/{max_attempts})")
            if attempts < max_attempts: continue
            return "ANPR_ERROR", 408, plate_tag # Request Timeout
        except Exception as e:
            logger.error(f"Error fetching ANPR XML from {target_key}: {e}")
            if attempts < max_attempts: continue
            return "ANPR_ERROR", 0, plate_tag

    
    return "NO_PLATE", 0, plate_tag

def fetch_from_camera(cam_settings, anpr_config, camera_name=None):
    """
    Fetch plate data from a specific camera using camera settings
    Returns: (plate, http_status, plate_tag, country_code)
    """
    if not cam_settings:
        return "NO_PLATE", 0, "licensePlate", None
    
    server = cam_settings.get('server')
    port = cam_settings.get('port', 80)
    url_path = cam_settings.get('URL', '/ISAPI/Event/notification/alertStream')
    username = cam_settings.get('username')
    password = cam_settings.get('password')
    plate_tag = cam_settings.get('plate', 'licensePlate')
    country_tag = cam_settings.get('country_tag', '')
    timeout = anpr_config.get('timeout', 10)
    cache_duration = anpr_config.get('cache_duration', 3.0)
    retry_count = anpr_config.get('retry_count', 0)
    
    # Use camera name as cache key if provided, otherwise use server:port
    cache_key = camera_name if camera_name else f"{server}:{port}"
    
    # Check Cache
    now = datetime.now()
    if cache_key in _PLATE_CACHE:
        cached = _PLATE_CACHE[cache_key]
        delta = (now - cached['timestamp']).total_seconds()
        if delta < cache_duration:
            logger.info(f"Returning cached plate for {cache_key}: {cached['plate']} (age: {delta:.1f}s)")
            cached_country_code = cached.get('country_code')
            return cached['plate'], cached['status'], plate_tag, cached_country_code
    
    url = f"http://{server}:{port}{url_path}"
    
    # Fetch with Retries
    attempts = 0
    max_attempts = retry_count + 1
    
    while attempts < max_attempts:
        attempts += 1
        try:
            auth = HTTPDigestAuth(username, password)
            response = requests.get(url, auth=auth, stream=True, timeout=timeout)
            http_status = response.status_code
            
            xml_content = ""
            if http_status == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8', errors='ignore')
                        xml_content += decoded_line + "\n"
                        if "</EventNotificationAlert>" in decoded_line or "</ResponseStatus>" in decoded_line:
                            break
                    if len(xml_content) > 30000: 
                        break
            else:
                xml_content = response.text
            
            if xml_content:
                log_anpr_xml(cache_key, xml_content, http_status)
                
                # Log raw query data
                try:
                    import opscalesrv
                    if opscalesrv.ENABLE_LOGGING:
                        opscalesrv.log_raw_data('QUERY', xml_content, {
                            'camera_name': cache_key,
                            'server': server,
                            'port': port,
                            'url': url,
                            'http_status': http_status,
                            'attempt': attempts,
                            'max_attempts': max_attempts
                        })
                except:
                    pass  # Silently fail if import not available
                
                if http_status != 200:
                    if attempts < max_attempts: continue
                    # Log error
                    try:
                        import opscalesrv
                        if opscalesrv.ENABLE_LOGGING:
                            opscalesrv.log_raw_data('ERROR', {
                                'error_type': 'HTTPError',
                                'http_status': http_status,
                                'camera': cache_key,
                                'url': url,
                                'response': xml_content[:500] if xml_content else None
                            })
                    except:
                        pass
                    return "ANPR_ERROR", http_status, plate_tag, None
                
                if "<ResponseStatus" in xml_content:
                    if attempts < max_attempts: continue
                    # Log error
                    try:
                        import opscalesrv
                        if opscalesrv.ENABLE_LOGGING:
                            opscalesrv.log_raw_data('ERROR', {
                                'error_type': 'ResponseStatusError',
                                'camera': cache_key,
                                'url': url,
                                'response': xml_content[:500] if xml_content else None
                            })
                    except:
                        pass
                    return "ANPR_ERROR", http_status, plate_tag, None
                
                plate = parse_plate_from_xml(xml_content, plate_tag)
                country_code = parse_country_code_from_xml(xml_content, country_tag)
                
                # Verify plate with country code if applicable
                if plate != "NO_PLATE":
                    try:
                        import opscalesrv
                        full_config = opscalesrv.CONFIG
                        if not opscalesrv.verify_plate_with_country(plate, country_code, country_tag, full_config):
                            logger.warning(f"Query: Plate '{plate}' rejected by country verification (country: {country_code})")
                            plate = "NO_PLATE"  # Reject plate
                    except Exception as e:
                        logger.error(f"Error verifying plate: {e}")
                        # On error, accept plate to avoid blocking valid plates
                
                if plate == "NO_PLATE" and attempts < max_attempts:
                    logger.info(f"Attempt {attempts}: No plate found, retrying...")
                    continue
                
                # Update Cache
                _PLATE_CACHE[cache_key] = {
                    'plate': plate,
                    'status': http_status,
                    'timestamp': now,
                    'country_code': country_code
                }
                return plate, http_status, plate_tag, country_code
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout connecting to camera {cache_key} (Attempt {attempts}/{max_attempts})")
            # Log timeout error
            try:
                import opscalesrv
                if opscalesrv.ENABLE_LOGGING:
                    opscalesrv.log_raw_data('ERROR', {
                        'error_type': 'Timeout',
                        'camera': cache_key,
                        'url': url,
                        'timeout': timeout,
                        'attempt': attempts,
                        'max_attempts': max_attempts
                    })
            except:
                pass
            if attempts < max_attempts: continue
            return "CAM_TIMEOUT", 408, plate_tag, None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to camera {cache_key}: {e}")
            # Log connection error
            try:
                import opscalesrv
                if opscalesrv.ENABLE_LOGGING:
                    opscalesrv.log_raw_data('ERROR', {
                        'error_type': 'ConnectionError',
                        'error_message': str(e),
                        'camera': cache_key,
                        'url': url,
                        'attempt': attempts,
                        'max_attempts': max_attempts
                    })
            except:
                pass
            if attempts < max_attempts: continue
            return "CAM_CONNECTION_ERROR", 0, plate_tag, None
        except Exception as e:
            logger.error(f"Error fetching ANPR XML from {cache_key}: {e}")
            # Log unexpected error
            try:
                import opscalesrv
                import traceback
                if opscalesrv.ENABLE_LOGGING:
                    opscalesrv.log_raw_data('ERROR', {
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'traceback': traceback.format_exc(),
                        'camera': cache_key,
                        'url': url,
                        'attempt': attempts,
                        'max_attempts': max_attempts
                    })
            except:
                pass
            if attempts < max_attempts: continue
            return "CAM_ERROR", 0, plate_tag, None
    
    # If we get here, all attempts failed but no exception was raised
    # This means we got empty or invalid responses
    logger.warning(f"All attempts failed for camera {cache_key}, returning CAM_ERROR")
    return "CAM_ERROR", 0, plate_tag, None

def parse_plate_from_xml(xml_data, plate_tag):
    """
    XML içinden belirtilen etiketi (plate_tag) bulur ve değerini döndürür.
    """
    try:
        # Hikvision XML namespace içerebilir, bu yüzden tag ismine göre arıyoruz
        # Basitlik için tag'i içeren bir arama yapıyoruz
        root = ET.fromstring(xml_data)
        
        # plate_tag içeren elementi ara (örn: licensePlate)
        # Namespace bağımsız arama için:
        for elem in root.iter():
            if plate_tag in elem.tag:
                if elem.text:
                    plate = elem.text.strip()
                    logger.info(f"Parsed Plate: {plate}")
                    return plate
    except Exception as e:
        logger.error(f"XML Parsing error: {e}")
    
    return "NO_PLATE"

def parse_country_code_from_xml(xml_data, country_tag):
    """
    XML içinden belirtilen country_tag etiketini bulur ve değerini döndürür.
    """
    if not country_tag:
        return None
    
    try:
        root = ET.fromstring(xml_data)
        
        # country_tag içeren elementi ara
        for elem in root.iter():
            if country_tag in elem.tag:
                if elem.text:
                    country_code = elem.text.strip()
                    logger.info(f"Parsed Country Code: {country_code}")
                    return country_code
    except Exception as e:
        logger.error(f"XML Parsing error for country code: {e}")
    
    return None

def log_anpr_xml(camera, xml_data, http_status=200):
    """
    Gelen XML verisini anpr_requests.log dosyasına yazar.
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"\n{'='*50}\nTIMESTAMP: {timestamp}\nCAMERA: {camera}\nHTTP STATUS: {http_status}\n{'='*50}\n{xml_data}\n"
        
        with open("anpr_requests.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write ANPR XML to log: {e}")

def test_camera(cam_settings):
    """
    Connects to the camera and returns (raw_xml, status_code, parsed_plate) for testing.
    """
    server = cam_settings.get('server')
    port = cam_settings.get('port', 80)
    url_path = cam_settings.get('URL', '/ISAPI/Event/notification/alertStream')
    username = cam_settings.get('username')
    password = cam_settings.get('password')
    plate_tag = cam_settings.get('plate', 'licensePlate')
    timeout = cam_settings.get('timeout', 10) # default to 10 if not provided

    url = f"http://{server}:{port}{url_path}"
    
    try:
        auth = HTTPDigestAuth(username, password)
        # Dynamic timeout used for testing
        response = requests.get(url, auth=auth, stream=True, timeout=timeout)
        http_status = response.status_code
        
        xml_content = ""
        if http_status == 200:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8', errors='ignore')
                    xml_content += decoded_line + "\n"
                    if "</EventNotificationAlert>" in decoded_line or "</ResponseStatus>" in decoded_line:
                        break
                if len(xml_content) > 30000: 
                    break
        else:
            xml_content = response.text
        
        # Parse plate if it's 200 OK and not a ResponseStatus error
        parsed_plate = "N/A"
        if http_status == 200 and "<ResponseStatus" not in xml_content:
            parsed_plate = parse_plate_from_xml(xml_content, plate_tag)
        elif "<ResponseStatus" in xml_content:
            parsed_plate = "CAM_ERROR"

        return xml_content, http_status, parsed_plate
            
    except requests.exceptions.Timeout:
        return "TIMEOUT: Camera did not send any data within 10 seconds. Is a car passing or is ANPR enabled?", 408, "TIMEOUT"
    except Exception as e:
        return str(e), 0, "ERROR"
