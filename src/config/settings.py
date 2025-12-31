import logging

DATABASE_URL = 'sqlite:///pypos.db'

def setup_logging():
    logging.basicConfig(level=logging.INFO, filename='logs/app.log', filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
