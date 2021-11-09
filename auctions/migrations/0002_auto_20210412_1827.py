from __future__ import unicode_literals
from django.db import migrations, models

def load_categories(apps, schema_editor):
    Category = apps.get_model("auctions", "Category")

    category_books = Category(id=0,title="Books")
    category_books.save()

    category_clothes = Category(id=1,title="Clothes")
    category_clothes.save()

    category_drinks = Category(id=2,title="Drinks")
    category_drinks.save()

    category_eletronics = Category(id=3,title="Eletronics")
    category_eletronics.save()

    category_games = Category(id=4,title="Games")
    category_games.save()

    category_house = Category(id=5,title="House")
    category_house.save()

    category_toys = Category(id=6,title="Toys")
    category_toys.save()

    category_vehicle = Category(id=7,title="Vehicle")
    category_vehicle.save()
    

class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_categories)
    ]