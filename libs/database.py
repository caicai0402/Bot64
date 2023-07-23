from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult

from libs.flag import PenaltyPolicyFlag

class Database:
    client = None
    db = None

    def __init__(self, endpoint: str=None) -> None:
        if Database.client == None and endpoint != None:
            Database.client = self.__connect(endpoint=endpoint)
            Database.db = Database.client['bot64']
        self.db = Database.db

    def __connect(self, endpoint: str) -> MongoClient:
        client = MongoClient(host=endpoint)
        client.admin.command('ping') # Raises error if failed
        print('Successfully connected to MongoDB.')
        return client
    
    ''' Private setters and getters '''

    def __get_guild_collection(self) -> Collection:
        return self.db['guild']

    def __insert_guild_document(self, document: dict) -> InsertOneResult:
        return self.__get_guild_collection().insert_one(document=document)

    def __get_guild_document(self, guild_id: str) -> Optional[dict]:
        return self.__get_guild_collection().find_one(filter={ '_id': guild_id })

    def __update_guild_document(self, guild_id: str, update: dict) -> UpdateResult:
        return self.__get_guild_collection().update_one(filter={ '_id': guild_id }, update=update)

    ''' Public setters and getters '''

    def init_guild_config(self, guild_id: str) -> InsertOneResult:
        new_config = {
            '_id': guild_id,
            'log_channel_id': None,
            'mute_role_id': None,
            'suspicious_policy': PenaltyPolicyFlag.Ignore.value,
            'malicious_policy': PenaltyPolicyFlag.Mute.value,
        }
        insertOneResult = self.__insert_guild_document(document=new_config)
        if insertOneResult.inserted_id != guild_id:
            raise Exception('Failed to initialize guild config.')
        return insertOneResult

    def get_guild_config(self, guild_id: str) -> dict:
        config = self.__get_guild_document(guild_id=guild_id)
        if config == None:
            self.init_guild_config(guild_id)
            config = self.__get_guild_document(guild_id=guild_id)
            if config == None:
                raise Exception('Failed to fetch guild config.')

        config['suspicious_policy'] = PenaltyPolicyFlag(config['suspicious_policy'])
        config['malicious_policy'] = PenaltyPolicyFlag(config['malicious_policy'])
        return config
    
    def update_guild_config(self, guild_id: str, update: dict) -> UpdateResult:
        self.get_guild_config(guild_id=guild_id) # Make sure guild configuration exists
        return self.__update_guild_document(guild_id=guild_id, update=update)
    
    def get_log_channel_id(self, guild_id: str) -> Optional[int]:
        return self.get_guild_config(guild_id=guild_id)['log_channel_id']
    
    def set_log_channel_id(self, guild_id: str, log_channel_id: Optional[int]) -> UpdateResult:
        return self.update_guild_config(guild_id=guild_id, update={ '$set': { 'log_channel_id': log_channel_id } })
    
    def get_mute_role_id(self, guild_id: str) -> Optional[int]:
        return self.get_guild_config(guild_id=guild_id)['mute_role_id']

    def set_mute_role_id(self, guild_id: str, mute_role_id: Optional[int]) -> UpdateResult:
        return self.update_guild_config(guild_id=guild_id, update={ '$set': { 'mute_role_id': mute_role_id } })
    
    def get_suspicious_policy(self, guild_id: str) -> PenaltyPolicyFlag:
        return self.get_guild_config(guild_id=guild_id)['suspicious_policy']

    def set_suspicious_policy(self, guild_id: str, suspicious_policy: PenaltyPolicyFlag) -> UpdateResult:
        return self.update_guild_config(guild_id=guild_id, update={ '$set': { 'suspicious_policy': suspicious_policy.value } })
    
    def get_malicious_policy(self, guild_id: str) -> PenaltyPolicyFlag:
        return self.get_guild_config(guild_id=guild_id)['malicious_policy']

    def set_malicious_policy(self, guild_id: str, malicious_policy: PenaltyPolicyFlag) -> UpdateResult:
        return self.update_guild_config(guild_id=guild_id, update={ '$set': { 'malicious_policy': malicious_policy.value } })
