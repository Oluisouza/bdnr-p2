import os
from faststream.rabbit import RabbitBroker
from dotenv import load_dotenv
from .models.corrida_model import Corrida

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

broker = RabbitBroker(RABBITMQ_URL)

async def publish_corrida_finalizada(corrida: Corrida):
    print(f"Publicando corrida finalizada: {corrida.id_corrida} no tópico 'corridas.finalizadas'...")
    await broker.publish(corrida.model_dump_json(), "corridas.finalizadas")
    print(f"Corrida {corrida.id_corrida} publicada com sucesso.")
    