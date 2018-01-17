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

NYC Councilmatic uses Solr version 7 to power legislation searches. If you already have Solr version 7 installed for another app, then you can by-pass these installation instructions. Otherwise, carefully read on.

Download latest solr distribution from a [reliable mirror](http://www.apache.org/dyn/closer.cgi/lucene/solr/). The Apache foundation suggests using the [University of Toronto mirror](http://mirror.dsrg.utoronto.ca/apache/lucene/solr/). You need to download two files:
(1) `solr-7.1.0.tgz` - Solr itself
(2) solr-7.1.0.tgz.asc - the detached signature for verification. Visit the [Apache server](http://archive.apache.org/dist/lucene/solr/7.1.0/), and then, `curl` or `wget` the signature to the directory where you downloaded Solr.

With the above downloads, [verify the package](https://www.apache.org/info/verification.html) using the .asc signature. Apache provides some rigid standards for verification, e.g., "face-to-face communication with multiple government-issued photo identification confirmations." However, you can also conduct your own Google background check on the signature owner to validate their identity. 

Finally, untar the directory (`tar xvf solr-7.1.0.tgz`), and `mv` it into `/opt` (or `/Applications`, for Mac users).

Congratulations! You downloaded Solr.

**Basic Solr Setup**

The following steps are fairly straightforward:

1. **Visit** your latest download, take a look at the solr directory (`cd solr-7.1.0/server/solr`), and within it, create a repo for NYC Councilmatic: `mkdir nyc-council-councilmatic`
2. In the newly created nyc-council-councilmatic repo, **create** a core file: `touch nyc-council-councilmatic/core.properties` (This file helps solr discover cores for multicore processing. That way, a single Solr installation can run multiple apps.)
3. Solr expects to find several files in the conf repo of Councilmatic. We'll use the example conf (`sample_techproducts_configs`) and pare it down. **Copy** the contents of `solr/configsets/sample_techproducts_configs/` into `solr/nyc-council-councilmatic`: `cp -R configsets/sample_techproducts_configs/* nyc-council-councilmatic/`.

Note: you do not need all the files provided in `sample_techproducts_configs`. You can safely remove several, including: `_rest_managed.json`, `_schema_analysis_stopwords_english.json`, `_schema_analysis_synonyms_english.json`, `mapping-FoldToASCII.txt`, `mapping-ISOLatin1Accent.txt`, `update-script.js`. You can peek inside `solr_configs` in the nyc-council-councilmatic repo to see what you do and do not need. 

**Define Schema and Run Solr**

We use a [classic schema file](https://lucene.apache.org/solr/guide/7_1/schema-factory-definition-in-solrconfig.html#switching-from-managed-schema-to-manually-edited-schema-xml), which defines the searchable fields in your application. You need to do three things to get situated with the Councilmatic schema.

1. Open `solrconfig.xml`, which lives inside `/solr/nyc-council-councilmatic/conf/`. Anywhere between the `<config>` tags, add the following:

```
<schemaFactory class="ClassicIndexSchemaFactory"/>
```

2. Rename the managed-schema file to schema.xml:

```
cd /solr/nyc-council-councilmatic/conf
mv managed-schema schema.xml
```

3. The `solr_configs` repo in NYC Councilmatic contains a working schema.xml. Copy the contents of this file into `/solr/nyc-council-councilmatic/conf/schema.xml`.

You're almost done - a few steps remain! In `settings_deployment.py`, be sure to include the correct URL in HAYSTACK_CONNECTIONS. The URL should align with the name of the solr core you created above:

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

Is your solr running? Go to `/solr-7.1.0/bin`, and execute:

```
./solr start
```

Then, visit [http://127.0.0.1:8983/solr/#/](http://127.0.0.1:8983/solr/#/), and see solr in action. If you need to stop solr, do the following:

```
/solr stop -p 8983
```

Finally, build your index, and visit `/search` on Councilmatic:

```
python manage.py rebuild_index
```

## Google Calendar API

NYC Councilmatic expects a client_secret.json file. It contains an API client ID and client secret, and so, this file should not appear in version control. You can create your own `json` file by following the [Step 1](https://developers.google.com/google-apps/calendar/quickstart/python) directions provided by Google.

## Dockerize Solr

You can run Solr locally, if you please. Containers, however, make life easier. Containers – as the name implies – are autonomous packages of code, little presents under the Christmas tree. All components of a Django application can be "containerized," [using Docker](https://www.docker.com/what-container). For ease of deployment, we put Solr inside a Docker container. 

Look at `docker-compose.yml`. It includes a solr container (or "service") called nyccouncilmatic_solr. This container has an image – [layers of code downloaded from Docker to disk](https://hub.docker.com/_/solr/). It also includes a list of volumes – resources shared between the host and the container. The first volume in the solr container has an environment variable: you need to customize it. Create an `.env` file at the root of nyc-council-councilmatic. You need to add a DATA_DIR variable that points to an empty repo, somewhere on your local machine. You can put this empty repo wherever you like. The following makes a couple suggestions:

```
# on Linux
DATA_DIR='/data/nyccouncilmatic-solr'
# on MacOS
DATA_DIR='/tmp/nyccouncilmatic-solr'
```

But why? This empty repo enforces data persistence. Data persists better on the host, then on the  impermanent Docker container. (Docker philosophy purports the temporality of containers. A container should do its work, then “poof,” go away.)

Dockerizing Solr comes with a few more "gotchas". We use [`solr-create -c nyc-council-councilmatic`](https://github.com/docker-solr/docker-solr#creating-cores) to create the nyc-council-councilmatic solr core. `solr-create` (as opposed to `solr-precreate`) insures that Solr rereads the schema file. However, the `solr-create` command [does not (re)create the core, if it finds a pre-existing core directory](https://github.com/docker-solr/docker-solr/blob/master/7.1/alpine/scripts/solr-create#L38). Thus, we tell Solr to discover data elsewhere:
(1) by telling docker-compose to mount data here: `/nyc-data`
(2) by pointing the solrconfig.xml to this location: `<dataDir>/nyc-data</dataDir>`  

Now, you are ready to instantiate your solr container! Run:

```
docker-compose up
# Or, run it in the background
docker-compose up -d
```

You can stop the container (if running as a daemon process), whenever you please:

```
docker-compose stop nyccouncilmatic_solr
```

## Solr down?

Is solr down on the server? If so, shell into the councilmatic server, and run:

```
sudo -u solr ./solr start -p 8984
```

(Specify the port. Otherwise, solr will try to run on 8983.)

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
