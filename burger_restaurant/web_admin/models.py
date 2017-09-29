from django.db import models
from django.db.models.signals import post_save, post_delete


class Restaurant(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    address = models.TextField(unique=True)

    def __str__(self):
        return 'Ресторан %s' % self.name

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)

    def __str__(self):
        return 'Категория %s' % self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, unique=True, blank=True)

    def __str__(self):
        return 'Подкатерория %s категории %s' % (self.name,
                                                 self.category.name)

    class Meta:
        verbose_name = 'Подкатерория'
        verbose_name_plural = 'Подкатерории'


class Dish(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=True)
    price = models.FloatField(default=0.0)
    category = models.ForeignKey(Category)
    subcategory = models.ForeignKey(Subcategory)

    def __str__(self):
        return 'Блюдо %s ценой %.2f' % (self.name, self.price)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def save(self, *args, **kwargs):
        super(Dish, self).save(*args, **kwargs)


class Order(models.Model):
    operator = models.CharField(max_length=256)
    restaurant = models.ForeignKey(Restaurant)
    total_price = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    status = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return 'Заказ №%d со статусом %s' % (self.id, self.status)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)


class DishesInOrder(models.Model):
    order = models.ForeignKey(Order)
    dish = models.ForeignKey(Dish)
    number = models.IntegerField(blank=True, default=1)
    total_per_dish = models.FloatField(default=0.0, blank=True)
    price_per_dish = models.FloatField(default=0.0, blank=True)

    def __str__(self):
        return 'Блюдо %s в заказе №%d' % (self.dish.name, self.order.id)

    class Meta:
        verbose_name = 'Блюдо в заказе'
        verbose_name_plural = 'Блюда в заказе'

    def save(self, *args, **kwargs):
        price_per_item = self.dish.price
        self.total_per_dish = price_per_item * self.number
        self.price_per_dish = price_per_item

        super(DishesInOrder, self).save(*args, **kwargs)


def refresh_order_for_instance(instance):
    order = instance.order

    all_dishes_in_order = DishesInOrder.objects.filter(order=order)
    order_total_price = 0
    for item in all_dishes_in_order:
        if not item.order.closed:
            order_total_price += item.total_per_dish

    order.total_price = order_total_price
    order.save(force_update=True)


def changed_price(sender, instance, created, **kwargs):
    all_dishes_in_order = DishesInOrder.objects.filter(dish=instance)
    for item in all_dishes_in_order:
        if not item.order.closed:
            item.total_per_dish = item.dish.price * item.number
            item.price_per_dish = item.dish.price
            item.save(force_update=True)


def refresh_order(sender, instance, created, **kwargs):
    refresh_order_for_instance(instance)


def delete_dish_from_order(sender, instance, **kwargs):
    refresh_order_for_instance(instance)


post_save.connect(refresh_order, sender=DishesInOrder)
post_delete.connect(delete_dish_from_order, sender=DishesInOrder)
post_save.connect(changed_price, sender=Dish)
