import random
def Generate_otp(length=6):
    """
    Generate a random OTP of given length.
    Args:
        type (int): Number of digits (default 6)
    """
    return random.randint(10**(length-1), 10**length - 1)
otp = Generate_otp(6)
mk_html_code = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>OTP Code</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f6f8;">

<table width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
        <td align="center" valign="middle">

            <table width="320" cellpadding="0" cellspacing="0" role="presentation"
                   style="background:#ffffff; border-radius:14px; padding:30px;
                          box-shadow:0 10px 30px rgba(0,0,0,0.15); text-align:center;">

                <tr>
                    <td>
                        <h2 style="margin:0; font-family:Arial,sans-serif; color:#111;">
                            Your OTP Code
                        </h2>
                        <p style="font-family:Arial,sans-serif; color:#555;">
                            Use this code in the application
                        </p>
                        <div style="
                            font-size:36px;
                            font-weight:bold;
                            letter-spacing:8px;
                            color:#2563eb;
                            margin-top:20px;">
                            {otp}
                        </div>
                    </td>
                </tr>

            </table>

        </td>
    </tr>
</table>

</body>
</html>
"""