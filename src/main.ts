import schema from './schema.json'
import { setupSpreadsheet } from './lib'

global.main = () => {
    /* set up spreadsheet */
    const spreadsheet = setupSpreadsheet(schema)

    /* create data validation */
    const manuscriptRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('manuscript__id'))
        .setHelpText('Manuscript ID must be listed on Manuscripts sheet.')
        .setAllowInvalid(false)
        .build()

    const collectionRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('collection__abbreviation'))
        .setHelpText('Collection must be listed on Collections sheet.')
        .setAllowInvalid(false)
        .build()

    const incipitRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('canonical_story__incipit'))
        .setHelpText('Incipit must match a Canonical Story.')
        .setAllowInvalid(false)
        .build()

    const canonicalStoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('canonical_story__macomber_id'))
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

    const positiveIntegerRule = SpreadsheetApp.newDataValidation()
        .requireNumberGreaterThan(0)
        .setHelpText('Must be a positive integer.')
        .setAllowInvalid(false)
        .build()

    const storyOriginRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('story_origin__name'))
        .setHelpText('Origin must be listed on Story Origin sheet.')
        .setAllowInvalid(false)
        .build()

    const fourDigitYearRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=REGEXMATCH(TO_TEXT(A2), "\d{4}"')
        .setHelpText('Must be a 4-digit year.')
        .setAllowInvalid(false)
        .build()

    /* apply rules/formulas */
    
    // manuscript
    spreadsheet.getRangeByName('manuscript__collection')
        .setDataValidation(collectionRule)

    spreadsheet.getRangeByName('manuscript__original_collection')
        .setDataValidation(collectionRule)

    spreadsheet.getRangeByName('manuscript__date_range_start')
        .setDataValidation(fourDigitYearRule)

    spreadsheet.getRangeByName('manuscript__date_range_end')
        .setDataValidation(fourDigitYearRule)   

    // canonical story
    spreadsheet.getRangeByName('canonical_story__origin')
        .setDataValidation(storyOriginRule)

    spreadsheet.getRangeByName('canonical_story__noneuropean_origin')
        .setDataValidation(booleanRule)

    spreadsheet.getRangeByName('canonical_story__incipit')
        .setDataValidation(incipitRule)

    spreadsheet.getRangeByName('canonical_story__macomber_id')
        .setDataValidation(positiveIntegerRule)

    // story instance
    spreadsheet.getRangeByName('story_instance__manuscript')
        .setDataValidation(manuscriptRule)

    spreadsheet.getRangeByName('story_instance__canonical_story')
        .setDataValidation(canonicalStoryRule)

    spreadsheet.getRangeByName('story_instance__folio')
        .setDataValidation(folioRule)

    spreadsheet.getRangeByName('story_instance__column_start')
        .setDataValidation(positiveIntegerRule)
    
    spreadsheet.getRangeByName('story_instance__line_start')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__column_end')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__line_end')
        .setDataValidation(positiveIntegerRule)

    // story origin
    spreadsheet.getRangeByName('story_origin__european')
        .setDataValidation(booleanRule)
}