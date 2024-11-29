import json


def load_settings(return_custom: str = None):
    """設定をファイルから読み込む"""
    try:
        with open("local.settings.json") as f:
            settings = json.load(f)
        if return_custom:
            return settings.get(return_custom)
        return settings
    except FileNotFoundError:
        settings = {
            "use_postgres": False,
            "postgres_config": {
                "host": "postgres",
                "port": 5432,
                "database": "main_db",
                "user": "postgres",
                "password": "postgres",
            },
            "sqlite_config": {
                "database": "main.db",
            },
        }
        with open("local.settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}
