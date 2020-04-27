import logging
import os
import jsonschema

from dockermake.constants import Constants
from dockermake.git.git import extract_git_repository, get_git_remote_origin_url
from dockermake.utils.helpers import load_json
from dockermake.utils.yaml_loader import YamlLoader


class Registries:
    """
    This class is implemented as a singleton.
    It holds the registries that are defined in the registries.yaml.
    """
    __instance = None

    class _RegistryInventory:
        JSON_SCHEMA = "registries_1_0.json"

        def __init__(self):
            self.registries = dict()
            self.push_only_to_defined_registries = Constants.DEFAULT_PUSH_ONLY_TO_DEFINED_REGISTRIES
            self.push_only_to_specific_projects = Constants.DEFAULT_PUSH_ONLY_TO_SPECIFIC_GIT_PROJECTS

        def load(self, args):
            if not os.path.isfile(args.registries_file):
                logging.info("no registries.yaml found at path: %s", args.registries_file)
                return

            registries = YamlLoader.safe_load_yaml(args.registries_file)
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas", self.JSON_SCHEMA)
            schema = load_json(schema_path)
            try:
                jsonschema.validate(registries, schema)
            except Exception as exception:
                raise Exception("The registries.yaml schema is invalid: %s" % str(exception))
            self.registries = registries["registries"]
            self.push_only_to_specific_projects = args.push_only_to_specific_git_projects
            self.push_only_to_defined_registries = args.push_only_to_defined_registries

        def get(self):
            return self.registries

        def check_allowed_to_push(self, registry_name):
            if not self.push_only_to_defined_registries and \
                    not self.push_only_to_specific_projects:
                return
            registry = self._find_registry_by_name_in_site_registries(registry_name)
            if not registry:
                raise Exception("Not allowed to push to %s: not defined in registries.yaml" % registry_name)

            if not self.push_only_to_specific_projects:
                return

            remote_url = get_git_remote_origin_url()
            if not remote_url:
                raise Exception("Not allowed to push: by configuration only allowed to push from "
                                "a git repository folder")
            repos = registry.get("repositories", [])
            git_repository = extract_git_repository(remote_url)
            if git_repository not in repos:
                raise Exception(
                    "Not allowed to push to %s: Repository %s (extracted from git remote url) not defined "
                    "in registries.yaml" % (registry_name, git_repository))

        def _find_registry_by_name_in_site_registries(self, registry_name):
            if registry_name in self.registries:
                return self.registries[registry_name]
            return None

        def get_registry_authentication(self, registry_name):
            registry = self._find_registry_by_name_in_site_registries(registry_name)
            user = Constants.REGISTRY_LOGIN_USER
            password = Constants.REGISTRY_LOGIN_PASSWORD
            if registry:
                if "auth" in registry and registry["auth"]:
                    user = registry["auth"].get("user", user)
                    password = registry["auth"].get("password", password)
            return user, password

    def __init__(self):
        if Registries.__instance is None:
            Registries.__instance = Registries._RegistryInventory()
        self.__dict__['_Registries__instance'] = Registries.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
