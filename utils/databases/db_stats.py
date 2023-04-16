from . import database13, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database13)


@instance.register
class Stats(Document, GetDoc):
    id = IntField(attribute='_id', required=True)

    daily_messages = DictField(StrField(), IntField(), default={})
    weekly_messages = DictField(StrField(), IntField(), default={})
    monthly_messages = DictField(StrField(), IntField(), default={})
    yearly_messages = DictField(StrField(), IntField(), default={})

    class Meta:
        collection_name = 'Stats'
