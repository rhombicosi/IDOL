from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ScalarizationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('scalarizations', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('scalarizations', self.channel_name)

    async def send_scalarizations(self, event):
        # message = {'id': event['task_id'], 'p_pk': event['problem_pk'], 'status': event['task_status']}
        # message = {'id': event['task_id'], 'status': event['task_status'], 'p_pk': event['problem_pk']}
        message = event['text']
        json_message = json.dumps(message, indent=4)

        await self.send(json_message)

