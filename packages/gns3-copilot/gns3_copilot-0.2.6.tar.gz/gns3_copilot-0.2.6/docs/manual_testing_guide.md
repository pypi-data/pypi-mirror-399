# GNS3 Copilot Manual Testing Guide

> This document provides a comprehensive manual testing process for GNS3 Copilot to help ensure the project's functionality and stability.

---

## Table of Contents

- [1. Environment Preparation Tests](#1-environment-preparation-tests)
- [2. Application Startup Tests](#2-application-startup-tests)
- [3. Settings Page Tests](#3-settings-page-tests)
- [4. Chat Page Tests](#4-chat-page-tests)
- [5. Tool Function Tests](#5-tool-function-tests)
- [6. Help Page Tests](#6-help-page-tests)
- [7. Boundary and Exception Tests](#7-boundary-and-exception-tests)
- [8. Persistence Tests](#8-persistence-tests)
- [9. UI/UX Tests](#9-uiux-tests)
- [10. Test Report Template](#10-test-report-template)

---

## 1. Environment Preparation Tests

### 1.1 Environment Dependency Checks

| Check Item | Command | Expected Result |
|------------|---------|-----------------|
| Python Version | `python --version` | Python 3.10 or higher |
| Virtual Environment | `source venv/bin/activate` | Terminal shows virtual environment activated |
| Dependency Installation | `pip install -e .` | No errors, all packages installed successfully |
| Installation Verification | `gns3-copilot --help` | Displays help information |

### 1.2 GNS3 Server Checks

| Check Item | Command | Expected Result |
|------------|---------|-----------------|
| Service Running Status | Access `http://localhost:3080` | Shows GNS3 Web interface |
| API Version Check | `curl http://localhost:3080/v2/version` | Returns version information in JSON format |
| Project List | `curl http://localhost:3080/v2/projects` | Returns project list (may be empty) |

### 1.3 Environment Variable Checks

| Check Item | Operation | Expected Result |
|------------|----------|-----------------|
| .env File | `ls -la | grep .env` | .env file exists in project root directory |
| Environment Variable Loading | Check application logs | Environment variables loaded correctly |

---

## 2. Application Startup Tests

### 2.1 Basic Startup Test

**Test Steps:**
```bash
gns3-copilot
```

| Verification Item | Expected Result |
|-------------------|-----------------|
| Browser Auto-opens | Default browser navigates to `http://localhost:8501` |
| Page Loads Successfully | Displays GNS3 Copilot title and sidebar navigation |
| No Console Errors | Application logs normal, no abnormal errors |
| Application Responsive | Page elements clickable, interaction normal |

### 2.2 Custom Port Startup Test

**Test Steps:**
```bash
gns3-copilot --server.port 8080
```

| Verification Item | Expected Result |
|-------------------|-----------------|
| Application on Specified Port | Browser navigates to `http://localhost:8080` |
| Default Port No Conflict | Port 8501 not occupied |

### 2.3 Network Access Startup Test

**Test Steps:**
```bash
gns3-copilot --server.address 0.0.0.0 --server.port 8080
```

| Verification Item | Expected Result |
|-------------------|-----------------|
| External Access | Other devices on same network can access `http://<IP>:8080` |

---

## 3. Settings Page Tests

### 3.1 Navigate to Settings Page

| Operation Step | Expected Result |
|----------------|-----------------|
| Click "Settings" link in sidebar | Page switches to Settings page |
| Display Configuration Form | All configuration items displayed grouped by category |

### 3.2 GNS3 Server Configuration

#### 3.2.1 API v2 Configuration Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Normal v2 Configuration** | Select API Version: v2, fill in Host, URL | Save successful, displays "Configuration saved" |
| **No Username/Password** | Leave username/password blank under API v2 | Save successful (v2 doesn't require authentication) |
| **Connection Test** | Click "Test Connection" button | Displays "Connection successful" |

#### 3.2.2 API v3 Configuration Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Normal v3 Configuration** | Select API Version: v3, fill in all fields | Save successful |
| **No Authentication Info** | Leave username/password blank under API v3 | Save fails, prompts for authentication info |
| **Connection Test** | Fill in correct username/password and test | Displays connection success or failure |

#### 3.2.3 Exception Cases Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Invalid URL** | Fill in `http://invalid-host:9999` | Prompts connection error on save |
| **Empty Host** | Leave Host field blank | Save fails, prompts required field |
| **GNS3 Service Not Started** | Fill in correct URL but service not running | Connection test fails |

### 3.3 LLM Model Configuration

#### 3.3.1 OpenAI Configuration Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Normal OpenAI Configuration** | Select Provider: openai, fill in Model Name and API Key | Save successful |
| **Using GPT Model** | Model Name: gpt-4o-mini | Save successful |
| **Invalid API Key** | Fill in wrong Key, send test message | Model call fails, displays authentication error |

#### 3.3.2 DeepSeek Configuration Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Normal DeepSeek Configuration** | Select Provider: deepseek, fill in API Key | Save successful |
| **Using DeepSeek Model** | Model Name: deepseek-chat | Save successful |
| **Test Model Call** | Send test message | AI responds normally |

#### 3.3.3 Third-Party Platform Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **OpenRouter Configuration** | Select openrouter, fill in Base URL and API Key | Save successful |
| **Using Custom Model** | Model Name: google/gemini-2.5-flash | Save successful |
| **xAI Configuration** | Select xai, fill in corresponding parameters | Save successful |

### 3.4 Other Settings

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Linux Credentials Configuration** | Fill in Linux Console Username and Password | Save successful |
| **Temperature Adjustment** | Drag slider to adjust | Value changes between 0.0-1.0 |
| **Voice Function Configuration** | Set VOICE=true | Voice function enabled |

### 3.5 Configuration Persistence Test

| Operation Steps | Expected Result |
|-----------------|-----------------|
| Modify all configurations and save | .env file in project root directory updated |
| Restart application | All configurations remain unchanged |
| Delete .env file | Application uses default configurations |

---

## 4. Chat Page Tests

### 4.1 Session Management Tests

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **New Session** | Click "New Session" button in sidebar | Generates new thread_id, session selector shows "New Session" |
| **View Session List** | View Session History dropdown in sidebar | Displays all historical sessions (including title and thread_id) |
| **Select Historical Session** | Select a historical session from dropdown | Page displays that session's message history |
| **Switch Session** | Select another session | Successfully switches to selected session |
| **Delete Session** | Click "Delete" button | Displays deletion success prompt, session removed from list |

### 4.2 Project Selection (No Project State)

#### 4.2.1 Project List Display Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Opened Projects** | Projects open in GNS3 | Page displays "Workspace Selection" and project card list |
| **No Opened Projects** | No projects open in GNS3 | Displays prompt "Please select an opened project..." |
| **Multiple Projects** | Multiple projects open in GNS3 | Displays cards for all projects |

#### 4.2.2 Project Card Information Test

| Check Item | Expected Result |
|------------|-----------------|
| Project Name | Displays project name |
| Project ID | Displays project UUID |
| Device Count | Displays Device_Number |
| Link Count | Displays Link_Number |
| Status | Displays project status (opened/closed) |
| Select Button | Displays "Select" button |

#### 4.2.3 Select Project Test

| Operation Steps | Expected Result |
|-----------------|-----------------|
| Click "Select" button of a project | Enters chat interface, sidebar displays current project name |

### 4.3 Basic Chat Function Tests

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Send Text Message** | Type "你好" in input box and press Enter | Message displays in chat interface, AI responds |
| **Streaming Response** | Observe response process | AI response displays progressively, not all at once |
| **Tool Call Display** | When AI calls a tool | Displays tool call information (tool name, parameters) and results |
| **Multi-turn Dialogue** | Send multiple related messages continuously | Context maintained, AI understands context |
| **Empty Input** | Send spaces or empty string | Prompts need to input content |

### 4.4 Session Title Generation Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **First Turn Dialogue** | Send first message and get response | Session list automatically generates new title |
| **Title Content** | View generated title | Title relates to dialogue content, length not exceeding 40 characters |
| **Multi-turn Dialogue** | Continue dialogue | Title no longer changes |
| **Switch Session** | Switch to another session | Each session title displays independently |

### 4.5 Switch/Exit Project Test

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Display Current Project** | View sidebar | Displays "Current Project: **{Project Name}**" |
| **Switch Project** | Click "Switch Project / Exit" button | Returns to project selection interface |
| **State Persistence** | Re-select previous project after switching | Historical messages and context maintained |

### 4.6 Message History Rendering Test

| Check Item | Expected Result |
|------------|-----------------|
| User Message | Displays on right side, with user icon |
| AI Message | Displays on left side, with robot icon |
| Tool Call | Displays tool call box, containing tool name, parameters |
| Tool Response | Displays tool response box, containing response content |
| Streaming Message | Updates progressively, finally settles to complete content |

---

## 5. Tool Function Tests

### 5.1 Topology Information Query Tests

#### 5.1.1 GNS3TopologyTool Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Query Complete Topology** | "查看当前项目拓扑" (View current project topology) | Displays complete project topology JSON |
| **Query Device Information** | "列出所有设备" (List all devices) | Displays all devices list and their detailed information |
| **Query Link Information** | "显示所有连接" (Show all connections) | Displays all links list and their detailed information |
| **Topology Context** | Query again after other operations | Topology information based on currently selected project |

### 5.2 Node Management Tool Tests

#### 5.2.1 GNS3TemplateTool Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Get All Templates** | "获取可用节点模板" (Get available node templates) | Lists all available templates on GNS3 server |
| **Query by Name** | "查找 Cisco IOSv 模板" (Find Cisco IOSv template) | Displays matching template information |
| **Query by Type** | "查找所有路由器模板" (Find all router templates) | Displays all router type templates |

#### 5.2.2 GNS3CreateNodeTool Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Create Single Node** | "创建一个名为 R1 的路由器" (Create a router named R1) | Node created successfully, returns node information |
| **Specify Template** | "使用 Cisco IOSv 模板创建路由器 R2" (Create router R2 using Cisco IOSv template) | Creates node using specified template |
| **Create Multiple Nodes** | "创建 3 个交换机" (Create 3 switches) | Creates multiple nodes, returns all node information |
| **Creation Failure** | "创建不存在的设备" (Create non-existent device) | Displays error message |

#### 5.2.3 GNS3StartNodeTool Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Start Single Node** | "启动 R1" (Start R1) | Displays startup progress, node starts successfully |
| **Start Multiple Nodes** | "启动所有路由器" (Start all routers) | Displays batch startup progress |
| **Progress Display** | Observe startup process | Displays progress bar and startup status |
| **Startup Failure** | "启动不存在的节点" (Start non-existent node) | Displays error message |

### 5.3 Link Management Tool Tests

#### 5.3.1 GNS3LinkTool Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Create Single Link** | "连接 R1 和 R2" (Connect R1 and R2) | Link created successfully, returns link information |
| **Specify Port** | "将 R1 的 g0/0 连接到 R2 的 g0/0" (Connect R1's g0/0 to R2's g0/0) | Creates link using specified ports |
| **Create Multiple Links** | "连接 R1-R2、R2-R3、R3-R1" (Connect R1-R2, R2-R3, R3-R1) | Creates multiple links |
| **Duplicate Link** | "再次连接 R1 和 R2" (Connect R1 and R2 again) | Displays port occupied or creation successful (different ports) |

### 5.4 Configuration Command Tool Tests

#### 5.4.1 ExecuteMultipleDeviceConfigCommands Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Single Device Configuration** | "在 R1 上配置 hostname Router1" (Configure hostname Router1 on R1) | Configuration commands executed successfully |
| **Multiple Device Configuration** | "在所有路由器上配置 loopback 0" (Configure loopback 0 on all routers) | Batch configuration, returns results for all devices |
| **Multiple Commands** | Configure hostname, banner motd, etc. on R1 | Multiple commands executed sequentially |
| **Complex Configuration** | "配置 OSPF 区域 0" (Configure OSPF area 0) | Multiple configuration commands executed correctly |

#### 5.4.2 Configuration Command Format Test

| Test Scenario | Input Format | Expected Result |
|---------------|--------------|-----------------|
| **JSON Format** | Valid JSON configuration array | Correctly parses and executes |
| **List Format** | Python list format | Correctly parses and executes |
| **Format Error** | Invalid JSON format | Displays format error prompt |

### 5.5 Display Command Tool Tests

#### 5.5.1 ExecuteMultipleDeviceCommands Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **View Configuration** | "在 R1 上显示 running-config" (Show running-config on R1) | Displays complete running configuration |
| **View Routing** | "在所有设备上显示路由表" (Show routing table on all devices) | Batch displays routing tables for each device |
| **View Interface** | "显示 R1 接口状态" (Show R1 interface status) | Displays interface detailed information |
| **Custom Command** | "在 R1 上执行 show version" (Execute show version on R1) | Executes specified display command |

#### 5.5.2 Output Format Test

| Check Item | Expected Result |
|------------|-----------------|
| Command Output Formatting | Displayed in code block for easy reading |
| Multiple Device Results Separation | Each device's results clearly separated |
| Error Handling | When execution fails on one device, other device results display normally |

### 5.6 VPCS Tool Tests

#### 5.6.1 VPCSMultiCommands Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Configure IP Address** | "在 PC1 上配置 ip 192.168.1.1/24" (Configure ip 192.168.1.1/24 on PC1) | Configuration successful |
| **Configure Gateway** | "在 PC1 上配置网关 192.168.1.254" (Configure gateway 192.168.1.254 on PC1) | Configuration successful |
| **Batch Configuration** | "配置所有 PC 的 IP 地址" (Configure IP addresses for all PCs) | Batch configuration successful |
| **Ping Test** | "在 PC1 上 ping 192.168.1.2" (Ping 192.168.1.2 from PC1) | Displays Ping results |
| **Traceroute** | "在 PC1 上 traceroute 8.8.8.8" (Traceroute 8.8.8.8 from PC1) | Displays route tracing results |

#### 5.6.2 Concurrent Execution Test

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Multiple PCs Simultaneous Configuration** | Execute commands on multiple PCs simultaneously | Commands execute concurrently, results returned correctly |
| **Execution Order** | Check logs | Each command executes in expected order |

### 5.7 Linux Telnet Tool Tests

#### 5.7.1 LinuxTelnetBatchTool Test

| Test Scenario | User Input | Expected Result |
|---------------|------------|-----------------|
| **Execute Single Command** | "在 Debian1 上运行 ls -la" (Run ls -la on Debian1) | Displays command output |
| **View System Information** | "在 Debian1 上运行 uname -a" (Run uname -a on Debian1) | Displays system information |
| **Batch Execution** | "在所有 Linux 设备上检查内存" (Check memory on all Linux devices) | Batch execution, displays each device's results |
| **Complex Command** | "在 Debian1 上运行 top -n 1" (Run top -n 1 on Debian1) | Displays process information |
| **Network Test** | "在 Debian1 上 ping google.com" (Ping google.com from Debian1) | Displays Ping results |

#### 5.7.2 Authentication Test

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Correct Credentials** | Use correct username and password | Successfully logs in and executes commands |
| **Wrong Credentials** | Use wrong username and password | Displays authentication failure error |
| **No Credentials** | Linux credentials not configured | Prompts need to configure credentials |

---

## 6. Help Page Tests

### 6.1 Help Page Display Test

| Operation Steps | Expected Result |
|-----------------|-----------------|
| Click "Help" link in sidebar | Page switches to Help page |
| Scroll page | Displays complete help content |
| Check Format | Markdown content renders correctly |
| Check Links | All internal and external links clickable |

### 6.2 Help Content Test

| Check Item | Expected Result |
|------------|-----------------|
| Project Introduction | Correctly displays project description |
| Feature List | Lists all main features |
| Usage Instructions | Provides clear usage steps |
| FAQ | Contains frequently asked questions and answers |
| Technical Support | Provides contact information or links |

---

## 7. Boundary and Exception Tests

### 7.1 Input Boundary Tests

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Empty Message** | Send empty string or only spaces | Prompts need to input content |
| **Super Long Message** | Send 5000+ character long message | Handles normally, won't crash |
| **Special Characters** | Send emoji, special symbols | Handles normally |
| **Chinese Input** | Send Chinese messages | AI understands and responds correctly |
| **Code Input** | Send code blocks or commands | Handles correctly |

### 7.2 Connection Exception Tests

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **GNS3 Service Disconnected** | Operate after closing GNS3 service | Displays connection error, prompts to check service |
| **API Key Invalid** | Use invalid or expired API Key | Displays authentication error |
| **Network Interrupted** | Send message after disconnecting network | Displays network error |
| **Timeout** | API request timeout | Displays timeout prompt |

### 7.3 Concurrency Tests

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Multi-session Switching** | Quickly switch multiple sessions | Each session data correct, no confusion |
| **Fast Sending** | Continuously and quickly send multiple messages | Messages processed in order, no loss |
| **Multiple Browser Tabs** | Open application in multiple tabs simultaneously | Each session runs independently |

### 7.4 Data Boundary Tests

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Many Messages** | 100+ messages in session | Page displays normally, scrolling smooth |
| **Many Projects** | 20+ projects in GNS3 | Project list displays normally |
| **Many Devices** | 50+ devices in project | Operations normal, response timely |

---

## 8. Persistence Tests

### 8.1 Session Persistence Tests

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Session Save** | Create new session, send messages, close application | Session exists after restarting application |
| **Message History** | Send multiple messages, then restart | All historical messages retained |
| **Session Title** | Generate title, then restart | Title remains unchanged |
| **Selected Project** | Select project, then restart | Project state maintained |

### 8.2 Configuration Persistence Tests

| Test Scenario | Operation Steps | Expected Result |
|---------------|----------------|-----------------|
| **Configuration Save** | Modify all configurations, then restart | All configurations remain unchanged |
| **.env File** | Check .env file content | Configurations correctly written to file |
| **Delete .env** | Delete .env, then restart | Application uses default configurations |

### 8.3 Database Check

| Check Item | Expected Result |
|------------|-----------------|
| Database File Exists | `gns3_langgraph.db` exists in project root |
| Session Data | SQLite stores all session records |
| Message Data | Each session's messages correctly stored |

---

## 9. UI/UX Tests

### 9.1 Responsive Layout Tests

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Desktop View** | View at 1920x1080 resolution | Layout normal |
| **Small Screen** | View at 1366x768 resolution | Layout adaptive |
| **Mobile** | Access using mobile browser | Layout adapts to mobile |

### 9.2 Interaction Tests

| Test Scenario | Operation | Expected Result |
|---------------|-----------|-----------------|
| **Sidebar Collapse** | Click collapse button | Sidebar collapses/expands |
| **Scroll Behavior** | Scroll long message list | Scrolling smooth |
| **Button States** | Mouse hover over buttons | Visual feedback |
| **Input Box** | Click input box | Gets focus, can input |

### 9.3 Loading State Tests

| Check Item | Expected Result |
|------------|-----------------|
| Application Startup | Displays loading animation |
| AI Response | Displays loading indicator |
| Tool Execution | Displays executing state |
| Error Prompts | Displays friendly error messages |

### 9.4 Style Tests

| Check Item | Expected Result |
|------------|-----------------|
| Color Scheme | Colors harmonious, sufficient contrast |
| Font Display | Fonts clear and readable |
| Icon Display | All icons display correctly |
| Spacing Layout | Element spacing reasonable |

---

## 10. Test Report Template

### Test Report

```markdown
# GNS3 Copilot Test Report

## Basic Information

| Item | Content |
|------|---------|
| Test Date | YYYY-MM-DD |
| Tester | [Tester Name] |
| Test Environment | - Python: [Version] <br> - GNS3 Server: [Version] <br> - Operating System: [OS] <br> - Browser: [Browser and Version] |
| Application Version | [Version Number] |

## Test Results Summary

| Item | Count |
|------|-------|
| Total Test Cases | XX |
| Passed | XX |
| Failed | XX |
| Skipped | XX |
| Pass Rate | XX% |

## Detailed Test Results

### 1. Environment Preparation Tests
| Case ID | Test Item | Status | Remarks |
|---------|-----------|--------|---------|
| 1.1 | Python Version Check | ✓/✗ | |
| 1.2 | Virtual Environment Check | ✓/✗ | |
| 1.3 | GNS3 Service Check | ✓/✗ | |
| ... | ... | ... | |

### 2. Application Startup Tests
| Case ID | Test Item | Status | Remarks |
|---------|-----------|--------|---------|
| ... | ... | ... | |

### 3. Settings Page Tests
| Case ID | Test Item | Status | Remarks |
|---------|-----------|--------|---------|
| ... | ... | ... | |

... (other test modules)

## Issues Found

### Issue 1
- **Problem Description**: [Detailed description]
- **Severity**: High/Medium/Low
- **Reproduction Steps**:
  1. [Step 1]
  2. [Step 2]
- **Expected Result**: [Expected result]
- **Actual Result**: [Actual result]
- **Screenshot**: (if available)
- **Related Logs**: (if available)

### Issue 2
...

## Improvement Suggestions

1. [Suggestion 1]
2. [Suggestion 2]

## Test Conclusion

[Test summary and conclusion]

## Signatures

| Role | Name | Date |
|------|------|------|
| Tester | [Signature] | [Date] |
| Reviewer | [Signature] | [Date] |
```

---

## Appendix

### A. Common Test Commands

```bash
# Start application
gns3-copilot

# Start application (custom port)
gns3-copilot --server.port 8080

# Run unit tests
python -m pytest tests/ -v

# View logs
tail -f log/gns3_copilot.log

# Check database
sqlite3 gns3_langgraph.db "SELECT * FROM checkpoints LIMIT 5;"
```

### B. Test Environment Preparation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Configure environment variables
cp .env.example .env
# Edit .env file, fill in configurations
```

### C. Test Checklist

- [ ] Environment preparation complete
- [ ] GNS3 server running normally
- [ ] Application startup successful
- [ ] Settings configuration complete
- [ ] Session management normal
- [ ] Project selection normal
- [ ] Basic chat functions normal
- [ ] All tool functions normal
- [ ] Help page normal
- [ ] Boundary exception handling normal
- [ ] Persistence functions normal
- [ ] UI/UX normal

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-24  
**Maintainer**: GNS3 Copilot Team
