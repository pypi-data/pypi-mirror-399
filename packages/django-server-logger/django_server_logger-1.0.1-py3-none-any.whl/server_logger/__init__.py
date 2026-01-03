import sys, subprocess, argparse, os
from server_logger.utils import get_ipv4_addresses, files_exists
from pathlib import Path

__version__ = "1.0.1"
__all__ = ['main', '__version__']


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('port', type=int, default=8000, help="Прослушиваемый порт", nargs='?')
    parser.add_argument('--filename', '-f', type=str, default='server.log',
                        help="Имя файла лога", const=None, nargs='?')
    parser.add_argument('--cert-folder', '-c', type=str, default='certs',
                        help="Папка с сертификатами", nargs='?')
    parser.add_argument('--version', '-v', action='version', version=__version__, help="Показать версию и выйти")
    parser.add_argument('--rewrite-file', '--rewrite', '--write-file',
                        '--write', '-r', '-w', action="store_true", help="Перезаписать файл", dest='rewrite_file')
    parser.add_argument('--http', action='store_false', help="Использовать HTTP", dest='https')

    args, unknown = parser.parse_known_args()
    files_exists(args.cert_folder)
    port = args.port

    with open(args.filename, 'w' if args.rewrite_file else 'a', encoding='utf-8') as file:
        protocol = 'https://' if args.https else 'http://'

        process = subprocess.Popen(
            ['python', 'manage.py', 'runserver_plus'] + unknown,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        for line in process.stdout:
            print(line, end='')
            file.write(line)
            file.flush()

        for ip in get_ipv4_addresses():
            print('Running on ', protocol, ip, ':', port, '/', sep='')

        process.wait()


if __name__ == '__main__':
    main()