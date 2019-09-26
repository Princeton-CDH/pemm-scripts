import schema from './schema.json'
import { setupSpreadsheet } from './lib'

global.main = () => {
    /* set up spreadsheet */
    const spreadsheet = setupSpreadsheet(schema)

    /* create data validation */
    const manuscriptRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('manuscripts__id'))
        .setHelpText('Manuscript ID must be listed on Manuscripts sheet.')
        .setAllowInvalid(false)
        .build()

    const repositoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('repositories__name'))
        .setHelpText('Repository must be listed on Repositories sheet.')
        .setAllowInvalid(false)
        .build()

    const incipitRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('canonical_stories__incipit'))
        .setHelpText('Incipit must match a Canonical Story.')
        .setAllowInvalid(false)
        .build()

    const canonicalStoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('canonical_stories__macomber_id'))
        .setHelpText('Story instance must correspond to a Canonical Story.')
        .setAllowInvalid(false)
        .build()

    const booleanRule = SpreadsheetApp.newDataValidation()
        .requireCheckbox()
        .setAllowInvalid(false)
        .build()

    const folioRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=REGEXMATCH(TO_TEXT(A2), "[1-9]\d*[rvab]?")')
        .setHelpText('Folio must be number optionally followed by [r,v,a,b].')
        .setAllowInvalid(false)
        .build()

    /* apply rules/formulas */
    
    // manuscript
    spreadsheet.getRangeByName('manuscript__repository')
        .setDataValidation(repositoryRule)

    spreadsheet.getRangeByName('manuscript__original_repository')
        .setDataValidation(repositoryRule)

    // canonical story
    spreadsheet.getRangeByName('canonical_story__noneuropean_origin')
        .setDataValidation(booleanRule)
        .setFormula('=if(and(not(isblank(A2)), not(isblank(C2)), isblank(D2)), true,)')

    spreadsheet.getRangeByName('canonical_story__incipit')
        .setDataValidation(incipitRule)

    // story instance
    spreadsheet.getRangeByName('story_instance__manuscript')
        .setDataValidation(manuscriptRule)

    spreadsheet.getRangeByName('story_instance__canonical_story')
        .setDataValidation(canonicalStoryRule)

    spreadsheet.getRangeByName('story_instance__folio')
        .setDataValidation(folioRule)
}