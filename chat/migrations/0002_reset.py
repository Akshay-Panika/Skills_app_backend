from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS chat_chatmessage CASCADE; DROP TABLE IF EXISTS chat_chatroom CASCADE;",
            reverse_sql="",
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('seller_online', models.BooleanField(default=False)),
                ('buyer_online', models.BooleanField(default=False)),
                ('seller_typing', models.BooleanField(default=False)),
                ('buyer_typing', models.BooleanField(default=False)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_rooms', to='user_auth.userauth')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_rooms', to='user_auth.userauth')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_rooms', to='service.service')),
            ],
            options={
                'unique_together': {('service', 'seller', 'buyer')},
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_delivered', models.BooleanField(default=False)),
                ('is_seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='user_auth.userauth')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatroom')),
            ],
        ),
    ]