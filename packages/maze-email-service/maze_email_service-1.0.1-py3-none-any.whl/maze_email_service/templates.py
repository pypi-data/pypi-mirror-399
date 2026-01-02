from jinja2 import Environment, BaseLoader, TemplateError
from .exceptions import EmailTemplateError

def render_template(html: str, variables: dict) -> str:
    try:
        env = Environment(
            loader=BaseLoader(),
            autoescape=True
        )
        template = env.from_string(html)
        return template.render(**variables)
    except TemplateError as ex:
        raise EmailTemplateError(str(ex))
