import uuid
from pydantic import BaseModel, Field

class Passageiro(BaseModel):
    nome: str
    telefone: str

class Motorista(BaseModel):
    nome: str
    nota: float

class Corrida(BaseModel):
    id_corrida: str = Field(default_factory=lambda: str(uuid.uuid4()))
    passageiro: Passageiro
    motorista: Motorista
    origem: str
    destino: str
    valor_corrida: float
    forma_pagamento: str

class CorridaInDB(Corrida):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {
            "id": lambda v: str(v)
        }