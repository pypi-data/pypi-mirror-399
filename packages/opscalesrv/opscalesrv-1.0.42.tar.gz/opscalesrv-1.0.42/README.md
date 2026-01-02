# OpScaleSrv - Serial Port HTTP Service with GUI

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.42-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**A powerful Python HTTP service for reading serial port data with modern GUI management, ANPR support, and SAP ABAP integration**

[Features](#-key-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation)

---

**By Altay Kireççi**  
[opriori](https://www.opriori.com) © 2025  
[GitHub](https://github.com/altaykirecci) • [PyPI](https://pypi.org/project/opscalesrv/) • [LinkedIn](https://www.linkedin.com/in/altaykireci)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [GUI Interface](#-gui-interface)
- [HTTP API](#-http-api)
- [ANPR Integration](#-anpr-integration)
- [ABAP Integration](#-abap-integration)
- [Command Line Options](#-command-line-options)
- [Use Cases](#-use-cases)
- [Troubleshooting](#-troubleshooting)
- [Multi-language Support](#-multi-language-support)
- [Recent Updates](#-recent-updates)
- [Support](#-support)

---

## 🎯 Overview

**OpScaleSrv** is a comprehensive solution for reading data from serial devices (Arduino, sensors, scales, PLCs) and providing it via a RESTful HTTP API. It features a modern dark-themed GUI for management, ANPR (Automatic Number Plate Recognition) camera integration with both query and listener modes, and ready-to-use ABAP code for SAP integration.

### What Makes OpScaleSrv Special?

- 🎨 **Modern GUI** - Beautiful dark-themed interface with real-time monitoring
- 📸 **ANPR Support** - Dual-mode ANPR integration (Query & Listener) for IP cameras
- 🔐 **Security** - Host-based access control with optional password protection
- 🌍 **Multi-language** - Supports 7 languages (EN, TR, DE, FR, RU, JA, KO)
- 💼 **SAP Integration** - Ready-to-use ABAP code included
- ⚡ **Real-time** - Live data visualization with traffic light indicators
- 🔧 **Flexible** - Full pyserial parameter support for any serial device
- 📁 **Workspace System** - Centralized configuration, logs, and license management
- 🔑 **License System** - Hardware-based license verification

---

## ✨ Key Features

### Core Functionality

- ✅ **Serial Port Reading** - Support for all pyserial parameters
- ✅ **HTTP REST API** - JSON responses with CORS support
- ✅ **Modern GUI** - PySide6-based management interface
- ✅ **Real-time Monitoring** - Live data display with visual indicators
- ✅ **Test Mode** - Mock data for development and testing
- ✅ **Comprehensive Logging** - Detailed request logging with filtering
- ✅ **Workspace Management** - Centralized data directory for config, logs, and licenses

### Advanced Features

- 🎯 **ANPR Integration** - Dual-mode support:
  - **Query Mode**: Actively fetch plates from IP cameras via ISAPI
  - **Listener Mode**: Receive plate data via HTTP POST from cameras
- 🏎️ **Parallel Reading** - Concurrent serial and camera reads for faster responses
- 🛡️ **Force Read Mode** - Option to read plates even if serial reading fails
- 🚀 **Smart Caching** - Configurable caching for rapid request handling
- 🔄 **Retry Mechanism** - Automatic retry for failed camera requests
- 🏷️ **Response Tags** - Custom response tags for multiple cameras/listeners
- 🔐 **Access Control** - Host-based IP and port restrictions
- 🔑 **Password Protection** - Optional authentication for settings
- 🌐 **Multi-language UI** - 7 languages supported
- 📊 **Traffic Light Indicator** - Visual status representation (Serial, ISAPI, Test)
- 🔄 **Auto-recovery** - Automatic configuration initialization
- ⚙️ **Settings Reset** - Easy reset to default configuration
- 🔒 **License System** - Hardware-based license verification

### Integration

- 💼 **SAP ABAP Integration** - Ready-to-use ABAP classes and reports
- 📡 **CORS Support** - Cross-origin requests enabled
- 🔌 **IoT Ready** - Arduino, Raspberry Pi, ESP32 compatible
- 🏭 **Industrial** - PLC and SCADA integration
- 🌐 **Custom Server URL** - Configure custom API endpoint paths

---

## 📦 Installation

### Method 1: Global Install (Recommended)

The easiest way to install OpScaleSrv:

```bash
pip install opscalesrv
opscalesrv --init  # Create configuration file
opscalesrv         # Start GUI application
```

### Method 2: Isolated Install (Using pipx)

If you want to keep your system clean and run OpScaleSrv as a standalone application:

```bash
pipx install opscalesrv
opscalesrv --init
opscalesrv
```

*`pipx` automatically handles virtual environments for you.*

### Method 3: Manual Virtual Environment

#### Windows
```cmd
mkdir opscalesrv
cd opscalesrv
python -m venv venv
venv\Scripts\activate
pip install opscalesrv
opscalesrv --init
opscalesrv
```

#### macOS / Linux
```bash
mkdir opscalesrv
cd opscalesrv
python3 -m venv venv
source venv/bin/activate
pip install opscalesrv
opscalesrv --init
opscalesrv
```

### Requirements

- Python 3.7 or higher
- PySide6 (for GUI) - automatically installed
- pyserial (for serial communication) - automatically installed
- requests (for HTTP requests and ANPR) - automatically installed

---

## 🚀 Quick Start

### 1. First Launch

When you first launch OpScaleSrv, you'll be prompted to select a workspace folder. This folder will store:
- Configuration file (`opscalesrv.json`)
- Log files (`requests.log`, `anpr_requests.log`)
- License file (`license.key`)

### 2. License Setup

On first launch, you'll see a license dialog. You need a valid license key for your machine. Contact the developer to obtain a license key.

### 3. Initialize Configuration

If configuration doesn't exist, it will be auto-created. You can also manually initialize:

```bash
opscalesrv --init
```

This creates `opscalesrv.json` with default configuration.

### 4. Configure Serial Port

Edit `opscalesrv.json` or use the GUI (Settings → Serial Port Settings):

```json
{
  "serial": {
    "port": "/dev/ttyUSB0",  // or "COM3" on Windows
    "baudrate": 9600,
    "bytesize": 8
  }
}
```

### 5. Start the Application

**GUI Mode (Recommended):**
```bash
opscalesrv
```

**Command Line Mode:**
```bash
opscalesrv --cli --host 0.0.0.0 --port 7373
```

**Test Mode (No Serial Device Required):**
```bash
opscalesrv --cli --test
```

### 6. Test the API

```bash
curl http://localhost:7373/
```

**Response:**
```json
{
  "message": {
    "value": 125.5,
    "msg": "Serial Value",
    "mode": "read",
    "result": "OK",
    "isapi_result": "DISABLED",
    "plate1": "NO_PLATE"
  },
  "timestamp": "2025-12-19T14:30:45.123456",
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "client_port": 54321,
  "cam_status": 0
}
```

---

## ⚙️ Configuration

### Configuration File Structure

The `opscalesrv.json` file contains all settings. You can edit it manually or use the GUI (Settings menu).

```json
{
  "settings": {
    "name": "My Scale Server",
    "port": 7373,
    "language": "en",
    "log_file": "requests.log",
    "log_all_requests": true,
    "deny_unknown_hosts": true,
    "encode": "utf-8",
    "server_url": "/",
    "serial": true,
    "isapi": "disabled"
  },
  "serial": {
    "port": "/dev/ttyUSB0",
    "baudrate": 9600,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "timeout": 1
  },
  "allowed_hosts": [
    {
      "ip": "127.0.0.1",
      "ports": [7373, 8080],
      "description": "Localhost access"
    }
  ],
  "query": {
    "cameras": [
      {
        "name": "entrance",
        "enabled": true,
        "server": "192.168.1.100",
        "port": 80,
        "URL": "/ISAPI/Event/notification/alertStream",
        "username": "admin",
        "password": "camera_password",
        "plate": "licensePlate",
        "response_tag": "plate1"
      }
    ],
    "parallel_read": true,
    "force_read": false,
    "cache_duration": 3.0,
    "timeout": 10,
    "retry_count": 0
  },
  "listener": {
    "listeners": [
      {
        "name": "entrance",
        "enabled": true,
        "url": "/anpr/notify",
        "plate_tag": "licensePlate",
        "response_tag": "plate1",
        "tolerance_minutes": 5.0,
        "timeout_seconds": 60.0,
        "picture_path": "/path/to/pictures"
      }
    ]
  }
}
```

### Settings Parameters

| Parameter | Type | Description | Values |
|-----------|------|-------------|--------|
| `name` | string | Server display name | Any string |
| `port` | integer | HTTP server port | 1-65535 |
| `language` | string | GUI language | `en`, `tr`, `de`, `fr`, `ru`, `ja`, `ko` |
| `log_file` | string | Log file path | Filename or absolute path |
| `log_all_requests` | boolean | Enable request logging | `true`, `false` |
| `deny_unknown_hosts` | boolean | Block unauthorized IPs | `true`, `false` |
| `encode` | string | Character encoding | `utf-8`, `iso-8859-9`, `ascii` |
| `server_url` | string | Custom API endpoint path | `/`, `/sap`, `/api`, etc. |
| `serial` | boolean | Enable serial reading | `true`, `false` |
| `isapi` | string | ANPR mode | `disabled`, `query`, `listen` |

### Serial Port Parameters

| Parameter | Type | Description | Example Values |
|-----------|------|-------------|----------------|
| `port` | string | Serial port path **[REQUIRED]** | `/dev/ttyUSB0`, `COM3`, `/dev/cu.usbserial-*` |
| `baudrate` | integer | Communication speed **[REQUIRED]** | `9600`, `19200`, `115200` |
| `bytesize` | integer | Data bits per character **[REQUIRED]** | `5`, `6`, `7`, `8` |
| `parity` | string | Parity checking | `"N"` (None), `"E"` (Even), `"O"` (Odd) |
| `stopbits` | float | Stop bits | `1`, `1.5`, `2` |
| `timeout` | float | Read timeout (seconds) | `0.1`, `1.0`, `null` (blocking) |
| `xonxoff` | boolean | Software flow control | `true`, `false` |
| `rtscts` | boolean | Hardware flow control RTS/CTS | `true`, `false` |
| `dsrdtr` | boolean | Hardware flow control DSR/DTR | `true`, `false` |

### Host Access Control

Configure which IP addresses can access the server:

```json
{
  "allowed_hosts": [
    {
      "ip": "192.168.1.100",
      "ports": [7373, 7374, 7375],
      "description": "Production SAP Server"
    },
    {
      "ip": "192.168.1.200",
      "ports": [7373],
      "description": "Development Machine"
    }
  ]
}
```

---

## 🖥️ GUI Interface

### Main Features

#### Traffic Light Indicators

The GUI displays three traffic light indicators:

- 🟡 **Yellow** - Idle / Waiting for data
- 🟢 **Green** - Successful operation
- 🔴 **Red** - Error occurred

**Indicators:**
1. **SERIAL** - Serial port reading status
2. **ISAPI** - ANPR camera status (Query/Listener mode)
3. **TEST** - Test mode indicator

#### Real-time Display

- **Value** - Large purple text showing sensor reading
- **Plate Data** - License plates from ANPR (with response tags)
- **Message** - Status message from serial device
- **Timestamp** - Last data update time
- **Status Bar** - Connection info and request details

### Menu Structure

#### Server Menu

- **Restart Server** - Reload configuration and restart HTTP server
- **Test Mode** - Toggle between real and simulated data
- **Set Password** - Configure password protection for settings
- **Generate ABAP Code** - Export ABAP files for SAP integration
- **Exit** - Close application

#### Settings Menu

- **Serial Port Settings** - Configure serial communication
- **ANPR Listener** - Configure HTTP POST listener for cameras
- **ANPR Query** - Configure active camera querying
- **Allowed Hosts** - Manage access control
- **General Configuration** - Server name, port, language, modes
- **---**
- **Reset Settings** - Reset to default configuration

#### Logs Menu

- **Show Logs** - View request logs in real-time
- **Clear Logs** - Empty the log file

#### Help Menu

- **About** - Version and author information

---

## 🌐 HTTP API

### Endpoints

#### `GET /` (or configured `server_url`)

Main endpoint for serial data retrieval.

**Request:**
```bash
curl http://localhost:7373/
```

**Success Response (200 OK):**
```json
{
  "message": {
    "value": 125.50,
    "msg": "Serial Value",
    "mode": "read",
    "result": "OK",
    "isapi_result": "OK",
    "plate1": "34 ABC 123",
    "plate2": "NO_PLATE"
  },
  "timestamp": "2025-12-19T14:30:45.123456",
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "client_port": 54321,
  "cam_status": 200
}
```

**Error Response (200 OK - but result=FAIL):**
```json
{
  "message": {
    "value": -1,
    "msg": "could not open port '/dev/ttyUSB0': FileNotFoundError",
    "mode": "read",
    "result": "FAIL",
    "isapi_result": "OK",
    "plate1": "NO_PLATE"
  },
  "timestamp": "2025-12-19T14:30:45.123456",
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "client_port": 54321,
  "cam_status": 0
}
```

#### `GET /entrance` (Legacy)

Read data with "entrance" context (for ANPR). Still supported for backward compatibility.

#### `GET /exit` (Legacy)

Read data with "exit" context (for ANPR). Still supported for backward compatibility.

#### `POST /anpr/notify` (Listener Mode)

Receive ANPR notifications from cameras. URL is configurable per listener.

**Request:**
- Content-Type: `application/xml` or `multipart/form-data`
- Body: XML data from camera

**Response:**
- `200 OK` with body `OK`

#### Test Mode Parameter

Add `?test=1` to any endpoint to force test mode:

```bash
curl http://localhost:7373/?test=1
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message.value` | number/string | Sensor value or -1 on error |
| `message.msg` | string | Status message or error description |
| `message.mode` | string | `"read"` (serial) or `"test"` (mock) |
| `message.result` | string | `"OK"` (success), `"FAIL"` (error), or `"DISABLED"` |
| `message.isapi_result` | string | `"OK"`, `"FAIL"`, or `"DISABLED"` |
| `message.<response_tag>` | string | License plate from ANPR or `"NO_PLATE"` |
| `timestamp` | string | ISO 8601 timestamp |
| `method` | string | HTTP method (always "GET") |
| `path` | string | Request path |
| `client_ip` | string | Client IP address |
| `client_port` | number | Client port number |
| `cam_status` | number | HTTP status code from camera (0 if not applicable) |

### CORS Support

All endpoints include CORS headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

---

## 📸 ANPR Integration

### Overview

OpScaleSrv supports integration with IP cameras for Automatic Number Plate Recognition. This is useful for:

- Weighbridge systems (truck scales)
- Parking management
- Access control systems
- Vehicle tracking

### Supported Cameras

- Hikvision IP cameras with ANPR capability
- Any camera supporting ISAPI protocol
- Any camera that can send HTTP POST notifications

### ANPR Modes

OpScaleSrv supports two ANPR modes:

#### 1. Query Mode (`isapi: "query"`)

Actively fetch plate data from cameras via ISAPI GET requests.

**Configuration:**
```json
{
  "settings": {
    "isapi": "query"
  },
  "query": {
    "cameras": [
      {
        "name": "entrance",
        "enabled": true,
        "server": "192.168.1.100",
        "port": 80,
        "URL": "/ISAPI/Event/notification/alertStream",
        "username": "admin",
        "password": "camera_password",
        "plate": "licensePlate",
        "response_tag": "plate1"
      }
    ],
    "parallel_read": true,
    "force_read": false,
    "cache_duration": 3.0,
    "timeout": 10,
    "retry_count": 0
  }
}
```

**Features:**
- Parallel reading from multiple cameras
- Configurable caching
- Automatic retry on failure
- Response tags for multiple cameras

#### 2. Listener Mode (`isapi: "listen"`)

Receive plate data via HTTP POST from cameras.

**Configuration:**
```json
{
  "settings": {
    "isapi": "listen"
  },
  "listener": {
    "listeners": [
      {
        "name": "entrance",
        "enabled": true,
        "url": "/anpr/notify",
        "plate_tag": "licensePlate",
        "response_tag": "plate1",
        "tolerance_minutes": 5.0,
        "timeout_seconds": 60.0,
        "picture_path": "/path/to/pictures"
      }
    ]
  }
}
```

**Features:**
- Passive listening (cameras push data)
- Time tolerance validation
- Automatic picture saving
- Multiple listener endpoints
- Response tags for multiple listeners

### Response Tags

Response tags allow you to identify plates from different cameras/listeners in the API response:

```json
{
  "message": {
    "plate1": "34 ABC 123",  // From camera/listener with response_tag="plate1"
    "plate2": "06 XYZ 789",  // From camera/listener with response_tag="plate2"
    "entrance": "NO_PLATE"   // From camera/listener with response_tag="entrance"
  }
}
```

### Usage

When ANPR is enabled:

1. The main window displays license plates with their response tags
2. API responses include plate fields using response tags
3. Different cameras/listeners for different gates
4. Real-time plate recognition display

**Test Mode with ANPR:**

When test mode is active with ANPR enabled:
- Query mode → plates: `"35ABC123"` (test value)
- Listener mode → plates: `"NO_PLATE"` (no listener data in test mode)
- When ANPR is disabled → all plates: `"ANPR_DISABLED"`

---

## 💼 ABAP Integration

### Overview

OpScaleSrv includes ready-to-use ABAP code for SAP integration, allowing you to call the serial service directly from SAP.

### Files Included

1. **`serial_service_test.abap`** - Standalone report program
2. **`serial_service_class.abap`** - Reusable OO class
3. **`serial_class_test.abap`** - Test program using the class

### Export ABAP Files

Use the GUI to export ABAP code:

1. **Server** → **Generate ABAP Code**
2. Select destination folder
3. Files will be copied for SAP import

Or use command line:

```bash
opscalesrv --abap
```

### ABAP Class Usage

#### Method 1: Get Full Result

```abap
DATA: ls_result TYPE zcl_serial_service=>ty_serial_result,
      lv_value  TYPE string.

TRY.
    ls_result = zcl_serial_service=>call_serial_service(
      iv_host = '192.168.1.100'
      iv_port = '7373'
      iv_path = '/'  " or '/entrance' or '/exit' or custom server_url
      iv_timeout = 10
    ).
    
    IF ls_result-success = abap_true.
      WRITE: / 'Value:', ls_result-value,
             / 'Plate:', ls_result-plate,
             / 'Result:', ls_result-result.
    ELSE.
      WRITE: / 'Error:', ls_result-error_text.
    ENDIF.
    
  CATCH zcl_serial_service=>connection_error
        zcl_serial_service=>timeout_error
        zcl_serial_service=>parse_error.
    WRITE: / 'Exception occurred'.
ENDTRY.
```

#### Method 2: Get Only Value

```abap
DATA: lv_value TYPE string.

TRY.
    lv_value = zcl_serial_service=>get_serial_value(
      iv_host = '192.168.1.100'
      iv_port = '7373'
    ).
    WRITE: / 'Serial Value:', lv_value.
    
  CATCH zcl_serial_service=>connection_error.
    WRITE: / 'Connection failed'.
ENDTRY.
```

#### Method 3: Test Connection

```abap
TRY.
    IF zcl_serial_service=>test_connection(
      iv_host = '192.168.1.100'
      iv_port = '7373'
    ) = abap_true.
      WRITE: / 'Connection OK'.
    ELSE.
      WRITE: / 'Connection failed'.
    ENDIF.
    
  CATCH zcl_serial_service=>connection_error.
    WRITE: / 'Error'.
ENDTRY.
```

### Class Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `call_serial_service` | host, port, path, timeout, test_mode | Full result structure | Get complete response |
| `get_serial_value` | host, port, timeout | String value | Get only the value field |
| `test_connection` | host, port, timeout | Boolean | Test if server is reachable |

### Exception Classes

- `connection_error` - Network or HTTP errors
- `timeout_error` - Request timeout
- `parse_error` - JSON parsing errors

---

## 🔧 Command Line Options

### Basic Usage

```bash
opscalesrv [OPTIONS]
```

### Available Options

| Option | Argument | Description |
|--------|----------|-------------|
| `--cli` | - | Run in legacy CLI mode (no GUI) |
| `--host` | HOST | Host to bind to (CLI mode only, default: localhost) |
| `--port` | PORT | Port to listen on (CLI mode only, default: 7373) |
| `--test` | - | Run in test mode (CLI mode only, returns mock data) |
| `--init` | - | Initialize configuration file and exit |
| `--abap` | - | Copy ABAP files to current directory and exit |
| `--help` | - | Show help message |

### Examples

**Start with custom host and port (CLI mode):**
```bash
opscalesrv --cli --host 0.0.0.0 --port 8080
```

**Test mode (CLI mode):**
```bash
opscalesrv --cli --test
```

**Initialize configuration:**
```bash
opscalesrv --init
```

**Export ABAP files:**
```bash
opscalesrv --abap
```

**GUI mode (default):**
```bash
opscalesrv
```

---

## 🎯 Use Cases

### 1. Weighbridge / Truck Scale

**Scenario:** Read weight from truck scale and integrate with SAP

- Serial scale connected to PC
- OpScaleSrv reads weight continuously
- SAP calls HTTP API to get current weight
- Optional ANPR for automatic truck identification

**Configuration:**
```json
{
  "serial": {
    "port": "COM3",
    "baudrate": 9600
  },
  "settings": {
    "isapi": "query"
  },
  "query": {
    "cameras": [
      {
        "name": "entrance",
        "enabled": true,
        "server": "192.168.1.100",
        "response_tag": "plate1"
      }
    ]
  }
}
```

### 2. IoT Sensor Monitoring

**Scenario:** Monitor temperature, humidity, or other sensors

- Arduino/ESP32 sends data via serial
- OpScaleSrv provides HTTP API
- Dashboard calls API for real-time data
- SCADA integration

### 3. Industrial Automation

**Scenario:** Connect PLC to business systems

- PLC communicates via RS232/RS485
- OpScaleSrv acts as gateway
- ERP system reads production data
- Real-time monitoring

### 4. Laboratory Equipment

**Scenario:** Read measurement devices

- Spectrometer, scales, sensors
- Serial data acquisition
- Database logging
- Web-based monitoring

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Port 7373 is already in use`

**Solution:**
- Use different port in GUI settings (Settings → General Configuration)
- Or use CLI: `opscalesrv --cli --port 8080`

#### 2. Serial Port Access Denied

**Error:** `could not open port '/dev/ttyUSB0': Permission denied`

**Solution (Linux):**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and log back in
```

**Solution (Windows):**
- Check Device Manager
- Ensure port is not used by another application
- Update driver if necessary

#### 3. Configuration File Not Found

**Error:** `No opscalesrv.json configuration file found`

**Solution:**
```bash
# Initialize configuration file
opscalesrv --init

# Or let it auto-create (GUI mode only)
opscalesrv
```

#### 4. License Verification Failed

**Error:** License dialog appears on startup

**Solution:**
- Contact the developer to obtain a license key for your machine
- License keys are hardware-specific
- Enter the license key in the dialog

#### 5. ABAP Connection Failed

**Symptoms:** SAP cannot reach the service

**Checklist:**
- [ ] Python service is running
- [ ] Firewall allows port 7373
- [ ] Host IP is in allowed_hosts
- [ ] Network connectivity (ping test)
- [ ] Correct URL in ABAP code (check server_url setting)

**Debug:**
```bash
# Test locally first
curl http://localhost:7373/

# Test from another machine
curl http://192.168.1.100:7373/
```

#### 6. GUI Doesn't Start

**Error:** `ModuleNotFoundError: No module named 'PySide6'`

**Solution:**
```bash
# Reinstall opscalesrv
pip uninstall opscalesrv
pip install opscalesrv
```

#### 7. ANPR Camera Not Responding

**Symptoms:** Camera returns timeout or connection error

**Checklist:**
- [ ] Camera IP address is correct
- [ ] Camera credentials are correct
- [ ] Camera supports ISAPI protocol
- [ ] Network connectivity (ping camera IP)
- [ ] Camera ANPR feature is enabled
- [ ] Check timeout settings in query configuration

**Debug:**
- Use GUI camera test feature (Settings → ANPR Query → Test Camera)
- Check `anpr_requests.log` for detailed XML responses

### Log Analysis

View logs for debugging:

**Using GUI:**
- Logs → Show Logs

**Using Command Line:**
```bash
# Linux/Mac
tail -f requests.log
tail -f anpr_requests.log

# Windows
Get-Content requests.log -Wait
Get-Content anpr_requests.log -Wait
```

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/altaykirecci/opscalesrv/issues)
2. Review the log files (`requests.log`, `anpr_requests.log`)
3. Test in `--test` mode first
4. Email: altay.kirecci@gmail.com

---

## 🌍 Multi-language Support

OpScaleSrv GUI supports 7 languages:

- 🇬🇧 English (en)
- 🇹🇷 Turkish (tr)
- 🇩🇪 German (de)
- 🇫🇷 French (fr)
- 🇷🇺 Russian (ru)
- 🇯🇵 Japanese (ja)
- 🇰🇷 Korean (ko)

**Change language:**
1. Settings → General Configuration
2. Select language from dropdown
3. Save and restart application

---

## 🆕 Recent Updates

### Version 1.0.41

- ✨ **Dual ANPR Modes**: Added Query and Listener modes for flexible camera integration
- 🏷️ **Response Tags**: Support for multiple cameras/listeners with custom response tags
- 📁 **Workspace System**: Centralized configuration, logs, and license management
- 🔒 **License System**: Hardware-based license verification
- 🌐 **Custom Server URL**: Configure custom API endpoint paths
- ⚙️ **Mode Controls**: Independent enable/disable for Serial and ISAPI modes
- 🎯 **Enhanced GUI**: Improved ANPR settings dialogs with test functionality
- 📸 **Picture Saving**: Automatic picture saving in Listener mode
- 🔄 **Improved Error Handling**: Better error messages and status indicators
- 🐛 Bug fixes and stability improvements

---

## 💬 Support

### Get Help

- 📧 **Email:** altay.kirecci@gmail.com
- 🌐 **Website:** [www.opriori.com](https://www.opriori.com)
- 🐛 **Issues:** [GitHub Issues](https://github.com/altaykirecci/opscalesrv/issues)
- 📖 **Documentation:** [PyPI Package](https://pypi.org/project/opscalesrv/)

### Social

- 💼 **LinkedIn:** [Altay Kirecci](https://www.linkedin.com/in/altaykireci)
- 🐙 **GitHub:** [@altaykirecci](https://github.com/altaykirecci)
- 📦 **PyPI Profile:** [altaykireci](https://pypi.org/user/altaykireci/)

---

## 🙏 Acknowledgments

- Built with ❤️ by [Altay Kireççi](https://www.linkedin.com/in/altaykireci)
- Powered by [PySide6](https://wiki.qt.io/Qt_for_Python) and [pyserial](https://github.com/pyserial/pyserial)
- Part of the [opriori](https://www.opriori.com) ecosystem

---

<div align="center">

**⭐ Star this project on GitHub if you find it useful! ⭐**

[GitHub](https://github.com/altaykirecci/opscalesrv) • [PyPI](https://pypi.org/project/opscalesrv/) • [Documentation](https://github.com/altaykirecci/opscalesrv/wiki)

---

**Made with ❤️ in Turkey**

© 2025 Altay Kireççi - opriori

</div>
