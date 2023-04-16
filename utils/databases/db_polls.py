from . import database3, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class Poll(Document, GetDoc):
    message_id = IntField(required=True, attribute='_id')

    title = StrField(required=True)
    options = ListField(StrField(), required=True)
    votes = ListField(IntField(), required=True)
    voted = ListField(IntField(), required=True)

    min_choices = IntField(required=True)
    max_choices = IntField(required=True)

    expire_date = DateTimeField(required=True)

    class Meta:
        collection_name = 'Polls'
