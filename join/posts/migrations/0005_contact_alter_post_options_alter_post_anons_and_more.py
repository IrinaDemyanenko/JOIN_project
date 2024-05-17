# Generated by Django 5.0.2 on 2024-04-22 13:14

import posts.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_group_options_alter_group_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, validators=[posts.validators.validate_not_empty])),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=100, validators=[posts.validators.validate_not_empty])),
                ('body', models.TextField(max_length=1000)),
                ('is_answered', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.AlterField(
            model_name='post',
            name='anons',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(validators=[posts.validators.validate_not_empty]),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(default='Название', max_length=50, validators=[posts.validators.validate_not_empty]),
        ),
    ]