from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    """
    Модель Product представляет товар
    """
    title = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    full_description = models.TextField()
    free_delivery = models.BooleanField(default=False)
    tags = models.ManyToManyField(
        'Tag', blank=True, related_name='images',
        verbose_name="связь многие ко многим с тегом продукта")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )
    is_limited = models.BooleanField(default=False)
    sort_index = models.PositiveIntegerField(
        default=50,
        verbose_name="Индекс популярности товара",
        help_text="Чем меньше значение, тем выше товар в топе."
                  " При одинаковом индексе учитывается количество покупок."
    )
    purchases_count = models.PositiveIntegerField(
        default=0,
        verbose_name="количество покупок",
        help_text="Автоматически увеличивается при каждой покупке."
                  " Редактировать вручную не требуется."
                  " Но если очень хочется то можно."
    )
    archived = models.BooleanField(
        default=False,
        verbose_name="Архивация товара (скрыт/доступен для продажи)",
        help_text = "Если включено, товар считается архивным и не отображается в каталоге для покупателей",
    )
    is_banner = models.BooleanField(
        default=False,
        verbose_name="Продающие товары (banners)",
        help_text="Если включено, товар попадает в блок banners на главной странице."
                  " Он же считается рекламным, продающим."
    )


    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


    def __str__(self):
        return self.title


class Category(models.Model):
    """
    Модель Category представляет категории товара
    """
    title = models.CharField(max_length=100)
    image = models.ForeignKey(
        "Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subcategories',
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активная категория",
        help_text="Если True, категория отображается на сайте."
                  " Если False — архивируется и не показывается."
    )


    def __str__(self):
        return self.title


class Specification(models.Model):
    """
    Характеристика товара
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications"
    )
    name = models.CharField(max_length=255, verbose_name="Название характеристики")
    value = models.CharField(max_length=1500, verbose_name="Полная характеристика товара")


    class Meta:
        verbose_name = "Specification"
        verbose_name_plural = "Specifications"


    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    """
    Модель Review - представляет собой отзывы на товар
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Связь с продуктом"
    )
    author = models.CharField(max_length=255)
    email = models.EmailField()
    text = models.TextField(verbose_name="Текст самого отзыва")
    rate = models.PositiveSmallIntegerField(
        verbose_name="оценка, например от 1 до 5",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"


    def __str__(self):
        return f"Review by {self.author} for {self.product.title}"


class Tag(models.Model):
    """
    Модель Tag - представляет тег товара(пример: "Gamin", "RGB", ""Sale)
    """
    name = models.CharField(max_length=25, unique=True, verbose_name="Название тега")


    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


    def __str__(self):
        return self.name

class Image(models.Model):
    """
    Модель Image представляет собой картинки товаров
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Связь с продуктом: один ко многим",
        null=True,
        blank=True,

    )
    src = models.ImageField(upload_to='images/', verbose_name="Ссылка где лежит картинка")
    alt = models.CharField(max_length=255, blank=True, verbose_name="Текстовое описание картинки")


    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"


    def __str__(self):
        return self.alt or self.src.name


class Sale(models.Model):
    """
    Модель Sale - представляет собой скидку на товар
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Связь с моделью продуктов, один к одному"
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена на товар со учетом скидки"
    )
    date_from = models.DateField(verbose_name="Дата начала акции\скидки")
    date_to = models.DateField(verbose_name="Дата конца акции\скидки")


    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"


    def __str__(self):
        return f"Sale for {self.product.title}"