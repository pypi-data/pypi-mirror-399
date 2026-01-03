import socket
from dataclasses import dataclass
from pathlib import Path


def get_ipv4_addresses(exclude_localhost: bool = False) -> list:
    """Получить все IPv4 адреса локального хоста"""
    ip_addresses = []

    # Получаем имя хоста
    hostname = socket.gethostname()

    try:
        # Получаем все IP адреса, связанные с хостом
        addresses = socket.getaddrinfo(hostname, None)

        for addr_info in addresses:
            # addr_info[0] - семейство адресов (AF_INET для IPv4)
            # addr_info[4][0] - IP адрес
            if addr_info[0] == socket.AF_INET:  # IPv4
                ip = addr_info[4][0]
                if ip not in ip_addresses and (ip != '127.0.0.1' or not exclude_localhost):
                    ip_addresses.append(ip)

    except socket.gaierror:
        pass

    # Если не нашли адресов, пробуем другой способ
    if not ip_addresses:
        try:
            # Создаем временный сокет для получения локального IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))  # Подключаемся к внешнему серверу
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip != '127.0.0.1' or not exclude_localhost:
                ip_addresses.append(local_ip)
        except:
            pass

    return ip_addresses


@dataclass(frozen=True)
class PemFiles:
    cert: str
    key: str


def files_exists(cert_folder: str) -> None:
    cert_folder_obj = Path(cert_folder)
    cert_pem = cert_folder_obj / 'cert.pem'
    key_pem = cert_folder_obj / 'key.pem'
    if not os.path.isfile('manage.py'):
        raise FileNotFoundError('manage.py not found')
    elif not cert_folder_obj.is_dir():
        raise NotADirectoryError(f'folder {cert_folder} not found')
    elif not cert_pem.is_file():
        raise FileNotFoundError('cert.pem not found')
    elif not key_pem.is_file():
        raise FileNotFoundError('key.pem not found')
