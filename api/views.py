from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Q
from .models import User, FriendRequest
from .serializers import UserSerializer, RegisterSerializer, FriendRequestSerializer
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from datetime import timedelta

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Ensure the email is in lowercase
        request.data['username'] = request.data.get('username', '').lower()
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if '@' in query:
            return User.objects.filter(email__iexact=query)
        else:
            #if we want to seach on username as well
            #return User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))
            return User.objects.filter(Q(email__icontains=query))

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user')
        if from_user.id == to_user_id:
            return Response({'error': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        to_user = User.objects.get(id=to_user_id)
        
        # Check if a friend request is already sent and pending
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'A friend request is already sent to this user and is pending.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has sent more than 3 friend requests in the last minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count()
        if recent_requests_count >= 3:
            return Response({'error': 'You cannot send more than 3 friend requests within a minute.'}, status=status.HTTP_400_BAD_REQUEST)

        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({'status': 'request sent'}, status=status.HTTP_201_CREATED)


    def put(self, request, pk):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request ID not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the request is for the current user
        if friend_request.to_user != request.user:
            return Response({'error': 'You are not authorized to accept or reject this friend request.'}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')
        if action == 'accept':
            from_user = friend_request.from_user
            to_user = friend_request.to_user
            from_user.friends.add(to_user)
            to_user.friends.add(from_user)
            friend_request.delete()
            return Response({'status': 'request accepted'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            friend_request.delete()
            return Response({'status': 'request rejected'}, status=status.HTTP_200_OK)


class FriendListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        return user.friends.all()

class PendingFriendRequestView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return user.received_requests.all()
