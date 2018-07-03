# qtbind
Simple, two-way data bindings support for View/Model/ViewModel design pattern with PyQt.

The package defines two major interfaces:
* IPropertyChanged that exposes "property_changed" signal
* View - an object that manages bindings of child widget properties to specified object properties.

### Example
```python
class Person(IPropertyChange):
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, val):
        self._name = val
        self.property_changed.emit('name', val)
    

class PersonView(QWidget, View):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self._name_edit = QLineEdit()
        # bind widget property to data context property:
        self.bind(self._name_edit, "text", "name")
        
def main():
    v = PersonView()
    v.context = Person()
    

```

Additionally, there is customized load_ui() method implementation that supports loading .ui files with custom < binding > elements.
The attributes of the _binding_ element:
 * path - data property name
 * mode - one of READ, WRITE or READ_WRITE. _default_: READ_WRITE

### Example
```xml
    <QLineEdit>
        <property name="text">
            <binding path="name" mode="READ"/>        
        </property>    
   </QLineEdit>
```