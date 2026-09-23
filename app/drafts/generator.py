from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from app.models.schema import TicketOut

env = Environment(loader=FileSystemLoader("app/drafts/templates"))

def generate_draft(ticket: TicketOut) -> str:
    """
    Load the template matching ticket.category
    (fallback to junk_ack.j2 if the category doesn't map to a file).
    Render it with the ticket's fields — sender, subject, entities, etc.
    Return the rendered string.
    """
    try:
        template_name = f"{ticket.category}_ack.j2"
        template= env.get_template(template_name)

    except TemplateNotFound:
        template= env.get_template("junk_ack.j2")

    context= ticket.model_dump()

    return (template.render(**context))