from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos (ajusta la URL según tu base de datos)
DATABASE_URL = "sqlite:///dbpasskeeper2.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
