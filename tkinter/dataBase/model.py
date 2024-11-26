# ====================
#  - Librerias -
# ====================
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Obtener el directorio actual del script

db_path = "dataBase.db"

# Definir la clase base para las clases de modelo
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    user = Column(String)
    foto = Column(String)
    medicamentos = relationship("Medicamento", back_populates="usuario")

class Medicamento(Base):
    __tablename__ = "medicamento"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuario.id'))
    medicamento = Column(String)
    horario = Column(String)
    usuario = relationship("Usuario", back_populates="medicamentos")
 

# Crear la conexión a la base de datos
engine = create_engine(f"sqlite:///{db_path}")

# Crear la tabla en la base de datos
Base.metadata.create_all(engine)