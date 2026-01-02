WELCOME_1_TEXT = """
Hey there!

 \n{0}\n

Here is the verification code you requested.
Type code into the challenge input field.
"""

WELCOME_1_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>{0}</title>
<style>
  .otp-code {{
    font-size: 3em;
    font-weight: bold;
    letter-spacing: 0.1em;
    margin: 1em 0;
  }}
</style>
</head>
  <body>
    <h1 class="otp-code">{1}</h1>

    <p>Hey there!</p>

    <p>
    Here is the verification code you requested.
    Type code into the challenge input field.
    </p>

  </body>
</html>
"""

PURCHASE_1_TEXT = """
You made a purchase!

{0}

You may paste this link into your browser to view and download your purchases:

 \n{1}\n

Thank you very much!
"""

# 0: subject,
# 1: request.host_url,
# 2: product_text,
# 3: total_cost,

PURCHASE_1_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>{0}</title>

</head>
  <body>
    <h2>
    You made a purchase!
    </h2>

    {2}

    <b>${3}</b>

    <p>
    You may <a href="{1}/u/purchases" style="font-weight: bold;" target="_blank">download your purchases</a> at any time.
    </p>

    <p>
    </p>

    <p style="font-size: .8em;">
    <span style="color: #aaaaaa;">
    You may paste this link into your browser to view or download your purchases:
    </span>
    <br>
    <br>
    <a href="{1}/u/purchases" style="color: #439fe0; font-weight: normal; text-decoration: none; word-break: break-word;" target="_blank">
    {1}/u/purchases
    </a>
    </p>

    <p>
    Thank you very much!
    </p>

  </body>
</html>
"""

SALE_1_TEXT = """
You made a sale!

{0}

You may paste this link into your browser to view your sales:

 \n{1}\n

Great job!
"""

# 0: subject,
# 1: shop.absolute_sales_url
# 2: product_text,
# 3: total_cost,

SALE_1_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>{0}</title>

</head>
  <body>
    <h2>
    You made a <u>sale</u>!
    </h2>

    <b>${3}</b>

    {2}

    <p>
    You may view <a href="{1}" style="font-weight: bold;" target="_blank">all your sales</a> at any time.
    </p>

    <p style="font-size: .8em;">
    <span style="color: #aaaaaa;">
    You may paste this link into your browser to view your sales:
    </span>
    <br>
    <br>
    <a href="{1}" style="color: #439fe0; font-weight: normal; text-decoration: none; word-break: break-word;" target="_blank">
    {1}
    </a>
    </p>

    <p>
    Great job!
    </p>

  </body>
</html>
"""


# 0: user.email
# 1: shop.name,
# 2: log in link.
INVITE_1_TEXT = """
Hey There!

{0} has invited you to join the {1} shop on Make Post Sell.

Click this link to log in.

{2}

Make Post Sell is a lightweight, open-source, public domain, software as a service ecommerce web application.
We hope you like our ethical approach to doing business online.

Thanks for sharing! <3
"""

# 0: subject,
# 1: user.email
# 2: shop.name,
# 3: log in link.

INVITE_1_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>{0}</title>

</head>
<body>

<h2>Hey There!</h2>

<p>
{1} has invited you to join {2} on Make Post Sell.
</p>

<p>
<a href="{3}">click this link to log in to the shop.</a>
</p>

<p>
Make Post Sell is a lightweight, open-source, public domain, software as a service ecommerce web application.
We hope you like our ethical approach to doing business online.
</p>

<p>
Thanks for sharing! <3
</p>

  </body>
</html>

"""
