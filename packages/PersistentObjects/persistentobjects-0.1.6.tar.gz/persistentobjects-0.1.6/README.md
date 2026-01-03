This is a very simple lib that provides the PersistantObject class, which saves all its attributes to the given json file. Exceptions are attributes suffixed with '_'.
Attributes are saved as soon as they are set.

[!IMPORTANT]
> morphing actions like appending, inserting, extending, etc. will not automaticly save!
> so its recomended to create a temp var, then append to it and at the end set the PersistantObject attr to the temp var.

with namespace(NAME) seperate sub namespaces can be created inside the object. 


## Usage example:
```python

from PersistantObject import PersistantObject

pobject = PersistantObject("save.json")

pobject.first_value = 10
pobject.second_value = "foo"

namespace = pobject.namespace("test_namespace") # creates a new namespace (new subdict in json)
namespace.third_value = [10, 5]


print(pobject.test_namespace.third_value) # alternate way to access namespaces

pobject.temp_ = True # suffixed with '_' so it will not be saved and behaves like a normal attribute.
```
