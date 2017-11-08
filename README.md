# New York City Councilmatic

![New York City Councilmatic](https://www.councilmatic.org/images/nyc.jpg)

NYC Councilmatic is a tool for understanding and tracking what’s happening in New York City Council.

This site connects NYC residents to local city council offices, for greater online public dialogue about issues in their communities.

Councilmatic helps you:

* Keep up with what your local representatives is up to
* See the schedule of public events
* Track and comment on issues you care about

NYC Councilmatic is free, non-profit, and non-partisan and the easiest way to access official New York City Council information.

Part of the [Councilmatic family](https://www.councilmatic.org/).


## Setup

**Install OS level dependencies:**

* Python 3.4
* PostgreSQL 9.4 +

**Install app requirements**

We recommend using [virtualenv](http://virtualenv.readthedocs.org/en/latest/virtualenv.html) and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html) for working in a virtualized development environment. [Read how to set up virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Once you have virtualenvwrapper set up,

```bash
git clone git@github.com:datamade/nyc-council-councilmatic.git
cd nyc-council-councilmatic
mkvirtualenv nyc-council-councilmatic
pip install -r requirements.txt
```

Afterwards, whenever you want to use this virtual environment to work on nyc-councilmatic, run `workon nyc-council-councilmatic`

**Create your settings file**

```bash
cp councilmatic/settings_deployment.py.example councilmatic/settings_deployment.py
```

Turn on DEBUG, and update your secret key to whatever you like.

```bash
SECRET_KEY = 'super secret key'

DEBUG = True
```

**Setup your database**

Before we can run the website, we need to create a database.

```bash
createdb nyc_councilmatic
```

Then, run migrations.

```bash
python manage.py migrate
```

Create an admin user. Set a username and password when prompted.

```bash
python manage.py createsuperuser
```

## Importing data from the open civic data api

Run the import_data management command. This will take a while, depending on volume (probably around half an hour ish for NYC)

```bash
python manage.py import_data
```

By default, the import_data command is smart about what it looks at on the OCD API. If you already have bills loaded, it won't look at everything on the API - it'll look at the most recently updated bill in your database, see when that bill was last updated on the OCD API, & then look through everything on the API that was updated after that point. If you'd like to load things that are older than what you currently have loaded, you can run the import_data management command with a `--delete` option, which removes everything from your database before loading.

The import_data command has some more nuance than the description above, for the different types of data it loads. If you have any questions, open up an issue and pester us to write better documentation.

## Running NYC Councilmatic locally

``` bash
python manage.py runserver
```

navigate to http://localhost:8000/

## Setup Solr search

**Install Open JDK or update Java**

On Ubuntu:

``` bash
$ sudo apt-get update
$ sudo apt-get install openjdk-7-jre-headless
```

On OS X:

1. Download latest Java from
[http://java.com/en/download/mac_download.jsp?locale=en](http://java.com/en/download/mac_download.jsp?locale=en)
2. Follow normal install procedure
3. Change system Java to use the version you just installed:

    ``` bash
    sudo mv /usr/bin/java /usr/bin/java16
    sudo ln -s /Library/Internet\ Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java /usr/bin/java
    ```

**Download Solr**

NYC Councilmatic uses Solr version 7 to power search fro legislation. If you already have Solr version 7 installed for another app, then you can by-pass these installation instructions. Otherwise, carefully read on.

Download latest solr distribution from a [reliable mirror](http://www.apache.org/dyn/closer.cgi/lucene/solr/). The Apache foundation suggests using the [University of Toronto mirror](http://mirror.dsrg.utoronto.ca/apache/lucene/solr/). You need to download two files:
(1) `solr-7.1.0.tgz` - Solr itself
(2) solr-7.1.0.tgz.asc - the detached signature for verification. (If you do not find a signature in the Toronto mirror, then grab a signature from [elsewhere](http://www.apache.org/dist/lucene/solr/7.1.0/). You can `curl` or `wget` the signature to the directory where you downloaded Solr.

Next, [verify the package](https://www.apache.org/info/verification.html) using the .asc signature from the official solr mirror. Apache provides some rigid standards for verification, e.g., "face-to-face communication with multiple government-issued photo identification confirmations." However, you can also conduct your own Google background check on the signature owner to validate their identity. 

Finally, untar the directory (`tar xvf solr-7.1.0.tgz`), and `mv` it into `/opt` (or `/Applications`, for Mac users).

Congratulations! You downloaded Solr.

**Setup Solr**

The next steps are fairly straightforward:

(1) Visit your latest download, take a look at the solr directory (`cd solr-7.1.0/server/solr`), and within it, create a repo for NYC Councilmatic: `mkdir nyc-council-councilmatic`

(2) In the newly created nyc-council-councilmatic repo, create a core file: `touch nyc-council-councilmatic/core.properties` (This file helps solr discover cores for multicore processing. That way, one Solr installation can run multiple apps.)

(3) Solr expects to find several files in the conf repo of Councilmatic. We'll use the example conf (`sample_techproducts_configs`) and parse it down. Copy the contents of `solr/configsets/sample_techproducts_configs/` into `solr/nyc-council-councilmatic`: `cp -R configsets/sample_techproducts_configs/* nyc-council-councilmatic/`.

[Note: you do not need all the files provided in `sample_techproducts_configs`. You can safely remove several, including: _rest_managed.json, _schema_analysis_stopwords_english.json, _schema_analysis_synonyms_english.json, mapping-FoldToASCII.txt, mapping-ISOLatin1Accent.txt, update-script.js.]

Next, you need to set-up the NYC Councilmatic schema. We use a [classic schema file](https://lucene.apache.org/solr/guide/7_1/schema-factory-definition-in-solrconfig.html#switching-from-managed-schema-to-manually-edited-schema-xml). First, open `solrconfig.xml`, which lives inside `/solr/nyc-council-councilmatic/conf/`. Anywhere between the `<config>` tags, add the following:

```
<schemaFactory class="ClassicIndexSchemaFactory"/>
```

Then, rename the managed-schema file to schema.xml:

```
cd /solr/nyc-council-councilmatic/conf
mv managed-schema schema.xml
```

The solr_scripts repo in NYC Councilmatic contains a working schema.xml. Copy the contents of this file into `/solr/nyc-council-councilmatic/conf/schema.xml`.

In `settings_deployment.py`, be sure to include the correct URL in HAYSTACK_CONNECTIONS. The URL should align with the name of the solr core you created above:

```
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        #'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        'URL': 'http://127.0.0.1:8983/solr/nyc-council-councilmatic',
    },
}
```

Finally, build your index:

```
python manage.py rebuild_index
```

Is your solr running? Go to `/solr-7.1.0/bin`, and run:

```
./solr start
```

Then, visit [http://127.0.0.1:8983/solr/#/](http://127.0.0.1:8983/solr/#/), and see solr in action. If you need to stop solr, do the following:

```
/solr stop -p 8983
```

**OPTIONAL: Install and configure Jetty for Solr**

Just running Solr as described above is probably OK in a development setting.
To deploy Solr in production, you'll want to use something like Jetty. Here's
how you'd do that on Ubuntu:

``` bash
sudo apt-get install jetty

# Backup stock init.d script
sudo mv /etc/init.d/jetty ~/jetty.orig

# Get init.d script suggested by Solr docs
sudo cp solr_scripts/jetty.sh /etc/init.d/jetty
sudo chown root.root /etc/init.d/jetty
sudo chmod 755 /etc/init.d/jetty

# Add Solr specific configs to /etc/default/jetty
sudo cp solr_scripts/jetty.conf /etc/default/jetty

# Change ownership of the Solr directory so Jetty can get at it
sudo chown -R jetty.jetty /opt/solr

# Start up Solr
sudo service jetty start

# Solr should now be running on port 8983
```

**Regenerate Solr schema**

While developing, if you need to make changes to the fields that are getting
indexed or how they are getting indexed, you'll need to regenerate the
schema.xml file that Solr uses to make it's magic. Here's how that works:

```
python manage.py build_solr_schema > solr_scripts/schema.xml
cp solr_scripts/schema.xml /opt/solr/solr/collection1/conf/schema.xml
```

In order for Solr to use the new schema file, you'll need to restart it.

**Using Solr for more than one Councilmatic on the same server**

If you intend to run more than one instance of Councilmatic on the same server,
you'll need to take a look at [this README](solr_scripts/README.md) to make sure you're
configuring things properly.

## A note on caching

Councilmatic uses template fragment caching, made easy with the [django-adv-cache-tag](http://documentup.com/twidi/django-adv-cache-tag) library. Instances of Councilmatic with [notifications](https://github.com/datamade/django-councilmatic-notifications) contain dynamically generated elements that change with each user. We do not cache such elements, but we do cache the content around them. The cached material (cache keys) expires in 600 seconds (ten minutes).

Be sure to include `django-adv-cache-tag` in your requirements and INSTALLED APPS, and also to turn off global caching (mainly, do not include FetchFromCacheMiddleware and UpdateCacheMiddleware in MIDDLEWARE_CLASSES). Finally, in settings.py, add `ADV_CACHE_INCLUDE_PK = True`, which allows you to give each cache key a primary ID.

N.B. Do not wrap the Events and Search page in cache tags, since these too have dynamically generated content.

## Team

* David Moore, Participatory Politics Foundation - project manager
* Forest Gregg, DataMade - Open Civic Data (OCD) and Legistar scraping
* Cathy Deng, DataMade - data models, front end
* Derek Eder, DataMade - front end
* Eric van Zanten, DataMade - search and dev ops
* Regina Compton, DataMade - developer

## Errors / Bugs

If something is not behaving intuitively, it is a bug, and should be reported.
Report it here: https://github.com/datamade/nyc-councilmatic/issues

## Note on Patches/Pull Requests

* Fork the project.
* Make your feature addition or bug fix.
* Commit, do not mess with rakefile, version, or history.
* Send a pull request. Bonus points for topic branches.

## Copyright

Copyright (c) 2015 Participatory Politics Foundation and DataMade. Released under the [MIT License](https://github.com/datamade/nyc-councilmatic/blob/master/LICENSE).
