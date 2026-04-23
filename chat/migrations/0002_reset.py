from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS chat_chatmessage CASCADE;",
            reverse_sql="",
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS chat_chatroom CASCADE;",
            reverse_sql="",
        ),
    ]