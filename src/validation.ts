import { Spreadsheet } from './spreadsheet'

export const setupValidation = (spreadsheet: Spreadsheet): Spreadsheet => {

    /* create data validation */
    const manuscriptRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('manuscript__manuscript_name'))
        .setHelpText('Manuscript name must be listed on Manuscripts sheet.')
        .setAllowInvalid(false)
        .build()

    const collectionRule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(spreadsheet.getRangeByName('collection__name'))
        .setHelpText('Collection must be listed on Collections sheet.')
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

    /* NOTE: regex validation must be bound to a single cell in the
     * beginning of the range (currently D2); this means it will
     * fail if the order of fields changes (either by changes to this
     * schema or by columns added manually later).
     * of fields is changed. Not sure how to get around this.

     * See regex match documentation:
     * https://support.google.com/docs/answer/3098292?hl=en
     */
    const folioRegex = '^[1-9]+\\d*[rvab]?$';
    const folioHelpText = 'Folio must be a number optionally followed by "r", "v", "a", or "b".'
    const folioRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(index(A:ZZ, row(), column())), "' + folioRegex + '")')
        .setHelpText(folioHelpText)
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

    /*
     * Referencing based on row and column within the current sheet.
     */
    const fourDigitYearRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(index(A:ZZ, row(), column())), "^[1-9]\\d{3}$")')
        .setHelpText('Must be a 4-digit year.')
        .setAllowInvalid(false)
        .build()

    const latitudeRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(index(A:ZZ, row(), column())), "^-?(([1-8]\\d(\\.\\d+)?)|90(\\.0+)?)$")')
        .setHelpText('Must be a valid latitude between -90 and 90°.')
        .setAllowInvalid(false)
        .build()

    const longitudeRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(index(A:ZZ, row(), column())), "^-?(180(\\.0+)?|((1[0-7]\\d)|([1-9]?\\d))(\\.\\d+)?)$")')
        .setHelpText('Must be a valid longitude between -180° and 180°.')
        .setAllowInvalid(false)
        .build()

    /*
     * Macomber identifiers are numeric with an optional letter suffix.
     * Letters used run from A through F, with one case of A1/A2.
     */
    const macomberIDRule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied('=regexmatch(to_text(index(A:ZZ, row(), column())), "^[1-9]\\d*(-[A-F][1-2]?)?$")')
        .setHelpText('Must be a number optionally followed by "-A" through "-F" or "-A2".')
        .setAllowInvalid(false)
        .build()


    /* apply rules/formulas */

    // manuscript
    spreadsheet.getRangeByName('manuscript__manuscript_name') // auto-creates names like "Vatican (GVE) 23"
        .setFormula('=if(and(not(isblank(B2)), not(isblank(D2))), concatenate(D2, " ", B2),)')

    spreadsheet.getRangeByName('manuscript__collection')
        .setDataValidation(collectionRule)

    spreadsheet.getRangeByName('manuscript__original_collection')
        .setDataValidation(collectionRule)

    spreadsheet.getRangeByName('manuscript__total_folios')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('manuscript__total_pages')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('manuscript__total_stories')
        .setFormula('=if(not(isblank(A2)),countif(story_instance__manuscript, A2),)')

    spreadsheet.getRangeByName('manuscript__date_range_start')
        .setDataValidation(fourDigitYearRule)

    spreadsheet.getRangeByName('manuscript__date_range_end')
        .setDataValidation(fourDigitYearRule)

    // canonical story
    spreadsheet.getRangeByName('canonical_story__origin')
        .setDataValidation(storyOriginRule)

    // use @ to set text format; center for readability
    spreadsheet.getRangeByName('canonical_story__macomber_id')
        .setDataValidation(macomberIDRule)
        .setNumberFormat('@')
        .setHorizontalAlignment('center')

    // story instance
    spreadsheet.getRangeByName('story_instance__manuscript')
        .setDataValidation(manuscriptRule)

    // use @ to set text format; should match macomber id format
    spreadsheet.getRangeByName('story_instance__canonical_story_id')
        .setDataValidation(canonicalStoryRule)
        .setNumberFormat('@')
        .setHorizontalAlignment('center')

    // display canonical story title based on canonical story id
    spreadsheet.getRangeByName('story_instance__canonical_story_title')
        .setFormula("=if(not(isblank(B2)), VLOOKUP(B2, 'Canonical Story'!A:B, 2, false), )")

    spreadsheet.getRangeByName('story_instance__folio_start')
        .setDataValidation(folioRule)

    spreadsheet.getRangeByName('story_instance__folio_end')
        .setDataValidation(folioRule)

    spreadsheet.getRangeByName('story_instance__column_start')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__line_start')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__column_end')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__line_end')
        .setDataValidation(positiveIntegerRule)

    spreadsheet.getRangeByName('story_instance__confidence_score')
        .setDataValidation(confidenceScoreRule)

    spreadsheet.getRangeByName('story_instance__macomber_incipit')
        .setDataValidation(booleanRule)

    spreadsheet.getRangeByName('story_instance__exclude_from_itool')
        .setDataValidation(booleanRule)

    // story origin
    spreadsheet.getRangeByName('story_origin__region')
        .setDataValidation(regionRule)

    // collection
    spreadsheet.getRangeByName('collection__name') // auto-creates names like "Vatican (GVE)"
        .setFormula('=if(and(not(isblank(B2)), not(isblank(C2))), concatenate(B2, " (", C2, ")"),)')

    spreadsheet.getRangeByName('collection__latitude')
        .setDataValidation(latitudeRule)
        .setNumberFormat('0.00000')

    spreadsheet.getRangeByName('collection__longitude')
        .setDataValidation(longitudeRule)
        .setNumberFormat('0.00000')

    /* return spreadsheet when setup completed */
    return spreadsheet
}