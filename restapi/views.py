#from django.shortcuts import render
from rest_framework import viewsets, generics, permissions
from .models import Book, Deal, EmailUser
from .serializers import BookSerializer, DealSerializer, EmailUserSerializer
from django_filters import rest_framework as filters
from .permissions import IsStaffOrTargetUser
from . import authentication
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter
from rest_framework.decorators import detail_route
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from mail_templated import send_mail


class ObtainAuthToken(APIView):
    permission_classes = []
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = EmailUserSerializer(user)
        return Response({'token': token.key, 'user': user_serializer.data})


obtain_auth_token = ObtainAuthToken.as_view()

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = (SearchFilter,)
    search_fields = ('book_title','isbn')
    # This will allow the client to filter the items in the list by making queries such as: 
    # http://example.com/api/books?search=russell
    def get_permissions(self):
        # allow non-authenticated user to retrieve via GET
        return (permissions.AllowAny() if self.request.method == 'GET'
                        else IsStaffOrTargetUser()),

class BookDetail(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('user__email','book__isbn')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        creator = request.data["user"]
        book = request.data["book"]
        is_seller = request.data["is_seller"]
        try:
            deal = Deal.objects.filter(book = book ).exclude(is_seller = is_seller)[0]
            dealer = deal.user
            Deal.objects.get(pk=deal.id).delete()
            send_mail('email/deal.tpl', {'user': creator, 'other_user': dealer, 'book': book},
                                         'test@mail.com', [creator])
            send_mail('email/deal.tpl', {'user': dealer, 'other_user': creator, 'book': book}, 
                                        'test@mail.com', [dealer])
            return Response({"user": dealer.email}, status=status.HTTP_202_ACCEPTED)

        except IndexError:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)       

class DealForUser(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DealSerializer

    def get_queryset(self):
        user = self.request.user
        return Deal.objects.filter(dealer = user)

class UserView(viewsets.ModelViewSet):
    queryset = EmailUser.objects.all()
    serializer_class = EmailUserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('email','is_staff')

    @detail_route()
    def deal_of(self, request, pk = None):
        user = self.get_object()
        deal = Deal.objects.filter(dealer = user).distinct()
        deal_json = DealSerializer(deal,many = True)
        return Response(deal_json)

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (permissions.AllowAny() if self.request.method == 'POST'
                        else IsStaffOrTargetUser()),

