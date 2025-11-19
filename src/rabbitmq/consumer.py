import asyncio
import json
import os
import aiohttp
from faststream import FastStream, AckPolicy
from faststream.rabbit import RabbitBroker, RabbitQueue
from faststream.rabbit import Channel
from faststream.rabbit.annotations import RabbitMessage

import config
from s3.downloader_pdf import download_pdf_from_message

# print(f"amqp://{config.RABBITMQ_LOG}:{config.RABBITMQ_PASS}@localhost:5672/")
UPLOAD_URL = "http://localhost:8000/api/upload"

channel_settings = Channel(prefetch_count=1, global_qos=True, publisher_confirms=True)

queue = RabbitQueue("doc_parsing", durable=True)
broker = RabbitBroker(
    url=f"amqp://{config.RABBITMQ_LOG}:{config.RABBITMQ_PASS}@10.146.33.66:5672/",
    # host="10.146.33.66",
    port=5672,
    virtualhost="infohub",
    default_channel=channel_settings,
)
app = FastStream(broker)


@broker.subscriber(
    queue=queue,
    ack_policy=AckPolicy.MANUAL,
    # prefetch_count=BATCH_SIZE  # Ограничиваем количество одновременно обрабатываемых сообщений
)  # MANUAL ACK_FIRST
async def handle_orders_and_send_message(msg: RabbitMessage):  # body: dict,
    try:
        data = json.loads(msg.body.decode())  # ← ключевой момент
        print("Получено:", data)

        file = data["file"]  # теперь работает
        card_id = data["cardId"]

        print("Файл:", file)
        print("cardId:", card_id)

        # скачиваем PDF и получаем путь к временному файлу
        local_path = await download_pdf_from_message(
            data
        )  # тут уже всё скачивается в downloads с рандомным именем

        # формируем данные для FastAPI /upload
        document_id = str(card_id)
        form_data = aiohttp.FormData()
        form_data.add_field(
            "file",
            open(local_path, "rb"),
            filename=os.path.basename(local_path),
            content_type="application/pdf",
        )
        form_data.add_field("documentId", document_id)

        # отправляем на FastAPI
        async with aiohttp.ClientSession() as session:
            async with session.post(UPLOAD_URL, data=form_data) as resp:
                if resp.status == 200:
                    print(f"Файл {local_path} успешно отправлен на /upload")
                    await msg.ack()
                else:
                    print(f"Ошибка при отправке файла: {resp.status}")
                    await msg.nack()

        # удаляем временный файл после обработки
        if os.path.exists(local_path):
            os.remove(local_path)

    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        await msg.nack()


asyncio.run(app.run())
