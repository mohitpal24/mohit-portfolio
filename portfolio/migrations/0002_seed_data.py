from django.db import migrations

def seed_data(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    Service = apps.get_model('portfolio', 'Service')

    # Seed Projects
    Project.objects.create(
        title="TeamFlow Royal",
        category="Full-Stack Development",
        description="A MERN stack task management system with JWT authentication, RBAC, project management, and task tracking. Built features including task assignment, status tracking, and user management. Integrated MongoDB Atlas, Express.js REST APIs, React Context API, and Tailwind CSS for a responsive user experience.",
        image="projects/teamflow_royal.png",
        project_url="https://team-task-royal.onrender.com/"
    )

    Project.objects.create(
        title="AI-Powered Journal Assistant",
        category="Artificial Intelligence & Backend",
        description="An AI journaling assistant using GPT-style language models with contextual memory via RAG. Built a Node.js/Express backend integrating PostgreSQL and pgvector for structured and vector data. Deployed a React frontend with JWT authentication on Vercel and Render with S3-compatible file storage.",
        image="projects/ai_journal.png",
        project_url="https://github.com/mohitpal24"
    )

    # Seed Services
    Service.objects.create(
        title="Full-Stack Engineering",
        description="Building responsive, modern user interfaces integrated with robust backend architectures. Experienced in Django, React, Node.js, and Express.js.",
        tags="Django, Python, React, Node.js, Express.js, MongoDB"
    )
    Service.objects.create(
        title="Backend & API Design",
        description="Designing scalable REST APIs and services with high performance. Secure authentication, RBAC, and clean database schemas.",
        tags="Python, Django, Flask, REST Framework, PostgreSQL, MySQL"
    )
    Service.objects.create(
        title="Frontend & UI Dev",
        description="Developing highly interactive, responsive, and performance-optimized layouts. Translating Figma designs to clean, modular, and responsive code.",
        tags="HTML, CSS, JavaScript, React, Tailwind CSS, Bootstrap"
    )
    Service.objects.create(
        title="Data Science & Intelligence",
        description="Leveraging AI/ML techniques for intelligent applications. Experience in vector databases, RAG implementations, and data automation pipelines.",
        tags="Python, pgvector, GPT-style APIs, RAG, Data Pipelines, AI & ML"
    )

def reverse_seed(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    Service = apps.get_model('portfolio', 'Service')
    Project.objects.all().delete()
    Service.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
