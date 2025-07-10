from turtle import st
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from .serializers import SpaceCreateSerializer, SpaceResponseSerializer
from .models import Space
from groups.models import Group


# Create your views here.
class SpaceCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpaceCreateSerializer

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        serializer = self.get_serializer(
            data=request.data, many=True, context={"group": group}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except serializer.ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": "공간 생성에 실패하였습니다.",
                    "data": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        spaces = [Space(group=group, **data) for data in serializer.validated_data]
        created = Space.objects.bulk_create(spaces)

        response_data = SpaceResponseSerializer(created, many=True).data

        return Response(
            {
                "success": True,
                "message": "공간 생성에 성공하였습니다.",
                "data": {"root": response_data},
            },
            status=status.HTTP_201_CREATED,
        )
