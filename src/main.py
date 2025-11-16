from fastapi import FastAPI, HTTPException
from typing import List
from bson import ObjectId
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError
from .models.corrida_model import Corrida, CorridaInDB
from .producer import publish_corrida_finalizada
from .database.mongo_client import get_mongo_db
from .database.redis_client import get_redis_client

app = FastAPI(
    title="Transflow API",
    description="API para gerenciamento de corridas e saldos de motoristas usando MongoDB e Redis."
)

@app.post("/corridas/", status_code=202, response_model=dict)
async def cadastrar_corrida(corrida: Corrida):
    try:
        await publish_corrida_finalizada(corrida)
        return {"status": "Corrida enviada para processamento.", "id_corrida": corrida.id_corrida}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao publicar corrida: {e}")
    
@app.get("/corridas/", response_model=List[CorridaInDB])
async def listar_corridas():
    mongo_db = await get_mongo_db()
    corridas_collection = mongo_db.corridas
    corridas_cursor = corridas_collection.find()
    corridas_list = await corridas_cursor.to_list(length=100)

    for corrida in corridas_list:
        corrida["_id"] = str(corrida["_id"])
    
    return corridas_list

@app.get("/corridas/{forma_pagamento}", response_model=List[CorridaInDB])
async def filtrar_corridas_por_pagamento(forma_pagamento: str):
    mongo_db = await get_mongo_db()
    corridas_collection = mongo_db.corridas
    corridas_cursor = corridas_collection.find({"forma_pagamento": forma_pagamento})
    corridas_list = await corridas_cursor.to_list(length=100)

    for corrida in corridas_list:
        corrida["_id"] = str(corrida["_id"])
    
    return corridas_list

@app.get("/saldo/{motorista}", response_model=dict)
async def consultar_saldo(motorista: str):
    redis = await get_redis_client()
    chave_saldo = f"saldo:{motorista.lower().replace(' ', '_')}"

    try:
        saldo = await redis.get(chave_saldo)
        if saldo is None:
            saldo = 0.0
        return {"motorista": motorista, "saldo": float(saldo)}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar saldo no Redis: {e}")
    
@app.on_event("startup")
async def startup_event():
    redis = await get_redis_client()
    await redis.set("saldo:carlaTeste", 100)
    await redis.set("saldo:joaoTeste", 250)
    print("Saldo inicial definido para motoristas de teste.")
