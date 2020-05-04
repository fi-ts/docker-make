import yaml


class YamlLoader:
    @staticmethod
    def safe_load_yaml(yaml_path):
        with open(yaml_path, "r", encoding='UTF-8') as yaml_file:
            try:
                return yaml.safe_load(yaml_file.read())
            except yaml.YAMLError as exception:
                raise Exception("Unable to parse %s:\n %s" % (yaml_path, exception))
