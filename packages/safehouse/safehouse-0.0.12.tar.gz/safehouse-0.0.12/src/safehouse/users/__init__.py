import json
import logging
from pathlib import Path
import uuid

from safehouse import services


logger = logging.Logger(__name__)
NULL_UUID = uuid.UUID(int=0)


class User:
    def __init__(self):
        self.ids_by_mode = {
            'live': NULL_UUID,
            'local': NULL_UUID,
            'standalone': NULL_UUID,
        }
        self.safehouse_directory = Path.home() / '.safehouse'
        self.organizations_directory = self.safehouse_directory / 'organizations'
        self.organizations_directory.mkdir(parents=True, exist_ok=True)
        self.load_ids()

    def __str__(self) -> str:
        return '\n\t'.join([f"{k}: {str(v)}" for k, v in self.ids_by_mode.items()])

    def id_for(self, mode: str) -> uuid.UUID:
        return self.ids_by_mode.get(mode, NULL_UUID)

    @property
    def json_file(self) -> Path:
        return self.safehouse_directory / 'user.json'

    def load_ids(self):
        if self.json_file.is_file() is False:
            try:
                self.ids_by_mode['local'] = services.users.get_local_user()['safehouse_id']
                self.save()
            except Exception as e:
                logger.error(f"couldn't retrieve local user: '{e}'")
                return
        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.ids_by_mode = {
                k: uuid.UUID(v)
                for k, v in json.load(f).items()
            }

    def save(self):
        with open(self.json_file, 'w') as f:
            serializable_ids = {
                k: str(v)
                for k, v in self.ids_by_mode.items()
            }
            json.dump(serializable_ids, f, indent=4)

    def set_id_for(self, mode: str, id: uuid.UUID) -> bool:
        if mode not in self.ids_by_mode.keys():
            logger.error(f"unknown mode '{mode}'")
            return False
        self.ids_by_mode[mode] = id
        print(self.ids_by_mode)
        self.save()
        return True
