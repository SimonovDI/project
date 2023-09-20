import threading
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from .models import Product
#from .parser.engine.parser_excel import main as excel_main
#from .parser.engine.parser_html import main as html_main
from .serializer import ProductSerializer
from .parser.engine.parser_zaoksky import main as zaoksky_main


class ParserLoadData(APIView):
    """
    Загрузка данных с парсеров
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAuthenticated]
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, requests):
        def parse(parser):
            data = parser().parse()
            for item in data:
                if item['price']:
                    model, _ = Product.objects.update_or_create(name=item['name'],
                                                                description=item['description'],
                                                                link=item['link'],
                                                                defaults={
                                                                    'price': item['price'],
                                                                    'up_name': item['up_name']
                                                                }
                                                                )

        t1 = threading.Thread(target=parse, args=(excel_main,))
        t2 = threading.Thread(target=parse, args=(html_main,))
        t3 = threading.Thread(target=parse, args=(zaoksky_main,))
        t1.start()
        t2.start()
        t3.start()
        return Response('Парсеры запущены')


class BaseDataGET(generics.ListAPIView):
    """
        Просмотр JSON формата
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


    def get_queryset(self):
        """
        Выборка данных
        :return: список JSON
        """

        queryset = Product.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__istartswith=name.title())
        return queryset


class BaseDetail(generics.RetrieveDestroyAPIView):

    """
        Прочитать, удалить, изменить данные
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
