import logging

import smbclient
from browser_use import ActionResult


def smb_copy_file_local_to_remote(username, password, server_name, share_name, local_file_path, remote_file_path, port='445'):
    """ This function is used to copy local file to public folder (share driver)

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        local_file_path(str): This is the local file path
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    port = int(port)
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        with open(local_file_path, 'rb') as local_file:
            with smbclient.open_file(fr'//{server_name}/{share_name}/{remote_file_path}', mode='wb', connection_cache=connection_cache) as remote_file:
                remote_file.write(local_file.read())
        smbclient.reset_connection_cache(connection_cache=connection_cache)
        logging.info('File copied successfully to remote SMB share.')
        return ActionResult(
            extracted_content='File copied successfully to remote SMB share.',
            long_term_memory='File copied successfully to remote SMB share.'
        )

    except Exception as e:
        smbclient.reset_connection_cache(connection_cache=connection_cache)
        logging.info(f'Failed to copy file: {e}')
        return ActionResult(
            extracted_content=f'Failed to copy file: {e}',
            long_term_memory=f'Failed to copy file: {e}'
        )
