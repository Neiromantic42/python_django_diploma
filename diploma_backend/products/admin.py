from django.contrib import admin
from .models import Product, Category, Specification, Review, Tag, Image, Sale


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1

class SpecificationInline(admin.StackedInline):
    model = Specification
    extra = 1

class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0

class SaleInline(admin.StackedInline):
    model = Sale
    extra = 0
    max_num = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Product в админке.
    """
    list_display = (
        "id",
        "title",
        "category",
        "price",
        "count",
        "date",
        "short_description",
        "free_delivery",
        "product_tags",
        "rating",
        "is_popular",
        "is_limited",
        "archived"

    )
    list_filter = ("is_limited", "free_delivery", "category")
    search_fields = ("title", "description", "full_description")
    filter_horizontal = ("tags",)
    inlines = [
        ImageInline,
        SpecificationInline,
        SaleInline,
        ReviewInline
    ]

    @admin.display(description="краткое описание товара")
    def short_description(self, obj):
        if not obj.full_description:
            return ""
        if len(obj.full_description) <= 48:
            return obj.full_description
        return obj.full_description[:48] + "..."

    @admin.display(description="Теги")
    def product_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "image", "parent", "is_active")
    search_fields = ("title", "is_active")



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", )
    search_fields = ("name", )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("src", "alt")
    search_fields = ("alt", )

