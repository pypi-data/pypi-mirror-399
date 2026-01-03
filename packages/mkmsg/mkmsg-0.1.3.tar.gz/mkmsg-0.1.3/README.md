# mkmsg

Python library to send:
- WhatsApp messages via WhatsApp Web
- Plain text emails
- HTML emails (Gmail)

## Installation
```bash
pip install mkmsg
```
## Usage

```python
>>> import mkmsg

>>> # Send a plain text email
>>> mkmsg.Send_mail(
...     "sender@gmail.com",
...     "APP_PASSWORD",
...     "Your Name",
...     "Test Email",
...     "Hello from mkmsg",
...     "receiver@gmail.com"
... )
'Email sent successfully'

>>> # Send an HTML email
>>> mkmsg.Send_html_mail(
...     "sender@gmail.com",
...     "APP_PASSWORD",
...     "Your Name",
...     "HTML Test",
...     "<h1>Hello World</h1>",
...     "receiver@gmail.com"
... )
'HTML email sent successfully'

>>> # Generate an OTP
>>> otp = mkmsg.Generate_otp(6)
>>> otp
'123456'

>>> # Send a WhatsApp message
>>> mkmsg.Send_whats_msg(
...     "201234567890",
...     "Hello from mkmsg",
...     10
... )
'WhatsApp message sent successfully'
