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

    def _get_or_create_tags(self, recipe: Recipe, tags: list[dict]) -> None:
        auth_user: User = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data: dict) -> Recipe:
        tags: list[dict] = validated_data.pop('tags', [])
        recipe: Recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe=recipe, tags=tags)

        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        tags: list[dict] | None = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(recipe=instance, tags=tags)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
