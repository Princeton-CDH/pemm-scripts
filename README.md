# pemm-scripts
![version](https://img.shields.io/github/package-json/v/Princeton-CDH/pemm-scripts)
[![clasp](https://img.shields.io/badge/built%20with-clasp-4285f4.svg)](https://github.com/google/clasp)
![license](https://img.shields.io/github/license/Princeton-CDH/pemm-scripts)

Tools for the [Princeton Ethiopian Miracles of Mary (PEMM)](https://cdh.princeton.edu/projects/ethiopian-miracles-mary-project/)
project, which catalogs folktales about miracles performed by the Virgin Mary
recorded in classical Ethiopic manuscripts. This project uses the [Apps Script Spreadsheet Service](https://developers.google.com/apps-script/reference/spreadsheet/) to create and manipulate data stored in [Google Sheets](https://docs.google.com/spreadsheets/).

## Development — Google Appscript code
### Setup

Clone the repository:
```sh
git clone git@github.com:Princeton-CDH/pemm.git
```
Install required javascript dependencies:
```sh
yarn # or npm install
```
Log in to `clasp`, the google apps script CLI:
```sh
yarn run login # or npm run login
```
This will open a browser window and ask you to authenticate with a google
account. after you've completed authentication, visit [script.google.com/home/usersettings](https://script.google.com/home/usersettings)
and turn on the "Google Apps Script API" toggle.

![Enable Apps Script API](https://user-images.githubusercontent.com/744973/54870967-a9135780-4d6a-11e9-991c-9f57a508bdf0.gif)

Next, create a new apps script project:
```sh
yarn setup # or npm run setup
```
Choose the `sheets` project type. `clasp` will automatically create a new
google sheets spreadsheet called "PEMM" in your google drive and initialize
an apps script project bound to that sheet.

Finally, compile the project's code and install it in your spreadsheet:
```sh
yarn build && yarn push # or npm run build && npm run push
```

Ff you open the newly created Google Sheet from your Drive, you should now
see the project's custom menu appear after a short delay. running commands for
the first time may prompt you to authenticate with google.

### Making changes

When you make changes to source code in the `src/` folder, you can rebuild the
project's code with:
```sh
yarn build # or npm run build
```
This will bundle all of the typescript that is loaded from `src/main.ts` and
transpile it into google apps script, creating the `build.gs` file in `build/`.

When actively developing, you can instead run a server with:
```sh
yarn dev # or npm run dev
```
This way, webpack will watch for changes and recompile the `build.gs` file
when you save any file.

### Pushing your changes

when you've finished making changes, you can push them up to google, which will
"install" the latest version in your spreadsheet:
```sh
yarn push # or npm run push
```
this will push the files in `build/` up to your project in the google apps
script IDE, overwriting its current contents.

### Debugging

You can see your deployed version of the project by
visiting the [google suite developer hub](https://script.google.com/home) and
clicking on your project. to enter the IDE, click "open project".

Here, you can run or debug functions that have been exported into the global
scope by binding them to the `global` object in `main.ts`. note that the first
time you run a function, google may ask you to grant permissions to the apps
script project.


## Development — Python code

Python code is in the `scripts` directory and includes a one-time data
conversion script, two scripts intended to be run as cron jobs,
and one very simple Flask app.

### Setup

- Recommended: create and activate a python 3.6 virtualenv::

    python3.6 -m venv pemm
    source pem/bin/activate

- Install required python dependencies::

    pip install -r requirements/dev.txt


See deploy notes and code for instructions on settings/configuration
and how to run the scripts.

## Tests

Not all code is tested, but the unit tests that exist can be run with
`pytest`

## License
This project is licensed under the [apache 2.0 license](https://github.com/Princeton-CDH/pemm-scripts/blob/master/LICENSE).
