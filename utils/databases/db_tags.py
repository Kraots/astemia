from . import database4, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database4)


@instance.register
class Tags(Document, GetDoc):
    name = StrField(required=True)
    content = StrField(default='None')
    attachment = StrField(default='None')

    owned_by = IntField(required=True)
    created_at = DateTimeField(required=True)

    uses = IntField(default=0)

    class Meta:
        collection_name = 'Tags'
