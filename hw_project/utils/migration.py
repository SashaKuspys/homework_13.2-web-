import os
import django

from pymongo import MongoClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw_project.settings")
django.setup()


from quotes.models import Quote, Tag, Author # noqa

client = MongoClient("mongodb://localhost")

db = client.hw

authors = db.authors.find()

for author_data in authors:
    author, created = Author.objects.get_or_create(
        fullname=author_data['fullname'],
        defaults={
            'born_date': author_data.get('born_date', ''),
            'born_location': author_data.get('born_location', ''),
            'description': author_data.get('description', '')
        }
    )

quotes = db.quotes.find()

for quote_data in quotes:
    tags = []
    for tag_name in quote_data.get('tags', []):
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)

    exist_quote = Quote.objects.filter(quote=quote_data['quote']).exists()

    if not exist_quote:
        author = db.authors.find_one({'_id': quote_data['author']})
        if author:
            author_instance = Author.objects.get(fullname=author['fullname'])
            quote_instance = Quote.objects.create(
                quote=quote_data['quote'],
                author=author_instance
            )
            quote_instance.tags.set(tags)