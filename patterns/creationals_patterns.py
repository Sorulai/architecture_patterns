from copy import deepcopy
from quopri import decodestring


class User:
    pass


class Customer(User):
    pass


class Manager(User):
    pass


class UserFactory:
    types = {
        'customer': Customer,
        'maanger': Manager
    }

    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


class ProductPrototype:

    def clone(self):
        return deepcopy(self)


class Product(ProductPrototype):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.products.append(self)


class PlayingProduct(Product):
    pass


class CollectProduct(Product):
    pass


class ProductFactory:
    types = {
        'playing': PlayingProduct,
        'collect': CollectProduct
    }

    @classmethod
    def create(cls, type_, name, category):
        print(type_)
        print(cls.types)
        return cls.types[type_](name, category)


class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.products = []

    def product_count(self):
        result = len(self.products)
        if self.category:
            result += self.category.product_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.customers = []
        self.managers = []
        self.products = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_product(type_, name, category):
        return ProductFactory.create(type_, name, category)

    def get_product(self, name):
        for item in self.products:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)
