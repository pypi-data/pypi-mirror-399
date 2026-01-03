import os
from typing import Any, Dict, Optional, Tuple

def list_folder(client, folder_id: str = None, indent=0):
    """
    List files and folders in the specified folder.
    """
    l = client.getList( folder_id )
    if ( 'success', True ) in l.items():
        for item in l.get( 'userFileVOList', [] ):
            name = item.get( 'fileName', '' )
            is_folder = item.get( 'isFolder' ) == 'Y'
            prefix = '  ' * indent
            if is_folder:
                print( f"{prefix}[D] {name} ({item.get('id')})" )
                list_folder( client, item.get('id'), indent + 1 )
            else:
                size = item.get( 'size', 0 )
                try:
                    size_bytes = int( size )
                except ( TypeError, ValueError ):
                    try:
                        size_bytes = int( float( size ) )
                    except Exception:
                        size_bytes = 0
                size_mb = size_bytes / ( 1024 * 1024 )
                print(f"{prefix}- {name} ({item.get('id')}) {size_mb:.2f} MB")
    else:
        print('Failed to list folder', folder_id)