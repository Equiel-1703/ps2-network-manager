from enum import Enum

class WidgetsNames(Enum):
    NETBIOS_LINE_EDIT = "netbios_line_edit"
    LOG_MSG_CONTAINER = "log_msg_container"
    SHARE_NAME_LABEL = "share_name_label"
    SHARE_FOLDER_PATH = "share_folder_path"
    SERVER_STATUS_LABEL = "server_status_label"
    
    CHANGE_FOLDER_BUTTON = "change_folder_button"
    
    INTERFACE_NAME_LABEL = "interface_name_label"
    INTERFACE_IP_LABEL = "interface_ip_label"
    INTERFACE_MASK_LABEL = "interface_mask_label"
    
    START_SERVER_BUTTON = "start_server_button"
    STOP_SERVER_BUTTON = "stop_server_button"
    CHANGE_INTERFACE_BUTTON = "change_interface_button"