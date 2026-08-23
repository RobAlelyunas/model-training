from pathlib import Path
import shutil
import sys

def initialize_app_storage(first_run: bool = True):
    """Initializes the app storage directories, skipping asset copying if not the first run."""
    
    # Always ensure the root storage directory paths exist
    get_target_models_dir().mkdir(parents=True, exist_ok=True)
    get_source_models_dir().mkdir(parents=True, exist_ok=True)
    get_templates_dir().mkdir(parents=True, exist_ok=True)
    get_datasets_dir().mkdir(parents=True, exist_ok=True)
    get_properties_dir().mkdir(parents=True, exist_ok=True)
    get_logs_dir().mkdir(parents=True, exist_ok=True)
    get_references_dir().mkdir(parents=True, exist_ok=True)

    if first_run:
        source_assets = get_source_assets_dir()  # Where default assets are stored in repo

        if not source_assets.exists():
            raise FileNotFoundError(f"Source assets not found at {source_assets}")
        
        # Copy default assets only on the initial run
        shutil.copytree(source_assets / "templates", get_templates_dir(), dirs_exist_ok=True)
        shutil.copytree(source_assets / "properties", get_properties_dir(), dirs_exist_ok=True)
        shutil.copytree(source_assets / "datasets", get_datasets_dir(), dirs_exist_ok=True)
        shutil.copytree(source_assets / "references", get_references_dir(), dirs_exist_ok=True)

        print("[Bootstrap] Default assets copied successfully for the first run.")

    print(f"[Bootstrap] Initialize app storage complete")

def get_templates_dir() -> Path:
    return get_app_storage_dir() / "templates"

def get_properties_dir() -> Path:
    return get_app_storage_dir() / "properties"

def get_datasets_dir() -> Path:
    return get_app_storage_dir() / "datasets"

def get_references_dir() -> Path:
    return get_app_storage_dir() / "references"

def get_generated_dir() -> Path:
    return get_app_storage_dir() / "generated"

def get_logs_dir() -> Path:
    return get_app_storage_dir() / "logs"

def get_source_models_dir() -> Path:
    return get_app_storage_dir() / "models" / "sources"

def get_target_models_dir() -> Path:
    return get_app_storage_dir() / "models" / "targets"

def get_source_assets_dir() -> Path:
    return get_project_root() / "assets"    

def get_app_storage_dir() -> Path:
    """Returns the writable storage directory for app files, configs, and models."""
    if getattr(sys, 'frozen', False): # if packaged with PyInstaller
        return Path.home() / "Library" / "Application Support" / "InteractiveModelTraining"
    else:
        return get_project_root() / "runtime"

def get_project_root() -> Path:
    """Returns the true root of the repository or the PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', '.'))
    return Path(__file__).parent.parent.parent



