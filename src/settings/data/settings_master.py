from configobj import ConfigObj
import copy
import atexit



class SettingsMasterStn:
    __instance = None
    settings_data = {}
    topics = []
    subscribers = {}


    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SettingsMasterStn, cls).__new__(cls)
            cls.atCreation()
            atexit.register(cls.atExit)
        return cls.__instance


    @classmethod
    def atCreation(cls):
        config = ConfigObj('settings.ini')
        cls.settings_data = config.dict()
        cls.topics = cls.settings_data.keys()
        for item in cls.settings_data.keys():
            cls.subscribers[item] = []


    @classmethod
    def atExit(cls):
        config = ConfigObj(cls.settings_data)
        config.filename = 'settings.ini'
        config.write()


################################## INTERFACING ####################################################
    @classmethod
    def subscribe(cls, topic:list|str, fn) -> None:
        if type(topic) == str:
            if topic not in cls.topics:
                return
            if fn in cls.subscribers[topic]:
                return
            cls.subscribers[topic].append(fn)

        elif type(topic) == list:
            for item in topic:
                cls.subscribe(item , fn)

        else:
            raise Exception(f'the variable type {type(topic)} is not supported for subscription.')
        
    
    @classmethod
    def unsubscribe(cls, topic:list|str, fn) -> None:
        if type(topic) == str:
            if topic not in cls.topics:
                return
            if fn not in cls.subscribers[topic]:
                return
            cls.subscribers[topic].remove(fn)

        elif type(topic) == list:
            for item in topic:
                cls.unsubscribe(item , fn)

        else:
            raise Exception(f'the variable type {type(topic)} is not supported for unsubscription.')


    @classmethod
    def getData(cls) -> dict:
        return copy.deepcopy(cls.settings_data)


    @classmethod
    def updateData(cls, new_data:dict) -> dict:
        dta = copy.deepcopy(cls.settings_data)
        dta.update(new_data)

        modified_settings = []
        for item in dta.keys():
            old_setting = cls.settings_data[item]
            new_setting = dta[item]
            if old_setting != new_setting:
                modified_settings.append(item)
                cls.settings_data[item] = new_setting

        for item in modified_settings:
            for fn in cls.subscribers[item]:
                fn()
        print(modified_settings)


    @classmethod
    def getSpecific(cls, topic:str) -> str:
        return cls.settings_data.get(topic, None)
    

    @classmethod
    def setSpecific(cls, topic:str, value:str, notify:bool=True) -> bool:
        ''' updates the value of `topic` to `value`. if the topic exists, return `True`, otherwise `False`. '''
        if topic in cls.topics:
            cls.settings_data[topic] = value

            if not notify:
                return True

            for fn in cls.subscribers[topic]:
                fn()
            return True
        
        return False