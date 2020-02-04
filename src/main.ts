import { setupSheet } from './sheet'
import { setupValidation } from './validation'

import schema from './schema.json'

/**
 * Main entrypoint for the application. This code runs automatically every time
 * the user opens the spreadsheet.
 */
global.onOpen = () => {
    SpreadsheetApp.getUi()
        .createMenu('PEMM')
        .addItem('Set up active sheet', 'setupActiveSheet')
        .addItem('Set up validation', 'setupAllValidation')
        .addToUi()
}

/**
 * Add headers & field protection to the currently active sheet. Errors if the
 * current sheet's name isn't listed in the json schema.
 */
global.setupActiveSheet = (): void => {
    // get the active spreadsheet, sheet, and sheet's name
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet()
    const sheet = SpreadsheetApp.getActiveSheet()
    const sheetName = sheet.getName()

    // find the schema for this sheet, error if not found
    const sheetSchema = schema.sheets.find(({ name }) => name == sheetName)
    if (sheetSchema === undefined) {
        const msg = `Unable to set up "${sheetName}": no matching schema found.`
        Logger.log(msg)
        SpreadsheetApp.getUi().alert(msg)
        return
    }

    // set up the sheet
    setupSheet(spreadsheet, sheet, sheetSchema)
}

/**
 * Apply all data validation to the active spreadsheet. Requires that all named 
 * ranges used in validation already be created via setupSheet().
 */
global.setupAllValidation = (): void => {
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet()
    setupValidation(spreadsheet)
}