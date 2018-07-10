# Logan
Logan is a log analysis tool based on Django Meerkat.
For now it is a full Django project,
but the goal is to refactor it in a Meerkat plugin
once plugins are supported by Meerkat.

- [Installation](#installation)
- [Building](#building)
- [Loading fixtures](#loading-fixtures)
- [Running](#running)
- [Usage](#usage)

## Installation
This tool is not installable through pip yet.
Clone the repository with `git clone git@gitlab.com:pawamoy/logan`.

## Building
This project is executed through Docker.
Run `make build` to build the Docker images,
then `make build-database` to initialize the database.
You can also make yourself a super-user with `make build-superuser`.

## Loading fixtures
Copy your NginX logs file in the repository.
The file must be named `nginx-access.log`.
Then run `make python` to get access to a Python shell inside a container.
Execute the following commands to parse and insert the logs in the database:
```python
from meerkat.models import RequestLog
RequestLog.parse_all()
```

## Running
To run the project, use the `make up` command.
Then go to [http://localhost:8000/admin](http://localhost:8000/admin)
and login with your super-user name and password.

## Usage
Once logged in, go to the requests logs page in the admin interface at
[http://localhost:8000/admin/meerkat/requestlogs](http://localhost:8000/admin/meerkat/requestlogs).
Use the available buttons and links to filter your selection.

![admin_page](img/admin_page.png)

Select one or more or all items in the current filtered queryset,
then click on the action called "Generate analysis for the selected items."

![admin_page](img/admin_page_selected.png)

Once the analysis is done, a message will appear with the link to see it,
something like [/analysis/1](http://localhost:8000/analysis/1/).

![admin_page](img/admin_page_analysis_done.png)

Click on the link to go to the analysis page.

![admin_page](img/analysis_page.png)

Use the mouse wheel to zoom/unzoom the graph.

![admin_page](img/analysis_page_zoom.png)

You can see all the analysis you generated on the home page.

![admin_page](img/home_page.png)