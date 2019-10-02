# pemm
![version](https://img.shields.io/github/package-json/v/Princeton-CDH/pemm)
[![clasp](https://img.shields.io/badge/built%20with-clasp-4285f4.svg)](https://github.com/google/clasp)
![license](https://img.shields.io/github/license/Princeton-CDH/pemm)

Google Apps Script tools for the [Princeton Ethiopian Miracles of Mary (PEMM)](https://cdh.princeton.edu/projects/ethiopian-miracles-mary-project/)
project, which catalogs folktales about miracles performed by the Virgin Mary
recorded in classical Ethiopic manuscripts.

## developing
### setup
clone the repository:
```sh
git clone git@github.com:Princeton-CDH/pemm.git
```
install required javascript dependencies:
```sh
yarn # or npm install
```
log in to `clasp`, the google apps script CLI:
```sh
yarn login # or npm run login
```
this will open a browser window and ask you to authenticate with a google
account. after you've completed authentication, visit [script.google.com/home/usersettings](https://script.google.com/home/usersettings)
and turn on the "Google Apps Script API" toggle.

![Enable Apps Script API](https://user-images.githubusercontent.com/744973/54870967-a9135780-4d6a-11e9-991c-9f57a508bdf0.gif)

finally, create a new apps script project:
```sh
yarn setup # or npm run setup
```
choose the `standalone` project type. now you're ready to make changes
to the code.
### making changes
before editing source code, run a development build server with webpack:
```sh
yarn build # or npm run build 
```
this will bundle all of the typescript that is loaded from `main.ts` and
transpile it into google apps script, creating the `build.gs` file in `build/`.
webpack will watch for changes and recompile the `build.gs` file when you save.
### pushing your changes
when you've finished making changes, you can push them up to google:
```sh
yarn push # or npm run push
```
this will push the files in `build/` up to your project in the google apps
script IDE, overwriting its current contents. you can open the project by
visiting the [google suite developer hub](https://script.google.com/home) and
clicking on your project. to enter the IDE, click "open project". here, you can
run or debug functions that have been exported into the global scope by binding
them to the `global` object in `main.ts`. note that the first time you run a
function, google will ask you to grant permissions to the apps script project.

## license
this project is licensed under the [apache 2.0 license](https://github.com/Princeton-CDH/pemm/blob/master/LICENSE).