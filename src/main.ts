import schema from './schema.json'
import { setupSpreadsheet } from './lib'

global.main = () => {
    /* set up spreadsheet */
    const spreadsheet = setupSpreadsheet(schema)

    /* create data validation */
    const manuscriptRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('manuscript__name'))
        .setHelpText('Manuscript name must be listed on Manuscripts sheet.')
        .setAllowInvalid(false)
        .build()

    const collectionRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('collection__name'))
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
        .setHelpText('Must reference a Canonical Story Macomber ID.')
        .setAllowInvalid(false)
        .build()

    const canonicalStoryTitleRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('canonical_story__macomber_title'))
        .setHelpText('Must reference a Canonical Story Macomber Title.')
        .setAllowInvalid(false)
        .build()

    const booleanRule = SpreadsheetApp.newDataValidation()
        .requireCheckbox()
        .setAllowInvalid(false)
        .build()

    const confidenceScoreRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(["High", "Medium", "Low"])
        .setAllowInvalid(false)
        .build()

    const regionRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(["Africa", "Europe", "Levant", "Other"])
        .setAllowInvalid(false)
        .build()

    /* FIXME this formula has to depend on a cell value specified in A1
     * notation for some reason, so it's brittle and will fail if the order
     * of fields is changed. Not sure how to get around this. See:
     * https://support.google.com/docs/answer/3098292?hl=en
     */
    const folioRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(C2), "^[1-9]\d*[rvab]?$")')
        .setHelpText('Folio must be a number optionally followed by "r", "v", "a", or "b".')
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

    /* FIXME this formula has to depend on a cell value specified in A1
     * notation for some reason, so it's brittle and will fail if the order
     * of fields is changed. Not sure how to get around this. See:
     * https://support.google.com/docs/answer/3098292?hl=en
     */
    const fourDigitYearRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(A2), "^[1-9]\d{3}$")')
        .setHelpText('Must be a 4-digit year.')
        .setAllowInvalid(false)
        .build()

    /* FIXME this formula has to depend on a cell value specified in A1
     * notation for some reason, so it's brittle and will fail if the order
     * of fields is changed. Not sure how to get around this. See:
     * https://support.google.com/docs/answer/3098292?hl=en
     */
    const centuryRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(G2), "^[1-9]\d?(\.(25|5|75))?$")')
        .setHelpText('Must be a one or two-digit number optionally followed by ".25", ".5", or ".75".')
        .setAllowInvalid(false)
        .build()

    /* FIXME this formula has to depend on a cell value specified in A1
     * notation for some reason, so it's brittle and will fail if the order
     * of fields is changed. Not sure how to get around this. See:
     * https://support.google.com/docs/answer/3098292?hl=en
     */
    const latitudeRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(F2), "^-?(([1-8]\d(\.\d+)?)|90(\.0+)?)$")')
        .setHelpText('Must be a valid latitude between -90 and 90°.')
        .setAllowInvalid(false)
        .build()

    /* FIXME this formula has to depend on a cell value specified in A1
     * notation for some reason, so it's brittle and will fail if the order
     * of fields is changed. Not sure how to get around this. See:
     * https://support.google.com/docs/answer/3098292?hl=en
     */
    const longitudeRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(G2), "^-?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$")')
        .setHelpText('Must be a valid longitude between -180° and 180°.')
        .setAllowInvalid(false)
        .build()

    /* apply rules/formulas */
    
    // manuscript
    spreadsheet.getRangeByName('manuscript__name') // auto-creates names like "Vatican (GVE) 23"
        .setFormula('=if(and(not(isblank(B2)), not(isblank(D2))), concatenate(D2, " ", B2),)')

    spreadsheet.getRangeByName('manuscript__collection')
        .setDataValidation(collectionRule)

    spreadsheet.getRangeByName('manuscript__original_collection')
        .setDataValidation(collectionRule)

    spreadsheet.getRangeByName('manuscript__number_of_stories')
        .setFormula('=if(not(isblank(A2)),countif(story_instance__manuscript, A2),)')

    // spreadsheet.getRangeByName('manuscript__date_range_start')
    //     .setDataValidation(fourDigitYearRule)

    // spreadsheet.getRangeByName('manuscript__date_range_end')
    //     .setDataValidation(fourDigitYearRule)

    // spreadsheet.getRangeByName('manuscript__century')
    //     .setDataValidation(centuryRule)

    // canonical story
    spreadsheet.getRangeByName('canonical_story__origin')
        .setDataValidation(storyOriginRule)

    spreadsheet.getRangeByName('canonical_story__incipit_source')
        .setDataValidation(manuscriptRule)

    // spreadsheet.getRangeByName('canonical_story__macomber_id')
    //     .setDataValidation(positiveIntegerRule)

    // story instance
    spreadsheet.getRangeByName('story_instance__manuscript')
        .setDataValidation(manuscriptRule)

    spreadsheet.getRangeByName('story_instance__canonical_story_id')
        .setDataValidation(canonicalStoryRule)

    spreadsheet.getRangeByName('story_instance__canonical_story_title')
        .setDataValidation(canonicalStoryTitleRule)

    // spreadsheet.getRangeByName('story_instance__folio')
    //     .setDataValidation(folioRule)

    // spreadsheet.getRangeByName('story_instance__column_start')
    //     .setDataValidation(positiveIntegerRule)
    
    // spreadsheet.getRangeByName('story_instance__line_start')
    //     .setDataValidation(positiveIntegerRule)

    // spreadsheet.getRangeByName('story_instance__column_end')
    //     .setDataValidation(positiveIntegerRule)

    // spreadsheet.getRangeByName('story_instance__line_end')
    //     .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__confidence_score')
        .setDataValidation(confidenceScoreRule)

    // story origin
    spreadsheet.getRangeByName('story_origin__region')
        .setDataValidation(regionRule)

    // collection
    spreadsheet.getRangeByName('collection__name') // auto-creates names like "Vatican (GVE)"
        .setFormula('=if(and(not(isblank(B2)), not(isblank(C2))), concatenate(B2, " (", C2, ")"),)')

    // spreadsheet.getRangeByName('collection__latitude')
    //     .setDataValidation(latitudeRule)
    //     .setNumberFormat('0.00000')

    // spreadsheet.getRangeByName('collection__longitude')
    //     .setDataValidation(longitudeRule)
    //     .setNumberFormat('0.00000')
}