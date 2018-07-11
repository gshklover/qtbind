from PyQt5.QtCore import QAbstractListModel, QModelIndex

from qtbind.interfaces import IPropertyChanged, Event


class ViewModel(IPropertyChanged):
    """
    Base class for ModelView objects.
    Objects of this type expose data to Views and add additional sorting/filtering/formatting capabilities
    """
    def __init__(self, model=None):
        super().__init__()
        self._model = model

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, val):
        if val == self._model:
            return

        self._model = val
        self.property_changed.emit(None, None)


class ViewModelProperty:
    """
    Property descriptor for exposing model properties to ViewModel
    """
    def __init__(self, prop_name):
        super().__init__()
        self._prop_name = prop_name

    def __get__(self, instance, type=None):
        return getattr(instance.model, self._prop_name)

    def __set__(self, instance, value):
        if value != getattr(instance.model, self._prop_name):
            setattr(instance.model, self._prop_name, value)
            instance.property_changed.emit(self._prop_name, value)
        return value

    def __delete__(self, instance):
        delattr(instance.model, self._prop_name)
        instance.property_changed.emit(self._prop_name, None)


class IContainerViewModel:
    """
    Interface for containers of items.
    A VM container registers for change notification to contained items and emits item_property_changed() signal
    """
    def __init__(self):
        super().__init__()
        self.item_property_changed = Event()


class ListViewModel(QAbstractListModel, ViewModel, IContainerViewModel):
    """
    View model for wrapping lists
    """
    def __init__(self, model, init=None, data_delegate=None):
        """
        Wrap a list of VM objects
        :param model: list
        :param data_delegate: actual implementation responsible for rendering data
                              unfortunately, Qt VM implementation is not really a VM as it doesn't reuse
                              the model for different views. Here, we attempt to do so.
        """
        super().__init__(model=model)
        IContainerViewModel.__init__(self)

        self._list = init if init is not None else []
        self._data_delegate = data_delegate

        if len(self._list):
            for item in self._list:
                if isinstance(item, IPropertyChanged):
                    item.property_changed.connect(lambda x, y: self._on_item_property_changed(item, x, y))

    def append(self, obj):
        index = self.index(len(self._list), 0)
        self.beginInsertRows(index, index)
        self._list.append(obj)
        self._model.append(obj.model)
        if isinstance(obj, IPropertyChanged):
            obj.property_changed.connect(lambda x, y: self._on_item_property_changed(obj, x, y))
        self.endInsertRows()

    def remove(self, obj):
        try:
            index = self._list.index(obj)
        except ValueError:
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self._list.remove(obj)
        self._model.remove(obj.model)
        if isinstance(obj, IPropertyChanged):
            obj.property_changed.disconnect(lambda x, y: self._on_item_property_changed(obj, x, y))
        self.endRemoveRows()

    def __getitem__(self, item):
        return self._list[item]

    def __len__(self):
        return len(self._list)

    def data(self, index, role):
        """
        Overrides QAbstractListModel
        """
        if not index.isValid():
            return None

        if self._data_delegate is not None:
            obj = self._list[index.row()]
            res = self._data_delegate(obj, role)
            if res is not None:
                return res

        return None

    def rowCount(self, parent):
        return len(self._list)

    def _on_item_property_changed(self, item, prop, val):
        """
        Called when one of the item's properties changes
        """
        try:
            row = self._list.index(item)
        except:
            return
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)
        self.item_property_changed.emit(item, prop, val)
