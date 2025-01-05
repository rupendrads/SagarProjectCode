class ConfigurableObject:
    def __init__(self, **kwargs):
        # Unpack kwargs and set them as attributes of the instance
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def display_attributes(self):
        # Display all the attributes set on this instance
        for attr, value in self.__dict__.items():
            print(f"{attr} = {value}")

# Usage
config_obj = ConfigurableObject(name="John Doe", age=32, occupation="Developer")

config_obj.display_attributes()
