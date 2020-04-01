from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Tag, Ingredient, Recipe
from recipes import serializers


class BaseRecipeAttributeViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin
):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttributeViewSet):

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttributeViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def _query_param_to_ints(self, qp):
        return [int(str_id) for str_id in qp.split(',')]

    def get_queryset(self):
        qp_tags = self.request.query_params.get('tags')
        qp_ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset
        if qp_tags:
            tags = self._query_param_to_ints(qp_tags)
            queryset = queryset.filter(tags__id__in=tags)
        if qp_ingredients:
            ingredients = self._query_param_to_ints(qp_ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients)

        return queryset.filter(user=self.request.user).order_by('-title')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            res = Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            res = Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return res
