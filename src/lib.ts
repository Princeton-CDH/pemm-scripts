// convenience type aliases for imported types
type Spreadsheet = GoogleAppsScript.Spreadsheet.Spreadsheet
type Sheet = GoogleAppsScript.Spreadsheet.Sheet
type Range = GoogleAppsScript.Spreadsheet.Range

// configuration object type for creating a Spreadsheet
interface SpreadsheetSchema {
    title: string,
    sheets: SheetSchema[],
}

// configuration object type for creating a Sheet
interface SheetSchema {
    name: string,
    fields: FieldSchema[],
    namedRanges: NamedRangeSchema[]
}

// configuration object type for creating a Field
interface FieldSchema {
    name: string,
}

// configuration object type for naming a given Range
interface NamedRangeSchema {
    name: string,
    range: string,
}

// pre-built header row style
export const headerStyle = SpreadsheetApp.newTextStyle().setBold(true).build()

/**
 * Creates and returns a new Spreadsheet object, including all sheets, according
 * to a provided schema object.
 * 
 * @param schema 
 */
export const setupSpreadsheet = (schema: SpreadsheetSchema): Spreadsheet => {
    const spreadsheet = SpreadsheetApp.create(schema.title)
    schema.sheets.forEach(sheetSchema => setupSheet(spreadsheet, sheetSchema))
    return spreadsheet
}

/**
 * Creates and returns a new Sheet object with headers initialized according to
 * a provided schema object.
 * 
 * @param spreadsheet 
 * @param schema 
 */
export const setupSheet = (spreadsheet: Spreadsheet, schema: SheetSchema): Sheet => {
    const sheet = spreadsheet.insertSheet(schema.name) // create the new sheet

    sheet // setup the headers
        .appendRow(schema.fields.map(f => f.name))
        .getDataRange()
        .setTextStyle(headerStyle)
        .setHorizontalAlignment('center')

    sheet.setFrozenRows(1) // freeze the headers

    if (schema.namedRanges) { // add named ranges, if any
        schema.namedRanges.forEach(r => setupNamedRange(spreadsheet, schema.name, r))
    }

    return sheet // return fully initialized sheet
}

/**
 * Assigns a human-friendly name to a given Range specified in A1 notation and
 * returns the Range object.
 * 
 * @param spreadsheet 
 * @param sheetName 
 * @param schema 
 */
export const setupNamedRange = (spreadsheet: Spreadsheet, sheetName: string, schema: NamedRangeSchema): Range => {
    const range = spreadsheet.getSheetByName(sheetName).getRange(schema.range) // Range object representing current area
    spreadsheet.setNamedRange(schema.name, range) // assign a name to that Range
    return spreadsheet.getRangeByName(schema.name) // return the given Range
}