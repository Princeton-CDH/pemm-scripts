import { SheetSchema } from './sheet'

// convenience type alias
export type Spreadsheet = GoogleAppsScript.Spreadsheet.Spreadsheet

// configuration object type for creating a Spreadsheet
export interface SpreadsheetSchema {
    title: string,
    sheets: SheetSchema[],
}



