from nanolib.abc import IRawConnection
from nanolib.network.connection.raw_connection import RawConnection
from nanolib.security.pnet.psk_conn import PskConn


def new_protected_conn(conn: RawConnection | IRawConnection, psk: str) -> PskConn:
    if len(psk) != 64:
        raise ValueError("Expected 32-byte pre shared key (PSK)")

    return PskConn(conn, psk)
