# Generated by Django 3.0.6 on 2020-05-16 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_remove_post_body2'),
    ]

    operations = [
        migrations.CreateModel(
            name='HighlightCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('body_highlighted', models.TextField(blank=True, editable=False)),
            ],
        ),
    ]
