import os
import motor.motor_asyncio


key1 = os.getenv('MONGODBKEY1')
cluster1 = motor.motor_asyncio.AsyncIOMotorClient(key1)
database1 = cluster1['Ukiyo']  # Mainly stores intros

key2 = os.getenv('MONGODBKEY2')
cluster2 = motor.motor_asyncio.AsyncIOMotorClient(key2)
database2 = cluster2['Ukiyo']  # Mainly stores levels

key3 = os.getenv('MONGODBKEY3')
cluster3 = motor.motor_asyncio.AsyncIOMotorClient(key3)
database3 = cluster3['Ukiyo']  # Extra stuff (mutes, rules, etc...) | and as of recently, polls

key4 = os.getenv('MONGODBKEY4')
cluster4 = motor.motor_asyncio.AsyncIOMotorClient(key4)
database4 = cluster4['Ukiyo']  # AFKs and warns

key5 = os.getenv('MONGODBKEY5')
cluster5 = motor.motor_asyncio.AsyncIOMotorClient(key5)
database5 = cluster5['Ukiyo']  # Marriages

key6 = os.getenv('MONGODBKEY6')
cluster6 = motor.motor_asyncio.AsyncIOMotorClient(key6)
database6 = cluster6['Ukiyo']  # Game

key7 = os.getenv('MONGODBKEY7')
cluster7 = motor.motor_asyncio.AsyncIOMotorClient(key7)
database7 = cluster7['Ukiyo']  # Birthdays

key8 = os.getenv('MONGODBKEY8')
cluster8 = motor.motor_asyncio.AsyncIOMotorClient(key8)
database8 = cluster8['Ukiyo']  # Bad Words & Confesscord Restrictions

key9 = os.getenv('MONGODBKEY9')
cluster9 = motor.motor_asyncio.AsyncIOMotorClient(key9)
database9 = cluster9['Ukiyo']  # Reminders

key10 = os.getenv('MONGODBKEY10')
cluster10 = motor.motor_asyncio.AsyncIOMotorClient(key10)
database10 = cluster10['Ukiyo']  # Todos

key11 = os.getenv('MONGODBKEY11')
cluster11 = motor.motor_asyncio.AsyncIOMotorClient(key11)
database11 = cluster11['Ukiyo']  # Sober App

key12 = os.getenv('MONGODBKEY12')
cluster12 = motor.motor_asyncio.AsyncIOMotorClient(key12)
database12 = cluster12['Ukiyo']  # BDSM tests

key13 = os.getenv('MONGODBKEY13')
cluster13 = motor.motor_asyncio.AsyncIOMotorClient(key13)
database13 = cluster13['Ukiyo']  # Stats for the chart
