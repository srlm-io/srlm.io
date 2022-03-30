---
layout: post
title: A Database Driven Static Website - Building UltrawideSnowboards.com
tags: [snowboarding, website, programming]
---

The retail snowboard industry is a mess. There are hundreds of brands selling a product that is all about feel but couched in the language of science. It's messed up, and just like cars every year there is a new lineup of buzzwordy models.

Throughout this mess there is the issue of sizing. As with other personal items size matters, but unlike other industries snowboarders can't keep it together long enough to standardize on a data interchange format that actually makes sense. Trying to find a board that's suitable for a big foot like me involved hours digging through slap dash online stores, downloading gigs of data in the process, and making lists of boards that might be suitable. The manual process is tedious to say the least.

![Screenshot of ultrawidesnowboards.com](/public/images/2022/03/29/ultrawidesnowboards_header_page.png)

[UltrawideSnowboards.com](https://ultrawidesnowboards.com/) is built to be a no-bull list of every board that fits a minimal set of criteria. For simplicity it is built as a static site but through some clever hacks has an almost dynamic database backend that makes adding new boards and brands easy.

Let's dive into all details and some technical Easter eggs (non robotic, GMO and gluten free, not derived from animal products).

<!--endexcerpt-->

Some background first: a snowboard is mostly about feel, but there are a few key metrics that are common to all snowboards and are provided by most manufacturers. These metrics are things that are easily measurable: length, width, the size of the curve it makes in the snow (aka sidecut), the spread of the foot mounting holes, the basic shape, the price. Pro tip if you're looking at board online and they don't bother to list these metrics: run away, what you're seeing is a couple of Bros hanging out in a garage and trying to steal your money so that they can go shredding. Anyways.

The vision for the site is to have a simple one page list of every board that meets a minimum set of size criteria. It's not trying to be a list of every snowboard ever made, it's not trying to sell one model over another, it's not even trying to be informative on all the differences between boards (it's unlikely that you could even make an informed decision without actually riding the boards in question so it's a fools quest to try and make a fully quantitative snowboard finder). The goal instead is just to put it all out there and provide a starting point for further research.

# Overview

The website is a static website ([Jekyll](https://jekyllrb.com/)) hosted on [Cloudflare Pages](https://pages.cloudflare.com/) and open source on [Github/UltrawideSnowboards](https://github.com/UltrawideSnowboards/ultrawidesnowboards.com). This gives it a global reach with very little effort along with all sorts of bonus things like HTTPS and build logs. It's also free. I'm using the various Cloudflare analytics, both server side and client side. The server side analytics ensures that I get an accurate page count even when client side trackers are blocked. I'm not really interested in feeding the massive Google and Facebook monsters.

The rest of this post is to document some of the more unique and interesting hacks I put together for this site.

# JSON Database for a Static Website

The list of snowboards is extremely repetitive. It's essentially the same format over and over, with a different image and some stats for each board:

![Screenshot example of a brand](/public/images/2022/03/29/ultrawidesnowboards_example_vendor.png)

It's also possible to filter the database to only display a selected subset. Custom board manufacturers, for example:

![Screenshot example of brands that do custom boards](/public/images/2022/03/29/ultrawidesnowboards_example_multiple_custom_vendors.png)

I could have just copied the HTML for each brand and board but that is tedious and uninspiring. A better way would be to store the boards in a database so that I can just pull the relevant boards and render them into a template. That's nice, but this is a static website. No databases for you.

So we need to get clever. Specifically, move the concept of a database from something "running" to something committed with the code. And even more specifically it boils down to this JSON file:

```json
{
    "brands": [
        {
            "custom_option": true,
            "logo": "2021/winterstick/logo.jpg",
            "name": "Winterstick",
            "short_name": "winterstick",
            "url": "https://www.winterstick.com/"
            "solid": {
                "boards": [
                    {
                        "category": "Powder",
                        "image": "2021/winterstick/roundtail.png",
                        "length": 168.0,
                        "name": "Roundtail",
                        "price": "$1000",
                        "profile": "Camber",
                        "setback": "50mm",
                        "shape": "Directional",
                        "short_name": "roundtail",
                        "side_cut": 9.5,
                        "stance": null,
                        "url": "https://www.winterstick.com/shop/roundtail-21-22/",
                        "waist_width": 27.8
                    },
                    {
                        "category": "Powder",
                        "image": "2021/winterstick/daydreamer.png",
                        "length": 167.0,
                        "name": "Day Dreamer",
                        "price": "$1200",
                        "profile": "Camber",
                        "setback": "50mm",
                        "shape": "Directional",
                        "short_name": "daydreamer",
                        "side_cut": 9.0,
                        "stance": null,
                        "url": "https://www.winterstick.com/shop/day-dreamer-21-22-solid/",
                        "waist_width": 27.5
                    }
                ],
                "maximum": null,
                "notes": "Winterstick will customize the width of a board for $100 more. Shown here are the stock ultrawide snowboards. All models available as a splitboard."
            },
            "splitboards": {
                "boards": [
                    ...
                ],
                "maximum": null,
                "notes": "..."
            },
            "custom": {
                "notes": "..."
            }
        }
        ...
    ]
}
```

Then we can create a Liquid template that iterates over a list of brands and boards:

```html
{% raw %}
{% for brand in brands %}
<div class="row" id="{{ brand.name }}">
    <div class="col-sm">
        <div class="card">
            <div class="card-body">
                        blah blash blah remove a bunch of stuff that isn't super interesting
                        ...
                        {% for board in brand[category].boards %}
                            <tr>
                                <td><a href="https://ultrawidesnowboards.com/url?link={{ board.url | url_encode}}" target="_blank"><img src="{{ site.github.url }}/assets/img/vendors/{{ board.image }}" class="snowboard"><img></a></td>
                                <td>{{ board.name }}</td>
                                <td>{{ board.length }}</td>
                                <td>{{ board.waist_width }}</td>
                                ...
                            </tr>
                        {% endfor %}
            ...
    </div>
</div>
{% endfor %}
{% endraw %}
```

Finally we can use that template by configuring our "filter" (ie, which subset of boards we're interested in displaying):

```html
{% raw %}
{% assign category = 'solid' %}

{% assign brands = site.data.snowboards.brands | where_exp:"brand", "brand[category].boards.size > 0" | where_exp:"brand", "brand[category].maximum != 0" %}
{% include brand-list.html %}
{% endraw %}
```

What all this does is allow me to create pages with different subtypes of boards all without having to have a real database or server. Everything is compiled at build time and generated into a static website. If I want to add a new brand or board I add it to the JSON, commit, and push. The build process takes care of bringing in the JSON content and converting to HTML. Easy.

There are limitations, of course. Users can't filter or sort. The default sort order ultimately boils down to the sort order of the data file. It's an unwieldy liquid template and include. But it works well for a hobby site like this, and I've never had the database go offline in the middle of Black Friday.

As a bonus, I have a handy script to make it easy to add new brands and boards to the database while avoiding the headache of manually editing JSON:

```bash
$ python3 snowboard_import_tool.py
Welcome to the snowboard import program
Please select an option:
Please select one of the following:
    0) Add Brand
    1) Add Snowboard
    2) Sort List
->
```

# Serverless Contact Form

When I first built the site I didn't bother to set up email, but I still wanted an easy way for people to reach out to me. I also did not want to set up a database or really any infrastructure at all. It [turns out](https://github.com/toperkin/staticFormEmails) that if you set up a Google Form then there is a secret url for it.

![Contact form screen shot](/public/images/2022/03/29/ultrawidesnowboards_contact_form.png)

The code is pretty simple:

```html
<form name="gform" id="gform" enctype="text/plain" action="https://docs.google.com/forms/d/e/FORM_HASH_HERE/formResponse?" target="hidden_iframe" onsubmit="submitted=true;">
    ...

    <input type="submit" class="btn btn-primary" value="Submit">
</form>
```

From there it just gets added to the responses Sheet. As a bonus you can configure the sheet to send an email every time a new row (ie contact) is added.

In the end I got some useful contacts and about 1-2 spam contacts per day. So somewhat useful, but the email solution just has less spam and is easier to monitor and respond to.

# Server Side Outbound Link Tracking

Although I don't really care about most analytics, I am interested in what links people click. Presumably this can be a measure of which are the most popular boards and it helps give a better impression of actual traffic and usage.

This hack is a variation on the form post above that works around the cross site scripting protection that is built into browsers. Instead of going directly to the target, each link goes to `https://ultrawidesnowboards.com/url?link=ACTUAL_LINK_HERE`. That `/url` address is a Cloudflare worker:

```js
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const statusCode = 301;
  console.log(request);
  for(var key of request.headers.keys()) {
   console.log(key);
   }
  try {
    const { searchParams } = new URL(request.url);
    let link = searchParams.get('link');

    let formSubmitParameters = new URLSearchParams();
    formSubmitParameters.append('submit', 'Submit');

    formSubmitParameters.append('entry.123456789', encodeURI(link));
    formSubmitParameters.append('entry.123456789', request.headers.get('user-agent'));
    // https://developers.cloudflare.com/workers/runtime-apis/request#incomingrequestcfproperties
    formSubmitParameters.append('entry.123456789', request.cf.country);
    formSubmitParameters.append('entry.123456789', request.cf.longitude);
    formSubmitParameters.append('entry.123456789', request.cf.latitude);
    formSubmitParameters.append('entry.123456789', request.cf.continent);
    formSubmitParameters.append('entry.123456789', request.cf.city);
    formSubmitParameters.append('entry.123456789', request.cf.region);
    formSubmitParameters.append('entry.123456789', request.cf.postalCode);

    const form_submit_response = await fetch('https://docs.google.com/forms/d/e/FORM_HASH_HERE/formResponse?' + formSubmitParameters.toString(), {
      method: 'GET',
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    return Response.redirect(link, 302);
  } catch (error) {
    return Response.redirect('https://ultrawidesnowboards.com/404', 302);
  }
}
```

This Cloudflare worker simply takes the request data and transforms it into a GET request that hits the Google Form, and then redirects the user to the desired URL. It's fast and relatively transparent. No client JS needed, and all the important non-creepy metadata is captured and sent to the Google Sheet. Once in the sheet some pivot tables do a nice job of aggregating the data in a useful way.
