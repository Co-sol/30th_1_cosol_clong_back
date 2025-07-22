from calendar import c
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .serializers import (
    SpaceCreateSerializer,
    SpaceResponseSerializer,
    SpaceInfoSerializer,
    SpaceUpdateSerializer,
    ItemCreateSerializer,
    ItemResponseSerializer,
    ItemUpdateSerializer,
    ChecklistIdSerializer,
)
from .models import Space, Item
from checklists.models import Checklist
from groups.models import Group


# 루트에서 공간 생성
class SpaceCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpaceCreateSerializer

    def post(self, request):
        try:
            user = request.user
            if user.group is None:
                raise Group.DoesNotExist
            group = user.group
        except Group.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "GROUP_NOT_FOUND",
                    "message": "해당 사용자는 그룹에 속해 있지 않습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(
            data=request.data, many=True, context={"group": group}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
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

        checklists = [
            Checklist(space_id=space, total_count=0, completed_count=0)
            for space in created
        ]
        created_checklists = Checklist.objects.bulk_create(checklists)  # 선언 추가

        response_data = SpaceResponseSerializer(created, many=True).data
        checklist_response_data = ChecklistIdSerializer(
            created_checklists, many=True
        ).data  # 추가

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


# 아이템 생성
class ItemCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemCreateSerializer

    def post(self, request, space_id):
        try:
            space = Space.objects.get(space_id=space_id)
        except Space.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "SPACE_NOT_FOUND",
                    "message": f"해당 ID에 해당하는 부모 공간이 존재하지 않습니다. {space_id}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(
            data=request.data, many=True, context={"space": space}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": "공간 생성에 실패하였습니다.",
                    "data": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = [Item(parent_space=space, **data) for data in serializer.validated_data]
        created = Item.objects.bulk_create(items)
        # 여러 공간 한꺼번에 DB 저장
        response_data = ItemResponseSerializer(created, many=True).data

        return Response(
            {
                "success": True,
                "message": "아이템 생성에 성공하였습니다.",
                "data": {"items": response_data},
            },
            status=status.HTTP_201_CREATED,
        )


# 루트에서 공간 수정/삭제
class ItemRUDAPIView(RetrieveUpdateDestroyAPIView):
    # Update, Delete만 있음

    permission_classes = [IsAuthenticated]
    # URL에서 받아올 space_id를 기준으로 함
    lookup_field = "item_id"
    lookup_url_kwarg = "item_id"
    queryset = Item.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() in ("patch"):
            return ItemUpdateSerializer
        return ItemResponseSerializer

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            item_id = self.kwargs.get("item_id")
            raise NotFound(
                {
                    "success": True,
                    "errorCode": "ITEM_NOT_FOUND",
                    "message": f"해당 ID에 해당하는 아이템이 존재하지 않습니다. {item_id}",
                }
            )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "아이템이 성공적으로 수정되었습니다",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "아이템이 성공적으로 삭제되었습니다",
                "data": {},
            },
            status=status.HTTP_204_NO_CONTENT,
        )


# 공간 목록 조회
class SpaceInfoView(GenericAPIView):
    serializer_class = SpaceInfoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            user = request.user
            if user.group is None:
                raise Group.DoesNotExist
            group = user.group
            spaces = Space.objects.filter(group=group)
            serializer = self.get_serializer(spaces, many=True)

            return Response(
                {
                    "success": True,
                    "message": "공간 목록 조회에 성공했습니다.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Group.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "GROUP_NOT_FOUND",
                    "message": "해당 사용자는 그룹에 속해 있지 않습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
