import requests
import json
import uuid
import socket
import getpass
import platform
import hashlib
import os
import sys

class AuthlyX:
    def __init__(self, owner_id, app_name, version, secret):
        self.base_url = "https://authly.cc/api/v1"
        self.session_id = None
        self.owner_id = owner_id
        self.app_name = app_name
        self.version = version
        self.secret = secret
        self.application_hash = None
        self.initialized = False
        
        self.response = {
            "success": False,
            "message": "",
            "raw": ""
        }
        
        self.user_data = {
            "username": "",
            "email": "",
            "license_key": "",
            "subscription": "",
            "expiry_date": "",
            "last_login": "",
            "hwid": "",
            "ip_address": "",
            "registered_at": ""
        }
        
        self.variable_data = {
            "var_key": "",
            "var_value": "",
            "updated_at": ""
        }
        
        self.update_data = {
            "available": False,
            "latest_version": "",
            "download_url": "",
            "force_update": False,
            "changelog": ""
        }
        
        self.chat_messages = {
            "channel_name": "",
            "messages": [],
            "count": 0
        }
        
        if not all([owner_id, app_name, version, secret]):
            self._error("Invalid application credentials provided.")
            sys.exit(1)
            
        self._calculate_application_hash()

    def _calculate_application_hash(self):
        """Automatically calculates the application hash from the current executable file."""
        try:
            file_path = sys.executable
            
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                
                self.application_hash = file_hash.hexdigest()
                self._log(f"[HASH] Calculated application hash: {self.application_hash[:16]}...")
                
        except Exception as e:
            self._log(f"[HASH_ERROR] Failed to calculate hash: {str(e)}")
            self.application_hash = "UNKNOWN_HASH"

    def _log(self, content):
        """Logs messages to file similar to C# version"""
        try:
            if sys.platform == "win32":
                base_dir = os.path.join(os.environ.get('PROGRAMDATA', ''), "AuthlyX", "logs", self.app_name)
            else:
                base_dir = "/var/log/AuthlyX"
                
            os.makedirs(base_dir, exist_ok=True)
            
            from datetime import datetime
            log_file = os.path.join(base_dir, f"{datetime.now().strftime('%b_%d_%Y')}_log.txt")
            
            redacted = self._redact(content)
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {redacted}\n")
                
        except Exception:
            pass

    def _redact(self, text):
        """Redacts sensitive information from logs"""
        if not text:
            return text
            
        import re
        fields = ["session_id", "owner_id", "secret", "password", "key", "license_key", "hash"]
        
        for field in fields:
            pattern = f'"{field}":\\s*"[^"]*"'
            text = re.sub(pattern, f'"{field}":"REDACTED"', text, flags=re.IGNORECASE)
            
        return text

    def _error(self, message):
        """Displays error message and exits"""
        self._log(f"[ERROR] {message}")
        
        if sys.platform == "win32":
            import subprocess
            try:
                subprocess.run([
                    'cmd.exe', '/c', 'start', 'cmd', '/C', 
                    f'color 4 && title AuthlyX Error && echo {message} && timeout /t 5'
                ], shell=True, capture_output=True)
            except:
                pass
                
        print(f"AuthlyX Error: {message}")
        sys.exit(1)

    def _post_json(self, endpoint, payload):
        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"AuthlyX-Python-Client/{self.version}"
            }
            
            if self.application_hash and endpoint != "init":
                payload["hash"] = self.application_hash
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            self.response["raw"] = response.text
            
            # Store status code for error handling
            status_code = response.status_code
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                self.response["success"] = False
                self.response["message"] = "Invalid JSON response from server"
                return {"success": False, "status_code": status_code, "data": {}}
            
            self.response["success"] = data.get("success", False)
            self.response["message"] = data.get("message", "")
            
            if self.response["success"] and "session_id" in data:
                self.session_id = data["session_id"]
            
            self._load_user_data(data)
            self._load_variable_data(data)
            self._load_update_data(data)
            self._load_chat_data(data)
            
            return {"success": self.response["success"], "status_code": status_code, "data": data}
            
        except requests.exceptions.RequestException as e:
            self.response["success"] = False
            self.response["message"] = f"Network error: {str(e)}"
            self._log(f"[NETWORK_ERROR] {str(e)}")
            return {"success": False, "status_code": 0, "data": {}}
        except Exception as e:
            self.response["success"] = False
            self.response["message"] = f"Unexpected error: {str(e)}"
            self._log(f"[ERROR] {str(e)}")
            return {"success": False, "status_code": 0, "data": {}}

    def _check_init(self):
        """Checks if AuthlyX has been initialized"""
        if not self.initialized:
            self._error("You must Initialize AuthlyX first")

    def _load_user_data(self, data):
        try:
            license_data = data.get("license", {})
            user_data = data.get("user", data.get("info", {}))
            
            if license_data:
                self.user_data["license_key"] = license_data.get("license_key", "")
                self.user_data["subscription"] = license_data.get("subscription", "")
                self.user_data["expiry_date"] = license_data.get("expiry_date", "")
                self.user_data["last_login"] = license_data.get("last_login", "")
                self.user_data["email"] = license_data.get("email", "")

            self.user_data["username"] = user_data.get("username", "")
            self.user_data["email"] = user_data.get("email", self.user_data["email"])
            self.user_data["subscription"] = user_data.get("subscription", self.user_data["subscription"])
            self.user_data["expiry_date"] = user_data.get("expiry_date", self.user_data["expiry_date"])
            self.user_data["last_login"] = user_data.get("last_login", self.user_data["last_login"])
            self.user_data["registered_at"] = user_data.get("created_at", "")
            
            self.user_data["hwid"] = self._get_system_hwid()
            self.user_data["ip_address"] = self._get_public_ip()
            
        except Exception as e:
            self._log(f"[USER_DATA_ERROR] {str(e)}")

    def _load_variable_data(self, data):
        try:
            variable = data.get("variable", {})
            self.variable_data["var_key"] = variable.get("var_key", "")
            self.variable_data["var_value"] = variable.get("var_value", "")
            self.variable_data["updated_at"] = variable.get("updated_at", "")
        except Exception as e:
            self._log(f"[VARIABLE_DATA_ERROR] {str(e)}")

    def _load_update_data(self, data):
        try:
            update = data.get("update", {})
            if update:
                self.update_data["available"] = update.get("available", False)
                self.update_data["latest_version"] = update.get("latest_version", "")
                self.update_data["download_url"] = update.get("download_url", "")
                self.update_data["force_update"] = update.get("force_update", False)
                self.update_data["changelog"] = update.get("changelog", "")
                
                if self.update_data["available"]:
                    self._log(f"[UPDATE] Update available: {self.update_data['latest_version']}, Force: {self.update_data['force_update']}")
            else:
                self.update_data = {
                    "available": False,
                    "latest_version": "",
                    "download_url": "",
                    "force_update": False,
                    "changelog": ""
                }
        except Exception as e:
            self._log(f"[UPDATE_DATA_ERROR] {str(e)}")

    def _load_chat_data(self, data):
        try:
            chat_data = data.get("data", {})
            if chat_data:
                self.chat_messages["channel_name"] = chat_data.get("channel_name", "")
                messages = chat_data.get("messages", [])
                
                # Clear and replace with latest data
                self.chat_messages["messages"] = []
                
                if messages:
                    for msg in messages:
                        chat_msg = {
                            "id": msg.get("id", 0),
                            "username": msg.get("username", ""),
                            "message": msg.get("message", ""),
                            "created_at": msg.get("created_at", "")
                        }
                        self.chat_messages["messages"].append(chat_msg)
                
                self.chat_messages["count"] = len(self.chat_messages["messages"])
            else:
                # Clear data if no data object
                self.chat_messages["channel_name"] = ""
                self.chat_messages["messages"] = []
                self.chat_messages["count"] = 0
        except Exception as e:
            self._log(f"[CHAT_DATA_ERROR] {str(e)}")
            self.chat_messages["messages"] = []
            self.chat_messages["count"] = 0

    def _get_system_hwid(self):
        try:
            if sys.platform == "win32":
                import ctypes
                import ctypes.wintypes
                GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
                NameDisplay = 3

                size = ctypes.wintypes.DWORD(0)
                GetUserNameEx(NameDisplay, None, ctypes.byref(size))
                if size.value:
                    buffer = ctypes.create_unicode_buffer(size.value)
                    if GetUserNameEx(NameDisplay, buffer, ctypes.byref(size)):
                        return str(uuid.uuid5(uuid.NAMESPACE_DNS, buffer.value))
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, platform.node() + getpass.getuser()))
        except:
            return "UNKNOWN_HWID"

    def _get_public_ip(self):
        """Gets public IP address like C# version"""
        try:
            response = requests.get("https://api.ipify.org", timeout=10)
            public_ip = response.text.strip()
            
            if public_ip and '.' in public_ip and len(public_ip) >= 7:
                self._log(f"[IP] Retrieved public IP: {public_ip}")
                return public_ip
        except Exception as e:
            self._log(f"[IP_ERROR] Failed to get public IP: {str(e)}")
        return "UNKNOWN_IP"

    def init(self):
        """Initializes the connection with AuthlyX"""
        try:
            payload = {
                "owner_id": self.owner_id,
                "app_name": self.app_name,
                "version": self.version,
                "secret": self.secret,
                "hash": self.application_hash
            }

            result = self._post_json("init", payload)
            data = result.get("data", {})
            status_code = result.get("status_code", 200)
            
            # Check for INVALID_VERSION error (status 426)
            if status_code == 426:
                error_code = data.get("code", "")
                if error_code == "INVALID_VERSION":
                    auto_update_enabled = data.get("auto_update_enabled", False)
                    download_url = data.get("auto_update_download_url", "")
                    
                    # Fallback: if auto_update_enabled is not present, check if update object exists
                    if not auto_update_enabled:
                        update_obj = data.get("update", {})
                        if update_obj:
                            update_download_url = update_obj.get("download_url", "")
                            if update_download_url:
                                auto_update_enabled = True
                                download_url = update_download_url
                                self._log("[AUTHLY_DEBUG] auto_update_enabled not found, but update object with download_url exists - assuming enabled")
                    
                    error_message = data.get("message", "Outdated Version")
                    
                    self._log(f"[AUTHLY] Version is outdated: {error_message}")
                    self._log(f"[AUTHLY] auto_update_enabled: {auto_update_enabled}, download_url: {download_url}")
                    
                    if not auto_update_enabled:
                        # Auto-update disabled - close after 5 seconds
                        self._log("[AUTHLY] Auto-update is disabled. Application will close in 5 seconds...")
                        print(f"[AUTHLY] {error_message}")
                        print("[AUTHLY] Auto-update is disabled. Application will close in 5 seconds...")
                        import time
                        time.sleep(5)
                        sys.exit(1)
                    else:
                        # Auto-update enabled - show console menu
                        print(f"\n[AUTHLY] {error_message}")
                        print("\n1. Download Latest")
                        print("2. Exit")
                        choice = input("\nSelect an option (1 or 2): ")
                        
                        if choice == "1" and download_url:
                            import webbrowser
                            webbrowser.open(download_url)
                            self._log("[AUTHLY] Opening download URL in browser...")
                            print("[AUTHLY] Opening download URL in browser...")
                        
                        sys.exit(1)

            if result.get("success", False):
                self.initialized = True
                self._log("[INIT] Successfully initialized AuthlyX session")
                
                if self.update_data["available"] and self.update_data["force_update"]:
                    self._log(f"[UPDATE] Force update required. Opening download URL: {self.update_data['download_url']}")
                    if self.update_data["download_url"]:
                        import webbrowser
                        webbrowser.open(self.update_data["download_url"])
                    self._error(f"Update required. Please install version {self.update_data['latest_version']} and restart the application.")
                    return False
                
                return True
            else:
                try:
                    if data.get("update"):
                        self._load_update_data(data)
                        if self.update_data["available"] and self.update_data["force_update"]:
                            self._log(f"[UPDATE] Force update required. Opening download URL: {self.update_data['download_url']}")
                            if self.update_data["download_url"]:
                                import webbrowser
                                webbrowser.open(self.update_data["download_url"])
                except:
                    pass
                
                self._error(f"Initialization failed: {self.response['message']}")
                return False
                
        except Exception as e:
            self._error(f"Initialization error: {str(e)}")
            return False

    def login(self, username, password):
        self._check_init()
            
        payload = {
            "session_id": self.session_id,
            "username": username,
            "password": password,
            "hwid": self._get_system_hwid(),
            "ip": self._get_public_ip()
        }
        result = self._post_json("login", payload)
        return result.get("success", False)

    def register(self, username, password, key, email=None):
        self._check_init()
            
        payload = {
            "session_id": self.session_id,
            "username": username,
            "password": password,
            "key": key,
            "hwid": self._get_system_hwid()
        }
        
        if email:
            payload["email"] = email
            
        result = self._post_json("register", payload)
        return result.get("success", False)

    def license_login(self, license_key):
        self._check_init()
            
        payload = {
            "session_id": self.session_id,
            "license_key": license_key,
            "hwid": self._get_system_hwid(),
            "ip": self._get_public_ip()
        }
        result = self._post_json("licenses", payload)
        return result.get("success", False)

    def get_variable(self, var_key):
        self._check_init()
            
        payload = {
            "session_id": self.session_id,
            "var_key": var_key
        }
        
        result = self._post_json("variables", payload)
        if result.get("success", False):
            return self.variable_data["var_value"]
        return ""

    def set_variable(self, var_key, var_value):
        self._check_init()
            
        payload = {
            "session_id": self.session_id,
            "var_key": var_key,
            "var_value": var_value
        }
        result = self._post_json("variables/set", payload)
        return result.get("success", False)

    def log(self, message):
        self._check_init()
            
        payload = {
            "session_id": self.session_id,
            "message": message
        }
        result = self._post_json("logs", payload)
        return result.get("success", False)

    def validate_session(self):
        """Validates the current session to check if it's still active"""
        if not self.initialized or not self.session_id:
            self._log("[VALIDATE_SESSION] Not initialized or session ID is empty")
            return False
        
        try:
            self._log(f"[VALIDATE_SESSION] Validating session: {self.session_id}")
            
            payload = {
                "session_id": self.session_id
            }
            
            result = self._post_json("validate-session", payload)
            
            is_valid = self.response.get('success', False) and 'valid' in self.response.get('message', '').lower()
            self._log(f"[VALIDATE_SESSION] Result: {is_valid}, Success: {self.response.get('success')}, Message: {self.response.get('message')}")
            
            return is_valid
        except Exception as e:
            self._log(f"[VALIDATE_SESSION] Exception: {str(e)}")
            return False

    def get_current_application_hash(self):
        return self.application_hash

    def get_session_id(self):
        return self.session_id

    def is_initialized(self):
        return self.initialized

    def get_app_name(self):
        return self.app_name
    def is_update_available(self):
        return self.update_data.get("available", False)

    def get_update_info(self):
        return self.update_data.copy()

    def open_download_url(self):
        if self.update_data.get("download_url"):
            import webbrowser
            webbrowser.open(self.update_data["download_url"])

    def get_chats(self, channel_name):
        """Get messages from a chat channel"""
        self._check_init()
        
        if not channel_name:
            self._log("[GET_CHATS_ERROR] Channel name cannot be empty")
            self.response["success"] = False
            self.response["message"] = "Channel name cannot be empty"
            self.chat_messages["messages"] = []
            self.chat_messages["count"] = 0
            return '{"success":false,"message":"Channel name cannot be empty"}'
        
        payload = {
            "session_id": self.session_id,
            "channel_name": channel_name,
            "limit": 100
        }
        
        result = self._post_json("chats/get", payload)
        
        # _load_chat_data is called in _post_json, so chat_messages is already populated
        if not result.get("success", False):
            self._log(f"[GET_CHATS_ERROR] Failed to get chats from channel '{channel_name}': {self.response['message']}")
            self.chat_messages["messages"] = []
            self.chat_messages["count"] = 0
        elif self.chat_messages["count"] > 0:
            self._log(f"[GET_CHATS_SUCCESS] Retrieved {self.chat_messages['count']} message(s) from channel '{channel_name}'")
        
        return self.response.get("raw", "")

    def send_chat(self, message, channel_name=None):
        """Send a message to a chat channel"""
        self._check_init()
        
        if not message:
            self._log("[SEND_CHAT_ERROR] Message cannot be empty")
            self.response["success"] = False
            self.response["message"] = "Message cannot be empty"
            return
        
        if channel_name is None:
            channel_name = self.app_name
        
        if not channel_name:
            self._log("[SEND_CHAT_ERROR] Channel name cannot be empty")
            self.response["success"] = False
            self.response["message"] = "Channel name cannot be empty"
            return
        
        self._log(f"[SEND_CHAT_DEBUG] Sending chat message to channel '{channel_name}': {message}")
        
        payload = {
            "session_id": self.session_id,
            "channel_name": channel_name,
            "message": message
        }
        
        result = self._post_json("chats/send", payload)
        
        if result.get("success", False):
            self._log(f"[SEND_CHAT_SUCCESS] Message sent successfully to channel '{channel_name}'")
        else:
            self._log(f"[SEND_CHAT_ERROR] Failed to send message: {self.response['message']}")