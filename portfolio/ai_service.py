import json
import urllib.error
import urllib.request

from django.conf import settings


PORTFOLIO_CONTEXT = """
Mohit Pal is a software engineer and B.Tech Computer Science (AI & ML) student at
KCC Institute of Technology & Management, graduating in 2026. He focuses on Python,
Django, scalable backends, REST APIs, databases, and polished full-stack products.
He completed a Developer Trainee program at HCL Tech from January to March 2025,
working with Java, object-oriented design, software architecture, and AI-assisted development.

Skills:
- Languages: C, C++, Java, Python, JavaScript
- Web: HTML, CSS, Bootstrap, Flask, Django, React, Node.js, Express.js, REST APIs
- Databases: MongoDB, MySQL, PostgreSQL, pgvector
- Tools: Git, GitHub, VS Code, Android Studio

Contact: mohitmusic2429@gmail.com, GitHub github.com/mohitpal24.
Mohit is open to suitable software engineering roles, internships, and collaborations.
""".strip()


class AIServiceError(Exception):
    pass


def ask_portfolio_ai(question, history, projects):
    if not settings.AI_API_KEY:
        raise AIServiceError("AI_NOT_CONFIGURED")

    project_context = "\n".join(
        f"- {project.title}: {project.description} Link: {project.project_url or 'not public'}"
        for project in projects
    )
    system_prompt = f"""
You are PAL, the AI portfolio assistant for Mohit Pal's website. Be warm, concise,
and conversational. Answer questions about Mohit using the verified context below.
You may answer ordinary greetings and simple general questions, but do not pretend
to be a general-purpose ChatGPT. If a question requires personal information not in
the context, say you do not know and suggest contacting Mohit. Never invent employers,
experience, skills, project details, availability, or private information. Keep most
answers below 110 words. Do not use Markdown tables.

VERIFIED CONTEXT
{PORTFOLIO_CONTEXT}

PROJECTS
{project_context}
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    for item in history[-8:]:
        if item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
            messages.append({"role": item["role"], "content": item["content"][:1000]})
    messages.append({"role": "user", "content": question})

    payload = json.dumps({
        "model": settings.AI_MODEL,
        "messages": messages,
        "temperature": 0.35,
        "max_completion_tokens": 260,
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{settings.AI_BASE_URL.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MohitPalPortfolio/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            result = json.loads(response.read().decode("utf-8"))
        answer = result["choices"][0]["message"]["content"].strip()
        if not answer:
            raise AIServiceError("EMPTY_AI_RESPONSE")
        return answer
    except urllib.error.HTTPError as exc:
        raw_error = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw_error)
            provider_error = error_payload.get("error", {})
            if isinstance(provider_error, dict):
                detail = provider_error.get("message", f"HTTP {exc.code}")
            else:
                detail = str(provider_error) or f"HTTP {exc.code}"
        except (json.JSONDecodeError, AttributeError):
            compact_body = " ".join(raw_error.split())[:180]
            detail = compact_body or f"HTTP {exc.code}"
        raise AIServiceError(f"AI_REQUEST_FAILED: {detail}") from exc
    except urllib.error.URLError as exc:
        raise AIServiceError(f"AI_REQUEST_FAILED: connection error ({exc.reason})") from exc
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise AIServiceError("AI_REQUEST_FAILED: unexpected provider response") from exc
