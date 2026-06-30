from django.db import migrations


def update_project_links(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    Project.objects.filter(title='TeamFlow Royal').update(
        project_url='https://team-task-royal.onrender.com/'
    )
    Project.objects.filter(title='AI-Powered Journal Assistant').update(
        project_url='https://github.com/mohitpal24'
    )


class Migration(migrations.Migration):
    dependencies = [('portfolio', '0002_seed_data')]
    operations = [migrations.RunPython(update_project_links, migrations.RunPython.noop)]
