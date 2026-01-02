
================
Development Journal
================

.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: top

Tue 23 Jun 2020 07:16:03 PM EDT
=================================

Ok so I'm on day 4 of my stay-cation at home and I've finally gotten around to working on one of my two important goals during my break.

1. implement coupon codes on makepostsell.com and 
2. utilize all cardboard into my landscape and out of my garage and house

I've made great progress on 2, but just started getting my toes wet on 1...

Gosh let me tell you, I spent the last 2 hours or so just getting parts of my release pipeline working again, end to end.

* I had to hard reboot the Jenkins server (`jenkins.foxhop.net`) which lives on my SmartOS host (`mbison.foxhop.net`)::

    ssh root@mbison.foxhop.net
    vmadm list
    vmadm stop --force <jenkins-uuid>
    vmadm start <jenkins-uuid>

* I had to fix tests in this repo (`make_post_sell`):

  See the previous commit in github for details, but basically I broke jenkins builds because I busted my `setup.py` when I broke some magic that I forgot I implemented to load `README.txt`, which I recently moved to `README.rst`... 

* I had to release new TLS certificates, which had expired, again!

Didn't I fix the TLS certificate expiring issue?

Let's check...

yup ... doh!

`akuma-crontab/init.sls`::

 deploy-new-letsencrypt-certs:
  cron.present:
    - comment: 'Deploy new certs every day at 4:25am'
    - name: salt -C 'remarkbox.* or sakura.* or ryu.*' state.sls letsencrypt.client
    - identifier: 'deploy-new-letsencrypt-certs'
    - minute: 25
    - hour: 19
    - user: root

So let's update that state to also include `mps-web*` so that it automatically get's it's certificates each day, if any new ones are present. In this way the cronjob that requests the new certs controls the speed of which the new certs are staged and then submitted each day.

Akuma (`akuma.foxhop.net`) is the `salt-master` (SaltStack).

Anyways, new cronjob:

::

 name: salt -C 'remarkbox.* or sakura.* or ryu.* or mps-web*' state.sls letsencrypt.client



Sat 01 Aug 2020 03:10:13 PM EDT
###################################

ok we are camping today and I've been messing with the make post sell codebase building out coupon code workflows all this week. We rented an RV for a week.

Place is real chill, and the kids get to socialize with family.

Anyways so I've been able to work a bit again on the coupon code system.

Previously I had all the models done but no real way to create coupons.

In my latest commit I created a new coupon form and the views/handlers to accept user data and generate Coupon instances.

I also created a cute coupon page which shop keepers could link to when sending out a marketing communications like emails or social media posts.

The coupon page makes it really easy for a customer to click a button labelled "apply coupon to active cart".

I still need to build the "apply coupon to active cart" button logic.

What does "apply" mean for a cart, whether single shop or marketplace?

Seems like there are two "states" a Coupon/Cart "attachment" could be in:

* `unqualified`
* `qualified`

a Coupon has certain qualification conditions which must be met by the cart before proceeding with checkout.

For example:

* a $20 minimum cart total
* coupon expired
* limit 1 per customer and the customer already used the coupon
* total redemption limit reached

These checks are verified when the user tries to click checkout.

If any fail, flash a message to the user explaining why and send them back to the cart.

These checks are verified once again, after the user clicks the "Yes, Complete Checkout" button. Failure at this stage bumps user back to cart with the error message.

The cart has a link to the attached coupon so the user may easily click it to reread the terms of the coupon.
The link also had an `X` which may be clicked to remove the coupon from the cart.

I was planning to day dream about this away from the keyboard but I instead day dreamed about it in this journal file.

This is an important next step. Finishing this means we work on integration/functional tests for a complete checkout process including adding a coupon to a cart (and all the numerous edgecases that could have).

Once we have those tests, we may safely ship coupon codes to production! 


Sun 23 Aug 2020 11:53:13 AM EDT
====================================

So I ran into a strange case where I deleted or in retrospect, renamed a field model field which happened to get into my alembic migrations.

This manifested quite a few commits later when I needed to migrate the database
again for a new table (in this case the table to relate many Coupons to Carts) I noticed that the migration was trying to remove the renamed field.

Now at first glance this wouldn't be a big deal, EXCEPT for the fact that my
development environment is sqlite3 and as of today, it still doesn't support
ALTER TABLE and DROP COLUMN so I new this migration, just by looking at the code that it would fail to apply.

Now I use master for all my work, even features because I don't have the memory to remember feature branches for all my different codebases. If I ever get a team around this codebase `make_post_sell` I would definately switch to a feature branch model.

Anyways I have a lot of changes in master, and I have not shipped to production in a long time. I have all the coupon code dashboard stuff queued up and I want to ship the whole feature MVP together as a unit; but I've been a bit scatter-brained and only working occasionally on `make_post_sell` over the last few months.

That said, in my defence the ONLY priority for `make_post_sell` is shipping coupon codes. So using master as the feature branch for coupon codes actually makes sense in some wierd way.

Anyways, shipping coupon codes is my #1 priority is because we want it ready for Jenn's back-to-school curriculum sales on https://shop.printableprompts.com.

Ok so back to the problem at hand, I needed to figure out when a line was added and when it was removed and I knew what string I needed to search for (`stripe_id`).

So the search when for when I added the line, because I shifted around how we store our stripe setup a few times in this app, I decided to see if the first commit to the `User` class had the field.

Sure enough, the first commit of the `User` class had a reference to `stripe_id`.

So master does not have `User.stripe_id` but the first commit to this file does have `User.stripe_id`. This means we need to find the commit when we deleted the line containing `stripe.id`.

Searched duckduckgo (DDG) with the query "determine the commit when a line was deleted" and came upon a stackoverflow forum post which helped me form this query::

 git log -c -S'stripe_id' /path/to/file.py

Unfortnately this didn't work, but this did!::

 git log -c -S'stripe_id'

Display all logs with commits for all files (`git log -c`) including only the commits that have the search string (`-S'stripe_id'`)

This gave me a handful of commits to scroll through looking for my match and sure enough I found the commit deleting the `stripe_id` field.

Then I figured out the missing context, my past self decided to rename `stripe_id` to `cus_id` but I didn't notice or didn't care that the column had existed in sqlite3 database since the start.

Here is the commit ::

 commit b70e46bfef7f7ef3442d23e6d66ebd7aea5fd767
 Author: russellballestrini <russell.ballestrini@gmail.com>
 Date:   Sun Sep 1 20:58:52 2019 -0400
 
     /billing functions as expected.
 
 diff --git a/make_post_sell/models/stripe_user_shop.py b/make_post_sell/models/stripe_user_shop.py
 index 912e6c3..4a4bb66 100644
 --- a/make_post_sell/models/stripe_user_shop.py
 +++ b/make_post_sell/models/stripe_user_shop.py
 @@ -17,7 +17,7 @@ class StripeUserShop(RBase, Base):
      shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
  
      # example: "cus_12345678AbCdEF".
 -    stripe_id = Column(Unicode(18), unique=True, nullable=False)
 +    cus_id = Column(Unicode(32), nullable=False)
  
      user = relationship(
          argument="User", backref=backref("stripe_user", cascade="all, delete-orphan")
 @@ -27,8 +27,6 @@ class StripeUserShop(RBase, Base):
          argument="Shop", backref=backref("stripe_shop", cascade="all, delete-orphan")
      )
  
 -    # def set_stripe_id
 -
      def __init__(self, user=None, shop=None):
          self.id = uuid.uuid1()
          self.user = user
 
.. image:: one-cannot-simply-meme

One cannot simply ALTER TABLE to rename a column in sqlite3

Ok so at this point, I'm not sure I care enough about the naming of this column and I don't want
to do the scary work of migrating the production sqlite3 database manually by hand. Maybe I automate an offline rename sqlite3 column script but for now I'm just not that interested in "operations" work.

So this commit will be renaming the `cus_id` column back to it's original name `stripe_id` on the `User` class.

Fri Jul 16 12:11:20 PM EDT 2021
=================================================

could there be slack bot workflows for interacting with a make_post_sell shop as an owner?

for example creating new products via bot commands, editing products via bot commands, etc.

and if this could be useful how does matrix fit into making chat bots? could a matrix bot be 
a one ring to rule them all sort of play where a bridge could be build between any chat service?

Ask if this is a good idea or not.

How about transaction data or daily/weekly/monthly reports notified via email, slack/chat?

anyways food for thought! think errbot UAC (user access control) plugin gitlab pipeline setup. but instead it could interact with make_post_sell API (the API is build and bot which speaks html/http/form and hack away). It's the web scraper's API. how will you prevent people from spamming the system? make it just as easy to delete spam.

imagine now a bot which changes prices for a group of products or a bot which changes all prices on a shop based on a metric multiplier or some other formula.

The chat bot allows others the ability to harness authenticated and canned API calls which they may give inputs, proper process leads to desirable outputs. It's the trivium. A proper bot unlocks a safe trivium for end user creators, operators, marketing people. The salesman position is removed, your work packaged and posted to your shop sells itself 24/7 - you don't even need to pay a sales clerk. You will however have to drive "traffic" to your content and to your shop and so the marketers job is never ending. Where will you take your business next?


Wed Nov 10 07:09:49 PM EST 2021
===================================


this release creates the concept of product visibility. seems to be working as I expect at this point so I'm happy. Let's Go!



Tue Nov 16 08:40:38 PM EST 2021
==============================================


[ ] we need to implement shop defined object stores.

engineering wants to test this feature with digital ocean spaces and s3 and gcp.

sales wants this feature to be an upsale for the $99/yr plan.

marketing likes this and could start to work on a pricing section on the homepage.
  wants to discuss contrants on the free account, like 500M capacity what is the cost-of that across various cloud providers?
  we don't want to kill the company trying to service free content creators.


Tue Nov 23 12:11:54 PM EST 2021
================================

Eureka, I need to built a streaming content system into make post sell.

I'll build my own BoobTube. 

I will try to overload the mps_product objects to support free "streaming" (broadcast) type "content" products.

A major difference in "content" versus "product" is that there is no way to purchase it, 
and the content page may autoplay and similar to a tube site. 

Leads the way to building in comments & community.

main difference is the metadata on the object store needs to allow "inline" streaming instead of "attachment".


Thu May 26 05:54:53 PM EDT 2022
==================================

ok I got dkim working with the new ed25519 signature_algorithm but for some reason pynacl which is needed for this routine isn't being installed even though I am calling it outright in requirements.txt ...  (AHH that was the problem, Makefile only uses requirements.py3.txt)

very strange, anyways I installed the package hot on memopoly.com so I'm ahead of myself seeing as the root cause of the dependency error is not fix, but SMTP is being DKIM signed & shipping to external relays!

That said, google complains & bounces an SMTP message back as follows:

.. code_block::

  May 26 17:18:14 memopoly.com postfix/smtp[287516]: 3E557206A4: to=<russell@example.com>, relay=gmail-smtp-in.l.google.com[2607:f8b0:4002:c09::1a]:25, delay=0.5, delays=0.01/0.01/0.04/0.43, dsn=5.7.1, status=bounced (host gmail-smtp-in.l.google.com[2607:f8b0:4002:c09::1a] said: 550-5.7.1 [2600:3c02::f03c:93ff:fe59:c935] Our system has detected that this 550-5.7.1 message does not meet IPv6 sending guidelines regarding PTR records 550-5.7.1 and authentication. Please review 550-5.7.1  https://support.google.com/mail/?p=IPv6AuthError for more information 550 5.7.1 . n184-20020a8172c1000000b002fe9ac76197si316115ywc.122 - gsmtp (in reply to end of DATA command))
  May 26 17:18:14 memopoly.com postfix/smtp[287516]: B9783216C9: to=<no-reply@www.memopoly.com>, relay=none, delay=0.07, delays=0/0/0.07/0, dsn=5.4.6, status=bounced (mail for www.memopoly.com loops back to myself)
  May 26 17:18:14 memopoly.com postfix/qmgr[224579]: B9783216C9: removed
  ^C

I am likely missing the SPF records so I'll add those next. 

[X] As for pynacl not installing, I'm stumped... requirements.py3.txt

we should rename requirements.py3.txt to requirements.txt at some point & finalize the switch from python2 to python3.


Tue Jul 19 04:46:15 PM EDT 2022
================================

after much back & forth in my head regarding how to build out physical projects, I've spent a couple days now trying to think out whether it's worth it to try to bite off multiple stores per shop, so multiple quantities per store location, instead of a simple quantity field on the Product object. I know asking the hard arch questions alone without a team & then having to deal with living with those consequencies has me at a fork in the road.

I think the safest way to proceed is to assume a shop will has one location.

This could be revisted again in the future.

I am honestly having a hard time working on this "physical product" feature & i'm not sure why. I feel repelled by the project & it's actually really hard for me to work on it & even so I keep myself thinking about it hoping a creative solution will pop into my head but so far I've only two ideas neither of which I am that excited to build alone.

I have a desire to table this project, temporarily at least.



Tue Sep 13 03:22:14 PM EDT 2022
=======================================

This is a script to recompute the file_bytes & total_file_bytes of every Product object of the database.

It will query the s3 backend and fix our meta data regarding content length for our capacity usage.


```

import botocore.exceptions

# begin the database transaction.
request.tm.begin()

all_products = models.get_all_products(request.dbsession)

for product in all_products:
    for file_key in product.file_keys:

        try:
            response = request.secure_uploads_client.head_object(
                Bucket=request.app["bucket.secure_uploads"],
                Key="{}/{}".format(product.s3_path, file_key)
            ) 
        except botocore.exceptions.ClientError:
            # skip the rest of this iteration.
            continue

        product_content_length = response["ContentLength"]

        tmp_file_bytes = product.file_bytes
        tmp_file_bytes[file_key] = product_content_length
        product.file_bytes = tmp_file_bytes

    request.dbsession.add(product)
    request.dbsession.flush()

# commit/close the database transaction to really make changes.
request.tm.commit()

```


Thu Sep 22 10:50:28 AM EDT 2022
===================================

RAW SQL shop file usage:

.. code_block::

 sqlite> select shop_id, SUM(total_file_bytes), name from mps_product inner join mps_shop on mps_product.shop_id=mps_shop.id group by shop_id;
 
 shop_id|SUM(total_file_bytes)|name
 19890a44f65c11ec86a2843a4b34def8|1536736|fab shop
 1ba703a2015711edb393843a4b34def8|958612|2022 shop
 9c1b286c007911ed9016843a4b34def8|349261|localhost.localhost



Sat Jun 22 11:44:51 AM EDT 2024
===================================

I worked with gpt-4 to make this example playwright script to log in, create a shop and create a product, the ffmpeg portion works but ends up with a black screen video...

the idea was to use playwright for demo vids but it moves entirely too fast for a demonstration. anyways heres the code if you want to mess with it again someday:


```
const { chromium } = require('playwright');
const { exec } = require('child_process');
const readline = require('readline');
const fs = require('fs');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Check if FFmpeg is installed
  exec('ffmpeg -version', (error, stdout, stderr) => {
    if (error) {
      console.error('FFmpeg is not installed or not found in PATH.');
      process.exit(1);
    } else {
      console.log('FFmpeg is installed:', stdout);
    }
  });

  // Start recording with FFmpeg
  const ffmpeg = exec('ffmpeg -y -f x11grab -s 1600x900 -i :0.0 -r 30 output.mp4', (error, stdout, stderr) => {
    if (error) {
      console.error('Error starting FFmpeg:', error);
      return;
    }
    console.log('FFmpeg output:', stdout);
    console.error('FFmpeg error output:', stderr);
  });

  try {
    // Navigate to the join or log in page
    await page.goto('https://www.memopoly.com/join-or-log-in');

    // Fill in the email and submit
    await page.fill('input[name="email"]', 'russell.ballestrini+test@gmail.com');
    await page.click('#submit');

    // Wait for the user to input the verification code
    rl.question('Please enter the verification code sent to your email: ', async (code) => {
      try {
        // Manual pause to allow user to switch back to the browser
        console.log('Please switch back to the browser and wait for the verification to complete.');
        await new Promise(resolve => setTimeout(resolve, 10000)); // 10 seconds pause

        await page.fill('input[name="raw-otp"]', code);
        await page.click('#submit'); // Assuming the same submit button is used for verification

        // Wait for a specific element that indicates the user is logged in
        await page.waitForSelector('a[href="/s/new"]', { timeout: 60000 });

        // Navigate to create shop page and create a shop
        await page.goto('https://www.memopoly.com/s/new');
        await page.fill('#name_input', 'My Shop');
        await page.fill('#phone_number_input', '1234567890');
        await page.fill('#billing_address_input', '123 Main St');
        await page.fill('#description_input', 'This is my shop.');
        await page.click('input[type="submit"]');

        // Navigate to create product page and create a product
        await page.goto('https://www.memopoly.com/p/new');
        await page.fill('#title_input', 'My Product');
        await page.fill('#description_input', 'This is my product.');
        await page.fill('#price_input', '19.99');
        await page.click('input[type="submit"]');

        // Stop recording
        ffmpeg.stdin.write('q');
        ffmpeg.stdin.end();

        await browser.close();
        rl.close();

        // Check if the output video file exists
        if (fs.existsSync('output.mp4')) {
          console.log('Video recording saved as output.mp4');
        } else {
          console.error('Video recording was not saved.');
        }
      } catch (error) {
        console.error('Error during verification and shop/product creation:', error);
        await browser.close();
        rl.close();
      }
    });
  } catch (error) {
    console.error('Error during initial navigation and email submission:', error);
    await browser.close();
    rl.close();
  }
})();

```


Fri Feb 28 07:08:00 AM EST 2025
==================================

ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMB/WLWwqsQaQhhFu7Hcxbl5ZnpDvu88Thoq/MdXwSQZ fox@nixos
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBkkOwYqPfaQIliMt6p6aRAOv6xDBY6dmZnN2m5qmtzO fox@cmbp


Thu May 29 10:52:00 AM EST 2025
==================================

we upgraded the os & build host from 22.04 to 24.04 LTS


Mon Jan 27 09:00:00 AM EST 2025
==================================

All day defect hunt with Claude Code assistance: Fixed critical AttributeError in free cart checkout flow.

**The Bug**: Production users reported crashes when checking out with free carts (when coupons made the total $0.00). The error was `AttributeError: 'NoneType' object has no attribute 'active_card'` in cart.py lines 458 and 468.

**Root Cause Analysis**: When a cart total is free (≤ $0.64), no stripe_user_shop object is created, so `stripe_user_shop` becomes `None`. The buggy code tried to access `stripe_user_shop.active_card` without null checking.

**The Hunt Process**:
1. Started with SSH connectivity issues (IPv4 timeout) - fixed by disabling systemd socket activation
2. Found Python 2/3 compatibility bug in base64 decoding - fixed `string.decode("base64")` → `base64.b64decode()`  
3. Discovered the main AttributeError during user checkout with coupon-applied cart
4. Added comprehensive unit tests for cart payment threshold logic (64 cent boundary)
5. Created regression test but struggled with coupon discount application

**Major Discovery**: Cart discount memoization bug! The `discounted_shop_totals_in_cents` property was being cached before coupons were applied. When other cart properties accessed it early, the discount calculation returned stale results showing no discount even with valid coupons attached.

**The Fixes**:
1. **cart.py lines 458, 468**: Added null checks: `stripe_user_shop and stripe_user_shop.active_card is None` and `stripe_user_shop.active_card if stripe_user_shop else None`
2. **coupon.py lines 143, 177**: Added `cart._bust_memoized_attributes()` after applying/removing coupons to clear stale discount calculations  
3. **cart_checkout.j2 lines 10-24**: Added conditional rendering: only show card section when `active_card` is not None, otherwise show "No payment required"
4. **test_functional.py**: Added comprehensive regression test `test_cart_checkout_free_coupon_full_flow_regression` covering the complete flow

**Key Technical Insights**:
- Memoization can hide timing bugs in complex property dependencies
- Free cart logic (≤64 cents) bypasses payment flow entirely, creating edge cases
- Template-level null safety is crucial when backend can return None for optional objects
- SQLAlchemy session refresh can break memoized calculations

**Validation**: All 87 tests pass. The regression test verifies that free carts with applied coupons can successfully reach checkout confirmation without crashes.

**Credit**: Major thanks to groupr for collaborative debugging and Claude Code for systematic analysis. This was a complex multi-layer bug requiring fixes across model logic, view controllers, templates, and proper test coverage.

**Evening Production Update - Invoice Discount Bug**: Later in the day, discovered a critical gap in our invoice model coverage. The Invoice object's new discount calculation properties (`subtotal_in_cents`, `discount_amount_in_cents`, `total_in_cents`) were not adequately tested for production scenarios.

**Specific Production Error**: User groupr attempted to checkout a $6.00 game with a $6.00 off coupon (making the total free), which triggered additional errors in the invoice discount calculation system. The invoice model was missing comprehensive test coverage for the new discount properties we added to fix the cart checkout bug.

**Extended Fix - Invoice Model Testing**:
1. **Added 6 comprehensive integration tests** in `TestInvoiceDiscountIntegration` class covering all invoice discount scenarios
2. **Added 1 unit test regression** `test_invoice_line_item_automatic_price_from_product_regression` for production pricing scenarios  
3. **Fixed Price object relationships** - Invoice line items need proper Product→Price relationships for `item.price.price_in_cents` calculations
4. **Production-realistic pricing** - All tests use $3.00+ amounts reflecting real-world usage vs previous test amounts under $1.00

**Integration Test Coverage Added**:
- Invoice discount calculations with real coupon redemptions ($5 off $13 subtotal scenarios)
- Free invoice scenarios ($4 off $3.50 product = $0 total, no payment required)
- Multiple coupon stacking ($5 + $3 off $15 product)
- Invalid/expired coupon handling (no discount applied)
- Handling cost edge cases (None, zero, high amounts)  
- Negative total protection (`max(0, subtotal - discount + handling)`)

**Technical Discovery**: The InvoiceLineItem constructor calls `product.current_price` which can fail with DetachedInstanceError in certain database session contexts. Integration tests needed proper Price object creation with `Price(product, amount_in_cents)` calls.

**Final Status**: **105 total tests pass** (87 original + 13 invoice unit tests + 6 invoice integration tests). Invoice discount system now has bulletproof test coverage for production scenarios including groupr's exact $6 game + $6 coupon = free checkout case.