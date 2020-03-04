import { SheetSchema, setupSheet } from './sheet'
import { setupValidation } from './validation'

// convenience type alias
export type Spreadsheet = GoogleAppsScript.Spreadsheet.Spreadsheet

// configuration object type for creating a Spreadsheet
export interface SpreadsheetSchema {
    title: string,
    sheets: SheetSchema[],
}

/**
 * Sets up all sheets on a given spreadsheet according to a provided schema,
 * creating each sheet if it doesn't already exist.
 * 
 * Applies all data validation.
 * 
 * @param spreadsheet
 * @param schema 
 */
export const setupSpreadsheet = (spreadsheet: Spreadsheet, schema: SpreadsheetSchema): Spreadsheet => {
    schema.sheets.forEach(({ name, fields }) => {
        // if the sheet doesn't exist yet, create it
        let sheet = spreadsheet.getSheetByName(name)
        if (sheet === null) sheet = spreadsheet.insertSheet(name)
        
        // call setupSheet to set up the sheet
        setupSheet(spreadsheet, sheet, { name, fields })
    })

    // apply data validation
    setupValidation(spreadsheet)
    
    // return spreadsheet when setup completed
    return spreadsheet
}

