from rest_framework import serializers
from core.models import Recipe, Tag, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_field = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    tags: TagSerializer = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',
        ]
        read_only_fields = ['id']

    def create(self, validated_data: dict) -> Recipe:
        tags: list[dict] = validated_data.pop('tags', [])
        recipe: Recipe = Recipe.objects.create(**validated_data)
        auth_user: User = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
