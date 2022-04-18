from datetime import date

from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, ListView, CreateView, BaseSerializer
from patterns.creationals_patterns import Engine, Logger, MapperRegistry
from framework.templator import render
from patterns.structural_patterns import AppRoute, Debug
from patterns.system_patterns import UnitOfWork

site = Engine()
logger = Logger('main')
routes = {}
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html',
                                object_list={'date': request.get('date', None), "title": "Онлайн-магазин фигурок",
                                             "categories": site.categories})


@AppRoute(routes=routes, url='/contact/')
class About:
    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('contact.html',
                                object_list={'date': request.get('date', None), "title": "Контакты"})


@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @Debug(name='CreateCategory')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            category_id = data.get('category_id')
            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)
            site.categories.append(new_category)
            return '200 OK', render('index.html',
                                    object_list={'date': request.get('date', None), "title": "Онлайн-магазин фигурок",
                                                 "categories": site.categories})
        else:
            categories = site.categories
            return '200 OK', render('create_category.html',
                                    categories=categories, object_list={"title": "Онлайн-магазин фигурок"})


@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    @Debug(name='CategoryList')
    def __call__(self, request):
        # logger.log('Список категорий')
        return '200 OK', render('category_list.html',
                                objects_list=site.categories, object_list={"title": "Онлайн-магазин фигурок"})


@AppRoute(routes=routes, url='/create-product/')
class CreateProduct:
    category_id = -1

    @Debug(name='CreateProduct')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))
                product = site.create_product(category.name, name, category)
                product.observers.append(email_notifier)
                product.observers.append(sms_notifier)
                site.products.append(product)

            return '200 OK', render('product_list.html',
                                    objects_list=category.products,
                                    name=category.name,
                                    id=category.id, object_list={"title": "Онлайн-магазин фигурок"})

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_product.html',
                                        name=category.name,
                                        id=category.id, object_list={"title": "Онлайн-магазин фигурок"})
            except KeyError:
                return '200 OK', 'No categories have been added yet'


@AppRoute(routes=routes, url='/products-list/')
class ProductsList:
    @Debug(name='ProductsList')
    def __call__(self, request):
        # logger.log('Список курсов')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('product_list.html',
                                    objects_list=category.products,
                                    name=category.name, id=category.id, object_list={"title": "Онлайн-магазин фигурок"})
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@AppRoute(routes=routes, url='/copy-product/')
class CopyProduct:
    @Debug(name='CopyProduct')
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_product = site.get_product(name)
            if old_product:
                new_name = f'copy_{name}'
                new_product = old_product.clone()
                new_product.name = new_name
                site.products.append(new_product)

            return '200 OK', render('product_list.html',
                                    objects_list=site.products,
                                    name=new_product.category.name, object_list={"title": "Онлайн-магазин фигурок"})
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@AppRoute(routes=routes, url='/customer-list/')
class StudentListView(ListView):
    template_name = 'customer_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('customer')
        return mapper.all()


@AppRoute(routes=routes, url='/create-customer/')
class StudentCreateView(CreateView):
    template_name = 'create_customer.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('customer', name)
        site.customers.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add-customer/')
class AddStudentByCourseCreateView(CreateView):
    template_name = 'add_customer.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['products'] = site.products
        context['customers'] = site.customers
        return context

    def create_obj(self, data: dict):
        course_name = data['course_name']
        course_name = site.decode_value(course_name)
        course = site.get_product(course_name)
        student_name = data['student_name']
        student_name = site.decode_value(student_name)
        student = site.get_customer(student_name)
        course.add_student(student)


@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='CourseApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.products).save()
