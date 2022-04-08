from datetime import date
from views import Index, About, CreateCategory, CategoryList, CreateProduct, ProductsList, CopyProduct


def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/contact/': About(),
    '/create-category/': CreateCategory(),
    '/category-list/': CategoryList(),
    '/create-product/': CreateProduct(),
    '/products-list/': ProductsList(),
    '/copy-product/': CopyProduct(),


}
