from framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html',
                                object_list={'date': request.get('date', None), "title": "Онлайн-магазин фигурок"})


class About:
    def __call__(self, request):
        print(request.get('request_params').get('comment'))
        return '200 OK', render('contact.html',
                                object_list={'date': request.get('date', None), "title": "Контакты"})
