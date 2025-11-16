import os
import json
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from dotenv import load_dotenv
from .database.redis_client import get_redis_client
from .database.mongo_client import get_mongo_db
from .models.corrida_model import Corrida

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

broker = RabbitBroker(RABBITMQ_URL)
app = FastStream(broker)

@broker.subscriber("corridas.finalizadas")
async def handle_corrida_finalizada(msg: str):
    try:
        print("Mensagem recebida do tópico 'corridas.finalizadas'. Processando...")
        corrida_data = json.loads(msg)
        corrida = Corrida(**corrida_data)

        print(f"Consumindo corrida finalizada: {corrida.id_corrida}")

        redis = await get_redis_client()
        motorista_nome = corrida.motorista.nome.lower().replace(" ", "_")
        chave_saldo = f"saldo:{motorista_nome}"
        
        novo_saldo = await redis.incrbyfloat(chave_saldo, corrida.valor_corrida)

        print(f"Saldo atualizado para o motorista {corrida.motorista.nome}: R$ {novo_saldo:.2f}")

        mongo_db = await get_mongo_db()
        corridas_collection = mongo_db.corridas
        await corridas_collection.insert_one(corrida.model_dump())

        print(f"Corrida {corrida.id_corrida} armazenada no MongoDB com sucesso.")
    
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a mensagem JSON: {e}")
    except Exception as e:
        print(f"Erro ao processar a corrida finalizada: {e}")