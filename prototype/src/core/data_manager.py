import json
import os
import uuid
from datetime import datetime
from logger_agent import log_agent

DATA_DIR = "data"
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
UNIVERSES_FILE = os.path.join(DATA_DIR, "universes.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
ROLES_FILE = os.path.join(DATA_DIR, "roles.json")

class DataManager:
    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        if not os.path.exists(CLIENTS_FILE):
            self._save_json(CLIENTS_FILE, [{"id": "internal", "name": "Internal"}])
            
        if not os.path.exists(TASKS_FILE):
            self._save_json(TASKS_FILE, [])

        if not os.path.exists(UNIVERSES_FILE):
            self._save_json(UNIVERSES_FILE, ["Jamagax Studio", "Personal", "Health"])
            
        if not os.path.exists(PROJECTS_FILE):
            self._save_json(PROJECTS_FILE, ["LifeOS 2.0", "GemShot", "Web Redesign"])

        if not os.path.exists(ROLES_FILE):
            self._save_json(ROLES_FILE, ["Diseñador", "Developer", "Manager", "Product Owner"])

    def _load_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_agent.error(f"Failed to load {filepath}", e)
            return []

    def _save_json(self, filepath, data):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            log_agent.error(f"Failed to save {filepath}", e)

    # --- UNIVERSES ---
    def get_universes(self):
        data = self._load_json(UNIVERSES_FILE)
        return sorted(data)

    def add_universe(self, name):
        data = self._load_json(UNIVERSES_FILE)
        if name and name not in data:
            data.append(name)
            data.sort()
            self._save_json(UNIVERSES_FILE, data)
            log_agent.log_event("DATA", f"New Universe Added: {name}")

    # --- PROJECTS ---
    def get_projects(self):
        data = self._load_json(PROJECTS_FILE)
        return sorted(data)

    def add_project(self, name):
        data = self._load_json(PROJECTS_FILE)
        if name and name not in data:
            data.append(name)
            data.sort()
            self._save_json(PROJECTS_FILE, data)
            log_agent.log_event("DATA", f"New Project Added: {name}")

    # --- ROLES ---
    def get_roles(self):
        data = self._load_json(ROLES_FILE)
        return sorted(data)

    def add_role(self, name):
        data = self._load_json(ROLES_FILE)
        if name and name not in data:
            data.append(name)
            data.sort()
            self._save_json(ROLES_FILE, data)
            log_agent.log_event("DATA", f"New Role Added: {name}")

    # --- CLIENTS ---
    def get_clients(self):
        """Returns list of client names."""
        data = self._load_json(CLIENTS_FILE)
        return [c["name"] for c in data]

    def add_client(self, name):
        data = self._load_json(CLIENTS_FILE)
        # Check duplicate
        if any(c['name'].lower() == name.lower() for c in data):
            return False
        
        new_client = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        data.append(new_client)
        self._save_json(CLIENTS_FILE, data)
        log_agent.log_event("DATA", f"New Client Added: {name}")
        return True

    # --- TASKS / LOGS ---
    def add_task_entry(self, entry_data):
        """
        Adds a record to tasks.json. 
        entry_data should contain: title, type, universe, project, client, file_path, tags
        """
        data = self._load_json(TASKS_FILE)
        
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "status": "todo" if entry_data.get('type') == 'Task' else "info",
            **entry_data
        }
        
        data.insert(0, record) # Prepend (newest first)
        self._save_json(TASKS_FILE, data)
        log_agent.log_event("DATA", f"Task/Entry indexed: {entry_data.get('title')}")

data_manager = DataManager()
