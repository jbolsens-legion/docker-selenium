import os
import re
import argparse
import yaml

def find_se_variables(directory):
    se_variables = set()
    pattern = re.compile(r'\bSE_[A-Z0-9_]+')
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.sh'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    se_variables.update(matches)
    return se_variables

def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan .sh files for environment variables starting with SE_")
    parser.add_argument("directory", type=str, help="Directory to scan")
    parser.add_argument("output_file", type=str, help="Output YAML file")
    args = parser.parse_args()

    se_variables = find_se_variables(args.directory)
    sorted_se_variables = sorted(se_variables)
    se_variables_dict = {var: None for var in sorted_se_variables}

    yaml.add_representer(type(None), represent_none)
    with open(args.output_file, 'w') as f:
        yaml.dump(se_variables_dict, f, default_flow_style=False)
