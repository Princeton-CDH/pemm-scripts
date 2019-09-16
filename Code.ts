import 'google-apps-script'

const sheetsConfig = [
    {
        "title": "Story Instances",
        "fields": [
            "Manuscript",
            "Canonical Story",
            "Folio Start",
            "Folio End",
            "Digitized Image",
            "Link",
            "Order in Manuscript",
            "Number of Images",
            "Has Illustrations",
            "Incipit",
            "Confidence Score"
        ]
    },
    {
        "title": "Canonical Stories",
        "fields": [
            "Macomber ID",
            "Macomber Title",
            "Origin",
            "Poncelet Number",
            "Non-European Origin",
            "Incipit",
            "Other IDs",
            "Other Titles"
        ]
    },
    {
        "title": "Manuscripts",
        "fields": [
            "ID",
            "Title",
            "Repository",
            "Original Repository",
            "Total Folios",
            "Total Pages",
            "Century",
            "Date Range",
            "Provenance",
            "Number of Stories"
        ]
    },
    {
        "title": "Repositories",
        "fields": [
            "Name",
            "Abbreviation",
            "Location"
        ]
    }
]

const centuries = [
    '12th',
    '13th',
    '14th',
    '15th',
    '16th',
    '17th',
    '18th',
    '19th',
    '20th',
]

function main() {
    // main spreadsheet
    const spreadSheet = SpreadsheetApp.create('PEMM Test')

    // setup header style
    const headerStyle = SpreadsheetApp
        .newTextStyle()
        .setBold(true)
        .build()

    // create the sheets
    sheetsConfig.forEach(sheet => {
        // create the sheet
        const newSheet = spreadSheet.insertSheet(sheet.title)
        // add the headers and protect them
        newSheet
            .appendRow(sheet.fields)
            .getDataRange()
            .setTextStyle(headerStyle)
            .setHorizontalAlignment('center')
        // freeze the headers
        newSheet.setFrozenRows(1)
    })

    // remove the default sheet
    const defaultSheet = spreadSheet.getSheetByName('Sheet1')
    spreadSheet.deleteSheet(defaultSheet)

    // create named ranges
    const repoNames = spreadSheet
        .getSheetByName('Repositories')
        .getRange('A2:A')
    const manuscriptIds = spreadSheet
        .getSheetByName('Manuscripts')
        .getRange('A2:A')
    const incipits = spreadSheet
        .getSheetByName('Canonical Stories')
        .getRange('F2:F')
    const canonicalStoryIds = spreadSheet
        .getSheetByName('Canonical Stories')
        .getRange('A2:A')
    spreadSheet.setNamedRange('RepositoryNames', repoNames)
    spreadSheet.setNamedRange('ManuscriptIDs', manuscriptIds)
    spreadSheet.setNamedRange('Incipits', incipits)
    spreadSheet.setNamedRange('CanonicalStoryIDs', canonicalStoryIds)

    // create data validation rules
    const manuscriptRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(manuscriptIds)
        .setAllowInvalid(false)
        .setHelpText('Manuscript ID must be listed on Manuscripts sheet.')
        .build()
    const repositoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(repoNames)
        .setAllowInvalid(false)
        .setHelpText('Repository must be listed on Repositories sheet.')
        .build()
    const incipitRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(incipits)
        .setAllowInvalid(false)
        .setHelpText('Incipit must match a Canonical Story.')
        .build()
    const canonicalStoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(canonicalStoryIds)
        .setAllowInvalid(false)
        .setHelpText('Story instance must correspond to a Canonical Story.')
        .build()
    const booleanRule = SpreadsheetApp.newDataValidation()
        .requireCheckbox()
        .setAllowInvalid(false)
        .build()
    const centuryRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(centuries)
        .setAllowInvalid(false)
        .setHelpText('Century must be between 10 and 20.')
        .build()

    // apply data validation rules and formulas
    spreadSheet.getSheetByName('Manuscripts')
        .getRange('C2:C')
        .setDataValidation(repositoryRule)
    spreadSheet.getSheetByName('Manuscripts')
        .getRange('D2:D')
        .setDataValidation(repositoryRule)
    spreadSheet.getSheetByName('Canonical Stories')
        .getRange('E2:E')
        .setDataValidation(booleanRule)
        .setFormula('=if(and(not(isblank(A2)), not(isblank(C2)), isblank(D2)), true,)')
    spreadSheet.getSheetByName('Canonical Stories')
        .getRange('F2:F')
        .setDataValidation(incipitRule)
    spreadSheet.getSheetByName('Story Instances')
        .getRange('A2:A')
        .setDataValidation(manuscriptRule)
    spreadSheet.getSheetByName('Story Instances')
        .getRange('B2:B')
        .setDataValidation(canonicalStoryRule)
}
