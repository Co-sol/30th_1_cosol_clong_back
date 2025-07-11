from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .serializers import (
    SpaceCreateSerializer,
    SpaceResponseSerializer,
    SpaceUpdateSerializer,
)
from .models import Space
from groups.models import Group


# 루트에서 공간 생성
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
        # 여러 공간 한꺼번에 DB 저장
        response_data = SpaceResponseSerializer(created, many=True).data

        return Response(
            {
                "success": True,
                "message": "공간 생성에 성공하였습니다.",
                "data": {"root": response_data},
            },
            status=status.HTTP_201_CREATED,
        )


# 루트에서 공간 수정/삭제
class SpaceRUDAPIView(RetrieveUpdateDestroyAPIView):
    # Update, Delete만 있음

    permission_classes = [IsAuthenticated]
    # URL에서 받아올 space_id를 기준으로 함
    lookup_field = "space_id"
    lookup_url_kwarg = "space_id"
    queryset = Space.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() in ("patch"):
            return SpaceUpdateSerializer
        return SpaceResponseSerializer

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            space_id = self.kwargs.get("space_id")
            raise NotFound(
                {
                    "success": True,
                    "errorCode": "SPACE_NOT_FOUND",
                    "message": f"해당 ID에 해당하는 공간이 존재하지 않습니다. {space_id}",
                }
            )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "공간이 성공적으로 수정되었습니다",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "공간이 성공적으로 삭제되었습니다",
                "data": {},
            },
            status=status.HTTP_204_NO_CONTENT,
        )
