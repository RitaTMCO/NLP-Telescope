# flake8: noqa
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Unbabel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import yaml

__version__ = "1.0.1"
__copyright__ = "2020 Unbabel. All rights reserved."

PATH_USER = "user/" 
PATH_DOWNLOADED_PLOTS = "user/downloaded_data/"

def read_yaml_file(file_yaml):
    file = open(PATH_USER + file_yaml, "r")
    data = yaml.safe_load(file)
    file.close()
    return data