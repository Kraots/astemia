from . import database4, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database4)


@instance.register
class Warns(Document, GetDoc):
    id = IntField(attribute='_id', required=True)

    warned_by = DictField(StrField(), IntField())

    warn_count = IntField()
    mute_streak = IntField()

    reset_warns = DateTimeField()
    reset_streak = DateTimeField()

    class Meta:
        collection_name = 'Warns'
