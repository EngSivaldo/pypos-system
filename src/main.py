import logging
from src.config.settings import setup_logging

def main():
    setup_logging()
    print('Sistema PDV Iniciado...')

if __name__ == '__main__':
    main()