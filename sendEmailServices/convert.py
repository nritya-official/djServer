from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import base64
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import base64
import qrcode
import io

def render_template(template_path, context):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_path)
    return template.render(context)

def generate_pdf_save(output_path, html_content):
    HTML(string=html_content).write_pdf(output_path)

def generate_pdf_stream(html_content):
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    #HTML(string=html_content).write_pdf('demo_ticket.pdf')
    pdf_buffer.seek(0)
    return pdf_buffer


def generate_qr_code(link):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Use an in-memory stream instead of saving to a file
    img_stream = io.BytesIO()
    img.save(img_stream)
    img_stream.seek(0)  # Reset the stream position

    return img_stream.read()


def generate_ticket_pdf(customer_name, studio_name, class_name,address, qr_code_link,timestamp_c,studio_timing,studio_days,output_path="output.pdf"):
    logo_path = "./logo.png"
    encoded_qr_code = generate_qr_code(qr_code_link)

    # Read the image and convert it to base64
    with open(logo_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Prepare the context with the base64-encoded image string and other data
    context = {
        "title": "Booking Ticket",
        "logo_base64": encoded_string,
        "customer_name": customer_name,
        "studio_name": studio_name,
        "class_name": class_name,
        "qr_code_base64": base64.b64encode(encoded_qr_code).decode('utf-8'),
        "timestamp_c":timestamp_c,
        "address":address,
        "studio_timing":studio_timing,
        "studio_days":studio_days,
    }

    html_content = render_template("ticket_templateNew.html", context)
    pdf_buffer = generate_pdf_stream(html_content)


    print(f"PDF generated successfully at {output_path}")
    return pdf_buffer
