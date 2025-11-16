import os
import json
from faststream.rabbit import RabbitBroker
from dotenv import load_dotenv
from .database.redis_client import redis_client
from .database.mongo_client import get_mongo_db
from .models.corrida_model import Corrida

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

broker = RabbitBroker(RABBITMQ_URL)

@broker.subscribe("corridas_finalizadas")
async def handle_corrida_finalizada(msg: str):
    try:
        print("Mensagem recebida no tópico 'corridas_finalizadas'. Processando...")
        corrida_data = json.loads(msg)
        corrida = Corrida(**corrida_data)

        print(f"Consumindo corrida finalizada: {corrida.id_corrida}")

        motorista_nome = corrida.motorista.nome.lower().replace(" ", "_")
        chave_saldo = f"saldo:{motorista_nome}"
        novo_saldo = await redis_client.incrbyfloat(chave_saldo, corrida.valor_corrida)

        print(f"Saldo atualizado para o motorista {corrida.motorista.nome}: R$ {novo_saldo:.2f}")

        mongo_db = await get_mongo_db()
        corridas_collection = mongo_db.corridas
        await corridas_collection.insert_one(corrida.model_dump())

        print(f"Corrida {corrida.id_corrida} armazenada no MongoDB com sucesso.")
    
    except Exception as e:
        print(f"Erro ao processar a corrida finalizada: {e}")