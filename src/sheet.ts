import { Spreadsheet } from './spreadsheet'
import { indexToAlpha, slugify } from './lib'

// convenience type alias
export type Sheet = GoogleAppsScript.Spreadsheet.Sheet

// configuration object type for creating a Sheet
export interface SheetSchema {
    name: string,
    fields: FieldSchema[],
}

// configuration object type for creating a Field
interface FieldSchema {
    name: string,
    notes?: string,
    protected?: boolean
}

// pre-built styles
const headerStyle = SpreadsheetApp.newTextStyle().setBold(true).build()
const protectedBackgroundColor = '#ffe5be'

/**
 * Set up a single sheet on a given spreadsheet according to a provided schema.
 *
 * Inserts a row of specially formatted column headers corresponding to the
 * field names, generates globally accessible named ranges for each field, and
 * applies data protection where specified in the schema.
 *
 * Returns sheet after setup is complete.
 *
 * @param spreadsheet
 * @param sheet
 * @param schema
 */
export const setupSheet = (spreadsheet: Spreadsheet, sheet: Sheet, schema: SheetSchema): Sheet => {
    // insert the header row & freeze it
    sheet.insertRows(1)
    sheet.setFrozenRows(1)

    // add the field names as styled headers
    const fieldNames = schema.fields.map(f => f.name)
    const fieldNotes = schema.fields.map(f => f.notes ? f.notes : '')
    sheet
        .getRange(1, 1, 1, fieldNames.length)
        .setValues([fieldNames])
        .setNotes([fieldNotes])
        .setTextStyle(headerStyle)
        .setHorizontalAlignment('center')

    // generate named ranges for all the fields
    schema.fields.forEach((field, index) => {
        // select data for the range in a1 notation like 'Sheet Name'!B2:B, see:
        // https://developers.google.com/sheets/api/guides/concepts#a1_notation
        const alpha = indexToAlpha(index)
        const a1notation = `\'${schema.name}\'!${alpha}2:${alpha}`
        const dataRange = sheet.getRange(a1notation)

        // create a global named range 'sheet_name__field_name', see:
        // https://developers.google.com/apps-script/reference/spreadsheet/named-range
        const rangeName = `${slugify(schema.name)}__${slugify(field.name)}`
        spreadsheet.setNamedRange(rangeName, dataRange)

        // add protection if the range should be read-only; see:
        // https://developers.google.com/apps-script/reference/spreadsheet/protection
        if (field.protected) {
            const protection = dataRange.protect()
            const me = Session.getActiveUser()
            const editorEmails = protection.getEditors().map(u => u.getEmail())
            protection.addEditor(me) // ensure we can still edit
            protection.removeEditors(editorEmails) // remove all others
            dataRange.setBackground(protectedBackgroundColor)
        }
    })

    // return sheet when setup completed
    return sheet
}