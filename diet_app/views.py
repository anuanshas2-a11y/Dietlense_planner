from django.shortcuts import render
from diet_app.models import *
from diet_app.serializers import *
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView,ListAPIView,DestroyAPIView
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from diet_app.utility_func import calculate_bmr
from diet_app.permissions import IsOwner
from django.utils import timezone
from django.db.models import Sum
from rest_framework.response import Response
# Create your views here.


class SignUpView(CreateAPIView):
    serializer_class=UserSerializer

class ProfileView(CreateAPIView):
    serializer_class=UserProfileSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def perform_create(self, serializer):
        user_object=self.request.user
        # data=serializer.validated_data
        # bmr=calculate_bmr(
        #     age=data.get('age'),
        #     weight=data.get('weight'),
        #     height=data.get('height'),
        #     gender=data.get('gender'),
        #     activity_level=data.get('activity_level'),
        
        # )
        return serializer.save(owner=user_object)

class ProfileRetrieveView(RetrieveAPIView,UpdateAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsOwner]
    serializer_class=UserProfileSerializer
    queryset=UserProfile.objects.all()

# class ProfileUpadteView(UpdateAPIView):
#     authentication_classes=[TokenAuthentication]
#     permission_classes=[IsOwner]
#     serializer_class=UserProfileSerializer
#     queryset=UserProfile.objects.all()


class UserRetriveView(RetrieveAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsOwner]
    serializer_class=UserSerializer
    queryset=CustomUser.objects.all()

class FoodCreateView(CreateAPIView,ListAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    serializer_class=FoodSerializer
    queryset=FoodLog.objects.all()

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

class FoodRetrieveView(RetrieveAPIView,UpdateAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    serializer_class=FoodSerializer
    queryset=FoodLog.objects.all()

class FoodDeleteView(DestroyAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsOwner]
    serializer_class=FoodSerializer
    queryset=FoodLog.objects.all()

class DietSummary(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsOwner]
    def get(self,request,*args,**kwargs):
        cur_date=timezone.now()
        queryset=FoodLog.objects.filter(created_at__date=cur_date,owner=request.user)
        calories_consumed=queryset.values("calories").aggregate(Sum('calories'))
        print(calories_consumed)
        print(request.user.profile.bmr)
        context={
            "total_calories_consumed":calories_consumed.get('calories__sum'),
            "daily_target":request.user.profile.bmr,
            "balance":request.user.profile.bmr-calories_consumed.get('calories__sum')
        }
        return Response (context)

