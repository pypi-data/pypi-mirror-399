from viso_sdk.constants.constants import *
from viso_sdk.constants.variables import *
from viso_sdk.constants.modules import *

NODE_TYPE = variables.get_node_type()
NODE_ID = variables.get_node_id()

ROOT_DIR = variables.get_container_dir()
LOG_DIR = variables.get_log_dir()
# 50MB
LOG_SIZE = 50 * 1024 * 1024
