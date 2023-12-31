# Generated by Django 2.0.5 on 2021-10-08 18:55

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(max_length=20, null=True)),
                ('number', models.CharField(max_length=100, null=True)),
                ('address', models.TextField(max_length=100, null=True)),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('about', models.TextField(null=True)),
                ('image', models.TextField(null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('parent', models.IntegerField(blank=True, null=True)),
                ('display', models.BooleanField(default=True)),
                ('image', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('zipcode', models.TextField(default='(0)')),
                ('delivery_flag', models.BooleanField(default=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'product_categories',
            },
        ),
        migrations.CreateModel(
            name='CategoriesMessage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'product_categories_message',
            },
        ),
        migrations.CreateModel(
            name='HomePageItems',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fix_id', models.IntegerField()),
                ('title', models.CharField(max_length=100, null=True)),
                ('sql', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'home_page_items',
            },
        ),
        migrations.CreateModel(
            name='ProductCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, null=True)),
                ('amount_order', models.FloatField(default=0)),
                ('amount_discount', models.FloatField(default=0)),
                ('coupon_type', models.CharField(choices=[('DOLLAR', ('DOLLAR', 'Dollar')), ('PERCENTAGE', ('PERCENTAGE', 'Percentage'))], default='DOLLAR', max_length=30)),
                ('user_id', models.IntegerField(default=0, null=True)),
                ('expired', models.DateTimeField()),
                ('comment', models.TextField()),
                ('display', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'product_coupon',
            },
        ),
        migrations.CreateModel(
            name='ProductPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('product_order', models.IntegerField(default=0)),
                ('payment_type', models.CharField(blank=True, max_length=250, null=True)),
                ('payment_request', models.TextField()),
                ('payment_response', models.TextField()),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'product_payment',
            },
        ),
        migrations.CreateModel(
            name='ProductPaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('user', models.IntegerField(default=0)),
                ('order_id', models.IntegerField(default=0, null=True)),
                ('order_invoice', models.IntegerField(default=0, null=True)),
                ('debit_credit', models.CharField(max_length=250)),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'product_payment_history',
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=200)),
                ('price', models.FloatField(default=0)),
                ('price_new', models.FloatField(default=0)),
                ('discount', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('discount_created', models.DateTimeField(blank=True, default=None, null=True)),
                ('weight', jsonfield.fields.JSONField(default=dict)),
                ('available', models.IntegerField(default=1)),
                ('image1', models.CharField(blank=True, max_length=250, null=True)),
                ('image2', models.CharField(blank=True, max_length=250, null=True)),
                ('image3', models.CharField(blank=True, max_length=250, null=True)),
                ('image4', models.CharField(blank=True, max_length=250, null=True)),
                ('tags', models.CharField(blank=True, max_length=250, null=True)),
                ('counter_visit', models.IntegerField(default=0)),
                ('counter_order', models.IntegerField(default=0)),
                ('display', models.BooleanField(default=True)),
                ('descriptions', models.TextField(blank=True, default='', null=True)),
                ('descriptions_html', models.TextField(blank=True, default='', null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.Categories')),
                ('shop', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'product_products',
            },
        ),
        migrations.CreateModel(
            name='ProductsAdvertising',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(blank=True, max_length=250, null=True)),
                ('type_id', models.IntegerField(default=0)),
                ('image', models.TextField(default='')),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'product_advertising',
            },
        ),
        migrations.CreateModel(
            name='ProductsCard',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_quality', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.Products')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'product_card',
            },
        ),
        migrations.CreateModel(
            name='ProductsOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('shop', models.IntegerField(default=0)),
                ('is_admin', models.BooleanField(default=False)),
                ('amount', models.FloatField(default=0)),
                ('tax_amount', models.FloatField(default=0)),
                ('zipcode_tax', models.FloatField(default=0)),
                ('tips', models.FloatField(default=0)),
                ('delivery_amount', models.FloatField(default=0)),
                ('total_amount', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('CANCEL', ('CANCEL', 'Cancel')), ('PAYMENT_PENDING', ('PAYMENT_PENDING', 'Payment Pending')), ('ORDERED', ('ORDERED', 'Ordered')), ('PENDING', ('PENDING', 'Pending')), ('PROCESSING', ('PROCESSING', 'Acknowledged')), ('SHIPPING', ('SHIPPING', 'Ready to Ship')), ('TRANSIT', ('TRANSIT', 'Transit')), ('COMPLETE', ('COMPLETE', 'Delivered'))], default='PAYMENT_PENDING', max_length=30)),
                ('is_payment', models.BooleanField(default=False)),
                ('address', models.TextField(max_length=100, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.ProductPayment')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('voucher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.ProductCoupon')),
            ],
            options={
                'db_table': 'product_order',
            },
        ),
        migrations.CreateModel(
            name='ProductsOrderItems',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_order', models.IntegerField(default=0)),
                ('product_price', models.FloatField(default=0)),
                ('product_price_final', models.FloatField(default=0)),
                ('product_discount', models.FloatField(default=0)),
                ('product_quantity', models.IntegerField(default=0)),
                ('shop', models.IntegerField(default=0)),
                ('is_admin', models.BooleanField(default=False)),
                ('other', models.CharField(default='', max_length=200, null=True)),
                ('status', models.CharField(choices=[('CANCEL', ('CANCEL', 'Cancel')), ('PAYMENT_PENDING', ('PAYMENT_PENDING', 'Payment Pending')), ('ORDERED', ('ORDERED', 'Ordered')), ('PENDING', ('PENDING', 'Pending')), ('PROCESSING', ('PROCESSING', 'Acknowledged')), ('SHIPPING', ('SHIPPING', 'Ready to Ship')), ('TRANSIT', ('TRANSIT', 'Transit')), ('COMPLETE', ('COMPLETE', 'Delivered'))], default='ORDERED', max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.Products')),
            ],
            options={
                'db_table': 'product_order_items',
            },
        ),
        migrations.CreateModel(
            name='ProductsReview',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product', models.IntegerField(default=0)),
                ('starts', models.IntegerField(default=0)),
                ('comment', models.CharField(blank=True, max_length=250, null=True)),
                ('user_id', models.IntegerField(default=0)),
                ('user_info', jsonfield.fields.JSONField(default=dict)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'product_review',
            },
        ),
        migrations.CreateModel(
            name='ProductsWeight',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('parent', models.IntegerField(blank=True, null=True)),
                ('value_type', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'product_weight',
            },
        ),
        migrations.CreateModel(
            name='ProductsWhiteList',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_quantity', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.Products')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'product_white_list',
            },
        ),
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('device_id', models.CharField(max_length=200)),
                ('token', models.TextField()),
                ('device_type', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'push_notification',
            },
        ),
        migrations.CreateModel(
            name='ShopZipcodes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tax', models.FloatField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'shop_zipcodes',
            },
        ),
        migrations.CreateModel(
            name='UsersForgotCode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('code', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'users_forgot_code',
            },
        ),
        migrations.CreateModel(
            name='ZipCodes',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('zipcode', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'zip_code',
            },
        ),
        migrations.AddField(
            model_name='shopzipcodes',
            name='zipcode',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web_api.ZipCodes'),
        ),
    ]
